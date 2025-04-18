"""
----------------------------------------------------------------
File name:                  utils.py
Author:                     Ignorant-lu
Date created:               2025/04/18
Description:                代理工具函数
----------------------------------------------------------------

Changed history:
                            2025/04/18: 初始创建
----------------------------------------------------------------
"""

import logging
import requests
import time
import os
import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# 获取日志记录器
logger = logging.getLogger(__name__)

def is_china_website(url):
    """
    检查URL是否为国内网站

    通过域名后缀和常见国内网站域名判断

    Args:
        url (str): 要检查的URL

    Returns:
        bool: 如果是国内网站返回True，否则返回False
    """

    # 如果是本地地址或内网地址，返回True
    if url.startswith('http://localhost') or url.startswith('http://127.0.0.1'):
        return True
    if not url:
        return False

    # 解析URL获取域名
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()

    # 如果是IP地址，无法判断，返回False
    if re.match(r'^\d+\.\d+\.\d+\.\d+$', domain):
        return False

    # 常见国内网站域名
    china_domains = [
        'baidu.com', 'qq.com', '163.com', 'sina.com.cn', 'sohu.com',
        'taobao.com', 'jd.com', 'weibo.com', 'aliyun.com', 'tencent.com',
        'bilibili.com', 'zhihu.com', 'douban.com', 'iqiyi.com', 'youku.com',
        'csdn.net', 'cnblogs.com', '126.com', 'ctrip.com', 'meituan.com',
        'wjx.cn', 'wjx.top'  # 问卷星域名
    ]

    # 检查是否为常见国内网站
    for china_domain in china_domains:
        if domain.endswith(china_domain):
            return True

    # 检查是否为中国域名
    china_tlds = ['.cn', '.com.cn', '.net.cn', '.org.cn', '.gov.cn', '.edu.cn']
    for tld in china_tlds:
        if domain.endswith(tld):
            return True

    # 默认返回False
    return False

def normalize_proxy_url(proxy_url):
    """
    标准化代理URL

    将代理URL标准化为HTTP协议，并确保协议参数和格式参数正确

    Args:
        proxy_url (str): 代理URL

    Returns:
        str: 标准化后的代理URL
    """
    if not proxy_url:
        return None

    # 记录原始URL
    logger.info(f"标准化代理URL: {proxy_url}")

    # 解析URL
    parsed_url = urlparse(proxy_url)

    # 确保使用HTTP协议
    if parsed_url.scheme == 'https':
        parsed_url = parsed_url._replace(scheme='http')
        logger.info(f"将HTTPS协议更改为HTTP: {urlunparse(parsed_url)}")

    # 如果是品赞API URL，确保所有必要参数正确
    if 'ipzan.com' in parsed_url.netloc:
        # 警告用户品赞代理只适用于国内网站
        logger.warning("注意: 品赞代理全部是国内IP，只能用于访问国内网站，不适合访问国外网站")
        # 解析查询参数
        query_params = parse_qs(parsed_url.query)

        # 检查必需参数
        if 'no' not in query_params:
            logger.error(f"缺少必需参数: no (套餐编号/账号)")
            return None

        # 检查模式参数
        if 'mode' in query_params:
            mode = query_params['mode'][0]
            # 如果是auth模式，需要检查secret参数
            if mode == 'auth' and 'secret' not in query_params:
                logger.error(f"使用auth模式时缺少secret参数")
                return None
        else:
            # 默认使用whitelist模式
            query_params['mode'] = ['whitelist']
            logger.info(f"添加参数: mode=whitelist")

        # 添加其他参数的默认值
        default_params = {
            'protocol': '1',  # HTTP/HTTPS协议，1表示HTTP/HTTPS，3表示SOCKS5
            'format': 'json',  # 返回格式，可选json或txt
            'num': '1',  # 提取数量，默认为1
            'minute': '5',  # 占用时长，可选值为3、5、10、15、30
            'pool': 'ordinary'  # IP类型，可选值为quality(优质IP)或ordinary(普通IP)
        }

        for param, default_value in default_params.items():
            if param not in query_params:
                query_params[param] = [default_value]
                logger.info(f"添加参数: {param}={default_value}")

        # 重新构建查询字符串
        query_string = urlencode(query_params, doseq=True)
        parsed_url = parsed_url._replace(query=query_string)

    # 重新构建URL
    normalized_url = urlunparse(parsed_url)
    logger.info(f"标准化后的代理URL: {normalized_url}")

    return normalized_url

def get_proxy_from_api(proxy_url):
    """
    从API获取代理

    从代理API获取代理IP和端口

    Args:
        proxy_url (str): 代理API URL

    Returns:
        dict: 代理配置，格式为 {'http': 'http://...', 'https': 'http://...'}
        None: 如果获取失败
    """
    if not proxy_url:
        return None

    # 标准化代理URL
    proxy_url = normalize_proxy_url(proxy_url)
    if not proxy_url:
        return None

    try:
        # 发送请求获取代理
        logger.info(f"尝试从API获取代理: {proxy_url}")
        api_response = requests.get(proxy_url, timeout=10, verify=False)

        if api_response.status_code == 200:
            logger.info(f"API响应: {api_response.text[:200]}...")

            # 尝试解析JSON响应
            try:
                data = api_response.json()
                logger.info(f"解析的JSON数据: {data}")

                # 处理品赞API响应
                if 'ipzan.com' in proxy_url:
                    logger.info(f"品赞API响应数据: {data}")

                    # 处理成功响应
                    if data.get('code') == 0:
                        # 检查数据格式
                        ip = None
                        port = None
                        account = None
                        password = None

                        # 处理不同的数据结构
                        if data.get('data'):
                            # 品赞API标准格式: {"data": {"list": [{"ip": "...", "port": "...", "account": "...", "password": "..."}]}}
                            if isinstance(data.get('data'), dict) and data.get('data', {}).get('list'):
                                proxy_list = data['data']['list']
                                if proxy_list and len(proxy_list) > 0:
                                    proxy_info = proxy_list[0]
                                    ip = proxy_info.get('ip')
                                    port = proxy_info.get('port')
                                    account = proxy_info.get('account')
                                    password = proxy_info.get('password')
                                    # 获取其他信息用于日志
                                    expired_time = proxy_info.get('expired')  # 过期时间
                                    net_type = proxy_info.get('net')  # 网络类型（电信、联通等）
                                    logger.info(f"从品赞API解析代理信息: IP={ip}, 端口={port}, 账号={account}, 密码={password}, 网络={net_type}")
                                    if expired_time:
                                        # 转换成时间格式
                                        import datetime
                                        expired_date = datetime.datetime.fromtimestamp(expired_time/1000)
                                        logger.info(f"代理过期时间: {expired_date.strftime('%Y-%m-%d %H:%M:%S')}")

                            # 格式2: {"data": [{"ip": "...", "port": "..."}]}
                            elif isinstance(data.get('data'), list) and len(data.get('data')) > 0:
                                proxy_info = data['data'][0]
                                ip = proxy_info.get('ip')
                                port = proxy_info.get('port')
                                account = proxy_info.get('account')
                                password = proxy_info.get('password')
                                logger.info(f"从格式2解析代理信息: IP={ip}, 端口={port}")

                            # 格式3: {"data": {"ip": "...", "port": "..."}}
                            elif isinstance(data.get('data'), dict) and 'ip' in data.get('data'):
                                proxy_info = data['data']
                                ip = proxy_info.get('ip')
                                port = proxy_info.get('port')
                                account = proxy_info.get('account')
                                password = proxy_info.get('password')
                                logger.info(f"从格式3解析代理信息: IP={ip}, 端口={port}")

                        # 直接在根级别包含IP和端口
                        elif 'ip' in data and 'port' in data:
                            ip = data.get('ip')
                            port = data.get('port')
                            account = data.get('account')
                            password = data.get('password')
                            logger.info(f"从根级别解析代理信息: IP={ip}, 端口={port}")

                        # 记录解析到的代理信息
                        if ip and port:
                            logger.info(f"代理IP: {ip}")
                            logger.info(f"代理端口: {port}")
                            if account:
                                logger.info(f"账号: {account}")
                            if password:
                                logger.info(f"密码: {password}")

                            # 构建代理URL
                            if account and password:
                                proxy_str = f"http://{account}:{password}@{ip}:{port}"
                            else:
                                proxy_str = f"http://{ip}:{port}"

                            logger.info(f"代理URL: {proxy_str}")
                            return {'http': proxy_str, 'https': proxy_str}
                        else:
                            logger.warning(f"未找到代理IP或端口")
                    # 处理错误响应
                    elif data.get('code') == -1:
                        error_message = data.get('message', '')
                        logger.warning(f"品赞API返回错误: {error_message}")

                        # 定义错误类型和对应的处理方式
                        error_types = {
                            '白名单': 'whitelist_error',  # 白名单错误
                            '套餐余量不足': 'package_error',  # 套餐错误
                            '套餐已过期': 'package_error',
                            '套餐被禁用': 'package_error',
                            '提取频率过快': 'rate_limit_error',  # 频率限制
                            '余额不足': 'balance_error',  # 余额不足
                            '用户被禁用': 'user_error',  # 用户错误
                            '身份未认证': 'auth_error',  # 认证错误
                            'secret密匙错误': 'auth_error',
                            '账号密码错误': 'auth_error'
                        }

                        # 确定错误类型
                        error_type = None
                        for key, value in error_types.items():
                            if key in error_message:
                                error_type = value
                                break

                        # 根据错误类型处理
                        if error_type == 'whitelist_error':
                            # 如果是白名单错误，尝试切换到auth模式
                            parsed_url = urlparse(proxy_url)
                            query_params = parse_qs(parsed_url.query)

                            # 检查当前模式
                            current_mode = query_params.get('mode', [''])[0]

                            if current_mode != 'auth':
                                # 切换到auth模式
                                query_params['mode'] = ['auth']

                                # 确保有secret参数
                                if 'secret' not in query_params and 'no' in query_params:
                                    # 使用账号作为密码，实际应该使用正确的密码
                                    # 如果环境变量中有密码，优先使用环境变量中的密码
                                    secret = os.environ.get('PINZAN_SECRET', query_params['no'][0])
                                    query_params['secret'] = [secret]
                                    logger.info(f"添加secret参数: {secret}")

                                # 重新构建查询字符串
                                query_string = urlencode(query_params, doseq=True)
                                parsed_url = parsed_url._replace(query=query_string)
                                new_url = urlunparse(parsed_url)

                                logger.info(f"尝试切换到auth模式: {new_url}")
                                return get_proxy_from_api(new_url)  # 递归调用自身
                            else:
                                # 如果已经是auth模式但仍然失败
                                logger.warning(f"已经使用auth模式，但仍然返回错误，可能是短时间内多次请求触发了限制")
                        elif error_type == 'rate_limit_error':
                            # 如果是频率限制，等待一段时间再重试
                            logger.warning("品赞API提取频率过快，等待几秒后再重试")
                            time.sleep(3)  # 等待3秒
                            return get_proxy_from_api(proxy_url)  # 递归调用自身
                        elif error_type == 'balance_error':
                            # 如果是余额不足，无法继续
                            logger.error("品赞API余额不足，请充值后再使用")
                            return None
                        elif error_type == 'package_error':
                            # 套餐相关错误
                            logger.warning(f"品赞API返回套餐错误: {error_message}")
                        elif error_type == 'user_error':
                            # 用户错误
                            logger.warning(f"品赞API返回用户错误: {error_message}")
                        elif error_type == 'auth_error':
                            # 认证错误
                            logger.warning(f"品赞API返回认证错误: {error_message}")
                        else:
                            # 其他错误
                            logger.warning(f"品赞API返回未知错误: {error_message}")

                        # 尝试使用环境变量中的代理
                        http_proxy = os.environ.get('HTTP_PROXY')
                        https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('HTTP_PROXY')

                        if http_proxy:
                            logger.info(f"尝试使用环境变量中的代理: HTTP_PROXY={http_proxy}, HTTPS_PROXY={https_proxy}")
                            # 测试环境变量中的代理是否可用
                            env_proxies = {
                                'http': http_proxy,
                                'https': https_proxy
                            }
                            if test_proxy(env_proxies, timeout=2):
                                logger.info(f"环境变量代理测试成功: {env_proxies}")
                                return env_proxies

                        # 直接返回空结果，系统将降级使用直接连接
                        logger.warning(f"无法获取代理，系统将降级使用直接连接")
                        return None
                    else:
                        logger.warning(f"API返回错误: {data}")
                else:
                    logger.warning(f"API返回错误: {data}")
            except ValueError:
                # 如果不是JSON，尝试解析TXT格式
                text_response = api_response.text.strip()
                logger.info(f"收到文本响应: {text_response[:200]}...")

                # 尝试不同的分隔符
                for separator in ['\n', '\r\n', ';', ',']:
                    lines = text_response.split(separator)
                    if len(lines) > 0:
                        # 处理第一行
                        first_line = lines[0].strip()
                        logger.info(f"尝试解析行: {first_line}")

                        # 尝试解析IP:PORT格式
                        if ':' in first_line:
                            parts = first_line.split(':')
                            if len(parts) >= 2:
                                ip = parts[0].strip()
                                port = parts[1].strip()

                                # 检查是否有账号密码
                                if len(parts) >= 4:  # IP:PORT:ACCOUNT:PASSWORD
                                    account = parts[2].strip()
                                    password = parts[3].strip()
                                    proxy_str = f"http://{account}:{password}@{ip}:{port}"
                                else:
                                    proxy_str = f"http://{ip}:{port}"

                                logger.info(f"从文本响应中解析到代理: {proxy_str}")
                                return {'http': proxy_str, 'https': proxy_str}

                        # 尝试解析空格分隔的格式 (IP PORT ACCOUNT PASSWORD)
                        parts = first_line.split()
                        if len(parts) >= 2:
                            ip = parts[0].strip()
                            port = parts[1].strip()

                            # 检查是否有账号密码
                            if len(parts) >= 4:
                                account = parts[2].strip()
                                password = parts[3].strip()
                                proxy_str = f"http://{account}:{password}@{ip}:{port}"
                            else:
                                proxy_str = f"http://{ip}:{port}"

                            logger.info(f"从文本响应中解析到代理: {proxy_str}")
                            return {'http': proxy_str, 'https': proxy_str}

                logger.warning(f"无法从文本响应中解析代理信息: {text_response[:200]}")
        else:
            logger.warning(f"API请求失败，状态码: {api_response.status_code}")
    except Exception as e:
        logger.warning(f"获取代理异常: {e}")

    return None

def should_use_pinzan_proxy(url):
    """
    检查是否应该使用品赞代理访问给定URL

    品赞代理全部是国内IP，只适合访问国内网站

    Args:
        url (str): 要访问的URL

    Returns:
        bool: 如果应该使用品赞代理返回True，否则返回False
    """
    # 如果URL为空，返回False
    if not url:
        return False

    # 如果是国内网站，返回True
    return is_china_website(url)

def test_proxy(proxy, timeout=3, retries=2):
    """
    测试代理连接

    测试代理连接是否可用

    Args:
        proxy (dict): 代理配置，格式为 {'http': 'http://...', 'https': 'http://...'}
        timeout (int): 连接超时时间，单位为秒，默认为3秒
        retries (int): 每个网站的重试次数，默认为2次

    Returns:
        bool: 测试是否成功
    """
    if not proxy:
        return False

    # 测试网站列表 - 只使用国内网站（因为品赞代理全部是国内IP）
    test_urls = [
        'http://www.baidu.com',  # 百度，国内最常用的网站
        'http://www.qq.com',     # 腾讯，国内常用网站
        'http://www.163.com',    # 网易，国内常用网站
        'http://www.sina.com.cn' # 新浪，国内常用网站
    ]

    for url in test_urls:
        # 对每个网站进行多次尝试
        for retry in range(retries):
            try:
                logger.info(f"测试代理连接: {proxy}, URL: {url}, 尝试次数: {retry+1}/{retries}")
                test_response = requests.get(
                    url,
                    proxies=proxy,
                    timeout=timeout,
                    verify=False  # 忽略SSL证书验证
                )
                if test_response.status_code == 200:
                    logger.info(f"代理连接测试成功: {url}")
                    return True
                else:
                    logger.warning(f"代理连接测试失败: {url}, 状态码: {test_response.status_code}, 尝试次数: {retry+1}/{retries}")
            except Exception as e:
                logger.warning(f"代理连接测试异常: {url}, 错误: {e}, 尝试次数: {retry+1}/{retries}")

            # 如果不是最后一次尝试，等待一下再重试
            if retry < retries - 1:
                import time
                time.sleep(0.5)  # 等待500毫秒再重试

    # 如果所有测试都失败，尝试不使用账号密码
    if 'http' in proxy and '@' in proxy['http']:
        try:
            # 提取IP和端口
            auth_url = proxy['http']
            ip_port = auth_url.split('@')[1]
            proxy_str = f"http://{ip_port}"
            logger.info(f"尝试不使用账号密码: {proxy_str}")
            proxy_no_auth = {'http': proxy_str, 'https': proxy_str}

            # 对无认证代理进行测试
            for url in test_urls:
                # 对每个网站进行多次尝试
                for retry in range(retries):
                    try:
                        logger.info(f"测试代理连接(无认证): {proxy_no_auth}, URL: {url}, 尝试次数: {retry+1}/{retries}")
                        test_response = requests.get(
                            url,
                            proxies=proxy_no_auth,
                            timeout=timeout,
                            verify=False
                        )
                        if test_response.status_code == 200:
                            logger.info(f"代理连接测试成功(无认证): {url}")
                            # 如果无认证模式成功，替换原始代理对象
                            proxy['http'] = proxy_str
                            proxy['https'] = proxy_str
                            if 'ftp' in proxy:
                                proxy['ftp'] = proxy_str
                            return True
                        else:
                            logger.warning(f"代理连接测试失败(无认证): {url}, 状态码: {test_response.status_code}, 尝试次数: {retry+1}/{retries}")
                    except Exception as e:
                        logger.warning(f"代理连接测试异常(无认证): {url}, 错误: {e}, 尝试次数: {retry+1}/{retries}")

                    # 如果不是最后一次尝试，等待一下再重试
                    if retry < retries - 1:
                        import time
                        time.sleep(0.5)  # 等待500毫秒再重试
        except Exception as e:
            logger.warning(f"处理无认证代理异常: {e}")

    return False

def get_and_test_proxy(proxy_url, max_retries=2, num_proxies=2, timeout=3):
    """
    获取并测试代理

    从API获取代理，并测试连接是否可用

    Args:
        proxy_url (str): 代理API URL
        max_retries (int): 每个代理的最大重试次数，默认为2次
        num_proxies (int): 尝试获取的代理数量，默认为2个
        timeout (int): 连接超时时间，单位为秒，默认为3秒

    Returns:
        dict: 代理配置，格式为 {'http': 'http://...', 'https': 'http://...'}
        None: 如果获取失败或测试失败
    """
    if not proxy_url:
        logger.warning("代理URL为空")
        return None

    # 标准化代理URL
    proxy_url = normalize_proxy_url(proxy_url)
    if not proxy_url:
        logger.warning("标准化代理URL失败")
        return None

    # 尝试获取多个代理
    for i in range(num_proxies):
        try:
            # 获取代理
            proxy = get_proxy_from_api(proxy_url)
            if not proxy:
                logger.warning(f"第 {i+1}/{num_proxies} 次获取代理失败")
                # 如果获取失败，等待一下再重试
                if i < num_proxies - 1:
                    time.sleep(1)  # 等待一秒再重试
                continue

            # 添加FTP代理支持
            if 'http' in proxy and 'https' in proxy:
                # 添加FTP代理支持，使用与其他协议相同的代理地址
                proxy['ftp'] = proxy['http']

            # 测试代理，使用改进的test_proxy函数
            if test_proxy(proxy, timeout=timeout, retries=max_retries):
                logger.info(f"第 {i+1}/{num_proxies} 个代理测试成功")
                return proxy

            logger.warning(f"第 {i+1}/{num_proxies} 个代理测试失败")
            # 如果测试失败，等待一下再获取下一个代理
            if i < num_proxies - 1:
                time.sleep(1)  # 等待一秒再重试
        except Exception as e:
            logger.error(f"获取或测试代理异常: {e}")
            # 如果发生异常，等待一下再重试
            if i < num_proxies - 1:
                time.sleep(1)  # 等待一秒再重试

    logger.error(f"尝试了 {num_proxies} 个代理，均测试失败")
    return None
