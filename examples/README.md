# 测试脚本

本目录包含各种测试脚本，用于测试系统的不同功能，包括LLM接口、代理功能以及它们的组合使用。

## 参数化测试脚本

`parameterized_test.py` 是一个统一的参数化测试脚本，整合了多个测试功能，支持通过命令行参数配置测试选项。

### 功能特点

- 支持测试不同的LLM提供商（OpenAI, Zhipu, Aliyun, Gemini, Tuzi等）
- 支持测试代理功能（品赞代理）
- 支持测试LLM与代理的组合使用
- 支持命令行参数配置测试选项

### 使用方法

```bash
python parameterized_test.py --test-type [llm|proxy|combined] --provider [openai|zhipu|aliyun|gemini|tuzi] --use-proxy [true|false]
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

### 示例

1. 测试阿里云LLM（不使用代理）：

```bash
python parameterized_test.py --test-type llm --provider aliyun --use-proxy false
```

2. 测试OpenAI与代理的组合使用：

```bash
python parameterized_test.py --test-type combined --provider openai
```

3. 仅测试代理功能：

```bash
python parameterized_test.py --test-type proxy
```

4. 测试特定模型：

```bash
python parameterized_test.py --test-type llm --provider gemini --model gemini-pro
```

## 集成测试脚本

`integrated_test.py` 是一个集成测试脚本，可以测试品赞代理和阿里云LLM功能。

### 使用方法

```bash
# 测试品赞代理
python examples\integrated_test.py --test-type proxy

# 测试阿里云LLM
python examples\integrated_test.py --test-type llm

# 测试所有功能
python examples\integrated_test.py --test-type all

# 使用详细模式
python examples\integrated_test.py --verbose

# 使用指定的环境变量文件
python examples\integrated_test.py --env-file .env.test
```

### 参数说明

- `--test-type`, `-t`: 测试类型，可选值为 `proxy`, `llm`, `all`，默认为 `all`
- `--env-file`, `-e`: 环境变量文件路径，默认为 `.env.real`
- `--verbose`, `-v`: 详细模式，输出更多日志信息

## 其他测试脚本

- `proxy_test.py`: 品赞代理测试脚本，支持更多参数和测试类型
- `llm_test.py`: LLM测试脚本，支持测试不同的LLM提供商
- `llm_aliyun_test.py`: 阿里云LLM测试脚本
- `llm_gemini_test.py`: Google Gemini LLM测试脚本
- `llm_openai_test.py`: OpenAI LLM测试脚本
- `llm_zhipu_test.py`: 智谱LLM测试脚本
- `llm_simple_test.py`: 简单的LLM测试脚本
- `llm_with_proxy_example.py`: 使用代理的LLM示例脚本

## 注意事项

1. 测试品赞代理前，请确保已将当前IP添加到品赞IP的白名单中
2. 测试LLM功能前，请确保已设置相应的API密钥
3. 环境变量文件应包含以下变量：
   - `PINZAN_API_URL`: 品赞API URL
   - `ALIYUN_API_KEY`: 阿里云API密钥
   - `OPENAI_API_KEY`: OpenAI API密钥
   - `ZHIPU_API_KEY`: 智谱AI API密钥
   - `GEMINI_API_KEY`: Google Gemini API密钥
   - `TUZI_API_KEY`: 兔子API密钥
