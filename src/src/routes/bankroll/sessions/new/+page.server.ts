import { fail, redirect } from '@sveltejs/kit';
import { cleanSessionForm, sessionValues } from '#lib/server/bankroll.ts';
import { db } from '#lib/server/db/index.ts';
import { bankrollSession } from '#lib/server/db/schema.ts';
import { values } from '#lib/server/forms.ts';
import { requireUser } from '#lib/server/guards.ts';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = (event) => {
	requireUser(event);
};

export const actions: Actions = {
	default: async (event) => {
		const user = requireUser(event);
		const data = await event.request.formData();
		const { errors, fields } = cleanSessionForm(data);
		if (errors.any) return fail(400, { errors: errors.toJSON(), values: values(data) });

		await db.insert(bankrollSession).values({ ...sessionValues(fields), userId: user.id });
		redirect(303, '/bankroll');
	}
};
