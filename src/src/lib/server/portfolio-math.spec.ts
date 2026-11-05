import { describe, expect, it } from 'vitest';
import {
	addShares,
	allocation,
	Decimal,
	removeShares,
	toDb,
	TradeError,
	trim
} from './portfolio-math.ts';

const d = (v: Decimal.Value) => new Decimal(v);
const position = (quantity: Decimal.Value, avgCost: Decimal.Value) => ({
	symbol: 'AAPL',
	quantity: d(quantity),
	avgCost: d(avgCost)
});

// Expected values come from the Django test suite (portfolio/tests.py).
describe('addShares', () => {
	it('opens a new position', () => {
		const next = addShares(position(0, 0), d(10), d(150));
		expect(toDb.quantity(next.quantity)).toBe('10.000000');
		expect(toDb.avgCost(next.avgCost)).toBe('150.0000');
		expect(toDb.money(next.costBasis)).toBe('1500.00');
	});

	it('re-averages the cost', () => {
		const next = addShares(position(10, 150), d(5), d(160));
		expect(next.quantity.toFixed()).toBe('15');
		expect(toDb.avgCost(next.avgCost)).toBe('153.3333');
		expect(toDb.money(next.costBasis)).toBe('2300.00');
	});

	it('supports fractional shares', () => {
		const next = addShares(position(0, 0), d('0.5'), d(500));
		expect(toDb.money(next.costBasis)).toBe('250.00');
	});

	it('rejects non-positive quantities', () => {
		expect(() => addShares(position(10, 150), d(0), d(1))).toThrow(TradeError);
		expect(() => addShares(position(10, 150), d(-1), d(1))).toThrow(TradeError);
	});
});

describe('removeShares', () => {
	it('keeps the average cost and returns the cost of what was sold', () => {
		const { position: next, costOfSold } = removeShares(position(10, 150), d(4));
		expect(costOfSold.toFixed()).toBe('600');
		expect(next.quantity.toFixed()).toBe('6');
		expect(next.avgCost.toFixed()).toBe('150');
	});

	it('rejects selling more than held', () => {
		expect(() => removeShares(position(10, 150), d(11))).toThrow(
			'Cannot sell 11 AAPL; only 10 held.'
		);
	});

	it('rejects non-positive quantities', () => {
		expect(() => removeShares(position(10, 150), d(0))).toThrow(TradeError);
	});
});

describe('allocation', () => {
	it('returns weights largest first, plus cash', () => {
		const result = allocation(d(500), [
			{ symbol: 'MSFT', marketValue: d(500) },
			{ symbol: 'AAPL', marketValue: d(1000) }
		]);
		expect(result.holdings).toEqual([
			{ symbol: 'AAPL', weight: 50 },
			{ symbol: 'MSFT', weight: 25 }
		]);
		expect(result.cashPct).toBe(25);
	});

	it('is empty when the portfolio is worth nothing', () => {
		expect(allocation(d(0), [])).toEqual({ holdings: [], cashPct: 0 });
	});
});

describe('rounding', () => {
	it('uses banker’s rounding like Django', () => {
		expect(toDb.money(d('0.125'))).toBe('0.12');
		expect(toDb.money(d('0.135'))).toBe('0.14');
	});

	it('trims share counts', () => {
		expect(trim('10.000000')).toBe('10');
		expect(trim('2.500000')).toBe('2.5');
		expect(trim('0.000001')).toBe('0.000001');
		expect(trim(null)).toBe('');
	});
});
