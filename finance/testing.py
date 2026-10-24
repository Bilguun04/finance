from django.contrib.auth import get_user_model
from django.test import TestCase


DEFAULT_PASSWORD = "SecurePassword123!"


class FinanceTestCase(TestCase):
    def setUp(self):
        self.user = self.create_user("test@example.com", password=DEFAULT_PASSWORD, display_name="Test User")

    def create_user(self, email, password=DEFAULT_PASSWORD, display_name=None):
        user = get_user_model().objects.create_user(username=email, email=email, password=password)
        return user

    def login(self, email, password=DEFAULT_PASSWORD):
        return self.client.login(username=email, password=password)
