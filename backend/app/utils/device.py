import uuid
import socket
from logging import getLogger

logger = getLogger(__name__)


def get_mac_address() -> str:
    """获取设备的唯一标识符"""
    mac_hex = uuid.UUID(int=uuid.getnode()).hex[-12:]

    mac_address = ":".join([mac_hex[i : i + 2] for i in range(0, 12, 2)])

    try:
        # 获取设备的唯一标识符并转换为十六进制字符串
        node = uuid.getnode()
        mac_hex = uuid.UUID(int=node).hex[-12:]
        # 以 MAC 地址的形式输出 mac_hex
        mac_address = ":".join([mac_hex[i : i + 2] for i in range(0, 12, 2)])
        logger.info(f"成功获取到 MAC 地址: {mac_address} (node: {node})")
        return mac_address
    except Exception as e:
        logger.error(f"获取 MAC 地址失败: {e}")
        return ""


def get_local_ip() -> str:
    """# 创建一个临时 socket 连接来获取本机 IP"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def get_client_id() -> str:
    """创建并返回一个客户端的唯一标识ID"""
    return str(uuid.uuid4())
