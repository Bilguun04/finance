/** Prices from the previous refresh, keyed by symbol. */
export type PreviousPrices = Record<string, number>;

/** Highlights a price that moved since the last refresh. */
export function flashClass(previous: PreviousPrices, symbol: string, price: number | undefined) {
	const before = previous[symbol];
	if (!before || price === undefined || price === before) return '';
	return price > before ? 'flash-up' : 'flash-down';
}
