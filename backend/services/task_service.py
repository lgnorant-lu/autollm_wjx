"""
----------------------------------------------------------------
File name:                  task_service.py
Author:                     Ignorant-lu
Date created:               2025/02/16
Description:                任务管理服务，提供问卷任务的创建、查询、执行和管理功能
----------------------------------------------------------------

Changed history:            
                            2025/02/22: 添加任务状态实时监控功能
                            2025/02/25: 增强任务并发处理能力
                            2025/04/17: 增强索引文件读写的鲁棒性
----------------------------------------------------------------
"""

import os
import json
import time
import uuid
import logging
import requests
import threading
import shutil
from enum import Enum
from config import Config
from services.survey_service import SurveyService
from core.wjx import WJXSubmitter
from datetime import datetime

logger = logging.getLogger(__name__)

class TaskService:
    """
    任务管理服务类
    
    负责问卷任务的创建、执行、监控和管理
    提供任务状态跟踪、数据存储和并发执行功能
    """
    def __init__(self):
        """
        初始化任务服务
        
        设置任务存储目录和相关服务
        """
        self.survey_service = SurveyService()
        
        # 任务目录 - 使用 Config 类属性
        self.tasks_dir = Config.TASKS_DIR 
        os.makedirs(self.tasks_dir, exist_ok=True)
        
        # 任务索引文件 - 使用 Config 类属性
        self.index_file = Config.TASK_INDEX_FILE
        
        # 加载任务索引
        self.index = self._load_index()
        
        # 运行中的任务
        self.running_tasks = {}
        
        # 恢复运行中的任务
        # self._restore_running_tasks()
    
    def _load_index(self):
        """
        加载任务索引 (增强鲁棒性)
        
        从索引文件中读取任务列表，失败时尝试备份文件
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
                        logger.info(f"成功加载主任务索引文件: {index_file}")
                    else:
                        logger.warning(f"主任务索引文件 {index_file} 为空")
                        # 文件存在但为空，可能也需要尝试备份
            except json.JSONDecodeError as e:
                logger.error(f"主任务索引文件 {index_file} JSON 解析错误: {e}")
            except Exception as e:
                logger.error(f"加载主任务索引文件 {index_file} 时发生未知错误: {e}", exc_info=True)

        # 2. 如果主文件加载失败或为空，尝试加载备份文件
        if loaded_index is None and os.path.exists(backup_file):
            logger.info(f"尝试加载备份任务索引文件: {backup_file}")
            try:
                with open(backup_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        loaded_index = json.loads(content)
                        logger.info(f"成功从备份文件加载任务索引: {backup_file}")
                        # 考虑用备份恢复主文件
                        try:
                            shutil.copy2(backup_file, index_file)
                            logger.info(f"已使用备份文件恢复主任务索引文件: {index_file}")
                        except Exception as copy_e:
                            logger.error(f"从备份恢复主任务索引文件失败: {copy_e}")
                    else:
                        logger.warning(f"备份任务索引文件 {backup_file} 为空")
            except json.JSONDecodeError as e:
                logger.error(f"备份任务索引文件 {backup_file} JSON 解析错误: {e}")
            except Exception as e:
                logger.error(f"加载备份任务索引文件 {backup_file} 时发生未知错误: {e}", exc_info=True)

        # 3. 如果都失败，初始化为空列表
        if loaded_index is None:
            logger.warning(f"主任务索引和备份索引均加载失败或为空，创建新索引")
            return []
        else:
            return loaded_index
    
    def _save_index(self):
        """
        保存任务索引 (增强鲁棒性 - 原子写入)
        
        将任务列表写入索引文件，使用临时文件和备份机制
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
                    logger.debug(f"已备份旧任务索引文件到: {backup_file}")
                except Exception as backup_e:
                    # 如果备份失败，可能磁盘空间不足或权限问题，仍然尝试继续替换
                    logger.warning(f"备份任务索引文件失败: {backup_e}. 尝试直接替换...")

            # 3. 将临时文件重命名为正式文件
            shutil.move(temp_file, index_file)
            logger.debug(f"任务索引已成功保存到: {index_file}")

        except Exception as e:
            logger.error(f"保存任务索引文件失败: {e}", exc_info=True)
            # 尝试清理临时文件
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception as clean_e:
                    logger.error(f"清理临时任务索引文件失败: {clean_e}")
    
    def _run_task(self, task_id, task_data):
        """
        执行后台任务
        
        在单独线程中执行任务的主要逻辑
        """
        try:
            # 查找问卷
            survey = self.survey_service.get_survey_by_id(task_data['survey_id'])
            if not survey:
                self._update_task_status(task_id, 'failed', message="找不到问卷数据")
                return
            
            # 初始化计数器
            total = task_data.get('count', 1)
            success_count = 0
            fail_count = 0
            
            # 更新任务状态
            self._update_task_status(task_id, 'running')
            
            # 创建提交器
            submitter = WJXSubmitter(survey_url=survey['url'], survey_config=survey)
            
            # 计算问卷复杂度
            survey_complexity = 5  # 默认中等复杂度
            if 'questions' in survey:
                # 基于问题数量和类型计算复杂度
                num_questions = len(survey['questions'])
                complex_types = sum(1 for q in survey['questions'] if q.get('type') in [4, 6, 11])  # 多选、矩阵、排序题
                simple_types = sum(1 for q in survey['questions'] if q.get('type') in [1, 3, 5, 8])  # 填空、单选、量表、评分
                
                # 计算复杂度得分 (0-10)
                survey_complexity = min(10, max(1, num_questions / 5 + complex_types * 0.5))
                logger.info(f"问卷复杂度计算: {survey_complexity:.1f}/10 (问题数: {num_questions}, 复杂问题: {complex_types}, 简单问题: {simple_types})")
            
            # 执行任务
            for i in range(total):
                try:
                    # 生成随机答案
                    answer_data = self._generate_answer_data(survey)
                    
                    # 提交问卷
                    result = submitter.submit(answer_data)
                    
                    if result.get('success', False):
                        success_count += 1
                        logger.info(f"任务提交成功: {task_id}, 进度: {i+1}/{total}")
                    else:
                        fail_count += 1
                        logger.warning(f"任务提交失败: {task_id}, 进度: {i+1}/{total}, 错误: {result.get('message', '未知错误')}")
                    
                    # 更新进度
                    progress = int((i + 1) / total * 100)
                    self._update_task_progress(task_id, progress, success_count, fail_count)
                    
                    # 添加模拟人类行为的随机延迟
                    delay = self._generate_human_like_delay(i + 1, total, survey_complexity)
                    time.sleep(delay)
                    
                except Exception as e:
                    fail_count += 1
                    logger.error(f"任务执行异常: {e}")
                    self._update_task_progress(task_id, 
                                              int((i + 1) / total * 100), 
                                              success_count, 
                                              fail_count)
            
            # 任务完成
            final_status = 'completed' if success_count > 0 else 'failed'
            self._update_task_status(task_id, final_status)
            logger.info(f"任务执行完成: {task_id}, 成功: {success_count}, 失败: {fail_count}")
        
        except Exception as e:
            logger.error(f"任务执行失败: {e}", exc_info=True)
            self._update_task_status(task_id, 'failed', message=f"执行错误: {str(e)}")
    
    def _update_task_status(self, task_id, status, message=None):
        """
        更新任务状态
        
        修改任务状态并保存到文件
        """
        task_file = os.path.join(self.tasks_dir, f"{task_id}.json")
        try:
            with open(task_file, 'r', encoding='utf-8') as f:
                task_data = json.load(f)
            
            task_data['status'] = status
            if message:
                task_data['message'] = message
            task_data['updated_at'] = time.strftime("%Y-%m-%d %H:%M:%S")
            
            with open(task_file, 'w', encoding='utf-8') as f:
                json.dump(task_data, f, ensure_ascii=False, indent=2)
            
            # 更新索引
            for task in self.index:
                if task['id'] == task_id:
                    task['status'] = status
                    break
            self._save_index()
            
            return True
        except Exception as e:
            logger.error(f"更新任务状态失败 {task_id}: {e}")
            return False
    
    def _update_task_progress(self, task_id, progress, success_count, fail_count):
        """
        更新任务进度
        
        修改任务进度并保存到文件
        """
        task_file = os.path.join(self.tasks_dir, f"{task_id}.json")
        try:
            with open(task_file, 'r', encoding='utf-8') as f:
                task_data = json.load(f)
            
            # 计算进度，确保在0-100之间
            progress = min(max(0, progress), 100)
            
            # 更新任务数据
            task_data['progress'] = progress
            task_data['success_count'] = success_count
            task_data['fail_count'] = fail_count
            task_data['completed_count'] = success_count + fail_count
            task_data['total_count'] = task_data.get('count', 0)
            task_data['updated_at'] = time.strftime("%Y-%m-%d %H:%M:%S")
            
            # 如果所有提交都完成了，更新状态为完成
            if task_data['completed_count'] >= task_data['total_count']:
                task_data['status'] = 'completed'
                task_data['progress'] = 100
            
            with open(task_file, 'w', encoding='utf-8') as f:
                json.dump(task_data, f, ensure_ascii=False, indent=2)
            
            # 更新索引
            for task in self.index:
                if task['id'] == task_id:
                    task['progress'] = progress
                    if task_data['status'] == 'completed':
                        task['status'] = 'completed'
                    break
            self._save_index()
            
            return True
        except Exception as e:
            logger.error(f"更新任务进度失败 {task_id}: {e}")
            return False
    
    def create_task(self, task_data):
        """
        创建新任务
        
        创建新的问卷提交任务
        """
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 验证必需字段
        required_fields = ['survey_id']
        for field in required_fields:
            if field not in task_data:
                raise ValueError(f"缺少必需字段: {field}")
        
        # 设置默认值
        defaults = {
            'count': 1,
            'use_proxy': False,
            'proxy_url': '',
            'use_llm': False,
            'llm_type': 'aliyun'
        }
        
        for field, value in defaults.items():
            if field not in task_data:
                task_data[field] = value
        
        # 获取问卷信息
        logger.info(f"正在获取问卷: {task_data['survey_id']}")
        survey = self.survey_service.get_survey_by_id(task_data['survey_id'])
        
        if not survey:
            # # 尝试重新解析问卷 # 注释掉或删除这部分
            # try:
            #     url = None
            #     # 检查是否已经有完整URL
            #     if 'url' in task_data and task_data['url']:
            #         url = task_data['url']
            #         # 确保URL有正确的协议
            #         if not url.startswith('http'):
            #             url = 'https://' + url
            #     else:
            #         # 构建默认URL
            #         url = f"https://www.wjx.cn/vm/{task_data['survey_id']}.aspx"
            #     
            #     logger.info(f"尝试重新解析问卷: {url}")
            #     survey = self.survey_service.parse_survey(url)
            #     if not survey:
            #         raise ValueError(f"问卷不存在 {task_data['survey_id']}")
            # except Exception as e:
            #     logger.error(f"重新解析问卷失败: {e}")
            #     raise ValueError(f"问卷不存在 {task_data['survey_id']}")
            raise ValueError(f"问卷不存在或加载失败: {task_data['survey_id']}，请确保在创建任务前已成功解析问卷。")
        
        # 创建任务数据
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        task = {
            'id': task_id,
            'survey_id': task_data['survey_id'],
            'count': task_data['count'],
            'created_at': now,
            'updated_at': now,
            'status': 'pending',
            'progress': 0,
            'success_count': 0,
            'fail_count': 0,
            'completed_count': 0,
            'total_count': task_data['count'],
            'use_proxy': task_data['use_proxy'],
            'proxy_url': task_data['proxy_url'],
            'use_llm': task_data['use_llm'],
            'llm_type': task_data['llm_type'],
            'message': '任务创建成功，等待执行'
        }
        
        # 保存任务
        try:
            file_path = os.path.join(self.tasks_dir, f"{task_id}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(task, f, ensure_ascii=False, indent=2)
            
            # 更新索引
            self.index.append({
                'id': task_id,
                'survey_id': task_data['survey_id'],
                'created_at': now,
                'status': 'pending',
                'file_path': file_path
            })
            self._save_index()
            
            # 启动后台任务
            thread = threading.Thread(
                target=self._submit_task,
                args=(task_id, task)
            )
            thread.daemon = True
            thread.start()
            
            logger.info(f"任务创建成功: {task_id}")
            return task_id
        except Exception as e:
            logger.error(f"创建任务异常: {e}", exc_info=True)
            raise Exception(f"创建任务失败: {str(e)}")
    
    def get_all_tasks(self):
        """
        获取所有任务
        
        返回任务索引列表
        """
        return self.index
    
    def get_task_by_id(self, task_id):
        """
        获取指定任务详情
        
        根据任务ID查找任务数据
        """
        for entry in self.index:
            if entry["id"] == task_id:
                try:
                    with open(entry["file_path"], 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    logger.error(f"读取任务数据失败 {task_id}: {e}")
                    return None
        return None
    
    def update_task_status(self, task_id, status):
        """
        更新任务状态
        
        根据任务ID更新任务状态
        """
        task = self.get_task_by_id(task_id)
        if not task:
            return False
        
        current_status = task['status']
        
        if status == current_status:
            return True  # 状态没变，视为成功
        
        if status == 'running':
            # 启动任务
            if current_status in ['created', 'paused']:
                # 更新状态
                if self._update_task_status(task_id, 'running'):
                    # 如果任务不在运行中，则启动线程
                    if task_id not in self.running_tasks or not self.running_tasks[task_id].is_alive():
                        task_thread = threading.Thread(
                            target=self._run_task,
                            args=(task_id, task)
                        )
                        task_thread.daemon = True
                        task_thread.start()
                        self.running_tasks[task_id] = task_thread
                    return True
            return False
            
        elif status == 'paused':
            # 暂停任务
            if current_status == 'running':
                return self._update_task_status(task_id, 'paused')
            return False
            
        elif status == 'stopped':
            # 停止任务
            if current_status in ['running', 'paused']:
                return self._update_task_status(task_id, 'stopped')
            return False
            
        return False
    
    def delete_task(self, task_id):
        """
        删除任务
        
        根据任务ID删除任务数据和索引
        """
        for i, entry in enumerate(self.index):
            if entry["id"] == task_id:
                try:
                    # 确保任务已停止
                    self.update_task_status(task_id, 'stopped')
                    
                    # 删除任务文件
                    if os.path.exists(entry["file_path"]):
                        os.remove(entry["file_path"])
                    
                    # 更新索引
                    self.index.pop(i)
                    self._save_index()
                    
                    # 从运行任务字典中移除
                    if task_id in self.running_tasks:
                        del self.running_tasks[task_id]
                    
                    return True
                except Exception as e:
                    logger.error(f"删除任务失败 {task_id}: {e}")
                    return False
        return False 

    def _submit_task(self, task_id, task_data):
        """
        执行提交任务
        
        负责任务的提交和状态更新
        """
        try:
            logger.info(f"开始执行任务: {task_id}")
            
            # 查找问卷信息
            survey = self.survey_service.get_survey_by_id(task_data['survey_id'])
            if not survey:
                self._update_task_status(task_id, 'failed', error="问卷不存在")
                return
            
            # 创建提交器实例
            submitter = WJXSubmitter(survey_url=survey['url'], survey_config=survey)
            
            # 任务执行参数
            total = task_data.get('count', 1)
            success_count = 0
            fail_count = 0
            
            # 更新任务状态为运行中
            self._update_task_status(task_id, 'running')
            
            # 检查是否使用LLM生成答案
            use_llm = task_data.get('use_llm', False)
            llm_answers = None
            
            # 计算问卷复杂度
            survey_complexity = 5  # 默认中等复杂度
            if 'questions' in survey:
                # 基于问题数量和类型计算复杂度
                num_questions = len(survey['questions'])
                complex_types = sum(1 for q in survey['questions'] if q.get('type') in [4, 6, 11])  # 多选、矩阵、排序题
                simple_types = sum(1 for q in survey['questions'] if q.get('type') in [1, 3, 5, 8])  # 填空、单选、量表、评分
                
                # 计算复杂度得分 (0-10)
                survey_complexity = min(10, max(1, num_questions / 5 + complex_types * 0.5))
                logger.info(f"问卷复杂度计算: {survey_complexity:.1f}/10 (问题数: {num_questions}, 复杂问题: {complex_types}, 简单问题: {simple_types})")
            
            # 如果使用LLM，生成答案数据
            if use_llm:
                try:
                    from core.llm_generator import LLMGenerator
                    
                    # 使用任务数据中的模型类型
                    llm_type = task_data.get('llm_type', 'aliyun')
                    logger.info(f"使用LLM生成器类型: {llm_type}")
                    
                    # 根据不同模型类型获取对应环境变量中的API密钥
                    api_key = None
                    if llm_type == 'aliyun':
                        api_key = "sk-5662a97464e1404d8c6a06c68520abf6"
                        logger.info("使用阿里云百炼API密钥")
                        logger.debug(f"API密钥: {api_key}")
                    
                    # 初始化LLM生成器
                    llm_gen = LLMGenerator(model_type=llm_type, api_key=api_key)
                    
                    # 调用生成答案
                    llm_answers = llm_gen.generate_answers(survey)
                    logger.info(f"已使用{llm_type}模型生成答案数据")
                    logger.debug(f"LLM生成的答案字典: {llm_answers}")
                    
                    # 将答案字典转换为问卷星提交格式
                    formatted_answers = []
                    for idx, value in llm_answers.items():
                        formatted_answers.append(f"{idx}${value}")
                    answer_data = "}".join(formatted_answers)
                    logger.info(f"转换后的提交格式: {answer_data}")
                    
                except Exception as e:
                    logger.error(f"LLM生成答案失败: {e}", exc_info=True)
                    # 回退到随机生成
                    use_llm = False
                    answer_data = self._generate_answer_data(survey)
            
            # 执行任务
            task_file = os.path.join(self.tasks_dir, f"{task_id}.json")
            
            for i in range(total):
                # 检查任务状态
                with open(task_file, 'r', encoding='utf-8') as f:
                    current_task = json.load(f)
                
                if current_task['status'] != 'running':
                    logger.info(f"任务已暂停或停止: {task_id}")
                    break
                
                # 生成提交数据
                try:
                    # 根据设置选择答案生成方式
                    if use_llm:
                        # 直接使用已经格式化好的答案数据
                        logger.info(f"使用LLM生成的答案: {answer_data}")
                    else:
                        # 使用随机生成的答案
                        answer_data = self._generate_answer_data(survey)
                    
                    # 使用代理
                    proxy = None
                    if task_data.get('use_proxy', False) and task_data.get('proxy_url'):
                        proxy_url = task_data['proxy_url'].strip()
                        if proxy_url:
                            try:
                                # 测试代理连接
                                test_response = requests.get(
                                    'https://www.baidu.cn',
                                    proxies={'http': proxy_url, 'https': proxy_url},
                                    timeout=5
                                )
                                # 如果能连接成功，设置代理
                                if test_response.status_code == 200:
                                    proxy = {'http': proxy_url, 'https': proxy_url}
                                    logger.info(f"成功连接代理: {proxy_url}")
                                else:
                                    logger.warning(f"代理连接测试失败: {proxy_url}, 状态码: {test_response.status_code}")
                            except Exception as e:
                                logger.warning(f"代理连接测试异常: {proxy_url}, 错误: {e}")
                                # 继续不使用代理
                    
                    # 如果代理测试失败，使用直接连接
                    if task_data.get('use_proxy', False) and not proxy:
                        logger.warning(f"代理连接失败，将使用直接连接方式提交")
                    
                    # 提交问卷
                    result = submitter.submit(answer_data, proxy)
                    
                    if result.get('success', False):
                        success_count += 1
                        logger.info(f"任务 {task_id}: 第 {i+1}/{total} 次提交成功")
                    else:
                        fail_count += 1
                        logger.warning(f"任务 {task_id}: 第 {i+1}/{total} 次提交失败: {result.get('message', '未知错误')}")
                    
                    # 更新进度
                    progress = int((i + 1) / total * 100)
                    self._update_task_progress(task_id, progress, success_count, fail_count)
                    
                    # 添加模拟人类行为的随机延迟
                    delay = self._generate_human_like_delay(i + 1, total, survey_complexity)
                    time.sleep(delay)
                    
                except Exception as e:
                    fail_count += 1
                    logger.error(f"任务 {task_id}: 单次提交异常: {e}")
                    self._update_task_progress(task_id, 
                                               int((i + 1) / total * 100), 
                                               success_count, 
                                               fail_count)
                    # 出错后短暂等待
                    time.sleep(3)
            
            # 任务完成
            final_status = 'completed' if success_count > 0 else 'failed'
            final_msg = f"完成: 成功{success_count}次, 失败{fail_count}次"
            self._update_task_status(task_id, final_status, message=final_msg)
            logger.info(f"任务执行完成: {task_id}, {final_msg}")
            
        except Exception as e:
            logger.error(f"提交任务失败: {e}", exc_info=True)
            self._update_task_status(task_id, 'failed', error=str(e)) 

    def _generate_answer_data(self, survey):
        """
        根据问卷数据生成答案
        
        自动生成答案数据
        """
        import random
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
                
                # 矩阵单选题 (6)
                elif q_type == 6:
                    if 'options' in question and isinstance(question['options'], list):
                        if question['options'] and isinstance(question['options'][0], list):
                            # 对每行随机选择一个选项
                            row_answers = []
                            for i in range(len(question['options'])):
                                # 对每行随机选择一个选项
                                cols = len(question['options'][i])
                                if cols > 0:
                                    col_index = random.randint(0, cols - 1)
                                    row_answers.append(str(col_index + 1))
                            
                            if row_answers:
                                answer = ','.join(row_answers)
                                submit_data_parts.append(f"{q_index}${answer}")
                                logger.debug(f"矩阵题 {q_index} 回答: {answer}")
                
                # 评分题 (8)
                elif q_type == 8:
                    # 评分题通常是1-5或1-10分
                    max_score = 5
                    if 'options' in question and len(question['options']) > 1:
                        if isinstance(question['options'][1], dict) and 'max' in question['options'][1]:
                            max_score = int(question['options'][1]['max'])
                    
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
                        order_str = '|'.join(map(str, order))
                        submit_data_parts.append(f"{q_index}${order_str}")
                        logger.debug(f"排序题 {q_index} 排序: {order_str}")
                
                # 量表题 (5)
                elif q_type == 5:
                    # 量表题，随机选择一个值
                    scale_max = 5
                    value = random.randint(1, scale_max)
                    submit_data_parts.append(f"{q_index}${value}")
                    logger.debug(f"量表题 {q_index} 选择: {value}")
                
                # 如果是其他题型，记录日志
                else:
                    logger.warning(f"未处理的题型 {q_type} 题目ID: {q_index}, 题目: {q_title}")
                
            except Exception as e:
                logger.error(f"生成问题 {q_index} 的答案时出错: {e}", exc_info=True)
                # 跳过这个问题，继续处理下一个
        
        # 将所有部分连接成一个字符串，使用 "}" 分隔
        submit_data = "}".join(submit_data_parts)
        logger.info(f"生成的提交数据包含 {len(submit_data_parts)} 个题目答案")
        
        return submit_data

    def _generate_human_like_delay(self, current_task_num, total_tasks, survey_complexity=None):
        """
        生成模拟人类行为的随机延迟时间
        
        根据当前任务进度、问卷复杂度等因素自适应调整延迟时间
        
        Args:
            current_task_num: 当前是第几个任务
            total_tasks: 总任务数
            survey_complexity: 问卷复杂度（可选，由问题数量和类型决定）
            
        Returns:
            float: 延迟时间（秒）
        """
        import random
        import math
        
        # 基础延迟范围
        base_min_delay = 5
        base_max_delay = 15
        
        # 1. 任务进度因素：开始和结束时更慢，中间更快
        progress_ratio = current_task_num / total_tasks
        
        # 使用正态分布模拟：开始较慢，中间加速，结束前变慢
        # 这样的曲线更接近真实人类行为模式
        progress_factor = 1 - 0.5 * math.exp(-(pow(progress_ratio - 0.5, 2) / 0.05))
        
        # 2. 引入自然变化：使用韦伯尔分布为延迟添加随机性
        # 这种分布比简单的均匀分布更接近人类随机性
        randomness = random.weibullvariate(1, 2) 
        while randomness > 3:  # 限制极端值
            randomness = random.weibullvariate(1, 2)
        
        # 3. 时间段调整：如果能获取到当前时间，可以根据时间段调整
        import datetime
        current_hour = datetime.datetime.now().hour
        time_factor = 1.0
        
        # 人们在不同时间段填写问卷的速度不同
        if 0 <= current_hour < 7:  # 深夜/凌晨：更慢
            time_factor = 1.3
        elif 7 <= current_hour < 12:  # 上午：正常
            time_factor = 1.0
        elif 12 <= current_hour < 14:  # 午休：较慢
            time_factor = 1.2
        elif 14 <= current_hour < 18:  # 下午：较快
            time_factor = 0.9
        elif 18 <= current_hour < 22:  # 晚上：正常
            time_factor = 1.0
        else:  # 深夜：较慢
            time_factor = 1.1
            
        # 4. 复杂度调整：根据问卷复杂度调整时间
        complexity_factor = 1.0
        if survey_complexity:
            # 简单问卷填写更快，复杂问卷填写更慢
            complexity_factor = 0.8 + (survey_complexity / 10) * 0.4  # 复杂度0-10的映射
        
        # 5. 批量提交因素：连续提交多个问卷时，后面的提交速度会加快
        batch_factor = 1.0
        if total_tasks > 5:
            # 批量任务中，速度会逐渐加快，但到最后会略微放慢
            batch_curve = 1 - 0.3 * (progress_ratio * (1 - progress_ratio * 0.3))
            batch_factor = max(0.7, batch_curve)
        
        # 6. 随机中断：模拟人类可能的暂停
        if random.random() < 0.05:  # 5%的概率出现较长暂停
            return random.uniform(20, 40)  # 随机暂停20-40秒
            
        # 计算最终延迟时间
        final_min_delay = base_min_delay * progress_factor * time_factor * complexity_factor * batch_factor
        final_max_delay = base_max_delay * progress_factor * time_factor * complexity_factor * batch_factor
        
        # 确保延迟时间在合理范围内
        final_min_delay = max(2, min(final_min_delay, 25))
        final_max_delay = max(final_min_delay + 2, min(final_max_delay, 40))
        
        # 应用随机因子并返回最终延迟
        delay = final_min_delay + (final_max_delay - final_min_delay) * randomness / 3
        
        # 记录延迟时间供调试
        logger.debug(f"生成的人类模拟延迟: {delay:.2f}秒 (进度: {progress_ratio:.2f}, 时间因子: {time_factor}, 复杂度: {complexity_factor})")
        
        return delay
        
    def get_tasks_paginated(self, page=1, page_size=10, sort_field='created_at', sort_order='desc'):
        """
        获取分页任务列表
        
        根据页码和每页记录数返回任务列表
        """
        tasks = []
        
        # 遍历索引获取详细任务信息
        for entry in self.index:
            try:
                with open(entry["file_path"], 'r', encoding='utf-8') as f:
                    task = json.load(f)
                    tasks.append(task)
            except Exception as e:
                logger.error(f"读取任务数据失败 {entry['id']}: {e}")
        
        # 排序
        reverse = sort_order.lower() == 'desc'
        
        # 处理不同类型的字段排序
        if sort_field in ['progress', 'count', 'success_count', 'fail_count']:
            # 数值型字段
            tasks.sort(key=lambda x: float(x.get(sort_field, 0) or 0), reverse=reverse)
        elif sort_field in ['created_at', 'updated_at']:
            # 时间型字段
            tasks.sort(key=lambda x: x.get(sort_field, ''), reverse=reverse)
        else:
            # 字符串型字段
            tasks.sort(key=lambda x: str(x.get(sort_field, '')), reverse=reverse)
        
        # 计算分页
        total = len(tasks)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        # 返回当前页的数据
        return tasks[start_idx:end_idx], total