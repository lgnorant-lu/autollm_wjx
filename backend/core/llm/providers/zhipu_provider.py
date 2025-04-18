"""
----------------------------------------------------------------
File name:                  zhipu_provider.py
Author:                     Ignorant-lu
Date created:               2025/04/01
Description:                智谱AI LLM提供商实现
----------------------------------------------------------------

Changed history:
                            2025/04/01: 初始创建
----------------------------------------------------------------
"""

import json
import logging
import requests
from typing import Dict, Any
from ..base import BaseLLMProvider
from ..factory import LLMFactory

logger = logging.getLogger(__name__)

class ZhipuProvider(BaseLLMProvider):
    """
    智谱AI LLM提供商

    使用智谱AI API生成文本
    """

    def _init_provider_config(self, **kwargs):
        """
        初始化智谱AI特定的配置

        Args:
            **kwargs: 配置参数
        """
        self.api_base = kwargs.get('api_base', 'https://open.bigmodel.cn/api/paas/v4')
        self.model = self.model or 'glm-4'
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

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
                logger.info(f"[模拟模式] 智谱AI生成文本, 提示词: {prompt[:50]}...")
                return f"[模拟响应] 这是来自智谱AI的模拟响应。提示词: {prompt[:30]}..."

            # 合并默认参数和传入的参数
            temperature = kwargs.get('temperature', self.temperature)
            max_tokens = kwargs.get('max_tokens', self.max_tokens)

            # 构建请求数据
            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens
            }

            # 发送请求
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=self.headers,
                json=data,
                timeout=self.timeout
            )

            # 检查响应状态
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                logger.error(f"智谱AI API错误: {response.status_code}, {response.text}")
                raise Exception(f"智谱AI API错误: {response.status_code}, {response.text}")

        except Exception as e:
            logger.error(f"智谱AI生成失败: {str(e)}")
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
                logger.info(f"[模拟模式] 智谱AI生成JSON, 提示词: {prompt[:50]}...")
                return {
                    "mock": True,
                    "provider": "智谱AI",
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
            logger.error(f"智谱AI生成JSON失败: {str(e)}")
            raise

# 注册提供商
LLMFactory.register_provider('zhipu', ZhipuProvider)
