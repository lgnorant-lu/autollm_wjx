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
                            2025/04/17: 增强索引文件读写的鲁棒性
----------------------------------------------------------------
"""

import os
import json
import time
import logging
import re
import shutil  # 添加 shutil 导入
from backend.core.parser import parse_survey, extract_survey_id
from backend.config import Config

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
        加载问卷索引 (增强鲁棒性)

        从索引文件中读取问卷元数据，失败时尝试备份文件
        """
        index_file = self.index_file
        backup_file = index_file + ".bak"
        loaded_index = None

        # 1. 尝试加载主索引文件
        if os.path.exists(index_file):
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        loaded_index = json.loads(content)
                        logger.info(f"成功加载主索引文件: {index_file}")
                    else:
                        logger.warning(f"主索引文件 {index_file} 为空")
                        # 文件存在但为空，可能也需要尝试备份
            except json.JSONDecodeError as e:
                logger.error(f"主索引文件 {index_file} JSON 解析错误: {e}")
            except Exception as e:
                logger.error(f"加载主索引文件 {index_file} 时发生未知错误: {e}", exc_info=True)

        # 2. 如果主文件加载失败或为空，尝试加载备份文件
        if loaded_index is None and os.path.exists(backup_file):
            logger.info(f"尝试加载备份索引文件: {backup_file}")
            try:
                with open(backup_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        loaded_index = json.loads(content)
                        logger.info(f"成功从备份文件加载索引: {backup_file}")
                        # 考虑用备份恢复主文件
                        try:
                            shutil.copy2(backup_file, index_file)
                            logger.info(f"已使用备份文件恢复主索引文件: {index_file}")
                        except Exception as copy_e:
                            logger.error(f"从备份恢复主索引文件失败: {copy_e}")
                    else:
                        logger.warning(f"备份索引文件 {backup_file} 为空")
            except json.JSONDecodeError as e:
                logger.error(f"备份索引文件 {backup_file} JSON 解析错误: {e}")
            except Exception as e:
                logger.error(f"加载备份索引文件 {backup_file} 时发生未知错误: {e}", exc_info=True)

        # 3. 如果都失败，初始化为空列表
        if loaded_index is None:
            logger.warning(f"主索引和备份索引均加载失败或为空，创建新索引")
            self.index = []
            # 尝试保存一次空索引以触发备份逻辑（如果可能）
            self._save_index()
        else:
            self.index = loaded_index

    def _save_index(self):
        """
        保存问卷索引 (增强鲁棒性 - 原子写入)

        将问卷元数据写入索引文件，使用临时文件和备份机制
        """
        index_file = self.index_file
        backup_file = index_file + ".bak"
        temp_file = index_file + ".tmp"

        try:
            # 1. 将当前索引写入临时文件
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, ensure_ascii=False, indent=2)

            # 2. 备份原文件（如果存在）
            if os.path.exists(index_file):
                try:
                    shutil.move(index_file, backup_file) # 使用 move 比 copy 更原子
                    logger.debug(f"已备份旧索引文件到: {backup_file}")
                except Exception as backup_e:
                    # 如果备份失败，可能磁盘空间不足或权限问题，仍然尝试继续替换
                    logger.warning(f"备份索引文件失败: {backup_e}. 尝试直接替换...")

            # 3. 将临时文件重命名为正式文件
            shutil.move(temp_file, index_file)
            logger.debug(f"索引已成功保存到: {index_file}")

        except Exception as e:
            logger.error(f"保存索引文件失败: {e}", exc_info=True)
            # 尝试清理临时文件
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception as clean_e:
                    logger.error(f"清理临时索引文件失败: {clean_e}")

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
                parser_result = parse_survey(url) # 接收字典返回值

                # 检查是否解析成功
                if 'error' in parser_result:
                    logger.error(f"解析问卷失败: {parser_result['error']}")
                    raise Exception(parser_result['error'])

                # 获取解析结果
                survey_result = parser_result.get("survey_data", {})
                questions_file_path = parser_result.get("questions_file_path")

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
                survey_file_path = os.path.join(self.surveys_dir, f"{survey_id}_{timestamp}.json")
                logger.info(f"保存问卷数据到文件: {survey_file_path}")
                with open(survey_file_path, 'w', encoding='utf-8') as f:
                    json.dump(survey_data, f, ensure_ascii=False, indent=2)

                # 更新索引
                index_entry = {
                    "id": survey_id,
                    "title": survey_title,
                    "url": url,
                    "created_at": timestamp,
                    "file_path": survey_file_path
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

                # 尝试删除 data/questions_*.json 文件
                if questions_file_path and os.path.exists(questions_file_path):
                    try:
                        os.remove(questions_file_path)
                        logger.info(f"成功删除冗余 questions 文件: {questions_file_path}")
                    except Exception as rm_err:
                        logger.warning(f"删除冗余 questions 文件失败: {questions_file_path}, Error: {rm_err}")
                elif questions_file_path:
                     logger.warning(f"冗余 questions 文件未找到，无法删除: {questions_file_path}")

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
        根据问卷ID获取问卷内容 (优先使用索引)

        Args:
            survey_id (str): 问卷ID

        Returns:
            dict: 问卷内容 或 None
        """
        if not survey_id:
            logger.error("问卷ID为空")
            return None

        logger.info(f"尝试获取问卷 ID: {survey_id}")

        # 1. 先检查缓存
        if survey_id in self.survey_cache:
            logger.info(f"问卷 {survey_id} 从缓存中获取")
            return self.survey_cache[survey_id]

        latest_file = None
        survey_data = None

        try:
            # 确保索引是最新的
            self._load_index()

            # 2. 优先尝试从索引加载
            indexed_path = None
            for entry in self.index:
                if entry.get("id") == survey_id:
                    indexed_path = entry.get("file_path")
                    break

            if indexed_path:
                logger.info(f"在索引中找到问卷 {survey_id} 的记录，路径: {indexed_path}")
                if os.path.exists(indexed_path):
                    try:
                        with open(indexed_path, 'r', encoding='utf-8') as f:
                            survey_data = json.load(f)
                        logger.info(f"成功通过索引加载问卷文件: {indexed_path}")
                        latest_file = indexed_path # 标记已找到文件
                    except json.JSONDecodeError as e:
                        logger.error(f"索引指向的文件 {indexed_path} JSON 解析错误: {e}。将尝试目录搜索。")
                        # 不要在此处 return None，让它继续尝试目录搜索
                    except Exception as e:
                        logger.error(f"读取索引指向的文件 {indexed_path} 时出错: {e}。将尝试目录搜索。")
                        # 不要在此处 return None
                else:
                    logger.warning(f"索引指向的文件 {indexed_path} 不存在。将尝试目录搜索。")
            else:
                logger.info(f"在索引中未找到问卷 {survey_id} 的记录。将尝试目录搜索。")

            # 3. 如果通过索引加载失败，则执行目录搜索作为后备
            if survey_data is None:
                logger.info(f"开始目录搜索问卷文件 (ID: {survey_id})")
                base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
                data_dir = os.path.join(base_dir, 'data')
                surveys_dir = os.path.join(data_dir, 'surveys') # 定义 surveys 目录路径

                latest_time = 0

                # 搜索顺序调整：优先搜索 surveys 目录下的 {id}_*.json，再搜索 data 根目录下的 questions_*.json

                # a. 搜索 data/surveys/ 目录
                if os.path.exists(surveys_dir):
                    logger.debug(f"搜索目录: {surveys_dir}")
                    for filename in os.listdir(surveys_dir):
                        # 要求文件名以 survey_id 开头
                        if filename.startswith(f"{survey_id}_") and filename.endswith('.json'):
                            file_path = os.path.join(surveys_dir, filename)
                            try:
                                file_time = os.path.getmtime(file_path)
                                if file_time > latest_time:
                                    latest_time = file_time
                                    latest_file = file_path
                                    logger.info(f"在 surveys 目录找到更新的文件: {filename}")
                            except OSError as e:
                                logger.warning(f"获取文件时间戳失败: {file_path}, Error: {e}")


                # b. 如果 surveys 目录没找到最新的，再搜索 data/ 根目录 (可能包含旧的 questions 文件)
                # 考虑是否真的需要这一步，或者只加载 surveys 目录的文件？暂时保留作为后备。
                if latest_file is None: # 只有在 surveys 目录没找到才搜索 data 根目录
                    logger.debug(f"未在 surveys 目录找到 {survey_id}_*.json，开始搜索 data 根目录下的 questions_{survey_id}_*.json")
                    if os.path.exists(data_dir):
                        logger.debug(f"搜索目录: {data_dir}")
                        for filename in os.listdir(data_dir):
                            if filename.startswith(f"questions_{survey_id}_") and filename.endswith('.json'):
                                file_path = os.path.join(data_dir, filename)
                                try:
                                    file_time = os.path.getmtime(file_path)
                                    if file_time > latest_time:
                                        latest_time = file_time
                                        latest_file = file_path # 即使是 questions 文件，也作为备选
                                        logger.info(f"在 data 根目录找到 questions 格式文件: {filename}")
                                except OSError as e:
                                    logger.warning(f"获取文件时间戳失败: {file_path}, Error: {e}")

                # 如果通过目录搜索找到了文件，则加载它
                if latest_file:
                    logger.info(f"目录搜索完成，使用最新的文件: {latest_file}")
                    try:
                        with open(latest_file, 'r', encoding='utf-8') as f:
                            survey_data = json.load(f)
                    except Exception as e:
                        logger.error(f"读取目录搜索找到的文件 {latest_file} 时出错: {e}")
                        return None # 如果备用加载也失败，则返回 None
                else:
                    logger.warning(f"通过索引和目录搜索均未找到问卷 ID: {survey_id} 的有效文件")
                    return None # 如果索引和目录搜索都找不到，返回 None

            # 4. 确保最终加载的数据格式正确并添加到缓存
            if survey_data:
                if not isinstance(survey_data, dict):
                    logger.error(f"最终加载的问卷数据格式错误，不是字典: {type(survey_data)}")
                    return None

                if 'id' not in survey_data or survey_data.get('id') != survey_id:
                    # 如果加载的是 questions_*.json，它可能没有 id 字段或 id 不匹配，强制修正
                    survey_data['id'] = survey_id
                    logger.info(f"修正问卷ID为: {survey_id}")

                # 添加到缓存
                self.survey_cache[survey_id] = survey_data
                logger.info(f"问卷 {survey_id} 已添加到缓存")
                return survey_data
            else:
                # 如果 survey_data 仍然是 None（理论上不应该到这里，除非上面逻辑有误）
                logger.error(f"处理问卷 {survey_id} 后数据为空，检查加载逻辑")
                return None

        except Exception as e:
            logger.error(f"获取问卷 {survey_id} 时发生意外错误: {e}", exc_info=True)
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