"""
----------------------------------------------------------------
File name:                  tuzi_provider.py
Author:                     Ignorant-lu
Date created:               2025/04/01
Description:                兔子API LLM提供商实现
----------------------------------------------------------------

Changed history:            
                            2025/04/01: 初始创建
----------------------------------------------------------------
"""

import json
import logging
import requests
from typing import Dict, Any, List, Optional
from ..base import BaseLLMProvider
from ..factory import LLMFactory

logger = logging.getLogger(__name__)

class TuziProvider(BaseLLMProvider):
    """
    兔子API LLM提供商
    
    使用兔子API生成文本，参考文档：https://wiki.tu-zi.com/zh/Code/python
    """
    
    def _init_provider_config(self, **kwargs):
        """
        初始化兔子API特定的配置
        
        Args:
            **kwargs: 配置参数
        """
        self.api_base = kwargs.get('api_base', 'https://api.tu-zi.com/v1')
        self.model = self.model or 'gpt-3.5-turbo'
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
                logger.error(f"兔子API错误: {response.status_code}, {response.text}")
                raise Exception(f"兔子API错误: {response.status_code}, {response.text}")
                
        except Exception as e:
            logger.error(f"兔子API生成失败: {str(e)}")
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
            logger.error(f"兔子API生成JSON失败: {str(e)}")
            raise

# 注册提供商
LLMFactory.register_provider('tuzi', TuziProvider)
