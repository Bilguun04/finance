import { json } from '@sveltejs/kit';
import { marketSnapshot } from '#lib/server/market.ts';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async () => json(await marketSnapshot());
