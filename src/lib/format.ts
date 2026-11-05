// Display helpers matching the Django template filters the app used.
// Dates are shown in UTC, the project's TIME_ZONE, so server and browser render the same text.

type Num = number | string;

const formatters = new Map<string, Intl.NumberFormat>();

function formatter(digits: number, grouping: boolean) {
	const key = `${digits}:${grouping}`;
	let f = formatters.get(key);
	if (!f) {
		f = new Intl.NumberFormat('en-US', {
			minimumFractionDigits: digits,
			maximumFractionDigits: digits,
			useGrouping: grouping
		});
		formatters.set(key, f);
	}
	return f;
}

/** `floatformat:N`: fixed decimals, no thousands separators. */
export function fixed(value: Num, digits = 2): string {
	return formatter(digits, false).format(Number(value));
}

/** `floatformat:"2g"`: two decimals with thousands separators, e.g. 1,234.50. */
export function money(value: Num): string {
	return formatter(2, true).format(Number(value));
}

/** +$1,234.50 or −$1,234.50 */
export function signedMoney(value: Num): string {
	const n = Number(value);
	return n < 0 ? `−$${money(-n)}` : `+$${money(n)}`;
}

/** Whole-dollar amounts with a sign, for bankroll results: +$50 or −$50. */
export function signedDollars(value: number): string {
	return value < 0 ? `−$${-value}` : `+$${value}`;
}

/** `+` prefix for non-negative numbers, used beside changes like "+1.25%". */
export function plus(value: number): string {
	return value >= 0 ? '+' : '';
}

/** CSS width for a percentage, like `stringformat:'.3f'`. */
export function width(pct: Num): string {
	return `${Math.max(0, Number(pct)).toFixed(3)}%`;
}

export function pluralize(count: number, suffix = 's'): string {
	return count === 1 ? '' : suffix;
}

const dateFormat = new Intl.DateTimeFormat('en-US', {
	month: 'short',
	day: 'numeric',
	year: 'numeric',
	timeZone: 'UTC'
});
const longDateFormat = new Intl.DateTimeFormat('en-US', {
	month: 'long',
	day: 'numeric',
	year: 'numeric',
	timeZone: 'UTC'
});
const timeFormat = new Intl.DateTimeFormat('en-US', {
	hour: 'numeric',
	minute: '2-digit',
	timeZone: 'UTC'
});

/** "Oct 5, 2026" (Django `date:"M j, Y"`) */
export const shortDate = (d: Date) => dateFormat.format(d).replace(/^(\w{3})\w*/, '$1');
/** "October 5, 2026" (Django `date:"F j, Y"`) */
export const longDate = (d: Date) => longDateFormat.format(d);
/** "3:05 PM" (Django `time:"g:i A"`) */
export const shortTime = (d: Date) => timeFormat.format(d);

/** `YYYY-MM-DDTHH:mm` in UTC, the value format of `<input type="datetime-local">`. */
export function dateTimeLocal(d: Date | null | undefined): string {
	return d ? d.toISOString().slice(0, 16) : '';
}

const TIMESINCE_CHUNKS: [number, string][] = [
	[60 * 60 * 24 * 365, 'year'],
	[60 * 60 * 24 * 30, 'month'],
	[60 * 60 * 24 * 7, 'week'],
	[60 * 60 * 24, 'day'],
	[60 * 60, 'hour'],
	[60, 'minute']
];

/** Django's `timesince`: "3 days, 4 hours", up to two adjacent units. */
export function timesince(from: Date, now: Date = new Date()): string {
	let seconds = Math.max(0, Math.floor((now.getTime() - from.getTime()) / 1000));
	const index = TIMESINCE_CHUNKS.findIndex(([size]) => seconds >= size);
	if (index === -1) return '0 minutes';

	const parts: string[] = [];
	for (const [size, name] of TIMESINCE_CHUNKS.slice(index, index + 2)) {
		const count = Math.floor(seconds / size);
		if (count === 0) break;
		parts.push(`${count} ${name}${pluralize(count)}`);
		seconds -= count * size;
	}
	return parts.join(', ');
}
