<script lang="ts">
	import { resolve } from '$app/paths';
	import './layout.css';
	import favicon from '#lib/assets/favicon.svg';
	import type { LayoutProps } from './$types';

	let { data, children }: LayoutProps = $props();

	const navLink =
		'text-sm font-medium text-slate-500 no-underline transition-colors hover:text-slate-900';
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<title>Finance Tracker</title>
</svelte:head>

<div class="m-0 min-h-screen bg-slate-50 font-sans leading-relaxed text-slate-900 antialiased">
	<nav
		class="sticky top-0 z-10 flex items-center justify-center border-b border-slate-200 bg-white px-6 py-3.5"
	>
		<div class="flex w-full max-w-5xl flex-wrap items-center justify-center gap-x-6 gap-y-2">
			<a class="link" href="https://bilguuntegshbayar.com">Portfolio</a>
			<a class="link" href="https://github.com/bilguun04/finance">Codebase</a>
			{#if data.user}
				<a class={navLink} href={resolve('/portfolio')}>Investments</a>
				<a class={navLink} href={resolve('/social')}>Friends</a>
				<a class={navLink} href={resolve('/bankroll')}>Dashboard</a>
				<a class={navLink} href={resolve('/account/profile')}>Profile</a>
				<form method="post" action="/account/logout" class="m-0">
					<button
						type="submit"
						class="cursor-pointer border-0 bg-transparent p-0 text-sm font-medium text-slate-500 transition-colors hover:text-slate-900"
						>Logout</button
					>
				</form>
			{:else}
				<a class={navLink} href={resolve('/account/login')}>Login</a>
				<a class={navLink} href={resolve('/account/register')}>Sign up</a>
			{/if}
		</div>
	</nav>

	<main class="mx-auto max-w-5xl px-6 pb-16">
		{#if data.messages.length}
			<ul class="mt-6 mb-6 list-none space-y-2 p-0">
				{#each data.messages as message, i (i)}
					<li
						class={[
							'rounded-md border border-l-4 border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 shadow-sm',
							message.level === 'success' && 'border-l-emerald-600 bg-emerald-50',
							message.level === 'error' && 'border-l-red-600 bg-red-50',
							message.level === 'info' && 'border-l-slate-400'
						]}
					>
						{message.text}
					</li>
				{/each}
			</ul>
		{/if}

		{@render children()}
	</main>
</div>
