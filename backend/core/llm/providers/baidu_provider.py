"""
----------------------------------------------------------------
File name:                  baidu_provider.py
Author:                     Ignorant-lu
Date created:               2025/04/01
Description:                百度文心一言 LLM提供商实现
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

class BaiduProvider(BaseLLMProvider):
    """
    百度文心一言 LLM提供商
    
    使用百度文心一言 API生成文本
    """
    
    def _init_provider_config(self, **kwargs):
        """
        初始化百度文心一言特定的配置
        
        Args:
            **kwargs: 配置参数
        """
        self.api_base = kwargs.get('api_base', 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat')
        self.model = self.model or 'completions'
        
        # 解析API密钥（格式：API_KEY:SECRET_KEY）
        if ':' in self.api_key:
            self.api_key, self.secret_key = self.api_key.split(':', 1)
        else:
            self.secret_key = kwargs.get('secret_key', '')
            
        # 获取访问令牌
        self.access_token = None
        
    def _get_access_token(self) -> str:
        """
        获取百度API访问令牌
        
        Returns:
            str: 访问令牌
        """
        if self.access_token:
            return self.access_token
            
        url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={self.api_key}&client_secret={self.secret_key}"
        
        response = requests.get(url, timeout=self.timeout)
        
        if response.status_code == 200:
            self.access_token = response.json()["access_token"]
            return self.access_token
        else:
            raise Exception(f"获取百度访问令牌失败: {response.status_code}, {response.text}")
        
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
            # 获取访问令牌
            access_token = self._get_access_token()
            
            # 合并默认参数和传入的参数
            temperature = kwargs.get('temperature', self.temperature)
            
            # 构建请求数据
            data = {
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature
            }
            
            # 发送请求
            response = requests.post(
                f"{self.api_base}/{self.model}?access_token={access_token}",
                headers={"Content-Type": "application/json"},
                json=data,
                timeout=self.timeout
            )
            
            # 检查响应状态
            if response.status_code == 200:
                return response.json()["result"]
            else:
                logger.error(f"百度API错误: {response.status_code}, {response.text}")
                raise Exception(f"百度API错误: {response.status_code}, {response.text}")
                
        except Exception as e:
            logger.error(f"百度生成失败: {str(e)}")
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
            logger.error(f"百度生成JSON失败: {str(e)}")
            raise

# 注册提供商
LLMFactory.register_provider('baidu', BaiduProvider)
