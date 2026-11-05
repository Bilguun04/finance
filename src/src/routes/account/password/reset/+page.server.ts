import { fail, redirect } from '@sveltejs/kit';
import { auth } from '#lib/server/auth.ts';
import { Errors, REQUIRED, text } from '#lib/server/forms.ts';
import type { Actions } from './$types';

export const actions: Actions = {
	default: async ({ request }) => {
		const data = await request.formData();
		const email = text(data, 'email');
		const errors = new Errors();
		if (!email) errors.add('email', REQUIRED);
		if (errors.any) return fail(400, { errors: errors.toJSON(), values: { email } });

		// Succeeds whether or not the account exists, so the form can't be used to discover emails.
		await auth.api.requestPasswordReset({ body: { email, redirectTo: '/account/reset/confirm' } });
		redirect(303, '/account/password/reset/done');
	}
};
