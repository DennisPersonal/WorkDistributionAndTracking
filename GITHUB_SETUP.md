# GitHub仓库设置指南 - 逐步操作

## 步骤1: 创建GitHub账户（如果还没有）

1. 访问 https://github.com/join
2. 填写：
   - 用户名 (Username)
   - 邮箱地址
   - 密码
3. 验证邮箱
4. 完成注册

## 步骤2: 在GitHub创建新仓库

1. 登录GitHub后，访问：https://github.com/new
2. 填写仓库信息：
   - **Owner**: 你的用户名
   - **Repository name**: `WorkDistributionAndTracking`
   - **Description**: `Work Distribution and Tracking System`
   - **Public** ✅ (选择公开)
   - **Initialize this repository with**: 
     - [ ] **不要勾选** "Add a README file" (我们已经有了)
     - [ ] **不要勾选** "Add .gitignore" (我们已经有了)
     - [ ] **不要勾选** "Choose a license" (我们已经有了)
3. 点击 **Create repository**

## 步骤3: 推送现有代码到GitHub

创建仓库后，你会看到以下命令。在终端中执行：

```bash
# 进入项目目录
cd ~/Documents/WorkDistributionAndTracking

# 添加远程仓库（复制GitHub页面上的URL）
git remote add origin https://github.com/YOUR_USERNAME/WorkDistributionAndTracking.git

# 推送代码到GitHub
git push -u origin main
```

## 步骤4: 验证推送成功

1. 访问你的仓库页面：
   `https://github.com/YOUR_USERNAME/WorkDistributionAndTracking`
2. 你应该看到所有文件
3. 检查提交历史

## 步骤5: 设置仓库功能

### 启用 Issues
1. 在仓库页面点击 **Settings**
2. 左侧选择 **Features**
3. 确保 **Issues** 已启用

### 设置分支保护规则（可选但推荐）
1. Settings → Branches
2. 点击 **Add branch protection rule**
3. 规则应用于：`main`
4. 启用：
   - [x] Require pull request reviews before merging
   - [x] Require status checks to pass before merging
   - [x] Require branches to be up to date before merging
5. 点击 **Create**

## 步骤6: 配置Git身份（如果还没设置）

```bash
# 设置你的Git用户名和邮箱
git config --global user.name "你的名字"
git config --global user.email "你的邮箱@example.com"

# 验证设置
git config --list | grep user
```

## 步骤7: 测试GitHub Actions

推送后，GitHub Actions会自动运行：
1. 访问仓库页面
2. 点击 **Actions** 标签页
3. 你应该看到CI工作流正在运行或已完成

## 故障排除

### 如果遇到认证问题
```bash
# 使用HTTPS（需要输入用户名和密码）
git remote set-url origin https://github.com/YOUR_USERNAME/WorkDistributionAndTracking.git

# 或使用SSH（需要设置SSH密钥）
git remote set-url origin git@github.com:YOUR_USERNAME/WorkDistributionAndTracking.git
```

### 如果提示"remote origin already exists"
```bash
# 先移除现有的远程仓库
git remote remove origin

# 然后重新添加
git remote add origin https://github.com/YOUR_USERNAME/WorkDistributionAndTracking.git
```

### 如果推送被拒绝
```bash
# 先拉取（如果是空仓库，这步不需要）
git pull origin main --allow-unrelated-histories

# 然后推送
git push -u origin main
```

## 完成后的检查清单

- [ ] GitHub仓库创建成功
- [ ] 代码推送成功
- [ ] 所有文件在GitHub上可见
- [ ] GitHub Actions工作流运行成功
- [ ] 可以访问 https://github.com/YOUR_USERNAME/WorkDistributionAndTracking

## 下一步：开始开发

仓库设置完成后，你可以：

1. **创建开发分支**
   ```bash
   git checkout -b develop
   git push -u origin develop
   ```

2. **创建功能分支**
   ```bash
   git checkout -b feature/add-task-management
   ```

3. **开始编码！**

## 有用的Git命令

```bash
# 查看状态
git status

# 查看远程仓库
git remote -v

# 查看分支
git branch -a

# 查看提交历史
git log --oneline --graph
```

## 需要帮助？

- GitHub官方文档：https://docs.github.com
- Git教程：https://git-scm.com/doc
- 项目问题：在仓库中创建Issue