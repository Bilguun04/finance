<script lang="ts">
	import { fixed, width } from '#lib/format.ts';
	import type { AllocationItem } from '#lib/types.ts';

	// Allocation bar and legend. Weights are percentages.
	let { items, cashPct }: { items: AllocationItem[]; cashPct: number } = $props();

	const COLORS = [
		'bg-indigo-500',
		'bg-cyan-500',
		'bg-amber-400',
		'bg-emerald-500',
		'bg-rose-400',
		'bg-violet-500'
	];
	const color = (i: number) => COLORS[i % COLORS.length];
</script>

<div>
	<!-- Decorative; the legend below carries the same numbers as text. -->
	<div class="flex h-2.5 overflow-hidden rounded-full bg-slate-100" aria-hidden="true">
		{#each items as item, i (item.symbol)}
			<div
				class="origin-left animate-grow-x {color(i)}"
				style:width={width(item.weight)}
				title="{item.symbol} {fixed(item.weight, 1)}%"
			></div>
		{/each}
		<div class="bg-slate-300" style:width={width(cashPct)} title="Cash {fixed(cashPct, 1)}%"></div>
	</div>
	<ul class="mt-3 flex list-none flex-wrap gap-x-4 gap-y-1 p-0 text-xs text-slate-500">
		{#each items as item, i (item.symbol)}
			<li class="flex items-center gap-1.5">
				<span class="size-2 rounded-full {color(i)}"></span><span
					class="font-semibold text-slate-700">{item.symbol}</span
				>
				{fixed(item.weight, 1)}%
			</li>
		{/each}
		<li class="flex items-center gap-1.5">
			<span class="size-2 rounded-full bg-slate-300"></span><span
				class="font-semibold text-slate-700">Cash</span
			>
			{fixed(cashPct, 1)}%
		</li>
	</ul>
</div>
