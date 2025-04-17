"""
----------------------------------------------------------------
File name:                  umid_token.py
Author:                     Ignorant-lu
Date created:               2025/03/03
Description:                阿里云UMID Token生成模块，用于问卷星验证
----------------------------------------------------------------

Changed history:            
                            2025/03/03: 从don&tn_id.py重构;
----------------------------------------------------------------
"""

import requests
import logging
import random
import time
import os
from config import get_config

# 配置日志
logger = logging.getLogger(__name__)

class UmidTokenGenerator:
    """阿里云UMID Token生成器"""
    
    def __init__(self, app_key="FFFF00000000016770EE"):
        """
        初始化UMID Token生成器
        
        Args:
            app_key: 阿里云应用密钥(默认问卷星使用的key)
        """
        self.app_key = app_key
        self.umidToken_url = 'https://ynuf.aliapp.org/service/um.json'
        self.config = get_config()
        
        # 设置请求头
        self.headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://www.wjx.cn',
            'Referer': 'https://www.wjx.cn/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Microsoft Edge";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        
        # 初始化cookies
        self.cookies = {}
    
    def generate_token(self):
        """
        生成UMID Token
        
        Returns:
            dict: 包含token信息的字典
        """
        try:
            logger.debug("开始生成UMID Token")
            
            # 随机生成的data参数 - 实际情况下这个值会在前端生成
            data_param = self._generate_data_param()
            
            params = {
                'data': data_param,
                'xa': self.app_key,
                'xt': '',
                'efy': '1',
            }
            
            # 使用代理（如果配置了）
            proxies = None
            if self.config.USE_PROXY and self.config.DEFAULT_PROXY_URL:
                proxies = {
                    'http': self.config.DEFAULT_PROXY_URL,
                    'https': self.config.DEFAULT_PROXY_URL
                }
                logger.debug(f"使用代理: {self.config.DEFAULT_PROXY_URL}")

            # 发送请求
            response = requests.post(
                url=self.umidToken_url,
                headers=self.headers,
                cookies=self.cookies,
                data=params,
                proxies=proxies,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.debug(f"成功获取UMID Token: {result.get('tn', '无token')[:10]}...")
                return result
            else:
                logger.error(f"获取UMID Token失败: HTTP {response.status_code}")
                return {"error": f"HTTP错误: {response.status_code}"}
                
        except requests.RequestException as e:
            logger.error(f"请求UMID Token时发生网络错误: {str(e)}")
            return {"error": f"网络错误: {str(e)}"}
        except Exception as e:
            logger.error(f"获取UMID Token时发生未知错误: {str(e)}", exc_info=True)
            return {"error": f"未知错误: {str(e)}"}
    
    def _generate_data_param(self):
        """
        生成用于请求的data参数
        
        Returns:
            str: 随机生成的data参数
        """
        # 在实际应用中，这个值应该由前端计算并传入
        # 这里我们使用一个固定的值作为示例，仅用于测试
        return '107!fDg1Dk7KfQ6f5SiIWPJ7TF8G9UNkZOwbfx2bJ%2FlpAT00az5SAT%2BUAy00wdLpvfNmmfYJ9QUpNtrX8dBvslTVku4dCzd8rIwLffxu1C1NG7fWNuwA5LbzUQ6DKPYp8DyeBEH3gos685pK2vfffNl0tJJiPfgJYVYoeAmfPfoHIN9iKfqxdI4qXNkGLYgN3Pjx5SGYxXG2WPYQdyCPdu4qCfGqCSlv7Knz%2FffJ1eWfwvZIk%2F0l0HXmX3mQNNtvowglMbfvVIOYKnTfGYWftbTLyH9WAWFRxtkEA0nu3odPX3sM7PhxuKAnj1ZzdYOOM3tJKVNK41qocslcJx6PBAn3oy1M6ertkDM6CzRZl28H9BvKU4mYUn4ZJUgumQDwnnmtPsidJRrky7cNjVho6Ei9E2dBxHcs0QgiYWBdxM9BSES2O%2BMSSWHoNfL8vNXu9xWwqs9IACFnP8v9dmZa4MjblJ8VSYEGiNJc5422J1prqon4J%2FFxaQZO3KBhZu8mm4m1P38AqY1vhoODXKn9c2BbIvZIOVMIiFrekZdzZAAUwgQcOr3td25jUjAsXaKCP7NKe9cOsVz%2Bf09e1NcI%2BqSc3e4s%2FkULyAr0SqdP2TRMoFIRPu4dM%2Bcako4K9ngzHce4TlEgfBBkWLjkulmMsjWNz9OH51Z1cWpWoOkqjT2Zp4UOfHdi3hhdmRMnpfxZjFnohIaQUEJtMvjyL85EcRoA&xa=FFFF00000000016770EE&xt=&efy=1'

# 单例模式
generator = UmidTokenGenerator()

def get_umid_token():
    """
    获取UMID Token的便捷函数
    
    Returns:
        dict: 包含token信息的字典
    """
    return generator.generate_token()

# 简单测试函数
if __name__ == "__main__":
    token_result = get_umid_token()
    print("UMID Token:", token_result) 