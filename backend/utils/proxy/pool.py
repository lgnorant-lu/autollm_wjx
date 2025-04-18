"""
----------------------------------------------------------------
File name:                  pool.py
Author:                     Ignorant-lu
Date created:               2025/04/01
Description:                代理池管理类，管理多个代理
----------------------------------------------------------------

Changed history:
                            2025/04/01: 初始创建
----------------------------------------------------------------
"""

import logging
import random
from typing import Dict, List, Any, Optional
from .base import BaseProxyProvider

logger = logging.getLogger(__name__)

class ProxyPool:
    """
    代理池管理类

    管理多个代理，支持轮询、随机等轮换策略
    """

    def __init__(self, providers: List[BaseProxyProvider] = None, **kwargs):
        """
        初始化代理池

        Args:
            providers: 代理提供商列表
            **kwargs: 其他参数
        """
        self.providers = providers or []
        self.proxies = []
        self.current_index = 0
        self.rotation_strategy = kwargs.get('rotation_strategy', 'round_robin')
        self.test_url = kwargs.get('test_url', 'https://www.baidu.com')

    def add_provider(self, provider: BaseProxyProvider):
        """
        添加代理提供商

        Args:
            provider: 代理提供商
        """
        self.providers.append(provider)
        logger.info(f"添加代理提供商: {provider.__class__.__name__}")

    def remove_provider(self, provider: BaseProxyProvider):
        """
        移除代理提供商

        Args:
            provider: 代理提供商
        """
        if provider in self.providers:
            self.providers.remove(provider)
            logger.info(f"移除代理提供商: {provider.__class__.__name__}")

    def add_proxy(self, proxy: Dict[str, str]):
        """
        添加代理

        Args:
            proxy: 代理配置
        """
        if proxy not in self.proxies:
            self.proxies.append(proxy)
            logger.debug(f"添加代理: {proxy}")

    def remove_proxy(self, proxy: Dict[str, str]):
        """
        移除代理

        Args:
            proxy: 代理配置
        """
        if proxy in self.proxies:
            self.proxies.remove(proxy)
            logger.debug(f"移除代理: {proxy}")

    def get_proxy(self) -> Optional[Dict[str, str]]:
        """
        获取代理

        根据轮换策略获取代理

        Returns:
            Dict[str, str]: 代理配置，如果没有可用代理则返回None
        """
        # 如果代理池为空，尝试直接从提供商获取
        if not self.proxies and self.providers:
            for provider in self.providers:
                try:
                    proxy = provider.get_proxy()
                    if proxy:
                        return proxy
                except Exception as e:
                    logger.error(f"从提供商获取代理失败: {provider.__class__.__name__}, 错误: {str(e)}")

            # 如果所有提供商都无法获取代理，尝试填充代理池
            self.fill_pool()

        # 如果仍然为空，返回None
        if not self.proxies:
            logger.warning("代理池为空，无法获取代理")
            return None

        # 根据轮换策略获取代理
        if self.rotation_strategy == 'round_robin':
            proxy = self._get_proxy_round_robin()
        elif self.rotation_strategy == 'random':
            proxy = self._get_proxy_random()
        else:
            logger.warning(f"未知的轮换策略: {self.rotation_strategy}，使用轮询策略")
            proxy = self._get_proxy_round_robin()

        return proxy

    def _get_proxy_round_robin(self) -> Dict[str, str]:
        """
        轮询策略获取代理

        Returns:
            Dict[str, str]: 代理配置
        """
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return proxy

    def _get_proxy_random(self) -> Dict[str, str]:
        """
        随机策略获取代理

        Returns:
            Dict[str, str]: 代理配置
        """
        return random.choice(self.proxies)

    def fill_pool(self):
        """
        填充代理池

        从所有提供商获取代理
        """
        logger.info("填充代理池")

        # 如果没有提供商，无法填充
        if not self.providers:
            logger.warning("没有代理提供商，无法填充代理池")
            return

        # 从每个提供商获取代理
        for provider in self.providers:
            try:
                proxy = provider.get_proxy()
                if proxy:
                    self.add_proxy(proxy)
            except Exception as e:
                logger.error(f"从提供商获取代理失败: {provider.__class__.__name__}, 错误: {str(e)}")

        logger.info(f"代理池填充完成，当前代理数量: {len(self.proxies)}")

    def validate_all(self):
        """
        验证所有代理是否可用

        移除不可用的代理
        """
        logger.info("验证所有代理")

        valid_proxies = []
        for proxy in self.proxies:
            # 随机选择一个提供商进行验证
            provider = random.choice(self.providers) if self.providers else None
            if provider and provider.validate_proxy(proxy, self.test_url):
                valid_proxies.append(proxy)
            else:
                logger.debug(f"代理不可用，移除: {proxy}")

        self.proxies = valid_proxies
        logger.info(f"代理验证完成，当前可用代理数量: {len(self.proxies)}")

        # 如果没有可用代理，填充代理池
        if not self.proxies:
            logger.info("没有可用代理，填充代理池")
            self.fill_pool()

    def get_stats(self) -> Dict[str, Any]:
        """
        获取代理池统计信息

        Returns:
            Dict[str, Any]: 统计信息
        """
        return {
            'total_proxies': len(self.proxies),
            'providers': [provider.__class__.__name__ for provider in self.providers],
            'rotation_strategy': self.rotation_strategy
        }
