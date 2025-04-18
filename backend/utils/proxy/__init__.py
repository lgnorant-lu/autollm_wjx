"""
----------------------------------------------------------------
File name:                  __init__.py
Author:                     Ignorant-lu
Date created:               2025/04/01
Description:                代理模块初始化
----------------------------------------------------------------

Changed history:
                            2025/04/01: 初始创建
----------------------------------------------------------------
"""

from .base import BaseProxyProvider
from .factory import ProxyFactory
from .pool import ProxyPool
from .utils import normalize_proxy_url, get_proxy_from_api, test_proxy, get_and_test_proxy, is_china_website, should_use_pinzan_proxy

__all__ = ['BaseProxyProvider', 'ProxyFactory', 'ProxyPool', 'normalize_proxy_url', 'get_proxy_from_api', 'test_proxy', 'get_and_test_proxy', 'is_china_website', 'should_use_pinzan_proxy']
