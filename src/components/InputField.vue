<script lang="ts" setup>
import { ref, computed } from 'vue';

const emit = defineEmits<{
    (e: 'sendMessage', text: string): void
    (e: 'phoneCallButtonClicked'): void
}>();

const message = ref<string>("");
const isFocused = ref<boolean>(false);
const displayMessage = computed(() => {
    if (!message.value && !isFocused.value) {
        return '请输入消息...'
    }
})

const clearInputField = () => {
    message.value = '';
};

const onInput = (e: Event) => {
    message.value = (e.target as HTMLDivElement).innerText;
}

const handleKeyPress = (e: KeyboardEvent) => {
    if (e.key === "Enter" && message.value) {
        e.preventDefault();
        emit('sendMessage', message.value);
        clearInputField();
        const messageInput = document.getElementById('messageInput');
        if (messageInput) {
            messageInput.innerText = "";
        }
    }
};

const handleSendButtonClick = () => {
    emit('sendMessage', message.value);
    clearInputField();
    const messageInput = document.getElementById('messageInput');
    if (messageInput) {
        messageInput.innerText = "";
    }
};
</script>

<template>

    <div class="input-field">
        <div 
            id="messageInput" 
            contenteditable="true" 
            @input="onInput" 
            @keydown="handleKeyPress"
            @focus="isFocused = true" 
            @blur="isFocused = false"
        >
            {{ displayMessage }}
        </div>
        <button id="send-message" @click="handleSendButtonClick">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 1.414L10.586 9H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z"
                    clip-rule="evenodd" />
            </svg>
        </button>
        <button id="phone-call" @click="emit('phoneCallButtonClicked')">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path
                    d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z" />
            </svg>
        </button>
    </div>
</template>

<style scoped lang="less">
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

        white-space: pre-wrap;
        /* 换行 */
        text-overflow: ellipsis;
        /* 当内容溢出时显示省略号 */
        cursor: text;

        &:focus {
            color: #1C1C1D;
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
        cursor: pointer;
    }

    #send-message {
        background-color: var(--primary-color);
    }

    #phone-call {
        background-color: #10b981;
    }
}
</style>
