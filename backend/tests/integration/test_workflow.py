"""
---------------------------------------------------------------
File name:                  test_workflow.py
Author:                     Ignorant-lu
Date created:               2025/03/28
Description:                工作流集成测试模块
----------------------------------------------------------------

Changed history:            
                            2025/03/28: 初始创建;
----
"""

import os
import json
import pytest
import logging
from backend.core.parser import parse_survey
from backend.services.survey_service import SurveyService
from backend.services.task_service import TaskService

# 设置日志
logger = logging.getLogger(__name__)

@pytest.mark.integration
def test_survey_parse_to_task_creation(sample_survey_url):
    """测试从问卷解析到任务创建的完整流程"""
    # 测试环境准备
    logger.info("开始测试从问卷解析到任务创建的完整流程")
    
    # 1. 使用SurveyService解析问卷
    survey_service = SurveyService()
    survey_id = survey_service.parse_survey(sample_survey_url)
    assert survey_id is not None, "问卷解析失败，未能获取问卷ID"
    logger.info(f"问卷解析成功，ID: {survey_id}")
    
    # 2. 获取解析后的问卷数据
    survey = survey_service.get_survey(survey_id)
    assert survey is not None, "获取问卷数据失败"
    assert "questions" in survey, "问卷数据中没有questions字段"
    assert len(survey["questions"]) > 0, "问卷没有包含任何问题"
    logger.info(f"成功获取问卷数据，问题数量: {len(survey['questions'])}")
    
    # 3. 使用TaskService创建任务
    task_service = TaskService()
    task_data = {
        "survey_id": survey_id,
        "count": 1,  # 测试只提交一次
        "use_llm": False,
        "use_proxy": False
    }
    
    # 注意：在集成测试中，我们可以mock实际的提交过程
    # 这里仅测试到任务创建步骤
    task_id = task_service.create_task(task_data)
    assert task_id is not None, "任务创建失败"
    logger.info(f"任务创建成功，ID: {task_id}")
    
    # 4. 验证任务数据
    task = task_service.get_task(task_id)
    assert task is not None, "获取任务数据失败"
    assert task["survey_id"] == survey_id, "任务数据中的survey_id不匹配"
    assert task["status"] in ["waiting", "created"], "任务状态不正确"
    logger.info(f"任务数据验证成功，状态: {task['status']}")
    
    logger.info("完整工作流测试成功") 