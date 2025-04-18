"""
----------------------------------------------------------------
File name:                  api_source.py
Author:                     Ignorant-lu
Date created:               2025/04/01
Description:                API代理源实现
----------------------------------------------------------------

Changed history:            
                            2025/04/01: 初始创建
----------------------------------------------------------------
"""

import logging
import requests
import json
import time
import random
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class APIProxySource:
    """
    API代理源
    
    从API获取代理
    """
    
    def __init__(self, api_url: str, **kwargs):
        """
        初始化API代理源
        
        Args:
            api_url: API URL
            **kwargs: 其他参数
        """
        self.api_url = api_url
        self.api_key = kwargs.get('api_key', '')
        self.timeout = kwargs.get('timeout', 10)
        self.max_retries = kwargs.get('max_retries', 3)
        self.cache_time = kwargs.get('cache_time', 300)  # 缓存时间（秒）
        self.params = kwargs.get('params', {})
        self.headers = kwargs.get('headers', {})
        
        # 缓存
        self.cache = []
        self.last_fetch_time = 0
        
    def get_proxy(self) -> Optional[Dict[str, str]]:
        """
        获取代理
        
        随机选择一个代理
        
        Returns:
            Dict[str, str]: 代理配置，如果没有可用代理则返回None
        """
        # 确保缓存已填充
        self._ensure_cache_filled()
        
        # 如果缓存为空，返回None
        if not self.cache:
            logger.warning("代理缓存为空，无法获取代理")
            return None
            
        # 随机选择一个代理
        return random.choice(self.cache)
        
    def get_proxies(self, count: int = 1) -> List[Dict[str, str]]:
        """
        获取多个代理
        
        随机选择多个代理
        
        Args:
            count: 代理数量
            
        Returns:
            List[Dict[str, str]]: 代理配置列表
        """
        # 确保缓存已填充
        self._ensure_cache_filled()
        
        # 如果缓存为空，返回空列表
        if not self.cache:
            logger.warning("代理缓存为空，无法获取代理")
            return []
            
        # 随机选择多个代理
        if len(self.cache) <= count:
            return self.cache.copy()
        else:
            return random.sample(self.cache, count)
            
    def _ensure_cache_filled(self):
        """
        确保缓存已填充
        
        如果缓存为空或已过期，则重新填充
        """
        current_time = time.time()
        if not self.cache or current_time - self.last_fetch_time > self.cache_time:
            logger.debug("填充代理缓存")
            self._fill_cache()
            self.last_fetch_time = current_time
            
    def _fill_cache(self):
        """
        填充缓存
        
        从API获取代理
        """
        try:
            # 构建请求参数
            params = self.params.copy()
            if self.api_key:
                params['api_key'] = self.api_key
                
            # 构建请求头
            headers = self.headers.copy()
            
            # 发送请求
            for retry in range(self.max_retries):
                try:
                    response = requests.get(
                        self.api_url,
                        params=params,
                        headers=headers,
                        timeout=self.timeout
                    )
                    
                    # 检查响应状态
                    if response.status_code == 200:
                        # 尝试解析JSON
                        try:
                            data = response.json()
                            self._parse_json_response(data)
                            break
                        except json.JSONDecodeError:
                            # 如果不是JSON，尝试解析文本
                            self._parse_text_response(response.text)
                            break
                    else:
                        logger.warning(f"API请求失败: {response.status_code}, {response.text}")
                        time.sleep(1)
                except Exception as e:
                    logger.warning(f"API请求异常: {str(e)}")
                    time.sleep(1)
                    
            logger.info(f"从API加载了 {len(self.cache)} 个代理")
                
        except Exception as e:
            logger.error(f"从API加载代理失败: {str(e)}")
            
    def _parse_json_response(self, data: Dict[str, Any]):
        """
        解析JSON响应
        
        Args:
            data: JSON数据
        """
        # 清空缓存
        self.cache = []
        
        # 尝试不同的JSON格式
        if isinstance(data, list):
            # 如果是列表，尝试解析每个元素
            for item in data:
                if isinstance(item, dict):
                    # 尝试常见的字段名
                    ip = item.get('ip') or item.get('host') or item.get('addr')
                    port = item.get('port')
                    
                    if ip and port:
                        proxy = {
                            'http': f'http://{ip}:{port}',
                            'https': f'http://{ip}:{port}'
                        }
                        self.cache.append(proxy)
                elif isinstance(item, str):
                    # 如果是字符串，尝试解析为 ip:port 格式
                    parts = item.split(':')
                    if len(parts) >= 2:
                        ip = parts[0]
                        port = parts[1]
                        proxy = {
                            'http': f'http://{ip}:{port}',
                            'https': f'http://{ip}:{port}'
                        }
                        self.cache.append(proxy)
        elif isinstance(data, dict):
            # 如果是字典，尝试解析常见的结构
            if 'data' in data and isinstance(data['data'], list):
                # 如果有data字段且为列表，递归解析
                self._parse_json_response(data['data'])
            elif 'proxies' in data and isinstance(data['proxies'], list):
                # 如果有proxies字段且为列表，递归解析
                self._parse_json_response(data['proxies'])
            elif 'result' in data and isinstance(data['result'], list):
                # 如果有result字段且为列表，递归解析
                self._parse_json_response(data['result'])
            else:
                # 尝试常见的字段名
                ip = data.get('ip') or data.get('host') or data.get('addr')
                port = data.get('port')
                
                if ip and port:
                    proxy = {
                        'http': f'http://{ip}:{port}',
                        'https': f'http://{ip}:{port}'
                    }
                    self.cache.append(proxy)
                    
    def _parse_text_response(self, text: str):
        """
        解析文本响应
        
        Args:
            text: 文本数据
        """
        # 清空缓存
        self.cache = []
        
        # 按行分割
        lines = text.splitlines()
        
        for line in lines:
            line = line.strip()
            if line:
                # 尝试解析为 ip:port 格式
                parts = line.split(':')
                if len(parts) >= 2:
                    ip = parts[0]
                    port = parts[1]
                    proxy = {
                        'http': f'http://{ip}:{port}',
                        'https': f'http://{ip}:{port}'
                    }
                    self.cache.append(proxy)
                    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        return {
            'total_proxies': len(self.cache),
            'api_url': self.api_url,
            'last_fetch_time': self.last_fetch_time
        }
