# 管道与重定向：tee、xargs、exec（Pipes & Redirection: tee, xargs, exec）

## 章节概述

本章系统讲解 Bash 中管道、重定向和文件描述符的高级用法，包括 `tee` 分流输出、`xargs` 参数转换、`exec` 进程替换以及自定义文件描述符的使用。这些是构建数据处理流水线的基础工具。

> **核心理念**：Unix 哲学——"一切皆文件，一切皆流"。管道连接命令，重定向控制数据流向，`xargs` 桥接文本与命令参数。

---

### 第1节：管道基础与高级用法（Pipe Basics & Advanced）

管道 `|` 将前一个命令的 stdout 连接到后一个命令的 stdin，是最基础的进程间通信方式。

#### 基本管道

```bash
# 简单管道链
cat /var/log/syslog | grep "error" | wc -l

# 管道 + 排序去重
ps aux | awk '{print $1}' | sort | uniq -c | sort -rn

# 管道 + 格式化
df -h | awk 'NR>1 {printf "%-20s %s used\n", $6, $5}'
```

#### 管道的限制

```bash
# 管道中的变量作用域隔离（子 shell）
count=0
echo -e "a\nb\nc" | while read line; do
    ((count++))
done
echo "Count: $count"  # 输出 0！子 shell 中的修改不传播

# 解决方案：使用进程替换
count=0
while read line; do
    ((count++))
done < <(echo -e "a\nb\nc")
echo "Count: $count"  # 输出 3
```

#### 仅管道 stderr

```bash
# 默认管道只传递 stdout
cmd1 2>&1 | cmd2       # stdout + stderr 都传递
cmd1 2>&1 | cmd2 1>&2  # 恢复 stdout 分离

# 仅传递 stderr 给 cmd2，stdout 继续
cmd1 2>&1 >/dev/null | cmd2
```

---

### 第2节：tee 分流输出（Tee for Output Splitting）

`tee` 将数据同时输出到屏幕和文件，是调试和日志记录的利器。

#### 基本用法

```bash
# 同时显示和保存
ls -la | tee output.txt

# 追加模式
echo "new line" | tee -a logfile.txt

# 写入多个文件
data_stream | tee file1.txt file2.txt file3.txt

# 同时写文件和继续管道
cat data.txt | tee processed.txt | sort | tee sorted.txt
```

#### 高级技巧

```bash
# 使用进程替换同时写多个日志
./deploy.sh 2>&1 | tee >(gzip > deploy.log.gz) > deploy.log

# 使用 here string
tee <<< "data to save" output.txt

# 仅在成功时保存
cmd1 | tee output.txt && echo "Success" || echo "Failed"

# 实时监控并记录
tail -f /var/log/syslog | tee >(grep "error" >> errors.log) | grep "critical"
```

#### tee 与重定向对比

| 方法 | 语法 | 功能 | 限制 |
|------|------|------|------|
| `>` | `cmd > file` | 仅写文件 | 无屏幕输出 |
| `>>` | `cmd >> file` | 追加文件 | 无屏幕输出 |
| `\|` | `cmd1 \| cmd2` | 管道连接 | 无文件保存 |
| `tee` | `cmd \| tee file` | 文件+管道 | 需要管道语法 |

---

### 第3节：重定向详解（Redirection Deep Dive）

#### 标准文件描述符

```bash
# fd 0 = stdin, fd 1 = stdout, fd 2 = stderr

# 输出重定向
cmd > file          # stdout -> file (覆盖)
cmd >> file         # stdout -> file (追加)
cmd 2> error.log    # stderr -> file
cmd 2>> error.log   # stderr -> file (追加)

# 输入重定向
cmd < input.txt     # 从文件读取 stdin

# 丢弃输出
cmd > /dev/null     # 丢弃 stdout
cmd 2>/dev/null     # 丢弃 stderr
cmd &>/dev/null     # 丢弃所有输出
```

#### Here Document

```bash
# 基本 here document
cat << EOF
Line 1: $HOME
Line 2: $(date)
Line 3: Variable: $UNSET_VAR
EOF

# 引用的 delimiter（不展开变量）
cat << 'EOF'
Literal text: $HOME will NOT be expanded
$(date) will NOT be executed
EOF

# 使用 here document
mysql -u root << 'SQL'
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(100)
);
SQL
```

#### Here String

```bash
# <<< 将字符串作为命令的 stdin
grep "pattern" <<< "$variable"
while read line; do
    echo "Processing: $line"
done <<< "$(ls /etc/*.conf)"

# 对比
echo "test" | cat       # 管道
cat <<< "test"          # here string
cat << EOF
test
EOF                    # here document
```

---

### 第4节：exec 替换进程（exec Process Replacement）

`exec` 用新进程替换当前 shell 进程，不创建子进程。

#### exec 重定向

```bash
# 将 fd 1 重定向到文件（影响后续所有命令）
exec > logfile.txt
echo "This goes to logfile"
ls -la  # 输出也到 logfile

# 恢复 stdout
exec 1>&2  # 恢复为 stderr（通常指终端）

# exec 打开文件描述符
exec 3> output.txt
echo "written to fd 3" >&3
exec 3>&-  # 关闭 fd 3
```

#### exec 进程替换

```bash
# 用新命令替换当前 shell
exec bash        # 启动新 bash 替换当前 shell
exec /bin/sh     # 替换为 sh
exec python3     # 替换为 Python（不返回）

# 常见场景：容器启动脚本
#!/bin/bash
# 初始化环境
source /etc/profile
export PATH="/app/bin:$PATH"

# 替换为实际应用（PID 不变）
exec "$@"
# 等价于：exec "$1" "$2" "$3" ...
```

#### exec vs 直接运行

| 方式 | 行为 | PID | 环境 | 返回 |
|------|------|-----|------|------|
| `cmd` | 创建子进程 | 新 PID | 继承 | 返回 |
| `exec cmd` | 替换当前进程 | 不变 | 继承 | 不返回 |

---

### 第5节：自定义文件描述符（Custom File Descriptors）

除了标准的 0/1/2，Bash 允许使用自定义文件描述符。

#### 打开与使用

```bash
# 打开 fd 3 用于写入
exec 3> output.txt
echo "line 1" >&3
echo "line 2" >&3
exec 3>&-  # 关闭

# 打开 fd 4 用于读取
exec 4< input.txt
while read -u 4 line; do
    echo "$line"
done
exec 4<&-

# 同时读写
exec 3<> data.txt
read -u 3 first_line
echo "new data" >&3
exec 3>&-
```

#### 实战：数据处理管道

```bash
#!/bin/bash
set -euo pipefail

INPUT="data.csv"
REPORT="/tmp/report.txt"

# 使用 fd 管理多个输出
exec 3> "$REPORT"
exec 4> /dev/null  # 丢弃中间数据

echo "=== Processing Report ===" >&3
echo "Date: $(date)" >&3
echo "" >&3

# 处理数据
while IFS=, read -r name age city; do
    if ((age > 18)); then
        echo "Adult: $name ($city)" >&3
    else
        echo "Minor: $name ($city)" >&4
    fi
done < "$INPUT"

# 关闭所有 fd
exec 3>&- 4>&-

echo "Report saved to $REPORT"
```

---

### 第6节：xargs 参数构造器（xargs Argument Builder）

`xargs` 将 stdin 转换为命令行参数，是管道与命令行之间的桥梁。

#### 基本用法

```bash
# 默认：用 stdin 作为参数
echo "file1 file2 file3" | xargs rm

# 指定每次传递的参数数量
echo -e "1\n2\n3\n4\n5" | xargs -n 2 echo
# 输出：
# 1 2
# 3 4
# 5

# 处理特殊字符（空格、引号等）
find . -name "*.txt" -print0 | xargs -0 rm -f

# 显示将要执行的命令
echo "file1 file2" | xargs -p rm  # 会提示确认
```

#### 并行执行

```bash
# -P 指定并行进程数
find /var/log -name "*.log" -print0 | xargs -0 -P 4 -n 1 gzip

# -I 替换字符串
ls *.jpg | xargs -I {} convert {} -resize 50% small_{}

# 从文件读取
xargs -a commands.txt -I {} sh -c '{}'

# 批量处理大列表
cat urls.txt | xargs -n 1 -P 8 wget -q
```

#### xargs vs for 循环

| 方法 | 性能 | 内存 | 适用场景 |
|------|------|------|----------|
| `for` 循环 | 逐条执行 | 低 | 复杂逻辑 |
| `xargs` | 批量/并行 | 低 | 简单命令 |
| `xargs -P` | 多进程并行 | 中 | IO 密集型 |

---

### 第7节：高级管道模式（Advanced Pipe Patterns）

#### 管道过滤器组合

```bash
# 构建日志分析流水线
cat /var/log/apache2/access.log \
    | awk '{print $1}' \         # 提取 IP
    | sort \                     # 排序
    | uniq -c \                   # 去重计数
    | sort -rn \                  # 按数量降序
    | head -20 \                  # 前 20 名
    | column -t                   # 格式化输出

# 错误日志聚合
journalctl -u nginx --since "1 hour ago" \
    | grep -i "error" \
    | sed 's/.*error: //' \
    | sort | uniq -c | sort -rn
```

#### 管道与信号处理

```bash
#!/bin/bash
# 管道信号传播
set -euo pipefail

# 管道失败检测
echo "test" | grep "pattern" | wc -l
# 默认：管道返回最后一个命令的退出码

# pipefail：管道中任一命令失败则整体失败
set -o pipefail
false | true  # 现在会返回非零退出码

# 管道中 trap 的传播
trap 'echo "Caught signal"' SIGINT
sleep 10 | cat  # Ctrl+C 只影响 cat，不影响 sleep
```

---

### 第8节：文件描述符 3+ 实战（FD 3+ in Practice）

#### 配置文件读取

```bash
#!/bin/bash
# 同时读取配置文件和命令行参数
CONFIG_FILE="${1:-/etc/myapp.conf}"

exec 3< "$CONFIG_FILE"
while IFS='=' read -r key value <&3; do
    # 跳过注释和空行
    [[ "$key" =~ ^#.*$ || -z "$key" ]] && continue
    
    # 通过变量名设置值
    declare "CONFIG_${key}=${value}"
done
exec 3<&-

echo "Loaded config: DB_HOST=$CONFIG_DB_HOST"
```

#### 日志分析器

```bash
#!/bin/bash
LOGFILE="${1:-/var/log/syslog}"

exec 3< "$LOGFILE"
exec 4> /tmp/log_stats.txt

echo "Log Analysis Report" >&4
echo "==================" >&4
echo "" >&4

declare -A LEVEL_COUNTS=()

while IFS= read -r line <&3; do
    # 提取日志级别
    if [[ "$line" =~ (DEBUG|INFO|WARN|ERROR|FATAL) ]]; then
        level="${BASH_REMATCH[1]}"
        ((LEVEL_COUNTS[$level]++))
    fi
done

# 写入统计
for level in DEBUG INFO WARN ERROR FATAL; do
    count=${LEVEL_COUNTS[$level]:-0}
    printf "%-8s: %d\n" "$level" "$count" >&4
done

exec 3<&- 4>&-
echo "Report saved to /tmp/log_stats.txt"
```

---

### 本章要点总结

- 管道 `|` 连接 stdout 到 stdin，子 shell 变量隔离
- `tee` 同时输出到屏幕和文件
- 重定向 `>` `>>` `<` `<<` `<<<` 控制数据流
- `exec` 替换当前进程或重定向文件描述符
- 自定义 fd 3+ 用于复杂数据处理
- `xargs` 将文本转换为命令参数，支持并行 `-P`

---

**上一章**：[[01_进程与信号：trap_前后台_信号处理|进程与信号]]
**下一章**：[[03_正则表达式：grep_sed_awk中的正则|正则表达式]]
