import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useConfigStore = defineStore('config', () => {
  const WSProxyURL = ref<string>("ws://localhost:5000")
  const isConnected = ref<boolean>(false)
  const sessionID = ref<string>("")
  const setWSProxyURL = (url: string) => {
    WSProxyURL.value = url
  }

  return { WSProxyURL, setWSProxyURL, isConnected, sessionID }
})
