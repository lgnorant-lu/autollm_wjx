# 测试指南

本文档提供了系统测试的详细指南，包括LLM接口测试、代理功能测试以及它们的组合测试。

## 测试脚本概述

系统提供了多种测试脚本，位于`examples`目录下，用于测试不同的功能：

- `parameterized_test.py`: 统一的参数化测试脚本，支持通过命令行参数配置测试选项
- `integrated_test.py`: 集成测试脚本，测试品赞代理和阿里云LLM
- `proxy_test.py`: 代理测试脚本，测试品赞代理功能
- `llm_test.py`: LLM测试脚本，支持测试不同的LLM提供商
- 各种特定LLM提供商的测试脚本（`llm_aliyun_test.py`, `llm_gemini_test.py`等）

## 参数化测试脚本

`parameterized_test.py`是一个统一的参数化测试脚本，整合了多个测试功能，支持通过命令行参数配置测试选项。

### 功能特点

- 支持测试不同的LLM提供商（OpenAI, Zhipu, Aliyun, Gemini, Tuzi等）
- 支持测试代理功能（品赞代理）
- 支持测试LLM与代理的组合使用
- 支持命令行参数配置测试选项

### 使用方法

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

### 示例

1. 测试阿里云LLM（不使用代理）：

```bash
python examples/parameterized_test.py --test-type llm --provider aliyun --use-proxy false
```

2. 测试OpenAI与代理的组合使用：

```bash
python examples/parameterized_test.py --test-type combined --provider openai
```

3. 仅测试代理功能：

```bash
python examples/parameterized_test.py --test-type proxy
```

4. 测试特定模型：

```bash
python examples/parameterized_test.py --test-type llm --provider gemini --model gemini-pro
```

## LLM测试

### 支持的LLM提供商

系统支持以下LLM提供商：

1. **OpenAI**
   - 模型：gpt-3.5-turbo, gpt-4等
   - 环境变量：`OPENAI_API_KEY`

2. **阿里云**
   - 模型：qwen-turbo, qwen-plus等
   - 环境变量：`ALIYUN_API_KEY`

3. **智谱AI**
   - 模型：chatglm_turbo, chatglm_pro等
   - 环境变量：`ZHIPU_API_KEY`

4. **Google Gemini**
   - 模型：gemini-pro等
   - 环境变量：`GEMINI_API_KEY`

5. **兔子API**
   - 环境变量：`TUZI_API_KEY`

### 测试内容

LLM测试主要包括以下内容：

1. **连接测试**：测试与LLM提供商的API连接是否正常
2. **生成测试**：测试LLM是否能正常生成文本
3. **代理兼容性测试**：测试LLM是否能与代理正常配合使用

## 代理测试

### 支持的代理提供商

系统目前支持品赞代理：

- 环境变量：`PINZAN_API_URL`

### 测试内容

代理测试主要包括以下内容：

1. **连接测试**：测试是否能正常获取代理
2. **IP变化测试**：测试使用代理后IP是否发生变化
3. **稳定性测试**：测试代理的稳定性和可靠性

## 组合测试

组合测试主要测试LLM与代理的组合使用，包括：

1. **不使用代理的LLM测试**：测试LLM在不使用代理的情况下是否正常工作
2. **使用代理的LLM测试**：测试LLM在使用代理的情况下是否正常工作
3. **对比测试**：对比使用代理和不使用代理的LLM性能差异

## 环境变量配置

测试脚本依赖于以下环境变量：

- `ALIYUN_API_KEY`: 阿里云API密钥
- `OPENAI_API_KEY`: OpenAI API密钥
- `ZHIPU_API_KEY`: 智谱AI API密钥
- `GEMINI_API_KEY`: Google Gemini API密钥
- `TUZI_API_KEY`: 兔子API密钥
- `PINZAN_API_URL`: 品赞代理API URL

这些环境变量可以在项目根目录的`.env.real`文件中设置。

## 注意事项

1. 测试品赞代理前，请确保已将当前IP添加到品赞IP的白名单中
2. 测试LLM功能前，请确保已设置相应的API密钥
3. 如果测试失败，请检查网络连接、API密钥和代理配置
4. 对于需要付费的API，请注意控制测试频率，避免不必要的费用

## 故障排除

如果测试失败，可以尝试以下方法：

1. 检查环境变量是否正确设置
2. 检查网络连接是否正常
3. 检查API密钥是否有效
4. 检查代理配置是否正确
5. 查看日志输出，了解详细错误信息

## 相关文档

- [LLM测试文档](testing/llm_testing.md)
- [代理测试文档](testing/proxy_testing.md)
- [品赞代理配置文档](proxy/pinzan_proxy_config.md)
- [代理优化文档](proxy/proxy_optimization.md)
- [使用示例文档](examples/usage_examples.md)
