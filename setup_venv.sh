#!/bin/bash
set -e

echo "创建问卷星自动化系统的Python虚拟环境..."

# 设置变量
VENV_NAME=".venv"
REQUIREMENTS_FILE="requirements.txt"

# 检查Python是否已安装
if ! command -v python3 &> /dev/null; then
    echo "Python未安装，请先安装Python 3.9或更高版本。"
    exit 1
fi

# 创建虚拟环境
if [ ! -d "$VENV_NAME" ]; then
    echo "创建虚拟环境: $VENV_NAME"
    python3 -m venv $VENV_NAME
else
    echo "虚拟环境已存在: $VENV_NAME"
fi

# 激活虚拟环境并安装依赖
echo "安装依赖..."
source $VENV_NAME/bin/activate
pip install --upgrade pip
pip install -r backend/$REQUIREMENTS_FILE

# 根据环境变量决定是否安装开发依赖
if [ "$DEV_MODE" = "1" ]; then
    echo "安装开发依赖..."
    pip install -r backend/requirements/requirements-dev.txt
fi

# 安装文档生成依赖（如需要）
if [ "$DOCS_MODE" = "1" ]; then
    echo "安装文档生成依赖..."
    pip install -r backend/requirements/requirements-docs.txt
fi

echo ""
echo "虚拟环境设置完成！"
echo "要激活虚拟环境，请运行: source $VENV_NAME/bin/activate"
echo ""