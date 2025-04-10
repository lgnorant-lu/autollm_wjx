import logging
from backend.core.parser import parse_survey, save_questions, extract_survey_id
from backend.core.optimizer import optimize_question_data
from backend.core.llm_generator import LLMGenerator
from backend.utils.ip_tracker import IPUsageTracker, get_current_ip
from backend.config import get_config

import time
import random
from datetime import datetime
import json
import os
import requests
from backend.core.wjx import WJXSubmitter
import concurrent.futures
from tqdm import tqdm
import glob

# 获取配置
config = get_config()

# 配置日志
logging.basicConfig(
    level=config.log_level_value,
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(config.PROXY_LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class SurveyTask:
    """问卷任务管理器"""
    
    def __init__(self, survey_url, questions_path, target_num=100, max_workers=5, use_proxy=None, proxy_url=None):
        """
        初始化问卷任务
        
        Args:
            survey_url: 问卷地址
            questions_path: 解析后的问卷题目JSON路径
            target_num: 目标提交数量
            max_workers: 最大并发数
            use_proxy: 是否使用代理，如果为None则使用配置中的默认设置
            proxy_url: 代理服务器URL，如果为None则使用配置中的默认URL
        """
        self.survey_url = survey_url
        self.questions_path = questions_path
        self.target_num = target_num
        self.max_workers = max_workers
        self.use_proxy = config.USE_PROXY if use_proxy is None else use_proxy
        self.proxy_url = config.DEFAULT_PROXY_URL if proxy_url is None else proxy_url
        self.submitter = WJXSubmitter(survey_url)
        self.ip_tracker = IPUsageTracker()
        
        # 加载问卷题目数据并规范化格式
        try:
            with open(questions_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 检查并统一数据格式
            if isinstance(data, list):
                # 如果是Question对象列表（直接从parser输出）
                self.question_data = {'questions': data}
            elif isinstance(data, dict) and 'questions' in data:
                # 如果已经是统一格式
                self.question_data = data
            else:
                # 不支持的格式
                logger.error(f"不支持的问卷数据格式，将尝试转换: {type(data)}")
                self.question_data = {'questions': data if isinstance(data, list) else [data]}
        except Exception as e:
            logger.error(f"加载问卷数据失败: {e}")
            self.question_data = {'questions': []}
            
        # 初始化进度条
        self.progress_bar = None
        
    def generate_answer_data(self, proxy_ip=None):
        """生成问卷答案数据"""
        submit_data_parts = []
        
        # 检查数据格式，确保与预期一致
        if isinstance(self.question_data, list):
            # 如果是列表（可能是从parser直接转换的dataclass列表），转换为预期的字典格式
            questions = self.question_data
        elif isinstance(self.question_data, dict) and 'questions' in self.question_data:
            # 如果是字典并且有questions字段，直接使用
            questions = self.question_data['questions']
        else:
            logger.error(f"不支持的问卷数据格式: {type(self.question_data)}")
            return ""
        
        for question in questions:
            # 检查并规范化问题数据
            if isinstance(question, dict):
                # 如果是从JSON加载的字典
                q_index = question.get('index')
                q_type = question.get('type')
                is_hidden = question.get('is_hidden', False)
            else:
                # 如果是dataclass对象
                q_index = getattr(question, 'index', None)
                q_type = getattr(question, 'type', None)
                is_hidden = getattr(question, 'is_hidden', False)
            
            if q_index is None or q_type is None:
                logger.warning(f"跳过无效题目: {question}")
                continue
            
            if is_hidden:
                logger.debug(f"跳过隐藏题目: {q_index}")
                continue
            
            # 根据题型生成更真实的回答
            if q_type == 1:  # 填空题
                # 使用更多样化的回答
                if 'title' in question and question['title']:
                    # 根据题目内容生成相关回答
                    if '姓名' in question['title']:
                        names = ['张三', '李四', '王五', '赵六', '陈七', '刘八']
                        text = random.choice(names)
                    elif '电话' in question['title'] or '手机' in question['title']:
                        text = f"1{random.choice(['3', '5', '7', '8', '9'])}{random.randint(100000000, 999999999)}"
                    elif '邮箱' in question['title'] or 'email' in question['title'].lower():
                        domains = ['qq.com', '163.com', 'gmail.com', 'outlook.com', 'hotmail.com']
                        text = f"user{random.randint(1000, 9999)}@{random.choice(domains)}"
                    else:
                        # 一般性文本回答
                        texts = [
                            f"这是第{random.randint(1, 10)}次参与此类问卷", 
                            "希望我的回答有所帮助",
                            "感谢您的问卷调查",
                            "我认为这很重要",
                            "没有特别的想法"
                        ]
                        text = random.choice(texts)
                else:
                    text = f"回答{random.randint(1, 100)}"
                submit_data_parts.append(f"{q_index}${text}")
                
            elif q_type == 6:  # 矩阵单选题
                if 'matrix_options' in question and 'matrix_rows' in question:
                    row_answers = []
                    for row_idx, _ in enumerate(question['matrix_rows']):
                        # 为每行随机选择一个选项
                        option_idx = random.randint(1, len(question['matrix_options']))
                        row_answers.append(f"{row_idx+1}_{option_idx}")
                    matrix_answer = '|'.join(row_answers)
                    submit_data_parts.append(f"{q_index}${matrix_answer}")
            
            elif q_type == 3:  # 单选题
                if question['options']:
                    # 根据ratio选择选项，优化权重选择逻辑
                    option_index = self._weighted_choice(question['ratio'] if 'ratio' in question else None)
                    submit_data_parts.append(f"{q_index}${option_index}")
                
            elif q_type == 4:  # 多选题
                if question['options']:
                    # 改进多选题的选择逻辑
                    min_choices = 1
                    max_choices = min(3, len(question['options']))
                    
                    # 如果题目中有"最多选择X项"的提示
                    if 'title' in question and question['title']:
                        title = question['title']
                        import re
                        max_match = re.search(r'最多选择(\d+)项', title)
                        if max_match:
                            max_choices = min(int(max_match.group(1)), len(question['options']))
                    
                    num_choices = random.randint(min_choices, max_choices)
                    
                    # 使用带权重的选择
                    weights = question.get('ratio', [1] * len(question['options']))
                    options = []
                    
                    # 确保不重复选择
                    available_options = list(range(1, len(question['options'])+1))
                    for _ in range(num_choices):
                        if not available_options:
                            break
                        idx = self._weighted_choice_from_list(available_options, weights[:len(available_options)])
                        options.append(idx)
                        available_options.remove(idx)
                    
                    options_str = '|'.join(map(str, sorted(options)))
                    submit_data_parts.append(f"{q_index}${options_str}")
                    
            elif q_type == 8:  # 评分题
                # 评分题通常是1-5或1-10分
                max_score = 5  # 默认5分制
                if 'max_score' in question:
                    max_score = question['max_score']
                score = random.randint(3, max_score)  # 稍微偏向高评分
                submit_data_parts.append(f"{q_index}${score}")
                
            elif q_type == 11:  # 排序题
                if 'options' in question:
                    num_options = len(question['options'])
                    # 生成随机排序
                    order = list(range(1, num_options + 1))
                    random.shuffle(order)
                    order_str = '|'.join(map(str, order))
                    submit_data_parts.append(f"{q_index}${order_str}")
                    
            elif q_type == 5:  # 量表题
                # 通常是李克特量表，1-5或1-7分
                scale_max = 5
                if 'scale_max' in question:
                    scale_max = question['scale_max']
                value = random.randint(1, scale_max)
                submit_data_parts.append(f"{q_index}${value}")
                
            elif q_type == 6:  # 矩阵量表题
                if 'matrix_rows' in question:
                    row_answers = []
                    scale_max = question.get('scale_max', 5)
                    for row_idx, _ in enumerate(question['matrix_rows']):
                        # 为每行随机选择一个评分
                        score = random.randint(1, scale_max)
                        row_answers.append(f"{row_idx+1}_{score}")
                    answer = '|'.join(row_answers)
                    submit_data_parts.append(f"{q_index}${answer}")
                    
            elif q_type == 9:  # 多项填空题
                if 'blank_items' in question:
                    item_answers = []
                    for item_idx, item in enumerate(question['blank_items']):
                        # 根据不同的填空项生成答案
                        text = f"填空项{item_idx+1}的回答"
                        item_answers.append(f"{item_idx+1}_{text}")
                    answer = '|'.join(item_answers)
                    submit_data_parts.append(f"{q_index}${answer}")
            
            # 更多题型处理可以在这里添加...
            
        return '}'.join(submit_data_parts)
    
    def _weighted_choice(self, weights):
        """根据权重随机选择"""
        if not weights:
            return 1  # 默认返回第一个选项
            
        total = sum(weights)
        r = random.uniform(0, total)
        upto = 0
        for i, w in enumerate(weights):
            upto += w
            if upto >= r:
                return i + 1  # 选项索引从1开始
        return 1
    
    def _weighted_choice_from_list(self, options, weights):
        """从给定选项列表中按权重随机选择"""
        # 如果没有权重或权重长度不对，使用均匀分布
        if not weights or len(weights) != len(options):
            return random.choice(options)
            
        # 标准化权重
        total = sum(weights)
        if total <= 0:
            return random.choice(options)
            
        weights = [w/total for w in weights]
        r = random.random()
        upto = 0
        for i, w in enumerate(weights):
            upto += w
            if upto >= r:
                return options[i]
        return options[-1]  # 保险起见返回最后一个
    
    def submit_single_task(self, task_id):
        """提交单个问卷任务"""
        # 修改这里的代理IP获取逻辑
        proxy_ip = get_current_ip(self.proxy_url) if self.use_proxy else None
        
        try:
            # 生成答案数据
            submit_data = self.generate_answer_data(proxy_ip)
            # print(submit_data)
            logging.debug("拦截请求数据:", submit_data)
            
            # 提交问卷
            result = self.submitter.submit(submit_data)
            
            # 记录结果
            if proxy_ip:
                self.ip_tracker.record_usage(proxy_ip, result['success'])
                
            # 更新进度条
            if self.progress_bar:
                self.progress_bar.update(1)
                
            # 随机等待
            time.sleep(random.uniform(1, 3))
            
            return result['success']
            
        except Exception as e:
            logger.error(f"任务 {task_id} 执行失败: {e}")
            if proxy_ip:
                self.ip_tracker.record_usage(proxy_ip, False)
            return False
    
    def run(self):
        """执行批量提交任务"""
        success_count = 0
        failed_count = 0
        
        logger.info(f"开始批量提交问卷任务, 目标数量: {self.target_num}")
        
        # 创建进度条
        self.progress_bar = tqdm(total=self.target_num, desc="问卷提交进度")
        
        # 使用线程池并发提交
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self.submit_single_task, i) for i in range(self.target_num)]
            
            for future in concurrent.futures.as_completed(futures):
                if future.result():
                    success_count += 1
                else:
                    failed_count += 1
                    
                # 如果失败次数过多, 提前终止
                if failed_count >= self.target_num // 2:
                    logger.error("失败次数过多, 提前终止任务")
                    break
        
        # 关闭进度条
        self.progress_bar.close()
        self.progress_bar = None
        
        # 输出统计信息
        logger.info(f"任务完成! 成功: {success_count}, 失败: {failed_count}")
        
        # 输出IP使用统计
        stats = self.ip_tracker.get_statistics()
        logger.info("\n=== IP使用统计 ===")
        logger.info(f"总计使用IP数: {stats['total_ips']}")
        logger.info(f"总请求次数: {stats['total_requests']}")
        logger.info(f"成功率: {stats['success_rate']:.2%}")
        
        return {
            "success": success_count, 
            "failed": failed_count,
            "ip_stats": stats
        }


def cleanup_data_files(directory=None, keep_days=None, pattern=None):
    """
    清理旧的数据文件
    
    Args:
        directory: 数据目录，如果为None则使用配置中的数据目录
        keep_days: 保留的天数，如果为None则使用配置中的设置
        pattern: 文件名匹配模式，如果为None则匹配所有文件
    """
    import os
    import time
    import glob
    from datetime import datetime, timedelta
    
    # 如果参数未指定，使用配置中的默认值
    if directory is None:
        directory = config.DATA_DIR
        
    if keep_days is None:
        keep_days = config.DATA_RETENTION_DAYS
    
    logger.info(f"开始清理数据文件，保留最近{keep_days}天的文件")
    
    # 获取当前时间
    now = time.time()
    # 计算保留时间界限
    cutoff = now - (keep_days * 24 * 60 * 60)
    
    # 获取所有文件
    if pattern:
        files = glob.glob(os.path.join(directory, pattern))
    else:
        files = glob.glob(os.path.join(directory, "*"))
    
    removed = 0
    kept = 0
    
    for f in files:
        if os.path.isfile(f):
            # 获取文件修改时间
            mtime = os.path.getmtime(f)
            if mtime < cutoff:
                try:
                    os.remove(f)
                    logger.debug(f"已删除旧文件: {f}")
                    removed += 1
                except Exception as e:
                    logger.error(f"删除文件失败 {f}: {e}")
            else:
                kept += 1
    
    logger.info(f"清理完成: 删除{removed}个文件，保留{kept}个文件")
    return removed, kept

def main():
    # 问卷URL
    url = "https://www.wjx.cn/vm/wWwct2F.aspx"
    # url = "https://www.wjx.cn/vm/hxxt2Oe.aspx"
    
    # 从URL中提取问卷ID
    survey_id = extract_survey_id(url)
    
    # 创建时间戳
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    
    # 创建日志目录
    os.makedirs(config.LOG_DIR, exist_ok=True)
    os.makedirs(os.path.join(config.LOG_DIR, 'tasks'), exist_ok=True)
    os.makedirs(config.DATA_DIR, exist_ok=True)
    
    # 设置日志文件名
    log_file = config.get_task_log_file(survey_id, timestamp)
    
    # 重新配置日志
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(config.LOG_FORMAT))
    
    for handler in logger.handlers[:]:
        if isinstance(handler, logging.FileHandler):
            logger.removeHandler(handler)
    
    logger.addHandler(file_handler)
    
    # 清理旧的数据文件
    cleanup_data_files(pattern="*.json")
    
    # 解析问卷
    logger.info(f"正在解析问卷: {url}")
    questions, stats = parse_survey(url)
    
    # 转换为统一格式，并保存
    formatted_questions = {
        "id": survey_id,
        "title": "问卷调查",  # 理想情况下从页面获取
        "url": url,
        "timestamp": timestamp,
        "questions": questions
    }
    
    # 使用自动命名保存问卷配置
    questions_path = save_questions(formatted_questions, url=url)
    logger.info(f"问卷解析完成，配置已保存到 {questions_path}")
    
    # 保存统计信息到自动命名的JSON文件
    stats_file_path = os.path.join(config.DATA_DIR, f"stats_{survey_id}_{timestamp}.json")
    with open(stats_file_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=4)
    logger.info(f"统计信息已保存到 {stats_file_path}")
    
    # 创建自动命名的IP使用记录文件
    ip_usage_file = config.get_ip_usage_file(survey_id, timestamp)
    ip_tracker = IPUsageTracker(log_file=ip_usage_file)
    
    # 打印统计信息
    logger.info(f"总题目数: {stats['total']}")
    logger.info("各题型题目数:")
    for q_type, count in stats['type_count'].items():
        logger.info(f"{q_type}: {count}")

    # 优化问卷数据结构
    optimized_file = os.path.join(config.DATA_DIR, f"questions_optimized_{survey_id}_{timestamp}.json")
    logger.info("正在优化问卷数据结构...")
    optimized_data = optimize_question_data(
        questions_path, 
        optimized_file
    )
    logger.info(f"问卷数据结构优化完成，保存到 {optimized_file}")
    
    # 是否使用LLM生成数据
    use_llm = False  # 设置为True启用LLM生成
    
    if use_llm:
        try:
            # 初始化LLM生成器（选择你要使用的模型）
            # 支持的模型: "openai", "zhipu", "baidu"
            llm_generator = LLMGenerator(
                model_type="zhipu",  # 这里选择智谱AI(免费有配额)
                api_key=config.LLM_API_KEYS.get('zhipu', '')  # 使用配置中的API密钥
            )
            
            # 为问卷生成答案
            logger.info("使用LLM生成问卷答案...")
            llm_answers = llm_generator.generate_answers(optimized_data)
            
            # 保存生成的答案到文件
            llm_answers_file = os.path.join(config.DATA_DIR, f"llm_answers_{survey_id}_{timestamp}.json")
            with open(llm_answers_file, "w", encoding="utf-8") as f:
                json.dump(llm_answers, f, ensure_ascii=False, indent=2)
            
            logger.info(f"LLM生成的答案已保存到 {llm_answers_file}")
            
        except Exception as e:
            logger.error(f"LLM生成失败: {e}")
            use_llm = False

    # 创建并执行问卷任务
    task = SurveyTask(
        survey_url=url,
        questions_path=questions_path,
        target_num=5,  # 目标提交数量
        max_workers=5,  # 并发数量
        # 使用配置中的代理设置
        use_proxy=config.USE_PROXY,
        proxy_url=config.DEFAULT_PROXY_URL
    )
    
    # 如果使用LLM生成的答案，传递给SurveyTask
    if use_llm:
        task.use_llm_answers = True
        task.llm_answers = llm_answers
    
    # 执行批量提交
    results = task.run()
    
    logger.info(f"\n任务完成！成功填写 {results['success']} 份，失败 {results['failed']} 次")

    # 清理旧的数据文件
    cleanup_data_files(pattern="*.json")  # 使用配置中的保留天数

if __name__ == "__main__":
    main()