<script lang="ts" setup>
import { useSettingStore } from "../../stores/setting";
import { ElMessage } from "element-plus";

const settingStore = useSettingStore();

const handleQuit = () => {
    settingStore.visible = false;
    const saveOK = settingStore.saveToLocal();
    if (!saveOK) {
        ElMessage.error("配置保存失败，请确认数据不为空");
        return;
    }
    ElMessage.success("配置已保存");
};
</script>

<template>
    <div class="setting-panel" :class="{ visible: settingStore.visible }">
        <div class="setting-content">
            <h2>设置</h2>
            <div style="display: flex; flex-direction: column">
                <label>OTA地址</label>
                <input 
                    v-model="settingStore.otaVersionUrl" 
                    type="text"
                    placeholder="例如: https://api.tenclass.net/xiaozhi/ota/" 
                />
            </div>
            <div style="display: flex; flex-direction: column">
                <label>远程服务器地址</label>
                <input v-model="settingStore.wsUrl" type="text" placeholder="例如: wss://api.domain.cn/xiaozhi/v1/" />
            </div>
            <div style="display: flex; flex-direction: column">
                <label>本地代理地址</label>
                <input v-model="settingStore.wsProxyUrl" type="text" placeholder="例如: ws://localhost:5000" />
            </div>
            <div style="display: flex; flex-direction: column">
                <label>本地服务器地址</label>
                <input v-model="settingStore.backendUrl" type="text" placeholder="例如: http://localhost:8081" />
            </div>
            <div style="display: flex; flex-direction: column">
                <div style="
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                ">
                    <label>Token 设置</label>
                    <label class="toggle-switch">
                        <input type="checkbox" :checked="settingStore.tokenEnable"
                            @click="settingStore.tokenEnable = !settingStore.tokenEnable" />
                        <span class="toggle-slider"></span>
                    </label>
                </div>
                <input v-model="settingStore.token" type="text" placeholder="开启后将在连接时携带 Token"
                    :disabled="!settingStore.tokenEnable" />
            </div>
        </div>
        <div class="bottom-buttons">
            <button id="quit" @click="handleQuit">退出</button>
        </div>
    </div>
</template>

<style lang="less" scoped>

input {
  padding: 0.6rem 0.8rem;
  outline: none;
  border: none;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  transition: all 0.1s ease-in-out;

  &:focus {
    border-color: var(--primary-color);
    box-shadow: var(--primary-neo-color) 0 0 0 2px;
  }
}

.setting-panel {
    position: absolute;
    display: flex;
    padding: 1rem;
    width: 100%;
    height: 100%;
    transition: all 0.1s ease-in-out;
    background-color: #fff;
    transform: translateX(100%);
    overflow: hidden;

    &.visible {
        transform: translateX(0);
    }

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

        input:checked+.toggle-slider {
            background-color: #34c759;
        }

        input:checked+.toggle-slider:before {
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

        #quit {
            width: 45%;
            padding: 0.8rem 0.8rem;
            color: #fff;
            font-size: 1rem;
            border: none;
            border-radius: 0.5rem;
            background-color: #f43f5e;
        }
    }
}
</style>
