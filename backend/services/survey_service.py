"""
----------------------------------------------------------------
File name:                  survey_service.py
Author:                     Ignorant-lu
Date created:               2025/02/15
Description:                问卷服务模块，提供问卷解析、存储和查询功能
----------------------------------------------------------------

Changed history:            
                            2025/02/22: 增加问卷标题和副标题提取支持
                            2025/03/03: 优化问卷结构存储格式
----------------------------------------------------------------
"""

import os
import json
import time
import logging
import re
from core.parser import parse_survey, extract_survey_id
from config import Config

logger = logging.getLogger(__name__)

class SurveyService:
    """
    问卷服务类
    
    负责问卷的获取、解析、存储和管理
    提供问卷元数据的索引和检索功能
    """
    def __init__(self):
        """
        初始化问卷服务
        
        设置问卷存储目录和索引文件
        """
        self.surveys_dir = Config.SURVEYS_DIR
        self.index_file = Config.SURVEY_INDEX_FILE
        self.survey_cache = {}  # 添加问卷缓存字典
        self._load_index()
    
    def _load_index(self):
        """
        加载问卷索引
        
        从索引文件中读取问卷元数据
        """
        try:
            if os.path.exists(self.index_file):
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        self.index = json.loads(content)
                    else:
                        logger.warning(f"索引文件 {self.index_file} 为空，创建新索引")
                        self.index = []
            else:
                logger.info(f"索引文件 {self.index_file} 不存在，创建新索引")
                self.index = []
                self._save_index()
        except Exception as e:
            logger.error(f"加载索引文件失败: {e}，创建新索引", exc_info=True)
            self.index = []
            self._save_index()
    
    def _save_index(self):
        """
        保存问卷索引
        
        将问卷元数据写入索引文件
        """
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)
    
    def parse_survey(self, url):
        """
        解析问卷
        
        获取问卷内容并存储到文件中
        """
        logger.info(f"开始解析问卷: {url}")
        
        try:
            # 获取问卷ID
            survey_id = extract_survey_id(url)
            
            # 检查是否已存在该问卷的解析结果
            existing_survey = None
            for entry in self.index:
                if entry["id"] == survey_id:
                    existing_survey = entry
                    break
            
            # 解析问卷
            try:
                logger.info(f"调用问卷解析函数: {url}")
                survey_result = parse_survey(url)
                
                # 检查是否解析成功
                if 'error' in survey_result:
                    logger.error(f"解析问卷失败: {survey_result['error']}")
                    raise Exception(survey_result['error'])
                
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                
                # 获取问卷数据
                survey_id = survey_result.get('id', survey_id)
                survey_title = survey_result.get('title', '未知标题')
                questions = survey_result.get('questions', [])
                
                logger.info(f"获取到问卷标题: {survey_title}, 题目数量: {len(questions)}")
                
                # 创建问卷数据
                survey_data = {
                    "id": survey_id,
                    "url": url,
                    "title": survey_title,
                    "created_at": timestamp,
                    "questions": questions
                }
                
                # 确保data/surveys目录存在
                os.makedirs(self.surveys_dir, exist_ok=True)
                
                # 保存问卷数据到新文件
                file_path = os.path.join(self.surveys_dir, f"{survey_id}_{timestamp}.json")
                logger.info(f"保存问卷数据到文件: {file_path}")
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(survey_data, f, ensure_ascii=False, indent=2)
                
                # 更新索引
                index_entry = {
                    "id": survey_id,
                    "title": survey_title,
                    "url": url,
                    "created_at": timestamp,
                    "file_path": file_path
                }
                
                # 如果已存在该问卷，更新索引并删除旧文件
                if existing_survey:
                    # 删除旧文件
                    if os.path.exists(existing_survey["file_path"]):
                        try:
                            os.remove(existing_survey["file_path"])
                            logger.info(f"删除已存在的问卷文件: {existing_survey['file_path']}")
                        except Exception as e:
                            logger.warning(f"删除旧问卷文件失败: {e}")
                    
                    # 更新索引中的条目
                    for i, entry in enumerate(self.index):
                        if entry["id"] == survey_id:
                            self.index[i] = index_entry
                            break
                else:
                    # 添加新条目到索引
                    self.index.append(index_entry)
                
                self._save_index()
                logger.info(f"问卷解析完成: {survey_id}")
                return survey_data
                
            except Exception as e:
                logger.error(f"解析问卷失败: {e}", exc_info=True)
                raise Exception(f"解析问卷失败: {str(e)}")
        
        except Exception as e:
            logger.error(f"解析问卷失败: {e}", exc_info=True)
            raise Exception(f"解析问卷失败: {str(e)}")
    
    def get_all_surveys(self):
        """
        获取所有问卷的基本信息
        
        返回问卷索引中的所有条目
        """
        return self.index
    
    def get_survey_by_id(self, survey_id):
        """
        根据问卷ID获取问卷内容
        
        Args:
            survey_id (str): 问卷ID
            
        Returns:
            dict: 问卷内容
        """
        if not survey_id:
            logger.error("问卷ID为空")
            return None
            
        logger.info(f"尝试获取问卷 ID: {survey_id}")
        
        # 先检查缓存
        if survey_id in self.survey_cache:
            logger.info(f"问卷 {survey_id} 从缓存中获取")
            return self.survey_cache[survey_id]
        
        try:
            # 获取基础目录
            base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
            data_dir = os.path.join(base_dir, 'data')
            
            # 检查目录是否存在
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
                logger.info(f"创建data目录: {data_dir}")
            
            # 首先尝试找到最新的问卷题目文件
            latest_file = None
            latest_time = 0
            
            logger.info(f"搜索问卷文件 (ID: {survey_id}) 在 {data_dir}")
            
            # 1. 首先查找questions_*格式的文件（更完整的数据）
            for filename in os.listdir(data_dir):
                if filename.startswith(f"questions_{survey_id}_") and filename.endswith('.json'):
                    file_path = os.path.join(data_dir, filename)
                    file_time = os.path.getmtime(file_path)
                    if file_time > latest_time:
                        latest_time = file_time
                        latest_file = file_path
                        logger.info(f"找到questions格式问卷文件: {filename}")
            
            # 2. 如果没找到，再检查surveys目录
            if not latest_file:
                surveys_dir = os.path.join(data_dir, 'surveys')
                if os.path.exists(surveys_dir):
                    for filename in os.listdir(surveys_dir):
                        if survey_id in filename and filename.endswith('.json'):
                            file_path = os.path.join(surveys_dir, filename)
                            file_time = os.path.getmtime(file_path)
                            if file_time > latest_time:
                                latest_time = file_time
                                latest_file = file_path
                                logger.info(f"找到surveys目录下的问卷文件: {filename}")
            
            # 3. 如果还没找到，尝试检查每个JSON文件的内容
            if not latest_file:
                for filename in os.listdir(data_dir):
                    if filename.endswith('.json'):
                        file_path = os.path.join(data_dir, filename)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                if isinstance(data, dict) and data.get('id') == survey_id:
                                    file_time = os.path.getmtime(file_path)
                                    if file_time > latest_time:
                                        latest_time = file_time
                                        latest_file = file_path
                                        logger.info(f"通过内容找到问卷文件: {filename}")
                        except Exception as e:
                            logger.warning(f"读取文件 {filename} 时出错: {e}")
                            continue
            
            # 如果找到了文件，读取内容
            if latest_file:
                logger.info(f"使用问卷文件: {latest_file}")
                try:
                    with open(latest_file, 'r', encoding='utf-8') as f:
                        survey_data = json.load(f)
                        
                    # 确保数据格式正确
                    if not isinstance(survey_data, dict):
                        logger.error(f"问卷数据格式错误，不是字典: {type(survey_data)}")
                        return None
                    
                    # 确保ID字段正确
                    if 'id' not in survey_data or survey_data['id'] != survey_id:
                        survey_data['id'] = survey_id
                        logger.info(f"修正问卷ID: {survey_id}")
                    
                    # 添加到缓存
                    self.survey_cache[survey_id] = survey_data
                    logger.info(f"问卷 {survey_id} 已添加到缓存")
                    
                    return survey_data
                    
                except Exception as e:
                    logger.error(f"读取问卷文件 {latest_file} 时出错: {e}")
                    return None
            
            logger.warning(f"未找到问卷 ID: {survey_id} 的文件")
            return None
                
        except Exception as e:
            logger.error(f"获取问卷 {survey_id} 时出错: {e}", exc_info=True)
            return None
    
    def delete_survey(self, survey_id):
        """
        删除问卷
        
        根据问卷ID从索引中查找并删除问卷数据和文件
        """
        for i, entry in enumerate(self.index):
            if entry["id"] == survey_id:
                try:
                    if os.path.exists(entry["file_path"]):
                        os.remove(entry["file_path"])
                    self.index.pop(i)
                    self._save_index()
                    logger.info(f"问卷已删除: {survey_id}")
                    return True
                except Exception as e:
                    logger.error(f"删除问卷失败 {survey_id}: {e}")
                    return False
        return False 
    
    def _extract_title_from_questions(self, questions):
        """
        从问卷数据中提取标题
        
        尝试从问题对象中找到标题相关字段
        """
        try:
            # 尝试从问题对象中找到标题相关字段
            if hasattr(questions, 'title'):
                return questions.title
            
            # 尝试从第一个问题的标题中提取问卷标题
            if questions and len(questions) > 0:
                if hasattr(questions[0], 'title'):
                    # 通常问卷的第一个问题标题可能包含问卷名称
                    first_title = questions[0].title
                    # 提取可能的问卷标题（如果有冒号分隔，取前半部分）
                    if ':' in first_title:
                        return first_title.split(':', 1)[0].strip()
                    elif '：' in first_title:
                        return first_title.split('：', 1)[0].strip()
            
            logger.warning("无法从问题中提取标题")
        except Exception as e:
            logger.error(f"提取标题时发生错误: {e}", exc_info=True)
        
        return None

    def _convert_to_serializable(self, questions):
        """
        将Question对象转换为可序列化的字典
        
        递归转换问题对象和选项对象为字典
        """
        if hasattr(questions, '__iter__'):
            serializable_questions = []
            for q in questions:
                if hasattr(q, '__dict__'):
                    # 如果是对象，转换为字典
                    q_dict = q.__dict__.copy()
                    # 如果options也是对象列表，也需要转换
                    if 'options' in q_dict and hasattr(q_dict['options'], '__iter__'):
                        q_dict['options'] = [
                            opt.__dict__ if hasattr(opt, '__dict__') else opt 
                            for opt in q_dict['options']
                        ]
                    serializable_questions.append(q_dict)
                else:
                    # 如果不是对象，直接添加
                    serializable_questions.append(q)
            return serializable_questions
        else:
            # 如果不是列表，则尝试转换单个对象
            return questions.__dict__ if hasattr(questions, '__dict__') else questions