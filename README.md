# 问卷星自动化系统 (WJX Survey Automation)

基于LLM的问卷星接口自动化提交系统，提供高效的问卷解析、智能填写和批量提交功能。

## 项目简介

在当今快节奏的社会环境中，本项目旨在通过自动化技术节省时间，避免繁杂的重复性工作。系统通过逆向分析问卷星提交接口，结合LLM技术生成合理答案，实现了高效的问卷自动提交流程。

### 主要特点

- 🚀 **高效解析**: 自动分析问卷结构、题型和选项
- 🤖 **智能填写**: 基于LLM的答案生成，保证数据的逻辑性与多样性
- 🔄 **并发任务**: 多线程处理，同时管理多个提交任务
- 📊 **任务监控**: 实时展示任务进度和状态
- 🛡️ **防检测机制**: 模拟真实用户行为，避开防作弊检测

## 系统架构

项目采用前后端分离架构：
- 前端：Vue.js 3.x + Vite + Element Plus
- 后端：Flask RESTful API + Gunicorn
- 数据存储：文件系统 (JSON)

## 快速开始

### 环境要求
- Python 3.9+
- Node.js 16+
- npm 7+
- Docker (可选，推荐)

### 方法一：使用Docker部署（推荐）

#### Windows环境下的Docker安装

1. **安装Docker Desktop**
   - 下载: [Docker Desktop官网](https://www.docker.com/products/docker-desktop)
   - 安装时确保启用WSL2或Hyper-V
   - 安装后重启电脑

2. **无Docker Desktop的情况**
   - 安装Docker CLI和Docker Compose：
     ```bash
     # 使用Chocolatey安装
     choco install docker-cli docker-compose
     
     # 或使用Scoop安装
     scoop install docker docker-compose
     ```
   - 配置Docker引擎连接（需要远程Docker服务器）

#### 项目部署

```bash
# 克隆仓库
git clone https://github.com/lgnorant-lu/autollm_wjx.git
cd autollm_wjx

# 启动开发环境
docker compose -f docker-compose.yml -f docker-compose.override.yml up -d

# 或仅启动生产环境
docker compose up -d
```

#### 验证部署

- 前端访问: http://localhost:80
- 后端API: http://localhost:5000

#### Docker常用命令

```bash
# 查看容器状态
docker ps

# 查看日志
docker compose logs -f

# 停止服务
docker compose down

# 重建镜像
docker compose build
```

### 方法二：本地开发环境部署

1. 克隆仓库
```bash
git clone https://github.com/lgnorant-lu/autollm_wjx.git
cd autollm_wjx
```

2. 后端部署
```bash
# 创建并激活虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
cd backend
flask run --host=0.0.0.0 --port=5000

# 或生产环境启动
gunicorn app:app -b 0.0.0.0:5000 --workers=4
```

3. 前端部署
```bash
cd frontend
npm install
npm run dev

# 生产环境构建
npm run build
# 然后将dist目录部署到Web服务器
```

## 主要功能

1. **问卷管理**
   - 解析问卷结构
   - 查看问卷详情
   - 管理已解析问卷

2. **任务管理**
   - 创建提交任务
   - 监控任务状态
   - 暂停/继续/取消任务

3. **系统设置**
   - 配置LLM服务
   - 设置代理选项
   - 自定义提交策略

## 技术栈

### 前端
- Vue.js 3.x
- Element Plus
- Vue Router
- Axios
- ECharts
- Vite构建工具

### 后端
- Flask
- Gunicorn (生产环境)
- BeautifulSoup4
- Requests
- APScheduler
- Pandas & NumPy
- Selenium (浏览器自动化)

## 项目结构

```
autollm_wjx/
├── backend/                # 后端代码
│   ├── core/               # 核心功能
│   │   ├── parser.py       # 问卷解析
│   │   ├── wjx.py          # 问卷星接口
│   │   └── submitter.py    # 提交引擎
│   ├── routes/             # API路由
│   ├── services/           # 业务服务
│   ├── data/               # 数据存储
│   ├── logs/               # 日志目录
│   └── app.py              # 应用入口
│
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── api/            # API调用
│   │   ├── components/     # 组件
│   │   ├── views/          # 页面
│   │   └── App.vue         # 根组件
│   ├── public/             # 静态资源
│   ├── package.json        # 依赖配置
│   └── vite.config.js      # 构建配置
│
├── docker-compose.yml          # Docker生产配置
├── docker-compose.override.yml # Docker开发配置
├── Dockerfile.backend          # 后端Docker构建文件
├── Dockerfile.frontend         # 前端Docker构建文件
├── .dockerignore               # Docker忽略文件
├── requirements.txt            # Python依赖
└── README.md                   # 项目文档
```

## 故障排除

### 常见问题解决

1. **端口占用**
   ```bash
   # Windows查看端口占用
   netstat -ano | findstr 5000
   netstat -ano | findstr 80

   # 结束进程
   taskkill /F /PID <进程ID>
   ```

2. **Docker相关问题**
   - 容器无法启动: `docker logs <容器ID>` 查看详细错误
   - 网络问题: 检查 `docker network ls` 和防火墙设置
   - 卷挂载问题: 确认路径和权限正确

3. **前后端连接问题**
   - 检查CORS设置
   - 验证API地址配置
   - 确认网络连接和防火墙设置

4. **依赖安装失败**
   - 更新pip和npm: `pip install --upgrade pip` / `npm update -g`
   - 检查网络连接和代理设置
   - 尝试使用镜像源: `pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`

## 注意事项

- 本项目仅用于学习和研究，请勿用于商业用途
- 使用时请遵守相关法律法规和问卷平台的使用条款
- 建议合理设置提交间隔和频率，避免对目标服务器造成压力

## 许可

MIT License
