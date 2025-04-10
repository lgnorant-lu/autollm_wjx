# 问卷星自动化系统快速入门指南

本指南提供了问卷星自动化系统的快速部署和使用说明，特别适合对Docker和部署不熟悉的新手用户。

## 一、系统要求

- **操作系统**: Windows 10/11
- **必要软件**: 
  - [Docker Desktop](https://www.docker.com/products/docker-desktop/)
  - PowerShell (Windows 10/11自带)

## 二、一键部署步骤

### 1. 安装Docker Desktop

如果您尚未安装Docker Desktop，请先从[官方网站](https://www.docker.com/products/docker-desktop/)下载并安装。

### 2. 运行一键部署脚本

1. 确保Docker Desktop已启动
2. 在项目根目录下，双击运行`setup.bat`脚本
3. 按照屏幕提示操作，脚本将自动：
   - 检查系统环境
   - 配置必要的文件和目录
   - 设置环境变量
   - 启动应用服务

### 3. 访问应用

部署完成后，系统会自动在浏览器中打开应用页面。默认访问地址：
- 前端界面: http://localhost:80
- 后端API: http://localhost:5000

## 三、常见操作

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

## 四、常见问题

### Docker相关问题

**问题**: Docker无法启动
**解决**: 确保您的Windows系统已启用Hyper-V和虚拟化功能。可在BIOS中开启虚拟化支持。

**问题**: 端口冲突
**解决**: 如果80或5000端口被占用，可以编辑`.env`文件修改`FRONTEND_PORT`和`BACKEND_PORT`。

### 应用相关问题

**问题**: 应用启动失败
**解决**: 运行`.\deploy.ps1 logs`查看详细错误信息，常见原因包括端口冲突或权限问题。

**问题**: 无法访问应用界面
**解决**: 确保Docker容器正在运行(`.\deploy.ps1 status`)，并检查防火墙设置是否允许相应端口的访问。

## 五、获取帮助

如需更详细的部署和使用说明，请参考：
- 完整部署文档: [docs/guides/Deployment.md](docs/guides/Deployment.md)
- 用户指南: [docs/guides/User.md](docs/guides/User.md)
- 中文技术文档: [docs/zh/README.md](docs/zh/README.md)

如有问题，请联系项目维护者或提交Issue。

---

祝您使用愉快！
