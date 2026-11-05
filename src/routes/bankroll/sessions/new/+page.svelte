<script lang="ts">
	import SessionForm from '#lib/components/SessionForm.svelte';
	import type { PageProps } from './$types';

	let { form }: PageProps = $props();
</script>

<SessionForm isEdit={false} initial={{ buyin: '0', buyout: '0' }} failure={form} />
