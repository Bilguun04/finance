import { json } from '@sveltejs/kit';
import { marketPulse } from '#lib/server/market.ts';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async () => json(await marketPulse());
