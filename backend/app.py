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
# 在Docker环境中，日志目录应该是/app/logs
if os.path.exists('/app'):
    # Docker环境
    LOG_DIR = os.path.join('/app', 'logs', 'api')
    DATA_DIR = os.path.join('/app', 'data')
else:
    # 本地环境
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

# 加载环境变量
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 加载.env文件
try:
    from dotenv import load_dotenv
    # 尝试加载.env文件
    if os.path.exists('.env'):
        load_dotenv('.env')
        logger.info("从.env加载环境变量")
    else:
        logger.warning("未找到.env文件")

    # 设置默认的环境变量
    if not os.environ.get('ALIYUN_API_KEY'):
        os.environ['ALIYUN_API_KEY'] = "sk-6a184121b6294b348256264e172ddac0"
        logger.info("设置默认阿里云API密钥")

    if not os.environ.get('PINZAN_API_URL'):
        os.environ['PINZAN_API_URL'] = "https://service.ipzan.com/core-extract?num=1&no=20250216408295864496&minute=1&format=json&repeat=1&protocol=1&pool=ordinary&mode=auth&secret=v5eomjhvanppt08"
        logger.info("设置默认品赞API URL")

    logger.info(f"当前环境变量: ALIYUN_API_KEY={os.environ.get('ALIYUN_API_KEY', '')[:5]}..., PINZAN_API_URL={os.environ.get('PINZAN_API_URL', '')[:20]}...")

except ImportError:
    logger.warning("未安装python-dotenv包，无法加载.env文件")

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 导入路由
from routes.survey_routes import survey_bp
from routes.task_routes import task_bp
from routes.config_routes import config_bp

# 加载配置
from routes.config_routes import load_config
config = load_config()
logger.info(f"加载系统配置: {config}")

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