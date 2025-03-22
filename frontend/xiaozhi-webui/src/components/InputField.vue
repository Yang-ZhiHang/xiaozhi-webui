<script setup></script>

<template>
  <div class="input-field">
    <input type="text" id="messageInput" placeholder="请输入消息..." />
    <button id="send-message" onclick="sendMessage()">
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
    <button id="phone-call">
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
</template>

<style lang="less" scoped>
.input-field {
  display: flex;
  padding: 0.75rem;
  background-color: #fff;
  border-top: 1px solid #e5e7eb;
  height: 5.5rem;
  gap: 0.5rem;

  #messageInput {
    flex: 1;
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
    background-color: #4f46e5;
  }

  #phone-call {
    background-color: #10b981;
  }
}
</style>
