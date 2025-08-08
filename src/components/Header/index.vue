<script setup lang="ts">
import ConnectionStatus from './ConnectionStatus.vue'
import Title from './Title.vue'

const props = defineProps<{
    connectionStatus: 'connected' | 'disconnected' | 'error'
}>()
</script>

<template>
    <Title />
    <ConnectionStatus :connection-status="props.connectionStatus"/>
</template>