from dataclasses import dataclass, field
from decimal import Decimal

ASSET_TYPE_CHOICES = [
    ("STOCK", "Stock"),
    ("ETF", "ETF"),
    ("CRYPTO", "Crypto"),
    ("BOND", "Bond"),
    ("CASH", "Cash"),
    ("OTHER", "Other"),
]
ASSET_TYPE_LABELS = dict(ASSET_TYPE_CHOICES)


@dataclass
class Holding:
    id: str
    symbol: str
    name: str
    asset_type: str
    quantity: Decimal
    cost_basis_per_unit: Decimal
    current_price: Decimal

    def get_asset_type_display(self):
        return ASSET_TYPE_LABELS.get(self.asset_type, self.asset_type)

    @property
    def market_value(self):
        return self.quantity * self.current_price

    @property
    def total_cost(self):
        return self.quantity * self.cost_basis_per_unit

    @property
    def gain_loss(self):
        return self.market_value - self.total_cost

    @property
    def gain_loss_pct(self):
        if self.total_cost == 0:
            return Decimal("0")
        return (self.gain_loss / self.total_cost) * 100


@dataclass
class Portfolio:
    uid: str
    name: str
    holdings: list = field(default_factory=list)

    @property
    def total_value(self):
        return sum((h.market_value for h in self.holdings), Decimal("0"))

    @property
    def total_cost(self):
        return sum((h.total_cost for h in self.holdings), Decimal("0"))

    @property
    def total_gain_loss(self):
        return self.total_value - self.total_cost

    @property
    def total_gain_loss_pct(self):
        if self.total_cost == 0:
            return Decimal("0")
        return (self.total_gain_loss / self.total_cost) * 100
