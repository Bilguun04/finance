<script lang="ts">
	// Radio choices drawn as a two-way toggle.
	type Props = {
		name: string;
		label: string;
		options: { value: string; label: string; negative?: boolean }[];
		selected: string;
	};

	let { name, label, options, selected }: Props = $props();
</script>

<div
	class="grid grid-cols-2 gap-1 rounded-lg bg-slate-100 p-1"
	role="radiogroup"
	aria-label={label}
>
	{#each options as option (option.value)}
		<label class="cursor-pointer">
			<input
				type="radio"
				{name}
				value={option.value}
				class="peer sr-only"
				checked={option.value === selected}
			/>
			<span
				class={[
					'block rounded-md py-1.5 text-center text-sm font-semibold text-slate-500 transition peer-checked:bg-white peer-checked:shadow-sm peer-focus-visible:ring-2 peer-focus-visible:ring-indigo-300',
					option.negative ? 'peer-checked:text-red-600' : 'peer-checked:text-emerald-700'
				]}>{option.label}</span
			>
		</label>
	{/each}
</div>
