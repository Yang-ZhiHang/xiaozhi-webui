import os
import uuid
from dotenv import load_dotenv
import asyncio
import multiprocessing
import atexit
from websocket_proxy import WebSocketProxy

# 默认配置
DEFAULT_CONFIG = {
    "WS_URL": "ws://localhost:5001",
    "ENABLE_TOKEN": "true",
    "DEVICE_TOKEN": "test_token",
    "PROXY_PORT": "5000",
    "PROXY_HOST": "0.0.0.0",
}


def get_dotenv():
    """确保 .env 文件存在，否则创建并使用默认配置"""
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_path):
        print("未找到 .env 文件，创建默认配置...")
        with open(env_path, "w") as f:
            for key, value in DEFAULT_CONFIG.items():
                f.write(f"{key}={value}\n")
    return env_path


env_path = get_dotenv()
load_dotenv(env_path)


# ========== 全局环境变量 start ==========
WS_URL = os.getenv("WS_URL", DEFAULT_CONFIG["WS_URL"])
ENABLE_TOKEN = (
    os.getenv("ENABLE_TOKEN", DEFAULT_CONFIG["ENABLE_TOKEN"]).lower() == "true"
)
if ENABLE_TOKEN:
    TOKEN = os.getenv("DEVICE_TOKEN", DEFAULT_CONFIG["DEVICE_TOKEN"])
PROXY_PORT = os.getenv("PROXY_PORT", DEFAULT_CONFIG["PROXY_PORT"])
PROXY_HOST = os.getenv("PROXY_HOST", DEFAULT_CONFIG["PROXY_HOST"])
# ========== 全局环境变量 end ==========

proxy_process = None


def get_mac_address():

    # 获取设备的唯一标识符并转换为十六进制字符串
    mac_hex = uuid.UUID(int=uuid.getnode()).hex[-12:]

    # 以 MAC 地址的形式输出 mac_hex
    mac_address = ":".join([mac_hex[i : i + 2] for i in range(0, 12, 2)])

    return mac_address


def cleanup():
    """清理进程"""
    global proxy_process
    if proxy_process:
        proxy_process.terminate()
        proxy_process.join()
        proxy_process = None


def run_proxy():
    """在单独的进程中运行proxy服务器"""
    proxy = WebSocketProxy()
    asyncio.run(proxy.main())


if __name__ == "__main__":
    # 注册退出时的清理函数
    atexit.register(cleanup)

    device_id = get_mac_address()
    print(f"Device ID: {device_id}")
    print(f"Token: {TOKEN}")
    print(f"WS URL: {WS_URL}")
    print(f"Proxy Server: {PROXY_HOST}:{PROXY_PORT}")

    # 启动 Proxy 服务器
    run_proxy()
    print("Proxy server started in background process")
