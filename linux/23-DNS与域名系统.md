# 23 - DNS 与域名系统

> DNS（Domain Name System）是互联网的电话簿。它将人类可读的域名（如 `www.example.com`）翻译为机器使用的 IP 地址。本章从 DNS 基本原理讲起，涵盖 Linux 上的 DNS 客户端配置、systemd-resolved 与 NetworkManager 的 DNS 管理、dig 等诊断工具的使用，以及现代 DNS 加密协议（DoH/DoT）的部署。

---

## 23.1 DNS 基本原理

### 域名解析过程

当你访问 `www.example.com` 时，DNS 解析过程如下：

```
用户输入 www.example.com
 │
 ▼
┌─────────────────────┐
│ 本地缓存 │ ← 浏览器缓存 / 系统缓存
│ (stub resolver) │
└─────────┬───────────┘
 │ 未命中
 ▼
┌─────────────────────┐
│ /etc/hosts │ ← 本地静态映射
└─────────┬───────────┘
 │ 未命中
 ▼
┌─────────────────────┐
│ DNS 递归解析器 │ ← 如 8.8.8.8 / 系统 DNS
│ (recursive) │
└─────────┬───────────┘
 │
 ▼ (迭代查询)
┌─────────┴─────────┬──────────┬──────────┐
│ 根域名服务器 (.) │ → .com │ → example.com │ → www.example.com
│ │ NS 记录 │ NS 记录 │ A 记录: 93.184.216.34
└────────────────────┴──────────┴──────────────┴─────────────
```

### 核心 DNS 记录类型

| 记录类型 | 用途 | 示例 |
|---------|------|------|
| **A** | IPv4 地址 | `example.com. A 93.184.216.34` |
| **AAAA** | IPv6 地址 | `example.com. AAAA 2606:2800:220:1:248:1893:25c8:1946` |
| **CNAME** | 别名（规范名称） | `www.example.com. CNAME example.com.` |
| **MX** | 邮件服务器 | `example.com. MX 10 mail.example.com.` |
| **NS** | 权威域名服务器 | `example.com. NS ns1.example.com.` |
| **TXT** | 文本信息（SPF/DKIM 等） | `example.com. TXT "v=spf1 ..."` |
| **SOA** | 权威区域起始 | 管理信息、序列号、刷新间隔等 |
| **PTR** | 反向解析（IP → 域名） | `34.216.184.93.in-addr.arpa. PTR example.com.` |
| **SRV** | 服务定位 | `_sip._tcp.example.com. SRV 10 60 5060 sip.example.com.` |
| **CAA** | 证书颁发机构授权 | `example.com. CAA 0 issue "letsencrypt.org"` |

---

## 23.2 客户端 DNS 配置

### /etc/resolv.conf

这是 Linux 上传统的 DNS 客户端配置文件：

```bash
# 查看当前配置
cat /etc/resolv.conf

# 典型内容
nameserver 8.8.8.8
nameserver 1.1.1.1
search example.com internal.example.com
options rotate timeout:2 attempts:3
```

| 指令 | 说明 |
|------|------|
| `nameserver` | DNS 服务器 IP（最多 3 个，按顺序查询） |
| `search` | 搜索域：补全不完整的主机名 |
| `options rotate` | 轮询使用 nameserver 列表 |
| `options timeout:N` | 查询超时时间（秒） |
| `options attempts:N` | 重试次数 |
| `options ndots:N` | 域名中至少 N 个点才视为 FQDN |

> 在现代 Linux 系统中，`/etc/resolv.conf` 通常由网络管理器动态生成，直接编辑会被覆盖。

### /etc/hosts 文件

静态主机名到 IP 的映射，在 DNS 之前查询：

```bash
127.0.0.1 localhost localhost.localdomain
::1 localhost localhost.localdomain

192.168.1.100 myserver.lan myserver
192.168.1.101 database.lan db
10.0.0.1 internal-api.example.com
```

### /etc/nsswitch.conf

控制名称解析的优先级：

```bash
# 查看当前配置
cat /etc/nsswitch.conf | grep hosts
# hosts: files dns # 先查 /etc/hosts，再查 DNS
# hosts: files mdns4_minimal dns # macOS 风格：先本地再 mDNS 再 DNS
# hosts: resolve [!UNAVAIL=return] files # systemd-resolved 模式
```

---

## 23.3 systemd-resolved 与 NetworkManager DNS

### systemd-resolved

现代 systemd 系统的 DNS 解决方案，提供本地 DNS 缓存和 DoT/DoH 支持：

```bash
# 启用 resolved
sudo systemctl enable --now systemd-resolved

# 创建符号链接（替代传统 /etc/resolv.conf）
sudo ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf

# 查看 DNS 状态
resolvectl status
resolvectl statistics

# 查询
resolvectl query archlinux.org
resolvectl query --type=MX gmail.com
```

配置文件 `/etc/systemd/resolved.conf`：

```ini
[Resolve]
# 上游 DNS 服务器
DNS=1.1.1.1#cloudflare-dns.com 8.8.8.8#dns.google 9.9.9.9#dns.quad9.net

# 备用 DNS
FallbackDNS=1.0.0.1 8.8.4.4

# DNS over TLS
DNSOverTLS=yes
# 或 opportunistic（尝试但不强制）

# DNSSEC 验证
DNSSEC=allow-downgrade

# 缓存
Cache=yes
CacheFromLocalhost=no

# 多播 DNS
MulticastDNS=yes
```

```bash
# 按接口设置 DNS（临时）
resolvectl dns eth0 8.8.8.8 1.1.1.1
resolvectl domain eth0 ~example.com

# 查看接口 DNS 配置
resolvectl dns eth0
resolvectl domain eth0
```

### NetworkManager DNS 管理

```bash
# NetworkManager 生成的 resolv.conf
cat /var/run/NetworkManager/resolv.conf

# nmcli 查看 DNS 配置
nmcli device show | grep DNS

# 为特定连接设置 DNS
nmcli connection modify "Wired" ipv4.dns "8.8.8.8 1.1.1.1"
nmcli connection modify "Wired" ipv4.ignore-auto-dns yes
nmcli connection up "Wired"
```

### NetworkManager 与 systemd-resolved 集成

```bash
# /etc/NetworkManager/conf.d/dns-backend.conf
[main]
dns=systemd-resolved
```

---

## 23.4 dig — DNS 诊断利器

`dig`（Domain Information Groper）是 Linux 上最重要的 DNS 查询工具。

### 安装

```bash
# Debian / Ubuntu
sudo apt install dnsutils

# RHEL / Fedora
sudo dnf install bind-utils

# openSUSE
sudo zypper install bind-utils

# Arch
sudo pacman -S bind-tools

# Alpine
apk add bind-tools
```

### 基本查询

```bash
# 最简查询（A 记录）
dig google.com

# 查询特定记录类型
dig example.com A # IPv4 地址
dig example.com AAAA # IPv6 地址
dig example.com MX # 邮件服务器
dig example.com CNAME # 别名
dig example.com TXT # 文本记录
dig example.com NS # 权威域名服务器
dig example.com SOA # 权威起始记录
dig example.com ANY # 所有记录（可能被过滤）

# 反向查询
dig -x 8.8.8.8 # PTR 记录
dig -x 2001:4860:4860::8888

# 指定 DNS 服务器
dig @8.8.8.8 example.com
dig @1.1.1.1 example.com MX
```

### 追踪解析路径

```bash
# 从根域名追踪完整解析过程（+trace）
dig +trace example.com

# 输出解读：
# 1. 根域名服务器的 NS 记录
# 2. .com 顶级域名的 NS 记录
# 3. example.com 的权威 NS 记录
# 4. 最终 A 记录
```

### 输出控制

```bash
# 仅显示结果（短格式）
dig +short example.com
# 93.184.216.34

dig +short example.com MX
# 0 .

dig +short example.com A @1.1.1.1

# 隐藏注释（DNS 头部信息）
dig +noall +answer example.com

# 显示详细统计
dig +stats example.com

# 多种输出格式
dig +noall +answer +comments example.com # 结果 + 注释
dig +noall +answer +question example.com # 结果 + 问题
```

### 理解 dig 输出

```
;; ANSWER SECTION:
example.com. 3600 IN A 93.184.216.34
 │ │ │ │ │
 │ │ │ │ └─ 解析结果
 │ │ │ └─ 记录类型
 │ │ └─ 网络类别（Internet）
 │ └─ TTL（该记录可缓存 3600 秒）
 └─ 查询的域名

;; Query time: 23 msec ← 查询耗时
;; SERVER: 8.8.8.8#53(8.8.8.8) ← 使用的 DNS 服务器
;; WHEN: Mon Jan 01 12:00:00 UTC 2024
;; MSG SIZE rcvd: 56 ← 响应大小
```

### 常用查询示例

```bash
# 检查 DNSSEC
dig +dnssec example.com

# 查询 DNSKEY（DNSSEC 密钥）
dig example.com DNSKEY

# 测试 DNS 服务器响应时间
dig @1.1.1.1 google.com | grep "Query time"
dig @8.8.8.8 google.com | grep "Query time"
dig @9.9.9.9 google.com | grep "Query time"

# 批量查询
for domain in google.com github.com archlinux.org; do
 echo "$domain: $(dig +short $domain)"
done

# CAA 记录（证书颁发授权）
dig example.com CAA
```

---

## 23.5 nslookup 与 host

### nslookup（交互式）

```bash
# 基本查询
nslookup example.com
nslookup example.com 8.8.8.8 # 指定服务器

# 交互模式
nslookup
> server 8.8.8.8 # 切换 DNS 服务器
> set type=MX # 设置查询类型
> example.com
> set type=A
> www.example.com
> set type=PTR
> 8.8.8.8
> exit
```

### host（简洁）

```bash
host example.com # A 和 AAAA
host -t MX example.com # 指定类型
host -t TXT example.com
host 8.8.8.8 # 自动反向解析
host -v example.com # 详细输出
```

---

## 23.6 DNS over HTTPS (DoH) 与 DNS over TLS (DoT)

### 为什么需要加密 DNS

传统 DNS 查询使用 UDP 53 端口明文传输，存在被监听、篡改的风险。DoH（DNS over HTTPS）和 DoT（DNS over TLS）提供了加密的 DNS 传输。

| 特性 | 传统 DNS (UDP) | DNS over TLS (DoT) | DNS over HTTPS (DoH) |
|------|---------------|-------------------|---------------------|
| 端口 | 53 | 853 | 443 |
| 加密 | 无 | TLS | HTTPS (TLS) |
| 协议 | DNS wire format | DNS wire format | HTTP/2 + JSON/DNS |
| 可识别性 | 容易识别 | 可识别（端口） | 混入 HTTPS 流量 |
| 防火墙友好 | 是 | 需开放 853 | 是（与 HTTPS 共享 443） |

### 公共加密 DNS 服务器

| 提供商 | DoT 地址 | DoH URL |
|--------|---------|---------|
| Cloudflare | `1.1.1.1` `1.0.0.1` | `https://cloudflare-dns.com/dns-query` |
| Google | `dns.google` | `https://dns.google/dns-query` |
| Quad9 | `dns.quad9.net` | `https://dns.quad9.net/dns-query` |
| AdGuard | `dns.adguard-dns.com` | `https://dns.adguard-dns.com/dns-query` |
| Mullvad | `dns.mullvad.net` | `https://dns.mullvad.net/dns-query` |

### systemd-resolved 配置 DoT

```ini
# /etc/systemd/resolved.conf
[Resolve]
DNS=1.1.1.1#cloudflare-dns.com 8.8.8.8#dns.google 9.9.9.9#dns.quad9.net
DNSOverTLS=yes
DNSSEC=allow-downgrade
```

```bash
sudo systemctl restart systemd-resolved

# 验证
resolvectl status | grep "DNS over TLS"
```

### 使用 dnscrypt-proxy（全功能方案）

```bash
# 安装
# Debian: sudo apt install dnscrypt-proxy
# Fedora: sudo dnf install dnscrypt-proxy
# Arch: sudo pacman -S dnscrypt-proxy

# 编辑 /etc/dnscrypt-proxy/dnscrypt-proxy.toml
# 选择 DoH/DoT 服务器，启用 DNSSEC，配置过滤规则

# 将系统 DNS 指向本地
# resolv.conf 中设置: nameserver 127.0.0.1
```

### 使用 stubby（DoT 纯方案）

```bash
# 安装
sudo apt install stubby # Debian/Ubuntu
sudo dnf install stubby # Fedora

# 配置 /etc/stubby/stubby.yml
# 启动后监听 127.0.0.1:53，上游使用 DoT

sudo systemctl enable --now stubby
```

---

## 23.7 常见 DNS 服务器对比

| DNS 服务器 | IP 地址 | 特点 |
|-----------|---------|------|
| Cloudflare | 1.1.1.1 | 快速、隐私保护（不记录日志） |
| Google | 8.8.8.8 | 高可用、全球 Anycast |
| Quad9 | 9.9.9.9 | 安全过滤（屏蔽恶意域名） |
| OpenDNS | 208.67.222.222 | 内容过滤、家长控制 |
| AdGuard | 94.140.14.14 | 广告和跟踪屏蔽 |
| 阿里云 DNS | 223.5.5.5 | 国内高速、稳定 |
| DNSPod | 119.29.29.29 | 国内、腾讯云 |
| 114DNS | 114.114.114.114 | 国内通用 |

---

## 23.8 DNS 故障排查

### 诊断流程

```bash
# 1. 确认是否可达目标服务器
ping -c 3 8.8.8.8
ping -c 3 google.com # 如果 IP 通但域名不通 → DNS 问题

# 2. 测试 DNS 服务器响应
dig @8.8.8.8 google.com # 指定 DNS 测试
nslookup google.com 1.1.1.1

# 3. 检查 /etc/resolv.conf
cat /etc/resolv.conf
# 确保 nameserver 指向正确的 DNS 服务器

# 4. 查看 DNS 查询过程
dig +trace google.com # 从根追溯
dig +short google.com @127.0.0.1 # 测试本地 DNS 代理

# 5. 检查 systemd-resolved 状态
resolvectl status
sudo systemctl status systemd-resolved

# 6. 查看 DNS 缓存
resolvectl statistics # systemd-resolved
sudo systemd-resolve --flush-caches

# 7. 检查 DNS 端口连通性
nc -zvu 8.8.8.8 53 # UDP 53
nc -z 8.8.8.8 53 # TCP 53（备用传输）
```

### 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| `Temporary failure in name resolution` | DNS 服务器不可达 | 检查网络连接和 resolv.conf |
| 解析很慢 | DNS 服务器响应慢 | 测试不同 DNS 服务器延迟 |
| 返回错误 IP | DNS 污染/劫持 | 使用 DoH/DoT 加密 DNS |
| 不能解析局域网主机名 | 缺少搜索域 | 添加 search 指令 |
| 解析结果不一致 | CDN 调度差异 | 理解 Anycast DNS 机制 |

### 性能测试

```bash
# 批量测试 DNS 响应时间
for dns in 1.1.1.1 8.8.8.8 9.9.9.9 114.114.114.114; do
 echo -n "$dns: "
 dig +time=2 +tries=1 @$dns google.com | grep "Query time" | awk '{print $4 " " $5}'
done

# 使用专门的 DNS 测速工具
# dnsperf, named 或 dnseval
```

---

## 23.9 DNS 缓存

### 本地 DNS 缓存机制

| 方案 | 说明 | 缓存位置 |
|------|------|---------|
| nscd | 传统 Name Service Cache Daemon | 内存 |
| systemd-resolved | 现代 systemd 方案 | 内存 |
| dnsmasq | 轻量 DNS 转发器+缓存 | 内存 |
| unbound | 递归解析器+缓存 | 内存 |
| nss-myhostname | systemd 内置本地主机名 | 直接/内存 |
| 浏览器自身 | 浏览器内置 DNS 缓存 | 浏览器内存 |

```bash
# systemd-resolved 缓存统计
resolvectl statistics
resolvectl flush-caches # 清空缓存

# dnsmasq 缓存
sudo systemctl restart dnsmasq # 清空缓存

# nscd 缓存
sudo systemctl restart nscd # 清空 nscd 缓存
```

---

## 23.10 相关章节

- [[11-网络配置基础]] — 网络接口、IP、路由基础
- [[57-DNS服务器搭建]] — 自建 DNS 服务器（BIND、Unbound、dnsmasq）
- [[22-防火墙与安全]] — DNS 端口访问控制

---

> **小结**：DNS 是互联网基础设施的核心。日常运维中，掌握 `dig` 诊断工具、理解 resolv.conf 配置机制、以及评价不同 DNS 服务器的优劣是基本能力。在生产环境中，推荐启用 DNS 加密（DoT/DoH）保护隐私，使用本地 DNS 缓存提升性能，并在排查网络故障时将 DNS 作为首要检查点。
