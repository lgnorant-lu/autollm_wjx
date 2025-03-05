"""
----------------------------------------------------------------
File name:                  task_service.py
Author:                     Ignorant-lu
Date created:               2025/03/05
Description:                任务管理服务，提供问卷任务的创建、查询、执行和管理功能
----------------------------------------------------------------

Changed history:            任务管理服务初始版本
                            2025/03/05: 添加任务状态实时监控功能
                            2025/03/05: 增强任务并发处理能力
----------------------------------------------------------------
"""

import os
import json
import time
import uuid
import logging
import threading
from enum import Enum
from config import Config
from services.survey_service import SurveyService
from core.wjx import WJXSubmitter

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
        self.config = Config()
        self.survey_service = SurveyService()
        
        # 任务目录
        self.tasks_dir = os.path.join(self.config.DATA_DIR, 'tasks')
        os.makedirs(self.tasks_dir, exist_ok=True)
        
        # 任务索引文件
        self.index_file = os.path.join(self.config.DATA_DIR, 'task_index.json')
        
        # 加载任务索引
        self.index = self._load_index()
        
        # 运行中的任务
        self.running_tasks = {}
        
        # 恢复运行中的任务
        # self._restore_running_tasks()
    
    def _load_index(self):
        """
        加载任务索引
        
        从索引文件中读取任务列表
        """
        try:
            if os.path.exists(self.index_file):
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        return json.loads(content)
                    else:
                        logger.warning(f"索引文件 {self.index_file} 为空，创建新索引")
                        return []
            else:
                logger.info(f"索引文件不存在，创建新索引: {self.index_file}")
                return []
        except Exception as e:
            logger.error(f"加载任务索引失败: {e}")
            return []
    
    def _save_index(self):
        """
        保存任务索引
        
        将任务列表写入索引文件
        """
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)
    
    def _run_task(self, task_id, task_data):
        """
        执行任务的线程函数
        
        负责任务的执行和状态更新
        """
        logger.info(f"开始执行任务: {task_id}")
        
        survey = self.survey_service.get_survey_by_id(task_data['survey_id'])
        if not survey:
            self._update_task_status(task_id, 'failed', '找不到问卷数据')
            return
        
        # 初始化提交器
        submitter = WJXSubmitter(survey_url=survey['url'])
        
        # 任务执行参数
        total = task_data['count']
        success_count = 0
        fail_count = 0
        
        # 更新任务状态为运行中
        self._update_task_status(task_id, 'running')
        
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
                # 这里应该调用您现有的生成答案的代码
                # 简化示例:
                answer_data = "1$选项1}2$填空回答"
                
                # 使用代理
                proxy = None
                if task_data.get('use_proxy', False) and task_data.get('proxy_url'):
                    proxy = {
                        'http': task_data['proxy_url'],
                        'https': task_data['proxy_url']
                    }
                
                # 提交问卷
                result = submitter.submit(answer_data, proxy)
                
                if result['success']:
                    success_count += 1
                else:
                    fail_count += 1
                    logger.warning(f"提交失败: {result['message']}")
                
                # 更新进度
                progress = int((i + 1) / total * 100)
                self._update_task_progress(task_id, progress, success_count, fail_count)
                
                # 添加一些随机延迟
                import random
                time.sleep(random.uniform(4, 10))
                
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
        
        生成任务ID，保存任务数据并更新索引
        """
        try:
            task_id = str(uuid.uuid4())
            
            # 确保必要的字段存在
            required_fields = ['survey_id', 'count']
            for field in required_fields:
                if field not in task_data:
                    raise ValueError(f"缺少必要字段: {field}")
            
            # 确保llm_type始终存在
            if task_data.get('use_llm', False) and 'llm_type' not in task_data:
                task_data['llm_type'] = 'aliyun'  # 默认使用阿里云
            
            # 查找问卷信息验证是否存在
            logger.info(f"正在获取问卷: {task_data['survey_id']}")
            survey = self.survey_service.get_survey_by_id(task_data['survey_id'])
            if not survey:
                raise ValueError(f"问卷不存在: {task_data['survey_id']}")
            
            # 创建任务记录
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            task_path = os.path.join(self.tasks_dir, f"{task_id}.json")
            
            task = {
                "id": task_id,
                "survey_id": task_data['survey_id'],
                "count": task_data['count'],
                "created_at": timestamp,
                "updated_at": timestamp,
                "status": "pending",
                "progress": 0,
                "success_count": 0,
                "fail_count": 0,
                "completed_count": 0,
                "total_count": task_data['count'],
                "use_proxy": task_data.get('use_proxy', False),
                "proxy_url": task_data.get('proxy_url', ''),
                "use_llm": task_data.get('use_llm', False),
                "llm_type": task_data.get('llm_type', 'aliyun'),  # 保存LLM类型
                "message": "任务创建成功，等待执行"
            }
            
            # 保存任务数据
            logger.info(f"正在保存任务数据到: {task_path}")
            with open(task_path, 'w', encoding='utf-8') as f:
                json.dump(task, f, ensure_ascii=False, indent=2)
            
            # 更新索引
            index_entry = {
                "id": task_id,
                "survey_id": task_data['survey_id'],
                "created_at": timestamp,
                "status": "pending",
                "file_path": task_path
            }
            self.index.append(index_entry)
            self._save_index()
            
            # 启动任务线程
            logger.info(f"正在启动任务线程: {task_id}")
            task_thread = threading.Thread(
                target=self._submit_task,
                args=(task_id, task),
                daemon=True
            )
            task_thread.start()
            self.running_tasks[task_id] = task_thread
            
            return task_id
        except Exception as e:
            logger.error(f"创建任务异常: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
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
            submitter = WJXSubmitter(survey_url=survey['url'])
            
            # 任务执行参数
            total = task_data.get('count', 1)
            success_count = 0
            fail_count = 0
            
            # 更新任务状态为运行中
            self._update_task_status(task_id, 'running')
            
            # 检查是否使用LLM生成答案
            use_llm = task_data.get('use_llm', False)
            llm_answers = None
            
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
                    
                    # 添加一些随机延迟，避免提交过快被检测
                    import random
                    time.sleep(random.uniform(2, 5))
                    
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
        
        if not survey or 'questions' not in survey:
            logger.error("问卷数据格式错误")
            return ""
        
        questions = survey['questions']
        
        for question in questions:
            try:
                q_index = question.get('index', 0)
                q_type = question.get('type', 0)
                
                # 忽略隐藏题目
                if question.get('is_hidden', False):
                    continue
                    
                # 单选题 (3)
                if q_type == 3:
                    if 'options' in question and len(question['options']) > 0:
                        # 随机选择一个选项
                        option_index = random.randint(0, len(question['options']) - 1)
                        submit_data_parts.append(f"{q_index}${option_index + 1}")
                
                # 多选题 (4)
                elif q_type == 4:
                    if 'options' in question and len(question['options']) > 0:
                        # 随机选择1-3个选项
                        num_options = len(question['options'])
                        num_to_select = min(random.randint(1, 3), num_options)
                        selected_options = random.sample(range(num_options), num_to_select)
                        options_str = ','.join([str(opt + 1) for opt in selected_options])
                        submit_data_parts.append(f"{q_index}${options_str}")
                
                # 填空题 (1)
                elif q_type == 1:
                    # 生成一个简单的填空回答
                    answers = ["很好", "不错", "一般", "满意", "需要改进"]
                    text = random.choice(answers)
                    submit_data_parts.append(f"{q_index}${text}")
                
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
                                submit_data_parts.append(f"{q_index}${','.join(row_answers)}")
                
                # 评分题 (8)
                elif q_type == 8:
                    # 评分题通常是1-5或1-10分
                    max_score = 5
                    if 'options' in question and len(question['options']) > 1:
                        if isinstance(question['options'][1], dict) and 'max' in question['options'][1]:
                            max_score = int(question['options'][1]['max'])
                    
                    score = random.randint(1, max_score)
                    submit_data_parts.append(f"{q_index}${score}")
                
                # 排序题 (11)
                elif q_type == 11:
                    if 'options' in question and len(question['options']) > 0:
                        # 生成随机排序
                        num_options = len(question['options'])
                        order = list(range(1, num_options + 1))
                        random.shuffle(order)
                        order_str = ','.join(map(str, order))
                        submit_data_parts.append(f"{q_index}${order_str}")
                
                # 量表题 (5)
                elif q_type == 5:
                    # 量表题，随机选择一个值
                    scale_max = 5
                    value = random.randint(1, scale_max)
                    submit_data_parts.append(f"{q_index}${value}")
                
                # 如果是其他题型，可以继续添加处理逻辑
                
            except Exception as e:
                logger.error(f"生成问题 {q_index} 的答案时出错: {e}")
                # 跳过这个问题，继续处理下一个
        
        # 将所有部分连接成一个字符串，使用 "}" 分隔
        submit_data = "}".join(submit_data_parts)
        logger.debug(f"生成的提交数据: {submit_data}")
        
        return submit_data 

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