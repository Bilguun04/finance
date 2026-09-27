from django.urls import reverse

from finance.testing import FinanceTestCase

from .services import get_profile


class AccountTests(FinanceTestCase):
    def test_signup_creates_user_profile_and_session(self):
        response = self.client.post(
            reverse("account:signup"),
            {
                "email": "alice@example.com",
                "password1": "correcthorsebattery9",
                "password2": "correcthorsebattery9",
            },
        )
        self.assertRedirects(response, reverse("core:dashboard"))
        user = self.get_user_model().objects.get(email="alice@example.com")
        self.assertTrue(user.is_authenticated)
        self.assertEqual(get_profile(user.pk)["email"], "alice@example.com")

    def get_user_model(self):
        from django.contrib.auth import get_user_model

        return get_user_model()

    def test_invalid_login_is_rejected(self):
        self.create_user("alice@example.com")
        response = self.client.post(
            reverse("account:login"),
            {"username": "alice@example.com", "password": "wrong-password"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a correct")

    def test_authenticated_user_can_edit_profile(self):
        user = self.create_user("carol@example.com", display_name="Carol")
        self.login("carol@example.com")
        response = self.client.post(
            reverse("account:profile_edit"),
            {"display_name": "Carol Danvers", "bio": "Investor"},
        )
        self.assertRedirects(response, reverse("account:profile"))
        profile = get_profile(user.pk)
        self.assertEqual(profile["display_name"], "Carol Danvers")

    def test_logout_clears_session(self):
        self.create_user("dave@example.com")
        self.login("dave@example.com")
        self.client.post(reverse("account:logout"))
        response = self.client.get(reverse("account:profile"))
        self.assertEqual(response.status_code, 302)
