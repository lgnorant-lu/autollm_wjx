#!/bin/bash
# 问卷星自动化系统GitHub更新脚本
# 作者: Ignorant-lu
# 描述: 用于从GitHub拉取最新更新并应用到本地
# 版本: 1.0

# 颜色定义
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${CYAN}=======================================================${NC}"
echo -e "${CYAN}        问卷星自动化系统GitHub更新脚本 v1.0           ${NC}"
echo -e "${CYAN}=======================================================${NC}"
echo
echo -e "${BLUE}本脚本将帮助您从GitHub拉取最新更新并应用到本地。${NC}"
echo
echo -e "${YELLOW}更新过程将执行以下操作：${NC}"
echo " - 检查Git是否已安装"
echo " - 检查远程仓库配置"
echo " - 拉取最新更新"
echo " - 合并更新到本地"
echo

# 确认是否继续
read -p "是否继续更新过程？(y/N): " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}已取消更新过程。${NC}"
    exit 0
fi

# 检查Git是否已安装
echo -e "${CYAN}正在检查系统要求...${NC}"
echo -e "${MAGENTA}[步骤 1/4] 检查Git...${NC}"

if ! command -v git &> /dev/null; then
    echo -e "${RED}错误: 未找到Git${NC}"
    echo -e "${YELLOW}请安装Git: https://git-scm.com/downloads${NC}"
    exit 1
else
    echo -e "${GREEN}  ✔ Git已安装${NC}"
fi

# 检查远程仓库配置
echo -e "${MAGENTA}[步骤 2/4] 检查远程仓库配置...${NC}"

if ! git remote | grep -q "origin"; then
    echo -e "${YELLOW}未找到远程仓库配置，正在添加...${NC}"
    if ! git remote add origin https://github.com/lgnorant-lu/autollm_wjx.git; then
        echo -e "${RED}错误: 无法添加远程仓库${NC}"
        exit 1
    else
        echo -e "${GREEN}  ✔ 远程仓库已添加${NC}"
    fi
else
    echo -e "${GREEN}  ✔ 远程仓库已配置${NC}"
fi

# 保存当前分支名称
current_branch=$(git rev-parse --abbrev-ref HEAD)
echo -e "${CYAN}当前分支: ${current_branch}${NC}"

# 拉取最新更新
echo -e "${MAGENTA}[步骤 3/4] 拉取最新更新...${NC}"

echo -e "${CYAN}正在从GitHub拉取最新更新...${NC}"
if ! git fetch origin; then
    echo -e "${RED}错误: 无法从GitHub拉取更新${NC}"
    echo -e "${YELLOW}可能是网络问题或GitHub访问受限${NC}"
    exit 1
else
    echo -e "${GREEN}  ✔ 已成功拉取最新更新${NC}"
fi

# 合并更新
echo -e "${MAGENTA}[步骤 4/4] 合并更新...${NC}"

# 检查是否有本地修改
stashed=0
if ! git diff --quiet; then
    echo -e "${YELLOW}检测到本地有未提交的修改。${NC}"
    echo -e "${YELLOW}请选择处理方式：${NC}"
    echo " 1. 保存修改并继续更新（推荐）"
    echo " 2. 丢弃修改并继续更新"
    echo " 3. 取消更新"
    
    read -p "请输入选项(1/2/3): " choice
    
    if [ "$choice" = "1" ]; then
        echo -e "${CYAN}正在保存本地修改...${NC}"
        if ! git stash; then
            echo -e "${RED}错误: 无法保存本地修改${NC}"
            exit 1
        else
            echo -e "${GREEN}  ✔ 本地修改已保存${NC}"
            stashed=1
        fi
    elif [ "$choice" = "2" ]; then
        echo -e "${CYAN}正在丢弃本地修改...${NC}"
        if ! git reset --hard; then
            echo -e "${RED}错误: 无法丢弃本地修改${NC}"
            exit 1
        else
            echo -e "${GREEN}  ✔ 本地修改已丢弃${NC}"
        fi
    else
        echo -e "${YELLOW}已取消更新过程。${NC}"
        exit 0
    fi
fi

# 合并远程更新
echo -e "${CYAN}正在合并更新...${NC}"
if ! git merge origin/main; then
    echo -e "${RED}错误: 合并冲突，请手动解决冲突后继续${NC}"
    echo -e "${YELLOW}您可以使用以下命令查看冲突文件：${NC}"
    echo " git status"
    echo -e "${YELLOW}解决冲突后，使用以下命令继续：${NC}"
    echo " git add ."
    echo " git merge --continue"
    exit 1
else
    echo -e "${GREEN}  ✔ 更新已成功合并${NC}"
fi

# 如果之前有保存的修改，尝试恢复
if [ $stashed -eq 1 ]; then
    echo -e "${CYAN}正在恢复本地修改...${NC}"
    if ! git stash pop; then
        echo -e "${YELLOW}警告: 恢复本地修改时发生冲突，请手动解决${NC}"
        echo -e "${YELLOW}您的修改已保存在stash中，可以使用以下命令查看：${NC}"
        echo " git stash list"
        echo -e "${YELLOW}使用以下命令应用修改：${NC}"
        echo " git stash apply"
    else
        echo -e "${GREEN}  ✔ 本地修改已恢复${NC}"
    fi
fi

echo
echo -e "${CYAN}=======================================================${NC}"
echo -e "${GREEN}✓✓✓ 更新完成！系统已更新到最新版本 ✓✓✓${NC}"
echo -e "${CYAN}=======================================================${NC}"
echo

# 询问是否重启应用
read -p "是否需要重启应用以应用更新？(Y/n): " restart
if [[ ! "$restart" =~ ^[Nn]$ ]]; then
    if [ -f "./deploy.sh" ]; then
        echo -e "${CYAN}正在重启应用...${NC}"
        bash ./deploy.sh restart
        echo -e "${GREEN}  ✔ 应用已重启${NC}"
    else
        echo -e "${YELLOW}未找到deploy.sh脚本，请手动重启应用${NC}"
    fi
fi

echo
echo -e "${BLUE}感谢使用问卷星自动化系统。如需帮助，请参考文档或联系支持团队。${NC}"
echo

read -p "按Enter键继续..."
