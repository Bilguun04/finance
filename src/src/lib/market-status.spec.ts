import { describe, expect, it } from 'vitest';
import { changeLabel, marketStatusAt, parseClock, type Holidays } from './market-status.ts';

// Instants in Eastern Time. November 2026 is EST (UTC-5).
const et = (iso: string) => new Date(`${iso}-05:00`);

describe('marketStatusAt', () => {
	it.each([
		['2026-11-04T03:59', 'overnight'],
		['2026-11-04T04:00', 'pre_market'],
		['2026-11-04T09:29', 'pre_market'],
		['2026-11-04T09:30', 'open'],
		['2026-11-04T15:59', 'open'],
		['2026-11-04T16:00', 'after_hours'],
		['2026-11-04T19:59', 'after_hours'],
		['2026-11-04T20:00', 'overnight'],
		// Friday after the after-hours close through Sunday 8pm.
		['2026-11-06T19:59', 'after_hours'],
		['2026-11-06T20:00', 'closed'],
		['2026-11-07T12:00', 'closed'],
		['2026-11-08T19:59', 'closed'],
		['2026-11-08T20:00', 'overnight']
	])('%s ET is %s', (time, state) => {
		expect(marketStatusAt(et(time)).state).toBe(state);
	});

	it('uses Eastern Time across daylight saving', () => {
		// July is EDT (UTC-4): 13:30 UTC is 9:30 ET.
		expect(marketStatusAt(new Date('2026-07-15T13:30:00Z')).state).toBe('open');
	});

	const holidays: Holidays = {
		'2026-11-26': { name: 'Thanksgiving Day', close: null, afterClose: null },
		'2026-11-27': {
			name: 'Day after Thanksgiving',
			close: parseClock('13:00'),
			afterClose: parseClock('17:00')
		}
	};

	it('is closed all day on a full holiday', () => {
		const status = marketStatusAt(et('2026-11-26T11:00'), holidays);
		expect(status).toEqual({
			state: 'closed',
			label: 'Market closed',
			holiday: 'Thanksgiving Day'
		});
	});

	it('closes early on a half day', () => {
		expect(marketStatusAt(et('2026-11-27T12:59'), holidays).state).toBe('open');
		expect(marketStatusAt(et('2026-11-27T13:00'), holidays).state).toBe('after_hours');
		// A Friday: after the early after-hours close the weekend starts.
		expect(marketStatusAt(et('2026-11-27T17:00'), holidays).state).toBe('closed');
	});
});

describe('changeLabel', () => {
	it('describes today only during or right after the session', () => {
		expect(changeLabel(marketStatusAt(et('2026-11-04T10:00')))).toBe('today');
		expect(changeLabel(marketStatusAt(et('2026-11-04T17:00')))).toBe('today');
		expect(changeLabel(marketStatusAt(et('2026-11-04T05:00')))).toBe('last session');
	});
});
