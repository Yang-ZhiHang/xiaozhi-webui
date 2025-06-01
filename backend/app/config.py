import os
from .libs.logger import get_logger
import json
from .libs.device import get_client_id, get_mac_address
from .constant.file import BASE_DIR

logger = get_logger(__name__)


class ConfigManager:

    def __init__(self):
        self._default_config = {
            "WS_URL": "wss://api.tenclass.net/xiaozhi/v1/",
            "WS_PROXY_URL": "ws://0.0.0.0:5000",
            "OTA_VERSION_URL": "https://api.tenclass.net/xiaozhi/ota/",
            "TOKEN_ENABLE": "true",
            "TOKEN": "test_token",
            "BACKEND_URL": "http://0.0.0.0:8081",
        }
        self._config = None
        self._init_config()

    def _init_config(self) -> None:
        """确保配置文件存在，否则创建并使用默认配置"""
        config_file_path = os.path.join(BASE_DIR, "config", "config.json")

        if not os.path.exists(config_file_path):
            logger.info("配置文件不存在，正在创建默认配置: ", config_file_path)
            os.makedirs(os.path.join(BASE_DIR, "config"), exist_ok=True)
            self._default_config["CLIENT_ID"] = get_client_id()
            self._default_config["DEVICE_ID"] = get_mac_address()
            with open(config_file_path, "w") as f:
                json.dump(self._default_config, f, indent=4)

        logger.info("正在加载配置: ", config_file_path)

        try:
            with open(config_file_path, "r") as f:
                self._config = json.load(f)
        except json.JSONDecodeError:
            logger.warning("配置文件格式错误，正在重置配置")
            with open(config_file_path, "w") as f:
                json.dump(self._default_config, f, indent=4)
            self._config = self._default_config

    def get(self, key: str) -> str:
        return self._config.get(key)

    def set(self, key: str, value: str) -> None:
        self._config[key] = value

    def get_config(self) -> dict:
        """获取配置文件内容"""
        return self._config

    def save_config(self) -> None:
        """保存配置文件内容"""
        config_file_path = os.path.join(BASE_DIR, "config", "config.json")
        with open(config_file_path, "w") as f:
            json.dump(self._config, f, indent=4)


configuration = ConfigManager()
