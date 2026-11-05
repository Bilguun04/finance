<script lang="ts">
	let { username, large = false }: { username: string; large?: boolean } = $props();
</script>

<span
	class={[
		'flex shrink-0 items-center justify-center rounded-full bg-indigo-100 font-semibold text-indigo-700 uppercase',
		large ? 'size-14 text-xl' : 'size-10 text-sm'
	]}
	aria-hidden="true">{username.charAt(0)}</span
>
