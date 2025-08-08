import { VoiceAnimationManager } from '../services/VoiceAnimationManager';

export enum ChatEvent {
    USER_START_SPEAKING = 'userStartSpeaking',
    USER_STOP_SPEAKING = 'userStopSpeaking',
    AI_START_SPEAKING = 'aiStartSpeaking',
    AI_STOP_SPEAKING = 'aiStopSpeaking',
}

export type ChatEventType =
    | ChatEvent.USER_START_SPEAKING
    | ChatEvent.USER_STOP_SPEAKING
    | ChatEvent.AI_START_SPEAKING
    | ChatEvent.AI_STOP_SPEAKING

export type ChatEventHandler = (data?: any) => void;

export enum ChatState {
    IDLE = "idle",
    AI_SPEAKING = "ai_speaking",
    USER_SPEAKING = "user_speaking",
}

export interface ChatStateDependencies {
    thresholds: {
        USER_SPEAKING: number;
        USER_INTERRUPT_AI: number;
    };
    timeout: {
        SILENCE: number;
    };
    callbacks: {
        sendAudioData: (data: Float32Array) => void;
        sendTextData: (text: any) => void;
        getSessionId: () => string;
    };
    voiceAnimationManager?: VoiceAnimationManager
}

// 状态转换接口
export interface ChatStateTransition {
    onEnter?: (oldState?: ChatState) => void;
    onExit?: (newState?: ChatState) => void;
    handleAudioLevel: (audioLevel: number, data?: any) => void;
}