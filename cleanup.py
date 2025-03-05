#!/usr/bin/env python
"""
项目清理脚本，用于清理项目中不必要的文件
"""

import os
import shutil
import glob

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
    print(f"正在清理目录: {directory}")
    
    # 清理日志文件
    for log_file in glob.glob(os.path.join(directory, "**/*.log"), recursive=True):
        try:
            os.remove(log_file)
            print(f"删除日志文件: {log_file}")
        except Exception as e:
            print(f"无法删除 {log_file}: {e}")
    
    # 清理缓存文件和目录
    for root, dirs, files in os.walk(directory, topdown=False):
        # 删除 __pycache__ 目录
        if "__pycache__" in dirs:
            pycache_dir = os.path.join(root, "__pycache__")
            try:
                shutil.rmtree(pycache_dir)
                print(f"删除目录: {pycache_dir}")
            except Exception as e:
                print(f"无法删除 {pycache_dir}: {e}")
        
        # 删除 node_modules 目录
        if "node_modules" in dirs and os.path.exists(os.path.join(root, "node_modules")):
            node_modules_dir = os.path.join(root, "node_modules")
            try:
                # 实际上不删除node_modules，太大了，只打印提示
                print(f"注意: 请手动删除 {node_modules_dir} 目录以节省空间")
            except Exception as e:
                print(f"无法处理 {node_modules_dir}: {e}")
        
        # 检查并删除不必要的文件
        for file in files:
            file_path = os.path.join(root, file)
            if not should_keep_file(file_path):
                try:
                    os.remove(file_path)
                    print(f"删除文件: {file_path}")
                except Exception as e:
                    print(f"无法删除 {file_path}: {e}")

def main():
    """主函数"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 确保目录结构存在
    for dir_path in KEEP_DIRS:
        full_path = os.path.join(script_dir, dir_path)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
            print(f"创建目录: {full_path}")
    
    # 清理项目目录
    cleanup_directory(script_dir)
    
    print("\n清理完成！")
    print("请注意：")
    print("1. 已经清理了临时文件、日志文件和缓存文件")
    print("2. 保留了所有Python、Vue、JS、JSON和配置文件")
    print("3. node_modules目录需要手动删除")
    print("4. 执行 'git init' 和首次提交前，请再次检查 .gitignore 文件是否满足需求")

if __name__ == "__main__":
    main()
