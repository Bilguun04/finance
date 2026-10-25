from django.urls import reverse

from finance.testing import FinanceTestCase

from . import services as sf


class FriendRequestFlowTests(FinanceTestCase):
    def setUp(self):
        super().setUp()
        self.alice = self.create_user("alice@example.com", display_name="Alice")
        self.bob = self.create_user("bob@example.com", display_name="Bob")
        self.carol = self.create_user("carol@example.com", display_name="Carol")


class FriendPortfolioVisibilityTests(FinanceTestCase):
    def setUp(self):
        super().setUp()
        self.alice = self.create_user("alice@example.com", display_name="Alice")
        self.bob = self.create_user("bob@example.com", display_name="Bob")