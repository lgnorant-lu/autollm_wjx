"""
----------------------------------------------------------------
File name:                  base.py
Author:                     Ignorant-lu
Date created:               2025/04/01
Description:                LLM抽象基类，定义统一的LLM接口
----------------------------------------------------------------

Changed history:
                            2025/04/01: 初始创建
----------------------------------------------------------------
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class BaseLLMProvider(ABC):
    """
    LLM提供商抽象基类

    定义统一的LLM接口，所有具体的LLM提供商实现都应继承此类
    """

    def __init__(self, api_key: str, model: str = None, **kwargs):
        """
        初始化LLM提供商

        Args:
            api_key: API密钥
            model: 模型名称，如果为None则使用默认模型
            **kwargs: 其他参数
        """
        self.api_key = api_key
        self.model = model
        self.max_retries = kwargs.get('max_retries', 3)
        self.timeout = kwargs.get('timeout', 30)
        self.temperature = kwargs.get('temperature', 0.7)
        self.max_tokens = kwargs.get('max_tokens', 500)
        self.mock = kwargs.get('mock', False)  # 模拟模式

        # 初始化提供商特定的配置
        self._init_provider_config(**kwargs)

    @abstractmethod
    def _init_provider_config(self, **kwargs):
        """
        初始化提供商特定的配置

        Args:
            **kwargs: 配置参数
        """
        pass

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        生成文本

        Args:
            prompt: 提示词
            **kwargs: 其他参数

        Returns:
            str: 生成的文本
        """
        pass

    @abstractmethod
    def generate_json(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        生成JSON格式的响应

        Args:
            prompt: 提示词
            **kwargs: 其他参数

        Returns:
            Dict[str, Any]: 生成的JSON数据
        """
        pass

    def generate_answers(self, question_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        为问卷生成答案

        Args:
            question_data: 问卷数据
            **kwargs: 其他参数

        Returns:
            Dict[str, Any]: 生成的答案
        """
        # 构建提示词
        prompt = self.build_prompt(question_data, **kwargs)

        # 生成JSON响应
        response = self.generate_json(prompt, **kwargs)

        # 解析响应
        return self.parse_response(response, question_data)

    def build_prompt(self, question_data: Dict[str, Any], **kwargs) -> str:
        """
        构建提示词

        Args:
            question_data: 问卷数据
            **kwargs: 其他参数

        Returns:
            str: 构建的提示词
        """
        # 角色定义和任务说明
        prompt = """你是一位专业的问卷填写助手，擅长模拟真实用户填写各类问卷。

任务：请帮我填写以下问卷，生成真实、合理的答案。

要求：
1. 答案必须真实、合理，像真人填写的一样
2. 对于选择题，只需提供选项编号
3. 对于填空题，提供合理且多样化的答案
4. 严格按照指定的JSON格式返回答案
5. 不要添加任何解释或额外文本，只返回JSON
"""

        # 问卷信息
        prompt += f"\n问卷标题：{question_data['title']}\n\n"

        # 问题部分 - 更加简洁高效
        for i, q in enumerate(question_data['questions']):
            # 跳过隐藏题目
            if q.get('is_hidden', False):
                continue

            q_type = q['type']
            q_index = q['index']
            q_title = q['title']

            prompt += f"问题{i+1}（ID: {q_index}）：{q_title}\n"

            # 根据题型添加不同的提示
            if q_type == 3:  # 单选题
                prompt += "（单选题）选项：\n"
                if 'options' in q and q['options']:
                    for j, opt in enumerate(q['options']):
                        prompt += f"  {j+1}. {opt}\n"

            elif q_type == 4:  # 多选题
                prompt += "（多选题）选项：\n"
                if 'options' in q and q['options']:
                    for j, opt in enumerate(q['options']):
                        prompt += f"  {j+1}. {opt}\n"

            elif q_type == 5:  # 量表题/评价题
                prompt += f"（量表题）范围：{q.get('min', 1)}-{q.get('max', 5)}\n"

                # 添加量表标题
                if 'scale_titles' in q and len(q['scale_titles']) >= 2:
                    prompt += f"  最小值含义: {q['scale_titles'][0]}\n"
                    prompt += f"  最大值含义: {q['scale_titles'][-1]}\n"

                # 添加量表选项
                if 'scale_options' in q and q['scale_options']:
                    prompt += "  选项:\n"
                    for opt in q['scale_options']:
                        prompt += f"    {opt}\n"

            elif q_type == 6:  # 矩阵题
                prompt += "（矩阵题）\n"

                # 添加行信息
                if 'rows' in q and q['rows']:
                    prompt += "  行：\n"
                    for j, row in enumerate(q['rows']):
                        prompt += f"    {j+1}. {row}\n"

                # 添加列信息
                if 'columns' in q and q['columns']:
                    prompt += "  列：\n"
                    for j, col in enumerate(q['columns']):
                        prompt += f"    {j+1}. {col}\n"

                # 标记是否为矩阵多选题
                if q.get('is_matrix_checkbox', False):
                    prompt += "  （此题为矩阵多选题，每行可选多个）\n"

            elif q_type == 1:  # 填空题
                prompt += "（填空题）\n"
                if 'max_length' in q:
                    prompt += f"  最大长度: {q['max_length']}\n"

            elif q_type == 2:  # 简答题
                prompt += "（简答题）\n"
                if 'max_length' in q:
                    prompt += f"  最大长度: {q['max_length']}\n"
                if 'rows' in q:
                    prompt += f"  行数: {q['rows']}\n"

            elif q_type == 7:  # 下拉题
                prompt += "（下拉题）选项：\n"
                if 'options' in q and q['options']:
                    for j, opt in enumerate(q['options']):
                        prompt += f"  {j+1}. {opt}\n"

            elif q_type == 8:  # 评分题
                prompt += f"（评分题）范围：{q.get('min', 1)}-{q.get('max', 10)}\n"

            elif q_type == 9:  # 矩阵填空/矩阵评分题
                prompt += "（矩阵填空/评分题）\n"
                if 'row_titles' in q and q['row_titles']:
                    prompt += "  行：\n"
                    for j, row in enumerate(q['row_titles']):
                        prompt += f"    {j+1}. {row}\n"

            elif q_type == 11:  # 排序题
                prompt += "（排序题）选项：\n"
                if 'options' in q and q['options']:
                    for j, opt in enumerate(q['options']):
                        prompt += f"  {j+1}. {opt}\n"

            # 添加空行分隔不同问题
            prompt += "\n"

        # 输出格式要求 - 更加清晰结构化
        prompt += """
输出格式：
请严格按照以下JSON格式返回答案：
```json
{
  "answers": [
    {"idx": "问题编号", "value": "答案值"},
    {"idx": "问题编号", "value": "答案值"},
    ...
  ]
}
```

答案格式说明：
- 单选题(type=3)：value为选项编号，如"2"
- 多选题(type=4)：value为选项编号列表，用"|"分隔，如"1|3|4"
- 下拉题(type=7)：value为选项编号，如"2"
- 填空题(type=1)：value为文本内容
- 简答题(type=2)：value为文本内容
- 矩阵单选题(type=6)：value格式为"行号!选项号,行号!选项号"，如"1!2,2!3,3!1"
- 矩阵多选题(type=6)：value格式为"行号!(选项号,选项号),行号!(选项号,选项号)"，如"1!(1,3),2!(2,4)"
- 量表题/评价题(type=5)：value为分数，如"5"
- 评分题(type=8)：value为分数，如"8"
- 矩阵填空/评分题(type=9)：value为每行的填空内容，用"^"分隔，如"回答1^回答2^回答3"
- 排序题(type=11)：value为选项编号列表，用","分隔，如"1,3,4,2"

注意：
1. 只返回JSON格式数据，不要有其他解释性文字
2. 确保JSON格式正确，不要有多余的逗号或缺少引号
3. 所有问题都必须有答案
"""
        return prompt

    def parse_response(self, response: Dict[str, Any], question_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析LLM返回的答案

        Args:
            response: LLM返回的响应
            question_data: 问卷数据

        Returns:
            Dict[str, Any]: 解析后的答案
        """
        try:
            # 验证格式
            if "answers" not in response:
                raise ValueError("返回数据缺少'answers'字段")

            # 格式化为问卷提交格式
            formatted_data = {}

            for ans in response["answers"]:
                idx = ans["idx"]
                value = ans["value"]
                formatted_data[idx] = value

            return formatted_data

        except Exception as e:
            logger.error(f"解析LLM响应失败: {str(e)}")
            # 返回空结果
            return {}

    def validate_response(self, response: Dict[str, Any], question_data: Dict[str, Any]) -> bool:
        """
        验证LLM返回的答案是否有效

        Args:
            response: LLM返回的响应
            question_data: 问卷数据

        Returns:
            bool: 是否有效
        """
        try:
            # 检查是否包含answers字段
            if "answers" not in response:
                logger.warning("响应缺少answers字段")
                return False

            # 检查answers是否为列表
            if not isinstance(response["answers"], list):
                logger.warning("answers不是列表")
                return False

            # 检查每个答案是否包含idx和value字段
            for ans in response["answers"]:
                if "idx" not in ans or "value" not in ans:
                    logger.warning("答案缺少idx或value字段")
                    return False

            return True

        except Exception as e:
            logger.error(f"验证LLM响应失败: {str(e)}")
            return False
