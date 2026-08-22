# 进程与信号：trap、前后台与信号处理（Process & Signal: trap, foreground/background, signal handling）

## 章节概述

本章深入讲解 Bash 中进程控制与信号处理的核心机制，涵盖前后台任务管理、作业控制命令、`trap` 信号捕获以及进程替换 `<()` 的高级用法。理解这些概念对于编写健壮的脚本和系统管理自动化至关重要。

> **核心理念**：信号是 Unix 系统中进程间通信的基础机制，`trap` 是 Bash 脚本优雅退出和资源清理的关键工具。掌握进程控制让你的脚本具备生产级可靠性。

---

### 第1节：前台与后台执行（Foreground & Background Execution）

Bash 允许在前台和后台之间灵活调度进程，实现并发任务管理。

#### 前台执行

```bash
# 默认所有命令都在前台执行
echo "This runs in foreground"
sleep 5  # 会阻塞终端直到完成

# 前台进程会接收终端信号（如 Ctrl+C 发送 SIGINT）
```

#### 后台执行 `&`

```bash
# 在命令末尾添加 & 将进程放入后台
sleep 10 &
echo "Background PID: $!"  # $! 记录最近后台进程的 PID

# 批量后台任务
for i in {1..5}; do
    sleep $((RANDOM % 10)) &
done
echo "All tasks launched"
wait  # 等待所有后台任务完成
```

#### nohup 与 disown

```bash
# nohup 防止 SIGHUP 终止进程
nohup long_running_task.sh &
disown  # 从 shell 的作业表中移除

# 或者一条命令实现
nohup ./server.sh > /var/log/server.log 2>&1 &
disown $!
```

#### 关键变量与文件

| 变量/文件 | 说明 | 示例值 |
|-----------|------|--------|
| `$!` | 最近后台进程 PID | `12345` |
| `$PPID` | 父进程 PID | `12340` |
| `/proc/$$/fd/0` | 当前进程标准输入 | 终端设备 |
| `$BASHPID` | 当前子 shell PID（Bash 4.1+） | `12346` |

---

### 第2节：作业控制（Job Control: jobs/fg/bg）

作业控制是管理多个终端任务的核心功能。

#### jobs 命令

```bash
# 列出所有作业
jobs

# 详细信息（显示 PID）
jobs -l

# 仅显示进程 ID
jobs -p

# 列出后台进程状态（非交互式 shell）
jobs -x echo "Job details: %1"

# 输出格式说明
# [1]+  Running                 sleep 100 &
# [2]-  Stopped                 vim file.txt
# [3]+  Done                    ./process.sh
```

#### fg 与 bg

```bash
# fg：将后台作业移到前台
fg %1       # 通过作业号
fg %sleep   # 通过命令名前缀匹配

# bg：继续暂停的作业在后台运行
bg %2       # 恢复暂停作业到后台

# 快捷键操作
# Ctrl+Z    暂停当前前台进程（发送 SIGTSTP）
# Ctrl+C    终止前台进程（发送 SIGINT）
# Ctrl+Y    前台进程就绪停止（SIGTSTP）
```

#### 作业管理实战

```bash
#!/bin/bash
# 同时下载多个文件
declare -a PIDS=()

for url in \
    "https://example.com/file1.tar.gz" \
    "https://example.com/file2.tar.gz" \
    "https://example.com/file3.tar.gz"
do
    wget "$url" -P /tmp/downloads/ &
    PIDS+=($!)
done

# 等待所有下载完成并检查结果
FAILED=0
for pid in "${PIDS[@]}"; do
    if ! wait "$pid"; then
        echo "Download failed for PID $pid" >&2
        ((FAILED++))
    fi
done

if [[ $FAILED -gt 0 ]]; then
    echo "Failed: $FAILED downloads"
    exit 1
fi
echo "All downloads completed successfully"
```

---

### 第3节：wait 等待进程（wait for Processes）

`wait` 用于同步等待指定或所有后台进程完成。

#### 基本用法

```bash
# 等待所有后台进程
sleep 5 &
sleep 3 &
wait
echo "All background tasks finished"

# 等待特定 PID
./task1.sh &
pid1=$!
./task2.sh &
pid2=$!

wait $pid1
echo "Task 1 finished"

wait $pid2
echo "Task 2 finished"

# 等待并获取退出状态
./script.sh &
wait $!
echo "Exit code: $?"
```

#### 等待任意一个完成（Bash 4.3+）

```bash
# wait -n 等待任意一个子进程完成
sleep 5 &
sleep 3 &
wait -n  # 返回第一个完成的进程 PID
echo "First task completed"

# 循环等待所有完成
while kill -0 "" 2>/dev/null; do
    wait -n 2>/dev/null || break
done
```

#### 错误处理模式

```bash
# 并行执行并收集退出码
run_parallel() {
    local pids=()
    for cmd in "$@"; do
        $cmd &
        pids+=($!)
    done

    local failures=0
    for pid in "${pids[@]}"; do
        if ! wait "$pid"; then
            echo "PID $pid failed with exit code $?" >&2
            ((failures++))
        fi
    done
    return $failures
}

run_parallel "./check_a.sh" "./check_b.sh" "./check_c.sh"
echo "Failures: $?"
```

---

### 第4节：trap 捕获信号（Signal Trapping）

`trap` 是 Bash 脚本健壮性的核心，用于捕获信号并执行清理逻辑。

#### trap 语法

```bash
# 语法
trap 'command' SIGNAL...

# 常用信号
trap '' SIGINT SIGTERM    # 忽略信号（空命令）
trap 'cleanup' EXIT       # 脚本退出时执行
trap 'echo "Received SIGHUP"' HUP
```

#### 优雅退出模式

```bash
#!/bin/bash
set -euo pipefail

TEMP_DIR=$(mktemp -d)
LOCK_FILE="/tmp/myapp_$$.lock"

# 清理函数
cleanup() {
    echo "Cleaning up..."
    rm -rf "$TEMP_DIR"
    rm -f "$LOCK_FILE"
}

# 注册清理钩子
trap cleanup EXIT

# 创建锁文件防止并发
if ! mkdir "$LOCK_FILE" 2>/dev/null; then
    echo "Another instance is running" >&2
    exit 1
fi

# 主逻辑
echo "Processing in $TEMP_DIR"
process_data "$TEMP_DIR"
echo "Done"

# cleanup 会在脚本正常退出、Ctrl+C、或 kill 时自动调用
```

#### trap 信号参考表

| 信号 | 编号 | 默认行为 | 常见触发 | trap 用法 |
|------|------|----------|----------|-----------|
| `SIGHUP` | 1 | 终止 | 终端关闭 | 重载配置 |
| `SIGINT` | 2 | 终止 | Ctrl+C | 优雅停止 |
| `SIGQUIT` | 3 | 核心转储 | Ctrl+\ | 调试 |
| `SIGTERM` | 15 | 终止 | kill 命令 | 清理资源 |
| `SIGKILL` | 9 | 终止(不可捕获) | kill -9 | 不可 trap |
| `SIGEXIT` | - | - | 子 shell 退出 | 清理临时文件 |

#### 调试陷阱

```bash
# DEBUG：每条命令执行前触发
trap 'echo "DEBUG: $BASH_COMMAND at line $LINENO"' DEBUG

# ERR：命令返回非零时触发（需 set -E）
set -E
trap 'echo "ERROR: command failed at line $LINENO" >&2' ERR

# RETURN：函数返回时触发
trap 'echo "Function $FUNCNAME returned"' RETURN
```

---

### 第5节：进程替换 `<()`（Process Substitution）

进程替换将命令输出伪装成文件，允许在需要文件参数的命令中使用管道。

#### 基本语法

```bash
# 语法：将命令输出作为文件
diff <(ls dir1) <(ls dir2)

# 同时比较两个目录
diff <(sort file1) <(sort file2)

# 读取多个源
while read -r line; do
    echo "$line"
done < <(generate_data)
```

#### 常见应用场景

```bash
# 比较两个命令的输出
diff <(ssh server1 cat /etc/config) <(ssh server2 cat /etc/config)

# 同时处理多个输入源
paste <(cut -f1 data.txt) <(cut -f2 data.txt) > combined.txt

# 在循环中使用
while IFS= read -r line; do
    process "$line"
done < <(find /path -name "*.log" -mtime -7)

# 比较排序后的输出
diff <(grep "ERROR" app.log | sort) <(grep "WARN" app.log | sort)
```

#### 进程替换 vs 管道 vs 临时文件

| 方法 | 语法 | 优点 | 缺点 | 适用场景 |
|------|------|------|------|----------|
| 管道 | `cmd1 \| cmd2` | 简洁、高效 | 单向、无随机访问 | 流式处理 |
| 临时文件 | `cmd > tmp; cmd2 tmp` | 可多次读取 | 需清理、磁盘IO | 大文件 |
| 进程替换 | `cmd1 <(cmd2)` | 像文件一样使用 | 子 shell、内存 | 比较、多输入 |

#### 反向进程替换 `>()`（Bash 4.1+）

```bash
# 将输出写入命令（作为文件）
echo "data" > >(tee output.txt)

# 分发输出到多个目标
generate_data > >(compress > archive.gz) > >(split -b 1M - chunks)

# 日志同时输出到文件和管道
./app.sh > >(tee app.log) 2>&1 | grep -v DEBUG
```

---

### 第6节：进程替换综合实战（Practical Process Control）

#### 并行任务控制器

```bash
#!/bin/bash
set -euo pipefail

MAX_PARALLEL=4
RUNNING=0
declare -A PIDS

# 信号处理
cleanup() {
    echo "Terminating all tasks..."
    for name in "${!PIDS[@]}"; do
        kill "${PIDS[$name]}" 2>/dev/null || true
    done
    exit 1
}
trap cleanup SIGINT SIGTERM

run_task() {
    local name=$1
    local cmd=$2

    # 等待空闲槽位
    while ((RUNNING >= MAX_PARALLEL)); do
        for name in "${!PIDS[@]}"; do
            if ! kill -0 "${PIDS[$name]}" 2>/dev/null; then
                unset "PIDS[$name]"
                ((RUNNING--))
            fi
        done
        sleep 0.1
    done

    # 启动任务
    $cmd &
    PIDS[$name]=$!
    ((RUNNING++))
}

# 使用示例
run_task "task1" "sleep 5"
run_task "task2" "sleep 3"
run_task "task3" "sleep 4"

# 等待所有完成
wait
echo "All tasks completed"
```

---

### 第7节：C 语言进程控制对比（C Process Control Comparison）

| 特性 | Bash | C 语言 |
|------|------|--------|
| 创建子进程 | `cmd &` | `fork()` |
| 等待进程 | `wait $pid` | `waitpid(pid, &status, 0)` |
| 信号捕获 | `trap 'cmd' SIG` | `signal(sig, handler)` |
| 执行替换 | `exec cmd` | `execvp(argv[0], argv)` |
| 进程组 | `set -m` (job control) | `setpgid(0, 0)` |
| 管道 | `cmd1 \| cmd2` | `pipe()` + `fork()` |

#### C 错误处理 vs Bash trap

```c
// C: 手动清理
void handler(int sig) {
    cleanup_temp_files();
    _exit(128 + sig);
}

int main() {
    signal(SIGINT, handler);
    signal(SIGTERM, handler);
    // ... 主逻辑
    atexit(cleanup_temp_files);  // 正常退出清理
}
```

```bash
# Bash: trap 自动清理
cleanup() { rm -rf "$TEMP_DIR"; }
trap cleanup EXIT  # 覆盖所有退出路径
# EXIT trap 在正常退出、exit()、信号终止时都会触发
```

---

### 本章要点总结

- `&` 将进程放入后台，`$!` 获取其 PID
- `jobs/fg/bg` 管理终端作业
- `wait` 同步等待后台进程
- `trap cleanup EXIT` 是脚本优雅退出的黄金模式
- `<()` 进程替换让命令输出像文件一样可用
- `trap '' SIGINT SIGTERM` 可以临时忽略信号

---

**下一章**：[[02_管道与重定向：tee_xargs_exec|管道与重定向：tee、xargs、exec]]
