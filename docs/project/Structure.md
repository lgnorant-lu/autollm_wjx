# 问卷星自动化系统 - 项目结构

[返回文档索引](../index.md) | [部署指南](../guides/Deployment.md) | [故障排除](../guides/Troubleshooting.md) | [静态前端备用方案](../guides/static-frontend.md)

本文档描述问卷星自动化系统的文件目录结构和各模块组成。

## 项目概述

问卷星自动化系统是一个用于自动化问卷调查流程的应用程序，包含前端和后端两个主要组件。前端使用Vue.js构建，后端使用Flask构建。

## 1. 目录结构概览

```
autollm_wjx/
├── backend/                 # 后端API服务
│   ├── api/                 # API接口定义
│   ├── core/                # 核心功能实现
│   ├── data/                # 数据存储目录
│   ├── tests/               # 测试代码
│   ├── utils/               # 工具函数
│   ├── app.py               # 主应用入口
│   ├── config.py            # 配置文件
│   └── requirements.txt     # 依赖管理
│
├── frontend/                # 前端应用
│   ├── public/              # 静态资源
│   ├── src/                 # 源代码
│   │   ├── api/             # API调用
│   │   ├── assets/          # 静态资源
│   │   ├── components/      # 组件
│   │   ├── router/          # 路由定义
│   │   ├── store/           # 状态管理
│   │   ├── views/           # 视图页面
│   │   ├── App.vue          # 主应用组件
│   │   └── main.js          # 入口文件
│   ├── package.json         # 依赖管理
│   └── nginx/               # Nginx配置
│
├── static_frontend/         # 静态前端备用方案
│   └── index.html           # 静态前端页面
│
├── docs/                    # 文档
│   ├── design/              # 设计文档
│   ├── diagrams/            # 架构和流程图
│   ├── guides/              # 使用指南
│   ├── project/             # 项目文档
│   └── references/          # 参考文档
│
├── deploy.ps1               # 部署脚本
├── docker-compose.yml       # Docker Compose配置
├── Dockerfile.backend       # 后端Docker配置
├── Dockerfile.frontend      # 前端Docker配置
├── static_server.py         # 静态服务器脚本
└── .env.example             # 环境变量示例文件
```

## 2. 后端服务详细结构

### 2.1 API模块 (`backend/api/`)

| 文件/目录 | 状态 | 描述 |
|----------|------|------|
| `__init__.py` | [已完成] | API包初始化 |
| `surveys.py` | [已完成] | 问卷相关API端点 |
| `tasks.py` | [已完成] | 任务相关API端点 |
| `submissions.py` | [已完成] | 提交结果相关API端点 |
| `config.py` | [已完成] | 系统配置相关API端点 |
| `auth.py` | [已完成] | 认证相关API端点 |

API模块负责处理所有HTTP请求，实现RESTful接口，包括请求验证、响应格式化和错误处理。每个文件对应一组相关的API端点。

### 2.2 核心功能模块 (`backend/core/`)

| 文件/目录 | 状态 | 描述 |
|----------|------|------|
| `__init__.py` | [已完成] | 核心包初始化 |
| `parser/` | [已完成] | 问卷解析模块 |
| `├── __init__.py` | [已完成] | 解析器包初始化 |
| `├── wjx_parser.py` | [已完成] | 问卷星HTML解析实现 |
| `├── question_extractor.py` | [已完成] | 问题和选项提取 |
| `├── html_utils.py` | [已完成] | HTML处理工具 |
| `generator/` | [已完成] | 答案生成模块 |
| `├── __init__.py` | [已完成] | 生成器包初始化 |
| `├── answer_generator.py` | [已完成] | 答案生成器基类 |
| `├── random_generator.py` | [已完成] | 随机答案生成器 |
| `├── fixed_generator.py` | [已完成] | 固定答案生成器 |
| `├── ai_generator.py` | [已完成] | AI辅助答案生成器 |
| `submitter/` | [已完成] | 问卷提交模块 |
| `├── __init__.py` | [已完成] | 提交器包初始化 |
| `├── submitter.py` | [已完成] | 提交器基类 |
| `├── wjx_submitter.py` | [已完成] | 问卷星提交实现 |
| `├── proxy_manager.py` | [已完成] | 代理IP管理 |
| `task_manager.py` | [已完成] | 任务管理与执行 |
| `survey_manager.py` | [已完成] | 问卷管理 |
| `data_manager.py` | [已完成] | 数据存储与访问 |

核心模块实现系统的主要业务逻辑，包括问卷解析、答案生成和问卷提交功能。这些模块相互协作，通过接口隔离实现功能解耦。

### 2.3 数据存储目录 (`backend/data/`)

| 目录 | 状态 | 描述 |
|------|------|------|
| `surveys/` | [已完成] | 存储问卷数据文件 |
| `tasks/` | [已完成] | 存储任务数据文件 |
| `submissions/` | [已完成] | 存储提交结果数据 |
| `config/` | [已完成] | 存储系统配置 |

数据以JSON文件形式存储，每种数据类型有独立的子目录，以ID为文件名进行组织。

### 2.4 工具函数 (`backend/utils/`)

| 文件 | 状态 | 描述 |
|------|------|------|
| `__init__.py` | [已完成] | 工具包初始化 |
| `logger.py` | [已完成] | 日志工具 |
| `file_utils.py` | [已完成] | 文件操作工具 |
| `http_utils.py` | [已完成] | HTTP请求工具 |
| `security.py` | [已完成] | 安全相关工具 |
| `validators.py` | [已完成] | 输入验证工具 |
| `export.py` | [已完成] | 数据导出工具 |

工具模块提供各种辅助功能，被其他模块共同使用，实现代码复用和功能集中管理。

## 3. 前端应用详细结构

### 3.1 源代码目录 (`frontend/src/`)

| 目录/文件 | 状态 | 描述 |
|----------|------|------|
| `api/` | [已完成] | API调用接口 |
| `├── index.js` | [已完成] | API客户端配置 |
| `├── surveys.js` | [已完成] | 问卷相关API |
| `├── tasks.js` | [已完成] | 任务相关API |
| `├── submissions.js` | [已完成] | 提交相关API |
| `assets/` | [已完成] | 静态资源 |
| `├── images/` | [已完成] | 图片资源 |
| `├── styles/` | [已完成] | 样式文件 |
| `components/` | [已完成] | 通用组件 |
| `├── common/` | [已完成] | 基础UI组件 |
| `├── survey/` | [已完成] | 问卷相关组件 |
| `├── task/` | [已完成] | 任务相关组件 |
| `router/` | [已完成] | 路由定义 |
| `├── index.js` | [已完成] | 路由配置 |
| `store/` | [已完成] | 状态管理 |
| `├── index.js` | [已完成] | Store配置 |
| `├── modules/` | [已完成] | 模块化状态 |
| `│   ├── surveys.js` | [已完成] | 问卷状态管理 |
| `│   ├── tasks.js` | [已完成] | 任务状态管理 |
| `│   ├── user.js` | [已完成] | 用户状态管理 |
| `views/` | [已完成] | 视图页面 |
| `├── Dashboard.vue` | [已完成] | 仪表盘页面 |
| `├── SurveyList.vue` | [已完成] | 问卷列表页面 |
| `├── SurveyDetail.vue` | [已完成] | 问卷详情页面 |
| `├── TaskList.vue` | [已完成] | 任务列表页面 |
| `├── TaskDetail.vue` | [已完成] | 任务详情页面 |
| `├── TaskCreate.vue` | [已完成] | 任务创建页面 |
| `├── Login.vue` | [已完成] | 登录页面 |
| `├── Settings.vue` | [已完成] | 设置页面 |
| `App.vue` | [已完成] | 主应用组件 |
| `main.js` | [已完成] | 入口文件 |

前端采用组件化开发，清晰划分各功能模块，使用状态管理实现数据共享，API模块统一处理与后端的通信。

## 4. 静态前端备用方案

### 4.1 组件说明

- **技术栈**: HTML, JavaScript
- **主要功能**: 当Docker无法拉取Nginx镜像时的备用方案
- **服务器**: Python HTTP服务器
- **端口**: 80

### 4.2 部署脚本 (deploy.ps1)

PowerShell脚本，用于管理应用的部署、启动和停止。支持以下命令：
- `setup`: 设置环境
- `start`: 启动应用
- `stop`: 停止应用
- `restart`: 重启应用
- `logs`: 查看日志
- `status`: 查看状态
- `prune`: 清理资源
- `static-frontend`: 启动静态前端服务器

## 5. 状态标记

- ✅ 后端API服务 - 正常运行
- ✅ 静态前端备用方案 - 正常运行
- ✅ Docker前端容器 - 正常运行（需要配置镜像加速器）

## 6. 模块依赖关系

```
                +-------------+
                |     API     |
                +------+------+
                       |
                       v
+----------+     +-----+------+     +-----------+
|   Auth   +---->+    Core    +<----+  Config   |
+----------+     +-----+------+     +-----------+
                       |
                       v
+----------+     +-----+------+     +-----------+
|  Parser  +<--->+ Task Manager+<--->+ Submitter |
+----------+     +-----+------+     +-----------+
                       |
                       v
                +------+------+
                | Data Manager |
                +------+------+
                       |
                       v
                +------+------+
                |  File System |
                +-------------+
```

核心模块与数据模块的依赖关系图，显示了系统主要组件间的交互。

---

[返回文档索引](../index.md) | [返回顶部](#问卷星自动化系统---项目结构)
