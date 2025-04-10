"""
----------------------------------------------------------------
File name:                  llm_generator.py
Author:                     Ignorant-lu
Date created:               2025/02/23
Description:                大语言模型答案生成模块，提供智能问卷填写功能
----------------------------------------------------------------

Changed history:            
                            2025/02/25: 添加多模型API支持(OpenAI、智谱、百度、阿里云)
                            2025/03/02: 优化提示词结构和错误处理
----------------------------------------------------------------
"""

import json
import requests
import os
import time
from typing import Dict, List, Any
import logging
import random
from openai import OpenAI

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

class LLMGenerator:
    """
    LLM答案生成器
    
    基于大型语言模型生成问卷答案
    支持多种模型API和自定义提示词
    """
    
    def __init__(self, model_type="aliyun", api_key=None):
        """
        初始化LLM生成器
        
        Args:
            model_type: 使用的模型类型，支持 "openai", "zhipu", "baidu", "aliyun"
            api_key: API密钥
        """
        self.model_type = model_type
        self.api_key = api_key or os.getenv(f"{model_type.upper()}_API_KEY")
        
        if not self.api_key:
            raise ValueError(f"未提供{model_type}的API密钥，请设置环境变量或直接传入")
            
        # 初始化不同模型的客户端
        if model_type == "aliyun":
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
        else:
            # 初始化不同模型的API端点
            self.endpoints = {
                "openai": "https://api.openai.com/v1/chat/completions",
                "zhipu": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
                "baidu": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions",
            }
    
    def generate_answers(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """为整个问卷生成答案"""
        try:
            logger.info(f"开始使用 {self.model_type} 生成答案")
            logger.info(f"问卷包含 {len(question_data.get('questions', []))} 个问题")
            
            # 构建提示词
            prompt = self._build_prompt(question_data)
            logger.debug(f"生成的提示词: {prompt[:200]}...")
            
            # 调用LLM API
            logger.info(f"调用 {self.model_type} API...")
            response = self._call_llm_api(prompt)
            logger.debug(f"API响应: {response[:200]}...")
            
            # 解析响应
            answers = self._parse_response(response, question_data)
            logger.info(f"成功解析答案, 包含 {len(answers)} 个回答")
            
            return answers
        except Exception as e:
            logger.error(f"生成答案失败: {str(e)}", exc_info=True)
            raise
    
    def _build_prompt(self, question_data: Dict[str, Any]) -> str:
        """构建提示词"""
        prompt = f"你是一位问卷填写助手。请帮我填写以下问卷，要求：\n"
        prompt += "1. 答案要真实、合理，像真人填写\n"
        prompt += "2. 对于选择题，只需回答选项编号\n"
        prompt += "3. 对于填空题，提供合理且多样化的答案\n"
        prompt += "4. 请按照规定的JSON格式返回答案\n\n"
        
        prompt += f"问卷标题：{question_data['title']}\n\n"
        
        for i, q in enumerate(question_data['questions']):
            prompt += f"问题{i+1}（{q['index']}）：{q['title']}\n"
            
            if q['type'] == 3:
                prompt += "（单选题）选项：\n"
                for j, opt in enumerate(q['options']):
                    prompt += f"  {j+1}. {opt}\n"
                    
            elif q['type'] == 4:
                prompt += "（多选题）选项：\n"
                for j, opt in enumerate(q['options']):
                    prompt += f"  {j+1}. {opt}\n"
                    
            elif q['type'] == 6:
                prompt += "（矩阵题）\n"
                prompt += "行：\n"
                for j, row in enumerate(q['rows']):
                    prompt += f"  {j+1}. {row}\n"
                prompt += "列：\n"
                for j, col in enumerate(q['columns']):
                    prompt += f"  {j+1}. {col}\n"

            # 余下题目逻辑补充
                        
            prompt += "\n"
            
        prompt += """
请用如下JSON格式返回答案：
{
  "answers": [
    {"idx": "问题编号(纯数字)", "value": "答案值"},
    ...
  ]
}

对于单选题，value是选项编号（如"2"）
对于多选题，value是选项编号列表（如"1|3|4", "|"是分隔符）
对于填空题，value是文本内容
对于矩阵题，value是每行的选择（如"1!2,2!3,3!1"，表示第1行选第2项，第2行选第3项，第3行选第1项）
对于量表题，value是填入分数（如"5"）
对于排序题，value是选项编号列表（如"1,3,4,2", ","是分隔符）

只返回JSON格式数据，不要有其他解释性文字。
"""
        return prompt
    
    def _call_llm_api(self, prompt: str) -> str:
        """调用不同的LLM API"""
        if self.model_type == "aliyun":
            return self._call_aliyun(prompt)
        elif self.model_type == "openai":
            return self._call_openai(prompt)
        elif self.model_type == "zhipu":
            return self._call_zhipu(prompt)
        elif self.model_type == "baidu":
            return self._call_baidu(prompt)
        else:
            raise ValueError(f"不支持的模型类型: {self.model_type}")
    
    def _call_openai(self, prompt: str) -> str:
        """调用OpenAI API"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        
        response = requests.post(self.endpoints["openai"], headers=headers, json=data)
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"OpenAI API错误: {response.status_code}, {response.text}")
    
    def _call_zhipu(self, prompt: str) -> str:
        """调用智谱API（ChatGLM）"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": "glm-4",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        
        response = requests.post(self.endpoints["zhipu"], headers=headers, json=data)
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"智谱API错误: {response.status_code}, {response.text}")
    
    def _call_baidu(self, prompt: str) -> str:
        """调用百度文心一言API"""
        # 获取访问令牌
        access_token = self._get_baidu_access_token()
        
        headers = {"Content-Type": "application/json"}
        
        data = {
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        
        response = requests.post(
            f"{self.endpoints['baidu']}?access_token={access_token}",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            return response.json()["result"]
        else:
            raise Exception(f"百度API错误: {response.status_code}, {response.text}")
    
    def _get_baidu_access_token(self) -> str:
        """获取百度API访问令牌"""
        api_key, secret_key = self.api_key.split(":")
        
        url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={api_key}&client_secret={secret_key}"
        
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            raise Exception(f"获取百度访问令牌失败: {response.status_code}, {response.text}")
    
    def _call_aliyun(self, prompt: str) -> str:
        """使用OpenAI客户端调用阿里云百炼API"""
        try:
            logger.info("准备调用阿里云百炼API")
            
            completion = self.client.chat.completions.create(
                model="qwen-turbo",
                messages=[
                    {"role": "system", "content": "你是一个专业的问卷填写助手，请帮助用户填写问卷。"},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # 获取生成的内容
            content = completion.choices[0].message.content
            logger.info("成功获取API响应")
            
            return content
            
        except Exception as e:
            logger.error(f"调用阿里云API失败: {str(e)}")
            raise Exception(f"阿里云API调用失败: {str(e)}")
    
    def _parse_response(self, response: str, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """解析LLM返回的答案"""
        try:
            # 尝试解析JSON
            ans_data = json.loads(response)
            
            # 验证格式
            if "answers" not in ans_data:
                raise ValueError("返回数据缺少'answers'字段")
                
            # 格式化为问卷提交格式
            formatted_data = {}
            
            for ans in ans_data["answers"]:
                idx = ans["idx"]
                value = ans["value"]
                formatted_data[idx] = value
                
            return formatted_data
            
        except json.JSONDecodeError:
            # 如果无法解析JSON，尝试从文本中提取
            import re
            
            pattern = r'"idx":\s*"([^"]+)",\s*"value":\s*"([^"]+)"'
            matches = re.findall(pattern, response)
            
            formatted_data = {}
            for idx, value in matches:
                formatted_data[idx] = value
                
            return formatted_data 