<script setup>
import { ref, defineEmits } from "vue";

const emits = defineEmits(["phoneCallPanelClose"]);

const closePhoneCallPanel = () => {
  emits("phoneCallPanelClose");
};
</script>

<template>
  <div class="phone-call-container">
    <div class="image-container">
      <img src="/public/avatar.png" alt="小智头像" />
    </div>

    <div class="button-container">
      <button @click="closePhoneCallPanel">
        <img src="/public/phone.png" alt="挂断" />
      </button>
    </div>
  </div>
</template>

<style scoped>
.phone-call-container {
  position: absolute;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 1rem;
  width: 100%;
  height: 100%;
  background-color: #fff;
  transform: translateY(-100%);
  overflow: hidden;
  transition: all 0.5s ease-in-out;

  &.active {
    transform: translateY(0);
  }

  .image-container {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 10rem;
    height: 10rem;
    margin: 100px auto;
    overflow: hidden;
    border-radius: 50%;
    box-shadow: 1px 1px 10px 1px rgba(0, 0, 0, 0.2);
    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
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
}
</style>
