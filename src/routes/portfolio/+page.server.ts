import { fail, redirect } from '@sveltejs/kit';
import { db } from '#lib/server/db/index.ts';
import { portfolio } from '#lib/server/db/schema.ts';
import { flash } from '#lib/server/flash.ts';
import { values } from '#lib/server/forms.ts';
import { requireUser } from '#lib/server/guards.ts';
import { listPortfolios } from '#lib/server/portfolio.ts';
import { cleanPortfolioForm } from '#lib/server/portfolio-forms.ts';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
	const user = requireUser(event);
	const portfolios = await listPortfolios(user.id);
	return {
		portfolios,
		totalNetLiquidity: portfolios.reduce((sum, p) => sum + p.netLiquidity, 0),
		totalCash: portfolios.reduce((sum, p) => sum + p.cash, 0)
	};
};

export const actions: Actions = {
	default: async (event) => {
		const user = requireUser(event);
		const data = await event.request.formData();
		const form = cleanPortfolioForm(data, { withCurrency: true });
		if (form.errors.any) {
			return fail(400, { errors: form.errors.toJSON(), values: values(data) });
		}

		const [created] = await db
			.insert(portfolio)
			.values({
				userId: user.id,
				name: form.name,
				currency: form.currency,
				isPublic: form.isPublic
			})
			.returning({ id: portfolio.id, name: portfolio.name });

		flash(event.cookies, 'success', `Created ${created.name}. Deposit some cash to start trading.`);
		redirect(303, `/portfolio/${created.id}`);
	}
};
