from django.urls import reverse

from finance.testing import FinanceTestCase

from . import services as sf


class FriendRequestFlowTests(FinanceTestCase):
    def setUp(self):
        super().setUp()
        self.alice = self.create_user("alice@example.com", display_name="Alice")
        self.bob = self.create_user("bob@example.com", display_name="Bob")
        self.carol = self.create_user("carol@example.com", display_name="Carol")

    def test_send_request_creates_pending(self):
        self.login("alice@example.com")
        self.client.post(reverse("social:friend_request_send", args=[self.bob.pk]))
        requests = sf.outgoing_requests(self.alice.pk)
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0]["to_uid"], self.bob.pk)

    def test_duplicate_request_prevented(self):
        self.login("alice@example.com")
        self.client.post(reverse("social:friend_request_send", args=[self.bob.pk]))
        self.client.post(reverse("social:friend_request_send", args=[self.bob.pk]))
        self.assertEqual(len(sf.outgoing_requests(self.alice.pk)), 1)

    def test_only_recipient_can_accept(self):
        friend_request = sf.send_friend_request(self.alice.pk, self.bob.pk)
        self.login("carol@example.com")
        response = self.client.post(reverse("social:friend_request_accept", args=[friend_request["id"]]))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(sf.get_friend_request(friend_request["id"])["status"], sf.STATUS_PENDING)

    def test_sender_cannot_accept_own_request(self):
        friend_request = sf.send_friend_request(self.alice.pk, self.bob.pk)
        self.login("alice@example.com")
        response = self.client.post(reverse("social:friend_request_accept", args=[friend_request["id"]]))
        self.assertEqual(response.status_code, 403)

    def test_recipient_can_accept_and_friendship_is_symmetric(self):
        friend_request = sf.send_friend_request(self.alice.pk, self.bob.pk)
        self.login("bob@example.com")
        response = self.client.post(reverse("social:friend_request_accept", args=[friend_request["id"]]))
        self.assertRedirects(response, reverse("social:friend_list"))

        self.assertIn(self.bob.pk, sf.friend_uids(self.alice.pk))
        self.assertIn(self.alice.pk, sf.friend_uids(self.bob.pk))
        self.assertTrue(sf.are_friends(self.alice.pk, self.bob.pk))

    def test_search_excludes_self_and_existing_friends(self):
        sf.send_friend_request(self.alice.pk, self.bob.pk)
        sf.respond_to_request(
            sf.find_existing_request(self.alice.pk, self.bob.pk)["id"], sf.STATUS_ACCEPTED
        )
        self.login("alice@example.com")
        response = self.client.get(reverse("social:friend_search"), {"q": "a"})
        uids = [u["uid"] for u in response.context["results"]]
        self.assertNotIn(self.alice.pk, uids)
        self.assertNotIn(self.bob.pk, uids)


class FriendPortfolioVisibilityTests(FinanceTestCase):
    def setUp(self):
        super().setUp()
        self.alice = self.create_user("alice@example.com", display_name="Alice")
        self.bob = self.create_user("bob@example.com", display_name="Bob")

    def test_non_friend_gets_403(self):
        self.login("bob@example.com")
        response = self.client.get(reverse("social:friend_portfolio", args=[self.alice.pk]))
        self.assertEqual(response.status_code, 403)

    def test_accepted_friend_gets_200(self):
        friend_request = sf.send_friend_request(self.alice.pk, self.bob.pk)
        sf.respond_to_request(friend_request["id"], sf.STATUS_ACCEPTED)
        self.login("bob@example.com")
        response = self.client.get(reverse("social:friend_portfolio", args=[self.alice.pk]))
        self.assertEqual(response.status_code, 200)

    def test_anonymous_redirected_to_login(self):
        response = self.client.get(reverse("social:friend_portfolio", args=[self.alice.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("account:login"), response.url)
