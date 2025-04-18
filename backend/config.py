"""
----------------------------------------------------------------
File name:                  config.py
Author:                     Ignorant-lu
Date created:               2025/02/15
Description:                系统配置模块，管理应用程序的各项配置和环境变量
----------------------------------------------------------------

Changed history:
                            2025/02/16: 添加目录配置、LLM配置和代理配置
                            2025/03/02: 添加IP追踪器配置和获取配置的方法
----------------------------------------------------------------
"""

import os
import logging

logger = logging.getLogger(__name__)

# 版本信息
def get_version():
    """获取应用版本号"""
    try:
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'VERSION'), 'r') as f:
            return f.read().strip()
    except Exception as e:
        logger.warning(f"无法读取版本文件: {e}")
        return "1.2.0"  # 默认版本

# 应用基础配置
APP_VERSION = get_version()
class Config:
    """
    应用程序配置类，包含所有全局配置项

    包括目录路径、文件位置、API密钥和代理配置等
    """
    # 基础目录 - 修改为使用绝对路径
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 数据存储目录 - Docker环境下使用/app/data，本地环境使用相对路径
    DATA_DIR = os.path.join(BASE_DIR, 'data')

    # 日志目录 - Docker环境下使用/app/logs，本地环境使用相对路径
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

    # 数据归档目录
    ARCHIVE_DIR = os.path.join(DATA_DIR, 'archive')
    os.makedirs(ARCHIVE_DIR, exist_ok=True)

    # 索引文件
    SURVEY_INDEX_FILE = os.path.join(DATA_DIR, 'indexes', 'survey_index.json')
    TASK_INDEX_FILE = os.path.join(DATA_DIR, 'indexes', 'task_index.json')

    # IP跟踪配置
    IP_USAGE_FILE = os.path.join(DATA_DIR, 'ip_usage.json')

    # 数据保留配置
    DATA_RETENTION_DAYS = 30
    ARCHIVE_RETENTION_DAYS = 90

    # LLM配置
    LLM_API_KEYS = {
        'openai': os.environ.get('OPENAI_API_KEY', ''),
        'zhipu': os.environ.get('ZHIPU_API_KEY', ''),
        'baidu': os.environ.get('BAIDU_API_KEY', '')
    }

    # 代理配置
    USE_PROXY = os.environ.get('USE_PROXY', 'False').lower() in ('true', 'yes', '1', 't')
    DEFAULT_PROXY_URL = os.environ.get('DEFAULT_PROXY_URL', '')

    # 日志配置
    LOG_LEVEL = logging.DEBUG
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    MAIN_LOG_FILE = os.path.join(LOG_DIR, 'app.log')
    PROXY_LOG_FILE = os.path.join(LOG_DIR, 'proxy_usage.log')

    def __init__(self):
        """初始化配置，可以在这里添加运行时的配置逻辑"""
        # 设置日志级别 - LOG_LEVEL现在是int类型，不需要转换
        self.log_level_value = self.LOG_LEVEL if isinstance(self.LOG_LEVEL, int) else getattr(logging, self.LOG_LEVEL.upper(), logging.INFO)

        logger.info(f"配置初始化完成, 基础目录: {self.BASE_DIR}")
        logger.info(f"数据目录: {self.DATA_DIR}")
        logger.info(f"日志目录: {self.LOG_DIR}")

    def get_ip_usage_file(self, survey_id=None, timestamp=None):
        """
        获取IP使用记录文件路径

        Args:
            survey_id: 问卷ID
            timestamp: 时间戳

        Returns:
            str: IP使用记录文件路径
        """
        if survey_id and timestamp:
            return os.path.join(self.DATA_DIR, f"ip_usage_{survey_id}_{timestamp}.json")
        return self.IP_USAGE_FILE

    def get_survey_file(self, survey_id, timestamp=None):
        """
        获取问卷数据文件路径

        Args:
            survey_id: 问卷ID
            timestamp: 时间戳

        Returns:
            str: 问卷数据文件路径
        """
        if timestamp:
            return os.path.join(self.SURVEYS_DIR, f"survey_{survey_id}_{timestamp}.json")
        return os.path.join(self.SURVEYS_DIR, f"survey_{survey_id}.json")

    def get_task_log_file(self, survey_id, timestamp):
        """
        获取任务日志文件路径

        Args:
            survey_id: 问卷ID
            timestamp: 时间戳

        Returns:
            str: 任务日志文件路径
        """
        return os.path.join(self.LOG_DIR, 'tasks', f"survey_{survey_id}_{timestamp}.log")

# 创建全局配置实例
config = Config()

def get_config():
    """获取全局配置对象"""
    return config