# 问卷星自动化系统Docker部署完整指南

[返回文档索引](../index.md) | [部署指南](Deployment.md) | [快速入门](QUICK_START.md)

本文档提供了问卷星自动化系统的Docker部署完整流程，包括所有必要的步骤和可能遇到的问题的解决方案。

## 目录

- [1. 前提条件](#1-前提条件)
- [2. 部署步骤](#2-部署步骤)
  - [2.1 获取代码](#21-获取代码)
  - [2.2 配置环境变量](#22-配置环境变量)
  - [2.3 使用一键部署脚本](#23-使用一键部署脚本)
  - [2.4 手动部署](#24-手动部署)
- [3. 修复常见问题](#3-修复常见问题)
  - [3.1 修复Content Security Policy (CSP)问题](#31-修复content-security-policy-csp问题)
  - [3.2 修复容器健康检查问题](#32-修复容器健康检查问题)
  - [3.3 修复数据目录权限问题](#33-修复数据目录权限问题)
- [4. 访问应用](#4-访问应用)
- [5. 管理Docker容器](#5-管理docker容器)
- [6. 更新应用](#6-更新应用)
- [7. 备份数据](#7-备份数据)
- [8. 故障排除](#8-故障排除)

## 1. 前提条件

1. 安装Docker和Docker Compose
2. 确保系统有足够的磁盘空间和内存
3. 确保端口80和5000未被占用

## 2. 部署步骤

### 2.1 获取代码

首先，确保您已经获取了完整的代码库：

```powershell
# 如果是从GitHub克隆
git clone <repository-url>
cd autollm_wjx

# 如果已有代码，确保代码是最新的
git pull
```

### 2.2 配置环境变量

创建或编辑`.env`文件，设置必要的环境变量：

```powershell
# 复制示例环境变量文件
copy .env.example .env

# 编辑.env文件，根据需要修改配置
notepad .env
```

主要环境变量说明：
- `FRONTEND_PORT`: 前端服务端口（默认80）
- `BACKEND_PORT`: 后端API端口（默认5000）
- `ENV_MODE`: 环境模式（production或development）
- `LLM_PROVIDER`: LLM提供商（如果使用）
- `LLM_API_KEY`: LLM API密钥（如果使用）

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

### 2.3 使用一键部署脚本

问卷星自动化系统提供了一键部署脚本，可以自动完成所有部署步骤：

```powershell
# 以管理员权限运行PowerShell
# 进入项目根目录
cd autollm_wjx

# 运行一键部署脚本
.\setup.ps1
```

脚本会执行以下操作：
1. 检查系统要求（Docker、PowerShell版本等）
2. 设置环境变量
3. 构建和启动Docker容器
4. 显示访问地址

### 2.4 手动部署（如果一键脚本失败）

如果一键部署脚本失败，可以按照以下步骤手动部署：

#### 2.4.1 确保Docker服务正在运行

```powershell
# 检查Docker状态
docker info
```

如果Docker未运行，请启动Docker Desktop或Docker服务。

#### 2.4.2 构建Docker镜像

```powershell
# 进入项目根目录
cd autollm_wjx

# 构建Docker镜像
docker-compose build
```

如果构建过程中遇到网络问题（如无法从Docker Hub下载镜像），可以尝试以下解决方案：

1. 配置Docker镜像加速器（如阿里云、腾讯云等）
2. 使用已有的镜像（如果之前已经构建过）
3. 使用VPN或代理

#### 2.4.3 启动Docker容器

```powershell
# 启动Docker容器
docker-compose up -d
```

#### 2.4.4 检查容器状态

```powershell
# 检查容器状态
docker-compose ps

# 或者
docker ps
```

确保所有容器都处于"Up"状态。

#### 2.4.5 查看容器日志

如果容器启动失败或运行异常，可以查看日志：

```powershell
# 查看前端容器日志
docker logs wjx-frontend

# 查看后端容器日志
docker logs wjx-backend
```

## 3. 修复常见问题

### 3.1 修复Content Security Policy (CSP)问题

如果前端页面无法加载外部资源（如CDN上的样式表）或连接到后端API，可能是CSP配置问题。解决方法：

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

### 3.2 修复容器健康检查问题

如果容器显示为"unhealthy"状态，可以修改docker-compose.yml文件，禁用健康检查：

```powershell
# 编辑docker-compose.yml文件
notepad docker-compose.yml

# 注释或删除healthcheck部分
# 然后重新启动容器
docker-compose down
docker-compose up -d
```

### 3.3 修复数据目录权限问题

如果后端容器无法访问数据目录，可能是权限问题：

```powershell
# 进入容器
docker exec -it wjx-backend /bin/bash

# 在容器内检查目录权限
ls -la /app/data
ls -la /app/logs

# 如果需要，修改权限
chmod -R 777 /app/data
chmod -R 777 /app/logs

# 退出容器
exit
```

## 4. 访问应用

部署完成后，可以通过以下URL访问应用：

- 前端页面：http://localhost:80（或您在.env中配置的FRONTEND_PORT）
- 后端API：http://localhost:5000（或您在.env中配置的BACKEND_PORT）
- API状态检查：http://localhost:5000/api/status

## 5. 管理Docker容器

### 5.1 启动容器

```powershell
docker-compose up -d
```

### 5.2 停止容器

```powershell
docker-compose down
```

### 5.3 重启容器

```powershell
docker-compose restart
```

### 5.4 查看日志

```powershell
# 查看所有容器的日志
docker-compose logs

# 查看特定容器的日志
docker-compose logs frontend
docker-compose logs backend

# 实时查看日志
docker-compose logs -f
```

### 5.5 进入容器

```powershell
# 进入前端容器
docker exec -it wjx-frontend /bin/sh

# 进入后端容器
docker exec -it wjx-backend /bin/bash
```

## 6. 更新应用

当有新版本发布时，可以按照以下步骤更新应用：

```powershell
# 拉取最新代码
git pull

# 重新构建镜像
docker-compose build

# 重启容器
docker-compose down
docker-compose up -d
```

## 7. 备份数据

定期备份数据是很重要的：

```powershell
# 备份数据目录
$backupDate = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = "backups\$backupDate"
mkdir -p $backupDir
copy -r data $backupDir
copy -r logs $backupDir
```

## 8. 故障排除

### 8.1 Docker容器无法启动

检查Docker服务是否正在运行：

```powershell
docker info
```

检查端口是否被占用：

```powershell
netstat -ano | findstr :80
netstat -ano | findstr :5000
```

### 8.2 前端无法连接到后端

检查nginx配置是否正确：

```powershell
docker exec wjx-frontend cat /etc/nginx/conf.d/default.conf
```

检查后端容器是否正常运行：

```powershell
docker logs wjx-backend
```

### 8.3 数据目录问题

检查数据目录是否存在并且有正确的权限：

```powershell
docker exec wjx-backend ls -la /app/data
docker exec wjx-backend ls -la /app/logs
```

### 8.4 网络问题

检查Docker网络是否正常：

```powershell
docker network ls
docker network inspect autollm_wjx_wjx-network
```

---

## 相关文档

- [部署指南](Deployment.md) - 详细的部署步骤和选项
- [快速入门](QUICK_START.md) - 系统快速入门指南
- [Docker说明](Docker_Explanation.md) - Docker Desktop与Docker的关系说明

[返回文档索引](../index.md) | [返回顶部](#问卷星自动化系统docker部署完整指南)
