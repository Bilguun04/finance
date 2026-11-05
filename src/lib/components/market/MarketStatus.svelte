<script lang="ts">
	import type { MarketStatus } from '#lib/types.ts';

	let { status }: { status: MarketStatus } = $props();

	const state = $derived(status.state);
	const extended = $derived(state === 'pre_market' || state === 'after_hours');
</script>

<span
	class={[
		'inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 font-bold',
		state === 'open'
			? 'bg-emerald-50 text-emerald-700'
			: extended
				? 'bg-amber-50 text-amber-700'
				: state === 'overnight'
					? 'bg-indigo-50 text-indigo-700'
					: 'bg-slate-100 text-slate-600'
	]}
	title="US market hours (ET): pre-market 4:00–9:30, regular 9:30–4:00, after-hours 4:00–8:00"
>
	<span class="relative flex h-2 w-2">
		{#if state === 'open'}
			<span
				class="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"
			></span>
		{/if}
		<span
			class={[
				'relative inline-flex h-2 w-2 rounded-full',
				state === 'open'
					? 'bg-emerald-500'
					: extended
						? 'bg-amber-500'
						: state === 'overnight'
							? 'bg-indigo-500'
							: 'bg-slate-400'
			]}
		></span>
	</span>
	{status.label}{#if status.holiday && state === 'closed'}&nbsp;· {status.holiday}{/if}
</span>
