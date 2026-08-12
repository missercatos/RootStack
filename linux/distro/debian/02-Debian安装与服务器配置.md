# Debian 安装与服务器配置

> Debian 是 Linux 世界的基石发行版之一，Ubuntu、Linux Mint、Deepin 等著名发行版都基于它。本章覆盖 Debian/Ubuntu 的安装流程、网络配置和服务器加固，适用于物理机、虚拟机和云环境。

---

## 1. 资源链接

| 资源 | 链接 |
|------|------|
| Debian 官方网站 | https://www.debian.org/ |
| Debian 下载 | https://www.debian.org/download |
| Debian 清华大学镜像 | https://mirrors.tuna.tsinghua.edu.cn/debian/ |
| Debian 中科大镜像 | https://mirrors.ustc.edu.cn/debian/ |
| Debian 阿里云镜像 | https://mirrors.aliyun.com/debian/ |
| Ubuntu 官方网站 | https://ubuntu.com/ |
| Ubuntu 下载 | https://ubuntu.com/download |
| Ubuntu 清华大学镜像 | https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ |
| Ubuntu 中科大镜像 | https://mirrors.ustc.edu.cn/ubuntu/ |

---

## 2. Debian 发行版族谱

### 2.1 版本体系

```
Debian 发行版生命周期（以当前 Bookworm 为例）:

Stable (Bookworm) ← 稳定版，生产环境首选
 ├── Updates ← 重要非安全更新
 ├── Security ← 安全更新
 └── Backports ← 从 Testing 回移植的新软件

Testing (Trixie) ← 下一版 Stable 的候选
Unstable (Sid) ← 滚动更新，始终叫 Sid
Experimental ← 激进软件包测试
```

| 版本 | 适用场景 | 更新频率 |
|------|----------|---------|
| Stable | 生产服务器、对企业 | 每 ~2 年一个大版本，之间仅安全更新 |
| Testing | 桌面用户、开发者 | 持续滚动更新 |
| Unstable (Sid) | 爱好者、包维护者 | 每日多次更新 |
| Experimental | 特定包测试 | 不定期 |

### 2.2 Ubuntu 与 Debian 的关系

```
Debian → 上游基础
 ├── Ubuntu → 基于 Debian Sid，每 6 个月发布
 │ ├── Linux Mint → 基于 Ubuntu
 │ ├── Pop!_OS → 基于 Ubuntu
 │ ├── Elementary → 基于 Ubuntu
 │ ├── KDE Neon → 基于 Ubuntu LTS
 │ └── Deepin → 基于 Debian/Ubuntu 混合
 └── Raspbian/Raspberry Pi OS → 基于 Debian
```

Ubuntu LTS vs 非 LTS:

| 版本类型 | 支持周期 | 推荐场景 |
|----------|----------|---------|
| LTS (如 24.04) | 5 年（Pro 10年） | 服务器、企业 |
| 非 LTS (如 24.10) | 9 个月 | 桌面尝鲜 |

---

## 3. Debian 安装流程

### 3.1 下载镜像

```bash
# Debian 12 (Bookworm) netinstall ISO（推荐，最小化安装后按需下载）
wget https://mirrors.tuna.tsinghua.edu.cn/debian-cd/current/amd64/iso-cd/debian-12.0.0-amd64-netinst.iso

# 完整 DVD ISO（离线安装包更多）
wget https://mirrors.tuna.tsinghua.edu.cn/debian-cd/current/amd64/iso-dvd/debian-12.0.0-amd64-DVD-1.iso

# 校验
sha256sum debian-12.0.0-amd64-netinst.iso
```

### 3.2 安装步骤（服务器模式）

```bash
# 制作启动盘
sudo dd bs=4M if=debian-12.0.0-amd64-netinst.iso of=/dev/sdb conv=fsync oflag=direct status=progress
```

安装过程中的关键选择：

```
1. 语言: English（推荐，便于问题排查）
2. 位置: China → Asia/Shanghai
3. 键盘: American English
4. 网络: 自动 DHCP，主机名如 debian-server
5. 域名: 留空或填写内部域名
6. 镜像: 选择 https → mirrors.tuna.tsinghua.edu.cn → /debian/
7. 分区: 选择 "Guided - use entire disk" 或手动
8. 软件选择:
 SSH server （服务器必须）
 Debian desktop （服务器不装桌面）
 Web server （手动配置更好）
 Standard system utilities
9. GRUB: 安装到 /dev/sda（主硬盘）
```

### 3.3 手动分区（服务器推荐方案）

```
方案 A: ext4 + swap（传统稳健）

/dev/sda1 512M EFI System (ESP) /boot/efi
/dev/sda2 20G ext4 /
/dev/sda3 RAM大小 swap swap
/dev/sda4 剩余 ext4 /var
（/home 可选，视需求）

方案 B: LVM + ext4（灵活扩容）

/dev/sda1 512M EFI System /boot/efi
/dev/sda2 剩余 LVM PV
 ├─ lv_root 20G ext4 /
 ├─ lv_swap RAM swap swap
 ├─ lv_var 剩余 ext4 /var
 └─ lv_home 可选 ext4 /home

方案 C: Btrfs + 子卷（高级，参照 Arch 安装指南中的方案）

/dev/sda1 512M EFI System /boot/efi
/dev/sda2 剩余 Btrfs
 ├─ @ / ext4 或 btrfs
 ├─ @home /home
 ├─ @log /var/log
 └─ @snapshots /.snapshots
```

### 3.4 自动化安装（preseed.cfg）

```bash
# 预设文件用于自动化安装
# 参考: https://wiki.debian.org/DebianInstaller/Preseed

# setup.sh — 生成 preseed 文件
cat > preseed.cfg << 'EOF'
d-i debian-installer/locale string en_US
d-i keyboard-configuration/xkb-keymap select us
d-i netcfg/choose_interface select auto
d-i netcfg/get_hostname string debian-server
d-i netcfg/get_domain string local

d-i mirror/country string manual
d-i mirror/http/hostname string mirrors.tuna.tsinghua.edu.cn
d-i mirror/http/directory string /debian
d-i mirror/http/proxy string

d-i passwd/root-login boolean true
d-i passwd/root-password password changeme
d-i passwd/root-password-again password changeme
d-i passwd/user-fullname string Admin User
d-i passwd/username string admin
d-i passwd/user-password password changeme
d-i passwd/user-password-again password changeme

d-i clock-setup/utc boolean true
d-i time/zone string Asia/Shanghai
d-i clock-setup/ntp boolean true

d-i partman-auto/method string regular
d-i partman-auto/choose_recipe select atomic
d-i partman-partitioning/confirm_write_new_label boolean true
d-i partman/choose_partition select finish
d-i partman/confirm boolean true
d-i partman/confirm_nooverwrite boolean true

d-i base-installer/kernel/image string linux-image-amd64
d-i apt-setup/non-free boolean true
d-i apt-setup/contrib boolean true

tasksel tasksel/first multiselect ssh-server, standard
d-i pkgsel/include string vim git curl htop rsync ufw

d-i grub-installer/only_debian boolean true
d-i grub-installer/with_other_os boolean true
d-i grub-installer/bootdev string /dev/sda

d-i finish-install/reboot_in_progress note
EOF

# 使用 preseed 文件自动化安装（将 preseed.cfg 放到安装介质或网络）
```

---

## 4. 安装后初始配置

### 4.1 网络配置

```bash
# 检查网络接口名
ip -br addr show

# 传统的 /etc/network/interfaces 方式
sudo vim /etc/network/interfaces
```

```
# /etc/network/interfaces （传统 ifupdown 方式）
# 默认 DHCP
auto lo
iface lo inet loopback

auto eth0
iface eth0 inet dhcp

# 静态 IP
# auto eth0
# iface eth0 inet static
# address 192.168.1.100/24
# gateway 192.168.1.1
# dns-nameservers 8.8.8.8 1.1.1.1
```

### 4.2 Netplan 配置（Ubuntu 默认）

详见 [[../debian/04-netplan与NetworkManager|netplan 与 NetworkManager]]。

```bash
# Ubuntu 使用 netplan
sudo vim /etc/netplan/00-installer-config.yaml
```

```yaml
network:
 version: 2
 ethernets:
 eth0:
 dhcp4: true
 # 静态 IP 示例:
 # eth0:
 # addresses:
 # - 192.168.1.100/24
 # routes:
 # - to: default
 # via: 192.168.1.1
 # nameservers:
 # addresses: [8.8.8.8, 1.1.1.1]
```

```bash
sudo netplan apply
```

### 4.3 添加 sudo 权限

```bash
# 安装 sudo（如果未安装）
apt install sudo

# 将用户加入 sudo 组
usermod -aG sudo admin

# 或用 visudo 编辑
visudo
# 取消注释: %sudo ALL=(ALL:ALL) ALL
```

### 4.4 配置中国镜像源

```bash
# 备份原有 sources.list
sudo cp /etc/apt/sources.list /etc/apt/sources.list.bak

# 替换为中国镜像（Debian 12）
sudo tee /etc/apt/sources.list << 'EOF'
deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm main contrib non-free non-free-firmware
deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm-updates main contrib non-free non-free-firmware
deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm-backports main contrib non-free non-free-firmware
deb https://mirrors.tuna.tsinghua.edu.cn/debian-security bookworm-security main contrib non-free non-free-firmware
EOF

sudo apt update
```

### 4.5 基础软件安装

```bash
# 更新系统
sudo apt update && sudo apt full-upgrade -y

# 安装基础工具
sudo apt install -y \
 vim git curl wget \
 htop btop tmux \
 net-tools iproute2 bridge-utils \
 unzip p7zip-full \
 nftables ufw \
 openssh-server fail2ban \
 man-db manpages \
 build-essential \
 rsync

# 可选：安装 firewalld（替代 ufw）
# sudo apt install -y firewalld
```

---

## 5. 服务器安全加固

### 5.1 SSH 安全

```bash
# 备份原始配置
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak

# 编辑 SSH 配置
sudo vim /etc/ssh/sshd_config
```

```
# 推荐的 SSH 安全配置
Port 2222 # 更改默认端口
PermitRootLogin no # 禁止 root SSH 登录
PasswordAuthentication no # 禁用密码登录（只用密钥）
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
MaxAuthTries 3 # 最大重试次数
ClientAliveInterval 300 # 保活间隔
ClientAliveCountMax 2 # 保活次数
X11Forwarding no
AllowAgentForwarding no
AllowTcpForwarding no
PermitTunnel no
MaxSessions 5
LoginGraceTime 30
```

```bash
# 重启 SSH
sudo systemctl restart sshd

# 配置 SSH 密钥（客户端执行）
ssh-keygen -t ed25519 -C "debian-server"
ssh-copy-id -p 2222 admin@server-ip
```

### 5.2 防火墙配置

```bash
# 方案 A：ufw（简单）
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 2222/tcp comment 'SSH'
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'
sudo ufw enable

# 方案 B：firewalld（企业级，参照 RHEL 章节）
# sudo apt install firewalld
# sudo systemctl enable --now firewalld

# 方案 C：nftables（底层）
# 参见 /etc/nftables.conf
```

### 5.3 fail2ban 防暴力破解

```bash
sudo apt install fail2ban

# 创建本地配置
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local

sudo vim /etc/fail2ban/jail.local
```

```
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5
ignoreip = 127.0.0.1/8 192.168.0.0/16

[sshd]
enabled = true
port = 2222
logpath = %(sshd_log)s
backend = %(sshd_backend)s
maxretry = 3
bantime = 86400
```

```bash
sudo systemctl enable --now fail2ban
sudo fail2ban-client status sshd
```

### 5.4 内核参数加固

```bash
sudo tee /etc/sysctl.d/99-security.conf << 'EOF'
# 限制内核日志访问
kernel.dmesg_restrict = 1
kernel.kptr_restrict = 2

# ASLR 地址空间随机化
kernel.randomize_va_space = 2

# SYN 洪水保护
net.ipv4.tcp_syncookies = 1

# 禁止 IP 转发（除非用作路由器）
net.ipv4.ip_forward = 0
net.ipv6.conf.all.forwarding = 0

# 禁止源路由
net.ipv4.conf.all.accept_source_route = 0
net.ipv6.conf.all.accept_source_route = 0

# 禁止 ICMP 重定向
net.ipv4.conf.all.accept_redirects = 0
net.ipv6.conf.all.accept_redirects = 0

# 反 IP 欺骗
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1

# 禁止广播 ICMP
net.ipv4.icmp_echo_ignore_broadcasts = 1

# 忽略错误消息
net.ipv4.icmp_ignore_bogus_error_responses = 1

# 日志可疑包
net.ipv4.conf.all.log_martians = 1

# Core dump 限制
fs.suid_dumpable = 0
kernel.core_pattern = |/bin/false

# 保护符号链接
fs.protected_symlinks = 1
fs.protected_hardlinks = 1

# 禁止非特权用户使用 BPF
kernel.unprivileged_bpf_disabled = 1
EOF

sudo sysctl -p /etc/sysctl.d/99-security.conf
```

### 5.5 自动安全更新

```bash
sudo apt install unattended-upgrades

# 启用
sudo dpkg-reconfigure -plow unattended-upgrades
# 选择 "Yes"

# 自定义配置：/etc/apt/apt.conf.d/50unattended-upgrades
# 参照 [[../debian/01-apt包管理|APT 包管理]] 中的无人值守升级章节
```

### 5.6 AppArmor

```bash
# Debian/Ubuntu 默认使用 AppArmor（而非 SELinux）
sudo apt install apparmor apparmor-utils

# 检查状态
sudo aa-status

# 为特定程序设置强制模式
sudo aa-enforce /etc/apparmor.d/usr.bin.nginx
```

---

## 6. Ubuntu 特有配置

### 6.1 PPA 管理

```bash
# 添加 PPA 前安装必要工具
sudo apt install software-properties-common

# 添加 PPA
sudo add-apt-repository ppa:ondrej/php
sudo add-apt-repository ppa:deadsnakes/ppa

# 更新源后安装
sudo apt update
sudo apt install php8.3
```

### 6.2 Snap 管理（Ubuntu 默认）

```bash
# 查看 snap 版本
snap version

# 查看已安装的 snap
snap list

# 安装 snap
sudo snap install vlc

# 删除 snap
sudo snap remove vlc

# 如果不想使用 snap（选做）
sudo systemctl stop snapd
sudo systemctl disable snapd

# 阻止 apt 再安装 snapd
sudo tee /etc/apt/preferences.d/nosnap.pref << 'EOF'
Package: snapd
Pin: release a=*
Pin-Priority: -10
EOF
```

### 6.3 Netplan

```bash
# Ubuntu 默认使用 netplan
# 详见 [[../debian/04-netplan与NetworkManager|netplan 与 NetworkManager]]

# 查看当前配置
cat /etc/netplan/*.yaml

# 应用配置
sudo netplan apply

# 测试配置（不实际应用）
sudo netplan try
```

---

## 7. 服务管理

### 7.1 systemd 服务基础

```bash
# 查看所有服务状态
systemctl list-units --type=service

# 启用开机自启
sudo systemctl enable sshd

# 同时启用并启动
sudo systemctl enable --now sshd

# 禁用开机自启
sudo systemctl disable bluetooth

# 屏蔽服务（即使被依赖也不启动）
sudo systemctl mask bluetooth

# 查看启动失败的服务
systemctl --failed

# 查看服务日志
journalctl -u sshd -f
journalctl -u sshd --since yesterday
```

### 7.2 常用服务器服务

```bash
# Web 服务器
sudo apt install nginx
sudo systemctl enable --now nginx

# 数据库
sudo apt install mariadb-server
sudo systemctl enable --now mariadb
sudo mysql_secure_installation

# Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER

# 监控
sudo apt install prometheus-node-exporter
sudo systemctl enable --now prometheus-node-exporter
```

---

## 8. 日志管理

```bash
# 查看系统日志
journalctl -xe
journalctl -b # 本次启动的日志
journalctl -b -1 # 上次启动的日志
journalctl --since "1 hour ago"
journalctl -u nginx -f # 实时跟踪

# 限制日志大小
sudo vim /etc/systemd/journald.conf
```

```
SystemMaxUse=500M
RuntimeMaxUse=100M
MaxRetentionSec=2week
```

```bash
sudo systemctl restart systemd-journald
```

---

## 9. 性能优化

### 9.1 针对服务器的优化

```bash
# 安装 tuned（RHEL 移植，Debian 也可用）
sudo apt install tuned
sudo systemctl enable --now tuned
sudo tuned-adm active
sudo tuned-adm profile throughput-performance # 或 virtual-guest / latency-performance

# CPU 调度器
sudo apt install linux-cpupower
# 查看当前调度器
cpupower frequency-info

# 文件描述符限制
sudo tee -a /etc/security/limits.conf << 'EOF'
* soft nofile 65535
* hard nofile 65535
* soft nproc 65535
* hard nproc 65535
EOF

# swap 倾向（减少对 swap 的依赖）
echo 'vm.swappiness=10' | sudo tee /etc/sysctl.d/99-swap.conf
sudo sysctl -p /etc/sysctl.d/99-swap.conf
```

---

## 10. 备份与恢复

```bash
# timeshift — 系统快照（类似 Btrfs 快照）
sudo apt install timeshift

# rsync 备份 /etc 和 /home
sudo rsync -avz /etc/ /backup/etc-$(date +%Y%m%d)/
sudo rsync -avz /home/ /backup/home-$(date +%Y%m%d)/

# 导出已安装包列表
dpkg --get-selections > ~/package-list.txt

# 从包列表恢复
sudo dpkg --set-selections < ~/package-list.txt
sudo apt-get dselect-upgrade
```

---

## 11. 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| SSH 连接被拒 | 端口不对或防火墙拦截 | 检查 `ss -tlnp \| grep ssh` |
| apt 找不到包 | 未添加 non-free/backports | 检查 sources.list |
| 时区不正确 | 未正确设置 | `sudo timedatectl set-timezone Asia/Shanghai` |
| Debian 无 sudo | 未安装 | `su -` 后 `apt install sudo` |
| 安装时提示缺少固件 | 硬件需要非自由固件 | 使用包含 non-free-firmware 的 ISO 或事后安装 |

---

## 12. 相关资源

- Debian 管理员手册: https://debian-handbook.info/
- Ubuntu 服务器指南: https://ubuntu.com/server/docs
- [[../debian/01-apt包管理|APT 包管理]]
- [[../debian/03-dpkg与deb打包|dpkg 与 deb 打包]]
- [[../debian/04-netplan与NetworkManager|netplan 与 NetworkManager]]
- [[../arch/01-安装指南|Arch Linux 安装指南]]
- [[../redhat/02-RHEL-CentOS安装与配置|RHEL/CentOS 安装与配置]]
