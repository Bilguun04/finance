import json

from django.urls import reverse

from finance.testing import FirestoreTestCase

from .firestore import get_profile
from .middleware import SESSION_COOKIE_NAME


class CreateSessionTests(FirestoreTestCase):
    def test_create_session_sets_cookie_and_creates_profile(self):
        user = self.create_user("alice@example.com", display_name="Alice")
        id_token = self.get_id_token("alice@example.com")

        response = self.client.post(
            reverse("account:create_session"),
            data=json.dumps({"idToken": id_token}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(SESSION_COOKIE_NAME, response.cookies)

        profile = get_profile(user.uid)
        self.assertIsNotNone(profile)
        self.assertEqual(profile["email"], "alice@example.com")

    def test_create_session_rejects_invalid_token(self):
        response = self.client.post(
            reverse("account:create_session"),
            data=json.dumps({"idToken": "not-a-real-token"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_create_session_rejects_missing_body(self):
        response = self.client.post(
            reverse("account:create_session"),
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)


class FirebaseLoginRequiredTests(FirestoreTestCase):
    def test_anonymous_redirected_to_login(self):
        response = self.client.get(reverse("account:profile"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("account:login"), response.url)

    def test_logged_in_user_can_view_profile(self):
        self.create_user("bob@example.com", display_name="Bob")
        self.login("bob@example.com")

        response = self.client.get(reverse("account:profile"))
        self.assertEqual(response.status_code, 200)


class ProfileEditTests(FirestoreTestCase):
    def test_profile_edit_updates_firestore(self):
        user = self.create_user("carol@example.com", display_name="Carol")
        self.login("carol@example.com")

        response = self.client.post(
            reverse("account:profile_edit"),
            {"display_name": "Carol Danvers", "bio": "Investor"},
        )
        self.assertRedirects(response, reverse("account:profile"))

        profile = get_profile(user.uid)
        self.assertEqual(profile["display_name"], "Carol Danvers")
        self.assertEqual(profile["bio"], "Investor")


class LogoutTests(FirestoreTestCase):
    def test_logout_clears_session(self):
        self.create_user("dave@example.com")
        self.login("dave@example.com")

        response = self.client.get(reverse("account:profile"))
        self.assertEqual(response.status_code, 200)

        self.client.post(reverse("account:logout"))

        response = self.client.get(reverse("account:profile"))
        self.assertEqual(response.status_code, 302)
