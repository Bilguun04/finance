import { and, asc, count, desc, eq, sum } from 'drizzle-orm';
import { error } from '@sveltejs/kit';
import { db } from '#lib/server/db/index.ts';
import {
	holding,
	portfolio,
	portfolioTransaction,
	type TransactionKind
} from '#lib/server/db/schema.ts';
import { getQuotes } from '#lib/server/market.ts';
import {
	addShares,
	Decimal,
	pct,
	removeShares,
	requirePositive,
	toDb,
	TradeError,
	trim,
	ZERO
} from '#lib/server/portfolio-math.ts';

export { TradeError };

const RECENT_TRANSACTIONS = 10;

type Tx = Parameters<Parameters<typeof db.transaction>[0]>[0];

/** Scoped to the owner so one user can never view or trade another user's portfolio. */
export async function getPortfolio(userId: string, id: number) {
	const [row] = Number.isSafeInteger(id)
		? await db
				.select()
				.from(portfolio)
				.where(and(eq(portfolio.id, id), eq(portfolio.userId, userId)))
		: [];
	if (!row) error(404, 'Not found');
	return row;
}

export async function listPortfolios(userId: string) {
	const rows = await db
		.select({
			id: portfolio.id,
			name: portfolio.name,
			cash: portfolio.cash,
			currency: portfolio.currency,
			netLiquidity: portfolio.netLiquidity,
			isPublic: portfolio.isPublic,
			createdAt: portfolio.createdAt,
			numHoldings: count(holding.id)
		})
		.from(portfolio)
		.leftJoin(holding, eq(holding.portfolioId, portfolio.id))
		.where(eq(portfolio.userId, userId))
		.groupBy(portfolio.id)
		.orderBy(asc(portfolio.createdAt));

	return rows.map((p) => ({ ...p, cash: Number(p.cash), netLiquidity: Number(p.netLiquidity) }));
}

/**
 * Locks the portfolio row for the rest of the transaction and returns its cash,
 * so two simultaneous trades can't both spend the same money.
 */
async function lockCash(tx: Tx, portfolioId: number) {
	const [row] = await tx
		.select({ cash: portfolio.cash })
		.from(portfolio)
		.where(eq(portfolio.id, portfolioId))
		.for('update');
	return new Decimal(row.cash);
}

/** Saves cash and refreshes the net-liquidity snapshot from the saved holdings. */
async function finish(tx: Tx, portfolioId: number, cash: Decimal) {
	const [{ total }] = await tx
		.select({ total: sum(holding.marketValue) })
		.from(holding)
		.where(eq(holding.portfolioId, portfolioId));
	const savedCash = toDb.cash(cash);
	await tx
		.update(portfolio)
		.set({ cash: savedCash, netLiquidity: toDb.money(new Decimal(savedCash).plus(total ?? 0)) })
		.where(eq(portfolio.id, portfolioId));
}

async function record(
	tx: Tx,
	portfolioId: number,
	kind: TransactionKind,
	fields: {
		symbol?: string;
		quantity?: Decimal;
		price: Decimal;
		fee?: Decimal;
		realizedGain?: Decimal;
	}
) {
	await tx.insert(portfolioTransaction).values({
		portfolioId,
		kind,
		symbol: fields.symbol ?? '',
		quantity: fields.quantity ? toDb.quantity(fields.quantity) : null,
		price: toDb.price(fields.price),
		fee: toDb.money(fields.fee ?? ZERO),
		realizedGain: fields.realizedGain ? toDb.money(fields.realizedGain) : null
	});
}

export async function addCash(portfolioId: number, amount: Decimal) {
	requirePositive({ amount });
	await db.transaction(async (tx) => {
		const cash = await lockCash(tx, portfolioId);
		await finish(tx, portfolioId, cash.plus(amount));
		await record(tx, portfolioId, 'DEPOSIT', { price: amount });
	});
}

export async function removeCash(portfolioId: number, amount: Decimal) {
	requirePositive({ amount });
	await db.transaction(async (tx) => {
		const cash = await lockCash(tx, portfolioId);
		if (amount.greaterThan(cash)) throw new TradeError('Insufficient cash in portfolio.');
		await finish(tx, portfolioId, cash.minus(amount));
		await record(tx, portfolioId, 'WITHDRAW', { price: amount });
	});
}

type Trade = { symbol: string; quantity: Decimal; price: Decimal; fee: Decimal };

/**
 * Buys shares, re-averaging the cost if the symbol is already held.
 * useCash = false records a position bought outside the app without touching cash.
 */
export async function buy(
	portfolioId: number,
	{ symbol, quantity, price, fee }: Trade,
	useCash = true
) {
	symbol = symbol.toUpperCase().trim();
	requirePositive({ quantity, price });

	await db.transaction(async (tx) => {
		let cash = await lockCash(tx, portfolioId);
		const cost = quantity.times(price).plus(fee);
		if (useCash) {
			if (cost.greaterThan(cash)) throw new TradeError('Insufficient cash in portfolio.');
			cash = cash.minus(cost);
		}

		await tx.insert(holding).values({ portfolioId, symbol }).onConflictDoNothing();
		const [current] = await tx
			.select()
			.from(holding)
			.where(and(eq(holding.portfolioId, portfolioId), eq(holding.symbol, symbol)))
			.for('update');

		const next = addShares(
			{ symbol, quantity: new Decimal(current.quantity), avgCost: new Decimal(current.avgCost) },
			quantity,
			price
		);
		await tx
			.update(holding)
			.set({
				quantity: toDb.quantity(next.quantity),
				avgCost: toDb.avgCost(next.avgCost),
				costBasis: toDb.money(next.costBasis),
				// The trade price is the freshest price we have; refreshing prices updates it later.
				marketValue: toDb.money(next.quantity.times(price))
			})
			.where(eq(holding.id, current.id));

		await finish(tx, portfolioId, cash);
		await record(tx, portfolioId, 'BUY', { symbol, quantity, price, fee });
	});
}

/** Sells shares and records the realized gain against the average cost. */
export async function sell(portfolioId: number, { symbol, quantity, price, fee }: Trade) {
	symbol = symbol.toUpperCase().trim();
	requirePositive({ quantity, price });

	await db.transaction(async (tx) => {
		const cash = await lockCash(tx, portfolioId);
		const [current] = await tx
			.select()
			.from(holding)
			.where(and(eq(holding.portfolioId, portfolioId), eq(holding.symbol, symbol)))
			.for('update');
		if (!current) throw new TradeError(`No ${symbol} holding to sell.`);

		const { position, costOfSold } = removeShares(
			{ symbol, quantity: new Decimal(current.quantity), avgCost: new Decimal(current.avgCost) },
			quantity
		);
		const proceeds = quantity.times(price).minus(fee);

		if (position.quantity.isZero()) {
			await tx.delete(holding).where(eq(holding.id, current.id));
		} else {
			await tx
				.update(holding)
				.set({
					quantity: toDb.quantity(position.quantity),
					costBasis: toDb.money(position.costBasis),
					marketValue: toDb.money(position.quantity.times(price))
				})
				.where(eq(holding.id, current.id));
		}

		await finish(tx, portfolioId, cash.plus(proceeds));
		await record(tx, portfolioId, 'SELL', {
			symbol,
			quantity,
			price,
			fee,
			realizedGain: proceeds.minus(costOfSold)
		});
	});
}

/** Reprices every holding with one batched quote lookup; holdings without a quote keep their value. */
export async function refreshMarketValues(portfolioId: number) {
	const symbols = await db
		.select({ symbol: holding.symbol })
		.from(holding)
		.where(eq(holding.portfolioId, portfolioId));
	// Fetch quotes before taking the lock so slow API calls don't hold it.
	const quotes = await getQuotes(symbols.map((h) => h.symbol));

	await db.transaction(async (tx) => {
		const cash = await lockCash(tx, portfolioId);
		// Re-read under the lock in case a trade changed quantities meanwhile.
		const holdings = await tx.select().from(holding).where(eq(holding.portfolioId, portfolioId));
		for (const h of holdings) {
			const quote = quotes[h.symbol];
			if (!quote) continue;
			// String() first so float prices don't carry binary noise into the decimal maths.
			const value = new Decimal(h.quantity).times(String(quote.price));
			await tx
				.update(holding)
				.set({ marketValue: toDb.money(value) })
				.where(eq(holding.id, h.id));
		}
		await finish(tx, portfolioId, cash);
	});
}

/** Everything the portfolio detail page shows. */
export async function portfolioBody(p: typeof portfolio.$inferSelect) {
	const [holdingRows, transactionRows, [{ realized }]] = await Promise.all([
		db
			.select()
			.from(holding)
			.where(eq(holding.portfolioId, p.id))
			.orderBy(desc(holding.marketValue), asc(holding.symbol)),
		db
			.select()
			.from(portfolioTransaction)
			.where(eq(portfolioTransaction.portfolioId, p.id))
			.orderBy(desc(portfolioTransaction.executedAt), desc(portfolioTransaction.id))
			.limit(RECENT_TRANSACTIONS),
		db
			.select({ realized: sum(portfolioTransaction.realizedGain) })
			.from(portfolioTransaction)
			.where(and(eq(portfolioTransaction.portfolioId, p.id), eq(portfolioTransaction.kind, 'SELL')))
	]);

	const cash = new Decimal(p.cash);
	const marketValue = holdingRows.reduce((s, h) => s.plus(h.marketValue), ZERO);
	const costBasis = holdingRows.reduce((s, h) => s.plus(h.costBasis), ZERO);
	const netLiquidity = cash.plus(marketValue);
	const unrealized = marketValue.minus(costBasis);

	const holdings = holdingRows.map((h) => {
		const value = new Decimal(h.marketValue);
		const basis = new Decimal(h.costBasis);
		return {
			symbol: h.symbol,
			displayQuantity: trim(h.quantity),
			avgCost: Number(h.avgCost),
			marketValue: value.toNumber(),
			costBasis: basis.toNumber(),
			unrealizedGain: value.minus(basis).toNumber(),
			weight: pct(value, netLiquidity).toNumber(),
			gainPct: pct(value.minus(basis), basis).toNumber()
		};
	});

	const transactions = transactionRows.map((t) => ({
		id: t.id,
		kind: t.kind,
		symbol: t.symbol,
		displayQuantity: trim(t.quantity),
		price: Number(t.price ?? 0),
		fee: Number(t.fee),
		executedAt: t.executedAt,
		// Trades store a per-share price; cash movements store the amount itself in price.
		amount:
			t.quantity !== null
				? new Decimal(t.quantity).times(t.price ?? 0).toNumber()
				: Number(t.price ?? 0),
		realizedGain: t.realizedGain === null ? null : Number(t.realizedGain)
	}));

	return {
		portfolio: {
			id: p.id,
			name: p.name,
			currency: p.currency,
			isPublic: p.isPublic,
			cash: cash.toNumber()
		},
		holdings,
		transactions,
		netLiquidity: netLiquidity.toNumber(),
		marketValue: marketValue.toNumber(),
		costBasis: costBasis.toNumber(),
		unrealizedGain: unrealized.toNumber(),
		unrealizedPct: pct(unrealized, costBasis).toNumber(),
		realizedGain: Number(realized ?? 0),
		cashPct: pct(cash, netLiquidity).toNumber()
	};
}
