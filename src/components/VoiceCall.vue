<script lang="ts" setup>
import { ChatState } from '@/types/chat';
import type { VoiceAnimationManager } from '@/services/VoiceAnimationManager';
import type { ChatStateManager } from '@/services/ChatStateManager';

const props = defineProps<{
    isVisible: boolean;
    voiceAnimationManager: VoiceAnimationManager;
    chatStateManager: ChatStateManager;
}>();

const emit = defineEmits<{
    (e: 'onShutDown'): void;
}>();
</script>

<template>
    <div class="phone-call-container" :class="{ visible: props.isVisible }">
        <div class="voice-avatar-container">
            <div class="voice-avatar" :class="{ speaking: props.chatStateManager.currentState.value === ChatState.AI_SPEAKING }">
                <img src="/avatar.jpg" alt="小智头像" />
            </div>
            <div v-for="i in 3" :key="i" :class="`ripple-${i}`"></div>
        </div>
        <div class="voice-wave-container">
            <div 
                class="voice-wave"
                :class="{ active: props.chatStateManager.currentState.value === ChatState.USER_SPEAKING }"
                :style="{ '--wave-height': `${voiceAnimationManager.voiceWaveHeight.value}px` }"
            >
                <div v-for="i in 10" :key="i" class="wave-line"></div>
            </div>
        </div>
        <div class="button-container">
            <button @click="emit('onShutDown')">
                <img src="/phone.png" alt="挂断" />
            </button>
        </div>
    </div>
</template>

<style scoped lang="less">
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

    &.visible {
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
            height: var(--wave-height, 6px);

            .wave-line {
                width: 5px;
                background: linear-gradient(180deg,
                        rgba(255, 64, 129, 0.8) 0%,
                        rgba(255, 121, 176, 0.6) 100%);
                border-radius: 4px;
                height: 3px;
                transition: height 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }

            &.active .wave-line {
                animation: voice-wave 1s ease-in-out infinite;
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
    .voice-avatar-container .ripple-1,
    .voice-avatar-container .ripple-2,
    .voice-avatar-container .ripple-3 {
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
            z-index: 2;

            &.speaking {
                animation: scale-avatar 1s ease-in-out infinite;
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

@keyframes scale-avatar {
    0% {
        transform: scale(1);
    }

    20% {
        transform: scale(1.02);
    }

    40% {
        transform: scale(1);
    }

    70% {
        transform: scale(1.05);
    }

    100% {
        transform: scale(1);
    }
}

@keyframes voice-wave {
    0% {
        height: 2px;
        opacity: 0.6;
    }

    50% {
        height: var(--wave-height, 6px);
        opacity: 0.8;
    }

    100% {
        height: 2px;
        opacity: 0.6;
    }
}
</style>
