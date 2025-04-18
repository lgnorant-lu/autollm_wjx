"""
----------------------------------------------------------------
File name:                  proxy_test.py
Author:                     Ignorant-lu
Date created:               2025/04/02
Description:                代理测试工具
----------------------------------------------------------------

Changed history:
                            2025/04/02: 初始创建
----------------------------------------------------------------
"""

import os
import sys
import logging
import argparse
import requests
import json
import socket
import time
from pathlib import Path

# 添加项目根目录到系统路径
root_dir = str(Path(__file__).parent.parent)
sys.path.append(root_dir)

# 直接导入模块，避免使用backend前缀
sys.path.append(os.path.join(root_dir, 'backend'))

# 导入相关模块
from utils.proxy.providers.pinzan_provider import PinzanProvider
from utils.env_loader import EnvLoader

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 设置品赞IP提供商的日志级别
logger = logging.getLogger('backend.utils.proxy.providers.pinzan_provider')

def setup_argparse():
    """
    设置命令行参数

    Returns:
        argparse.ArgumentParser: 命令行参数解析器
    """
    parser = argparse.ArgumentParser(description='代理测试工具')

    # 测试类型
    parser.add_argument('--test-type', '-t', type=str, default='http',
                        choices=['http', 'https', 'socks5', 'all'],
                        help='测试类型: http, https, socks5, all')

    # 测试URL
    parser.add_argument('--url', '-u', type=str,
                        default='http://httpbin.org/ip',
                        help='测试URL')

    # 代理协议
    parser.add_argument('--protocol', '-p', type=str, default='http',
                        choices=['http', 'https', 'socks5'],
                        help='代理协议: http, https, socks5')

    # 详细模式
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='详细模式')

    # 超时时间
    parser.add_argument('--timeout', type=int, default=10,
                        help='请求超时时间（秒）')

    # 重试次数
    parser.add_argument('--retries', type=int, default=3,
                        help='请求重试次数')

    # 环境变量文件
    parser.add_argument('--env-file', type=str, default='.env',
                        help='环境变量文件路径')

    # API URL
    parser.add_argument('--api-url', type=str, default='',
                        help='品赞API URL，如果不提供则从环境变量中获取')

    return parser

def get_direct_ip(url, timeout=10):
    """
    获取直连IP

    Args:
        url: 测试URL
        timeout: 超时时间（秒）

    Returns:
        str: 直连IP
    """
    try:
        response = requests.get(url, timeout=timeout)
        if 'ip' in response.json():
            return response.json()['ip']
        elif 'origin' in response.json():
            return response.json()['origin']
        else:
            return None
    except Exception as e:
        logging.error(f"获取直连IP失败: {str(e)}")
        return None

def test_http_proxy(provider, url, timeout=10, retries=3):
    """
    测试HTTP代理

    Args:
        provider: 代理提供商
        url: 测试URL
        timeout: 超时时间（秒）
        retries: 重试次数

    Returns:
        bool: 测试是否成功
    """
    logging.info("=== 测试HTTP代理 ===")

    # 获取直连IP
    direct_ip = get_direct_ip(url, timeout)
    if not direct_ip:
        logging.error("无法获取直连IP，跳过测试")
        return False

    logging.info(f"直连IP: {direct_ip}")

    # 获取代理
    proxy = provider.get_proxy()
    if not proxy:
        logging.error("获取代理失败")
        return False

    logging.info(f"代理信息: {proxy}")

    # 测试代理
    success = False
    for i in range(retries):
        try:
            logging.info(f"尝试 {i+1}/{retries}...")
            proxy_response = requests.get(url, proxies=proxy, timeout=timeout)

            if 'ip' in proxy_response.json():
                proxy_ip = proxy_response.json()['ip']
            elif 'origin' in proxy_response.json():
                proxy_ip = proxy_response.json()['origin']
            else:
                logging.error("响应中没有IP信息")
                continue

            logging.info(f"代理IP: {proxy_ip}")

            if direct_ip != proxy_ip:
                logging.info("代理测试成功，IP已更换")
                success = True
                break
            else:
                logging.warning("代理测试失败，IP未更换")
        except Exception as e:
            logging.error(f"代理测试异常: {str(e)}")
            time.sleep(1)  # 等待1秒后重试

    return success

def test_https_proxy(provider, url, timeout=10, retries=3):
    """
    测试HTTPS代理

    Args:
        provider: 代理提供商
        url: 测试URL
        timeout: 超时时间（秒）
        retries: 重试次数

    Returns:
        bool: 测试是否成功
    """
    logging.info("=== 测试HTTPS代理 ===")

    # 确保URL是HTTPS
    if not url.startswith('https://'):
        url = 'https://httpbin.org/ip'
        logging.info(f"切换到HTTPS URL: {url}")

    # 获取直连IP
    direct_ip = get_direct_ip(url, timeout)
    if not direct_ip:
        logging.error("无法获取直连IP，跳过测试")
        return False

    logging.info(f"直连IP: {direct_ip}")

    # 获取代理
    proxy = provider.get_proxy()
    if not proxy:
        logging.error("获取代理失败")
        return False

    logging.info(f"代理信息: {proxy}")

    # 测试代理
    success = False
    for i in range(retries):
        try:
            logging.info(f"尝试 {i+1}/{retries}...")
            proxy_response = requests.get(url, proxies=proxy, timeout=timeout)

            if 'ip' in proxy_response.json():
                proxy_ip = proxy_response.json()['ip']
            elif 'origin' in proxy_response.json():
                proxy_ip = proxy_response.json()['origin']
            else:
                logging.error("响应中没有IP信息")
                continue

            logging.info(f"代理IP: {proxy_ip}")

            if direct_ip != proxy_ip:
                logging.info("代理测试成功，IP已更换")
                success = True
                break
            else:
                logging.warning("代理测试失败，IP未更换")
        except Exception as e:
            logging.error(f"代理测试异常: {str(e)}")
            time.sleep(1)  # 等待1秒后重试

    return success

def test_socks5_proxy(provider, url, timeout=10, retries=3):
    """
    测试SOCKS5代理

    Args:
        provider: 代理提供商
        url: 测试URL
        timeout: 超时时间（秒）
        retries: 重试次数

    Returns:
        bool: 测试是否成功
    """
    logging.info("=== 测试SOCKS5代理 ===")

    # 检查是否安装了socks库
    try:
        import socks
        import socket
    except ImportError:
        logging.error("未安装socks库，请使用pip install PySocks安装")
        return False

    # 获取直连IP
    direct_ip = get_direct_ip(url, timeout)
    if not direct_ip:
        logging.error("无法获取直连IP，跳过测试")
        return False

    logging.info(f"直连IP: {direct_ip}")

    # 获取代理
    proxy = provider.get_proxy()
    if not proxy:
        logging.error("获取代理失败")
        return False

    logging.info(f"代理信息: {proxy}")

    # 从代理URL中提取信息
    http_proxy = proxy.get('http', '')
    if not http_proxy:
        logging.error("代理URL为空")
        return False

    # 解析代理URL
    try:
        # 提取协议、认证信息、IP和端口
        if '@' in http_proxy:
            auth, ip_port = http_proxy.split('@')
            protocol = auth.split('://')[0]
            auth = auth.split('://')[1]
            username, password = auth.split(':')
        else:
            protocol, ip_port = http_proxy.split('://')
            username, password = None, None

        ip, port = ip_port.split(':')
        port = int(port)

        logging.info(f"解析的代理信息 - 协议: {protocol}, IP: {ip}, 端口: {port}, 用户名: {username}, 密码: {password}")
    except Exception as e:
        logging.error(f"解析代理URL失败: {str(e)}")
        return False

    # 测试代理
    success = False
    for i in range(retries):
        try:
            logging.info(f"尝试 {i+1}/{retries}...")

            # 保存原始socket
            original_socket = socket.socket

            # 设置SOCKS5代理
            socks.set_default_proxy(socks.SOCKS5, ip, port, username=username, password=password)
            socket.socket = socks.socksocket

            # 发送请求
            proxy_response = requests.get(url, timeout=timeout)

            # 恢复原始socket
            socket.socket = original_socket

            if 'ip' in proxy_response.json():
                proxy_ip = proxy_response.json()['ip']
            elif 'origin' in proxy_response.json():
                proxy_ip = proxy_response.json()['origin']
            else:
                logging.error("响应中没有IP信息")
                continue

            logging.info(f"代理IP: {proxy_ip}")

            if direct_ip != proxy_ip:
                logging.info("代理测试成功，IP已更换")
                success = True
                break
            else:
                logging.warning("代理测试失败，IP未更换")
        except Exception as e:
            logging.error(f"代理测试异常: {str(e)}")
            # 恢复原始socket
            socket.socket = original_socket
            time.sleep(1)  # 等待1秒后重试

    return success

def get_current_ip():
    """
    获取当前IP

    Returns:
        str: 当前IP
    """
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=10)
        return response.json()['ip']
    except Exception as e:
        logging.error(f"获取当前IP失败: {str(e)}")
        return None

def main():
    """
    主函数
    """
    # 解析命令行参数
    parser = setup_argparse()
    args = parser.parse_args()

    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)

    # 加载环境变量
    env_file = Path(args.env_file)
    if env_file.exists():
        EnvLoader.load_env(str(env_file))
        logging.info(f"从文件加载环境变量: {env_file}")
    else:
        logging.warning(f"环境变量文件不存在: {env_file}")

    # 获取API URL
    api_url = args.api_url or os.environ.get('PINZAN_API_URL', '')
    if not api_url:
        logging.error("未设置品赞IP API URL，请在环境变量中设置PINZAN_API_URL或使用--api-url参数")
        return

    # 获取当前IP
    current_ip = get_current_ip()
    if current_ip:
        logging.info(f"当前IP: {current_ip}")
        logging.info(f"请确保已将此IP添加到品赞IP的白名单中")

    # 创建品赞IP提供商
    provider = PinzanProvider(
        api_url=api_url,
        protocol=args.protocol
    )

    # 运行测试
    results = {}

    if args.test_type in ['http', 'all']:
        results['http'] = test_http_proxy(provider, args.url, args.timeout, args.retries)

    if args.test_type in ['https', 'all']:
        https_url = args.url if args.url.startswith('https://') else 'https://httpbin.org/ip'
        results['https'] = test_https_proxy(provider, https_url, args.timeout, args.retries)

    if args.test_type in ['socks5', 'all']:
        results['socks5'] = test_socks5_proxy(provider, args.url, args.timeout, args.retries)

    # 输出测试结果
    logging.info("=== 测试结果 ===")
    for test_type, success in results.items():
        logging.info(f"{test_type}: {'成功' if success else '失败'}")

    # 总结
    if all(results.values()):
        logging.info("所有测试都成功")
    elif any(results.values()):
        logging.info("部分测试成功")
    else:
        logging.error("所有测试都失败")
        if current_ip:
            logging.error(f"请确保已将IP {current_ip} 添加到品赞IP的白名单中")

if __name__ == "__main__":
    main()
