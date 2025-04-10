"""
---------------------------------------------------------------
File name:                  test_parser.py
Author:                     Ignorant-lu
Date created:               2025/03/05
Description:                解析器测试模块
----------------------------------------------------------------

Changed history:            
                            2025/03/05: 初始创建;
                            2025/03/28: 更新文件路径;
----
"""

import os
import json
import logging
import pytest
from backend.core.parser import parse_survey, QuestionEncoder
from backend.services.survey_service import SurveyService

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_parse_and_serialize(sample_survey_url):
    """测试问卷解析和序列化过程"""
    # 1. 解析问卷
    url = sample_survey_url
    logger.info(f"开始解析问卷: {url}")
    questions, stats = parse_survey(url)
    logger.info(f"解析完成，获取到 {len(questions)} 个问题")
    
    # 2. 测试原始序列化 (使用QuestionEncoder)
    try:
        serialized_orig = json.dumps(questions, cls=QuestionEncoder, ensure_ascii=False)
        logger.info(f"原始序列化成功，长度: {len(serialized_orig)}")
        # 保存到文件以便检查
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        with open(os.path.join(data_dir, "test_serialized_orig.json"), "w", encoding="utf-8") as f:
            f.write(serialized_orig)
    except Exception as e:
        logger.error(f"原始序列化失败: {e}")
    
    # 3. 使用SurveyService中的方法进行序列化
    try:
        ss = SurveyService()
        serialized_ss = ss._convert_to_serializable(questions)
        logger.info(f"服务序列化成功，转换后问题数量: {len(serialized_ss) if isinstance(serialized_ss, list) else 'Not a list'}")
        # 保存到文件以便检查
        with open(os.path.join(data_dir, "test_serialized_ss.json"), "w", encoding="utf-8") as f:
            json.dump(serialized_ss, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"服务序列化失败: {e}")
    
    # 4. 测试反序列化
    try:
        ss_json = json.dumps(serialized_ss, ensure_ascii=False)
        deserialized = json.loads(ss_json)
        logger.info(f"反序列化成功，转换后问题数量: {len(deserialized) if isinstance(deserialized, list) else 'Not a list'}")
    except Exception as e:
        logger.error(f"反序列化失败: {e}")
    
    # 5. 保存一个测试问卷对象用于比较
    try:
        test_survey = {
            "id": "test_survey",
            "url": url,
            "title": stats.get('title', '问卷调查'),
            "created_at": "20250328_test",
            "questions": serialized_ss,
            "stats": stats
        }
        with open(os.path.join(data_dir, "test_survey.json"), "w", encoding="utf-8") as f:
            json.dump(test_survey, f, ensure_ascii=False, indent=2)
        logger.info("测试问卷保存成功")
    except Exception as e:
        logger.error(f"保存测试问卷失败: {e}")

if __name__ == "__main__":
    # 手动运行测试时使用
    logging.basicConfig(level=logging.INFO)
    # 创建示例URL
    url = 'https://www.wjx.cn/vm/wWwct2F.aspx'
    test_parse_and_serialize(url) 