from django.contrib.auth import get_user_model
from django.test import TestCase

from account.services import create_profile_if_missing

DEFAULT_PASSWORD = "correcthorsebattery9"


class FinanceTestCase(TestCase):

    def create_user(self, email, password=DEFAULT_PASSWORD, display_name=None):
        user = get_user_model().objects.create_user(username=email, email=email, password=password)
        create_profile_if_missing(user, display_name=display_name or email.split("@")[0])
        return user

    def login(self, email, password=DEFAULT_PASSWORD):
        return self.client.login(username=email, password=password)
