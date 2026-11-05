// Mirrors Django's username field and AUTH_PASSWORD_VALIDATORS so accounts follow the same rules as before.

export const USERNAME_MAX_LENGTH = 150;
export const USERNAME_PATTERN = /^[\p{L}\p{N}_.@+-]+$/u;

export const PASSWORD_MIN_LENGTH = 8;
// A short list of the most common passwords; Django ships ~20k, this catches the obvious ones.
const COMMON_PASSWORDS = new Set([
	'password',
	'password1',
	'password123',
	'12345678',
	'123456789',
	'1234567890',
	'qwerty123',
	'qwertyuiop',
	'iloveyou',
	'sunshine',
	'princess',
	'football',
	'baseball',
	'welcome1',
	'welcome123',
	'letmein1',
	'trustno1',
	'superman',
	'starwars',
	'passw0rd',
	'abc12345',
	'11111111',
	'00000000',
	'monkey123',
	'dragon123',
	'admin123',
	'whatever',
	'computer'
]);

/** Returns Django-style error messages; empty when the password is acceptable. */
export function validatePassword(password: string, personal: string[] = []): string[] {
	const errors: string[] = [];
	const lowered = password.toLowerCase();

	for (const value of personal) {
		// Django compares with a similarity ratio; a substring check covers the realistic cases.
		const attribute = value.toLowerCase().split('@')[0];
		if (attribute.length >= 3 && (lowered.includes(attribute) || attribute.includes(lowered))) {
			errors.push('The password is too similar to your personal information.');
			break;
		}
	}
	if (password.length < PASSWORD_MIN_LENGTH) {
		errors.push(
			`This password is too short. It must contain at least ${PASSWORD_MIN_LENGTH} characters.`
		);
	}
	if (COMMON_PASSWORDS.has(lowered)) errors.push('This password is too common.');
	if (/^\d+$/.test(password)) errors.push('This password is entirely numeric.');
	return errors;
}
