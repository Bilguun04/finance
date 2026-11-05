<script lang="ts">
	import { fixed, money, plus } from '#lib/format.ts';
	import type { Quote } from '#lib/types.ts';
	import { flashClass, type PreviousPrices } from './flash.ts';

	type Props = {
		item: { symbol: string; name: string; quote: Quote | null; rangePct: number };
		index: number;
		changeLabel: string;
		previous: PreviousPrices;
	};

	let { item, index, changeLabel, previous }: Props = $props();

	const up = $derived((item.quote?.change ?? 0) >= 0);
	const delay = $derived(`${index * 70}ms`);
	const range = $derived(`${Math.round(item.rangePct)}%`);
</script>

<div
	class="animate-fade-up rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition duration-200 hover:-translate-y-0.5 hover:shadow-md {flashClass(
		previous,
		item.symbol,
		item.quote?.price
	)}"
	style:animation-delay={delay}
>
	<div class="flex items-start justify-between gap-2">
		<div>
			<p class="text-sm font-bold text-slate-900">{item.symbol}</p>
			<p class="text-xs text-slate-400">{item.name}</p>
		</div>
		{#if item.quote}
			<span
				class={[
					'inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold tabular-nums',
					up ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'
				]}
			>
				{up ? '▲' : '▼'}
				{fixed(item.quote.changePct, 2)}%
			</span>
		{/if}
	</div>

	{#if item.quote}
		<p class="mt-4 text-2xl font-bold tracking-tight text-slate-900 tabular-nums">
			${money(item.quote.price)}
		</p>
		<p class={['text-xs font-medium tabular-nums', up ? 'text-emerald-600' : 'text-red-600']}>
			{plus(item.quote.change)}{fixed(item.quote.change, 2)}
			{changeLabel}
		</p>

		<!-- DAY RANGE -->
		<div class="mt-4">
			<div class="relative h-1 rounded-full bg-slate-100">
				<div
					class={[
						'absolute inset-y-0 left-0 origin-left animate-grow-x rounded-full',
						up ? 'bg-emerald-300' : 'bg-red-300'
					]}
					style:width={range}
					style:animation-delay={delay}
				></div>
				<span
					class={[
						'absolute top-1/2 h-2.5 w-2.5 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-white shadow',
						up ? 'bg-emerald-500' : 'bg-red-500'
					]}
					style:left={range}
				></span>
			</div>
			<div class="mt-1.5 flex justify-between text-[10px] font-medium text-slate-400 tabular-nums">
				<span>{fixed(item.quote.low, 2)}</span>
				<span>Day range</span>
				<span>{fixed(item.quote.high, 2)}</span>
			</div>
		</div>
	{:else}
		<p class="mt-4 text-2xl font-bold text-slate-300">—</p>
		<p class="text-xs text-slate-400">Unavailable</p>
	{/if}
</div>
