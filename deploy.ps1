# 问卷星自动化系统部署脚本 (Windows PowerShell版)
# 作者: Ignorant-lu
# 描述: 用于在Windows环境下部署和管理问卷星自动化系统的PowerShell脚本

# 颜色定义函数
function Write-ColorText {
    param (
        [string]$Text,
        [string]$Color = "White"
    )
    Write-Host $Text -ForegroundColor $Color
}

# 提供脚本说明
function Show-Usage {
    Write-ColorText "问卷星自动化系统部署脚本 (Windows版)" "Cyan"
    Write-Host ""
    Write-Host "用法: .\deploy.ps1 [命令]"
    Write-Host ""
    Write-Host "命令:"
    Write-Host "  setup       - 初始设置环境和配置"
    Write-Host "  start       - 启动应用服务"
    Write-Host "  stop        - 停止应用服务"
    Write-Host "  restart     - 重启应用服务"
    Write-Host "  logs        - 查看应用日志"
    Write-Host "  status      - 查看应用状态"
    Write-Host "  update      - 更新应用(拉取最新代码并重建)"
    Write-Host "  backup      - 备份数据"
    Write-Host "  restore     - 恢复数据"
    Write-Host "  prune       - 清理未使用的资源(镜像、容器、卷)"
    Write-Host ""
    Write-Host "示例:"
    Write-Host "  .\deploy.ps1 setup"
    Write-Host "  .\deploy.ps1 start"
    Write-Host "  .\deploy.ps1 logs backend"
    Write-Host ""
}

# 检查必要的命令
function Check-Requirements {
    Write-ColorText "检查系统要求..." "Cyan"

    # 检查Docker
    if (-not (Get-Command "docker" -ErrorAction SilentlyContinue)) {
        Write-ColorText "错误: Docker未安装" "Red"
        Write-Host "请参考 https://docs.docker.com/desktop/install/windows-install/ 安装Docker Desktop"
        exit 1
    }

    # 检查Docker Compose
    $dockerComposeCheck = docker compose version 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-ColorText "错误: Docker Compose未安装或未正常工作" "Red"
        Write-Host "Docker Desktop应包含Docker Compose，请确保Docker Desktop正确安装"
        exit 1
    } else {
        Write-ColorText "Docker Compose已安装" "Green"
    }

    # 检查Docker是否正在运行
    try {
        $dockerInfo = docker info 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-ColorText "错误: Docker未运行" "Red"
            Write-Host "请启动Docker Desktop后再试"
            exit 1
        }
    } catch {
        Write-ColorText "错误: Docker未运行" "Red"
        Write-Host "请启动Docker Desktop后再试"
        exit 1
    }

    Write-ColorText "系统要求检查通过" "Green"
}

# 初始设置环境
function Setup-Environment {
    Write-ColorText "设置环境..." "Cyan"

    # 检查.env文件是否存在
    if (-not (Test-Path ".env")) {
        if (Test-Path ".env.example") {
            Write-ColorText "未找到.env文件, 从.env.example创建" "Yellow"
            Copy-Item ".env.example" ".env"
            Write-ColorText "请编辑.env文件配置环境变量" "Yellow"
            Write-ColorText "编辑完成后重新运行 .\deploy.ps1 setup" "Yellow"
            exit 0
        } else {
            Write-ColorText "错误: 未找到.env.example文件" "Red"
            exit 1
        }
    }

    # 创建必要的目录
    New-Item -Path ".\logs\backend" -ItemType Directory -Force | Out-Null
    New-Item -Path ".\logs\frontend" -ItemType Directory -Force | Out-Null
    New-Item -Path ".\data\backend" -ItemType Directory -Force | Out-Null

    Write-ColorText "环境设置完成" "Green"
    Write-ColorText "现在可以使用 .\deploy.ps1 start 启动应用" "Yellow"
}

# 启动应用
function Start-App {
    Write-ColorText "启动应用..." "Cyan"

    # 从.env加载环境变量
    $envContent = Get-Content ".env" -ErrorAction SilentlyContinue
    $ENV_MODE = "production"
    $FRONTEND_PORT = "80"
    $BACKEND_PORT = "5000"

    foreach ($line in $envContent) {
        if ($line -match "ENV_MODE=(.*)") {
            $ENV_MODE = $matches[1].Trim()
        }
        if ($line -match "FRONTEND_PORT=(.*)") {
            $FRONTEND_PORT = $matches[1].Trim()
        }
        if ($line -match "BACKEND_PORT=(.*)") {
            $BACKEND_PORT = $matches[1].Trim()
        }
    }

    # 根据环境模式启动
    try {
        if ($ENV_MODE -eq "development") {
            Write-ColorText "以开发模式启动..." "Yellow"
            docker compose -f docker-compose.yml -f docker-compose.override.yml up -d
            if ($LASTEXITCODE -ne 0) {
                Write-ColorText "错误: Docker Compose 命令失败" "Red"
                exit 1
            }
        } else {
            Write-ColorText "以生产模式启动..." "Green"
            docker compose up -d
            if ($LASTEXITCODE -ne 0) {
                Write-ColorText "错误: Docker Compose 命令失败" "Red"
                exit 1
            }
        }

        Write-ColorText "Docker Compose 启动命令已执行。" "Green"
        Write-ColorText "请使用 'docker compose ps' 或 'docker ps' 检查容器状态。" "Yellow"
        Write-ColorText "前端访问地址 (如果成功启动): http://localhost:$FRONTEND_PORT" "Yellow"
        Write-ColorText "后端API地址 (如果成功启动): http://localhost:$BACKEND_PORT" "Yellow"

    } catch {
        Write-ColorText "错误: 启动应用时出错 (docker compose up -d 失败)" "Red"
        Write-Error "错误详情: $($_.Exception.Message)"
        if ($_.ScriptStackTrace) { Write-Error "StackTrace: $($_.ScriptStackTrace)" }
        if ($_.ErrorDetails) { Write-Error "ErrorDetails: $($_.ErrorDetails)" }
        exit 1
    }
}

# 停止应用
function Stop-App {
    Write-ColorText "停止应用..." "Cyan"
    docker compose down
    Write-ColorText "应用已停止" "Green"
}

# 重启应用
function Restart-App {
    Write-ColorText "重启应用..." "Cyan"
    Stop-App
    Start-App
    Write-ColorText "应用已重启" "Green"
}

# 查看应用日志
function Show-Logs {
    param (
        [string]$service
    )

    if ([string]::IsNullOrEmpty($service)) {
        Write-ColorText "查看所有服务日志..." "Cyan"
        docker compose logs --tail=100
    } else {
        Write-ColorText "查看 $service 服务日志..." "Cyan"
        docker compose logs --tail=100 $service
    }
}

# 查看应用状态
function Show-Status {
    Write-ColorText "应用状态..." "Cyan"
    docker compose ps
    Write-Host ""
    Write-ColorText "资源使用情况..." "Cyan"

    # 获取所有运行中的容器ID
    $containers = docker compose ps -q
    if ($containers) {
        docker stats --no-stream $containers
    } else {
        Write-ColorText "没有运行中的容器" "Yellow"
    }
}

# 更新应用
function Update-App {
    Write-ColorText "更新应用..." "Cyan"

    # 备份当前数据
    Write-ColorText "备份当前数据..." "Yellow"
    Backup-Data

    # 拉取最新代码
    Write-ColorText "拉取最新代码..." "Yellow"
    git pull

    # 重建并重启
    Write-ColorText "重建容器..." "Yellow"
    docker compose build

    # 重启应用
    Restart-App

    Write-ColorText "应用更新完成" "Green"
}

# 备份数据
function Backup-Data {
    Write-ColorText "备份数据..." "Cyan"

    # 创建备份目录
    $backupDir = ".\backups"
    if (-not (Test-Path $backupDir)) {
        New-Item -Path $backupDir -ItemType Directory | Out-Null
    }

    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupFile = "$backupDir\backup_$timestamp.zip"

    # 备份数据目录
    Write-ColorText "备份数据目录..." "Yellow"
    Compress-Archive -Path ".\data", ".\logs", ".\.env" -DestinationPath $backupFile -Force

    Write-ColorText "数据备份完成: $backupFile" "Green"
}

# 恢复数据
function Restore-Data {
    param (
        [string]$backupFile
    )

    if ([string]::IsNullOrEmpty($backupFile)) {
        Write-ColorText "错误: 请指定要恢复的备份文件" "Red"
        Write-Host "用法: .\deploy.ps1 restore .\backups\backup_20250328_142500.zip"
        exit 1
    }

    if (-not (Test-Path $backupFile)) {
        Write-ColorText "错误: 备份文件 $backupFile 不存在" "Red"
        exit 1
    }

    Write-ColorText "恢复数据..." "Cyan"

    # 停止应用
    Stop-App

    # 备份当前数据(以防万一)
    Write-ColorText "备份当前数据..." "Yellow"
    Backup-Data

    # 恢复数据
    Write-ColorText "恢复数据从 $backupFile ..." "Yellow"
    Expand-Archive -Path $backupFile -DestinationPath "." -Force

    # 重启应用
    Start-App

    Write-ColorText "数据恢复完成" "Green"
}

# 清理资源
function Prune-Resources {
    Write-ColorText "清理未使用的资源..." "Cyan"

    Write-ColorText "清理未使用的容器..." "Yellow"
    docker container prune -f

    Write-ColorText "清理未使用的镜像..." "Yellow"
    docker image prune -f

    Write-ColorText "清理未使用的网络..." "Yellow"
    docker network prune -f

    Write-ColorText "清理未使用的卷..." "Yellow"
    # 注意: 卷包含数据，不强制清理
    $response = Read-Host "警告: 这将删除所有未使用的卷，可能导致数据丢失。是否继续？(y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        docker volume prune
    } else {
        Write-ColorText "已取消卷清理" "Yellow"
    }

    Write-ColorText "资源清理完成" "Green"
}

# 主函数
function Main {
    param (
        [string]$command,
        [string]$arg
    )

    # 如果没有命令参数，显示使用说明
    if ([string]::IsNullOrEmpty($command)) {
        Show-Usage
        exit 0
    }

    # 检查系统要求
    Check-Requirements

    # 根据命令执行相应的操作
    switch ($command) {
        "setup" {
            Setup-Environment
            break
        }
        "start" {
            Start-App
            break
        }
        "stop" {
            Stop-App
            break
        }
        "restart" {
            Restart-App
            break
        }
        "logs" {
            Show-Logs -service $arg
            break
        }
        "status" {
            Show-Status
            break
        }
        "update" {
            Update-App
            break
        }
        "backup" {
            Backup-Data
            break
        }
        "restore" {
            Restore-Data -backupFile $arg
            break
        }
        "prune" {
            Prune-Resources
            break
        }
        default {
            Write-ColorText "错误: 未知命令 $command" "Red"
            Show-Usage
            exit 1
        }
    }
}

# 执行主函数，传入所有参数
Main $args[0] $args[1]