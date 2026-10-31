from decimal import Decimal

from django.db import IntegrityError
from django.urls import reverse

from finance.testing import FinanceTestCase
from portfolio.models import Portfolio

from . import services as sf
from .models import FriendRequest


class FriendServiceTests(FinanceTestCase):
    def setUp(self):
        super().setUp()
        self.alice = self.create_user("alice@example.com", display_name="Alice")
        self.bob = self.create_user("bob@example.com", display_name="Bob")
        self.carol = self.create_user("carol@example.com", display_name="Carol")

    def befriend(self, a, b):
        request = sf.send_request(a, b)
        sf.accept_request(b, request.id)

    def test_send_and_accept(self):
        request = sf.send_request(self.alice, self.bob)
        self.assertEqual(sf.relationship(self.alice, self.bob), "sent")
        self.assertEqual(sf.relationship(self.bob, self.alice), "received")
        self.assertFalse(sf.are_friends(self.alice, self.bob))

        sf.accept_request(self.bob, request.id)

        self.assertTrue(sf.are_friends(self.alice, self.bob))
        self.assertTrue(sf.are_friends(self.bob, self.alice))
        self.assertEqual(sf.relationship(self.alice, self.bob), "friends")
        self.assertIsNotNone(sf.friendship(self.alice, self.bob).responded_at)

    def test_only_recipient_can_accept(self):
        request = sf.send_request(self.alice, self.bob)
        with self.assertRaises(sf.FriendshipError):
            sf.accept_request(self.alice, request.id)
        with self.assertRaises(sf.FriendshipError):
            sf.accept_request(self.carol, request.id)
        self.assertFalse(sf.are_friends(self.alice, self.bob))

    def test_cannot_add_self(self):
        with self.assertRaises(sf.FriendshipError):
            sf.send_request(self.alice, self.alice)

    def test_db_rejects_self_request(self):
        with self.assertRaises(IntegrityError):
            FriendRequest.objects.create(from_user=self.alice, to_user=self.alice)

    def test_duplicate_request_is_rejected(self):
        sf.send_request(self.alice, self.bob)
        with self.assertRaises(sf.FriendshipError):
            sf.send_request(self.alice, self.bob)

    def test_request_to_existing_friend_is_rejected(self):
        self.befriend(self.alice, self.bob)
        with self.assertRaises(sf.FriendshipError):
            sf.send_request(self.bob, self.alice)

    def test_crossed_requests_become_friendship(self):
        sf.send_request(self.alice, self.bob)
        request = sf.send_request(self.bob, self.alice)

        self.assertEqual(request.status, FriendRequest.Status.ACCEPTED)
        self.assertTrue(sf.are_friends(self.alice, self.bob))
        self.assertEqual(FriendRequest.objects.count(), 1)

    def test_decline_allows_a_fresh_request(self):
        request = sf.send_request(self.alice, self.bob)
        sf.decline_request(self.bob, request.id)

        self.assertIsNone(sf.relationship(self.alice, self.bob))
        sf.send_request(self.alice, self.bob)
        self.assertEqual(sf.relationship(self.alice, self.bob), "sent")

    def test_cancel_is_sender_only(self):
        request = sf.send_request(self.alice, self.bob)
        with self.assertRaises(sf.FriendshipError):
            sf.cancel_request(self.bob, request.id)
        sf.cancel_request(self.alice, request.id)
        self.assertFalse(FriendRequest.objects.exists())

    def test_unfriend(self):
        self.befriend(self.alice, self.bob)
        sf.unfriend(self.bob, self.alice)
        self.assertFalse(sf.are_friends(self.alice, self.bob))
        with self.assertRaises(sf.FriendshipError):
            sf.unfriend(self.bob, self.alice)

    def test_friends_of_covers_both_directions(self):
        self.befriend(self.alice, self.bob)
        self.befriend(self.carol, self.alice)
        sf.send_request(self.alice, self.user)  # pending, not a friend yet

        self.assertEqual(list(sf.friends_of(self.alice)), [self.bob, self.carol])
        self.assertEqual(list(sf.friends_of(self.bob)), [self.alice])

    def test_incoming_and_outgoing(self):
        sf.send_request(self.alice, self.bob)
        sf.send_request(self.carol, self.alice)
        self.assertEqual([r.to_user for r in sf.outgoing_requests(self.alice)], [self.bob])
        self.assertEqual([r.from_user for r in sf.incoming_requests(self.alice)], [self.carol])


class FriendRequestFlowTests(FinanceTestCase):
    def setUp(self):
        super().setUp()
        self.alice = self.create_user("alice@example.com", display_name="Alice")
        self.bob = self.create_user("bob@example.com", display_name="Bob")
        self.carol = self.create_user("carol@example.com", display_name="Carol")
        self.client.force_login(self.alice)

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("social:friends"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("account:login"), response.url)

    def test_search_requires_exact_username(self):
        response = self.client.get(reverse("social:friends"), {"q": "BOB@example.com"})
        self.assertEqual(response.context["match"], self.bob)

        response = self.client.get(reverse("social:friends"), {"q": "bob"})
        self.assertIsNone(response.context["match"])
        self.assertContains(response, "Usernames must match exactly")

    def test_search_never_shows_email_of_other_users(self):
        self.bob.username = "bobby"
        self.bob.save()
        response = self.client.get(reverse("social:friends"), {"q": "bobby"})
        self.assertContains(response, "bobby")
        self.assertNotContains(response, "bob@example.com")

    def test_search_for_self(self):
        response = self.client.get(reverse("social:friends"), {"q": self.alice.username})
        self.assertEqual(response.context["match_relationship"], "self")
        self.assertContains(response, "That's you")

    def test_send_request_keeps_search(self):
        response = self.client.post(reverse("social:send_request"), {"username": self.bob.username, "q": self.bob.username})
        self.assertRedirects(response, reverse("social:friends") + "?q=bob%40example.com")
        self.assertEqual(sf.relationship(self.alice, self.bob), "sent")

    def test_send_request_to_unknown_user_404s(self):
        response = self.client.post(reverse("social:send_request"), {"username": "nobody"})
        self.assertEqual(response.status_code, 404)

    def test_duplicate_request_shows_error(self):
        sf.send_request(self.alice, self.bob)
        response = self.client.post(reverse("social:send_request"), {"username": self.bob.username}, follow=True)
        self.assertContains(response, "You already sent")

    def test_accept_and_decline(self):
        from_bob = sf.send_request(self.bob, self.alice)
        from_carol = sf.send_request(self.carol, self.alice)

        response = self.client.get(reverse("social:friends"))
        self.assertContains(response, self.bob.username)
        self.assertContains(response, self.carol.username)

        self.client.post(reverse("social:accept_request", args=[from_bob.id]))
        self.client.post(reverse("social:decline_request", args=[from_carol.id]))

        self.assertTrue(sf.are_friends(self.alice, self.bob))
        self.assertIsNone(sf.relationship(self.alice, self.carol))

    def test_cannot_accept_someone_elses_request(self):
        request = sf.send_request(self.bob, self.carol)
        response = self.client.post(reverse("social:accept_request", args=[request.id]), follow=True)
        self.assertContains(response, "no longer exists")
        self.assertFalse(sf.are_friends(self.bob, self.carol))

    def test_cancel(self):
        request = sf.send_request(self.alice, self.bob)
        self.client.post(reverse("social:cancel_request", args=[request.id]))
        self.assertFalse(FriendRequest.objects.exists())

    def test_unfriend(self):
        sf.accept_request(self.alice, sf.send_request(self.bob, self.alice).id)
        response = self.client.post(reverse("social:unfriend", args=[self.bob.username]))
        self.assertRedirects(response, reverse("social:friends"))
        self.assertFalse(sf.are_friends(self.alice, self.bob))

    def test_actions_reject_get(self):
        request = sf.send_request(self.bob, self.alice)
        for url in [
            reverse("social:send_request"),
            reverse("social:accept_request", args=[request.id]),
            reverse("social:decline_request", args=[request.id]),
            reverse("social:cancel_request", args=[request.id]),
            reverse("social:unfriend", args=[self.bob.username]),
        ]:
            self.assertEqual(self.client.get(url).status_code, 405)


class FriendPortfolioVisibilityTests(FinanceTestCase):
    def setUp(self):
        super().setUp()
        self.alice = self.create_user("alice@example.com", display_name="Alice")
        self.bob = self.create_user("bob@example.com", display_name="Bob")

        self.shared = Portfolio.objects.create(user=self.bob, name="Growth", is_public=True)
        self.shared.add_cash(Decimal("10000"))
        self.shared.buy("AAPL", Decimal("10"), Decimal("150"))  # $1,500 of $10,000 = 15%
        self.shared.buy("MSFT", Decimal("10"), Decimal("350"))  # $3,500 = 35%, cash $5,000 = 50%
        self.private = Portfolio.objects.create(user=self.bob, name="Secret stash")
        self.private.add_cash(Decimal("777"))

        self.profile_url = reverse("social:friend_profile", args=[self.bob.username])
        self.client.force_login(self.alice)

    def befriend(self):
        sf.accept_request(self.bob, sf.send_request(self.alice, self.bob).id)

    def test_non_friend_gets_404(self):
        self.assertEqual(self.client.get(self.profile_url).status_code, 404)

    def test_pending_request_is_not_enough(self):
        sf.send_request(self.alice, self.bob)
        self.assertEqual(self.client.get(self.profile_url).status_code, 404)

    def test_friend_sees_only_public_portfolios(self):
        self.befriend()
        response = self.client.get(self.profile_url)
        self.assertContains(response, "Growth")
        self.assertNotContains(response, "Secret stash")

    def test_friend_sees_percentages_not_dollars(self):
        self.befriend()
        response = self.client.get(self.profile_url)

        entry = response.context["shared"][0]
        self.assertEqual([h["symbol"] for h in entry["holdings"]], ["MSFT", "AAPL"])
        self.assertEqual(entry["holdings"][0]["weight"], Decimal("35"))
        self.assertEqual(entry["holdings"][1]["weight"], Decimal("15"))
        self.assertEqual(entry["cash_pct"], Decimal("50"))

        self.assertContains(response, "35.0%")
        self.assertNotContains(response, "$")
        for amount in ["10000", "10,000", "3500", "3,500", "1500", "1,500", "5000", "5,000", "777"]:
            self.assertNotContains(response, amount)

    def test_unfriending_revokes_access(self):
        self.befriend()
        sf.unfriend(self.alice, self.bob)
        self.assertEqual(self.client.get(self.profile_url).status_code, 404)

    def test_making_portfolio_private_hides_it(self):
        self.befriend()
        self.shared.is_public = False
        self.shared.save()
        response = self.client.get(self.profile_url)
        self.assertNotContains(response, "Growth")
        self.assertContains(response, "Nothing shared yet")

    def test_friends_list_shows_shared_count(self):
        self.befriend()
        Portfolio.objects.create(user=self.bob, name="Also public", is_public=True)
        response = self.client.get(reverse("social:friends"))
        friend = response.context["friends"][0]
        self.assertEqual(friend.shared_count, 2)
        self.assertContains(response, "2 shared portfolios")

    def test_empty_shared_portfolio(self):
        self.befriend()
        Portfolio.objects.create(user=self.bob, name="Brand new", is_public=True)
        response = self.client.get(self.profile_url)
        self.assertContains(response, "Nothing in this portfolio yet.")
