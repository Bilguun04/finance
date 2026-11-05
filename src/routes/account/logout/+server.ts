import { redirect } from '@sveltejs/kit';
import { auth } from '#lib/server/auth.ts';
import type { RequestHandler } from './$types';

// POST only, like Django's LogoutView. SvelteKit's origin check guards this form post against CSRF.
export const POST: RequestHandler = async ({ request, locals }) => {
	if (locals.session) await auth.api.signOut({ headers: request.headers });
	redirect(303, '/');
};
