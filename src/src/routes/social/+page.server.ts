import { error, redirect, type RequestEvent } from '@sveltejs/kit';
import { flash } from '#lib/server/flash.ts';
import { text } from '#lib/server/forms.ts';
import { requireUser } from '#lib/server/guards.ts';
import {
	acceptRequest,
	cancelRequest,
	declineRequest,
	findUser,
	friendsOf,
	FriendshipError,
	incomingRequests,
	outgoingRequests,
	relationship,
	sendRequest
} from '#lib/server/social.ts';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
	const user = requireUser(event);
	const query = (event.url.searchParams.get('q') ?? '').trim();
	// Exact (case-insensitive) match only, so nobody can browse the user list by typing partial names.
	const match = query ? await findUser(query) : null;

	const [matchRelationship, incoming, outgoing, friends] = await Promise.all([
		match ? relationship(user.id, match) : null,
		incomingRequests(user.id),
		outgoingRequests(user.id),
		friendsOf(user.id)
	]);

	return { query, match, matchRelationship, incoming, outgoing, friends };
};

/** Return to the friends page, keeping the search the action was made from. */
function backToFriends(query: string): never {
	redirect(303, query ? `/social?${new URLSearchParams({ q: query })}` : '/social');
}

/** Runs a request action (accept/decline/cancel) on the posted request id. */
function requestAction(
	action: (userId: string, requestId: number) => Promise<void>,
	successMessage: string
) {
	return async (event: RequestEvent) => {
		const user = requireUser(event);
		const data = await event.request.formData();
		try {
			await action(user.id, Number(text(data, 'id')));
			flash(event.cookies, 'success', successMessage);
		} catch (err) {
			if (!(err instanceof FriendshipError)) throw err;
			flash(event.cookies, 'error', err.message);
		}
		backToFriends(text(data, 'q'));
	};
}

export const actions: Actions = {
	send: async (event) => {
		const user = requireUser(event);
		const data = await event.request.formData();
		const to = await findUser(text(data, 'username'));
		if (!to) error(404, 'Not found');

		try {
			const status = await sendRequest(user.id, to);
			flash(
				event.cookies,
				'success',
				status === 'ACCEPTED'
					? `${to.username} had already asked you. You're now friends!`
					: `Friend request sent to ${to.username}.`
			);
		} catch (err) {
			if (!(err instanceof FriendshipError)) throw err;
			flash(event.cookies, 'error', err.message);
		}
		backToFriends(text(data, 'q'));
	},
	accept: requestAction(acceptRequest, 'Friend request accepted.'),
	decline: requestAction(declineRequest, 'Friend request declined.'),
	cancel: requestAction(cancelRequest, 'Friend request cancelled.')
};
