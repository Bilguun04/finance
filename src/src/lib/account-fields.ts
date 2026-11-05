import type { CardField } from '#lib/types.ts';

export const PASSWORD_HELP = [
	'Your password can’t be too similar to your other personal information.',
	'Your password must contain at least 8 characters.',
	'Your password can’t be a commonly used password.',
	'Your password can’t be entirely numeric.'
];

/** The "new password" + confirmation pair used by password change and reset. */
export const NEW_PASSWORD_FIELDS: CardField[] = [
	{
		name: 'new_password1',
		label: 'New password',
		type: 'password',
		autocomplete: 'new-password',
		help: PASSWORD_HELP
	},
	{
		name: 'new_password2',
		label: 'New password confirmation',
		type: 'password',
		autocomplete: 'new-password'
	}
];
