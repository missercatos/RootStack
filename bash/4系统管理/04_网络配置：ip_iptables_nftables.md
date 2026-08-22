# 网络配置：ip, iptables, nftables | Network Configuration

## 章节概述

> **核心理念**：网络是 Linux 系统的命脉——从配置 IP 地址、管理路由表，到设置防火墙规则，每一层都关系到系统的连通性和安全性。掌握这些工具就像理解 C 语言的网络编程一样重要。

---

### 第1节：ip 命令详解

#### 1.1 ip addr 网络地址管理

```bash
# 查看所有网络接口
ip addr
ip a

# 查看特定接口
ip addr show eth0

# 添加 IP 地址
sudo ip addr add 192.168.1.100/24 dev eth0

# 删除 IP 地址
sudo ip addr del 192.168.1.100/24 dev eth0

# 禁用接口
sudo ip link set eth0 down

# 启用接口
sudo ip link set eth0 up

# 设置 MTU
sudo ip link set eth0 mtu 1500
```

#### 1.2 ip route 路由管理

```bash
# 查看路由表
ip route
ip r

# 添加默认路由
sudo ip route add default via 192.168.1.1

# 添加静态路由
sudo ip route add 10.0.0.0/8 via 192.168.1.254

# 删除路由
sudo ip route del 10.0.0.0/8

# 查看特定路由
ip route get 8.8.8.8
```

#### 1.3 ip link 链路管理

```bash
# 查看所有网络接口
ip link show

# 启用/禁用接口
sudo ip link set eth0 up
sudo ip link set eth0 down

# 设置接口名称
sudo ip link set eth0 name wan0

# 设置 ARP 选项
sudo ip link set eth0 arp off

# 查看接口统计
ip -s link show eth0
```

### 第2节：ss/netstat

#### 2.1 ss 命令（推荐）

```bash
# 查看所有监听端口
ss -tlnp

# 查看所有 TCP 连接
ss -tan

# 查看 UDP 连接
ss -ulnp

# 查看特定端口
ss -tlnp | grep :80

# 查看连接状态统计
ss -s

# 查看 UNIX 域套接字
ss -xlp
```

| 选项 | 说明 |
|------|------|
| `-t` | TCP 协议 |
| `-u` | UDP 协议 |
| `-l` | 仅监听 |
| `-n` | 不解析服务名 |
| `-p` | 显示进程信息 |
| `-a` | 所有连接 |
| `-s` | 统计信息 |

#### 2.2 netstat 命令（旧版）

```bash
# 查看所有监听端口
netstat -tlnp

# 查看所有连接
netstat -an

# 查看路由表
netstat -r

# 查看网络接口统计
netstat -i

# 查看特定端口
netstat -tlnp | grep :80
```

### 第3节：iptables 基本规则

#### 3.1 表和链的概念

```
iptables 四表五链:

表 (Tables):
├── filter    - 过滤（默认表）
├── nat       - 网络地址转换
├── mangle    - 修改数据包
└── raw       - 跟踪连接

链 (Chains):
├── INPUT     - 入站数据包
├── OUTPUT    - 出站数据包
├── FORWARD   - 转发数据包
├── PREROUTING  - 路由前
└── POSTROUTING - 路由后
```

#### 3.2 iptables 基本操作

```bash
# 查看规则
sudo iptables -L -n -v
sudo iptables -L -n --line-numbers

# 允许 SSH
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# 允许 HTTP/HTTPS
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# 允许已建立的连接
sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# 拒绝所有其他入站
sudo iptables -P INPUT DROP

# 删除规则
sudo iptables -D INPUT 3

# 清空所有规则
sudo iptables -F
```

#### 3.3 iptables 高级规则

```bash
# 限制连接速率
sudo iptables -A INPUT -p tcp --dport 80 -m limit --limit 100/min --limit-burst 200 -j ACCEPT

# 基于 IP 地址过滤
sudo iptables -A INPUT -s 192.168.1.0/24 -j ACCEPT
sudo iptables -A INPUT -s 10.0.0.0/8 -j DROP

# 端口转发
sudo iptables -t nat -A PREROUTING -p tcp --dport 8080 -j REDIRECT --to-port 80

# 记录被拒绝的数据包
sudo iptables -A INPUT -j LOG --log-prefix "IPTables-Dropped: "
```

### 第4节：nftables（iptables 继任者）

#### 4.1 nftables 基本语法

```bash
# 查看规则
sudo nft list ruleset

# 添加表
sudo nft add table inet filter

# 添加链
sudo nft add chain inet filter input { type filter hook input priority 0 \; }

# 添加规则
sudo nft add rule inet filter input tcp dport 22 accept
sudo nft add rule inet filter input tcp dport { 80, 443 } accept
sudo nft add rule inet filter input ct state established,related accept
sudo nft add rule inet filter input drop
```

#### 4.2 nftables 配置文件

```bash
# /etc/nftables.conf
#!/usr/sbin/nft -f

flush ruleset

table inet filter {
    chain input {
        type filter hook input priority 0; policy drop;
        
        # 允许本地
        iif "lo" accept
        
        # 允许已建立的连接
        ct state established,related accept
        
        # 允许 SSH
        tcp dport 22 accept
        
        # 允许 HTTP/HTTPS
        tcp dport { 80, 443 } accept
        
        # 允许 ICMP
        icmp type echo-request accept
        
        # 记录并丢弃其他
        log prefix "nft-drop: " drop
    }
    
    chain forward {
        type filter hook forward priority 0; policy drop;
    }
    
    chain output {
        type filter hook output priority 0; policy accept;
    }
}
```

### 第5节：DNS 配置

#### 5.1 /etc/resolv.conf

```bash
# 查看 DNS 配置
cat /etc/resolv.conf

# 格式:
# nameserver 8.8.8.8
# nameserver 8.8.4.4
# search example.com
# domain example.com
```

#### 5.2 DNS 测试工具

```bash
# 查询域名
nslookup example.com
dig example.com
dig example.com +short

# 查询特定记录类型
dig example.com A
dig example.com MX
dig example.com NS

# 反向 DNS 查询
dig -x 8.8.8.8

# 测试 DNS 解析
host example.com

# 查看本地 DNS 缓存
systemd-resolve --statistics
```

### 第6节：网络调试

#### 6.1 连通性测试

```bash
# Ping 测试
ping -c 4 8.8.8.8
ping -c 4 -s 1472 example.com  # MTU 测试

# 路由跟踪
traceroute example.com
tracepath example.com

# DNS 解析测试
dig +trace example.com

# 端口测试
nc -zv example.com 80
nc -zv example.com 443
```

#### 6.2 网络性能测试

```bash
# 带宽测试
iperf3 -c server_ip
iperf3 -s  # 服务端模式

# 延迟测试
ping -c 100 example.com | tail -1

# 下载速度测试
curl -o /dev/null -w "Speed: %{speed_download} bytes/sec\n" https://example.com/file.tar.gz

# 网络抓包
sudo tcpdump -i eth0 port 80
sudo tcpdump -i eth0 host 192.168.1.100
sudo tcpdump -i eth0 -w capture.pcap
```

#### 6.3 网络配置持久化

```bash
# Ubuntu/Debian: /etc/network/interfaces
auto eth0
iface eth0 inet static
    address 192.168.1.100
    netmask 255.255.255.0
    gateway 192.168.1.1
    dns-nameservers 8.8.8.8 8.8.4.4

# CentOS/RHEL: /etc/sysconfig/network-scripts/ifcfg-eth0
DEVICE=eth0
BOOTPROTO=static
IPADDR=192.168.1.100
NETMASK=255.255.255.0
GATEWAY=192.168.1.1
DNS1=8.8.8.8
DNS2=8.8.4.4
ONBOOT=yes
```
