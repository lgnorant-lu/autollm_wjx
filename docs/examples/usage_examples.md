# 使用示例文档

本文档提供了系统各个功能的使用示例，包括LLM API和IP代理的使用方法。

## LLM API使用示例

### 1. 基本使用

```python
from backend.core.llm_generator import LLMGenerator

# 创建LLM生成器
llm_gen = LLMGenerator(
    provider='aliyun',  # 提供商，支持'openai'、'zhipu'、'aliyun'、'gemini'、'tuzi'等
    api_key='your_api_key',  # API密钥
    model='qwen-turbo'  # 模型名称（可选）
)

# 生成文本
response = llm_gen.generate_text("你好，请介绍一下自己")
print(response)
```

### 2. 使用环境变量

```python
import os
from dotenv import load_dotenv
from backend.core.llm_generator import LLMGenerator

# 加载环境变量
load_dotenv()

# 创建LLM生成器
llm_gen = LLMGenerator(
    provider='openai',
    api_key=os.environ.get('OPENAI_API_KEY')
)

# 生成文本
response = llm_gen.generate_text("你好，请介绍一下自己")
print(response)
```

### 3. 生成问卷答案

```python
from backend.core.llm_generator import LLMGenerator

# 创建LLM生成器
llm_gen = LLMGenerator(provider='aliyun', api_key='your_api_key')

# 准备问卷数据
survey = {
    'title': '用户满意度调查',
    'questions': [
        {
            'index': 1,
            'type': 3,  # 单选题
            'title': '您的性别是？',
            'options': ['男', '女']
        },
        {
            'index': 2,
            'type': 1,  # 填空题
            'title': '您对我们的产品有什么建议？'
        },
        {
            'index': 3,
            'type': 4,  # 多选题
            'title': '您使用过哪些功能？',
            'options': ['功能A', '功能B', '功能C', '功能D']
        }
    ]
}

# 生成答案
answers = llm_gen.generate_answers(survey)
print(answers)
```

### 4. 使用不同的LLM提供商

#### OpenAI

```python
llm_gen = LLMGenerator(
    provider='openai',
    api_key=os.environ.get('OPENAI_API_KEY'),
    model='gpt-3.5-turbo'
)
```

#### 智谱AI

```python
llm_gen = LLMGenerator(
    provider='zhipu',
    api_key=os.environ.get('ZHIPU_API_KEY'),
    model='chatglm_turbo'
)
```

#### 阿里云

```python
llm_gen = LLMGenerator(
    provider='aliyun',
    api_key=os.environ.get('ALIYUN_API_KEY'),
    model='qwen-turbo'
)
```

#### Google Gemini

```python
llm_gen = LLMGenerator(
    provider='gemini',
    api_key=os.environ.get('GEMINI_API_KEY'),
    model='gemini-pro'
)
```

#### 兔子API

```python
llm_gen = LLMGenerator(
    provider='tuzi',
    api_key=os.environ.get('TUZI_API_KEY')
)
```

## IP代理使用示例

### 1. 基本使用

```python
import requests

def get_proxy_from_pinzan(proxy_url):
    """从品赞API获取代理"""
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

# 使用代理
proxy_url = "http://service.ipzan.com/core-extract?num=1&no=YOUR_NO&minute=1&format=json&repeat=1&protocol=1&pool=ordinary&mode=auth&secret=YOUR_SECRET"
proxy = get_proxy_from_pinzan(proxy_url)

if proxy:
    proxies = {
        'http': proxy,
        'https': proxy
    }
    
    # 使用代理发送请求
    response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=10)
    print(f"当前IP: {response.json().get('origin')}")
```

### 2. 使用代理工厂

```python
from backend.core.proxy.proxy_factory import get_proxy_instance

# 创建品赞代理实例
proxy = get_proxy_instance('pinzan')

# 获取代理
proxy_dict = proxy.get_proxy()

if proxy_dict:
    # 使用代理发送请求
    response = requests.get('http://httpbin.org/ip', proxies=proxy_dict, timeout=10)
    print(f"当前IP: {response.json().get('origin')}")
```

### 3. 与LLM结合使用

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
    response = llm_gen.generate_text("你好，请介绍一下自己")
    print(response)
```

### 4. 代理轮换

```python
from backend.core.proxy.proxy_factory import get_proxy_instance
import time

def get_rotating_proxy(max_retries=3):
    """获取轮换代理"""
    for _ in range(max_retries):
        proxy = get_proxy_instance('pinzan')
        proxy_dict = proxy.get_proxy()
        
        if proxy_dict and proxy.test_proxy():
            return proxy_dict
        
        # 等待一段时间再重试
        time.sleep(2)
    
    return None

# 使用轮换代理
proxy_dict = get_rotating_proxy()

if proxy_dict:
    # 使用代理发送请求
    response = requests.get('http://httpbin.org/ip', proxies=proxy_dict, timeout=10)
    print(f"当前IP: {response.json().get('origin')}")
```

## 参数化测试示例

### 1. 测试LLM功能

```bash
python examples/parameterized_test.py --test-type llm --provider aliyun --use-proxy false
```

### 2. 测试代理功能

```bash
python examples/parameterized_test.py --test-type proxy
```

### 3. 测试LLM与代理的组合使用

```bash
python examples/parameterized_test.py --test-type combined --provider openai
```

### 4. 测试特定模型

```bash
python examples/parameterized_test.py --test-type llm --provider gemini --model gemini-pro
```

## 相关文档

- [测试指南](../testing_guide.md)
- [LLM测试文档](../testing/llm_testing.md)
- [代理测试文档](../testing/proxy_testing.md)
- [品赞代理配置文档](../proxy/pinzan_proxy_config.md)
- [代理优化文档](../proxy/proxy_optimization.md)
