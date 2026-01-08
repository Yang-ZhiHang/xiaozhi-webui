from app.utils.logger import setup_logging
from app.utils.system_info import setup_opus

setup_logging()
setup_opus()  # 在导入 opuslib 之前 windows 需要手动加载 opus.dll 动态链接库

if __name__ == "__main__":
    # import run_proxy 需要在 setup_opus 初始化 opuslib 之后导入
    from app.proxy.process_handler import run_proxy

    run_proxy()
