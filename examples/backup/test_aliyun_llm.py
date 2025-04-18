"""
测试阿里云LLM
"""

import os
import sys
import logging
import threading
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

def test_aliyun_llm(api_key):
    """测试阿里云LLM"""
    try:
        logger.info("初始化阿里云LLM生成器...")

        # 初始化LLM生成器
        logger.info(f"开始初始化阿里云LLM生成器，API密钥: {api_key[:5]}...")
        try:
            llm_gen = LLMGenerator(model_type='aliyun', api_key=api_key)
            logger.info("阿里云LLM生成器初始化成功")
        except Exception as e:
            logger.error(f"阿里云LLM生成器初始化失败: {e}")
            raise

        # 测试生成答案
        logger.info("测试生成答案...")
        question_data = {
            'title': '测试问卷',
            'questions': [
                {
                    'id': '1',
                    'index': '1',
                    'title': '你好，请介绍一下自己和你公司',
                    'type': 1,  # 填空题
                    'options': []
                }
            ]
        }

        # 添加超时处理
        def generate_with_timeout():
            nonlocal llm_gen, question_data
            try:
                response = llm_gen.generate_answers(question_data)
                logger.info(f"生成的答案: {response}")
                return response
            except Exception as e:
                logger.error(f"生成答案异常: {e}")
                return None

        # 创建线程
        thread = threading.Thread(target=generate_with_timeout)
        thread.daemon = True
        thread.start()

        # 等待最多15秒
        thread.join(15)

        if thread.is_alive():
            logger.warning("生成答案超时，可能是网络问题或服务器响应慢")
            return False

        logger.info("阿里云LLM测试成功")
        return True
    except Exception as e:
        logger.error(f"阿里云LLM测试失败: {e}")
        return False

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

    # 测试阿里云LLM
    success = test_aliyun_llm(api_key)

    if success:
        logger.info("阿里云LLM测试成功")
    else:
        logger.error("阿里云LLM测试失败")

if __name__ == "__main__":
    main()
