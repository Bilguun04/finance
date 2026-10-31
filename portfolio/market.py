import json
import logging
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, time
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

FINNHUB_BASE_URL = "https://finnhub.io/api/v1"
# Also used as the landing page's HTMX refresh interval.
QUOTE_CACHE_SECONDS = 120
# Prices barely move outside regular trading hours, so cache them longer to save API calls.
OFF_HOURS_QUOTE_CACHE_SECONDS = 900
HOLIDAY_CACHE_SECONDS = 24 * 60 * 60

# US market sessions, Eastern Time.
MARKET_TZ = ZoneInfo("America/New_York")
PRE_MARKET_OPEN = time(4, 0)
MARKET_OPEN = time(9, 30)
MARKET_CLOSE = time(16, 0)
AFTER_HOURS_CLOSE = time(20, 0)

MARKET_STATE_LABELS = {
    "pre_market": "Pre-market",
    "open": "Market open",
    "after_hours": "After-hours",
    "overnight": "Overnight",
    "closed": "Market closed",
}


def _get(endpoint, **params):
    params["token"] = settings.FINNHUB_API_KEY
    url = f"{FINNHUB_BASE_URL}/{endpoint}?{urlencode(params)}"
    with urlopen(url, timeout=5) as response:
        return json.loads(response.read())


def get_quote(symbol, cache_seconds=QUOTE_CACHE_SECONDS):
    """Return the latest quote for a symbol, or None if unavailable.

    Keys: price, change, change_pct, high, low, open, prev_close.
    """
    symbol = symbol.upper()
    cache_key = f"finnhub:quote:{symbol}"
    quote = cache.get(cache_key)
    if quote is not None:
        return quote

    try:
        data = _get("quote", symbol=symbol)
    except (URLError, TimeoutError, ValueError) as exc:
        logger.warning("Finnhub quote failed for %s: %s", symbol, exc)
        return None

    # Finnhub returns all zeros for unknown symbols.
    if not data.get("c"):
        return None

    quote = {
        "price": data["c"],
        "change": data["d"],
        "change_pct": data["dp"],
        "high": data["h"],
        "low": data["l"],
        "open": data["o"],
        "prev_close": data["pc"],
    }
    cache.set(cache_key, quote, cache_seconds)
    return quote


def get_quotes(symbols):
    """Fetch several quotes in parallel. Returns {symbol: quote or None}."""
    if get_market_status()["state"] == "open":
        cache_seconds = QUOTE_CACHE_SECONDS
    else:
        cache_seconds = OFF_HOURS_QUOTE_CACHE_SECONDS

    with ThreadPoolExecutor(max_workers=8) as pool:
        quotes = pool.map(lambda symbol: get_quote(symbol, cache_seconds), symbols)
        return dict(zip(symbols, quotes))


def get_market_holidays():
    """Return US market holidays as {date: {"name", "close", "after_close"}}.

    "close" and "after_close" are None when the market is shut all day,
    or the early-close times on half days.
    """
    holidays = cache.get("finnhub:market-holidays")
    if holidays is not None:
        return holidays

    try:
        data = _get("stock/market-holiday", exchange="US")
    except (URLError, TimeoutError, ValueError) as exc:
        logger.warning("Finnhub market holidays failed: %s", exc)
        return {}

    holidays = {}
    for holiday in data.get("data", []):
        # Times look like "09:30-13:00"; Finnhub sometimes uses ":" as the separator.
        trading = re.findall(r"\d{1,2}:\d{2}", holiday.get("tradingHour") or "")
        post_market = re.findall(r"\d{1,2}:\d{2}", holiday.get("postMarket") or "")
        holidays[date.fromisoformat(holiday["atDate"])] = {
            "name": holiday["eventName"],
            "close": time.fromisoformat(trading[-1]) if trading else None,
            "after_close": time.fromisoformat(post_market[-1]) if post_market else None,
        }

    cache.set("finnhub:market-holidays", holidays, HOLIDAY_CACHE_SECONDS)
    return holidays


def _is_weekend_close(weekday, clock, after_close):
    """True from Friday's after-hours close until overnight trading starts Sunday evening."""
    return (
        weekday == 5
        or (weekday == 4 and clock >= after_close)
        or (weekday == 6 and clock < AFTER_HOURS_CLOSE)
    )


def get_market_status(now=None):
    """Return the current US market session as {"state", "label", "holiday"}.

    Weekdays run pre-market, regular session, after-hours, then overnight.
    The market is closed from Friday's after-hours close until Sunday evening,
    and on full-day holidays.
    """
    now = (now or datetime.now(MARKET_TZ)).astimezone(MARKET_TZ)
    clock = now.time()
    holiday = get_market_holidays().get(now.date()) or {}

    close = holiday.get("close") or MARKET_CLOSE
    after_close = holiday.get("after_close") or AFTER_HOURS_CLOSE

    # now.weekday(): Monday is 0
    if _is_weekend_close(now.weekday(), clock, after_close) or (holiday and not holiday["close"]):
        state = "closed"
    elif PRE_MARKET_OPEN <= clock < MARKET_OPEN:
        state = "pre_market"
    elif MARKET_OPEN <= clock < close:
        state = "open"
    elif close <= clock < after_close:
        state = "after_hours"
    else:
        state = "overnight"

    return {
        "state": state,
        "label": MARKET_STATE_LABELS[state],
        "holiday": holiday.get("name"),
    }
