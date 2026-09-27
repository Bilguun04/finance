from decimal import Decimal

from django.urls import reverse

from finance.testing import FinanceTestCase

from . import services as pf


class HoldingComputedFieldsTests(FinanceTestCase):
    def test_market_value_and_gain_loss(self):
        user = self.create_user("alice@example.com")
        holding = pf.add_holding(
            user.pk,
            {
                "symbol": "AAPL",
                "name": "",
                "asset_type": "STOCK",
                "quantity": Decimal("10"),
                "cost_basis_per_unit": Decimal("100.00"),
                "current_price": Decimal("150.00"),
            },
        )
        self.assertEqual(holding.market_value, Decimal("1500.00"))
        self.assertEqual(holding.total_cost, Decimal("1000.00"))
        self.assertEqual(holding.gain_loss, Decimal("500.00"))
        self.assertEqual(holding.gain_loss_pct, Decimal("50.00"))

    def test_portfolio_totals_sum_across_holdings(self):
        user = self.create_user("alice@example.com")
        pf.add_holding(
            user.pk,
            {
                "symbol": "AAPL",
                "name": "",
                "asset_type": "STOCK",
                "quantity": Decimal("10"),
                "cost_basis_per_unit": Decimal("100.00"),
                "current_price": Decimal("150.00"),
            },
        )
        pf.add_holding(
            user.pk,
            {
                "symbol": "BTC",
                "name": "",
                "asset_type": "CRYPTO",
                "quantity": Decimal("1"),
                "cost_basis_per_unit": Decimal("20000.00"),
                "current_price": Decimal("18000.00"),
            },
        )
        portfolio = pf.get_or_create_portfolio(user.pk)
        self.assertEqual(portfolio.total_value, Decimal("19500.00"))
        self.assertEqual(portfolio.total_cost, Decimal("21000.00"))
        self.assertEqual(portfolio.total_gain_loss, Decimal("-1500.00"))


class HoldingOwnershipTests(FinanceTestCase):
    def setUp(self):
        super().setUp()
        self.user_a = self.create_user("alice@example.com")
        self.user_b = self.create_user("bob@example.com")
        self.holding_a = pf.add_holding(
            self.user_a.pk,
            {
                "symbol": "AAPL",
                "name": "",
                "asset_type": "STOCK",
                "quantity": Decimal("10"),
                "cost_basis_per_unit": Decimal("100.00"),
                "current_price": Decimal("150.00"),
            },
        )

    def test_anonymous_redirected_to_login(self):
        response = self.client.get(reverse("portfolio:detail"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("account:login"), response.url)

    def test_user_cannot_edit_another_users_holding(self):
        self.login("bob@example.com")
        response = self.client.get(reverse("portfolio:holding_edit", args=[self.holding_a.id]))
        self.assertEqual(response.status_code, 404)

    def test_user_cannot_delete_another_users_holding(self):
        self.login("bob@example.com")
        response = self.client.post(reverse("portfolio:holding_delete", args=[self.holding_a.id]))
        self.assertEqual(response.status_code, 404)
        self.assertIsNotNone(pf.get_holding(self.user_a.pk, self.holding_a.id))

    def test_owner_can_edit_own_holding(self):
        self.login("alice@example.com")
        response = self.client.post(
            reverse("portfolio:holding_edit", args=[self.holding_a.id]),
            {
                "symbol": "AAPL",
                "name": "",
                "asset_type": "STOCK",
                "quantity": "10",
                "cost_basis_per_unit": "100.00",
                "current_price": "200.00",
            },
        )
        self.assertRedirects(response, reverse("portfolio:detail"))
        updated = pf.get_holding(self.user_a.pk, self.holding_a.id)
        self.assertEqual(updated.current_price, Decimal("200.00"))


class HoldingHtmxTests(FinanceTestCase):
    def test_htmx_create_returns_partial(self):
        self.create_user("alice@example.com")
        self.login("alice@example.com")

        response = self.client.post(
            reverse("portfolio:holding_add"),
            {
                "symbol": "AAPL",
                "name": "",
                "asset_type": "STOCK",
                "quantity": "10",
                "cost_basis_per_unit": "100.00",
                "current_price": "150.00",
            },
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AAPL")
        self.assertNotContains(response, "<!doctype html>")
