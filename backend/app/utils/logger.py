import os
from logging.handlers import RotatingFileHandler
import logging
from colorlog import ColoredFormatter
from ..constant.file import BASE_DIR
import sys


def setup_logging():
    """
    配置日志
    """
    # Windows 控制台编码修复
    if sys.platform == "win32":
        # 设置控制台编码为 UTF-8
        try:
            # Python 3.7+ 支持
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except AttributeError:
            # 兼容较老版本
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
        
        # 设置环境变量确保正确的编码
        os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    log_dir = os.path.join(BASE_DIR, "logs")
    os.makedirs(log_dir, exist_ok=True)

    # 日志文件路径
    log_file = os.path.join(log_dir, "app.log")

    # 创建根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # 清除已有的处理器（避免重复添加）
    if root_logger.handlers:
        root_logger.handlers.clear()

    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # 创建按文件大小分割的文件处理器
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding='utf-8'
    ) 
    file_handler.setLevel(logging.INFO)
    setattr(file_handler, 'suffix', "%Y-%m-%d.log")

    # 创建格式化器
    formatter = logging.Formatter(
        "%(asctime)s [%(name)s] - %(levelname)s - %(message)s - %(processName)s",
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 控制台颜色格式化器
    color_formatter = ColoredFormatter(
        "%(green)s%(asctime)s%(reset)s [%(blue)s%(name)s%(reset)s] - "
        "%(log_color)s%(levelname)s%(reset)s - %(green)s%(message)s%(reset)s - "
        "%(cyan)s%(processName)s%(reset)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "white", 
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
        secondary_log_colors={"asctime": {"green": "green"}, "name": {"blue": "blue"}},
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(color_formatter)
    file_handler.setFormatter(formatter)

    # 添加处理器到根日志记录器
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # 输出日志配置信息
    logging.info("日志系统初始化完毕，路径: %s", log_file)

    return log_file


def get_logger(name: str) -> logging.Logger:
    """
    获取统一配置的日志记录器

    Args:
        name: 日志记录器名称，通常是模块名

    Returns:
        logging.Logger: 配置好的日志记录器

    examples:
        logger = get_logger(__name__)
        logger.info("这是一条信息")
        logger.error("出错了: %s", error_msg)
    """
    logger = logging.getLogger(name)

    # 添加一些辅助方法
    def log_error_with_exc(msg, *args, **kwargs):
        """记录错误并自动包含异常堆栈"""
        kwargs["exc_info"] = True
        logger.error(msg, *args, **kwargs)

    # 添加到日志记录器
    setattr(logger, 'error_exc', log_error_with_exc)

    return logger
