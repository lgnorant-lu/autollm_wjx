"""
----------------------------------------------------------------
File name:                  base.py
Author:                     Ignorant-lu
Date created:               2025/04/01
Description:                代理抽象基类，定义统一的代理接口
----------------------------------------------------------------

Changed history:
                            2025/04/01: 初始创建
----------------------------------------------------------------
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import logging
import requests

logger = logging.getLogger(__name__)

class BaseProxyProvider(ABC):
    """
    代理提供商抽象基类

    定义统一的代理接口，所有具体的代理提供商实现都应继承此类
    """

    def __init__(self, api_key: str = None, **kwargs):
        """
        初始化代理提供商

        Args:
            api_key: API密钥（如果需要）
            **kwargs: 其他参数
        """
        self.api_key = api_key
        self.timeout = kwargs.get('timeout', 10)
        self.max_retries = kwargs.get('max_retries', 3)

        # 初始化提供商特定的配置
        self._init_provider_config(**kwargs)

    @abstractmethod
    def _init_provider_config(self, **kwargs):
        """
        初始化提供商特定的配置

        Args:
            **kwargs: 配置参数
        """
        pass

    @abstractmethod
    def get_proxy(self, **kwargs) -> Dict[str, str]:
        """
        获取代理

        Args:
            **kwargs: 其他参数

        Returns:
            Dict[str, str]: 代理配置，格式为 {'http': 'http://ip:port', 'https': 'http://ip:port'}
        """
        pass

    def get_proxies(self, count: int = 1, **kwargs) -> List[Dict[str, str]]:
        """
        获取多个代理

        Args:
            count: 代理数量
            **kwargs: 其他参数

        Returns:
            List[Dict[str, str]]: 代理配置列表
        """
        # 默认实现，循环调用get_proxy方法
        proxies = []
        for _ in range(count):
            proxy = self.get_proxy(**kwargs)
            if proxy and proxy not in proxies:
                proxies.append(proxy)
        return proxies

    def validate_proxy(self, proxy: Dict[str, str], test_url: str = 'https://www.baidu.com') -> bool:
        """
        验证代理是否可用

        Args:
            proxy: 代理配置
            test_url: 测试URL

        Returns:
            bool: 代理是否可用
        """
        try:
            response = requests.get(
                test_url,
                proxies=proxy,
                timeout=self.timeout
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"代理验证失败: {proxy}, 错误: {str(e)}")
            return False

    def get_current_ip(self, proxy: Dict[str, str] = None) -> Optional[str]:
        """
        获取当前IP

        Args:
            proxy: 代理配置

        Returns:
            str: 当前IP，如果获取失败则返回None
        """
        try:
            response = requests.get(
                'http://httpbin.org/ip',
                proxies=proxy,
                timeout=self.timeout
            )
            if response.status_code == 200:
                return response.json().get('origin')
            return None
        except Exception as e:
            logger.warning(f"获取当前IP失败: {str(e)}")
            return None
