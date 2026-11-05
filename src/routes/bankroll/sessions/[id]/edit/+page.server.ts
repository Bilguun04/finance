import { fail, redirect } from '@sveltejs/kit';
import { eq } from 'drizzle-orm';
import { dateTimeLocal } from '#lib/format.ts';
import { cleanSessionForm, getSession, sessionValues } from '#lib/server/bankroll.ts';
import { db } from '#lib/server/db/index.ts';
import { bankrollSession } from '#lib/server/db/schema.ts';
import { values } from '#lib/server/forms.ts';
import { requireUser } from '#lib/server/guards.ts';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
	const user = requireUser(event);
	const s = await getSession(user.id, Number(event.params.id));
	return {
		initial: {
			host: s.host,
			format: s.format,
			type: s.type ?? '',
			stakes: s.stakes,
			session_start: dateTimeLocal(s.sessionStart),
			session_end: dateTimeLocal(s.sessionEnd),
			buyin: String(s.buyin),
			buyout: String(s.buyout)
		}
	};
};

export const actions: Actions = {
	default: async (event) => {
		const user = requireUser(event);
		const s = await getSession(user.id, Number(event.params.id));
		const data = await event.request.formData();
		const { errors, fields } = cleanSessionForm(data);
		if (errors.any) return fail(400, { errors: errors.toJSON(), values: values(data) });

		await db.update(bankrollSession).set(sessionValues(fields)).where(eq(bankrollSession.id, s.id));
		redirect(303, '/bankroll');
	}
};
