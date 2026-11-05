<script lang="ts">
	import { resolve } from '$app/paths';
	import MarketPulse from '#lib/components/market/MarketPulse.svelte';
	import MarketSnapshot from '#lib/components/market/MarketSnapshot.svelte';
	import MarketStatus from '#lib/components/market/MarketStatus.svelte';
	import type { PreviousPrices } from '#lib/components/market/flash.ts';
	import type {
		MarketPulse as Pulse,
		MarketSnapshot as Snapshot,
		MarketStatus as Status,
		Ticker
	} from '#lib/types.ts';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	const FEATURES = [
		{
			color: 'bg-indigo-50 text-indigo-600',
			icon: 'M4 6h16M4 12h16M4 18h7',
			title: 'Portfolio tracking',
			text: 'Record stocks, ETFs, funds, and other investments with quantities and purchase prices in one organized portfolio.'
		},
		{
			color: 'bg-emerald-50 text-emerald-600',
			icon: 'M7 12l3-3 3 3 4-4m4 4a9 9 0 11-18 0 9 9 0 0118 0z',
			title: 'Performance insights',
			text: 'See your portfolio value, invested capital, returns, and individual position performance without digging through spreadsheets.'
		},
		{
			color: 'bg-cyan-50 text-cyan-600',
			icon: 'M11 3v18m4-14v10M7 8v8m12-6v4M3 10v4',
			title: 'Allocation overview',
			text: 'Understand how much of your portfolio is concentrated in individual assets and see your overall investment structure.'
		},
		{
			color: 'bg-amber-50 text-amber-600',
			icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M9 20H4v-2a3 3 0 015-2.83m8 4.83v-2a5 5 0 00-10 0v2m10 0H9',
			title: 'Social investing',
			text: 'Connect with friends, share portfolios selectively, and discover how people in your circle approach investing.'
		}
	];
	const STEPS = [
		{
			color: 'bg-indigo-500',
			title: 'Add your investments',
			text: 'Enter the assets you own, the number of shares, and your purchase information.'
		},
		{
			color: 'bg-cyan-500',
			title: 'Build your portfolio',
			text: 'Finance Tracker organizes your positions into a simple portfolio view with values, weights, and performance.'
		},
		{
			color: 'bg-emerald-500',
			title: 'Follow your progress',
			text: 'Return whenever you want to understand how your investments have changed and where your portfolio stands.'
		}
	];
	const INFO_CARDS = [
		{
			color: 'text-indigo-600',
			label: 'Visibility',
			title: "Your investments shouldn't live across scattered notes.",
			text: 'Bring your portfolio information together so you can see your positions and overall financial picture without jumping between multiple tools.'
		},
		{
			color: 'text-cyan-600',
			label: 'Perspective',
			title: 'Performance means more with context.',
			text: "Understand both portfolio-level results and individual positions instead of focusing only on whether today's market happens to be green or red."
		},
		{
			color: 'text-emerald-600',
			label: 'Long-term thinking',
			title: 'Built around your portfolio, not market noise.',
			text: 'Keep your attention on ownership, allocation, progress, and long-term portfolio development instead of endless market headlines.'
		}
	];

	// Live market widgets: refresh on an interval, flash prices that changed since the last refresh,
	// and stop entrance animations from replaying on every refresh.
	let pulse = $state<{ data: Pulse; previous: PreviousPrices; version: number } | null>(null);
	let snapshot = $state<{ data: Snapshot; previous: PreviousPrices; version: number } | null>(null);
	let pulseLoaded = $state(false);
	let snapshotLoaded = $state(false);
	let liveStatus = $state<Status | null>(null);
	let updated = $state('just now');

	const marketStatus = $derived(liveStatus ?? data.marketStatus);

	function prices(tickers: Pick<Ticker, 'symbol' | 'quote'>[]): PreviousPrices {
		return Object.fromEntries(
			tickers.filter((t) => t.quote).map((t) => [t.symbol, t.quote!.price])
		);
	}

	async function fetchJson<T>(url: string): Promise<T | null> {
		try {
			const response = await fetch(url);
			return response.ok ? await response.json() : null;
		} catch {
			return null;
		}
	}

	function stamp() {
		updated = new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
	}

	async function refreshPulse() {
		const next = await fetchJson<Pulse>('/api/market/pulse');
		if (!next) return;
		const old = pulse?.data;
		const previous = old
			? prices([old.headline, ...old.indexes, ...old.gainers, ...old.losers])
			: {};
		pulse = { data: next, previous, version: (pulse?.version ?? 0) + 1 };
		stamp();
		if (!pulseLoaded) setTimeout(() => (pulseLoaded = true), 1500);
	}

	async function refreshSnapshot() {
		const next = await fetchJson<Snapshot>('/api/market/snapshot');
		if (!next) return;
		const old = snapshot?.data;
		const previous = old ? prices([...old.indexes, ...old.stocks]) : {};
		snapshot = { data: next, previous, version: (snapshot?.version ?? 0) + 1 };
		liveStatus = next.marketStatus;
		stamp();
		if (!snapshotLoaded) setTimeout(() => (snapshotLoaded = true), 1500);
	}

	$effect(() => {
		const refresh = () => {
			refreshPulse();
			refreshSnapshot();
		};
		refresh();
		const timer = setInterval(refresh, data.refreshSeconds * 1000);
		return () => clearInterval(timer);
	});
</script>

<svelte:head>
	<title>Finance Tracker</title>
</svelte:head>

<!-- HERO -->
<section
	id="hero"
	class="grid gap-12 py-12 lg:grid-cols-[1fr_1fr] lg:items-center lg:gap-16 lg:py-20"
>
	<!-- LEFT -->
	<div>
		<div
			class="mb-5 inline-flex items-center gap-2 rounded-full border border-indigo-100 bg-indigo-50 px-3 py-1.5"
		>
			<span class="h-2 w-2 rounded-full bg-indigo-500"></span>
			<span class="text-xs font-bold tracking-wider text-indigo-600 uppercase">
				Personal Finance Tracker
			</span>
		</div>

		<h1
			class="max-w-3xl text-5xl leading-[1.05] font-bold tracking-tight text-slate-900 sm:text-6xl lg:text-7xl"
		>
			Understand your
			<span class="text-indigo-600">portfolio.</span>
			Invest with clarity.
		</h1>

		<p class="mt-6 max-w-2xl text-lg leading-8 text-slate-500">
			Track your investments, understand where your money is allocated, monitor performance, and
			share your progress with people you trust — all from one simple dashboard.
		</p>

		<div class="mt-8 flex flex-wrap gap-3">
			<a
				href={resolve('/account/register')}
				class="inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-5 py-3 text-sm font-semibold text-white no-underline shadow-sm transition hover:bg-indigo-700"
			>
				Create your portfolio

				<svg
					class="h-4 w-4"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
					aria-hidden="true"
				>
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
				</svg>
			</a>

			<a
				href={resolve('/account/login')}
				class="inline-flex items-center justify-center rounded-lg border border-slate-300 bg-white px-5 py-3 text-sm font-semibold text-slate-700 no-underline transition hover:border-slate-400 hover:bg-slate-50"
			>
				Log in
			</a>
		</div>

		<!-- QUICK VALUE PROPS -->
		<div
			class="mt-10 grid max-w-2xl grid-cols-1 gap-4 border-t border-slate-200 pt-6 sm:grid-cols-3"
		>
			<div>
				<div class="mb-2 flex items-center gap-2">
					<div
						class="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600"
					>
						<svg
							class="h-4 w-4"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
							aria-hidden="true"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M3 10h18M7 15h1m4 0h1m-8 4h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
							/>
						</svg>
					</div>
					<p class="text-sm font-bold text-slate-800">Holdings</p>
				</div>
				<p class="text-xs leading-5 text-slate-500">Keep every investment organized.</p>
			</div>

			<div>
				<div class="mb-2 flex items-center gap-2">
					<div
						class="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600"
					>
						<svg
							class="h-4 w-4"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
							aria-hidden="true"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M3 17l6-6 4 4 8-8"
							/>
						</svg>
					</div>
					<p class="text-sm font-bold text-slate-800">Performance</p>
				</div>
				<p class="text-xs leading-5 text-slate-500">Follow gains and losses clearly.</p>
			</div>

			<div>
				<div class="mb-2 flex items-center gap-2">
					<div class="flex h-8 w-8 items-center justify-center rounded-lg bg-cyan-50 text-cyan-600">
						<svg
							class="h-4 w-4"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
							aria-hidden="true"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0"
							/>
						</svg>
					</div>
					<p class="text-sm font-bold text-slate-800">Community</p>
				</div>
				<p class="text-xs leading-5 text-slate-500">Connect with trusted friends.</p>
			</div>
		</div>
	</div>

	<!-- DASHBOARD PREVIEW -->
	<div class="relative">
		<!-- DECORATIVE BACKGROUND -->
		<div
			class="absolute -inset-4 -z-10 rounded-3xl bg-linear-to-br from-indigo-100 via-slate-50 to-cyan-100 blur-2xl"
		></div>

		<div
			class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl shadow-slate-300/40"
			data-loaded={pulseLoaded || undefined}
		>
			{#if pulse}
				{#key pulse.version}
					<MarketPulse pulse={pulse.data} previous={pulse.previous} />
				{/key}
			{:else}
				<div class="space-y-6 p-6" aria-label="Loading market pulse">
					<div class="h-10 w-1/2 skeleton rounded-md"></div>
					<div class="h-12 w-2/3 skeleton rounded-md"></div>
					<div class="h-2.5 skeleton rounded-full"></div>
					<div class="grid grid-cols-3 gap-4">
						<div class="h-12 skeleton rounded-md"></div>
						<div class="h-12 skeleton rounded-md"></div>
						<div class="h-12 skeleton rounded-md"></div>
					</div>
					<div class="h-14 skeleton rounded-md"></div>
					<div class="h-14 skeleton rounded-md"></div>
					<div class="h-14 skeleton rounded-md"></div>
				</div>
			{/if}
		</div>
	</div>
</section>

<!-- MARKETS -->
<section class="border-t border-slate-200 py-12">
	<div class="mb-6 flex flex-wrap items-end justify-between gap-2">
		<div>
			<p class="mb-3 text-xs font-bold tracking-[0.18em] text-indigo-600 uppercase">
				Markets today
			</p>
			<h2 class="text-3xl font-bold tracking-tight text-slate-900">Major indexes &amp; stocks</h2>
		</div>
		<div class="flex items-center gap-3 text-xs text-slate-400">
			<MarketStatus status={marketStatus} />
			<span>Updated {updated} · Finnhub</span>
		</div>
	</div>

	<div data-loaded={snapshotLoaded || undefined}>
		{#if snapshot}
			{#key snapshot.version}
				<MarketSnapshot snapshot={snapshot.data} previous={snapshot.previous} />
			{/key}
		{:else}
			<div class="space-y-8" aria-label="Loading market data">
				<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
					<div class="h-44 skeleton rounded-xl"></div>
					<div class="h-44 skeleton rounded-xl"></div>
					<div class="h-44 skeleton rounded-xl"></div>
					<div class="h-44 skeleton rounded-xl"></div>
				</div>
				<div class="h-96 skeleton rounded-xl"></div>
			</div>
		{/if}
	</div>
</section>

<!-- PRODUCT INTRO -->
<section class="border-t border-slate-200 py-16 lg:py-20">
	<div class="grid gap-10 lg:grid-cols-[0.8fr_1.2fr] lg:gap-20">
		<div>
			<p class="mb-3 text-xs font-bold tracking-[0.18em] text-indigo-600 uppercase">
				One portfolio. One view.
			</p>

			<h2 class="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
				Know exactly where your money is going.
			</h2>

			<p class="mt-5 leading-7 text-slate-500">
				Finance Tracker turns individual positions into a complete view of your investment portfolio
				— helping you understand what you own, how it is performing, and how your portfolio is
				structured.
			</p>
		</div>

		<div class="grid gap-4 sm:grid-cols-2">
			{#each FEATURES as feature (feature.title)}
				<div
					class="rounded-xl border border-slate-200 bg-white p-6 transition hover:-translate-y-1 hover:shadow-lg hover:shadow-slate-200/60"
				>
					<div class="mb-5 flex h-11 w-11 items-center justify-center rounded-xl {feature.color}">
						<svg
							class="h-5 w-5"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
							aria-hidden="true"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d={feature.icon}
							/>
						</svg>
					</div>

					<h3 class="text-lg font-bold text-slate-900">{feature.title}</h3>

					<p class="mt-2 text-sm leading-6 text-slate-500">{feature.text}</p>
				</div>
			{/each}
		</div>
	</div>
</section>

<!-- HOW IT WORKS -->
<section class="rounded-2xl bg-slate-900 px-6 py-12 text-white sm:px-10 lg:px-12 lg:py-16">
	<div class="mb-10 max-w-2xl">
		<p class="mb-3 text-xs font-bold tracking-[0.18em] text-indigo-300 uppercase">
			Simple by design
		</p>

		<h2 class="text-3xl font-bold tracking-tight sm:text-4xl">
			From scattered investments to one clear portfolio.
		</h2>

		<p class="mt-4 leading-7 text-slate-400">Getting started takes only a few steps.</p>
	</div>

	<div class="grid gap-8 md:grid-cols-3">
		{#each STEPS as step, i (step.title)}
			<div>
				<div
					class="mb-5 flex h-10 w-10 items-center justify-center rounded-full font-bold {step.color}"
				>
					{i + 1}
				</div>

				<h3 class="text-lg font-bold">{step.title}</h3>

				<p class="mt-2 text-sm leading-6 text-slate-400">{step.text}</p>
			</div>
		{/each}
	</div>
</section>

<!-- INFORMATION SECTION -->
<section class="py-16 lg:py-20">
	<div class="grid gap-5 md:grid-cols-3">
		{#each INFO_CARDS as card (card.label)}
			<article class="rounded-xl border border-slate-200 bg-slate-50 p-6">
				<p class="mb-4 text-xs font-bold tracking-wider uppercase {card.color}">{card.label}</p>

				<h3 class="text-xl font-bold text-slate-900">{card.title}</h3>

				<p class="mt-3 text-sm leading-6 text-slate-500">{card.text}</p>
			</article>
		{/each}
	</div>
</section>

<!-- PRIVACY / TRUST -->
<section class="border-y border-slate-200 py-12">
	<div class="flex flex-col gap-8 lg:flex-row lg:items-center lg:justify-between">
		<div class="max-w-2xl">
			<div class="mb-3 flex items-center gap-2 text-emerald-600">
				<svg
					class="h-5 w-5"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
					aria-hidden="true"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M12 11c1.657 0 3-1.343 3-3V6a3 3 0 10-6 0v2c0 1.657 1.343 3 3 3zm6 0H6a2 2 0 00-2 2v7h16v-7a2 2 0 00-2-2z"
					/>
				</svg>

				<span class="text-xs font-bold tracking-wider uppercase">Your portfolio. Your control.</span
				>
			</div>

			<h2 class="text-2xl font-bold text-slate-900">Share only what you choose to share.</h2>

			<p class="mt-3 leading-7 text-slate-500">
				Your investment portfolio is personal. Social features are designed around selective
				sharing, so you remain in control of how your portfolio is presented to others.
			</p>
		</div>

		<div class="grid grid-cols-2 gap-3 sm:grid-cols-3">
			<div class="rounded-lg border border-slate-200 bg-white px-5 py-4">
				<p class="text-xs text-slate-400">Portfolio</p>
				<p class="mt-1 text-sm font-bold text-slate-800">Organized</p>
			</div>

			<div class="rounded-lg border border-slate-200 bg-white px-5 py-4">
				<p class="text-xs text-slate-400">Sharing</p>
				<p class="mt-1 text-sm font-bold text-slate-800">Selective</p>
			</div>

			<div class="col-span-2 rounded-lg border border-slate-200 bg-white px-5 py-4 sm:col-span-1">
				<p class="text-xs text-slate-400">Experience</p>
				<p class="mt-1 text-sm font-bold text-slate-800">Simple</p>
			</div>
		</div>
	</div>
</section>

<!-- FINAL CTA -->
<section class="py-16 lg:py-20">
	<div class="relative overflow-hidden rounded-2xl bg-indigo-600 px-6 py-12 sm:px-10 lg:px-14">
		<!-- DECORATION -->
		<div class="absolute -top-24 -right-20 h-64 w-64 rounded-full bg-white/10"></div>
		<div class="absolute right-32 -bottom-32 h-64 w-64 rounded-full bg-indigo-400/30"></div>

		<div class="relative flex flex-col gap-8 lg:flex-row lg:items-center lg:justify-between">
			<div class="max-w-2xl">
				<p class="mb-3 text-xs font-bold tracking-[0.18em] text-indigo-200 uppercase">
					Start tracking today
				</p>

				<h2 class="text-3xl font-bold tracking-tight text-white sm:text-4xl">
					Build a clearer picture of your financial future.
				</h2>

				<p class="mt-4 max-w-xl leading-7 text-indigo-100">
					Create your portfolio, organize your investments, and start following your progress from
					one simple dashboard.
				</p>
			</div>

			<div class="flex shrink-0 flex-wrap gap-3">
				<a
					href={resolve('/account/register')}
					class="rounded-lg bg-white px-5 py-3 text-sm font-bold text-indigo-600 no-underline shadow-sm transition hover:bg-indigo-50"
				>
					Create free account
				</a>

				<a
					href={resolve('/account/login')}
					class="rounded-lg border border-indigo-400 px-5 py-3 text-sm font-bold text-white no-underline transition hover:bg-indigo-500"
				>
					Log in
				</a>
			</div>
		</div>
	</div>
</section>
