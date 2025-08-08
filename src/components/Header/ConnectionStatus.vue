<script lang="ts" setup>
import { computed } from 'vue';
import { useSettingStore } from '@/stores/setting';

const settingStore = useSettingStore();
const connectionStatusClass = computed(() => props.connectionStatus);
const connectionStatusText = computed(() => {
    const texts = {
        connected: '在线',
        disconnected: '离线',
        error: '错误'
    }
    return texts[props.connectionStatus];
});

const props = defineProps<{
    connectionStatus: 'connected' | 'disconnected' | 'error'
}>()
</script>

<template>
    <div class="status-container">
        <div :class="['connection-status', connectionStatusClass]" ref="connectionState">
            {{ connectionStatusText }}
        </div>
        <div class="device-id">设备ID：{{ settingStore.deviceId }}</div>
    </div>
</template>

<style scoped lang="less">
.status-container {
    display: flex;
    align-items: center;
    padding: 0.75rem;
    height: 3.5rem;
    font-size: 0.85rem;
    background-color: #f9fafb;
    border-bottom: 1px solid #e5e7eb;

    .connection-status {
        display: flex;
        align-items: center;
        padding: 4px 10px;
        border-radius: 1rem;

        &.connected {
            color: green;
            background-color: rgba(0, 255, 0, 0.1);

            &::before {
                content: "";
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background-color: green;
                margin-right: 5px;
            }
        }

        &.disconnected {
            color: grey;
            background-color: rgba(0, 0, 0, 0.1);

            &::before {
                content: "";
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background-color: grey;
                margin-right: 5px;
            }
        }

        &.error {
            color: red;
            background-color: rgba(255, 0, 0, 0.1);

            &::before {
                content: "";
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background-color: red;
                margin-right: 5px;
            }
        }
    }

    .device-id {
        margin-left: 1rem;
    }
}
</style>
