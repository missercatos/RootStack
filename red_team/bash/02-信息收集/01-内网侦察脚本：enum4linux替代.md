# 内网侦察脚本：enum4linux替代

在渗透测试的信息收集阶段，内网侦察是获取目标网络信息的关键步骤。本章介绍如何使用纯Bash脚本实现类似enum4linux的功能，包括主机发现、端口扫描、服务识别和枚举。

---

## 主机发现

### Ping扫描脚本

```bash
#!/bin/bash
# ping_discovery.sh - 网段主机发现脚本

NETWORK=$1
TIMEOUT=1

echo "[+] 开始扫描网段: $NETWORK"

for i in $(seq 1 254); do
    (ping -c 1 -W $TIMEOUT $NETWORK.$i > /dev/null 2>&1 && echo "[+] $NETWORK.$i 在线") &
done
wait

echo "[+] 扫描完成"
```

### ARP扫描脚本

```bash
#!/bin/bash
# arp_discovery.sh - ARP主机发现（仅限本机网段）

INTERFACE=$1
NETWORK=$2

echo "[+] 使用ARP扫描网段: $NETWORK"

# 使用arping进行ARP扫描
for i in $(seq 1 254); do
    (arping -c 1 -I $INTERFACE $NETWORK.$i > /dev/null 2>&1 && echo "[+] $NETWORK.$i 在线") &
done
wait
```

### 综合主机发现脚本

```bash
#!/bin/bash
# host_discovery.sh - 综合主机发现脚本

NETWORK=$1
OUTPUT_FILE="hosts_$(date +%Y%m%d).txt"

echo "[+] 开始主机发现..."

# Ping扫描
for i in $(seq 1 254); do
    (ping -c 1 -W 1 $NETWORK.$i > /dev/null 2>&1 && echo $NETWORK.$i >> $OUTPUT_FILE) &
done
wait

echo "[+] 发现 $(wc -l < $OUTPUT_FILE) 台主机"
```

---

## 端口扫描

### 基础端口扫描

```bash
#!/bin/bash
# port_scan_basic.sh - 基础端口扫描

TARGET=$1
START_PORT=$2
END_PORT=$3

echo "[+] 扫描目标: $TARGET"

for port in $(seq $START_PORT $END_PORT); do
    (echo > /dev/tcp/$TARGET/$port) 2>/dev/null && echo "[+] 端口 $port 开放"
done
```

### Nmap替代扫描

```bash
#!/bin/bash
# port_scan_nc.sh - 使用nc进行端口扫描

TARGET=$1
PORTS="21 22 23 25 53 80 110 111 135 139 143 443 445 993 995 1433 1521 3306 3389 5432 5900 8080 8443"

echo "[+] 扫描目标: $TARGET"

for port in $PORTS; do
    (nc -z -w 1 $TARGET $port 2>/dev/null && echo "[+] 端口 $port 开放") &
done
wait
```

### 并发端口扫描

```bash
#!/bin/bash
# port_scan_parallel.sh - 并发端口扫描

TARGET=$1
START_PORT=${2:-1}
END_PORT=${3:-65535}

echo "[+] 并发扫描目标: $TARGET"
echo "[+] 扫描端口范围: $START_PORT - $END_PORT"

# 使用xargs进行并发扫描
seq $START_PORT $END_PORT | xargs -P 100 -I {} bash -c '
    echo > /dev/tcp/'$TARGET'/{} 2>/dev/null && echo "[+] 端口 {} 开放"
'
```

### 使用/proc/net/tcp扫描

```bash
#!/bin/bash
# scan_proc.sh - 通过/proc/net/tcp扫描

TARGET=$1
TIMEOUT=1

echo "[+] 扫描目标: $TARGET"

# 读取/proc/net/tcp获取连接信息
cat /proc/net/tcp | awk '{print $2}' | grep -v local | while read line; do
    port=$((16#${line##*:}))
    if [ $port -gt 0 ] && [ $port -lt 65535 ]; then
        (echo > /dev/tcp/$TARGET/$port 2>/dev/null && echo "[+] 端口 $port 开放") &
    fi
done
wait
```

---

## 服务识别

### Banner抓取脚本

```bash
#!/bin/bash
# banner_grab.sh - 服务Banner抓取

TARGET=$1
PORT=$2

echo "[+] 抓取目标 $TARGET:$PORT 的banner..."

# 使用nc抓取banner
BANNER=$(echo "" | nc -w 3 $TARGET $port 2>/dev/null)

if [ -n "$BANNER" ]; then
    echo "[+] Banner: $BANNER"
else
    echo "[-] 无法获取banner"
fi
```

### 多端口Banner抓取

```bash
#!/bin/bash
# banner_multi.sh - 多端口Banner抓取

TARGET=$1
PORTS="21 22 23 25 80 110 143 443 993 995 3306 3389 5432"

echo "[+] 抓取目标 $TARGET 的banner..."

for port in $PORTS; do
    BANNER=$(echo "" | nc -w 2 $TARGET $port 2>/dev/null)
    if [ -n "$BANNER" ]; then
        echo "[+] 端口 $port: $BANNER"
    fi
done
```

### HTTP服务识别

```bash
#!/bin/bash
# http_identify.sh - HTTP服务识别

TARGET=$1
PORT=${2:-80}

echo "[+] 识别HTTP服务: $TARGET:$PORT"

# 获取HTTP头信息
curl -sI http://$TARGET:$PORT

# 获取服务器信息
curl -sI http://$TARGET:$PORT | grep -i "server\|x-powered-by"
```

### SMB服务识别

```bash
#!/bin/bash
# smb_identify.sh - SMB服务识别

TARGET=$1

echo "[+] 识别SMB服务: $TARGET"

# 使用nmblookup
nmblookup -A $TARGET

# 使用smbclient
smbclient -L $TARGET -N

# 使用rpcclient
rpcclient -U "" -N $TARGET -c "srvinfo"
```

---

## LDAP枚举

### LDAP基础枚举

```bash
#!/bin/bash
# ldap_enum.sh - LDAP基础枚举

TARGET=$1
BASE_DN=$2

echo "[+] LDAP枚举: $TARGET"

# 匿名绑定测试
ldapsearch -x -H ldap://$TARGET -b "$BASE_DN" "(objectClass=*)"

# 枚举用户
ldapsearch -x -H ldap://$TARGET -b "$BASE_DN" "(objectClass=user)" sAMAccountName

# 枚举组
ldapsearch -x -H ldap://$TARGET -b "$BASE_DN" "(objectClass=group)" cn
```

### 高级LDAP枚举

```bash
#!/bin/bash
# ldap_enum_advanced.sh - 高级LDAP枚举

TARGET=$1
BASE_DN=$2
USER=$3
PASS=$4

echo "[+] 高级LDAP枚举: $TARGET"

# 认证绑定
ldapsearch -x -H ldap://$TARGET -D "$USER" -w "$PASS" -b "$BASE_DN" "(objectClass=*)"

# 枚举管理员组
ldapsearch -x -H ldap://$TARGET -D "$USER" -w "$PASS" -b "$BASE_DN" "(&(objectClass=group)(cn=Domain Admins))" member

# 枚举计算机
ldapsearch -x -H ldap://$TARGET -D "$USER" -w "$PASS" -b "$BASE_DN" "(objectClass=computer)" cn
```

---

## 综合侦察脚本

### 完整内网侦察脚本

```bash
#!/bin/bash
# enum4linux_alt.sh - enum4linux替代脚本

TARGET=$1
OUTPUT_DIR="enum_$(date +%Y%m%d)"

mkdir -p $OUTPUT_DIR

echo "[+] 开始枚举目标: $TARGET"

# 基本信息
echo "[+] 获取基本信息..."
ping -c 1 $TARGET > $OUTPUT_DIR/ping.txt
whois $TARGET > $OUTPUT_DIR/whois.txt 2>/dev/null

# 端口扫描
echo "[+] 扫描端口..."
nmap -sS -sV -O $TARGET > $OUTPUT_DIR/nmap_full.txt

# 服务枚举
echo "[+] 枚举服务..."
# SSH
ssh -o StrictHostKeyChecking=no $TARGET "uname -a" > $OUTPUT_DIR/ssh_info.txt 2>/dev/null

# SMB
smbclient -L $TARGET -N > $OUTPUT_DIR/smb_info.txt 2>/dev/null

# HTTP
curl -sI http://$TARGET > $OUTPUT_DIR/http_info.txt 2>/dev/null

echo "[+] 信息已保存到 $OUTPUT_DIR/"
```

### 自动化侦察脚本

```bash
#!/bin/bash
# auto_recon.sh - 自动化侦察脚本

TARGET=$1
REPORT="recon_report_$(date +%Y%m%d).txt"

echo "======================================" > $REPORT
echo "侦察报告: $TARGET" >> $REPORT
echo "时间: $(date)" >> $REPORT
echo "======================================" >> $REPORT

# 主机信息
echo -e "\n[主机信息]" >> $REPORT
ping -c 3 $TARGET >> $REPORT 2>/dev/null

# 端口扫描
echo -e "\n[端口扫描]" >> $REPORT
nmap -sS -sV $TARGET >> $REPORT 2>/dev/null

# DNS信息
echo -e "\n[DNS信息]" >> $REPORT
dig $TARGET >> $REPORT 2>/dev/null
nslookup $TARGET >> $REPORT 2>/dev/null

echo "[+] 报告已保存到 $REPORT"
```

---

## 工具安装

### 安装必要工具

```bash
# Debian/Ubuntu
sudo apt update
sudo apt install -y nmap netcat smbclient ldap-utils dnsutils curl

# CentOS/RHEL
sudo yum install -y nmap nc samba-client openldap-clients bind-utils curl

# macOS
brew install nmap netcat smbclient openldap bind curl
```

### 工具组合使用

```bash
# 使用nmap进行服务枚举
nmap -sV -sC -O -A $TARGET

# 使用enum4linux进行SMB枚举
enum4linux -a $TARGET

# 使用ldapsearch进行LDAP枚举
ldapsearch -x -H ldap://$TARGET -b "DC=example,DC=com"
```

---

## 最佳实践

1. **被动侦察优先**：优先使用被动侦察技术，减少被检测的风险
2. **扫描速度控制**：适当控制扫描速度，避免触发IDS/IPS
3. **结果保存**：及时保存扫描结果，便于后续分析
4. **隐蔽性**：使用随机源端口和延迟，提高隐蔽性
5. **合规性**：确保所有操作在授权范围内进行

---

*最后更新：2026-08-22*
