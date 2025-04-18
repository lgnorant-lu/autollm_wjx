"""
----------------------------------------------------------------
File name:                  pinzan_provider.py
Author:                     Ignorant-lu
Date created:               2025/04/01
Description:                品赞IP代理提供商实现
----------------------------------------------------------------

Changed history:
                            2025/04/01: 初始创建
                            2025/04/02: 根据官方API文档更新实现
----------------------------------------------------------------
"""

import logging
import requests
import json
import time
import os
import re
from typing import Dict, List, Any, Optional
from ..base import BaseProxyProvider
from ..factory import ProxyFactory

logger = logging.getLogger(__name__)

class PinzanProvider(BaseProxyProvider):
    """
    品赞IP代理提供商

    使用品赞IP API获取代理
    官方文档: https://www.ipzan.com/help
    """

    def _init_provider_config(self, **kwargs):
        """
        初始化品赞IP特定的配置

        Args:
            **kwargs: 配置参数
        """
        # 从环境变量或配置中获取API URL
        self.api_url = kwargs.get('api_url', os.environ.get('PINZAN_API_URL', ''))

        # 代理协议
        self.protocol = kwargs.get('protocol', os.environ.get('PINZAN_PROTOCOL', 'http'))

        # 返回格式（根据API URL自动判断）
        self.format = kwargs.get('format', '')
        if not self.format:
            if self.api_url and ('format=json' in self.api_url or '.json' in self.api_url):
                self.format = 'json'
            else:
                self.format = 'txt'

        # 输出调试信息
        logger.debug(f"品赞IP返回格式: {self.format}")

        # 缓存
        self.cache_time = int(kwargs.get('cache_time', os.environ.get('PINZAN_CACHE_TIME', '60')))  # 缓存时间（秒）
        self.cache = {}
        self.last_fetch_time = 0

    def get_proxy(self, **kwargs) -> Dict[str, str]:
        """
        获取代理

        Args:
            **kwargs: 其他参数

        Returns:
            Dict[str, str]: 代理配置
        """
        # 检查缓存
        current_time = time.time()
        if self.cache and current_time - self.last_fetch_time < self.cache_time:
            logger.debug("使用缓存的代理")
            return self.cache

        # 检查API URL是否存在
        if not self.api_url:
            logger.error("未设置API URL")
            return {}

        try:
            # 发送请求
            response = requests.get(
                self.api_url,
                timeout=self.timeout
            )

            # 检查响应状态
            if response.status_code == 200:
                # 根据返回格式解析数据
                if self.format == 'json':
                    data = response.json()

                    # 检查响应数据
                    if data.get('code') == 0:
                        proxy_list = data.get('data', {}).get('list', [])

                        if proxy_list and len(proxy_list) > 0:
                            proxy_data = proxy_list[0]
                            ip = proxy_data.get('ip')
                            port = proxy_data.get('port')

                            if ip and port:
                                # 如果有账号密码
                                auth = ''
                                if proxy_data.get('account') and proxy_data.get('password'):
                                    auth = f"{proxy_data.get('account')}:{proxy_data.get('password')}@"

                                # 根据协议构建代理URL
                                proxy = {}

                                # 根据协议类型构建代理URL
                                if self.protocol.lower() == 'socks5':
                                    # SOCKS5协议
                                    proxy['http'] = f'socks5://{auth}{ip}:{port}'
                                    proxy['https'] = f'socks5://{auth}{ip}:{port}'
                                else:
                                    # HTTP/HTTPS协议
                                    proxy['http'] = f'http://{auth}{ip}:{port}'

                                    # HTTPS代理
                                    # 如果协议是https，则使用https协议
                                    # 否则使用http协议（因为大多数HTTP代理也可以用于HTTPS请求）
                                    if self.protocol.lower() == 'https':
                                        proxy['https'] = f'https://{auth}{ip}:{port}'
                                    else:
                                        proxy['https'] = f'http://{auth}{ip}:{port}'

                                # 更新缓存
                                self.cache = proxy
                                self.last_fetch_time = current_time

                                return proxy
                            else:
                                logger.error(f"品赞IP响应缺少IP或端口: {data}")
                        else:
                            logger.error(f"品赞IP响应缺少代理列表: {data}")
                    else:
                        logger.error(f"品赞IP API错误: {data.get('message')}")
                else:  # 处理txt格式
                    # 检查是否是JSON格式的响应
                    try:
                        # 尝试解析JSON
                        data = json.loads(response.text)

                        # 如果是有效的JSON响应，则将其当作JSON格式处理
                        if data.get('code') == 0 and data.get('data', {}).get('list'):
                            logger.info("检测到JSON格式响应，切换为JSON格式处理")
                            self.format = 'json'
                            proxy_list = data.get('data', {}).get('list', [])

                            if proxy_list and len(proxy_list) > 0:
                                proxy_data = proxy_list[0]
                                ip = proxy_data.get('ip')
                                port = proxy_data.get('port')

                                if ip and port:
                                    # 如果有账号密码
                                    auth = ''
                                    if proxy_data.get('account') and proxy_data.get('password'):
                                        auth = f"{proxy_data.get('account')}:{proxy_data.get('password')}@"

                                    # 根据协议构建代理URL
                                    proxy = {}

                                    # 根据协议类型构建代理URL
                                    if self.protocol.lower() == 'socks5':
                                        # SOCKS5协议
                                        proxy['http'] = f'socks5://{auth}{ip}:{port}'
                                        proxy['https'] = f'socks5://{auth}{ip}:{port}'
                                    else:
                                        # HTTP/HTTPS协议
                                        proxy['http'] = f'http://{auth}{ip}:{port}'

                                        # HTTPS代理
                                        # 如果协议是https，则使用https协议
                                        # 否则使用http协议（因为大多数HTTP代理也可以用于HTTPS请求）
                                        if self.protocol.lower() == 'https':
                                            proxy['https'] = f'https://{auth}{ip}:{port}'
                                        else:
                                            proxy['https'] = f'http://{auth}{ip}:{port}'

                                    # 更新缓存
                                    self.cache = proxy
                                    self.last_fetch_time = current_time

                                    return proxy

                            logger.error(f"品赞IP响应缺少有效的代理信息: {data}")
                            return {}
                        elif data.get('code') != 0:
                            logger.error(f"品赞IP API错误: {data.get('message')}")
                            return {}
                    except json.JSONDecodeError:
                        # 不是JSON格式，继续处理TXT格式
                        pass

                    # 处理TXT格式
                    lines = response.text.strip().split('\n')
                    if lines and len(lines) > 0:
                        line = lines[0].strip()

                        # 检查是否包含错误信息
                        if 'error' in line.lower() or ('code' in line.lower() and 'status' in line.lower()):
                            logger.error(f"品赞IP响应错误: {line}")
                            return {}

                        # 解析代理格式
                        parts = line.split(':')
                        if len(parts) >= 2:
                            ip = parts[0]
                            port = parts[1]

                            # 检查IP和端口是否有效
                            if not self._is_valid_ip(ip) or not port.isdigit():
                                logger.error(f"品赞IP响应包含无效的IP或端口: {line}")
                                return {}

                            # 如果有账号密码
                            auth = ''
                            if len(parts) >= 4:
                                username = parts[2]
                                password = parts[3]
                                auth = f'{username}:{password}@'

                            # 根据协议构建代理URL
                            proxy = {}

                            # 根据协议类型构建代理URL
                            if self.protocol.lower() == 'socks5':
                                # SOCKS5协议
                                proxy['http'] = f'socks5://{auth}{ip}:{port}'
                                proxy['https'] = f'socks5://{auth}{ip}:{port}'
                            else:
                                # HTTP/HTTPS协议
                                proxy['http'] = f'http://{auth}{ip}:{port}'

                                # HTTPS代理
                                # 如果协议是https，则使用https协议
                                # 否则使用http协议（因为大多数HTTP代理也可以用于HTTPS请求）
                                if self.protocol.lower() == 'https':
                                    proxy['https'] = f'https://{auth}{ip}:{port}'
                                else:
                                    proxy['https'] = f'http://{auth}{ip}:{port}'

                            # 更新缓存
                            self.cache = proxy
                            self.last_fetch_time = current_time

                            return proxy
                        else:
                            logger.error(f"品赞IP响应格式错误: {line}")
                    else:
                        logger.error("品赞IP响应为空")
            else:
                logger.error(f"品赞IP API请求失败: {response.status_code}, {response.text}")

            # 如果获取失败，返回缓存（如果有）
            if self.cache:
                logger.warning("获取新代理失败，使用缓存的代理")
                return self.cache

            # 如果没有缓存，返回空代理
            return {}

        except Exception as e:
            logger.error(f"品赞IP获取代理失败: {str(e)}")

            # 如果获取失败，返回缓存（如果有）
            if self.cache:
                logger.warning("获取新代理失败，使用缓存的代理")
                return self.cache

            # 如果没有缓存，返回空代理
            return {}

    def _is_valid_ip(self, ip: str) -> bool:
        """
        验证IP是否有效

        Args:
            ip: IP地址

        Returns:
            bool: IP是否有效
        """
        # 简单的IP格式验证
        pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
        if not re.match(pattern, ip):
            return False

        # 验证每个数字是否在有效范围内
        parts = ip.split('.')
        for part in parts:
            if not part.isdigit() or int(part) > 255:
                return False

        return True

    # 使用基类中的get_proxies方法的默认实现

# 注册提供商
ProxyFactory.register_provider('pinzan', PinzanProvider)
