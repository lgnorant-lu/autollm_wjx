"""
----------------------------------------------------------------
File name:                  __init__.py
Author:                     Ignorant-lu
Date created:               2025/04/01
Description:                代理提供商模块初始化
----------------------------------------------------------------

Changed history:            
                            2025/04/01: 初始创建
----------------------------------------------------------------
"""

# 导入所有提供商
from .pinzan_provider import PinzanProvider
from .custom_provider import CustomProvider

# 导出所有提供商
__all__ = [
    'PinzanProvider',
    'CustomProvider'
]
