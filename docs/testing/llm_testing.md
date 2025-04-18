# LLM测试指南

本文档提供了LLM（大语言模型）测试的详细指南，包括不同提供商的配置、测试类型和常见问题解决方案。

## LLM提供商配置

系统支持多种LLM提供商，每种提供商都需要特定的配置：

### 1. OpenAI

- **环境变量**: `OPENAI_API_KEY`
- **支持模型**: gpt-3.5-turbo, gpt-4等
- **配置示例**:
  ```python
  config = {
      'provider': 'openai',
      'api_key': os.environ.get('OPENAI_API_KEY'),
      'model': 'gpt-3.5-turbo'  # 可选，默认为gpt-3.5-turbo
  }
  ```

### 2. 阿里云

- **环境变量**: `ALIYUN_API_KEY`
- **支持模型**: qwen-turbo, qwen-plus等
- **配置示例**:
  ```python
  config = {
      'provider': 'aliyun',
      'api_key': os.environ.get('ALIYUN_API_KEY'),
      'model': 'qwen-turbo'  # 可选，默认为qwen-turbo
  }
  ```

### 3. 智谱AI

- **环境变量**: `ZHIPU_API_KEY`
- **支持模型**: chatglm_turbo, chatglm_pro等
- **配置示例**:
  ```python
  config = {
      'provider': 'zhipu',
      'api_key': os.environ.get('ZHIPU_API_KEY'),
      'model': 'chatglm_turbo'  # 可选，默认为chatglm_turbo
  }
  ```

### 4. Google Gemini

- **环境变量**: `GEMINI_API_KEY`
- **支持模型**: gemini-pro等
- **配置示例**:
  ```python
  config = {
      'provider': 'gemini',
      'api_key': os.environ.get('GEMINI_API_KEY'),
      'model': 'gemini-pro'  # 可选，默认为gemini-pro
  }
  ```

### 5. 兔子API

- **环境变量**: `TUZI_API_KEY`
- **配置示例**:
  ```python
  config = {
      'provider': 'tuzi',
      'api_key': os.environ.get('TUZI_API_KEY')
  }
  ```

## 测试类型

系统支持多种测试类型，可以根据需要选择：

### 1. 基本连接测试

测试与LLM提供商的API连接是否正常：

```python
from backend.core.llm_generator import LLMGenerator

# 创建LLM生成器
llm_gen = LLMGenerator(provider='aliyun', api_key='your_api_key')

# 测试连接
response = llm_gen.generate_text("Hello")
print(response)
```

### 2. 问卷答案生成测试

测试LLM是否能正确生成问卷答案：

```python
from backend.core.llm_generator import LLMGenerator

# 创建LLM生成器
llm_gen = LLMGenerator(provider='aliyun', api_key='your_api_key')

# 准备问卷数据
survey = {
    'title': '测试问卷',
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
            'title': '请简述您的工作经历'
        }
    ]
}

# 生成答案
answers = llm_gen.generate_answers(survey)
print(answers)
```

### 3. 代理兼容性测试

测试LLM是否能与代理正常配合使用：

```python
from backend.core.llm_generator import LLMGenerator

# 创建带代理的LLM生成器
llm_gen = LLMGenerator(
    provider='aliyun',
    api_key='your_api_key',
    proxy='http://your_proxy_url'
)

# 测试生成
response = llm_gen.generate_text("Hello")
print(response)
```

## 参数化测试

系统提供了参数化测试脚本，支持通过命令行参数配置测试选项：

```bash
python examples/parameterized_test.py --test-type [llm|proxy|combined] --provider [openai|zhipu|aliyun|gemini|tuzi] --use-proxy [true|false]
```

### 参数说明

- `--test-type`: 测试类型
  - `llm`: 仅测试LLM功能
  - `proxy`: 仅测试代理功能
  - `combined`: 测试LLM和代理的组合使用（默认）

- `--provider`: LLM提供商
  - `openai`: OpenAI
  - `zhipu`: 智谱AI
  - `aliyun`: 阿里云（默认）
  - `gemini`: Google Gemini
  - `tuzi`: 兔子API

- `--model`: LLM模型名称（可选）
  - 例如：`gpt-3.5-turbo`、`qwen-turbo`等

- `--use-proxy`: 是否使用代理（仅对llm测试类型有效）
  - `true`: 使用代理
  - `false`: 不使用代理（默认）

## 常见问题

### 1. API密钥问题

**问题**: API密钥无效或过期
**解决方案**:
- 检查环境变量是否正确设置
- 确认API密钥是否有效
- 检查API密钥是否有足够的配额

### 2. 网络连接问题

**问题**: 无法连接到LLM提供商的API
**解决方案**:
- 检查网络连接
- 尝试使用代理
- 确认API服务是否可用

### 3. 响应格式问题

**问题**: LLM返回的响应格式不正确
**解决方案**:
- 检查提示词是否正确
- 调整模型参数
- 尝试不同的模型

### 4. 代理兼容性问题

**问题**: LLM无法与代理正常配合使用
**解决方案**:
- 确认代理格式是否正确
- 检查代理是否可用
- 尝试不同的代理提供商

## 相关文档

- [测试指南](../testing_guide.md)
- [代理测试文档](proxy_testing.md)
- [品赞代理配置文档](../proxy/pinzan_proxy_config.md)
- [使用示例文档](../examples/usage_examples.md)
