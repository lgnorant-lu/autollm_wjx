#Requires -Version 5.0
# -*- coding: utf-8 -*-
<#
.SYNOPSIS
    问卷星自动化系统一键部署脚本 (PowerShell 版本)
.DESCRIPTION
    本脚本将帮助您快速部署问卷星自动化系统，检查依赖项并启动服务。
    请确保以管理员权限运行此脚本，以便正确检查和启动 Docker 服务。
.NOTES
    Author: AI Assistant based on original bat script
    Date:   (Current Date)
#>

# --- 配置 ---
# 启用严格模式
Set-StrictMode -Version Latest

# --- 消息定义 ---
$MSG_TITLE = "问卷星自动化系统一键部署脚本 (PowerShell)"
$MSG_WELCOME = "本脚本将帮助您快速部署问卷星自动化系统。"
$MSG_CONFIRM_PROMPT = "是否继续部署过程？(y/N):"
$MSG_CANCELLED = "已取消部署过程。"
$MSG_CHECKING_REQ = "正在检查系统要求..."
$MSG_ADMIN_REQUIRED = "警告：建议以管理员权限运行此脚本以获得最佳兼容性（例如检查和启动 Docker 服务）。"
$MSG_POWERSHELL_OK = "PowerShell 版本检查通过。"
$MSG_ERR_NO_DOCKER_CMD = "错误: 未找到 Docker 命令 (不在 PATH 中)"
$MSG_CHECKING_DOCKER_INSTALL = "正在检查 Docker 是否已安装..."
$MSG_CHECKING_DOCKER_CACHE = "检查缓存的 Docker 路径..."
$MSG_FOUND_DOCKER_CACHE = "找到 Docker (来自缓存):"
$MSG_CHECKING_DOCKER_SERVICE = "检查 Docker 服务..."
$MSG_FOUND_DOCKER_SERVICE = "找到 Docker 服务"
$MSG_ERR_SERVICE_CHECK_FAILED = "检查 Docker 服务失败 (可能需要管理员权限)"
$MSG_CHECKING_DOCKER_REG = "检查注册表中的 Docker 信息..."
$MSG_FOUND_DOCKER_REG = "从注册表找到 Docker 安装路径:"
$MSG_CHECKING_DOCKER_COMMON = "检查常见安装位置..."
$MSG_FOUND_DOCKER_COMMON = "找到 Docker:"
$MSG_CHECKING_DOCKER_STARTMENU = "检查开始菜单..."
$MSG_FOUND_DOCKER_SHORTCUT = "找到 Docker 快捷方式:"
$MSG_SEARCHING_DRIVE = "搜索系统驱动器 (限制深度)..."
$MSG_SEARCHING_PATH = "搜索"
$MSG_FOUND_DOCKER_SEARCH = "找到 Docker:"
$MSG_DOCKER_FOUND_NOT_IN_PATH = "找到 Docker 可执行文件，但它不在系统 PATH 中。将尝试使用找到的路径。"
$MSG_ERR_DOCKER_NOT_FOUND = "错误：未找到 Docker 安装。请确认 Docker Desktop 已正确安装。"
$MSG_INSTALL_DOCKER = "请安装 Docker Desktop，参考:"
$MSG_DOCKER_CMD_OK = "Docker 命令检查通过。"
$MSG_WARN_DOCKER_NOT_RUNNING = "警告: Docker 守护程序未运行 (docker info 失败)"
$MSG_TRYING_START_DOCKER = "正在尝试启动 Docker Desktop..."
$MSG_USING_CACHED_DOCKER_PATH = "使用缓存的 Docker 路径:"
$MSG_FOUND_DOCKER_DESKTOP = "找到 Docker Desktop:"
$MSG_FINDING_DOCKER_REG_APP = "尝试从注册表查找 Docker Desktop App Path..."
$MSG_FOUND_DOCKER_DESKTOP_REG = "从注册表找到 Docker Desktop:"
$MSG_FINDING_DOCKER_STARTMENU = "尝试从开始菜单启动 Docker Desktop..."
$MSG_WAITING_DOCKER_START = "等待 Docker Desktop 启动 (最多 30 秒)..."
$MSG_DOCKER_STARTED_SUCCESS = "Docker 已成功启动！"
$MSG_DOCKER_START_FAILED = "尝试启动 Docker Desktop 失败。"
$MSG_TRYING_DOCKER_SERVICE = "尝试通过服务启动 Docker..."
$MSG_FOUND_DOCKER_SERVICE_START = "找到 Docker 服务，尝试启动..."
$MSG_DOCKER_STARTED_SERVICE = "成功通过服务启动 Docker！"
$MSG_ERR_CANNOT_START_DOCKER = "错误: 无法自动启动 Docker Desktop"
$MSG_DOCKER_TROUBLESHOOT_PROMPT = "请确认以下事项："
$MSG_DOCKER_TROUBLESHOOT_1 = " 1. Docker Desktop 已正确安装"
$MSG_DOCKER_TROUBLESHOOT_2 = " 2. 如果安装在自定义位置，请手动启动 Docker Desktop"
$MSG_DOCKER_TROUBLESHOOT_3 = " 3. 确保您的防火墙或安全软件不阻止 Docker 运行"
$MSG_DOCKER_TROUBLESHOOT_4 = " 4. 如果您刚刚安装了 Docker Desktop，请尝试重启计算机"
$MSG_DOCKER_TROUBLESHOOT_5 = " 5. 以管理员权限运行此脚本可能有助于自动启动"
$MSG_DOCKER_MANUAL_START_PROMPT = "您可以手动启动 Docker Desktop，然后按 Enter 键继续..."
$MSG_DOCKER_NOW_RUNNING = "Docker 现在已经运行！"
$MSG_DOCKER_STILL_NOT_RUNNING = "Docker 仍然未运行，请手动启动 Docker Desktop 后重新运行此脚本"
$MSG_ERR_DOCKER_TIMEOUT = "错误: Docker 启动超时"
$MSG_RETRY_AFTER_MANUAL_START = "请手动启动 Docker Desktop，然后重新运行此脚本。"
$MSG_SYS_CHECK_OK = "系统检查通过！"
$MSG_ERR_NOT_ROOT_DIR = "错误: 当前目录不是项目根目录 (未找到 docker-compose.yml)"
$MSG_ERR_RUN_IN_ROOT_DIR = "请将此脚本放在项目根目录（包含 docker-compose.yml 的目录）下运行。"
$MSG_ERR_NO_DEPLOY_SCRIPT = "错误: 未找到 deploy.ps1 脚本"
$MSG_ENSURE_DEPLOY_SCRIPT = "请确保 deploy.ps1 脚本位于项目根目录。"
$MSG_SETTING_ENV = "正在设置环境 (调用 deploy.ps1 setup)..."
$MSG_ERR_ENV_SETUP_FAILED = "环境设置失败 (deploy.ps1 setup 调用失败)"
$MSG_ENV_DETECTED = "检测到 .env 文件，是否需要编辑？(y/N):"
$MSG_START_APP_PROMPT = "是否立即启动应用？(Y/n):"
$MSG_STARTING_APP = "正在启动应用 (调用 deploy.ps1 start)..."
$MSG_ERR_APP_START_FAILED = "应用启动失败 (deploy.ps1 start 调用失败)"
$MSG_APP_STARTED_SUCCESS = "应用已成功启动！"
$MSG_APP_MGMT_INFO = "您可以通过 deploy.ps1 脚本管理应用 (start, stop, restart, logs)。"
$MSG_FRONTEND_URL = "前端访问地址:"
$MSG_BACKEND_URL = "后端API地址:"
$MSG_OPEN_BROWSER_PROMPT = "是否在浏览器中打开前端页面？(Y/n):"
$MSG_DEPLOY_COMPLETE = "部署过程已完成！"
$MSG_THANK_YOU = "感谢使用问卷星自动化系统。"
$MSG_EXIT_PROMPT = "按 Enter 键退出..."

# --- 全局变量 ---
$DockerExePath = $null # 用于存储找到的 Docker 可执行文件路径（如果不在PATH中）
$DockerPathCacheFile = Join-Path $env:TEMP "docker_path_cache.txt"
$IsAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

# --- 函数定义 ---

function Exit-Script($exitCode = 0) {
    Read-Host -Prompt $MSG_EXIT_PROMPT | Out-Null
    exit $exitCode
}

# Helper function to check directory for docker.exe
# Needs to be defined *before* Find-DockerCliInstallation
function Check-DirectoryForDockerCli($Directory) {
    if (-not $Directory -or -not (Test-Path -LiteralPath $Directory)) {
        Write-Warning "Check-DirectoryForDockerCli: Invalid directory provided: '$Directory'"
        return $null
    }
    $cliPath = Join-Path $Directory "docker.exe"
    if (Test-Path -LiteralPath $cliPath) {
        return $cliPath
    }
    $cliPathBin = Join-Path $Directory "resources\bin\docker.exe" # Common location
    if (Test-Path -LiteralPath $cliPathBin) {
        return $cliPathBin
    }
    return $null
}

# Function to find docker.exe path
function Find-DockerCliInstallation {
    Write-Host $MSG_CHECKING_DOCKER_INSTALL
    $dockerCliPath = $null
    $dockerDesktopPath = $null

    # 1. 检查缓存 (优先缓存 CLI 路径)
    Write-Host $MSG_CHECKING_DOCKER_CACHE
    if (Test-Path -LiteralPath $DockerPathCacheFile) { # Use LiteralPath here too
        # Read the first line and trim any leading/trailing whitespace
        $cachedPath = (Get-Content $DockerPathCacheFile | Select-Object -First 1).Trim()
        # Use -LiteralPath and check if $cachedPath is not empty
        if ($cachedPath -and (Test-Path -LiteralPath $cachedPath -ErrorAction SilentlyContinue)) {
            if ($cachedPath -like '*docker.exe') {
                Write-Host "$MSG_FOUND_DOCKER_CACHE (CLI) $cachedPath"
                # Verify it's really docker.exe (basic check)
                try {
                    & $cachedPath --version > $null
                    if ($?) { return $cachedPath, $null }
                } catch {}
                Write-Warning "Cached path '$cachedPath' looks like docker.exe but failed verification."
            } elseif ($cachedPath -like '*Docker Desktop.exe') {
                 # Might be Desktop path from old cache
                 Write-Host "$MSG_FOUND_DOCKER_CACHE (Desktop) $cachedPath"
                 $dockerDesktopPath = $cachedPath
                 # Attempt to find CLI relative to Desktop path if CLI not found yet
                 try {
                     $desktopItem = Get-Item -LiteralPath $dockerDesktopPath -ErrorAction Stop
                     $cliCheckDir = $desktopItem.Directory.FullName
                     $potentialCli = Check-DirectoryForDockerCli -Directory $cliCheckDir # Now call the globally defined function
                     if ($potentialCli) {
                         Write-Host "  (找到 CLI 相对于缓存的 Desktop 路径: $potentialCli)"
                         # Verify CLI
                         try {
                            & $potentialCli --version > $null
                            if ($?) { return $potentialCli, $dockerDesktopPath }
                         } catch {}
                         Write-Warning "Found potential CLI '$potentialCli' relative to cached Desktop, but failed verification."
                     }
                 } catch {
                     Write-Warning "无法获取缓存的 Desktop 路径 '$dockerDesktopPath' 的目录信息: $($_.Exception.Message)"
                 }
            } else {
                 Write-Warning "Cached path '$cachedPath' is not recognized as docker.exe or Docker Desktop.exe"
            }
        } else {
             Write-Warning "Cached path '$cachedPath' is invalid, not found, or contains illegal characters."
             # Optionally remove the invalid cache file
             try { Remove-Item -LiteralPath $DockerPathCacheFile -ErrorAction SilentlyContinue } catch {}
        }
    }

    # 2. 检查服务路径 (可能包含 CLI)
    Write-Host $MSG_CHECKING_DOCKER_SERVICE
    try {
        $dockerService = Get-Service -Name 'docker' -ErrorAction SilentlyContinue
        if ($dockerService) {
            Write-Host $MSG_FOUND_DOCKER_SERVICE
            $servicePathRaw = (Get-CimInstance Win32_Service -Filter "Name='docker'").PathName
            if ($servicePathRaw -match '"(.*?)"') {
                $servicePath = $Matches[1]
                $serviceDir = Split-Path -Path $servicePath -Parent
                $dockerCliPath = Check-DirectoryForDockerCli -Directory $serviceDir
                if ($dockerCliPath) {
                     Write-Host "  (找到 CLI 通过服务路径: $dockerCliPath)"
                }
                # Also check if service path points to Docker Desktop
                if (-not $dockerDesktopPath -and ($servicePath -like '*Docker Desktop.exe') -and (Test-Path $servicePath)) {
                    $dockerDesktopPath = $servicePath
                    Write-Host "  (找到 Desktop 通过服务路径: $dockerDesktopPath)"
                }
            }
        }
    } catch {
        Write-Warning $MSG_ERR_SERVICE_CHECK_FAILED
    }

    # 3. 检查注册表 (寻找 Docker Desktop 安装位置, 然后推断 CLI)
    if (-not $dockerCliPath) {
        Write-Host $MSG_CHECKING_DOCKER_REG
        $uninstallKeys = @(
            'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*',
            'HKLM:\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*'
        )
        foreach ($keyPath in $uninstallKeys) {
             try {
                # Attempt to get InstallLocation directly first
                $regEntry = Get-ItemProperty $keyPath -ErrorAction SilentlyContinue | Where-Object { $_.InstallLocation -ne $null -and ($_.DisplayName -like '*Docker Desktop*' -or $_.DisplayName -like '*Docker*' )} | Select-Object -First 1
                if ($regEntry -and $regEntry.InstallLocation) {
                    $installDir = $regEntry.InstallLocation
                    $dockerCliPath = Check-DirectoryForDockerCli -Directory $installDir
                    if ($dockerCliPath) {
                        Write-Host "$MSG_FOUND_DOCKER_REG (CLI 推断自 $installDir) $dockerCliPath"
                        # Check for desktop path as well
                        $potentialDesktopPath = Join-Path $installDir "Docker Desktop.exe"
                        if (-not $dockerDesktopPath -and (Test-Path $potentialDesktopPath)) {
                            $dockerDesktopPath = $potentialDesktopPath
                            Write-Host "  (找到 Desktop: $dockerDesktopPath)"
                        }
                        break # Found CLI
                    } elseif (-not $dockerDesktopPath) {
                        # Check if InstallLocation itself points to Docker Desktop
                        $potentialDesktopPath = Join-Path $installDir "Docker Desktop.exe"
                         if (Test-Path $potentialDesktopPath) {
                            $dockerDesktopPath = $potentialDesktopPath
                            Write-Host "$MSG_FOUND_DOCKER_REG (Desktop) $dockerDesktopPath"
                            # Still need to check this dir for CLI
                            $dockerCliPath = Check-DirectoryForDockerCli -Directory (Split-Path $dockerDesktopPath -Parent)
                            if ($dockerCliPath) { Write-Host "  (找到 CLI: $dockerCliPath)"; break }
                        }
                    }
                }
            } catch {}
        }
    }

    # 4. 检查常见安装位置 (CLI 和 Desktop)
    if (-not $dockerCliPath) {
        Write-Host $MSG_CHECKING_DOCKER_COMMON
        $commonPaths = @(
            # Prioritize potential CLI paths
            "$env:ProgramFiles\Docker\Docker\resources\bin\docker.exe",
            "$env:ProgramFiles\Docker\Docker\docker.exe",
            "$env:ProgramFiles\Docker\docker.exe",
            "${env:ProgramFiles(x86)}\Docker\Docker\resources\bin\docker.exe",
            "${env:ProgramFiles(x86)}\Docker\Docker\docker.exe",
            # Desktop paths
            "$env:ProgramFiles\Docker\Docker\Docker Desktop.exe",
            "${env:ProgramFiles(x86)}\Docker\Docker\Docker Desktop.exe",
            "D:\Program Files\Docker\Docker\resources\bin\docker.exe", # Custom drive
            "D:\Program Files\Docker\Docker\docker.exe",
            "D:\Program Files\Docker\Docker\Docker Desktop.exe",
            "D:\Docker\Docker Desktop\resources\bin\docker.exe",
            "D:\Docker\Docker Desktop\docker.exe",
            "D:\Docker\Docker Desktop\Docker Desktop.exe",
            "D:\Docker Desktop\resources\bin\docker.exe",
            "D:\Docker Desktop\docker.exe",
            "D:\Docker Desktop\Docker Desktop.exe"
        )
        foreach ($path in $commonPaths) {
            if (Test-Path $path) {
                if ($path -like '*docker.exe') {
                    Write-Host "$MSG_FOUND_DOCKER_COMMON (CLI) $path"
                    $dockerCliPath = $path
                    # If we found CLI, try to find Desktop nearby if not already found
                    if (-not $dockerDesktopPath) {
                         $potentialDesktopPath = Join-Path (Split-Path $path -Parent -Resolve) "Docker Desktop.exe"
                         if (!(Test-Path $potentialDesktopPath)) { # Check one level up from resources/bin
                            $potentialDesktopPath = Join-Path (Split-Path (Split-Path $path -Parent) -Parent -Resolve) "Docker Desktop.exe"
                         }
                         if (Test-Path $potentialDesktopPath) {
                              $dockerDesktopPath = $potentialDesktopPath
                              Write-Host "  (找到 Desktop: $dockerDesktopPath)"
                         }
                    }
                    break # Found CLI, exit loop
                } elseif ($path -like '*Docker Desktop.exe' -and (-not $dockerDesktopPath)) {
                    Write-Host "$MSG_FOUND_DOCKER_COMMON (Desktop) $path"
                    $dockerDesktopPath = $path
                    # If we found Desktop, check for CLI nearby
                    $dockerCliPath = Check-DirectoryForDockerCli -Directory (Split-Path $path -Parent)
                    if ($dockerCliPath) {
                        Write-Host "  (找到 CLI: $dockerCliPath)"
                        break # Found both, exit loop
                    }
                }
            }
        }
    }

    # Cache the found CLI path if successful
    if ($dockerCliPath) {
        try {
            Set-Content -Path $DockerPathCacheFile -Value $dockerCliPath -Encoding UTF8 -Force
        } catch {
            Write-Warning "无法写入 Docker CLI 路径缓存文件: $DockerPathCacheFile"
        }
        return $dockerCliPath, $dockerDesktopPath
    } elseif ($dockerDesktopPath) {
        # Cache desktop path if CLI not found but desktop was
         try {
            Set-Content -Path $DockerPathCacheFile -Value $dockerDesktopPath -Encoding UTF8 -Force
        } catch {
            Write-Warning "无法写入 Docker Desktop 路径缓存文件: $DockerPathCacheFile"
        }
         return $null, $dockerDesktopPath # Return only desktop path
    }

    return $null, $null # Return nulls if nothing found
}

# Function to Start Docker Desktop and wait for daemon
# Takes the *Desktop* exe path and *CLI* exe path as input
function Start-Docker($DesktopPath, $CliPath) {
    Write-Host $MSG_TRYING_START_DOCKER
    $startedGui = $false

    # 优先尝试使用找到的 Desktop 路径启动 GUI
    if ($DesktopPath -and (Test-Path $DesktopPath)) {
        Write-Host "尝试使用路径启动 Docker Desktop GUI: $DesktopPath"
        try {
            Start-Process -FilePath $DesktopPath
            $startedGui = $true
        } catch {
            Write-Warning "使用路径启动 Docker Desktop GUI 失败: $($_.Exception.Message)"
        }
    }

    # 尝试从注册表 App Path 启动 GUI
    if (-not $startedGui) {
         Write-Host $MSG_FINDING_DOCKER_REG_APP
         $appPath = (Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\Docker Desktop.exe' -ErrorAction SilentlyContinue).'(Default)'
         if ($appPath -and (Test-Path $appPath)) {
             Write-Host "$MSG_FOUND_DOCKER_DESKTOP_REG $appPath"
             try {
                Start-Process -FilePath $appPath
                $startedGui = $true
             } catch {
                 Write-Warning "从 App Path 启动 Docker GUI 失败: $($_.Exception.Message)"
             }
         }
    }

    # 尝试使用 Shell 命令启动 GUI
    if (-not $startedGui) {
        Write-Host $MSG_FINDING_DOCKER_STARTMENU
        try {
            Start-Process "shell:AppsFolder\Docker.Docker.Docker" -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 3 # Give it a moment
            $startedGui = $true # Assume started if no error
        } catch { }
    }

    # 尝试使用服务启动 (可能会启动后台服务，但不一定是 GUI)
    if (-not $startedGui -and $IsAdmin) {
        Write-Host $MSG_TRYING_DOCKER_SERVICE
        $dockerService = Get-Service -Name 'docker' -ErrorAction SilentlyContinue
        if ($dockerService -and $dockerService.Status -ne 'Running') {
            Write-Host $MSG_FOUND_DOCKER_SERVICE_START
            try {
                Start-Service -Name 'docker'
                Start-Sleep -Seconds 5 # 给服务启动时间
                Write-Host $MSG_DOCKER_STARTED_SERVICE
            } catch {
                Write-Warning "启动 Docker 服务失败: $($_.Exception.Message)"
            }
        } elseif ($dockerService.Status -eq 'Running'){
             Write-Host "Docker 服务已经在运行。"
        }
    }

    if (-not $startedGui -and $dockerService -eq $null) {
        Write-Error $MSG_DOCKER_START_FAILED
        return $false
    }

    # 等待 Docker 守护进程响应 (using docker info)
    Write-Host $MSG_WAITING_DOCKER_START
    $waitTime = 0
    $maxWaitTime = 60 # Increased timeout
    $dockerInfoOutput = $null
    $dockerReady = $false

    while ($waitTime -lt $maxWaitTime) {
        $dockerInfoResult = $null
        $lastError = $null
        try {
            Write-Host "DEBUG: Attempting 'docker info' (Wait Loop)..." -ForegroundColor Cyan
            if ($CliPath) {
                 Write-Host "DEBUG: Using CLI Path: '$CliPath'" -ForegroundColor Cyan
                 $dockerInfoResult = & $CliPath info -ErrorAction Stop 2>&1
            } else {
                 Write-Host "DEBUG: Using 'docker' from PATH" -ForegroundColor Cyan
                 $dockerInfoResult = docker info -ErrorAction Stop 2>&1
            }
            # If command succeeded without error:
            Write-Host "DEBUG: 'docker info' command SUCCEEDED in wait loop." -ForegroundColor Green
            $dockerReady = $true
            break # Exit the while loop
        } catch {
            # Capture error details
            $lastError = $_ # Store the full error record
            Write-Warning "DEBUG: 'docker info' command FAILED in wait loop. Error: $($_.Exception.Message)"
            if ($_.ScriptStackTrace) { Write-Warning "DEBUG: StackTrace: $($_.ScriptStackTrace)" }
            # Check if output was captured before error
            if ($dockerInfoResult -ne $null) {
                Write-Warning "DEBUG: Output before error (if any): $dockerInfoResult"
            } elseif ($_.TargetObject) {
                 Write-Warning "DEBUG: Error TargetObject: $($_.TargetObject)"
            }
        }

        Start-Sleep -Seconds 3 # Wait longer between checks
        $waitTime += 3
        Write-Host "." -NoNewline
    }
    Write-Host ""

    if ($dockerReady) {
        Write-Host $MSG_DOCKER_STARTED_SUCCESS -ForegroundColor Green
        return $true
    } else {
        Write-Error $MSG_ERR_DOCKER_TIMEOUT
        if ($lastError -ne $null) {
             Write-Error "Last error during 'docker info' check: $($lastError.Exception.Message)"
             # Try to get more info if it was a command not found error
             if ($lastError.Exception.Message -like "*无法将?docker?项识别*" -or $lastError.FullyQualifiedErrorId -eq 'CommandNotFoundException') {
                  Write-Error "Docker command not found, even after attempts. Check installation and PATH."
             }
        } else {
            Write-Warning "Timeout occurred but no specific error was captured from the last 'docker info' attempt."
        }
        return $false
    }
}


# --- 脚本主体 ---

Clear-Host
Write-Host $MSG_TITLE
Write-Host ("-" * $MSG_TITLE.Length)
Write-Host $MSG_WELCOME
Write-Host ""

# 检查管理员权限
if (-not $IsAdmin) {
    Write-Warning $MSG_ADMIN_REQUIRED
}

# 确认是否继续
$confirm = Read-Host -Prompt $MSG_CONFIRM_PROMPT
if ($confirm -ne 'y') {
    Write-Host $MSG_CANCELLED
    Exit-Script
}
Write-Host ""

# --- 检查系统要求 ---
Write-Host $MSG_CHECKING_REQ

# 1. 检查 PowerShell
Write-Host $MSG_POWERSHELL_OK

# 2. 检查 Docker 命令是否存在于 PATH 或可查找
$DockerCliPath = $null
$DockerDesktopPath = $null
$dockerCmd = Get-Command docker -ErrorAction SilentlyContinue
$DockerCliInSystemPath = $false # Flag

if ($dockerCmd) {
    Write-Host $MSG_DOCKER_CMD_OK
    $DockerCliPath = $dockerCmd.Source
    $DockerCliInSystemPath = $true
    # Try to find Desktop path nearby if possible, for starting GUI
    $DockerDesktopPath = Join-Path (Split-Path $DockerCliPath -Parent) "Docker Desktop.exe"
    if (-not (Test-Path $DockerDesktopPath)) {
        $DockerDesktopPath = Join-Path (Split-Path (Split-Path $DockerCliPath -Parent) -Parent) "Docker Desktop.exe" # Try one level higher
        if (-not (Test-Path $DockerDesktopPath)) {
             $DockerDesktopPath = $null # Give up finding desktop path automatically
        }
    }

} else {
    Write-Warning $MSG_ERR_NO_DOCKER_CMD
    # 尝试查找 Docker CLI 和 Desktop 安装路径
    $DockerCliPath, $DockerDesktopPath = Find-DockerCliInstallation

    if (-not $DockerCliPath) {
        Write-Error $MSG_ERR_DOCKER_NOT_FOUND
        Write-Host "$MSG_INSTALL_DOCKER https://docs.docker.com/desktop/install/windows-install/"
        # Start-Process "https://docs.docker.com/desktop/install/windows-install/"
        Exit-Script 1
    } else {
         Write-Host "找到 Docker CLI: $DockerCliPath"
         if ($DockerDesktopPath) { Write-Host "找到 Docker Desktop: $DockerDesktopPath"}
         else { Write-Host "未自动找到 Docker Desktop GUI 路径，将尝试其他启动方法。"}
    }
}

# --- Add Docker Context Check ---
Write-Host "--- Checking Docker Context --- " -ForegroundColor Yellow
try {
    $contextOutput = $null
    $contextCmd = "docker context show"
    if (-not $DockerCliInSystemPath -and $DockerCliPath) {
        Write-Host "DEBUG: Running context check using CLI Path: '$DockerCliPath'" -ForegroundColor Cyan
        $contextCmd = "& '$($DockerCliPath)' context show"
        $contextOutput = Invoke-Expression $contextCmd 2>&1
    } else {
        Write-Host "DEBUG: Running context check using 'docker' from PATH" -ForegroundColor Cyan
        $contextOutput = docker context show 2>&1
    }
    Write-Host "Current Docker Context:"
    if ($contextOutput -like "*error*" -or $contextOutput -like "*unknown*" -or $LASTEXITCODE -ne 0) {
        Write-Warning "Docker context output indicates an issue:"
        Write-Warning ($contextOutput | Out-String)
    } else {
        Write-Host ($contextOutput | Out-String) -ForegroundColor Green
    }
} catch {
    Write-Warning "DEBUG: Failed to get Docker context: $($_.Exception.Message)"
    if ($_.ScriptStackTrace) { Write-Warning "DEBUG: StackTrace: $($_.ScriptStackTrace)" }
}
Write-Host "----------------------------- " -ForegroundColor Yellow
# --- End Docker Context Check ---

# 3. 检查 Docker 是否运行 (docker info)
Write-Host "正在检查 Docker 守护进程状态 (docker info)..."
$dockerInfoOutput = $null
$dockerCheckError = $null
$dockerRunning = $false
try {
    Write-Host "DEBUG: Attempting initial 'docker info' check..." -ForegroundColor Cyan
    if (-not $DockerCliInSystemPath -and $DockerCliPath) {
        Write-Host "DEBUG: Using CLI Path: '$DockerCliPath'" -ForegroundColor Cyan
        $dockerInfoOutput = & $DockerCliPath info -ErrorAction Stop 2>&1
    } else {
        Write-Host "DEBUG: Using 'docker' from PATH" -ForegroundColor Cyan
        $dockerInfoOutput = docker info -ErrorAction Stop 2>&1
    }
    Write-Host "DEBUG: Initial 'docker info' check SUCCEEDED." -ForegroundColor Green
    $dockerRunning = $true
} catch {
    $dockerCheckError = $_ # Store error record
    Write-Warning "DEBUG: Initial 'docker info' check FAILED. Error: $($_.Exception.Message)"
    # Display captured output if any
    if ($dockerInfoOutput -ne $null) { Write-Warning "DEBUG: Output before error: $dockerInfoOutput" }
}

if (-not $dockerRunning) {
    Write-Warning $MSG_WARN_DOCKER_NOT_RUNNING
    # Display the specific error from the initial check, if one occurred
    if ($dockerCheckError -ne $null) {
        Write-Warning "Reason for initial failure: $($dockerCheckError.Exception.Message)"
        # Check if it was command not found
         if ($dockerCheckError.Exception.Message -like "*无法将?docker?项识别*" -or $dockerCheckError.FullyQualifiedErrorId -eq 'CommandNotFoundException') {
              Write-Error "Docker command not found. Cannot proceed."
              Exit-Script 1
         }
    }

    # 尝试启动 Docker (pass both Desktop and CLI paths)
    if (-not (Start-Docker -DesktopPath $DockerDesktopPath -CliPath $DockerCliPath)) {
        Write-Error $MSG_ERR_CANNOT_START_DOCKER
        Write-Host $MSG_DOCKER_TROUBLESHOOT_PROMPT
        Write-Host $MSG_DOCKER_TROUBLESHOOT_1
        Write-Host $MSG_DOCKER_TROUBLESHOOT_2
        Write-Host $MSG_DOCKER_TROUBLESHOOT_3
        Write-Host $MSG_DOCKER_TROUBLESHOOT_4
        Write-Host $MSG_DOCKER_TROUBLESHOOT_5
        Write-Host ""
        Read-Host -Prompt $MSG_DOCKER_MANUAL_START_PROMPT | Out-Null

        # 再次检查 (use try/catch again)
        Write-Host "DEBUG: Re-checking 'docker info' after manual prompt..." -ForegroundColor Cyan
        $dockerInfoOutput = $null
        $lastCheckError = $null
        $manualStartSuccess = $false
        try {
             if (-not $DockerCliInSystemPath -and $DockerCliPath) {
                 $dockerInfoOutput = & $DockerCliPath info -ErrorAction Stop 2>&1
             } else {
                 $dockerInfoOutput = docker info -ErrorAction Stop 2>&1
             }
             $manualStartSuccess = $true
        } catch {
            $lastCheckError = $_
        }

        if (-not $manualStartSuccess) {
            Write-Error $MSG_DOCKER_STILL_NOT_RUNNING
             if ($lastCheckError -ne $null) {
                 Write-Error "Final 'docker info' check failed: $($lastCheckError.Exception.Message)"
             }
             Exit-Script 1
        } else {
            Write-Host $MSG_DOCKER_NOW_RUNNING -ForegroundColor Green
        }
    }
} else {
    Write-Host "Docker 守护进程已运行。" -ForegroundColor Green
    # Optionally display some output from the successful initial check
    # Write-Host "DEBUG: Initial 'docker info' output snippet: $($dockerInfoOutput | Select-Object -First 5 | Out-String)"
}

Write-Host $MSG_SYS_CHECK_OK
Write-Host ""

# --- 部署步骤 ---

# 检查当前目录是否为项目根目录
$composeFile = ".\docker-compose.yml"
if (-not (Test-Path $composeFile)) {
    Write-Error $MSG_ERR_NOT_ROOT_DIR
    Write-Host $MSG_ERR_RUN_IN_ROOT_DIR
    Exit-Script 1
}

# 检查部署脚本
$deployScript = ".\deploy.ps1"
if (-not (Test-Path $deployScript)) {
    Write-Error $MSG_ERR_NO_DEPLOY_SCRIPT
    Write-Host $MSG_ENSURE_DEPLOY_SCRIPT
    Exit-Script 1
}

# 设置环境
Write-Host $MSG_SETTING_ENV
try {
    & $deployScript setup -ErrorAction Stop
} catch {
    Write-Error $MSG_ERR_ENV_SETUP_FAILED
    Write-Error "错误详情: $($_.Exception.Message)"
    Exit-Script 1
}

# 配置环境变量 (.env)
$envFile = ".\.env"
if (Test-Path $envFile) {
    $editEnv = Read-Host -Prompt $MSG_ENV_DETECTED
    if ($editEnv -eq 'y') {
        Start-Process notepad $envFile
        Write-Host "请在 Notepad 中编辑 .env 文件，保存并关闭后按 Enter 继续..."
        Read-Host | Out-Null
    }
}

# 启动应用
$startNow = Read-Host -Prompt $MSG_START_APP_PROMPT
if ($startNow -ne 'n') {
    Write-Host $MSG_STARTING_APP
    try {
        & $deployScript start -ErrorAction Stop
    } catch {
        Write-Error $MSG_ERR_APP_START_FAILED
        Write-Error "错误详情: $($_.Exception.Message)"
        Exit-Script 1
    }

    Write-Host ""
    Write-Host $MSG_APP_STARTED_SUCCESS -ForegroundColor Green
    Write-Host $MSG_APP_MGMT_INFO
    Write-Host ""

    # 获取端口信息 (简单解析 .env)
    $FRONTEND_PORT = 80 # Default
    $BACKEND_PORT = 5000 # Default
    if (Test-Path $envFile) {
        try {
            $envContent = Get-Content $envFile -Raw
            # 手动解析环境变量文件
            foreach($line in ($envContent -split "`n")) {
                $line = $line.Trim()
                if ($line -and -not $line.StartsWith('#')) {
                    $key, $value = $line -split '=', 2
                    if ($key -eq 'FRONTEND_PORT') { $FRONTEND_PORT = $value.Trim() }
                    if ($key -eq 'BACKEND_PORT') { $BACKEND_PORT = $value.Trim() }
                }
            }
        } catch {
             Write-Warning "解析 .env 文件获取端口失败: $($_.Exception.Message)"
        }
    }

    Write-Host "$MSG_FRONTEND_URL http://localhost:$FRONTEND_PORT"
    Write-Host "$MSG_BACKEND_URL http://localhost:$BACKEND_PORT"

    # 询问是否在浏览器中打开
    Write-Host ""
    $openBrowser = Read-Host -Prompt $MSG_OPEN_BROWSER_PROMPT
    if ($openBrowser -ne 'n') {
        try {
            Start-Process "http://localhost:$FRONTEND_PORT"
        } catch {
            Write-Warning "无法自动打开浏览器: $($_.Exception.Message)"
        }
    }
}

Write-Host ""
Write-Host $MSG_DEPLOY_COMPLETE
Write-Host $MSG_THANK_YOU

Exit-Script 0