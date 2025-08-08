import { ElMessage } from "element-plus";

export class AudioService {
  private static instance: AudioService;
  private _audioContext: AudioContext;
  private _audioStream: MediaStream | null = null;
  private _userMediaNode: MediaStreamAudioSourceNode | null = null;
  private _processorNode: AudioWorkletNode | null = null;
  private _onProcess: ((audioLevel: number, audioData: Float32Array) => void) | null = null;
  private _sourceNode: AudioBufferSourceNode | null = null;
  private _audioQueue: AudioBuffer[] = [];
  private _onQueueEmpty: (() => void) | null = null;

  private constructor() {
    this._audioContext = new (window.AudioContext || window.webkitAudioContext)({
      sampleRate: 16000,
    }); // webkit 兼容苹果 Safari 浏览器
  }

  /**
   * 音频电平检测
   * @param {Float32Array} audioData 音频数据
   * @returns {number} 音频电平值
   */
  private detectAudioLevel = (audioData: Float32Array): number => {
    if (!audioData || !audioData.length) return 0;
    let sum = 0;
    for (let i = 0; i < audioData.length; i++) {
      sum += Math.abs(audioData[i]);
    }
    return sum / audioData.length;
  }

  public static getInstance(): AudioService {
    if (!AudioService.instance) {
      AudioService.instance = new AudioService();
    }
    return AudioService.instance;
  }

  public getAudioContext(): AudioContext {
    return this._audioContext;
  }

  public async decodeAudioData(arrayBuffer: ArrayBuffer): Promise<AudioBuffer> {
    return await this._audioContext.decodeAudioData(arrayBuffer);
  }

  public enqueueAudio = (audioBuffer: AudioBuffer) => {
    try {
      this._audioQueue.push(audioBuffer);
      console.log("[AudioManager][enqueueAudio] Audio enqueued");
    } catch (e) {
      console.error("[AudioManager][enqueueAudio] Error:", e);
    }
  };

  public onQueueEmpty(callback: () => void) {
    this._onQueueEmpty = callback;
  }

  public onProcess(callback: (audioLevel: number, audioData: Float32Array) => void) {
    this._onProcess = callback;
  }

  public playAudio = async () => {
    if (this._audioQueue.length === 0) {
      console.log("[AudioManager][playAudio] Audio queue is empty.");
      this._onQueueEmpty?.();
      return;
    }

    const audioBuffer: AudioBuffer = this._audioQueue.shift() as AudioBuffer;

    // 创建播放节点
    this._sourceNode = this._audioContext.createBufferSource();
    this._sourceNode.buffer = audioBuffer;
    this._sourceNode.connect(this._audioContext.destination);
    this._sourceNode.onended = () => {
      this._sourceNode!.disconnect();
      this.playAudio();
    };
    this._sourceNode.start();
  };

  public stopPlaying = () => {
    if (this._sourceNode) {
      this._sourceNode.stop();
      this._sourceNode.disconnect();
      this._sourceNode = null;
    }
  };

  private loadAudioWorklet = async () => {
    // 加载音频处理脚本
    if (!this._audioContext.audioWorklet) {
      console.warn("[AudioManager][prepareMediaResources] AudioWorklet is not supported in this browser.");
      throw new Error("浏览器不支持 AudioWorklet");
    }
    await this._audioContext.audioWorklet.addModule(
      "/audioProcessor.js"
    );
    console.log("[AudioManager][prepareMediaResources] Audio processor loaded.")
  }

  private initAudioStream = async () => {
    // 初始化音频流
    if (!navigator.mediaDevices) {
      console.warn("[AudioManager][prepareMediaResources] MediaDevices API is not supported in this browser.");
      throw new Error("浏览器不支持 userMedia");
    }
    this._audioStream = await navigator.mediaDevices.getUserMedia({
      audio: {
        sampleRate: 24000,
        channelCount: 1,
        echoCancellation: true,
        noiseSuppression: true,
      },
      video: false,
    }).catch((err: unknown) => {
      console.log("[AudioManager][startRecording] Error getting user media:", err);
      return null;
    });
    console.log("[AudioManager][startRecording] UserMedia created:", this._audioStream);
  }

  private initUserMediaNode = () => {
    // 初始化用户媒体流节点
    // 利用 MediaStream 创建音频源节点
    if (this._audioStream) {
      this._userMediaNode = this._audioContext.createMediaStreamSource(this._audioStream);
      console.log("[AudioManager][prepareMediaResources] userMediaNode created:", this._userMediaNode);
    }
  }

  private initProcessorNode = () => {
    // 初始化音频处理节点
    // 使用自定义的 audioContext 节点，用于后续处理音频数据
    // https://developer.mozilla.org/zh-CN/docs/Web/API/AudioWorkletNode
    this._processorNode = new AudioWorkletNode(this._audioContext, "audioProcessor", {
      processorOptions: {
        bufferSize: 960, // 16KHz 的采样频率下，60ms 包含的采样点个数
      },
    });

    // 处理节点的出口回调函数，用于接收 process 函数处理后的音频数据
    this._processorNode.port.onmessage = (e: MessageEvent) => {
      if (!(e.data instanceof Float32Array)) {
        console.warn("[AudioManager][processorNode.port.onmessage] Unexpected data format:", typeof e.data);
        return;
      }
      const audioLevel = this.detectAudioLevel(e.data);
      console.log("[AudioManager][processorNode.port.onmessage] Audio Level:", audioLevel.toFixed(2));
      this._onProcess?.(audioLevel, e.data);
    };
  }

  // 初始化语音通话需要的媒体资源
  public prepareMediaResources = async () => {
    try {
      await this.loadAudioWorklet();
      await this.initAudioStream();
      this.initUserMediaNode();
      this.initProcessorNode();
    } catch (error: unknown) {
      console.error("[AudioManager][prepareMediaResources] Error:", error);
      ElMessage.error(error as string);
      return;
    }

    if (!this._audioStream || !this._userMediaNode || !this._processorNode) {
      console.log("[AudioManager][connectMediaResources] Resources not ready.");
      return;
    }
    this._userMediaNode.connect(this._processorNode);
    this._audioStream.getTracks().forEach((track) => (track.enabled = true));

    if (this._audioContext.state === "suspended") {
      await this._audioContext.resume();
      console.log("[AudioManager][prepareMediaResources] AudioContext resumed.");
    }
  };

  public stopAudioStream = () => {
    if (this._audioStream) {
      this._audioStream.getTracks().forEach((track) => track.enabled = false);
      console.log("[AudioManager][stopAudioStream] Audio stream stopped.");
    }
  }

  public stopUserMediaNode = () => {
    if (this._userMediaNode) {
      this._userMediaNode.disconnect();
      console.log("[AudioManager][stopUserMediaNode] User media node stopped.");
    }
  }

  public stopMediaResources = () => {
    this.stopAudioStream();
    this.stopUserMediaNode();
    console.log("[AudioManager][stopMediaResources] Media resources stopped.");
  }

  public clearAudioQueue = () => {
    this._audioQueue = [];
  }

  public clearAudioStream = () => {
    if (this._audioStream) {
      this._audioStream.getTracks().forEach((track) => track.stop());
      this._audioStream = null;
      console.log("[AudioManager][clearMediaResources] this._audioStream closed");
    }
  }

  public clearUserMediaNode = () => {
    if (this._userMediaNode) {
      this._userMediaNode.disconnect();
      this._userMediaNode = null;
      console.log("[AudioManager][clearMediaResources] this._userMediaNode closed");
    }
  }

  public clearProcessorNode = () => {
    if (this._processorNode) {
      this._processorNode.port.onmessage = null;
      this._processorNode.disconnect();
      this._processorNode = null;
      console.log("[AudioManager][clearMediaResources] this._processorNode closed");
    }
  }

  public clearMediaResources = () => {
    this.clearAudioQueue();
    this.clearAudioStream();
    this.clearUserMediaNode();
    this.clearProcessorNode();
  };
}