from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CashForm, PortfolioForm, PortfolioSettingsForm, TradeForm
from .models import Portfolio, Transaction

RECENT_TRANSACTIONS = 10
DETAIL_URL = "portfolio:detail"


def _trim(value):
    """10.000000 -> "10", 2.500000 -> "2.5"; share counts read better without padding."""
    return f"{value.normalize():f}" if value is not None else ""


def _get_portfolio(request, pk):
    # Scoped to the owner so one user can never view or trade another user's portfolio.
    return get_object_or_404(Portfolio, pk=pk, user=request.user)


def _body_context(portfolio, trade_form=None, cash_form=None, notice=None):
    holdings = list(portfolio.holdings.order_by("-market_value", "symbol"))
    market_value = sum((holding.market_value for holding in holdings), Decimal("0"))
    cost_basis = sum((holding.cost_basis for holding in holdings), Decimal("0"))
    net_liquidity = portfolio.cash + market_value

    for holding in holdings:
        holding.display_quantity = _trim(holding.quantity)
        holding.weight = holding.market_value / net_liquidity * 100 if net_liquidity else Decimal("0")
        holding.gain_pct = holding.unrealized_gain / holding.cost_basis * 100 if holding.cost_basis else Decimal("0")

    transactions = list(portfolio.transactions.all()[:RECENT_TRANSACTIONS])
    for txn in transactions:
        txn.display_quantity = _trim(txn.quantity)
        # Trades store a per-share price; cash movements store the amount itself in price.
        txn.amount = txn.quantity * txn.price if txn.quantity is not None else txn.price

    realized = portfolio.transactions.filter(kind=Transaction.Kind.SELL).aggregate(total=Sum("realized_gain"))["total"]
    unrealized = market_value - cost_basis

    return {
        "portfolio": portfolio,
        "holdings": holdings,
        "transactions": transactions,
        "net_liquidity": net_liquidity,
        "market_value": market_value,
        "cost_basis": cost_basis,
        "unrealized_gain": unrealized,
        "unrealized_pct": unrealized / cost_basis * 100 if cost_basis else Decimal("0"),
        "realized_gain": realized or Decimal("0"),
        "cash_pct": portfolio.cash / net_liquidity * 100 if net_liquidity else Decimal("0"),
        "trade_form": trade_form or TradeForm(),
        "cash_form": cash_form or CashForm(),
        "notice": notice,
    }


def _respond(request, portfolio, notice=None, **forms):
    """HTMX requests get the refreshed body partial; plain form posts get a full page."""
    context = _body_context(portfolio, notice=notice, **forms)
    if request.htmx:
        return render(request, "portfolio/_portfolio_body.html", context)
    if notice and not forms:
        messages.success(request, notice)
        return redirect(DETAIL_URL, portfolio.pk)
    return render(request, "portfolio/detail.html", context)


@login_required
def dashboard(request):
    form = PortfolioForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        portfolio = form.save(commit=False)
        portfolio.user = request.user
        portfolio.save()
        messages.success(request, f"Created {portfolio.name}. Deposit some cash to start trading.")
        return redirect(DETAIL_URL, portfolio.pk)

    portfolios = request.user.portfolios.annotate(num_holdings=Count("holdings")).order_by("created_at")
    context = {
        "portfolios": portfolios,
        "form": form,
        "total_net_liquidity": sum((p.net_liquidity for p in portfolios), Decimal("0")),
        "total_cash": sum((p.cash for p in portfolios), Decimal("0")),
    }
    return render(request, "portfolio/dashboard.html", context)


@login_required
def detail(request, pk):
    portfolio = _get_portfolio(request, pk)
    return render(request, "portfolio/detail.html", _body_context(portfolio))


@login_required
@require_POST
def trade(request, pk):
    portfolio = _get_portfolio(request, pk)
    form = TradeForm(request.POST)
    if not form.is_valid():
        return _respond(request, portfolio, trade_form=form)

    data = form.cleaned_data
    try:
        if data["side"] == "BUY":
            portfolio.buy(data["symbol"], data["quantity"], data["price"], fee=data["fee"], use_cash=data["use_cash"])
        else:
            portfolio.sell(data["symbol"], data["quantity"], data["price"], fee=data["fee"])
    except ValueError as exc:
        form.add_error(None, str(exc))
        return _respond(request, portfolio, trade_form=form)

    verb = "Bought" if data["side"] == "BUY" else "Sold"
    return _respond(request, portfolio, notice=f"{verb} {_trim(data['quantity'])} {data['symbol']} at ${data['price']:,.2f}.")


@login_required
@require_POST
def cash(request, pk):
    portfolio = _get_portfolio(request, pk)
    form = CashForm(request.POST)
    if not form.is_valid():
        return _respond(request, portfolio, cash_form=form)

    amount = form.cleaned_data["amount"]
    try:
        if form.cleaned_data["action"] == "DEPOSIT":
            portfolio.add_cash(amount)
        else:
            portfolio.remove_cash(amount)
    except ValueError as exc:
        form.add_error(None, str(exc))
        return _respond(request, portfolio, cash_form=form)

    verb = "Deposited" if form.cleaned_data["action"] == "DEPOSIT" else "Withdrew"
    return _respond(request, portfolio, notice=f"{verb} ${amount:,.2f}.")


@login_required
@require_POST
def refresh_prices(request, pk):
    portfolio = _get_portfolio(request, pk)
    portfolio.refresh_market_values()
    return _respond(request, portfolio, notice="Prices refreshed.")


@login_required
def settings(request, pk):
    portfolio = _get_portfolio(request, pk)
    form = PortfolioSettingsForm(request.POST or None, instance=portfolio)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Portfolio settings saved.")
        return redirect(DETAIL_URL, portfolio.pk)
    return render(request, "portfolio/settings.html", {"portfolio": portfolio, "form": form})


@login_required
@require_POST
def delete(request, pk):
    portfolio = _get_portfolio(request, pk)
    name = portfolio.name
    portfolio.delete()
    messages.success(request, f"Deleted {name}.")
    return redirect("portfolio:dashboard")
