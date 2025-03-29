import os
from urllib.parse import urlparse
import uuid
import asyncio
import atexit
from websocket_proxy import WebSocketProxy
from flask import Flask, jsonify, request
from flask_cors import CORS
import multiprocessing
import json

# 默认配置
DEFAULT_CONFIG = {
    "WS_URL": "wss://api.tenclass.net/xiaozhi/v1/",
    "TOKEN_ENABLE": "true",
    "DEVICE_TOKEN": "test_token",
    "PROXY_HOST": "0.0.0.0",
    "PROXY_PORT": "5000",
    "BACKEND_HOST": "0.0.0.0",
    "BACKEND_PORT": "8081",
}


def get_mac_address():

    # 获取设备的唯一标识符并转换为十六进制字符串
    mac_hex = uuid.UUID(int=uuid.getnode()).hex[-12:]

    # 以 MAC 地址的形式输出 mac_hex
    mac_address = ":".join([mac_hex[i : i + 2] for i in range(0, 12, 2)])

    return mac_address


def get_env():
    """确保配置文件存在，否则创建并使用默认配置"""
    config_path = os.path.join(os.path.dirname(__file__), "config", "config.json")
    if not os.path.exists(config_path):
        print("[app][get_env] 未找到配置文件，正在创建: ", config_path)
        os.makedirs(os.path.join(os.path.dirname(__file__), "config"), exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(DEFAULT_CONFIG, f)
    print("[app][get_env] 正在加载配置文件: ", config_path)
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except json.JSONDecodeError:
        print("[app][get_env] 配置文件格式错误，正在重置为默认配置")
        with open(config_path, "w") as f:
            json.dump(DEFAULT_CONFIG, f)
        config = DEFAULT_CONFIG
    return config


# ========== 全局环境变量 start ==========
config = get_env()

WS_URL = config["WS_URL"]

TOKEN_ENABLE = config["TOKEN_ENABLE"] == "true"
DEVICE_TOKEN = config["DEVICE_TOKEN"]

PROXY_PORT = config["PROXY_PORT"]
PROXY_HOST = config["PROXY_HOST"]

BACKEND_PORT = config["BACKEND_PORT"]
BACKEND_HOST = config["BACKEND_HOST"]

DEVICE_ID = get_mac_address()

proxy_process = None
# ========== 全局环境变量 end ==========


def cleanup():
    """清理进程"""
    global proxy_process
    if proxy_process:
        proxy_process.terminate()
        proxy_process.join()
        proxy_process = None


def run_proxy():
    """在单独的进程中运行proxy服务器"""
    proxy = WebSocketProxy(
        device_id=DEVICE_ID,
        websocket_url=WS_URL,
        proxy_host=PROXY_HOST,
        proxy_port=PROXY_PORT,
        token_enable=TOKEN_ENABLE,
        token=DEVICE_TOKEN,
    )
    asyncio.run(proxy.main())


app = Flask(__name__)
CORS(app)


@app.route("/config", methods=["GET"])
def get_config():
    """获取配置信息"""
    config = get_env()
    print("[app][get_config] 配置文件: ", config)
    data = {
        "ws_url": config["WS_URL"],
        "ws_proxy_url": f"ws://{config["PROXY_HOST"]}:{config["PROXY_PORT"]}",
        "token_enable": config["TOKEN_ENABLE"],
        "device_id": DEVICE_ID,
        "code": 0,
    }
    if config["TOKEN_ENABLE"]:
        data["token"] = config["DEVICE_TOKEN"]

    return jsonify(data), 200


@app.route("/save_config", methods=["POST"])
def save_config():
    """保存配置信息"""
    data = request.json
    config = get_env()
    ws_proxy_url = data["WS_PROXY_URL"]
    proxy_host = urlparse(ws_proxy_url).hostname
    proxy_port = urlparse(ws_proxy_url).port
    data["PROXY_HOST"] = proxy_host
    data["PROXY_PORT"] = proxy_port
    data["DEVICE_TOKEN"] = data["TOKEN"]
    del data["TOKEN"], data["WS_PROXY_URL"]
    config.update(data)
    print("[app][save_config] 更新后的配置文件: ", config)
    with open(
        os.path.join(os.path.dirname(__file__), "config", "config.json"), "w"
    ) as f:
        json.dump(config, f, indent=4)
    return jsonify({"code": 0, "message": "配置已保存"}), 200


if __name__ == "__main__":
    # 注册退出时的清理函数
    atexit.register(cleanup)

    print(f"Proxy Server: {PROXY_HOST}:{PROXY_PORT}")
    print(f"Device ID: {DEVICE_ID}")
    print(f"Token: {DEVICE_TOKEN}")
    print(f"WS URL: {WS_URL}")

    # 启动 Proxy 服务器
    proxy_process = multiprocessing.Process(target=run_proxy)
    proxy_process.start()
    print("Proxy server started in background process")

    # 启动 Flask 服务器
    app.run(host=BACKEND_HOST, port=BACKEND_PORT, debug=False)
