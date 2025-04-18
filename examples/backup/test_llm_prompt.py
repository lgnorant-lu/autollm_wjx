"""
测试LLM提示词生成
"""

import sys
import os
import json
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.llm.providers.aliyun_provider import AliyunProvider

# 设置日志级别
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_llm_prompt():
    """测试LLM提示词生成"""
    # 加载问卷数据
    survey_file = "D:\\狗py\\pythonProject1\\wjx_api_trying_0\\data\\questions_ri0BVx6_20250418_071516.json"
    
    try:
        with open(survey_file, 'r', encoding='utf-8') as f:
            survey_data = json.load(f)
        
        logger.info(f"成功加载问卷文件: {survey_file}")
        logger.info(f"问卷标题: {survey_data.get('title', '未知')}")
        logger.info(f"问题数量: {len(survey_data.get('questions', []))}")
        
        # 初始化阿里云LLM提供商
        api_key = "sk-6a184121b6294b348256264e172ddac0"  # 示例密钥
        provider = AliyunProvider(api_key=api_key)
        
        # 生成提示词
        logger.info("开始生成提示词...")
        prompt = provider.build_prompt(survey_data)
        
        # 打印提示词的前500个字符
        logger.info(f"生成的提示词前500个字符: {prompt[:500]}...")
        
        # 查找量表题的提示词
        scale_questions = [q for q in survey_data.get('questions', []) if q.get('type') == 5]
        for i, q in enumerate(scale_questions[:3]):
            q_index = q.get('index')
            
            # 在提示词中查找该题目
            start_idx = prompt.find(f"问题{q_index}（{q_index}）：")
            if start_idx != -1:
                end_idx = prompt.find("\n\n", start_idx)
                if end_idx == -1:
                    end_idx = len(prompt)
                
                question_prompt = prompt[start_idx:end_idx]
                logger.info(f"\n量表题 {q_index} 的提示词:\n{question_prompt}")
        
    except Exception as e:
        logger.error(f"测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_llm_prompt()
