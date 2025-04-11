@echo off
:: 设置控制台代码页为UTF-8
chcp 65001 >nul

:: 启用命令扩展
verify on
setlocal enableextensions

:: 问卷星自动化系统本地部署脚本
:: 作者: Ignorant-lu
:: 版本: 2.5 - 调试版本

:: 设置标题
title 问卷星自动化系统本地部署

:: 获取脚本目录
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo ===============================================================
echo              问卷星自动化系统本地部署 v2.5
echo ===============================================================
echo.
echo 本脚本将帮助您在本地环境中部署问卷星自动化系统。
echo.
echo 部署过程包括：
echo  - 系统环境检查
echo  - Python虚拟环境配置
echo  - 依赖项安装
echo  - 环境配置
echo  - 服务启动
echo.

:: 创建临时文件用于命令输出
set "TEMP_FILE=%TEMP%\setup_output.txt"
if exist "%TEMP_FILE%" del "%TEMP_FILE%"

:: 确认是否继续
set /p confirm=是否继续部署？(y/N):
if /i not "%confirm%"=="y" (
    echo 已取消部署。
    goto :eof
)

:: 检查系统要求
echo 正在检查系统要求...
echo [步骤 1/5] 检查必要组件...

:: 检查Python
echo  - 检查Python...
python --version > "%TEMP_FILE%" 2>&1
if %errorlevel% neq 0 (
    echo 错误：未找到Python
    echo 请安装Python 3.9或更高版本：https://www.python.org/downloads/
    type "%TEMP_FILE%"
    start https://www.python.org/downloads/
    pause
    exit /b 1
)
type "%TEMP_FILE%"
echo   + Python检查通过

:: 检查pip
echo  - 检查pip...
pip --version > "%TEMP_FILE%" 2>&1
if %errorlevel% neq 0 (
    echo 错误：未找到pip
    echo 请确保pip已随Python一起安装
    type "%TEMP_FILE%"
    pause
    exit /b 1
)
type "%TEMP_FILE%"
echo   + pip检查通过

:: 检查Node.js
echo  - 检查Node.js...
node --version > "%TEMP_FILE%" 2>&1
if %errorlevel% neq 0 (
    echo 错误：未找到Node.js
    echo 请安装Node.js 16或更高版本：https://nodejs.org/
    type "%TEMP_FILE%"
    start https://nodejs.org/
    pause
    exit /b 1
)
type "%TEMP_FILE%"
echo   + Node.js检查通过

:: 检查npm
echo  - 检查npm...
call npm --version > "%TEMP_FILE%" 2>&1
if %errorlevel% neq 0 (
    echo 错误：未找到npm
    echo 请确保npm已随Node.js一起安装
    type "%TEMP_FILE%"
    pause
    exit /b 1
)
type "%TEMP_FILE%"
echo   + npm检查通过

echo 系统检查通过！
echo.

:: 检查项目目录
echo [步骤 2/5] 检查项目环境...
echo  - 检查项目文件...

if not exist "backend" (
    echo 错误：不在项目根目录
    echo 请在项目根目录（包含backend和frontend目录的目录）下运行此脚本
    pause
    exit /b 1
)
echo   + 项目文件检查通过

:: 创建必要的目录
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "data\surveys" mkdir data\surveys
if not exist "data\tasks" mkdir data\tasks
if not exist "logs\api" mkdir logs\api
echo   + 数据目录创建完成

:: 创建Python虚拟环境
echo [步骤 3/5] 创建Python虚拟环境...

set "VENV_CREATED=0"

if exist "venv" (
    set /p "RECREATE=检测到已存在的虚拟环境，是否重新创建？(y/N): "
    if /i "%RECREATE%"=="y" (
        echo 正在删除旧的虚拟环境...
        rmdir /s /q venv
        set "VENV_CREATED=0"
    ) else (
        echo   + 使用现有虚拟环境
        set "VENV_CREATED=1"
    )
)

if "%VENV_CREATED%"=="0" (
    echo 正在创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo 错误：创建虚拟环境失败
        pause
        exit /b 1
    )
    echo   + 虚拟环境创建完成
)

:: 安装后端依赖
echo [步骤 4/5] 安装依赖...
echo  - 安装后端依赖...

call venv\Scripts\activate.bat
pip install -r backend\requirements.txt
if errorlevel 1 (
    echo 错误：安装后端依赖失败
    pause
    exit /b 1
)
echo   + 后端依赖安装完成

:: 安装前端依赖
echo  - 安装前端依赖...
cd frontend
call npm install
if errorlevel 1 (
    echo 错误：安装前端依赖失败
    cd ..
    pause
    exit /b 1
)

:: 确保安装了vite
call npm install --save-dev vite @vitejs/plugin-vue
if errorlevel 1 (
    echo 错误：安装Vite失败
    cd ..
    pause
    exit /b 1
)
echo   + 前端依赖安装完成
cd ..

:: 启动服务
echo [步骤 5/5] 启动服务...
echo  - 启动后端服务...
start "后端服务" cmd /k "call venv\Scripts\activate.bat && python backend\app.py"
echo   + 后端服务已启动

echo  - 启动前端服务...
cd frontend
start "前端服务" cmd /k "npm run dev"
cd ..
echo   + 前端服务已启动

echo.
echo ===============================================================
echo 部署完成！服务正在启动...
echo.
echo 您可以通过以下地址访问应用：
echo 前端界面：http://localhost:5173
echo 后端API：http://localhost:5000
echo.
echo 按任意键退出...
pause >nul 