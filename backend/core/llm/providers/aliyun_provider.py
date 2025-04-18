"""
----------------------------------------------------------------
File name:                  aliyun_provider.py
Author:                     Ignorant-lu
Date created:               2025/04/01
Description:                阿里云百炼 LLM提供商实现
----------------------------------------------------------------

Changed history:
                            2025/04/01: 初始创建
----------------------------------------------------------------
"""

import json
import logging
from typing import Dict, Any
from openai import OpenAI
from ..base import BaseLLMProvider
from ..factory import LLMFactory

logger = logging.getLogger(__name__)

class AliyunProvider(BaseLLMProvider):
    """
    阿里云百炼 LLM提供商

    使用阿里云百炼 API生成文本
    """

    def _init_provider_config(self, **kwargs):
        """
        初始化阿里云百炼特定的配置

        Args:
            **kwargs: 配置参数
        """
        # 设置默认API基础URL，使用OpenAI兼容模式
        # 参考官方文档：https://help.aliyun.com/zh/model-studio/first-api-call-to-qwen
        self.api_base = kwargs.get('api_base', 'https://dashscope.aliyuncs.com/compatible-mode/v1')

        # 设置默认模型，可用模型包括：qwen-turbo，qwen-plus，qwen-max，qwen-max-1201，qwen-max-longcontext
        self.model = self.model or 'qwen-turbo'

        # 记录模型和API基础URL
        logger.info(f"使用阿里云通义千问模型: {self.model}, API基础URL: {self.api_base}")

        # 输出原始参数信息
        logger.info(f"AliyunProvider.__init__ 参数: api_key={self.api_key[:5]}...")
        logger.info(f"AliyunProvider.__init__ 原始 kwargs 包含的键: {list(kwargs.keys())}")

        # 处理代理参数，但不传递给OpenAI客户端
        # 在LLMFactory中已经删除了代理参数，这里不需要再处理
        # 但为了兼容性，仍然保留这部分代码
        self.proxies = None

        # 如果还有代理相关的参数，删除它们
        proxy_keys = []
        for key in list(kwargs.keys()):
            if 'proxy' in key.lower():
                value = kwargs.pop(key, None)
                proxy_keys.append(key)
                logger.info(f"删除代理参数: {key}={value}")

        if proxy_keys:
            logger.warning(f"阿里云提供商不支持代理参数，已删除: {', '.join(proxy_keys)}")

        # 输出清理后的参数信息
        logger.info(f"AliyunProvider.__init__ 清理后的 kwargs 包含的键: {list(kwargs.keys())}")

        # 初始化OpenAI客户端
        try:
            # 注意：OpenAI客户端不支持proxies参数，需要在环境变量中设置
            # 如果需要使用代理，请设置环境变量 HTTP_PROXY 和 HTTPS_PROXY
            logger.info(f"开始初始化OpenAI客户端: api_key={self.api_key[:5]}..., base_url={self.api_base}")

            # 检查环境变量中的代理设置
            # 注意：环境变量中的代理设置已经在LLMGenerator中删除，这里不需要再删除
            # 但为了兼容性，仍然检查环境变量中的代理设置
            import os
            http_proxy = os.environ.get('HTTP_PROXY')
            https_proxy = os.environ.get('HTTPS_PROXY')
            http_proxy_lower = os.environ.get('http_proxy')
            https_proxy_lower = os.environ.get('https_proxy')

            # 记录环境变量中的代理设置
            if http_proxy or https_proxy or http_proxy_lower or https_proxy_lower:
                logger.info(f"环境变量中的代理设置: HTTP_PROXY={http_proxy}, HTTPS_PROXY={https_proxy}, http_proxy={http_proxy_lower}, https_proxy={https_proxy_lower}")

            # 初始化参数
            # 注意：只传递api_key和base_url参数，不传递其他参数
            logger.info(f"OpenAI客户端初始化参数: api_key={self.api_key[:5]}..., base_url={self.api_base}")

            # 使用最简单的方式初始化OpenAI客户端
            # 直接使用构造函数，只传递必要的参数
            # 先尝试使用最简单的方式
            try:
                # 使用最简单的方式初始化OpenAI客户端
                import httpx
                # 创建HTTPX客户端，不使用代理
                http_client = httpx.Client()
                # 初始化OpenAI客户端，使用自定义的HTTP客户端
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.api_base,
                    http_client=http_client
                )
            except Exception as e:
                logger.warning(f"使用自定义HTTP客户端初始化OpenAI失败: {e}")
                # 如果失败，尝试使用最简单的方式
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.api_base
                )

            # 注意：环境变量中的代理设置已经在LLMGenerator中删除和恢复，这里不需要再恢复
            logger.info(f"成功初始化阿里云客户端")
        except Exception as e:
            logger.error(f"初始化阿里云客户端失败: {e}")
            logger.error(f"异常类型: {type(e).__name__}")
            logger.error(f"异常详情: {str(e)}")
            raise

    def generate(self, prompt: str, **kwargs) -> str:
        """
        生成文本

        Args:
            prompt: 提示词
            **kwargs: 其他参数

        Returns:
            str: 生成的文本
        """
        try:
            # 如果启用了模拟模式，返回模拟响应
            if self.mock:
                logger.info(f"[模拟模式] 阿里云生成文本, 提示词: {prompt[:50]}...")
                return f"[模拟响应] 这是来自阿里云的模拟响应。提示词: {prompt[:30]}..."

            # 合并默认参数和传入的参数
            temperature = kwargs.get('temperature', self.temperature)
            max_tokens = kwargs.get('max_tokens', self.max_tokens)

            # 构建系统提示词
            system_prompt = kwargs.get('system_prompt', "你是一个专业的问卷填写助手，请帮助用户填写问卷。")

            # 调用API
            # 参考官方文档：https://help.aliyun.com/zh/model-studio/first-api-call-to-qwen
            logger.info(f"调用阿里云通义千问API: 模型={self.model}, 温度={temperature}, 最大输出长度={max_tokens}")
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            logger.info(f"阿里云通义千问API调用成功")

            # 获取生成的内容
            return completion.choices[0].message.content

        except Exception as e:
            logger.error(f"阿里云生成失败: {str(e)}")
            raise

    def generate_json(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        生成JSON格式的响应

        Args:
            prompt: 提示词
            **kwargs: 其他参数

        Returns:
            Dict[str, Any]: 生成的JSON数据
        """
        try:
            # 如果启用了模拟模式，返回模拟响应
            if self.mock:
                logger.info(f"[模拟模式] 阿里云生成JSON, 提示词: {prompt[:50]}...")
                return {
                    "mock": True,
                    "provider": "阿里云",
                    "prompt": prompt[:50] + "...",
                    "answers": [
                        {"idx": "1", "value": "模拟答案值1"},
                        {"idx": "2", "value": "模拟答案值2"},
                        {"idx": "3", "value": "模拟答案值3"}
                    ]
                }

            # 添加JSON格式要求
            json_prompt = prompt + "\n请确保返回的是有效的JSON格式。"

            # 生成文本
            response_text = self.generate(json_prompt, **kwargs)

            # 尝试解析JSON
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                # 如果解析失败，尝试从文本中提取JSON部分
                import re
                json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(1))

                # 如果仍然失败，尝试从文本中提取花括号内的内容
                json_match = re.search(r'{.*}', response_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0))

                # 如果所有尝试都失败，抛出异常
                raise ValueError("无法从响应中解析JSON")

        except Exception as e:
            logger.error(f"阿里云生成JSON失败: {str(e)}")
            raise

# 注册提供商
LLMFactory.register_provider('aliyun', AliyunProvider)
