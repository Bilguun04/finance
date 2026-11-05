export type FlashMessage = { level: 'success' | 'error' | 'info'; text: string };

/** Errors returned by a failed form action, plus what was typed so the form can be refilled. */
export type FormFailure = {
	errors: { fields: Record<string, string[]>; nonField: string[] };
	values: Record<string, string>;
};

/** A field in the shared account form card. */
export type CardField = {
	name: string;
	label: string;
	type?: string;
	autocomplete?: AutoFill;
	help?: string | string[];
	maxlength?: number;
};

export type Quote = {
	price: number;
	change: number;
	changePct: number;
	high: number;
	low: number;
	open: number;
	prevClose: number;
};

export type MarketState = 'pre_market' | 'open' | 'after_hours' | 'overnight' | 'closed';

export type MarketStatus = { state: MarketState; label: string; holiday: string | null };

export type Ticker = { symbol: string; name: string; quote: Quote | null };

export type MarketSnapshot = {
	marketStatus: MarketStatus;
	changeLabel: string;
	indexes: (Ticker & { rangePct: number })[];
	stocks: (Ticker & { rangePct: number })[];
};

export type Mover = { symbol: string; name: string; quote: Quote; barPct: number };

export type MarketPulse = {
	marketStatus: MarketStatus;
	changeLabel: string;
	headline: Ticker;
	indexes: Ticker[];
	gainers: Mover[];
	losers: Mover[];
};

export type AllocationItem = { symbol: string; weight: number };
