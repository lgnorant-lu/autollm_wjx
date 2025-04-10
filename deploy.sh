#!/bin/bash

# 问卷星自动化系统部署脚本
# 作者: Ignorant-lu
# 描述: 用于部署和管理问卷星自动化系统的脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 提供脚本说明
print_usage() {
    echo -e "${BLUE}问卷星自动化系统部署脚本${NC}"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  setup       - 初始设置环境和配置"
    echo "  start       - 启动应用服务"
    echo "  stop        - 停止应用服务"
    echo "  restart     - 重启应用服务"
    echo "  logs        - 查看应用日志"
    echo "  status      - 查看应用状态"
    echo "  update      - 更新应用(拉取最新代码并重建)"
    echo "  backup      - 备份数据"
    echo "  restore     - 恢复数据"
    echo "  prune       - 清理未使用的资源(镜像、容器、卷)"
    echo ""
    echo "示例:"
    echo "  $0 setup"
    echo "  $0 start"
    echo "  $0 logs backend"
    echo ""
}

# 检查必要的命令
check_requirements() {
    echo -e "${BLUE}检查系统要求...${NC}"
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}错误: Docker未安装${NC}"
        echo "请参考 https://docs.docker.com/get-docker/ 安装Docker"
        exit 1
    fi
    
    # 检查Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${YELLOW}警告: Docker Compose未找到, 尝试使用Docker Compose插件...${NC}"
        if ! docker compose version &> /dev/null; then
            echo -e "${RED}错误: Docker Compose未安装${NC}"
            echo "请参考 https://docs.docker.com/compose/install/ 安装Docker Compose"
            exit 1
        else
            echo -e "${GREEN}Docker Compose插件已安装${NC}"
            # 使用别名以便后续统一使用docker-compose命令
            alias docker-compose="docker compose"
        fi
    fi
    
    echo -e "${GREEN}系统要求检查通过${NC}"
}

# 初始设置环境
setup() {
    echo -e "${BLUE}设置环境...${NC}"
    
    # 检查.env文件是否存在
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            echo -e "${YELLOW}未找到.env文件, 从.env.example创建${NC}"
            cp .env.example .env
            echo -e "${YELLOW}请编辑.env文件配置环境变量${NC}"
            echo -e "${YELLOW}编辑完成后重新运行 $0 setup${NC}"
            exit 0
        else
            echo -e "${RED}错误: 未找到.env.example文件${NC}"
            exit 1
        fi
    fi
    
    # 创建必要的目录
    mkdir -p ./logs/backend
    mkdir -p ./logs/frontend
    mkdir -p ./data/backend
    
    # 设置目录权限
    chmod -R 755 ./logs
    chmod -R 755 ./data
    
    echo -e "${GREEN}环境设置完成${NC}"
    echo -e "${YELLOW}现在可以使用 $0 start 启动应用${NC}"
}

# 启动应用
start() {
    echo -e "${BLUE}启动应用...${NC}"
    
    # 检查环境模式
    source .env 2>/dev/null || true
    ENV_MODE=${ENV_MODE:-production}
    
    # 根据环境模式启动
    if [ "$ENV_MODE" = "development" ]; then
        echo -e "${YELLOW}以开发模式启动...${NC}"
        docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
    else
        echo -e "${GREEN}以生产模式启动...${NC}"
        docker-compose up -d
    fi
    
    echo -e "${GREEN}应用启动成功${NC}"
    echo -e "${YELLOW}前端访问地址: http://localhost:${FRONTEND_PORT:-80}${NC}"
    echo -e "${YELLOW}后端API地址: http://localhost:${BACKEND_PORT:-5000}${NC}"
}

# 停止应用
stop() {
    echo -e "${BLUE}停止应用...${NC}"
    docker-compose down
    echo -e "${GREEN}应用已停止${NC}"
}

# 重启应用
restart() {
    echo -e "${BLUE}重启应用...${NC}"
    stop
    start
    echo -e "${GREEN}应用已重启${NC}"
}

# 查看应用日志
logs() {
    local service=$1
    
    if [ -z "$service" ]; then
        echo -e "${BLUE}查看所有服务日志...${NC}"
        docker-compose logs --tail=100 -f
    else
        echo -e "${BLUE}查看 $service 服务日志...${NC}"
        docker-compose logs --tail=100 -f $service
    fi
}

# 查看应用状态
status() {
    echo -e "${BLUE}应用状态...${NC}"
    docker-compose ps
    echo ""
    echo -e "${BLUE}资源使用情况...${NC}"
    docker stats --no-stream $(docker-compose ps -q)
}

# 更新应用
update() {
    echo -e "${BLUE}更新应用...${NC}"
    
    # 备份当前数据
    echo -e "${YELLOW}备份当前数据...${NC}"
    backup
    
    # 拉取最新代码
    echo -e "${YELLOW}拉取最新代码...${NC}"
    git pull
    
    # 重建并重启
    echo -e "${YELLOW}重建容器...${NC}"
    docker-compose build
    
    # 重启应用
    restart
    
    echo -e "${GREEN}应用更新完成${NC}"
}

# 备份数据
backup() {
    echo -e "${BLUE}备份数据...${NC}"
    
    # 创建备份目录
    BACKUP_DIR="./backups"
    BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).tar.gz"
    mkdir -p $BACKUP_DIR
    
    # 备份数据目录
    echo -e "${YELLOW}备份数据目录...${NC}"
    tar -czf $BACKUP_FILE ./data ./logs .env
    
    echo -e "${GREEN}数据备份完成: $BACKUP_FILE${NC}"
}

# 恢复数据
restore() {
    local backup_file=$1
    
    if [ -z "$backup_file" ]; then
        echo -e "${RED}错误: 请指定要恢复的备份文件${NC}"
        echo "用法: $0 restore ./backups/backup_20250328_142500.tar.gz"
        exit 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        echo -e "${RED}错误: 备份文件 $backup_file 不存在${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}恢复数据...${NC}"
    
    # 停止应用
    stop
    
    # 备份当前数据(以防万一)
    echo -e "${YELLOW}备份当前数据...${NC}"
    backup
    
    # 恢复数据
    echo -e "${YELLOW}恢复数据从 $backup_file ...${NC}"
    tar -xzf $backup_file
    
    # 重启应用
    start
    
    echo -e "${GREEN}数据恢复完成${NC}"
}

# 清理资源
prune() {
    echo -e "${BLUE}清理未使用的资源...${NC}"
    
    echo -e "${YELLOW}清理未使用的容器...${NC}"
    docker container prune -f
    
    echo -e "${YELLOW}清理未使用的镜像...${NC}"
    docker image prune -f
    
    echo -e "${YELLOW}清理未使用的网络...${NC}"
    docker network prune -f
    
    echo -e "${YELLOW}清理未使用的卷...${NC}"
    # 注意: 卷包含数据，不强制清理
    docker volume prune
    
    echo -e "${GREEN}资源清理完成${NC}"
}

# 主函数
main() {
    local command=$1
    local arg=$2
    
    # 如果没有命令参数，显示使用说明
    if [ -z "$command" ]; then
        print_usage
        exit 0
    fi
    
    # 检查系统要求
    check_requirements
    
    # 根据命令执行相应的操作
    case $command in
        setup)
            setup
            ;;
        start)
            start
            ;;
        stop)
            stop
            ;;
        restart)
            restart
            ;;
        logs)
            logs $arg
            ;;
        status)
            status
            ;;
        update)
            update
            ;;
        backup)
            backup
            ;;
        restore)
            restore $arg
            ;;
        prune)
            prune
            ;;
        *)
            echo -e "${RED}错误: 未知命令 $command${NC}"
            print_usage
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@" 