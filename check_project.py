#!/usr/bin/env python3
"""检查项目结构完整性"""

import os
import sys

def check_project_structure():
    """检查项目结构"""
    print("🔍 检查 Work Distribution and Tracking System 项目结构")
    print("=" * 60)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    required_files = [
        "README.md",
        "run.py",
        "src/config.py",
        "src/app/__init__.py",
        "src/app/models.py",
        "src/app/routes.py",
        "src/app/auth.py",
        "src/app/forms.py",
        "requirements/base.txt",
        ".gitignore",
        ".env.example",
        "scripts/setup_db.py"
    ]
    
    required_dirs = [
        "src/app/static/css",
        "src/app/static/js",
        "src/app/static/images",
        "src/app/templates",
        "tests",
        "docs",
        ".github/workflows"
    ]
    
    print("\n📁 检查必需文件:")
    all_files_ok = True
    for file in required_files:
        path = os.path.join(base_dir, file)
        if os.path.exists(path):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - 缺失")
            all_files_ok = False
    
    print("\n📁 检查必需目录:")
    all_dirs_ok = True
    for directory in required_dirs:
        path = os.path.join(base_dir, directory)
        if os.path.isdir(path):
            print(f"  ✅ {directory}/")
        else:
            print(f"  ❌ {directory}/ - 缺失")
            all_dirs_ok = False
    
    print("\n📊 检查Git仓库:")
    git_dir = os.path.join(base_dir, ".git")
    if os.path.isdir(git_dir):
        print("  ✅ Git仓库已初始化")
        
        # 检查是否有提交
        import subprocess
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "-1"],
                cwd=base_dir,
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                print("  ✅ 已有Git提交")
            else:
                print("  ⚠️  还没有Git提交")
        except:
            print("  ⚠️  无法检查Git提交")
    else:
        print("  ❌ Git仓库未初始化")
    
    print("\n🐍 检查Python环境:")
    try:
        import flask
        print(f"  ✅ Flask已安装: {flask.__version__}")
    except ImportError:
        print("  ❌ Flask未安装")
    
    try:
        import sqlalchemy
        print(f"  ✅ SQLAlchemy已安装: {sqlalchemy.__version__}")
    except ImportError:
        print("  ❌ SQLAlchemy未安装")
    
    print("\n" + "=" * 60)
    
    if all_files_ok and all_dirs_ok:
        print("🎉 项目结构完整！可以开始开发。")
        print("\n🚀 下一步建议:")
        print("  1. 创建GitHub仓库: ./setup_github.sh YOUR_USERNAME")
        print("  2. 设置虚拟环境: python3 -m venv venv")
        print("  3. 安装依赖: pip install -r requirements/base.txt")
        print("  4. 初始化数据库: python scripts/setup_db.py")
        print("  5. 运行应用: python run.py")
        return 0
    else:
        print("⚠️  项目结构不完整，请检查缺失的文件/目录。")
        return 1

if __name__ == "__main__":
    sys.exit(check_project_structure())