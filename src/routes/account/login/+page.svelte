<script lang="ts">
	import { resolve } from '$app/paths';
	import { enhance } from '$app/forms';
	import type { PageProps } from './$types';

	let { data, form }: PageProps = $props();

	let reveal = $state(false);
	let passwordInput = $state<HTMLInputElement>();

	const errors = $derived(form?.errors);
	const inputClass = (field: string) => [
		'h-11 w-full rounded-lg border bg-white px-3.5 text-sm text-slate-900 shadow-sm transition outline-none placeholder:text-slate-400 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100',
		errors?.fields[field] ? 'border-red-400' : 'border-slate-300'
	];

	function togglePassword() {
		reveal = !reveal;
		passwordInput?.focus();
	}
</script>

<svelte:head>
	<title>Log in | Finance Tracker</title>
</svelte:head>

<div
	class="mx-auto mt-8 grid max-w-5xl overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl shadow-slate-900/5 lg:grid-cols-[1.05fr_1fr]"
>
	<!-- BRAND PANEL -->
	<aside
		class="relative hidden overflow-hidden bg-linear-to-br from-indigo-600 via-indigo-700 to-slate-900 p-10 text-white lg:flex lg:flex-col lg:justify-between"
	>
		<!-- Background grid -->
		<svg
			class="pointer-events-none absolute inset-0 h-full w-full opacity-[0.07]"
			aria-hidden="true"
		>
			<defs>
				<pattern id="login-grid" width="32" height="32" patternUnits="userSpaceOnUse">
					<path d="M32 0H0V32" fill="none" stroke="white" stroke-width="1" />
				</pattern>
			</defs>
			<rect width="100%" height="100%" fill="url(#login-grid)" />
		</svg>
		<div
			class="pointer-events-none absolute -top-24 -right-24 h-72 w-72 rounded-full bg-indigo-400/30 blur-3xl"
			aria-hidden="true"
		></div>

		<div class="relative">
			<div
				class="mb-6 inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-3 py-1.5"
			>
				<span class="h-2 w-2 rounded-full bg-emerald-400"></span>
				<span class="text-xs font-bold tracking-wider text-indigo-100 uppercase"
					>Finance Tracker</span
				>
			</div>
			<h2 class="text-4xl leading-[1.1] font-bold tracking-tight">
				Your money,<br />
				<span class="text-indigo-200">at a glance.</span>
			</h2>
			<p class="mt-4 max-w-sm text-sm leading-6 text-indigo-100/80">
				Pick up right where you left off: track performance, review sessions, and see where every
				dollar sits.
			</p>
		</div>

		<!-- Preview card -->
		<div
			class="relative my-10 rounded-xl border border-white/10 bg-white/10 p-5 shadow-2xl shadow-slate-950/30 backdrop-blur-sm"
		>
			<div class="flex items-start justify-between">
				<div>
					<div class="text-xs font-semibold tracking-wider text-indigo-200 uppercase">
						Portfolio value
					</div>
					<div class="mt-1 text-2xl font-bold">$48,215.30</div>
				</div>
				<span
					class="inline-flex items-center gap-1 rounded-full bg-emerald-400/15 px-2 py-1 text-xs font-semibold text-emerald-300"
				>
					<svg
						class="h-3 w-3"
						fill="none"
						stroke="currentColor"
						stroke-width="2.5"
						viewBox="0 0 24 24"
						aria-hidden="true"
					>
						<path stroke-linecap="round" stroke-linejoin="round" d="M5 15l7-7 7 7" />
					</svg>
					12.4%
				</span>
			</div>
			<svg
				class="mt-4 h-20 w-full"
				viewBox="0 0 300 80"
				preserveAspectRatio="none"
				aria-hidden="true"
			>
				<defs>
					<linearGradient id="login-spark" x1="0" x2="0" y1="0" y2="1">
						<stop offset="0%" stop-color="#6ee7b7" stop-opacity="0.35" />
						<stop offset="100%" stop-color="#6ee7b7" stop-opacity="0" />
					</linearGradient>
				</defs>
				<path
					d="M0 62 L25 58 L50 64 L75 50 L100 54 L125 40 L150 44 L175 32 L200 36 L225 22 L250 26 L275 14 L300 10 L300 80 L0 80 Z"
					fill="url(#login-spark)"
				/>
				<path
					d="M0 62 L25 58 L50 64 L75 50 L100 54 L125 40 L150 44 L175 32 L200 36 L225 22 L250 26 L275 14 L300 10"
					fill="none"
					stroke="#6ee7b7"
					stroke-width="2"
					stroke-linejoin="round"
					stroke-linecap="round"
					vector-effect="non-scaling-stroke"
				/>
			</svg>
			<div class="mt-3 flex justify-between text-[11px] font-medium text-indigo-200/70">
				<span>Jan</span><span>Mar</span><span>May</span><span>Jul</span><span>Sep</span>
			</div>
		</div>

		<ul class="relative m-0 grid list-none gap-3 p-0 text-sm text-indigo-100">
			<li class="flex items-center gap-3">
				<span class="flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-white/10">
					<svg
						class="h-3.5 w-3.5"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						viewBox="0 0 24 24"
						aria-hidden="true"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
						/>
					</svg>
				</span>
				Your data stays private to your account
			</li>
			<li class="flex items-center gap-3">
				<span class="flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-white/10">
					<svg
						class="h-3.5 w-3.5"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						viewBox="0 0 24 24"
						aria-hidden="true"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
						/>
					</svg>
				</span>
				Bankroll and portfolio tracking in one place
			</li>
		</ul>
	</aside>

	<!-- FORM -->
	<section class="flex flex-col justify-center px-6 py-10 sm:px-12 sm:py-14">
		<div class="mx-auto w-full max-w-sm">
			<h1 class="text-3xl leading-tight font-bold tracking-tight text-slate-900">Welcome back</h1>
			<p class="mt-2 text-sm text-slate-500">Log in to continue to your dashboard.</p>

			<form method="post" class="mt-8" novalidate use:enhance>
				<input type="hidden" name="next" value={data.next} />

				{#if errors?.nonField.length}
					<div
						class="mb-5 flex gap-3 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
						role="alert"
					>
						<svg
							class="mt-0.5 h-4 w-4 shrink-0"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
							viewBox="0 0 24 24"
							aria-hidden="true"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"
							/>
						</svg>
						<div>
							{#each errors.nonField as error, i (i)}<p>{error}</p>{/each}
						</div>
					</div>
				{/if}

				<div class="space-y-5">
					<div>
						<div class="mb-1.5 flex items-center justify-between">
							<label class="text-sm font-semibold text-slate-700" for="id_username">Username</label>
						</div>
						<input
							id="id_username"
							name="username"
							autocomplete="username"
							maxlength="150"
							value={form?.values.username ?? ''}
							class={inputClass('username')}
						/>
						{#each errors?.fields.username ?? [] as error, i (i)}
							<p class="mt-1.5 text-xs text-red-600">{error}</p>
						{/each}
					</div>

					<div>
						<div class="mb-1.5 flex items-center justify-between">
							<label class="text-sm font-semibold text-slate-700" for="id_password">Password</label>
							<a
								class="text-xs font-medium text-indigo-600 no-underline hover:text-indigo-700 hover:underline"
								href={resolve('/account/password/reset')}>Forgot password?</a
							>
						</div>
						<div class="relative">
							<input
								bind:this={passwordInput}
								id="id_password"
								name="password"
								type={reveal ? 'text' : 'password'}
								autocomplete="current-password"
								class={[inputClass('password'), 'pr-12']}
							/>
							<button
								type="button"
								onclick={togglePassword}
								class="absolute inset-y-0 right-0 flex w-11 cursor-pointer items-center justify-center rounded-r-lg border-0 bg-transparent text-slate-400 transition-colors hover:text-slate-700"
								aria-label={reveal ? 'Hide password' : 'Show password'}
								aria-pressed={reveal}
							>
								{#if reveal}
									<svg
										class="h-5 w-5"
										fill="none"
										stroke="currentColor"
										stroke-width="1.7"
										viewBox="0 0 24 24"
										aria-hidden="true"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											d="M3 3l18 18M10.6 5.1A10.8 10.8 0 0112 5c6.5 0 10 7 10 7a17.6 17.6 0 01-3.2 4.2M6.6 6.6C3.8 8.5 2 12 2 12s3.5 7 10 7a9.9 9.9 0 005.4-1.6M9.9 9.9a3 3 0 004.2 4.2"
										/>
									</svg>
								{:else}
									<svg
										class="h-5 w-5"
										fill="none"
										stroke="currentColor"
										stroke-width="1.7"
										viewBox="0 0 24 24"
										aria-hidden="true"
									>
										<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z" />
										<circle cx="12" cy="12" r="3" />
									</svg>
								{/if}
							</button>
						</div>
						{#each errors?.fields.password ?? [] as error, i (i)}
							<p class="mt-1.5 text-xs text-red-600">{error}</p>
						{/each}
					</div>
				</div>

				<button
					type="submit"
					class="mt-7 flex h-11 w-full cursor-pointer items-center justify-center gap-2 rounded-lg border-0 bg-indigo-600 text-sm font-semibold text-white shadow-sm shadow-indigo-600/30 transition hover:bg-indigo-700 focus-visible:ring-4 focus-visible:ring-indigo-200 focus-visible:outline-none"
				>
					Log in
					<svg
						class="h-4 w-4"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						viewBox="0 0 24 24"
						aria-hidden="true"
					>
						<path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
					</svg>
				</button>
			</form>

			<div
				class="my-8 flex items-center gap-4 text-xs text-slate-400 before:h-px before:flex-1 before:bg-slate-200 after:h-px after:flex-1 after:bg-slate-200"
			>
				New to Finance Tracker?
			</div>

			<a
				href={resolve('/account/register')}
				class="flex h-11 w-full items-center justify-center rounded-lg border border-slate-300 bg-white text-sm font-semibold text-slate-700 no-underline transition hover:border-slate-400 hover:bg-slate-50"
			>
				Create a free account
			</a>
		</div>
	</section>
</div>
