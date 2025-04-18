"""
简单测试答案生成功能
"""

import sys
import os
import json
import logging
import random

# 设置日志级别
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_answer_data(survey):
    """
    根据问卷数据生成答案
    """
    submit_data_parts = []

    if not survey:
        logger.error("问卷数据为空")
        return ""

    if 'questions' not in survey:
        logger.error("问卷数据格式错误: 缺少questions字段")
        return ""

    if not survey['questions'] or len(survey['questions']) == 0:
        logger.error("问卷没有题目数据")
        return ""

    questions = survey['questions']
    logger.info(f"开始生成答案，问卷题目数量: {len(questions)}")

    for question in questions:
        try:
            q_index = question.get('index', 0)
            q_type = question.get('type', 0)
            q_title = question.get('title', 'Unknown title')

            logger.debug(f"处理题目 {q_index}: {q_title} (类型: {q_type})")

            # 忽略隐藏题目
            if question.get('is_hidden', False):
                logger.debug(f"跳过隐藏题目: {q_index}")
                continue

            # 单选题 (3)
            if q_type == 3:
                if 'options' in question and len(question['options']) > 0:
                    # 随机选择一个选项
                    option_index = random.randint(0, len(question['options']) - 1)
                    submit_data_parts.append(f"{q_index}${option_index + 1}")
                    logger.debug(f"单选题 {q_index} 选择了选项 {option_index + 1}: {question['options'][option_index]}")

            # 多选题 (4)
            elif q_type == 4:
                if 'options' in question and len(question['options']) > 0:
                    # 随机选择1-3个选项
                    num_options = len(question['options'])
                    num_to_select = min(random.randint(1, 3), num_options)
                    selected_options = random.sample(range(num_options), num_to_select)
                    options_str = '|'.join([str(opt + 1) for opt in selected_options])
                    submit_data_parts.append(f"{q_index}${options_str}")
                    logger.debug(f"多选题 {q_index} 选择了选项: {options_str}")

            # 填空题 (1)
            elif q_type == 1:
                # 生成一个简单的填空回答
                answers = ["很好", "不错", "一般", "满意", "需要改进"]
                text = random.choice(answers)
                submit_data_parts.append(f"{q_index}${text}")
                logger.debug(f"填空题 {q_index} 填写了: {text}")

            # 简答题 (2)
            elif q_type == 2:
                # 简答题格式同填空题，但内容可以更长
                answers = [
                    "我认为这个产品非常好用，推荐给大家。",
                    "整体体验不错，但还有提升空间。",
                    "使用过程中遇到了一些问题，希望能够改进。",
                    "我对这个产品的意见是功能齐全，但界面可以更美观。",
                    "建议增加更多的自定义选项，提高用户体验。"
                ]
                text = random.choice(answers)
                submit_data_parts.append(f"{q_index}${text}")
                logger.debug(f"简答题 {q_index} 填写了: {text}")

            # 下拉题 (7)
            elif q_type == 7:
                if 'options' in question and len(question['options']) > 0:
                    # 随机选择一个选项
                    option_index = random.randint(0, len(question['options']) - 1)
                    submit_data_parts.append(f"{q_index}${option_index + 1}")
                    logger.debug(f"下拉题 {q_index} 选择了选项 {option_index + 1}: {question['options'][option_index]}")

            # 矩阵单选/多选/量表题 (6)
            elif q_type == 6:
                if 'options' in question and isinstance(question['options'], list):
                    if question['options'] and isinstance(question['options'][0], list):
                        # 检查是否为矩阵多选题
                        is_matrix_checkbox = question.get('is_matrix_checkbox', False)
                        
                        # 对每行生成答案
                        row_answers = []
                        for i in range(len(question['options'])):
                            cols = len(question['options'][i])
                            if cols > 0:
                                if is_matrix_checkbox:
                                    # 矩阵多选题，每行随机选择1-3个选项
                                    num_to_select = min(random.randint(1, 3), cols)
                                    selected_cols = random.sample(range(cols), num_to_select)
                                    col_answers = []
                                    for col in selected_cols:
                                        col_answers.append(str(col + 1))
                                    # 矩阵多选题的格式是"行号!(选项号1|选项号2|选项号3)"
                                    row_answers.append(f"{i+1}!({','.join(col_answers)})")
                                else:
                                    # 矩阵单选题，每行随机选择一个选项
                                    col_index = random.randint(0, cols - 1)
                                    # 矩阵单选题的格式是"行号!选项号"
                                    row_answers.append(f"{i+1}!{col_index+1}")

                        if row_answers:
                            answer = ','.join(row_answers)
                            submit_data_parts.append(f"{q_index}${answer}")
                            logger.debug(f"矩阵题 {q_index} 回答: {answer}")

            # 量表题/评价题 (5)
            elif q_type == 5:
                # 量表题，随机选择一个值
                scale_max = 5
                if 'max' in question:
                    scale_max = int(question.get('max', 5))
                value = random.randint(1, scale_max)
                submit_data_parts.append(f"{q_index}${value}")
                logger.debug(f"量表题/评价题 {q_index} 选择: {value}")

            # 评分题 (8)
            elif q_type == 8:
                # 评分题通常是1-5或1-10分
                max_score = 5
                if 'max' in question:
                    max_score = int(question.get('max', 5))
                score = random.randint(1, max_score)
                submit_data_parts.append(f"{q_index}${score}")
                logger.debug(f"评分题 {q_index} 评分: {score}")

            # 排序题 (11)
            elif q_type == 11:
                if 'options' in question and len(question['options']) > 0:
                    # 生成随机排序
                    num_options = len(question['options'])
                    order = list(range(1, num_options + 1))
                    random.shuffle(order)
                    # 注意：排序题应该使用逗号（,）作为分隔符，而不是竖线（|）
                    order_str = ','.join(map(str, order))
                    submit_data_parts.append(f"{q_index}${order_str}")
                    logger.debug(f"排序题 {q_index} 排序: {order_str}")

            # 矩阵填空/矩阵评分题 (9)
            elif q_type == 9:
                # 检查是否有行标题
                if 'row_titles' in question and question['row_titles']:
                    row_titles = question['row_titles']
                    num_rows = len(row_titles)
                    
                    # 检查是否为个人信息填写
                    is_personal_info = question.get('is_personal_info', False)
                    
                    # 生成每行的填空内容
                    row_answers = []
                    for i in range(num_rows):
                        if is_personal_info:
                            # 个人信息填写
                            personal_info = ["张三", "18", "男", "北京", "13800138000", "test@example.com"]
                            if i < len(personal_info):
                                row_answers.append(personal_info[i])
                            else:
                                row_answers.append(f"信息{i+1}")
                        else:
                            # 普通矩阵填空
                            row_answers.append(f"回答{i+1}")
                    
                    # 使用^(接口符)分隔不同行的填空内容
                    answer = "^".join(row_answers)
                    submit_data_parts.append(f"{q_index}${answer}")
                    logger.debug(f"矩阵填空/评分题 {q_index} 回答: {answer}")
                else:
                    # 如果没有行标题，使用默认回答
                    submit_data_parts.append(f"{q_index}$默认回答")
                    logger.debug(f"矩阵填空/评分题 {q_index} 使用默认回答")

            # 如果是其他题型，记录日志
            else:
                logger.warning(f"未处理的题型 {q_type} 题目ID: {q_index}, 题目: {q_title}")

        except Exception as e:
            logger.error(f"生成问题 {q_index} 的答案时出错: {e}")
            # 跳过这个问题，继续处理下一个

    # 将所有部分连接成一个字符串，使用 "}" 分隔
    submit_data = "}".join(submit_data_parts)
    logger.info(f"生成的提交数据包含 {len(submit_data_parts)} 个题目答案")

    return submit_data

def test_answer_generation():
    """测试答案生成功能"""
    # 加载问卷数据
    survey_file = "D:\\狗py\\pythonProject1\\wjx_api_trying_0\\data\\questions_wWwct2F_20250418_061342.json"
    
    try:
        with open(survey_file, 'r', encoding='utf-8') as f:
            survey = json.load(f)
        
        logger.info(f"成功加载问卷文件: {survey_file}")
        logger.info(f"问卷标题: {survey.get('title', '未知')}")
        logger.info(f"问题数量: {len(survey.get('questions', []))}")
        
        # 统计题型
        type_count = {}
        for q in survey.get('questions', []):
            q_type = q.get('type')
            type_count[q_type] = type_count.get(q_type, 0) + 1
        
        logger.info(f"题型统计: {type_count}")
        
        # 生成答案
        answer_data = generate_answer_data(survey)
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
    
    except Exception as e:
        logger.error(f"测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_answer_generation()
