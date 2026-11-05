import type { MarketState, MarketStatus } from '#lib/types.ts';

// US market sessions, Eastern Time, as minutes since midnight.
export const MARKET_TZ = 'America/New_York';
const PRE_MARKET_OPEN = 4 * 60;
const MARKET_OPEN = 9 * 60 + 30;
const MARKET_CLOSE = 16 * 60;
const AFTER_HOURS_CLOSE = 20 * 60;

export const MARKET_STATE_LABELS: Record<MarketState, string> = {
	pre_market: 'Pre-market',
	open: 'Market open',
	after_hours: 'After-hours',
	overnight: 'Overnight',
	closed: 'Market closed'
};

/** A market holiday. `close`/`afterClose` are null when the market is shut all day, or early-close times. */
export type Holiday = { name: string; close: number | null; afterClose: number | null };
/** Keyed by ISO date, e.g. "2026-12-25". */
export type Holidays = Record<string, Holiday>;

/** "13:00" -> 780 */
export function parseClock(value: string): number {
	const [h, m] = value.split(':').map(Number);
	return h * 60 + m;
}

const WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const easternParts = new Intl.DateTimeFormat('en-US', {
	timeZone: MARKET_TZ,
	year: 'numeric',
	month: '2-digit',
	day: '2-digit',
	hour: '2-digit',
	minute: '2-digit',
	weekday: 'short',
	hourCycle: 'h23'
});

/** The Eastern Time calendar date, weekday (Monday = 0) and clock for an instant. */
export function easternTime(now: Date) {
	const parts = Object.fromEntries(easternParts.formatToParts(now).map((p) => [p.type, p.value]));
	return {
		date: `${parts.year}-${parts.month}-${parts.day}`,
		weekday: WEEKDAYS.indexOf(parts.weekday),
		clock: (Number(parts.hour) % 24) * 60 + Number(parts.minute)
	};
}

/** True from Friday's after-hours close until overnight trading starts Sunday evening. */
function isWeekendClose(weekday: number, clock: number, afterClose: number) {
	return (
		weekday === 5 ||
		(weekday === 4 && clock >= afterClose) ||
		(weekday === 6 && clock < AFTER_HOURS_CLOSE)
	);
}

/**
 * The US market session at `now`.
 *
 * Weekdays run pre-market, regular session, after-hours, then overnight.
 * The market is closed from Friday's after-hours close until Sunday evening, and on full-day holidays.
 */
export function marketStatusAt(now: Date, holidays: Holidays = {}): MarketStatus {
	const { date, weekday, clock } = easternTime(now);
	const holiday = holidays[date];

	const close = holiday?.close ?? MARKET_CLOSE;
	const afterClose = holiday?.afterClose ?? AFTER_HOURS_CLOSE;

	let state: MarketState;
	if (isWeekendClose(weekday, clock, afterClose) || (holiday && holiday.close === null)) {
		state = 'closed';
	} else if (PRE_MARKET_OPEN <= clock && clock < MARKET_OPEN) {
		state = 'pre_market';
	} else if (MARKET_OPEN <= clock && clock < close) {
		state = 'open';
	} else if (close <= clock && clock < afterClose) {
		state = 'after_hours';
	} else {
		state = 'overnight';
	}

	return { state, label: MARKET_STATE_LABELS[state], holiday: holiday?.name ?? null };
}

/** Quote changes are against the previous close, so outside today's sessions they describe the last session. */
export function changeLabel(status: MarketStatus): string {
	return status.state === 'open' || status.state === 'after_hours' ? 'today' : 'last session';
}
