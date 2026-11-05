<script lang="ts">
	import FormCard from '#lib/components/FormCard.svelte';
	import type { CardField } from '#lib/types.ts';
	import type { PageProps } from './$types';

	let { form }: PageProps = $props();

	const fields: CardField[] = [
		{ name: 'email', label: 'Email', type: 'email', autocomplete: 'email' }
	];
</script>

<svelte:head>
	<title>Reset password | Finance Tracker</title>
</svelte:head>

<section class="mx-auto mt-8 max-w-md">
	<h1 class="mb-3 text-3xl leading-tight font-bold tracking-tight">Reset password</h1>
	<p class="mb-6 text-sm text-slate-500">
		Enter your account's email and we'll send you a link to choose a new password.
	</p>
	<FormCard {fields} submitLabel="Send reset link" failure={form} />
</section>
