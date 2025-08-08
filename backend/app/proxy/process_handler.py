import signal
import sys
from urllib.parse import urlparse
from .websocket_proxy import WebSocketProxy
from ..config import ConfigManager
from ..utils.logger import get_logger
import asyncio

logger = get_logger(__name__)


def cleanup(process):
    """清理进程"""
    if process and process.is_alive():
        logger.info("正在关闭代理进程...")
        process.terminate()
        process.join(timeout=5)
        if process.is_alive():
            logger.warning("强制关闭代理进程")
            process.kill()
            process.join()
        logger.info("代理进程已关闭")


def run_proxy():
    """在单独的进程中运行代理服务器"""
    try:
        configuration = ConfigManager()
        ws_proxy_url = configuration.get_str("WS_PROXY_URL")
        proxy = WebSocketProxy(
            device_id=configuration.get_str("DEVICE_ID"),
            client_id=configuration.get_str("CLIENT_ID"),
            websocket_url=configuration.get_str("WS_URL"),
            ota_version_url=configuration.get_str("OTA_VERSION_URL"),
            proxy_host=urlparse(ws_proxy_url).hostname,
            proxy_port=urlparse(ws_proxy_url).port,
            token_enable=configuration.get_bool("TOKEN_ENABLE"),
            token=configuration.get_str("DEVICE_TOKEN"),
        )
        
        # 运行代理服务器
        asyncio.run(proxy.main())
        
    except KeyboardInterrupt:
        logger.info("代理进程收到中断信号")
    except Exception as e:
        logger.error(f"代理进程异常: {e}")
    finally:
        logger.info("代理进程退出")
