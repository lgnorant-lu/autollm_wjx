"""
----------------------------------------------------------------
File name:                  ip_tracker.py
Author:                     Ignorant-lu
Date created:               2025/02/15
Description:                IP追踪器模块，提供IP地址记录和管理功能
----------------------------------------------------------------

Changed history:            2025/02/15: 从main.py提取IP跟踪相关功能
                            2025/03/02: 更新为使用配置模块
----------------------------------------------------------------
"""

import json
import os
import logging
from datetime import datetime
import requests

# 导入后端配置模块
from backend.config import get_config

logger = logging.getLogger(__name__)
config = get_config()

class IPUsageTracker:
    """IP使用跟踪器，用于记录和统计代理IP使用情况"""

    def __init__(self, log_file=None):
        """
        初始化IP使用跟踪器

        Args:
            log_file: 记录IP使用情况的JSON文件路径，如果为None则使用配置中的默认路径
        """
        self.log_file = log_file if log_file else config.IP_USAGE_FILE
        self.usage_data = self._load_usage_data()

    def _load_usage_data(self):
        """从文件加载IP使用数据，如果文件不存在则初始化空数据"""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载IP使用数据失败: {e}")
                return {'ips': {}, 'total_requests': 0, 'success_rate': 0}
        return {'ips': {}, 'total_requests': 0, 'success_rate': 0}

    def _save_usage_data(self):
        """保存IP使用数据到文件"""
        try:
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(self.usage_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存IP使用数据失败: {e}")

    def record_usage(self, ip: str, success: bool):
        """
        记录IP使用情况

        Args:
            ip: 使用的IP地址
            success: 是否成功使用
        """
        if ip not in self.usage_data['ips']:
            self.usage_data['ips'][ip] = {
                'total_uses': 0,
                'successful_uses': 0,
                'last_used': None
            }

        ip_data = self.usage_data['ips'][ip]
        ip_data['total_uses'] += 1
        if success:
            ip_data['successful_uses'] += 1
        ip_data['last_used'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self.usage_data['total_requests'] += 1
        total_success = sum(ip['successful_uses'] for ip in self.usage_data['ips'].values())
        self.usage_data['success_rate'] = total_success / self.usage_data['total_requests'] if self.usage_data['total_requests'] > 0 else 0

        self._save_usage_data()

    def get_statistics(self):
        """
        获取IP使用统计信息

        Returns:
            dict: 包含总IP数、总请求数、成功率和最常用IP的统计信息
        """
        return {
            'total_ips': len(self.usage_data['ips']),
            'total_requests': self.usage_data['total_requests'],
            'success_rate': self.usage_data['success_rate'],
            'most_used_ips': sorted(
                self.usage_data['ips'].items(),
                key=lambda x: x[1]['total_uses'],
                reverse=True
            )[:5]
        }

def get_current_ip(proxy_url: str = None) -> str:
    """
    获取当前使用的IP

    Args:
        proxy_url: 代理服务器URL，如果为None则使用配置中的默认代理URL

    Returns:
        str: 当前使用的IP地址，如果获取失败则返回None
    """
    # 如果没有提供代理URL，则使用环境变量中的代理URL
    if proxy_url is None:
        # 尝试从环境变量中获取代理URL
        proxy_url = os.environ.get('PINZAN_API_URL', '')

        # 如果环境变量中没有，则使用配置中的默认URL
        if not proxy_url and hasattr(config, 'DEFAULT_PROXY_URL'):
            proxy_url = config.DEFAULT_PROXY_URL

    if not proxy_url:
        logger.warning("未配置代理URL，无法获取当前IP")
        return None

    try:
        # 使用httpbin.org获取当前IP
        response = requests.get('http://httpbin.org/ip', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'origin' in data:
                return data['origin']
        return None
    except Exception as e:
        logger.error(f"获取IP失败: {e}")
        return None