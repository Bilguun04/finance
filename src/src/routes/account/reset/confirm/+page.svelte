<script lang="ts">
	import { resolve } from '$app/paths';
	import FormCard from '#lib/components/FormCard.svelte';
	import { NEW_PASSWORD_FIELDS } from '#lib/account-fields.ts';
	import type { PageProps } from './$types';

	let { data, form }: PageProps = $props();

	const valid = $derived(data.validLink && !form?.expired);
</script>

<svelte:head>
	<title>{valid ? 'Choose a new password' : 'Link expired'} | Finance Tracker</title>
</svelte:head>

<section class="mx-auto mt-8 max-w-md">
	{#if valid}
		<h1 class="mb-6 text-3xl leading-tight font-bold tracking-tight">Choose a new password</h1>
		<FormCard fields={NEW_PASSWORD_FIELDS} submitLabel="Set password" failure={form} />
	{:else}
		<h1 class="mb-3 text-3xl leading-tight font-bold tracking-tight">Link expired</h1>
		<p class="mb-6 text-slate-500">This reset link is invalid or has already been used.</p>
		<a
			class="inline-block rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-900 no-underline hover:bg-slate-100"
			href={resolve('/account/password/reset')}>Request a new link</a
		>
	{/if}
</section>
