import { error, redirect, type RequestEvent } from '@sveltejs/kit';
import { asc, eq, and } from 'drizzle-orm';
import { db } from '#lib/server/db/index.ts';
import { holding, portfolio } from '#lib/server/db/schema.ts';
import { flash } from '#lib/server/flash.ts';
import { requireUser } from '#lib/server/guards.ts';
import { allocation, Decimal } from '#lib/server/portfolio-math.ts';
import { findUser, friendship, FriendshipError, unfriend } from '#lib/server/social.ts';
import type { Actions, PageServerLoad } from './$types';

async function findFriend(event: RequestEvent<{ username: string }>) {
	const user = requireUser(event);
	const friend = await findUser(event.params.username);
	const link = friend ? await friendship(user.id, friend.id) : null;
	// 404 rather than 403 so non-friends can't tell what's behind the page.
	if (!friend || !link) error(404, 'Not found');
	return { user, friend, link };
}

export const load: PageServerLoad = async (event) => {
	const { friend, link } = await findFriend(event);

	const portfolios = await db
		.select()
		.from(portfolio)
		.where(and(eq(portfolio.userId, friend.id), eq(portfolio.isPublic, true)))
		.orderBy(asc(portfolio.createdAt));

	// Percentages only, never dollar amounts.
	const shared = await Promise.all(
		portfolios.map(async (p) => {
			const holdings = await db
				.select({ symbol: holding.symbol, marketValue: holding.marketValue })
				.from(holding)
				.where(eq(holding.portfolioId, p.id));
			return {
				portfolio: { id: p.id, name: p.name, currency: p.currency },
				...allocation(
					new Decimal(p.cash),
					holdings.map((h) => ({ symbol: h.symbol, marketValue: new Decimal(h.marketValue) }))
				)
			};
		})
	);

	return { friend, friendsSince: link.respondedAt, shared };
};

export const actions: Actions = {
	unfriend: async (event) => {
		const { user, friend } = await findFriend(event);
		try {
			await unfriend(user.id, friend);
			flash(event.cookies, 'success', `You're no longer friends with ${friend.username}.`);
		} catch (err) {
			if (!(err instanceof FriendshipError)) throw err;
			flash(event.cookies, 'error', err.message);
		}
		redirect(303, '/social');
	}
};
