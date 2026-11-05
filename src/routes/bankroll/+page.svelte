<script lang="ts">
	import { resolve } from '$app/paths';
	import { shortDate, signedDollars } from '#lib/format.ts';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
</script>

<svelte:head>
	<title>Bankroll | Finance Tracker</title>
</svelte:head>

<div class="space-y-8 pt-8">
	<section
		class="relative overflow-hidden rounded-2xl bg-indigo-600 px-6 py-10 text-white shadow-xl shadow-indigo-200/60 sm:px-10"
	>
		<div class="relative z-10 max-w-2xl">
			<p class="mb-3 text-xs font-semibold tracking-[0.18em] text-indigo-200 uppercase">
				Bankroll / session log
			</p>
			<h1 class="max-w-xl text-4xl leading-tight font-semibold tracking-tight sm:text-5xl">
				Know where your game stands.
			</h1>
			<p class="mt-4 max-w-xl text-base leading-7 text-indigo-100">
				A clean record of every buy-in, cash-out, and long night at the table.
			</p>
			<a
				href={resolve('/bankroll/sessions/new')}
				class="mt-7 inline-flex items-center gap-2 rounded-lg bg-white px-4 py-2.5 text-sm font-semibold text-indigo-600 no-underline shadow-sm transition hover:bg-indigo-50"
				><span class="text-lg leading-none">+</span> Log a session</a
			>
		</div>
		<div class="absolute -top-20 -right-12 h-72 w-72 rounded-full bg-white/10"></div>
		<div class="absolute right-24 -bottom-32 h-72 w-72 rounded-full bg-indigo-400/30"></div>
	</section>

	<section class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
		<article
			class="rounded-xl border border-t-4 border-indigo-100 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg hover:shadow-indigo-100"
		>
			<p class="text-xs font-semibold tracking-wider text-slate-500 uppercase">Net profit</p>
			<p
				class={[
					'mt-3 text-3xl font-semibold',
					data.netProfit >= 0 ? 'text-emerald-600' : 'text-red-600'
				]}
			>
				{signedDollars(data.netProfit)}
			</p>
			<p class="mt-2 text-sm text-slate-500">Across all recorded sessions</p>
		</article>
		<article
			class="rounded-xl border border-t-4 border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg hover:shadow-slate-200/60"
		>
			<p class="text-xs font-semibold tracking-wider text-slate-500 uppercase">Sessions</p>
			<p class="mt-3 text-3xl font-semibold text-slate-900">{data.totalSessions}</p>
			<p class="mt-2 text-sm text-slate-500">{data.winningSessions} winning sessions</p>
		</article>
		<article
			class="rounded-xl border border-t-4 border-cyan-100 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg hover:shadow-cyan-100"
		>
			<p class="text-xs font-semibold tracking-wider text-slate-500 uppercase">Total buy-in</p>
			<p class="mt-3 text-3xl font-semibold text-slate-900">${data.totalBuyin}</p>
			<p class="mt-2 text-sm text-slate-500">Capital put into play</p>
		</article>
		<article
			class="rounded-xl border border-t-4 border-amber-100 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg hover:shadow-amber-100"
		>
			<p class="text-xs font-semibold tracking-wider text-slate-500 uppercase">Total cash-out</p>
			<p class="mt-3 text-3xl font-semibold text-slate-900">${data.totalBuyout}</p>
			<p class="mt-2 text-sm text-slate-500">Returned from the table</p>
		</article>
	</section>

	<section class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
		<div
			class="flex flex-col gap-3 border-b border-slate-200 px-5 py-5 sm:flex-row sm:items-center sm:justify-between sm:px-6"
		>
			<div>
				<p class="text-xs font-semibold tracking-wider text-slate-500 uppercase">History</p>
				<h2 class="mt-1 text-2xl font-semibold tracking-tight text-slate-900">Recent sessions</h2>
			</div>
			<a
				href={resolve('/bankroll/sessions/new')}
				class="text-sm font-semibold text-indigo-600 no-underline hover:text-indigo-800"
				>Add another session &rarr;</a
			>
		</div>
		{#if data.sessions.length}
			<div class="overflow-x-auto">
				<table class="w-full min-w-180 text-left">
					<thead
						class="border-y border-slate-100 bg-slate-50 text-xs tracking-wider text-slate-500 uppercase"
						><tr
							><th class="px-6 py-3 font-semibold">Session</th><th class="px-4 py-3 font-semibold"
								>Format</th
							><th class="px-4 py-3 font-semibold">Date</th><th
								class="px-4 py-3 text-right font-semibold">Buy-in</th
							><th class="px-4 py-3 text-right font-semibold">Cash-out</th><th
								class="px-6 py-3 text-right font-semibold">Result</th
							></tr
						></thead
					>
					<tbody class="divide-y divide-slate-100">
						{#each data.sessions as session (session.id)}
							<tr class="transition-colors hover:bg-emerald-50/40">
								<td class="px-6 py-4"
									><p class="font-semibold text-slate-900">{session.host}</p>
									<p class="mt-0.5 text-sm text-slate-500">
										{session.type || 'General play'}{#if session.stakes}
											<span class="text-slate-300">·</span> {session.stakes}{/if}
									</p></td
								>
								<td class="px-4 py-4 text-sm text-slate-600">{session.format}</td>
								<td class="px-4 py-4 text-sm text-slate-600">{shortDate(session.sessionStart)}</td>
								<td class="px-4 py-4 text-right text-sm text-slate-600">${session.buyin}</td>
								<td class="px-4 py-4 text-right text-sm text-slate-600">${session.buyout}</td>
								<td class="px-6 py-4 text-right"
									><span
										class={[
											'inline-flex rounded-full px-2.5 py-1 text-sm font-semibold',
											session.profit >= 0
												? 'bg-emerald-100 text-emerald-700'
												: 'bg-red-100 text-red-700'
										]}>{signedDollars(session.profit)}</span
									><a
										href={resolve('/bankroll/sessions/[id]/edit', { id: String(session.id) })}
										class="ml-2 text-xs font-semibold text-slate-400 hover:text-slate-700">Edit</a
									></td
								>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{:else}
			<div class="px-6 py-16 text-center">
				<p class="text-lg font-semibold text-slate-900">No sessions yet</p>
				<p class="mt-2 text-sm text-slate-500">
					Log your first session to start tracking your bankroll.
				</p>
			</div>
		{/if}
	</section>
</div>
