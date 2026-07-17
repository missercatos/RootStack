# GitHub 仓库设置指南

以下操作均在 `github.com` 网页端进行，不需要写代码。

---

**快速导航**（Obsidian 中可点击跳转；下同）

- [[#^nav-1|1 仓库基础设置]]
- [[#^nav-2|2 协作管理]]
- [[#^nav-3|3 分支保护]]
- [[#^nav-4|4 Issue 管理]]
- [[#^nav-5|5 Pull Request 管理]]
- [[#^nav-6|6 Releases]]
- [[#^nav-7|7 安全设置]]
- [[#^nav-8|8 Webhooks]]
- [[#^nav-9|9 其他实用设置]]
- [[#^nav-links|相关链接]]

---

<a id="nav-1"></a>
## 1 仓库基础设置 ^nav-1

进入仓库后点击顶部 **Settings** tab。

### 改名 / 改描述 / 加 Topics

| 操作 | 路径 | 说明 |
|------|------|------|
| 改仓库名 | Settings → General → Repository name | 改后旧地址自动 301 跳转 |
| 改描述 | Settings → General → Description | 显示在仓库页顶部名称下方 |
| 加标签 | 仓库页顶部齿轮图标  (齿轮图标)  或 Settings → General → Topics | 输 `c` `cpp` `algorithm` 按回车添加 |

Topics 让其他人在 GitHub Explore 搜索标签时能搜到你的仓库。

### 切换可见性

```
Settings → Danger Zone → Change visibility
→ Make public / Make private → 输入仓库名确认
```

- **Public**：任何人都能看见、clone、fork
- **Private**：只有你和 Collaborator 能看见

### 归档 / 删除

| 操作 | 位置 | 后果 |
|------|------|------|
| 归档 | Settings → Danger Zone → Archive | 仓库只读，不能发 Issue/PR |
| 删除 | Settings → Danger Zone → Delete | 不可恢复（关联的 Issues/PR/Wiki 全部丢失）|

---

<a id="nav-2"></a>
## 2 协作管理 ^nav-2

### 可见性切换（私⇄公）

```
Settings → Danger Zone → Change visibility
→ Change to public / Change to private
→ 输入仓库名确认
```

| 场景 | 操作 | 注意 |
|------|------|------|
| 个人项目想公开 | 改为 Public | 任何人都能 clone/fork，此前 Issues 不变 |
| 公开项目想私有 | 改为 Private | 已 fork 的副本不会被删除，但无法再公开访问 |

### 添加 Collaborator

进入目标仓库：

```
Settings → Collaborators → Add people
→ 输入对方 GitHub 用户名或邮箱
→ 选择权限 → Add
→ 对方会收到邀请邮件/通知，接受后即生效
```

权限三种：

| 权限 | 说明 |
|------|------|
| Read | 看代码、提 Issue、看 Discussions |
| Write | 可以 push 分支、提 PR、合并 PR |
| Admin | 所有操作，包括改仓库设置、删仓库、加人 |

**批量加人：** 如果团队超过 3 人，建议先创建 Organization（见下一节），用 Team 管理权限，而非逐个加 Collaborator。

### 创建组织 (Organization)

组织是 GitHub 上管理多人协作的标准方式，仓库归组织所有，不依赖个人账号。

**创建步骤：**

```
GitHub 右上角 + → New organization
→ 选 Free 方案（免费，无限协作）
→ 填写组织名（如 RootStack-Project，以后不可改）
→ 填写联系邮箱
→ 选择 "My personal account"（组织归属到你的账号下管理）
→ 可添加成员（可跳过，稍后在组织页加）
→ Complete setup
```

创建后你就是组织的 **Owner**（超级管理员）。

**在组织下创建新仓库：**

```
组织页 → Repositories tab → New repository
→ 填写仓库名、描述、可见性
→ 注意 Owner 已自动选的该组织名
→ Create repository
```

**给组织添加成员：**

```
组织页 → People → Invite member
→ 输入用户名或邮箱 → Invite
→ 对方接受后，你可以在 Teams 里给他分配权限
```

**Teams（推荐）：** 在组织里建 Team 可以批量管理权限：

```
组织页 → Teams → New team
→ 填 team 名（如 "core-devs"、"contributors"）
→ Add members → Add repositories（给这个 team 哪些仓库的什么权限）
→ 一个 team 的人自动获得相同权限，加人时直接加进 team 即可
```

### 转移仓库所有权（个人→组织）

把当前在你个人名下的仓库**完整转给组织**，包括 Issues、PR、Wiki、Stars 全部保留。

```
仓库页 → Settings → Danger Zone → Transfer ownership
→ 输入目标组织名（必须先创建好组织）
→ 输入仓库名确认
→ 输入 GitHub 密码确认
```

**转移后你需要做的：**

```bash
# 本地更新远程地址
git remote set-url origin https://github.com/组织名/仓库名.git

# 验证
git remote -v
```

转移后你在组织里默认还是 Admin，可以继续管理这个仓库。建议在组织里加一个 Team，把你自己和其他活跃成员放进去统一管理权限。

---

<a id="nav-3"></a>
## 3 分支保护 ^nav-3

防止有人直接 push 到 `clean-main` 破坏历史：

```
Settings → Branches → Add branch protection rule
→ Branch name pattern: clean-main
```

**推荐勾选：**

| 选项 | 作用 |
|------|------|
| Require a pull request before merging | 禁止直接 push，必须先提 PR |
| Require approvals | 至少需要 1 人 review 批准才能合并 |
| Dismiss stale pull request approvals | 新 push 后旧 approval 自动失效 |
| Require status checks to pass before merging | 需要 CI 检查通过（需要先配 Actions）|
| Do not allow bypassing the above settings | 管理员也要遵守规则 |

---

<a id="nav-4"></a>
## 4 Issue 管理 ^nav-4

### 创建 Issue

```
Issues tab → New issue
→ 写标题 + 描述（支持 Markdown）
→ 右侧 Assignees: 指派给谁
→ Labels: 加标签分类
→ Projects: 关联看板
→ Submit new issue
```

### Labels 管理

```
Issues tab → Labels → New label
```

RootStack 推荐 Labels：

| 标签 | 颜色 | 用途 |
|------|------|------|
| `bug` | 红 | 内容错误 |
| `enhancement` | 蓝 | 新内容建议 |
| `question` | 绿 | 疑问 |
| `documentation` | 灰 | 文档改进 |
| `help wanted` | 橙 | 希望社区参与 |

### Milestone（里程碑）

```
Issues tab → Milestones → New milestone
→ 填标题、截止日期、描述
→ 往 Issue 右侧 Milestone 选择某个里程碑
```

用于管理大版本（如 `v1.0` 发布前所有需要完成的 Issues）。

---

<a id="nav-5"></a>
## 5 Pull Request 管理 ^nav-5

### 网页端 PR 流程

```
仓库页 → Pull Requests tab → New pull request
→ base: clean-main（要合并到哪）
→ compare: feature-x（从哪里合并）
→ Create pull request
→ 写标题 + 描述，关联 Issue（输入 # 编号）
→ 右侧 Assignees / Reviewers / Labels / Projects
→ Create pull request
```

### 合并后的分支清理

PR 合并后在网页端会看到 **Delete branch** 按钮，点击即可删掉远程分支。

### PR 模板

在根目录创建 `.github/PULL_REQUEST_TEMPLATE.md`，每次新建 PR 会自动填充内容：

```markdown
## 描述
请简要说明改动内容。

## 关联 Issue
Fixes #(编号)

## 检查清单
- [ ] 内容经过本地验证
- [ ] 相关双链接已补充
- [ ] 代码/公式格式正确
```

---

<a id="nav-6"></a>
## 6 Releases ^nav-6

将 tag 转为一个可浏览的发布页：

```
Code tab → Releases → Draft a new release
→ Choose a tag: 选已有 tag 或输入新 tag 名创建
→ Release title: 比如 "v0.1.0 - 首个预览版"
→ Write description: 写 changelog（改动列表）
→ Attach binaries: 可选上传文件
→ Publish release
```

发布后页面会显示：
- 版本号和 tag 名
- 发布时间
- 下载（Source code zip/tar.gz）
- 如果有上传二进制附件也会列出来

---

<a id="nav-7"></a>
## 7 安全设置 ^nav-7

```
Settings → Security
```

| 功能 | 位置 | 说明 |
|------|------|------|
| Secrets | Secrets and variables → Actions | 存 API token、密码等环境变量，CI 中可用 |
| Dependabot alerts | Code security → Dependabot alerts | 自动检测依赖漏洞并告警 |
| Dependabot security updates | Code security → Dependabot security updates | 自动提 PR 修漏洞 |
| Code scanning | Code security → Code scanning | 自动扫描代码漏洞 |
| Secret scanning | Code security → Secret scanning | 检测仓库中是否暴露了密钥 |

### Actions Secrets 用途

| Secret 名 | 存什么 | 用于 |
|-----------|--------|------|
| `GITHUB_TOKEN` | 自动生成 | 仓库内 Actions 操作（push、PR）|
| `GH_TOKEN` | Personal access token | 跨仓库操作（如自动提 PR 到其他 repo）|

---

<a id="nav-8"></a>
## 8 Webhooks ^nav-8

让 GitHub 在特定事件发生时通知你的外部服务：

```
Settings → Webhooks → Add webhook
→ Payload URL: http://你的服务器/webhook
→ Content type: application/json
→ 选择触发事件: push / pull_request / issues / releases 等
→ Add webhook
```

常见场景：
- 有人 push 后自动通知 Discord/Slack 频道
- 新 release 后触发自动部署
- Issue 创建后同步到项目管理工具

---

<a id="nav-9"></a>
## 9 其他实用设置 ^nav-9

### 仓库话题 / 社交卡片

```
Settings → General → Social preview
→ 上传一张 1280×640 图片，作为仓库链接的预览图
```

### 禁止 Force Push

```
Settings → Branches → Add rule → clean-main
→ 勾选 "Deny force pushes"
```

防止有人 `git push --force` 覆盖历史。

### 默认分支

```
Settings → Branches → Default branch
→ 将 main / master 或 clean-main 设为默认
```

影响：clone 时默认拉取分支、PR 默认目标分支。

### 启用 Wiki / Projects / Discussions

```
Settings → General → Features
→ 勾选 Wikis / Issues / Projects / Discussions / Sponsorships
```

- **Wiki**：简易文档（类似小博客）
- **Projects**：看板管理（Kanban）
- **Discussions**：论坛式讨论（比 Issue 更自由）

---

<a id="nav-links"></a>
## 相关链接 ^nav-links

- [[git.md|Git 与 GitHub 终端操作指南]]
- [[ISSUES|问题讨论与贡献指南]]
- 本仓库地址：https://github.com/missercatos/RootStack
