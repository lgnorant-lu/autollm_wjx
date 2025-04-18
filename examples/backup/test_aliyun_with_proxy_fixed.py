"""
测试阿里云LLM与代理一起使用（修复版）
"""

import os
import sys
import json
import logging
import requests
from pathlib import Path
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# 添加项目根目录到系统路径
root_dir = str(Path(__file__).parent.parent)
sys.path.append(root_dir)

# 导入相关模块
from backend.core.llm_generator import LLMGenerator

def get_current_ip():
    """获取当前IP"""
    try:
        response = requests.get('http://httpbin.org/ip', timeout=10)
        if response.status_code == 200:
            logger.info(f"当前IP: {response.json().get('origin')}")
            return response.json().get('origin')
        else:
            logger.error(f"获取当前IP失败，状态码: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"获取当前IP异常: {e}")
        return None

def get_proxy_from_pinzan(proxy_url):
    """从品赞API获取代理"""
    try:
        # 确保使用HTTP协议
        if proxy_url.startswith('https://'):
            proxy_url = proxy_url.replace('https://', 'http://')
            logger.info(f"将HTTPS协议更改为HTTP: {proxy_url}")
        
        # 获取代理IP
        logger.info("尝试从品赞API获取代理IP...")
        api_response = requests.get(proxy_url, timeout=10, verify=False)
        
        if api_response.status_code == 200:
            logger.info(f"品赞API响应: {api_response.text[:200]}...")
            
            # 尝试解析JSON响应
            try:
                data = api_response.json()
                logger.info(f"解析的JSON数据: {data}")
                
                if data.get('code') == 0 and data.get('data', {}).get('list'):
                    proxy_info = data['data']['list'][0]
                    ip = proxy_info.get('ip')
                    port = proxy_info.get('port')
                    account = proxy_info.get('account')
                    password = proxy_info.get('password')
                    
                    logger.info(f"代理IP: {ip}")
                    logger.info(f"代理端口: {port}")
                    logger.info(f"账号: {account}")
                    logger.info(f"密码: {password}")
                    
                    if ip and port:
                        # 构建代理URL
                        if account and password:
                            proxy_str = f"http://{account}:{password}@{ip}:{port}"
                        else:
                            proxy_str = f"http://{ip}:{port}"
                        
                        logger.info(f"代理URL: {proxy_str}")
                        return proxy_str
                    else:
                        logger.error("未找到代理IP或端口")
                else:
                    logger.error(f"品赞API返回错误: {data}")
            except ValueError:
                # 如果不是JSON，尝试解析TXT格式
                lines = api_response.text.strip().split('\n')
                if lines:
                    ip_port = lines[0].strip()
                    logger.info(f"从TXT响应中获取到IP:端口 - {ip_port}")
                    
                    if ':' in ip_port:
                        # 构建代理URL
                        proxy_str = f"http://{ip_port}"
                        logger.info(f"代理URL: {proxy_str}")
                        return proxy_str
                    else:
                        logger.error(f"无法从TXT响应中解析IP:端口 - {lines}")
        else:
            logger.error(f"品赞API请求失败，状态码: {api_response.status_code}")
    except Exception as e:
        logger.error(f"获取代理异常: {e}")
    
    return None

def main():
    """主函数"""
    # 加载环境变量
    load_dotenv('.env.real')
    
    # 获取阿里云API密钥和品赞代理URL
    api_key = os.environ.get('ALIYUN_API_KEY')
    proxy_url = os.environ.get('PINZAN_API_URL')
    
    if not api_key:
        logger.error("未设置阿里云API密钥，请在.env.real文件中设置ALIYUN_API_KEY")
        return
    
    if not proxy_url:
        logger.error("未设置品赞代理URL，请在.env.real文件中设置PINZAN_API_URL")
        return
    
    logger.info(f"阿里云API密钥: {api_key[:5]}...")
    logger.info(f"品赞代理URL: {proxy_url[:30]}...")
    
    # 获取当前IP
    current_ip = get_current_ip()
    
    # 从品赞API获取代理
    proxy_str = get_proxy_from_pinzan(proxy_url)
    if not proxy_str:
        logger.error("无法从品赞API获取代理")
        return
    
    # 设置代理
    proxy = {'http': proxy_str, 'https': proxy_str}
    
    # 初始化LLM生成器
    logger.info("开始初始化阿里云LLM生成器（使用代理）...")
    try:
        llm_gen = LLMGenerator(model_type='aliyun', api_key=api_key, proxy=proxy)
        logger.info("阿里云LLM生成器初始化成功")
        
        # 测试生成文本
        logger.info("测试生成文本...")
        question_data = {
            'title': '测试问卷',
            'questions': [
                {
                    'id': '1',
                    'index': '1',
                    'title': '你好，请介绍一下自己的优点',
                    'type': 1,  # 填空题
                    'options': []
                }
            ]
        }
        
        # 生成答案
        try:
            answers = llm_gen.generate_answers(question_data)
            logger.info(f"生成的答案: {answers}")
            logger.info("测试成功")
        except Exception as e:
            logger.error(f"生成答案失败: {e}")
            logger.error("测试失败")
    except Exception as e:
        logger.error(f"阿里云LLM生成器初始化失败: {e}")
        logger.error("测试失败")
    
    # 获取当前IP（再次检查，看是否使用了代理）
    new_ip = get_current_ip()
    
    # 比较IP
    if current_ip and new_ip:
        if current_ip != new_ip:
            logger.info("IP已更换，代理生效")
        else:
            logger.warning("IP未更换，代理未生效")

if __name__ == "__main__":
    main()
