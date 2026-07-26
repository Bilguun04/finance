from decimal import Decimal

from django.urls import reverse

from finance.testing import FirestoreTestCase
from portfolio import firestore as pf


class CoreViewTests(FirestoreTestCase):
    def test_anonymous_sees_landing_page(self):
        response = self.client.get(reverse("core:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/landing.html")

    def test_authenticated_index_redirects_to_dashboard(self):
        self.create_user("alice@example.com")
        self.login("alice@example.com")
        response = self.client.get(reverse("core:index"))
        self.assertRedirects(response, reverse("core:dashboard"))

    def test_dashboard_shows_aggregated_totals(self):
        user = self.create_user("alice@example.com")
        pf.add_holding(
            user.uid,
            {
                "symbol": "AAPL",
                "name": "",
                "asset_type": "STOCK",
                "quantity": Decimal("10"),
                "cost_basis_per_unit": Decimal("100.00"),
                "current_price": Decimal("150.00"),
            },
        )
        self.login("alice@example.com")
        response = self.client.get(reverse("core:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["portfolio"].total_value, Decimal("1500.00"))

    def test_anonymous_dashboard_redirects_to_login(self):
        response = self.client.get(reverse("core:dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("account:login"), response.url)
