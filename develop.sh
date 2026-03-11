#!/bin/bash

# 开发环境启动脚本
# 使用方法: ./develop.sh [command]
# 命令: start | stop | test | shell | deps | clean

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Work Distribution and Tracking System ${NC}"
    echo -e "${BLUE}========================================${NC}"
}

check_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        echo -e "${RED}错误: 虚拟环境不存在${NC}"
        echo "请先运行: python3 -m venv venv"
        exit 1
    fi
    
    if [ -z "$VIRTUAL_ENV" ]; then
        echo -e "${YELLOW}提示: 虚拟环境未激活${NC}"
        echo "正在激活虚拟环境..."
        source "$VENV_DIR/bin/activate"
        if [ $? -ne 0 ]; then
            echo -e "${RED}错误: 无法激活虚拟环境${NC}"
            exit 1
        fi
        echo -e "${GREEN}虚拟环境已激活${NC}"
    fi
}

start_dev() {
    print_header
    check_venv
    
    echo -e "${GREEN}启动开发服务器...${NC}"
    echo -e "访问: ${YELLOW}http://localhost:5001${NC}"
    echo -e "管理员账户: ${YELLOW}admin / admin123${NC}"
    echo -e "按 Ctrl+C 停止服务器"
    echo ""
    
    python run.py
}

stop_dev() {
    echo -e "${YELLOW}停止开发服务器...${NC}"
    pkill -f "python run.py" 2>/dev/null || true
    echo -e "${GREEN}服务器已停止${NC}"
}

run_tests() {
    print_header
    check_venv
    
    echo -e "${GREEN}运行测试...${NC}"
    pytest tests/ -v --cov=src --cov-report=term-missing
}

open_shell() {
    check_venv
    
    echo -e "${GREEN}打开Flask shell...${NC}"
    export FLASK_APP=run.py
    export FLASK_ENV=development
    flask shell
}

install_deps() {
    print_header
    
    if [ ! -d "$VENV_DIR" ]; then
        echo -e "${GREEN}创建虚拟环境...${NC}"
        python3 -m venv venv
    fi
    
    check_venv
    
    echo -e "${GREEN}安装依赖...${NC}"
    pip install --upgrade pip
    pip install -r requirements/base.txt
    pip install -r requirements/dev.txt
    
    echo -e "${GREEN}依赖安装完成${NC}"
}

setup_db() {
    check_venv
    
    echo -e "${GREEN}初始化数据库...${NC}"
    python scripts/init_system.py
}

init_system() {
    check_venv
    
    echo -e "${GREEN}初始化完整系统...${NC}"
    python scripts/init_system.py
}

clean_env() {
    echo -e "${YELLOW}清理环境...${NC}"
    
    # 停止服务器
    stop_dev
    
    # 删除虚拟环境
    if [ -d "$VENV_DIR" ]; then
        echo -e "${YELLOW}删除虚拟环境...${NC}"
        rm -rf "$VENV_DIR"
    fi
    
    # 删除数据库文件
    if [ -f "work_tracking.db" ]; then
        echo -e "${YELLOW}删除数据库文件...${NC}"
        rm -f work_tracking.db
    fi
    
    # 删除上传目录
    if [ -d "uploads" ]; then
        echo -e "${YELLOW}删除上传文件...${NC}"
        rm -rf uploads
    fi
    
    # 删除Python缓存
    echo -e "${YELLOW}清理Python缓存...${NC}"
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    
    echo -e "${GREEN}环境清理完成${NC}"
}

show_help() {
    print_header
    echo -e "使用方法: ${GREEN}./develop.sh [command]${NC}"
    echo ""
    echo -e "可用命令:"
    echo -e "  ${YELLOW}start${NC}    - 启动开发服务器"
    echo -e "  ${YELLOW}stop${NC}     - 停止开发服务器"
    echo -e "  ${YELLOW}test${NC}     - 运行测试"
    echo -e "  ${YELLOW}shell${NC}    - 打开Flask shell"
    echo -e "  ${YELLOW}deps${NC}     - 安装依赖"
    echo -e "  ${YELLOW}db${NC}       - 初始化数据库"
    echo -e "  ${YELLOW}init${NC}     - 初始化完整系统"
    echo -e "  ${YELLOW}clean${NC}    - 清理开发环境"
    echo -e "  ${YELLOW}help${NC}     - 显示帮助信息"
    echo ""
    echo -e "示例:"
    echo -e "  ${GREEN}./develop.sh deps${NC}   # 安装依赖"
    echo -e "  ${GREEN}./develop.sh db${NC}     # 初始化数据库"
    echo -e "  ${GREEN}./develop.sh start${NC}  # 启动服务器"
}

# 主逻辑
case "${1:-help}" in
    start)
        start_dev
        ;;
    stop)
        stop_dev
        ;;
    test)
        run_tests
        ;;
    shell)
        open_shell
        ;;
    deps)
        install_deps
        ;;
    db)
        setup_db
        ;;
    init)
        init_system
        ;;
    clean)
        clean_env
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}未知命令: $1${NC}"
        show_help
        exit 1
        ;;
esac