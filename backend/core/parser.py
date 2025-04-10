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
    # 3: 单选题
    # 4: 多选题
    # 5: 量表题
    # 6: 矩阵题
    # 8: 评分题
    # 11: 排序题
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
        output_path = save_questions(questions, url=url, survey_stats={"title": title})
        if output_path:
            logger.info(f"问卷 {survey_id} 解析完成，已保存到 {output_path}")
        else:
            logger.warning(f"问卷 {survey_id} 解析完成，但保存失败")
        
        return survey_data
        
    except requests.exceptions.SSLError as e:
        logger.error(f"SSL错误: {e}", exc_info=True)
        return {"error": f"SSL连接错误: {str(e)}", "id": extract_survey_id(url), "title": "未知标题", "questions": []}
    except requests.exceptions.ConnectionError as e:
        logger.error(f"连接错误: {e}", exc_info=True)
        return {"error": f"连接错误: {str(e)}", "id": extract_survey_id(url), "title": "未知标题", "questions": []}
    except requests.exceptions.Timeout as e:
        logger.error(f"请求超时: {e}", exc_info=True)
        return {"error": f"请求超时: {str(e)}", "id": extract_survey_id(url), "title": "未知标题", "questions": []}
    except Exception as e:
        logger.error(f"解析问卷时出错: {e}", exc_info=True)
        return {"error": f"解析错误: {str(e)}", "id": extract_survey_id(url), "title": "未知标题", "questions": []}


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
            output_path = f"data/questions_{survey_id}_{timestamp}.json"
        else:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_path = f"data/questions_{timestamp}.json"
    
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
        if q_type == 3 or q_type == 4:  # 单选或多选
            option_divs = q_elem.find_all('div', class_='label')
            options = []
            for opt in option_divs:
                opt_text = opt.get_text(strip=True)
                if opt_text:
                    options.append(opt_text)
            question_data["options"] = options
            
        elif q_type == 6:  # 矩阵题
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
                        
            # 将行和列组合为二维数组
            matrix_options = []
            for _ in range(len(row_titles)):
                matrix_options.append(col_titles.copy())
                
            question_data["options"] = matrix_options
            question_data["row_titles"] = row_titles
            
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
            
        # 返回问题数据
        return question_data
            
    except Exception as e:
        logger.error(f"提取问题 {index} 时出错: {e}", exc_info=True)
        return None


if __name__ == "__main__":
    # url = "https://www.wjx.cn/vm/PrvPXfZ.aspx"
    url = "https://www.wjx.cn/vm/wWwct2F.aspx"
    print(f"开始解析问卷: {url}")
    questions, stats = parse_survey(url)
    print(f"问卷标题: {stats.get('title', '未知')}")
    print(f"问卷副标题: {stats.get('subtitle', '无')}")
    print(f"问题总数: {stats.get('total', 0)}")
    print(f"题型统计: {stats.get('type_count', {})}")
    
    output_path = save_questions(questions, url=url, survey_stats=stats)
    print(f"问卷解析完成，已保存为 {output_path}")
    
    # 打印问题样例
    if questions:
        print("\n问题示例:")
        sample = questions[0]
        print(f"题号: {sample.index}, 类型: {sample.type}")
        print(f"题目: {sample.title}")
        if sample.options:
            print(f"选项: {sample.options}")