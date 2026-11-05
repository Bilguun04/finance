import { fail, redirect } from '@sveltejs/kit';
import { APIError } from 'better-auth/api';
import { eq, sql } from 'drizzle-orm';
import { auth } from '#lib/server/auth.ts';
import { db } from '#lib/server/db/index.ts';
import { user } from '#lib/server/db/schema.ts';
import { Errors, REQUIRED, text } from '#lib/server/forms.ts';
import { LOGIN_REDIRECT_URL } from '#lib/server/guards.ts';
import { USERNAME_MAX_LENGTH, USERNAME_PATTERN, validatePassword } from '#lib/server/passwords.ts';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = ({ locals }) => {
	if (locals.user) redirect(302, LOGIN_REDIRECT_URL);
};

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export const actions: Actions = {
	default: async ({ request }) => {
		const data = await request.formData();
		const username = text(data, 'username');
		const email = text(data, 'email');
		const password1 = data.get('password1')?.toString() ?? '';
		const password2 = data.get('password2')?.toString() ?? '';
		const errors = new Errors();

		if (!username) errors.add('username', REQUIRED);
		else if (username.length > USERNAME_MAX_LENGTH) {
			errors.add(
				'username',
				`Ensure this value has at most ${USERNAME_MAX_LENGTH} characters (it has ${username.length}).`
			);
		} else if (!USERNAME_PATTERN.test(username)) {
			errors.add(
				'username',
				'Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters.'
			);
		} else if (
			(await db.select({ id: user.id }).from(user).where(eq(user.username, username.toLowerCase())))
				.length
		) {
			errors.add('username', 'A user with that username already exists.');
		}

		if (!email) errors.add('email', REQUIRED);
		else if (!EMAIL_PATTERN.test(email)) errors.add('email', 'Enter a valid email address.');
		else if (
			(
				await db
					.select({ id: user.id })
					.from(user)
					.where(sql`lower(${user.email}) = ${email.toLowerCase()}`)
			).length
		) {
			errors.add('email', 'An account with this email already exists.');
		}

		if (!password1) errors.add('password1', REQUIRED);
		if (!password2) errors.add('password2', REQUIRED);
		if (password1 && password2) {
			if (password1 !== password2) {
				errors.add('password2', 'The two password fields didn’t match.');
			} else {
				for (const error of validatePassword(password2, [username, email])) {
					errors.add('password2', error);
				}
			}
		}

		if (!errors.any) {
			try {
				// Signs the new user in too, like Django's register view did.
				await auth.api.signUpEmail({
					body: { email, password: password1, name: username, username, displayUsername: username }
				});
			} catch (error) {
				if (!(error instanceof APIError)) throw error;
				errors.nonField.push(error.message || 'Registration failed.');
			}
		}

		if (errors.any) {
			return fail(400, { errors: errors.toJSON(), values: { username, email } });
		}
		redirect(303, LOGIN_REDIRECT_URL);
	}
};
