import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import type { RequestEvent } from '@sveltejs/kit';
import { getRequestEvent } from '$app/server';
import * as schema from './schema';
import { DATABASE_URL } from '$app/env/private';

if (!DATABASE_URL) throw new Error('DATABASE_URL is not set');

function connect() {
	const client = postgres(DATABASE_URL, { max: 1 });
	return { client, db: drizzle(client, { schema }) };
}

type Db = ReturnType<typeof connect>['db'];

// Cloudflare Workers can't reuse a socket across requests, so there each request gets its own
// connection, closed when the request finishes (see hooks.server.ts). Node keeps one shared pool.
const isWorkers = typeof navigator !== 'undefined' && navigator.userAgent === 'Cloudflare-Workers';

const perRequest = new WeakMap<RequestEvent, ReturnType<typeof connect>>();
let shared: Db | undefined;

function sharedDb() {
	return (shared ??= drizzle(postgres(DATABASE_URL), { schema }));
}

function currentDb(): Db {
	if (!isWorkers) return sharedDb();

	let event: RequestEvent | undefined;
	try {
		event = getRequestEvent();
	} catch {
		// Outside a request (e.g. while better-auth reads the schema at startup); no query runs here.
		return sharedDb();
	}
	let connection = perRequest.get(event);
	if (!connection) {
		connection = connect();
		perRequest.set(event, connection);
	}
	return connection.db;
}

/** Closes the request's connection on Workers. Called once the response is ready. */
export function releaseDb(event: RequestEvent) {
	const connection = perRequest.get(event);
	if (!connection) return;
	perRequest.delete(event);
	const closing = connection.client.end();
	const ctx = (event.platform as { ctx?: { waitUntil(p: Promise<unknown>): void } } | undefined)
		?.ctx;
	ctx?.waitUntil(closing);
}

export const db = new Proxy({} as Db, {
	get(_, prop) {
		const target = currentDb();
		const value = Reflect.get(target, prop, target);
		return typeof value === 'function' ? value.bind(target) : value;
	}
});
