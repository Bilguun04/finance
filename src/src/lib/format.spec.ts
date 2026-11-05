import { describe, expect, it } from 'vitest';
import { fixed, money, shortDate, shortTime, signedMoney, timesince } from './format.ts';

describe('number formatting', () => {
	it('matches Django floatformat', () => {
		expect(money(1234.5)).toBe('1,234.50');
		expect(money('1000000')).toBe('1,000,000.00');
		expect(fixed(1234.567, 1)).toBe('1234.6');
		expect(signedMoney(-1234.5)).toBe('−$1,234.50');
		expect(signedMoney(0)).toBe('+$0.00');
	});
});

describe('dates', () => {
	const date = new Date('2026-09-05T15:04:00Z');

	it('formats in UTC', () => {
		expect(shortDate(date)).toBe('Sep 5, 2026');
		expect(shortTime(date)).toBe('3:04 PM');
	});

	it('timesince uses up to two adjacent units', () => {
		const now = new Date('2026-09-08T19:30:00Z');
		expect(timesince(date, now)).toBe('3 days, 4 hours');
		expect(timesince(now, now)).toBe('0 minutes');
		expect(timesince(new Date('2026-09-08T19:29:00Z'), now)).toBe('1 minute');
	});
});
