# 57 - DNS 服务器搭建

> DNS 是互联网的基础设施之一。虽然大多数场景下我们可以使用云服务商的 DNS 或公共 DNS（如 8.8.8.8、114.114.114.114），但自建 DNS 服务器在内部网络管理、域名托管、DNS 劫持防护、Kubernetes 服务发现等场景中仍不可或缺。本章在 [[23-DNS与域名系统]] 的基础上，深入讲解 BIND9、Unbound、dnsmasq 和 CoreDNS 的搭建与配置。

---

## 57.1 权威 DNS vs 递归 DNS

### 两种 DNS 服务器类型

```
递归 DNS（Recursive Resolver） 权威 DNS（Authoritative Server）
 用户请求 google.com 返回 google.com 的 IP
 │ │
 ▼ ▼
┌──────────┐ .root ┌─────────┐ ┌──────────────┐
│ 递归查询 │ ──────▶ │ 根服务器 │ │ ns1.google │
│ (Unbound)│ ◀────── │ │ │ .com 权威DNS │
└──────────┘ .com └─────────┘ └──────────────┘
 │ ▲
 │ ns1.google.com │
 └─────────────────────────────────────────┘
```

| 特性 | 递归 DNS | 权威 DNS |
|------|---------|---------|
| 用途 | 替用户解析域名 | 存储域名的最终 DNS 记录 |
| 典型服务 | Unbound, BIND（递归模式） | BIND9, PowerDNS, CoreDNS |
| 缓存 | 大量缓存加速请求 | 不缓存（返回自己管理的记录） |
| 查询来源 | 局域网客户端 | 全互联网 |
| 安全 | DNSSEC 验证 | DNSSEC 签名 |

---

## 57.2 BIND9：权威 DNS 服务器

BIND（Berkeley Internet Name Domain）是最古老、使用最广泛的 DNS 服务器软件。

### 安装

```bash
# Debian / Ubuntu
sudo apt install bind9 bind9utils bind9-doc -y

# RHEL / Fedora
sudo dnf install bind bind-utils -y

# Arch
sudo pacman -S bind

# 启动
sudo systemctl enable --now named # BIND 的服务名是 named
```

### 配置文件结构

```bash
# 主配置目录
# Debian/Ubuntu: /etc/bind/
# RHEL/Fedora: /etc/named.conf 或 /etc/named/
# Arch: /etc/named.conf
```

```
/etc/bind/
├── named.conf # 主配置文件（包含其他配置）
├── named.conf.options # 全局选项
├── named.conf.local # 本地 zone 定义
├── named.conf.default-zones # 默认 zone
├── zones/
│ ├── db.example.com # 正向解析 zone 文件
│ └── db.192.168.1 # 反向解析 zone 文件
```

### 基本配置

```bash
sudo vim /etc/bind/named.conf.options
```

```
options {
 directory "/var/cache/bind";
 listen-on port 53 { 127.0.0.1; 192.168.1.10; };
 listen-on-v6 port 53 { ::1; };
 allow-query { 192.168.0.0/16; 10.0.0.0/8; localhost; };
 allow-transfer { 192.168.1.20; }; # 允许从服务器传输 zone

 recursion no; # 权威 DNS 关闭递归
 dnssec-validation auto;
 version "Not disclosed"; # 隐藏版本号
};
```

### Zone 文件格式

**正向解析 zone（域名 → IP）：**

```bash
# 在 named.conf.local 中声明 zone
sudo vim /etc/bind/named.conf.local
```

```
zone "example.com" {
 type master;
 file "/etc/bind/zones/db.example.com";
 allow-update { none; };
};
```

```bash
sudo mkdir -p /etc/bind/zones
sudo vim /etc/bind/zones/db.example.com
```

```
$TTL 86400
$ORIGIN example.com.

; SOA 记录（Start of Authority）
@ IN SOA ns1.example.com. admin.example.com. (
 2026072401 ; 序列号（YYYYMMDDNN 格式）
 3600 ; Refresh（从服务器多久检查一次更新）
 1800 ; Retry（检查失败后重试间隔）
 604800 ; Expire（从服务器过期时间）
 86400 ; Minimum TTL（否定应答缓存时间）
)

; NS 记录（指定域名服务器）
@ IN NS ns1.example.com.
@ IN NS ns2.example.com.

; A 记录（域名 → IPv4）
ns1 IN A 192.168.1.10
ns2 IN A 192.168.1.20
@ IN A 192.168.1.100 ; example.com 本身

; AAAA 记录（域名 → IPv6）
@ IN AAAA 2001:db8::100

; CNAME 记录（别名）
www IN CNAME @
mail IN CNAME @
docs IN CNAME ghs.google.com. ; 指向外部服务

; MX 记录（邮件服务器）
@ IN MX 10 mail.example.com.
@ IN MX 20 mx-backup.example.com.

; TXT 记录（文本记录，SPF/DKIM/验证等）
@ IN TXT "v=spf1 ip4:192.168.1.100 ~all"

; SRV 记录（服务定位）
_sip._tcp IN SRV 10 5 5060 sip.example.com.
```

### 反向解析 zone（IP → 域名）

```bash
sudo vim /etc/bind/named.conf.local
```

```
zone "1.168.192.in-addr.arpa" {
 type master;
 file "/etc/bind/zones/db.192.168.1";
};
```

```bash
sudo vim /etc/bind/zones/db.192.168.1
```

```
$TTL 86400
@ IN SOA ns1.example.com. admin.example.com. (
 2026072401 3600 1800 604800 86400 )

 IN NS ns1.example.com.

10 IN PTR ns1.example.com.
20 IN PTR ns2.example.com.
100 IN PTR example.com.
101 IN PTR web.example.com.
```

### 验证与重载

```bash
# 检查主配置文件语法
sudo named-checkconf

# 检查 zone 文件语法
sudo named-checkzone example.com /etc/bind/zones/db.example.com
sudo named-checkzone 1.168.192.in-addr.arpa /etc/bind/zones/db.192.168.1

# 重载配置（不中断服务）
sudo rndc reload

# 或重启
sudo systemctl reload named
```

### 测试 DNS 解析

```bash
# 向本机 DNS 查询
dig @192.168.1.10 example.com A
dig @192.168.1.10 www.example.com

# 查询 MX 记录
dig @192.168.1.10 example.com MX

# 反向查询
dig @192.168.1.10 -x 192.168.1.10

# 查询 NS 记录
dig @192.168.1.10 example.com NS

# 查询 SOA（获取序列号、刷新时间等）
dig @192.168.1.10 example.com SOA

# 递归追踪（使用公共 DNS）
dig +trace example.com

# AXFR 全量传输测试（从服务器用）
dig @192.168.1.10 example.com AXFR
```

---

## 57.3 主从复制

多台 DNS 服务器提供冗余，通过 zone transfer 同步记录。

**主服务器（Master）：**

```bash
sudo vim /etc/bind/named.conf.options
```

```
options {
 allow-transfer { 192.168.1.20; }; # 允许从服务器传输
 also-notify { 192.168.1.20; }; # 变更时主动通知从服务器
 notify yes;
};
```

**从服务器（Slave）：**

```bash
sudo vim /etc/bind/named.conf.local
```

```
zone "example.com" {
 type slave;
 file "/var/cache/bind/db.example.com.slave";
 masters { 192.168.1.10; };
};
```

```bash
sudo systemctl restart named

# 验证从服务器同步成功
dig @192.168.1.20 example.com SOA
ls -la /var/cache/bind/
```

---

## 57.4 Unbound：递归 DNS 解析器

Unbound 是轻量、安全的递归 DNS 解析器，支持 DNSSEC 验证、缓存、访问控制，常被用作局域网 DNS 缓存服务器。

### 安装与基本配置

```bash
sudo apt install unbound -y # Debian/Ubuntu
sudo dnf install unbound -y # RHEL/Fedora
sudo pacman -S unbound # Arch

# 编辑配置
sudo vim /etc/unbound/unbound.conf
```

```
server:
 interface: 0.0.0.0
 interface: ::0
 port: 53
 access-control: 192.168.0.0/16 allow
 access-control: 10.0.0.0/8 allow
 access-control: 127.0.0.0/8 allow

 # 上游 DNS（如需转发而非递归）
 # forward-zone:
 # name: "."
 # forward-addr: 8.8.8.8
 # forward-addr: 1.1.1.1

 # 拒绝操作时打印最少信息
 hide-identity: yes
 hide-version: yes

 # 缓存设置
 cache-min-ttl: 300
 cache-max-ttl: 86400

 # DNSSEC
 auto-trust-anchor-file: "/var/lib/unbound/root.key"
 val-clean-additional: yes
 val-permissive-mode: no

 # 隐私
 qname-minimisation: yes # DNS 查询名称最小化
 prefetch: yes # 缓存条目接近过期时主动刷新
```

```bash
sudo systemctl enable --now unbound

# 测试
dig @127.0.0.1 google.com
```

### DNSSEC 验证

```bash
# 验证一个已签名的域名
dig @127.0.0.1 cloudflare.com +dnssec
# 返回结果中应有 ad（authenticated data）标志

# 验证一个未正确签名的域名
dig @127.0.0.1 www.dnssec-failed.org
# 应返回 SERVFAIL

# 检查信任锚
sudo unbound-anchor -l
```

### 自定义根区域转发

当需要将内部域名指向 BIND 权威服务器时：

```bash
sudo vim /etc/unbound/unbound.conf.d/custom.conf
```

```
# 将内部域名的查询转发到本地 BIND 权威服务器
stub-zone:
 name: "example.com"
 stub-addr: 192.168.1.10@53

# 反向解析区域
stub-zone:
 name: "1.168.192.in-addr.arpa"
 stub-addr: 192.168.1.10@53

# 隐私/安全相关的域名本地阻断
local-zone: "use-application-dns.net" static
local-data: "use-application-dns.net. 3600 IN A 0.0.0.0"
```

---

## 57.5 dnsmasq：轻量 DNS + DHCP

dnsmasq 是嵌入式设备和小型局域网中常用的轻量级 DNS 转发器和 DHCP 服务器。

### 安装与配置

```bash
sudo apt install dnsmasq -y # Debian/Ubuntu
sudo dnf install dnsmasq -y # RHEL/Fedora

# 配置文件： /etc/dnsmasq.conf
sudo vim /etc/dnsmasq.conf
```

```ini
# 监听接口
interface=eth0
listen-address=127.0.0.1
listen-address=192.168.1.1

# 上游 DNS（转发）
server=114.114.114.114
server=8.8.8.8

# 本地域名解析（hosts 文件）
domain=home.local
expand-hosts

# 自定义 DNS 记录
address=/router.home.local/192.168.1.1
address=/nas.home.local/192.168.1.50
address=/printer.home.local/192.168.1.60

# CNAME
cname=www,home.local

# 缓存大小
cache-size=1000

# DHCP
dhcp-range=192.168.1.100,192.168.1.200,12h
dhcp-option=3,192.168.1.1 # 默认网关
dhcp-option=6,192.168.1.1 # DNS 服务器
dhcp-host=aa:bb:cc:dd:ee:ff,192.168.1.101,web-server # 静态 DHCP

# 日志
log-queries
log-dhcp
```

```bash
sudo systemctl enable --now dnsmasq

# 客户端测试
dig @192.168.1.1 nas.home.local
```

### dnsmasq 常用场景

```bash
# 场景 1：DNS 分流 — 国内域名走国内 DNS，其他走 Google DNS
# /etc/dnsmasq.d/split-dns.conf
server=/cn/114.114.114.114
server=/com/114.114.114.114
server=/net/114.114.114.114
server=/#/8.8.8.8

# 场景 2：开发环境泛域名解析
address=/dev/127.0.0.1
# app1.dev → 127.0.0.1
# api.app1.dev → 127.0.0.1

# 场景 3：广告/追踪域名屏蔽
# /etc/dnsmasq.d/adblock.conf
address=/doubleclick.net/0.0.0.0
address=/analytics.example.com/0.0.0.0
# 可以使用 hosts 文件批量导入
```

---

## 57.6 CoreDNS：现代插件式 DNS

CoreDNS 用 Go 编写，是 Kubernetes 的默认 DNS，也适用于传统服务器场景。通过插件链实现灵活功能。

### 安装

```bash
# 从 GitHub 下载二进制
COREDNS_VER=$(curl -s https://api.github.com/repos/coredns/coredns/releases/latest | jq -r .tag_name)
wget https://github.com/coredns/coredns/releases/download/${COREDNS_VER}/coredns_${COREDNS_VER#v}_linux_amd64.tgz
tar xzf coredns_*_linux_amd64.tgz
sudo mv coredns /usr/local/bin/

# 创建 systemd 服务
sudo tee /etc/systemd/system/coredns.service << 'EOF'
[Unit]
Description=CoreDNS
After=network.target

[Service]
User=nobody
ExecStart=/usr/local/bin/coredns -conf /etc/coredns/Corefile
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF
```

### Corefile 配置

```bash
sudo mkdir /etc/coredns
sudo vim /etc/coredns/Corefile
```

```dns
# 递归解析（本地 DNS 缓存）
. {
 forward . 8.8.8.8 1.1.1.1
 cache 3600
 errors
 log
 health :8053
 prometheus :9153
}

# 权威服务器 — example.com 域
example.com {
 file /etc/coredns/example.com.zone
 log
 errors
}

# 内部服务发现 — 从 /etc/hosts 加载
internal.local {
 hosts /etc/coredns/internal.hosts {
 fallthrough
 }
 log
}
```

```bash
# Zone 文件格式（与 BIND 相同）
sudo vim /etc/coredns/example.com.zone
```

```
$ORIGIN example.com.
$TTL 3600

@ IN SOA ns1.example.com. admin.example.com. 2026072401 7200 3600 1209600 3600
@ IN NS ns1.example.com.
ns1 IN A 192.168.1.10
@ IN A 192.168.1.100
www IN CNAME @
```

```bash
# hosts 格式的内部服务记录
sudo vim /etc/coredns/internal.hosts
```

```
192.168.1.10 ns1.internal.local
192.168.1.50 nas.internal.local
192.168.1.60 printer.internal.local
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now coredns
```

### CoreDNS 常用插件

| 插件 | 功能 |
|------|------|
| `file` | 从 zone 文件加载记录（类似 BIND） |
| `forward` | 转发到上游 DNS |
| `cache` | DNS 缓存 |
| `hosts` | 从 hosts 文件加载记录 |
| `kubernetes` | K8s 服务发现 |
| `rewrite` | 重写 DNS 查询 |
| `health` | HTTP 健康检查端点 |
| `prometheus` | Prometheus metrics 端点 |
| `etcd` | 从 etcd 读取 DNS 记录 |
| `log` | 查询日志 |

---

## 57.7 DNS 安全性

### 速率限制（BIND RRL）

```bash
sudo vim /etc/bind/named.conf.options
```

```
options {
 rate-limit {
 responses-per-second 5;
 window 5;
 slip 2;
 };
};
```

### 限制查询来源

```bash
# BIND
allow-query { 192.168.0.0/16; localhost; };
allow-recursion { 192.168.0.0/16; localhost; };

# Unbound
access-control: 0.0.0.0/0 refuse
access-control: 192.168.0.0/16 allow
```

### DNSSEC 签名（在权威 DNS 上）

```bash
# BIND 9.9+ 内置 DNSSEC 签名
dnssec-keygen -a RSASHA256 -b 2048 -n ZONE example.com
dnssec-keygen -a RSASHA256 -b 2048 -n ZONE -f KSK example.com

sudo vim /etc/bind/named.conf.local
```

```
zone "example.com" {
 type master;
 file "/etc/bind/zones/db.example.com.signed";
 auto-dnssec maintain;
 inline-signing yes;
};
```

```bash
sudo rndc sign example.com
dig @127.0.0.1 example.com +dnssec
```

### TSIG（事务签名，用于 zone transfer 认证）

```bash
# 生成共享密钥
tsig-keygen -a HMAC-SHA256 slave-key >> /etc/bind/named.conf.local

# 在主从服务器 named.conf 中都配置
key "slave-key" {
 algorithm hmac-sha256;
 secret "生成的base64密钥";
};

# 主服务器
allow-transfer { key slave-key; };

# 从服务器
masters { 192.168.1.10 key slave-key; };
```

---

## 57.8 DNS 服务器选型指南

| 场景 | 推荐方案 | 理由 |
|------|---------|------|
| 自建权威 DNS（域名托管） | BIND9 | 历史悠久、文档丰富、业界标准 |
| 局域网 DNS 缓存 | Unbound | 安全、支持 DNSSEC、隐私保护 |
| 小型/家庭网络 DNS+DHCP | dnsmasq | 极简配置，一条命令配好 |
| Kubernetes 集群 DNS | CoreDNS | 原生 K8s 集成，插件化灵活 |
| 大规模权威 DNS（API 驱动） | PowerDNS | 数据库后端，支持 API 管理 |
| 公共 DNS 服务（高并发） | BIND9 + Unbound | 分级架构 |

---

## 57.9 排错与诊断

```bash
# 检查 DNS 服务器是否响应
dig @dns-server +short example.com
nslookup example.com dns-server

# 测试权威 DNS
dig @auth-ns example.com SOA

# 检测 DNSSEC 链
dig +dnssec example.com +multi

# 测试递归和缓存时间
dig example.com | grep "Query time"
dig example.com | grep "Query time" # 第二次应接近 0

# 检查 zone transfer 是否开放（不应对外网开放）
dig @dns-server example.com AXFR

# 检查 BIND 日志
sudo journalctl -u named -f
sudo tail -f /var/log/named/query.log # 如启用 querylog

# 检查 Unbound 日志
sudo journalctl -u unbound -f

# 检查端口监听
sudo ss -tulnp | grep 53

# 测试从外网解析（检查是否只有被允许的网段可以查询）
nmap -Pn -p 53 --script dns-recursion dns-server-ip
```

### 常见问题

| 问题 | 可能原因 | 解决 |
|------|---------|------|
| `SERVFAIL` | Zone 文件语法错误 | `named-checkzone` 检查 |
| 递归查询失败 | 上游 DNS 不可达 | 检查防火墙和上游联通性 |
| 从服务器未同步 | zone transfer 被拒 | 检查 `allow-transfer` 和 `also-notify` |
| 解析慢 | 缓存太小/上游慢 | 增大 cache-size，更换上游 |
| DNSSEC 验证失败 | 系统时间不准 | `timedatectl` 检查 NTP 同步 |

---

## 57.10 本章总结

| DNS 服务器 | 类型 | 典型用途 | 核心配置 |
|-----------|------|---------|---------|
| BIND9 | 权威 + 递归 | 域名托管、主从复制 | `named.conf` + zone 文件 |
| Unbound | 递归解析器 | 局域网 DNS 缓存、DNSSEC 验证 | `unbound.conf` |
| dnsmasq | 转发器 + DHCP | 家庭/小型网络 | `dnsmasq.conf` |
| CoreDNS | 插件式 | K8s 服务发现、灵活路由 | `Corefile` |

> 进一步阅读：DNS 协议基础与客户端配置见 [[23-DNS与域名系统]]，防火墙规则中的 DNS 端口控制见 [[22-防火墙与安全]]。
