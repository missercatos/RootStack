# Git 与 GitHub 终端操作指南

## 1 安装 Git

| 平台 | 命令 |
|------|------|
| Debian/Ubuntu | `sudo apt update && sudo apt install git` |
| Arch Linux | `sudo pacman -S git` |
| Fedora | `sudo dnf install git` |
| macOS (Homebrew) | `brew install git` |
| Windows (winget) | `winget install Git.Git` |
| Windows (手动) | 下载 https://git-scm.com/download/win |

安装后验证：

```bash
git --version
```

> 推荐使用终端原生 Git。Windows 用户安装时选择 "Git from the command line and also from 3rd-party software" 并选 "Use native Windows Secure Channel library"。

---

## 2 初始配置

```bash
# 必设：用户名和邮箱（显示在 commit 中）
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# 推荐设置
git config --global init.defaultBranch main
git config --global core.editor "vim"     # 或 nano / code --wait
git config --global pull.rebase true      # pull 默认用 rebase

# 查看配置
git config --list
```

---

## 3 基础操作

```bash
# 初始化新仓库
mkdir my-project && cd my-project
git init

# 克隆现有仓库
git clone https://github.com/用户名/仓库名.git
git clone git@github.com:用户名/仓库名.git   # SSH 方式（无需输密码）

# 查看状态
git status                # 简洁模式: git status -s

# 暂存与提交
git add file.md           # 暂存单个文件
git add .                 # 暂存所有变更
git add -p                # 交互式分段暂存

git commit -m "feat: 添加xxx功能"
git commit -am "fix: 修复xxx"   # 跳过 add，仅对已跟踪文件有效

# 查看历史
git log                   # 完整日志
git log --oneline         # 一行一条
git log --oneline --graph # 带分支图
git log -5                # 最近 5 条

# 查看变更
git diff                  # 工作区 vs 暂存区
git diff --staged         # 暂存区 vs 上次 commit
git diff HEAD~1           # 与上一条 commit 对比

# 撤销操作
git restore file.md       # 丢弃工作区修改
git restore --staged file # 取消暂存
git commit --amend        # 修改上次 commit 信息或内容
git reset HEAD~1          # 撤销上次 commit，保留修改
git reset --hard HEAD~1   # 彻底撤销（慎用，无法恢复）
```

---

## 4 分支管理

```bash
# 查看分支
git branch                # 本地分支
git branch -a             # 所有分支（含远程）

# 新建与切换
git branch feature-x      # 新建分支
git checkout feature-x    # 切换
git switch feature-x      # 新语法，切换
git switch -c feature-x   # 新建并切换

# 合并
git switch main
git merge feature-x       # 将 feature-x 合并到 main

# 变基（rebase）—— 保持线性历史
git switch feature-x
git rebase main           # 将 feature-x 的基移动到 main 顶端

# 合并 vs 变基
# merge: 产生合并节点，保留真实分支历史
# rebase: 线性历史，更整洁但改写 commit hash

# 删除分支
git branch -d feature-x           # 删除本地（已合并）
git branch -D feature-x           # 强制删除（未合并也删）
git push origin --delete feature-x # 删除远程分支

# 解决冲突
# 合并冲突时，编辑冲突文件 → 去掉 <<<< / ==== / >>>> → 保存
git add . && git commit           # 合并后提交
# rebase 冲突时: 解决冲突 → git add . → git rebase --continue
```

---

## 5 远程仓库

```bash
# 查看远程
git remote -v

# 添加远程
git remote add origin https://github.com/用户名/仓库名.git

# 推送与拉取
git push origin main             # 推送到远程 main
git push -u origin feature-x     # 首次推送，建立跟踪
git pull                         # 拉取并合并（pull = fetch + merge）
git fetch                        # 仅拉取，不合并

# 多远程（常用于 Fork）
git remote add upstream https://github.com/原作者/仓库名.git
git fetch upstream
git merge upstream/main          # 从上游合并更新

# 查看远程分支
git branch -r
git checkout -b local-branch origin/remote-branch
```

---

## 6 .gitignore

在仓库根目录创建 `.gitignore`，写入不需要跟踪的文件模式：

```
# 编译产物
*.o
*.exe
build/

# 系统文件
.DS_Store
Thumbs.db

# IDE 配置
.vscode/
.idea/

# 环境与依赖
.env
node_modules/
```

```bash
# .gitignore 生效的前提：文件尚未被跟踪
# 如果已经跟踪，需先删除缓存
git rm --cached 文件名
```

RootStack 推荐 `.gitignore`:

```
.DS_Store
Thumbs.db
.obsidian/workspace
*.exe
*.o
build/
temp/
```

---

## 7 Fork & PR 实战

以下是从 Fork 到提交 Pull Request 的完整流程：

```bash
# 第一步：在 GitHub 网页上 Fork 目标仓库

# 第二步：克隆自己的 Fork
git clone https://github.com/你的用户名/仓库名.git
cd 仓库名

# 第三步：添加上游仓库（用于同步原项目更新）
git remote add upstream https://github.com/原作者/仓库名.git

# 第四步：创建功能分支（永远不在 main 上改）
git checkout -b my-fix

# 第五步：修改文件并提交
# vim file.md    ← 编辑文件
git add .
git commit -m "fix: 修正xxx错误"

# 第六步：推送到自己的 Fork
git push origin my-fix

# 第七步：去 GitHub 网页
# 你的仓库页面会出现 "Compare & pull request" 按钮，点击即可

# 第八步：同步上游更新（下次贡献前做）
git checkout main
git fetch upstream
git merge upstream/main
git push origin main
```

### PR 自检清单

- [ ] commit 信息清晰，包含改动说明
- [ ] 只改了目标文件，没有混入无关修改
- [ ] 如果修改代码，已经自己测试过
- [ ] 分支名有意义（`fix/typo`, `feat/add-xxx`）

### 跨仓库 PR（Fork → 原项目）

最典型的场景：你 fork 了别人的仓库，在自己的 master 上改了代码，想向原仓库的 `clean-main` 分支提交 PR。

```bash
# 确保本地 master 与原仓库的 clean-main 同步
git remote add upstream https://github.com/原作者/仓库名.git
git fetch upstream
git checkout master
git merge upstream/clean-main

# 推送你的改动到自己的 fork
git push origin master

# 用 gh 发起 PR（指定目标仓库、目标分支、来源分支）
gh pr create \
  --repo 原作者/仓库名 \
  --base clean-main \
  --head 你的用户名:master \
  --title "PR 标题" \
  --body "描述改动内容"
```

关键参数：

| 参数 | 含义 | 示例 |
|------|------|------|
| `--repo` | PR 要提交到的目标仓库（原项目） | `--repo 原作者/仓库名` |
| `--base` | 目标仓库的分支（你要合并到哪） | `--base clean-main` |
| `--head` | 你的 fork 和分支（`你的用户名:分支名`） | `--head 你的用户名:master` |

---

## 8 作为仓库主人：审查与合并 PR

```bash
# 查看所有 PR 列表
gh pr list

# 在终端查看某个 PR 的改动
gh pr view 42                           # 查看 PR #42
gh pr checkout 42                        # 切换到 PR 分支本地审查
git fetch origin pull/42/head:pr-42
git checkout pr-42

# 审查后合并
git checkout main
git merge pr-42                         # 方式一：命令行合并
git push origin main

# 或使用 gh 合并
gh pr merge 42 --merge                  # merge 方式
gh pr merge 42 --squash                 # squash 方式（压成一条 commit）
gh pr merge 42 --rebase                 # rebase 方式

# 关闭 PR（不合并）
gh pr close 42

# 撤销已合并的 PR（git revert）
# 如果合并后发现问题，用 revert 创建一个"反 commit"来撤销，而非 reset
git revert -m 1 <merge-commit的hash>
# -m 1 表示保留主分支，撤销合并进来的内容
# 推荐用 revert 而非 reset，因为 revert 不改写历史，多人协作更安全

# 在原仓库网页版也可以直接点 "Merge pull request"
```

### 三种合并方式

| 方式 | 命令 | 历史 |
|------|------|------|
| Merge commit | `gh pr merge --merge` | 保留所有 commit，加一个 merge 节点 |
| Squash | `gh pr merge --squash` | 所有 commit 压成一条 |
| Rebase | `gh pr merge --rebase` | 线性合并，不产生 merge 节点 |

---

## 9 GitHub CLI (gh)

`gh` 是 GitHub 官方命令行工具，覆盖从 Issue 到 PR 到 Actions 的完整操作。

```bash
# 安装
# Linux: https://github.com/cli/cli/blob/trunk/docs/install_linux.md
sudo apt install gh          # Debian/Ubuntu
sudo pacman -S github-cli    # Arch
brew install gh              # macOS
winget install GitHub.cli    # Windows

# 登录
gh auth login                # 按提示选择浏览器登录或 token 登录

# Issue 操作
gh issue list
gh issue create
gh issue view 42

# PR 操作
gh pr list
gh pr create                 # 交互式创建 PR
gh pr create --title "xxx" --body "yyy"
gh pr checkout 42
gh pr review 42 --approve
gh pr merge 42

# 仓库操作
gh repo view
gh repo clone 用户名/仓库名
gh fork                      # 命令行 fork 当前仓库

# 查看 CI 状态
gh run list
gh run watch
```

---

## 10 常见问题

### Q: 提交时发现漏了一个文件怎么办？

```bash
git add 漏掉的文件
git commit --amend --no-edit    # 合并到上一个 commit
# 如果已推送，需加 --force-with-lease
git push --force-with-lease
```

### Q: 如何撤销最近一次推送？

```bash
git reset --hard HEAD~1
git push --force-with-lease origin main
# 警告：如果其他人已拉取此分支，不要 force push
```

### Q: 提交信息写错了？

```bash
git commit --amend -m "新的正确信息"
```

### Q: 冲突了怎么办？

冲突标记格式：

```
<<<<<<< HEAD
当前分支的内容
=======
合并进来的内容
>>>>>>> feature-x
```

1. 手动编辑文件，保留你想要的版本，删掉 `<<<<<`、`=====`、`>>>>>`
2. 保存文件
3. `git add .`
4. `git commit`

### Q: 不小心在 main 分支改了代码怎么办？

```bash
# 把 main 上的改动搬到新分支
git switch -c feature-x
git switch main
git reset --hard origin/main    # 把 main 重置到远程状态
```

### Q: 如何撤回暂存区的文件？

```bash
git restore --staged file.md
```

### Q: 想扔掉所有未提交的修改？

```bash
git restore .                  # 丢弃工作区所有修改
git clean -fd                  # 删除未跟踪的文件和目录
```

---

## 推荐阅读

- [Pro Git 中文版 (官方书籍)](https://git-scm.com/book/zh/v2)
- [GitHub CLI 文档](https://cli.github.com/manual/)
- [git.md 文件本身](./git.md) 就是本仓库的 Git 指南，欢迎通过 [[ISSUES|问题讨论区]] 提出改进建议
