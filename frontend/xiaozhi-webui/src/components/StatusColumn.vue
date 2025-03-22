<script lang="ts" setup>
const deviceId: string = "d0:39:57:4b:59:8c";
</script>

<template>
  <div class="status-container">
    <!-- <div class="connect-signal disconnected">未连接</div> -->
    <div class="connect-signal disconnected">离线</div>
    <div class="device-id">设备ID：{{ deviceId }}</div>
  </div>
</template>

<style lang="less" scoped>
.status-container {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  height: 4.5rem;
  font-size: 0.85rem;
  background-color: #f9fafb;
  border-bottom: 1px solid #e5e7eb;

  .connect-signal {
    display: flex;
    align-items: center;
    padding: 4px 10px;
    border-radius: 1rem;

    &.disconnected {
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
  }

  .device-id {
    margin-left: 1rem;
  }
}
</style>
