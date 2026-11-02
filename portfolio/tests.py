from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.urls import reverse

from finance.testing import FinanceTestCase
from .models import Holding, Portfolio, Transaction


def make_quotes(**prices):
    """Shape a get_quotes() result the way portfolio.market returns it (float prices)."""
    return {symbol: {"price": price} if price is not None else None for symbol, price in prices.items()}


class PortfolioModelTests(FinanceTestCase):
    def test_create_portfolio(self):
        portfolio = Portfolio.objects.create(user=self.user, name="Main")
        self.assertEqual(portfolio.user, self.user)
        self.assertEqual(portfolio.name, "Main")
        self.assertEqual(portfolio.cash, Decimal("0"))
        self.assertEqual(portfolio.currency, "USD")
        self.assertAlmostEqual(portfolio.net_liquidity, Decimal("0"))

    def test_create_multiple_portfolios(self):
        portfolio1 = Portfolio.objects.create(user=self.user, name="Main")
        portfolio2 = Portfolio.objects.create(user=self.user, name="Retirement")

        for portfolio in [portfolio1, portfolio2]:
            self.assertEqual(portfolio.user, self.user)
            self.assertIn(portfolio.name, ["Main", "Retirement"])
            self.assertEqual(portfolio.cash, Decimal("0"))
            self.assertEqual(portfolio.currency, "USD")
            self.assertAlmostEqual(portfolio.net_liquidity, Decimal("0"))

    def test_deleting_portfolio(self):
        portfolio = Portfolio.objects.create(user=self.user)
        portfolio.delete()
        self.assertFalse(Portfolio.objects.exists())

    def test_portfolio_str(self):
        portfolio = Portfolio.objects.create(user=self.user, name="Main")
        self.assertEqual(str(portfolio), f"{portfolio.name} ({self.user}, {portfolio.currency})")

    def test_modify_portfolio(self):
        portfolio = Portfolio.objects.create(user=self.user, name="Main")
        self.assertEqual(portfolio.name, "Main")
        portfolio.name = "Modified"
        portfolio.save()
        self.assertEqual(portfolio.name, "Modified")

    def test_holdings_count(self):
        portfolio = Portfolio.objects.create(user=self.user)
        Holding.objects.create(portfolio=portfolio, symbol="AAPL", quantity=Decimal("1"), avg_cost=Decimal("1"))
        Holding.objects.create(portfolio=portfolio, symbol="MSFT", quantity=Decimal("1"), avg_cost=Decimal("1"))
        self.assertEqual(portfolio.holdings_count, 2)


class HoldingModelTests(FinanceTestCase):
    def setUp(self):
        super().setUp()
        self.portfolio = Portfolio.objects.create(user=self.user)

    def create_holding(self, symbol="AAPL", quantity="10", avg_cost="150", market_value="1500"):
        return Holding.objects.create(
            portfolio=self.portfolio,
            symbol=symbol,
            quantity=Decimal(quantity),
            avg_cost=Decimal(avg_cost),
            market_value=Decimal(market_value),
        )

    def test_create_holding(self):
        holding = Holding.objects.create(
            portfolio=self.portfolio,
            symbol="AAPL",
            quantity=Decimal("10"),
            avg_cost=Decimal("150"),
            market_value=Decimal("1500"),
        )
        self.assertEqual(holding.portfolio, self.portfolio)
        self.assertEqual(holding.symbol, "AAPL")
        self.assertEqual(holding.quantity, Decimal("10"))
        self.assertEqual(holding.avg_cost, Decimal("150"))
        self.assertEqual(holding.cost_basis, Decimal("1500.00"))
        self.assertEqual(holding.market_value, Decimal("1500.00"))
        self.assertEqual(holding.fraction_of_net_worth, Decimal("100.00"))

    def test_create_multiple_holdings(self):
        holding1 = self.create_holding(symbol="AAPL", quantity="10", avg_cost="150", market_value="1500")
        holding2 = self.create_holding(symbol="GOOGL", quantity="5", avg_cost="2000", market_value="10000")

        for holding in [holding1, holding2]:
            self.assertEqual(holding.portfolio, self.portfolio)
            self.assertIn(holding.symbol, ["AAPL", "GOOGL"])
            self.assertIn(holding.quantity, [Decimal("10"), Decimal("5")])
            self.assertIn(holding.avg_cost, [Decimal("150"), Decimal("2000")])
            self.assertIn(holding.cost_basis, [Decimal("1500.00"), Decimal("10000.00")])
            self.assertIn(holding.market_value, [Decimal("1500.00"), Decimal("10000.00")])

    def test_save_computes_cost_basis(self):
        holding = self.create_holding(quantity="10", avg_cost="150")
        holding.refresh_from_db()
        self.assertEqual(holding.cost_basis, Decimal("1500.00"))

    def test_cost_basis_supports_fractional_shares(self):
        holding = self.create_holding(quantity="2.5", avg_cost="100")
        holding.refresh_from_db()
        self.assertEqual(holding.cost_basis, Decimal("250.00"))

    def test_save_uppercases_symbol(self):
        holding = self.create_holding(symbol=" aapl ")
        self.assertEqual(holding.symbol, "AAPL")

    def test_str(self):
        holding = self.create_holding(quantity="10", avg_cost="150")
        self.assertEqual(str(holding), "AAPL - 10 shares at $150.00 each")

    def test_symbol_is_unique_per_portfolio(self):
        self.create_holding(symbol="AAPL")
        with self.assertRaises(IntegrityError):
            self.create_holding(symbol="AAPL")

    def test_same_symbol_allowed_in_different_portfolios(self):
        self.create_holding(symbol="AAPL")
        other = Portfolio.objects.create(user=self.user, name="Other")
        Holding.objects.create(portfolio=other, symbol="AAPL", quantity=Decimal("1"), avg_cost=Decimal("1"))
        self.assertEqual(Holding.objects.filter(symbol="AAPL").count(), 2)

    def test_deleting_portfolio_deletes_holdings(self):
        self.create_holding()
        self.portfolio.delete()
        self.assertFalse(Holding.objects.exists())

    def test_add_shares_reaverages_cost(self):
        holding = self.create_holding(quantity="10", avg_cost="150")

        holding.add_shares(Decimal("5"), Decimal("160"))
        holding.save()

        holding.refresh_from_db()
        self.assertEqual(holding.quantity, Decimal("15"))
        # (10 * 150 + 5 * 160) / 15 = 153.3333...
        self.assertEqual(holding.avg_cost, Decimal("153.3333"))
        self.assertEqual(holding.cost_basis, Decimal("2300.00"))

    def test_remove_shares_keeps_average_cost_and_returns_cost_of_sold(self):
        holding = self.create_holding(quantity="10", avg_cost="150")

        cost_of_sold = holding.remove_shares(Decimal("4"))

        self.assertEqual(cost_of_sold, Decimal("600"))
        self.assertEqual(holding.quantity, Decimal("6"))
        self.assertEqual(holding.avg_cost, Decimal("150"))

    def test_remove_shares_rejects_more_than_held(self):
        holding = self.create_holding(quantity="10")
        with self.assertRaises(ValueError):
            holding.remove_shares(Decimal("11"))

    def test_add_and_remove_shares_reject_non_positive_quantity(self):
        holding = self.create_holding()
        with self.assertRaises(ValueError):
            holding.add_shares(Decimal("0"), Decimal("100"))
        with self.assertRaises(ValueError):
            holding.remove_shares(Decimal("-1"))

    @patch("portfolio.models.get_quotes")
    def test_update_market_value_fetches_quote(self, mock_get_quotes):
        mock_get_quotes.return_value = make_quotes(AAPL=200.0)
        holding = self.create_holding(quantity="10", avg_cost="150")

        holding.update_market_value()

        holding.refresh_from_db()
        self.assertEqual(holding.market_value, Decimal("2000.00"))
        mock_get_quotes.assert_called_once_with(["AAPL"])

    @patch("portfolio.models.get_quotes")
    def test_update_market_value_with_given_price_skips_lookup(self, mock_get_quotes):
        holding = self.create_holding(quantity="10")

        holding.update_market_value(210.5)

        holding.refresh_from_db()
        self.assertEqual(holding.market_value, Decimal("2105.00"))
        mock_get_quotes.assert_not_called()

    @patch("portfolio.models.get_quotes")
    def test_update_market_value_keeps_old_value_when_quote_unavailable(self, mock_get_quotes):
        # get_quotes() always returns the symbol as a key, with None when the lookup fails.
        mock_get_quotes.return_value = make_quotes(AAPL=None)
        holding = self.create_holding(market_value="1500")

        holding.update_market_value()

        holding.refresh_from_db()
        self.assertEqual(holding.market_value, Decimal("1500.00"))

    def test_fraction_of_net_worth(self):
        # Net worth = cash (1000) + holdings market value (3000) = 4000.
        self.portfolio.cash = Decimal("1000")
        self.portfolio.save()
        holding = self.create_holding(market_value="3000")

        self.assertEqual(holding.fraction_of_net_worth, Decimal("75"))

    def test_fraction_of_net_worth_is_zero_when_net_worth_is_zero(self):
        holding = self.create_holding(market_value="0")
        self.assertEqual(holding.fraction_of_net_worth, Decimal("0"))

    def test_unrealized_gain(self):
        holding = self.create_holding(quantity="10", avg_cost="150", market_value="1800")
        self.assertEqual(holding.unrealized_gain, Decimal("300"))


class PortfolioCashTests(FinanceTestCase):
    def setUp(self):
        super().setUp()
        self.portfolio = Portfolio.objects.create(user=self.user)

    def test_add_cash(self):
        txn = self.portfolio.add_cash(Decimal("500"))

        self.portfolio.refresh_from_db()
        self.assertEqual(self.portfolio.cash, Decimal("500.00"))
        self.assertEqual(self.portfolio.net_liquidity, Decimal("500.00"))
        self.assertEqual(txn.kind, Transaction.Kind.DEPOSIT)
        self.assertEqual(txn.price, Decimal("500"))

    def test_remove_cash(self):
        self.portfolio.add_cash(Decimal("500"))

        txn = self.portfolio.remove_cash(Decimal("200"))

        self.portfolio.refresh_from_db()
        self.assertEqual(self.portfolio.cash, Decimal("300.00"))
        self.assertEqual(self.portfolio.net_liquidity, Decimal("300.00"))
        self.assertEqual(txn.kind, Transaction.Kind.WITHDRAW)

    def test_remove_cash_rejects_overdraft(self):
        self.portfolio.add_cash(Decimal("100"))
        with self.assertRaises(ValueError):
            self.portfolio.remove_cash(Decimal("100.01"))
        self.portfolio.refresh_from_db()
        self.assertEqual(self.portfolio.cash, Decimal("100.00"))
        self.assertEqual(self.portfolio.transactions.count(), 1)

    def test_cash_amounts_must_be_positive(self):
        with self.assertRaises(ValueError):
            self.portfolio.add_cash(Decimal("0"))
        with self.assertRaises(ValueError):
            self.portfolio.remove_cash(Decimal("-5"))

    def test_add_cash_accepts_int(self):
        self.portfolio.add_cash(250)
        self.portfolio.refresh_from_db()
        self.assertEqual(self.portfolio.cash, Decimal("250.00"))


class PortfolioTradingTests(FinanceTestCase):
    def setUp(self):
        super().setUp()
        self.portfolio = Portfolio.objects.create(user=self.user)
        self.portfolio.add_cash(Decimal("10000"))

    def holding(self, symbol="AAPL"):
        return self.portfolio.holdings.get(symbol=symbol)

    def test_buy_new_holding(self):
        txn = self.portfolio.buy("aapl", Decimal("10"), Decimal("150"), fee=Decimal("1"))

        holding = self.holding()
        self.assertEqual(holding.quantity, Decimal("10"))
        self.assertEqual(holding.avg_cost, Decimal("150"))
        self.assertEqual(holding.cost_basis, Decimal("1500.00"))
        self.assertEqual(holding.market_value, Decimal("1500.00"))

        self.portfolio.refresh_from_db()
        self.assertEqual(self.portfolio.cash, Decimal("8499.00"))
        self.assertEqual(self.portfolio.net_liquidity, Decimal("9999.00"))

        self.assertEqual(txn.kind, Transaction.Kind.BUY)
        self.assertEqual(txn.symbol, "AAPL")
        self.assertEqual(txn.fee, Decimal("1"))

    def test_buy_existing_holding_reaverages_cost(self):
        self.portfolio.buy("AAPL", Decimal("10"), Decimal("150"))
        self.portfolio.buy("AAPL", Decimal("5"), Decimal("160"))

        holding = self.holding()
        self.assertEqual(holding.quantity, Decimal("15"))
        self.assertEqual(holding.avg_cost, Decimal("153.3333"))
        self.assertEqual(self.portfolio.holdings_count, 1)

        self.portfolio.refresh_from_db()
        self.assertEqual(self.portfolio.cash, Decimal("7700.00"))

    def test_buy_rejects_insufficient_cash_and_changes_nothing(self):
        with self.assertRaises(ValueError):
            self.portfolio.buy("AAPL", Decimal("100"), Decimal("150"))

        self.portfolio.refresh_from_db()
        self.assertEqual(self.portfolio.cash, Decimal("10000.00"))
        self.assertFalse(self.portfolio.holdings.exists())
        self.assertFalse(self.portfolio.transactions.filter(kind=Transaction.Kind.BUY).exists())

    def test_buy_fee_counts_toward_insufficient_cash(self):
        with self.assertRaises(ValueError):
            self.portfolio.buy("AAPL", Decimal("100"), Decimal("100"), fee=Decimal("0.01"))

    def test_buy_without_cash_tracks_external_position(self):
        self.portfolio.buy("AAPL", Decimal("10"), Decimal("150"), use_cash=False)

        self.portfolio.refresh_from_db()
        self.assertEqual(self.portfolio.cash, Decimal("10000.00"))
        self.assertEqual(self.portfolio.net_liquidity, Decimal("11500.00"))
        self.assertEqual(self.holding().quantity, Decimal("10"))

    def test_buy_rejects_non_positive_values(self):
        with self.assertRaises(ValueError):
            self.portfolio.buy("AAPL", Decimal("0"), Decimal("150"))
        with self.assertRaises(ValueError):
            self.portfolio.buy("AAPL", Decimal("1"), Decimal("-150"))

    def test_partial_sell(self):
        self.portfolio.buy("AAPL", Decimal("10"), Decimal("150"))

        txn = self.portfolio.sell("AAPL", Decimal("4"), Decimal("200"), fee=Decimal("2"))

        holding = self.holding()
        self.assertEqual(holding.quantity, Decimal("6"))
        self.assertEqual(holding.avg_cost, Decimal("150"))
        self.assertEqual(holding.cost_basis, Decimal("900.00"))
        self.assertEqual(holding.market_value, Decimal("1200.00"))

        self.portfolio.refresh_from_db()
        # 10000 - 1500 + (4 * 200 - 2) = 9298
        self.assertEqual(self.portfolio.cash, Decimal("9298.00"))
        self.assertEqual(self.portfolio.net_liquidity, Decimal("10498.00"))

        self.assertEqual(txn.kind, Transaction.Kind.SELL)
        # Proceeds 798 - cost of sold shares 600 = 198
        self.assertEqual(txn.realized_gain, Decimal("198"))

    def test_selling_everything_deletes_holding(self):
        self.portfolio.buy("AAPL", Decimal("10"), Decimal("150"))

        self.portfolio.sell("AAPL", Decimal("10"), Decimal("140"))

        self.assertFalse(self.portfolio.holdings.exists())
        self.portfolio.refresh_from_db()
        self.assertEqual(self.portfolio.cash, Decimal("9900.00"))
        self.assertEqual(self.portfolio.transactions.get(kind=Transaction.Kind.SELL).realized_gain, Decimal("-100.00"))

    def test_sell_more_than_held_changes_nothing(self):
        self.portfolio.buy("AAPL", Decimal("10"), Decimal("150"))

        with self.assertRaises(ValueError):
            self.portfolio.sell("AAPL", Decimal("11"), Decimal("150"))

        self.assertEqual(self.holding().quantity, Decimal("10"))
        self.portfolio.refresh_from_db()
        self.assertEqual(self.portfolio.cash, Decimal("8500.00"))
        self.assertFalse(self.portfolio.transactions.filter(kind=Transaction.Kind.SELL).exists())

    def test_sell_unknown_symbol(self):
        with self.assertRaises(ValueError):
            self.portfolio.sell("AAPL", Decimal("1"), Decimal("150"))

    def test_sell_symbol_is_case_insensitive(self):
        self.portfolio.buy("AAPL", Decimal("10"), Decimal("150"))
        self.portfolio.sell("aapl", Decimal("1"), Decimal("150"))
        self.assertEqual(self.holding().quantity, Decimal("9"))

    @patch("portfolio.models.get_quotes")
    def test_refresh_market_values_batches_one_lookup(self, mock_get_quotes):
        self.portfolio.buy("AAPL", Decimal("10"), Decimal("150"))
        self.portfolio.buy("MSFT", Decimal("5"), Decimal("400"))
        mock_get_quotes.return_value = make_quotes(AAPL=200.0, MSFT=None)

        self.portfolio.refresh_market_values()

        mock_get_quotes.assert_called_once()
        self.assertCountEqual(mock_get_quotes.call_args.args[0], ["AAPL", "MSFT"])
        self.assertEqual(self.holding("AAPL").market_value, Decimal("2000.00"))
        # No quote for MSFT, so its last known value is kept.
        self.assertEqual(self.holding("MSFT").market_value, Decimal("2000.00"))
        self.portfolio.refresh_from_db()
        # Cash 10000 - 1500 - 2000 = 6500, plus 2000 + 2000.
        self.assertEqual(self.portfolio.net_liquidity, Decimal("10500.00"))


class TransactionModelTests(FinanceTestCase):
    def setUp(self):
        super().setUp()
        self.portfolio = Portfolio.objects.create(user=self.user)
        self.executed_at = datetime(2026, 10, 1, 14, 30, tzinfo=timezone.utc)

    def test_buy_transaction(self):
        txn = Transaction.objects.create(
            portfolio=self.portfolio,
            kind=Transaction.Kind.BUY,
            symbol="AAPL",
            quantity=Decimal("10"),
            price=Decimal("150"),
            executed_at=self.executed_at,
        )
        txn.refresh_from_db()
        self.assertEqual(txn.kind, "BUY")
        self.assertEqual(txn.fee, Decimal("0"))
        self.assertIsNone(txn.realized_gain)
        self.assertEqual(str(txn), "BUY 10.000000 AAPL @ 150.0000")

    def test_cash_transaction_needs_no_symbol_or_quantity(self):
        txn = Transaction(portfolio=self.portfolio, kind=Transaction.Kind.DEPOSIT, price=Decimal("500"))
        txn.full_clean()
        txn.save()
        self.assertEqual(txn.symbol, "")
        self.assertIsNone(txn.quantity)

    def test_executed_at_defaults_to_now(self):
        txn = Transaction.objects.create(portfolio=self.portfolio, kind=Transaction.Kind.DEPOSIT, price=Decimal("1"))
        self.assertIsNotNone(txn.executed_at)

    def test_invalid_kind_is_rejected(self):
        txn = Transaction(portfolio=self.portfolio, kind="GIFT", executed_at=self.executed_at)
        with self.assertRaises(ValidationError):
            txn.full_clean()

    def test_newest_first(self):
        older = Transaction.objects.create(
            portfolio=self.portfolio, kind=Transaction.Kind.DEPOSIT, price=Decimal("1"),
            executed_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        newer = Transaction.objects.create(
            portfolio=self.portfolio, kind=Transaction.Kind.DEPOSIT, price=Decimal("1"),
            executed_at=self.executed_at,
        )
        self.assertEqual(list(self.portfolio.transactions.all()), [newer, older])

    def test_deleting_portfolio_deletes_transactions(self):
        Transaction.objects.create(portfolio=self.portfolio, kind=Transaction.Kind.DEPOSIT, price=Decimal("100"))
        self.portfolio.delete()
        self.assertFalse(Transaction.objects.exists())


class PortfolioViewTests(FinanceTestCase):
    HTMX = {"HTTP_HX_REQUEST": "true"}

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)
        self.portfolio = Portfolio.objects.create(user=self.user, name="Main")
        self.portfolio.add_cash(Decimal("10000"))
        self.other_user = self.create_user("other@example.com")
        self.other_portfolio = Portfolio.objects.create(user=self.other_user, name="Theirs")

    def url(self, name, portfolio=None):
        return reverse(f"portfolio:{name}", args=[(portfolio or self.portfolio).pk])

    def test_pages_require_login(self):
        self.client.logout()
        for url in [reverse("portfolio:dashboard"), self.url("detail"), self.url("settings")]:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn(reverse("account:login"), response.url)

    def test_dashboard_lists_only_own_portfolios(self):
        response = self.client.get(reverse("portfolio:dashboard"))
        self.assertContains(response, "Main")
        self.assertNotContains(response, "Theirs")

    def test_create_portfolio(self):
        response = self.client.post(reverse("portfolio:dashboard"), {"name": "Retirement", "currency": "cad"})
        created = Portfolio.objects.get(name="Retirement")
        self.assertRedirects(response, self.url("detail", created))
        self.assertEqual(created.user, self.user)
        self.assertEqual(created.currency, "CAD")
        self.assertFalse(created.is_public)

    def test_detail_shows_holdings(self):
        self.portfolio.buy("AAPL", Decimal("10"), Decimal("150"))
        response = self.client.get(self.url("detail"))
        self.assertContains(response, "AAPL")
        self.assertContains(response, "$8,500.00")

    def test_other_users_portfolio_is_not_found(self):
        self.assertEqual(self.client.get(self.url("detail", self.other_portfolio)).status_code, 404)
        self.assertEqual(self.client.get(self.url("settings", self.other_portfolio)).status_code, 404)
        response = self.client.post(self.url("cash", self.other_portfolio), {"action": "DEPOSIT", "amount": "5"})
        self.assertEqual(response.status_code, 404)
        self.other_portfolio.refresh_from_db()
        self.assertEqual(self.other_portfolio.cash, Decimal("0"))

    def test_actions_reject_get(self):
        for name in ["trade", "cash", "refresh", "delete"]:
            self.assertEqual(self.client.get(self.url(name)).status_code, 405)

    def test_buy_via_htmx_returns_body_partial(self):
        response = self.client.post(
            self.url("trade"),
            {"side": "BUY", "symbol": "aapl", "quantity": "10", "price": "150", "fee": "", "use_cash": "on"},
            **self.HTMX,
        )
        self.assertTemplateUsed(response, "portfolio/_portfolio_body.html")
        self.assertTemplateNotUsed(response, "portfolio/detail.html")
        self.assertContains(response, "Bought 10 AAPL at $150.00.")
        self.portfolio.refresh_from_db()
        self.assertEqual(self.portfolio.cash, Decimal("8500.00"))

    def test_buy_without_pay_from_cash_keeps_cash(self):
        self.client.post(self.url("trade"), {"side": "BUY", "symbol": "AAPL", "quantity": "10", "price": "150"}, **self.HTMX)
        self.portfolio.refresh_from_db()
        self.assertEqual(self.portfolio.cash, Decimal("10000.00"))
        self.assertEqual(self.portfolio.holdings.get().quantity, Decimal("10"))

    def test_buy_with_insufficient_cash_shows_error(self):
        response = self.client.post(
            self.url("trade"),
            {"side": "BUY", "symbol": "AAPL", "quantity": "1000", "price": "150", "use_cash": "on"},
            **self.HTMX,
        )
        self.assertContains(response, "Insufficient cash in portfolio.")
        self.assertFalse(self.portfolio.holdings.exists())

    def test_invalid_trade_form_shows_field_errors(self):
        response = self.client.post(
            self.url("trade"), {"side": "BUY", "symbol": "AA PL", "quantity": "-1", "price": "150"}, **self.HTMX,
        )
        self.assertContains(response, "Use letters, numbers, dots or dashes")
        self.assertContains(response, "greater than or equal to")
        self.assertFalse(self.portfolio.holdings.exists())

    def test_sell(self):
        self.portfolio.buy("AAPL", Decimal("10"), Decimal("150"))
        response = self.client.post(
            self.url("trade"), {"side": "SELL", "symbol": "AAPL", "quantity": "4", "price": "200"}, **self.HTMX,
        )
        self.assertContains(response, "Sold 4 AAPL at $200.00.")
        self.assertEqual(self.portfolio.holdings.get().quantity, Decimal("6"))

    def test_sell_unknown_symbol_shows_error(self):
        response = self.client.post(
            self.url("trade"), {"side": "SELL", "symbol": "MSFT", "quantity": "1", "price": "200"}, **self.HTMX,
        )
        self.assertContains(response, "No MSFT holding to sell.")

    def test_deposit_without_htmx_redirects_with_message(self):
        response = self.client.post(self.url("cash"), {"action": "DEPOSIT", "amount": "250.50"}, follow=True)
        self.assertRedirects(response, self.url("detail"))
        self.assertContains(response, "Deposited $250.50.")
        self.portfolio.refresh_from_db()
        self.assertEqual(self.portfolio.cash, Decimal("10250.50"))

    def test_withdraw_overdraft_shows_error(self):
        response = self.client.post(self.url("cash"), {"action": "WITHDRAW", "amount": "20000"}, **self.HTMX)
        self.assertContains(response, "Insufficient cash in portfolio.")
        self.portfolio.refresh_from_db()
        self.assertEqual(self.portfolio.cash, Decimal("10000.00"))

    def test_failed_trade_without_htmx_renders_full_page_with_errors(self):
        response = self.client.post(self.url("trade"), {"side": "SELL", "symbol": "MSFT", "quantity": "1", "price": "1"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "portfolio/detail.html")
        self.assertContains(response, "No MSFT holding to sell.")

    @patch("portfolio.models.get_quotes")
    def test_refresh_prices(self, mock_get_quotes):
        self.portfolio.buy("AAPL", Decimal("10"), Decimal("150"))
        mock_get_quotes.return_value = make_quotes(AAPL=200.0)

        response = self.client.post(self.url("refresh"), **self.HTMX)

        self.assertContains(response, "Prices refreshed.")
        self.assertEqual(self.portfolio.holdings.get().market_value, Decimal("2000.00"))

    def test_settings_update(self):
        response = self.client.post(self.url("settings"), {"name": "Long term", "is_public": "on"})
        self.assertRedirects(response, self.url("detail"))
        self.portfolio.refresh_from_db()
        self.assertEqual(self.portfolio.name, "Long term")
        self.assertTrue(self.portfolio.is_public)

    def test_delete(self):
        response = self.client.post(self.url("delete"))
        self.assertRedirects(response, reverse("portfolio:dashboard"))
        self.assertFalse(Portfolio.objects.filter(pk=self.portfolio.pk).exists())

    def test_cannot_delete_other_users_portfolio(self):
        self.assertEqual(self.client.post(self.url("delete", self.other_portfolio)).status_code, 404)
        self.assertTrue(Portfolio.objects.filter(pk=self.other_portfolio.pk).exists())
