"""
----------------------------------------------------------------
File name:                  app.py
Author:                     Ignorant-lu
Date created:               2025/02/15
Description:                问卷星自动化系统后端入口文件，提供Web API和核心功能
----------------------------------------------------------------

Changed history:            
                            2025/02/18: 添加日志配置，注册API蓝图，初始化目录结构
----------------------------------------------------------------
"""

from flask import Flask, jsonify
from flask_cors import CORS
import os
import logging
import sys


# 设置项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 将backend目录添加到Python路径
sys.path.insert(0, BASE_DIR)

# 确保必要的目录存在
LOG_DIR = os.path.join(os.path.dirname(BASE_DIR), 'logs', 'api')
DATA_DIR = os.path.join(BASE_DIR, 'data')
SURVEYS_DIR = os.path.join(DATA_DIR, 'surveys')
TASKS_DIR = os.path.join(DATA_DIR, 'tasks')

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(SURVEYS_DIR, exist_ok=True)
os.makedirs(TASKS_DIR, exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    # level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'api.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 导入路由
from routes.survey_routes import survey_bp
from routes.task_routes import task_bp
from routes.config_routes import config_bp

# 注册路由蓝图
app.register_blueprint(survey_bp, url_prefix='/api/surveys')
app.register_blueprint(task_bp, url_prefix='/api/tasks')
app.register_blueprint(config_bp, url_prefix='/api/config')

@app.route('/')
def index():
    """
    API根路径，返回服务状态信息
    
    Returns:
        JSON: 包含API名称、版本和状态的JSON响应
    """
    return jsonify({
        "name": "问卷星自动化系统API",
        "version": "1.0.0",
        "status": "运行中"
    })

if __name__ == '__main__':
    logger.info("启动API服务器，端口5000")
    app.run(debug=True, port=5000)