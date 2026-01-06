import { computed, ref } from "vue";
import {
    ChatState,
    ChatEvent,
    type ChatStateDependencies,
    type ChatStateTransition,
    type ChatEventHandler,
} from "@/types/chat";
import { AIListening_Start, AIListening_Stop, AbortMessage } from "@/types/message";
import { log } from "@/common/log";

export class ChatStateManager {
    private _currentState = ref<ChatState>(ChatState.IDLE);
    readonly currentState = computed<ChatState>(() => this._currentState.value);
    private deps: ChatStateDependencies;
    private transitions: Map<ChatState, ChatStateTransition>;
    private eventHandlers: Map<ChatEvent, ChatEventHandler[]> = new Map();
    private silenceTimer: ReturnType<typeof setTimeout> | null = null;

    constructor(deps: ChatStateDependencies) {
        this.transitions = new Map<ChatState, ChatStateTransition>();
        this.deps = deps;
        this.initializeTransitions();
    }

    public on(event: ChatEvent, handler: ChatEventHandler) {
        if (!this.eventHandlers.get(event)) {
            this.eventHandlers.set(event, []);
        }
        this.eventHandlers.get(event)!.push(handler);
    }

    public emit(event: ChatEvent, data?: any) {
        this.eventHandlers.get(event)?.forEach(handler => handler(data));
    }

    private initializeTransitions() {
        this.transitions.set(ChatState.IDLE, {
            onEnter: () => { },
            handleAudioLevel: (audioLevel: number) => {
                if (audioLevel > this.deps.thresholds.USER_SPEAKING) {
                    this.setState(ChatState.USER_SPEAKING);
                }
            }
        })

        this.transitions.set(ChatState.USER_SPEAKING, {
            onEnter: (oldState) => {
                if (oldState === ChatState.USER_SPEAKING) return;
                const aiListening_Start = AIListening_Start;
                this.deps.callbacks.sendTextData(aiListening_Start)
                console.log("[ChatStateManager][USER_SPEAKING.onEnter] User started speaking");
                this.emit(ChatEvent.USER_START_SPEAKING)
            },
            onExit: () => {
                if (this.silenceTimer) {
                    clearTimeout(this.silenceTimer);
                    this.silenceTimer = null;
                }
                const aiListening_Stop = AIListening_Stop;
                this.deps.callbacks.sendTextData(aiListening_Stop);
                console.log("[ChatStateManager][USER_SPEAKING.onExit] User stoped speaking");
                this.emit(ChatEvent.USER_STOP_SPEAKING)
            },
            handleAudioLevel: (audioLevel: number, data: Float32Array) => {
                this.deps.callbacks.sendAudioData(data);
                if (audioLevel < this.deps.thresholds.USER_SPEAKING) {
                    if (!this.silenceTimer) {
                        // 用户停止说话 {SLIENCE} 秒后，切换到 AI_SPEAKING 状态
                        this.silenceTimer = setTimeout(() => {
                            console.log("[ChatStateManager][USER_SPEAKING.handleAudioLevel] User stopped speaking, time's up");
                            this.setState(ChatState.AI_SPEAKING);
                            this.silenceTimer = null;
                        }, this.deps.timeout.SILENCE);
                    }
                } else {
                    this.deps.voiceAnimationManager?.updateUserWave(audioLevel);
                    if (this.silenceTimer) {
                        console.log("[ChatStateManager][USER_SPEAKING.handleAudioLevel] User is still speaking, clearing silence timer");
                        clearTimeout(this.silenceTimer);
                        this.silenceTimer = null;
                    }
                }
            },
        })

        this.transitions.set(ChatState.AI_SPEAKING, {
            onEnter: (oldState) => {
                if (oldState === ChatState.AI_SPEAKING) return;
                this.emit(ChatEvent.AI_START_SPEAKING)
            },
            onExit: () => {
                this.emit(ChatEvent.AI_STOP_SPEAKING)
            },
            handleAudioLevel: (audioLevel: number) => {
                if (audioLevel > this.deps.thresholds.USER_INTERRUPT_AI) {
                    const abortMessage = AbortMessage(this.deps.callbacks.getSessionId());
                    this.deps.callbacks.sendTextData(abortMessage);
                    this.setState(ChatState.USER_SPEAKING);
                }
            },
        })
    }

    public setState(newState: ChatState) {
        const oldState = this.currentState.value;
        const oldTransition = this.transitions.get(oldState);
        const newTransition = this.transitions.get(newState);
        oldTransition?.onExit?.();
        this._currentState.value = newState;
        log("State changed from", oldState, "to", newState)
        newTransition?.onEnter?.(oldState);
    }

    public handleUserAudioLevel(audioLevel: number, data: Float32Array) {
        const currentTransition = this.transitions.get(this.currentState.value);
        currentTransition?.handleAudioLevel(audioLevel, data);
    }

    public destroy() {
        if (this.silenceTimer) {
            clearTimeout(this.silenceTimer);
            this.silenceTimer = null;
        }
    }
}