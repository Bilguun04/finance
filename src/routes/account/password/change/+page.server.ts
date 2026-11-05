import { fail, redirect } from '@sveltejs/kit';
import { APIError } from 'better-auth/api';
import { auth } from '#lib/server/auth.ts';
import { Errors, REQUIRED } from '#lib/server/forms.ts';
import { displayName, requireUser } from '#lib/server/guards.ts';
import { validatePassword } from '#lib/server/passwords.ts';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = (event) => {
	requireUser(event);
};

export const actions: Actions = {
	default: async (event) => {
		const user = requireUser(event);
		const data = await event.request.formData();
		const oldPassword = data.get('old_password')?.toString() ?? '';
		const password1 = data.get('new_password1')?.toString() ?? '';
		const password2 = data.get('new_password2')?.toString() ?? '';
		const errors = new Errors();

		if (!oldPassword) errors.add('old_password', REQUIRED);
		if (!password1) errors.add('new_password1', REQUIRED);
		if (!password2) errors.add('new_password2', REQUIRED);
		if (password1 && password2) {
			if (password1 !== password2) {
				errors.add('new_password2', 'The two password fields didn’t match.');
			} else {
				for (const error of validatePassword(password2, [displayName(user), user.email])) {
					errors.add('new_password2', error);
				}
			}
		}

		if (!errors.any) {
			try {
				// Keeps this session signed in and signs out everywhere else, like Django's update_session_auth_hash.
				await auth.api.changePassword({
					headers: event.request.headers,
					body: { currentPassword: oldPassword, newPassword: password1, revokeOtherSessions: true }
				});
			} catch (error) {
				if (!(error instanceof APIError)) throw error;
				errors.add(
					'old_password',
					'Your old password was entered incorrectly. Please enter it again.'
				);
			}
		}

		if (errors.any) return fail(400, { errors: errors.toJSON(), values: {} });
		redirect(303, '/account/password/change/done');
	}
};
