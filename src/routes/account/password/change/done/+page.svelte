<script lang="ts">
	import { resolve } from '$app/paths';
</script>

<svelte:head>
	<title>Password changed | Finance Tracker</title>
</svelte:head>

<section class="mx-auto mt-8 max-w-md">
	<h1 class="mb-3 text-3xl leading-tight font-bold tracking-tight">Password changed</h1>
	<p class="mb-6 text-slate-500">Your password has been updated.</p>
	<a
		class="inline-block rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-900 no-underline hover:bg-slate-100"
		href={resolve('/account/profile')}>Back to profile</a
	>
</section>
