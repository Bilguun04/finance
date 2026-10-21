from django.urls import reverse

from finance.testing import FinanceTestCase

from .services import get_profile


class AccountTests(FinanceTestCase):
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

    def test_logout_clears_session(self):
        self.create_user("dave@example.com")
        self.login("dave@example.com")
        self.client.post(reverse("account:logout"))
        response = self.client.get(reverse("account:profile"))
        self.assertEqual(response.status_code, 302)
