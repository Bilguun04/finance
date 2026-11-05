<script lang="ts">
	import { fixed, money, plus } from '#lib/format.ts';
	import type { MarketPulse } from '#lib/types.ts';
	import { flashClass, type PreviousPrices } from './flash.ts';
	import MarketMovers from './MarketMovers.svelte';

	let { pulse, previous }: { pulse: MarketPulse; previous: PreviousPrices } = $props();

	const headline = $derived(pulse.headline);
</script>

<!-- HEADER -->
<div class="flex items-center justify-between border-b border-slate-100 px-6 py-5">
	<div>
		<p class="text-xs font-bold tracking-wider text-slate-400 uppercase">
			Market pulse · {pulse.marketStatus.label}
		</p>
		<h2 class="mt-1 text-lg font-bold text-slate-900">US markets</h2>
	</div>

	{#if headline.quote}
		{#if headline.quote.change >= 0}
			<span
				class="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-3 py-1 text-xs font-bold text-emerald-700"
			>
				<span class="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
				Market up
			</span>
		{:else}
			<span
				class="inline-flex items-center gap-1.5 rounded-full bg-red-50 px-3 py-1 text-xs font-bold text-red-700"
			>
				<span class="h-1.5 w-1.5 rounded-full bg-red-500"></span>
				Market down
			</span>
		{/if}
	{/if}
</div>

<!-- HEADLINE INDEX -->
<div class="border-b border-slate-100 px-6 py-6">
	<p class="text-sm font-medium text-slate-500">
		{headline.name} <span class="text-slate-400">· {headline.symbol}</span>
	</p>

	{#if headline.quote}
		<div class="flex flex-wrap items-end justify-between gap-4">
			<div>
				<p
					class="-mx-1 mt-1 rounded-md px-1 text-4xl font-bold tracking-tight text-slate-900 tabular-nums {flashClass(
						previous,
						headline.symbol,
						headline.quote.price
					)}"
				>
					${money(headline.quote.price)}
				</p>
				<p
					class={[
						'mt-2 text-sm font-semibold tabular-nums',
						headline.quote.change >= 0 ? 'text-emerald-600' : 'text-red-600'
					]}
				>
					{plus(headline.quote.change)}{fixed(headline.quote.change, 2)}
					<span class="font-medium"
						>({plus(headline.quote.changePct)}{fixed(headline.quote.changePct, 2)}%)</span
					>
					<span class="ml-1 font-normal text-slate-400">{pulse.changeLabel}</span>
				</p>
			</div>

			<div class="rounded-lg bg-slate-50 px-4 py-3 text-right">
				<p class="text-xs font-medium text-slate-400">Day range</p>
				<p class="mt-1 text-sm font-bold text-slate-800 tabular-nums">
					{fixed(headline.quote.low, 2)} – {fixed(headline.quote.high, 2)}
				</p>
			</div>
		</div>
	{:else}
		<p class="mt-1 text-4xl font-bold text-slate-300">—</p>
		<p class="mt-2 text-sm text-slate-400">Unavailable</p>
	{/if}
</div>

<!-- OTHER INDEXES -->
<div class="grid grid-cols-3 divide-x divide-slate-100 border-b border-slate-100">
	{#each pulse.indexes as item, i (item.symbol)}
		<div
			class="animate-fade-up p-4 {flashClass(previous, item.symbol, item.quote?.price)}"
			style:animation-delay="{i * 90}ms"
		>
			<p class="text-xs text-slate-400">{item.name}</p>
			{#if item.quote}
				<p
					class={[
						'mt-1 text-sm font-bold tabular-nums',
						item.quote.changePct >= 0 ? 'text-emerald-600' : 'text-red-600'
					]}
				>
					{plus(item.quote.changePct)}{fixed(item.quote.changePct, 2)}%
				</p>
			{:else}
				<p class="mt-1 text-sm font-bold text-slate-300">—</p>
			{/if}
		</div>
	{/each}
</div>

<!-- MOVERS -->
<div class="space-y-6 px-6 py-5">
	<div>
		<h3 class="mb-3 text-sm font-bold text-slate-900">Top gainers</h3>
		<MarketMovers movers={pulse.gainers} up={true} changeLabel={pulse.changeLabel} {previous} />
	</div>

	<div>
		<h3 class="mb-3 text-sm font-bold text-slate-900">Top losers</h3>
		<MarketMovers movers={pulse.losers} up={false} changeLabel={pulse.changeLabel} {previous} />
	</div>
</div>
