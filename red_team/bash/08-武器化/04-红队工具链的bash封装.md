# 红队工具链的bash封装

## 概述

将常用红队工具（nmap、metasploit、sqlmap等）用bash封装，实现自动化工作流和结果收集。本文介绍常用工具的bash封装、自动化工作流和结果收集。

## 核心理念

- **统一接口**：所有工具使用统一的调用方式
- **自动化工作流**：工具组合自动执行
- **结果收集**：统一的输出格式和存储
- **日志记录**：所有操作可追溯

---

## 1. 工具封装

### 1.1 Nmap 封装

```bash
scan_nmap() {
    local target="$1" output_dir="${2:-.}"
    local scan_type="${3:-default}"

    echo "[*] Nmap 扫描: $target (类型: $scan_type)"

    case "$scan_type" in
        quick)
            nmap -T4 -F "$target" -oN "${output_dir}/nmap_quick_${target}.txt"
            ;;
        full)
            nmap -sC -sV -O -A "$target" -oN "${output_dir}/nmap_full_${target}.txt"
            ;;
        vuln)
            nmap --script vuln "$target" -oN "${output_dir}/nmap_vuln_${target}.txt"
            ;;
        default)
            nmap -sC -sV "$target" -oN "${output_dir}/nmap_default_${target}.txt"
            ;;
    esac
    echo "[+] 扫描完成"
}
```

### 1.2 SQLmap 封装

```bash
scan_sqlmap() {
    local url="$1" output_dir="${2:-.}"
    local level="${3:-3}" risk="${4:-2}"

    echo "[*] SQLmap 扫描: $url"

    sqlmap -u "$url" \
        --level="$level" --risk="$risk" \
        --batch \
        --output-dir="$output_dir" \
        --crawl=3 \
        --forms \
        --random-agent

    echo "[+] SQLmap 扫描完成"
}
```

### 1.3 Metasploit 封装

```bash
run_msf() {
    local module="$1" rhost="$2" lhost="$3" lport="${4:-4444}"

    echo "[*] Metasploit: $module"

    msfconsole -q -x "
        use $module;
        set RHOSTS $rhost;
        set LHOST $lhost;
        set LPORT $lport;
        exploit -z;
        exit
    " 2>/dev/null

    echo "[+] Metasploit 执行完成"
}
```

---

## 2. 自动化工作流

```bash
workflow_pentest() {
    local target="$1" output_dir="${2:-/tmp/pentest_$(date +%Y%m%d)}"

    mkdir -p "$output_dir"

    echo "[*] === 自动化渗透测试工作流 ==="
    echo "[*] 目标: $target"
    echo "[*] 输出: $output_dir"

    # 阶段1: 信息收集
    echo "[*] 阶段1: 信息收集"
    scan_nmap "$target" "$output_dir" "full"

    # 阶段2: 漏洞扫描
    echo "[*] 阶段2: 漏洞扫描"
    scan_sqlmap "http://$target" "$output_dir"

    # 阶段3: 漏洞利用
    echo "[*] 阶段3: 漏洞利用"
    # run_msf "exploit/multi/handler" "$target"

    # 阶段4: 报告生成
    echo "[*] 阶段4: 报告生成"
    generate_pentest_report "$target" "$output_dir"

    echo "[+] 工作流完成"
}
```

---

## 3. 结果收集

```bash
generate_pentest_report() {
    local target="$1" output_dir="$2"
    local report="${output_dir}/report.html"

    cat > "$report" << EOF
<!DOCTYPE html>
<html>
<head><title>渗透测试报告: $target</title></head>
<body>
<h1>渗透测试报告</h1>
<p>目标: $target</p>
<p>时间: $(date '+%Y-%m-%d %H:%M:%S')</p>
<h2>发现</h2>
<pre>
$(cat ${output_dir}/nmap_*.txt 2>/dev/null | head -100)
</pre>
</body>
</html>
EOF
    echo "[+] 报告已生成: $report"
}

collect_results() {
    local output_dir="$1"
    echo "[*] 收集结果..."

    # 合并所有结果
    cat ${output_dir}/*.txt > "${output_dir}/all_results.txt"

    # 统计发现
    local vuln_count
    vuln_count=$(grep -c "VULNERABLE" ${output_dir}/*.txt 2>/dev/null || echo 0)
    echo "[+] 发现漏洞: $vuln_count"

    # 生成摘要
    echo "扫描时间: $(date)" > "${output_dir}/summary.txt"
    echo "目标: $target" >> "${output_dir}/summary.txt"
    echo "漏洞数: $vuln_count" >> "${output_dir}/summary.txt"
}
```

---

## 4. 综合工具脚本

```bash
#!/usr/bin/env bash
# 红队工具链综合脚本

TARGET="$1"
OUTPUT_DIR="/tmp/redteam_$(date +%Y%m%d_%H%M%S)"

mkdir -p "$OUTPUT_DIR"

echo "[*] === 红队工具链 ==="

# Nmap 扫描
scan_nmap "$TARGET" "$OUTPUT_DIR" "full"

# SQLmap 扫描
scan_sqlmap "http://$TARGET" "$OUTPUT_DIR"

# 目录枚举
gobuster dir -u "http://$TARGET" -w /usr/share/wordlists/dirb/common.txt \
    -o "${OUTPUT_DIR}/dirs.txt" 2>/dev/null

# 结果收集
collect_results "$OUTPUT_DIR"

echo "[+] 完成! 结果: $OUTPUT_DIR"
```

---

## 总结

本文介绍了红队工具链的bash封装：nmap、sqlmap、metasploit的自动化调用，自动化渗透测试工作流，以及结果收集和报告生成。这些封装可以大大提高渗透测试效率。
