"""
测试答案生成功能
"""

import sys
import os
import json
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.task_service import TaskService
from backend.services.survey_service import SurveyService

# 设置日志级别
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_answer_generation():
    """测试答案生成功能"""
    # 初始化服务
    survey_service = SurveyService()
    task_service = TaskService()
    
    # 加载问卷
    survey_id = "wWwct2F"  # 使用已有的问卷ID
    survey = survey_service.get_survey(survey_id)
    
    if not survey:
        logger.error(f"未找到问卷: {survey_id}")
        return
    
    logger.info(f"成功加载问卷: {survey_id}")
    logger.info(f"问卷标题: {survey.get('title', '未知')}")
    logger.info(f"问题数量: {len(survey.get('questions', []))}")
    
    # 统计题型
    type_count = {}
    for q in survey.get('questions', []):
        q_type = q.get('type')
        type_count[q_type] = type_count.get(q_type, 0) + 1
    
    logger.info(f"题型统计: {type_count}")
    
    # 生成答案
    answer_data = task_service._generate_answer_data(survey)
    logger.info(f"生成的答案数据: {answer_data}")
    
    # 解析答案数据
    answer_parts = answer_data.split("}")
    logger.info(f"答案部分数量: {len(answer_parts)}")
    
    for part in answer_parts:
        if not part:
            continue
        
        try:
            q_index, value = part.split("$")
            logger.info(f"题目 {q_index} 的答案: {value}")
        except Exception as e:
            logger.error(f"解析答案部分出错: {part}, 错误: {e}")

if __name__ == "__main__":
    test_answer_generation()
