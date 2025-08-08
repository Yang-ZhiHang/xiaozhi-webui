import { computed, ref } from 'vue'
import type { WebSocketMessage } from '@/types/message'
import type { WebSocketDependencies, WebSocketHandlers } from '@/types/websocket'

export class WebSocketService {
    private _connectionStatus = ref<'connected' | 'disconnected' | 'error'>('disconnected')
    readonly connectionStatus = computed(() => this._connectionStatus.value)
    private ws: WebSocket | null = null
    private handlers: WebSocketHandlers
    private reconnectTimer: number | null = null
    private deps: WebSocketDependencies

    constructor(deps: WebSocketDependencies, handlers: WebSocketHandlers) {
        this.deps = deps
        this.handlers = handlers
    }

    public connect(url: string | URL): void {
        this.ws = new WebSocket(url)
        this.ws.onopen = this.handleOpen.bind(this)
        this.ws.onclose = this.handleClose.bind(this)
        this.ws.onerror = this.handleError.bind(this)
        this.ws.onmessage = this.handleMessage.bind(this)
    }

    public disconnect(): void {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer)
            this.reconnectTimer = null
        }
        this.ws?.close()
        this.ws = null
    }

    public setConnectionStatus(status: 'connected' | 'disconnected' | 'error'): void {
        this._connectionStatus.value = status
    }

    public sendTextMessage(message: any): void {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            console.warn("[WebSocketService] Connection not ready")
            return
        }

        const data = typeof message === 'string' ? message : JSON.stringify(message)
        this.ws.send(data)
    }

    public sendAudioMessage(data: Float32Array): void {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            console.warn("[WebSocketService] Connection not ready")
            return
        }
        this.ws.send(data)
    }

    private handleOpen(): void {
        console.log("[WebSocketService] Connected to server", this.deps.settingStore.wsProxyUrl)
        this._connectionStatus.value = "connected"

        // 发送 Hello 消息
        this.sendHelloMessage()
        this.handlers.onConnect?.()
    }

    private handleClose(event: CloseEvent): void {
        console.log(`[WebSocketService] Connection closed: ${event.code} ${event.reason}`)
        this._connectionStatus.value = "disconnected"
        this.deps.settingStore.sessionId = ""
        this.handlers.onDisconnect?.(event)
    }

    private handleError(error: Event): void {
        console.error("[WebSocketService] Error:", error)
        this._connectionStatus.value = "error"
        this.handlers.onError?.(error)
    }

    private async handleMessage(event: MessageEvent<any>): Promise<void> {
        try {
            if (event.data instanceof Blob) {
                const arrayBuffer: ArrayBuffer = await event.data.arrayBuffer();
                const audioBuffer: AudioBuffer = await this.deps.decodeAudioData(arrayBuffer);
                await this.handleAudioMessage(audioBuffer)
            } else {
                await this.handleTextMessage(event.data)
            }
        } catch (e) {
            console.error("[WebSocketService][handleMessage] Error processing message:", e)
        }
    }

    private async handleAudioMessage(audioBuffer: AudioBuffer): Promise<void> {
        await this.handlers.onAudioMessage?.(audioBuffer)
    }

    private async handleTextMessage(data: any): Promise<void> {
        const message = JSON.parse(data) as WebSocketMessage
        if (message.type === "hello") {
            this.deps.settingStore.sessionId = message.session_id!
        }
        await this.handlers.onTextMessage?.(message)
    }

    private sendHelloMessage(): void {
        const helloMessage = {
            type: "hello",
            version: 3,
            audio_params: {
                format: "opus",
                sample_rate: 16000,  // 需要与后端采样率相匹配（直接改为 24000 将导致语音对话频繁中断）
                channels: 1,
                frame_duration: 60,
            }
        }
        this.sendTextMessage(helloMessage)
    }
}