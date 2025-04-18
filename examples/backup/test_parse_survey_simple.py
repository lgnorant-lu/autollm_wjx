"""
简化版测试问卷解析功能
"""

import sys
import os
import json
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.parser import parse_survey

# 设置日志级别
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_parse_survey():
    """测试问卷解析功能"""
    # 测试URL
    url = "https://www.wjx.cn/vm/ri0BVx6.aspx"
    
    logger.info(f"开始解析问卷: {url}")
    
    try:
        # 解析问卷
        result = parse_survey(url)
        
        if 'error' in result:
            logger.error(f"解析错误: {result['error']}")
            return
        
        survey_data = result.get('survey_data', {})
        questions_file_path = result.get('questions_file_path')
        
        logger.info(f"问卷标题: {survey_data.get('title', '未知')}")
        logger.info(f"问题数量: {len(survey_data.get('questions', []))}")
        
        # 查找量表题
        scale_questions = [q for q in survey_data.get('questions', []) if q.get('type') == 5]
        logger.info(f"量表题数量: {len(scale_questions)}")
        
        # 打印前3个量表题详情
        for i, q in enumerate(scale_questions[:3]):
            logger.info(f"\n量表题 {i+1}:")
            logger.info(f"题号: {q.get('index')}")
            logger.info(f"题目: {q.get('title')}")
            logger.info(f"最小值: {q.get('min')}")
            logger.info(f"最大值: {q.get('max')}")
            
            if 'scale_titles' in q:
                logger.info(f"量表标题: {q.get('scale_titles')}")
            
            if 'scale_options' in q:
                logger.info(f"量表选项: {q.get('scale_options')}")
            
            if 'scale_values' in q:
                logger.info(f"量表值: {q.get('scale_values')}")
        
        logger.info(f"问卷解析完成，已保存为 {questions_file_path}")
        
    except Exception as e:
        logger.error(f"解析过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_parse_survey()
