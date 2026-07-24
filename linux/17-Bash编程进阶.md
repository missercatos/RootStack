# 17 - Bash 编程进阶

> 掌握变量展开、进程替换、信号处理与健壮错误处理——将脚本从"能用"提升到"可靠"的关键进阶知识。

---

## 17.1 高级参数展开

### 提供默认值

```bash
# ${var:-default} — 如果 var 未设置或为空，使用 default（不修改变量本身）
username="${1:-admin}"
log_file="${LOG_FILE:-/var/log/app.log}"

# ${var:=default} — 如果未设置或为空，使用 default 并赋值给 var
: "${CONFIG_DIR:=/etc/myapp}"    # 给 CONFIG_DIR 赋默认值
: "${DEBUG:=0}"                   # : 是空命令，仅用来做展开

# ${var:?error_message} — 如果未设置或为空，输出错误并退出
api_key="${API_KEY:?错误: 请设置 API_KEY 环境变量}"
output_dir="${1:?用法: $0 <输出目录>}"

# ${var:+value} — 如果 var 已设置且非空，使用 value（否则为空）
debug_prefix="${DEBUG_ON:+"[DEBUG] "}"
echo "${debug_prefix}处理中..."
# DEBUG_ON 未设置时不输出前缀，设置时输出 "[DEBUG] 处理中..."
```

### 模式删除与替换

```bash
path="/usr/local/bin/script.sh"

# 删除前缀（# 最短匹配，## 最长匹配）
echo "${path#*/}"          # usr/local/bin/script.sh  （删除到第一个 /）
echo "${path##*/}"         # script.sh                 （删除到最后一个 /）

# 删除后缀（% 最短匹配，%% 最长匹配）
echo "${path%.*}"          # /usr/local/bin/script     （删除最后一个 . 及之后）
echo "${path%%.*}"         # /usr/local/bin/script     （同上）
echo "${path%/*}"          # /usr/local/bin            （删除最后一个 / 及之后）
echo "${path%%/*}"         # （空）                     （删除到第一个 / 及之后）

# 替换（/ 首个匹配，// 全部匹配）
url="http://example.com/path/to/page"
echo "${url/http/https}"                # https://example.com:8080/...
echo "${url//\//-}"                     # http:--example.com:8080-path-to-page

# 前后缀替换（# 开头，% 结尾）
filename="backup-2026-07-24.tar.gz"
echo "${filename/#backup/archive}"      # archive-2026-07-24.tar.gz
echo "${filename/%.tar.gz/.tgz}"        # backup-2026-07-24.tgz
echo "${filename/%24/25}"              # backup-2026-07-25.tar.gz
echo "${filename/#backup-/}"            # 2026-07-24.tar.gz

# 获取长度
echo "${#filename}"                     # 25

# 子字符串
echo "${filename:7:10}"                 # 2026-07-24

# 大小写转换
echo "${filename^^}"                    # BACKUP-2026-07-24.TAR.GZ
echo "${filename,,}"                    # backup-2026-07-24.tar.gz

# 位置参数展开
echo "${@:2}"          # 从第二个参数开始输出
echo "${@:2:3}"        # 从第二个参数开始取 3 个
echo "${@: -1}"        # 最后一个参数
```

### 间接引用

```bash
name="Alice"
var_name="name"
echo "${!var_name}"             # Alice（间接展开）

# 关联数组间接引用
declare -A config
config["host"]="localhost"
key="host"
echo "${config[$key]}"          # localhost

# 使用 nameref（Bash 4.3+）
declare -n ref="name"
echo "$ref"                     # Alice
name="Bob"
echo "$ref"                     # Bob
```

### 综合应用：配置解析函数

```bash
get_config() {
    local config_file="${1:-config.ini}"
    local key="$2"
    local default="${3:-}"

    if [ ! -f "$config_file" ]; then
        echo "${default}"
        return
    fi

    local value
    value=$(grep -E "^${key}=" "$config_file" | head -1 | sed "s/^${key}=//")
    echo "${value:-$default}"
}

# 使用
db_host=$(get_config "app.conf" "DB_HOST" "localhost")
db_port=$(get_config "app.conf" "DB_PORT" "5432")
```

---

## 17.2 关联数组深入

```bash
declare -A stats

# 批量赋值
stats=(
    ["total"]=0
    ["passed"]=0
    ["failed"]=0
    ["skipped"]=0
)

# 条件判断中使用
if [[ -z "${stats[total]}" ]]; then
    echo "尚未初始化"
fi

if [[ -v stats[passed] ]]; then
    echo "passed 键存在"
fi

# 嵌套使用场景：多维数据模拟
declare -A server_web01
server_web01=(
    ["ip"]="10.0.1.10"
    ["port"]="80"
    ["status"]="running"
)

declare -A server_db01
server_db01=(
    ["ip"]="10.0.2.10"
    ["port"]="5432"
    ["status"]="running"
)

# 统计脚本日志中的状态码分布
declare -A http_codes
while read -r line; do
    code=$(echo "$line" | awk '{print $9}')
    ((http_codes["$code"]++))
done < /var/log/nginx/access.log

echo "HTTP 状态码分布:"
for code in "${!http_codes[@]}"; do
    printf "  %3s: %d 次\n" "$code" "${http_codes[$code]}"
done | sort -n
```

---

## 17.3 子 Shell

### 圆括号 ( ) 与花括号 { } 的区别

```bash
# (command) — 在子 shell 中执行，变量修改不影响父 shell
result="外部值"
( result="内部值"; echo "$result" )    # 输出: 内部值
echo "$result"                           # 输出: 外部值  (未变!)

# { command; } — 在同一 shell 中执行，变量修改会保留
result="外部值"
{ result="内部值"; echo "$result"; }    # 输出: 内部值
echo "$result"                           # 输出: 内部值  (已修改!)

# 语法注意：花括号内的命令必须以分号或换行结尾，前后要有空格
{ echo "hello"; echo "world"; }          # 正确
{ echo "hello"; echo "world";}           # 花括号前必须有空格

# 子 shell 的常见用法

# 1. 临时切换目录
(cd /tmp && ls -la)
echo "$(pwd)"                            # 仍在原目录

# 2. 组合多个命令的输出
output=$( (echo "开始"; ls; echo "结束") )

# 3. 批量环境变量修改
(export PATH="/custom/bin:$PATH"; which mytool)

# 4. 使用 umask
(umask 077; touch secret_file)
```

### 子 shell 的性能考虑

```bash
# 不推荐：频繁创建子 shell（尤其在循环中）
for i in {1..1000}; do
    count=$(cat file.txt | wc -l)         # 每次创建一个子 shell
done

# 推荐：减少子 shell 创建
count=$(wc -l < file.txt)                 # 只创建一次
for i in {1..1000}; do
    echo "$count"
done

# 管道中的每一段默认都在子 shell 中执行
# 这会导致 while 循环中的变量修改丢失！
count=0
cat /etc/passwd | while read -r line; do
    ((count++))
done
echo "$count"   # 0！！！在管道右侧的 while 在子 shell 中，修改不保存

# 解决方案：进程替换
while read -r line; do
    ((count++))
done < <(cat /etc/passwd)
echo "$count"   # 正确输出
```

---

## 17.4 进程替换

```bash
# <(command) — 将命令输出作为文件
# >(command) — 将文件内容作为命令输入

# 比较两个命令的输出（无需临时文件）
diff <(ls /etc) <(ls /usr/local/etc)

# 逐行处理命令输出（避免管道导致的变量作用域问题）
while IFS= read -r line; do
    process_line "$line"
done < <(grep "ERROR" /var/log/app.log)

# 同时将数据发送到多个命令
echo "data" | tee >(gzip > data.gz) >(bzip2 > data.bz2) > /dev/null

# 合并两个排序文件
comm <(sort file1.txt) <(sort file2.txt)

# 比较两个命令的退出码（在子 shell 中运行）
diff <(ssh host1 cat /etc/hosts) <(ssh host2 cat /etc/hosts)

# 将 stderr 也通过进程替换
command 2> >(tee error.log)
```

---

## 17.5 Trap — 信号捕获与清理

```bash
#!/bin/bash

declare temp_dir

cleanup() {
    local exit_code=$?
    echo "清理临时文件..."
    rm -rf "$temp_dir" 2>/dev/null
    echo "脚本退出，退出码: $exit_code"
    exit $exit_code
}

# 注册 trap（脚本退出、中断或终止时执行 cleanup）
trap cleanup EXIT SIGINT SIGTERM

temp_dir=$(mktemp -d -t "myapp.XXXXXX")
echo "临时目录: $temp_dir"

# 主逻辑
echo "处理中（按 Ctrl+C 中断）..."
sleep 30
echo "处理完成"

# EXIT 信号即使正常退出也会触发
# SIGINT  = Ctrl+C (2)
# SIGTERM = kill 默认信号 (15)
# SIGHUP  = 终端关闭 (1)
# SIGQUIT = Ctrl+\ (3)
```

### 常用信号列表

```bash
# 使用 trap -l 查看所有信号
# 常见信号:
#  1  SIGHUP    挂起（终端断开）
#  2  SIGINT    中断（Ctrl+C）
#  3  SIGQUIT   退出（Ctrl+\）
#  9  SIGKILL   强制终止（无法捕获）
# 15  SIGTERM   终止（kill 默认）
# 17  SIGCHLD   子进程状态改变
# 19  SIGSTOP   暂停（无法捕获）
# 18  SIGCONT   继续执行
#  0  EXIT      Shell 退出（Bash 特有，非 POSIX）

# trap 示例：重新读取配置
reload_config() {
    echo "收到 SIGHUP，重新加载配置..."
    source /etc/myapp/config
}
trap reload_config SIGHUP

# DEBUG trap：每条命令执行前触发（调试用）
trap 'echo "执行: $BASH_COMMAND"' DEBUG

# ERR trap：命令失败时触发（需 set -e 或直接 trap ERR）
trap 'echo "第 $LINENO 行出错: $BASH_COMMAND"' ERR

# RETURN trap：函数或 source 返回时触发
myfunc() {
    trap 'echo "myfunc 返回"' RETURN
    echo "函数执行中..."
}
myfunc
```

---

## 17.6 调试技巧

```bash
# 方法一：set -x（最常用）
set -x                    # 开启追踪
critical_operation
set +x                    # 关闭追踪

# 自定义 PS4 显示更多信息
export PS4='+ ${BASH_SOURCE:-$0}:${LINENO:-0}:${FUNCNAME[0]:+${FUNCNAME[0]}()} '

# 方法二：set -v（打印执行的原始行）
set -v

# 方法三：bash -n（语法检查，不执行）
bash -n script.sh

# 方法四：bash -x（执行并追踪）
bash -x script.sh

# 方法五：使用 DEBUG trap 记录每条命令
trap 'printf "[%(%T)T] %s:%d %s\n" -1 "${BASH_SOURCE[0]}" "$LINENO" "$BASH_COMMAND"' DEBUG

# 方法六：局部调试
_debug() {
    [ "${DEBUG:-0}" = "1" ] && echo "[DEBUG] $*" >&2
}
_debug "变量 x 的值: $x"

# 方法七：bashdb（Bash 调试器，类似 gdb）
# yay -S bashdb  # 安装
# bashdb script.sh

# 常见调试技巧
# 1. 打印变量值
echo "变量 x 的值: '${x}' (长度: ${#x})" >&2

# 2. 显示调用栈
print_stack() {
    local i
    for ((i = 0; i < ${#FUNCNAME[@]}; i++)); do
        echo "  [$i] ${FUNCNAME[$i]} — ${BASH_SOURCE[$i]:-$0}:${BASH_LINENO[$i-1]:-0}"
    done
}
```

---

## 17.7 信号处理最佳实践

```bash
#!/bin/bash

# 完整的信号处理脚本模板
set -euo pipefail

readonly PID_FILE="/var/run/mydaemon.pid"
readonly LOCK_FILE="/var/run/mydaemon.lock"

shutdown() {
    echo "[INFO] 收到关闭信号，执行优雅退出..."
    if [ -f "$PID_FILE" ]; then
        local pid
        pid=$(cat "$PID_FILE")
        kill -TERM "$pid" 2>/dev/null || true
    fi
    rm -f "$LOCK_FILE" "$PID_FILE"
    exit 0
}

# 只捕获 TERM 和 INT，不覆盖 EXIT（避免干扰正常退出逻辑）
trap shutdown SIGTERM SIGINT

# 创建锁文件防止多实例
if [ -f "$LOCK_FILE" ]; then
    echo "[ERROR] 另一个实例正在运行"
    exit 1
fi
echo $$ > "$LOCK_FILE"

# 记录 PID
echo $$ > "$PID_FILE"

# 后台任务管理
declare -a pids
for i in 1 2 3; do
    (
        sleep $((RANDOM % 10 + 1))
        echo "Worker $i 完成"
    ) &
    pids+=($!)
done

# 传递信号给子进程
propagate_signal() {
    local sig="$1"
    for pid in "${pids[@]}"; do
        kill "-$sig" "$pid" 2>/dev/null || true
    done
}
trap 'propagate_signal TERM' SIGTERM SIGINT

# 等待所有子进程
wait_for_all() {
    local failed=0
    for pid in "${pids[@]}"; do
        if ! wait "$pid"; then
            failed=1
        fi
    done
    return $failed
}

wait_for_all
```

---

## 17.8 临时文件管理

```bash
# mktemp — 安全创建临时文件/目录

# 创建临时文件
tmpfile=$(mktemp)
echo "临时文件: $tmpfile"           # 例如: /tmp/tmp.XXXXXX

# 创建指定后缀的临时文件
tmpfile=$(mktemp --suffix=.json)
echo "临时文件: $tmpfile"           # /tmp/tmp.XXXXXX.json

# 创建临时目录
tmpdir=$(mktemp -d -t "myapp.XXXXXX")
echo "临时目录: $tmpdir"            # /tmp/myapp.XXXXXX

# 在指定目录创建
tmpfile=$(mktemp -p /var/tmp app_XXXXXX)

# 安全模式（只有创建者可读写）
# mktemp 默认权限 600，目录为 700

# 推荐的清理模式
cleanup_temp() {
    local exit_code=$?
    if [ -n "${tmpdir:-}" ] && [ -d "$tmpdir" ]; then
        rm -rf "$tmpdir"
        echo "[CLEANUP] 已删除临时目录"
    fi
    exit $exit_code
}

tmpdir=$(mktemp -d -t "script.XXXXXX")
trap cleanup_temp EXIT SIGINT SIGTERM

# 实际使用
config_file="$tmpdir/config"
data_file="$tmpdir/data.json"
echo '{"key": "value"}' > "$data_file"

# 使用 fd 操作临时文件（更安全）
exec 3> >(gzip > "$tmpdir/output.gz")
echo "压缩数据" >&3
exec 3>&-
```

---

## 17.9 getopts — 命令行选项解析

```bash
#!/bin/bash

usage() {
    cat << 'EOF'
用法: $0 [选项] <文件>

选项:
    -h          显示此帮助信息
    -v          详细输出模式
    -o FILE     指定输出文件
    -n NUM      最大处理数量
    -d          调试模式

示例:
    $0 -v -o result.txt -n 100 data.csv
EOF
    exit 1
}

# 初始化默认值
verbose=0
output_file=""
max_count=0
debug=0

while getopts ":hvo:n:d" opt; do
    case "$opt" in
        h) usage ;;
        v) verbose=1 ;;
        o) output_file="$OPTARG" ;;
        n)
            if ! [[ "$OPTARG" =~ ^[0-9]+$ ]]; then
                echo "错误: -n 需要正整数参数" >&2
                exit 1
            fi
            max_count="$OPTARG"
            ;;
        d) debug=1 ;;
        :)
            echo "错误: 选项 -$OPTARG 需要一个参数" >&2
            usage
            ;;
        \?)
            echo "错误: 未知选项 -$OPTARG" >&2
            usage
            ;;
    esac
done

shift $((OPTIND - 1))   # 移除已处理的选项，剩下位置参数

# 检查剩余参数
if [ $# -eq 0 ]; then
    echo "错误: 需要指定输入文件" >&2
    usage
fi

input_file="$1"

# 使用解析结果
echo "输入文件: $input_file"
[ "$verbose" -eq 1 ] && echo "详细模式已启用"
[ -n "$output_file" ] && echo "输出文件: $output_file"
[ "$max_count" -gt 0 ] && echo "最大处理: $max_count"
[ "$debug" -eq 1 ] && echo "调试模式已启用"
```

---

## 17.10 Here Document 和 Here String

### Here Document

```bash
# 基本用法
cat << 'EOF'
这是多行文本
不会进行变量展开
$HOME 和 $(date) 都是原样输出
EOF

# 使用变量展开（不加引号）
user="root"
cat << ENDMSG
用户 $user 的家目录是 $HOME
当前时间: $(date)
ENDMSG

# 抑制前导 Tab（使用 <<- 配合无缩进的结束标记）
if [ "$debug" = "1" ]; then
    cat <<- 'DEBUG'
        调试信息:
        第1行
        第2行
    DEBUG
fi

# 将 heredoc 赋值给变量
config=$(cat << 'CONFIG'
server {
    listen 80;
    server_name localhost;
}
CONFIG
)

# 写入文件
sudo tee /etc/nginx/conf.d/myapp.conf << 'NGINX_CONF'
server {
    listen 8080;
    root /var/www/myapp;
    index index.html;
}
NGINX_CONF

# 输出到命令（管道）
cat << 'SQL' | mysql -u root -p
CREATE DATABASE IF NOT EXISTS mydb;
USE mydb;
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100)
);
SQL
```

### Here String

```bash
# <<< 将字符串作为标准输入
grep "root" <<< "$(cat /etc/passwd)"

# 读取变量作为输入
read -r first second <<< "Hello World"
echo "$first"   # Hello
echo "$second"  # World

# 用 IFS 分割复杂字符串
IFS=':' read -r user pass uid gid gecos home shell <<< "$(getent passwd root)"
echo "用户: $user, Shell: $shell, UID: $uid"

# 处理数组
arr=("apple" "banana" "cherry")
command <<< "${arr[*]}"
```

---

## 17.11 命名管道（FIFO）

```bash
# 创建
mkfifo /tmp/myfifo
# 或
mknod /tmp/myfifo p

# 使用示例 1：简单进程通信
# 终端 1:
mkfifo /tmp/chat
while read -r msg < /tmp/chat; do
    echo "收到: $msg"
done

# 终端 2:
echo "Hello!" > /tmp/chat

# 使用示例 2：并行处理
mkfifo /tmp/pipe1 /tmp/pipe2

# 启动两个消费者
grep "ERROR" /tmp/pipe1 > errors.log &
grep "WARN" /tmp/pipe2 > warnings.log &

# 启动生产者
tee /tmp/pipe1 /tmp/pipe2 < /var/log/app.log

# 清理
rm -f /tmp/pipe1 /tmp/pipe2
wait

# 使用示例 3：控制并发数
# 通过 FIFO 实现信号量控制
concurrent_jobs=3
job_queue=$(mktemp -u)

mkfifo "$job_queue"
exec 3<>"$job_queue"

for ((i = 0; i < concurrent_jobs; i++)); do
    echo >&3
done

for task in task_{1..10}; do
    read -r -u3                          # 获取令牌
    (
        echo "处理 $task..."
        sleep $((RANDOM % 5 + 1))
        echo "完成 $task"
        echo >&3                         # 归还令牌
    ) &
done
wait
rm -f "$job_queue"
```

---

## 17.12 并行执行

```bash
# 方法一：后台运行 + wait
echo "开始并行任务..."
for server in web01 web02 web03 db01 db02; do
    (
        echo "部署到 $server..."
        ssh "$server" 'sudo systemctl restart nginx'
        echo "$server 部署完成"
    ) &
done
echo "等待所有任务完成..."
wait
echo "全部完成!"

# 方法二：xargs -P 并行
echo "web01 web02 web03 db01" | tr ' ' '\n' | \
    xargs -P 4 -I {} ssh {} 'sudo systemctl restart nginx'

# 方法三：控制并发数（带令牌桶）
max_jobs=4
running=0
declare -a pids=()

start_job() {
    local cmd="$1"
    if [ $running -ge $max_jobs ]; then
        wait -n                          # 等待任意一个完成
        ((running--))
    fi
    eval "$cmd" &
    pids+=($!)
    ((running++))
}

for i in {1..20}; do
    start_job "echo 处理任务 $i; sleep $((RANDOM % 3 + 1))"
done
wait

# 方法四：GNU Parallel（功能最强大）
# parallel -j 4 gzip ::: *.log
# parallel -j 10 'ssh {} "uptime"' ::: server{1..50}
# parallel --bar -j 4 'sleep {}; echo done {}' ::: 1 2 3 4 5
```

---

## 17.13 脚本性能优化

```bash
# 1. 避免在循环中使用管道和外部命令
# 坏:
for file in *.txt; do
    lines=$(cat "$file" | wc -l)
done

# 好:
for file in *.txt; do
    lines=$(wc -l < "$file")
done

# 更好（一次调用）:
wc -l *.txt

# 2. 使用内置命令代替外部命令
# 使用 [[ ]] 代替 [ ]（内置 vs 外部 test）
# 使用 $(( )) 代替 expr
# 使用 "${str#*/}" 代替 basename
# 使用 "${str%/*}" 代替 dirname
# 使用 "${str/old/new}" 代替 sed（简单替换）
# 使用 read -r line 代替 head -1

# 3. 减少子 shell 创建
# 坏: echo "$(echo "$(echo nested)")"
# 好: 直接使用变量

# 4. 批量 I/O 操作
# 坏:
while read -r line; do
    echo "$line" >> output.txt
done < input.txt

# 好:
while read -r line; do
    printf '%s\n' "$line"
done < input.txt > output.txt           # 一次重定向

# 5. 使用 case 代替多个 if-elif
# case 是内置的，比 if-elif 链更快

# 6. 缓存重复计算结果
# 坏: for i in {1..100}; do echo $(date +%s); done
# 好: ts=$(date +%s); for i in {1..100}; do echo "$ts"; done

# 7. 使用关联数组做查表，而非多次 grep
declare -A config
while IFS='=' read -r key value; do
    config["$key"]="$value"
done < config.ini
# 之后直接用 ${config[key]} 查询
```

---

## 17.14 编写健壮脚本的原则

```bash
#!/bin/bash
# 健壮脚本模板

# === 1. 严格模式 ===
set -euo pipefail
IFS=$'\n\t'

# === 2. 常量定义（只读） ===
readonly SCRIPT_NAME="$(basename "$0")"
readonly SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
readonly CONFIG_FILE="${HOME}/.config/myapp/config"

# === 3. 函数优先定义 ===
log_info()  { echo "[INFO]  $(date '+%Y-%m-%d %H:%M:%S') $*"; }
log_error() { echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') $*" >&2; }
log_debug() { [ "${DEBUG:-0}" = "1" ] && echo "[DEBUG] $(date '+%Y-%m-%d %H:%M:%S') $*"; }

die() {
    log_error "$@"
    exit 1
}

assert_command_exists() {
    command -v "$1" >/dev/null 2>&1 || die "需要 $1 但未安装"
}

# === 4. 依赖检查 ===
assert_command_exists "curl"
assert_command_exists "jq"

# === 5. 参数验证 ===
validate_args() {
    if [ $# -lt 1 ]; then
        die "用法: $SCRIPT_NAME <必需参数> [可选参数]"
    fi
}

# === 6. 锁机制防止并发 ===
readonly LOCK_FILE="/tmp/${SCRIPT_NAME}.lock"
acquire_lock() {
    exec 200>"$LOCK_FILE"
    if ! flock -n 200; then
        die "另一个 $SCRIPT_NAME 实例正在运行"
    fi
}

# === 7. 清理 ===
cleanup() {
    local exit_code=$?
    log_info "清理中..."
    rm -f "$LOCK_FILE"
    [ -n "${temp_dir:-}" ] && rm -rf "$temp_dir"
    exit $exit_code
}
trap cleanup EXIT SIGINT SIGTERM

# === 8. 临时目录 ===
temp_dir=$(mktemp -d -t "${SCRIPT_NAME}.XXXXXX")

# === 9. 主逻辑 ===
main() {
    validate_args "$@"
    acquire_lock
    log_info "脚本开始执行"

    # 你的逻辑放这里

    log_info "脚本执行完成"
}

main "$@"
```

### 常见健壮性 Checklist

| 检查项 | 说明 |
|--------|------|
| `set -euo pipefail` | 遇错即停，防止未定义变量，管道错误传播 |
| 锁文件 | 防止多实例并发执行 |
| 临时文件清理 | trap EXIT 确保清理 |
| 参数验证 | 检查必需参数是否存在，格式是否正确 |
| 依赖检查 | 确保外部命令可用 |
| 日志输出 | 区分 INFO/WARN/ERROR，包含时间戳 |
| 输出到 stderr | 错误消息和提示输出到 >&2 |
| 权限检查 | 如需要 root，在开头检查 |
| `$HOME` 容错 | 使用 `${HOME:-/tmp}` 防止 HOME 未定义 |
| 路径安全 | 始终用双引号包裹路径，防止空格问题 |

---

> **延伸阅读**: [[16-Bash编程基础]] 涵盖变量、循环与函数等核心语法。[[20-Shell脚本实战]] 提供生产级脚本编写示例。[[18-正则与文本处理三剑客]] 深入文本处理工具。
