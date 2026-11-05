import { aliasedTable, and, asc, count, eq, inArray, or } from 'drizzle-orm';
import { db } from '#lib/server/db/index.ts';
import { friendRequest, portfolio, user } from '#lib/server/db/schema.ts';
import { displayName } from '#lib/server/guards.ts';

export class FriendshipError extends Error {}

export type Person = { id: string; username: string };
export type Relationship = 'self' | 'friends' | 'sent' | 'received' | null;

const person = (u: typeof user.$inferSelect): Person => ({ id: u.id, username: displayName(u) });

const between = (a: string, b: string) =>
	or(
		and(eq(friendRequest.fromUserId, a), eq(friendRequest.toUserId, b)),
		and(eq(friendRequest.fromUserId, b), eq(friendRequest.toUserId, a))
	);

const accepted = eq(friendRequest.status, 'ACCEPTED');
const pending = eq(friendRequest.status, 'PENDING');

/** Usernames are stored lowercased by better-auth, so lookups are case-insensitive. */
export async function findUser(username: string) {
	if (!username) return null;
	const [row] = await db.select().from(user).where(eq(user.username, username.toLowerCase()));
	return row ? person(row) : null;
}

/** How `userId` relates to `other`. */
export async function relationship(userId: string, other: Person): Promise<Relationship> {
	if (userId === other.id) return 'self';
	const [request] = await db.select().from(friendRequest).where(between(userId, other.id)).limit(1);
	if (!request) return null;
	if (request.status === 'ACCEPTED') return 'friends';
	return request.fromUserId === userId ? 'sent' : 'received';
}

export async function friendship(userId: string, otherId: string) {
	const [row] = await db
		.select()
		.from(friendRequest)
		.where(and(between(userId, otherId), accepted))
		.limit(1);
	return row ?? null;
}

/** Friends ordered by username, each with how many portfolios they share. */
export async function friendsOf(userId: string) {
	const rows = await db
		.select({ from: friendRequest.fromUserId, to: friendRequest.toUserId })
		.from(friendRequest)
		.where(
			and(accepted, or(eq(friendRequest.fromUserId, userId), eq(friendRequest.toUserId, userId)))
		);
	const ids = rows.map((r) => (r.from === userId ? r.to : r.from));
	if (!ids.length) return [];

	const friends = await db
		.select({ user, sharedCount: count(portfolio.id) })
		.from(user)
		.leftJoin(portfolio, and(eq(portfolio.userId, user.id), eq(portfolio.isPublic, true)))
		.where(inArray(user.id, ids))
		.groupBy(user.id)
		.orderBy(asc(user.username));
	return friends.map((f) => ({ ...person(f.user), sharedCount: f.sharedCount }));
}

const otherUser = aliasedTable(user, 'other_user');

export async function incomingRequests(userId: string) {
	const rows = await db
		.select({ request: friendRequest, from: otherUser })
		.from(friendRequest)
		.innerJoin(otherUser, eq(otherUser.id, friendRequest.fromUserId))
		.where(and(eq(friendRequest.toUserId, userId), pending))
		.orderBy(asc(friendRequest.createdAt));
	return rows.map((r) => ({
		id: r.request.id,
		createdAt: r.request.createdAt,
		from: person(r.from)
	}));
}

export async function outgoingRequests(userId: string) {
	const rows = await db
		.select({ request: friendRequest, to: otherUser })
		.from(friendRequest)
		.innerJoin(otherUser, eq(otherUser.id, friendRequest.toUserId))
		.where(and(eq(friendRequest.fromUserId, userId), pending))
		.orderBy(asc(friendRequest.createdAt));
	return rows.map((r) => ({ id: r.request.id, createdAt: r.request.createdAt, to: person(r.to) }));
}

/** Sends a request, or accepts theirs if `to` already asked `fromId`. Returns the resulting status. */
export async function sendRequest(fromId: string, to: Person): Promise<'PENDING' | 'ACCEPTED'> {
	if (fromId === to.id) throw new FriendshipError("You can't add yourself as a friend.");

	return db.transaction(async (tx) => {
		const [existing] = await tx
			.select()
			.from(friendRequest)
			.where(between(fromId, to.id))
			.limit(1)
			.for('update');

		if (!existing) {
			const inserted = await tx
				.insert(friendRequest)
				.values({ fromUserId: fromId, toUserId: to.id })
				.onConflictDoNothing()
				.returning({ id: friendRequest.id });
			// Lost a race with an identical request sent at the same moment.
			if (!inserted.length) throw new FriendshipError(`You already sent ${to.username} a request.`);
			return 'PENDING';
		}
		if (existing.status === 'ACCEPTED') {
			throw new FriendshipError(`You're already friends with ${to.username}.`);
		}
		if (existing.fromUserId === fromId) {
			throw new FriendshipError(`You already sent ${to.username} a request.`);
		}
		await tx
			.update(friendRequest)
			.set({ status: 'ACCEPTED', respondedAt: new Date() })
			.where(eq(friendRequest.id, existing.id));
		return 'ACCEPTED';
	});
}

const GONE = 'That friend request no longer exists.';

export async function acceptRequest(userId: string, requestId: number) {
	const updated = await db
		.update(friendRequest)
		.set({ status: 'ACCEPTED', respondedAt: new Date() })
		.where(and(eq(friendRequest.id, requestId), eq(friendRequest.toUserId, userId), pending))
		.returning({ id: friendRequest.id });
	if (!updated.length) throw new FriendshipError(GONE);
}

export async function declineRequest(userId: string, requestId: number) {
	const deleted = await db
		.delete(friendRequest)
		.where(and(eq(friendRequest.id, requestId), eq(friendRequest.toUserId, userId), pending))
		.returning({ id: friendRequest.id });
	if (!deleted.length) throw new FriendshipError(GONE);
}

export async function cancelRequest(userId: string, requestId: number) {
	const deleted = await db
		.delete(friendRequest)
		.where(and(eq(friendRequest.id, requestId), eq(friendRequest.fromUserId, userId), pending))
		.returning({ id: friendRequest.id });
	if (!deleted.length) throw new FriendshipError(GONE);
}

export async function unfriend(userId: string, other: Person) {
	const deleted = await db
		.delete(friendRequest)
		.where(and(between(userId, other.id), accepted))
		.returning({ id: friendRequest.id });
	if (!deleted.length) throw new FriendshipError(`You're not friends with ${other.username}.`);
}
