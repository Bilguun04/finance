import { charField, checkbox, choiceField, decimalField, Errors } from '#lib/server/forms.ts';
import { ZERO } from '#lib/server/portfolio-math.ts';

const SYMBOL_PATTERN = /^[A-Z0-9.-]{1,12}$/;

/** Name/currency/visibility, shared by the create form and settings (where currency is fixed). */
export function cleanPortfolioForm(data: FormData, { withCurrency }: { withCurrency: boolean }) {
	const errors = new Errors();
	const name = charField(data, 'name', errors, { maxLength: 100 });
	const currency = withCurrency
		? charField(data, 'currency', errors, { maxLength: 3 }).toUpperCase()
		: undefined;
	return { errors, name, currency, isPublic: checkbox(data, 'is_public') };
}

export function cleanTradeForm(data: FormData) {
	const errors = new Errors();
	const side = choiceField(data, 'side', errors, ['BUY', 'SELL'] as const);

	const symbol = charField(data, 'symbol', errors, { maxLength: 12 }).toUpperCase();
	if (symbol && !errors.fields.symbol && !SYMBOL_PATTERN.test(symbol)) {
		errors.add('symbol', 'Use letters, numbers, dots or dashes, e.g. AAPL or BRK.B.');
	}

	const quantity = decimalField(data, 'quantity', errors, {
		maxDigits: 18,
		decimalPlaces: 6,
		min: '0.000001'
	});
	const price = decimalField(data, 'price', errors, {
		maxDigits: 14,
		decimalPlaces: 4,
		min: '0.0001'
	});
	const fee =
		decimalField(data, 'fee', errors, {
			maxDigits: 10,
			decimalPlaces: 2,
			min: 0,
			required: false
		}) ?? ZERO;

	return {
		errors,
		side,
		trade: { symbol, quantity: quantity ?? ZERO, price: price ?? ZERO, fee },
		useCash: checkbox(data, 'use_cash')
	};
}

export function cleanCashForm(data: FormData) {
	const errors = new Errors();
	const action = choiceField(data, 'action', errors, ['DEPOSIT', 'WITHDRAW'] as const);
	const amount = decimalField(data, 'amount', errors, {
		maxDigits: 14,
		decimalPlaces: 2,
		min: '0.01'
	});
	return { errors, action, amount: amount ?? ZERO };
}
