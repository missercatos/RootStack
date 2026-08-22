# CTF中bash逆向题型

## 概述

CTF竞赛中的bash相关题目涉及脚本逆向、编码解码、环境变量利用等多个方面。本文详细介绍常见的bash逆向题型及解题技巧。

## 核心理念

- **理解执行流程**：分析bash脚本的执行逻辑
- **编码识别**：快速识别各种编码方式
- **变量追踪**：跟踪环境变量和局部变量的变化
- **工具辅助**：善用bash调试工具辅助分析

---

## 1. bash 脚本逆向

### 1.1 静态分析技巧

```bash
# 查看脚本内容（排除空行和注释）
cat script.sh | grep -v '^#' | grep -v '^$'

# 查找所有变量赋值
grep -oP '[A-Za-z_]+=' script.sh

# 查找所有命令调用
grep -oP '^[a-z]+' script.sh

# 查找所有函数定义
grep -oP '^[a-zA-Z_]+\(\)' script.sh

# 查找所有 eval/base64/decode 调用
grep -n 'eval\|base64\|decode\|exec\|system\|passthru' script.sh
```

### 1.2 动态调试

```bash
# 使用 bash -x 跟踪执行
bash -x script.sh

# 使用 PS4 显示更多信息
PS4='+(${BASH_SOURCE}:${LINENO}): ${FUNCNAME[0]:+${FUNCNAME[0]}(): }' bash -x script.sh

# 使用 trap 拦截信号
trap 'echo "Signal received at line $LINENO"' DEBUG
```

### 1.3 常见混淆手法

```bash
# base64 混淆
echo "aGVsbG8gd29ybGQ=" | base64 -d
# 解码: hello world

# hex 编码
echo "68656c6c6f" | xxd -r -p

# chr 拼接
echo $'\x48\x65\x6c\x6c\x6f'

# 变量拼接
a=he; b=ll; c=o
echo ${a}${b}${c}

# 字符串反转
echo "dlrow olleh" | rev
```

---

## 2. eval/base64 解码

### 2.1 多层 base64 解码

```bash
multi_decode_base64() {
    local encoded="$1"
    local decoded="$encoded"
    local layer=0

    while true; do
        local temp
        temp=$(echo "$decoded" | base64 -d 2>/dev/null) || break
        if [[ "$temp" == "$decoded" ]]; then
            break
        fi
        decoded="$temp"
        ((layer++))
        echo "[Layer $layer] $decoded"
    done

    echo "最终解码结果: $decoded"
    echo "共 $layer 层"
}
```

### 2.2 eval 混淆分析

```bash
# 安全分析：不执行，只查看
safe_analyze_eval() {
    local script="$1"
    sed 's/eval/echo/g' "$script" | bash 2>/dev/null
}
```

### 2.3 混合编码解码

```bash
decode_mixed() {
    local input="$1"

    # 尝试 base64
    if echo "$input" | base64 -d 2>/dev/null | grep -qP '[a-zA-Z]'; then
        echo "Base64: $(echo "$input" | base64 -d)"
    fi

    # 尝试 hex
    if echo "$input" | xxd -r -p 2>/dev/null | grep -qP '[a-zA-Z]'; then
        echo "Hex: $(echo "$input" | xxd -r -p)"
    fi

    # 尝试 URL decode
    if echo "$input" | python3 -c "import sys,urllib.parse; print(urllib.parse.unquote(sys.stdin.read()))" 2>/dev/null | grep -qP '[a-zA-Z]'; then
        echo "URL: $(echo "$input" | python3 -c "import sys,urllib.parse; print(urllib.parse.unquote(sys.stdin.read()))")"
    fi

    # ROT13
    echo "ROT13: $(echo "$input" | tr 'A-Za-z' 'N-ZA-Mn-za-m')"
}
```

---

## 3. 环境变量利用

### 3.1 环境变量注入

```bash
# 利用 IFS 分割
IFS=','
set a,b,c,d
echo "$1"  # 输出: a

# 利用 PATH 劫持
create_fake_command() {
    local cmd="$1" payload="$2"
    local tmp_dir="/tmp/fake_$$"
    mkdir -p "$tmp_dir"
    echo "#!/bin/bash" > "$tmp_dir/$cmd"
    echo "$payload" >> "$tmp_dir/$cmd"
    chmod +x "$tmp_dir/$cmd"
    export PATH="$tmp_dir:$PATH"
}

# 利用 BASH_ENV
export BASH_ENV="/tmp/malicious.sh"
```

### 3.2 隐藏变量

```bash
# 在变量名中使用特殊字符
declare -x $'\x41\x42\x43'="hidden_value"
echo ${!'\x41\x42\x43'}

# 利用 /proc/self/environ
cat /proc/self/environ | tr '\0' '\n'

# 利用 declare 查看所有变量
declare -p
```

---

## 4. 文件描述符题目

### 4.1 文件描述符操作

```bash
# 打开文件描述符
exec 3< /etc/passwd
cat <&3
exec 3<&-

# 写入文件描述符
exec 4> /tmp/output.txt
echo "data" >&4
exec 4>&-

# 管道文件描述符
exec 3< <(echo "data from fd 3")
read line <&3
echo "$line"
```

### 4.2 常见文件描述符技巧

```bash
read_from_fd() {
    local fd="$1"
    local line
    while read -u "$fd" line; do
        echo "$line"
    done
}

# 创建匿名管道
mkfifo /tmp/pipe_$$
exec 3<>/tmp/pipe_$$
echo "data through pipe" >&3
read <&3
exec 3>&-
rm -f /tmp/pipe_$$
```

---

## 5. 管道题目

### 5.1 管道基础

```bash
# 管道连接
echo "data" | grep "pattern" | sed 's/old/new/g'

# 命名管道 (FIFO)
mkfifo /tmp/mypipe
# 终端1: echo "secret" > /tmp/mypipe
# 终端2: cat /tmp/mypipe

# 进程替换
diff <(ls /dir1) <(ls /dir2)
```

### 5.2 管道中的信号处理

```bash
set -o pipefail
command1 | command2 | command3
echo "Exit status: ${PIPESTATUS[@]}"
```

---

## 6. CTF 解题模板

```bash
#!/usr/bin/env bash
# CTF Bash 逆向解题模板

set -euo pipefail

# 颜色输出
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()  { echo -e "${YELLOW}[*]${NC} $*"; }
ok()    { echo -e "${GREEN}[+]${NC} $*"; }
fail()  { echo -e "${RED}[-]${NC} $*"; }

# base64 自动解码
auto_base64() {
    local input="$1"
    local decoded
    decoded=$(echo "$input" | base64 -d 2>/dev/null) || { fail "base64 解码失败"; return 1; }
    ok "Base64: $decoded"
}

# hex 自动解码
auto_hex() {
    local input="$1"
    local decoded
    decoded=$(echo "$input" | xxd -r -p 2>/dev/null) || { fail "hex 解码失败"; return 1; }
    ok "Hex: $decoded"
}

# 逐字符分析
analyze_chars() {
    local input="$1"
    for ((i=0; i<${#input}; i++)); do
        local c="${input:$i:1}"
        local ord=$(printf '%d' "'$c")
        echo "  [$i] '$c' -> $ord (0x$(printf '%02x' $ord))"
    done
}

# XOR 分析
xor_analyze() {
    local input="$1" key="$2"
    local result=""
    for ((i=0; i<${#input}; i++)); do
        local c1=$(printf '%d' "'${input:$i:1}")
        local c2=$(printf '%d' "'${key:$((i % ${#key})):1}")
        local xored=$((c1 ^ c2))
        result+=$(printf '\x%02x' "$xored")
    done
    echo "$result" | xxd -r -p
}

# 主函数
main() {
    info "CTF Bash 逆向解题工具"
    echo "用法:"
    echo "  auto_base64 "encoded_string""
    echo "  auto_hex "hex_string""
    echo "  analyze_chars "string""
    echo "  xor_analyze "input" "key""
}

[[ "${BASH_SOURCE[0]}" == "$0" ]] && main "$@"
