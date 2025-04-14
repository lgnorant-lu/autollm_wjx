# 问卷星自动化系统 - 部署指南

[返回文档索引](../index.md) | [项目结构](../project/Structure.md) | [故障排除](Troubleshooting.md) | [静态前端备用方案](static-frontend.md)

本文档提供问卷星自动化系统的部署说明，包括Docker部署、静态前端备用方案和传统部署方式。

## 目录

- [1. 环境要求](#1-环境要求)
- [2. Docker配置](#2-docker配置)
- [3. Docker部署方法](#3-docker部署方法)
- [4. 静态前端备用方案](#4-静态前端备用方案)
- [5. 传统部署](#5-传统部署)
- [6. 访问应用](#6-访问应用)
- [7. 管理应用](#7-管理应用)
- [8. 环境变量](#8-环境变量)
- [9. 高级部署选项](#9-高级部署选项)
- [10. SSL配置](#10-ssl配置)

## 1. 环境要求

### 1.1 基本要求

- 操作系统: Linux(推荐Ubuntu 20.04+), Windows Server 2019+, macOS
- Python 3.9+
- Node.js 16+
- npm 7+
- Docker(如使用容器化部署)
- 至少2GB内存
- 至少10GB存储空间

### 1.2 网络要求

- 互联网连接(用于调用LLM API和访问问卷星)
- 如部署在云服务器上，需开放以下端口：
  - 80/443: Web访问
  - 5000: API服务(如果不使用反向代理)

## 2. Docker配置

### 2.1 镜像加速器配置

为了解决从Docker Hub拉取镜像的网络问题，建议配置Docker镜像加速器。在Docker Desktop的设置中，找到"Docker Engine"配置部分，添加以下配置：

```json
{
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  },
  "experimental": false,
  "registry-mirrors": [
    "https://mirror.ccs.tencentyun.com",
    "https://repo.huaweicloud.com/dockerhub",
    "https://docker.mirrors.ustc.edu.cn",
    "https://mirrors.tuna.tsinghua.edu.cn/docker-ce",
    "https://hub-mirror.c.163.com",
    "https://reg-mirror.qiniu.com",
    "https://dockerhub-mirror.ccr.runedgex.com",
    "https://dockerproxy.com"
  ]
}
```

保存配置后重启Docker Desktop。

**注意**：配置镜像加速器后，您应该能够成功拉取nginx镜像，这对于前端容器的构建是必要的。如果仍然无法拉取镜像，可以使用静态前端备用方案（见下文）。

### 2.2 健康检查配置

如果您的网络环境不稳定，可能会导致容器健康检查失败。在这种情况下，建议禁用健康检查。编辑docker-compose.yml文件，注释或删除所有的healthcheck部分。

## 3. Docker部署方法

### 3.1 前提条件

- 安装Docker: [Docker安装指南](https://docs.docker.com/get-docker/)
- 安装Docker Compose: [Docker Compose安装指南](https://docs.docker.com/compose/install/)

### 3.2 获取代码

```bash
git clone https://github.com/yourusername/autollm_wjx.git
cd autollm_wjx
```

### 3.3 配置环境变量

创建`.env`文件在项目根目录：

```
# 环境配置
ENV_MODE=production

# 端口配置
FRONTEND_PORT=80
BACKEND_PORT=5000

# LLM API配置
LLM_PROVIDER=openai
LLM_API_KEY=your_api_key_here
LLM_MODEL=gpt-3.5-turbo

# 代理配置
USE_PROXY=false
DEFAULT_PROXY_URL=

# 生产环境配置
FLASK_ENV=production
LOG_LEVEL=INFO
```

### 3.4 使用Docker Compose部署（推荐）

1. 确保Docker Desktop已启动并配置了镜像加速器
2. 打开PowerShell或终端，进入项目根目录
3. 运行一键部署脚本：

```powershell
# Windows
.\setup.ps1
```

或者使用部署脚本手动启动：

```powershell
# Windows
.\deploy.ps1 start

# Linux/Mac
./deploy.sh start
```

这将启动后端API服务和前端服务。

### 3.5 处理常见部署问题

#### 3.5.1 Content Security Policy (CSP)问题

如果前端页面无法加载外部资源（如CDN上的样式表）或连接到后端API，可能是nginx配置中的CSP头部设置不正确。解决方法：

```powershell
# 创建正确的nginx配置文件
$cspConfig = @"
server {
    listen 80;
    server_name localhost;

    # 启用gzip压缩
    gzip on;
    gzip_comp_level 5;
    gzip_min_length 256;
    gzip_proxied any;
    gzip_types
        application/javascript
        application/json
        application/xml
        text/css
        text/plain
        text/xml;

    # 安全相关头部
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-XSS-Protection "1; mode=block";
    add_header X-Content-Type-Options "nosniff";

    # 修改CSP以允许外部资源和API连接
    add_header Content-Security-Policy "default-src 'self' https: http:; script-src 'self' 'unsafe-inline' 'unsafe-eval' https: http:; style-src 'self' 'unsafe-inline' https: http:; img-src 'self' data: https: http:; font-src 'self' data: https: http:; connect-src 'self' https: http: ws: wss:;";

    # 静态文件服务
    location / {
        root   /usr/share/nginx/html;
        index  index.html;
        try_files `$uri `$uri/ /index.html;
        expires 30d;
    }

    # 静态资源缓存策略
    location ~* \.(css|js|jpg|jpeg|png|gif|ico|svg)`$ {
        root /usr/share/nginx/html;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    # API代理
    location /api {
        proxy_pass http://backend:5000/api;
        proxy_http_version 1.1;
        proxy_set_header Upgrade `$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host `$host;
        proxy_set_header X-Real-IP `$remote_addr;
        proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto `$scheme;
        proxy_cache_bypass `$http_upgrade;
    }

    # 后端根路径代理
    location = / {
        proxy_pass http://backend:5000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade `$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host `$host;
        proxy_set_header X-Real-IP `$remote_addr;
        proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto `$scheme;
        proxy_cache_bypass `$http_upgrade;
    }

    # 错误页面
    error_page 404 /index.html;
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
"@

# 将配置写入文件
$cspConfig | Out-File -Encoding utf8 -FilePath .\frontend\nginx\default.conf.new

# 复制配置到容器
docker cp .\frontend\nginx\default.conf.new wjx-frontend:/etc/nginx/conf.d/default.conf

# 重新加载nginx配置
docker exec wjx-frontend nginx -s reload
```

#### 3.5.2 容器健康检查问题

如果容器显示为"unhealthy"状态，可以修改docker-compose.yml文件，禁用健康检查：

```powershell
# 编辑docker-compose.yml文件
notepad docker-compose.yml

# 注释或删除healthcheck部分
# 然后重新启动容器
docker-compose down
docker-compose up -d
```

## 4. 静态前端备用方案

如果由于网络问题无法从Docker Hub拉取Nginx镜像，可以使用静态前端备用方案：

1. 确保Docker Desktop已启动
2. 打开PowerShell或终端，进入项目根目录
3. 运行以下命令启动后端API服务：

```powershell
docker compose up -d backend
```

4. 运行以下命令启动静态前端服务器：

```powershell
# Windows
.\deploy.ps1 static-frontend

# Linux/Mac
./deploy.sh static-frontend
```

更多关于静态前端备用方案的信息，请参阅[静态前端备用方案](static-frontend.md)文档。

## 5. 传统部署

如果您不想使用Docker，可以使用传统方式部署。

### 5.1 后端部署

#### 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/Mac
source venv/bin/activate
# Windows
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

#### 配置环境变量

创建`.env`文件在项目根目录或设置系统环境变量：

```
FLASK_ENV=production
LLM_PROVIDER=openai
LLM_API_KEY=your_api_key_here
LLM_MODEL=gpt-3.5-turbo
```

#### 启动后端服务

**使用Gunicorn(推荐，仅Linux/Mac)**:

```bash
cd backend
gunicorn --bind 0.0.0.0:5000 --workers=4 app:app
```

**使用Flask内置服务器(不推荐用于生产)**:

```bash
cd backend
flask run --host=0.0.0.0 --port=5000
```

**使用systemd服务(Linux)**:

创建服务文件`/etc/systemd/system/autollm_wjx.service`:

```
[Unit]
Description=AutoLLM WJX Backend Service
After=network.target

[Service]
User=youruser
WorkingDirectory=/path/to/autollm_wjx/backend
ExecStart=/path/to/autollm_wjx/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers=4 app:app
Restart=on-failure
Environment="FLASK_ENV=production"
Environment="LLM_PROVIDER=openai"
Environment="LLM_API_KEY=your_api_key_here"
Environment="LLM_MODEL=gpt-3.5-turbo"

[Install]
WantedBy=multi-user.target
```

启动服务:

```bash
sudo systemctl enable autollm_wjx
sudo systemctl start autollm_wjx
```

### 5.2 前端部署

#### 构建前端

```bash
cd frontend
npm install
npm run build
```

构建完成后，生成的静态文件位于`frontend/dist`目录。

#### 部署到Web服务器

**使用Nginx(推荐)**:

安装Nginx:

```bash
# Ubuntu/Debian
sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx
```

配置Nginx:

创建`/etc/nginx/sites-available/autollm_wjx`文件:

```nginx
server {
    listen 80;
    server_name your_domain.com;

    # 前端静态文件
    location / {
        root /path/to/autollm_wjx/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # API代理
    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用站点:

```bash
sudo ln -s /etc/nginx/sites-available/autollm_wjx /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 6. 访问应用

- 前端访问地址：http://localhost:80
- 后端API地址：http://localhost:5000
- API状态检查：http://localhost:5000/api/status

## 7. 管理应用

使用`deploy.ps1`脚本管理应用：

- `.\deploy.ps1 setup`: 设置环境
- `.\deploy.ps1 start`: 启动应用
- `.\deploy.ps1 stop`: 停止应用
- `.\deploy.ps1 restart`: 重启应用
- `.\deploy.ps1 logs`: 查看日志
- `.\deploy.ps1 status`: 查看状态
- `.\deploy.ps1 prune`: 清理资源
- `.\deploy.ps1 static-frontend`: 启动静态前端服务器

## 8. 环境变量

可以通过`.env`文件配置以下环境变量：

- `ENV_MODE`: 环境模式，可选值为`development`或`production`，默认为`production`
- `FRONTEND_PORT`: 前端服务端口，默认为`80`
- `BACKEND_PORT`: 后端API服务端口，默认为`5000`
- `FLASK_ENV`: Flask环境，默认为`production`
- `LOG_LEVEL`: 日志级别，默认为`INFO`
- `LLM_PROVIDER`: LLM提供商，可选值为`openai`等
- `LLM_API_KEY`: LLM API密钥
- `LLM_MODEL`: LLM模型名称，如`gpt-3.5-turbo`
- `USE_PROXY`: 是否使用代理，可选值为`true`或`false`
- `DEFAULT_PROXY_URL`: 默认代理URL

完整的`.env`文件示例：

```
# 环境配置
ENV_MODE=production

# 端口配置
FRONTEND_PORT=80
BACKEND_PORT=5000

# LLM配置
LLM_PROVIDER=openai
LLM_API_KEY=your_api_key_here
LLM_MODEL=gpt-3.5-turbo

# 代理配置
USE_PROXY=false
DEFAULT_PROXY_URL=

# 日志级别
LOG_LEVEL=INFO
```

## 9. 高级部署选项

### 9.1 开发环境部署

```powershell
# 使用开发配置启动
docker compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

### 9.2 更新部署

```powershell
# 拉取最新代码
git pull

# 重新构建并启动
docker compose down
docker compose build
docker compose up -d
```

### 9.3 备份数据

定期备份以下目录:

- `data/`: 系统数据目录
- `.env`: 环境配置文件

示例备份脚本:

```bash
#!/bin/bash
BACKUP_DIR="/backup/autollm_wjx/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR
cp -r /path/to/autollm_wjx/data $BACKUP_DIR
cp /path/to/autollm_wjx/.env $BACKUP_DIR
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR
```

### 9.4 自动备份

使用crontab设置定期备份:

```bash
# 每天凌晨2点备份
0 2 * * * /path/to/backup.sh
```

### 9.5 日志位置

- Docker部署:
  - 应用日志: `docker compose logs -f`
  - 后端日志: `/app/logs/api/app.log`（容器内路径）
  - Nginx访问日志: `/var/log/nginx/access.log`
  - Nginx错误日志: `/var/log/nginx/error.log`

## 10. SSL配置

### 10.1 使用Let's Encrypt(推荐)

```bash
# 安装certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your_domain.com

# 自动续期
sudo certbot renew --dry-run
```

### 10.2 使用自签名证书

```bash
# 生成证书
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/autollm_wjx.key -out /etc/ssl/certs/autollm_wjx.crt
```

在Nginx配置中启用SSL:

```nginx
server {
    listen 443 ssl;
    server_name your_domain.com;

    ssl_certificate /etc/ssl/certs/autollm_wjx.crt;
    ssl_certificate_key /etc/ssl/private/autollm_wjx.key;

    # 其他配置同上
}

server {
    listen 80;
    server_name your_domain.com;
    return 301 https://$host$request_uri;
}
```

---

## 相关文档

- [项目结构](../project/Structure.md) - 项目目录结构和组件说明
- [故障排除](Troubleshooting.md) - 常见问题和解决方案
- [静态前端备用方案](static-frontend.md) - 当Docker无法连接时的替代方案
- [开发指南](Development.md) - 如何进行二次开发

[返回文档索引](../index.md) | [返回顶部](#问卷星自动化系统---部署指南)
