import { and, desc, eq } from 'drizzle-orm';
import { error } from '@sveltejs/kit';
import { db } from '#lib/server/db/index.ts';
import { bankrollSession, SESSION_FORMATS, type SessionFormat } from '#lib/server/db/schema.ts';
import { charField, choiceField, dateTimeField, Errors, integerField } from '#lib/server/forms.ts';

export function cleanSessionForm(data: FormData) {
	const errors = new Errors();
	const fields = {
		host: charField(data, 'host', errors, { maxLength: 100 }),
		format: choiceField(data, 'format', errors, Object.keys(SESSION_FORMATS) as SessionFormat[]),
		type: charField(data, 'type', errors, { maxLength: 100, required: false }) || null,
		stakes: charField(data, 'stakes', errors, { maxLength: 100 }),
		sessionStart: dateTimeField(data, 'session_start', errors),
		sessionEnd: dateTimeField(data, 'session_end', errors),
		buyin: integerField(data, 'buyin', errors, { min: 0 }),
		buyout: integerField(data, 'buyout', errors, { min: 0 })
	};
	return { errors, fields };
}

/** The validated fields, ready to save. Only call when `errors.any` is false. */
export function sessionValues(fields: ReturnType<typeof cleanSessionForm>['fields']) {
	return { ...fields, sessionStart: fields.sessionStart!, sessionEnd: fields.sessionEnd! };
}

export async function listSessions(userId: string) {
	return db
		.select()
		.from(bankrollSession)
		.where(eq(bankrollSession.userId, userId))
		.orderBy(desc(bankrollSession.sessionStart));
}

/** Scoped to the owner, like portfolios. */
export async function getSession(userId: string, id: number) {
	const [row] = Number.isSafeInteger(id)
		? await db
				.select()
				.from(bankrollSession)
				.where(and(eq(bankrollSession.id, id), eq(bankrollSession.userId, userId)))
		: [];
	if (!row) error(404, 'Not found');
	return row;
}
