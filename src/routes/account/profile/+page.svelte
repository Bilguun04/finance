<script lang="ts">
	import { resolve } from '$app/paths';
	import { longDate } from '#lib/format.ts';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	// The profile page is login-only, so the layout always has a user here.
	const user = $derived(data.user!);
</script>

<svelte:head>
	<title>Profile | Finance Tracker</title>
</svelte:head>

<h1 class="mt-8 mb-6 text-3xl leading-tight font-bold tracking-tight">{user.username}</h1>

<dl
	class="mb-6 grid max-w-md grid-cols-[auto_1fr] gap-x-6 gap-y-3 rounded-lg border border-slate-200 bg-white p-5 text-sm shadow-sm"
>
	<dt class="font-semibold text-slate-500">Username</dt>
	<dd class="m-0">{user.username}</dd>
	<dt class="font-semibold text-slate-500">Email</dt>
	<dd class="m-0">{user.email}</dd>
	<dt class="font-semibold text-slate-500">Member since</dt>
	<dd class="m-0">{longDate(user.createdAt)}</dd>
</dl>

<a
	class="inline-block rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-900 no-underline hover:bg-slate-100"
	href={resolve('/account/password/change')}>Change password</a
>
