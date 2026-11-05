<script lang="ts">
	import { resolve } from '$app/paths';
	import { enhance } from '$app/forms';
	import Field from '#lib/components/Field.svelte';
	import type { FormFailure } from '#lib/types.ts';

	// The bankroll session form, shared by the "log" and "edit" pages.
	type Props = {
		isEdit: boolean;
		initial: Record<string, string>;
		failure?: FormFailure | null;
	};

	let { isEdit, initial, failure }: Props = $props();

	const value = (name: string) => failure?.values[name] ?? initial[name] ?? '';
	const errors = (name: string) => failure?.errors.fields[name];
</script>

<svelte:head>
	<title>{isEdit ? 'Edit session' : 'Log session'} | Finance Tracker</title>
</svelte:head>

<div class="mx-auto max-w-3xl pt-8">
	<a
		href={resolve('/bankroll')}
		class="text-sm font-semibold text-slate-500 no-underline hover:text-slate-900"
		>&larr; Back to dashboard</a
	>
	<div class="mt-5 rounded-lg border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
		<p class="text-xs font-semibold tracking-wider text-emerald-700 uppercase">
			Bankroll / session log
		</p>
		<h1 class="mt-2 text-3xl font-semibold text-slate-900">
			{isEdit ? 'Edit session' : 'Log a new session'}
		</h1>
		<p class="mt-2 text-sm text-slate-500">
			Capture the details now so your results stay useful later.
		</p>

		<form method="post" class="mt-8 space-y-6" use:enhance>
			{#if failure?.errors.nonField.length}
				<div class="rounded-md bg-red-50 px-4 py-3 text-sm text-red-700">
					{failure.errors.nonField.join(' ')}
				</div>
			{/if}
			<div class="grid gap-5 sm:grid-cols-2">
				<Field
					label="Host"
					name="host"
					maxlength={100}
					required
					value={value('host')}
					errors={errors('host')}
				/>
				<Field label="Format" name="format" errors={errors('format')}>
					{#snippet children({ id })}
						<select {id} name="format" required value={value('format')}>
							<option value="">---------</option>
							<option value="homegame">Home game</option>
							<option value="casino">Casino</option>
						</select>
					{/snippet}
				</Field>
				<Field
					label="Type"
					name="type"
					maxlength={100}
					value={value('type')}
					errors={errors('type')}
				/>
				<Field
					label="Stakes"
					name="stakes"
					maxlength={100}
					required
					value={value('stakes')}
					errors={errors('stakes')}
				/>
				<Field
					label="Session start (UTC)"
					name="session_start"
					type="datetime-local"
					required
					value={value('session_start')}
					errors={errors('session_start')}
				/>
				<Field
					label="Session end (UTC)"
					name="session_end"
					type="datetime-local"
					required
					value={value('session_end')}
					errors={errors('session_end')}
				/>
				<Field
					label="Buyin"
					name="buyin"
					type="number"
					min="0"
					step="1"
					required
					value={value('buyin')}
					errors={errors('buyin')}
				/>
				<Field
					label="Buyout"
					name="buyout"
					type="number"
					min="0"
					step="1"
					required
					value={value('buyout')}
					errors={errors('buyout')}
				/>
			</div>
			<div class="flex items-center justify-end gap-4 border-t border-slate-100 pt-6">
				<a
					href={resolve('/bankroll')}
					class="text-sm font-semibold text-slate-500 no-underline hover:text-slate-900">Cancel</a
				>
				<button
					type="submit"
					class="cursor-pointer rounded-md bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-700"
					>{isEdit ? 'Save changes' : 'Save session'}</button
				>
			</div>
		</form>
	</div>
</div>
