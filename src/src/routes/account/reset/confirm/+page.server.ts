import { fail, redirect } from '@sveltejs/kit';
import { APIError } from 'better-auth/api';
import { auth } from '#lib/server/auth.ts';
import { Errors, REQUIRED } from '#lib/server/forms.ts';
import { validatePassword } from '#lib/server/passwords.ts';
import type { Actions, PageServerLoad } from './$types';

// The emailed link goes through better-auth's /api/auth/reset-password/:token, which checks the token
// and lands here with either ?token=... or ?error=INVALID_TOKEN.
export const load: PageServerLoad = ({ url }) => {
	const token = url.searchParams.get('token');
	return { validLink: Boolean(token) && !url.searchParams.has('error') };
};

export const actions: Actions = {
	default: async ({ request, url }) => {
		const token = url.searchParams.get('token') ?? '';
		const data = await request.formData();
		const password1 = data.get('new_password1')?.toString() ?? '';
		const password2 = data.get('new_password2')?.toString() ?? '';
		const errors = new Errors();

		if (!password1) errors.add('new_password1', REQUIRED);
		if (!password2) errors.add('new_password2', REQUIRED);
		if (password1 && password2) {
			if (password1 !== password2) {
				errors.add('new_password2', 'The two password fields didn’t match.');
			} else {
				for (const error of validatePassword(password2)) errors.add('new_password2', error);
			}
		}
		if (errors.any) return fail(400, { errors: errors.toJSON(), values: {}, expired: false });

		try {
			await auth.api.resetPassword({ body: { newPassword: password1, token } });
		} catch (error) {
			if (!(error instanceof APIError)) throw error;
			return fail(400, { errors: errors.toJSON(), values: {}, expired: true });
		}
		redirect(303, '/account/reset/done');
	}
};
