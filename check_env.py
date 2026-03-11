#!/usr/bin/env python3
"""检查开发环境配置"""

import os
import sys
import subprocess
import platform

def print_header(text):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_success(text):
    """打印成功信息"""
    print(f"✅ {text}")

def print_warning(text):
    """打印警告信息"""
    print(f"⚠️  {text}")

def print_error(text):
    """打印错误信息"""
    print(f"❌ {text}")

def check_python_version():
    """检查Python版本"""
    print_header("Python环境检查")
    
    version = sys.version_info
    print(f"Python版本: {sys.version.split()[0]}")
    
    if version.major == 3 and version.minor >= 9:
        print_success("Python版本符合要求 (3.9+)")
        return True
    else:
        print_error("Python版本过低，需要3.9或更高版本")
        return False

def check_virtual_environment():
    """检查虚拟环境"""
    print_header("虚拟环境检查")
    
    in_venv = sys.prefix != sys.base_prefix
    if in_venv:
        print_success(f"在虚拟环境中: {sys.prefix}")
        return True
    else:
        print_warning("不在虚拟环境中")
        print("建议激活虚拟环境: source venv/bin/activate")
        return False

def check_dependencies():
    """检查依赖包"""
    print_header("依赖包检查")
    
    required_packages = [
        ("flask", "2.3.0"),
        ("flask_sqlalchemy", "3.0.0"),
        ("flask_login", "0.6.0"),
        ("flask_wtf", "1.1.0"),
        ("sqlalchemy", "2.0.0"),
        ("werkzeug", "2.3.0"),
        ("jinja2", "3.1.0"),
        ("wtforms", "3.0.0"),
        ("bcrypt", "4.0.0"),
        ("python_dotenv", "1.0.0"),
    ]
    
    all_installed = True
    for package, min_version in required_packages:
        try:
            module = __import__(package.replace("-", "_"))
            version = getattr(module, "__version__", "未知")
            
            # 简单版本检查
            if version != "未知":
                print_success(f"{package}: {version}")
            else:
                print_success(f"{package}: 已安装")
                
        except ImportError:
            print_error(f"{package}: 未安装")
            all_installed = False
    
    return all_installed

def check_project_structure():
    """检查项目结构"""
    print_header("项目结构检查")
    
    required_files = [
        "run.py",
        "src/config.py",
        "src/app/__init__.py",
        "src/app/models.py",
        "src/app/routes.py",
        "src/app/auth.py",
        "src/app/forms.py",
        ".env",
        "requirements/base.txt",
    ]
    
    required_dirs = [
        "src/app/static/css",
        "src/app/templates",
        "tests",
    ]
    
    all_ok = True
    
    for file in required_files:
        if os.path.exists(file):
            print_success(f"{file}")
        else:
            print_error(f"{file} - 缺失")
            all_ok = False
    
    for directory in required_dirs:
        if os.path.isdir(directory):
            print_success(f"{directory}/")
        else:
            print_error(f"{directory}/ - 缺失")
            all_ok = False
    
    return all_ok

def check_database():
    """检查数据库配置"""
    print_header("数据库配置检查")
    
    env_file = ".env"
    if os.path.exists(env_file):
        print_success(f"环境文件存在: {env_file}")
        
        with open(env_file, 'r') as f:
            content = f.read()
            
        if "DATABASE_URL" in content:
            print_success("数据库URL已配置")
        else:
            print_warning("数据库URL未配置")
            
        if "SECRET_KEY" in content and "dev-secret-key" not in content:
            print_success("密钥已配置")
        else:
            print_warning("请更新SECRET_KEY")
    else:
        print_error("环境文件缺失")
        return False
    
    return True

def check_git():
    """检查Git配置"""
    print_header("Git配置检查")
    
    try:
        # 检查Git仓库
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print_success("Git仓库已初始化")
            
            # 检查远程仓库
            result = subprocess.run(
                ["git", "remote", "-v"],
                capture_output=True,
                text=True
            )
            
            if "origin" in result.stdout:
                print_success("远程仓库已配置")
            else:
                print_warning("远程仓库未配置")
                
            return True
        else:
            print_warning("不在Git仓库中")
            return False
            
    except FileNotFoundError:
        print_error("Git未安装")
        return False

def main():
    """主函数"""
    print_header("Work Distribution and Tracking System - 环境检查")
    print(f"系统: {platform.system()} {platform.release()}")
    print(f"时间: {subprocess.check_output(['date']).decode().strip()}")
    
    checks = [
        ("Python版本", check_python_version()),
        ("虚拟环境", check_virtual_environment()),
        ("依赖包", check_dependencies()),
        ("项目结构", check_project_structure()),
        ("数据库配置", check_database()),
        ("Git配置", check_git()),
    ]
    
    print_header("检查结果汇总")
    
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    
    for name, result in checks:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\n通过: {passed}/{total}")
    
    if passed == total:
        print_success("所有检查通过！可以开始开发。")
        print("\n🚀 启动命令:")
        print("  python run.py")
        print("  或")
        print("  ./develop.sh start")
        return 0
    else:
        print_warning("有些检查未通过，请修复后再继续。")
        print("\n🔧 修复建议:")
        print("  1. 安装依赖: pip install -r requirements/base.txt")
        print("  2. 激活虚拟环境: source venv/bin/activate")
        print("  3. 检查缺失的文件")
        return 1

if __name__ == "__main__":
    sys.exit(main())