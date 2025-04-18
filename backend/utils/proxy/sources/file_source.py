"""
----------------------------------------------------------------
File name:                  file_source.py
Author:                     Ignorant-lu
Date created:               2025/04/01
Description:                文件代理源实现
----------------------------------------------------------------

Changed history:            
                            2025/04/01: 初始创建
----------------------------------------------------------------
"""

import logging
import os
import random
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class FileProxySource:
    """
    文件代理源
    
    从文件加载代理
    """
    
    def __init__(self, file_path: str, **kwargs):
        """
        初始化文件代理源
        
        Args:
            file_path: 文件路径
            **kwargs: 其他参数
        """
        self.file_path = file_path
        self.encoding = kwargs.get('encoding', 'utf-8')
        self.proxies = []
        self.load_proxies()
        
    def load_proxies(self):
        """
        加载代理
        
        从文件加载代理
        """
        try:
            if not os.path.exists(self.file_path):
                logger.error(f"代理文件不存在: {self.file_path}")
                return
                
            with open(self.file_path, 'r', encoding=self.encoding) as f:
                lines = f.readlines()
                
            self.proxies = []
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
                        self.proxies.append(proxy)
                        
            logger.info(f"从文件加载了 {len(self.proxies)} 个代理")
                
        except Exception as e:
            logger.error(f"从文件加载代理失败: {str(e)}")
            
    def get_proxy(self) -> Optional[Dict[str, str]]:
        """
        获取代理
        
        随机选择一个代理
        
        Returns:
            Dict[str, str]: 代理配置，如果没有可用代理则返回None
        """
        if not self.proxies:
            logger.warning("代理列表为空，无法获取代理")
            return None
            
        return random.choice(self.proxies)
        
    def get_proxies(self, count: int = 1) -> List[Dict[str, str]]:
        """
        获取多个代理
        
        随机选择多个代理
        
        Args:
            count: 代理数量
            
        Returns:
            List[Dict[str, str]]: 代理配置列表
        """
        if not self.proxies:
            logger.warning("代理列表为空，无法获取代理")
            return []
            
        if len(self.proxies) <= count:
            return self.proxies.copy()
        else:
            return random.sample(self.proxies, count)
            
    def add_proxy(self, proxy: Dict[str, str]):
        """
        添加代理
        
        Args:
            proxy: 代理配置
        """
        if proxy not in self.proxies:
            self.proxies.append(proxy)
            logger.debug(f"添加代理: {proxy}")
            
    def remove_proxy(self, proxy: Dict[str, str]):
        """
        移除代理
        
        Args:
            proxy: 代理配置
        """
        if proxy in self.proxies:
            self.proxies.remove(proxy)
            logger.debug(f"移除代理: {proxy}")
            
    def save_proxies(self):
        """
        保存代理
        
        将代理保存到文件
        """
        try:
            with open(self.file_path, 'w', encoding=self.encoding) as f:
                for proxy in self.proxies:
                    http_proxy = proxy.get('http', '')
                    if http_proxy.startswith('http://'):
                        http_proxy = http_proxy[7:]
                    f.write(f"{http_proxy}\n")
                    
            logger.info(f"保存了 {len(self.proxies)} 个代理到文件")
                
        except Exception as e:
            logger.error(f"保存代理到文件失败: {str(e)}")
            
    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        return {
            'total_proxies': len(self.proxies),
            'file_path': self.file_path
        }
