# 代理优化文档

本文档提供了代理基类和工厂类的优化说明，包括设计思路、实现细节和使用示例。

> **重要提示：品赞IP代理全部是国内IP，只能用于访问国内网站，不适合访问国外网站。系统已经自动判断网站类型，只对国内网站使用品赞代理。**

## 设计思路

代理优化的主要目标是：

1. 提高代码复用性
2. 增强可扩展性
3. 简化使用方式
4. 提升错误处理能力
5. 智能判断代理适用性

为此，我们采用了工厂模式和策略模式的组合，通过代理工厂类创建不同类型的代理实例。同时，我们添加了网站分类和代理适用性检查功能，确保只对适合的网站使用品赞代理。

## 代理基类

代理基类定义了所有代理类型的通用接口和行为：

```python
class BaseProxy:
    """代理基类"""

    def __init__(self, proxy_url=None):
        """初始化代理"""
        self.proxy_url = proxy_url
        self.proxy_dict = None
        self.last_used = None
        self.success_count = 0
        self.fail_count = 0

    def get_proxy(self):
        """获取代理"""
        raise NotImplementedError("子类必须实现get_proxy方法")

    def test_proxy(self):
        """测试代理"""
        raise NotImplementedError("子类必须实现test_proxy方法")

    def format_proxy(self, proxy_str):
        """格式化代理字符串为代理字典"""
        if not proxy_str:
            return None

        self.proxy_dict = {
            'http': proxy_str,
            'https': proxy_str
        }

        return self.proxy_dict

    def update_stats(self, success=True):
        """更新代理使用统计"""
        self.last_used = datetime.now()
        if success:
            self.success_count += 1
        else:
            self.fail_count += 1
```

## 代理工厂类

代理工厂类负责创建不同类型的代理实例：

```python
def get_proxy_instance(proxy_type='pinzan', proxy_url=None):
    """
    获取代理实例

    Args:
        proxy_type: 代理类型，支持'pinzan'、'custom'等
        proxy_url: 代理URL，如果为None则使用环境变量中的配置

    Returns:
        代理实例
    """
    if proxy_type == 'pinzan':
        from .pinzan_proxy import PinzanProxy
        return PinzanProxy(proxy_url)
    elif proxy_type == 'custom':
        from .custom_proxy import CustomProxy
        return CustomProxy(proxy_url)
    else:
        raise ValueError(f"不支持的代理类型: {proxy_type}")
```

## 品赞代理实现

品赞代理类继承自代理基类，实现了特定的获取和测试方法：

```python
class PinzanProxy(BaseProxy):
    """品赞代理类"""

    def __init__(self, proxy_url=None):
        """初始化品赞代理"""
        super().__init__(proxy_url)
        if not self.proxy_url:
            self.proxy_url = os.environ.get('PINZAN_API_URL')

    def get_proxy(self):
        """从品赞API获取代理"""
        try:
            # 确保使用HTTP协议
            if self.proxy_url.startswith('https://'):
                self.proxy_url = self.proxy_url.replace('https://', 'http://')

            response = requests.get(self.proxy_url, timeout=10)

            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')

                if 'json' in content_type:
                    # JSON格式响应
                    data = response.json()

                    if isinstance(data, list) and len(data) > 0:
                        proxy_data = data[0]
                        proxy_str = f"http://{proxy_data.get('ip')}:{proxy_data.get('port')}"

                        # 如果有用户名和密码，添加认证信息
                        if proxy_data.get('user') and proxy_data.get('pass'):
                            proxy_str = f"http://{proxy_data.get('user')}:{proxy_data.get('pass')}@{proxy_data.get('ip')}:{proxy_data.get('port')}"

                        return self.format_proxy(proxy_str)
                else:
                    # 文本格式响应
                    lines = response.text.strip().split('\n')
                    if lines and len(lines) > 0:
                        proxy_line = lines[0].strip()

                        # 检查是否已经是完整的代理URL
                        if not (proxy_line.startswith('http://') or proxy_line.startswith('https://')):
                            proxy_line = f"http://{proxy_line}"

                        return self.format_proxy(proxy_line)

            return None
        except Exception as e:
            logger.error(f"从品赞API获取代理异常: {e}")
            return None

    def test_proxy(self):
        """测试代理连接"""
        if not self.proxy_dict:
            self.proxy_dict = self.get_proxy()

        if not self.proxy_dict:
            return False

        try:
            response = requests.get('http://httpbin.org/ip', proxies=self.proxy_dict, timeout=10)

            if response.status_code == 200:
                self.update_stats(success=True)
                return True
            else:
                self.update_stats(success=False)
                return False
        except Exception as e:
            logger.error(f"测试代理连接异常: {e}")
            self.update_stats(success=False)
            return False
```

## 使用示例

### 1. 基本使用

```python
from backend.core.proxy.proxy_factory import get_proxy_instance

# 创建品赞代理实例
proxy = get_proxy_instance('pinzan')

# 获取代理
proxy_dict = proxy.get_proxy()

# 测试代理
if proxy.test_proxy():
    print("代理可用")
else:
    print("代理不可用")
```

### 2. 与LLM结合使用

```python
from backend.core.proxy.proxy_factory import get_proxy_instance
from backend.core.llm_generator import LLMGenerator

# 创建品赞代理实例
proxy = get_proxy_instance('pinzan')

# 获取代理
proxy_dict = proxy.get_proxy()

if proxy_dict:
    # 创建LLM生成器，使用代理
    llm_gen = LLMGenerator(
        provider='aliyun',
        api_key=os.environ.get('ALIYUN_API_KEY'),
        proxy=proxy_dict['http']  # 使用http代理
    )

    # 测试LLM生成
    response = llm_gen.generate_text("Hello")
    print(response)
```

## 网站分类与代理适用性

为了解决品赞代理只能访问国内网站的限制，我们添加了网站分类和代理适用性检查功能。

### 1. 国内网站判断

```python
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

    # 解析URL获取域名
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()

    # 如果没有域名，返回False
    if not domain:
        return False

    # 检查域名后缀
    china_tlds = ['.cn', '.com.cn', '.net.cn', '.org.cn', '.gov.cn', '.edu.cn']
    for tld in china_tlds:
        if domain.endswith(tld):
            return True

    # 常见国内网站域名
    china_domains = [
        'baidu.com', 'qq.com', '163.com', 'sina.com.cn', 'sohu.com',
        'taobao.com', 'jd.com', 'weibo.com', 'aliyun.com', 'tencent.com',
        'bilibili.com', 'zhihu.com', 'douban.com', 'iqiyi.com', 'youku.com',
        'csdn.net', 'cnblogs.com', '126.com', 'ctrip.com', 'meituan.com',
        'wjx.cn', 'wjx.top'  # 问卷星域名
    ]

    for china_domain in china_domains:
        if domain == china_domain or domain.endswith('.' + china_domain):
            return True

    return False
```

### 2. 代理适用性检查

```python
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
```

### 3. LLM提供商分类

对于LLM提供商，我们根据其地域特性决定是否使用品赞代理：

```python
# 检查是否为国内LLM提供商
 is_china_llm = llm_type in ['aliyun', 'baidu', 'zhipu']
 if not is_china_llm:
     logger.warning(f"品赞代理不适合访问国外LLM提供商({llm_type})，将使用直接连接")
     # 如果不是国内LLM，不使用品赞代理
     proxy_url = None
```

## 优化建议

### 1. 代理池实现

为了提高代理的可用性和性能，可以实现代理池：

```python
class ProxyPool:
    """代理池类"""

    def __init__(self, proxy_type='pinzan', pool_size=5):
        """初始化代理池"""
        self.proxy_type = proxy_type
        self.pool_size = pool_size
        self.proxies = []
        self.init_pool()

    def init_pool(self):
        """初始化代理池"""
        for _ in range(self.pool_size):
            proxy = get_proxy_instance(self.proxy_type)
            if proxy.get_proxy() and proxy.test_proxy():
                self.proxies.append(proxy)

    def get_proxy(self):
        """获取代理"""
        if not self.proxies:
            return None

        # 使用轮询策略
        proxy = self.proxies.pop(0)
        self.proxies.append(proxy)

        return proxy.proxy_dict
```

### 2. 错误重试机制

添加错误重试机制，提高代理获取的成功率：

```python
def get_and_test_proxy(proxy_url, max_retries=3, num_proxies=3):
    """
    获取并测试代理，带重试机制

    Args:
        proxy_url: 代理API URL
        max_retries: 最大重试次数
        num_proxies: 尝试的代理数量

    Returns:
        可用的代理字典
    """
    for _ in range(max_retries):
        for _ in range(num_proxies):
            proxy = get_proxy_instance('pinzan', proxy_url)
            proxy_dict = proxy.get_proxy()

            if proxy_dict and proxy.test_proxy():
                return proxy_dict

        # 等待一段时间再重试
        time.sleep(2)

    return None
```

## 相关文档

- [测试指南](../testing_guide.md)
- [代理测试文档](../testing/proxy_testing.md)
- [品赞代理配置文档](pinzan_proxy_config.md)
- [使用示例文档](../examples/usage_examples.md)
