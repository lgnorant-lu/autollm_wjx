"""
----------------------------------------------------------------
File name:                  wjx.py
Author:                     Ignorant-lu
Date created:               2025/02/16
Description:                问卷星提交模块，负责提交问卷和答案生成
----------------------------------------------------------------

Changed history:
                            2025/02/22: 添加代理支持和提交任务管理功能
----------------------------------------------------------------
"""

import requests
import re
from datetime import datetime, timedelta
import json
import os
import random
import logging
from core.parser import extract_survey_id, parse_survey
import time

# 配置日志记录
logger = logging.getLogger(__name__)

class WJXSubmitter:
    """
    问卷星提交工具类

    提供问卷自动提交、答案生成、任务管理等功能
    """

    def __init__(self, survey_url="https://www.wjx.cn/vm/wWwct2F.aspx", config_path=None):
        """
        初始化问卷提交器

        Args:
            survey_url: 问卷星URL
            config_path: 问卷配置文件路径，如果为None则使用默认路径
        """
        # 确保URL格式正确
        if not survey_url.startswith('http'):
            survey_url = 'https://' + survey_url

        self.survey_url = survey_url
        # 使用动态计算的路径，而不是硬编码路径
        if config_path is None:
            # 使用Config类中定义的DATA_DIR
            from config import Config
            config_path = os.path.join(Config.DATA_DIR, "stats.json")

        self.config_path = config_path
        self.survey_id = extract_survey_id(survey_url)
        self.config = None
        self.headers = {
            'Accept': 'text/plain, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://www.wjx.cn',
            'Referer': survey_url,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Microsoft Edge";v="129", "Chromium";v="129"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        # cookies保留为空, 大部分场景无需cookies也能成功提交
        self.cookies = {}

    def _extract_shortid(self, url):
        """从URL中提取问卷短ID"""
        match = re.search(r'vm/([a-zA-Z0-9]+)\.aspx', url)
        if match:
            return match.group(1)
        raise ValueError(f"无法从URL中提取问卷ID: {url}")

    def load_config(self):
        """加载问卷配置"""
        # 确保配置路径是绝对路径
        config_path = os.path.abspath(self.config_path) if not os.path.isabs(self.config_path) else self.config_path

        # 首先尝试加载已有配置
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)

                # 验证配置的完整性
                if not self.config.get('questions', []) or not self.config.get('total'):
                    logger.warning(f"配置文件格式不完整，尝试重新解析问卷")
                else:
                    logger.info(f"成功加载配置, 问卷共 {self.config['total']} 道题目")
                    return True
            except json.JSONDecodeError as e:
                logger.error(f"配置文件JSON解析错误: {e}")
            except UnicodeDecodeError as e:
                logger.error(f"配置文件编码错误: {e}")
            except Exception as e:
                logger.error(f"读取配置文件时发生未知错误: {e}", exc_info=True)

        # 配置文件不存在或加载失败，尝试解析问卷
        logger.info(f"尝试解析问卷: {self.survey_url}")
        try:
            survey_data = parse_survey(self.survey_url)

            # 检查parse_survey是否返回了错误
            if survey_data.get("error"):
                logger.error(f"解析问卷失败: {survey_data['error']}")
                return False

            # 验证survey_data的完整性
            questions = survey_data.get("questions", [])
            if not questions:
                logger.error("解析的问卷没有包含任何问题")
                return False

            title = survey_data.get("title", "未知标题")
            survey_id = survey_data.get("id", self.survey_id)

            # 构建统计信息
            stats = {
                "title": title,
                "total": len(questions),
                "parsed_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }

            # 创建配置
            self.config = {
                "id": survey_id,
                "total": len(questions),
                "questions": questions,
                "stats": stats,
                "url": self.survey_url
            }

            # 确保目录存在并保存配置
            try:
                os.makedirs(os.path.dirname(config_path), exist_ok=True)
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, ensure_ascii=False, indent=2)

                logger.info(f"已创建并保存新配置到 {config_path}，问卷共 {self.config['total']} 道题目")
                return True
            except PermissionError as e:
                logger.error(f"保存配置文件权限不足: {e}")
            except OSError as e:
                logger.error(f"保存配置文件操作系统错误: {e}")
            except Exception as e:
                logger.error(f"保存配置文件时发生未知错误: {e}", exc_info=True)

        except requests.exceptions.RequestException as e:
            logger.error(f"网络请求错误: {e}")
        except Exception as e:
            logger.error(f"解析问卷时发生未知错误: {e}", exc_info=True)

        return False

    def get_jqnonce(self):
        """获取jqnonce参数, 用于提交表单验证"""
        try:
            html = requests.get(self.survey_url, headers=self.headers).text
            pattern = re.compile(r'jqnonce\s*=\s*"(.*?)";')
            match = pattern.search(html)
            if match:
                jqnonce = match.group(1)
                logger.debug(f"获取到jqnonce: {jqnonce}")
                return jqnonce
            else:
                raise ValueError("未找到jqnonce")
        except Exception as e:
            logger.error(f"获取jqnonce失败: {e}")
            return None

    def get_ktimes(self, questions_count):
        """
        计算ktimes参数

        Args:
            questions_count: 问卷题目总数
        """
        return questions_count + 2 + random.randint(int(0.25*questions_count), int(0.6*questions_count))

    def dataenc(self, s, ktimes):
        """
        数据加密函数

        Args:
            s: 要加密的字符串
            ktimes: ktimes值
        """
        t = ktimes % 10
        t = t or 1  # 如果 t=0 则设为1
        return ''.join([chr(ord(c) ^ t) for c in s])

    def get_starttime(self, min_seconds=27, max_seconds=600):
        """
        生成随机开始时间

        Args:
            min_seconds: 最小提前秒数
            max_seconds: 最大提前秒数
        """
        now = datetime.now()
        max_time = random.randint(max(min_seconds+15, 42), random.randint(71, random.randint(250, max_seconds)))
        random_time = random.randint(min_seconds, max_time)
        older = now - timedelta(seconds=random_time)
        return older.strftime('%Y/%m/%d %H:%M:%S')

    def build_submit_data(self, question_data):
        """
        构建提交数据

        Args:
            question_data: 问卷题目数据, 通常来自解析后的JSON

        Returns:
            构建好的submitdata字符串
        """
        # TODO: 实现根据问卷题目生成答案的逻辑
        # 这部分需要根据解析的问卷数据构建符合规则的答案
        # 暂时返回一个示例数据
        logger.warning("使用示例数据提交, 请实现具体的数据构建逻辑")
        return '1$1}2$2}3$25}4$754}5$2}6$54}7$45}8$2|7}9$2}10$1}11$2}12$2}13$1}14$3|9}15$1}16$254}17$45}18$45}19$45}20$2'

    def submit(self, submit_data=None, proxy=None):
        """提交问卷"""
        # 加载问卷配置
        if not self.config:
            if not self.load_config():
                return {"success": False, "message": "加载问卷配置失败"}

        # 获取jqnonce
        jqnonce = self.get_jqnonce()
        if not jqnonce:
            return {"success": False, "message": "获取jqnonce失败"}

        questions_count = self.config["total"]
        ktimes = self.get_ktimes(questions_count)
        starttime = self.get_starttime()

        # 构建请求参数
        params = {
            'shortid': self.survey_id,
            'starttime': starttime,
            'ktimes': f'{ktimes}',
            'jqnonce': jqnonce,
            'jqsign': self.dataenc(jqnonce, ktimes),
        }

        # 构建提交数据
        if not submit_data:
            logger.warning("未提供提交数据, 将使用示例数据")
            submit_data = self.build_submit_data(None)

        data = {
            'submitdata': submit_data,
        }

        # 日志记录请求信息
        logger.info(f"提交问卷 {self.survey_id} 参数: {params}")
        logger.info(f"提交问卷 {self.survey_id} 数据: {data}")

        # 提交请求
        try:
            logger.info(f"开始提交问卷 {self.survey_id}")
            response = requests.post(
                'https://www.wjx.cn/joinnew/processjq.ashx',
                params=params,
                cookies=self.cookies,
                headers=self.headers,
                data=data,
                proxies=proxy
            )

            result_text = response.text
            logger.info(f"问卷提交响应: {result_text}")

            success = '10' in result_text or '提交成功' in result_text

            if success:
                logger.info("问卷提交成功")
                return {"success": True, "message": "提交成功", "response": result_text}
            else:
                logger.warning(f"问卷提交失败: {result_text}")
                return {"success": False, "message": result_text, "response": result_text}

        except Exception as e:
            logger.error(f"提交问卷异常: {e}", exc_info=True)
            return {"success": False, "message": str(e)}

    def validate_data(self, submit_data):
        """
        验证提交数据的格式是否正确

        Args:
            submit_data: 提交的数据字符串

        Returns:
            验证结果，格式为 {"valid": bool, "errors": list}
        """
        # 实现数据验证逻辑
        parts = submit_data.split('}')
        errors = []

        for part in parts:
            if not part:
                continue

            try:
                q_index, value = part.split('$')
                q_index = int(q_index)

                # 这里可以添加更多的验证逻辑
                # 例如，检查题目类型和答案格式是否匹配

            except Exception as e:
                errors.append(f"格式错误: {part}, 原因: {str(e)}")

        return {"valid": len(errors) == 0, "errors": errors}


if __name__ == '__main__':
    # 配置日志输出
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 使用示例
    submitter = WJXSubmitter()
    result = submitter.submit(None)
    print(result)
