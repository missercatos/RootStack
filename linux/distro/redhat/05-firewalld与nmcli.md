# firewalld 与 nmcli 网络管理

> firewalld 是 RHEL/CentOS/Fedora 默认的动态防火墙管理工具，基于 nftables（RHEL 8+）或 iptables（RHEL 7）。nmcli 是 NetworkManager 的命令行界面。本章是两者完整的操作参考手册。

---

## 1. 资源链接

| 资源 | 链接 |
|------|------|
| firewalld 官网 | https://firewalld.org/ |
| firewalld 文档 | https://firewalld.org/documentation/ |
| NetworkManager 文档 | https://networkmanager.dev/ |
| Red Hat 网络指南 | https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9/html/configuring_and_managing_networking/ |
| 清华镜像 | https://mirrors.tuna.tsinghua.edu.cn/centos/ |

---

## 2. firewalld 基础

### 2.1 firewalld vs iptables/nftables

```
                          firewalld
                         /    |    \
                        /     |     \
                  (D-Bus 接口、zone 概念、rich rules)
                      /         |         \
                     /          |          \
              nftables     iptables    ip6tables
           (RHEL 8+/Fed) (RHEL 7/CentOS 7)
```

firewalld 的优势：
- 动态修改规则无需中断连接
- zone 抽象简化网络信任管理
- 支持网络接口变化时自动切换 zone
- D-Bus API 支持编程控制

### 2.2 安装与状态

```bash
# 安装（RHEL/CentOS/Fedora 通常已预装）
sudo dnf install firewalld

# 启动
sudo systemctl enable --now firewalld

# 查看状态
sudo firewall-cmd --state
sudo systemctl status firewalld

# 停止（使用 nftables/iptables 替代）
sudo systemctl stop firewalld
sudo systemctl disable firewalld

# 紧急模式：丢弃所有入站流量
sudo firewall-cmd --panic-on
sudo firewall-cmd --panic-off
sudo firewall-cmd --query-panic
```

### 2.3 Zone（区域）概念

```
Zone 按信任级别从高到低：
trusted  → 信任所有网络连接
home     → 家庭网络（信任局域网其他计算机）
internal → 内部网络（中等信任）
work     → 工作网络（信任但不过度）
public   → 公共网络（默认，不信任其他计算机）★ 默认
external → 外部网络（NAT 伪装，仅允许选定入站）
dmz      → 隔离区（仅允许特定入站服务）
block    → 拒绝所有入站（只回复 ICMP 拒绝）
drop     → 丢弃所有入站（不回复）
```

---

## 3. firewall-cmd 完整命令参考

### 3.1 Zone 管理

```bash
# 查看默认 zone
sudo firewall-cmd --get-default-zone

# 设置默认 zone
sudo firewall-cmd --set-default-zone=home

# 列出所有 zone
sudo firewall-cmd --get-zones

# 查看活动 zone（有网络接口绑定）
sudo firewall-cmd --get-active-zones

# 查看特定 zone 的配置
sudo firewall-cmd --zone=public --list-all
sudo firewall-cmd --list-all            # 默认 zone

# 查看接口属于哪个 zone
sudo firewall-cmd --get-zone-of-interface=eth0

# 将接口绑定到 zone（临时）
sudo firewall-cmd --zone=internal --change-interface=eth0

# 永久绑定（推荐）
sudo firewall-cmd --zone=internal --change-interface=eth0 --permanent
sudo firewall-cmd --reload

# 从 zone 中移除接口
sudo firewall-cmd --zone=internal --remove-interface=eth0 --permanent
```

### 3.2 服务管理

```bash
# 列出所有预定义服务
sudo firewall-cmd --get-services

# 列出 zone 中已启用的服务
sudo firewall-cmd --zone=public --list-services

# 添加服务
sudo firewall-cmd --zone=public --add-service=http --permanent
sudo firewall-cmd --zone=public --add-service=https --permanent

# 删除服务
sudo firewall-cmd --zone=public --remove-service=ssh --permanent

# 查看服务定义
sudo firewall-cmd --info-service=ssh

# 添加多个服务一行完成
sudo firewall-cmd --zone=public --add-service={http,https,ftp} --permanent
```

### 3.3 端口管理

```bash
# 添加端口
sudo firewall-cmd --zone=public --add-port=8080/tcp --permanent
sudo firewall-cmd --zone=public --add-port=5000-5100/tcp --permanent    # 端口范围
sudo firewall-cmd --zone=public --add-port=53/udp --permanent

# 删除端口
sudo firewall-cmd --zone=public --remove-port=8080/tcp --permanent

# 列出 zone 中的端口
sudo firewall-cmd --zone=public --list-ports

# 添加端口+协议组合
sudo firewall-cmd --zone=public --add-port=443/tcp --permanent
```

### 3.4 Rich Rules（富规则）

```bash
# Rich rules 提供比 service/port 更精细的控制

# 语法：
# firewall-cmd --add-rich-rule='rule [family="ipv4|ipv6"] [source address="..."] [destination address="..."]
#     [service|port|protocol|icmp-block|masquerade|forward-port] [log] [audit] [accept|reject|drop]'

# 示例 1：允许特定 IP 访问 SSH
sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="192.168.1.100" service name="ssh" accept'

# 示例 2：允许特定 IP 段访问特定端口
sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="10.0.0.0/8" port port="3306" protocol="tcp" accept'

# 示例 3：限制连接速率（防暴力破解）
sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" service name="ssh" limit value="6/m" accept'

# 示例 4：拒绝特定 IP
sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="1.2.3.4" reject'

# 示例 5：日志记录丢弃的包
sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" port port="22" protocol="tcp" log prefix="SSH-ATTEMPT: " level="warning" limit value="10/m" drop'

# 示例 6：端口转发
sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="192.168.1.0/24" forward-port port="80" protocol="tcp" to-port="8080" to-addr="10.0.0.10"'

# 查看 rich rules
sudo firewall-cmd --zone=public --list-rich-rules

# 删除 rich rule
sudo firewall-cmd --permanent --remove-rich-rule='rule family="ipv4" source address="192.168.1.100" service name="ssh" accept'
```

### 3.5 Direct Rules（直接规则）

```bash
# direct rules 直接操作 nftables/iptables，不经 firewalld 抽象层

# 添加 direct rule
sudo firewall-cmd --permanent --direct --add-rule ipv4 filter INPUT 0 \
    -p tcp --dport 8443 -j ACCEPT

# 查看 direct rules
sudo firewall-cmd --direct --get-all-rules

# 删除 direct rule
sudo firewall-cmd --permanent --direct --remove-rule ipv4 filter INPUT 0 \
    -p tcp --dport 8443 -j ACCEPT
```

### 3.6 NAT 伪装 (Masquerade)

```bash
# 启用 NAT 伪装（将服务器用作路由器）
sudo firewall-cmd --zone=external --add-masquerade --permanent

# 端口转发（将 80 端口转发到内网 192.168.1.10:8080）
sudo firewall-cmd --zone=external --add-forward-port=port=80:proto=tcp:toport=8080:toaddr=192.168.1.10 --permanent

# 端口转发到本机其他端口
sudo firewall-cmd --zone=public --add-forward-port=port=80:proto=tcp:toport=8080 --permanent
```

### 3.7 ICMP 过滤

```bash
# 查看支持的 ICMP 类型
sudo firewall-cmd --get-icmptypes

# 阻止 ICMP echo (ping)
sudo firewall-cmd --zone=public --add-icmp-block=echo-request --permanent

# 允许 ICMP echo
sudo firewall-cmd --zone=public --remove-icmp-block=echo-request --permanent

# 查看 zone 中已阻止的 ICMP 类型
sudo firewall-cmd --zone=public --list-icmp-blocks
```

### 3.8 自定义服务

```bash
# 复制默认服务文件
sudo cp /usr/lib/firewalld/services/ssh.xml /etc/firewalld/services/myservice.xml

# 自定义服务示例
sudo vim /etc/firewalld/services/myservice.xml
```

```xml
<?xml version="1.0" encoding="utf-8"?>
<service>
    <short>My Custom Service</short>
    <description>A custom application that uses ports 9000-9005 TCP</description>
    <port protocol="tcp" port="9000-9005"/>
    <port protocol="udp" port="9000"/>
</service>
```

```bash
# 重新加载使新服务生效
sudo firewall-cmd --reload

# 使用自定义服务
sudo firewall-cmd --permanent --add-service=myservice
```

---

## 4. firewalld 配置持久化

```bash
# 所有 --permanent 的修改需要 reload 才生效
sudo firewall-cmd --reload

# 查看 permanent 配置（未生效的）
sudo firewall-cmd --permanent --list-all

# 对比 runtime 和 permanent
sudo firewall-cmd --list-all            # runtime
sudo firewall-cmd --permanent --list-all # permanent

# 将 runtime 配置保存为 permanent（慎用）
sudo firewall-cmd --runtime-to-permanent

# 配置文件位置
# /etc/firewalld/
#     firewalld.conf          主配置
#     zones/                  自定义 zone
#     services/               自定义服务
#     ipsets/                 IP 集合
#     policies/               策略
#     helpers/                连接助手
# /usr/lib/firewalld/         系统默认配置
```

---

## 5. nmcli 完整命令参考

### 5.1 基础信息

```bash
# 查看整体状态
nmcli general status
nmcli -t -f RUNNING general

# 主机名操作
nmcli general hostname
sudo nmcli general hostname new-hostname

# 查看所有设备
nmcli device status
nmcli device show eth0

# 查看网络接口信息
nmcli -p device show              # 格式化输出

# 无线电管理
nmcli radio all
nmcli radio wifi on
nmcli radio wifi off
```

### 5.2 连接管理

```bash
# 列出所有连接配置
nmcli connection show
nmcli connection show --active

# 查看连接详情
nmcli connection show "eth0"

# 启用连接
sudo nmcli connection up "eth0"

# 停用连接
sudo nmcli connection down "eth0"

# 删除连接
sudo nmcli connection delete "old-eth0"

# 修改连接自动连接属性
sudo nmcli connection modify "eth0" connection.autoconnect yes

# 重新加载连接配置
sudo nmcli connection reload

# 重新激活连接（应用新配置）
sudo nmcli connection up "eth0"
```

### 5.3 创建与修改连接

```bash
# 创建 DHCP 以太网连接
sudo nmcli connection add \
    type ethernet \
    con-name "office" \
    ifname eth0 \
    autoconnect yes

# 创建静态 IP 连接
sudo nmcli connection add \
    type ethernet \
    con-name "static-lan" \
    ifname eth0 \
    ipv4.method manual \
    ipv4.addresses "192.168.1.100/24" \
    ipv4.gateway "192.168.1.1" \
    ipv4.dns "8.8.8.8 1.1.1.1" \
    ipv4.dns-search "example.com" \
    autoconnect yes

# 修改已有连接的 IP
sudo nmcli connection modify "eth0" \
    ipv4.method manual \
    ipv4.addresses "192.168.2.100/24" \
    ipv4.gateway "192.168.2.1" \
    ipv4.dns "8.8.8.8"

# 修改回 DHCP
sudo nmcli connection modify "eth0" ipv4.method auto

# 添加额外 IP 地址
sudo nmcli connection modify "eth0" +ipv4.addresses "192.168.1.200/24"

# 设置 mtu
sudo nmcli connection modify "eth0" ethernet.mtu 9000

# 设置 MAC 地址（克隆）
sudo nmcli connection modify "eth0" ethernet.cloned-mac-address 00:11:22:33:44:55
```

### 5.4 WiFi 连接

```bash
# 扫描
nmcli device wifi list
nmcli device wifi rescan

# 连接
sudo nmcli device wifi connect "SSID" password "password"
# 隐藏 SSID
sudo nmcli device wifi connect "SSID" password "password" hidden yes

# 创建持久 WiFi 连接
sudo nmcli connection add \
    type wifi \
    con-name "home-wifi" \
    ifname wlan0 \
    ssid "MyWiFi" \
    wifi-sec.key-mgmt wpa-psk \
    wifi-sec.psk "password" \
    autoconnect yes

# 查看保存的 WiFi 密码
sudo nmcli connection show "home-wifi" -s | grep psk
```

### 5.5 Bonding

```bash
# 创建 Bond（链路聚合）
sudo nmcli connection add \
    type bond \
    con-name "bond0" \
    ifname bond0 \
    bond.options "mode=802.3ad,miimon=100,lacp_rate=fast" \
    ipv4.method manual \
    ipv4.addresses "192.168.1.100/24" \
    ipv4.gateway "192.168.1.1"

# 添加 slave 接口
sudo nmcli connection add \
    type ethernet \
    con-name "bond0-port1" \
    ifname eth0 \
    master bond0

sudo nmcli connection add \
    type ethernet \
    con-name "bond0-port2" \
    ifname eth1 \
    master bond0

# 启动 Bond
sudo nmcli connection up bond0

# Bond 模式参数：
# mode=active-backup   — 主备
# mode=balance-rr      — 轮询（需交换机支持）
# mode=balance-xor     — XOR 负载均衡
# mode=802.3ad         — LACP（需交换机配置）
# mode=balance-tlb     — 适配器发送负载均衡
# mode=balance-alb     — 自适应负载均衡
```

### 5.6 Bridge

```bash
# 创建 Bridge（KVM/容器用）
sudo nmcli connection add \
    type bridge \
    con-name "br0" \
    ifname br0 \
    stp yes \
    ipv4.method manual \
    ipv4.addresses "192.168.1.100/24" \
    ipv4.gateway "192.168.1.1"

# 添加 slave
sudo nmcli connection add \
    type ethernet \
    con-name "br0-eth0" \
    ifname eth0 \
    master br0

# 启动
sudo nmcli connection up br0
sudo nmcli connection up br0-eth0
```

### 5.7 VLAN

```bash
# 创建 VLAN 接口
sudo nmcli connection add \
    type vlan \
    con-name "vlan10" \
    dev eth0 \
    id 10 \
    ipv4.method manual \
    ipv4.addresses "192.168.10.10/24"

# 查看 VLAN
nmcli connection show | grep vlan

# 删除 VLAN
sudo nmcli connection delete "vlan10"
```

### 5.8 Team（RHEL 7 旧 bonding 替代）

```bash
# teamd 在 RHEL 7 中替代 bonding，RHEL 8+ 推荐 bonding
# 创建 Team
sudo nmcli connection add \
    type team \
    con-name "team0" \
    ifname team0 \
    config '{"runner": {"name": "activebackup"}}' \
    ipv4.method manual \
    ipv4.addresses "192.168.1.100/24"

# 添加 slave
sudo nmcli connection add \
    type ethernet \
    con-name "team0-port1" \
    ifname eth0 \
    master team0
```

### 5.9 nmtui

```bash
# 启动 curses 界面
nmtui

# 直接进入特定菜单
nmtui edit            # 编辑连接
nmtui connect         # 激活连接
nmtui hostname        # 设置主机名
```

---

## 6. 高级网络配置

### 6.1 IP 路由管理

```bash
# 查看路由表
ip route show

# 添加静态路由（临时）
sudo ip route add 10.0.0.0/24 via 192.168.1.254

# 添加默认网关
sudo ip route add default via 192.168.1.1

# nmcli 方式添加静态路由
sudo nmcli connection modify "eth0" \
    +ipv4.routes "10.0.0.0/24 192.168.1.254" \
    +ipv4.routes "172.16.0.0/16 192.168.1.253"
```

### 6.2 DNS 配置

```bash
# nmcli 设置 DNS
sudo nmcli connection modify "eth0" \
    ipv4.dns "8.8.8.8 1.1.1.1" \
    ipv4.dns-search "example.com"
    ipv4.ignore-auto-dns yes     # 忽略 DHCP 提供的 DNS

# 重新应用
sudo nmcli connection up "eth0"

# 查看当前 DNS 配置
cat /etc/resolv.conf
nmcli device show eth0 | grep DNS
```

### 6.3 多宿主机（多默认网关）

```bash
# 为每个连接设置不同的 metric（数字越小优先级越高）
sudo nmcli connection modify "eth0" ipv4.route-metric 100
sudo nmcli connection modify "eth1" ipv4.route-metric 200

# 或使用路由表
sudo nmcli connection modify "eth0" \
    +ipv4.routes "0.0.0.0/0 192.168.1.1 table=100" \
    ipv4.routing-rules "priority 100 from 192.168.1.0/24 table 100"
```

---

## 7. 调试与排错

```bash
# 查看当前防火墙规则
sudo firewall-cmd --list-all-zones
sudo nft list ruleset                  # 查看底层 nftables 规则

# 测试网络连通性
ping -c 4 8.8.8.8
ping -c 4 google.com

# 端口测试
ss -tlnp                              # 监听端口
nc -zv localhost 80                   # 本地端口测试

# 网卡信息
ethtool eth0
ethtool -S eth0                       # 统计信息

# 网络日志
journalctl -u NetworkManager -f
journalctl -u firewalld -f

# dns 诊断
dig +short google.com
resolvectl status

# 抓包
sudo tcpdump -i eth0 -nn port 80
sudo tcpdump -i any -nn host 192.168.1.100

# 防火墙调试
sudo firewall-cmd --get-active-zones
sudo firewall-cmd --zone=public --list-all
```

---

## 8. 常见配置场景

### 8.1 Web 服务器

```bash
sudo firewall-cmd --permanent --add-service={http,https}
sudo firewall-cmd --permanent --add-port=8080/tcp    # 备用端口
sudo firewall-cmd --reload
```

### 8.2 数据库服务器

```bash
# 只允许内网访问
sudo firewall-cmd --permanent --new-zone=dbzone
sudo firewall-cmd --permanent --zone=dbzone --add-source=192.168.0.0/16
sudo firewall-cmd --permanent --zone=dbzone --add-port=3306/tcp    # MySQL
sudo firewall-cmd --permanent --zone=dbzone --add-port=5432/tcp    # PostgreSQL
sudo firewall-cmd --reload
```

### 8.3 路由器/NAT 网关

```bash
# 假设 eth0 是外网，eth1 是内网
sudo firewall-cmd --permanent --zone=external --change-interface=eth0
sudo firewall-cmd --permanent --zone=internal --change-interface=eth1
sudo firewall-cmd --permanent --zone=external --add-masquerade
sudo firewall-cmd --reload

# 启用 IP 转发
echo 'net.ipv4.ip_forward=1' | sudo tee /etc/sysctl.d/99-forwarding.conf
sudo sysctl -p /etc/sysctl.d/99-forwarding.conf
```

### 8.4 Docker 环境（firewalld 共存）

```bash
# Docker 和 firewalld 可能冲突，推荐：
# 方案 1：使用 firewalld + podman（podman 原生支持 firewalld）
# 方案 2：Docker zone 配置
sudo firewall-cmd --permanent --new-zone=docker
sudo firewall-cmd --permanent --zone=docker --add-source=172.17.0.0/16
sudo firewall-cmd --permanent --zone=docker --add-source=172.18.0.0/16
sudo firewall-cmd --reload
```

---

## 9. 相关资源

- firewalld 官方文档: https://firewalld.org/
- firewalld rich language: `man firewalld.richlanguage`
- NetworkManager 参考: `man nmcli`
- nmcli 示例: `man nmcli-examples`
- Red Hat 网络指南: https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9/html/configuring_and_managing_networking/
- [[../redhat/02-RHEL-CentOS安装与配置|RHEL 安装与配置]]
- [[../redhat/04-SELinux深入|SELinux 深入]]
- [[../debian/04-netplan与NetworkManager|netplan 与 NetworkManager]]
