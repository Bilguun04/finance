<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { HTMLInputAttributes } from 'svelte/elements';

	// A labelled input with its errors, styled like the Django `_field.html` partial.
	// Pass `children` to render a custom control (e.g. a <select>) instead of an input.
	type Props = Omit<HTMLInputAttributes, 'children'> & {
		label: string;
		name: string;
		errors?: string[];
		children?: Snippet<[{ id: string }]>;
	};

	let { label, name, errors = [], children, id: idProp, ...rest }: Props = $props();

	const id = $derived(idProp ?? `id_${name}`);
</script>

<div
	class="[&_input]:w-full [&_input]:rounded-lg [&_input]:border [&_input]:border-slate-300 [&_input]:bg-white [&_input]:px-3 [&_input]:py-2 [&_input]:text-sm [&_input]:text-slate-900 [&_input]:shadow-sm [&_input]:transition [&_input:focus]:border-indigo-500 [&_input:focus]:ring-2 [&_input:focus]:ring-indigo-100 [&_input:focus]:outline-none [&_select]:w-full [&_select]:rounded-lg [&_select]:border [&_select]:border-slate-300 [&_select]:bg-white [&_select]:px-3 [&_select]:py-2 [&_select]:text-sm"
>
	<label for={id} class="mb-1.5 block text-xs font-semibold tracking-wider text-slate-500 uppercase"
		>{label}</label
	>
	{#if children}
		{@render children({ id })}
	{:else}
		<input {id} {name} aria-invalid={errors.length > 0 || undefined} {...rest} />
	{/if}
	{#each errors as error, i (i)}<p class="mt-1 text-xs text-red-600">{error}</p>{/each}
</div>
