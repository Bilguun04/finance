from decimal import Decimal

from .dataclasses import Holding as HoldingData
from .dataclasses import Portfolio as PortfolioData
from .models import Holding, Portfolio


def _holding_data(holding):
    return HoldingData(
        id=str(holding.id),
        symbol=holding.symbol,
        name=holding.name,
        asset_type=holding.asset_type,
        quantity=holding.quantity,
        cost_basis_per_unit=holding.cost_basis_per_unit,
        current_price=holding.current_price,
    )


def _portfolio_data(portfolio):
    return PortfolioData(
        uid=portfolio.user_id,
        name=portfolio.name,
        holdings=[_holding_data(holding) for holding in portfolio.holdings.all()],
    )


def get_or_create_portfolio(user_id, name="My Portfolio"):
    portfolio, _ = Portfolio.objects.get_or_create(user_id=user_id, defaults={"name": name})
    return _portfolio_data(portfolio)


def _portfolio_for_user(user_id):
    portfolio, _ = Portfolio.objects.get_or_create(user_id=user_id)
    return portfolio


def get_holding(user_id, holding_id):
    try:
        holding = Holding.objects.get(id=holding_id, portfolio__user_id=user_id)
    except Holding.DoesNotExist:
        return None
    return _holding_data(holding)


def add_holding(user_id, data):
    holding = Holding.objects.create(portfolio=_portfolio_for_user(user_id), **data)
    return _holding_data(holding)


def update_holding(user_id, holding_id, data):
    Holding.objects.filter(id=holding_id, portfolio__user_id=user_id).update(**data)
    return get_holding(user_id, holding_id)


def delete_holding(user_id, holding_id):
    Holding.objects.filter(id=holding_id, portfolio__user_id=user_id).delete()