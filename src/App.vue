<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import { useSettingStore } from "./stores/setting";
import {
  type HelloResponse,
  type UserEcho,
  type AIResponse_Emotion,
  type AIResponse_Text,
  type WebSocketMessage,
  AbortMessage,
  UserMessage,
} from "./types/message";
import { ElMessage, ElMessageBox } from "element-plus";
import { error, log, warn } from "./common/log";
import Header from "./components/Header/index.vue";
import SettingPanel from "./components/Setting/index.vue";
import VoiceCall from "./components/VoiceCall.vue";
import InputField from "./components/InputField.vue";
import ChatContainer from "./components/ChatContainer.vue";
import { wsMatcher } from "./common/regex";

const settingStore = useSettingStore();

// ---------- 语音对话配置 start --------------
import { ChatStateManager } from "./services/ChatStateManager";
import { ChatEvent, ChatState, Role } from "./types/chat";
import { VoiceAnimationManager } from "./services/VoiceAnimationManager";
import { AudioService } from "./services/AudioManager";

const voiceAnimationManager = new VoiceAnimationManager();
const chatStateManager = new ChatStateManager({
  thresholds: {
    USER_SPEAKING: 0.04,
    USER_INTERRUPT_AI: 0.1,
  },
  timeout: {
    SILENCE: 1000,
  },
  callbacks: {
    sendAudioData(data: Float32Array) {
      wsService.sendAudioMessage(data);
    },
    sendTextData(text: string) {
      wsService.sendTextMessage(text);
    },
    getSessionId() {
      return settingStore.sessionId;
    },
  },
  voiceAnimationManager: voiceAnimationManager,
});
const audioService = AudioService.getInstance();
audioService.onQueueEmpty(() => {
  chatStateManager.setState(ChatState.IDLE);
});
audioService.onProcess((audioLevel: number, audioData: Float32Array) => {
  chatStateManager.handleUserAudioLevel(audioLevel, audioData);
});
chatStateManager.on(ChatEvent.USER_START_SPEAKING, async () => {
  audioService.stopPlaying();
  audioService.clearAudioQueue();
});
chatStateManager.on(ChatEvent.AI_START_SPEAKING, () => {
  audioService.playAudio();
});
// ---------- 语音对话配置 end ----------------

// ---------- WebSocket 配置 start ----------
import { WebSocketService } from "./services/WebSocketManager";
const chatContainerRef = ref<InstanceType<typeof ChatContainer> | null>(null);
const wsService = new WebSocketService(
  {
    decodeAudioData: (arrayBuffer: ArrayBuffer) =>
      audioService.decodeAudioData(arrayBuffer),
    settingStore: settingStore,
  },
  {
    async onAudioMessage(audioBuffer: AudioBuffer) {
      log("Audio data received.");
      switch (chatStateManager.currentState.value as ChatState) {
        case ChatState.USER_SPEAKING:
          warn("User is speaking, discarding audio data.");
          audioService.enqueueAudio(audioBuffer);
          break;
        case ChatState.IDLE:
          log("Audio is not playing, set ai speaking...");
          audioService.enqueueAudio(audioBuffer);
          chatStateManager.setState(ChatState.AI_SPEAKING);
          break;
        case ChatState.AI_SPEAKING:
          log("AI is speaking, enqueuing audio data.");
          audioService.enqueueAudio(audioBuffer);
          break;
        default:
          error("Unknown state:", chatStateManager.currentState.value);
      }
    },
    async onTextMessage(message: WebSocketMessage) {
      log("Text message received:", message);

      switch (message.type) {
        case "hello":
          const helloMessage = message as HelloResponse;
          settingStore.sessionId = helloMessage.session_id!;
          log("Session ID:", helloMessage.session_id);
          break;

        case "stt":
          const sttMessage = message as UserEcho;
          if (sttMessage.text?.trim()) {
            chatContainerRef.value?.appendMessage(Role.USER, sttMessage.text);
          }
          break;

        case "llm":
          const emotionMessage = message as AIResponse_Emotion;
          if (emotionMessage.text?.trim()) {
            chatContainerRef.value?.appendMessage(Role.AI, emotionMessage.text);
          }
          break;

        case "tts":
          switch (message.state) {
            case "sentence_start":
              const textMessage = message as AIResponse_Text;
              const blackList = ["%"];
              if (blackList.some(item => textMessage.text.trim().startsWith(item))) {
                log("Received control message:", textMessage.text);
                break;
              }
              chatContainerRef.value?.appendMessage(Role.AI, textMessage.text!);
              break;
            case "start":
            case "sentence_end":
              break;
          }
          break;
      }
    },
    onConnect() {
      ElMessage.success("连接成功");
    },
    onDisconnect() {
      ElMessage.error("连接已断开，正在尝试重连");
      setTimeout(() => {
        wsService.connect(settingStore.wsProxyUrl);
      }, 3000);
    },
  }
);
// ---------- WebSocket 配置 end ------------

const sendAbortMessage = () => {
  const abortMessage = AbortMessage(settingStore.sessionId);
  wsService.sendTextMessage(abortMessage);
};

const sendMessage = (text: string) => {
  const textMessage = UserMessage(text);
  if (chatStateManager.currentState.value == ChatState.AI_SPEAKING) {
    sendAbortMessage();
    audioService.clearAudioQueue();
  }
  wsService.sendTextMessage(textMessage);
};

const isVoiceCallVisible = ref<boolean>(false);

const showVoiceCallPanel = async () => {
  sendAbortMessage();
  audioService.clearAudioQueue();
  isVoiceCallVisible.value = true;
  await audioService.prepareMediaResources();
  if (chatStateManager.currentState.value != ChatState.IDLE) {
    chatStateManager.setState(ChatState.IDLE);
  }
};

const closeVoiceCallPanel = async () => {
  isVoiceCallVisible.value = false;
  sendAbortMessage();
  audioService.stopMediaResources();
};

const ensureProxyUrl = async () => {
  if (!settingStore.wsProxyUrl) {
    const { value: wsProxyUrl } = await ElMessageBox.prompt(
      "请输入代理服务器地址：",
      "提示",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        inputValue: "ws://localhost:5000",
        inputPattern: wsMatcher,
        inputErrorMessage: "请输入有效的服务器地址(ws:// 或 wss:// 开头)",
      }
    );
    settingStore.wsProxyUrl = wsProxyUrl;
    ElMessage.success("代理服务器地址已保存");
  }
};

onMounted(async () => {
  const loaded = settingStore.loadFromLocal();
  if (loaded) {
    ElMessage.success("本地配置加载成功");
    wsService.connect(settingStore.wsProxyUrl);
    return;
  }

  await ensureProxyUrl();

  settingStore.saveToLocal();
  ElMessage.warning("未发现本地配置，默认配置已加载并缓存至本地");
  wsService.connect(settingStore.wsProxyUrl);
});

onUnmounted(() => {
  log("Clearing resources...");
  chatStateManager.destroy();
  audioService.clearMediaResources();
});
</script>

<template>
  <div class="app-container">
    <Header :connection-status="wsService.connectionStatus.value" />
    <ChatContainer class="chat-container" ref="chatContainerRef" />
    <InputField
      @send-message="(text: string) => sendMessage(text)"
      @phone-call-button-clicked="showVoiceCallPanel"
    />
    <SettingPanel />
    <VoiceCall
      :voice-animation-manager="voiceAnimationManager"
      :chat-state-manager="chatStateManager"
      :is-visible="isVoiceCallVisible"
      @on-shut-down="closeVoiceCallPanel"
    />
  </div>
</template>

<style>
.app-container {
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}
</style>
