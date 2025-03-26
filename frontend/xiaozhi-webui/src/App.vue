<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from "vue";

const configStore = useConfigStore();
const deviceId = ref<string>("00:00:00:00:00:00");

// ---------- 输入框相关 start ----------
const chatContainer = ref<HTMLDivElement | null>(null);
const messageInput = ref<HTMLDivElement | null>(null);

/**
 * 初始化输入框的 placeholder
 */
const initInputField = (): void => {
  if (!messageInput) {
    console.error("[initInputField] Message input element not found.");
    return;
  }
  messageInput.value!.innerText = "请输入消息...";
  messageInput.value!.addEventListener(
    "focus",
    function (event: FocusEvent): void {
      messageInput.value!.style.color = "#1C1C1D";
      if (messageInput.value!.innerText === "请输入消息...") {
        messageInput.value!.innerText = "";
      }
    }
  );

  messageInput.value!.addEventListener(
    "blur",
    function (event: FocusEvent): void {
      if (messageInput.value!.innerText === "") {
        messageInput.value!.style.color = "#8C8C8E";
        messageInput.value!.innerText = "请输入消息...";
      }
    }
  );
};

onMounted(() => {
  initInputField();
});

/**
 * 添加消息到聊天框
 * @param {string} type 消息类型，user/server
 * @param {string} text 消息内容
 * @returns
 */
const appendMessage = (type: string, text: string) => {
  if (!chatContainer) {
    console.error("[InputField] Chat container element not found.");
    return;
  }

  const messageContainer: HTMLDivElement = document.createElement("div");
  const messageContent: HTMLDivElement = document.createElement("div");
  const messageTime: HTMLDivElement = document.createElement("div");
  const formattedMessage: string = text.replace(/\n/g, "<br>");
  const now: Date = new Date();

  messageContainer.className = `message ${type}`;
  messageContent.className = "message-content";
  messageTime.className = "message-time";
  messageContent.innerHTML = formattedMessage;
  messageTime.textContent = now.toLocaleTimeString("zh-CN", {
    hour: "2-digit",
    minute: "2-digit",
  });

  messageContainer.appendChild(messageContent);
  messageContainer.appendChild(messageTime);
  chatContainer.value!.appendChild(messageContainer);

  // 将内容底部和视口底部对齐
  chatContainer.value!.scrollTop =
    chatContainer.value!.scrollHeight - chatContainer.value!.clientHeight;

  return messageContainer;
};

/**
 * 客户端发送消息至服务端
 */
function sendMessage() {
  if (!messageInput) {
    console.error("[App][sendMessage] Message input element not found.");
    return;
  }

  const message = messageInput.value!.innerText;

  if (message) {
    // 发送文本消息
    const textMessage = JSON.stringify({
      type: "listen",
      state: "detect",
      text: message,
      source: "text", // 标记这是文本消息
    });
    ws.send(textMessage);
    messageInput.value!.innerText = "";
    // appendMessage("user", message);
  } else if (!configStore.getSessionID()) {
    console.error("[App][sendMessage] No session ID available");
    appendMessage("server", "机器人：抱歉，小智正在忙，请待会再聊吧。");
  }
}

const handleKeyPress = (event: KeyboardEvent) => {
  if (event.key === "Enter") {
    event.preventDefault();
    sendMessage();
  }
};
// ---------- 输入框相关 end ------------

// ---------- WebSocket 连接相关 start ----------
import { useConfigStore } from "./stores/config";
let ws: WebSocket;
const isMounted = ref<boolean>(false);
const connectionState = ref<HTMLDivElement | null>(null);
const connectionStateText = ref<string>("离线");

/**
 * 连接 WebSocket 服务器
 */
const connect = (): void => {
  if (!connectionState.value) {
    try {
      connectionState.value = document.querySelector(".connection-state") as HTMLDivElement;
    } catch (error: unknown) {
      console.error(
        "[App][connect] Error setting connection status to disconnected:",
        error
      );
    }
  }

  const WSProxyURL = configStore.getWSProxyURL();
  console.log("[App][connect] Connecting to:", WSProxyURL);
  ws = new WebSocket(WSProxyURL);

  // WebSocket 保持连接状态时的回调函数
  ws.onopen = function () {
    console.log("[App][ws.onopen] Connected to WebSocket server");

    try {
      connectionState.value!.classList.remove("error");
      connectionState.value!.classList.add("connected");
      connectionState.value!.classList.remove("disconnected");
      connectionStateText.value = "在线";
    } catch (error: unknown) {
      console.error(
        "[App][ws.onopen] Error setting connection status to connected:",
        error
      );
    }

    // 发送 Hello 消息
    const helloMessage = JSON.stringify({
      type: "hello",
      version: 3,
      transport: "websocket",
      audio_params: {
        format: "opus",
        sample_rate: 16000,
        channels: 1,
        frame_duration: 60,
      },
    });
    console.log("[App][ws.onopen] Sending hello message:", helloMessage);
    ws.send(helloMessage);
  };

  // WebSocket 断开连接时的回调函数
  ws.onclose = function (event) {
    console.log(
      `[App][ws.onclose] WebSocket closed: ${event.code} ${event.reason}`
    );
    configStore.setSessionID("");

    try {
      connectionState.value!.classList.remove("error");
      connectionState.value!.classList.add("disconnected");
      connectionState.value!.classList.remove("connected");
      connectionStateText.value = "离线";
    } catch (error: unknown) {
      console.error(
        "[App][ws.onclose] Error setting connection status to disconnected:",
        error
      );
    }
    
    // 3 秒后重连
    setTimeout(connect, 3000);
  };

  // WebSocket 错误时的回调函数
  ws.onerror = function (error) {
    console.error("[App][ws.onerror] WebSocket error:", error);

    try {
      connectionState.value!.classList.remove("disconnected");
      connectionState.value!.classList.remove("connected");
      connectionState.value!.classList.add("error");
      connectionStateText.value = "错误";
    } catch (error: unknown) {
      console.error(
        "[App][ws.onerror] Error setting connection status to error:",
        error
      );
    }
  };

  // WebSocket 接收到消息时的回调函数
  ws.onmessage = async function (event) {
    try {
      // 处理音频消息
      if (event.data instanceof Blob) {
        // console.log("[App][ws.onmessage] Audio data received", event.data);
        if (SPEAKING.value) {
          await enqueueAudio(event.data);
          return;
        } else {
          await enqueueAudio(event.data);
          playNextAudio();
        }
      }
      // 处理文本消息
      else {
        const data = JSON.parse(event.data);
        // console.log("[App][ws.onmessage] Text message received:", data);

        // WebSocket 握手成功，获取 session_id
        if (data.type === "hello") {
          configStore.setSessionID(data.session_id);
          console.log("[App][ws.onmessage] Session ID:", data.session_id);
        }
        // 客户端发送的语音在服务端的识别结果
        else if (data.type === "stt") {
          if (data.text && data.text.trim() && !data.source) {
            appendMessage("user", data.text);
          }
        }
        // 服务端返回的表情信息
        else if (data.type === "llm") {
          if (data.text && data.text.trim()) {
            appendMessage("server", data.text);
          }
        }
        // 服务端返回的文本信息
        else if (data.type === "tts") {
          if (data.state === "sentence_start") {
            appendMessage("server", data.text);
            chatContainer.value!.scrollTop = chatContainer.value!.scrollHeight;
          }
        } else if (data.state === "end" || data.state === "stop") {
          console.log("[App][ws.onmessage] AI speak stopped.");
        }
      }
    } catch (e) {
      console.error("[App][ws.onmessage] Error processing message:", e);
    }
  };
};

onMounted(() => {
  isMounted.value = true;

  // 等待 DOM 渲染完成后再连接
  nextTick(() => {
    connect();
  });
});

onUnmounted(() => {
  isMounted.value = false;
});
// ---------- WebSocket 连接相关 end ------------

// ---------- 设置面板相关 start ------------
const settingPanel = ref<HTMLDivElement | null>(null);
const showSettingPanel = () => {
  if (!settingPanel.value) {
    console.log("[App][connect] settingPanel is null");
    return;
  }
  settingPanel.value!.classList.toggle("settingPanelVisible");
};
// ---------- 设置面板相关 end --------------

// ---------- 语音处理相关 start ------------
declare global {
  interface Window {
    AudioContext: typeof AudioContext;
    webkitAudioContext: typeof AudioContext;
  }
}
const SPEAKING = ref<boolean>(false);
const audioContext = new (window.AudioContext || window.webkitAudioContext)();
const gainNode = audioContext.createGain();
const audioQueue = ref<AudioBuffer[]>([]);
let currentTime = 0;
gainNode.connect(audioContext.destination);
audioContext.suspend();

/**
 * 播放音频队列中的下一个音频
 */
const playNextAudio = (): void => {
  // console.log("[App][playNextAudio] Audio List:", audioQueue.value);
  if (SPEAKING.value) {
    return;
  }
  if (audioQueue.value.length === 0) {
    return;
  }

  const nextAudioBuffer: AudioBuffer | undefined = audioQueue.value.shift();
  if (nextAudioBuffer) {
    SPEAKING.value = true;
    playBlob(nextAudioBuffer);
  }
};

/**
 * 播放音频列表中的 AudioBuffer 语音文件
 * @param {AudioBuffer} audioBuffer 解码后的音频数据
 */
const playBlob = async (audioBuffer: AudioBuffer) => {
  try {
    // 恢复音频上下文（需要用户交互后调用）
    if (audioContext.state === "suspended") {
      await audioContext.resume();
    }

    // 创建播放节点
    const source = audioContext.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(gainNode);

    // 计算精确播放时间
    if (currentTime < audioContext.currentTime) {
      currentTime = audioContext.currentTime;
    }

    // 调度播放
    source.start(currentTime);
    currentTime += audioBuffer.duration;

    // 播放结束处理
    source.onended = () => {
      SPEAKING.value = false;
      playNextAudio();
    };
  } catch (e) {
    console.error("[App][playBlob] 音频解码失败:", e);
  }
};

/**
 * 将 Wave 音频解码后添加到队列中
 * @param {Blob} blob Wave 音频文件
 */
const enqueueAudio = async (blob: Blob): Promise<void> => {
  try {
    const arrayBuffer: ArrayBuffer = await blob.arrayBuffer();
    const audioBuffer: AudioBuffer = await audioContext.decodeAudioData(
      arrayBuffer
    );
    audioQueue.value.push(audioBuffer);
    if (!SPEAKING.value) {
      playNextAudio();
    }
  } catch (e) {
    console.error("[App][enqueueAudio] ", e);
  }
};
// ---------- 语音处理相关 end --------------

// ---------- 设置面板 start ------------
const WSURL = ref<HTMLInputElement | null>(null);
const WSProxyURL = ref<HTMLInputElement | null>(null);
const tokenEnable = ref<boolean>(false);
const token = ref<HTMLInputElement | null>(null);

onMounted(async () => {
  await configStore.init();
  deviceId.value = configStore.getDeviceID();
  WSURL.value!.value = configStore.getWSURL();
  WSProxyURL.value!.value = configStore.getWSProxyURL();
  tokenEnable.value = configStore.getTokenEnable();
  token.value!.value = configStore.getToken();
});
// ---------- 设置面板 end --------------
</script>

<template>
  <div class="app-container">
    <!-- 我来组成头部 -->
    <div class="header-container">
      <span class="title">小智AI</span>
      <button class="setting" @click="showSettingPanel">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-6 w-6"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
          />
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
          />
        </svg>
      </button>
    </div>

    <!-- 状态栏 -->
    <div class="status-container">
      <!-- <div class="connection-status disconnected">未连接</div> -->
      <div
        v-if="isMounted"
        class="connection-status disconnected"
        ref="connectionState"
      >
        {{ connectionStateText }}
      </div>
      <div class="device-id">设备ID：{{ deviceId }}</div>
    </div>

    <!-- 聊天记录 -->
    <div class="chat-container" ref="chatContainer"></div>

    <!-- 输入区域 -->
    <div class="input-field">
      <div
        id="messageInput"
        tabindex="0"
        contenteditable="true"
        type="text"
        ref="messageInput"
        @keydown="handleKeyPress"
        placeholder="请输入消息..."
      ></div>
      <button id="send-message" @click="sendMessage">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path
            fill-rule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 1.414L10.586 9H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z"
            clip-rule="evenodd"
          />
        </svg>
      </button>
      <!-- <button id="phone-call">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path
            d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z"
          />
        </svg>
      </button> -->
    </div>

    <!-- 设置面板 -->
    <div class="setting-panel" ref="settingPanel">
      <div class="setting-content">
        <h2>设置</h2>
        <div style="display: flex; flex-direction: column">
          <label>远程服务器地址</label>
          <input
            type="text"
            placeholder="例如: wss://api.domain.cn/xiaozhi/v1/"
            ref="WSURL"
          />
        </div>
        <div style="display: flex; flex-direction: column">
          <label>本地代理地址</label>
          <input
            type="text"
            placeholder="例如: ws://localhost:5000"
            ref="WSProxyURL"
          />
        </div>
        <div style="display: flex; flex-direction: column">
          <div
            style="
              display: flex;
              justify-content: space-between;
              align-items: center;
            "
          >
            <label>Token 设置</label>
            <label class="toggle-switch">
              <input
                type="checkbox"
                :checked="tokenEnable"
                @click="tokenEnable = !tokenEnable"
              />
              <span class="toggle-slider"></span>
            </label>
          </div>
          <input
            type="text"
            placeholder="开启后将在连接时携带 Token"
            ref="token"
            :disabled="!tokenEnable"
          />
        </div>
      </div>
      <div class="bottom-buttons">
        <button id="save-config">保存配置</button>
        <button id="quit" @click="showSettingPanel">退出</button>
      </div>
    </div>
  </div>
</template>

<style>
.app-container {
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;

  /* 头部容器 */
  .header-container {
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

    .setting {
      display: flex;
      align-items: center;
      padding: 0.5rem;
      right: 1rem;
      height: 2.5rem;
      width: 2.5rem;
      color: white;
      border: none;
      border-radius: 0.5rem;
      background-color: #726bea;
    }
  }

  /* 聊天记录容器 */
  .chat-container {
    flex: 1;
    margin: 0.5rem;
    padding: 0.5rem;
    background-color: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    overflow-y: auto;
    scrollbar-width: none;

    .message.server,
    .message.user {
      .message-content {
        width: max-content;
        padding: 0.5rem 1rem;
        white-space: pre-line;
        text-overflow: ellipsis;
        cursor: text;
        overflow-wrap: break-word;
        word-break: break-word;
        max-width: 89%;
      }
      .message-time {
        color: #9ca3af;
        font-size: 0.75rem;
        margin-top: 0.25rem;
      }
    }

    .message.server {
      margin: 0.5rem 0;
      .message-content {
        background-color: #fff;
        border: 1px solid #e5e7eb;
        box-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
        border-radius: 1rem 1rem 1rem 5px;
        color: #232b36;
      }
    }

    .message.user {
      margin: 0.5rem 0;
      .message-content {
        background-color: var(--primary-color);
        border-radius: 1rem 1rem 5px 1rem;
        color: white;
        margin-left: auto;
      }
      .message-time {
        text-align: right;
      }
    }
  }

  /* 状态容器 */
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

  /* 输入区域 */
  .input-field {
    display: flex;
    padding: 0.75rem;
    min-width: 350px;
    background-color: #fff;
    border-top: 1px solid #e5e7eb;
    gap: 0.4rem;
    align-items: flex-end;

    #messageInput {
      flex: 1;
      padding: 0.6rem 0.8rem;
      width: 100%;
      height: 100%;
      color: #8c8c8e;
      background-color: #fff;
      outline: none;
      border: 1px solid #e5e7eb;
      border-radius: 0.5rem;
      transition: all 0.1s ease-in-out;
      max-height: 5.5rem;
      overflow-y: auto;
      scrollbar-width: none;

      white-space: pre-wrap; /* 换行 */
      text-overflow: ellipsis; /* 当内容溢出时显示省略号 */
      cursor: text;

      &:focus {
        border-color: var(--primary-color);
        box-shadow: var(--primary-neo-color) 0 0 0 2px;
      }
    }

    #send-message,
    #phone-call {
      padding: 0.7rem;
      width: 3rem;
      height: 3rem;
      color: white;
      border: none;
      border-radius: 0.8rem;
    }

    #send-message {
      background-color: var(--primary-color);
    }

    #phone-call {
      background-color: #10b981;
    }
  }

  /* 设置面板 */
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

    &.settingPanelVisible {
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
        background-color: var(--primary-color);
      }

      #quit {
        background-color: #f43f5e;
      }
    }
  }
}
</style>
