<script lang="ts">
	import { fixed, money } from '#lib/format.ts';
	import type { MarketSnapshot } from '#lib/types.ts';
	import { flashClass, type PreviousPrices } from './flash.ts';
	import MarketCard from './MarketCard.svelte';

	let { snapshot, previous }: { snapshot: MarketSnapshot; previous: PreviousPrices } = $props();
</script>

<div class="space-y-8">
	<div>
		<p class="mb-3 text-xs font-semibold tracking-wider text-slate-400 uppercase">
			Indexes (via ETFs)
		</p>
		<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
			{#each snapshot.indexes as item, i (item.symbol)}
				<MarketCard {item} index={i} changeLabel={snapshot.changeLabel} {previous} />
			{/each}
		</div>
	</div>

	<div>
		<p class="mb-3 text-xs font-semibold tracking-wider text-slate-400 uppercase">Major stocks</p>
		<div
			class="divide-y divide-slate-100 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm"
		>
			{#each snapshot.stocks as item, i (item.symbol)}
				{@const up = (item.quote?.change ?? 0) >= 0}
				<div
					class="flex animate-fade-up items-center gap-4 px-5 py-3.5 transition-colors hover:bg-slate-50 {flashClass(
						previous,
						item.symbol,
						item.quote?.price
					)}"
					style:animation-delay="{i * 50}ms"
				>
					<div
						class="flex h-9 w-12 shrink-0 items-center justify-center rounded-lg bg-slate-900 text-xs font-bold text-white"
					>
						{item.symbol}
					</div>
					<p class="min-w-0 flex-1 truncate text-sm font-semibold text-slate-800">{item.name}</p>

					{#if item.quote}
						<!-- DAY RANGE -->
						<div class="hidden w-40 sm:block">
							<div class="relative h-1 rounded-full bg-slate-100">
								<span
									class={[
										'absolute top-1/2 h-2 w-2 -translate-x-1/2 -translate-y-1/2 rounded-full',
										up ? 'bg-emerald-500' : 'bg-red-500'
									]}
									style:left="{Math.round(item.rangePct)}%"
								></span>
							</div>
							<div class="mt-1 flex justify-between text-[10px] text-slate-400 tabular-nums">
								<span>{fixed(item.quote.low, 2)}</span>
								<span>{fixed(item.quote.high, 2)}</span>
							</div>
						</div>

						<p class="w-24 text-right text-sm font-bold text-slate-900 tabular-nums">
							${money(item.quote.price)}
						</p>
						<span
							class={[
								'inline-flex w-20 items-center justify-center gap-1 rounded-full py-0.5 text-xs font-semibold tabular-nums',
								up ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'
							]}
						>
							{up ? '▲' : '▼'}
							{fixed(item.quote.changePct, 2)}%
						</span>
					{:else}
						<p class="text-sm text-slate-400">Unavailable</p>
					{/if}
				</div>
			{/each}
		</div>
	</div>
</div>
