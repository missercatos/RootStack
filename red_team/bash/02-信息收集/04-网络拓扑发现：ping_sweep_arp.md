# 网络拓扑发现：ping_sweep_arp

网络拓扑发现是信息收集的重要环节，通过ping扫描、ARP扫描和路由分析可以了解目标网络的结构和主机分布。

---

## Ping扫描

### 基础Ping扫描

```bash
#!/bin/bash
# ping_sweep.sh - 基础Ping扫描

NETWORK=$1
TIMEOUT=1

echo "[+] 扫描网段: $NETWORK.0/24"

for i in $(seq 1 254); do
    (ping -c 1 -W $TIMEOUT $NETWORK.$i > /dev/null 2>&1 && echo "[+] $NETWORK.$i 在线") &
done
wait

echo "[+] 扫描完成"
```

### 批量Ping扫描

```bash
#!/bin/bash
# ping_sweep_batch.sh - 批量Ping扫描

NETWORKS=$1
TIMEOUT=1

echo "[+] 批量扫描网段..."

for network in $NETWORKS; do
    echo "[+] 扫描 $network.0/24"
    for i in $(seq 1 254); do
        (ping -c 1 -W $TIMEOUT $network.$i > /dev/null 2>&1 && echo "[+] $network.$i 在线") &
    done
    wait
done
```

### Ping扫描优化

```bash
#!/bin/bash
# ping_sweep_optimized.sh - 优化的Ping扫描

NETWORK=$1
TIMEOUT=1
MAX_PARALLEL=50

echo "[+] 优化Ping扫描: $NETWORK.0/24"

# 使用xargs控制并发
seq 1 254 | xargs -P $MAX_PARALLEL -I {} bash -c "
    ping -c 1 -W $TIMEOUT $NETWORK.{} > /dev/null 2>&1 && echo '[+] $NETWORK.{} 在线'
"
```

### ICMP类型扫描

```bash
#!/bin/bash
# ping_icmp_types.sh - ICMP类型扫描

TARGET=$1

echo "[+] 扫描目标的ICMP响应..."

# Echo Request
echo "[+] Echo Request (Type 8):"
ping -c 1 -W 1 $TARGET

# Timestamp Request
echo "[+] Timestamp Request (Type 13):"
echo "13" | xxd -r -p | xxd -p | nc -u -w 1 $TARGET 123 2>/dev/null

# Address Mask Request
echo "[+] Address Mask Request (Type 17):"
echo "17" | xxd -r -p | xxd -p | nc -u -w 1 $TARGET 123 2>/dev/null
```

---

## ARP扫描

### 基础ARP扫描

```bash
#!/bin/bash
# arp_sweep.sh - 基础ARP扫描

INTERFACE=$1
NETWORK=$2

echo "[+] ARP扫描网段: $NETWORK.0/24"

for i in $(seq 1 254); do
    (arping -c 1 -I $INTERFACE $NETWORK.$i > /dev/null 2>&1 && echo "[+] $NETWORK.$i 在线") &
done
wait
```

### ARP扫描工具

```bash
#!/bin/bash
# arp_scan_tool.sh - ARP扫描工具

INTERFACE=$1
NETWORK=$2

echo "[+] 使用arp-scan扫描..."

# 使用arp-scan
sudo arp-scan -I $INTERFACE $NETWORK.0/24

# 或使用netdiscover
sudo netdiscover -r $NETWORK.0/24 -i $INTERFACE
```

### ARP缓存分析

```bash
#!/bin/bash
# arp_cache.sh - ARP缓存分析

echo "[+] 分析ARP缓存..."

# 显示ARP缓存
echo "[+] ARP缓存:"
arp -a

# 显示详细信息
echo "[+] ARP详细信息:"
ip neigh show

# 清除ARP缓存
echo "[+] 清除ARP缓存:"
sudo ip neigh flush all
```

---

## 子网发现

### 网络接口分析

```bash
#!/bin/bash
# subnet_discovery.sh - 子网发现

echo "[+] 发现本地子网..."

# 获取网络接口信息
echo "[+] 网络接口:"
ip addr show 2>/dev/null || ifconfig 2>/dev/null

# 获取路由表
echo "[+] 路由表:"
ip route show 2>/dev/null || route -n 2>/dev/null

# 计算子网
echo "[+] 计算子网:"
for interface in $(ip -o link show | awk -F: '{print $2}' | tr -d ' '); do
    ip_addr=$(ip addr show $interface | grep "inet " | awk '{print $2}')
    if [ -n "$ip_addr" ]; then
        echo "$interface: $ip_addr"
    fi
done
```

### 主动子网发现

```bash
#!/bin/bash
# subnet_active.sh - 主动子网发现

echo "[+] 主动发现子网..."

# 扫描本地网络
LOCAL_IP=$(ip route get 1 | head -1 | awk '{print $7}')
NETWORK=$(echo $LOCAL_IP | cut -d. -f1-3)

echo "[+] 本地IP: $LOCAL_IP"
echo "[+] 扫描网络: $NETWORK.0/24"

# Ping扫描
for i in $(seq 1 254); do
    (ping -c 1 -W 1 $NETWORK.$i > /dev/null 2>&1 && echo "[+] $NETWORK.$i 在线") &
done
wait
```

### 多网段扫描

```bash
#!/bin/bash
# multi_subnet.sh - 多网段扫描

echo "[+] 扫描多个网段..."

SUBNETS=$1
INTERFACE=$2

for subnet in $SUBNETS; do
    echo "[+] 扫描 $subnet.0/24"
    
    # Ping扫描
    for i in $(seq 1 254); do
        (ping -c 1 -W 1 $subnet.$i > /dev/null 2>&1 && echo "[+] $subnet.$i 在线") &
    done
    wait
    
    # ARP扫描
    if [ -n "$INTERFACE" ]; then
        for i in $(seq 1 254); do
            (arping -c 1 -I $INTERFACE $subnet.$i > /dev/null 2>&1 && echo "[+] $subnet.$i 在线(ARP)") &
        done
        wait
    fi
done
```

---

## 路由表分析

### 路由表枚举

```bash
#!/bin/bash
# route_enum.sh - 路由表枚举

echo "[+] 枚举路由表..."

# Linux路由表
echo "[+] Linux路由表:"
ip route show 2>/dev/null

# 静态路由
echo "[+] 静态路由:"
cat /etc/network/routes 2>/dev/null
cat /etc/sysconfig/network-scripts/route-* 2>/dev/null

# 默认网关
echo "[+] 默认网关:"
ip route show default 2>/dev/null
route -n 2>/dev/null | grep "0.0.0.0"
```

### 路由跟踪

```bash
#!/bin/bash
# traceroute.sh - 路由跟踪

TARGET=$1

echo "[+] 跟踪到 $TARGET 的路由..."

# 使用traceroute
traceroute $TARGET

# 或使用tracepath
tracepath $TARGET

# 或使用mtr
mtr --report $TARGET
```

### 路由策略分析

```bash
#!/bin/bash
# route_policy.sh - 路由策略分析

echo "[+] 分析路由策略..."

# 策略路由
echo "[+] 策略路由:"
ip rule show

# 路由表
echo "[+] 路由表:"
ip route show table all

# 路由缓存
echo "[+] 路由缓存:"
ip route show cache
```

---

## DNS枚举

### 基础DNS枚举

```bash
#!/bin/bash
# dns_enum.sh - 基础DNS枚举

DOMAIN=$1

echo "[+] DNS枚举: $DOMAIN"

# DNS记录查询
echo "[+] A记录:"
dig $DOMAIN A +short

echo "[+] AAAA记录:"
dig $DOMAIN AAAA +short

echo "[+] MX记录:"
dig $DOMAIN MX +short

echo "[+] NS记录:"
dig $DOMAIN NS +short

echo "[+] TXT记录:"
dig $DOMAIN TXT +short

echo "[+] SOA记录:"
dig $DOMAIN SOA +short
```

### 子域名枚举

```bash
#!/bin/bash
# subdomain_enum.sh - 子域名枚举

DOMAIN=$1

echo "[+] 枚举子域名: $DOMAIN"

# 使用字典枚举
SUBDOMAINS="www mail ftp smtp pop imap webmail ns1 ns2 dns vpn api dev staging test admin portal"

for sub in $SUBDOMAINS; do
    result=$(dig +short $sub.$DOMAIN A)
    if [ -n "$result" ]; then
        echo "[+] $sub.$DOMAIN: $result"
    fi
done

# 使用DNS区域传送
echo "[+] 尝试DNS区域传送:"
dig axfr $DOMAIN @ns1.$DOMAIN
```

### DNS反向查询

```bash
#!/bin/bash
# dns_reverse.sh - DNS反向查询

IP=$1

echo "[+] DNS反向查询: $IP"

# PTR记录查询
echo "[+] PTR记录:"
dig -x $IP +short

# 多个IP反向查询
for i in $(seq 1 10); do
    result=$(dig -x $IP.$i +short)
    if [ -n "$result" ]; then
        echo "[+] $IP.$i: $result"
    fi
done
```

---

## 端口扫描辅助

### 快速端口扫描

```bash
#!/bin/bash
# port_quick.sh - 快速端口扫描

TARGET=$1

echo "[+] 快速扫描 $TARGET 的常用端口..."

PORTS="21 22 23 25 53 80 110 135 139 143 443 445 993 995 1433 1521 3306 3389 5432 5900 8080"

for port in $PORTS; do
    (echo > /dev/tcp/$TARGET/$port) 2>/dev/null && echo "[+] 端口 $port 开放" &
done
wait
```

### Banner抓取

```bash
#!/bin/bash
# banner_grab.sh - Banner抓取

TARGET=$1
PORT=$2

echo "[+] 抓取 $TARGET:$PORT 的banner..."

# 使用nc抓取
echo "" | nc -w 3 $TARGET $PORT

# 使用nmap
nmap -sV -p $PORT $TARGET
```

---

## 综合拓扑发现脚本

### 完整拓扑发现

```bash
#!/bin/bash
# topo_discovery.sh - 综合拓扑发现

REPORT="topo_$(date +%Y%m%d).txt"

echo "======================================" > $REPORT
echo "网络拓扑发现报告" >> $REPORT
echo "时间: $(date)" >> $REPORT
echo "======================================" >> $REPORT

# 本地网络信息
echo -e "\n[本地网络信息]" >> $REPORT
ip addr show >> $REPORT 2>/dev/null
ip route show >> $REPORT 2>/dev/null

# 扫描本地网段
LOCAL_IP=$(ip route get 1 | head -1 | awk '{print $7}')
NETWORK=$(echo $LOCAL_IP | cut -d. -f1-3)

echo -e "\n[扫描 $NETWORK.0/24]" >> $REPORT
for i in $(seq 1 254); do
    (ping -c 1 -W 1 $NETWORK.$i > /dev/null 2>&1 && echo "$NETWORK.$i 在线" >> $REPORT) &
done
wait

# DNS枚举
echo -e "\n[DNS信息]" >> $REPORT
cat /etc/resolv.conf >> $REPORT 2>/dev/null

echo "[+] 报告已保存到 $REPORT"
```

### 自动化拓扑映射

```bash
#!/bin/bash
# auto_topo.sh - 自动化拓扑映射

NETWORK=$1
OUTPUT="topo_map_$(date +%Y%m%d).txt"

echo "[+] 自动化拓扑映射: $NETWORK.0/24"

# 主机发现
echo "[+] 主机发现..."
ALIVE_HOSTS=()
for i in $(seq 1 254); do
    (ping -c 1 -W 1 $NETWORK.$i > /dev/null 2>&1 && echo $NETWORK.$i >> /tmp/alive_hosts.txt) &
done
wait

# 读取存活主机
if [ -f /tmp/alive_hosts.txt ]; then
    ALIVE_HOSTS=$(cat /tmp/alive_hosts.txt)
fi

# 端口扫描
echo "[+] 端口扫描..."
for host in $ALIVE_HOSTS; do
    echo "=== $host ===" >> $OUTPUT
    for port in 21 22 23 25 53 80 110 135 139 143 443 445 3306 3389; do
        (echo > /dev/tcp/$host/$port) 2>/dev/null && echo "端口 $port 开放" >> $OUTPUT &
    done
    wait
done

echo "[+] 拓扑映射完成，结果保存到 $OUTPUT"
```

---

## 隐蔽扫描技术

### 低速扫描

```bash
#!/bin/bash
# scan_stealth.sh - 低速隐蔽扫描

NETWORK=$1
DELAY=0.5

echo "[+] 低速隐蔽扫描: $NETWORK.0/24"

for i in $(seq 1 254); do
    (ping -c 1 -W 1 $NETWORK.$i > /dev/null 2>&1 && echo "[+] $NETWORK.$i 在线") &
    sleep $DELAY
done
wait
```

### 随机化扫描

```bash
#!/bin/bash
# scan_random.sh - 随机化扫描

NETWORK=$1

echo "[+] 随机化扫描: $NETWORK.0/24"

# 随机化IP顺序
shuf -i 1-254 | while read i; do
    (ping -c 1 -W 1 $NETWORK.$i > /dev/null 2>&1 && echo "[+] $NETWORK.$i 在线") &
done
wait
```

### 伪造源IP扫描

```bash
#!/bin/bash
# scan_spoofed.sh - 伪造源IP扫描（需要root权限）

NETWORK=$1
SPOOFED_IP=$2

echo "[+] 伪造源IP扫描..."

# 使用hping3
sudo hping3 -1 -a $SPOOFED_IP -c 1 $NETWORK.1
```

---

## 工具推荐

| 工具 | 用途 | 安装方式 |
|------|------|----------|
| nmap | 综合扫描 | apt install nmap |
| arping | ARP扫描 | apt install arping |
| netdiscover | ARP发现 | apt install netdiscover |
| hping3 | 高级扫描 | apt install hping3 |
| masscan | 高速扫描 | apt install masscan |
| fping | 并发ping | apt install fping |
| dnsenum | DNS枚举 | apt install dnsenum |
| fierce | 子域名枚举 | pip install fierce |

---

## 最佳实践

1. **被动优先**：优先使用被动侦察技术，减少被检测的风险
2. **分层扫描**：先快速扫描，再深入扫描
3. **结果验证**：验证扫描结果的准确性
4. **隐蔽性**：使用随机化和延迟技术提高隐蔽性
5. **合规性**：确保所有操作在授权范围内进行

---

*最后更新：2026-08-22*
