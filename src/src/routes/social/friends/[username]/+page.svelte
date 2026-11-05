<script lang="ts">
	import { resolve } from '$app/paths';
	import { enhance } from '$app/forms';
	import Allocation from '#lib/components/Allocation.svelte';
	import Avatar from '#lib/components/Avatar.svelte';
	import { fixed, pluralize, shortDate, width } from '#lib/format.ts';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	const friend = $derived(data.friend);
</script>

<svelte:head>
	<title>{friend.username} | Finance Tracker</title>
</svelte:head>

<div class="space-y-6 pt-8">
	<a
		href={resolve('/social')}
		class="text-sm font-semibold text-slate-500 no-underline hover:text-slate-900">&larr; Friends</a
	>

	<div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
		<div class="flex min-w-0 items-center gap-4">
			<Avatar username={friend.username} large />
			<div class="min-w-0">
				<h1 class="truncate text-3xl font-semibold tracking-tight text-slate-900">
					{friend.username}
				</h1>
				{#if data.friendsSince}
					<p class="text-sm text-slate-500">Friends since {shortDate(data.friendsSince)}</p>
				{/if}
			</div>
		</div>
		<form
			method="post"
			action="?/unfriend"
			class="m-0 shrink-0"
			use:enhance={({ cancel }) => {
				if (!confirm(`Remove ${friend.username} from your friends?`)) cancel();
			}}
		>
			<button
				type="submit"
				class="cursor-pointer rounded-lg border border-slate-300 bg-white px-3.5 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-red-300 hover:bg-red-50 hover:text-red-700"
				>Unfriend</button
			>
		</form>
	</div>

	{#if data.shared.length}
		<section class="grid gap-6 md:grid-cols-2">
			{#each data.shared as entry (entry.portfolio.id)}
				<article class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
					<div class="flex items-start justify-between gap-3">
						<div class="min-w-0">
							<h2 class="truncate text-xl font-semibold tracking-tight text-slate-900">
								{entry.portfolio.name}
							</h2>
							<p class="mt-0.5 text-sm text-slate-500">
								{entry.holdings.length} holding{pluralize(entry.holdings.length)}
							</p>
						</div>
						<span
							class="shrink-0 rounded-full bg-slate-100 px-2 py-0.5 text-xs font-semibold text-slate-600"
							>{entry.portfolio.currency}</span
						>
					</div>

					{#if entry.holdings.length || entry.cashPct}
						<div class="mt-5">
							<Allocation items={entry.holdings} cashPct={entry.cashPct} />
						</div>
						<ul class="m-0 mt-5 list-none space-y-3 border-t border-slate-100 p-0 pt-5">
							{#each entry.holdings as item (item.symbol)}
								<li class="grid grid-cols-[4.5rem_1fr_3.5rem] items-center gap-3 text-sm">
									<span class="truncate font-semibold text-slate-900">{item.symbol}</span>
									<span class="h-1.5 overflow-hidden rounded-full bg-slate-100"
										><span
											class="block h-full rounded-full bg-indigo-400"
											style:width={width(item.weight)}
										></span></span
									>
									<span class="text-right text-slate-600 tabular-nums"
										>{fixed(item.weight, 1)}%</span
									>
								</li>
							{/each}
							<li class="grid grid-cols-[4.5rem_1fr_3.5rem] items-center gap-3 text-sm">
								<span class="font-semibold text-slate-500">Cash</span>
								<span class="h-1.5 overflow-hidden rounded-full bg-slate-100"
									><span
										class="block h-full rounded-full bg-slate-300"
										style:width={width(entry.cashPct)}
									></span></span
								>
								<span class="text-right text-slate-500 tabular-nums"
									>{fixed(entry.cashPct, 1)}%</span
								>
							</li>
						</ul>
					{:else}
						<p class="mt-5 rounded-lg bg-slate-50 p-4 text-center text-sm text-slate-500">
							Nothing in this portfolio yet.
						</p>
					{/if}
				</article>
			{/each}
		</section>
	{:else}
		<div class="rounded-xl border border-dashed border-slate-300 px-6 py-16 text-center">
			<p class="text-lg font-semibold text-slate-900">Nothing shared yet</p>
			<p class="mt-2 text-sm text-slate-500">
				{friend.username} hasn't made any portfolio visible to friends.
			</p>
		</div>
	{/if}
</div>
