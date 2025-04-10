# GitHub推送与更新指南

本指南提供了如何与GitHub仓库交互的详细步骤，包括推送本地更新到远程仓库和从远程仓库获取更新。

## 目录

- [推送本地更新到GitHub](#推送本地更新到github)
  - [方法一：使用脚本（推荐）](#方法一使用脚本推荐)
  - [方法二：手动执行命令](#方法二手动执行命令)
  - [方法三：使用GitHub Desktop](#方法三使用github-desktop)
- [从GitHub获取更新](#从github获取更新)
  - [方法一：使用一键式更新脚本（推荐）](#方法一使用一键式更新脚本推荐)
  - [方法二：手动执行命令](#方法二手动执行命令-1)
- [版本管理最佳实践](#版本管理最佳实践)
- [常见问题解决](#常见问题解决)

# 推送本地更新到GitHub

## 方法一：使用脚本（推荐）

我们已经为你准备了两个脚本，你可以根据你的操作系统选择使用：

- Windows用户：运行 `push_to_github.bat`
- Linux/Mac用户：运行 `push_to_github.sh`（可能需要先执行 `chmod +x push_to_github.sh` 赋予执行权限）

这些脚本会尝试自动完成推送过程，如果遇到身份验证问题，会提供进一步的指导。

## 方法二：手动执行命令

如果你更喜欢手动执行命令，或者脚本无法正常工作，可以按照以下步骤操作：

### 1. 添加远程仓库

```bash
# 如果已经有名为origin的远程仓库，先删除它
git remote remove origin

# 添加新的远程仓库
git remote add origin https://github.com/lgnorant-lu/autollm_wjx.git
```

### 2. 强制推送

```bash
# 强制推送本地dev分支到远程main分支
git push -f origin dev:main
```

如果遇到身份验证问题，可以尝试以下方法：

#### 使用个人访问令牌（PAT）

1. 在GitHub上创建个人访问令牌：
   - 访问 https://github.com/settings/tokens
   - 点击 "Generate new token"
   - 选择 "repo" 权限
   - 生成并复制令牌

2. 使用令牌设置远程URL：

```bash
git remote set-url origin https://[用户名]:[个人访问令牌]@github.com/lgnorant-lu/autollm_wjx.git
```

3. 再次尝试推送：

```bash
git push -f origin dev:main
```

#### 使用SSH方式

如果你已经设置了SSH密钥，可以使用SSH方式：

```bash
git remote set-url origin git@github.com:lgnorant-lu/autollm_wjx.git
git push -f origin dev:main
```

## 方法三：使用GitHub Desktop

如果你更喜欢图形界面，可以使用GitHub Desktop：

1. 安装并打开[GitHub Desktop](https://desktop.github.com/)
2. 添加本地仓库
3. 在菜单中选择 "Repository" > "Push" 并勾选 "Force push" 选项

## 验证推送结果

推送完成后，访问 https://github.com/lgnorant-lu/autollm_wjx 查看远程仓库是否已更新为本地内容。

## 注意事项

- 强制推送会**永久删除**远程仓库中的历史记录，请确保你真的想这样做
- 如果有其他人也在使用这个仓库，强制推送可能会导致他们的工作出现问题
- 推送前最好先备份远程仓库的内容，以防万一

# 从GitHub获取更新

## 方法一：使用一键式更新脚本（推荐）

我们已经为你准备了一键式更新脚本，你可以根据你的操作系统选择使用：

- Windows用户：运行 `update_from_github.bat`
- Linux/Mac用户：运行 `update_from_github.sh`（可能需要先执行 `chmod +x update_from_github.sh` 赋予执行权限）

这些脚本会自动执行以下操作：

1. 检查Git是否已安装
2. 检查远程仓库配置
3. 拉取最新更新
4. 合并更新到本地
5. 处理可能的合并冲突
6. 恢复本地修改（如果有）

脚本提供了交互式界面，会在每个步骤提供清晰的指导，并在遇到问题时提供解决方案。

## 方法二：手动执行命令

如果你更喜欢手动执行命令，或者脚本无法正常工作，可以按照以下步骤操作：

### 1. 确保远程仓库已配置

```bash
# 检查远程仓库配置
git remote -v

# 如果没有配置，添加远程仓库
git remote add origin https://github.com/lgnorant-lu/autollm_wjx.git
```

### 2. 拉取最新更新

```bash
# 拉取最新更新
git fetch origin
```

### 3. 合并更新

```bash
# 如果有本地修改，可以先保存
git stash

# 合并远程更新
git merge origin/main

# 如果之前有保存的修改，恢复它们
git stash pop
```

如果在合并过程中遇到冲突，Git会提示你解决冲突。你需要手动编辑冲突文件，然后：

```bash
# 标记冲突已解决
git add .

# 继续合并过程
git merge --continue
```

# 版本管理最佳实践

- 定期从GitHub拉取更新，保持本地代码与远程仓库同步
- 在进行重要修改前，先创建分支，完成后再合并回主分支
- 提交代码时添加清晰的提交信息，描述你所做的更改
- 避免直接在main分支上工作，尽量使用feature分支进行开发
- 使用`.gitignore`文件排除不需要版本控制的文件（如临时文件、编译产物等）

# 常见问题解决

## 身份验证失败

如果遇到身份验证问题，可以参考[推送本地更新到GitHub](#推送本地更新到github)部分的身份验证解决方案。

## 合并冲突

合并冲突通常发生在同一文件的同一部分被不同人修改时。解决步骤：

1. 使用`git status`查看冲突文件
2. 打开冲突文件，寻找`<<<<<<<`、`=======`和`>>>>>>>`标记
3. 编辑文件解决冲突，保留你想要的内容
4. 使用`git add .`标记冲突已解决
5. 使用`git merge --continue`或`git commit`完成合并

## 网络问题

如果遇到网络问题导致无法连接GitHub：

1. 检查你的网络连接
2. 尝试使用VPN或代理服务器
3. 如果使用HTTPS连接，可以尝试切换到SSH连接

## 其他问题

如果遇到其他问题，可以：

1. 查阅[GitHub官方文档](https://docs.github.com/cn)
2. 在[GitHub社区](https://github.community/)寻求帮助
3. 联系项目维护者获取支持
