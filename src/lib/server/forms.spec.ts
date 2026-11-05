import { describe, expect, it } from 'vitest';
import { cleanCashForm, cleanTradeForm } from './portfolio-forms.ts';
import { validatePassword } from './passwords.ts';

const form = (fields: Record<string, string>) => {
	const data = new FormData();
	for (const [k, v] of Object.entries(fields)) data.set(k, v);
	return data;
};

describe('cleanTradeForm', () => {
	const valid = { side: 'BUY', symbol: ' brk.b ', quantity: '1.5', price: '410.1234', fee: '' };

	it('cleans a valid order', () => {
		const result = cleanTradeForm(form({ ...valid, use_cash: 'on' }));
		expect(result.errors.any).toBe(false);
		expect(result.trade.symbol).toBe('BRK.B');
		expect(result.trade.fee.toFixed()).toBe('0');
		expect(result.useCash).toBe(true);
	});

	it('reports Django-style field errors', () => {
		const result = cleanTradeForm(
			form({ ...valid, symbol: 'AA PL', quantity: '0', price: '1.00001', side: 'HOLD' })
		);
		expect(result.errors.fields).toEqual({
			side: ['Select a valid choice. HOLD is not one of the available choices.'],
			symbol: ['Use letters, numbers, dots or dashes, e.g. AAPL or BRK.B.'],
			quantity: ['Ensure this value is greater than or equal to 0.000001.'],
			price: ['Ensure that there are no more than 4 decimal places.']
		});
	});

	it('requires the core fields', () => {
		const result = cleanTradeForm(form({}));
		expect(Object.keys(result.errors.fields).sort()).toEqual([
			'price',
			'quantity',
			'side',
			'symbol'
		]);
	});
});

describe('cleanCashForm', () => {
	it('rejects amounts below a cent and bad numbers', () => {
		expect(
			cleanCashForm(form({ action: 'DEPOSIT', amount: '0.001' })).errors.fields.amount
		).toEqual(['Ensure this value is greater than or equal to 0.01.']);
		expect(cleanCashForm(form({ action: 'DEPOSIT', amount: 'ten' })).errors.fields.amount).toEqual([
			'Enter a number.'
		]);
		expect(
			cleanCashForm(form({ action: 'WITHDRAW', amount: '1234567890123.5' })).errors.fields.amount
		).toEqual(['Ensure that there are no more than 12 digits before the decimal point.']);
	});
});

describe('validatePassword', () => {
	it('accepts a reasonable password', () => {
		expect(validatePassword('correct horse battery', ['alice', 'alice@example.com'])).toEqual([]);
	});

	it('applies the Django validators', () => {
		expect(validatePassword('1234567')).toEqual([
			'This password is too short. It must contain at least 8 characters.',
			'This password is entirely numeric.'
		]);
		expect(validatePassword('password')).toEqual(['This password is too common.']);
		expect(validatePassword('alice2026!', ['alice'])).toEqual([
			'The password is too similar to your personal information.'
		]);
	});
});
