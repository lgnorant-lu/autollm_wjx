# 问卷星自动化系统

一个用于自动创建、提交和管理问卷星调查的系统，支持随机生成答案和使用大语言模型(LLM)生成答案。

## 文档导航

| 文档类别 | 文档链接 | 说明 |
|------------|------------|------|
| **快速入门** | [快速入门指南](QUICK_START.md) | 适合新手用户的快速入门指南 |
| **部署指南** | [部署指南](docs/guides/Deployment.md) | 包含一键式部署、Docker部署和本地直接运行等多种方式 |
| **开发指南** | [开发指南](docs/guides/Development.md) | 适合开发者的二次开发指南 |
| **测试指南** | [测试指南](docs/guides/Testing.md) | 说明如何进行单元测试和集成测试 |
| **用户指南** | [用户指南](docs/guides/User.md) | 说明系统的使用方法 |
| **设计文档** | [架构设计](docs/design/Architecture.md)<br>[数据库设计](docs/design/Database.md)<br>[接口设计](docs/design/API.md)<br>[安全设计](docs/design/Security.md) | 系统设计相关文档 |
| **项目管理** | [项目结构](docs/project/Structure.md)<br>[任务进度](docs/project/Thread.md)<br>[变更日志](docs/project/Log.md)<br>[问题跟踪](docs/project/Issues.md)<br>[图表文档](docs/project/Diagram.md) | 项目管理相关文档 |
| **中文文档** | [中文文档目录](docs/zh/README.md)<br>[业务逻辑文档](docs/zh/问卷星自动化系统业务逻辑文档.md)<br>[后端实现细节](docs/zh/问卷星自动化系统后端实现细节文档.md)<br>[后端架构文档一](docs/zh/问卷星自动化系统后端架构文档_Part1.md)<br>[后端架构文档二](docs/zh/问卷星自动化系统后端架构文档_Part2.md) | 中文技术文档 |

## 系统特点

- 支持问卷解析与分析
- 支持多种题型自动填写（单选、多选、填空、评分等）
- 支持随机答案生成
- 支持使用大语言模型(LLM)生成智能答案
- 支持批量任务管理与执行
- 支持进度监控与结果统计
- 支持自定义提交间隔与模拟真实用户行为
- 支持Docker容器化部署
- 兼容Windows、Linux和MacOS系统

## 系统架构

该系统采用前后端分离架构：

- **前端**: Vue.js + Element Plus
- **后端**: Python + Flask
- **数据库**: 文件系统存储 (JSON)
- **部署**: Docker + Docker Compose

## 快速开始 (Windows)

### 方式一: 一键部署 (推荐)

1. 确保已安装 [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/) (注意: Docker Desktop与Docker本体不同，详见[Docker说明](docs/guides/Docker_Explanation.md))
2. 下载此项目到本地
3. 双击运行 `setup.bat` 文件
4. 按照提示完成安装和配置
5. 访问 `http://localhost:80` (或配置的其他端口) 打开系统界面

### 方式二: 使用PowerShell脚本部署

1. 确保已安装 [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
2. 打开PowerShell终端(以管理员身份运行)
3. 进入项目根目录
4. 运行以下命令:

```powershell
# 设置PowerShell执行策略为Bypass，允许运行脚本
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 初始化环境
.\deploy.ps1 setup

# 根据提示编辑.env文件配置环境变量

# 启动应用
.\deploy.ps1 start
```

5. 访问 `http://localhost:80` (或配置的其他端口) 打开系统界面

### 方式三: 手动部署

1. 确保已安装 [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
2. 复制 `.env.example` 为 `.env` 并编辑配置
3. 在项目根目录中打开命令提示符或PowerShell
4. 运行以下命令:

```cmd
# 构建镜像
docker-compose build

# 启动容器
docker-compose up -d
```

5. 访问 `http://localhost:80` (或配置的其他端口) 打开系统界面

## 系统配置 (.env文件)

项目配置主要通过 `.env` 文件进行，关键配置项包括:

```
# 环境配置
ENV_MODE=production             # production或development
FLASK_ENV=production            # production或development
NODE_ENV=production             # production或development
LOG_LEVEL=INFO                  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# 端口配置
BACKEND_PORT=5000               # 后端服务端口
FRONTEND_PORT=80                # 前端服务端口

# API配置
API_URL=http://localhost:5000   # 前端访问后端API的URL

# LLM配置（如果使用大语言模型生成答案）
LLM_PROVIDER=openai             # 大语言模型提供商: openai, baidu, zhipu等
LLM_API_KEY=your_api_key_here   # API密钥
LLM_MODEL=gpt-3.5-turbo         # 使用的模型名称

# 代理配置
USE_PROXY=false                 # 是否使用代理
DEFAULT_PROXY_URL=              # 默认代理URL，例如 http://127.0.0.1:7890
```

## 依赖管理

本项目使用分层的依赖管理方式，以支持不同的开发和部署环境。

### 依赖文件结构

- `backend/requirements.txt`: 主依赖文件
- `backend/requirements/requirements-base.txt`: 核心依赖
- `backend/requirements/requirements-prod.txt`: 生产环境依赖
- `backend/requirements/requirements-dev.txt`: 开发环境依赖
- `backend/requirements/requirements-docs.txt`: 文档生成依赖

### 使用虚拟环境

建议在开发环境中使用虚拟环境，以隔离项目依赖，防止与其他项目冲突。本项目提供了自动创建虚拟环境的脚本。

#### Windows 环境

```batch
# 创建并设置虚拟环境
setup_venv.bat

# 激活虚拟环境
call wjx_venv\Scripts\activate.bat

# 安装开发依赖
set DEV_MODE=1
setup_venv.bat

# 安装文档依赖
set DOCS_MODE=1
setup_venv.bat
```

#### Linux/macOS 环境

```bash
# 创建并设置虚拟环境
bash setup_venv.sh

# 激活虚拟环境
source wjx_venv/bin/activate

# 安装开发依赖
export DEV_MODE=1
bash setup_venv.sh

# 安装文档依赖
export DOCS_MODE=1
bash setup_venv.sh
```

### 锁定依赖版本

为确保开发和部署环境的一致性，可以使用依赖锁定文件：

#### Windows 环境

```batch
# 生成锁定文件
lock_dependencies.bat
```

#### Linux/macOS 环境

```bash
# 生成锁定文件
bash lock_dependencies.sh
```

### Docker 环境

Docker环境已配置好依赖管理，无需额外设置。使用以下命令运行：

```bash
# 开发环境
docker-compose -f docker-compose.yml -f docker-compose.override.yml up

# 生产环境
docker-compose up -d
```

## 使用说明

### 创建新任务

1. 在系统首页点击"创建任务"按钮
2. 输入问卷星链接（格式为: `https://www.wjx.cn/vm/xxxx.aspx` 或仅ID部分）
3. 设置任务参数，包括:
   - 提交次数: 需要提交的问卷数量
   - 使用LLM: 是否使用大语言模型生成答案
   - 使用代理: 是否使用代理服务
4. 点击"创建"按钮

### 查看任务状态

1. 在"任务列表"页面可以查看所有任务
2. 任务信息包括:
   - 任务ID
   - 问卷标题
   - 进度百分比
   - 成功/失败数量
   - 创建时间
   - 状态 (等待中/运行中/已完成/失败)

### 查看任务详情

1. 在任务列表中点击任务ID可以查看详情
2. 详情页包括:
   - 问卷结构
   - 提交记录
   - 失败原因(如有)

## 管理脚本 (deploy.ps1) 使用说明

脚本提供多种命令用于管理系统:

```powershell
# 初始设置环境和配置
.\deploy.ps1 setup

# 启动应用服务
.\deploy.ps1 start

# 停止应用服务
.\deploy.ps1 stop

# 重启应用服务
.\deploy.ps1 restart

# 查看应用日志
.\deploy.ps1 logs
# 或查看特定服务日志
.\deploy.ps1 logs backend
.\deploy.ps1 logs frontend

# 查看应用状态
.\deploy.ps1 status

# 更新应用(拉取最新代码并重建)
.\deploy.ps1 update

# 备份数据
.\deploy.ps1 backup

# 恢复数据
.\deploy.ps1 restore .\backups\backup_20250328_142500.zip

# 清理未使用的资源(镜像、容器、卷)
.\deploy.ps1 prune
```

## 常见问题解答

### Q: 系统启动后无法访问前端页面
A: 请检查以下几点:
- Docker Desktop是否正常运行
- 前端容器是否启动成功，可通过 `.\deploy.ps1 status` 查看
- 端口是否被占用，可在 `.env` 文件中修改端口配置
- 防火墙是否允许相应端口的访问

### Q: 无法解析问卷
A: 请检查:
- 问卷链接格式是否正确
- 是否需要设置代理 (中国大陆地区可能需要代理)
- 问卷是否存在密码保护或需要登录

### Q: 使用LLM功能失败
A: 请确保:
- 已在 `.env` 文件中正确配置LLM相关参数
- API密钥有效且未超出配额
- 如使用国际API，可能需要配置代理

## 故障排除

### Docker 相关问题

运行以下命令检查Docker服务状态:

```powershell
# 检查Docker是否运行
docker info

# 检查容器状态
docker-compose ps

# 查看详细日志
docker-compose logs
```

### 网络连接问题

排查网络连接问题:
1. 确认本地网络连接正常
2. 检查防火墙设置，确保不阻止Docker网络
3. 如使用代理，确认代理服务正常工作

## 系统更新

建议定期更新系统以获取最新功能和安全修复:

```powershell
# 拉取最新代码并重建应用
.\deploy.ps1 update
```

## 开发者指南

若要进行二次开发:

1. 将 `.env` 文件中的 `ENV_MODE` 设置为 `development`
2. 重启应用: `.\deploy.ps1 restart`
3. 前端代码位于 `frontend` 目录
4. 后端代码位于 `backend` 目录
5. 进行修改后，重新构建并启动应用

## 许可证

本项目采用 MIT 许可证
