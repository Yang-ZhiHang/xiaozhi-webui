<script lang="ts" setup>
import SettingButton from '../Setting/SettingButton.vue'

</script>

<template>
    <div class="title-container">
        <span class="title">小智</span>
        <SettingButton />
    </div>
</template>

<style scoped>
.title-container {
    display: flex;
    position: relative;
    padding: 1rem;
    background-color: var(--primary-color);
    height: 4.5rem;

    .title {
        display: flex;
        align-items: center;
        flex: 1;
        font-size: 1.25rem;
        font-weight: bold;
        color: white;
        height: 100%;
    }
}
</style>