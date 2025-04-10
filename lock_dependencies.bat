@echo off
echo 生成依赖锁定文件...

:: 设置变量
set VENV_NAME=wjx_venv
set REQUIREMENTS_DIR=backend\requirements

:: 激活虚拟环境
call %VENV_NAME%\Scripts\activate.bat

:: 安装pip-tools
pip install pip-tools

:: 生成锁定文件
echo 为基础依赖生成锁定文件...
pip-compile --output-file=%REQUIREMENTS_DIR%\requirements-base.lock %REQUIREMENTS_DIR%\requirements-base.txt

echo 为生产依赖生成锁定文件...
pip-compile --output-file=%REQUIREMENTS_DIR%\requirements-prod.lock %REQUIREMENTS_DIR%\requirements-prod.txt

echo 为开发依赖生成锁定文件...
pip-compile --output-file=%REQUIREMENTS_DIR%\requirements-dev.lock %REQUIREMENTS_DIR%\requirements-dev.txt

echo 为文档依赖生成锁定文件...
pip-compile --output-file=%REQUIREMENTS_DIR%\requirements-docs.lock %REQUIREMENTS_DIR%\requirements-docs.txt

echo 依赖锁定文件生成完成！ 