"""
----------------------------------------------------------------
File name:                  config.py
Author:                     Ignorant-lu
Date created:               2025/03/05
Description:                系统配置模块，管理应用程序的各项配置和环境变量
----------------------------------------------------------------

Changed history:            初始化系统配置信息
                            2025/03/05: 添加目录配置、LLM配置和代理配置
----------------------------------------------------------------
"""

import os

# 应用基础配置
class Config:
    """
    应用程序配置类，包含所有全局配置项
    
    包括目录路径、文件位置、API密钥和代理配置等
    """
    # 基础目录 - 修改为使用绝对路径
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # 数据存储目录
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    
    # 日志目录
    LOG_DIR = os.path.join(BASE_DIR, 'logs')
    
    # 确保目录存在
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # 问卷数据存储目录
    SURVEYS_DIR = os.path.join(DATA_DIR, 'surveys')
    os.makedirs(SURVEYS_DIR, exist_ok=True)
    
    # 任务数据存储目录
    TASKS_DIR = os.path.join(DATA_DIR, 'tasks')
    os.makedirs(TASKS_DIR, exist_ok=True)
    
    # 索引文件
    SURVEY_INDEX_FILE = os.path.join(DATA_DIR, 'survey_index.json')
    TASK_INDEX_FILE = os.path.join(DATA_DIR, 'task_index.json')
    
    # LLM配置
    LLM_API_KEYS = {
        'openai': os.environ.get('OPENAI_API_KEY', ''),
        'zhipu': os.environ.get('ZHIPU_API_KEY', ''),
        'baidu': os.environ.get('BAIDU_API_KEY', '')
    }
    
    # 代理配置
    DEFAULT_PROXY_URL = os.environ.get('DEFAULT_PROXY_URL', '')