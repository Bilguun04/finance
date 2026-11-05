<script lang="ts">
	import { resolve } from '$app/paths';
	import FormCard from '#lib/components/FormCard.svelte';
	import { PASSWORD_HELP } from '#lib/account-fields.ts';
	import type { CardField } from '#lib/types.ts';
	import type { PageProps } from './$types';

	let { form }: PageProps = $props();

	const fields: CardField[] = [
		{
			name: 'username',
			label: 'Username',
			autocomplete: 'username',
			maxlength: 150,
			help: 'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
		},
		{ name: 'email', label: 'Email', type: 'email', autocomplete: 'email' },
		{
			name: 'password1',
			label: 'Password',
			type: 'password',
			autocomplete: 'new-password',
			help: PASSWORD_HELP
		},
		{
			name: 'password2',
			label: 'Password confirmation',
			type: 'password',
			autocomplete: 'new-password',
			help: 'Enter the same password as before, for verification.'
		}
	];
</script>

<svelte:head>
	<title>Sign up | Finance Tracker</title>
</svelte:head>

<div class="mt-8 grid gap-8 lg:grid-cols-2 lg:items-center">
	<section class="hidden overflow-hidden rounded-lg lg:block">
		<img
			class="h-full min-h-140 w-full object-cover"
			src="/asset/signup.jpg"
			alt="A welcoming workspace for managing your finances"
		/>
	</section>
	<section class="mx-auto">
		<div class="mb-6">
			<h1 class="text-3xl leading-tight font-bold tracking-tight">Create your account</h1>
			<p class="mt-2 text-sm text-slate-500">
				Already have an account?
				<a
					class="font-medium text-indigo-600 underline underline-offset-2 hover:text-indigo-700"
					href={resolve('/account/login')}>Log in</a
				>
			</p>
		</div>

		<FormCard {fields} submitLabel="Create account" failure={form} />
	</section>
</div>
