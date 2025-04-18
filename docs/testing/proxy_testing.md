# 代理测试指南

本文档提供了代理功能测试的详细指南，包括不同类型代理的配置、测试方法和常见问题解决方案。

> **重要提示：品赞IP代理全部是国内IP，只能用于访问国内网站，不适合访问国外网站。系统已经自动判断网站类型，只对国内网站使用品赞代理。**

## 代理类型

系统支持多种类型的代理：

### 1. HTTP代理

HTTP代理是最基本的代理类型，适用于大多数HTTP请求：

```python
proxy = "http://username:password@host:port"
```

### 2. HTTPS代理

HTTPS代理用于加密的HTTPS请求：

```python
proxy = "https://username:password@host:port"
```

### 3. SOCKS5代理

SOCKS5代理提供更高级的功能，支持TCP和UDP：

```python
proxy = "socks5://username:password@host:port"
```

## 代理提供商

### 品赞代理

品赞代理是系统默认支持的代理提供商：

- **环境变量**: `PINZAN_API_URL`
- **API格式**:
  - TXT格式: `http://service.ipzan.com/core-extract?num=1&no=xxxxx&minute=1&format=txt&repeat=1&protocol=1&pool=ordinary`
  - JSON格式: `http://service.ipzan.com/core-extract?num=1&no=xxxxx&minute=1&format=json&repeat=1&protocol=1&pool=ordinary&mode=auth&secret=xxxxx`

## 测试方法

### 1. 基本连接测试

测试代理连接是否正常：

```python
import requests

def test_proxy(proxy_url):
    try:
        # 获取当前IP（不使用代理）
        response = requests.get('http://httpbin.org/ip', timeout=10)
        original_ip = response.json().get('origin')
        print(f"当前IP: {original_ip}")

        # 使用代理获取IP
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=10)
        proxy_ip = response.json().get('origin')
        print(f"代理IP: {proxy_ip}")

        # 检查IP是否变化
        if proxy_ip != original_ip:
            print("代理测试成功!")
            return True
        else:
            print("代理测试失败，IP未变化")
            return False
    except Exception as e:
        print(f"代理测试异常: {e}")
        return False
```

### 2. 品赞代理测试

测试从品赞API获取代理并使用：

```python
import requests

def get_proxy_from_pinzan(proxy_url):
    try:
        # 确保使用HTTP协议
        if proxy_url.startswith('https://'):
            proxy_url = proxy_url.replace('https://', 'http://')

        response = requests.get(proxy_url, timeout=10)

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

                    return proxy_str
            else:
                # 文本格式响应
                lines = response.text.strip().split('\n')
                if lines and len(lines) > 0:
                    proxy_line = lines[0].strip()

                    # 检查是否已经是完整的代理URL
                    if proxy_line.startswith('http://') or proxy_line.startswith('https://'):
                        return proxy_line

                    # 否则假设是IP:端口格式
                    return f"http://{proxy_line}"

        return None
    except Exception as e:
        print(f"从品赞API获取代理异常: {e}")
        return None
```

### 3. 网站分类测试

测试系统对国内外网站的判断功能：

```python
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
        'http://www.edu.cn',
        'http://www.wjx.cn'
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

    print("测试国内网站判断:")
    for url in china_websites:
        result = is_china_website(url)
        should_use = should_use_pinzan_proxy(url)
        print(f"{url} -> 国内网站: {result}, 应使用品赞代理: {should_use}")

    print("测试国外网站判断:")
    for url in foreign_websites:
        result = is_china_website(url)
        should_use = should_use_pinzan_proxy(url)
        print(f"{url} -> 国内网站: {result}, 应使用品赞代理: {should_use}")

    print("测试本地网站判断:")
    for url in local_websites:
        result = is_china_website(url)
        should_use = should_use_pinzan_proxy(url)
        print(f"{url} -> 国内网站: {result}, 应使用品赞代理: {should_use}")
```

### 4. 代理适用性测试

测试系统对不同类型网站的代理选择功能：

```python
def test_proxy_selection():
    """测试代理选择功能"""
    # 测试国内网站
    china_url = 'http://www.baidu.com'
    # 测试国外网站
    foreign_url = 'http://www.google.com'

    # 品赞代理URL
    pinzan_proxy_url = os.environ.get('PINZAN_API_URL')

    # 测试国内网站使用品赞代理
    if should_use_pinzan_proxy(china_url):
        proxy = get_proxy_from_api(pinzan_proxy_url)
        if proxy:
            print(f"成功为国内网站 {china_url} 获取品赞代理: {proxy}")
            # 测试代理连接
            if test_proxy(proxy, timeout=5):
                print(f"使用品赞代理访问国内网站 {china_url} 成功")
            else:
                print(f"使用品赞代理访问国内网站 {china_url} 失败")
        else:
            print(f"无法为国内网站 {china_url} 获取品赞代理")
    else:
        print(f"国内网站 {china_url} 判断失败，应该返回True")

    # 测试国外网站不使用品赞代理
    if not should_use_pinzan_proxy(foreign_url):
        print(f"正确判断国外网站 {foreign_url} 不应使用品赞代理")
        # 使用直接连接
        try:
            response = requests.get(foreign_url, timeout=10)
            print(f"直接连接访问国外网站 {foreign_url} 成功，状态码: {response.status_code}")
        except Exception as e:
            print(f"直接连接访问国外网站 {foreign_url} 失败: {e}")
    else:
        print(f"国外网站 {foreign_url} 判断失败，应该返回False")
```

### 5. 参数化测试

系统提供了参数化测试脚本，支持通过命令行参数配置测试选项：

```bash
python examples/parameterized_test.py --test-type proxy
```

## HTTP代理问题

HTTP代理是最常用的代理类型，但也有一些常见问题：

### 1. 认证问题

**问题**: 代理需要认证但未提供认证信息
**解决方案**:
- 确保代理URL包含用户名和密码
- 检查认证信息是否正确

### 2. 连接超时

**问题**: 连接代理服务器超时
**解决方案**:
- 检查代理服务器是否可用
- 增加超时时间
- 尝试其他代理服务器

## HTTPS代理问题

HTTPS代理用于加密连接，可能会有一些特殊问题：

### 1. SSL证书问题

**问题**: SSL证书验证失败
**解决方案**:
- 使用`verify=False`参数（不推荐用于生产环境）
- 配置正确的证书
- 使用HTTP代理替代

### 2. 协议转换问题

**问题**: 代理服务器不支持HTTPS
**解决方案**:
- 将HTTPS代理URL改为HTTP
- 使用支持HTTPS的代理服务器

## SOCKS5代理问题

SOCKS5代理提供更高级的功能，但也有一些特殊问题：

### 1. 依赖问题

**问题**: 缺少SOCKS5支持
**解决方案**:
- 安装`requests[socks]`或`PySocks`
- 确保正确导入SOCKS5支持模块

### 2. 协议兼容性

**问题**: 某些请求与SOCKS5不兼容
**解决方案**:
- 尝试使用HTTP/HTTPS代理
- 检查SOCKS5代理配置

## 常见问题

### 1. 代理可用性问题

**问题**: 代理服务器不可用或已过期
**解决方案**:
- 定期刷新代理
- 实现代理轮换机制
- 添加代理可用性检查

### 2. IP限制问题

**问题**: 目标网站限制代理IP访问
**解决方案**:
- 使用高质量代理
- 降低请求频率
- 实现IP轮换策略

### 3. 性能问题

**问题**: 使用代理导致请求变慢
**解决方案**:
- 选择低延迟代理
- 实现代理性能监控
- 对性能要求不高的请求才使用代理

### 4. 品赞代理限制问题

**问题**: 品赞代理只能访问国内网站
**解决方案**:
- 使用`is_china_website`函数判断网站类型
- 使用`should_use_pinzan_proxy`函数决定是否使用品赞代理
- 对国外网站使用直接连接或其他代理
- 对国内LLM提供商（阿里云、百度、智谱）使用品赞代理
- 对国外LLM提供商（如OpenAI）使用直接连接或其他代理

## 相关文档

- [测试指南](../testing_guide.md)
- [LLM测试文档](llm_testing.md)
- [品赞代理配置文档](../proxy/pinzan_proxy_config.md)
- [代理优化文档](../proxy/proxy_optimization.md)
- [使用示例文档](../examples/usage_examples.md)
