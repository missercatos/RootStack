# Shell 本质：Bash 在系统中的位置 (Shell Essence: Bash's Place in the System)

## 章节概述

理解 Shell 的本质是用户与内核之间的"翻译官"。本章梳理 Shell 家族（sh/bash/zsh/dash），区分内建命令与外部命令，理解环境变量如何在父子进程间传递，以及 Shell 的进程模型。

> **核心理念**：Shell 是内核的"外衣"（shell 的字面意思），它把用户的自然语言指令翻译成内核能理解的系统调用。

---

### 第1节：什么是 Shell

Shell 是一个**命令行解释器**（command interpreter），位于操作系统内核与用户之间。

```
┌─────────────────────────────┐
│        用户输入命令          │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│         Shell 层             │
│  解析命令 → 查找程序 → 执行  │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│         内核 (Kernel)        │
│  进程管理 / 文件系统 / 设备   │
└─────────────────────────────┘
```

**Shell 的三大功能：**
1. **命令解释**：读取用户输入，解析为可执行的操作
2. **程序控制**：启动子进程执行外部程序
3. **环境管理**：维护变量、路径、别名等运行环境

---

### 第2节：Shell 家族

| Shell | 作者/组织 | 特点 | 默认位置 |
|-------|----------|------|----------|
| `sh` (Bourne Shell) | Stephen Bourne | 原始 Shell，POSIX 标准 | `/bin/sh` |
| `bash` (Bourne Again Shell) | GNU 项目 | sh 的增强版，功能丰富 | `/bin/bash` |
| `zsh` (Z Shell) | Paul Falstad | Bash 超集，macOS 默认 | `/bin/zsh` |
| `dash` | Debian 项目 | 轻量快速，Debian/Ubuntu 默认 `/bin/sh` | `/bin/dash` |
| `fish` | 用户友好项目 | 语法最友好，非 POSIX 兼容 | `/usr/bin/fish` |

```bash
# 查看当前系统使用的 shell
echo $SHELL

# 查看系统中所有可用 shell
cat /etc/shells

# 临时切换 shell
zsh        # 切换到 zsh
exit       # 返回原 shell
```

> **重要**：`/bin/sh` 在不同系统上可能是 bash、dash 或其他 shell。脚本中应明确使用 `#!/bin/bash` 或 `#!/usr/bin/env bash`。

---

### 第3节：内建命令 vs 外部命令

Shell 内建命令由 Shell 自身直接执行，无需创建子进程；外部命令需要 fork + exec。

```bash
# 内建命令示例
echo "hello"        # 内建（Bash 直接执行）
cd /tmp             # 内建（必须在当前 shell 执行）
export PATH=...     # 内建
type echo           # 显示: echo is a shell builtin
type ls             # 显示: ls is /bin/ls
```

**内建命令 vs 外部命令对比：**

| 特性 | 内建命令 | 外部命令 |
|------|----------|----------|
| 执行方式 | Shell 直接执行 | 创建子进程执行 |
| 速度 | 快（无 fork） | 较慢（需 fork+exec） |
| 环境影响 | 影响当前 Shell | 在子进程中执行 |
| 可移植性 | 依赖 Shell 实现 | 依赖系统安装 |
| 示例 | `cd`, `export`, `echo` | `ls`, `grep`, `awk` |

```bash
# 查看所有内建命令
compgen -b

# 查看某个命令是内建还是外部
type -a echo
```

---

### 第4节：环境变量传递

Shell 通过环境变量在父子进程间传递信息。

```bash
# 设置环境变量
export MY_VAR="Hello Bash"
export PATH="/usr/local/bin:$PATH"

# 子进程会继承环境变量
bash -c 'echo $MY_VAR'    # 输出: Hello Bash

# 普通变量不会传递给子进程
LOCAL_VAR="local only"
bash -c 'echo $LOCAL_VAR' # 输出为空
```

**变量作用域图：**

```
父 Shell
├── export MY_VAR="hello"    ← 环境变量
├── LOCAL="local"            ← 局部变量
│
└── 子 Shell (bash)
    ├── $MY_VAR → "hello"    ✓ 可访问
    └── $LOCAL   → ""        ✗ 不可见
```

| 变量类型 | 定义方式 | 子进程继承 | 当前 Shell |
|----------|----------|------------|------------|
| 环境变量 | `export VAR=val` | 是 | 是 |
| 局部变量 | `VAR=val` | 否 | 是 |
| `local` 变量 | `local VAR=val` | 否 | 仅函数内 |

---

### 第5节：进程模型

Bash 执行外部命令时，遵循 fork-exec 模型。

```bash
# 每个外部命令都是一个子进程
ps -f --forest
# 可以看到 bash 是 ps 的父进程

# 后台运行
sleep 100 &
echo "sleep 在后台运行，PID: $!"

# 等待后台进程
wait $!
```

**进程层次示例：**

```
terminal (PID 1000)
└── bash (PID 1001)          ← 你的 shell
    ├── vim (PID 1002)       ← 前台进程
    └── bash (PID 1003)      ← 子 shell (执行 bash script.sh)
        └── grep (PID 1004)  ← grep 是脚本的子进程
```

> **核心理解**：每个外部命令都是一个独立的进程，通过环境变量和文件描述符与父进程通信。

---

### 第6节：Shell 的执行流程

```bash
#!/usr/bin/env bash
# Shell 解析脚本的步骤:
# 1. 读取一行
# 2. 解析 (词法分析、变量替换、命令替换)
# 3. 执行 (内建直接执行，外部命令 fork+exec)
# 4. 回到步骤 1，直到文件结束

# 示例：Shell 的替换顺序
echo "Today is $(date +%Y-%m-%d)"
# $(date +%Y-%m-%d) 先被执行，结果替换到字符串中
```

**Shell 替换优先级：**

1. 命令替换 `$(cmd)` 或 `` `cmd` ``
2. 算术替换 `$((expr))`
3. 参数替换 `${var}`
4. 引号内不做替换（`'单引号'` 保持原样）

---

### 第7节：Shell 脚本 vs C 程序

| 特性 | Bash 脚本 | C 程序 |
|------|-----------|--------|
| 执行方式 | 解释执行，逐行解析 | 编译为二进制后执行 |
| 速度 | 较慢 | 快（接近硬件） |
| 类型系统 | 无类型（一切都是字符串） | 强类型 |
| 内存管理 | 自动（Shell 管理） | 手动（malloc/free） |
| 并发模型 | 进程（fork）或后台（&） | 进程/线程/协程 |
| 适用场景 | 系统管理、自动化、胶水语言 | 高性能计算、系统编程 |
| 错误处理 | 退出码 `$?` | 返回码 + errno |

```c
// C 的进程创建示例
#include <unistd.h>
int main() {
    pid_t pid = fork();
    if (pid == 0) {
        // 子进程
        execlp("ls", "ls", "-la", NULL);
    } else {
        // 父进程
        wait(NULL);
    }
    return 0;
}
```

```bash
# Bash 等效操作
ls -la &      # 后台运行（隐式 fork）
wait          # 等待完成
```

---

### 第8节：课后练习

1. 用 `type` 命令分别查看 `cd`、`ls`、`echo`、`export`、`pwd` 是内建还是外部命令
2. 编写脚本验证子进程是否能读取父进程的局部变量
3. 使用 `ps --forest` 观察执行一个简单脚本时的进程树

**相关章节：**
- [[../00_环境搭建与第一个脚本|上一章：环境搭建]]
- [[../02_变量与数据类型：字符串_整数_数组|下一章：变量与数据类型]]
