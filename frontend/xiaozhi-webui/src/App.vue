<script setup lang="ts">
import { ref } from "vue";

import Header from "./components/Header.vue";
import ChatBox from "./components/ChatBox.vue";
import InputField from "./components/InputField.vue";
import StatusColumn from "./components/StatusColumn.vue";
import SettingPanel from "./components/SettingPanel.vue";

const isSettingVisible = ref<boolean>(false);

</script>

<template>
  <div class="chat-container">
    <Header @show-setting-panel="isSettingVisible = true"></Header>
    <StatusColumn></StatusColumn>
    <ChatBox></ChatBox>
    <InputField></InputField>
    <SettingPanel :class="{ 'slide-out': isSettingVisible }" @quit-setting-panel="isSettingVisible = false"></SettingPanel>
  </div>
</template>

<style scoped>
.chat-container {
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;

  ChatBox {
    flex: 1;
  }

  .slide-out {
    transform: translateX(0);
  }
}
</style>
