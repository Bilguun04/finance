import { ORIGIN, BETTER_AUTH_SECRET } from '$app/env/private';
import { betterAuth } from 'better-auth/minimal';
import { drizzleAdapter } from 'better-auth/adapters/drizzle';
import { username } from 'better-auth/plugins';
import { sveltekitCookies } from 'better-auth/svelte-kit';
import { getRequestEvent } from '$app/server';
import { db } from '#lib/server/db/index.ts';
import { USERNAME_MAX_LENGTH, USERNAME_PATTERN } from '#lib/server/passwords.ts';

export const auth = betterAuth({
	baseURL: ORIGIN,
	secret: BETTER_AUTH_SECRET,
	database: drizzleAdapter(db, { provider: 'pg' }),
	emailAndPassword: {
		enabled: true,
		minPasswordLength: 8,
		revokeSessionsOnPasswordReset: true,
		// Like Django's console email backend: print the email instead of sending it.
		// Swap this for a real email provider before going to production.
		sendResetPassword: async ({ user, url }) => {
			console.info(
				[
					`To: ${user.email}`,
					'Subject: Reset your Finance Tracker password',
					'',
					`Hi ${user.name},`,
					'',
					'We received a request to reset the password for your Finance Tracker account.',
					'',
					'Choose a new password here:',
					url,
					'',
					"If you didn't request this, you can ignore this email; your password won't change."
				].join('\n')
			);
		}
	},
	plugins: [
		// Same rules as Django's username field: up to 150 letters, digits and @/./+/-/_.
		username({
			minUsernameLength: 1,
			maxUsernameLength: USERNAME_MAX_LENGTH,
			usernameValidator: (value) => USERNAME_PATTERN.test(value)
		}),
		sveltekitCookies(getRequestEvent) // make sure this is the last plugin in the array
	]
});

export type AuthUser = typeof auth.$Infer.Session.user;
