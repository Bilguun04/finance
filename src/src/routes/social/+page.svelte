<script lang="ts">
	import { resolve } from '$app/paths';
	import { enhance } from '$app/forms';
	import Avatar from '#lib/components/Avatar.svelte';
	import { pluralize, timesince } from '#lib/format.ts';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	const smallButton = 'cursor-pointer rounded-lg px-3 py-1.5 text-sm font-semibold transition';
	const primary = `${smallButton} bg-indigo-600 text-white hover:bg-indigo-700`;
	const secondary = `${smallButton} border border-slate-300 bg-white text-slate-700 hover:bg-slate-50`;
</script>

<svelte:head>
	<title>Friends | Finance Tracker</title>
</svelte:head>

<div class="space-y-6 pt-8">
	<div>
		<p class="text-xs font-semibold tracking-wider text-indigo-600 uppercase">Social</p>
		<h1 class="mt-1 text-3xl font-semibold tracking-tight text-slate-900">Friends</h1>
		<p class="mt-1 text-sm text-slate-500">
			Friends see the allocation of portfolios you mark "Visible to friends", as percentages only,
			never dollar amounts.
		</p>
	</div>

	<div class="grid gap-6 lg:grid-cols-3 lg:items-start">
		<!-- Friend list -->
		<section
			class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm lg:col-span-2"
		>
			<div class="flex items-baseline justify-between border-b border-slate-200 px-5 py-5 sm:px-6">
				<h2 class="text-xl font-semibold tracking-tight text-slate-900">Your friends</h2>
				<p class="text-sm text-slate-500">{data.friends.length} total</p>
			</div>
			{#if data.friends.length}
				<ul class="m-0 list-none divide-y divide-slate-100 p-0">
					{#each data.friends as friend (friend.id)}
						<li>
							<a
								href={resolve('/social/friends/[username]', { username: friend.username })}
								class="flex items-center gap-3 px-5 py-4 text-slate-900 no-underline transition-colors hover:bg-slate-50 sm:px-6"
							>
								<Avatar username={friend.username} />
								<span class="min-w-0 flex-1">
									<span class="block truncate font-semibold">{friend.username}</span>
									<span class="block text-sm text-slate-500"
										>{friend.sharedCount
											? `${friend.sharedCount} shared portfolio${pluralize(friend.sharedCount)}`
											: 'Nothing shared yet'}</span
									>
								</span>
								<span class="text-sm font-semibold text-indigo-600">View &rarr;</span>
							</a>
						</li>
					{/each}
				</ul>
			{:else}
				<div class="px-6 py-16 text-center">
					<p class="text-lg font-semibold text-slate-900">No friends yet</p>
					<p class="mt-2 text-sm text-slate-500">
						Ask a friend for their username and search for it.
					</p>
				</div>
			{/if}
		</section>

		<div class="space-y-6">
			<!-- Search -->
			<section class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
				<h2 class="text-xl font-semibold tracking-tight text-slate-900">Add a friend</h2>
				<form method="get" class="mt-4 flex gap-2">
					<label for="friend-search" class="sr-only">Username</label>
					<input
						id="friend-search"
						type="search"
						name="q"
						value={data.query}
						placeholder="Exact username"
						autocomplete="off"
						required
						class="min-w-0 flex-1 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 focus:outline-none"
					/>
					<button
						type="submit"
						class="cursor-pointer rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-indigo-700"
						>Search</button
					>
				</form>

				{#if data.query}
					{#if data.match}
						<div class="mt-4 flex items-center gap-3 rounded-lg bg-slate-50 p-3">
							<Avatar username={data.match.username} />
							<span class="min-w-0 flex-1 truncate font-semibold text-slate-900"
								>{data.match.username}</span
							>
							{#if data.matchRelationship === 'self'}
								<span class="text-sm text-slate-500">That's you</span>
							{:else if data.matchRelationship === 'friends'}
								<a
									href={resolve('/social/friends/[username]', { username: data.match.username })}
									class="text-sm font-semibold text-indigo-600 no-underline hover:text-indigo-800"
									>Friends &rarr;</a
								>
							{:else if data.matchRelationship === 'sent'}
								<span
									class="rounded-full bg-amber-100 px-2.5 py-1 text-xs font-semibold text-amber-700"
									>Request sent</span
								>
							{:else if data.matchRelationship === 'received'}
								<span
									class="rounded-full bg-indigo-100 px-2.5 py-1 text-xs font-semibold text-indigo-700"
									>Asked you, see below</span
								>
							{:else}
								<form method="post" action="?/send" class="m-0" use:enhance>
									<input type="hidden" name="username" value={data.match.username} />
									<input type="hidden" name="q" value={data.query} />
									<button type="submit" class={primary}>Add friend</button>
								</form>
							{/if}
						</div>
					{:else}
						<p class="mt-4 rounded-lg bg-slate-50 p-3 text-sm text-slate-500">
							No one goes by <span class="font-semibold text-slate-700">{data.query}</span>.
							Usernames must match exactly.
						</p>
					{/if}
				{/if}
			</section>

			<!-- Requests -->
			{#if data.incoming.length}
				<section class="rounded-xl border border-indigo-200 bg-white p-5 shadow-sm">
					<h2 class="text-xl font-semibold tracking-tight text-slate-900">
						Requests <span
							class="ml-1 rounded-full bg-indigo-600 px-2 py-0.5 align-middle text-xs font-semibold text-white"
							>{data.incoming.length}</span
						>
					</h2>
					<ul class="m-0 mt-4 list-none space-y-3 p-0">
						{#each data.incoming as req (req.id)}
							<li class="flex items-center gap-3">
								<Avatar username={req.from.username} />
								<span class="min-w-0 flex-1">
									<span class="block truncate font-semibold text-slate-900"
										>{req.from.username}</span
									>
									<span class="block text-xs text-slate-500">{timesince(req.createdAt)} ago</span>
								</span>
								<form method="post" action="?/accept" class="m-0" use:enhance>
									<input type="hidden" name="id" value={req.id} />
									<input type="hidden" name="q" value={data.query} />
									<button type="submit" class={primary}>Accept</button>
								</form>
								<form method="post" action="?/decline" class="m-0" use:enhance>
									<input type="hidden" name="id" value={req.id} />
									<input type="hidden" name="q" value={data.query} />
									<button type="submit" class={secondary}>Decline</button>
								</form>
							</li>
						{/each}
					</ul>
				</section>
			{/if}

			{#if data.outgoing.length}
				<section class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
					<h2 class="text-xl font-semibold tracking-tight text-slate-900">Sent</h2>
					<ul class="m-0 mt-4 list-none space-y-3 p-0">
						{#each data.outgoing as req (req.id)}
							<li class="flex items-center gap-3">
								<Avatar username={req.to.username} />
								<span class="min-w-0 flex-1">
									<span class="block truncate font-semibold text-slate-900">{req.to.username}</span>
									<span class="block text-xs text-slate-500">Waiting for a reply</span>
								</span>
								<form method="post" action="?/cancel" class="m-0" use:enhance>
									<input type="hidden" name="id" value={req.id} />
									<input type="hidden" name="q" value={data.query} />
									<button type="submit" class={secondary}>Cancel</button>
								</form>
							</li>
						{/each}
					</ul>
				</section>
			{/if}
		</div>
	</div>
</div>
