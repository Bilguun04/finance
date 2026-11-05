<script lang="ts">
	import { resolve } from '$app/paths';
	import { enhance } from '$app/forms';
	import Field from '#lib/components/Field.svelte';
	import { money, pluralize, shortDate } from '#lib/format.ts';
	import type { PageProps } from './$types';

	let { data, form }: PageProps = $props();

	const errors = $derived(form?.errors);
	const values = $derived(form?.values);
	const hasPortfolios = $derived(data.portfolios.length > 0);
</script>

<svelte:head>
	<title>Portfolios | Finance Tracker</title>
</svelte:head>

<div class="space-y-8 pt-8">
	<section
		class="relative overflow-hidden rounded-2xl bg-indigo-600 px-6 py-10 text-white shadow-xl shadow-indigo-200/60 sm:px-10"
	>
		<div class="relative z-10 flex flex-col gap-8 sm:flex-row sm:items-end sm:justify-between">
			<div class="max-w-xl">
				<p class="mb-3 text-xs font-semibold tracking-[0.18em] text-indigo-200 uppercase">
					Investments / portfolios
				</p>
				<h1 class="text-4xl leading-tight font-semibold tracking-tight sm:text-5xl">
					Everything you own, in one place.
				</h1>
				<p class="mt-4 text-base leading-7 text-indigo-100">
					Track cash, positions and gains across every portfolio you run.
				</p>
			</div>
			{#if hasPortfolios}
				<div class="shrink-0 sm:text-right">
					<p class="text-xs font-semibold tracking-wider text-indigo-200 uppercase">
						Combined net liquidity
					</p>
					<p class="mt-1 text-4xl font-semibold tabular-nums">${money(data.totalNetLiquidity)}</p>
					<p class="mt-1 text-sm text-indigo-100">${money(data.totalCash)} in cash</p>
				</div>
			{/if}
		</div>
		<div class="absolute -top-20 -right-12 h-72 w-72 rounded-full bg-white/10"></div>
		<div class="absolute right-24 -bottom-32 h-72 w-72 rounded-full bg-indigo-400/30"></div>
	</section>

	<section class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
		{#each data.portfolios as portfolio (portfolio.id)}
			<a
				href={resolve('/portfolio/[id]', { id: String(portfolio.id) })}
				class="group flex flex-col rounded-xl border border-slate-200 bg-white p-5 text-slate-900 no-underline shadow-sm transition hover:-translate-y-0.5 hover:border-indigo-200 hover:shadow-lg hover:shadow-indigo-100"
			>
				<div class="flex items-start justify-between gap-3">
					<div class="min-w-0">
						<p class="truncate text-lg font-semibold group-hover:text-indigo-700">
							{portfolio.name}
						</p>
						<p class="mt-0.5 text-xs text-slate-500">Since {shortDate(portfolio.createdAt)}</p>
					</div>
					<div class="flex shrink-0 gap-1.5">
						<span class="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-semibold text-slate-600"
							>{portfolio.currency}</span
						>
						{#if portfolio.isPublic}<span
								class="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-semibold text-emerald-700"
								>Public</span
							>{/if}
					</div>
				</div>
				<p class="mt-6 text-xs font-semibold tracking-wider text-slate-500 uppercase">
					Net liquidity
				</p>
				<p class="mt-1 text-3xl font-semibold tabular-nums">${money(portfolio.netLiquidity)}</p>
				<div class="mt-4 flex gap-6 border-t border-slate-100 pt-4 text-sm text-slate-500">
					<p>
						<span class="font-semibold text-slate-900 tabular-nums">${money(portfolio.cash)}</span> cash
					</p>
					<p>
						<span class="font-semibold text-slate-900">{portfolio.numHoldings}</span>
						holding{pluralize(portfolio.numHoldings)}
					</p>
				</div>
			</a>
		{/each}

		<div
			class={[
				'rounded-xl border border-dashed border-slate-300 bg-white/60 p-5',
				!hasPortfolios && 'sm:col-span-2 lg:col-span-3'
			]}
		>
			<p class="text-lg font-semibold text-slate-900">
				{hasPortfolios ? 'New portfolio' : 'Create your first portfolio'}
			</p>
			<p class="mt-1 text-sm text-slate-500">
				Separate accounts or strategies, e.g. "Long term" or "TFSA".
			</p>
			<form method="post" class="mt-5 space-y-4" use:enhance>
				<div
					class={['grid gap-4', hasPortfolios ? 'grid-cols-[2fr_1fr]' : 'sm:grid-cols-[2fr_1fr]']}
				>
					<Field
						label="Name"
						name="name"
						maxlength={100}
						required
						value={values?.name ?? 'Main'}
						errors={errors?.fields.name}
					/>
					<Field
						label="Currency"
						name="currency"
						maxlength={3}
						required
						value={values?.currency ?? 'USD'}
						errors={errors?.fields.currency}
					/>
				</div>
				<label class="flex items-center gap-2 text-sm text-slate-600">
					<input
						type="checkbox"
						name="is_public"
						id="id_is_public"
						class="size-4 accent-indigo-600"
						checked={values ? 'is_public' in values : false}
					/>
					Visible to friends
				</label>
				<button
					type="submit"
					class="w-full cursor-pointer rounded-lg bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-indigo-700"
					>Create portfolio</button
				>
			</form>
		</div>
	</section>
</div>
