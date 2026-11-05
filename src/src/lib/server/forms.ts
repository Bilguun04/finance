import Decimal from 'decimal.js';

// Small form helpers that reproduce Django's field cleaning and error messages.

export const REQUIRED = 'This field is required.';

export type FieldErrors = Record<string, string[]>;

export function text(data: FormData, name: string): string {
	// Django's CharField strips surrounding whitespace by default.
	return (data.get(name)?.toString() ?? '').trim();
}

export function checkbox(data: FormData, name: string): boolean {
	return data.has(name);
}

/** Collects field errors as a form is cleaned. */
export class Errors {
	fields: FieldErrors = {};
	nonField: string[] = [];

	add(field: string, message: string) {
		(this.fields[field] ??= []).push(message);
	}

	get any() {
		return this.nonField.length > 0 || Object.keys(this.fields).length > 0;
	}

	toJSON() {
		return { fields: this.fields, nonField: this.nonField };
	}
}

export function charField(
	data: FormData,
	name: string,
	errors: Errors,
	{ maxLength, required = true }: { maxLength: number; required?: boolean }
): string {
	const value = text(data, name);
	if (!value) {
		if (required) errors.add(name, REQUIRED);
	} else if (value.length > maxLength) {
		errors.add(
			name,
			`Ensure this value has at most ${maxLength} characters (it has ${value.length}).`
		);
	}
	return value;
}

export function choiceField<T extends string>(
	data: FormData,
	name: string,
	errors: Errors,
	choices: readonly T[]
): T {
	const value = text(data, name);
	if (!value) errors.add(name, REQUIRED);
	else if (!choices.includes(value as T)) {
		errors.add(name, `Select a valid choice. ${value} is not one of the available choices.`);
	}
	return value as T;
}

/** Like Django's DecimalField: validates digits, decimal places and the minimum. */
export function decimalField(
	data: FormData,
	name: string,
	errors: Errors,
	opts: { maxDigits: number; decimalPlaces: number; min?: Decimal.Value; required?: boolean }
): Decimal | null {
	const raw = text(data, name);
	if (!raw) {
		if (opts.required ?? true) errors.add(name, REQUIRED);
		return null;
	}
	if (!/^[+-]?(\d+\.?\d*|\.\d+)$/.test(raw)) {
		errors.add(name, 'Enter a number.');
		return null;
	}
	const value = new Decimal(raw);
	const [whole, fraction = ''] = value.abs().toFixed().split('.');
	const wholeDigits = whole === '0' ? 0 : whole.length;
	const maxWhole = opts.maxDigits - opts.decimalPlaces;

	if (opts.min !== undefined && value.lessThan(opts.min)) {
		errors.add(
			name,
			`Ensure this value is greater than or equal to ${new Decimal(opts.min).toFixed()}.`
		);
	} else if (wholeDigits + fraction.length > opts.maxDigits) {
		errors.add(name, `Ensure that there are no more than ${opts.maxDigits} digits in total.`);
	} else if (fraction.length > opts.decimalPlaces) {
		errors.add(name, `Ensure that there are no more than ${opts.decimalPlaces} decimal places.`);
	} else if (wholeDigits > maxWhole) {
		errors.add(
			name,
			`Ensure that there are no more than ${maxWhole} digits before the decimal point.`
		);
	}
	return value;
}

export function integerField(
	data: FormData,
	name: string,
	errors: Errors,
	{ min }: { min?: number } = {}
): number {
	const raw = text(data, name);
	if (!raw) {
		errors.add(name, REQUIRED);
		return 0;
	}
	if (!/^[+-]?\d+$/.test(raw)) {
		errors.add(name, 'Enter a whole number.');
		return 0;
	}
	const value = Number(raw);
	if (min !== undefined && value < min) {
		errors.add(name, `Ensure this value is greater than or equal to ${min}.`);
	} else if (value > 2147483647) {
		errors.add(name, 'Ensure this value is less than or equal to 2147483647.');
	}
	return value;
}

/** Parses a `datetime-local` value. The app runs in UTC like the Django project did. */
export function dateTimeField(data: FormData, name: string, errors: Errors): Date | null {
	const raw = text(data, name);
	if (!raw) {
		errors.add(name, REQUIRED);
		return null;
	}
	const date = new Date(/[zZ]|[+-]\d\d:\d\d$/.test(raw) ? raw : `${raw}Z`);
	if (Number.isNaN(date.getTime())) {
		errors.add(name, 'Enter a valid date/time.');
		return null;
	}
	return date;
}

/** Form values to send back so a failed submission keeps what the user typed. */
export function values(data: FormData, exclude: string[] = []): Record<string, string> {
	const out: Record<string, string> = {};
	for (const [key, value] of data) {
		if (typeof value === 'string' && !exclude.includes(key)) out[key] = value;
	}
	return out;
}
