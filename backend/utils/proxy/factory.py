"""
----------------------------------------------------------------
File name:                  factory.py
Author:                     Ignorant-lu
Date created:               2025/04/01
Description:                代理工厂类，用于创建不同的代理提供商实例
----------------------------------------------------------------

Changed history:            
                            2025/04/01: 初始创建
----------------------------------------------------------------
"""

import logging
from typing import Dict, Type, Any, Optional
from .base import BaseProxyProvider

logger = logging.getLogger(__name__)

class ProxyFactory:
    """
    代理工厂类
    
    用于创建不同的代理提供商实例
    """
    
    # 注册的提供商类
    _providers: Dict[str, Type[BaseProxyProvider]] = {}
    
    @classmethod
    def register_provider(cls, provider_name: str, provider_class: Type[BaseProxyProvider]):
        """
        注册代理提供商
        
        Args:
            provider_name: 提供商名称
            provider_class: 提供商类
        """
        cls._providers[provider_name] = provider_class
        logger.info(f"注册代理提供商: {provider_name}")
        
    @classmethod
    def create(cls, provider_name: str, api_key: str = None, **kwargs) -> Optional[BaseProxyProvider]:
        """
        创建代理提供商实例
        
        Args:
            provider_name: 提供商名称
            api_key: API密钥
            **kwargs: 其他参数
            
        Returns:
            BaseProxyProvider: 代理提供商实例，如果提供商不存在则返回None
        """
        if provider_name not in cls._providers:
            logger.error(f"未知的代理提供商: {provider_name}")
            return None
            
        try:
            provider_class = cls._providers[provider_name]
            return provider_class(api_key=api_key, **kwargs)
        except Exception as e:
            logger.error(f"创建代理提供商实例失败: {str(e)}")
            return None
    
    @classmethod
    def get_available_providers(cls) -> Dict[str, str]:
        """
        获取可用的代理提供商列表
        
        Returns:
            Dict[str, str]: 提供商名称和描述的字典
        """
        return {name: provider.__doc__ for name, provider in cls._providers.items()}
