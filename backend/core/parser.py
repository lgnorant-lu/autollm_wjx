"""
----------------------------------------------------------------
File name:                  parser.py
Author:                     Ignorant-lu
Date created:               2025/02/15
Description:                问卷解析模块，负责解析问卷星的问卷结构和内容
----------------------------------------------------------------

Changed history:
                            2025/02/18: 增加问卷标题和副标题提取功能
                            2025/02/22: 改进不同题型处理逻辑，优化选项和ratio配置
                            2025/02/23: 改进问卷保存格式，使用实际标题
----------------------------------------------------------------
"""

from typing import List, Optional, Tuple, Union, Dict
from dataclasses import dataclass, asdict
import json
import re
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import time
import urllib3
import logging
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.config import Config

logger = logging.getLogger(__name__)


@dataclass
class Question:
    """
    问卷题目数据结构

    包含题目的各种属性，如题号、题型、标题、选项等
    支持多种问卷题型的数据存储
    """
    index: int  # 实际题号
    type: int   # 题型：
    # 1: 填空题
    # 2: 简答题（格式同填空题）
    # 3: 单选题
    # 4: 多选题
    # 5: 量表题/评价题
    # 6: 矩阵单选/多选/量表题
    # 7: 下拉题
    # 8: 评分题
    # 9: 矩阵填空/矩阵评分题
    # 11: 排序题
    # 注：还有多级下拉题，但由于复杂度高且罕见，暂不实现完整解析
    title: str  # 题目
    title_index: int  # 题目题号(没有则为-1)
    options: Union[List[str], List[List[str]], None] = None  # 支持多维结构
    ratio: Union[List[int], List[List[int]], None] = None    # 概率结构适配选项
    is_hidden: bool = False  # 是否隐藏
    relation: Optional[Tuple[int, int]] = None  # 关联逻辑
    jumps: Optional[List[Tuple[int, int]]] = None  # 跳题逻辑


class QuestionEncoder(json.JSONEncoder):
    """
    问卷题目JSON编码器

    用于将Question对象序列化为JSON格式
    """
    def default(self, obj):
        """
        转换Question对象为JSON可序列化的字典

        Args:
            obj: 要序列化的对象

        Returns:
            dict: 序列化后的字典
        """
        if isinstance(obj, Question):
            return asdict(obj)  # 转换dataclass为字典
        return super().default(obj)


def parse_survey(url):
    """
    解析问卷调查

    Args:
        url (str): 问卷链接，支持短链接

    Returns:
        dict: 包含问卷内容的字典
    """
    # 禁用不安全请求警告
    urllib3.disable_warnings()

    logger.info(f"开始解析问卷: {url}")

    # 确保URL格式正确
    if not url.startswith('http'):
        url = 'https://' + url
    logger.info(f"解析URL: {url}")

    try:
        session = requests.Session()
        session.verify = False  # 禁用SSL验证，解决SSL连接问题
        session.trust_env = False

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'
        }

        response = session.get(url, headers=headers, timeout=15)

        if response.status_code != 200:
            logger.error(f"获取问卷内容失败，状态码: {response.status_code}")
            return {"error": f"获取问卷内容失败，状态码: {response.status_code}"}

        soup = BeautifulSoup(response.text, 'html.parser')

        # 尝试提取标题
        title_element = soup.find('title')
        if title_element:
            title = title_element.text.strip()
            # 去除标题中可能存在的"问卷星"字样
            title = re.sub(r'问卷星', '', title).strip()
        else:
            title = "未知标题"
            logger.warning("未找到问卷标题")

        # 提取问题列表
        questions = []
        question_elements = soup.select('div.field')

        if not question_elements:
            logger.warning(f"未找到任何题目，检查选择器是否正确，尝试备用方法")
            # 尝试其他选择器
            question_elements = soup.select('div[type]')

            if not question_elements:
                logger.error("使用备用选择器仍未找到任何题目")
                return {
                    "id": extract_survey_id(url),
                    "title": title,
                    "questions": [],
                    "error": "未能解析到问题内容"
                }

        logger.info(f"找到 {len(question_elements)} 个题目元素")

        for index, q_elem in enumerate(question_elements):
            try:
                question_data = extract_question(q_elem, index)
                if question_data:
                    questions.append(question_data)
            except Exception as e:
                logger.error(f"解析题目 {index+1} 时出错: {e}", exc_info=True)

        survey_id = extract_survey_id(url)
        survey_data = {
            "id": survey_id,
            "title": title,
            "questions": questions
        }

        # 将问卷数据保存到文件
        questions_file_path = save_questions(questions, url=url, survey_stats={"title": title})
        if questions_file_path:
            logger.info(f"问卷 {survey_id} 解析完成，已保存到 {questions_file_path}")
        else:
            logger.warning(f"问卷 {survey_id} 解析完成，但保存失败")

        # 返回包含 survey_data 和 questions 文件路径的字典
        return {"survey_data": survey_data, "questions_file_path": questions_file_path}

    except requests.exceptions.SSLError as e:
        logger.error(f"SSL错误: {e}", exc_info=True)
        # 返回错误时也包含基本信息
        return {"error": f"SSL连接错误: {str(e)}", "survey_data": {"id": extract_survey_id(url), "title": "未知标题", "questions": []}, "questions_file_path": None}
    except requests.exceptions.ConnectionError as e:
        logger.error(f"连接错误: {e}", exc_info=True)
        return {"error": f"连接错误: {str(e)}", "survey_data": {"id": extract_survey_id(url), "title": "未知标题", "questions": []}, "questions_file_path": None}
    except requests.exceptions.Timeout as e:
        logger.error(f"请求超时: {e}", exc_info=True)
        return {"error": f"请求超时: {str(e)}", "survey_data": {"id": extract_survey_id(url), "title": "未知标题", "questions": []}, "questions_file_path": None}
    except Exception as e:
        logger.error(f"解析问卷时出错: {e}", exc_info=True)
        return {"error": f"解析错误: {str(e)}", "survey_data": {"id": extract_survey_id(url), "title": "未知标题", "questions": []}, "questions_file_path": None}


def extract_survey_id(url):
    """
    从URL中提取问卷ID

    Args:
        url: 问卷URL

    Returns:
        str: 问卷ID
    """
    import re
    # 尝试匹配标准问卷星URL
    wjx_pattern = r'wjx\.cn/[^/]+/([A-Za-z0-9]+)\.aspx'
    match = re.search(wjx_pattern, url)
    if match:
        return match.group(1)
    # 尝试匹配短链接
    short_pattern = r'wjx\.cn/([A-Za-z0-9]+)'
    match = re.search(short_pattern, url)
    if match:
        return match.group(1)
    # 如果都匹配不到，返回URL的MD5值
    import hashlib
    return hashlib.md5(url.encode()).hexdigest()[:8]


def save_questions(questions, output_path=None, url=None, survey_stats=None):
    """
    保存问卷题目到JSON文件

    Args:
        questions: 问卷题目列表
        output_path: 输出文件路径
        url: 问卷URL
        survey_stats: 问卷统计信息

    Returns:
        str: 输出文件路径
    """
    # 自动生成文件名
    if output_path is None:
        if url:
            survey_id = extract_survey_id(url)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(Config.DATA_DIR, f"questions_{survey_id}_{timestamp}.json")
        else:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(Config.DATA_DIR, f"questions_{timestamp}.json")

    # 确保输出一致的格式
    if isinstance(questions, list):
        # 获取问卷标题
        title = "问卷调查"
        if survey_stats and 'title' in survey_stats and survey_stats['title']:
            title = survey_stats['title']

        # 转换为统一格式
        formatted_data = {
            "id": extract_survey_id(url) if url else "",
            "title": title,  # 使用从问卷中提取的标题
            "subtitle": survey_stats.get('subtitle', '') if survey_stats else '',
            "url": url or "",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "questions": questions
        }
    else:
        formatted_data = questions

    # 创建目录
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 保存JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(formatted_data, f, cls=QuestionEncoder, ensure_ascii=False, indent=4)

    return output_path


def extract_question(q_elem, index):
    """
    从HTML元素中提取问题数据

    Args:
        q_elem: 问题HTML元素
        index: 问题索引

    Returns:
        dict: 问题数据字典
    """
    try:
        # 获取题目类型和索引
        q_type = int(q_elem.get('type', 0))
        q_index = int(q_elem.get('topic', 0))

        # 如果没有有效的题目类型或索引，跳过
        if q_type == 0 or q_index == 0:
            logger.warning(f"跳过无效问题元素: type={q_type}, index={q_index}")
            return None

        # 获取题目标题
        title_div = q_elem.find('div', class_='field-label')
        title = title_div.get_text(strip=True) if title_div else ''

        # 检查题目是否隐藏
        style = q_elem.get('style', '').lower()
        is_hidden = 'display: none' in style or 'display:none' in style

        # 初始化问题数据
        question_data = {
            "index": q_index,
            "type": q_type,
            "title": title,
            "is_hidden": is_hidden,
            "options": []
        }

        # 根据题型提取选项
        if q_type == 1:  # 填空题
            # 检查是否有输入框
            input_elem = q_elem.find('input', {'type': 'text'})
            if input_elem:
                question_data["is_fillblank"] = True  # 标记为填空题
                # 检查是否有限制长度
                max_length = input_elem.get('maxlength')
                if max_length:
                    question_data["max_length"] = int(max_length)

        elif q_type == 2:  # 简答题，格式同填空题
            # 检查是否有文本区
            textarea_elem = q_elem.find('textarea')
            if textarea_elem:
                question_data["is_essay"] = True  # 标记为简答题
                # 检查是否有限制长度
                max_length = textarea_elem.get('maxlength')
                if max_length:
                    question_data["max_length"] = int(max_length)
                # 检查行数
                rows = textarea_elem.get('rows')
                if rows:
                    question_data["rows"] = int(rows)

        elif q_type == 3 or q_type == 4:  # 单选或多选
            option_divs = q_elem.find_all('div', class_='label')
            options = []
            for opt in option_divs:
                opt_text = opt.get_text(strip=True)
                if opt_text:
                    options.append(opt_text)
            question_data["options"] = options

        elif q_type == 5:  # 量表题/评价题
            # 获取量表题的最小值和最大值
            min_val = 1
            max_val = 5

            # 检查是否有量表元素
            scale_div = q_elem.find('div', class_='scale-div')
            if scale_div:
                # 检查是否为评价题
                is_evaluation = q_elem.get('pj') == '1'

                # 获取量表标题
                scale_titles = []
                scale_title_divs = q_elem.select('.scaleTitle div')
                for div in scale_title_divs:
                    title_text = div.get_text(strip=True)
                    if title_text:
                        scale_titles.append(title_text)

                # 获取量表选项
                scale_options = []
                scale_values = []
                scale_option_titles = []
                scale_items = q_elem.select('ul.modlen5 li a')
                for item in scale_items:
                    val = item.get('val')
                    title = item.get('title')
                    if val and title:
                        scale_options.append(f"{val}. {title}")
                        scale_values.append(val)
                        scale_option_titles.append(title)
                        # 更新最大值
                        try:
                            item_val = int(val)
                            max_val = max(max_val, item_val)
                        except (ValueError, TypeError):
                            pass

                # 如果没有找到量表选项，尝试其他方式
                if not scale_options:
                    # 尝试找到所有的选项按钮
                    option_buttons = q_elem.select('a.rate-off')
                    for button in option_buttons:
                        val = button.get('val')
                        title = button.get('title')
                        if val and title:
                            scale_options.append(f"{val}. {title}")
                            scale_values.append(val)
                            scale_option_titles.append(title)
                            # 更新最大值
                            try:
                                item_val = int(val)
                                max_val = max(max_val, item_val)
                            except (ValueError, TypeError):
                                pass

                # 如果没有标题但有选项，使用选项作为标题
                if not scale_titles and scale_option_titles:
                    if len(scale_option_titles) >= 2:
                        scale_titles = [scale_option_titles[0], scale_option_titles[-1]]

                # 存储量表选项信息
                question_data["scale_options"] = scale_options
                question_data["scale_values"] = scale_values
                question_data["scale_titles"] = scale_titles

                # 如果是评价题，检查是否有标签
                evaluation_tags = []
                if is_evaluation:
                    tag_items = q_elem.select('.evaluateTagItem')
                    for tag in tag_items:
                        tag_text = tag.get_text(strip=True)
                        if tag_text and tag_text != '写评价':  # 排除“写评价”按钮
                            evaluation_tags.append(tag_text)

                question_data["scale_titles"] = scale_titles
                question_data["scale_options"] = scale_options
                question_data["is_evaluation"] = is_evaluation
                if evaluation_tags:
                    question_data["evaluation_tags"] = evaluation_tags

            question_data["min"] = min_val
            question_data["max"] = max_val
            question_data["is_rating"] = True  # 标记为评价题

        elif q_type == 6:  # 矩阵单选/多选/量表题
            # 获取行标题
            row_titles = []
            for row in q_elem.find_all('tr', class_='rowtitle'):
                row_text = row.get_text(strip=True)
                if row_text:
                    row_titles.append(row_text)

            # 获取列选项
            col_titles = []
            thead = q_elem.find('tr', class_='trlabel')
            if thead:
                for th in thead.find_all('th')[1:]:  # 跳过第一个，通常是行标题的标题
                    col_text = th.get_text(strip=True)
                    if col_text:
                        col_titles.append(col_text)

            # 检测是否为矩阵多选题
            is_matrix_checkbox = False
            checkboxes = q_elem.find_all('input', {'type': 'checkbox'})
            if checkboxes:
                is_matrix_checkbox = True

            # 将行和列组合为二维数组
            matrix_options = []
            for _ in range(len(row_titles)):
                matrix_options.append(col_titles.copy())

            question_data["options"] = matrix_options
            question_data["row_titles"] = row_titles
            question_data["is_matrix_checkbox"] = is_matrix_checkbox  # 标记是否为矩阵多选题

        elif q_type == 7:  # 下拉题
            # 获取下拉选项
            options = []
            select_elem = q_elem.find('select')
            if select_elem:
                for option in select_elem.find_all('option'):
                    # 跳过“请选择”等默认选项
                    if option.get('value') and option.get('value') != '-2':
                        opt_text = option.get_text(strip=True)
                        if opt_text:
                            options.append(opt_text)

            question_data["options"] = options
            question_data["is_dropdown"] = True  # 标记为下拉题

        elif q_type == 8:  # 评分题
            # 获取最小值和最大值
            min_val = 0
            max_val = 10
            input_elem = q_elem.find('input', {'type': 'range'})
            if input_elem:
                min_val = int(input_elem.get('min', 0))
                max_val = int(input_elem.get('max', 10))

            question_data["min"] = min_val
            question_data["max"] = max_val

        elif q_type == 9:  # 矩阵填空/矩阵评分题
            # 获取行标题
            row_titles = []
            for row in q_elem.find_all('tr', class_='rowtitle'):
                row_text = row.get_text(strip=True)
                if row_text:
                    row_titles.append(row_text)

            # 检测是否为个人信息填写
            is_personal_info = q_elem.get('gapfill') == '1'

            question_data["row_titles"] = row_titles
            question_data["is_personal_info"] = is_personal_info
            question_data["is_matrix_fillblank"] = True  # 标记为矩阵填空题

        # 返回问题数据
        return question_data

    except Exception as e:
        logger.error(f"提取问题 {index} 时出错: {e}", exc_info=True)
        return None


if __name__ == "__main__":
    # 设置日志级别
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # url = "https://www.wjx.cn/vm/PrvPXfZ.aspx"
    # url = "https://www.wjx.cn/vm/hpaiyPF.aspx#"
    url = "https://www.wjx.cn/vm/rLxBFZD.aspx"
    print(f"开始解析问卷: {url}")

    try:
        # 解析问卷
        result = parse_survey(url)

        if 'error' in result:
            print(f"解析错误: {result['error']}")
        else:
            survey_data = result.get('survey_data', {})
            questions_file_path = result.get('questions_file_path')

            print(f"问卷标题: {survey_data.get('title', '未知')}")
            print(f"问题总数: {len(survey_data.get('questions', []))}")

            # 统计题型数量
            type_count = {}
            for q in survey_data.get('questions', []):
                q_type = q.get('type')
                type_count[q_type] = type_count.get(q_type, 0) + 1

            print(f"题型统计: {type_count}")
            print(f"问卷解析完成，已保存为 {questions_file_path}")

            # 打印问题样例
            questions = survey_data.get('questions', [])
            if questions:
                print("\n问题示例:")
                for i, q in enumerate(questions[:3]):  # 只打印前3个问题
                    print(f"\n问题 {i+1}:")
                    print(f"题号: {q.get('index')}, 类型: {q.get('type')}")
                    print(f"题目: {q.get('title')}")
                    if 'options' in q and q['options']:
                        print(f"选项: {q['options']}")
                    if 'is_fillblank' in q and q['is_fillblank']:
                        print("类型: 填空题")
                    if 'is_essay' in q and q['is_essay']:
                        print("类型: 简答题")
                    if 'is_dropdown' in q and q['is_dropdown']:
                        print("类型: 下拉题")
                    if 'is_rating' in q and q['is_rating']:
                        print("类型: 量表题/评价题")
                    if 'is_evaluation' in q and q['is_evaluation']:
                        print("类型: 评价题")
                    if 'is_matrix_checkbox' in q and q['is_matrix_checkbox']:
                        print("类型: 矩阵多选题")
                    if 'is_matrix_fillblank' in q and q['is_matrix_fillblank']:
                        print("类型: 矩阵填空题")
    except Exception as e:
        print(f"解析过程中出错: {e}")
        import traceback
        traceback.print_exc()