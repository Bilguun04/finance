<script lang="ts">
	import { resolve } from '$app/paths';
	import { enhance } from '$app/forms';
	import Field from '#lib/components/Field.svelte';
	import type { PageProps } from './$types';

	let { data, form }: PageProps = $props();

	const p = $derived(data.portfolio);
	const values = $derived(form?.values);
</script>

<svelte:head>
	<title>Settings · {p.name} | Finance Tracker</title>
</svelte:head>

<div class="mx-auto max-w-2xl space-y-6 pt-8">
	<a
		href={resolve('/portfolio/[id]', { id: String(p.id) })}
		class="text-sm font-semibold text-slate-500 no-underline hover:text-slate-900"
		>&larr; Back to {p.name}</a
	>

	<section class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
		<p class="text-xs font-semibold tracking-wider text-indigo-600 uppercase">Portfolio settings</p>
		<h1 class="mt-2 text-3xl font-semibold text-slate-900">{p.name}</h1>
		<p class="mt-2 text-sm text-slate-500">
			Currency ({p.currency}) is fixed once a portfolio is created.
		</p>

		<form method="post" action="?/save" class="mt-8 space-y-5" use:enhance>
			<Field
				label="Name"
				name="name"
				maxlength={100}
				required
				value={values?.name ?? p.name}
				errors={form?.errors.fields.name}
			/>
			<label class="flex items-start gap-2.5 rounded-lg bg-slate-50 p-3 text-sm">
				<input
					type="checkbox"
					name="is_public"
					id="id_is_public"
					class="mt-0.5 size-4 shrink-0 accent-indigo-600"
					checked={values ? 'is_public' in values : p.isPublic}
				/>
				<span
					><span class="font-semibold text-slate-700">Visible to friends</span><span
						class="mt-0.5 block text-xs text-slate-500"
						>Friends see which symbols you hold and each one's share of the portfolio, never dollar
						amounts.</span
					></span
				>
			</label>
			<div class="flex items-center justify-end gap-4 border-t border-slate-100 pt-6">
				<a
					href={resolve('/portfolio/[id]', { id: String(p.id) })}
					class="text-sm font-semibold text-slate-500 no-underline hover:text-slate-900">Cancel</a
				>
				<button
					type="submit"
					class="cursor-pointer rounded-lg bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-indigo-700"
					>Save changes</button
				>
			</div>
		</form>
	</section>

	<section class="rounded-xl border border-red-200 bg-white p-6 shadow-sm sm:p-8">
		<p class="text-xs font-semibold tracking-wider text-red-600 uppercase">Danger zone</p>
		<h2 class="mt-2 text-xl font-semibold text-slate-900">Delete this portfolio</h2>
		<p class="mt-2 text-sm text-slate-500">
			Removes its holdings and every recorded transaction. This can't be undone.
		</p>
		<form
			method="post"
			action="?/delete"
			class="mt-5"
			use:enhance={({ cancel }) => {
				if (!confirm(`Delete ${p.name} and all of its history?`)) cancel();
			}}
		>
			<button
				type="submit"
				class="cursor-pointer rounded-lg border border-red-600 bg-red-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:border-red-700 hover:bg-red-700"
				>Delete portfolio</button
			>
		</form>
	</section>
</div>
