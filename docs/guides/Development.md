# 开发指南

[返回主页](../../README.md) | [快速入门](../../QUICK_START.md) | [部署指南](Deployment.md) | [测试指南](Testing.md)

本文档提供问卷星自动化系统的开发指南，帮助开发者理解项目结构和开发流程。

## 目录

- [1. 开发环境设置](#1-开发环境设置)
- [2. 项目结构](#2-项目结构)
- [3. 后端开发](#3-后端开发)
- [4. 前端开发](#4-前端开发)
- [5. API文档](#5-api文档)
- [6. 测试](#6-测试)

## 1. 开发环境设置

### 1.1 必要条件

- Python 3.9+
- Node.js 16+
- npm 7+
- Git
- 推荐使用VSCode作为IDE

### 1.2 环境设置步骤

1. **克隆仓库**

```bash
git clone https://github.com/yourusername/autollm_wjx.git
cd autollm_wjx
```

2. **设置后端开发环境**

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -r requirements-dev.txt
```

3. **设置前端开发环境**

```bash
cd frontend
npm install
```

### 1.3 环境变量配置

创建`.env`文件在项目根目录：

```
# 开发环境配置
FLASK_ENV=development
FLASK_APP=backend/app.py
FLASK_DEBUG=1

# LLM API配置
LLM_PROVIDER=openai
LLM_API_KEY=your_api_key_here
LLM_MODEL=gpt-3.5-turbo

# 其他配置
LOG_LEVEL=DEBUG
```

## 2. 项目结构

参考[项目结构文档](../project/Structure.md)了解详细的项目结构。

## 3. 开发工作流程

### 3.1 分支管理

遵循GitFlow工作流：

- `main`: 稳定版本分支
- `develop`: 开发分支
- `feature/*`: 功能分支
- `bugfix/*`: 错误修复分支
- `release/*`: 发布准备分支

### 3.2 功能开发流程

1. 从`develop`分支创建功能分支
   ```bash
   git checkout develop
   git pull
   git checkout -b feature/your-feature-name
   ```

2. 在功能分支上进行开发

3. 提交更改
   ```bash
   git add .
   git commit -m "[模块名] 动作: 详细描述"
   ```

4. 推送到远程仓库
   ```bash
   git push origin feature/your-feature-name
   ```

5. 创建Pull Request到`develop`分支

6. 代码审查通过后合并

### 3.3 本地开发运行

1. **运行后端服务**

```bash
# 在项目根目录
source venv/bin/activate  # 或在Windows上: venv\Scripts\activate
cd backend
flask run --host=0.0.0.0 --port=5000
```

2. **运行前端服务**

```bash
cd frontend
npm run dev
```

## 4. 编码规范

### 4.1 Python代码规范

- 遵循PEP 8编码风格
- 使用Google风格文档字符串
- 类名使用PascalCase（如`UserManager`）
- 函数/方法名使用snake_case（如`get_user_info`）
- 常量使用大写下划线（如`MAX_RETRY_COUNT`）
- 每个文件必须包含标准文件头注释

```python
"""
---------------------------------------------------------------
File name:                  example.py
Author:                     lgnorant-lu
Date created:               YYYY/MM/DD
Description:                简要描述文件功能
----------------------------------------------------------------

Changed history:
                            YYYY/MM/DD: 初始创建;
                            YYYY/MM/DD: 功能修改说明;
----
"""
```

### 4.2 JavaScript/Vue代码规范

- 遵循Airbnb JavaScript风格指南
- Vue组件使用PascalCase命名（如`TaskList.vue`）
- 使用ES6+语法
- 组件属性顺序：props, data, computed, watch, lifecycle methods, methods
- 使用ESLint和Prettier保持代码风格一致

### 4.3 提交信息规范

提交信息格式：`[模块名] 动作: 详细描述`

例如：
- `[parser] 修复: 解决矩阵题型解析问题`
- `[frontend] 新增: 任务详情页面`
- `[api] 优化: 提高并发请求处理性能`

## 5. 测试

### 5.1 单元测试

- 使用pytest进行Python代码测试
- 使用Jest进行JavaScript代码测试
- 测试文件命名为`test_<module_name>.py`或`<module_name>.test.js`

运行后端测试：
```bash
cd backend
pytest
```

运行前端测试：
```bash
cd frontend
npm test
```

### 5.2 集成测试

- API测试使用pytest和requests
- 前端组件测试使用Vue Test Utils

### 5.3 代码覆盖率

- 后端目标覆盖率：80%
- 前端目标覆盖率：70%

## 6. 调试技巧

### 6.1 后端调试

- 使用Flask Debug模式
- 使用`logging`模块记录信息
- VSCode调试配置在`.vscode/launch.json`中

### 6.2 前端调试

- 使用Vue DevTools
- 使用浏览器开发者工具
- 使用ESLint进行代码问题检测

## 7. 性能优化

- 使用缓存机制减少API调用
- 批量处理大量数据
- 优化数据库查询和文件读写操作
- 实现适当的错误处理和重试机制

## 8. 常见问题解决

### 8.1 问卷解析失败

- 检查HTML结构变化
- 查看详细日志
- 尝试更新解析规则

### 8.2 LLM API调用失败

- 验证API密钥
- 检查网络连接
- 查看API限制和使用配额
- 实现备用模型

### 8.3 开发环境问题

- 清理缓存：`npm cache clean --force`
- 重新安装依赖：`pip install -r requirements.txt --force-reinstall`
- 检查版本兼容性

## 9. 贡献指南

1. 先创建Issue讨论你要解决的问题或添加的功能
2. Fork仓库并创建功能分支
3. 开发并编写测试
4. 确保所有测试通过
5. 创建Pull Request
6. 等待代码审查和讨论
7. 合并更改

---

## 相关文档

- [部署指南](Deployment.md) - 如何部署系统
- [测试指南](Testing.md) - 如何进行测试
- [用户指南](User.md) - 系统使用说明
- [架构设计](../design/Architecture.md) - 系统架构设计
- [接口设计](../design/API.md) - API接口设计

[返回顶部](#开发指南) | [返回主页](../../README.md) | [快速入门](../../QUICK_START.md)