import { computed, ref } from "vue";

export class VoiceAnimationManager {
    private readonly maxWaveHeight: number = 24;
    private readonly minWaveHeight: number = 6;
    private readonly maxAIScale: number = 1.05;
    private readonly minAIScale: number = 1;
    private _avatarScale = ref<number>(1);
    private _voiceWaveHeight = ref<number>(0);
    readonly voiceWaveHeight = computed(() => this._voiceWaveHeight.value);
    readonly avatarScale = computed(() => this._avatarScale.value);

    constructor() { }

    public setVoiceWaveHeight(height: number) {
        this._voiceWaveHeight.value = Math.min(Math.max(height, this.minWaveHeight), this.maxWaveHeight);
    }

    public updateUserWave(audioLevel: number) {
        if (audioLevel > 0.01) {
            this.setVoiceWaveHeight(this.minWaveHeight + audioLevel * 100);
        } else {
            this.setVoiceWaveHeight(this.minWaveHeight);
        }
    }
}