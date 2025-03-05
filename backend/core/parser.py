"""
----------------------------------------------------------------
File name:                  parser.py
Author:                     Ignorant-lu
Date created:               2025/03/05
Description:                问卷星问卷解析模块，用于解析问卷结构、题目和选项
----------------------------------------------------------------

Changed history:            问卷星解析模块初始版本
                            2025/03/05: 增加问卷标题和副标题提取功能
                            2025/03/05: 改进不同题型处理逻辑，优化选项和ratio配置
                            2025/03/05: 改进问卷保存格式，使用实际标题
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


def parse_survey(url: str) -> Tuple[List[Question], Dict[str, int]]:
    """
    解析问卷HTML并返回题目列表和统计信息
    
    Args:
        url: 问卷URL
        
    Returns:
        tuple: 题目列表和统计信息
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    questions = []
    total_questions = 0
    question_type_count = {}

    # 问卷 Title 的 title & subtitle 获取与格式化(去除多余空格和各种转义符)
    T_title = soup.find('h1', class_='htitle').string if soup.find('h1', class_='htitle') else ''
    T_subtitle = soup.find('span', class_='description').string if soup.find('span', class_='description') else ''
    T_title = T_title.strip().replace('\n', '').replace('\r', '').replace(' ', '')
    T_subtitle = T_subtitle.strip().replace('\n', '').replace('\r', '').replace(' ', '')

    # 问卷题目及相关信息
    for div in soup.find_all('div', class_='field'):
        if not div.get('topic'):
            continue

        q_type = int(div.get('type', 0))
        q_index = int(div.get('topic', 0))

        # 获取题目标题
        title_div = div.find('div', class_='field-label')
        title = title_div.get_text(strip=True) if title_div else ''

        # 优化: 使用正则提取标题索引
        title_index_match = re.match(r'^(\\d+)', title)
        title_index = int(title_index_match.group(1)) if title_index_match else -1

        # 优化: 分题型处理选项
        options = None
        if q_type in (3, 4):  # 单选/多选
            options = [opt.get_text(strip=True) for opt in div.find_all('div', class_='label') if opt.get_text(strip=True)]
        elif q_type == 6:  # 矩阵题
            row_titles = [opt.get_text(strip=True) for opt in div.find_all('tr', class_='rowtitle') if opt.get_text(strip=True)]
            col_options = [th.get_text(strip=True) for th in div.find('tr', class_='trlabel').find_all('th')[1:]]
            options = [col_options for _ in row_titles] if row_titles and col_options else None
        elif q_type == 8:  # 滑块题
            title_spans = [span.get_text(strip=True) for span in div.find_all('span', class_='itemTitleSpan') if span.get_text(strip=True)]
            input_elem = div.find('input', type='text')
            input_attrs = {
                'min': input_elem.get('min', '0'),
                'max': input_elem.get('max', '10'),
            } if input_elem else {}
            options = [title_spans, input_attrs] if title_spans and input_attrs else None

        # 优化: 统一空值处理
        if options:
            if isinstance(options[0], list):  # 二维数组
                if not all(options):  # 确保所有子列表非空
                    options = None
            elif not options:  # 一维数组
                options = None

        # 优化: 强化隐藏判断逻辑
        style = div.get('style', '').lower()
        is_hidden = bool(re.search(r'display\s*:\s*none', style))

        # 优化: 分题型初始化ratio
        ratio = None
        if options:
            if q_type in (3, 4):  # 一维选项
                ratio = [1] * len(options)
            elif q_type == 6:  # 矩阵题
                num_rows = len(options)  # 行数
                num_cols = len(options[0]) if options else 0  # 列数
                ratio = [[1] * num_cols for _ in range(num_rows)]  # 每个选项的概率均为1
            elif q_type == 8 and len(options) == 2:  # 滑块(评分)题
                min_val = int(options[1].get('min', 0))
                max_val = int(options[1].get('max', 10))
                ratio = [1] * (max_val - min_val + 1)  # 根据范围生成概率列表
            elif q_type == 5:
                # 量表嵌套各个基础题型,需判断(判断逻辑体系需重构)
                # 单多选填空
                pass

        # 检查跳题逻辑
        jumps = []
        if div.get('hasjump') == '1':
            for input_tag in div.find_all('input'):
                jump_to = input_tag.get('jumpto')
                if jump_to:
                    jumps.append((int(jump_to), int(input_tag.get('value', 0))))

        # 检查关联逻辑
        relation = None
        if div.get('relation'):
            rel_parts = div.get('relation').split(',')
            if len(rel_parts) == 2:
                relation = (int(rel_parts[0]), int(rel_parts[1]))

        question = Question(
            index=q_index,
            type=q_type,
            title=title,
            title_index=title_index,
            options=options,
            ratio=ratio,
            is_hidden=is_hidden,
            relation=relation,
            jumps=jumps if jumps else None
        )
        questions.append(question)

        total_questions += 1
        question_type_count[q_type] = question_type_count.get(q_type, 0) + 1

    # 返回题目列表和统计信息
    return questions, {
        'title': T_title,
        'subtitle': T_subtitle,
        'total': total_questions,
        'type_count': question_type_count
    }


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