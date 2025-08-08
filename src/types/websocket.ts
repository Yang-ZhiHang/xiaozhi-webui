import type { WebSocketMessage } from './message';
import { useSettingStore } from '@/stores/setting';

export interface WebSocketHandlers {
    onConnect?: () => void;
    onDisconnect?: (event: CloseEvent) => void;
    onError?: (err: unknown) => void;
    onAudioMessage: (audioBuffer: AudioBuffer) => Promise<void>;
    onTextMessage: (message: WebSocketMessage) => Promise<void>;
}

export interface WebSocketDependencies {
    decodeAudioData: (arrayBuffer: ArrayBuffer) => Promise<AudioBuffer>;
    settingStore: ReturnType<typeof useSettingStore>;
}