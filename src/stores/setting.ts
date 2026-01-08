import { ref, type Ref } from 'vue'
import { defineStore } from 'pinia'
import { log, warn } from '@/common/log'

export const useSettingStore = defineStore('setting', () => {
	// state
	const sessionId = ref<string>("")
	const wsProxyUrl = ref<string>("")
	const tokenEnable = ref<boolean>(false)
	const token = ref<string>("")
	const visible = ref<boolean>(false)

	const configRefMap: Record<string, Ref<string | boolean>> = {
		ws_proxy_url: wsProxyUrl,
		token_enable: tokenEnable,
		token: token,
	}

	const saveToLocal = (): boolean => {
		const configJson = {
			ws_proxy_url: wsProxyUrl.value,
			token_enable: tokenEnable.value,
			token: token.value,
		}

		// 通过标记切换字段必填需求，避免可选项为空时出现误判
		const requiredWhenEnabled: Record<string, () => boolean> = {
			token: () => tokenEnable.value,
		}
		const dataOK = Object.entries(configJson).every(([key, value]) => {
			const isRequired = requiredWhenEnabled[key]?.() ?? true
			if (!isRequired) return true
			return value !== ""
		})

		if (dataOK) {
			localStorage.setItem('settings', JSON.stringify(configJson))
			log("配置文件更新成功", configJson)
		} else {
			warn("配置文件数据不完整，未保存", configJson)
		}
		return dataOK
	}

	const updateConfig = (settings: any) => {
		Object.entries(configRefMap).forEach(([key, ref]) => {
			if (settings[key] !== undefined && settings[key] !== null) {
				ref.value = settings[key]
			}
		})
	}

	const loadFromLocal = (): boolean => {
		const localConfig = localStorage.getItem('settings')
		if (localConfig) {
			updateConfig(JSON.parse(localConfig))
			log("配置文件加载成功")
			return true
		}
		log("配置文件不存在")
		return false
	}

	const destoryLocal = () => {
		localStorage.removeItem('settings')
		log("本地缓存配置文件已删除")
	}

	return {
		sessionId,
		wsProxyUrl,
		tokenEnable,
		token,
		visible,
		updateConfig,
		saveToLocal,
		loadFromLocal,
		destoryLocal,
	}
})

