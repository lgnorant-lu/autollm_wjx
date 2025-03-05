import os
import json
import time
import logging
from core.parser import parse_survey, extract_survey_id
from config import Config

logger = logging.getLogger(__name__)

class SurveyService:
    def __init__(self):
        """初始化问卷服务"""
        self.surveys_dir = Config.SURVEYS_DIR
        self.index_file = Config.SURVEY_INDEX_FILE
        self._load_index()
    
    def _load_index(self):
        """加载问卷索引"""
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
        """保存问卷索引"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)
    
    def parse_survey(self, url):
        """解析问卷"""
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
                questions, stats = parse_survey(url)
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                
                # 将Question对象转换为可序列化的字典
                serializable_questions = self._convert_to_serializable(questions)
                
                # 从统计信息中获取问卷标题
                survey_title = stats.get('title', '') or self._extract_title_from_questions(questions) or "问卷调查"
                logger.info(f"获取到问卷标题: {survey_title}")
                
                # 创建问卷数据
                survey_data = {
                    "id": survey_id,
                    "url": url,
                    "title": survey_title,
                    "created_at": timestamp,
                    "questions": serializable_questions,
                    "stats": stats
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
                    "title": survey_data["title"],
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
        """获取所有问卷的基本信息"""
        return self.index
    
    def get_survey_by_id(self, survey_id):
        """获取指定问卷的详细信息"""
        for entry in self.index:
            if entry["id"] == survey_id:
                try:
                    with open(entry["file_path"], 'r', encoding='utf-8') as f:
                        logger.info(f"读取问卷数据成功 {survey_id}")
                        logger.info(f"文件路径: {entry['file_path']}")
                        return json.load(f)
                except Exception as e:
                    logger.error(f"读取问卷数据失败 {survey_id}: {e}")
                    return None
        return None
    
    def delete_survey(self, survey_id):
        """删除问卷"""
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
        """从问卷数据中提取标题"""
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
        """将Question对象转换为可序列化的字典"""
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