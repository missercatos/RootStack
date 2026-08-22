# 陷阱与错误处理：errtrap、exittrap（Traps & Error Handling: errtrap, exittrap）

## 章节概述

本章系统讲解 Bash 中的陷阱机制（trap）与错误处理策略，包括 `trap EXIT` 资源清理、`trap ERR` 错误捕获、`trap DEBUG` 调试钩子、函数中的错误处理、`set -euo pipefail` 最佳实践，以及与 C 语言错误处理的对比。这是编写生产级 Bash 脚本的必备知识。

> **核心理念**：健壮的脚本必须处理所有退出路径——正常结束、错误退出、信号中断。`trap EXIT` 是实现"单一清理入口"的黄金模式。

---

### 第1节：trap EXIT 资源清理（trap EXIT Resource Cleanup）

`trap EXIT` 在脚本以任何方式退出时触发——正常 `exit`、`set -e` 终止、信号中断、甚至 `return`。

```bash
#!/bin/bash
set -euo pipefail

TEMP_DIR=$(mktemp -d)
LOCK_FILE="/tmp/myapp_$$.lock"

cleanup() {
    local exit_code=$?
    echo "Cleaning up..."
    rm -rf "$TEMP_DIR"
    rm -f "$LOCK_FILE"
    exit $exit_code
}

trap cleanup EXIT

# 主逻辑
mkdir -p "$LOCK_FILE"
echo "Processing in $TEMP_DIR"
process_data "$TEMP_DIR"
echo "Done"
# cleanup 会在脚本退出时自动调用
```

#### EXIT trap 的触发场景

```bash
# 正常退出
trap 'echo "Goodbye"' EXIT
echo "Hello"
exit 0
# 输出：Hello, Goodbye

# set -e 导致退出
set -e
trap 'echo "Error cleanup"' EXIT
false  # 触发退出
# 输出：Error cleanup

# 信号中断
trap 'echo "Interrupted"' EXIT INT TERM
sleep 10
# Ctrl+C 输出：Interrupted

# return 退出函数
my_func() {
    trap 'echo "Func cleanup"' EXIT
    echo "In function"
    return 0
}
my_func
# 输出：In function, Func cleanup
```

#### EXIT trap 参数

```bash
trap '
    echo "Exit code: $?"
    echo "Last command: $BASH_COMMAND"
    echo "Line: $LINENO"
' EXIT

# 自定义退出处理
trap '
    if [[ $? -ne 0 ]]; then
        echo "Script failed with exit code $?" >&2
    fi
' EXIT
```

---

### 第2节：trap ERR 错误捕获（trap ERR Error Handling）

`trap ERR` 在命令返回非零退出码时触发（需 `set -E` 或 `set -e`）。

```bash
#!/bin/bash
set -euo pipefail

handle_error() {
    echo "ERROR at line $1, command: '$2'" >&2
    echo "Exit code: $3" >&2
}

trap 'handle_error $LINENO "$BASH_COMMAND" $?' ERR

# 示例
echo "Starting"
false  # 触发 ERR trap
echo "This won't execute"
```

#### ERR trap 继承（Bash 4.3+）

```bash
# ERR trap 默认不传播到子函数
set -E  # 启用 ERR trap 继承

my_func() {
    false  # 会触发 ERR trap
}

trap 'echo "Error caught"' ERR
my_func
```

#### ERR trap 限制

```bash
# 以下情况不会触发 ERR：
# 1. 命令在条件上下文中失败
if false; then echo "no"; fi  # 不触发

# 2. 管道中（除非 pipefail）
false | true  # 不触发
set -o pipefail
false | true  # 触发（最后一个命令失败）

# 3. 取反命令
! false  # 不触发

# 4. 逻辑运算符
false || true  # 不触发
```

---

### 第3节：trap DEBUG 调试钩子（trap DEBUG）

`trap DEBUG` 在每条命令执行前触发，用于调试和追踪。

```bash
#!/bin/bash

# 基本调试追踪
trap 'echo "[DEBUG] Line $LINENO: $BASH_COMMAND"' DEBUG

echo "Step 1"
sleep 1
echo "Step 2"
```

#### 条件调试输出

```bash
#!/bin/bash
DEBUG_LEVEL="${DEBUG_LEVEL:-0}"

debug_log() {
    ((DEBUG_LEVEL > 0)) && echo "[DEBUG] $1" >&2
}

trap 'debug_log "Line $LINENO: $BASH_COMMAND"' DEBUG

# 或使用 DEBUG level 控制
trap '
    if [[ ${DEBUG_LEVEL:-0} -ge 2 ]]; then
        echo "[TRACE] $BASH_COMMAND" >&2
    elif [[ ${DEBUG_LEVEL:-0} -ge 1 ]]; then
        echo "[DEBUG] Line $LINENO" >&2
    fi
' DEBUG
```

#### 调试陷阱实战

```bash
#!/bin/bash
# 高级调试脚本

# 性能追踪
PS4='+ ${EPOCHREALTIME-$(date +%s.%N)} ${BASH_SOURCE}:${LINENO}: '
exec 3>/tmp/debug_$$
BASH_XTRACEFD=3

# 条件启用
if [[ "${TRACE:-0}" == "1" ]]; then
    set -x
fi

# 自定义调试输出
debug() {
    if [[ "${DEBUG:-0}" == "1" ]]; then
        echo "[DEBUG $(date +%H:%M:%S)] $*" >&2
    fi
}

trap 'debug "Executing: $BASH_COMMAND"' DEBUG
```

---

### 第4节：函数中的错误处理（Error Handling in Functions）

```bash
# 函数错误处理模式
safe_func() {
    # 方式 1：返回退出码
    if ! command_that_might_fail; then
        echo "Command failed" >&2
        return 1
    fi
    return 0
}

# 方式 2：使用 || 链式处理
safe_func() {
    command1 || { echo "Failed" >&2; return 1; }
    command2 || return 2
    command3 || return 3
}

# 方式 3：set -e + ERR trap
set -E
trap 'echo "Error in $FUNCNAME" >&2' ERR

risky_func() {
    dangerous_command  # 失败会触发 ERR trap
}
```

#### 错误传播策略

```bash
#!/bin/bash
set -euo pipefail

# 策略 1：每个函数检查返回值
step1() {
    risky_operation || { echo "Step 1 failed" >&2; return 1; }
}

step2() {
    another_operation || { echo "Step 2 failed" >&2; return 1; }
}

main() {
    step1 || exit 1
    step2 || exit 2
}

# 策略 2：使用 ERR trap 统一处理
trap 'echo "Error at line $LINENO: $BASH_COMMAND" >&2; exit 1' ERR

main() {
    step1
    step2
}

# 策略 3：重试机制
retry() {
    local max_attempts=$1
    shift
    local attempt=1

    while ((attempt <= max_attempts)); do
        if "$@"; then
            return 0
        fi
        echo "Attempt $attempt failed, retrying..." >&2
        ((attempt++))
        sleep 1
    done

    echo "All $max_attempts attempts failed" >&2
    return 1
}

retry 3 flaky_operation
```

---

### 第5节：set -euo pipefail 最佳实践（Best Practices）

#### 推荐脚本模板

```bash
#!/bin/bash
# 生产级脚本模板
set -euo pipefail
IFS=$'\n\t'

# 错误处理
on_error() {
    local exit_code=$?
    local line_no=$1
    echo "ERROR: Script failed at line $line_no with exit code $exit_code" >&2
    echo "  Command: $BASH_COMMAND" >&2
    exit $exit_code
}

trap 'on_error $LINENO' ERR

# 清理处理
cleanup() {
    local exit_code=$?
    # 清理临时文件
    [[ -d "${TEMP_DIR:-}" ]] && rm -rf "$TEMP_DIR"
    [[ -f "${LOCK_FILE:-}" ]] && rm -f "$LOCK_FILE"
    return $exit_code
}

trap cleanup EXIT

# 信号处理
trap 'echo "Interrupted" >&2; exit 130' INT TERM

# 初始化
TEMP_DIR=$(mktemp -d)
LOCK_FILE="/tmp/myapp_$$.lock"

# 主逻辑
main() {
    echo "Starting..."
    # 你的代码
    echo "Done"
}

main "$@"
```

#### set -euo pipefail 解析

| 选项 | 功能 | 等效 C 概念 |
|------|------|-------------|
| `set -e` | 命令失败退出 | `if (ret != 0) exit(ret);` |
| `set -u` | 未定义变量报错 | 编译器警告 `-Wuninitialized` |
| `set -o pipefail` | 管道失败传播 | `waitpid()` 检查 |

```bash
# set -e 的陷阱
set -e
# 失败命令在子 shell 中不影响父 shell
(subshell_false)  # 不退出
# 管道中的失败（无 pipefail）
false | true  # 不退出
# 条件上下文
false && echo "no"  # 不退出

# 正确的错误处理
set -euo pipefail
# 以上陷阱都被消除
```

---

### 第6节：信号处理最佳实践（Signal Handling Best Practices）

```bash
#!/bin/bash

# 正确的信号处理模式
setup_signals() {
    trap 'cleanup; exit 130' INT    # Ctrl+C
    trap 'cleanup; exit 143' TERM   # kill
    trap 'cleanup; exit 126' QUIT   # Ctrl+\
    trap '' HUP                     # 忽略 SIGHUP
}

cleanup() {
    # 只执行一次清理
    if [[ -z "${CLEANUP_DONE:-}" ]]; then
        CLEANUP_DONE=1
        rm -rf "${TEMP_DIR:-}"
        rm -f "${LOCK_FILE:-}"
        echo "Cleanup completed" >&2
    fi
}

# 主脚本
setup_signals
trap cleanup EXIT

# ... 主逻辑 ...
```

#### 信号处理顺序

```bash
#!/bin/bash
# 信号处理顺序演示

# EXIT 最后触发
trap 'echo "1. EXIT trap"' EXIT

# INT 和 TERM 在退出前触发
trap 'echo "2. INT trap"' INT
trap 'echo "3. TERM trap"' TERM

# ERR 在错误时触发
trap 'echo "4. ERR trap"' ERR

# DEBUG 在每条命令前触发
trap 'echo "5. DEBUG trap"' DEBUG

# 执行顺序：DEBUG -> ERR -> INT/TERM -> EXIT
```

---

### 第7节：C 语言错误处理对比（C Error Handling Comparison）

| 特性 | Bash | C |
|------|------|---|
| 错误检测 | `set -e` | `errno` + 检查 |
| 错误传播 | `return $?` | `return -1` |
| 资源清理 | `trap cleanup EXIT` | `atexit()` + `goto` |
| 信号处理 | `trap 'cmd' SIG` | `signal()` / `sigaction()` |
| 调试 | `set -x` | `gdb` |
| 内存管理 | 自动 | 手动 `malloc/free` |

```c
// C：经典的 goto 清理模式
int main() {
    char *temp = NULL;
    FILE *fp = NULL;
    int result = -1;

    temp = malloc(256);
    if (!temp) goto cleanup;

    fp = fopen("output.txt", "w");
    if (!fp) goto cleanup;

    // 主逻辑
    if (do_work(fp) < 0) goto cleanup;

    result = 0;

cleanup:
    if (fp) fclose(fp);
    if (temp) free(temp);
    return result;
}
```

```bash
# Bash：trap EXIT 实现相同功能
trap cleanup EXIT

temp=$(mktemp)
fp=$(mktemp)

do_work || { echo "Failed"; exit 1; }

cleanup() {
    rm -f "$temp" "$fp"
}
```

#### Bash 错误处理 vs C

```c
// C: 错误处理需要大量样板代码
int divide(int a, int b, int *result) {
    if (b == 0) {
        errno = EINVAL;
        return -1;
    }
    *result = a / b;
    return 0;
}

// 使用
int res;
if (divide(10, 0, &res) < 0) {
    perror("divide");
    exit(EXIT_FAILURE);
}
```

```bash
# Bash：简洁得多
divide() {
    (( $2 == 0 )) && { echo "Division by zero" >&2; return 1; }
    echo $(( $1 / $2 ))
}

result=$(divide 10 0) || exit 1
```

---

### 第8节：复杂错误处理模式（Complex Error Handling Patterns）

```bash
#!/bin/bash
# 模式 1：重试 + 退避
retry_with_backoff() {
    local max_attempts=$1
    local base_delay=$2
    shift 2

    for ((attempt=1; attempt<=max_attempts; attempt++)); do
        if "$@"; then
            return 0
        fi

        local delay=$((base_delay * attempt))
        echo "Attempt $attempt failed, retrying in ${delay}s..." >&2
        sleep "$delay"
    done

    echo "All $max_attempts attempts failed" >&2
    return 1
}

retry_with_backoff 3 2 curl -sf http://api.example.com

# 模式 2：错误收集
declare -a ERRORS=()

collect_error() {
    ERRORS+=("Line $1: $2")
}

trap 'collect_error $LINENO "$BASH_COMMAND"' ERR

# ... 执行多个可能失败的命令 ...

if [[ ${#ERRORS[@]} -gt 0 ]]; then
    echo "Errors encountered:" >&2
    printf '  %s\n' "${ERRORS[@]}" >&2
    exit 1
fi

# 模式 3：原子操作
atomic_write() {
    local target=$1
    local temp="${target}.tmp.$$"

    # 写入临时文件
    if ! write_to_file "$temp"; then
        rm -f "$temp"
        return 1
    fi

    # 原子重命名
    mv "$temp" "$target"
}

# 模式 4：幂等操作
idempotent_setup() {
    local lockfile="/tmp/setup_$$.lock"

    # 确保只执行一次
    if [[ -f "$lockfile" ]]; then
        echo "Setup already completed" >&2
        return 0
    fi

    # 执行设置
    perform_setup

    # 创建锁文件
    touch "$lockfile"
}
```

---

### 本章要点总结

- `trap cleanup EXIT` 是资源清理的黄金模式
- `trap ERR` 捕获命令失败，需 `set -E` 启用继承
- `trap DEBUG` 在每条命令前触发，用于调试追踪
- `set -euo pipefail` 是生产脚本的标配
- ERR trap 在条件上下文、管道中不会触发
- EXIT trap 在所有退出路径都会触发——最可靠

---

**上一章**：[[08_高级参数展开：${var:-default}_模式匹配|高级参数展开]]
**回到目录**：[[../README|Bash 精通篇]]
