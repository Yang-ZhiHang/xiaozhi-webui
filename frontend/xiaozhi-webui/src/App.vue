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

    if (isPlaying) {
      abortPlayingAndClean();
    }

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
      connectionState.value = document.querySelector(
        ".connection-state"
      ) as HTMLDivElement;
    } catch (error: unknown) {
      console.error(
        "[App][connect] Error setting connection status to disconnected:",
        error
      );
    }
  }

  const WSProxyURL = configStore.getWSProxyURL();
  // console.log("[App][connect] Connecting to:", WSProxyURL);
  ws = new WebSocket(WSProxyURL);

  // WebSocket 保持连接状态时的回调函数
  ws.onopen = function () {
    console.log("[App][ws.onopen] Connected to WebSocket server:", WSProxyURL);

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
        console.log("[App][ws.onmessage] Audio data received", event.data);
        if (isPlaying) {
          console.log("[App][ws.onmessage] Audio is playing, enqueuing...");
          await enqueueAudio(event.data);
          return;
        } else {
          console.log(
            "[App][ws.onmessage] Audio is not playing, playing now..."
          );
          await enqueueAudio(event.data);
          playNextAudio();
        }
      }
      // 处理文本消息
      else {
        const data = JSON.parse(event.data);
        console.log("[App][ws.onmessage] Text message received:", data);

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
          if (data.state === "stop") {
            console.log("[App][ws.onmessage] AI speak done.");
            await startRecording();
          } else if (data.state === "sentence_start") {
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
// ---------- WebSocket 连接相关 end ------------

// ---------- 设置面板相关 start ------------
const WSURL = ref<HTMLInputElement | null>(null);
const WSProxyURL = ref<HTMLInputElement | null>(null);
const tokenEnable = ref<boolean>(false);
const token = ref<HTMLInputElement | null>(null);
const settingPanel = ref<HTMLDivElement | null>(null);

const handleSaveConfig = () => {
  const ws_url = WSURL.value!.value;
  const ws_proxy_url = WSProxyURL.value!.value;
  const token_enable = tokenEnable.value;
  const token_value = token.value!.value;
  const data = {
    WS_URL: ws_url,
    WS_PROXY_URL: ws_proxy_url,
    TOKEN_ENABLE: token_enable,
    TOKEN: token_value,
  };
  configStore.saveConfig(data);
  settingPanel.value!.classList.remove("settingPanelVisible");
};

const showSettingPanel = async () => {
  if (!settingPanel.value) {
    console.log("[App][connect] settingPanel is null");
    return;
  }
  await configStore.init();
  deviceId.value = configStore.getDeviceID();
  WSURL.value!.value = configStore.getWSURL();
  WSProxyURL.value!.value = configStore.getWSProxyURL();
  tokenEnable.value = configStore.getTokenEnable();
  token.value!.value = configStore.getToken();
  settingPanel.value!.classList.toggle("settingPanelVisible");
};

const closeSettingPanel = () => {
  if (!settingPanel.value) {
    console.log("[App][connect] settingPanel is null");
    return;
  }
  settingPanel.value!.classList.remove("settingPanelVisible");
};

// ---------- 设置面板相关 end --------------

// ---------- 语音处理相关 start ------------
declare global {
  interface Window {
    AudioContext: typeof AudioContext;
    webkitAudioContext: typeof AudioContext;
  }
}

const audioContext = new (window.AudioContext || window.webkitAudioContext)({
  sampleRate: 16000,
});
const audioQueue = ref<AudioBuffer[]>([]);

let isPlaying: boolean = false;
let currentTime = 0;
let animationCheckInterval: number | null = null;
let analyser: AnalyserNode;
let gainNode: GainNode;

/**
 * 初始化音频分析器
 */ /**
 * 播放音频队列中的下一个音频
 */
const playNextAudio = (): void => {
  console.log("[App][playNextAudio] Audio List:", audioQueue.value);
  if (isPlaying) {
    return;
  }
  if (audioQueue.value.length === 0) {
    updateAIWaveAnimation(0);
    return;
  }

  const nextAudioBuffer: AudioBuffer | undefined = audioQueue.value.shift();
  if (nextAudioBuffer) {
    playBlob(nextAudioBuffer);
  }
};

/**
 * 停止播放音频，并清空队列，将播放状态设置为 false
 */
const abortPlayingAndClean = (): void => {
  audioContext.suspend();
  isPlaying = false;
  audioQueue.value = [];

  // 通知小智，你被打断了
  const abort_message = {
    type: "abort",
    session_id: configStore.getSessionID(),
  };
  ws.send(JSON.stringify(abort_message));
};

/**
 * 播放音频列表中的 AudioBuffer 语音文件
 * @param {AudioBuffer} audioBuffer 解码后的音频数据
 */
const playBlob = async (audioBuffer: AudioBuffer) => {
  try {
    // 恢复 audioContext 为活跃状态
    if (audioContext.state === "suspended") {
      await audioContext.resume();
    }
    // 创建播放节点
    const source = audioContext.createBufferSource();
    source.buffer = audioBuffer;

    // 创建音频分析器
    if (isPhoneCallPanelVisible.value && !analyser) {
      analyser = audioContext.createAnalyser();
      analyser.fftSize = 256; // 设置 FFT 大小
    }
    // 创建增益节点
    if (isPhoneCallPanelVisible.value && !gainNode) {
      gainNode = audioContext.createGain();
    }

    if (isPhoneCallPanelVisible.value) {
      source.connect(analyser);
      analyser.connect(gainNode);
      gainNode.connect(audioContext.destination);
      const bufferLength = analyser.frequencyBinCount;
      const dataArray = new Float32Array(bufferLength);
      if (animationCheckInterval) {
        clearInterval(animationCheckInterval);
        animationCheckInterval = null;
      }
      // 设置音频分析定时器（节流）
      animationCheckInterval = setInterval(() => {
        if (isPlaying && isPhoneCallPanelVisible.value) {
          analyser.getFloatTimeDomainData(dataArray);
          const audioLevel = detectAudioLevel(dataArray);
          console.log(
            "[App][animationCheckInterval] Audio Level:",
            audioLevel.toFixed(2)
          );
          updateAIWaveAnimation(audioLevel);
        }
      }, 100);

      // 确保音频片段之间无间隙
      const currentTime = audioContext.currentTime;
      const startTime = Math.max(currentTime, nextPlayTime);

      // 添加淡入淡出效果
      const fadeDuration = 0.005;
      gainNode.gain.setValueAtTime(0, startTime);
      gainNode.gain.linearRampToValueAtTime(1, startTime + fadeDuration);
      gainNode.gain.setValueAtTime(
        1,
        startTime + audioBuffer.duration - fadeDuration
      );
      gainNode.gain.linearRampToValueAtTime(
        0,
        startTime + audioBuffer.duration
      );

      isPlaying = true;
      console.log("[App][playBlob] set isPlaying = true.");

      source.start(startTime);
      nextPlayTime = startTime + audioBuffer.duration;

      source.onended = () => {
        isPlaying = false;
        source.disconnect();
        gainNode.disconnect();
        analyser.disconnect();
        console.log("[App][playBlob] set isPlaying = false");
        playNextAudio();
      };
    } else {
      source.connect(audioContext.destination);

      // 计算精确播放时间
      if (currentTime < audioContext.currentTime) {
        currentTime = audioContext.currentTime;
      }

      isPlaying = true;
      console.log("[App][playBlob] set isPlaying = true.");

      // 调度播放
      source.start(currentTime);
      currentTime += audioBuffer.duration;

      // 播放结束处理
      source.onended = () => {
        isPlaying = false;
        source.disconnect();
        console.log("[App][playBlob] set isPlaying = false");
        playNextAudio();
      };
    }
  } catch (e) {
    console.error("[App][playBlob] Audio play fail:", e);
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
    if (!isPlaying) {
      playNextAudio();
    }
  } catch (e) {
    console.error("[App][enqueueAudio] ", e);
  }
};
// ---------- 语音处理相关 end --------------

// ---------- 设置面板 start ------------
// ---------- 设置面板 end --------------

// ---------- 语音通话 start --------------

const isPhoneCallPanelVisible = ref<boolean>(false);
let audioStream: MediaStream | null = null;
let processorNode: AudioWorkletNode | null = null;
let isRecording: boolean = false;
let haveFirstSpoke: boolean = false;
let lastAudioTime = 0;
let nextPlayTime = 0;
const SILENCE_TIMEOUT = 2000; // 5秒无音频输入则认为是静音

// 显示电话呼叫面板
const showPhoneCallPanel = async () => {
  // 如果小智正在讲话，就暂停讲话
  if (isPlaying) {
    abortPlayingAndClean();
  }
  isPhoneCallPanelVisible.value = true;

  // TODO: 开启用户声音监听
  // 如果用户声音大于一定阈值，开始录音
  // 开始录音后，如果用户声音小于一定阈值一段时间，停止录音

  // 清除还未播放的音频
  audioQueue.value = [];
  isPlaying = false;
  nextPlayTime = 0;

  // 保持 audioContext 为活跃状态
  if (audioContext.state === "suspended") {
    await audioContext.resume();
  }

  // 加载音频处理脚本
  await audioContext.audioWorklet.addModule(
    "/src/utils/audio/audioProcessor.ts"
  );
  // console.log("[App][startRecording] New audioContext created:", audioContext);

  // 初始化音频流
  try {
    audioStream = await navigator.mediaDevices.getUserMedia({
      audio: {
        sampleRate: 16000,
        channelCount: 1,
        echoCancellation: true,
        noiseSuppression: true,
      },
    });
    // console.log("[App][startRecording] UserMedia created:", audioStream);
  } catch (err: unknown) {
    console.log("[App][startRecording] Error getting user media:", err);
  }

  // 利用 MediaStream 创建音频源节点
  const source = audioContext.createMediaStreamSource(audioStream!);

  if (!processorNode) {
    // 使用自定义的 audioContext 节点，用于后续处理音频数据
    // https://developer.mozilla.org/zh-CN/docs/Web/API/AudioWorkletNode
    processorNode = new AudioWorkletNode(audioContext, "audioProcessor", {
      processorOptions: {
        bufferSize: 960, // 16KHz 的采样频率下，60ms 包含的采样点个数
      },
    });
    // console.log("[App][startRecording] AudioWorkletNode created:", processorNode);

    // 建立音频节点连接
    source.connect(processorNode);

    // Web Audio API 需要形成完整的音频处理图才会工作
    // 所以需要将 processorNode 连接到 audioContext 的输出节点
    processorNode.connect(audioContext.destination);

    // 添加错误监听
    processorNode.onprocessorerror = (e) => {
      console.error("Processor error:", e);
    };

    // （主线程）处理节点的出口回调函数，用于接收 process 函数处理后的音频数据
    processorNode.port.onmessage = (e: MessageEvent) => {
      if (isRecording && ws && ws.readyState === WebSocket.OPEN) {
        // TODO: 检测音量
        // 开始说话就设置静音定时器，防抖
        let audioLevel = 0;
        if (e.data instanceof Float32Array) {
          audioLevel = detectAudioLevel(e.data);
        } else if (e.data.buffer) {
          const audioData = new Float32Array(e.data.buffer);
          audioLevel = detectAudioLevel(audioData);
          ws.send(e.data.buffer);
        }
        if (audioLevel > 0.01 && !haveFirstSpoke) {
          haveFirstSpoke = true;
        }
        if (haveFirstSpoke) {
          if (audioLevel > 0.01 && e.data instanceof Float32Array) {
            lastAudioTime = Date.now();
            updateUserWaveAnimation(audioLevel);
            ws.send(e.data);
          } else if (audioLevel > 0.01 && e.data.buffer) {
            lastAudioTime = Date.now();
            updateUserWaveAnimation(audioLevel);
            ws.send(e.data.buffer);
          } else if (
            audioLevel < 0.01 &&
            Date.now() - lastAudioTime > SILENCE_TIMEOUT
          ) {
            stopRecording();
          }
        }
      }
    };
  } else {
    source.connect(processorNode);
    processorNode.connect(audioContext.destination);
  }

  await startRecording();
};

// 关闭电话呼叫面板
const closePhoneCallPanel = async () => {
  isPhoneCallPanelVisible.value = false;

  // TODO: 关闭用户声音监听
  // 清理录音相关资源
  if (animationCheckInterval) {
    clearInterval(animationCheckInterval);
    animationCheckInterval = null;
  }
  await stopRecording();
};

// 开始录音并发送音频数据
function startRecording() {
  haveFirstSpoke = false;
  isRecording = true;
  lastAudioTime = Date.now();

  // 发送开始录音信号
  if (ws && ws.readyState === WebSocket.OPEN) {
    const startMessage = JSON.stringify({
      type: "listen",
      state: "start",
      mode: "auto",
    });
    ws.send(startMessage);
    console.log("[App][startRecording] Sending start message:", startMessage);
  }

  if (audioStream) {
    audioStream.getTracks().forEach((track) => (track.enabled = true));
  }
}

// 停止录音
function stopRecording() {
  isRecording = false;
  // 发送停止信号
  if (ws && ws.readyState === WebSocket.OPEN) {
    const stopMessage = JSON.stringify({
      type: "listen",
      state: "stop",
      mode: "auto",
    });
    ws.send(stopMessage);
    console.log("[App][stopRecording] Stop message send:", stopMessage);
  }

  // 停止资源
  if (audioStream) {
    audioStream.getTracks().forEach((track) => (track.enabled = false));
  }
  if (processorNode) {
    processorNode.disconnect();
    ws.send(JSON.stringify({ type: "reset" }));
  }

  // 等待当前音频播放完成
  if (audioContext) {
    const currentTime = audioContext.currentTime;
    if (nextPlayTime > currentTime) {
      setTimeout(() => {
        audioQueue.value = [];
        isPlaying = false;
        nextPlayTime = 0;
      }, (nextPlayTime - currentTime) * 1000);
    } else {
      audioQueue.value = [];
      isPlaying = false;
      nextPlayTime = 0;
    }
  }

  showUserWaveAnimation(false);
  updateUserWaveAnimation(0);
  updateAIWaveAnimation(0);
}

/**
 * 音频电平检测
 * @param {Float32Array} audioData 音频数据
 * @returns {number} 音频电平值
 */
function detectAudioLevel(audioData: Float32Array): number {
  if (!audioData || !audioData.length) return 0;
  let sum = 0;
  for (let i = 0; i < audioData.length; i++) {
    sum += Math.abs(audioData[i]);
  }
  return sum / audioData.length;
}

onUnmounted(async () => {
  console.log("[App][onUnmounted] Clearing resources...");
  if (processorNode) {
    processorNode.port.onmessage = null;
    processorNode.disconnect();
    processorNode = null;
  }
  if (audioStream) {
    audioStream.getTracks().forEach((track) => track.stop());
    audioStream = null;
  }
  if (audioContext) {
    audioQueue.value = [];
    isRecording = false;
    isPlaying = false;
    await audioContext.close();
  }
  isMounted.value = false;
});
// ---------- 语音通话 end ----------------

// ---------- 对话的动态效果 start ----------

// 用户讲话时的波形动画
const voiceWave = ref<HTMLDivElement | null>(null);
function showUserWaveAnimation(show: boolean) {
  if (!voiceWave.value) {
    console.log("[App][showUserWaveAnimation] voiceWave is null, updating...");
    voiceWave.value = document.querySelector(".voice-wave");
    return;
  }
  if (show) {
    voiceWave.value.classList.add("active");
  } else {
    voiceWave.value.classList.remove("active");
  }
}

// 更新用户说话时的波形显示
function updateUserWaveAnimation(audioLevel: number) {
  const maxHeight = 24; // 最大高度
  const minHeight = 6; // 最小高度

  if (audioLevel > 0.01) {
    const height = Math.min(maxHeight, minHeight + audioLevel * 100);
    document.documentElement.style.setProperty("--wave-height", `${height}px`);
    showUserWaveAnimation(true);
  } else {
    showUserWaveAnimation(false);
  }
}

// 小智说话时的涟漪动画和头像动画
const voiceAvatar = ref<HTMLDivElement | null>(null);
function updateAIWaveAnimation(audioLevel: number) {
  const maxScale = 1.05;

  if (!voiceAvatar.value) {
    console.log("[App][updateAIWaveAnimation] avatar is null, updating...");
    voiceAvatar.value = document.querySelector(".voice-avatar");
    return;
  }

  if (audioLevel > 0.01) {
    // 根据音频电平计算缩放值
    const scale = 1 + Math.min(maxScale - 1, audioLevel * 2); // 最大缩放到1.05
    voiceAvatar.value.style.transform = `scale(${scale})`;
    voiceAvatar.value.classList.add("speaking");
  } else {
    voiceAvatar.value.style.transform = "scale(1)";
    if (audioLevel === 0) {
      voiceAvatar.value.classList.remove("speaking");
    }
  }
}
// ---------- 对话的动态效果 end ------------


onMounted(() => {
  initInputField();
  isMounted.value = true;
});

onMounted(async () => {
  await configStore.init();
  deviceId.value = configStore.getDeviceID();
  WSURL.value!.value = configStore.getWSURL();
  WSProxyURL.value!.value = configStore.getWSProxyURL();
  tokenEnable.value = configStore.getTokenEnable();
  token.value!.value = configStore.getToken();

  await nextTick(() => {
    connect();
  });
});
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
      <button id="phone-call" @click="showPhoneCallPanel">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path
            d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z"
          />
        </svg>
      </button>
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
        <button id="save-config" @click="handleSaveConfig">保存配置</button>
        <button id="quit" @click="closeSettingPanel">退出</button>
      </div>
    </div>

    <!-- 语音通话界面 -->
    <div
      class="phone-call-container"
      :class="{ active: isPhoneCallPanelVisible }"
    >
      <div class="voice-avatar-container">
        <div class="voice-avatar" ref="voiceAvatar">
          <div class="ripple-1"></div>
          <div class="ripple-2"></div>
          <div class="ripple-3"></div>
          <img src="/avatar.jpg" alt="小智头像" />
        </div>
      </div>
      <div class="voice-wave-container">
        <div class="voice-wave" ref="voiceWave">
          <div class="wave-line"></div>
          <div class="wave-line"></div>
          <div class="wave-line"></div>
          <div class="wave-line"></div>
          <div class="wave-line"></div>
          <div class="wave-line"></div>
          <div class="wave-line"></div>
          <div class="wave-line"></div>
          <div class="wave-line"></div>
          <div class="wave-line"></div>
        </div>
      </div>
      <div class="button-container">
        <button @click="closePhoneCallPanel">
          <img src="/phone.png" alt="挂断" />
        </button>
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

  /* 语音通话界面 */
  .phone-call-container {
    position: absolute;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 1rem;
    width: 100%;
    height: 100%;
    background-color: #151414;
    transform: translateY(-100%);
    overflow: hidden;
    transition: all 0.5s ease-in-out;

    &.active {
      transform: translateY(0);
    }

    .button-container {
      display: flex;
      justify-content: center;
      align-items: center;
      padding-bottom: 3rem;
      img {
        width: 5rem;
        height: 5rem;
        border-radius: 50%;
        box-shadow: 1px 1px 10px 1px rgba(0, 0, 0, 0.2);
        cursor: pointer;
      }
    }

    /* 用户说话时的音浪动画 */
    .voice-wave-container {
      position: absolute;
      left: 50%;
      bottom: 180px;
      transform: translateX(-50%);
      width: 320px;
      height: 80px;
      display: flex;
      justify-content: center;
      align-items: center;

      .voice-wave {
        display: flex;
        align-items: center;
        gap: 2px;
        height: 100%;

        .wave-line {
          width: 5px;
          background: linear-gradient(
            180deg,
            rgba(255, 64, 129, 0.8) 0%,
            rgba(255, 121, 176, 0.6) 100%
          );
          border-radius: 4px;
          height: 3px;
          transition: height 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        &.active .wave-line {
          animation: voiceWave 1s ease-in-out infinite;
          will-change: height, opacity;

          /* 给每个线条不同的动画延迟，创造波浪效果 */
          &:nth-child(1) {
            animation-delay: -0.4s;
          }
          &:nth-child(2) {
            animation-delay: -0.3s;
          }
          &:nth-child(3) {
            animation-delay: -0.2s;
          }
          &:nth-child(4) {
            animation-delay: -0.1s;
          }
          &:nth-child(5) {
            animation-delay: 0s;
          }
          &:nth-child(6) {
            animation-delay: -0.1s;
          }
          &:nth-child(7) {
            animation-delay: -0.2s;
          }
          &:nth-child(8) {
            animation-delay: -0.3s;
          }
          &:nth-child(9) {
            animation-delay: -0.4s;
          }
          &:nth-child(10) {
            animation-delay: -0.5s;
          }
        }
      }
    }

    /* 多层涟漪效果 */
    .voice-avatar .ripple-1,
    .voice-avatar .ripple-2,
    .voice-avatar .ripple-3 {
      content: "";
      position: absolute;
      border: 2px solid rgba(255, 255, 255, 0.6);
      border-radius: 50%;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%) scale(1);
      pointer-events: none;
      width: 100%;
      height: 100%;
      opacity: 0;
      z-index: 1;
    }

    /* 小智头像的涟漪动画 */
    .voice-avatar-container {
      position: relative;
      display: flex;
      justify-content: center;
      align-items: center;
      margin: 100px auto;
      width: 10rem;
      height: 10rem;

      .voice-avatar {
        position: relative;
        overflow: visible;
        height: 100%;
        width: 100%;
        border-radius: 10%;
        box-shadow: 1px 1px 10px 1px rgba(0, 0, 0, 0.2);
        transition: all 0.1s ease-in-out;

        &.speaking {
          animation: none;
          transform-origin: center;
          will-change: transform;

          .ripple-1 {
            animation: rippleWave 2s linear infinite;
            animation-delay: 0s;
          }

          .ripple-2 {
            animation: rippleWave 2s linear infinite;
            animation-delay: 0.8s;
          }

          .ripple-3 {
            animation: rippleWave 2s linear infinite;
            animation-delay: 1.6s;
          }
        }

        img {
          width: 100%;
          height: 100%;
          object-fit: cover;
          border: 2px solid #fff;
          border-radius: 10%;
          z-index: 2;
        }
      }
    }
  }
}

/* 涟漪动画 */
@keyframes rippleWave {
  0% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.8;
  }
  50% {
    opacity: 0.4;
  }
  100% {
    transform: translate(-50%, -50%) scale(2);
    opacity: 0;
  }
}

/* 音浪动画 */
@keyframes voiceWave {
  0% {
    height: 2px;
    opacity: 0.6;
  }
  50% {
    height: var(--wave-height, 24px);
    opacity: 0.8;
  }
  100% {
    height: 2px;
    opacity: 0.6;
  }
}
</style>
