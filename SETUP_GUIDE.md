# Work Distribution and Tracking System - 设置指南

## 项目已成功创建！

你的Flask项目已经创建在：`~/Documents/WorkDistributionAndTracking/`

## 1. 项目结构概览

```
WorkDistributionAndTracking/
├── src/                    # 源代码
│   ├── app/               # Flask应用
│   │   ├── static/        # 静态文件 (CSS, JS, 图片)
│   │   ├── templates/     # HTML模板
│   │   ├── __init__.py    # 应用工厂
│   │   ├── models.py      # 数据模型
│   │   ├── routes.py      # 主路由
│   │   ├── auth.py        # 认证路由
│   │   └── forms.py       # 表单定义
│   └── config.py          # 配置文件
├── requirements/          # Python依赖
├── scripts/              # 工具脚本
├── tests/                # 测试文件
├── docs/                 # 文档
├── .github/              # GitHub工作流
└── 各种配置文件
```

## 2. 快速开始

### 步骤1: 设置Python虚拟环境
```bash
cd ~/Documents/WorkDistributionAndTracking
python -m venv venv
source venv/bin/activate  # Mac/Linux
# 或
venv\Scripts\activate     # Windows
```

### 步骤2: 安装依赖
```bash
pip install -r requirements/base.txt
pip install -r requirements/dev.txt
```

### 步骤3: 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，设置 SECRET_KEY 等
```

### 步骤4: 初始化数据库
```bash
python scripts/setup_db.py
```

### 步骤5: 运行开发服务器
```bash
python run.py
```

访问 http://localhost:5001

## 3. 默认登录凭证

运行 `scripts/setup_db.py` 后创建的用户：
- **管理员**: username=`admin`, password=`admin123`
- **用户1**: username=`user1`, password=`user1123`
- **用户2**: username=`user2`, password=`user2123`
- **用户3**: username=`user3`, password=`user3123`

## 4. 设置GitHub仓库

### 选项A: 使用GitHub CLI (推荐)
1. 安装GitHub CLI: `brew install gh`
2. 登录: `gh auth login`
3. 创建仓库: `gh repo create WorkDistributionAndTracking --public --source=. --remote=origin --push`

### 选项B: 手动创建
1. 访问 https://github.com/new
2. 仓库名称: `WorkDistributionAndTracking`
3. 描述: "Work Distribution and Tracking System"
4. 选择: Public
5. 不要初始化README (我们已经有了)
6. 创建后，按照提示推送现有代码

### 选项C: 使用网页界面
```bash
# 添加远程仓库
git remote add origin https://github.com/YOUR_USERNAME/WorkDistributionAndTracking.git

# 推送代码
git push -u origin main
```

## 5. 开发工作流

### 创建新功能分支
```bash
git checkout -b feature/your-feature-name
```

### 提交更改
```bash
git add .
git commit -m "描述你的更改"
git push origin feature/your-feature-name
```

### 创建Pull Request
1. 在GitHub上创建Pull Request
2. 等待CI测试通过
3. 请求代码审查
4. 合并到main分支

## 6. 版本控制策略

### 分支结构
- `main`: 生产就绪代码
- `develop`: 开发集成分支
- `feature/*`: 功能开发
- `bugfix/*`: 问题修复
- `release/*`: 发布准备

### 版本标签
```bash
# 创建版本标签
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## 7. 下一步开发任务

### 高优先级
1. 完善任务管理界面
2. 添加项目CRUD功能
3. 实现用户权限系统
4. 添加数据可视化图表

### 中优先级
1. 实现文件上传功能
2. 添加电子邮件通知
3. 创建REST API
4. 添加搜索功能

### 低优先级
1. 多语言支持
2. 主题切换
3. 移动应用
4. 第三方集成

## 8. 有用的命令

### 开发
```bash
# 运行测试
pytest

# 代码格式化
black src/
isort src/

# 代码检查
flake8 src/
pylint src/
```

### 数据库
```bash
# 重置数据库
python scripts/setup_db.py

# 使用Flask shell
flask shell
```

### 部署
```bash
# 生产环境运行
gunicorn -w 4 -b 0.0.0.0:5001 run:app

# Docker构建
docker build -t work-tracking .
```

## 9. 获取帮助

- 查看 `docs/` 目录中的文档
- 检查 `README.md` 获取最新信息
- 使用 `flask routes` 查看所有路由
- 访问 http://localhost:5001/help (开发中)

## 10. 贡献指南

1. Fork仓库
2. 创建功能分支
3. 编写测试
4. 确保代码通过所有检查
5. 提交Pull Request

---

**项目已准备好开始开发！** 🚀

开始编码前，请先设置GitHub仓库以启用版本跟踪。