# 20 - Shell 脚本实战

> 本章将前面学到的 Bash 知识应用于实际系统管理场景。每个范例包含完整脚本和逐段解析，可直接使用或在此基础上定制。

---

## 20.1 系统健康检查脚本

### 需求

定期检查服务器的 CPU、内存、磁盘、网络、进程是否正常，生成简要健康报告。

### 完整脚本

```bash
#!/bin/bash
# system_health.sh — 系统健康检查
set -euo pipefail

readonly SCRIPT_NAME="$(basename "$0")"
readonly REPORT_FILE="/tmp/system_health_$(date +%Y%m%d_%H%M%S).txt"

# 颜色输出
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m'  # No Color

check_ok()   { echo -e "  ${GREEN}[✓]${NC} $*"; }
check_warn() { echo -e "  ${YELLOW}[!]${NC} $*"; }
check_fail() { echo -e "  ${RED}[✗]${NC} $*"; }

# --- 1. CPU ---
check_cpu() {
    echo "━━━ CPU ━━━"
    local cpu_usage
    cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print 100 - $8}' | cut -d'%' -f1)
    local load
    load=$(uptime | awk -F'load average: ' '{print $2}' | cut -d',' -f1)

    echo "  当前使用率: ${cpu_usage}%"
    echo "  1 分钟负载: ${load}"

    if (( $(echo "$cpu_usage > 90" | bc -l) )); then
        check_fail "CPU 使用率过高 (>90%)"
    elif (( $(echo "$cpu_usage > 70" | bc -l) )); then
        check_warn "CPU 使用率偏高 (>70%)"
    else
        check_ok "CPU 使用率正常"
    fi
}

# --- 2. 内存 ---
check_memory() {
    echo "━━━ 内存 ━━━"
    local total used free avail percent
    read -r total used free shared buff_cache avail <<< \
        $(free -m | awk '/^Mem:/{print $2, $3, $4, $5, $6, $7}')

    local percent_used=$(( used * 100 / total ))

    echo "  总计: ${total}MB  已用: ${used}MB  可用: ${avail}MB"
    echo "  使用率: ${percent_used}%"

    if [ "$percent_used" -gt 95 ]; then
        check_fail "内存几乎用尽 (>95%)"
    elif [ "$percent_used" -gt 80 ]; then
        check_warn "内存使用偏高 (>80%)"
    else
        check_ok "内存使用正常"
    fi
}

# --- 3. 磁盘 ---
check_disk() {
    echo "━━━ 磁盘 ━━━"
    local has_issue=0
    while IFS= read -r line; do
        local fs used_percent mount
        fs=$(echo "$line" | awk '{print $1}')
        used_percent=$(echo "$line" | awk '{print $5}' | tr -d '%')
        mount=$(echo "$line" | awk '{print $6}')

        printf "  %-20s %-15s" "$fs" "$mount"

        if [ "$used_percent" -gt 95 ]; then
            echo " 使用 ${used_percent}%"
            check_fail "分区 $mount 几乎用尽 (${used_percent}%)"
            has_issue=1
        elif [ "$used_percent" -gt 80 ]; then
            echo " 使用 ${used_percent}%"
            check_warn "分区 $mount 使用率偏高 (${used_percent}%)"
        else
            echo " 使用 ${used_percent}%"
            check_ok "分区 $mount 正常"
        fi
    done < <(df -h | grep -E '^/dev/' | grep -vE '/(boot|efi)')

    return $has_issue
}

# --- 4. 服务 ---
check_services() {
    echo "━━━ 关键服务 ━━━"
    local services=("sshd" "nginx" "docker" "cron" "systemd-journald")
    for svc in "${services[@]}"; do
        if systemctl is-active --quiet "$svc" 2>/dev/null; then
            check_ok "$svc 运行中"
        else
            check_warn "$svc 未运行或未安装"
        fi
    done
}

# --- 5. 网络 ---
check_network() {
    echo "━━━ 网络 ━━━"

    # 连通性测试
    if ping -c 1 -W 2 8.8.8.8 > /dev/null 2>&1; then
        check_ok "外网连通 (8.8.8.8)"
    else
        check_fail "外网不通 (8.8.8.8)"
    fi

    # 端口监听
    echo "  监听端口:"
    ss -tlnp 2>/dev/null | awk 'NR>1{printf "    %-5s %-20s\n", $4, $NF}' | head -10

    # TCP 连接统计
    local established time_wait close_wait
    established=$(ss -tan | grep -c ESTAB || true)
    time_wait=$(ss -tan | grep -c TIME-WAIT || true)
    close_wait=$(ss -tan | grep -c CLOSE-WAIT || true)
    echo "  TCP: ESTAB=$established  TIME-WAIT=$time_wait  CLOSE-WAIT=$close_wait"
}

# --- 6. 最近错误 ---
check_recent_errors() {
    echo "━━━ 近期系统错误 ━━━"
    local journal_errors
    journal_errors=$(journalctl -p 3 -xb --no-pager -n 5 2>/dev/null || true)
    if [ -n "$journal_errors" ]; then
        echo "$journal_errors" | while read -r line; do
            echo "  $line"
        done
    else
        check_ok "无近期严重错误"
    fi
}

# --- 主流程 ---
main() {
    cat << 'HEADER'
╔═══════════════════════════════════╗
║       系统健康检查报告            ║
╚═══════════════════════════════════╝
HEADER
    echo "主机名: $(hostname)"
    echo "内核:   $(uname -r)"
    echo "时间:   $(date '+%Y-%m-%d %H:%M:%S')"
    echo "运行:   $(uptime -p)"
    echo ""

    check_cpu
    echo ""
    check_memory
    echo ""
    check_disk
    echo ""
    check_services
    echo ""
    check_network
    echo ""
    check_recent_errors

    echo ""
    echo "报告已保存至: $REPORT_FILE"
}

main | tee "$REPORT_FILE"
```

### 逐段解析

| 部分 | 说明 |
|------|------|
| `set -euo pipefail` | 严格模式，遇错即停 |
| 颜色变量 | ANSI 转义码，提升可读性 |
| `check_ok/warn/fail` | 统一的状态输出函数 |
| `check_cpu` | 用 `top -bn1` 获取实时 CPU，`awk` 计算非空闲比例 |
| `check_memory` | 从 `free -m` 解析，使用 `read` 多变量赋值 |
| `check_disk` | 只关注 `/dev/` 设备分区，排除 boot/efi |
| `check_services` | 用 `systemctl is-active` 批量检查服务 |
| `check_network` | ping 测外网，`ss` 查看端口和 TCP 状态 |
| `check_recent_errors` | `journalctl -p 3` 提取严重日志 |
| `main \| tee` | 输出到终端的同时保存为文件 |

---

## 20.2 日志轮转脚本

### 需求

对应用日志进行每日自动轮转，保留最近 N 天的日志，超期自动删除。

### 完整脚本

```bash
#!/bin/bash
# log_rotate.sh — 日志轮转

set -euo pipefail

readonly LOG_DIR="${1:-/var/log/myapp}"
readonly RETENTION_DAYS="${2:-7}"
readonly MAX_LOG_SIZE_MB="${3:-100}"

# 创建日志目录
mkdir -p "$LOG_DIR"

rotate_log() {
    local log_file="$1"

    # 如果日志为空或不存在，跳过
    if [ ! -s "$log_file" ]; then
        return
    fi

    local base_name
    base_name="$(basename "$log_file")"
    local date_suffix
    date_suffix=$(date +%Y%m%d_%H%M%S)
    local rotated="${log_file}.${date_suffix}.gz"

    # 压缩并轮转
    if gzip -c "$log_file" > "$rotated"; then
        : > "$log_file"         # 清空原文件（不删除，防止 fd 丢失）
        echo "[ROTATE] $log_file → $rotated ($(du -h "$rotated" | cut -f1))"
    else
        echo "[ERROR] 轮转 $log_file 失败" >&2
        return 1
    fi
}

cleanup_old_logs() {
    echo "[CLEANUP] 清理 ${RETENTION_DAYS} 天前的日志..."

    find "$LOG_DIR" -name "*.gz" -type f -mtime "+${RETENTION_DAYS}" \
        -print0 | while IFS= read -r -d '' old_log; do
        rm -f "$old_log"
        echo "  已删除: $old_log"
    done
}

check_size_rotation() {
    for log_file in "$LOG_DIR"/*.log; do
        [ -f "$log_file" ] || continue

        local size_mb
        size_mb=$(du -m "$log_file" | cut -f1)

        if [ "$size_mb" -gt "$MAX_LOG_SIZE_MB" ]; then
            echo "[SIZE] $log_file 超过 ${MAX_LOG_SIZE_MB}MB (当前: ${size_mb}MB)，触发轮转"
            rotate_log "$log_file"
        fi
    done
}

main() {
    echo "=== 日志轮转 $(date '+%Y-%m-%d %H:%M:%S') ==="
    echo "日志目录: $LOG_DIR"
    echo "保留天数: $RETENTION_DAYS"
    echo "大小阈值: ${MAX_LOG_SIZE_MB}MB"
    echo ""

    # 按大小检查轮转
    check_size_rotation

    # 也按日期轮转所有非空日志（每日一次）
    for log_file in "$LOG_DIR"/*.log; do
        [ -f "$log_file" ] || continue
        rotate_log "$log_file"
    done

    # 清理旧日志
    cleanup_old_logs

    echo "轮转完成"
}

main "$@"
```

### 逐段解析

| 部分 | 说明 |
|------|------|
| 参数默认值 | `${1:-default}` 提供默认配置 |
| `rotate_log` | 用 `gzip -c` 压缩后 `: >` 清空原文件，保留 fd |
| `cleanup_old_logs` | `find -mtime -print0 \| xargs -0` 安全处理文件名 |
| `check_size_rotation` | `du -m` 检查大小，超阈值触发轮转 |
| `: > "$log_file"` | 空命令重定向：清空文件但不中断写入的进程 |

---

## 20.3 备份自动化脚本

### 需求

定时备份指定目录，支持增量备份，远程同步，邮件通知。

### 完整脚本

```bash
#!/bin/bash
# backup.sh — 目录备份

set -euo pipefail

readonly BACKUP_SRC="${BACKUP_SRC:-/var/www /etc/nginx /etc/myapp}"
readonly BACKUP_DST="${BACKUP_DST:-/backup}"
readonly BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S)"
readonly RETENTION_COUNT="${RETENTION_COUNT:-7}"
readonly REMOTE_HOST="${REMOTE_HOST:-}"        # user@host:/path
readonly SNAPSHOT_FILE="$BACKUP_DST/latest.snar"

log()  { echo "[$(date '+%H:%M:%S')] $*"; }
error() { echo "[$(date '+%H:%M:%S')] [ERROR] $*" >&2; }

# 检查备份目录
init_backup() {
    mkdir -p "$BACKUP_DST"

    if [ ! -w "$BACKUP_DST" ]; then
        error "备份目录 $BACKUP_DST 不可写"
        exit 1
    fi
}

# 执行 tar 增量备份
do_backup() {
    local archive="$BACKUP_DST/${BACKUP_NAME}.tar.gz"
    local snapshot="$SNAPSHOT_FILE"

    log "开始备份: $BACKUP_SRC"

    if [ -f "$snapshot" ]; then
        log "使用增量模式（基于已有快照）"
        local incremental="${BACKUP_DST}/${BACKUP_NAME}_inc.tar.gz"
        if tar -czf "$incremental" \
            --listed-incremental="$snapshot" \
            --warning=no-file-changed \
            $BACKUP_SRC 2>/dev/null; then
            local size
            size=$(du -h "$incremental" | cut -f1)
            log "增量备份完成: $incremental ($size)"
            echo "$incremental"
            return 0
        else
            error "增量备份失败，回退到全量"
        fi
    fi

    # 全量备份
    log "执行全量备份..."
    if tar -czf "$archive" \
        --listed-incremental="$snapshot" \
        $BACKUP_SRC 2>/dev/null; then
        local size
        size=$(du -h "$archive" | cut -f1)
        log "全量备份完成: $archive ($size)"
        echo "$archive"
    else
        error "全量备份失败"
        exit 1
    fi
}

# 远程同步
sync_remote() {
    if [ -z "$REMOTE_HOST" ]; then
        log "未配置远程主机，跳过远程同步"
        return
    fi

    log "同步到远程: $REMOTE_HOST"
    if rsync -avz --delete "$BACKUP_DST/" "$REMOTE_HOST" 2>&1; then
        log "远程同步完成"
    else
        error "远程同步失败"
    fi
}

# 清理旧备份
cleanup_old() {
    log "清理旧备份（保留最近 $RETENTION_COUNT 份）..."

    local count
    count=$(find "$BACKUP_DST" -name "backup_*.tar.gz" -type f | wc -l)

    if [ "$count" -gt "$RETENTION_COUNT" ]; then
        find "$BACKUP_DST" -name "backup_*.tar.gz" -type f \
            | sort \
            | head -n "-$RETENTION_COUNT" \
            | while read -r old; do
            rm -f "$old"
            log "  删除: $old"
        done
    fi

    # 也清理旧的增量备份
    find "$BACKUP_DST" -name "backup_*_inc.tar.gz" -type f -mtime +${RETENTION_COUNT} -delete
}

# 备份校验
verify_backup() {
    local archive="$1"
    if [ ! -f "$archive" ]; then
        error "备份文件不存在: $archive"
        return 1
    fi

    log "校验备份完整性: $archive"
    if gzip -t "$archive" 2>/dev/null; then
        log "备份校验通过 ✓"
    elif tar -tzf "$archive" >/dev/null 2>&1; then
        log "备份校验通过 ✓"
    else
        error "备份校验失败 ✗"
        return 1
    fi
}

main() {
    log "══════ 备份任务开始 ══════"

    init_backup

    local latest_backup
    latest_backup=$(do_backup)

    verify_backup "$latest_backup"

    sync_remote

    cleanup_old

    log "══════ 备份任务完成 ══════"
}

main "$@"
```

### 逐段解析

| 部分 | 说明 |
|------|------|
| `--listed-incremental` | GNU tar 增量备份：首次创建 snapshot 文件，之后只备份变更 |
| 增量回退 | 增量失败时自动回退到全量备份 |
| `rsync -avz --delete` | 远程镜像同步，`--delete` 删除远程多余文件 |
| 保留策略 | `head -n "-$N"` 保留最新的 N 份 |
| 校验 | `gzip -t` 和 `tar -tzf` 双重校验压缩包 |

---

## 20.4 服务监控与告警脚本

### 需求

监控关键服务的可用性（HTTP 端点和进程），异常时发送告警。

### 完整脚本

```bash
#!/bin/bash
# monitor.sh — 服务监控

set -euo pipefail

readonly CONFIG_FILE="${MONITOR_CONFIG:-/etc/monitor/targets.conf}"
readonly ALERT_SCRIPT="${ALERT_SCRIPT:-/usr/local/bin/send_alert.sh}"
readonly LOCK_FILE="/tmp/monitor.lock"
readonly STATE_FILE="/tmp/monitor_state.txt"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

# 锁机制
if [ -f "$LOCK_FILE" ]; then
    log "检测到另一个监控实例运行中，退出"
    exit 0
fi
echo $$ > "$LOCK_FILE"
trap 'rm -f "$LOCK_FILE"' EXIT

# 默认监控目标
declare -A targets=(
    ["nginx"]="http://localhost:80/health|200"
    ["api"]="http://localhost:8080/api/ping|200"
    ["ssh"]="tcp://localhost:22"
    ["db"]="tcp://localhost:5432"
)

# 如果配置文件存在，从文件加载
if [ -f "$CONFIG_FILE" ]; then
    declare -A loaded_targets
    while IFS='=' read -r name url; do
        [[ "$name" =~ ^# ]] && continue
        [ -z "$name" ] && continue
        loaded_targets["$name"]="$url"
    done < "$CONFIG_FILE"
    for key in "${!loaded_targets[@]}"; do
        targets["$key"]="${loaded_targets[$key]}"
    done
fi

# 加载之前的状态
declare -A prev_state
if [ -f "$STATE_FILE" ]; then
    while IFS='=' read -r name state; do
        prev_state["$name"]="$state"
    done < "$STATE_FILE"
fi

# 检查 HTTP 端点
check_http() {
    local name="$1"
    local url="$2"
    local expected_code="${3:-200}"
    local timeout=${4:-5}

    local http_code
    http_code=$(curl -s -o /dev/null -w '%{http_code}' \
        --connect-timeout "$timeout" --max-time "$timeout" "$url" 2>/dev/null || echo "000")

    if [ "$http_code" = "$expected_code" ]; then
        echo "OK"
        return 0
    else
        echo "FAIL (期望 $expected_code, 实际 $http_code)"
        return 1
    fi
}

# 检查 TCP 端口
check_tcp() {
    local name="$1"
    local host="$2"
    local port="$3"
    local timeout=${4:-3}

    if timeout "$timeout" bash -c "echo > /dev/tcp/$host/$port" 2>/dev/null; then
        echo "OK"
        return 0
    else
        echo "FAIL (无连接)"
        return 1
    fi
}

# 发送告警
send_alert() {
    local name="$1"
    local status="$2"
    local message="$3"

    log "[ALERT] $name → $status: $message"

    if [ -x "$ALERT_SCRIPT" ]; then
        "$ALERT_SCRIPT" "$name" "$status" "$message"
    fi
}

# 主检查逻辑
check_targets() {
    local has_issue=0

    for name in "${!targets[@]}"; do
        local target="${targets[$name]}"
        local result=""

        if [[ "$target" =~ ^https?:// ]]; then
            local url="${target%%|*}"
            local expected="${target##*|}"
            [ "$expected" = "$target" ] && expected="200"
            result=$(check_http "$name" "$url" "$expected")
        elif [[ "$target" =~ ^tcp:// ]]; then
            local host_port="${target#tcp://}"
            local host="${host_port%%:*}"
            local port="${host_port##*:}"
            result=$(check_tcp "$name" "$host" "$port")
        else
            log "[WARN] 未知协议: $target"
            continue
        fi

        local prev="${prev_state[$name]:-OK}"
        echo "$name=$result" >> "${STATE_FILE}.tmp"

        if [ "$result" != "OK" ]; then
            if [ "$prev" = "OK" ]; then
                # 状态变更：OK → FAIL
                send_alert "$name" "DOWN" "$result"
            fi
            has_issue=1
        elif [ "$result" = "OK" ] && [ "$prev" != "OK" ]; then
            # 状态变更：FAIL → OK（恢复）
            send_alert "$name" "UP" "服务已恢复"
        fi

        printf "  %-15s %s\n" "$name" "$result"
    done

    mv "${STATE_FILE}.tmp" "$STATE_FILE" 2>/dev/null || true
    return $has_issue
}

main() {
    log "══════ 服务监控检查 ══════"
    check_targets
    local ret=$?
    log "检查完成，状态: $([ $ret -eq 0 ] && echo '全部正常' || echo '有异常')"
}

main "$@"
```

### 逐段解析

| 部分 | 说明 |
|------|------|
| `/dev/tcp/host/port` | Bash 内置 TCP 连接，不需要 nc/telnet |
| 状态持久化 | `$STATE_FILE` 记录上次状态，检测 OK→FAIL 和 FAIL→OK 转换 |
| 配置文件 | `targets.conf` 支持外部配置，格式 `name=url` |
| 告警去重 | 只有状态变更时才发送告警，避免重复通知 |
| `curl -w '%{http_code}'` | 精确提取 HTTP 状态码 |

---

## 20.5 文件处理流水线

### 需求

搜索、过滤、排序、格式化输出文件信息，支持多种筛选条件。

### 完整脚本

```bash
#!/bin/bash
# file_pipeline.sh — 文件搜索与处理流水线

set -euo pipefail

readonly SEARCH_DIR="${1:-.}"
readonly SIZE_THRESHOLD_MB="${2:-10}"
readonly OUTPUT_FILE="${3:-large_files_report.txt}"

# 使用关联数组做文件类型统计
declare -A ext_count
declare -A ext_total_size

log() { echo "[$(date +%H:%M:%S)] $*"; }

main() {
    log "开始分析: $SEARCH_DIR"
    log "阈值: ${SIZE_THRESHOLD_MB}MB"

    {
        echo "═══════════════════════════════════════════════"
        echo "  大文件报告"
        echo "  目录: $SEARCH_DIR"
        echo "  生成时间: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "═══════════════════════════════════════════════"
        echo ""

        # 流水线：find → 过滤 → 处理 → 排序 → 格式化
        find "$SEARCH_DIR" -type f -size "+${SIZE_THRESHOLD_MB}M" -print0 2>/dev/null \
            | xargs -0 du -h --time \
            | sort -rh \
            | awk -v threshold="$SIZE_THRESHOLD_MB" '
            BEGIN {
                printf "%-10s %-16s %-8s %s\n", "大小", "修改时间", "类型", "路径"
                printf "══════════════════════════════════════════════════════════════\n"
            }
            {
                size = $1
                date_str = $2
                # 文件路径从第3列开始（xargs du -h --time 输出: size date path）
                path = ""
                for (i = 3; i <= NF; i++) path = path (i>3?" ":"") $i

                # 提取扩展名
                ext = "无"
                if (path ~ /\./) {
                    ext = path
                    sub(/.*\./, "", ext)
                    ext = tolower(ext)
                }

                printf "%-10s %-16s %-8s %s\n", size, date_str, ext, path
            }' \
            | tee "$OUTPUT_FILE"

        echo ""
        echo "=== 按扩展名统计 ==="

        # 第二轮处理：按扩展名聚合
        find "$SEARCH_DIR" -type f -size "+${SIZE_THRESHOLD_MB}M" -print0 2>/dev/null \
            | xargs -0 du -b \
            | awk '{
                path = ""
                for (i = 2; i <= NF; i++) path = path (i>2?" ":"") $i
                ext = "无"
                if (path ~ /\./) { ext = path; sub(/.*\./, "", ext); ext = tolower(ext) }
                count[ext]++
                size[ext] += $1
            }
            END {
                printf "%-10s %-8s %s\n", "总大小", "数量", "扩展名"
                for (ext in count)
                    printf "%-10s %-8d %s\n", human(size[ext]), count[ext], ext
            }
            function human(bytes, units, i) {
                units = "KMGT"
                for (i = 1; bytes >= 1024 && i <= 4; i++) bytes /= 1024
                return sprintf("%.1f%c", bytes, substr(units, i-1, 1))
            }' \
            | sort -rh

    } 2>/dev/null

    log "报告已保存至: $OUTPUT_FILE"
    log "共找到 $(wc -l < "$OUTPUT_FILE" | xargs) 行"
}

main
```

### 逐段解析

| 部分 | 说明 |
|------|------|
| `find -size +NM` | 按文件大小筛选 |
| `-print0 \| xargs -0` | 安全处理含空格和特殊字符的文件名 |
| `du -h --time` | 显示人类可读大小和修改时间 |
| `sort -rh` | 按人类可读大小降序排列 |
| `awk` 双轮处理 | 第一轮生成详细列表，第二轮按扩展名聚合统计 |
| `human()` 函数 | 内置 `awk` 函数将字节转为 KB/MB/GB |

---

## 20.6 系统信息搜集脚本

### 需求

一键搜集系统的硬件、软件、网络完整信息，用于问题排查或资产盘点。

### 完整脚本

```bash
#!/bin/bash
# sysinfo.sh — 系统信息全面搜集

set -euo pipefail

readonly OUTPUT_DIR="${1:-/tmp/sysinfo_$(hostname)_$(date +%Y%m%d)}"
mkdir -p "$OUTPUT_DIR"

log() { echo "[INFO] $*"; }

collect_system() {
    log "收集系统基本信息..."
    {
        echo "主机名: $(hostname)"
        echo "内核版本: $(uname -r)"
        echo "发行版: $(cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d'"' -f2 || echo '未知')"
        echo "架构: $(uname -m)"
        echo "运行时间: $(uptime -p)"
        echo "当前用户: $(whoami)"
        echo "时区: $(timedatectl show --property=Timezone --value 2>/dev/null || date +%Z)"
    } > "$OUTPUT_DIR/system.txt"
}

collect_cpu() {
    log "收集 CPU 信息..."
    {
        lscpu 2>/dev/null || cat /proc/cpuinfo
    } > "$OUTPUT_DIR/cpu.txt"
}

collect_memory() {
    log "收集内存信息..."
    {
        echo "=== free -h ==="
        free -h
        echo ""
        echo "=== /proc/meminfo ==="
        cat /proc/meminfo
    } > "$OUTPUT_DIR/memory.txt"
}

collect_disk() {
    log "收集磁盘信息..."
    {
        echo "=== lsblk ==="
        lsblk -o NAME,SIZE,TYPE,MOUNTPOINT,FSTYPE,LABEL 2>/dev/null || lsblk
        echo ""
        echo "=== df -h ==="
        df -h
        echo ""
        echo "=== fdisk -l ==="
        sudo fdisk -l 2>/dev/null || true
    } > "$OUTPUT_DIR/disk.txt"
}

collect_network() {
    log "收集网络信息..."
    {
        echo "=== ip addr ==="
        ip addr show 2>/dev/null || ifconfig
        echo ""
        echo "=== ip route ==="
        ip route show 2>/dev/null || route -n
        echo ""
        echo "=== ss -tlnp ==="
        ss -tlnp 2>/dev/null || netstat -tlnp
        echo ""
        echo "=== DNS ==="
        cat /etc/resolv.conf 2>/dev/null || true
    } > "$OUTPUT_DIR/network.txt"
}

collect_packages() {
    log "收集软件包信息..."
    {
        echo "=== 已安装包数量 ==="
        if command -v dpkg &>/dev/null; then
            dpkg -l | wc -l
            echo "(dpkg 系统)"
        elif command -v rpm &>/dev/null; then
            rpm -qa | wc -l
            echo "(rpm 系统)"
        elif command -v pacman &>/dev/null; then
            pacman -Q | wc -l
            echo "(pacman/Arch 系统)"
        else
            echo "未知包管理器"
        fi

        echo ""
        echo "=== 关键包版本 ==="
        for cmd in bash systemd gcc python3 node nginx docker; do
            command -v "$cmd" &>/dev/null && echo "$cmd: $($cmd --version 2>&1 | head -1)" || true
        done
    } > "$OUTPUT_DIR/packages.txt"
}

collect_processes() {
    log "收集进程信息..."
    {
        echo "=== 进程总数 ==="
        ps aux --no-headers | wc -l

        echo ""
        echo "=== 资源使用前 10 ==="
        ps aux --sort=-%mem | head -11

        echo ""
        echo "=== 僵尸进程 ==="
        ps aux | awk '$8 ~ /Z/ {print}' || echo "无僵尸进程"

        echo ""
        echo "=== systemctl failed ==="
        systemctl list-units --state=failed --no-legend 2>/dev/null || echo "无失败服务"
    } > "$OUTPUT_DIR/processes.txt"
}

collect_logs() {
    log "收集近期日志摘要..."
    {
        echo "=== journalctl 最近 50 行 ==="
        journalctl -n 50 --no-pager 2>/dev/null || echo "journalctl 不可用"

        echo ""
        echo "=== dmesg 最后 50 行 ==="
        dmesg | tail -50 2>/dev/null || true
    } > "$OUTPUT_DIR/logs.txt"
}

package() {
    log "打包信息..."
    local archive="${OUTPUT_DIR}.tar.gz"
    tar -czf "$archive" -C "$(dirname "$OUTPUT_DIR")" "$(basename "$OUTPUT_DIR")"
    rm -rf "$OUTPUT_DIR"
    echo "══════════════════════════════"
    echo "  系统信息已打包至: $archive"
    echo "  大小: $(du -h "$archive" | cut -f1)"
    echo "══════════════════════════════"
}

main() {
    echo "╔═══════════════════════════════════╗"
    echo "║    系统信息收集工具 v1.0          ║"
    echo "╚═══════════════════════════════════╝"
    echo ""

    collect_system
    collect_cpu
    collect_memory
    collect_disk
    collect_network
    collect_packages
    collect_processes
    collect_logs
    package
}

main
```

### 逐段解析

| 部分 | 说明 |
|------|------|
| 分类收集 | 每类信息存入独立文件，便于按需查阅 |
| 跨发行版兼容 | `||` 回退机制：优先用新命令，fallback 到旧命令 |
| 包管理器检测 | `dpkg/rpm/pacman` 自动检测并适配 |
| 资源前 10 | `ps aux --sort=-%mem` 按内存逆序取头部 |
| 打包 | 收集完成后打包为一个 tar.gz 文件便于传输 |
| `systemctl list-units --state=failed` | 快速发现失败的系统服务 |

---

## 20.7 批量用户管理脚本

### 需求

从 CSV 文件批量创建用户、设置密码、分配组。

### 完整脚本

```bash
#!/bin/bash
# user_batch.sh — 批量用户管理

set -euo pipefail

readonly PASSWD_FILE="${1:-users.csv}"
# CSV 格式: username,full_name,groups,shell
# 示例: alice,Alice Wang,sudo:docker,/bin/bash

log()   { echo "[$(date +%H:%M:%S)] $*"; }
die()   { log "[ERROR] $*"; exit 1; }

# 需要 root 权限
[ "$(id -u)" -eq 0 ] || die "请使用 root 权限运行"

[ -f "$PASSWD_FILE" ] || die "文件不存在: $PASSWD_FILE"

# 生成随机密码
gen_password() {
    tr -dc 'A-Za-z0-9!@#$%' < /dev/urandom | head -c 16
    echo
}

create_user() {
    local username="$1"
    local full_name="$2"
    local groups="$3"
    local shell="${4:-/bin/bash}"
    local password

    # 检查用户是否已存在
    if id "$username" &>/dev/null; then
        log "[SKIP] 用户 $username 已存在"
        return 0
    fi

    password=$(gen_password)

    # 创建用户
    if useradd -m -c "$full_name" -s "$shell" "$username"; then
        echo "$username:$password" | chpasswd
        chage -d 0 "$username"    # 首次登录强制修改密码

        # 分配到附加组
        if [ -n "$groups" ]; then
            IFS=':' read -ra group_arr <<< "$groups"
            for grp in "${group_arr[@]}"; do
                # 确保组存在
                getent group "$grp" &>/dev/null || groupadd "$grp"
                usermod -aG "$grp" "$username"
            done
        fi

        log "[OK] 创建用户 $username ($full_name)"
        echo "  密码: $password  (首次登录需修改)"
        echo "  组: ${groups:-无}"
        echo "  Shell: $shell"

        # 输出凭据到文件（仅 root 可读）
        printf "%-15s %-25s %s\n" "$username" "$full_name" "$password" >> /root/user_credentials.txt
    else
        log "[FAIL] 无法创建用户 $username"
        return 1
    fi
}

delete_user() {
    local username="$1"
    if id "$username" &>/dev/null; then
        userdel -r "$username" 2>/dev/null && log "[DEL] 已删除用户 $username" \
            || log "[FAIL] 无法删除用户 $username"
    else
        log "[SKIP] 用户 $username 不存在"
    fi
}

# 主流程
main() {
    log "用户名册处理: $PASSWD_FILE"

    local total=0 created=0 skipped=0 failed=0

    # 读取 CSV，跳过注释行和空行
    while IFS=',' read -r username full_name groups shell; do
        # 跳过注释和空行
        [[ "$username" =~ ^# ]] && continue
        [ -z "$username" ] && continue

        # 去除首尾空格
        username=$(echo "$username" | xargs)
        full_name=$(echo "$full_name" | xargs)
        groups=$(echo "$groups" | xargs)
        shell=$(echo "${shell:-/bin/bash}" | xargs)

        ((total++))
        log "--- 处理: $username ---"

        if create_user "$username" "$full_name" "$groups" "$shell"; then
            ((created++))
        else
            ((failed++))
        fi
    done < "$PASSWD_FILE"

    echo ""
    log "══════ 处理完成 ══════"
    log "总计: $total | 创建: $created | 跳过: $skipped | 失败: $failed"
    [ -f /root/user_credentials.txt ] && log "凭据文件: /root/user_credentials.txt"
}

main
```

### 逐段解析

| 部分 | 说明 |
|------|------|
| CSV 解析 | `IFS=',' read` 按逗号分割，`xargs` 去除空格 |
| `gen_password` | `/dev/urandom` 生成 16 位随机密码 |
| `chage -d 0` | 首次登录强制修改密码 |
| 组处理 | `IFS=':'` 分割冒号分隔的多组 |
| 凭据文件 | `/root/user_credentials.txt` 仅 root 可读，记录账号密码 |
| 幂等性 | 已存在的用户跳过，支持重复执行 |

---

## 20.8 多服务器软件包更新

### 需求

在多台服务器上执行软件包更新，支持并行执行，输出汇总报告。

### 完整脚本

```bash
#!/bin/bash
# update_servers.sh — 批量服务器软件更新

set -euo pipefail

readonly SERVER_LIST="${1:-servers.txt}"
# servers.txt 格式: user@hostname 或 hostname
readonly MAX_PARALLEL="${MAX_PARALLEL:-4}"

log() { echo "[$(date +%H:%M:%S)] $*"; }

[ -f "$SERVER_LIST" ] || { log "服务器列表文件不存在: $SERVER_LIST"; exit 1; }

# 检测包管理器并执行更新
remote_update() {
    local host="$1"
    local ssh_cmd

    if [[ "$host" == *@* ]]; then
        ssh_cmd="ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=accept-new $host"
    else
        ssh_cmd="ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=accept-new root@$host"
    fi

    local result=""

    # 尝试连接
    if ! $ssh_cmd "echo connected" &>/dev/null; then
        echo "CONNECTION_FAILED"
        return
    fi

    # 检测系统并执行更新
    result=$($ssh_cmd 'bash -s' 2>&1 << 'UPDATE_SCRIPT'
set -euo pipefail

if command -v apt-get &>/dev/null; then
    echo "DEB"
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -qq && apt-get upgrade -y -qq && echo "DONE" || echo "FAILED"
elif command -v dnf &>/dev/null; then
    echo "RPM_DNF"
    dnf update -y -q && echo "DONE" || echo "FAILED"
elif command -v yum &>/dev/null; then
    echo "RPM_YUM"
    yum update -y -q && echo "DONE" || echo "FAILED"
elif command -v pacman &>/dev/null; then
    echo "ARCH"
    pacman -Syu --noconfirm && echo "DONE" || echo "FAILED"
elif command -v zypper &>/dev/null; then
    echo "SUSE"
    zypper update -y && echo "DONE" || echo "FAILED"
elif command -v apk &>/dev/null; then
    echo "ALPINE"
    apk update && apk upgrade && echo "DONE" || echo "FAILED"
else
    echo "UNKNOWN"
fi

# 检查是否需要重启
if [ -f /var/run/reboot-required ] || needs-restarting -r &>/dev/null 2>&1; then
    echo "REBOOT_REQUIRED"
fi

# 最后 5 行更新日志
journalctl -n 5 --no-pager 2>/dev/null || tail -5 /var/log/pacman.log 2>/dev/null || true
UPDATE_SCRIPT
    )
    echo "$result"
}

# 并行执行更新
main() {
    log "══════ 批量服务器更新 ══════"
    log "服务器列表: $SERVER_LIST"
    log "最大并行数: $MAX_PARALLEL"
    log ""

    local servers=()
    while IFS= read -r host; do
        [[ "$host" =~ ^# ]] && continue
        [ -z "$host" ] && continue
        servers+=("$host")
    done < "$SERVER_LIST"

    local total=${#servers[@]}
    log "共 $total 台服务器"
    echo ""

    # 使用临时目录存放每台服务器的结果
    local tmp_dir
    tmp_dir=$(mktemp -d -t "update.XXXXXX")
    trap 'rm -rf "$tmp_dir"' EXIT

    local running=0
    declare -A results

    for host in "${servers[@]}"; do
        # 控制并发
        while [ "$running" -ge "$MAX_PARALLEL" ]; do
            wait -n 2>/dev/null || true
            ((running--))
        done

        (
            log "[$host] 开始更新..."
            local output
            output=$(remote_update "$host")
            echo "$output" > "$tmp_dir/${host//[@.]/_}.txt"
            log "[$host] 完成"
        ) &
        ((running++))
    done
    wait

    # 汇总报告
    echo ""
    echo "╔════════════════════════════════════════════╗"
    echo "║              更新汇总报告                  ║"
    echo "╚════════════════════════════════════════════╝"
    echo ""

    local success=0 fail=0 conn_fail=0

    for host in "${servers[@]}"; do
        local result_file="$tmp_dir/${host//[@.]/_}.txt"
        printf "%-30s " "$host"

        if [ ! -f "$result_file" ]; then
            echo "无结果（脚本异常）"
            ((fail++))
            continue
        fi

        local result
        result=$(cat "$result_file")

        if echo "$result" | grep -q "CONNECTION_FAILED"; then
            echo "连接失败"
            ((conn_fail++))
        elif echo "$result" | grep -q "DONE"; then
            local distro
            distro=$(echo "$result" | head -1)
            if echo "$result" | grep -q "REBOOT_REQUIRED"; then
                echo "✓ 成功 [$distro] 需重启"
            else
                echo "✓ 成功 [$distro]"
            fi
            ((success++))
        elif echo "$result" | grep -q "FAILED"; then
            echo "✗ 更新失败"
            ((fail++))
        else
            echo "状态不明"
            ((fail++))
        fi
    done

    echo ""
    log "总计: $total | 成功: $success | 失败: $fail | 连接失败: $conn_fail"
}

main
```

### 逐段解析

| 部分 | 说明 |
|------|------|
| 包管理器检测 | SSH 远程检测 `apt-get/dnf/yum/pacman/zypper/apk` |
| Heredoc 远程执行 | `<< 'UPDATE_SCRIPT'` 在远程主机上执行整个脚本块 |
| 并发控制 | 计数器 + `wait -n` 实现有限并行 |
| 结果收集 | 每台服务器结果写入临时文件，最后汇总报告 |
| 重启检测 | `/var/run/reboot-required` (Debian) / `needs-restarting` (RHEL) |
| `StrictHostKeyChecking=accept-new` | 自动接受新主机的 host key |

---

## 20.9 脚本可移植性

### POSIX sh vs Bash

```bash
# Bash 独有的特性（在 #!/bin/sh 下不可用）
# - [[ ]] 条件表达式 → 用 [ ] 代替
# - (( )) 算术 → 用 $(( )) 代替
# - 数组 → 用位置参数或 IFS 字符串模拟
# - {1..10} 花括号展开 → 用 seq
# - &> 重定向 → 用 > file 2>&1
# - local 关键字 → 函数变量需小心命名
# - declare/typeset → 不可用
# - here string <<< → 用 heredoc << EOF
# - ${var,,} / ${var^^} → 用 tr
# - 进程替换 <() >() → 用 FIFO

# POSIX 兼容写法示例
#!/bin/sh
# 原先 Bash:
# name="${1:-admin}"
# 在 /bin/sh 中同样可用（这是 POSIX 定义的）

# 原先 Bash: if [[ "$x" =~ ^[0-9]+$ ]]; then
# POSIX: case "$x" in ''|*[!0-9]*) echo "不是数字";; *) echo "是数字";; esac

# 原先 Bash: for i in {1..10}; do
# POSIX: for i in $(seq 1 10); do

# 原先 Bash: arr=("a" "b" "c"); echo "${arr[@]}"
# POSIX: set -- "a" "b" "c"; for item do echo "$item"; done

# 检测当前 shell
check_shell() {
    if [ -n "${BASH_VERSION:-}" ]; then
        echo "Bash $BASH_VERSION"
    elif [ -n "${ZSH_VERSION:-}" ]; then
        echo "Zsh $ZSH_VERSION"
    else
        case "$(readlink /proc/$$/exe 2>/dev/null)" in
            *dash*) echo "Dash" ;;
            *bash*) echo "Bash" ;;
            *) echo "Unknown shell" ;;
        esac
    fi
}
```

### 跨平台注意事项

```bash
# 1. 命令路径差异
# Linux /bin 和 /usr/bin 通常合并，macOS 不一定
# 使用: command -v <cmd> 检查而非硬编码路径

# 2. sed 差异
# Linux: sed -i 's/foo/bar/g' file
# macOS: sed -i '' 's/foo/bar/g' file
# 兼容写法:
sed -i.bak 's/foo/bar/g' file && rm file.bak

# 3. echo 差异
# 某些 shell 的 echo 不支持 -n 和 -e
# 使用 printf 代替: printf '%s\n' "$var"

# 4. 数组在 POSIX sh 中不可用
# 使用字符串 + IFS 分割代替

# 5. readlink 差异
# Linux: readlink -f /path
# macOS: 需要安装 coreutils (greadlink) 或用 Python 替代

# 6. date 差异
# Linux: date -d "1 day ago"
# macOS: date -v -1d
# 兼容: 使用 Python/Perl 处理复杂日期

# 7. stat 差异
# Linux: stat -c %Y file   (修改时间戳)
# macOS: stat -f %m file
# 兼容: 使用 ls -l 配合 awk 或使用 test -nt/-ot
```

---

## 20.10 使用 ShellCheck 进行静态检查

### 安装与使用

```bash
# 安装
# Arch:       sudo pacman -S shellcheck
# Debian:     sudo apt install shellcheck
# macOS:      brew install shellcheck
# 在线版:     https://www.shellcheck.net/

# 基本使用
shellcheck script.sh

# 检查整个目录
shellcheck scripts/*.sh

# 指定 severity 级别
shellcheck -S warning script.sh       # 只显示 warning 及以上
shellcheck -S error script.sh         # 只显示 error

# 排除特定规则
shellcheck -e SC2086 -e SC1091 script.sh

# 输出格式
shellcheck -f json script.sh          # JSON 格式
shellcheck -f gcc script.sh           # GCC 兼容格式（IDE 集成）
shellcheck -f diff script.sh          # Diff 格式
```

### 常见 ShellCheck 规则

| 规则 | 说明 | 示例 |
|------|------|------|
| SC2086 | 变量未加双引号 | `echo $var` → `echo "$var"` |
| SC2002 | 无用的 cat | `cat file \| grep X` → `grep X file` |
| SC2164 | `cd` 后未检查 | `cd /tmp || exit` |
| SC1091 | 未找到 source 的文件 | source 非固定路径的文件 |
| SC2034 | 未使用的变量 | 检查是否拼写错误 |
| SC2046 | 命令替换未被引用 | `$(cmd)` 处加双引号 |
| SC2068 | 数组未正确引用 | `"${arr[@]}"` |
| SC2155 | export 和赋值分开 | `export VAR; VAR=$(cmd)` |
| SC2181 | 使用 $? 而非直接判断 | `if cmd; then` 代替 `cmd; if [ $? -eq 0 ]` |
| SC2166 | 使用 `[ $x = $y ]` | 推荐 `[ "$x" = "$y" ]` |

```bash
# ShellCheck 内联注释控制
# shellcheck disable=SC2086    # 忽略下一行的 SC2086
echo $unquoted_var

# shellcheck disable=SC1091,SC1090  # 忽略多个规则
source /etc/profile

# 也可以对整个函数禁用
# shellcheck disable=SC2034
unused_vars() {
    local temp=1        # 有意未使用
}
```

---

## 20.11 综合实践原则

| 原则 | 说明 |
|------|------|
| 可读性优先 | 脚本是可维护代码，清晰命名、合理注释 |
| 幂等性 | 脚本可重复安全执行，不产生副作用 |
| 错误处理 | `set -euo pipefail`，关键操作检查返回值 |
| 日志完备 | 包含时间戳、日志级别、输出到 stderr |
| 参数验证 | 检查必需参数，提供 `-h` 帮助 |
| 锁机制 | 长时间运行的脚本使用文件锁防止并发 |
| 临时文件清理 | `trap cleanup EXIT` 确保清理 |
| 最小权限 | 不需要 root 则不检查，需要则开头检查 |
| 可测试 | 关键逻辑封装为函数，可单独测试 |
| 版本控制 | 脚本纳入 Git 管理，不要只存在服务器上 |

### 排错速查

```bash
# 脚本不执行？
# → chmod +x script.sh
# → ./script.sh 或 bash script.sh
# → 检查 shebang: head -1 script.sh

# 变量值不对？
# → echo "DEBUG: var='${var}'" >&2
# → set -x 追踪执行

# 管道不工作？
# → 检查 PIPESTATUS
# → 检查是否在子 shell 中（变量丢失）
# → 改用进程替换 < <(cmd)

# 路径含空格出错？
# → 用双引号包裹所有变量: "$path"

# 脚本在 cron 中不工作？
# → 使用绝对路径
# → PATH 不同，需完整声明
# → 检查环境变量：cron 环境极简
```

---

> **延伸阅读**: [[17-Bash编程进阶]] 涵盖参数展开、trap 信号处理和健壮脚本模板。[[18-正则与文本处理三剑客]] 详解日志分析和数据处理工具。[[54-服务器初始化与基线配置]] 服务器初始化最佳实践。[[16-Bash编程基础]] 语法速查与入门指南。
