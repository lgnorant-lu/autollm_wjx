"""
统一的参数化测试脚本 - 测试LLM提供商和代理
"""

import os
import sys
import logging
import argparse
import requests
from datetime import datetime
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

def test_llm(llm_type, api_key, proxy=None):
    """测试LLM"""
    try:
        logger.info(f"初始化{llm_type}生成器...")
        
        # 初始化参数
        kwargs = {}
        if proxy:
            kwargs['proxy'] = proxy
            logger.info(f"使用代理初始化LLM: {proxy}")
        
        # 初始化LLM生成器
        llm_gen = LLMGenerator(model_type=llm_type, api_key=api_key, **kwargs)
        logger.info(f"{llm_type}生成器初始化成功")
        
        # 测试生成答案
        logger.info("测试生成答案...")
        question_data = {
            'title': '测试问卷',
            'questions': [
                {
                    'id': '1',
                    'index': '1',
                    'title': '你好，请介绍一下自己',
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
            return True
        except Exception as e:
            logger.error(f"生成答案失败: {e}")
            logger.error("测试失败")
            return False
    except Exception as e:
        logger.error(f"{llm_type}生成器初始化失败: {e}")
        logger.error("测试失败")
        return False

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='统一的参数化测试脚本 - 测试LLM提供商和代理')
    parser.add_argument('--llm-type', '-l', type=str, default='aliyun',
                        choices=['aliyun', 'openai', 'zhipu', 'baidu', 'tuzi', 'gemini'],
                        help='LLM提供商类型')
    parser.add_argument('--use-proxy', '-p', action='store_true',
                        help='是否使用代理')
    parser.add_argument('--env-file', '-e', type=str, default='.env.real',
                        help='环境变量文件路径')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='详细模式')
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 加载环境变量
    load_dotenv(args.env_file)
    
    # 获取API密钥
    api_key_env_var = f"{args.llm_type.upper()}_API_KEY"
    api_key = os.environ.get(api_key_env_var)
    
    if not api_key:
        logger.error(f"未设置{args.llm_type}的API密钥，请在{args.env_file}文件中设置{api_key_env_var}")
        return
    
    logger.info(f"{args.llm_type}的API密钥: {api_key[:5]}...")
    
    # 获取当前IP
    current_ip = get_current_ip()
    
    # 如果使用代理，获取代理
    proxy = None
    if args.use_proxy:
        proxy_url = os.environ.get('PINZAN_API_URL')
        if not proxy_url:
            logger.error(f"未设置品赞代理URL，请在{args.env_file}文件中设置PINZAN_API_URL")
            return
        
        logger.info(f"品赞代理URL: {proxy_url[:30]}...")
        
        # 从品赞API获取代理
        proxy_str = get_proxy_from_pinzan(proxy_url)
        if proxy_str:
            proxy = {'http': proxy_str, 'https': proxy_str}
        else:
            logger.error("无法从品赞API获取代理")
            return
    
    # 测试LLM
    success = test_llm(args.llm_type, api_key, proxy)
    
    # 如果使用代理，再次获取当前IP，检查是否更换
    if args.use_proxy:
        new_ip = get_current_ip()
        
        # 比较IP
        if current_ip and new_ip:
            if current_ip != new_ip:
                logger.info("IP已更换，代理生效")
            else:
                logger.warning("IP未更换，代理未生效")

if __name__ == "__main__":
    main()
