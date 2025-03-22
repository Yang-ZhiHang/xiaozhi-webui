<script setup>
import { defineEmits } from "vue";

const emits = defineEmits(["quit-setting-panel"]);

function quitSettingPanel() {
  emits("quit-setting-panel");
}
</script>

<template>
  <div class="setting-panel">
    <div class="setting-content">
      <h2>设置</h2>
      <div style="display: flex; flex-direction: column">
        <label>远程服务器地址</label>
        <input type="text" />
      </div>
      <div style="display: flex; flex-direction: column">
        <label>本地代理地址</label>
        <input type="text" />
      </div>
      <div style="display: flex; flex-direction: column">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <label>Token 设置</label>
          <label class="toggle-switch">
            <input type="checkbox" />
            <span class="toggle-slider"></span>
          </label>
        </div>
        <input type="text" />
      </div>
    </div>
    <div class="bottom-buttons">
      <button id="save-config">保存配置</button>
      <button id="quit" @click="quitSettingPanel">退出</button>
    </div>
  </div>
</template>

<style lang="less" scoped>
.setting-panel {
  position: absolute;
  display: flex;
  padding: 1rem;
  width: 100%;
  height: 100%;
  transition: all 0.2s ease-in-out;
  background-color: #fff;
  transform: translateX(100%);
  overflow: hidden;

  .setting-content {
    flex: 1;
    padding: 1rem;

    h2 {
      margin-bottom: 1rem;
      font-size: 1.5rem;
      font-weight: bold;
    }

    label {
      margin-bottom: 0.5rem;
      font-size: 0.9rem;
    }

    input {
      margin-bottom: 1rem;
      line-height: 1.5rem;
    }

    .toggle-switch {
      position: relative;
      display: inline-block;
      width: 50px;
      height: 30px;
    }

    .toggle-switch input {
      opacity: 0;
      width: 0;
      height: 0;
    }

    .toggle-slider {
      position: absolute;
      cursor: pointer;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-color: #e9e9ea;
      transition: 0.4s;
      border-radius: 31px;
    }

    .toggle-slider:before {
      position: absolute;
      content: "";
      height: 27px;
      width: 27px;
      left: 2px;
      bottom: 2px;
      background-color: white;
      transition: 0.25s;
      border-radius: 50%;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }

    input:checked + .toggle-slider {
      background-color: #34c759;
    }

    input:checked + .toggle-slider:before {
      transform: translateX(20px);
    }
  }

  .bottom-buttons {
    display: flex;
    justify-content: space-evenly;
    align-items: center;
    width: 100%;
    padding: 1rem 0;
    position: absolute;
    bottom: 0;
    left: 0;
    border-top: 1px solid #e5e7eb;

    #save-config,
    #quit {
      width: 45%;
      padding: 0.8rem 0.8rem;
      color: #fff;
      font-size: 1rem;
      border: none;
      border-radius: 0.5rem;
    }

    #save-config {
      background-color: #4f46e5;
    }

    #quit {
      background-color: #f43f5e;
    }
  }
}
</style>
