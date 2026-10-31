from decimal import Decimal

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

from portfolio.market import get_quotes


def to_decimal(value):
    # str() first so floats from the quote API don't carry binary noise (0.1 -> 0.1000000000000000055...).
    return value if isinstance(value, Decimal) else Decimal(str(value))


def require_positive(**values):
    for name, value in values.items():
        if value <= 0:
            raise ValueError(f"{name} must be positive.")


class Portfolio(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="portfolios")
    name = models.CharField(max_length=100, default="Main")
    cash = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="USD")
    # Snapshot of cash + holdings' market value, refreshed whenever either changes.
    net_liquidity = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def holdings_count(self):
        return self.holdings.count()

    def calculate_net_liquidity(self):
        return self.cash + sum((holding.market_value for holding in self.holdings.all()), Decimal("0"))

    def update_net_liquidity(self):
        self.net_liquidity = self.calculate_net_liquidity()
        self.save(update_fields=["net_liquidity"])

    def _lock(self):
        """Lock this portfolio's row for the rest of the transaction and reload its cash,
        so two simultaneous trades can't both spend the same money."""
        self.cash = Portfolio.objects.select_for_update().values_list("cash", flat=True).get(pk=self.pk)

    def _finish(self):
        self.net_liquidity = self.calculate_net_liquidity()
        self.save(update_fields=["cash", "net_liquidity"])

    def add_cash(self, amount, executed_at=None):
        amount = to_decimal(amount)
        require_positive(amount=amount)
        with transaction.atomic():
            self._lock()
            self.cash += amount
            self._finish()
            return self.transactions.create(
                kind=Transaction.Kind.DEPOSIT, price=amount, executed_at=executed_at or timezone.now(),
            )

    def remove_cash(self, amount, executed_at=None):
        amount = to_decimal(amount)
        require_positive(amount=amount)
        with transaction.atomic():
            self._lock()
            if amount > self.cash:
                raise ValueError("Insufficient cash in portfolio.")
            self.cash -= amount
            self._finish()
            return self.transactions.create(
                kind=Transaction.Kind.WITHDRAW, price=amount, executed_at=executed_at or timezone.now(),
            )

    def buy(self, symbol, quantity, price, fee=0, executed_at=None, use_cash=True):
        """Buy shares, re-averaging the cost if the symbol is already held.

        use_cash=False records a position bought outside the app without touching cash.
        """
        symbol = symbol.upper().strip()
        quantity, price, fee = to_decimal(quantity), to_decimal(price), to_decimal(fee)
        require_positive(quantity=quantity, price=price)

        with transaction.atomic():
            self._lock()
            cost = quantity * price + fee
            if use_cash:
                if cost > self.cash:
                    raise ValueError("Insufficient cash in portfolio.")
                self.cash -= cost

            holding, _ = Holding.objects.select_for_update().get_or_create(portfolio=self, symbol=symbol)
            holding.add_shares(quantity, price)
            # The trade price is the freshest price we have; refresh_market_values() updates it later.
            holding.market_value = holding.quantity * price
            holding.save()

            self._finish()
            return self.transactions.create(
                kind=Transaction.Kind.BUY, symbol=symbol, quantity=quantity, price=price, fee=fee,
                executed_at=executed_at or timezone.now(),
            )

    def sell(self, symbol, quantity, price, fee=0, executed_at=None):
        """Sell shares and record the realized gain against the average cost."""
        symbol = symbol.upper().strip()
        quantity, price, fee = to_decimal(quantity), to_decimal(price), to_decimal(fee)
        require_positive(quantity=quantity, price=price)

        with transaction.atomic():
            self._lock()
            try:
                holding = self.holdings.select_for_update().get(symbol=symbol)
            except Holding.DoesNotExist:
                raise ValueError(f"No {symbol} holding to sell.")

            cost_of_sold = holding.remove_shares(quantity)
            proceeds = quantity * price - fee
            self.cash += proceeds

            if holding.quantity == 0:
                holding.delete()
            else:
                holding.market_value = holding.quantity * price
                holding.save()

            self._finish()
            return self.transactions.create(
                kind=Transaction.Kind.SELL, symbol=symbol, quantity=quantity, price=price, fee=fee,
                realized_gain=proceeds - cost_of_sold, executed_at=executed_at or timezone.now(),
            )

    def refresh_market_values(self):
        """Reprice every holding with one batched quote lookup."""
        holdings = list(self.holdings.all())
        quotes = get_quotes([holding.symbol for holding in holdings])
        for holding in holdings:
            quote = quotes.get(holding.symbol)
            if quote:
                holding.update_market_value(quote["price"])
        self.update_net_liquidity()

    def __str__(self):
        return f"{self.name} ({self.user}, {self.currency})"


class Holding(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="holdings")
    symbol = models.CharField(max_length=12)
    quantity = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    avg_cost = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    # Always quantity * avg_cost; kept in sync by save().
    cost_basis = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    market_value = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    @property
    def fraction_of_net_worth(self):
        '''
        Calculates the fraction of the portfolio's net worth that this holding represents.
        '''
        net_worth = self.portfolio.calculate_net_liquidity()
        if net_worth == 0:
            return Decimal("0")
        return self.market_value / net_worth * 100

    @property
    def unrealized_gain(self):
        return self.market_value - self.cost_basis

    def add_shares(self, quantity, price):
        '''
        Adds shares and re-averages the cost. Does not save; the caller saves once when done.
        '''
        quantity, price = to_decimal(quantity), to_decimal(price)
        require_positive(quantity=quantity, price=price)
        total = self.quantity + quantity
        self.avg_cost = (self.avg_cost * self.quantity + price * quantity) / total
        self.quantity = total

    def remove_shares(self, quantity):
        '''
        Removes shares and returns their cost basis, for realized-gain maths.
        The average cost doesn't change on a sell. Does not save.
        '''
        quantity = to_decimal(quantity)
        require_positive(quantity=quantity)
        if quantity > self.quantity:
            raise ValueError(f"Cannot sell {quantity} {self.symbol}; only {self.quantity} held.")
        self.quantity -= quantity
        return quantity * self.avg_cost

    def update_market_value(self, price=None):
        '''
        Reprices the holding. Fetches a quote when no price is given; keeps the old value if none is available.
        '''
        if price is None:
            quote = get_quotes([self.symbol]).get(self.symbol)
            if not quote:
                return
            price = quote["price"]
        self.market_value = self.quantity * to_decimal(price)
        self.save(update_fields=["market_value"])

    def save(self, *args, **kwargs):
        self.symbol = self.symbol.upper().strip()
        self.cost_basis = self.quantity * self.avg_cost
        update_fields = kwargs.get("update_fields")
        if update_fields is not None and {"quantity", "avg_cost"} & set(update_fields):
            kwargs["update_fields"] = {*update_fields, "cost_basis"}
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.symbol} - {self.quantity} shares at ${self.avg_cost:.2f} each"

    class Meta:
        unique_together = ("portfolio", "symbol")
        indexes = [models.Index(fields=["portfolio", "symbol"])]


class Transaction(models.Model):
    class Kind(models.TextChoices):
        BUY = "BUY"; SELL = "SELL"; DEPOSIT = "DEPOSIT"; WITHDRAW = "WITHDRAW"
        DIVIDEND = "DIVIDEND"; FEE = "FEE"; SPLIT = "SPLIT"
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="transactions")
    kind = models.CharField(max_length=10, choices=Kind.choices)
    symbol = models.CharField(max_length=12, blank=True)
    quantity = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
    # Per-share price for trades; the cash amount for deposits and withdrawals.
    price = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    executed_at = models.DateTimeField(default=timezone.now)
    realized_gain = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    def __str__(self):
        if self.symbol:
            return f"{self.kind} {self.quantity} {self.symbol} @ {self.price}"
        return f"{self.kind} {self.price}"

    class Meta:
        ordering = ["-executed_at"]
        indexes = [
            models.Index(fields=["portfolio", "executed_at"]),
            models.Index(fields=["symbol"]),
        ]
