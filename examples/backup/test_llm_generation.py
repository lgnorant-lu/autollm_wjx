"""
测试LLM生成答案
"""

import sys
import os
import json
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.llm_generator import LLMGenerator
from backend.core.llm.providers.aliyun_provider import AliyunProvider

# 设置日志级别
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_llm_generation():
    """测试LLM生成答案"""
    # 加载问卷数据
    survey_file = "D:\\狗py\\pythonProject1\\wjx_api_trying_0\\data\\questions_ri0BVx6_20250418_071516.json"

    try:
        with open(survey_file, 'r', encoding='utf-8') as f:
            survey_data = json.load(f)

        logger.info(f"成功加载问卷文件: {survey_file}")
        logger.info(f"问卷标题: {survey_data.get('title', '未知')}")
        logger.info(f"问题数量: {len(survey_data.get('questions', []))}")

        # 初始化LLM生成器
        api_key = os.environ.get('ALIYUN_API_KEY')
        if not api_key:
            # 使用硬编码的API密钥进行测试
            api_key = "sk-6a184121b6294b348256264e172ddac0"  # 这是一个示例密钥，实际使用时请替换为您的密钥
            logger.info(f"使用硬编码的API密钥: {api_key[:5]}...")

        provider = AliyunProvider(api_key=api_key)
        llm_gen = LLMGenerator(provider=provider)

        # 生成答案
        logger.info("开始生成答案...")
        answers = llm_gen.generate_answers(survey_data)

        logger.info(f"生成的答案: {answers}")

    except Exception as e:
        logger.error(f"测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_llm_generation()
