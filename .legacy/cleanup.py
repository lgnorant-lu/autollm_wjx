#!/usr/bin/env python
"""
项目清理脚本，用于清理项目中不必要的文件
"""

import os
import shutil
import glob
import time
import logging
from datetime import datetime
import sys

# 添加项目根目录到Python路径，确保可以导入backend模块
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# 导入配置模块
try:
    from backend.config import get_config
    config = get_config()
    using_config = True
    print("成功导入配置模块")
except ImportError:
    print("无法导入配置模块，使用默认配置")
    using_config = False

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 需要保留的目录结构
KEEP_DIRS = [
    "backend",
    "backend/core",
    "backend/routes",
    "backend/services",
    "backend/utils",
    "backend/data",
    "backend/logs",
    "frontend",
    "frontend/src",
    "frontend/src/api",
    "frontend/src/assets",
    "frontend/src/components",
    "frontend/src/router",
    "frontend/src/styles",
    "frontend/src/views",
    "frontend/public",
    "data/archive",
    "logs/api",
    "logs/tasks",
    "logs/proxy",
    "logs/System",
    "logs/Frontend",
    "logs/Backend",
]

# 需要保留的文件扩展名
KEEP_EXTENSIONS = [".py", ".vue", ".js", ".json", ".css", ".html", ".md", ".txt", ".yml", ".yaml", ".conf"]

# 需要保留的特定文件
KEEP_FILES = [
    "README.md",
    "requirements.txt",
    "Dockerfile.backend",
    "Dockerfile.frontend",
    "docker-compose.yml",
    "docker-compose.override.yml",
    ".gitignore",
    "frontend/package.json",
    "frontend/vite.config.js",
    "frontend/index.html",
    "frontend/nginx.conf",
]

def should_keep_file(file_path):
    """判断文件是否应该保留"""
    # 检查是否在特定保留文件列表中
    if os.path.basename(file_path) in KEEP_FILES:
        return True
    
    # 检查文件扩展名
    _, ext = os.path.splitext(file_path)
    if ext in KEEP_EXTENSIONS:
        # 排除临时备份文件、临时文件等
        if file_path.endswith("_last_1.py") or file_path.endswith(".tmp"):
            return False
        return True
    
    return False

def cleanup_directory(directory):
    """清理目录中的不必要文件"""
    logger.info(f"正在清理目录: {directory}")
    
    # 清理日志文件
    for log_file in glob.glob(os.path.join(directory, "**/*.log"), recursive=True):
        try:
            os.remove(log_file)
            logger.info(f"删除日志文件: {log_file}")
        except Exception as e:
            logger.error(f"无法删除 {log_file}: {e}")
    
    # 清理缓存文件和目录
    for root, dirs, files in os.walk(directory, topdown=False):
        # 删除 __pycache__ 目录
        if "__pycache__" in dirs:
            pycache_dir = os.path.join(root, "__pycache__")
            try:
                shutil.rmtree(pycache_dir)
                logger.info(f"删除目录: {pycache_dir}")
            except Exception as e:
                logger.error(f"无法删除 {pycache_dir}: {e}")
        
        # 删除 node_modules 目录
        if "node_modules" in dirs and os.path.exists(os.path.join(root, "node_modules")):
            node_modules_dir = os.path.join(root, "node_modules")
            try:
                # 实际上不删除node_modules，太大了，只打印提示
                logger.info(f"注意: 请手动删除 {node_modules_dir} 目录以节省空间")
            except Exception as e:
                logger.error(f"无法处理 {node_modules_dir}: {e}")
        
        # 检查并删除不必要的文件
        for file in files:
            file_path = os.path.join(root, file)
            if not should_keep_file(file_path):
                try:
                    os.remove(file_path)
                    logger.debug(f"删除文件: {file_path}")
                except Exception as e:
                    logger.error(f"无法删除 {file_path}: {e}")

def archive_old_data(directory=None, archive_dir=None, keep_days=None):
    """
    将旧的数据文件移至归档目录
    
    Args:
        directory: 数据目录
        archive_dir: 归档目录
        keep_days: 保留最近几天的文件不归档
    """
    # 如果使用配置模块，则优先使用配置值
    if using_config:
        directory = directory or config.DATA_DIR
        archive_dir = archive_dir or config.ARCHIVE_DIR
        keep_days = keep_days or config.DATA_RETENTION_DAYS
    else:
        directory = directory or "data"
        archive_dir = archive_dir or "data/archive"
        keep_days = keep_days or 30
        
    logger.info(f"归档旧数据文件，保留最近{keep_days}天的文件...")
    
    # 确保归档目录存在
    os.makedirs(archive_dir, exist_ok=True)
    
    # 获取当前时间
    now = time.time()
    # 计算保留时间界限
    cutoff = now - (keep_days * 24 * 60 * 60)
    
    # 获取所有JSON文件
    files = glob.glob(os.path.join(directory, "*.json"))
    
    archived = 0
    kept = 0
    
    for f in files:
        if os.path.isfile(f) and not f.startswith(archive_dir):
            # 获取文件修改时间
            mtime = os.path.getmtime(f)
            if mtime < cutoff:
                try:
                    # 移动到归档目录
                    dest_file = os.path.join(archive_dir, os.path.basename(f))
                    shutil.move(f, dest_file)
                    logger.info(f"已归档文件: {f} -> {dest_file}")
                    archived += 1
                except Exception as e:
                    logger.error(f"归档文件失败 {f}: {e}")
            else:
                kept += 1
    
    logger.info(f"归档完成: 归档{archived}个文件，保留{kept}个文件")
    return archived, kept

def cleanup_archives(archive_dir=None, max_age_days=None):
    """
    清理归档目录中的超过指定天数的文件
    
    Args:
        archive_dir: 归档目录
        max_age_days: 最大保留天数
    """
    # 如果使用配置模块，则优先使用配置值
    if using_config:
        archive_dir = archive_dir or config.ARCHIVE_DIR
        max_age_days = max_age_days or config.ARCHIVE_RETENTION_DAYS
    else:
        archive_dir = archive_dir or "data/archive"
        max_age_days = max_age_days or 90
        
    logger.info(f"清理归档目录中的旧文件，删除超过{max_age_days}天的文件...")
    
    # 获取当前时间
    now = time.time()
    # 计算保留时间界限
    cutoff = now - (max_age_days * 24 * 60 * 60)
    
    # 获取所有归档文件
    files = glob.glob(os.path.join(archive_dir, "*.json"))
    
    removed = 0
    kept = 0
    
    for f in files:
        if os.path.isfile(f):
            # 获取文件修改时间
            mtime = os.path.getmtime(f)
            if mtime < cutoff:
                try:
                    os.remove(f)
                    logger.info(f"已删除旧归档文件: {f}")
                    removed += 1
                except Exception as e:
                    logger.error(f"删除归档文件失败 {f}: {e}")
            else:
                kept += 1
    
    logger.info(f"归档清理完成: 删除{removed}个文件，保留{kept}个文件")
    return removed, kept

def main():
    """主函数"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 确保目录结构存在
    for dir_path in KEEP_DIRS:
        full_path = os.path.join(script_dir, dir_path)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
            logger.info(f"创建目录: {full_path}")
    
    # 归档旧的数据文件
    archive_old_data()
    
    # 清理过旧的归档文件
    cleanup_archives()
    
    # 清理项目目录
    cleanup_directory(script_dir)
    
    logger.info("\n清理完成！")
    logger.info("请注意：")
    logger.info("1. 已经清理了临时文件、日志文件和缓存文件")
    logger.info("2. 已将30天以前的数据文件归档")
    logger.info("3. 已删除90天以前的归档文件")
    logger.info("4. 保留了所有Python、Vue、JS、JSON和配置文件")
    logger.info("5. node_modules目录需要手动删除")
    logger.info("6. 执行 'git init' 和首次提交前，请再次检查 .gitignore 文件是否满足需求")

if __name__ == "__main__":
    main()
