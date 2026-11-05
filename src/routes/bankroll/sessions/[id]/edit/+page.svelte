<script lang="ts">
	import SessionForm from '#lib/components/SessionForm.svelte';
	import type { PageProps } from './$types';

	let { data, form }: PageProps = $props();
</script>

<SessionForm isEdit={true} initial={data.initial} failure={form} />
