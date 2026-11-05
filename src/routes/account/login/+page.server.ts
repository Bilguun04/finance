import { fail, redirect } from '@sveltejs/kit';
import { APIError } from 'better-auth/api';
import { auth } from '#lib/server/auth.ts';
import { Errors, REQUIRED, text } from '#lib/server/forms.ts';
import { safeNext } from '#lib/server/guards.ts';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = ({ locals, url }) => {
	if (locals.user) redirect(302, safeNext(url.searchParams.get('next')));
	return { next: url.searchParams.get('next') ?? '' };
};

export const actions: Actions = {
	default: async ({ request }) => {
		const data = await request.formData();
		const username = text(data, 'username');
		const password = data.get('password')?.toString() ?? '';
		const next = safeNext(text(data, 'next'));

		const errors = new Errors();
		if (!username) errors.add('username', REQUIRED);
		if (!password) errors.add('password', REQUIRED);

		if (!errors.any) {
			try {
				await auth.api.signInUsername({ body: { username, password } });
			} catch (error) {
				if (!(error instanceof APIError)) throw error;
				errors.nonField.push(
					'Please enter a correct username and password. Note that both fields may be case-sensitive.'
				);
			}
		}

		if (errors.any) return fail(400, { errors: errors.toJSON(), values: { username } });
		redirect(303, next);
	}
};
