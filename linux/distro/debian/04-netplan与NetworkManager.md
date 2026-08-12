# netplan 与 NetworkManager 网络配置

> Debian/Ubuntu 系统的网络配置从传统的 ifupdown 演进到 netplan（Ubuntu）和 NetworkManager/systemd-networkd。本章是完整网络配置指南，覆盖 netplan YAML 配置、NetworkManager 命令行、systemd-networkd 和高级网络功能。

---

## 1. 资源链接

| 资源 | 链接 |
|------|------|
| Netplan 官方文档 | https://netplan.readthedocs.io/ |
| NetworkManager 文档 | https://networkmanager.dev/docs/ |
| Debian 官方下载 | https://www.debian.org/download |
| 清华镜像 | https://mirrors.tuna.tsinghua.edu.cn/debian/ |
| Ubuntu 官方下载 | https://ubuntu.com/download |

---

## 2. 网络配置栈对比

| 配置方式 | 发行版默认 | 特点 | 适用场景 |
|----------|-----------|------|---------|
| `/etc/network/interfaces` | Debian 9-11 | 传统 ifupdown | 服务器、嵌入式 |
| netplan | Ubuntu 17.10+ | 声明式 YAML | 桌面、服务器 |
| NetworkManager | 多数桌面版 | D-Bus 驱动，GUI/CLI/TUI | 桌面、笔记本 |
| systemd-networkd | CoreOS, 容器 | systemd 原生 | 容器、服务器 |

### 2.1 它们的关系

```
netplan（声明式配置层）
 ├── 后端渲染器：NetworkManager
 └── 后端渲染器：systemd-networkd

NetworkManager（连接管理器）
 ├── nmcli（命令行）
 ├── nmtui（终端界面）
 └── nm-connection-editor（GUI）

systemd-networkd（系统网络守护进程）
 └── /etc/systemd/network/*.network 配置

ifupdown（传统，已逐步淘汰）
 └── /etc/network/interfaces
```

---

## 3. netplan 完整配置（Ubuntu 默认）

### 3.1 基本配置

```bash
# 配置文件位置
ls /etc/netplan/

# 命名规范：数字越小优先级越高
# 00-installer-config.yaml
# 01-network-manager-all.yaml
```

### 3.2 静态 IP 配置

```yaml
# /etc/netplan/01-static.yaml
network:
 version: 2
 renderer: networkd # 或 NetworkManager
 ethernets:
 eth0:
 dhcp4: no
 addresses:
 - 192.168.1.100/24
 routes:
 - to: default
 via: 192.168.1.1
 nameservers:
 addresses:
 - 8.8.8.8
 - 1.1.1.1
 search:
 - example.com
```

### 3.3 DHCP 配置

```yaml
# /etc/netplan/01-dhcp.yaml
network:
 version: 2
 renderer: networkd
 ethernets:
 eth0:
 dhcp4: true
 dhcp4-overrides:
 use-dns: false # 不覆盖 DNS（手动指定 DNS）
 use-routes: true
 dhcp6: false # 禁用 IPv6 DHCP
```

### 3.4 多网卡配置

```yaml
# /etc/netplan/02-multi-nic.yaml
network:
 version: 2
 renderer: networkd
 ethernets:
 eth0: # 管理网络
 dhcp4: true
 eth1: # 存储网络（静态）
 dhcp4: no
 addresses:
 - 10.0.0.10/24
 routes:
 - to: 10.0.0.0/24
 via: 10.0.0.1
 eth2: # 心跳网络（无网关）
 dhcp4: no
 addresses:
 - 192.168.99.10/24
```

### 3.5 Bonding（链路聚合）

```yaml
# /etc/netplan/03-bond.yaml
network:
 version: 2
 renderer: networkd
 ethernets:
 eth0:
 dhcp4: no
 eth1:
 dhcp4: no
 bonds:
 bond0:
 dhcp4: no
 addresses:
 - 192.168.1.100/24
 routes:
 - to: default
 via: 192.168.1.1
 nameservers:
 addresses: [8.8.8.8, 1.1.1.1]
 interfaces:
 - eth0
 - eth1
 parameters:
 mode: 802.3ad # LACP 模式
 transmit-hash-policy: layer3+4
 mii-monitor-interval: 100
 lacp-rate: fast
 # 其他常见模式：
 # mode: active-backup # 主备
 # mode: balance-rr # 轮询
 # mode: balance-xor # XOR 负载均衡
```

### 3.6 Bridging（网桥）

```yaml
# /etc/netplan/04-bridge.yaml — KVM/容器用网桥
network:
 version: 2
 renderer: networkd
 ethernets:
 eth0:
 dhcp4: no
 bridges:
 br0:
 dhcp4: true
 interfaces:
 - eth0
 parameters:
 stp: true
 forward-delay: 4
```

### 3.7 VLAN

```yaml
# /etc/netplan/05-vlan.yaml
network:
 version: 2
 renderer: networkd
 ethernets:
 eth0:
 dhcp4: no
 vlans:
 vlan10: # VLAN ID 10
 id: 10
 link: eth0
 addresses:
 - 192.168.10.10/24
 vlan20: # VLAN ID 20
 id: 20
 link: eth0
 addresses:
 - 192.168.20.10/24
```

### 3.8 WiFi 配置（NetworkManager 后端）

```yaml
# /etc/netplan/06-wifi.yaml
network:
 version: 2
 renderer: NetworkManager
 wifis:
 wlan0:
 dhcp4: true
 access-points:
 "MyWiFi-2.4G":
 password: "my-secret-password"
 "MyWiFi-5G":
 password: "another-password"
 # 企业 WPA2-Enterprise
 # "CorporateWiFi":
 # auth:
 # key-management: eap
 # method: peap
 # identity: "user@company.com"
 # password: "corp-password"
```

### 3.9 netplan 管理命令

```bash
# 应用配置（使其生效）
sudo netplan apply

# 测试配置（不实际应用，有问题会回滚）
sudo netplan try

# 生成底层配置文件（不应用）
sudo netplan generate

# 查看当前配置
netplan status

# 查看所有网络接口
netplan status --all

# 调试
sudo netplan --debug apply
sudo netplan --debug generate
```

---

## 4. NetworkManager 完整命令参考

### 4.1 nmcli 常规操作

```bash
# 查看整体网络状态
nmcli general status
nmcli -t general hostname # 查看主机名

# 设置主机名
sudo nmcli general hostname new-hostname

# 查看无线电状态（WiFi/WWAN）
nmcli radio
nmcli radio wifi on # 开启 WiFi
nmcli radio wifi off # 关闭 WiFi
```

### 4.2 连接管理

```bash
# 列出所有连接配置
nmcli connection show

# 显示连接详情
nmcli connection show "Wired connection 1"

# 查看活动连接
nmcli connection show --active

# 启用连接
nmcli connection up "connection-name"

# 停用连接
nmcli connection down "connection-name"

# 删除连接
nmcli connection delete "connection-name"

# 重新加载连接
nmcli connection reload
```

### 4.3 设备管理

```bash
# 列出设备
nmcli device status
nmcli device show

# 查看特定设备
nmcli device show eth0

# 连接设备到已知连接
nmcli device connect eth0

# 断开设备
nmcli device disconnect eth0

# WiFi 扫描
nmcli device wifi list
nmcli device wifi rescan # 重新扫描
```

### 4.4 创建连接

```bash
# 创建 DHCP 以太网连接
nmcli connection add \
 type ethernet \
 con-name "office-lan" \
 ifname eth0 \
 autoconnect yes

# 创建静态 IP 连接
nmcli connection add \
 type ethernet \
 con-name "static-home" \
 ifname eth0 \
 ipv4.method manual \
 ipv4.addresses "192.168.1.100/24" \
 ipv4.gateway "192.168.1.1" \
 ipv4.dns "8.8.8.8 1.1.1.1" \
 autoconnect yes

# 创建 WiFi 连接
nmcli connection add \
 type wifi \
 con-name "home-wifi" \
 ifname wlan0 \
 ssid "MyWiFi" \
 wifi-sec.key-mgmt wpa-psk \
 wifi-sec.psk "my-secret-password" \
 autoconnect yes

# 修改已有连接的属性
nmcli connection modify "office-lan" \
 ipv4.method manual \
 ipv4.addresses "192.168.2.100/24" \
 ipv4.gateway "192.168.2.1"
```

### 4.5 Bond 连接

```bash
# 创建 Bond 连接（主备模式）
nmcli connection add \
 type bond \
 con-name "bond0" \
 ifname bond0 \
 bond.options "mode=active-backup,miimon=100" \
 ipv4.method manual \
 ipv4.addresses "192.168.1.100/24" \
 ipv4.gateway "192.168.1.1"

# 添加 slave 接口
nmcli connection add \
 type ethernet \
 con-name "bond0-port1" \
 ifname eth0 \
 master bond0

nmcli connection add \
 type ethernet \
 con-name "bond0-port2" \
 ifname eth1 \
 master bond0

# Bond 模式：
# active-backup — 主备故障转移
# balance-rr — 轮询（需交换机支持）
# balance-xor — XOR 负载均衡
# 802.3ad — LACP（需交换机支持）
# balance-tlb — 发送负载均衡
# balance-alb — 自适应负载均衡
```

### 4.6 Bridge 连接

```bash
# 创建 Bridge
nmcli connection add \
 type bridge \
 con-name "br0" \
 ifname br0 \
 stp yes \
 ipv4.method manual \
 ipv4.addresses "192.168.1.100/24" \
 ipv4.gateway "192.168.1.1"

# 添加 slave
nmcli connection add \
 type ethernet \
 con-name "br0-port" \
 ifname eth0 \
 master br0

# 启动
nmcli connection up br0
```

### 4.7 VLAN

```bash
# 创建 VLAN 接口
nmcli connection add \
 type vlan \
 con-name "vlan10" \
 dev eth0 \
 id 10 \
 ipv4.method manual \
 ipv4.addresses "192.168.10.10/24"
```

### 4.8 nmtui — 终端图形界面

```bash
# 启动 nmtui
nmtui

# 功能：
# Edit a connection — 编辑连接
# Activate a connection — 激活连接
# Set system hostname — 设置主机名
```

---

## 5. systemd-networkd 配置

### 5.1 启用 systemd-networkd

```bash
# 停止 NetworkManager 及其他网络服务
sudo systemctl stop NetworkManager
sudo systemctl disable NetworkManager

# 启用 systemd-networkd + systemd-resolved
sudo systemctl enable --now systemd-networkd
sudo systemctl enable --now systemd-resolved

# 设置 DNS 符号链接
sudo ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf
```

### 5.2 .network 文件

```bash
# DHCP 配置
# /etc/systemd/network/20-dhcp.network
```

```
[Match]
Name=eth0

[Network]
DHCP=yes
# IPv6 是否自动获取
IPv6AcceptRA=yes

[DHCPv4]
UseDNS=no # 不使用 DHCP 提供的 DNS
```

```bash
# 静态 IP 配置
# /etc/systemd/network/20-static.network
```

```
[Match]
Name=eth0

[Network]
Address=192.168.1.100/24
Gateway=192.168.1.1
DNS=8.8.8.8
DNS=1.1.1.1
Domains=example.com
```

### 5.3 Bond 配置

```bash
# 首先创建虚拟设备
# /etc/systemd/network/30-bond0.netdev
```

```
[NetDev]
Name=bond0
Kind=bond

[Bond]
Mode=802.3ad
MIIMonitorSec=1s
LACPTransmitRate=fast
```

```bash
# /etc/systemd/network/30-bond0.network
```

```
[Match]
Name=bond0

[Network]
Address=192.168.1.100/24
Gateway=192.168.1.1
DNS=8.8.8.8
```

```bash
# Slave 接口
# /etc/systemd/network/30-eth0-slave.network
```

```
[Match]
Name=eth0

[Network]
Bond=bond0
```

### 5.4 Bridge 配置

```bash
# /etc/systemd/network/40-br0.netdev
```

```
[NetDev]
Name=br0
Kind=bridge
```

```bash
# /etc/systemd/network/40-br0.network
```

```
[Match]
Name=br0

[Network]
Address=192.168.1.100/24
Gateway=192.168.1.1
```

```bash
# /etc/systemd/network/40-eth0-bridge.network
```

```
[Match]
Name=eth0

[Network]
Bridge=br0
```

### 5.5 VLAN 配置

```bash
# /etc/systemd/network/50-vlan10.netdev
```

```
[NetDev]
Name=vlan10
Kind=vlan

[VLAN]
Id=10
```

```bash
# /etc/systemd/network/50-vlan10.network
```

```
[Match]
Name=vlan10

[Network]
Address=192.168.10.10/24
```

```bash
# 或直接在 .network 文件中使用 VLAN= 指令
```

```
[Match]
Name=eth0

[Network]
VLAN=vlan10
VLAN=vlan20

[Address]
Address=192.168.10.10/24

[Address]
Address=192.168.20.10/24
```

### 5.6 systemd-networkd 管理命令

```bash
# 查看接口状态
networkctl status

# 查看特定接口
networkctl status eth0

# 列出所有接口
networkctl list

# 重新加载配置
sudo networkctl reload

# 重新配置特定接口
sudo networkctl reconfigure eth0

# 显示 LLDP 邻居（链路发现）
networkctl lldp
```

---

## 6. 传统 ifupdown (/etc/network/interfaces)

```bash
# Debian 9-11 默认使用此方式
# /etc/network/interfaces
```

```
# Loopback
auto lo
iface lo inet loopback

# DHCP
auto eth0
iface eth0 inet dhcp

# 静态 IP
# auto eth0
# iface eth0 inet static
# address 192.168.1.100/24
# gateway 192.168.1.1
# dns-nameservers 8.8.8.8 1.1.1.1

# Bridge（用于 KVM 虚拟机）
# auto br0
# iface br0 inet dhcp
# bridge_ports eth0
# bridge_stp on
# bridge_fd 0
```

```bash
# 管理命令
sudo ifup eth0 # 启用接口
sudo ifdown eth0 # 停用接口
sudo ifup -a # 启用所有 auto 接口
sudo ifdown -a # 停用所有接口
```

---

## 7. 调试与排错

```bash
# 查看所有接口
ip addr show
ip -br addr show

# 查看路由表
ip route show
ip -6 route show

# 查看 ARP 缓存
ip neigh show

# DNS 解析测试
resolvectl status # systemd-resolved
nmcli device show eth0 | grep DNS # NetworkManager
dig google.com
nslookup google.com

# 网络连通性
ping -c 3 8.8.8.8 # 测试 IP 连通性
ping -c 3 google.com # 测试 DNS 是否正常
mtr google.com # 路径追踪

# 端口监听
ss -tlnp
ss -ulnp

# 网络流量
sudo tcpdump -i eth0 -n port 80
sudo tcpdump -i any -w capture.pcap

# 查看带宽使用
sudo iftop -i eth0 # 需要安装 iftop
nethogs eth0 # 需要安装 nethogs

# 查看 NetworkManager 日志
journalctl -u NetworkManager -f

# 查看 systemd-networkd 日志
journalctl -u systemd-networkd -f
```

---

## 8. 相关资源

- Netplan 文档: https://netplan.readthedocs.io/
- Netplan 配置示例: https://netplan.io/examples/
- NetworkManager 参考: `man nmcli-examples`
- systemd-networkd: `man systemd.network`
- Debian 网络配置 Wiki: https://wiki.debian.org/NetworkConfiguration
- [[../debian/01-apt包管理|APT 包管理]]
- [[../debian/02-Debian安装与服务器配置|Debian 安装与服务器配置]]
- [[../redhat/05-firewalld与nmcli|firewalld 与 nmcli（RHEL 版）]]
