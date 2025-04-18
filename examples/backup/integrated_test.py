"""
集成测试脚本 - 测试品赞代理和阿里云LLM
"""

import os
import sys
import logging
import requests
import threading
import argparse
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
        # 尝试多个服务获取IP
        services = [
            'http://httpbin.org/ip',  # 返回 {"origin": "x.x.x.x"}
            'https://api.ipify.org?format=json',  # 返回 {"ip": "x.x.x.x"}
            'https://ifconfig.me/ip'  # 直接返回IP地址
        ]
        
        for service in services:
            try:
                response = requests.get(service, timeout=10)
                if response.status_code == 200:
                    # 处理不同的响应格式
                    if service.endswith('/ip') and not service.endswith('.me/ip'):
                        # JSON响应
                        data = response.json()
                        ip = data.get('origin') or data.get('ip')
                        if ip:
                            logger.info(f"从{service}获取到当前IP: {ip}")
                            return ip
                    else:
                        # 纯文本响应
                        ip = response.text.strip()
                        logger.info(f"从{service}获取到当前IP: {ip}")
                        return ip
            except Exception as e:
                logger.warning(f"从{service}获取IP失败: {e}")
                continue
        
        logger.error("无法从任何服务获取当前IP")
        return None
    except Exception as e:
        logger.error(f"获取当前IP异常: {e}")
        return None

def test_direct_connection():
    """测试直接连接"""
    try:
        response = requests.get('http://httpbin.org/ip', timeout=10)
        if response.status_code == 200:
            logger.info(f"直接连接成功，IP: {response.json().get('origin')}")
            return response.json().get('origin')
        else:
            logger.error(f"直接连接失败，状态码: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"直接连接异常: {e}")
        return None

def test_proxy_connection(proxy_url):
    """测试代理连接"""
    try:
        # 打印代理URL
        logger.info(f"测试代理URL: {proxy_url}")
        
        # 如果是品赞API URL，尝试获取代理IP
        if 'ipzan.com' in proxy_url:
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
                                
                                # 测试代理连接
                                proxies = {'http': proxy_str, 'https': proxy_str}
                                
                                try:
                                    logger.info("尝试使用代理连接httpbin.org...")
                                    start_time = datetime.now()
                                    logger.info(f"请求开始时间: {start_time}")
                                    
                                    response = requests.get('http://httpbin.org/ip', 
                                                           proxies=proxies, 
                                                           timeout=10)
                                    
                                    end_time = datetime.now()
                                    logger.info(f"请求结束时间: {end_time}")
                                    logger.info(f"请求耗时: {(end_time - start_time).total_seconds()} 秒")
                                    
                                    logger.info(f"响应状态码: {response.status_code}")
                                    
                                    if response.status_code == 200:
                                        logger.info(f"代理连接成功，IP: {response.json().get('origin')}")
                                        return response.json().get('origin'), proxies
                                    else:
                                        logger.error(f"代理连接失败，状态码: {response.status_code}")
                                except Exception as e:
                                    logger.error(f"代理连接异常: {e}")
                            else:
                                logger.error("未找到代理IP或端口")
                        else:
                            logger.error(f"品赞API返回错误: {data}")
                            if data.get('code') == -1 and '白名单' in data.get('message', ''):
                                current_ip = get_current_ip()
                                if current_ip:
                                    logger.error(f"当前IP {current_ip} 不在品赞白名单中")
                                    logger.error(f"请先将此IP添加到品赞IP的白名单中，然后再运行测试")
                                    logger.error(f"白名单设置地址: https://www.ipzan.com/#/personal/whitelist")
                    except ValueError:
                        logger.error(f"无法解析JSON响应: {api_response.text}")
                else:
                    logger.error(f"品赞API请求失败，状态码: {api_response.status_code}")
            except Exception as e:
                logger.error(f"请求品赞API异常: {e}")
        else:
            # 直接使用代理URL
            proxies = {'http': proxy_url, 'https': proxy_url}
            logger.info(f"使用代理: {proxies}")
            
            try:
                response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=10)
                if response.status_code == 200:
                    logger.info(f"代理连接成功，IP: {response.json().get('origin')}")
                    return response.json().get('origin'), proxies
                else:
                    logger.error(f"代理连接失败，状态码: {response.status_code}")
            except Exception as e:
                logger.error(f"代理连接异常: {e}")
    except Exception as e:
        logger.error(f"代理连接异常: {e}")
    
    return None, None

def test_aliyun_llm(api_key, proxy=None):
    """测试阿里云LLM"""
    try:
        logger.info("初始化阿里云LLM生成器...")
        
        # 初始化参数
        kwargs = {}
        if proxy:
            kwargs['proxy'] = proxy
            logger.info(f"使用代理初始化LLM: {proxy}")
        
        # 初始化LLM生成器
        llm_gen = LLMGenerator(model_type='aliyun', api_key=api_key, **kwargs)
        logger.info("阿里云LLM生成器初始化成功")
        
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
        
        # 添加超时处理
        def generate_with_timeout():
            nonlocal llm_gen, question_data
            try:
                response = llm_gen.generate_answers(question_data)
                logger.info(f"生成的答案: {response}")
                return response
            except Exception as e:
                logger.error(f"生成答案异常: {e}")
                return None
        
        # 创建线程
        thread = threading.Thread(target=generate_with_timeout)
        thread.daemon = True
        thread.start()
        
        # 等待最多15秒
        thread.join(15)
        
        if thread.is_alive():
            logger.warning("生成答案超时，可能是网络问题或服务器响应慢")
            return False
        
        logger.info("阿里云LLM测试成功")
        return True
    except Exception as e:
        logger.error(f"阿里云LLM测试失败: {e}")
        return False

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='集成测试脚本 - 测试品赞代理和阿里云LLM')
    parser.add_argument('--test-type', '-t', type=str, default='all',
                        choices=['proxy', 'llm', 'all'],
                        help='测试类型: proxy, llm, all')
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
    
    # 获取品赞API URL和阿里云API密钥
    proxy_url = os.environ.get('PINZAN_API_URL')
    api_key = os.environ.get('ALIYUN_API_KEY')
    
    # 测试品赞代理
    if args.test_type in ['proxy', 'all']:
        if not proxy_url:
            logger.error(f"未设置品赞API URL，请在{args.env_file}文件中设置PINZAN_API_URL")
        else:
            logger.info(f"品赞API URL: {proxy_url[:30]}...")
            
            # 获取当前IP
            current_ip = get_current_ip()
            if current_ip:
                logger.info(f"当前IP: {current_ip}")
                logger.info(f"请确保已将此IP添加到品赞IP的白名单中")
                logger.info(f"白名单设置地址: https://www.ipzan.com/#/personal/whitelist")
            
            # 测试直接连接
            direct_ip = test_direct_connection()
            
            # 测试代理连接
            proxy_ip, proxies = test_proxy_connection(proxy_url)
            
            # 比较结果
            if direct_ip and proxy_ip:
                if direct_ip != proxy_ip:
                    logger.info("代理测试成功，IP已更换")
                else:
                    logger.warning("代理测试失败，IP未更换")
            else:
                logger.error("代理测试失败，无法获取IP")
                if current_ip:
                    logger.error(f"请确保已将IP {current_ip} 添加到品赞IP的白名单中")
    
    # 测试阿里云LLM
    if args.test_type in ['llm', 'all']:
        if not api_key:
            logger.error(f"未设置阿里云API密钥，请在{args.env_file}文件中设置ALIYUN_API_KEY")
        else:
            logger.info(f"阿里云API密钥: {api_key[:5]}...")
            
            # 测试阿里云LLM（不使用代理）
            logger.info("测试阿里云LLM（不使用代理）...")
            llm_success = test_aliyun_llm(api_key)
            
            if llm_success:
                logger.info("阿里云LLM测试成功（不使用代理）")
            else:
                logger.error("阿里云LLM测试失败（不使用代理）")
            
            # 如果有代理，测试阿里云LLM（使用代理）
            if args.test_type == 'all' and 'proxies' in locals() and proxies:
                logger.info("测试阿里云LLM（使用代理）...")
                llm_proxy_success = test_aliyun_llm(api_key, proxies)
                
                if llm_proxy_success:
                    logger.info("阿里云LLM测试成功（使用代理）")
                else:
                    logger.error("阿里云LLM测试失败（使用代理）")

if __name__ == "__main__":
    main()
