<script lang="ts">
	import { resolve } from '$app/paths';
	import { enhance, type SubmitFunction } from '$app/forms';
	import Allocation from '#lib/components/Allocation.svelte';
	import Field from '#lib/components/Field.svelte';
	import Segmented from '#lib/components/Segmented.svelte';
	import { fixed, money, shortDate, shortTime, signedMoney } from '#lib/format.ts';
	import type { PageProps } from './$types';

	let { data, form }: PageProps = $props();

	const p = $derived(data.portfolio);
	const notice = $derived(form && 'notice' in form ? form.notice : null);
	const trade = $derived(form && 'form' in form && form.form === 'trade' ? form : null);
	const cash = $derived(form && 'form' in form && form.form === 'cash' ? form : null);

	// Disable a form's submit button while its request is in flight.
	let pending = $state<Record<string, boolean>>({});
	const track =
		(name: string): SubmitFunction =>
		() => {
			pending[name] = true;
			return async ({ update }) => {
				await update();
				pending[name] = false;
			};
		};

	const KIND_STYLES: Record<string, string> = {
		BUY: 'bg-emerald-100 text-emerald-700',
		SELL: 'bg-red-100 text-red-700',
		DEPOSIT: 'bg-indigo-100 text-indigo-700',
		WITHDRAW: 'bg-amber-100 text-amber-700'
	};
	const kindLabel = (kind: string) => kind.charAt(0) + kind.slice(1).toLowerCase();
	const gainColor = (value: number) => (value >= 0 ? 'text-emerald-600' : 'text-red-600');
</script>

<svelte:head>
	<title>{p.name} | Finance Tracker</title>
</svelte:head>

<div class="space-y-6 pt-8">
	<div>
		<a
			href={resolve('/portfolio')}
			class="text-sm font-semibold text-slate-500 no-underline hover:text-slate-900"
			>&larr; All portfolios</a
		>
		<div class="mt-3 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
			<div class="min-w-0">
				<div class="flex flex-wrap items-center gap-2">
					<h1 class="truncate text-3xl font-semibold tracking-tight text-slate-900">{p.name}</h1>
					<span class="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-semibold text-slate-600"
						>{p.currency}</span
					>
					{#if p.isPublic}
						<span
							class="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-semibold text-emerald-700"
							>Visible to friends</span
						>
					{:else}
						<span class="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-semibold text-slate-500"
							>Private</span
						>
					{/if}
				</div>
				<p class="mt-1 text-sm text-slate-500">
					Values use the latest saved prices. Refresh to fetch live quotes.
				</p>
			</div>
			<div class="flex shrink-0 items-center gap-2">
				<form method="post" action="?/refresh" class="m-0" use:enhance={track('refresh')}>
					<button
						type="submit"
						disabled={pending.refresh}
						class="group inline-flex cursor-pointer items-center gap-2 rounded-lg border border-slate-300 bg-white px-3.5 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:opacity-60"
					>
						<svg
							class="size-4 group-disabled:animate-spin"
							viewBox="0 0 20 20"
							fill="none"
							stroke="currentColor"
							stroke-width="1.8"
							aria-hidden="true"
							><path
								d="M16.5 10a6.5 6.5 0 1 1-1.9-4.6M16.5 3.5v3h-3"
								stroke-linecap="round"
								stroke-linejoin="round"
							/></svg
						>
						Refresh prices
					</button>
				</form>
				<a
					href={resolve('/portfolio/[id]/settings', { id: String(p.id) })}
					class="rounded-lg border border-slate-300 bg-white px-3.5 py-2 text-sm font-semibold text-slate-700 no-underline shadow-sm transition hover:bg-slate-50"
					>Settings</a
				>
			</div>
		</div>
	</div>

	<div class="space-y-6">
		{#if notice}
			{#key notice}
				<output
					class="block animate-fade-up rounded-md border border-l-4 border-slate-200 border-l-emerald-600 bg-emerald-50 px-4 py-3 text-sm text-slate-700 shadow-sm"
					>{notice}</output
				>
			{/key}
		{/if}

		<!-- Summary -->
		<section class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
			<article
				class="rounded-xl border border-t-4 border-indigo-100 border-t-indigo-500 bg-white p-5 shadow-sm"
			>
				<p class="text-xs font-semibold tracking-wider text-slate-500 uppercase">Net liquidity</p>
				<p class="mt-3 text-3xl font-semibold text-slate-900 tabular-nums">
					${money(data.netLiquidity)}
				</p>
				<p class="mt-2 text-sm text-slate-500">Cash plus holdings</p>
			</article>
			<article
				class="rounded-xl border border-t-4 border-slate-200 border-t-slate-400 bg-white p-5 shadow-sm"
			>
				<p class="text-xs font-semibold tracking-wider text-slate-500 uppercase">Cash</p>
				<p class="mt-3 text-3xl font-semibold text-slate-900 tabular-nums">${money(p.cash)}</p>
				<p class="mt-2 text-sm text-slate-500">{fixed(data.cashPct, 1)}% of portfolio</p>
			</article>
			<article
				class="rounded-xl border border-t-4 border-cyan-100 border-t-cyan-500 bg-white p-5 shadow-sm"
			>
				<p class="text-xs font-semibold tracking-wider text-slate-500 uppercase">Unrealized gain</p>
				<p class="mt-3 text-3xl font-semibold tabular-nums {gainColor(data.unrealizedGain)}">
					{signedMoney(data.unrealizedGain)}
				</p>
				<p class="mt-2 text-sm text-slate-500">
					{fixed(data.unrealizedPct, 2)}% on ${money(data.costBasis)} invested
				</p>
			</article>
			<article
				class="rounded-xl border border-t-4 border-amber-100 border-t-amber-400 bg-white p-5 shadow-sm"
			>
				<p class="text-xs font-semibold tracking-wider text-slate-500 uppercase">Realized gain</p>
				<p class="mt-3 text-3xl font-semibold tabular-nums {gainColor(data.realizedGain)}">
					{signedMoney(data.realizedGain)}
				</p>
				<p class="mt-2 text-sm text-slate-500">Locked in from sales</p>
			</article>
		</section>

		<div class="grid gap-6 lg:grid-cols-3 lg:items-start">
			<!-- Holdings -->
			<section
				class="min-w-0 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm lg:col-span-2"
			>
				<div class="border-b border-slate-200 px-5 py-5 sm:px-6">
					<p class="text-xs font-semibold tracking-wider text-slate-500 uppercase">Positions</p>
					<h2 class="mt-1 text-2xl font-semibold tracking-tight text-slate-900">Holdings</h2>

					{#if data.netLiquidity}
						<div class="mt-4">
							<Allocation items={data.holdings} cashPct={data.cashPct} />
						</div>
					{/if}
				</div>

				{#if data.holdings.length}
					<div class="overflow-x-auto">
						<table class="w-full min-w-160 text-left">
							<thead
								class="border-b border-slate-100 bg-slate-50 text-xs tracking-wider text-slate-500 uppercase"
							>
								<tr>
									<th class="px-6 py-3 font-semibold">Symbol</th>
									<th class="px-4 py-3 text-right font-semibold">Shares</th>
									<th class="px-4 py-3 text-right font-semibold">Avg cost</th>
									<th class="px-4 py-3 text-right font-semibold">Market value</th>
									<th class="px-6 py-3 text-right font-semibold">Unrealized</th>
								</tr>
							</thead>
							<tbody class="divide-y divide-slate-100">
								{#each data.holdings as holding (holding.symbol)}
									<tr class="transition-colors hover:bg-slate-50">
										<td class="px-6 py-4">
											<p class="font-semibold text-slate-900">{holding.symbol}</p>
											<p class="mt-0.5 text-xs text-slate-500">
												{fixed(holding.weight, 1)}% of portfolio
											</p>
										</td>
										<td class="px-4 py-4 text-right text-sm text-slate-600 tabular-nums"
											>{holding.displayQuantity}</td
										>
										<td class="px-4 py-4 text-right text-sm text-slate-600 tabular-nums"
											>${money(holding.avgCost)}</td
										>
										<td class="px-4 py-4 text-right tabular-nums">
											<p class="text-sm font-semibold text-slate-900">
												${money(holding.marketValue)}
											</p>
											<p class="mt-0.5 text-xs text-slate-500">cost ${money(holding.costBasis)}</p>
										</td>
										<td class="px-6 py-4 text-right">
											<span
												class={[
													'inline-flex rounded-full px-2.5 py-1 text-sm font-semibold tabular-nums',
													holding.unrealizedGain >= 0
														? 'bg-emerald-100 text-emerald-700'
														: 'bg-red-100 text-red-700'
												]}>{signedMoney(holding.unrealizedGain)}</span
											>
											<p class="mt-1 text-xs tabular-nums {gainColor(holding.gainPct)}">
												{fixed(holding.gainPct, 2)}%
											</p>
										</td>
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				{:else}
					<div class="px-6 py-16 text-center">
						<p class="text-lg font-semibold text-slate-900">No holdings yet</p>
						<p class="mt-2 text-sm text-slate-500">
							{p.cash
								? 'Use the trade panel to buy your first position.'
								: 'Deposit cash, then buy your first position.'}
						</p>
					</div>
				{/if}
			</section>

			<!-- Trade + cash -->
			<div class="space-y-6">
				<section class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
					<p class="text-xs font-semibold tracking-wider text-slate-500 uppercase">Order</p>
					<h2 class="mt-1 text-xl font-semibold tracking-tight text-slate-900">Trade</h2>
					<form
						method="post"
						action="?/trade"
						class="group mt-4 space-y-4"
						use:enhance={track('trade')}
					>
						<Segmented
							name="side"
							label="Side"
							selected={trade?.values.side ?? 'BUY'}
							options={[
								{ value: 'BUY', label: 'Buy' },
								{ value: 'SELL', label: 'Sell', negative: true }
							]}
						/>
						{#if trade?.errors.nonField.length}
							<div class="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700" role="alert">
								{trade.errors.nonField.join(' ')}
							</div>
						{/if}
						<Field
							label="Symbol"
							name="symbol"
							maxlength={12}
							required
							value={trade?.values.symbol ?? ''}
							errors={trade?.errors.fields.symbol}
						/>
						<div class="grid grid-cols-2 gap-3">
							<Field
								label="Quantity"
								name="quantity"
								type="number"
								step="0.000001"
								min="0.000001"
								required
								value={trade?.values.quantity ?? ''}
								errors={trade?.errors.fields.quantity}
							/>
							<Field
								label="Price per share"
								name="price"
								type="number"
								step="0.0001"
								min="0.0001"
								required
								value={trade?.values.price ?? ''}
								errors={trade?.errors.fields.price}
							/>
						</div>
						<Field
							label="Fee"
							name="fee"
							type="number"
							step="0.01"
							min="0"
							value={trade?.values.fee ?? '0'}
							errors={trade?.errors.fields.fee}
						/>
						<label
							class="flex items-start gap-2.5 rounded-lg bg-slate-50 p-3 text-sm group-has-[input[value=SELL]:checked]:hidden"
						>
							<input
								type="checkbox"
								name="use_cash"
								id="id_use_cash"
								class="mt-0.5 size-4 shrink-0 accent-indigo-600"
								checked={trade ? 'use_cash' in trade.values : true}
							/>
							<span
								><span class="font-semibold text-slate-700">Pay from cash</span><span
									class="mt-0.5 block text-xs text-slate-500"
									>Untick to record shares you bought outside this app.</span
								></span
							>
						</label>
						<button
							type="submit"
							disabled={pending.trade}
							class="w-full cursor-pointer rounded-lg bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-indigo-700 disabled:opacity-60"
							>Place order</button
						>
					</form>
				</section>

				<section class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
					<div class="flex items-baseline justify-between">
						<div>
							<p class="text-xs font-semibold tracking-wider text-slate-500 uppercase">Funding</p>
							<h2 class="mt-1 text-xl font-semibold tracking-tight text-slate-900">Cash</h2>
						</div>
						<p class="text-sm text-slate-500 tabular-nums">${money(p.cash)} available</p>
					</div>
					<form method="post" action="?/cash" class="mt-4 space-y-4" use:enhance={track('cash')}>
						<Segmented
							name="action"
							label="Action"
							selected={cash?.values.action ?? 'DEPOSIT'}
							options={[
								{ value: 'DEPOSIT', label: 'Deposit' },
								{ value: 'WITHDRAW', label: 'Withdraw', negative: true }
							]}
						/>
						{#if cash?.errors.nonField.length}
							<div class="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700" role="alert">
								{cash.errors.nonField.join(' ')}
							</div>
						{/if}
						<Field
							label="Amount"
							name="amount"
							type="number"
							step="0.01"
							min="0.01"
							required
							value={cash?.values.amount ?? ''}
							errors={cash?.errors.fields.amount}
						/>
						<button
							type="submit"
							disabled={pending.cash}
							class="w-full cursor-pointer rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-900 transition hover:bg-slate-50 disabled:opacity-60"
							>Confirm</button
						>
					</form>
				</section>
			</div>
		</div>

		<!-- Activity -->
		<section class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
			<div class="border-b border-slate-200 px-5 py-5 sm:px-6">
				<p class="text-xs font-semibold tracking-wider text-slate-500 uppercase">History</p>
				<h2 class="mt-1 text-2xl font-semibold tracking-tight text-slate-900">Recent activity</h2>
			</div>
			{#if data.transactions.length}
				<div class="overflow-x-auto">
					<table class="w-full min-w-160 text-left">
						<thead
							class="border-b border-slate-100 bg-slate-50 text-xs tracking-wider text-slate-500 uppercase"
						>
							<tr>
								<th class="px-6 py-3 font-semibold">Date</th>
								<th class="px-4 py-3 font-semibold">Type</th>
								<th class="px-4 py-3 font-semibold">Details</th>
								<th class="px-4 py-3 text-right font-semibold">Amount</th>
								<th class="px-6 py-3 text-right font-semibold">Realized</th>
							</tr>
						</thead>
						<tbody class="divide-y divide-slate-100">
							{#each data.transactions as txn (txn.id)}
								<tr class="transition-colors hover:bg-slate-50">
									<td class="px-6 py-3.5 text-sm text-slate-600"
										>{shortDate(txn.executedAt)}<span class="block text-xs text-slate-400"
											>{shortTime(txn.executedAt)}</span
										></td
									>
									<td class="px-4 py-3.5">
										<span
											class="inline-flex rounded-full px-2.5 py-0.5 text-xs font-semibold {KIND_STYLES[
												txn.kind
											] ?? 'bg-slate-100 text-slate-600'}">{kindLabel(txn.kind)}</span
										>
									</td>
									<td class="px-4 py-3.5 text-sm text-slate-600">
										{#if txn.symbol}
											<span class="font-semibold text-slate-900">{txn.symbol}</span> &middot;
											{txn.displayQuantity} @ ${money(txn.price)}
											{#if txn.fee}<span class="block text-xs text-slate-400"
													>fee ${money(txn.fee)}</span
												>{/if}
										{:else}
											Cash
										{/if}
									</td>
									<td
										class="px-4 py-3.5 text-right text-sm font-semibold text-slate-900 tabular-nums"
										>${money(txn.amount)}</td
									>
									<td class="px-6 py-3.5 text-right text-sm font-semibold tabular-nums">
										{#if txn.realizedGain !== null}
											<span class={gainColor(txn.realizedGain)}
												>{signedMoney(txn.realizedGain)}</span
											>
										{:else}
											<span class="text-slate-300">&mdash;</span>
										{/if}
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			{:else}
				<div class="px-6 py-12 text-center text-sm text-slate-500">
					Deposits, trades and withdrawals will show up here.
				</div>
			{/if}
		</section>
	</div>
</div>
