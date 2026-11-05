import { FINNHUB_API_KEY } from '$app/env/private';
import { changeLabel, marketStatusAt, parseClock, type Holidays } from '#lib/market-status.ts';
import type { MarketPulse, MarketSnapshot, MarketStatus, Quote, Ticker } from '#lib/types.ts';

const FINNHUB_BASE_URL = 'https://finnhub.io/api/v1';
/** Also used as the landing page's refresh interval. */
export const QUOTE_CACHE_SECONDS = 120;
// Prices barely move outside regular trading hours, so cache them longer to save API calls.
const OFF_HOURS_QUOTE_CACHE_SECONDS = 900;
const HOLIDAY_CACHE_SECONDS = 24 * 60 * 60;

// Finnhub's free tier has no raw index data, so indexes are shown via the ETFs that track them.
const MARKET_INDEXES: [string, string][] = [
	['SPY', 'S&P 500'],
	['QQQ', 'Nasdaq 100'],
	['DIA', 'Dow Jones'],
	['IWM', 'Russell 2000']
];
const MARKET_STOCKS: [string, string][] = [
	['AAPL', 'Apple'],
	['MSFT', 'Microsoft'],
	['NVDA', 'Nvidia'],
	['AMZN', 'Amazon'],
	['GOOGL', 'Alphabet'],
	['META', 'Meta'],
	['TSLA', 'Tesla']
];
const MOVERS_COUNT = 3;

// Per-instance cache, the equivalent of Django's default local-memory cache.
const cache = new Map<string, { value: unknown; expires: number }>();

function cached<T>(key: string): T | undefined {
	const entry = cache.get(key);
	if (!entry) return undefined;
	if (entry.expires < Date.now()) {
		cache.delete(key);
		return undefined;
	}
	return entry.value as T;
}

function store(key: string, value: unknown, seconds: number) {
	cache.set(key, { value, expires: Date.now() + seconds * 1000 });
}

type FinnhubQuote = {
	c: number;
	d: number;
	dp: number;
	h: number;
	l: number;
	o: number;
	pc: number;
};
type FinnhubHolidays = {
	data?: { atDate: string; eventName: string; tradingHour?: string; postMarket?: string }[];
};

async function finnhub<T>(endpoint: string, params: Record<string, string>): Promise<T> {
	const query = new URLSearchParams({ ...params, token: FINNHUB_API_KEY });
	const response = await fetch(`${FINNHUB_BASE_URL}/${endpoint}?${query}`, {
		signal: AbortSignal.timeout(5000)
	});
	if (!response.ok) throw new Error(`HTTP ${response.status}`);
	return (await response.json()) as T;
}

/** The latest quote for a symbol, or null if unavailable. */
export async function getQuote(
	symbol: string,
	cacheSeconds = QUOTE_CACHE_SECONDS
): Promise<Quote | null> {
	symbol = symbol.toUpperCase();
	const key = `finnhub:quote:${symbol}`;
	const hit = cached<Quote>(key);
	if (hit) return hit;

	let data: FinnhubQuote;
	try {
		data = await finnhub<FinnhubQuote>('quote', { symbol });
	} catch (error) {
		console.warn(`Finnhub quote failed for ${symbol}:`, error);
		return null;
	}

	// Finnhub returns all zeros for unknown symbols.
	if (!data?.c) return null;

	const quote: Quote = {
		price: data.c,
		change: data.d,
		changePct: data.dp,
		high: data.h,
		low: data.l,
		open: data.o,
		prevClose: data.pc
	};
	store(key, quote, cacheSeconds);
	return quote;
}

/** Fetches several quotes in parallel. */
export async function getQuotes(symbols: string[]): Promise<Record<string, Quote | null>> {
	const status = await getMarketStatus();
	const seconds = status.state === 'open' ? QUOTE_CACHE_SECONDS : OFF_HOURS_QUOTE_CACHE_SECONDS;
	const quotes = await Promise.all(symbols.map((symbol) => getQuote(symbol, seconds)));
	return Object.fromEntries(symbols.map((symbol, i) => [symbol, quotes[i]]));
}

/** US market holidays, including early-close half days. */
export async function getMarketHolidays(): Promise<Holidays> {
	const key = 'finnhub:market-holidays';
	const hit = cached<Holidays>(key);
	if (hit) return hit;

	let data: FinnhubHolidays;
	try {
		data = await finnhub<FinnhubHolidays>('stock/market-holiday', { exchange: 'US' });
	} catch (error) {
		console.warn('Finnhub market holidays failed:', error);
		return {};
	}

	const holidays: Holidays = {};
	for (const holiday of data?.data ?? []) {
		// Times look like "09:30-13:00"; Finnhub sometimes uses ":" as the separator.
		const trading: string[] = (holiday.tradingHour ?? '').match(/\d{1,2}:\d{2}/g) ?? [];
		const postMarket: string[] = (holiday.postMarket ?? '').match(/\d{1,2}:\d{2}/g) ?? [];
		holidays[holiday.atDate] = {
			name: holiday.eventName,
			close: trading.length ? parseClock(trading[trading.length - 1]) : null,
			afterClose: postMarket.length ? parseClock(postMarket[postMarket.length - 1]) : null
		};
	}

	store(key, holidays, HOLIDAY_CACHE_SECONDS);
	return holidays;
}

export async function getMarketStatus(now = new Date()): Promise<MarketStatus> {
	return marketStatusAt(now, await getMarketHolidays());
}

async function marketContext() {
	const marketStatus = await getMarketStatus();
	return { marketStatus, changeLabel: changeLabel(marketStatus) };
}

const allSymbols = () => [...MARKET_INDEXES, ...MARKET_STOCKS].map(([symbol]) => symbol);

/** Where the current price sits within today's low–high range, 0–100. */
function rangePct(quote: Quote | null) {
	if (!quote || quote.high <= quote.low) return 50;
	return ((quote.price - quote.low) / (quote.high - quote.low)) * 100;
}

export async function marketSnapshot(): Promise<MarketSnapshot> {
	const quotes = await getQuotes(allSymbols());
	const rows = (tickers: [string, string][]) =>
		tickers.map(([symbol, name]) => ({
			symbol,
			name,
			quote: quotes[symbol],
			rangePct: rangePct(quotes[symbol])
		}));

	return { indexes: rows(MARKET_INDEXES), stocks: rows(MARKET_STOCKS), ...(await marketContext()) };
}

export async function marketPulse(): Promise<MarketPulse> {
	const quotes = await getQuotes(allSymbols());

	const [headlineSymbol, headlineName] = MARKET_INDEXES[0];
	const indexes: Ticker[] = MARKET_INDEXES.slice(1).map(([symbol, name]) => ({
		symbol,
		name,
		quote: quotes[symbol]
	}));

	const stocks = MARKET_STOCKS.flatMap(([symbol, name]) => {
		const quote = quotes[symbol];
		return quote ? [{ symbol, name, quote }] : [];
	}).sort((a, b) => b.quote.changePct - a.quote.changePct);

	// Bar lengths are relative to the biggest move of the day.
	const biggestMove = Math.max(0, ...stocks.map((s) => Math.abs(s.quote.changePct)));
	const movers = stocks.map((s) => ({
		...s,
		barPct: biggestMove ? (Math.abs(s.quote.changePct) / biggestMove) * 100 : 0
	}));

	return {
		headline: { symbol: headlineSymbol, name: headlineName, quote: quotes[headlineSymbol] },
		indexes,
		gainers: movers.filter((s) => s.quote.changePct > 0).slice(0, MOVERS_COUNT),
		losers: [...movers]
			.reverse()
			.filter((s) => s.quote.changePct < 0)
			.slice(0, MOVERS_COUNT),
		...(await marketContext())
	};
}
