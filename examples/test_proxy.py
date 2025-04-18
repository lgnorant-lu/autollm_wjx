"""
----------------------------------------------------------------
File name:                  test_proxy.py
Author:                     Ignorant-lu
Date created:               2025/05/01
Description:                测试代理功能
----------------------------------------------------------------

Changed history:
                            2025/05/01: 初始创建
----------------------------------------------------------------
"""

import os
import sys
import logging
import requests
from dotenv import load_dotenv

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv('.env.real')

# 导入代理工具
from backend.utils.proxy.utils import normalize_proxy_url, get_proxy_from_api, test_proxy, get_and_test_proxy, is_china_website, should_use_pinzan_proxy

def test_get_proxy():
    """测试获取代理"""
    # 从环境变量获取代理URL
    proxy_url = os.environ.get('PINZAN_API_URL')
    if not proxy_url:
        logger.error("环境变量中未设置PINZAN_API_URL")
        return False

    logger.info(f"原始代理URL: {proxy_url}")

    # 标准化代理URL
    normalized_url = normalize_proxy_url(proxy_url)
    logger.info(f"标准化后的代理URL: {normalized_url}")

    # 获取代理
    proxy = get_proxy_from_api(normalized_url)
    logger.info(f"获取到的代理: {proxy}")

    if not proxy:
        logger.error("获取代理失败")
        return False

    # 添加FTP代理支持
    if 'http' in proxy and 'https' in proxy:
        proxy['ftp'] = proxy['http']
        logger.info(f"添加FTP代理支持: {proxy['ftp']}")

    # 测试代理
    logger.info("测试代理连接...")
    if test_proxy(proxy, timeout=3, retries=2):
        logger.info("代理连接测试成功")
        return True
    else:
        logger.error("代理连接测试失败")
        return False

def test_get_and_test_proxy():
    """测试获取并测试代理"""
    # 从环境变量获取代理URL
    proxy_url = os.environ.get('PINZAN_API_URL')
    if not proxy_url:
        logger.error("环境变量中未设置PINZAN_API_URL")
        return False

    logger.info(f"原始代理URL: {proxy_url}")

    # 获取并测试代理，使用优化的参数
    proxy = get_and_test_proxy(proxy_url, max_retries=2, num_proxies=2, timeout=3)
    logger.info(f"获取并测试的代理: {proxy}")

    if proxy:
        # 打印详细信息
        if 'http' in proxy:
            logger.info(f"HTTP代理: {proxy['http']}")
        if 'https' in proxy:
            logger.info(f"HTTPS代理: {proxy['https']}")
        if 'ftp' in proxy:
            logger.info(f"FTP代理: {proxy['ftp']}")
        logger.info("获取并测试代理成功")
        return True
    else:
        logger.error("获取并测试代理失败")
        return False

def test_direct_request():
    """测试直接请求"""
    # 使用国内网站进行测试
    test_url = 'http://www.baidu.com'
    try:
        logger.info(f"测试直接请求URL: {test_url}")
        response = requests.get(test_url, timeout=3)
        if response.status_code == 200:
            logger.info(f"直接请求成功: {test_url}")
            logger.info(f"响应内容长度: {len(response.text)} 字节")
            return True
        else:
            logger.warning(f"直接请求失败: {test_url}, 状态码: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"直接请求异常: {test_url}, 错误: {e}")
        return False

def test_proxy_request():
    """测试代理请求"""
    # 从环境变量获取代理URL
    proxy_url = os.environ.get('PINZAN_API_URL')
    if not proxy_url:
        logger.error("环境变量中未设置PINZAN_API_URL")
        return False

    # 获取并测试代理
    proxy = get_and_test_proxy(proxy_url, max_retries=2, num_proxies=2, timeout=3)
    if not proxy:
        logger.error("获取代理失败")
        return False

    # 测试多个国内网站（因为品赞代理全部是国内IP）
    test_urls = [
        'http://www.baidu.com',    # 百度
        'http://www.qq.com',       # 腾讯
        'http://www.163.com',      # 网易
        'http://www.sina.com.cn',  # 新浪
        'http://www.sohu.com'      # 搜狐
    ]

    success = False
    for url in test_urls:
        try:
            logger.info(f"测试代理请求URL: {url}")
            response = requests.get(url, proxies=proxy, timeout=3)
            if response.status_code == 200:
                logger.info(f"代理请求成功: {url}")
                logger.info(f"响应内容: {response.text[:200]}...")
                success = True
                break
            else:
                logger.warning(f"代理请求失败: {url}, 状态码: {response.status_code}")
        except Exception as e:
            logger.warning(f"代理请求异常: {url}, 错误: {e}")

    return success

def test_website_classification():
    """测试网站分类功能"""
    # 测试国内网站
    china_websites = [
        'http://www.baidu.com',
        'http://www.qq.com',
        'http://www.163.com',
        'http://www.sina.com.cn',
        'http://www.taobao.com',
        'http://www.jd.com',
        'http://www.gov.cn',
        'http://www.edu.cn'
    ]

    # 测试国外网站
    foreign_websites = [
        'http://www.google.com',
        'http://www.facebook.com',
        'http://www.twitter.com',
        'http://www.youtube.com',
        'http://www.amazon.com',
        'http://www.openai.com',
        'http://www.github.com',
        'http://httpbin.org'
    ]

    # 测试本地网站
    local_websites = [
        'http://localhost:8080',
        'http://127.0.0.1:5000',
        'http://localhost'
    ]

    logger.info("测试国内网站判断:")
    for url in china_websites:
        result = is_china_website(url)
        should_use = should_use_pinzan_proxy(url)
        logger.info(f"{url} -> 国内网站: {result}, 应使用品赞代理: {should_use}")

    logger.info("测试国外网站判断:")
    for url in foreign_websites:
        result = is_china_website(url)
        should_use = should_use_pinzan_proxy(url)
        logger.info(f"{url} -> 国内网站: {result}, 应使用品赞代理: {should_use}")

    logger.info("测试本地网站判断:")
    for url in local_websites:
        result = is_china_website(url)
        should_use = should_use_pinzan_proxy(url)
        logger.info(f"{url} -> 国内网站: {result}, 应使用品赞代理: {should_use}")

if __name__ == "__main__":
    logger.info("开始测试代理功能")

    # 测试网站分类
    logger.info("测试网站分类...")
    test_website_classification()

    # 测试直接请求
    logger.info("测试直接请求...")
    test_direct_request()

    # 测试获取代理
    logger.info("测试获取代理...")
    test_get_proxy()

    # 测试获取并测试代理
    logger.info("测试获取并测试代理...")
    test_get_and_test_proxy()

    # 测试代理请求
    logger.info("测试代理请求...")
    test_proxy_request()

    logger.info("代理功能测试完成")
