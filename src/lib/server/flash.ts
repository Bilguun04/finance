import type { Cookies } from '@sveltejs/kit';
import type { FlashMessage } from '#lib/types.ts';

// One-time messages shown after a redirect, like Django's messages framework with cookie storage.

const COOKIE = 'flash';

export function flash(cookies: Cookies, level: FlashMessage['level'], text: string) {
	const messages = [...readFlash(cookies), { level, text }];
	cookies.set(COOKIE, JSON.stringify(messages), {
		path: '/',
		httpOnly: true,
		sameSite: 'lax',
		maxAge: 60
	});
}

function readFlash(cookies: Cookies): FlashMessage[] {
	const raw = cookies.get(COOKIE);
	if (!raw) return [];
	try {
		const parsed = JSON.parse(raw);
		return Array.isArray(parsed) ? parsed : [];
	} catch {
		return [];
	}
}

/** Returns pending messages and clears them so they show only once. */
export function consumeFlash(cookies: Cookies): FlashMessage[] {
	const messages = readFlash(cookies);
	if (messages.length) cookies.delete(COOKIE, { path: '/' });
	return messages;
}
