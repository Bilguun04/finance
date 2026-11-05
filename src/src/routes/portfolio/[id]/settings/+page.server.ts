import { fail, redirect, type RequestEvent } from '@sveltejs/kit';
import { eq } from 'drizzle-orm';
import { db } from '#lib/server/db/index.ts';
import { portfolio } from '#lib/server/db/schema.ts';
import { flash } from '#lib/server/flash.ts';
import { values } from '#lib/server/forms.ts';
import { requireUser } from '#lib/server/guards.ts';
import { getPortfolio } from '#lib/server/portfolio.ts';
import { cleanPortfolioForm } from '#lib/server/portfolio-forms.ts';
import type { Actions, PageServerLoad } from './$types';

async function ownPortfolio(event: RequestEvent<{ id: string }>) {
	const user = requireUser(event);
	return getPortfolio(user.id, Number(event.params.id));
}

export const load: PageServerLoad = async (event) => {
	const p = await ownPortfolio(event);
	return { portfolio: { id: p.id, name: p.name, currency: p.currency, isPublic: p.isPublic } };
};

export const actions: Actions = {
	save: async (event) => {
		const p = await ownPortfolio(event);
		const data = await event.request.formData();
		// Currency is fixed once a portfolio exists; changing it would relabel every past trade.
		const form = cleanPortfolioForm(data, { withCurrency: false });
		if (form.errors.any) {
			return fail(400, { errors: form.errors.toJSON(), values: values(data) });
		}

		await db
			.update(portfolio)
			.set({ name: form.name, isPublic: form.isPublic })
			.where(eq(portfolio.id, p.id));
		flash(event.cookies, 'success', 'Portfolio settings saved.');
		redirect(303, `/portfolio/${p.id}`);
	},

	delete: async (event) => {
		const p = await ownPortfolio(event);
		// Holdings and transactions go with it (ON DELETE CASCADE).
		await db.delete(portfolio).where(eq(portfolio.id, p.id));
		flash(event.cookies, 'success', `Deleted ${p.name}.`);
		redirect(303, '/portfolio');
	}
};
