"""
----------------------------------------------------------------
File name:                  factory.py
Author:                     Ignorant-lu
Date created:               2025/04/01
Description:                LLM工厂类，用于创建不同的LLM提供商实例
----------------------------------------------------------------

Changed history:
                            2025/04/01: 初始创建
----------------------------------------------------------------
"""

import logging
from typing import Dict, Type, Any, Optional
from .base import BaseLLMProvider

logger = logging.getLogger(__name__)

class LLMFactory:
    """
    LLM工厂类

    用于创建不同的LLM提供商实例
    """

    # 注册的提供商类
    _providers: Dict[str, Type[BaseLLMProvider]] = {}

    @classmethod
    def register_provider(cls, provider_name: str, provider_class: Type[BaseLLMProvider]):
        """
        注册LLM提供商

        Args:
            provider_name: 提供商名称
            provider_class: 提供商类
        """
        cls._providers[provider_name] = provider_class
        logger.info(f"注册LLM提供商: {provider_name}")

    @classmethod
    def create(cls, provider_name: str, api_key: str, **kwargs) -> Optional[BaseLLMProvider]:
        """
        创建LLM提供商实例

        Args:
            provider_name: 提供商名称
            api_key: API密钥
            **kwargs: 其他参数

        Returns:
            BaseLLMProvider: LLM提供商实例，如果提供商不存在则返回None
        """
        if provider_name not in cls._providers:
            logger.error(f"未知的LLM提供商: {provider_name}")
            return None

        try:
            provider_class = cls._providers[provider_name]

            # 输出原始参数信息
            logger.info(f"LLMFactory.create 参数: provider_name={provider_name}, api_key={api_key[:5]}...")
            logger.info(f"LLMFactory.create 原始 kwargs 包含的键: {list(kwargs.keys())}")

            # 对于所有提供商，先复制参数
            kwargs_copy = kwargs.copy()

            # 对于阿里云提供商，删除所有代理相关的参数
            if provider_name == 'aliyun':
                # 对于阿里云，只传递api_key参数，删除所有其他参数
                kwargs_copy = {}
                logger.info(f"阿里云提供商只使用api_key参数，删除所有其他参数")

            # 输出清理后的参数信息
            logger.info(f"LLMFactory.create 清理后的 kwargs 包含的键: {list(kwargs_copy.keys())}")

            # 使用处理后的kwargs_copy
            logger.info(f"开始初始化提供商类: {provider_class.__name__}")
            provider = provider_class(api_key=api_key, **kwargs_copy)
            logger.info(f"成功初始化提供商类: {provider_class.__name__}")
            return provider
        except Exception as e:
            logger.error(f"创建LLM提供商实例失败: {str(e)}")
            return None

    @classmethod
    def get_available_providers(cls) -> Dict[str, str]:
        """
        获取可用的LLM提供商列表

        Returns:
            Dict[str, str]: 提供商名称和描述的字典
        """
        return {name: provider.__doc__ for name, provider in cls._providers.items()}
