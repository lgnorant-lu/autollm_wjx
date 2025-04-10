# 部署指南

本文档提供问卷星自动化系统的部署说明，包括Docker和传统部署两种方式。

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

## 2. Docker部署(推荐)

Docker部署是最简单且推荐的部署方式，可确保在不同环境中一致运行。

### 2.1 前提条件

- 安装Docker: [Docker安装指南](https://docs.docker.com/get-docker/)
- 安装Docker Compose: [Docker Compose安装指南](https://docs.docker.com/compose/install/)

### 2.2 获取代码

```bash
git clone https://github.com/yourusername/autollm_wjx.git
cd autollm_wjx
```

### 2.3 配置环境变量

创建`.env`文件在项目根目录：

```
# LLM API配置
LLM_PROVIDER=openai
LLM_API_KEY=your_api_key_here
LLM_MODEL=gpt-3.5-turbo

# 生产环境配置
FLASK_ENV=production
LOG_LEVEL=INFO
```

### 2.4 启动服务

#### 生产环境部署

```bash
# 构建和启动容器
docker compose up -d

# 查看日志
docker compose logs -f
```

#### 开发环境部署

```bash
# 使用开发配置启动
docker compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

### 2.5 访问服务

- Web界面: http://yourserver:80
- API服务: http://yourserver:5000

### 2.6 停止服务

```bash
docker compose down
```

### 2.7 更新部署

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker compose down
docker compose build
docker compose up -d
```

## 4. 本地直接运行

如果您不想使用Docker，或者希望在本地环境中直接运行应用（适合开发者或不想使用Docker的用户），可以使用以下方式部署。

### 4.1 后端部署

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

### 4.2 前端部署

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

## 5. SSL配置

### 5.1 使用Let's Encrypt(推荐)

```bash
# 安装certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your_domain.com

# 自动续期
sudo certbot renew --dry-run
```

### 5.2 使用自签名证书

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

## 5. 日志和监控

### 5.1 日志位置

- Docker部署:
  - 应用日志: `docker compose logs -f`
  - 容器日志: `/var/lib/docker/containers/[container-id]/[container-id]-json.log`

- 传统部署:
  - 后端日志: `logs/api.log`
  - Nginx访问日志: `/var/log/nginx/access.log`
  - Nginx错误日志: `/var/log/nginx/error.log`

### 5.2 监控

建议使用Prometheus + Grafana进行监控，具体配置请参考相关文档。

## 6. 备份策略

### 6.1 数据备份

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

### 6.2 自动备份

使用crontab设置定期备份:

```bash
# 每天凌晨2点备份
0 2 * * * /path/to/backup.sh
```

## 7. 常见问题

### 7.1 Docker相关问题

- **容器无法启动**: 检查日志`docker compose logs`
- **端口冲突**: 修改`docker-compose.yml`中的端口映射
- **权限问题**: 确保数据目录可写入

### 7.2 性能优化

- 增加Gunicorn工作进程数
- 配置Nginx缓存静态资源
- 使用Redis缓存频繁访问的数据

### 7.3 故障恢复

1. 检查日志文件定位问题
2. 尝试重启服务
3. 如果数据损坏，从备份恢复
4. 检查网络和防火墙设置