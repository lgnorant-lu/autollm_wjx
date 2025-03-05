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
- 前端：Vue.js + Element Plus
- 后端：Flask RESTful API
- 数据存储：文件系统 (JSON)

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 14+
- npm 6+

### 安装步骤

1. 克隆仓库
```bash
git clone https://github.com/yourusername/wjx-automation.git
cd wjx-automation
```

2. 安装后端依赖
```bash
pip install -r requirements.txt
```

3. 安装前端依赖
```bash
cd frontend
npm install
```

4. 启动后端服务
```bash
cd backend
python app.py
```

5. 启动前端开发服务器
```bash
cd frontend
npm run dev
```

### Docker部署

使用Docker Compose快速部署整个应用：

```bash
docker-compose up -d
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

### 后端
- Flask
- BeautifulSoup4
- Requests
- APScheduler
- 多线程处理

## 项目结构

```
wjx-automation/
├── backend/                # 后端代码
│   ├── core/               # 核心功能
│   │   ├── parser.py       # 问卷解析
│   │   ├── wjx.py          # 问卷星接口
│   │   └── submitter.py    # 提交引擎
│   ├── routes/             # API路由
│   ├── services/           # 业务服务
│   └── app.py              # 应用入口
│
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── api/            # API调用
│   │   ├── components/     # 组件
│   │   ├── views/          # 页面
│   │   └── App.vue         # 根组件
│   ├── package.json        # 依赖配置
│   └── vite.config.js      # 构建配置
│
├── docker-compose.yml      # Docker配置
├── requirements.txt        # Python依赖
└── README.md               # 项目文档
```

## 注意事项

- 本项目仅用于学习和研究，请勿用于商业用途
- 使用时请遵守相关法律法规和问卷平台的使用条款
- 建议合理设置提交间隔和频率，避免对目标服务器造成压力

## 许可

MIT License
