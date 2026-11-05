import { consumeFlash } from '#lib/server/flash.ts';
import { displayName } from '#lib/server/guards.ts';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = ({ locals, cookies, url }) => {
	// Reading the pathname re-runs this load on every navigation, so flash messages show once and then clear.
	const pathname = String(url.pathname);

	return {
		user: locals.user
			? {
					username: displayName(locals.user),
					email: locals.user.email,
					createdAt: locals.user.createdAt
				}
			: null,
		messages: consumeFlash(cookies)
	};
};
