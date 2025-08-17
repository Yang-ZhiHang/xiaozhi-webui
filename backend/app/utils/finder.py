from typing import Optional
from ..constants import WORK_DIR
import os
from .logger import get_logger

logger = get_logger(__name__)

def find_libs_dir(system: str = "", arch: str = "") -> Optional[str]:
        """查找libs目录（用于动态库）

        Args:
            system: 系统名称（如Windows、Linux、Darwin）
            arch: 架构名称（如x64、x86、arm64）

        Returns:
            找到的libs目录绝对路径，未找到返回None
        """
        # 基础libs目录
        libs_dir = os.path.join(WORK_DIR, "libs")
        if not os.path.exists(libs_dir):
            logger.error(f"未找到libs目录: {libs_dir}")
            return None

        # 如果指定了系统和架构，查找具体的子目录
        if system and arch:
            specific_dir = os.path.join(libs_dir, system, arch)
            logger.info(f"spec: {specific_dir}")
            if os.path.isdir(specific_dir):
                return specific_dir
        elif system:
            system_dir = os.path.join(libs_dir, system)
            if os.path.isdir(system_dir):
                return system_dir

        return libs_dir