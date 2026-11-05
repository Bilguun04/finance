import Decimal from 'decimal.js';

// Pure money maths for portfolios, kept apart from the database so it is easy to test.
// Values are rounded the way Django's DecimalField saved them (banker's rounding to the column's places).

// Python's Decimal default precision, so intermediate results match the Django app.
Decimal.set({ precision: 28 });

export { Decimal };

export class TradeError extends Error {}

export const ZERO = new Decimal(0);

export const round = (value: Decimal, places: number) =>
	value.toDecimalPlaces(places, Decimal.ROUND_HALF_EVEN);

/** Column precisions, matching the schema. */
export const toDb = {
	cash: (v: Decimal) => round(v, 2).toFixed(2),
	money: (v: Decimal) => round(v, 2).toFixed(2),
	quantity: (v: Decimal) => round(v, 6).toFixed(6),
	price: (v: Decimal) => round(v, 4).toFixed(4),
	avgCost: (v: Decimal) => round(v, 4).toFixed(4)
};

export function requirePositive(values: Record<string, Decimal>) {
	for (const [name, value] of Object.entries(values)) {
		if (value.lessThanOrEqualTo(0)) throw new TradeError(`${name} must be positive.`);
	}
}

/** 10.000000 -> "10", 2.500000 -> "2.5"; share counts read better without padding. */
export function trim(value: Decimal.Value | null | undefined): string {
	return value === null || value === undefined ? '' : new Decimal(value).toFixed();
}

export type Position = { symbol: string; quantity: Decimal; avgCost: Decimal };

/** Adds shares and re-averages the cost. Returns the new position and its (unrounded) cost basis. */
export function addShares(position: Position, quantity: Decimal, price: Decimal) {
	requirePositive({ quantity, price });
	const total = position.quantity.plus(quantity);
	const avgCost = position.avgCost
		.times(position.quantity)
		.plus(price.times(quantity))
		.dividedBy(total);
	return { ...position, quantity: total, avgCost, costBasis: total.times(avgCost) };
}

/**
 * Removes shares and returns their cost basis, for realized-gain maths.
 * The average cost doesn't change on a sell.
 */
export function removeShares(position: Position, quantity: Decimal) {
	requirePositive({ quantity });
	if (quantity.greaterThan(position.quantity)) {
		throw new TradeError(
			`Cannot sell ${quantity.toFixed()} ${position.symbol}; only ${trim(position.quantity)} held.`
		);
	}
	const remaining = position.quantity.minus(quantity);
	return {
		position: { ...position, quantity: remaining, costBasis: remaining.times(position.avgCost) },
		costOfSold: quantity.times(position.avgCost)
	};
}

export const pct = (part: Decimal, whole: Decimal) =>
	whole.isZero() ? ZERO : part.dividedBy(whole).times(100);

/**
 * Each holding's share of the portfolio in percent, largest first, plus the cash share.
 * Percentages only, so it's safe to show to friends without revealing dollar amounts.
 */
export function allocation(cash: Decimal, holdings: { symbol: string; marketValue: Decimal }[]) {
	const sorted = [...holdings].sort(
		(a, b) => b.marketValue.comparedTo(a.marketValue) || a.symbol.localeCompare(b.symbol)
	);
	const total = sorted.reduce((sum, h) => sum.plus(h.marketValue), cash);
	if (total.isZero()) return { holdings: [], cashPct: 0 };
	return {
		holdings: sorted.map((h) => ({
			symbol: h.symbol,
			weight: pct(h.marketValue, total).toNumber()
		})),
		cashPct: pct(cash, total).toNumber()
	};
}
