"""
----------------------------------------------------------------
File name:                  llm_generator.py
Author:                     Ignorant-lu
Date created:               2025/02/23
Description:                大语言模型答案生成模块，提供智能问卷填写功能
----------------------------------------------------------------

Changed history:
                            2025/02/25: 添加多模型API支持(OpenAI、智谱、百度、阿里云)
                            2025/03/02: 优化提示词结构和错误处理
                            2025/04/01: 重构为使用LLM抽象接口，添加兔子API和Gemini支持
----------------------------------------------------------------
"""

import json
import os
import logging
from typing import Dict, List, Any, Optional

from .llm import LLMFactory
from .llm.base import BaseLLMProvider

logger = logging.getLogger(__name__)

class LLMGenerator:
    """
    LLM答案生成器

    基于大型语言模型生成问卷答案
    支持多种模型API和自定义提示词
    """

    def __init__(self, model_type="aliyun", api_key=None, **kwargs):
        """
        初始化LLM生成器

        Args:
            model_type: 使用的模型类型，支持 "openai", "zhipu", "baidu", "aliyun", "tuzi", "gemini"
            api_key: API密钥
            **kwargs: 其他参数
        """
        self.model_type = model_type
        self.mock = kwargs.get('mock', False)  # 模拟模式

        # 如果启用了模拟模式，使用模拟的API密钥
        if self.mock:
            self.api_key = api_key or f"mock-{model_type}-api-key"
        else:
            self.api_key = api_key or os.getenv(f"{model_type.upper()}_API_KEY")

        if not self.api_key:
            raise ValueError(f"未提供{model_type}的API密钥，请设置环境变量或直接传入")

        # 创建LLM提供商实例
        kwargs['mock'] = self.mock  # 添加模拟模式参数

        # 处理代理参数，如果存在
        if 'proxy' in kwargs:
            proxy = kwargs.pop('proxy', None)
            if proxy:
                # 将代理参数转换为OpenAI客户端支持的格式
                proxies = {}
                if isinstance(proxy, dict):
                    # 如果是字典格式，直接使用
                    proxies = proxy
                elif isinstance(proxy, str):
                    # 如果是字符串格式，转换为字典
                    proxies = {'http': proxy, 'https': proxy}

                # 对于所有提供商，传递代理参数
                if model_type == 'aliyun':
                    # 阿里云使用OpenAI客户端，需要设置环境变量
                    import os
                    # 设置环境变量代理
                    if isinstance(proxies, dict):
                        http_proxy = proxies.get('http')
                        https_proxy = proxies.get('https')
                        if http_proxy:
                            os.environ['HTTP_PROXY'] = http_proxy
                        if https_proxy:
                            os.environ['HTTPS_PROXY'] = https_proxy
                        logger.info(f"阿里云使用环境变量代理: HTTP_PROXY={http_proxy}, HTTPS_PROXY={https_proxy}")

                    # 不传递代理参数给阿里云提供商
                    # 对于阿里云，不需要在kwargs中设置代理参数
                    # 因为我们已经在环境变量中设置了代理
                    # 删除所有代理相关的参数
                    for key in list(kwargs.keys()):
                        if 'proxy' in key.lower():
                            kwargs.pop(key, None)
                else:
                    # 其他提供商支持代理参数
                    # 在创建LLM提供商实例时会添加代理参数
                    logger.info(f"使用代理初始化LLM: {model_type}, 代理: {proxies}")

        # 创建LLM提供商实例
        try:
            # 输出原始参数信息
            logger.info(f"初始化LLM提供商前的参数: model_type={model_type}, api_key={self.api_key[:5]}...")
            logger.info(f"原始 kwargs 包含的键: {list(kwargs.keys())}")

            # 对于所有提供商，删除所有代理相关的参数
            # 然后根据提供商类型添加适当的代理参数
            kwargs_clean = kwargs.copy()

            # 对于阿里云，不传递任何参数
            if model_type == 'aliyun':
                # 对于阿里云，只传递api_key参数，删除所有其他参数
                kwargs_clean = {}
                logger.info(f"阿里云提供商只使用api_key参数，删除所有其他参数")
            else:
                # 对于其他提供商，删除所有代理相关的参数，然后添加proxies参数
                proxy_keys = []
                for key in list(kwargs_clean.keys()):
                    if 'proxy' in key.lower():
                        proxy_keys.append(key)
                        kwargs_clean.pop(key, None)
                        logger.info(f"删除代理参数: {key}")

                if proxy_keys:
                    logger.info(f"删除了以下代理参数: {', '.join(proxy_keys)}")

                # 添加proxies参数
                if proxies:
                    kwargs_clean['proxies'] = proxies
                    logger.info(f"添加代理参数: proxies={proxies}")

            # 输出清理后的参数信息
            logger.info(f"清理后的 kwargs 包含的键: {list(kwargs_clean.keys())}")

            # 使用清理后的参数创建LLM提供商实例
            logger.info(f"开始创建LLM提供商实例: {model_type}")

            # 对于阿里云，只传递api_key参数
            if model_type == 'aliyun':
                # 对于阿里云，直接导入并创建提供商实例，而不通过LLMFactory
                # 参考官方文档：https://help.aliyun.com/zh/model-studio/first-api-call-to-qwen
                try:
                    # 尝试使用绝对导入
                    from backend.core.llm.providers.aliyun_provider import AliyunProvider
                    # 只传递api_key参数，不传递其他参数
                    # 先清除环境变量中的代理设置
                    import os
                    http_proxy = os.environ.pop('HTTP_PROXY', None)
                    https_proxy = os.environ.pop('HTTPS_PROXY', None)
                    http_proxy_lower = os.environ.pop('http_proxy', None)
                    https_proxy_lower = os.environ.pop('https_proxy', None)

                    # 记录删除的环境变量
                    if http_proxy or https_proxy or http_proxy_lower or https_proxy_lower:
                        logger.info(f"删除环境变量中的代理设置: HTTP_PROXY={http_proxy}, HTTPS_PROXY={https_proxy}, http_proxy={http_proxy_lower}, https_proxy={https_proxy_lower}")

                    # 创建提供商实例
                    self.provider = AliyunProvider(api_key=self.api_key)
                    logger.info(f"直接创建阿里云提供商实例，只使用api_key参数")

                    # 恢复环境变量中的代理设置
                    if http_proxy:
                        os.environ['HTTP_PROXY'] = http_proxy
                    if https_proxy:
                        os.environ['HTTPS_PROXY'] = https_proxy
                    if http_proxy_lower:
                        os.environ['http_proxy'] = http_proxy_lower
                    if https_proxy_lower:
                        os.environ['https_proxy'] = https_proxy_lower
                except Exception as e:
                    # 如果导入失败，尝试使用相对导入
                    logger.warning(f"导入AliyunProvider失败，尝试使用相对导入: {e}")
                    try:
                        # 尝试使用相对导入
                        from core.llm.providers.aliyun_provider import AliyunProvider

                        # 先清除环境变量中的代理设置
                        import os
                        http_proxy = os.environ.pop('HTTP_PROXY', None)
                        https_proxy = os.environ.pop('HTTPS_PROXY', None)
                        http_proxy_lower = os.environ.pop('http_proxy', None)
                        https_proxy_lower = os.environ.pop('https_proxy', None)

                        # 记录删除的环境变量
                        if http_proxy or https_proxy or http_proxy_lower or https_proxy_lower:
                            logger.info(f"删除环境变量中的代理设置: HTTP_PROXY={http_proxy}, HTTPS_PROXY={https_proxy}, http_proxy={http_proxy_lower}, https_proxy={https_proxy_lower}")

                        # 只传递api_key参数，不传递其他参数
                        self.provider = AliyunProvider(api_key=self.api_key)
                        logger.info(f"使用相对导入创建阿里云提供商实例，只使用api_key参数")

                        # 恢复环境变量中的代理设置
                        if http_proxy:
                            os.environ['HTTP_PROXY'] = http_proxy
                        if https_proxy:
                            os.environ['HTTPS_PROXY'] = https_proxy
                        if http_proxy_lower:
                            os.environ['http_proxy'] = http_proxy_lower
                        if https_proxy_lower:
                            os.environ['https_proxy'] = https_proxy_lower
                    except Exception as e2:
                        # 如果两种导入方式都失败，记录错误并抛出异常
                        logger.error(f"导入AliyunProvider失败: {e2}")
                        logger.error(f"异常类型: {type(e2).__name__}")
                        logger.error(f"异常详情: {str(e2)}")
                        raise
            else:
                self.provider = LLMFactory.create(model_type, self.api_key, **kwargs_clean)
            logger.info(f"成功创建LLM提供商实例: {model_type}")

            if not self.provider:
                logger.error(f"创建LLM提供商实例失败: {model_type}, 返回了None")
                raise ValueError(f"创建LLM提供商实例失败: {model_type}")
        except Exception as e:
            logger.error(f"创建LLM提供商实例异常: {e}")
            logger.error(f"异常类型: {type(e).__name__}")
            logger.error(f"异常详情: {str(e)}")
            raise ValueError(f"创建LLM提供商实例失败: {model_type}")

    def generate_answers(self, question_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """为整个问卷生成答案"""
        try:
            logger.info(f"开始使用 {self.model_type} 生成答案")
            logger.info(f"问卷包含 {len(question_data.get('questions', []))} 个问题")

            # 调用提供商生成答案
            answers = self.provider.generate_answers(question_data, **kwargs)
            logger.info(f"成功解析答案, 包含 {len(answers)} 个回答")

            return answers
        except Exception as e:
            logger.error(f"生成答案失败: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def get_available_providers() -> Dict[str, str]:
        """
        获取可用的LLM提供商列表

        Returns:
            Dict[str, str]: 提供商名称和描述的字典
        """
        return LLMFactory.get_available_providers()

    @staticmethod
    def create_provider(provider_name: str, api_key: str, **kwargs) -> Optional[BaseLLMProvider]:
        """
        创建LLM提供商实例

        Args:
            provider_name: 提供商名称
            api_key: API密钥
            **kwargs: 其他参数

        Returns:
            BaseLLMProvider: LLM提供商实例，如果提供商不存在则返回None
        """
        return LLMFactory.create(provider_name, api_key, **kwargs)