import { redirect } from '@sveltejs/kit';
import { changeLabel } from '#lib/market-status.ts';
import { LOGIN_REDIRECT_URL } from '#lib/server/guards.ts';
import { getMarketStatus, QUOTE_CACHE_SECONDS } from '#lib/server/market.ts';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
	if (locals.user) redirect(302, LOGIN_REDIRECT_URL);

	const marketStatus = await getMarketStatus();
	return {
		refreshSeconds: QUOTE_CACHE_SECONDS,
		marketStatus,
		changeLabel: changeLabel(marketStatus)
	};
};
