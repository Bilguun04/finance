<script lang="ts">
	import { resolve } from '$app/paths';
</script>

<svelte:head>
	<title>Password reset | Finance Tracker</title>
</svelte:head>

<section class="mx-auto mt-8 max-w-md">
	<h1 class="mb-3 text-3xl leading-tight font-bold tracking-tight">Password reset</h1>
	<p class="mb-6 text-slate-500">Your password has been set. You can now log in.</p>
	<a
		class="inline-block rounded-md border border-indigo-600 bg-indigo-600 px-4 py-2 text-sm font-semibold text-white no-underline hover:bg-indigo-700"
		href={resolve('/account/login')}>Log in</a
	>
</section>
