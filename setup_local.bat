@echo off
:: 问卷星自动化系统本地部署一键式脚本
:: 作者: Ignorant-lu
:: 描述: 用于在Windows环境下快速部署问卷星自动化系统（本地直接运行版）
:: 版本: 1.0

setlocal enabledelayedexpansion
title 问卷星自动化系统本地部署

:: 颜色定义
set "CYAN=[36m"
set "GREEN=[32m"
set "YELLOW=[33m"
set "RED=[31m"
set "BLUE=[34m"
set "MAGENTA=[35m"
set "NC=[0m"

echo %CYAN%=======================================================%NC%
echo %CYAN%        问卷星自动化系统本地部署一键式脚本 v1.0           %NC%
echo %CYAN%=======================================================%NC%
echo.
echo %BLUE%本脚本将帮助您在本地环境中直接运行问卷星自动化系统，无需Docker。%NC%
echo %BLUE%适合开发者或不想使用Docker的用户。%NC%
echo.
echo %YELLOW%部署过程将执行以下操作：%NC%
echo  - 检查系统环境和必要组件
echo  - 创建Python虚拟环境
echo  - 安装后端和前端依赖
echo  - 配置环境变量
echo  - 启动应用服务
echo.

:: 确认是否继续
set /p confirm=是否继续部署过程？(y/N): 
if /i not "%confirm%"=="y" (
    echo %YELLOW%已取消部署过程。%NC%
    goto :eof
)

:: 检查系统要求
echo %CYAN%正在检查系统要求...%NC%
echo %MAGENTA%[步骤 1/5] 检查必要组件...%NC%

:: 检查Python
echo  - 检查Python...
python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo %RED%错误: 未找到Python%NC%
    echo %YELLOW%请安装Python 3.9或更高版本: https://www.python.org/downloads/%NC%
    start https://www.python.org/downloads/
    pause
    exit /b 1
) else (
    for /f "tokens=2" %%a in ('python --version 2^>^&1') do set "python_version=%%a"
    echo %GREEN%  ✔ Python !python_version! 已安装%NC%
)

:: 检查pip
echo  - 检查pip...
pip --version >nul 2>nul
if %errorlevel% neq 0 (
    echo %RED%错误: 未找到pip%NC%
    echo %YELLOW%请确保pip已安装，通常随Python一起安装%NC%
    pause
    exit /b 1
) else (
    echo %GREEN%  ✔ pip已安装%NC%
)

:: 检查Node.js
echo  - 检查Node.js...
node --version >nul 2>nul
if %errorlevel% neq 0 (
    echo %RED%错误: 未找到Node.js%NC%
    echo %YELLOW%请安装Node.js 16或更高版本: https://nodejs.org/%NC%
    start https://nodejs.org/
    pause
    exit /b 1
) else (
    for /f "tokens=1" %%a in ('node --version') do set "node_version=%%a"
    echo %GREEN%  ✔ Node.js !node_version! 已安装%NC%
)

:: 检查npm
echo  - 检查npm...
npm --version >nul 2>nul
if %errorlevel% neq 0 (
    echo %RED%错误: 未找到npm%NC%
    echo %YELLOW%请确保npm已安装，通常随Node.js一起安装%NC%
    pause
    exit /b 1
) else (
    for /f "tokens=1" %%a in ('npm --version') do set "npm_version=%%a"
    echo %GREEN%  ✔ npm !npm_version! 已安装%NC%
)

echo %GREEN%系统检查通过！%NC%
echo.

:: 检查当前目录是否为项目根目录
echo %MAGENTA%[步骤 2/5] 检查项目环境...%NC%
echo  - 检查项目文件...

if not exist "backend" (
    echo %RED%错误: 当前目录不是项目根目录%NC%
    echo %YELLOW%请将此脚本放在项目根目录（包含backend和frontend目录的目录）下运行。%NC%
    pause
    exit /b 1
) else (
    echo %GREEN%  ✔ 项目文件检查通过%NC%
)

:: 创建Python虚拟环境
echo %MAGENTA%[步骤 3/5] 创建Python虚拟环境...%NC%

if exist "venv" (
    echo %YELLOW%检测到已存在的虚拟环境，是否重新创建？(y/N):%NC%
    set /p recreate_venv=
    if /i "%recreate_venv%"=="y" (
        echo %CYAN%正在删除旧的虚拟环境...%NC%
        rmdir /s /q venv
        echo %CYAN%正在创建新的虚拟环境...%NC%
        python -m venv venv
        echo %GREEN%  ✔ 虚拟环境已重新创建%NC%
    ) else (
        echo %GREEN%  ✔ 使用现有虚拟环境%NC%
    )
) else (
    echo %CYAN%正在创建虚拟环境...%NC%
    python -m venv venv
    echo %GREEN%  ✔ 虚拟环境已创建%NC%
)

:: 安装后端依赖
echo %MAGENTA%[步骤 4/5] 安装依赖...%NC%
echo  - 安装后端依赖...

call venv\Scripts\activate.bat
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo %RED%错误: 安装后端依赖失败%NC%
    pause
    exit /b 1
) else (
    echo %GREEN%  ✔ 后端依赖安装完成%NC%
)

:: 安装前端依赖
echo  - 安装前端依赖...
cd frontend
npm install
if %errorlevel% neq 0 (
    echo %RED%错误: 安装前端依赖失败%NC%
    cd ..
    pause
    exit /b 1
) else (
    echo %GREEN%  ✔ 前端依赖安装完成%NC%
    cd ..
)

:: 配置环境变量
echo %MAGENTA%[步骤 5/5] 配置环境变量...%NC%

if exist ".env" (
    echo %YELLOW%检测到.env文件，是否需要编辑？(y/N):%NC%
    set /p edit_env=
    if /i "%edit_env%"=="y" (
        echo %CYAN%正在打开.env文件进行编辑...%NC%
        notepad .env
        echo %GREEN%  ✔ 环境变量已编辑%NC%
    ) else (
        echo %GREEN%  ✔ 使用现有环境变量%NC%
    )
) else (
    echo %CYAN%未找到.env文件，正在创建...%NC%
    copy .env.example .env
    if %errorlevel% neq 0 (
        echo %YELLOW%未找到.env.example文件，创建默认.env文件...%NC%
        (
            echo # LLM API配置
            echo LLM_PROVIDER=openai
            echo LLM_API_KEY=your_api_key_here
            echo LLM_MODEL=gpt-3.5-turbo
            echo.
            echo # 环境配置
            echo FLASK_ENV=development
            echo LOG_LEVEL=DEBUG
            echo.
            echo # 端口配置
            echo BACKEND_PORT=5000
            echo FRONTEND_PORT=8080
        ) > .env
    )
    echo %YELLOW%请编辑.env文件设置您的API密钥和其他配置%NC%
    notepad .env
    echo %GREEN%  ✔ 环境变量已配置%NC%
)

echo.
echo %CYAN%=======================================================%NC%
echo %GREEN%✓✓✓ 本地环境配置完成！✓✓✓%NC%
echo %CYAN%=======================================================%NC%
echo.

:: 询问是否启动应用
echo %CYAN%是否立即启动应用？(Y/n):%NC%
set /p start_now=
if /i not "%start_now%"=="n" (
    echo %CYAN%正在启动应用...%NC%
    echo %YELLOW%这将打开两个新的命令行窗口，分别运行前端和后端服务%NC%
    
    :: 启动后端
    start cmd /k "title 问卷星自动化系统-后端 & echo 正在启动后端服务... & call venv\Scripts\activate.bat & cd backend & python app.py"
    
    :: 启动前端
    start cmd /k "title 问卷星自动化系统-前端 & echo 正在启动前端服务... & cd frontend & npm run serve"
    
    echo %GREEN%  ✔ 应用已启动%NC%
    
    :: 获取端口信息
    for /f "tokens=1,* delims==" %%a in (.env) do (
        if "%%a"=="FRONTEND_PORT" set FRONTEND_PORT=%%b
        if "%%a"=="BACKEND_PORT" set BACKEND_PORT=%%b
    )
    
    if not defined FRONTEND_PORT set FRONTEND_PORT=8080
    if not defined BACKEND_PORT set BACKEND_PORT=5000
    
    set FRONTEND_PORT=!FRONTEND_PORT: =!
    set BACKEND_PORT=!BACKEND_PORT: =!
    
    echo %MAGENTA%应用访问地址:%NC%
    echo %GREEN%  ✔ 前端界面: %YELLOW%http://localhost:!FRONTEND_PORT!%NC%
    echo %GREEN%  ✔ 后端API: %YELLOW%http://localhost:!BACKEND_PORT!%NC%
    
    :: 询问是否在浏览器中打开
    echo.
    echo %CYAN%是否在浏览器中打开前端页面？(Y/n):%NC%
    set /p open_browser=
    if /i not "%open_browser%"=="n" (
        echo %CYAN%正在打开浏览器...%NC%
        timeout /t 5 >nul
        start http://localhost:!FRONTEND_PORT!
        echo %GREEN%  ✔ 浏览器已打开%NC%
    )
) else (
    echo %YELLOW%已跳过应用启动。您可以稍后手动启动应用：%NC%
    echo  1. 启动后端: 打开命令行，运行以下命令
    echo     call venv\Scripts\activate.bat
    echo     cd backend
    echo     python app.py
    echo.
    echo  2. 启动前端: 在另一个命令行窗口，运行以下命令
    echo     cd frontend
    echo     npm run serve
)

echo.
echo %BLUE%感谢使用问卷星自动化系统。如需帮助，请参考文档或联系支持团队。%NC%
echo %YELLOW%快速入门指南请参考项目根目录下的QUICK_START.md文件。%NC%
echo.

pause
