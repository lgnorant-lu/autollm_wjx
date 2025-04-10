@echo off
echo 创建问卷星自动化系统的Python虚拟环境...

:: 设置变量
set VENV_NAME=wjx_venv
set REQUIREMENTS_FILE=requirements.txt

:: 检查Python是否已安装
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python未安装，请先安装Python 3.9或更高版本。
    exit /b 1
)

:: 创建虚拟环境
if not exist %VENV_NAME% (
    echo 创建虚拟环境: %VENV_NAME%
    python -m venv %VENV_NAME%
) else (
    echo 虚拟环境已存在: %VENV_NAME%
)

:: 激活虚拟环境并安装依赖
echo 安装依赖...
call %VENV_NAME%\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r backend\%REQUIREMENTS_FILE%

:: 根据环境变量决定是否安装开发依赖
if "%DEV_MODE%"=="1" (
    echo 安装开发依赖...
    python -m pip install -r backend\requirements\requirements-dev.txt
)

:: 安装文档生成依赖（如需要）
if "%DOCS_MODE%"=="1" (
    echo 安装文档生成依赖...
    python -m pip install -r backend\requirements\requirements-docs.txt
)

echo.
echo 虚拟环境设置完成！
echo 要激活虚拟环境，请运行: call %VENV_NAME%\Scripts\activate.bat
echo.

exit /b 0 