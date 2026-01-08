import os
import json
from .utils.device import get_client_id, get_mac_address
from .constant.file import BASE_DIR
from logging import getLogger

logger = getLogger(__name__)


class ConfigManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self._default_config = {
            "WS_URL": "wss://api.tenclass.net/xiaozhi/v1/",
            "WS_PROXY_URL": "ws://0.0.0.0:5000",
            "OTA_VERSION_URL": "https://api.tenclass.net/xiaozhi/ota/",
            "TOKEN_ENABLE": True,
            "TOKEN": "test_token",
        }
        self._config = {}
        self._init_config()

    def _init_config(self) -> None:
        """确保配置文件存在，否则创建并使用默认配置"""
        config_file_path = os.path.join(BASE_DIR, "config", "config.json")

        if not os.path.exists(config_file_path):
            logger.info("本地配置文件不存在，正在创建默认配置: ", config_file_path)
            os.makedirs(os.path.join(BASE_DIR, "config"), exist_ok=True)
            self._default_config["CLIENT_ID"] = get_client_id()
            self._default_config["DEVICE_ID"] = get_mac_address()
            with open(config_file_path, "w") as f:
                json.dump(self._default_config, f, indent=4)

        logger.info(f"正在加载本地配置: {config_file_path}")

        try:
            with open(config_file_path, "r") as f:
                self._config = json.load(f)
        except json.JSONDecodeError:
            logger.warning("配置文件格式错误，正在重置配置")
            with open(config_file_path, "w") as f:
                json.dump(self._default_config, f, indent=4)
            self._config = self._default_config

    def get(self, key: str) -> str | bool | None:
        return self._config.get(key)

    def get_str(self, key: str, default: str = "") -> str:
        value = self._config.get(key, default)
        return str(value) if value is not None else default

    def get_bool(self, key: str, default: bool = False) -> bool:
        value = self._config.get(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes", "on")
        return bool(value)

    def get_int(self, key: str, default: int = 0) -> int:
        value = self._config.get(key, default)
        try:
            return int(value) if value is not None else default
        except (ValueError, TypeError):
            return default

    def set(self, key: str, value: str | bool) -> None:
        self._config[key] = value

    @property
    def config(self) -> dict:
        return self._config

    def save_config(self) -> None:
        config_file_path = os.path.join(BASE_DIR, "config", "config.json")
        with open(config_file_path, "w") as f:
            json.dump(self._config, f, indent=4)
