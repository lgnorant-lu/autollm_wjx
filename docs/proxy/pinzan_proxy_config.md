# 品赞IP代理配置指南

本文档提供了品赞IP代理的详细配置指南，包括API格式、认证方式和使用示例。

> **重要提示：品赞IP代理全部是国内IP，只能用于访问国内网站，不适合访问国外网站（如Google、OpenAI等）。系统已经自动判断网站类型，只对国内网站使用品赞代理。**

## API格式

品赞IP代理提供了两种API格式：

### 1. TXT格式（白名单模式）

TXT格式API不需要账号密码，但需要将您的IP添加到白名单：

```
http://service.ipzan.com/core-extract?num=1&no=YOUR_NO&minute=1&format=txt&repeat=1&protocol=1&pool=ordinary
```

### 2. JSON格式（认证模式）

JSON格式API需要提供认证信息，但不受白名单限制：

```
http://service.ipzan.com/core-extract?num=1&no=YOUR_NO&minute=1&format=json&repeat=1&protocol=1&pool=ordinary&mode=auth&secret=YOUR_SECRET
```

## 参数说明

API URL中的参数说明：

- `num`: 提取数量，建议设置为1
- `no`: 品赞账号编号
- `minute`: 有效时长（分钟）
- `format`: 返回格式，可选txt或json
- `repeat`: 是否允许重复提取，1表示允许
- `protocol`: 代理协议，1表示HTTP，2表示HTTPS，3表示SOCKS5
- `pool`: 代理池类型，ordinary表示普通池
- `mode`: 认证模式，auth表示使用认证
- `secret`: 认证密钥

## 配置方法

### 1. 环境变量配置

在`.env`文件中配置品赞API URL：

```
PINZAN_API_URL=http://service.ipzan.com/core-extract?num=1&no=YOUR_NO&minute=1&format=json&repeat=1&protocol=1&pool=ordinary&mode=auth&secret=YOUR_SECRET
```

### 2. 代码中直接配置

在代码中直接配置品赞API URL：

```python
proxy_url = "http://service.ipzan.com/core-extract?num=1&no=YOUR_NO&minute=1&format=json&repeat=1&protocol=1&pool=ordinary&mode=auth&secret=YOUR_SECRET"
```

## 使用示例

### 1. 获取代理

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

### 2. 使用代理

```python
import requests

def use_proxy(proxy_url):
    try:
        # 获取代理
        proxy = get_proxy_from_pinzan(proxy_url)

        if not proxy:
            print("无法获取代理")
            return False

        # 使用代理
        proxies = {
            'http': proxy,
            'https': proxy
        }

        # 测试代理
        response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=10)

        if response.status_code == 200:
            print(f"使用代理成功，当前IP: {response.json().get('origin')}")
            return True
        else:
            print(f"使用代理失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"使用代理异常: {e}")
        return False
```

## 协议支持

品赞IP代理支持多种协议：

### 1. HTTP代理

HTTP代理是最基本的代理类型，适用于大多数HTTP请求：

```
protocol=1
```

### 2. HTTPS代理

HTTPS代理用于加密的HTTPS请求：

```
protocol=2
```

### 3. SOCKS5代理

SOCKS5代理提供更高级的功能，支持TCP和UDP：

```
protocol=3
```

## 网站分类与代理适用性

系统自动判断网站类型，只对国内网站使用品赞代理。

### 1. 国内网站判断

系统通过以下方式判断网站是否为国内网站：

- 域名后缀：`.cn`、`.com.cn`、`.net.cn`、`.org.cn`、`.gov.cn`、`.edu.cn`等
- 常见国内网站域名：`baidu.com`、`qq.com`、`163.com`、`wjx.cn`等
- 本地地址：`localhost`、`127.0.0.1`等

### 2. 代理适用性检查

系统提供了`should_use_pinzan_proxy`函数，用于判断是否应该使用品赞代理访问给定URL：

```python
# 检查是否应该使用品赞代理
if should_use_pinzan_proxy(url):
    # 使用品赞代理
    proxy = get_proxy_from_api(proxy_url)
else:
    # 使用直接连接或其他代理
    proxy = None
```

### 3. LLM提供商分类

系统会根据LLM提供商的地域特性决定是否使用品赞代理：

- 国内LLM提供商（阿里云、百度、智谱）：使用品赞代理
- 国外LLM提供商（如OpenAI）：不使用品赞代理，而是使用直接连接或其他代理

## 常见问题

### 1. 白名单问题

**问题**: 使用TXT格式API但未将IP添加到白名单
**解决方案**:
- 登录品赞后台添加IP到白名单
- 使用JSON格式API（认证模式）

### 2. 认证问题

**问题**: 使用JSON格式API但认证失败
**解决方案**:
- 检查no和secret是否正确
- 确认账号是否有效

### 3. 代理质量问题

**问题**: 代理质量不稳定
**解决方案**:
- 使用高质量代理池
- 实现代理质量检测
- 添加代理轮换机制

### 4. 国外网站访问问题

**问题**: 使用品赞代理访问国外网站失败
**解决方案**:
- 不要使用品赞代理访问国外网站
- 使用其他支持国外访问的代理服务
- 系统已自动判断网站类型，只对国内网站使用品赞代理

## 相关文档

- [测试指南](../testing_guide.md)
- [代理测试文档](../testing/proxy_testing.md)
- [代理优化文档](proxy_optimization.md)
- [使用示例文档](../examples/usage_examples.md)
