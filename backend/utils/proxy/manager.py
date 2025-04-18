"""
----------------------------------------------------------------
File name:                  manager.py
Author:                     Ignorant-lu
Date created:               2025/04/01
Description:                代理管理器，统一管理代理
----------------------------------------------------------------

Changed history:
                            2025/04/01: 初始创建
----------------------------------------------------------------
"""

import logging
import os
import json
import time
from typing import Dict, List, Any, Optional
from .pool import ProxyPool
from .factory import ProxyFactory
from .base import BaseProxyProvider
from ..env_loader import EnvLoader

logger = logging.getLogger(__name__)

class ProxyManager:
    """
    代理管理器

    统一管理代理，支持多种代理源和轮换策略
    """

    def __init__(self, config_file: str = None, env_file: str = '.env', **kwargs):
        """
        初始化代理管理器

        Args:
            config_file: 配置文件路径
            env_file: 环境变量文件路径
            **kwargs: 其他参数
        """
        # 加载环境变量
        EnvLoader.load_env(env_file)

        self.config_file = config_file
        self.config = {}
        self.pool = ProxyPool(**kwargs)
        self.enabled = kwargs.get('enabled', True)

        # 加载配置
        if config_file:
            self.load_config()

    def load_config(self):
        """
        加载配置

        从配置文件加载配置
        """
        try:
            if not self.config_file or not os.path.exists(self.config_file):
                logger.warning(f"配置文件不存在: {self.config_file}")
                return

            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)

            # 设置启用状态
            self.enabled = self.config.get('enabled', True)

            # 设置轮换策略
            rotation_strategy = self.config.get('rotation_strategy', 'round_robin')
            self.pool.rotation_strategy = rotation_strategy

            # 加载提供商
            providers = self.config.get('providers', [])
            for provider_config in providers:
                provider_type = provider_config.get('type')
                if not provider_type:
                    logger.warning("提供商配置缺少type字段")
                    continue

                # 创建提供商
                provider = self._create_provider(provider_config)
                if provider:
                    self.pool.add_provider(provider)

            logger.info(f"从配置文件加载了 {len(self.pool.providers)} 个代理提供商")

        except Exception as e:
            logger.error(f"加载配置失败: {str(e)}")

    def save_config(self):
        """
        保存配置

        将配置保存到配置文件
        """
        try:
            if not self.config_file:
                logger.warning("未指定配置文件路径")
                return

            # 更新配置
            self.config['enabled'] = self.enabled
            self.config['rotation_strategy'] = self.pool.rotation_strategy

            # 创建目录
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)

            # 保存配置
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)

            logger.info(f"保存配置到文件: {self.config_file}")

        except Exception as e:
            logger.error(f"保存配置失败: {str(e)}")

    def _create_provider(self, config: Dict[str, Any]) -> Optional[BaseProxyProvider]:
        """
        创建代理提供商

        Args:
            config: 提供商配置

        Returns:
            BaseProxyProvider: 代理提供商实例，如果创建失败则返回None
        """
        try:
            provider_type = config.get('type')
            api_key = config.get('api_key', '')

            # 创建提供商
            provider = ProxyFactory.create(provider_type, api_key, **config)

            return provider

        except Exception as e:
            logger.error(f"创建代理提供商失败: {str(e)}")
            return None

    def add_provider(self, provider_type: str, api_key: str = None, **kwargs):
        """
        添加代理提供商

        Args:
            provider_type: 提供商类型
            api_key: API密钥
            **kwargs: 其他参数
        """
        try:
            # 创建提供商
            provider = ProxyFactory.create(provider_type, api_key, **kwargs)
            if provider:
                self.pool.add_provider(provider)

                # 更新配置
                if 'providers' not in self.config:
                    self.config['providers'] = []

                provider_config = {
                    'type': provider_type,
                    'api_key': api_key,
                    **kwargs
                }
                self.config['providers'].append(provider_config)

                # 保存配置
                self.save_config()

                logger.info(f"添加代理提供商: {provider_type}")
            else:
                logger.error(f"创建代理提供商失败: {provider_type}")

        except Exception as e:
            logger.error(f"添加代理提供商失败: {str(e)}")

    def remove_provider(self, provider_type: str):
        """
        移除代理提供商

        Args:
            provider_type: 提供商类型
        """
        try:
            # 移除提供商
            for provider in self.pool.providers:
                if provider.__class__.__name__ == f"{provider_type.capitalize()}Provider":
                    self.pool.remove_provider(provider)

                    # 更新配置
                    if 'providers' in self.config:
                        self.config['providers'] = [p for p in self.config['providers'] if p.get('type') != provider_type]

                    # 保存配置
                    self.save_config()

                    logger.info(f"移除代理提供商: {provider_type}")
                    break

        except Exception as e:
            logger.error(f"移除代理提供商失败: {str(e)}")

    def get_proxy(self) -> Optional[Dict[str, str]]:
        """
        获取代理

        如果启用了代理，则从代理池获取代理，否则返回None

        Returns:
            Dict[str, str]: 代理配置，如果未启用代理或没有可用代理则返回None
        """
        if not self.enabled:
            logger.debug("代理未启用")
            return None

        return self.pool.get_proxy()

    def validate_proxy(self, proxy: Dict[str, str], test_url: str = 'https://www.baidu.com') -> bool:
        """
        验证代理是否可用

        Args:
            proxy: 代理配置
            test_url: 测试URL

        Returns:
            bool: 代理是否可用
        """
        # 随机选择一个提供商进行验证
        if self.pool.providers:
            provider = self.pool.providers[0]
            return provider.validate_proxy(proxy, test_url)
        return False

    def get_current_ip(self, proxy: Dict[str, str] = None) -> Optional[str]:
        """
        获取当前IP

        Args:
            proxy: 代理配置

        Returns:
            str: 当前IP，如果获取失败则返回None
        """
        # 随机选择一个提供商获取当前IP
        if self.pool.providers:
            provider = self.pool.providers[0]
            return provider.get_current_ip(proxy)
        return None

    def set_enabled(self, enabled: bool):
        """
        设置是否启用代理

        Args:
            enabled: 是否启用
        """
        self.enabled = enabled

        # 更新配置
        self.config['enabled'] = enabled

        # 保存配置
        self.save_config()

        logger.info(f"设置代理启用状态: {enabled}")

    def set_rotation_strategy(self, strategy: str):
        """
        设置轮换策略

        Args:
            strategy: 轮换策略
        """
        self.pool.rotation_strategy = strategy

        # 更新配置
        self.config['rotation_strategy'] = strategy

        # 保存配置
        self.save_config()

        logger.info(f"设置代理轮换策略: {strategy}")

    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息

        Returns:
            Dict[str, Any]: 统计信息
        """
        return {
            'enabled': self.enabled,
            'rotation_strategy': self.pool.rotation_strategy,
            'providers': [provider.__class__.__name__ for provider in self.pool.providers],
            'proxies': len(self.pool.proxies)
        }
