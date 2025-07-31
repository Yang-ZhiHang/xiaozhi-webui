<script setup lang="ts">
import { ref, nextTick } from 'vue';
import type { Message } from '@/types/message';

const messages = ref<Message[]>([]);

// 处理文本内容，去除结尾的，。标点符号
const processText = (text: string): string => {
    text = text.replace(/[，。]$/, '');
    return text;
};

const appendMessage = (type: 'user' | 'ai', text: string) => {
    const now = new Date();
    messages.value.push({
        type,
        content: processText(text),
        time: now.toLocaleTimeString("zh-CN", {
            hour: "2-digit",
            minute: "2-digit",
        })
    });
    nextTick(() => {
        const container = document.querySelector('.chat-container');
        if (container) {
            container.scrollTop = container.scrollHeight;
        }
    });
};

defineExpose({
    appendMessage
});
</script>

<template>
    <div class="chat-container" ref="chatContainerRef">
        <div v-for="(msg, index) in messages" :key="index" :class="['message', msg.type]">
            <div class="message-content" v-html="msg.content"></div>
            <div class="message-time">{{ msg.time }}</div>
        </div>
    </div>
</template>

<style scoped lang="less">
.chat-container {
    flex: 1;
    margin: 0.5rem;
    padding: 0.5rem;
    background-color: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    overflow-y: auto;
    scrollbar-width: none;

    .message.ai,
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

    .message.ai {
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
</style>