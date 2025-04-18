"""
----------------------------------------------------------------
File name:                  custom_provider.py
Author:                     Ignorant-lu
Date created:               2025/04/01
Description:                自定义代理提供商实现
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
from ..base import BaseProxyProvider
from ..factory import ProxyFactory

logger = logging.getLogger(__name__)

class CustomProvider(BaseProxyProvider):
    """
    自定义代理提供商
    
    支持从文件、URL或固定列表获取代理
    """
    
    def _init_provider_config(self, **kwargs):
        """
        初始化自定义代理提供商特定的配置
        
        Args:
            **kwargs: 配置参数
        """
        # 代理源类型：file, url, list
        self.source_type = kwargs.get('source_type', 'list')
        
        # 文件路径
        self.file_path = kwargs.get('file_path', '')
        
        # URL
        self.url = kwargs.get('url', '')
        
        # 代理列表
        self.proxy_list = kwargs.get('proxy_list', [])
        
        # 缓存
        self.cache_time = kwargs.get('cache_time', 300)  # 缓存时间（秒）
        self.cache = []
        self.last_fetch_time = 0
        
    def get_proxy(self, **kwargs) -> Dict[str, str]:
        """
        获取代理
        
        Args:
            **kwargs: 其他参数
            
        Returns:
            Dict[str, str]: 代理配置
        """
        # 确保缓存已填充
        self._ensure_cache_filled()
        
        # 如果缓存为空，返回空代理
        if not self.cache:
            logger.warning("代理缓存为空，无法获取代理")
            return {}
            
        # 随机选择一个代理
        proxy = random.choice(self.cache)
        return proxy
    
    def get_proxies(self, count: int = 1, **kwargs) -> List[Dict[str, str]]:
        """
        获取多个代理
        
        Args:
            count: 代理数量
            **kwargs: 其他参数
            
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
        填充代理缓存
        
        根据源类型从不同来源获取代理
        """
        if self.source_type == 'file':
            self._fill_from_file()
        elif self.source_type == 'url':
            self._fill_from_url()
        elif self.source_type == 'list':
            self._fill_from_list()
        else:
            logger.warning(f"未知的源类型: {self.source_type}")
    
    def _fill_from_file(self):
        """从文件填充缓存"""
        try:
            if not self.file_path:
                logger.error("未指定文件路径")
                return
                
            with open(self.file_path, 'r') as f:
                lines = f.readlines()
                
            self.cache = []
            for line in lines:
                line = line.strip()
                if line:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        ip = parts[0]
                        port = parts[1]
                        proxy = {
                            'http': f'http://{ip}:{port}',
                            'https': f'http://{ip}:{port}'
                        }
                        self.cache.append(proxy)
                        
            logger.info(f"从文件加载了 {len(self.cache)} 个代理")
                
        except Exception as e:
            logger.error(f"从文件加载代理失败: {str(e)}")
    
    def _fill_from_url(self):
        """从URL填充缓存"""
        try:
            if not self.url:
                logger.error("未指定URL")
                return
                
            response = requests.get(self.url, timeout=self.timeout)
            
            if response.status_code == 200:
                content = response.text
                lines = content.splitlines()
                
                self.cache = []
                for line in lines:
                    line = line.strip()
                    if line:
                        parts = line.split(':')
                        if len(parts) >= 2:
                            ip = parts[0]
                            port = parts[1]
                            proxy = {
                                'http': f'http://{ip}:{port}',
                                'https': f'http://{ip}:{port}'
                            }
                            self.cache.append(proxy)
                            
                logger.info(f"从URL加载了 {len(self.cache)} 个代理")
            else:
                logger.error(f"从URL获取代理失败: {response.status_code}, {response.text}")
                
        except Exception as e:
            logger.error(f"从URL加载代理失败: {str(e)}")
    
    def _fill_from_list(self):
        """从列表填充缓存"""
        try:
            if not self.proxy_list:
                logger.error("代理列表为空")
                return
                
            self.cache = []
            for proxy_str in self.proxy_list:
                if proxy_str:
                    parts = proxy_str.split(':')
                    if len(parts) >= 2:
                        ip = parts[0]
                        port = parts[1]
                        proxy = {
                            'http': f'http://{ip}:{port}',
                            'https': f'http://{ip}:{port}'
                        }
                        self.cache.append(proxy)
                        
            logger.info(f"从列表加载了 {len(self.cache)} 个代理")
                
        except Exception as e:
            logger.error(f"从列表加载代理失败: {str(e)}")

# 注册提供商
ProxyFactory.register_provider('custom', CustomProvider)
