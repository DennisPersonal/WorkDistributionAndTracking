# Work Distribution and Tracking System

一个基于Flask的工作分配与跟踪系统。

## 功能特性

- ✅ 用户认证与权限管理
- ✅ 工作任务的创建、分配与跟踪
- ✅ 进度监控与报告生成
- ✅ 团队协作与通信
- ✅ 数据可视化与分析

## 技术栈

- **后端**: Python 3.9+ with Flask
- **前端**: HTML5, CSS3, JavaScript
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **模板引擎**: Jinja2
- **ORM**: SQLAlchemy
- **认证**: Flask-Login

## 快速开始

### 1. 环境设置
```bash
# 克隆仓库
git clone https://github.com/yourusername/WorkDistributionAndTracking.git
cd WorkDistributionAndTracking

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements/base.txt
pip install -r requirements/dev.txt
```

### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件设置你的配置
```

### 3. 初始化数据库
```bash
python scripts/setup_db.py
```

### 4. 运行开发服务器
```bash
python run.py
```
访问 http://localhost:5000

## 项目结构

```
WorkDistributionAndTracking/
├── src/                    # 源代码
├── tests/                  # 测试文件
├── docs/                   # 文档
├── scripts/                # 工具脚本
├── requirements/           # Python依赖
└── .github/               # GitHub工作流
```

## 开发指南

### 代码风格
- 使用 Black 进行代码格式化
- 使用 isort 进行导入排序
- 遵循 PEP 8 规范

### 测试
```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_models.py

# 生成测试覆盖率报告
pytest --cov=src
```

### 数据库迁移
```bash
# 创建迁移
flask db migrate -m "迁移描述"

# 应用迁移
flask db upgrade
```

## 部署

### 生产环境
1. 设置生产环境变量
2. 使用 Gunicorn 或 uWSGI
3. 配置 Nginx 反向代理
4. 设置 PostgreSQL 数据库

### Docker 部署
```bash
docker build -t work-tracking .
docker run -p 5000:5000 work-tracking
```

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 联系方式

- 项目维护者: [你的名字]
- 问题反馈: [GitHub Issues](https://github.com/yourusername/WorkDistributionAndTracking/issues)