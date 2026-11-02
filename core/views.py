import finnhub

from portfolio.market import QUOTE_CACHE_SECONDS, get_market_status, get_quotes

from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

import os
from dotenv import load_dotenv

load_dotenv()

finnhub_client = finnhub.Client(api_key=os.getenv("FINNHUB_API_KEY"))

# Finnhub's free tier has no raw index data, so indexes are shown via the ETFs that track them.
MARKET_INDEXES = [
    ("SPY", "S&P 500"),
    ("QQQ", "Nasdaq 100"),
    ("DIA", "Dow Jones"),
    ("IWM", "Russell 2000"),
]
MARKET_STOCKS = [
    ("AAPL", "Apple"),
    ("MSFT", "Microsoft"),
    ("NVDA", "Nvidia"),
    ("AMZN", "Amazon"),
    ("GOOGL", "Alphabet"),
    ("META", "Meta"),
    ("TSLA", "Tesla"),
]
MOVERS_COUNT = 3


def _market_context():
    market_status = get_market_status()
    # Quote changes are against the previous close, so outside today's sessions they describe the last session.
    if market_status["state"] in ("open", "after_hours"):
        change_label = "today"
    else:
        change_label = "last session"
    return {"market_status": market_status, "change_label": change_label}


def index(request):
    if request.user.is_authenticated:
        return redirect("portfolio:dashboard")
    context = {"refresh_seconds": QUOTE_CACHE_SECONDS, **_market_context()}
    return render(request, "core/landing.html", context)


def market_snapshot(request):
    quotes = get_quotes([symbol for symbol, _ in MARKET_INDEXES + MARKET_STOCKS])

    def range_pct(quote):
        # Where the current price sits within today's low–high range, 0–100.
        if not quote or quote["high"] <= quote["low"]:
            return 50
        return (quote["price"] - quote["low"]) / (quote["high"] - quote["low"]) * 100

    def rows(tickers):
        return [
            {"symbol": symbol, "name": name, "quote": quotes[symbol], "range_pct": range_pct(quotes[symbol])}
            for symbol, name in tickers
        ]

    context = {"indexes": rows(MARKET_INDEXES), "stocks": rows(MARKET_STOCKS), **_market_context()}
    return render(request, "core/_market_snapshot.html", context)


def market_pulse(request):
    quotes = get_quotes([symbol for symbol, _ in MARKET_INDEXES + MARKET_STOCKS])

    headline_symbol, headline_name = MARKET_INDEXES[0]
    indexes = [
        {"symbol": symbol, "name": name, "quote": quotes[symbol]}
        for symbol, name in MARKET_INDEXES[1:]
    ]

    stocks = [
        {"symbol": symbol, "name": name, "quote": quotes[symbol]}
        for symbol, name in MARKET_STOCKS
        if quotes[symbol]
    ]
    stocks.sort(key=lambda s: s["quote"]["change_pct"], reverse=True)

    # Bar lengths are relative to the biggest move of the day.
    biggest_move = max((abs(s["quote"]["change_pct"]) for s in stocks), default=0)
    for stock in stocks:
        stock["bar_pct"] = abs(stock["quote"]["change_pct"]) / biggest_move * 100 if biggest_move else 0

    context = {
        "headline": {"symbol": headline_symbol, "name": headline_name, "quote": quotes[headline_symbol]},
        "indexes": indexes,
        "gainers": [s for s in stocks if s["quote"]["change_pct"] > 0][:MOVERS_COUNT],
        "losers": [s for s in reversed(stocks) if s["quote"]["change_pct"] < 0][:MOVERS_COUNT],
        **_market_context(),
    }
    return render(request, "core/_market_pulse.html", context)

