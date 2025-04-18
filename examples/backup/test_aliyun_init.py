"""
测试阿里云LLM初始化
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# 添加项目根目录到系统路径
root_dir = str(Path(__file__).parent.parent)
sys.path.append(root_dir)

# 导入相关模块
from backend.core.llm_generator import LLMGenerator

def main():
    """主函数"""
    # 加载环境变量
    load_dotenv('.env.real')
    
    # 获取阿里云API密钥
    api_key = os.environ.get('ALIYUN_API_KEY')
    if not api_key:
        logger.error("未设置阿里云API密钥，请在.env.real文件中设置ALIYUN_API_KEY")
        return
    
    logger.info(f"阿里云API密钥: {api_key[:5]}...")
    
    # 初始化LLM生成器
    logger.info("开始初始化阿里云LLM生成器...")
    try:
        llm_gen = LLMGenerator(model_type='aliyun', api_key=api_key)
        logger.info("阿里云LLM生成器初始化成功")
        logger.info("测试成功")
    except Exception as e:
        logger.error(f"阿里云LLM生成器初始化失败: {e}")
        logger.error("测试失败")

if __name__ == "__main__":
    main()
