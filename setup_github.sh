#!/bin/bash

# GitHub仓库设置脚本
# 使用方法：./setup_github.sh YOUR_GITHUB_USERNAME

set -e  # 遇到错误时退出

echo "🎯 Work Distribution and Tracking System - GitHub仓库设置"
echo "========================================================"

# 检查参数
if [ $# -eq 0 ]; then
    echo "❌ 错误：请提供GitHub用户名"
    echo "使用方法：./setup_github.sh YOUR_GITHUB_USERNAME"
    exit 1
fi

GITHUB_USERNAME=$1
REPO_NAME="WorkDistributionAndTracking"
REPO_URL="https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"

echo "📁 项目目录：$(pwd)"
echo "👤 GitHub用户名：${GITHUB_USERNAME}"
echo "📦 仓库名称：${REPO_NAME}"
echo "🔗 仓库URL：${REPO_URL}"
echo ""

# 检查是否在正确的目录
if [ ! -f "run.py" ] || [ ! -d "src" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

# 检查Git状态
echo "🔍 检查Git状态..."
if [ ! -d ".git" ]; then
    echo "❌ 错误：这不是一个Git仓库"
    exit 1
fi

# 检查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  警告：有未提交的更改"
    read -p "是否继续？(y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "操作取消"
        exit 0
    fi
fi

# 设置Git用户信息（如果还没设置）
echo "👤 配置Git用户信息..."
if [ -z "$(git config user.name)" ]; then
    git config user.name "${GITHUB_USERNAME}"
fi

if [ -z "$(git config user.email)" ]; then
    git config user.email "${GITHUB_USERNAME}@users.noreply.github.com"
fi

echo "✅ Git用户：$(git config user.name)"
echo "✅ Git邮箱：$(git config user.email)"
echo ""

# 检查远程仓库是否已存在
if git remote | grep -q origin; then
    echo "⚠️  远程仓库 'origin' 已存在"
    CURRENT_URL=$(git remote get-url origin)
    echo "当前URL：${CURRENT_URL}"
    
    if [ "${CURRENT_URL}" != "${REPO_URL}" ]; then
        read -p "是否更新远程仓库URL？(y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git remote set-url origin "${REPO_URL}"
            echo "✅ 远程仓库URL已更新"
        fi
    fi
else
    echo "🔗 添加远程仓库..."
    git remote add origin "${REPO_URL}"
    echo "✅ 远程仓库已添加"
fi

echo ""
echo "📋 请完成以下步骤："
echo "1. 访问 https://github.com/new"
echo "2. 创建仓库："
echo "   - Repository name: ${REPO_NAME}"
echo "   - Description: Work Distribution and Tracking System"
echo "   - Public repository"
echo "   - 不要初始化README、.gitignore或license"
echo "3. 创建完成后，按Enter键继续..."
read -p ""

echo ""
echo "🚀 推送代码到GitHub..."
echo "这可能需要一些时间..."

# 尝试推送
if git push -u origin main; then
    echo ""
    echo "🎉 成功！代码已推送到GitHub"
    echo ""
    echo "📊 仓库信息："
    echo "   URL: ${REPO_URL}"
    echo "   GitHub Actions: ${REPO_URL}/actions"
    echo "   Issues: ${REPO_URL}/issues"
    echo ""
    echo "🔧 下一步："
    echo "   1. 访问 ${REPO_URL} 查看代码"
    echo "   2. 点击 'Actions' 标签查看CI状态"
    echo "   3. 开始开发新功能！"
    echo ""
    echo "💡 开发命令："
    echo "   git checkout -b feature/your-feature-name"
    echo "   # 编写代码..."
    echo "   git add . && git commit -m '描述'"
    echo "   git push origin feature/your-feature-name"
else
    echo ""
    echo "❌ 推送失败"
    echo ""
    echo "🔧 可能的原因："
    echo "   1. 仓库还没创建 - 请先创建仓库"
    echo "   2. 认证问题 - 可能需要输入用户名密码"
    echo "   3. 网络问题 - 检查网络连接"
    echo ""
    echo "💡 手动推送命令："
    echo "   git push -u origin main"
    echo ""
    echo "📖 详细指南请查看 GITHUB_SETUP.md"
fi

echo ""
echo "✨ 设置完成！"