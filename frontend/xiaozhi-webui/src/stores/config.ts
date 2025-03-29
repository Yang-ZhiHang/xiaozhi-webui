import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useConfigStore = defineStore('config', () => {
  const WSURL = ref<string>("wss://api.tenclass.net/xiaozhi/v1/")
  const WSProxyURL = ref<string>("ws://localhost:5000")
  const tokenEnable = ref<boolean>(false)
  const token = ref<string>("")
  const sessionID = ref<string>("")
  const deviceID = ref<string>("")

  // Setters
  const setWSProxyURL = (url: string): void => {
    WSProxyURL.value = url
  }
  const setWSURL = (url: string): void => {
    WSURL.value = url
  }
  const setTokenEnable = (enabled: boolean): void => {
    tokenEnable.value = enabled
  }
  const setSessionID = (id: string): void => {
    sessionID.value = id
  }
  const setDeviceID = (id: string): void => {
    deviceID.value = id
  }
  const setToken = (t: string): void => {
    token.value = t
  }

  // Getters
  const getWSURL = (): string => {
    return WSURL.value
  }
  const getWSProxyURL = (): string => {
    return WSProxyURL.value
  }
  const getTokenEnable = (): boolean => {
    return tokenEnable.value
  }
  const getSessionID = (): string => {
    return sessionID.value
  }
  const getDeviceID = (): string => {
    return deviceID.value
  }
  const getToken = (): string => {
    return token.value
  }

  // Initialization
  const init = async () => {
    try {
      const response = await fetch(import.meta.env.VITE_APP_SERVER_URL + "/config")
      const data = await response.json()
      if (data.ws_proxy_url) {
        setWSProxyURL(data.ws_proxy_url)
      }
      if (data.ws_url) {
        setWSURL(data.ws_url)
      }
      if (data.token_enable) {
        setTokenEnable(data.token_enable)
        setToken(data.token)
      }
      if (data.device_id) {
        setDeviceID(data.device_id)
      }
    } catch (error) {
      console.error("[useConfigStore][init]", error)
    }
  }

  return {
    init,
    setWSURL,
    setWSProxyURL,
    setTokenEnable,
    setSessionID,
    setDeviceID,
    setToken,
    getWSURL,
    getWSProxyURL,
    getTokenEnable,
    getSessionID,
    getDeviceID,
    getToken
  }
})
