"""
问卷星验证码处理模块
处理阿里云验证码(NVC)的生成与验证
"""

import requests
import re
import urllib.parse
import json
import random
import time
import logging
from core.umid_token import get_umid_token  # 添加导入

# 配置日志
logger = logging.getLogger(__name__)


class AliyunVerification:
    """阿里云验证码处理类"""
    
    def __init__(self, survey_url, app_key="FFFF00000000016770EE"):
        """
        初始化验证处理器
        
        Args:
            survey_url: 问卷URL
            app_key: 阿里云应用密钥(默认问卷星使用的key)
        """
        self.survey_url = survey_url
        self.app_key = app_key
        self.analyze_url = 'https://cf.aliyun.com/nvc/nvcAnalyze.jsonp'
        self.prepare_url = 'https://cf.aliyun.com/nvc/nvcPrepare.jsonp'
        self.umidToken_url = 'https://ynuf.aliapp.org/service/um.json'
        
        # 设置请求头
        self.headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://www.wjx.cn/',
            'Sec-Fetch-Dest': 'script',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Microsoft Edge";v="129", "Chromium";v="129"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        
        # 初始化cookies
        self.cookies = {}

    @staticmethod
    def generate_callback():
        """生成随机的jsonp回调名称"""
        return ("jsonp_" + str(random.random())).replace(".", "")

    @staticmethod
    def generate_c_value():
        """生成c参数值(时间戳:随机数)"""
        return f"{int(time.time()*1000)}:{random.random()}"
    
    def generate_umid_tokens(self):
        """
        生成umidToken，使用umid_token模块的功能
        
        Returns:
            dict: 包含umidToken的字典
        """
        logger.debug("开始生成UMID Token")
        
        # 使用新的umid_token模块获取token
        token_result = get_umid_token()
        
        # 检查是否成功获取token
        if "error" in token_result:
            logger.error(f"获取UMID Token失败: {token_result['error']}")
            return {"success": False, "error": token_result["error"]}
        
        logger.debug(f"成功获取UMID Token")
        return {"success": True, "data": token_result}



    def convert_to_query_string(self, data):
        """
        将多层嵌套的字典转换为URL编码的查询字符串
        
        Args:
            data: 可能包含多层嵌套结构的字典
            
        Returns:
            编码后的查询字符串
        """
        def process_value(value):
            """递归处理值，自动序列化嵌套结构"""
            if isinstance(value, (dict, list)):
                return json.dumps(value, separators=(',', ':'), ensure_ascii=False)
            elif isinstance(value, str):
                try:  # 检测已经是JSON字符串的情况
                    json.loads(value)
                    return value  # 已经是合法JSON字符串则保留
                except:
                    return value
            else:
                return str(value)

        pairs = []
        for key, value in data.items():
            # 处理多层嵌套值
            processed_value = process_value(value)
            
            # 对键值进行编码
            encoded_key = urllib.parse.quote(str(key), safe='')
            encoded_value = urllib.parse.quote(processed_value, safe='')
            
            pairs.append(f"{encoded_key}={encoded_value}")

        return "&".join(pairs)
    
    def prepare(self):
        """
        执行验证准备请求
        
        Returns:
            准备请求的响应结果
        """
        logger.debug("执行验证准备请求")
        
        # 生成准备请求参数
        c_value = self.generate_c_value()
        callback = self.generate_callback()
        
        params_prepare = {
            "a": json.dumps({
                "a": self.app_key,
                "c": c_value,
                "d": "ic_activity",
            }, separators=(',', ':')),
            "callback": callback
        }
        
        # 构造请求URL
        params_formatted = self.convert_to_query_string(params_prepare)
        
        try:
            # 发送准备请求
            response = requests.get(
                self.prepare_url, 
                params=params_formatted, 
                cookies=self.cookies, 
                headers=self.headers
            )
            
            # 解析JSONP响应
            jsonp_response = response.text
            json_str = re.search(r'{.*}', jsonp_response).group(0)
            result = json.loads(json_str)
            
            logger.debug(f"验证准备完成: {result}")
            return {
                'success': True,
                'result': result,
                'c_value': c_value
            }
            
        except Exception as e:
            logger.error(f"验证准备失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_verification(self, b_value=""):
        """
        获取验证结果
        
        Args:
            b_value: b参数值(可选)
            
        Returns:
            验证结果
        """
        logger.debug("开始获取验证结果")
        
        # 准备请求
        prep_result = self.prepare()
        if not prep_result['success']:
            return prep_result
        
        # 生成umidToken
        umid_token = self.generate_umid_tokens()
        
        # 构建验证请求参数
        c_value = prep_result.get('c_value', self.generate_c_value())
        
        analyze_data = {
            "a": json.dumps({
                "a": self.app_key,
                "c": c_value,
                "d": "ic_activity",
                "j": {"test": 1},
                "h": {
                    "umidToken": umid_token['tn']
                },
                "b": b_value,
                "e": prep_result['result']['result']['result']['c']
            }, separators=(',', ':')),
            "v": 0.04,  # 版本号(可能需要更新)
            "callback": "callback"
        }
        
        # 构造请求URL
        query_string = self.convert_to_query_string(analyze_data)
        url = f"{self.analyze_url}?{query_string}"
        
        try:
            # 发送验证请求
            response = requests.get(url, headers=self.headers, cookies=self.cookies)
            
            # 解析JSONP响应
            jsonp_response = response.text
            json_str = re.search(r'{.*}', jsonp_response).group(0)
            result = json.loads(json_str)
            
            logger.debug(f"验证结果获取成功: {result}")
            return {
                'success': True,
                'result': result,
                'umidToken': umid_token['tn']
            }
            
        except Exception as e:
            logger.error(f"获取验证结果失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_verification_data(self):
        """
        获取可用于问卷提交的验证数据
        
        Returns:
            验证数据字典
        """
        result = self.get_verification()
        
        if not result['success']:
            logger.error("获取验证数据失败")
            return None
        
        verification_result = result['result']
        
        # 从结果中提取必要的验证信息
        try:
            verification_data = {
                'umidToken': result.get('umidToken', ''),
                'token': verification_result.get('result', {}).get('token', ''),
                'sessionId': verification_result.get('result', {}).get('sessionId', ''),
                'sig': verification_result.get('result', {}).get('sig', '')
            }
            return verification_data
        except Exception as e:
            logger.error(f"解析验证数据失败: {e}")
            return None


# 简单使用示例
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 使用示例
    verifier = AliyunVerification("https://www.wjx.cn/vm/hxxt2Oe.aspx")
    verification_data = verifier.get_verification_data()

    if verification_data:
        print("验证数据获取成功:")
        print(json.dumps(verification_data, indent=2, ensure_ascii=False))
    else:
        print("验证数据获取失败") 