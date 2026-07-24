# 21 - 网络配置详解（iwctl 与替代方案）

> 网络是现代 Linux 系统的命脉。本章将从 Linux 网络栈基础讲起，深入讲解 iwd/iwctl 无线网络管理，
> 并全面覆盖 NetworkManager、systemd-networkd、wpa_supplicant 等替代方案，以及有线网络、DNS、
> 防火墙、VPN 等关键主题。Arch Linux 给予用户最大的网络配置自由——也意味着你需要真正理解它。

---

## 21.1 Linux 网络栈基础

### 网络接口

Linux 将所有网络设备抽象为**网络接口**。常见接口命名：

| 前缀 | 含义 | 示例 |
|------|------|------|
| `lo` | 回环接口 | `lo` |
| `eth` | 传统以太网 | `eth0` |
| `en` | Predictable 以太网 | `enp3s0`、`eno1` |
| `wl` | 无线接口 | `wlan0`、`wlp2s0` |
| `ww` | WWAN（移动网络） | `wwan0` |

查看所有网络接口：

```bash
ip link show
```

### IP 地址

```bash
# 查看所有接口的 IP 地址
ip addr show

# 临时添加 IP
ip addr add 192.168.1.100/24 dev enp3s0

# 删除 IP
ip addr del 192.168.1.100/24 dev enp3s0
```

### 路由

```bash
# 查看路由表
ip route show

# 添加默认网关
ip route add default via 192.168.1.1 dev enp3s0

# 添加静态路由
ip route add 10.0.0.0/8 via 192.168.1.254
```

### DNS

DNS 配置文件为 `/etc/resolv.conf`：

```
nameserver 8.8.8.8
nameserver 1.1.1.1
search example.com
```

> 在现代 Arch 系统中，`/etc/resolv.conf` 通常由 `systemd-resolved` 或 `NetworkManager` 管理，
> 不建议手动编辑。

---

## 21.2 iwd 架构与安装

### iwd 是什么

**iwd**（iNet Wireless Daemon）是 Intel 开发的现代无线网络守护进程，用于替代 `wpa_supplicant`。
其架构包含：

| 组件 | 功能 |
|------|------|
| `iwd` | 核心守护进程，管理无线连接 |
| `iwctl` | 交互式命令行客户端 |
| `iwmon` | 无线监控工具（调试用） |
| `libell` | iwd 依赖的底层库（Embedded Linux Library） |

### 安装与启动

```bash
# 安装
pacman -S iwd

# 启动并设为开机自启
systemctl enable --now iwd.service
```

验证服务状态：

```bash
systemctl status iwd.service
```

---

## 21.3 iwctl 交互式命令详解

进入 iwctl 交互模式：

```bash
iwctl
```

### 基本操作流程

```
# 列出所有无线设备
[iwd]# device list

# 扫描可用网络（以 wlan0 为例）
[iwd]# station wlan0 scan

# 显示扫描结果
[iwd]# station wlan0 get-networks

# 连接到网络（会提示输入密码）
[iwd]# station wlan0 connect "MyWiFi"

# 查看连接状态
[iwd]# station wlan0 show

# 断开连接
[iwd]# station wlan0 disconnect
```

### 非交互式用法

```bash
# 直接在命令行完成操作
iwctl station wlan0 scan
iwctl station wlan0 get-networks
iwctl --passphrase "my_password" station wlan0 connect "MyWiFi"
```

### 管理已知网络

```
[iwd]# known-networks list
[iwd]# known-networks "MyWiFi" forget
[iwd]# known-networks "MyWiFi" show
```

### 适配器管理

```
[iwd]# adapter list
[iwd]# adapter phy0 show
[iwd]# adapter phy0 set-property Powered on
```

### WPS 连接

```
[iwd]# wsc list
[iwd]# wsc wlan0 push-button
[iwd]# wsc wlan0 start-pin 12345678
```

---

## 21.4 WPA2/WPA3 Enterprise 连接

企业级 Wi-Fi（如 eduroam）需要手动创建配置文件。

在 `/var/lib/iwd/` 下创建 `eduroam.8021x` 文件：

```ini
[Security]
EAP-Method=PEAP
EAP-Identity=anonymous@example.edu
EAP-PEAP-CACert=/etc/ssl/certs/ca-certificates.crt
EAP-PEAP-ServerDomainMask=*.example.edu
EAP-PEAP-Phase2-Method=MSCHAPV2
EAP-PEAP-Phase2-Identity=user@example.edu
EAP-PEAP-Phase2-Password=your_password

[Settings]
AutoConnect=true
```

支持的 EAP 方法：

| 方法 | 说明 |
|------|------|
| `PEAP` | 最常见的企业认证 |
| `TTLS` | 隧道 TLS |
| `TLS` | 证书认证 |
| `PWD` | 密码认证 |

EAP-TLS 示例（证书认证）：

```ini
[Security]
EAP-Method=TLS
EAP-Identity=user@example.com
EAP-TLS-CACert=/etc/ssl/certs/ca.pem
EAP-TLS-ClientCert=/etc/ssl/certs/client.pem
EAP-TLS-ClientKey=/etc/ssl/private/client.key

[Settings]
AutoConnect=true
```

---

## 21.5 iwd 配置文件详解

### 全局配置

主配置文件位于 `/etc/iwd/main.conf`：

```ini
[General]
EnableNetworkConfiguration=true
AddressRandomization=once
AddressRandomizationRange=full

[Network]
EnableIPv6=true
NameResolvingService=systemd
RoutePriorityOffset=300

[Scan]
DisablePeriodicScan=false
InitialPeriodicScanInterval=1
MaximumPeriodicScanInterval=300

[Blacklist]
InitialTimeout=60
Multiplier=30
MaximumTimeout=86400
```

### 网络配置文件

已连接网络的凭据保存在 `/var/lib/iwd/` 目录：

| 文件扩展名 | 网络类型 |
|-----------|---------|
| `.open` | 开放网络 |
| `.psk` | WPA/WPA2 Personal |
| `.8021x` | WPA Enterprise |

PSK 网络配置示例（`/var/lib/iwd/MyWiFi.psk`）：

```ini
[Security]
PreSharedKey=abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890
Passphrase=my_password

[Settings]
AutoConnect=true
Hidden=false
```

---

## 21.6 iwd 作为独立网络管理器

iwd 可以独立运行，无需 NetworkManager 或 dhcpcd。

在 `/etc/iwd/main.conf` 中启用内置 DHCP 和 DNS：

```ini
[General]
EnableNetworkConfiguration=true

[Network]
NameResolvingService=systemd
```

配合 `systemd-resolved` 处理 DNS：

```bash
systemctl enable --now systemd-resolved.service
ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf
```

如果不想使用 `systemd-resolved`，可改用 `resolvconf`：

```ini
[Network]
NameResolvingService=resolvconf
```

### 静态 IP 配置

在网络配置文件中添加 `[IPv4]` 段：

```ini
[IPv4]
Address=192.168.1.100
Netmask=255.255.255.0
Gateway=192.168.1.1
Broadcast=192.168.1.255
DNS=8.8.8.8
```

---

## 21.7 iwd 常见问题排查

### 查看日志

```bash
journalctl -u iwd.service -b
```

### 使用 iwmon 进行无线诊断

```bash
# 启用监控模式
iwmon
```

### 常见问题

| 问题 | 解决方案 |
|------|---------|
| 找不到无线设备 | 检查驱动是否加载：`lspci -k`、`dmesg \| grep wifi` |
| 扫描无结果 | 确认射频未被禁用：`rfkill list`、`rfkill unblock wifi` |
| 连接后无 IP | 启用 `EnableNetworkConfiguration=true` 或安装 dhcpcd |
| DNS 无法解析 | 检查 `/etc/resolv.conf` 是否正确配置 |
| WPA3 连接失败 | 确认内核和驱动支持 SAE |
| 频繁断连 | 检查电源管理：`iw dev wlan0 set power_save off` |

---

## 21.8 替代方案：NetworkManager

NetworkManager 是最流行的全功能网络管理器，适合桌面用户。

### 安装

```bash
pacman -S networkmanager
systemctl enable --now NetworkManager.service
```

> 注意：NetworkManager 与 iwd 不能同时管理同一接口。如果要让 NetworkManager 使用 iwd 作为后端：

```bash
# /etc/NetworkManager/conf.d/wifi_backend.conf
[device]
wifi.backend=iwd
```

### nmcli 命令行工具

```bash
# 查看所有连接
nmcli connection show

# 查看设备状态
nmcli device status

# 扫描并连接 Wi-Fi
nmcli device wifi list
nmcli device wifi connect "MyWiFi" password "my_password"

# 创建静态 IP 连接
nmcli connection add type ethernet con-name "static-eth" ifname enp3s0 \
  ipv4.method manual ipv4.addresses 192.168.1.100/24 \
  ipv4.gateway 192.168.1.1 ipv4.dns "8.8.8.8 1.1.1.1"

# 启用/禁用连接
nmcli connection up "static-eth"
nmcli connection down "static-eth"

# 修改已有连接
nmcli connection modify "MyWiFi" ipv4.dns "8.8.8.8"

# 删除连接
nmcli connection delete "MyWiFi"
```

### nmtui 文本界面

```bash
nmtui
```

提供直观的 TUI 界面，适合不熟悉 nmcli 的用户。

---

## 21.9 替代方案：systemd-networkd + systemd-resolved

纯 systemd 方案，轻量且无额外依赖。

### 启用服务

```bash
systemctl enable --now systemd-networkd.service
systemctl enable --now systemd-resolved.service
ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf
```

### 有线 DHCP 配置

创建 `/etc/systemd/network/20-wired.network`：

```ini
[Match]
Name=enp3s0

[Network]
DHCP=yes
DNS=8.8.8.8
DNS=1.1.1.1

[DHCPv4]
RouteMetric=100
```

### 无线网络

systemd-networkd 本身不管理无线连接，需要配合 `iwd` 或 `wpa_supplicant`。

配合 iwd 的 networkd 配置示例（`/etc/systemd/network/25-wireless.network`）：

```ini
[Match]
Name=wlan0

[Network]
DHCP=yes

[DHCPv4]
RouteMetric=600
```

### 静态 IP 配置

```ini
[Match]
Name=enp3s0

[Network]
Address=192.168.1.100/24
Gateway=192.168.1.1
DNS=8.8.8.8
DNS=1.1.1.1
```

---

## 21.10 替代方案：wpa_supplicant + dhcpcd

传统方案，最灵活但配置最繁琐。

### 安装

```bash
pacman -S wpa_supplicant dhcpcd
```

### 配置 wpa_supplicant

```bash
# 生成配置文件
wpa_passphrase "MyWiFi" "my_password" > /etc/wpa_supplicant/wpa_supplicant-wlan0.conf
```

配置文件内容：

```
ctrl_interface=/run/wpa_supplicant
update_config=1
country=CN

network={
    ssid="MyWiFi"
    psk=abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890
    key_mgmt=WPA-PSK
    priority=1
}
```

### 启动

```bash
systemctl enable --now wpa_supplicant@wlan0.service
systemctl enable --now dhcpcd@wlan0.service
```

### wpa_cli 交互式操作

```bash
wpa_cli -i wlan0
> scan
> scan_results
> add_network
> set_network 0 ssid "MyWiFi"
> set_network 0 psk "my_password"
> enable_network 0
> save_config
> quit
```

---

## 21.11 替代方案：ConnMan 与 netctl

### ConnMan

Intel 开发的轻量网络管理器：

```bash
pacman -S connman
systemctl enable --now connman.service

# 使用 connmanctl
connmanctl technologies
connmanctl enable wifi
connmanctl scan wifi
connmanctl services
connmanctl connect wifi_xxxx_managed_psk
```

### netctl（Arch 传统方案）

```bash
pacman -S netctl

# 复制模板
cp /etc/netctl/examples/ethernet-dhcp /etc/netctl/my-ethernet
cp /etc/netctl/examples/wireless-wpa /etc/netctl/my-wifi
```

编辑 `/etc/netctl/my-wifi`：

```bash
Description='My WiFi'
Interface=wlan0
Connection=wireless
Security=wpa
ESSID='MyWiFi'
Key='my_password'
IP=dhcp
```

```bash
# 启动
netctl start my-wifi

# 设为开机自启
netctl enable my-wifi

# 自动切换（需要 wpa_actiond）
systemctl enable netctl-auto@wlan0.service
```

> netctl 现已不太活跃，新安装推荐使用 iwd 或 NetworkManager。

---

## 21.12 有线网络配置

### 使用 systemd-networkd

```ini
# /etc/systemd/network/20-wired.network
[Match]
Name=enp3s0

[Network]
DHCP=yes
```

### 使用 dhcpcd

```bash
pacman -S dhcpcd
systemctl enable --now dhcpcd@enp3s0.service
```

### 手动配置（临时）

```bash
ip link set enp3s0 up
ip addr add 192.168.1.100/24 dev enp3s0
ip route add default via 192.168.1.1
echo "nameserver 8.8.8.8" > /etc/resolv.conf
```

---

## 21.13 静态 IP vs DHCP

| 特性 | DHCP | 静态 IP |
|------|------|---------|
| 配置难度 | 自动获取 | 需手动指定 |
| 适用场景 | 普通客户端 | 服务器、固定设备 |
| IP 冲突 | DHCP 服务器管理 | 需自行避免 |
| 灵活性 | IP 可能变化 | 固定不变 |

### dhcpcd 静态 IP

编辑 `/etc/dhcpcd.conf`：

```
interface enp3s0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=8.8.8.8 1.1.1.1
```

---

## 21.14 DNS 配置

### systemd-resolved

```bash
systemctl enable --now systemd-resolved.service
ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf
```

配置 `/etc/systemd/resolved.conf`：

```ini
[Resolve]
DNS=8.8.8.8#dns.google 1.1.1.1#cloudflare-dns.com
FallbackDNS=9.9.9.9 149.112.112.112
DNSSEC=allow-downgrade
DNSOverTLS=opportunistic
Domains=~.
Cache=yes
```

查看状态：

```bash
resolvectl status
resolvectl query archlinux.org
```

### 手动管理 /etc/resolv.conf

如果不使用任何 DNS 管理器：

```bash
# 防止被覆盖
chattr +i /etc/resolv.conf
```

---

## 21.15 网桥、VLAN 与 Bonding

### 网桥（Bridge）

使用 systemd-networkd 创建网桥：

```ini
# /etc/systemd/network/10-bridge.netdev
[NetDev]
Name=br0
Kind=bridge
```

```ini
# /etc/systemd/network/11-bind-to-bridge.network
[Match]
Name=enp3s0

[Network]
Bridge=br0
```

```ini
# /etc/systemd/network/12-bridge-dhcp.network
[Match]
Name=br0

[Network]
DHCP=yes
```

### VLAN

```ini
# /etc/systemd/network/10-vlan100.netdev
[NetDev]
Name=vlan100
Kind=vlan

[VLAN]
Id=100
```

```ini
# /etc/systemd/network/11-enp3s0.network
[Match]
Name=enp3s0

[Network]
VLAN=vlan100
```

使用 `ip` 命令临时创建：

```bash
ip link add link enp3s0 name vlan100 type vlan id 100
ip addr add 10.0.100.1/24 dev vlan100
ip link set vlan100 up
```

### Bonding（链路聚合）

```ini
# /etc/systemd/network/10-bond0.netdev
[NetDev]
Name=bond0
Kind=bond

[Bond]
Mode=802.3ad
TransmitHashPolicy=layer3+4
MIIMonitorSec=1s
LACPTransmitRate=fast
```

```ini
# /etc/systemd/network/11-bond0-slave.network
[Match]
Name=enp3s0 enp4s0

[Network]
Bond=bond0
```

---

## 21.16 防火墙

### nftables（推荐）

```bash
pacman -S nftables
systemctl enable --now nftables.service
```

基本规则文件 `/etc/nftables.conf`：

```nft
#!/usr/sbin/nft -f

flush ruleset

table inet filter {
    chain input {
        type filter hook input priority filter; policy drop;
        ct state established,related accept
        iif "lo" accept
        ct state invalid drop
        icmp type echo-request accept
        tcp dport 22 accept
        tcp dport { 80, 443 } accept
    }

    chain forward {
        type filter hook forward priority filter; policy drop;
    }

    chain output {
        type filter hook output priority filter; policy accept;
    }
}
```

```bash
# 重新加载规则
nft -f /etc/nftables.conf

# 查看当前规则
nft list ruleset
```

### iptables（传统）

```bash
# 基本规则
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A INPUT -i lo -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -j DROP

# 保存规则
iptables-save > /etc/iptables/iptables.rules
systemctl enable --now iptables.service
```

### firewalld

```bash
pacman -S firewalld
systemctl enable --now firewalld.service

firewall-cmd --zone=public --add-service=ssh --permanent
firewall-cmd --zone=public --add-port=8080/tcp --permanent
firewall-cmd --reload
firewall-cmd --list-all
```

---

## 21.17 网络调试工具

| 工具 | 用途 | 安装包 |
|------|------|--------|
| `ip` | 接口/路由/地址管理 | `iproute2`（预装） |
| `ss` | 套接字统计 | `iproute2`（预装） |
| `ping` | ICMP 连通性测试 | `iputils`（预装） |
| `traceroute` | 路由追踪 | `traceroute` |
| `dig` | DNS 查询 | `bind-tools` |
| `nslookup` | DNS 查询 | `bind-tools` |
| `tcpdump` | 抓包分析 | `tcpdump` |
| `nmap` | 端口扫描 | `nmap` |
| `mtr` | 增强版 traceroute | `mtr` |
| `curl` | HTTP 请求测试 | `curl`（预装） |
| `ethtool` | 网卡参数查看 | `ethtool` |

### 常用命令示例

```bash
# 查看监听端口
ss -tlnp

# 查看所有连接
ss -tunap

# DNS 查询
dig archlinux.org
dig @8.8.8.8 archlinux.org +short

# 追踪路由
traceroute -n archlinux.org
mtr archlinux.org

# 抓包
tcpdump -i enp3s0 -n port 80
tcpdump -i any -w capture.pcap

# 测试带宽
pacman -S iperf3
iperf3 -s          # 服务端
iperf3 -c 1.2.3.4  # 客户端
```

---

## 21.18 VPN 配置

### WireGuard

```bash
pacman -S wireguard-tools
```

生成密钥对：

```bash
wg genkey | tee privatekey | wg pubkey > publickey
```

客户端配置 `/etc/wireguard/wg0.conf`：

```ini
[Interface]
PrivateKey = <客户端私钥>
Address = 10.0.0.2/24
DNS = 1.1.1.1

[Peer]
PublicKey = <服务端公钥>
Endpoint = vpn.example.com:51820
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25
```

```bash
# 启动
wg-quick up wg0

# 设为开机自启
systemctl enable --now wg-quick@wg0.service

# 查看状态
wg show
```

使用 systemd-networkd 管理 WireGuard：

```ini
# /etc/systemd/network/50-wg0.netdev
[NetDev]
Name=wg0
Kind=wireguard

[WireGuard]
PrivateKey=<客户端私钥>
ListenPort=51820

[WireGuardPeer]
PublicKey=<服务端公钥>
Endpoint=vpn.example.com:51820
AllowedIPs=0.0.0.0/0
PersistentKeepalive=25
```

```ini
# /etc/systemd/network/51-wg0.network
[Match]
Name=wg0

[Network]
Address=10.0.0.2/24
DNS=1.1.1.1
```

### OpenVPN

```bash
pacman -S openvpn
```

```bash
# 使用配置文件连接
openvpn --config client.ovpn

# 设为服务
cp client.ovpn /etc/openvpn/client/client.conf
systemctl enable --now openvpn-client@client.service
```

---

## 21.19 网络方案选型指南

| 使用场景 | 推荐方案 |
|---------|---------|
| 桌面用户（GNOME/KDE） | NetworkManager |
| 极简安装 / 服务器 | systemd-networkd + iwd |
| 仅需 Wi-Fi（安装时） | iwctl |
| 容器 / 虚拟化宿主 | systemd-networkd + 网桥 |
| 传统服务器 | dhcpcd 或 systemd-networkd |
| 嵌入式 / IoT | ConnMan 或 iwd 独立模式 |

> 关键原则：同一时间只运行一个网络管理器，避免冲突。
> 例如不要同时启用 NetworkManager 和 systemd-networkd。

---

## 21.20 本章测验

> [!example] 📝 自测题目

> [!question]- 选择题 1：iwd 中用于交互式管理无线网络的命令行客户端是？
> - A. iwconfig
> - B. iwctl
> - C. nmcli
> - D. wpa_cli
>
> > [!success]- 点击查看答案
> > **B**
> > iwctl 是 iwd 提供的交互式命令行客户端，用于扫描、连接和管理无线网络。

> [!question]- 选择题 2：iwd 存储已连接网络凭据的目录是？
> - A. /etc/iwd/
> - B. /etc/NetworkManager/
> - C. /var/lib/iwd/
> - D. /run/iwd/
>
> > [!success]- 点击查看答案
> > **C**
> > iwd 将已知网络的配置文件（.open、.psk、.8021x）保存在 /var/lib/iwd/ 目录中。

> [!question]- 选择题 3：如果无线网卡被射频开关禁用了，应该使用什么命令解除？
> - A. ip link set wlan0 up
> - B. rfkill unblock wifi
> - C. iwctl adapter phy0 set-property Powered on
> - D. nmcli radio wifi on
>
> > [!success]- 点击查看答案
> > **B**
> > `rfkill unblock wifi` 用于解除射频硬/软开关的禁用状态。这是排查"扫描无结果"问题的常见步骤。

> [!question]- 判断题 4：NetworkManager 和 iwd 可以同时管理同一个无线接口而不会冲突
> - A. ✓ 正确
> - B. ✗ 错误
>
> > [!success]- 点击查看答案
> > **B. ✗ 错误**
> > 同一时间只能由一个网络管理器管理同一接口。如果要共存，可以配置 NetworkManager 使用 iwd 作为后端（wifi.backend=iwd）。

> [!question]- 选择题 5：在 systemd-networkd 配置中，网络配置文件应放在哪个目录？
> - A. /etc/network/interfaces.d/
> - B. /etc/systemd/network/
> - C. /etc/NetworkManager/conf.d/
> - D. /var/lib/systemd/network/
>
> > [!success]- 点击查看答案
> > **B**
> > systemd-networkd 的 .network、.netdev、.link 配置文件放在 /etc/systemd/network/ 目录中。

> [!question]- 选择题 6：nftables 规则文件的默认路径是？
> - A. /etc/iptables/rules.v4
> - B. /etc/firewalld/zones/
> - C. /etc/nftables.conf
> - D. /etc/ufw/rules
>
> > [!success]- 点击查看答案
> > **C**
> > nftables 的规则文件默认位于 /etc/nftables.conf，通过 `nft -f /etc/nftables.conf` 加载。

> [!question]- 判断题 7：systemd-networkd 本身可以独立完成无线网络的认证和连接
> - A. ✓ 正确
> - B. ✗ 错误
>
> > [!success]- 点击查看答案
> > **B. ✗ 错误**
> > systemd-networkd 只负责网络配置（IP、路由等），不能管理无线认证。需要配合 iwd 或 wpa_supplicant 来处理无线连接。

> [!question]- 选择题 8：WireGuard VPN 使用哪个命令快速启动连接？
> - A. openvpn --config wg0.conf
> - B. wg-quick up wg0
> - C. systemctl start vpn@wg0
> - D. nmcli vpn connect wg0
>
> > [!success]- 点击查看答案
> > **B**
> > `wg-quick up wg0` 是启动 WireGuard VPN 连接的快捷命令，它会读取 /etc/wireguard/wg0.conf 配置文件。

> [!question]- 选择题 9：查看系统当前监听的 TCP 端口应使用什么命令？
> - A. netstat -a
> - B. ss -tlnp
> - C. ip route show
> - D. dig localhost
>
> > [!success]- 点击查看答案
> > **B**
> > `ss -tlnp` 显示所有监听中的 TCP 端口（-t TCP、-l 监听、-n 数字显示、-p 显示进程）。ss 是 iproute2 套件中替代 netstat 的现代工具。

> [!question]- 判断题 10：在 iwd 的 main.conf 中设置 EnableNetworkConfiguration=true 后，iwd 可以独立运行无需 dhcpcd 或 NetworkManager
> - A. ✓ 正确
> - B. ✗ 错误
>
> > [!success]- 点击查看答案
> > **A. ✓ 正确**
> > 启用该选项后，iwd 内置的 DHCP 客户端会自动获取 IP 地址，配合 systemd-resolved 处理 DNS，即可独立完成网络管理。
