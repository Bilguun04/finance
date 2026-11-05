import { fail, type RequestEvent } from '@sveltejs/kit';
import { money } from '#lib/format.ts';
import { values, type Errors } from '#lib/server/forms.ts';
import { requireUser } from '#lib/server/guards.ts';
import {
	addCash,
	buy,
	getPortfolio,
	portfolioBody,
	refreshMarketValues,
	removeCash,
	sell,
	TradeError
} from '#lib/server/portfolio.ts';
import { cleanCashForm, cleanTradeForm } from '#lib/server/portfolio-forms.ts';
import { trim } from '#lib/server/portfolio-math.ts';
import type { Actions, PageServerLoad } from './$types';

async function ownPortfolio(event: RequestEvent<{ id: string }>) {
	const user = requireUser(event);
	return getPortfolio(user.id, Number(event.params.id));
}

export const load: PageServerLoad = async (event) => portfolioBody(await ownPortfolio(event));

/** A failed submission of one of the two panels; the page refills that panel and shows its errors. */
const failed = (form: 'trade' | 'cash', data: FormData, errors: Errors) =>
	fail(400, { form, errors: errors.toJSON(), values: values(data) });

export const actions: Actions = {
	trade: async (event) => {
		const p = await ownPortfolio(event);
		const data = await event.request.formData();
		const { errors, side, trade, useCash } = cleanTradeForm(data);
		if (errors.any) return failed('trade', data, errors);

		try {
			if (side === 'BUY') await buy(p.id, trade, useCash);
			else await sell(p.id, trade);
		} catch (error) {
			if (!(error instanceof TradeError)) throw error;
			errors.nonField.push(error.message);
			return failed('trade', data, errors);
		}

		const verb = side === 'BUY' ? 'Bought' : 'Sold';
		return {
			notice: `${verb} ${trim(trade.quantity)} ${trade.symbol} at $${money(trade.price.toNumber())}.`
		};
	},

	cash: async (event) => {
		const p = await ownPortfolio(event);
		const data = await event.request.formData();
		const { errors, action, amount } = cleanCashForm(data);
		if (errors.any) return failed('cash', data, errors);

		try {
			if (action === 'DEPOSIT') await addCash(p.id, amount);
			else await removeCash(p.id, amount);
		} catch (error) {
			if (!(error instanceof TradeError)) throw error;
			errors.nonField.push(error.message);
			return failed('cash', data, errors);
		}

		const verb = action === 'DEPOSIT' ? 'Deposited' : 'Withdrew';
		return { notice: `${verb} $${money(amount.toNumber())}.` };
	},

	refresh: async (event) => {
		const p = await ownPortfolio(event);
		await refreshMarketValues(p.id);
		return { notice: 'Prices refreshed.' };
	}
};
