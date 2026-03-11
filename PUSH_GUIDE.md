# GitHub代码推送指南

## 你的仓库信息
- **用户名**: DennisPersonal
- **仓库名**: WorkDistributionAndTracking
- **仓库URL**: https://github.com/DennisPersonal/WorkDistributionAndTracking

## 推送方法选择

### 方法A: 使用GitHub CLI（最简单）
```bash
# 1. 安装GitHub CLI（如果还没安装）
brew install gh

# 2. 登录
gh auth login
# 选择：GitHub.com → HTTPS → 在浏览器中登录

# 3. 推送代码
cd ~/Documents/WorkDistributionAndTracking
git push -u origin main
```

### 方法B: 使用Personal Access Token
```bash
# 1. 生成Token（一次性）：
#    访问：https://github.com/settings/tokens
#    点击 "Generate new token (classic)"
#    权限选择：repo (全部)
#    生成并复制Token

# 2. 推送时使用Token作为密码
cd ~/Documents/WorkDistributionAndTracking
git push -u origin main
# 用户名：DennisPersonal
# 密码：粘贴你的Token
```

### 方法C: 创建SSH密钥（最安全）
```bash
# 1. 生成SSH密钥
ssh-keygen -t ed25519 -C "your_email@example.com"
# 按Enter接受默认位置
# 可以设置密码（可选）

# 2. 将公钥添加到GitHub
cat ~/.ssh/id_ed25519.pub
# 复制输出的内容

# 3. 在GitHub添加SSH密钥：
#    访问：https://github.com/settings/keys
#    点击 "New SSH key"
#    粘贴公钥内容

# 4. 更新远程仓库URL为SSH
cd ~/Documents/WorkDistributionAndTracking
git remote set-url origin git@github.com:DennisPersonal/WorkDistributionAndTracking.git

# 5. 推送代码
git push -u origin main
```

### 方法D: 使用Git Credential Manager
```bash
# 1. 配置Git使用credential helper
git config --global credential.helper osxkeychain

# 2. 推送（会提示输入凭证）
cd ~/Documents/WorkDistributionAndTracking
git push -u origin main
# 第一次会提示保存凭证
```

## 快速解决方案

### 如果你只想快速推送：
```bash
cd ~/Documents/WorkDistributionAndTracking

# 尝试使用credential helper
git config --global credential.helper osxkeychain

# 推送
git push -u origin main
# 如果提示认证，使用：
# 用户名：DennisPersonal
# 密码：你的GitHub密码 或 Personal Access Token
```

### 如果还是不行，使用完整命令：
```bash
cd ~/Documents/WorkDistributionAndTracking

# 清除现有远程配置
git remote remove origin 2>/dev/null || true

# 重新添加
git remote add origin https://github.com/DennisPersonal/WorkDistributionAndTracking.git

# 推送
git push -u origin main
```

## 验证推送成功

推送成功后：
1. 访问：https://github.com/DennisPersonal/WorkDistributionAndTracking
2. 你应该看到所有文件
3. 点击 "Actions" 标签查看CI状态
4. 点击 "commits" 查看提交历史

## 常见问题解决

### 错误：Authentication failed
```bash
# 清除保存的凭证
git credential-osxkeychain erase
host=github.com
protocol=https

# 重新尝试
git push -u origin main
```

### 错误：Permission denied
确保你有仓库的写入权限。仓库应该是公开的，并且你是所有者。

### 错误：Repository not found
检查仓库URL是否正确：
```bash
git remote -v
# 应该显示：
# origin  https://github.com/DennisPersonal/WorkDistributionAndTracking.git
```

## 完成后的操作

推送成功后：
```bash
# 创建开发分支
git checkout -b develop
git push -u origin develop

# 查看仓库状态
git log --oneline -5
git status
```

## 需要帮助？
- GitHub帮助：https://docs.github.com
- Git文档：https://git-scm.com/doc
- 在仓库中创建Issue：https://github.com/DennisPersonal/WorkDistributionAndTracking/issues