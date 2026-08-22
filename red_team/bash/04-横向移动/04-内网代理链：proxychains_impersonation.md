# 内网代理链：proxychains与身份冒充

## 章节概述

在渗透测试中，当目标位于内网深处时，需要通过代理链进行多级跳转。proxychains 是 Linux 下最常用的代理链工具，配合 SSH 动态代理可以实现灵活的内网穿透。本章系统性地讲解 proxychains 配置、SSH 动态代理、多级代理链、内网穿透技术以及代理自动化脚本。

> **核心理念**
> 内网代理的本质是建立多层网络隧道，将流量从攻击者机层层转发到目标内网。关键在于代理链的稳定性和隐蔽性，以及代理配置的自动化管理。

---

### 第1节 proxychains 配置

#### 1.1 proxychains 基础配置

```bash
# proxychains 配置文件位置
# /etc/proxychains.conf
# ~/.proxychains/proxychains.conf

# 配置示例
cat > /tmp/proxychains.conf << 'EOF'
# proxychains 配置

# 代理类型: dynamic_chain, strict_chain, random_chain
dynamic_chain

# DNS 解析设置
proxy_dns

# 超时设置
tcp_read_time_out 15000
tcp_connect_time_out 8000

# 代理列表
[ProxyList]
# socks5 代理
socks5 127.0.0.1 1080
# HTTP 代理
# http 127.0.0.1 8080
EOF

# 使用配置文件运行
proxychains -f /tmp/proxychains.conf curl ifconfig.me
```

#### 1.2 proxychains 链式配置

```bash
#!/usr/bin/env bash
# proxychains_chain.sh - 构建代理链配置
set -euo pipefail

OUTPUT="${1:-/tmp/proxychains_chain.conf}"
PROXIES="${2:?用法: $0 <输出文件> <代理列表>}"

cat > "$OUTPUT" << EOF
# 代理链配置 - 自动生成
strict_chain

proxy_dns

tcp_read_time_out 15000
tcp_connect_time_out 8000

[ProxyList]
EOF

while IFS= read -r proxy; do
    echo "$proxy" >> "$OUTPUT"
done < "$PROXIES"

echo "[+] 代理链配置已生成: $OUTPUT"
cat "$OUTPUT"
```

---

### 第2节 SSH 动态代理

#### 2.1 创建 SOCKS 代理

```bash
#!/usr/bin/env bash
# ssh_socks_proxy.sh - SSH 动态代理
set -euo pipefail

TARGET="${1:?用法: $0 <目标IP> [端口]}"
PORT="${2:-22}"
SOCKS_PORT="${3:-1080}"
USER="${4:-root}"

echo "[*] 创建 SSH SOCKS 代理..."
echo "    目标: $TARGET:$PORT"
echo "    本地端口: $SOCKS_PORT"

# 后台运行 SSH 动态代理
ssh -D "$SOCKS_PORT" -f -C -q -N \
    -o StrictHostKeyChecking=no \
    -o ServerAliveInterval=60 \
    -p "$PORT" "$USER@$TARGET"

echo "[+] SOCKS 代理已启动: 127.0.0.1:$SOCKS_PORT"

# 测试代理
echo "[*] 测试代理..."
proxychains curl -s http://ifconfig.me 2>/dev/null || echo "[-] 代理测试失败"
```

#### 2.2 代理管理

```bash
#!/usr/bin/env bash
# proxy_manager.sh - 代理管理工具
set -euo pipefail

case "${1:-help}" in
    start)
        TARGET="${2:?需要目标IP}"
        PORT="${3:-1080}"
        echo "[*] 启动代理: $TARGET -> localhost:$PORT"
        ssh -D "$PORT" -f -C -q -N \
            -o StrictHostKeyChecking=no \
            "$TARGET"
        echo "[+] 代理已启动"
        ;;
    stop)
        echo "[*] 停止所有 SSH 代理..."
        pkill -f "ssh -D" 2>/dev/null
        echo "[+] 代理已停止"
        ;;
    list)
        echo "[*] 活跃代理:"
        ps aux | grep "ssh -D" | grep -v grep
        ;;
    test)
        echo "[*] 测试代理连接..."
        curl -s --socks5-hostname 127.0.0.1:1080 http://ifconfig.me 2>/dev/null
        ;;
    *)
        echo "用法: $0 {start|stop|list|test} [选项]"
        ;;
esac
```

---

### 第3节 多级代理链

#### 3.1 多级代理搭建

```bash
#!/usr/bin/env bash
# multi_hop_proxy.sh - 多级代理搭建
set -euo pipefail

# 跳板机列表
JUMPS=("user1@host1" "user2@host2" "user3@host3")
FINAL_TARGET="target@internal_host"

echo "[*] 搭建多级代理链..."

# 构建 SSH 跳转命令
SSH_CMD="ssh"
for jump in "${JUMPS[@]}"; do
    SSH_CMD="$SSH_CMD -J $jump"
done

echo "[*] 代理链: ${JUMPS[*]} -> $FINAL_TARGET"
echo "[*] 执行: $SSH_CMD $FINAL_TARGET"

# 建立隧道
$SSH_CMD -D 1080 -f -C -q -N "$FINAL_TARGET" 2>/dev/null

echo "[+] 多级代理已建立"
echo "[*] 使用: proxychains curl http://internal_host"
```

#### 3.2 proxychains 配置多级代理

```bash
# proxychains 多级代理配置
cat > /etc/proxychains_multi.conf << 'EOF'
# 多级代理配置

# 使用 dynamic_chain 允许部分代理失败
dynamic_chain

proxy_dns

tcp_read_time_out 20000
tcp_connect_time_out 10000

[ProxyList]
# 第一级代理 (跳板机1)
socks5 192.168.1.100 1080
# 第二级代理 (跳板机2)
socks5 10.0.0.50 1080
# 第三级代理 (目标网关)
socks5 172.16.0.10 1080
EOF

# 使用
proxychains -f /etc/proxychains_multi.conf curl http://172.16.0.100
```

---

### 第4节 内网穿透

#### 4.1 SSH 隧道内网穿透

```bash
#!/usr/bin/env bash
# ssh_tunnel_pivot.sh - SSH 隧道内网穿透
set -euo pipefail

VPS_IP="${1:?用法: $0 <VPS_IP>}"
VPS_PORT="${2:-22}"
LOCAL_SOCKS="${3:-1080}"

echo "[*] SSH 隧道内网穿透..."
echo "    VPS: $VPS_IP:$VPS_PORT"
echo "    本地 SOCKS: $LOCAL_SOCKS"

# 方案1: 反向 SOCKS 代理
# 在目标机器上运行（反向连接到 VPS）
# ssh -R 1080:127.0.0.1:1080 user@vps_ip

# 方案2: 本地转发
# ssh -L 8080:internal_host:80 user@target

# 方案3: 动态转发（SOCKS 代理）
ssh -D "$LOCAL_SOCKS" -f -C -q -N \
    -o StrictHostKeyChecking=no \
    -o ServerAliveInterval=60 \
    "root@$VPS_IP"

echo "[+] 隧道已建立"
```

#### 4.2 端口转发自动化

```bash
#!/usr/bin/env bash
# port_forward_auto.sh - 自动化端口转发
set -euo pipefail

CONFIG_FILE="${1:?用法: $0 <配置文件>}"

echo "[*] 读取转发配置..."

while IFS=',' read -r type local_port remote_host remote_port; do
    case "$type" in
        local)
            echo "[*] 本地转发: localhost:$local_port -> $remote_host:$remote_port"
            ssh -L "$local_port:$remote_host:$remote_port" -f -N \
                -o StrictHostKeyChecking=no target_host
            ;;
        remote)
            echo "[*] 远程转发: $remote_host:$remote_port -> localhost:$local_port"
            ssh -R "$remote_port:localhost:$local_port" -f -N \
                -o StrictHostKeyChecking=no target_host
            ;;
        dynamic)
            echo "[*] 动态转发: SOCKS on localhost:$local_port"
            ssh -D "$local_port" -f -N \
                -o StrictHostKeyChecking=no target_host
            ;;
    esac
done < "$CONFIG_FILE"

echo "[+] 所有转发已建立"
```

---

### 第5节 代理自动化脚本

#### 5.1 综合代理管理器

```bash
#!/usr/bin/env bash
# proxy_automation.sh - 代理自动化管理
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info()  { echo -e "${YELLOW}[*]${NC} $*"; }
log_found() { echo -e "${RED}[+]${NC} $*"; }
log_ok()    { echo -e "${GREEN}[+]${NC} $*"; }

PROXY_DIR="/tmp/proxies"
mkdir -p "$PROXY_DIR"

# 启动代理
start_proxy() {
    local name="$1"
    local target="$2"
    local port="${3:-1080}"

    log_info "启动代理: $name -> $target:$port"

    ssh -D "$port" -f -C -q -N \
        -o StrictHostKeyChecking=no \
        -o ServerAliveInterval=60 \
        -o ExitOnForwardFailure=yes \
        "$target" 2>/dev/null

    if [[ $? -eq 0 ]]; then
        log_ok "代理已启动: $name (端口: $port)"
        echo "$port" > "$PROXY_DIR/$name.pid"
    else
        echo "[-] 代理启动失败: $name"
    fi
}

# 停止代理
stop_proxy() {
    local name="$1"
    local pid_file="$PROXY_DIR/$name.pid"

    if [[ -f "$pid_file" ]]; then
        local port
        port=$(cat "$pid_file")
        # 查找并杀死使用该端口的 SSH 进程
        pid=$(lsof -i :"$port" -t 2>/dev/null | head -1)
        if [[ -n "$pid" ]]; then
            kill "$pid" 2>/dev/null
            log_ok "代理已停止: $name"
        fi
        rm -f "$pid_file"
    fi
}

# 测试代理
test_proxy() {
    local name="$1"
    local port="$2"

    log_info "测试代理: $name"

    result=$(curl -s --socks5-hostname "127.0.0.1:$port" \
        --connect-timeout 5 http://ifconfig.me 2>/dev/null)

    if [[ -n "$result" ]]; then
        log_ok "代理正常: $name (出口IP: $result)"
    else
        echo "[-] 代理异常: $name"
    fi
}

case "${1:-help}" in
    start)
        start_proxy "$2" "$3" "${4:-1080}"
        ;;
    stop)
        stop_proxy "$2"
        ;;
    test)
        test_proxy "$2" "${3:-1080}"
        ;;
    status)
        log_info "活跃代理:"
        ps aux | grep "ssh -D" | grep -v grep | awk '{print "  " $NF}'
        ;;
    *)
        echo "用法: $0 {start|stop|test|status} [选项]"
        ;;
esac
