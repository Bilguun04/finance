import { redirect, type RequestEvent } from '@sveltejs/kit';

export const LOGIN_URL = '/account/login';
export const LOGIN_REDIRECT_URL = '/portfolio';

/** Like Django's @login_required: sends anonymous users to the login page, then back here. */
export function requireUser(event: RequestEvent) {
	const user = event.locals.user;
	if (!user) {
		const next = event.url.pathname + event.url.search;
		redirect(
			event.request.method === 'GET' ? 302 : 303,
			`${LOGIN_URL}?next=${encodeURIComponent(next)}`
		);
	}
	return user;
}

/** Only allow same-site paths as a post-login redirect, never another origin. */
export function safeNext(next: string | null | undefined): string {
	if (next && next.startsWith('/') && !next.startsWith('//') && !next.startsWith('/\\')) {
		return next;
	}
	return LOGIN_REDIRECT_URL;
}

export function displayName(user: {
	username?: string | null;
	displayUsername?: string | null;
	name: string;
}) {
	return user.displayUsername || user.username || user.name;
}
