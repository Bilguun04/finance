import { sql } from 'drizzle-orm';
import {
	boolean,
	check,
	index,
	integer,
	numeric,
	pgTable,
	timestamp,
	unique,
	varchar,
	text
} from 'drizzle-orm/pg-core';
import { user } from './auth.schema';

export * from './auth.schema';

const id = () => integer('id').primaryKey().generatedAlwaysAsIdentity();
const userRef = (name: string) =>
	text(name)
		.notNull()
		.references(() => user.id, { onDelete: 'cascade' });

// Decimal columns come back from postgres as strings; do maths on them with decimal.js.

export const portfolio = pgTable(
	'portfolio',
	{
		id: id(),
		userId: userRef('user_id'),
		name: varchar('name', { length: 100 }).notNull().default('Main'),
		cash: numeric('cash', { precision: 14, scale: 2 }).notNull().default('0'),
		currency: varchar('currency', { length: 3 }).notNull().default('USD'),
		// Snapshot of cash + holdings' market value, refreshed whenever either changes.
		netLiquidity: numeric('net_liquidity', { precision: 14, scale: 2 }).notNull().default('0'),
		isPublic: boolean('is_public').notNull().default(false),
		createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow()
	},
	(t) => [index('portfolio_user_id_idx').on(t.userId)]
);

export const holding = pgTable(
	'holding',
	{
		id: id(),
		portfolioId: integer('portfolio_id')
			.notNull()
			.references(() => portfolio.id, { onDelete: 'cascade' }),
		symbol: varchar('symbol', { length: 12 }).notNull(),
		quantity: numeric('quantity', { precision: 18, scale: 6 }).notNull().default('0'),
		avgCost: numeric('avg_cost', { precision: 14, scale: 4 }).notNull().default('0'),
		// Always quantity * avg_cost; kept in sync whenever either changes.
		costBasis: numeric('cost_basis', { precision: 14, scale: 2 }).notNull().default('0'),
		marketValue: numeric('market_value', { precision: 14, scale: 2 }).notNull().default('0')
	},
	(t) => [unique('holding_portfolio_symbol_unique').on(t.portfolioId, t.symbol)]
);

export const TRANSACTION_KINDS = [
	'BUY',
	'SELL',
	'DEPOSIT',
	'WITHDRAW',
	'DIVIDEND',
	'FEE',
	'SPLIT'
] as const;
export type TransactionKind = (typeof TRANSACTION_KINDS)[number];

export const portfolioTransaction = pgTable(
	'portfolio_transaction',
	{
		id: id(),
		portfolioId: integer('portfolio_id')
			.notNull()
			.references(() => portfolio.id, { onDelete: 'cascade' }),
		kind: varchar('kind', { length: 10 }).$type<TransactionKind>().notNull(),
		symbol: varchar('symbol', { length: 12 }).notNull().default(''),
		quantity: numeric('quantity', { precision: 18, scale: 6 }),
		// Per-share price for trades; the cash amount for deposits and withdrawals.
		price: numeric('price', { precision: 14, scale: 4 }),
		fee: numeric('fee', { precision: 10, scale: 2 }).notNull().default('0'),
		executedAt: timestamp('executed_at', { withTimezone: true }).notNull().defaultNow(),
		realizedGain: numeric('realized_gain', { precision: 14, scale: 2 })
	},
	(t) => [
		index('portfolio_transaction_portfolio_executed_idx').on(t.portfolioId, t.executedAt),
		index('portfolio_transaction_symbol_idx').on(t.symbol)
	]
);

export const SESSION_FORMATS = { homegame: 'Home game', casino: 'Casino' } as const;
export type SessionFormat = keyof typeof SESSION_FORMATS;

// Named bankroll_session so it doesn't clash with better-auth's `session` table.
export const bankrollSession = pgTable(
	'bankroll_session',
	{
		id: id(),
		userId: userRef('user_id'),
		host: varchar('host', { length: 100 }).notNull(), // playground or homegame host
		format: varchar('format', { length: 100 }).$type<SessionFormat>().notNull(),
		type: varchar('type', { length: 100 }), // poker, blackjack, roulette etc.
		stakes: varchar('stakes', { length: 100 }).notNull(), // 1/2$, 2/5$ etc.
		date: timestamp('date', { withTimezone: true }).notNull().defaultNow(),
		sessionStart: timestamp('session_start', { withTimezone: true }).notNull(),
		sessionEnd: timestamp('session_end', { withTimezone: true }).notNull(),
		buyin: integer('buyin').notNull().default(0),
		buyout: integer('buyout').notNull().default(0)
	},
	(t) => [
		index('bankroll_session_user_id_idx').on(t.userId),
		check('bankroll_session_buyin_positive', sql`${t.buyin} >= 0`),
		check('bankroll_session_buyout_positive', sql`${t.buyout} >= 0`)
	]
);

/**
 * A pending request, or, once accepted, the friendship itself.
 * Declining, cancelling and unfriending delete the row, so either person can send a fresh request later.
 */
export const friendRequest = pgTable(
	'friend_request',
	{
		id: id(),
		fromUserId: userRef('from_user_id'),
		toUserId: userRef('to_user_id'),
		status: varchar('status', { length: 10 })
			.$type<'PENDING' | 'ACCEPTED'>()
			.notNull()
			.default('PENDING'),
		createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
		respondedAt: timestamp('responded_at', { withTimezone: true })
	},
	(t) => [
		unique('unique_friend_request_direction').on(t.fromUserId, t.toUserId),
		check('no_self_friend_request', sql`${t.fromUserId} <> ${t.toUserId}`),
		index('friend_request_to_user_idx').on(t.toUserId)
	]
);
