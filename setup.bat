@echo off
:: 问卷星自动化系统一键部署脚本
:: 作者: Ignorant-lu
:: 描述: 用于在Windows环境下快速部署问卷星自动化系统

setlocal enabledelayedexpansion
title 问卷星自动化系统一键部署

:: 颜色定义
set "CYAN=[36m"
set "GREEN=[32m"
set "YELLOW=[33m"
set "RED=[31m"
set "NC=[0m"

echo %CYAN%问卷星自动化系统一键部署脚本%NC%
echo.
echo 本脚本将帮助您快速部署问卷星自动化系统。
echo.

:: 确认是否继续
set /p confirm=是否继续部署过程？(y/N):
if /i not "%confirm%"=="y" (
    echo 已取消部署过程。
    goto :eof
)

:: 检查系统要求
echo %CYAN%正在检查系统要求...%NC%

:: 检查PowerShell
where powershell >nul 2>nul
if %errorlevel% neq 0 (
    echo %RED%错误: 未找到PowerShell%NC%
    echo 请确保您的系统安装了PowerShell。
    pause
    exit /b 1
)

:: 检查Docker
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo %RED%错误: 未找到Docker%NC%
    echo 请安装Docker Desktop，参考: https://docs.docker.com/desktop/install/windows-install/
    echo 安装完成后重新运行此脚本。
    start https://docs.docker.com/desktop/install/windows-install/
    pause
    exit /b 1
)

:: 检查Docker是否运行
docker info >nul 2>nul
if %errorlevel% neq 0 (
    echo %YELLOW%警告: Docker未运行%NC%
    echo 正在尝试启动Docker Desktop...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    echo 请等待Docker Desktop启动完成（约1分钟）...

    :: 等待Docker启动
    echo 正在等待Docker启动...
    for /l %%i in (1,1,30) do (
        timeout /t 2 >nul
        docker info >nul 2>nul
        if !errorlevel! equ 0 (
            echo %GREEN%Docker已成功启动！%NC%
            goto :docker_running
        )
        echo 等待中... %%i/30
    )

    echo %RED%错误: Docker启动超时%NC%
    echo 请手动启动Docker Desktop，然后重新运行此脚本。
    pause
    exit /b 1
)

:docker_running
echo %GREEN%系统检查通过！%NC%
echo.

:: 检查当前目录是否为项目根目录
if not exist "docker-compose.yml" (
    echo %RED%错误: 当前目录不是项目根目录%NC%
    echo 请将此脚本放在项目根目录（包含docker-compose.yml的目录）下运行。
    pause
    exit /b 1
)

:: 检查部署脚本
if not exist "deploy.ps1" (
    echo %YELLOW%未找到deploy.ps1脚本，正在创建...%NC%
    echo 请确保您复制了正确的deploy.ps1内容到项目根目录。
    pause
    exit /b 1
)

:: 设置环境
echo %CYAN%正在设置环境...%NC%
powershell -ExecutionPolicy Bypass -File .\deploy.ps1 setup

if %errorlevel% neq 0 (
    echo %RED%环境设置失败%NC%
    pause
    exit /b 1
)

:: 配置环境变量
if exist ".env" (
    echo %YELLOW%检测到.env文件，是否需要编辑？(y/N):%NC%
    set /p edit_env=
    if /i "%edit_env%"=="y" (
        notepad .env
    )
)

:: 启动应用
echo %CYAN%是否立即启动应用？(Y/n):%NC%
set /p start_now=
if /i not "%start_now%"=="n" (
    echo %CYAN%正在启动应用...%NC%
    powershell -ExecutionPolicy Bypass -File .\deploy.ps1 start

    if %errorlevel% neq 0 (
        echo %RED%应用启动失败%NC%
        pause
        exit /b 1
    )

    echo.
    echo %GREEN%应用已成功启动！%NC%
    echo 您可以通过以下方式管理应用:
    echo   - 启动: .\deploy.ps1 start
    echo   - 停止: .\deploy.ps1 stop
    echo   - 重启: .\deploy.ps1 restart
    echo   - 查看日志: .\deploy.ps1 logs
    echo.

    :: 获取端口信息
    for /f "tokens=1,* delims==" %%a in (.env) do (
        if "%%a"=="FRONTEND_PORT" set FRONTEND_PORT=%%b
        if "%%a"=="BACKEND_PORT" set BACKEND_PORT=%%b
    )

    if not defined FRONTEND_PORT set FRONTEND_PORT=80
    if not defined BACKEND_PORT set BACKEND_PORT=5000

    set FRONTEND_PORT=!FRONTEND_PORT: =!
    set BACKEND_PORT=!BACKEND_PORT: =!

    echo %YELLOW%前端访问地址: http://localhost:!FRONTEND_PORT!%NC%
    echo %YELLOW%后端API地址: http://localhost:!BACKEND_PORT!%NC%

    :: 询问是否在浏览器中打开
    echo.
    echo %CYAN%是否在浏览器中打开前端页面？(Y/n):%NC%
    set /p open_browser=
    if /i not "%open_browser%"=="n" (
        start http://localhost:!FRONTEND_PORT!
    )
)

echo.
echo %GREEN%部署过程已完成！%NC%
echo 感谢使用问卷星自动化系统。

pause