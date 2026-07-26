from django.urls import reverse

from finance.testing import FirestoreTestCase

from . import firestore as sf


class FriendRequestFlowTests(FirestoreTestCase):
    def setUp(self):
        super().setUp()
        self.alice = self.create_user("alice@example.com", display_name="Alice")
        self.bob = self.create_user("bob@example.com", display_name="Bob")
        self.carol = self.create_user("carol@example.com", display_name="Carol")
        # Logging in at least once is what creates each user's Firestore profile
        # doc in production (see account.views.create_session) — friend requests
        # can only target users who have signed in at least once.
        for email in ("alice@example.com", "bob@example.com", "carol@example.com"):
            self.login(email)

    def test_send_request_creates_pending(self):
        self.login("alice@example.com")
        self.client.post(reverse("social:friend_request_send", args=[self.bob.uid]))
        requests = sf.outgoing_requests(self.alice.uid)
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0]["to_uid"], self.bob.uid)

    def test_duplicate_request_prevented(self):
        self.login("alice@example.com")
        self.client.post(reverse("social:friend_request_send", args=[self.bob.uid]))
        self.client.post(reverse("social:friend_request_send", args=[self.bob.uid]))
        self.assertEqual(len(sf.outgoing_requests(self.alice.uid)), 1)

    def test_only_recipient_can_accept(self):
        friend_request = sf.send_friend_request(self.alice.uid, self.bob.uid)
        self.login("carol@example.com")
        response = self.client.post(reverse("social:friend_request_accept", args=[friend_request["id"]]))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(sf.get_friend_request(friend_request["id"])["status"], sf.STATUS_PENDING)

    def test_sender_cannot_accept_own_request(self):
        friend_request = sf.send_friend_request(self.alice.uid, self.bob.uid)
        self.login("alice@example.com")
        response = self.client.post(reverse("social:friend_request_accept", args=[friend_request["id"]]))
        self.assertEqual(response.status_code, 403)

    def test_recipient_can_accept_and_friendship_is_symmetric(self):
        friend_request = sf.send_friend_request(self.alice.uid, self.bob.uid)
        self.login("bob@example.com")
        response = self.client.post(reverse("social:friend_request_accept", args=[friend_request["id"]]))
        self.assertRedirects(response, reverse("social:friend_list"))

        self.assertIn(self.bob.uid, sf.friend_uids(self.alice.uid))
        self.assertIn(self.alice.uid, sf.friend_uids(self.bob.uid))
        self.assertTrue(sf.are_friends(self.alice.uid, self.bob.uid))

    def test_search_excludes_self_and_existing_friends(self):
        sf.send_friend_request(self.alice.uid, self.bob.uid)
        sf.respond_to_request(
            sf.find_existing_request(self.alice.uid, self.bob.uid)["id"], sf.STATUS_ACCEPTED
        )
        self.login("alice@example.com")
        response = self.client.get(reverse("social:friend_search"), {"q": "a"})
        uids = [u["uid"] for u in response.context["results"]]
        self.assertNotIn(self.alice.uid, uids)
        self.assertNotIn(self.bob.uid, uids)


class FriendPortfolioVisibilityTests(FirestoreTestCase):
    def setUp(self):
        super().setUp()
        self.alice = self.create_user("alice@example.com", display_name="Alice")
        self.bob = self.create_user("bob@example.com", display_name="Bob")

    def test_non_friend_gets_403(self):
        self.login("bob@example.com")
        response = self.client.get(reverse("social:friend_portfolio", args=[self.alice.uid]))
        self.assertEqual(response.status_code, 403)

    def test_accepted_friend_gets_200(self):
        friend_request = sf.send_friend_request(self.alice.uid, self.bob.uid)
        sf.respond_to_request(friend_request["id"], sf.STATUS_ACCEPTED)
        self.login("bob@example.com")
        response = self.client.get(reverse("social:friend_portfolio", args=[self.alice.uid]))
        self.assertEqual(response.status_code, 200)

    def test_anonymous_redirected_to_login(self):
        response = self.client.get(reverse("social:friend_portfolio", args=[self.alice.uid]))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("account:login"), response.url)
