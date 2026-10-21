from decimal import Decimal

from django.urls import reverse

from finance.testing import FinanceTestCase


class CoreViewTests(FinanceTestCase):
    def test_anonymous_sees_landing_page(self):
        response = self.client.get(reverse("core:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/landing.html")