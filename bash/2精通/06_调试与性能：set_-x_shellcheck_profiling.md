# 调试与性能：set -x、shellcheck、profiling（Debugging & Performance: set -x, shellcheck, profiling）

## 章节概述

本章系统讲解 Bash 脚本的调试技术、静态分析、性能分析与优化策略。涵盖 `set` 选项、`bash -n` 语法检查、`shellcheck` 静态分析、`time` 性能计时，以及避免子 shell 和管道的性能优化技巧，并与 C 语言调试工具对比。

> **核心理念**：调试是编程中最耗时的环节。Bash 提供了丰富的调试工具链，从 `set -x` 追踪到 `shellcheck` 静态分析，合理使用可大幅降低排错成本。

---

### 第1节：set 选项详解（set Options Deep Dive）

`set` 是 Bash 内置命令，用于控制 shell 行为和启用调试选项。

#### 调试选项

| 选项 | 功能 | 用途 |
|------|------|------|
| `set -x` | 执行追踪 | 显示每条命令展开后的实际内容 |
| `set -e` | 命令失败即退出 | 避免错误累积 |
| `set -u` | 未定义变量报错 | 防止变量拼写错误 |
| `set -o pipefail` | 管道失败传播 | 检测管道中任意命令失败 |
| `set -n` | 语法检查（不执行） | 验证脚本语法 |
| `set -v` | 显示输入行 | 原始脚本内容 |

#### 推荐脚本头

```bash
#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

# 等效于 C 的 -Wall -Werror
# -e：类似 C 的 errno 检查
# -u：类似 C 的未初始化变量警告
# -o pipefail：C 中无直接对应
```

#### set -x 详解

```bash
# 基本追踪
set -x
echo "Hello"
ls /tmp
set +x  # 关闭追踪

# 输出示例：
# + echo 'Hello'
# Hello
# + ls /tmp

# 在函数中追踪
debug_func() {
    set -x
    local x=1
    local y=$((x + 2))
    set +x
}

# 控制追踪输出
exec 2>/tmp/trace.log  # 重定向追踪到文件
set -x
# ... 命令 ...
set +x
exec 2>&2  # 恢复 stderr
```

#### set -e 行为详解

```bash
# set -e 的复杂行为
set -e

# 失败命令会终止脚本
false  # 脚本在此终止

# 以下情况不会触发退出：
# 条件命令：if, while, until
if false; then echo "no"; fi

# 管道中的命令（除非 pipefail）
false | true  # 不会退出

# 取反命令
! false  # 不会退出

# 逻辑运算符
false || true  # 不会退出
```

#### set -u 使用陷阱

```bash
set -u

# 普通变量
echo "$UNDEFINED_VAR"  # 报错：unbound variable

# 数组空元素（Bash 4.4+）
arr=()
echo "${arr[0]}"  # Bash 4.4+ 不报错，旧版本报错

# 特殊参数
echo "$@"  # 空参数列表时可能报错
echo "$*"  # 同上

# 安全检查
: "${VAR:?Variable is not set}"
echo "$VAR"
```

---

### 第2节：bash -n 语法检查（bash -n Syntax Check）

```bash
# 基本语法检查
bash -n script.sh

# 仅检查语法，不执行
bash -n << 'SCRIPT'
#!/bin/bash
if [ -f file ]; then
    echo "exists"
else
    echo "missing"
fi
SCRIPT

# 检查管道中的脚本
cat script.sh | bash -n

# 常见错误类型
# - 缺少 fi/done/esac
# - 引号不匹配
# - 语法错误

# 示例错误
bash -n << 'ERROR'
if [ -f file ]; then
    echo "exists"
    # 缺少 fi
ERROR
# 输出：line X: syntax error: unexpected end of file
```

#### -n vs -v vs -x

| 选项 | 功能 | 执行代码 | 适用阶段 |
|------|------|----------|----------|
| `-n` | 语法检查 | 否 | 编写时 |
| `-v` | 逐行回显 | 是 | 调试时 |
| `-x` | 命令追踪 | 是 | 调试时 |

---

### 第3节：shellcheck 静态分析（shellcheck Static Analysis）

[ShellCheck](https://www.shellcheck.net/) 是最强大的 Bash 静态分析工具。

```bash
# 安装
# Ubuntu/Debian
sudo apt install shellcheck

# macOS
brew install shellcheck

# 基本使用
shellcheck script.sh

# 指定 shell
shellcheck -s bash script.sh
shellcheck -s sh script.sh    # POSIX sh

# JSON 输出（用于 CI）
shellcheck -f json script.sh

# 排除特定警告
shellcheck -e SC2086,SC2046 script.sh

# 包含/排除代码
shellcheck -e SC2086 script.sh    # 排除
shellcheck -i SC2086 script.sh    # 仅显示
```

#### 常见 shellcheck 警告

| 代码 | 含义 | 修复 |
|------|------|------|
| SC2086 | 变量未加引号 | `"$var"` |
| SC2046 | 命令替换未加引号 | `"$()"` |
| SC2006 | 使用反引号 | 改用 `$()` |
| SC2009 | `ps` 使用模式 | 使用 `pgrep` |
| SC2012 | 使用 `ls` 获取文件 | 改用 glob |
| SC2034 | 变量赋值但未使用 | 删除或使用 |
| SC2154 | 变量未定义 | 检查拼写 |

```bash
# shellcheck 预处理指令
#!/bin/bash
# shellcheck disable=SC2086
echo $unquoted_var  # 此行不检查 SC2086

# 整个文件禁用
# shellcheck disable=SC2086
```

---

### 第4节：time 性能计时（time Performance Timing）

```bash
# 内置 time（精度较低）
time ls /usr/bin

# 格式化输出
TIMEFORMAT='%R seconds (real) %U seconds (user) %S seconds (sys)'
time {
    find / -name "*.log" -mtime -1 2>/dev/null | wc -l
}

# 多次测量取平均
for i in {1..10}; do
    /usr/bin/time -f "%e" ./script.sh 2>/dev/null
done | awk '{sum+=$1; n++} END {print "Avg:", sum/n}'

# /usr/bin/time 详细信息
/usr/bin/time -v ./heavy_task.sh
# 输出包含：最大驻留集大小、页错误、上下文切换等
```

#### 计时对比

| 工具 | 精度 | 输出信息 | 安装 |
|------|------|----------|------|
| `time` | 秒 | real/user/sys | 内置 |
| `/usr/bin/time` | 毫秒 | 详细资源使用 | 系统 |
| `hyperfine` | 纳秒 | 统计分析 | 需安装 |

---

### 第5节：性能优化（Performance Optimization）

#### 避免子 shell

```bash
# 差：子 shell 中修改变量
count=0
echo -e "a\nb\nc" | while read line; do
    ((count++))
done
echo "$count"  # 0

# 好：使用进程替换
count=0
while read line; do
    ((count++))
done < <(echo -e "a\nb\nc")
echo "$count"  # 3

# 好：使用 lastpipe（Bash 4.2+）
shopt -s lastpipe
count=0
echo -e "a\nb\nc" | while read line; do
    ((count++))
done
echo "$count"  # 3
```

#### 减少外部命令

```bash
# 差：大量外部命令
for i in {1..1000}; do
    echo "$i" | awk '{print $1 * 2}'
done

# 好：单次 awk 处理
seq 1 1000 | awk '{print $1 * 2}'

# 差：循环中频繁调用 grep
for file in *.txt; do
    grep "pattern" "$file"
done

# 好：单次 grep
grep "pattern" *.txt
```

#### 字符串操作优化

```bash
# 差：使用外部命令
filename=$(echo "/path/to/file.txt" | sed 's/.*\///' | sed 's/\.txt$//')

# 好：使用参数展开
filename=$(basename "/path/to/file.txt" .txt)

# 好：纯 Bash 参数展开
filepath="/path/to/file.txt"
filename="${filepath##*/}"
filename="${filename%.txt}"

# 差：使用外部命令做字符串替换
result=$(echo "$string" | sed 's/old/new/g')

# 好：使用 Bash 替换
result="${string//old/new}"
```

#### 数组 vs 临时文件

```bash
# 差：使用临时文件收集数据
tmpfile=$(mktemp)
for i in {1..1000}; do
    echo "$i" >> "$tmpfile"
done
sort "$tmpfile"
rm "$tmpfile"

# 好：使用数组
declare -a data=()
for i in {1..1000}; do
    data+=("$i")
done
printf '%s\n' "${data[@]}" | sort
```

---

### 第6节：性能分析（Performance Profiling）

```bash
# 生成调试版本
bash -x script.sh 2> debug.log

# 分析 debug.log
grep '+' debug.log | wc -l           # 命令总数
grep '+' debug.log | head -20        # 前 20 条命令

# time 分析各阶段
time_stage() {
    local start=$SECONDS
    "$@"
    echo "$1: $((SECONDS - start))s"
}

time_stage "Download" download_files
time_stage "Process" process_data
time_stage "Upload" upload_results

# 内存分析
/usr/bin/time -v ./memory_heavy.sh 2>&1 | grep -i "maximum resident"

# CPU 分析
perf stat ./script.sh  # Linux
sample ./script.sh     # macOS
```

#### profiling 脚本模板

```bash
#!/bin/bash
# profile.sh - 简单的 Bash 性能分析
set -euo pipefail

PROF_FILE="/tmp/bash_profile_$$"
trap 'rm -f "$PROF_FILE"' EXIT

# 启用时间追踪
export PS4='+ ${EPOCHREALTIME-$(date +%s.%N)} ${BASH_SOURCE}:${LINENO}: '
exec 3>"$PROF_FILE"
BASH_XTRACEFD=3
set -x

# === 你的代码放这里 ===
for i in {1..100}; do
    process_item "$i"
done
# === 结束 ===

set +x
exec 3>&-

# 分析
echo "=== Profile Results ==="
awk -F'[ +]' '{
    time = $2
    cmd = $4
    total[cmd] += time
    count[cmd]++
}
END {
    for (cmd in total)
        printf "%-40s avg: %10.6f  count: %d\n", cmd, total[cmd]/count[cmd], count[cmd]
}' "$PROF_FILE" | sort -t: -k2 -rn
```

---

### 第7节：Bash vs C 调试对比（Bash vs C Debugging）

| 特性 | Bash | C |
|------|------|---|
| 语法检查 | `bash -n` | `gcc -fsyntax-only` |
| 静态分析 | `shellcheck` | `clang-tidy` |
| 运行时追踪 | `set -x` | `gdb` |
| 性能分析 | `time` / `profile.sh` | `gprof` / `perf` |
| 内存检查 | 有限 | `valgrind` |
| 覆盖率 | `bashcov` | `gcov` |
| 断点调试 | 无原生支持 | `gdb break` |

```c
// C: 使用 gdb 调试
// gcc -g script.c -o script
// gdb ./script
// (gdb) break main
// (gdb) run
// (gdb) print variable

// Bash: 等效调试
// bash -x script.sh
// 或在脚本中手动设置断点
read -p "Press enter to continue..."
```

---

### 本章要点总结

- `set -euo pipefail` 是生产脚本的标配
- `set -x` 输出每条命令展开后的实际内容
- `bash -n` 仅检查语法不执行
- `shellcheck` 是最强大的静态分析工具
- 避免子 shell 和外部命令是性能优化关键
- 使用参数展开替代外部命令处理字符串

---

**上一章**：[[05_awk文本处理：字段分割_数组_END块|awk 文本处理]]
**下一章**：[[07_子shell与命令替换：执行上下文|子 shell 与命令替换]]
