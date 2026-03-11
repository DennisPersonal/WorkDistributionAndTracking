# Work Distribution and Tracking System - 快速开始

## 🚀 一键启动

```bash
# 进入项目目录
cd ~/Documents/WorkDistributionAndTracking

# 使用开发脚本（推荐）
./develop.sh init    # 初始化系统（创建用户、组织架构、测试数据）
./develop.sh start   # 启动开发服务器
```

## 📋 手动步骤

### 1. 设置虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# 或
venv\Scripts\activate     # Windows
```

### 2. 安装依赖
```bash
pip install -r requirements/base.txt
pip install -r requirements/dev.txt
```

### 3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，设置你的配置
# 如果需要AI功能，设置 DEEPSEEK_API_KEY
```

### 4. 初始化系统
```bash
python scripts/init_system.py
```

### 5. 启动服务器
```bash
python run.py
```

访问 http://localhost:5001

## 👥 默认用户

系统初始化后创建：
- **总监**: `director` / `director123`
- **经理1-4**: `manager1`-`manager4` / `manager1123`-`manager4123`
- **员工1-40**: `employee1`-`employee40` / `employee1123`-`employee40123`

## 🎯 核心功能

### 1. 组织架构管理
- **访问**: `/org/chart` (总监)
- **功能**: 可视化三级关系图，拖拽编辑汇报关系
- **架构**: 1总监 → 4经理 → 40员工

### 2. AI任务分析
- **访问**: `/ai/analyze` (经理/总监)
- **功能**: 输入任务描述，AI自动拆解为步骤清单
- **支持**: DeepSeek API (默认模拟模式)

### 3. 智能任务分配
- **功能**: 基于步骤数量自动分配给员工
- **算法**: 考虑工作负载均衡，避免超负荷

### 4. 多级任务视图
- **员工视图**: 今日/本周/本月任务，优先级颜色标识
- **经理视图**: 查看团队工作负载，分配任务
- **总监视图**: 整体组织统计，监控进度

### 5. 提醒系统
- **自动提醒**: 任务截止前提醒
- **手动提醒**: 经理可发送报告提醒

## 🔧 开发工具

### 开发脚本
```bash
./develop.sh start    # 启动服务器
./develop.sh stop     # 停止服务器
./develop.sh test     # 运行测试
./develop.sh shell    # 打开Flask shell
./develop.sh deps     # 安装依赖
./develop.sh init     # 初始化系统
./develop.sh clean    # 清理环境
```

### 环境检查
```bash
python check_env.py
```

## 🛠️ 技术栈

### 后端
- **框架**: Python Flask
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **ORM**: SQLAlchemy 2.0
- **AI集成**: DeepSeek API (可切换OpenAI/本地模型)

### 前端
- **UI框架**: Bootstrap 5
- **图表**: 组织架构图 (D3.js)
- **交互**: 拖拽编辑，实时更新
- **响应式**: 适配桌面和移动端

### 开发工具
- **测试**: pytest
- **代码质量**: flake8, black, isort
- **CI/CD**: GitHub Actions
- **版本控制**: Git + GitHub

## 📁 项目结构

```
WorkDistributionAndTracking/
├── src/app/                    # Flask应用
│   ├── ai_integration.py      # AI集成模块
│   ├── ai_routes.py           # AI相关路由
│   ├── organization_chart.py  # 组织架构模块
│   ├── org_routes.py          # 组织架构路由
│   ├── task_views.py          # 任务视图模块
│   ├── task_routes.py         # 任务相关路由
│   ├── models_extended.py     # 数据模型
│   └── ...                    # 其他核心文件
├── scripts/                   # 工具脚本
├── tests/                     # 测试文件
├── requirements/              # Python依赖
└── ...                       # 配置文件
```

## 🎨 界面特点

### 美观简洁
- 现代卡片式设计
- 一致的颜色主题
- 合理的留白和排版
- 响应式布局

### 用户体验
- 直观的操作界面
- 清晰的视觉反馈
- 快速的任务切换
- 实时状态更新

## 🔒 安全特性

- 本地部署，数据不外传
- 密码哈希加密存储
- 角色权限控制
- 输入验证和过滤

## 🚀 下一步

### 开始开发
1. 阅读 `PROJECT_REQUIREMENTS.md` 了解完整需求
2. 查看 `src/app/` 目录下的模块
3. 从添加新功能或修改现有功能开始

### 部署生产
1. 配置生产环境变量
2. 使用 PostgreSQL 数据库
3. 设置 Gunicorn + Nginx
4. 配置 HTTPS

## 📞 支持

- **GitHub仓库**: https://github.com/DennisPersonal/WorkDistributionAndTracking
- **问题反馈**: 在GitHub创建Issue
- **文档**: 查看项目中的 `.md` 文件

---

**现在可以开始使用系统了！** 🎉

启动服务器后，使用总监账户登录，体验完整的组织架构管理和AI任务分析功能。