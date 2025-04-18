"""
----------------------------------------------------------------
File name:                  env_loader.py
Author:                     Ignorant-lu
Date created:               2025/04/02
Description:                环境变量加载工具
----------------------------------------------------------------

Changed history:
                            2025/04/02: 初始创建
----------------------------------------------------------------
"""

import os
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class EnvLoader:
    """
    环境变量加载工具

    从.env文件加载环境变量
    """

    @staticmethod
    def load_env(env_file: str = '.env') -> bool:
        """
        从.env文件加载环境变量

        Args:
            env_file: .env文件路径

        Returns:
            bool: 是否成功加载
        """
        try:
            # 尝试多个可能的环境变量文件路径
            env_paths = [
                # 尝试.env文件
                Path(env_file),  # 当前目录
                Path(os.path.join(os.path.dirname(os.path.dirname(__file__)), env_file)),  # backend目录
                Path(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), env_file)),  # 项目根目录
            ]

            loaded = False

            # 尝试每个路径
            for env_path in env_paths:
                if env_path.exists():
                    # 读取.env文件
                    with open(env_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()

                            # 跳过空行和注释
                            if not line or line.startswith('#'):
                                continue

                            # 解析环境变量
                            if '=' in line:
                                key, value = line.split('=', 1)
                                key = key.strip()
                                value = value.strip().strip('"').strip("'")

                                # 设置环境变量
                                os.environ[key] = value
                                logger.debug(f"设置环境变量: {key}={value}")

                    logger.info(f"从文件加载环境变量: {env_path}")
                    loaded = True
                    break

            # 如果没有找到环境变量文件，尝试设置默认值
            if not loaded:
                logger.warning(f"未找到环境变量文件，将使用默认值")

                # 设置默认的LLM API密钥
                if not os.environ.get('ALIYUN_API_KEY'):
                    os.environ['ALIYUN_API_KEY'] = "sk-5662a97464e1404d8c6a06c68520abf6"
                    logger.info("设置默认阿里云API密钥")

                # 设置默认的品赞API URL
                if not os.environ.get('PINZAN_API_URL'):
                    os.environ['PINZAN_API_URL'] = "https://service.ipzan.com/core-extract?num=1&no=20250216408295864496&minute=1&format=json&repeat=1&protocol=1&pool=ordinary&mode=auth&secret=v5eomjhvanppt08"
                    logger.info("设置默认品赞API URL")

            # 输出当前环境变量
            logger.info(f"当前环境变量: ALIYUN_API_KEY={os.environ.get('ALIYUN_API_KEY', '')[:5]}..., PINZAN_API_URL={os.environ.get('PINZAN_API_URL', '')[:20]}...")

            return True

        except Exception as e:
            logger.error(f"加载环境变量失败: {str(e)}")
            return False

    @staticmethod
    def get_env(key: str, default: str = '') -> str:
        """
        获取环境变量

        Args:
            key: 环境变量名
            default: 默认值

        Returns:
            str: 环境变量值
        """
        return os.environ.get(key, default)

    @staticmethod
    def get_env_dict(prefix: str = '') -> Dict[str, str]:
        """
        获取指定前缀的所有环境变量

        Args:
            prefix: 环境变量前缀

        Returns:
            Dict[str, str]: 环境变量字典
        """
        env_dict = {}

        for key, value in os.environ.items():
            if not prefix or key.startswith(prefix):
                env_dict[key] = value

        return env_dict
