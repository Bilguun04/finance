<script lang="ts">
	import FormCard from '#lib/components/FormCard.svelte';
	import { NEW_PASSWORD_FIELDS } from '#lib/account-fields.ts';
	import type { PageProps } from './$types';

	let { form }: PageProps = $props();

	const fields = [
		{
			name: 'old_password',
			label: 'Old password',
			type: 'password',
			autocomplete: 'current-password' as const
		},
		...NEW_PASSWORD_FIELDS
	];
</script>

<svelte:head>
	<title>Change password | Finance Tracker</title>
</svelte:head>

<section class="mx-auto mt-8 max-w-md">
	<h1 class="mb-6 text-3xl leading-tight font-bold tracking-tight">Change password</h1>
	<FormCard {fields} submitLabel="Change password" failure={form} />
</section>
