import { listSessions } from '#lib/server/bankroll.ts';
import { SESSION_FORMATS } from '#lib/server/db/schema.ts';
import { requireUser } from '#lib/server/guards.ts';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
	const user = requireUser(event);
	const sessions = (await listSessions(user.id)).map((s) => ({
		id: s.id,
		host: s.host,
		type: s.type,
		stakes: s.stakes,
		format: SESSION_FORMATS[s.format] ?? s.format,
		sessionStart: s.sessionStart,
		buyin: s.buyin,
		buyout: s.buyout,
		profit: s.buyout - s.buyin
	}));

	const totalBuyin = sessions.reduce((sum, s) => sum + s.buyin, 0);
	const totalBuyout = sessions.reduce((sum, s) => sum + s.buyout, 0);

	return {
		sessions,
		totalSessions: sessions.length,
		totalBuyin,
		totalBuyout,
		netProfit: totalBuyout - totalBuyin,
		winningSessions: sessions.filter((s) => s.profit > 0).length
	};
};
