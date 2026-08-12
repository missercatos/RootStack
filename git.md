# Git 与 GitHub 终端操作指南

**快速导航**（Obsidian 中可点击跳转；下同）

- [[#^nav-1|1 安装 Git]]
- [[#^nav-2|2 初始配置]]
- [[#^nav-3|3 基础操作]]
- [[#^nav-4|4 分支管理]]
- [[#^nav-5|5 远程仓库]]
- [[#^nav-6|6 .gitignore]]
- [[#^nav-7|7 Fork & PR 实战]]
- [[#^nav-8|8 审查与合并 PR]]
- [[#^nav-9|9 GitHub CLI]]
- [[#^nav-10|10 情景现场]]
- [[#^nav-11|11 常见问题]]
- [[#^nav-12|12 git stash（临时保存）]]
- [[#^nav-13|13 版本标签与发布]]
- [[#^nav-14|14 网页端操作]]
- [[#^nav-15|15 签名提交]]
- [[#^nav-16|16 子模块 (Submodule)]]
- [[#^nav-17|17 内部原理与文件存储]]
- [[#^nav-recommended|推荐阅读]]

---

<a id="nav-1"></a>
## 1 安装 Git ^nav-1

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

<a id="nav-2"></a>
## 2 初始配置 ^nav-2

```bash
# 必设：用户名和邮箱（显示在 commit 中）
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# 推荐设置
git config --global init.defaultBranch main
git config --global core.editor "vim" # 或 nano / code --wait
git config --global pull.rebase true # pull 默认用 rebase

# 查看配置
git config --list
```

---

<a id="nav-3"></a>
## 3 基础操作 ^nav-3

```bash
# 初始化新仓库
mkdir my-project && cd my-project
git init

# 克隆现有仓库
git clone https://github.com/用户名/仓库名.git
git clone git@github.com:用户名/仓库名.git # SSH 方式（无需输密码）

# 查看状态
git status # 简洁模式: git status -s

# 暂存与提交
git add file.md # 暂存单个文件
git add . # 暂存所有变更
git add -p # 交互式分段暂存

git commit -m "feat: 添加xxx功能"
git commit -am "fix: 修复xxx" # 跳过 add，仅对已跟踪文件有效

# 查看历史
git log # 完整日志
git log --oneline # 一行一条
git log --oneline --graph # 带分支图
git log -5 # 最近 5 条

# 查看变更
git diff # 工作区 vs 暂存区
git diff --staged # 暂存区 vs 上次 commit
git diff HEAD~1 # 与上一条 commit 对比

# 撤销操作
git restore file.md # 丢弃工作区修改
git restore --staged file # 取消暂存
git commit --amend # 修改上次 commit 信息或内容
git reset HEAD~1 # 撤销上次 commit，保留修改
git reset --hard HEAD~1 # 彻底撤销（慎用，无法恢复）
```

---

<a id="nav-4"></a>
## 4 分支管理 ^nav-4

```bash
# 查看分支
git branch # 本地分支
git branch -a # 所有分支（含远程）

# 新建与切换
git branch feature-x # 新建分支
git checkout feature-x # 切换
git switch feature-x # 新语法，切换
git switch -c feature-x # 新建并切换

# 合并
git switch main
git merge feature-x # 将 feature-x 合并到 main

# 变基（rebase）—— 保持线性历史
git switch feature-x
git rebase main # 将 feature-x 的基移动到 main 顶端

# 合并 vs 变基
# merge: 产生合并节点，保留真实分支历史
# rebase: 线性历史，更整洁但改写 commit hash

# 删除分支
git branch -d feature-x # 删除本地（已合并）
git branch -D feature-x # 强制删除（未合并也删）
git push origin --delete feature-x # 删除远程分支

# 解决冲突
# 合并冲突时，编辑冲突文件 → 去掉 <<<< / ==== / >>>> → 保存
git add . && git commit # 合并后提交
# rebase 冲突时: 解决冲突 → git add . → git rebase --continue
```

---

<a id="nav-5"></a>
## 5 远程仓库 ^nav-5

```bash
# 查看远程
git remote -v

# 添加远程
git remote add origin https://github.com/用户名/仓库名.git

# 推送与拉取
git push origin main # 推送到远程 main
git push -u origin feature-x # 首次推送，建立跟踪
git pull # 拉取并合并（pull = fetch + merge）
git fetch # 仅拉取，不合并

# 多远程（常用于 Fork）
git remote add upstream https://github.com/原作者/仓库名.git
git fetch upstream
git merge upstream/main # 从上游合并更新

# 查看远程分支
git branch -r
git checkout -b local-branch origin/remote-branch
```

---

<a id="nav-6"></a>
## 6 .gitignore ^nav-6

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

<a id="nav-7"></a>
## 7 Fork & PR 实战 ^nav-7

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
# vim file.md ← 编辑文件
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

<a id="nav-8"></a>
## 8 作为仓库主人：审查与合并 PR ^nav-8

```bash
# 查看所有 PR 列表
gh pr list

# 在终端查看某个 PR 的改动
gh pr view 42 # 查看 PR #42
gh pr checkout 42 # 切换到 PR 分支本地审查
git fetch origin pull/42/head:pr-42
git checkout pr-42

# 审查后合并
git checkout main
git merge pr-42 # 方式一：命令行合并
git push origin main

# 或使用 gh 合并
gh pr merge 42 --merge # merge 方式
gh pr merge 42 --squash # squash 方式（压成一条 commit）
gh pr merge 42 --rebase # rebase 方式

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

<a id="nav-9"></a>
## 9 GitHub CLI (gh) ^nav-9

`gh` 是 GitHub 官方命令行工具，覆盖从 Issue 到 PR 到 Actions 的完整操作。

```bash
# 安装
# Linux: https://github.com/cli/cli/blob/trunk/docs/install_linux.md
sudo apt install gh # Debian/Ubuntu
sudo pacman -S github-cli # Arch
brew install gh # macOS
winget install GitHub.cli # Windows

# 登录
gh auth login # 按提示选择浏览器登录或 token 登录

# Issue 操作
gh issue list
gh issue create
gh issue view 42

# PR 操作
gh pr list
gh pr create # 交互式创建 PR
gh pr create --title "xxx" --body "yyy"
gh pr checkout 42
gh pr review 42 --approve
gh pr merge 42

# 仓库操作
gh repo view
gh repo clone 用户名/仓库名
gh repo create 新仓库名 # 在当前账号下创建仓库（交互式）
gh repo create 新仓库名 --public # 直接指定公开
gh repo create 新仓库名 --private # 直接指定私有
gh repo create 组织名/新仓库名 # 在组织下创建仓库
gh repo create 新仓库名 --clone # 创建后自动 clone 到本地
gh repo create 仓库名 --public --source=. --remote=origin --push
创建新仓库并推送

# 仓库可见性切换（私→公 or 公→私）
gh repo edit --visibility public # 改为公开
gh repo edit --visibility private # 改为私有

# 邀请 Collaborator（通过 gh api）
gh api repos/用户名/仓库名/collaborators/被邀请的用户名 -X PUT
# 查看已邀请的 Collaborator
gh api repos/用户名/仓库名/collaborators

# 转移仓库到组织（通过 gh api）
gh api repos/用户名/仓库名/transfer -X POST \
 -f new_owner=组织名

# 创建组织（gh 无直接命令，通过 API 需要特殊 token）
# 推荐在网页端操作：右上角 + → New organization

gh fork # 命令行 fork 当前仓库

# 查看 CI 状态
gh run list
gh run watch
```

---

<a id="nav-10"></a>
## 10 情景现场 ^nav-10

### 场景一：参与大项目（无仓库权限，Fork + 跨仓库 PR）

你发现某个开源项目有个 bug，想修掉它。你没有该项目仓库的写入权限，所以需要 Fork。

```bash
# ---- 第 1 步：Fork ----
# 在浏览器打开 GitHub 项目页，点击右上角 Fork
# 或在终端（已安装 gh）：
gh repo clone 原作者/大项目 --fork # 自动 fork 并 clone 你的 fork

# 如果已经手动 fork，用 clone 拉自己的副本
git clone https://github.com/你的用户名/大项目.git
cd 大项目

# 添加上游仓库（原项目），用于后续同步
git remote add upstream https://github.com/原作者/大项目.git

# ---- 第 2 步：建分支 ----
git switch -c fix/login-bug
# 原则：永远不在 master/main 上直接改

# ---- 第 3 步：修改 + 测试 ----
# vim src/login.c ← 修改代码
# make test ← 本地测试通过
git diff # 确认改动正确

# ---- 第 4 步：提交 + 推送 ----
git add src/login.c
git commit -m "fix: 登录模块空指针检查异常"
git push origin fix/login-bug

# ---- 第 5 步：发起 PR ----
gh pr create \
 --repo 原作者/大项目 \
 --base clean-main \
 --head 你的用户名:fix/login-bug \
 --title "fix: 登录模块空指针检查异常" \
 --body "在特定输入下 login() 会走空指针分支，增加了 NULL 检查。"

# PR 提交后，项目维护者会看到你的 PR，审查后合并或要求修改。

# ---- 第 6 步：同步上游（下次贡献前必做） ----
git checkout main
git fetch upstream
git merge upstream/clean-main
git push origin main
```

---

### 场景二：项目参与者（有仓库权限，同仓库 PR）

你在团队项目中有一个新功能要做，你有仓库的写入权限，直接在同一仓库内操作。

```bash
# ---- 第 1 步：拉取最新代码 ----
git clone https://github.com/团队名/项目.git
cd 项目
# 或如果已 clone：git pull origin clean-main

# ---- 第 2 步：建分支 ----
git switch -c feat/user-avatar

# ---- 第 3 步：修改 + 测试 ----
# vim src/user/avatar.c
# go test ./... ← 测试通过
git status # 确认改了什么

# ---- 第 4 步：提交 + 推送 ----
git add .
git commit -m "feat: 用户头像上传功能"
git push origin feat/user-avatar

# ---- 第 5 步：发起 PR ----
# 目标分支是团队仓库的 clean-main，来源是刚才推送的 feat/user-avatar
gh pr create \
 --base clean-main \
 --head feat/user-avatar \
 --title "feat: 用户头像上传功能" \
 --body "实现了头像裁剪、压缩和 CDN 上传"

# ---- 第 6 步：审查后修改 ----
# 如果审查者要求修改
# vim src/user/avatar.c
git add .
git commit -m "fix: 根据审查意见调整压缩参数"
git push origin feat/user-avatar # PR 自动更新

# ---- 第 7 步：PR 合并后删分支 ----
git checkout clean-main
git pull origin clean-main
git branch -d feat/user-avatar
git push origin --delete feat/user-avatar
```

---

<a id="nav-11"></a>
## 11 常见问题 ^nav-11

### Q: 提交时发现漏了一个文件怎么办？

```bash
git add 漏掉的文件
git commit --amend --no-edit # 合并到上一个 commit
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
git reset --hard origin/main # 把 main 重置到远程状态
```

### Q: 如何撤回暂存区的文件？

```bash
git restore --staged file.md
```

### Q: 想扔掉所有未提交的修改？

```bash
git restore . # 丢弃工作区所有修改
git clean -fd # 删除未跟踪的文件和目录
```

---

<a id="nav-12"></a>
## 12 git stash（临时保存） ^nav-12

`git stash` 把**工作区和暂存区的改动临时收起来**（相当于存进一个"草稿箱"），让工作区回到干净状态；需要时再取回来。常用于：正在改一半、突然要切分支或修紧急 bug。

### 常用命令

```bash
git stash # 保存工作区 + 暂存区改动
git stash list # 查看 stash 列表（含 stash 的记录）
git stash apply stash@{0} # 恢复最近一次（apply 后仍保留记录）
git stash pop # 恢复并删除该条记录
git stash drop stash@{0} # 只删除某条记录，不恢复
git stash clear # 清空所有 stash
git stash show stash@{0} # 查看某条 stash 改了哪些文件
```

### 查看记录

stash 是 git 中的**特殊提交**，可以被直接查看：

```bash
# 1. 命令行视图
git stash list # WIP on master: 提交信息
git log --all --oneline # 显示包含 stash 在内的所有提交

# 2. 底层视图（stash 提交本身）
git cat-file -t refs/stash # commit（stash 本质是一个提交）
git cat-file -p refs/stash # 查看 stash 提交的完整内容
git reflog # 查看所有引用（分支、HEAD、stash）的操作记录

# 3. 恢复指定内容
git stash show -p stash@{0} # 查看 diff
git stash apply stash@{0} # 恢复
```

### stash 的底层原理

stash 不是普通分支上的提交，它有两个特殊之处：

1. **引用位置特殊**：普通提交挂在分支上（`refs/heads/master`），stash 挂在 `refs/stash` 上——所以 `git log` 默认看不到，只有 `git log --all`、`git stash list`、`git reflog` 能看到
2. **双亲提交**：普通提交有 1 个 parent，stash 有 **2 个 parent**（原分支 HEAD + 当时的暂存区快照）

```bash
# 查看 stash 的双亲结构
git cat-file -p refs/stash
# tree 8c5e8f... ← 保存的工作区内容
# parent a1b2c3d... ← 原分支 HEAD
# parent 5f9e1d2... ← 当时的暂存区状态
```

> 安全提示：`git stash drop` / `git stash clear` 会删除记录，误删后可用 `git fsck --unreachable` + `git stash apply` 找回。

---

<a id="nav-13"></a>
## 13 版本标签与发布 ^nav-13

### 语义化版本 (Semantic Versioning)

版本号格式 **MAJOR.MINOR.PATCH**，例如 `v1.2.3`：

| 位 | 称 | 说明 | 例子 |
|----|-----|------|------|
| MAJOR | 主版本 | 不兼容的 API 变更 / 重大重构 | `v1.0.0` → `v2.0.0` |
| MINOR | 次版本 | 向下兼容的新功能 / 新增内容 | `v1.0.0` → `v1.1.0` |
| PATCH | 修订号 | 向下兼容的 bug 修复 / 小修正 | `v1.0.0` → `v1.0.1` |

RootStack 是文档项目，按里程碑手动打 tag：

```bash
# 查看当前版本（最近的 tag）
git describe --tags

# 打 lightweight tag（只是一个标记）
git tag v0.1.0

# 推荐：annotated tag（包含作者、日期、信息）
git tag -a v0.1.0 -m "首个可读版本：Phase 1-12 内容就绪"

# 推送 tag 到远程（默认不会随 git push 推送）
git push origin v0.1.0 # 推送单个 tag
git push origin --tags # 推送所有本地 tag

# 列出所有 tag
git tag -l "v0.*"

# 删除 tag
git tag -d v0.1.0 # 删除本地
git push origin --delete v0.1.0 # 删除远程
```

### 网页端操作 tag（GitHub 网页）

```bash
# 1. 打开仓库 https://github.com/用户名/仓库名
# 2. 点击页面中间的 Tags（或 Releases）
# 3. 点击 "Create a new release" → "Choose a tag" → 输入新 tag 名
# 如果没有这个 tag，GitHub 会自动创建
# 4. 填写 Release title 和描述
# 5. 点击 "Publish release"
```

| 操作 | 终端命令 | 网页入口 |
| ---------- | --------------------------------------------------------------- | ------------------------------------ |
| 创建 tag | `git tag -a v0.1.0 -m "msg"` + `git push origin v0.1.0` | 仓库页 → Releases → Draft a new release |
| 查看 tag | `git tag -l` | 仓库页 → Tags |
| 删除 tag | `git tag -d v0.1.0` + `git push --delete origin v0.1.0` | Releases → 对应 release → Delete |
| 发布 Release | `gh release create v0.1.0 --title "v0.1.0" --notes "changelog"` | 创建 release 页面 → Publish release |

---

<a id="nav-14"></a>
## 14 GitHub 网页端操作 ^nav-14

### 创建仓库

1. 登录 GitHub，点击右上角 `+` → **New repository**
2. 填仓库名（例如 `my-project`），写描述
3. 选择 **Public**（公开）或 **Private**（私有）
4. 可选：初始化 README、.gitignore、license
5. 点击 **Create repository**
6. 创建后按页面提示 push 本地代码

### 仓库设置（Settings tab）

进入仓库后点顶部 **Settings**：

| 设置项 | 位置 | 说明 |
|--------|------|------|
| Repository name | Settings → General | 改仓库名 |
| Description | Settings → General | 仓库描述（显示在仓库页顶部） |
| Topics | 仓库页顶部齿轮图标 (齿轮图标) 或 Settings → General | 加标签如 `c` `cpp` `algorithm` `obsidian` |
| Visibility | Settings → Danger Zone → Change visibility | 公开/私有切换 |
| Archive | Settings → Danger Zone → Archive this repository | 归档（只读）|
| Delete | Settings → Danger Zone → Delete this repository | 删除（不可恢复）|

### 添加 Collaborator

```
Settings → Collaborators → Add people → 输入 GitHub 用户名 → Add
```

被添加的人有仓库的**写入权限**，可以 push、创建分支、合并 PR。

### 网页端 Fork + PR

```
# Fork（在自己账号下创建副本）
打开目标仓库 → 点右上角 "Fork" → Create fork

# 提交 Pull Request
自己的 Fork 仓库 → 点 "Pull Request" tab → "New pull request"
 → base repository: 原仓库 → base branch: clean-main
 → head repository: 自己的 Fork → compare branch: 自己的分支
 → Create pull request → 填写标题和描述 → Create
```

### 网页端 Issue 管理

```
仓库页 → Issues tab → New issue
 → 写标题 + 描述（支持 Markdown）
 → 右侧 Assignees: 指派给谁
 → Labels: 加标签（bug / enhancement / question）
 → Projects: 关联项目看板
 → Submit new issue
```

Issue 操作：Comment（评论）、Close（关闭）、Reopen（重新打开）、Pin（置顶）、Lock（锁定讨论）。

### 网页端 PR Review

PR 页面 → Files changed tab → 逐行浏览改动 → 点击行号前的 `+` 发表评论
→ Finish your review → 三种结果：

| 选项 | 说明 |
|------|------|
| Comment | 普通评论（不阻止合并）|
| Approve | 批准（同意合并）|
| Request changes | 要求修改（阻止合并直到解决）|

---

<a id="nav-15"></a>
## 15 签名提交 ^nav-15

### SSH key（免密推送）

SSH 方式 clone 和 push 不需要输密码：

```bash
# 检查已有 key
ls -la ~/.ssh/id_ed25519.pub

# 生成新 key
ssh-keygen -t ed25519 -C "your@email.com"
# 一路回车，可选设置 passphrase

# 查看公钥
cat ~/.ssh/id_ed25519.pub
# 复制输出内容（以 ssh-ed25519 开头）
```

添加到 GitHub（网页端）：

```
Settings → SSH and GPG keys → New SSH key
 → Title: 起个名字（比如 "我的笔记本"）
 → Key: 粘贴刚才复制的公钥
 → Add SSH key
```

之后 clone 用 SSH 地址：

```bash
git clone git@github.com:用户名/仓库名.git
```

### GPG 签名（Verified 标记）

让 commit 显示绿色的 **Verified** 徽章：

```bash
# 1. 安装 GPG
# Debian/Ubuntu
sudo apt install gnupg
# Arch
sudo pacman -S gnupg

# 2. 生成 GPG 密钥（交互式）
gpg --full-generate-key
# 选 RSA and RSA → 4096 bits → 1y（或 0 永不过期）
# 填姓名和邮箱（必须与 git config user.email 一致）
# 设置密码

# 3. 列出密钥，记下指纹（sec 行后的长串）
gpg --list-secret-keys --keyid-format LONG
# 例如 sec rsa4096/AAAAAAAAAAAAAAAA 2026-01-01
# 指纹就是 AAAAAAAAAAAAAAAA

# 4. 导出公钥
gpg --armor --export AAAAAAAAAAAAAAAA
# 复制输出（从 -----BEGIN PGP PUBLIC KEY BLOCK----- 开始）
```

添加到 GitHub（网页端）：

```
Settings → SSH and GPG keys → New GPG key
 → Key: 粘贴上面导出的公钥
 → Add GPG key
```

```bash
# 5. 配置 git 使用该密钥签名
git config --global user.signingkey AAAAAAAAAAAAAAAA
git config --global commit.gpgsign true # 默认所有 commit 签名

# 6. 签名提交
git commit -S -m "feat: 添加xxx功能" # -S 指定签名
# 或全局已启用时正常 commit 即可

# 7. 验证签名
git log --show-signature -1
```

| 认证方式 | 用途 | 设置位置 |
|---------|------|---------|
| SSH key | clone/push 免密 | Settings → SSH and GPG keys → New SSH key |
| GPG key | commit 显示 Verified | Settings → SSH and GPG keys → New GPG key |
| Personal token | API 访问 / HTTPS clone | Settings → Developer settings → Personal access tokens |

---

<a id="nav-16"></a>
## 16 子模块 (Submodule) ^nav-16

子模块允许你在一个 Git 仓库中嵌入另一个 Git 仓库的特定版本。

### 子模块的本质

子模块不是文件拷贝，而是**指针引用**——Git 记录的是目标仓库的 commit hash（模式 `160000`），而非实际文件内容：

```bash
# 查看子模块的 gitlink 条目（160000 表示子模块）
git ls-tree HEAD red_team/
# → 160000 commit a1b2c3d4... red_team
```

- GitHub 仓库页面上，子模块目录会显示 `->` 箭头（如 `red_team ->`）
- 箭头后面的 commit hash 指向被嵌入仓库的某个版本
- 子模块信息存储在仓库根目录的 `.gitmodules` 文件中

### 添加子模块

```bash
git submodule add https://github.com/用户名/外部仓库.git 本地目录名
```

执行后：
1. 创建 `.gitmodules` 文件（记录子模块路径和 URL）
2. 在 Git 索引中添加一个 `160000` 类型的 gitlink 条目
3. 自动 clone 外部仓库到指定目录

### 克隆包含子模块的仓库

```bash
# 方式一：克隆时一并拉取子模块
git clone --recursive https://github.com/用户名/仓库名.git

# 方式二：已克隆后初始化子模块
git clone https://github.com/用户名/仓库名.git
cd 仓库名
git submodule update --init # 拉取所有子模块
git submodule update --init --recursive # 嵌套子模块也拉取
```

如果没有 `--recursive` 或不执行 `submodule update`，子模块目录在本地就是空的。

### 更新子模块到最新版本

```bash
# 进入子模块目录，拉取最新
cd 子模块目录
git pull origin main
cd ..

# 提交更新后的子模块指针
git add 子模块目录
git commit -m "chore: 更新子模块到最新"
```

### 子模块解耦为普通文件

当不需要子模块的独立性（如想直接在父仓库中管理内容）时，将子模块转为普通文件：

```bash
# 1. 删除子模块的 gitlink（从索引移除，保留工作区文件）
git rm --cached 子模块目录

# 2. 删除 .gitmodules 中的对应条目（如果不再需要任何子模块）
# rm .gitmodules

# 3. 删除子模块元数据
rm -rf .git/modules/子模块目录

# 4. 将实际文件添加到父仓库
git add 子模块目录
git commit -m "子模块解耦为普通文件"
```

执行后，GitHub 上的 `->` 箭头消失，clone 也能直接拉下全部文件。

### 删除子模块

```bash
# 1. 从索引和 .gitmodules 移除
git submodule deinit -f 子模块目录
# 2. 从文件系统删除
rm -rf 子模块目录
# 3. 从 Git 跟踪中移除
git rm -f 子模块目录
# 4. 提交
git commit -m "移除子模块"
```

### 子模块常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| 克隆后子模块目录是空的 | 未执行 `submodule update --init` | 执行 `git submodule update --init --recursive` |
| 子模块在 GitHub 上显示 `->` 箭头 | 子模块是 git link，不是普通文件 | 执行解耦操作（见上） |
| 修改了子模块内容但父仓库不认 | 需要在子模块目录内先 commit | 进入子模块目录 `git add && git commit`，再回父仓库 `git add && git commit` |
| 子模块 detached HEAD | 子模块默认处于分离头指针状态 | 进入子模块目录 `git checkout main` |

---

<a id="nav-17"></a>
## 17 内部原理与文件存储 ^nav-17

理解 `.git` 目录和对象模型，是排查问题、手动恢复数据（如被删除的文件/提交）的基础，也是安全测试中"git 信息泄露"类漏洞的核心原理。

### .git 目录结构

| 路径 | 作用 |
|------|------|
| `.git/HEAD` | 当前所在分支的指针，内容形如 `ref: refs/heads/master` |
| `.git/refs/heads/` | 本地分支引用（每个文件内容是对应提交的 40 位 sha1） |
| `.git/refs/tags/` | 标签引用 |
| `.git/refs/stash` | stash 引用（`git stash` 时创建，普通分支提交不会出现） |
| `.git/objects/` | 对象数据库（commit/tree/blob/tag 四种对象） |
| `.git/objects/xx/yyy...` | 松散对象：sha1 前 2 位作目录名，后 38 位作文件名，内容经 zlib 压缩 |
| `.git/logs/HEAD` | HEAD 操作日志（reflog），记录每次提交/回退/切换 |
| `.git/logs/refs/` | 各引用的操作日志 |
| `.git/index` | 暂存区索引（记录已 `git add` 的文件） |
| `.git/config` | 仓库级配置 |

### 对象模型：commit → tree → blob

git 的所有数据都是对象，通过 sha1 引用：

```
commit（一个版本快照）
 └─ tree（目录快照）
 ├─ tree（子目录）
 └─ blob（文件内容）
```

| 对象 | 对应内容 | 示例 |
|------|---------|------|
| `blob` | 文件内容 | `git cat-file -p 1d7bc08` → 显示文件内容 |
| `tree` | 目录条目（文件名 + 对象 sha1） | `git ls-tree HEAD` |
| `commit` | 一个提交（tree + parent + 作者/提交者信息） | `git cat-file -p HEAD` |
| `tag` | 带注释的标签 | `git cat-file -p v1.0` |

### 查看对象的命令

```bash
git cat-file -t <sha1> # 查看对象类型（blob/tree/commit/tag）
git cat-file -p <sha1> # 查看对象内容（p = pretty）
git cat-file -s <sha1> # 查看对象大小
git ls-tree HEAD # 查看 HEAD 的目录树
git ls-tree -r HEAD # 递归列出所有文件
git rev-parse HEAD # 把名字解析成 sha1
git rev-list --all --objects # 列出所有提交涉及的所有对象（含历史被删的）
git fsck --unreachable # 找不可达对象（被删除的提交/文件）
```

### 手动读取松散对象（不借助 git 命令）

松散对象 = `zlib 压缩 + "类型 大小\x00内容"` 的明文前缀。可用脚本直接还原：

```bash
python3 - <<'PY'
import zlib
with open("objects/1d/7bc08b84173edb1a7be8e03ca7ad92a5861cff", "rb") as f:
 data = zlib.decompress(f.read())
print(data[:4]) # 类型：blob / tree / commit
print(data[data.find(b"\x00")+1:]) # 去掉 "blob 20\0" 头，得到内容
PY
```

### 查看记录（reflog 与日志）

```bash
git log --all --oneline # 所有分支 + stash 的提交
git log --oneline HEAD~3..HEAD # 最近 3 条
git reflog # 所有"引用移动"记录（含已 reset/已删分支的旧提交）
git reflog show refs/stash # 查看 stash 引用的操作记录
```

> `git reflog` 是找回"手滑 reset 丢掉的提交"的关键：`git reflog` 找到旧 sha1 后 `git checkout <sha1>` 或 `git branch 新分支 <sha1>` 即可恢复。

## 推荐阅读 ^nav-recommended

- [Pro Git 中文版 (官方书籍)](https://git-scm.com/book/zh/v2)
- [GitHub CLI 文档](https://cli.github.com/manual/)
- [[red_team/ctf_trea/Web/信息泄露/Git泄露/Git泄露|Git泄露考点精讲]] -- git 信息泄露考点（.git 目录泄露源码）
- [[red_team/ctf_trea/Web/信息泄露/Git泄露/Stash|Stash 变式考点]] -- flag 被 git stash 藏进 refs/stash 的考题
- [git.md 文件本身](./git.md) 就是本仓库的 Git 指南，欢迎通过 [[ISSUES|问题讨论区]] 提出改进建议
