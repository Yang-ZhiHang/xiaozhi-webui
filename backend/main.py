from urllib.parse import urlparse
from app.utils.logger import get_logger, setup_logging
from app.utils.system_info import setup_opus

setup_logging()
setup_opus()  # 在导入 opuslib 之前 windows 需要手动加载 opus.dll 动态链接库

logger = get_logger(__name__)


if __name__ == "__main__":
    import atexit
    import signal
    import sys
    import multiprocessing
    import uvicorn

    from app import create_app
    from app.config import ConfigManager
    from app.proxy.process_handler import run_proxy, cleanup

    proxy_process = None
    app = create_app()
    configuration = ConfigManager()

    # 信号处理函数
    def signal_handler(signum, frame):
        logger.info(f"收到信号 {signum}，开始优雅关闭...")
        cleanup(proxy_process)
        sys.exit(0)

    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 注册退出时的清理函数
    atexit.register(cleanup, proxy_process)

    try:
        # 启动 Proxy 服务器
        proxy_process = multiprocessing.Process(target=run_proxy, name="ProxyProcess")
        proxy_process.start()
        logger.info(
            f"代理服务器已启动: {configuration.get('WS_PROXY_URL')}, PID: {proxy_process.pid}"
        )

        # 启动 FastAPI 服务器
        BACKEND_URL = str(configuration.get("BACKEND_URL"))
        parsed_url = urlparse(BACKEND_URL)
        BACKEND_HOST = parsed_url.hostname
        BACKEND_PORT = parsed_url.port
        
        if BACKEND_HOST is None or BACKEND_PORT is None:
            logger.error(f"无效的 BACKEND_URL: {BACKEND_URL}")
            cleanup(proxy_process)
            exit(1)
            
        logger.info(f"FastAPI 服务器地址: {BACKEND_HOST}:{BACKEND_PORT}")
        uvicorn.run(app, host=BACKEND_HOST, port=BACKEND_PORT)
        
    except KeyboardInterrupt:
        logger.info("主进程收到中断信号")
    except Exception as e:
        logger.error(f"主进程异常: {e}")
    finally:
        cleanup(proxy_process)
        logger.info("所有服务已关闭")
