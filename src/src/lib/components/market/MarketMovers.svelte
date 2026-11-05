<script lang="ts">
	import { fixed, money } from '#lib/format.ts';
	import type { Mover } from '#lib/types.ts';
	import { flashClass, type PreviousPrices } from './flash.ts';

	type Props = { movers: Mover[]; up: boolean; changeLabel: string; previous: PreviousPrices };

	let { movers, up, changeLabel, previous }: Props = $props();
</script>

{#if movers.length}
	<div class="space-y-3">
		{#each movers as stock, i (stock.symbol)}
			<div
				class="-mx-2 flex animate-fade-up items-center gap-3 rounded-lg px-2 py-1 transition-colors hover:bg-slate-50 {flashClass(
					previous,
					stock.symbol,
					stock.quote.price
				)}"
				style:animation-delay="{i * 90}ms"
			>
				<div
					class={[
						'flex h-9 w-12 shrink-0 items-center justify-center rounded-lg text-xs font-bold',
						up ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'
					]}
				>
					{stock.symbol}
				</div>

				<div class="min-w-0 flex-1">
					<div class="mb-1.5 flex items-baseline justify-between gap-2">
						<p class="truncate text-sm font-bold text-slate-800">{stock.name}</p>
						<p class="text-sm font-bold text-slate-800 tabular-nums">${money(stock.quote.price)}</p>
					</div>
					<div class="flex items-center gap-3">
						<div class="h-1.5 flex-1 overflow-hidden rounded-full bg-slate-100">
							<div
								class={[
									'h-full origin-left animate-grow-x rounded-full',
									up ? 'bg-emerald-500' : 'bg-red-500'
								]}
								style:width="{Math.round(stock.barPct)}%"
								style:animation-delay="{i * 90}ms"
							></div>
						</div>
						<p
							class={[
								'w-14 text-right text-xs font-semibold tabular-nums',
								up ? 'text-emerald-600' : 'text-red-600'
							]}
						>
							{up ? '+' : ''}{fixed(stock.quote.changePct, 2)}%
						</p>
					</div>
				</div>
			</div>
		{/each}
	</div>
{:else}
	<p class="text-xs text-slate-400">
		None of the major stocks are {up ? 'up' : 'down'}
		{changeLabel}.
	</p>
{/if}
