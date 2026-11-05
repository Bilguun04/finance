<script lang="ts">
	import { enhance } from '$app/forms';
	import type { CardField, FormFailure } from '#lib/types.ts';

	// Shared card for the simple account forms (sign up, password change/reset).

	type Props = { fields: CardField[]; submitLabel: string; failure?: FormFailure | null };

	let { fields, submitLabel, failure }: Props = $props();
</script>

<form
	method="post"
	use:enhance
	class="space-y-5 rounded-lg border border-slate-200 bg-white p-6 shadow-sm [&_input]:w-full [&_input]:rounded-md [&_input]:border [&_input]:border-slate-300 [&_input]:bg-white [&_input]:px-3 [&_input]:py-2 [&_input]:text-slate-900 [&_input]:transition [&_input]:outline-none [&_input:focus]:border-indigo-500 [&_input:focus]:ring-2 [&_input:focus]:ring-indigo-100 [&_label]:mb-1 [&_label]:block [&_label]:text-sm [&_label]:font-semibold [&_label]:text-slate-700"
>
	{#if failure?.errors.nonField.length}
		<div class="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
			<ul class="m-0 pl-4">
				{#each failure.errors.nonField as error, i (i)}<li>{error}</li>{/each}
			</ul>
		</div>
	{/if}

	{#each fields as field (field.name)}
		{@const errors = failure?.errors.fields[field.name] ?? []}
		<div>
			<label for="id_{field.name}">{field.label}</label>
			<input
				id="id_{field.name}"
				name={field.name}
				type={field.type ?? 'text'}
				autocomplete={field.autocomplete}
				maxlength={field.maxlength}
				value={field.type === 'password' ? '' : (failure?.values[field.name] ?? '')}
				aria-invalid={errors.length > 0 || undefined}
				required
			/>

			{#if field.help}
				<div class="mt-1 text-xs leading-relaxed text-slate-500">
					{#if Array.isArray(field.help)}
						<ul class="m-0 list-disc pl-4">
							{#each field.help as line, i (i)}<li>{line}</li>{/each}
						</ul>
					{:else}
						{field.help}
					{/if}
				</div>
			{/if}

			{#if errors.length}
				<div class="mt-2 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
					<ul class="m-0 pl-4">
						{#each errors as error, i (i)}<li>{error}</li>{/each}
					</ul>
				</div>
			{/if}
		</div>
	{/each}

	<button
		type="submit"
		class="w-full cursor-pointer rounded-md border border-indigo-600 bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:border-indigo-700 hover:bg-indigo-700"
	>
		{submitLabel}
	</button>
</form>
