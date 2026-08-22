# 自动化渗透框架：从bash开始

## 概述

使用bash构建自动化渗透框架，实现模块化攻击、自动化扫描和报告生成。本文介绍框架设计、模块化攻击、自动化扫描利用和报告生成。

## 核心理念

- **模块化设计**：每个功能独立成模块
- **自动化流程**：减少人工干预
- **可扩展性**：易于添加新模块
- **结果标准化**：统一的输出格式

---

## 1. 框架设计

```bash
#!/usr/bin/env bash
# 自动化渗透框架

FRAMEWORK_DIR="/opt/pentest-framework"
MODULES_DIR="${FRAMEWORK_DIR}/modules"
RESULTS_DIR="${FRAMEWORK_DIR}/results"
LOG_FILE="${FRAMEWORK_DIR}/framework.log"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; NC='\033[0m'

log_info()    { echo -e "${BLUE}[*]${NC} $*" | tee -a "$LOG_FILE"; }
log_success() { echo -e "${GREEN}[+]${NC} $*" | tee -a "$LOG_FILE"; }
log_warn()    { echo -e "${YELLOW}[!]${NC} $*" | tee -a "$LOG_FILE"; }
log_error()   { echo -e "${RED}[-]${NC} $*" | tee -a "$LOG_FILE"; }

# 模块加载器
load_module() {
    local module="$1"
    local module_file="${MODULES_DIR}/${module}.sh"
    if [[ ! -f "$module_file" ]]; then
        log_error "模块不存在: $module"
        return 1
    fi
    source "$module_file"
    log_info "已加载模块: $module"
}

# 扫描结果存储
declare -A SCAN_RESULTS=()
save_result() {
    local key="$1" value="$2"
    SCAN_RESULTS["$key"]="$value"
}
```

---

## 2. 模块化攻击

```bash
# 信息收集模块
module_recon() {
    local target="$1"
    log_info "=== 信息收集模块 ==="

    # 端口扫描
    nmap -sC -sV -O "$target" -oN "${RESULTS_DIR}/nmap_${target}.txt"

    # 目录枚举
    gobuster dir -u "http://$target" -w /usr/share/wordlists/dirb/common.txt \
        -o "${RESULTS_DIR}/dirs_${target}.txt" 2>/dev/null

    # 服务识别
    for port in 21 22 25 80 443 8080; do
        (echo "" | nc -w 3 "$target" "$port" 2>/dev/null | head -1) &
    done
    wait
}

# 漏洞扫描模块
module_vulnscan() {
    local target="$1"
    log_info "=== 漏洞扫描模块 ==="

    nmap --script vuln "$target" -oN "${RESULTS_DIR}/vuln_${target}.txt"
    nikto -h "http://$target" -o "${RESULTS_DIR}/nikto_${target}.txt" 2>/dev/null
}

# 漏洞利用模块
module_exploit() {
    local target="$1" vuln="$2"
    log_info "=== 漏洞利用模块 ==="

    case "$vuln" in
        sqli)
            sqlmap -u "http://$target/page?id=1" --batch --dump-all
            ;;
        rce)
            # 自定义RCE利用
            ;;
    esac
}
```

---

## 3. 自动化扫描+利用

```bash
full_scan() {
    local target="$1"
    log_info "=== 全自动渗透: $target ==="

    # 阶段1: 信息收集
    log_info "阶段1: 信息收集"
    module_recon "$target"

    # 阶段2: 漏洞扫描
    log_info "阶段2: 漏洞扫描"
    module_vulnscan "$target"

    # 阶段3: 漏洞利用
    log_info "阶段3: 漏洞利用"
    module_exploit "$target" "sqli"

    # 阶段4: 报告生成
    log_info "阶段4: 报告生成"
    generate_report "$target"
}
```

---

## 4. 报告生成

```bash
generate_report() {
    local target="$1"
    local report_file="${RESULTS_DIR}/report_${target}_$(date +%Y%m%d).html"

    cat > "$report_file" << EOF
<!DOCTYPE html>
<html>
<head><title>渗透测试报告: $target</title></head>
<body>
<h1>渗透测试报告</h1>
<p>目标: $target</p>
<p>时间: $(date '+%Y-%m-%d %H:%M:%S')</p>
<h2>发现</h2>
<ul>
$(for key in "${!SCAN_RESULTS[@]}"; do echo "<li>$key: ${SCAN_RESULTS[$key]}</li>"; done)
</ul>
</body>
</html>
EOF
    log_success "报告已生成: $report_file"
}
```

---

## 总结

本文介绍了使用bash构建自动化渗透框架的方法：模块化设计、自动化扫描利用和报告生成。该框架可以快速扩展新的攻击模块。

---

## 5. 任务调度

```bash
declare -A TASK_QUEUE=()
declare -A TASK_RESULTS=()

add_task() {
    local task_id="$1" module="$2" target="$3" params="${4:-}"
    TASK_QUEUE["$task_id"]="${module}|${target}|${params}"
    log_info "添加任务: $task_id ($module -> $target)"
}

execute_task() {
    local task_id="$1"
    local data="${TASK_QUEUE[$task_id]:-}"
    [[ -z "$data" ]] && { log_error "任务不存在: $task_id"; return 1; }

    IFS='|' read -r module target params <<< "$data"
    log_info "执行任务: $task_id"

    local start_time
    start_time=$(date +%s)

    # 执行模块
    load_module "$module"
    "module_${module}" "$target" $params

    local end_time
    end_time=$(date +%s)
    local duration=$((end_time - start_time))

    TASK_RESULTS["$task_id"]="completed|${duration}s"
    log_success "任务完成: $task_id (耗时: ${duration}s)"
}

run_all_tasks() {
    log_info "执行所有任务..."
    for task_id in "${!TASK_QUEUE[@]}"; do
        execute_task "$task_id" &
    done
    wait
    log_success "所有任务完成"
}
```

## 6. 会话管理

```bash
SESSION_DIR="/tmp/pentest_sessions"

save_session() {
    local session_name="${1:-default}"
    local session_file="${SESSION_DIR}/${session_name}.session"
    mkdir -p "$SESSION_DIR"

    cat > "$session_file" << EOF
# 会话保存
TARGETS=${TARGETS[@]:-}
RESULTS=${!SCAN_RESULTS[@]:-}
TIMESTAMP=$(date -Iseconds)
EOF
    log_info "会话已保存: $session_file"
}

load_session() {
    local session_name="$1"
    local session_file="${SESSION_DIR}/${session_name}.session"

    if [[ ! -f "$session_file" ]]; then
        log_error "会话不存在: $session_name"
        return 1
    fi

    source "$session_file"
    log_info "会话已加载: $session_name"
}

list_sessions() {
    log_info "可用会话:"
    for session in "${SESSION_DIR}"/*.session; do
        [[ -f "$session" ]] && echo "  $(basename "$session" .session)"
    done
}
```

## 7. 并发控制

```bash
MAX_PARALLEL=10
ACTIVE_JOBS=0

wait_for_slot() {
    while (( ACTIVE_JOBS >= MAX_PARALLEL )); do
        sleep 0.1
        ACTIVE_JOBS=$(jobs -r | wc -l)
    done
    ((ACTIVE_JOBS++))
}

job_done() {
    ((ACTIVE_JOBS--))
}

parallel_execute() {
    local cmd="$1"
    wait_for_slot
    eval "$cmd" &
    job_done
}
```

## 8. 错误恢复

```bash
with_retry() {
    local max_attempts="${1:-3}"
    local delay="${2:-2}"
    shift 2
    local cmd=("$@")

    local attempt=1
    while (( attempt <= max_attempts )); do
        if "${cmd[@]}"; then
            return 0
        fi
        log_warn "尝试 $attempt/$max_attempts 失败, ${delay}s后重试"
        sleep "$delay"
        ((attempt++))
    done
    log_error "所有尝试均失败"
    return 1
}

with_timeout() {
    local timeout="$1"
    shift
    timeout "$timeout" "$@"
    local rc=$?
    if (( rc == 124 )); then
        log_warn "命令执行超时 (${timeout}s)"
    fi
    return $rc
}
```

## 9. 数据持久化

```bash
export_results_json() {
    local output_file="${1:-results.json}"
    echo "{" > "$output_file"
    echo "  \"timestamp\": \"$(date -Iseconds)\"," >> "$output_file"
    echo "  \"results\": {" >> "$output_file"

    local first=true
    for key in "${!SCAN_RESULTS[@]}"; do
        [[ "$first" == true ]] && first=false || echo "," >> "$output_file"
        echo "    \"$key\": \"${SCAN_RESULTS[$key]}\"" >> "$output_file"
    done

    echo "  }" >> "$output_file"
    echo "}" >> "$output_file"
    log_info "结果已导出: $output_file"
}

import_results_json() {
    local input_file="$1"
    if [[ ! -f "$input_file" ]]; then
        log_error "文件不存在: $input_file"
        return 1
    fi
    # 使用python3解析JSON
    python3 -c "
import json, sys
with open('$input_file') as f:
    data = json.load(f)
for k, v in data.get('results', {}).items():
    print(f'{k}={v}')
" | while IFS='=' read -r key value; do
        SCAN_RESULTS["$key"]="$value"
    done
    log_info "结果已导入"
}
```
