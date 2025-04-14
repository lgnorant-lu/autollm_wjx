# 问卷星自动化系统快速入门指南

[返回主页](README.md) | [部署指南](docs/guides/Deployment.md) | [用户指南](docs/guides/User.md)

本指南提供了问卷星自动化系统的快速部署和使用说明，适合各种类型的用户。

## 一、系统要求

- **操作系统**: Windows 10/11
- **必要软件**:
  - 选项A（Docker部署）: [Docker Desktop](https://www.docker.com/products/docker-desktop/)
  - 选项B（本地部署）: Python 3.9+, Node.js 16+, npm 7+
  - PowerShell (Windows 10/11自带)

## 二、部署选项

您可以选择以下任一方式部署系统：

### 选项A: Docker一键部署（推荐，适合所有用户）

#### 1. 安装Docker Desktop

如果您尚未安装Docker Desktop，请先从[官方网站](https://www.docker.com/products/docker-desktop/)下载并安装。

#### 2. 运行一键部署脚本

1. 确保Docker Desktop已启动
2. 在项目根目录下，双击运行`setup.bat`脚本
3. 按照屏幕提示操作，脚本将自动：
   - 检查系统环境
   - 配置必要的文件和目录
   - 设置环境变量
   - 启动应用服务

### 选项B: 本地直接运行（适合开发者或不想使用Docker的用户）

#### 方式1: 使用一键式脚本（推荐）

1. 安装必要的软件：
   - [Python 3.9+](https://www.python.org/downloads/)
   - [Node.js 16+](https://nodejs.org/)

2. 在项目根目录下，双击运行`setup_local.bat`脚本

3. 按照屏幕提示操作，脚本将自动：
   - 检查系统环境
   - 创建Python虚拟环境
   - 安装后端和前端依赖
   - 配置环境变量
   - 启动应用服务

#### 方式2: 手动设置

1. 安装必要的软件

   - 安装 [Python 3.9+](https://www.python.org/downloads/)
   - 安装 [Node.js 16+](https://nodejs.org/)

2. 设置环境

   1. 在项目根目录下，运行以下命令创建虚拟环境：
      ```
      python -m venv venv
      .\venv\Scripts\activate
      pip install -r requirements.txt
      ```

   2. 设置前端环境：
      ```
      cd frontend
      npm install
      cd ..
      ```

   3. 复制环境变量文件：
      ```
      copy .env.example .env
      ```

3. 启动应用

   1. 启动后端：
      ```
      .\venv\Scripts\activate
      cd backend
      python app.py
      ```

   2. 在新的命令行窗口中启动前端：
      ```
      cd frontend
      npm run serve
      ```

## 三、访问应用

部署完成后，可以通过以下地址访问应用：

- **Docker部署**:
  - 前端界面: http://localhost:80
  - 后端API: http://localhost:5000

- **本地部署**:
  - 前端界面: http://localhost:8080
  - 后端API: http://localhost:5000

## 四、常见操作

所有操作都可以通过`deploy.ps1`脚本完成，在PowerShell或命令提示符中运行：

```
# 启动应用
.\deploy.ps1 start

# 停止应用
.\deploy.ps1 stop

# 重启应用
.\deploy.ps1 restart

# 查看日志
.\deploy.ps1 logs

# 查看应用状态
.\deploy.ps1 status

# 更新应用
.\deploy.ps1 update

# 备份数据
.\deploy.ps1 backup

# 恢复数据
.\deploy.ps1 restore .\backups\backup_20250328_142500.zip
```

## 五、常见问题

### Docker相关问题

**问题**: Docker无法启动
**解决**: 确保您的Windows系统已启用Hyper-V和虚拟化功能。可在BIOS中开启虚拟化支持。

**问题**: 端口冲突
**解决**: 如果80或5000端口被占用，可以编辑`.env`文件修改`FRONTEND_PORT`和`BACKEND_PORT`。

**问题**: Docker无法从Docker Hub拉取nginx镜像
**解决**:
1. 配置Docker镜像加速器，在Docker Desktop的设置中，找到"Docker Engine"配置部分，添加镜像加速器配置。
2. 使用静态前端备用方案：
   ```powershell
   # 启动后端API服务
   docker compose up -d backend

   # 启动静态前端服务器
   .\deploy.ps1 static-frontend
   ```

### 应用相关问题

**问题**: 应用启动失败
**解决**: 运行`.\deploy.ps1 logs`查看详细错误信息，常见原因包括端口冲突或权限问题。

**问题**: 无法访问应用界面
**解决**: 确保Docker容器正在运行(`.\deploy.ps1 status`)，并检查防火墙设置是否允许相应端口的访问。

## 六、获取帮助

如需更详细的部署和使用说明，请参考：

### 指南文档
- [完整部署文档](docs/guides/Deployment.md) - 详细的部署步骤和选项
- [用户指南](docs/guides/User.md) - 系统功能和操作说明
- [开发指南](docs/guides/Development.md) - 二次开发相关信息
- [测试指南](docs/guides/Testing.md) - 如何进行测试

### 技术文档
- [中文技术文档目录](docs/zh/README.md) - 中文技术文档入口
- [架构设计文档](docs/design/Architecture.md) - 系统架构设计
- [数据库设计文档](docs/design/Database.md) - 数据存储设计
- [接口设计文档](docs/design/API.md) - API接口设计

### 项目管理
- [项目结构](docs/project/Structure.md) - 项目文件结构
- [变更日志](docs/project/Log.md) - 项目变更记录

如有问题，请联系项目维护者或提交Issue。

---

[返回顶部](#问卷星自动化系统快速入门指南) | [返回主页](README.md)

祝您使用愉快！
