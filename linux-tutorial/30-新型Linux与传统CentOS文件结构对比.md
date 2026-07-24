# 30 - 新型 Linux 与传统 CentOS 文件结构对比

> 随着 CentOS 8 生命周期结束、CentOS Stream 转为上游滚动分支，越来越多的运维工程师开始接触 Arch Linux、Fedora、openSUSE 等现代发行版。本章将系统性对比传统 RHEL/CentOS 文件结构与以 Arch Linux 为代表的现代发行版文件结构，帮助读者理解不同发行版的设计哲学，顺利完成迁移。

---

## 30.1 Linux 发行版分类总览

### 30.1.1 按包管理体系分类

| 体系 | 包格式 | 包管理器 | 代表发行版 |
|------|--------|----------|------------|
| RPM 系 | `.rpm` | yum / dnf / zypper | RHEL, CentOS, Fedora, openSUSE |
| DEB 系 | `.deb` | apt / dpkg | Debian, Ubuntu, Linux Mint |
| 独立系 | 各自格式 | pacman / portage / nix / xbps | Arch, Gentoo, NixOS, Void |

### 30.1.2 按更新模式分类

| 模式 | 特点 | 代表 |
|------|------|------|
| 滚动更新（Rolling Release） | 持续更新，无大版本号 | Arch, openSUSE Tumbleweed, Gentoo |
| 固定版本（Point Release） | 有明确版本号和生命周期 | RHEL, Ubuntu LTS, Debian Stable |
| 半滚动 | 基础系统固定，部分组件滚动 | CentOS Stream, Fedora |

### 30.1.3 按 init 系统分类

| Init 系统 | 说明 | 使用的发行版 |
|-----------|------|-------------|
| systemd | 当前主流 | Arch, Fedora, RHEL 7+, Debian 8+, Ubuntu 15.04+ |
| SysVinit | 传统 init，使用 `/etc/init.d/` 脚本 | Devuan, 旧版 RHEL/CentOS |
| runit | 轻量级监督型 init | Void Linux |
| OpenRC | 基于依赖的 init | Gentoo（默认）, Alpine |

---

## 30.2 CentOS/RHEL 传统文件结构

### 30.2.1 目录布局

CentOS 6/7 遵循传统 FHS（Filesystem Hierarchy Standard）中 `/bin`、`/sbin`、`/lib`、`/lib64` 作为独立顶层目录的设计：

```
/
├── bin/          # 基础用户命令（ls, cp, cat...）
├── sbin/         # 系统管理命令（fdisk, ip, mount...）
├── lib/          # 32 位共享库
├── lib64/        # 64 位共享库
├── usr/
│   ├── bin/      # 非基础用户命令
│   ├── sbin/     # 非基础系统管理命令
│   ├── lib/      # 应用程序库
│   ├── lib64/    # 64 位应用库
│   ├── local/    # 本地编译安装的软件
│   └── share/    # 架构无关数据
├── etc/
│   ├── sysconfig/    # RHEL 特有的系统配置目录
│   ├── init.d/       # SysV 服务脚本（CentOS 6）
│   ├── yum.conf      # YUM 配置
│   └── yum.repos.d/  # 仓库定义
├── var/
│   ├── log/
│   │   └── messages  # 传统系统日志
│   └── cache/yum/    # YUM 缓存
└── opt/              # 第三方商业软件
```

**关键特征：** `/bin` 和 `/usr/bin` 是独立的目录，存放不同重要等级的程序。这一设计源自早期 Unix 磁盘空间不足，需将 `/usr` 放在单独分区的历史。

### 30.2.2 `/bin` vs `/usr/bin` 的历史分离

在 CentOS 6 及更早版本中：

```bash
# /bin 中是启动和单用户模式必需的命令
ls -la /bin/ls
# -rwxr-xr-x. 1 root root 117608 /bin/ls

# /usr/bin 中是正常运行时才需要的命令
ls -la /usr/bin/vim
# -rwxr-xr-x. 1 root root 2337192 /usr/bin/vim

# 它们是完全独立的目录
stat /bin
# File: '/bin'
# Size: 4096    Blocks: 8    IO Block: 4096   directory
```

从 CentOS 7 开始（跟随 Fedora 17），RHEL 系也开始了 `/usr` 合并，但保留了兼容性软链接：

```bash
# CentOS 7+ 中 /bin 已变为软链接
ls -ld /bin
# lrwxrwxrwx. 1 root root 7 /bin -> usr/bin

ls -ld /sbin
# lrwxrwxrwx. 1 root root 8 /sbin -> usr/sbin

ls -ld /lib
# lrwxrwxrwx. 1 root root 7 /lib -> usr/lib

ls -ld /lib64
# lrwxrwxrwx. 1 root root 9 /lib64 -> usr/lib64
```

### 30.2.3 YUM/DNF 包管理

```bash
# CentOS 7 使用 YUM
yum install httpd
yum update
yum search nginx
yum info kernel
yum groupinstall "Development Tools"
yum repolist

# CentOS 8+ / RHEL 8+ 使用 DNF
dnf install httpd
dnf module list
dnf module enable nodejs:18
dnf provides /usr/bin/dig

# 仓库配置
cat /etc/yum.repos.d/CentOS-Base.repo
```

```ini
# /etc/yum.conf 典型配置
[main]
gpgcheck=1
installonly_limit=3
clean_requirements_on_remove=True
best=True
skip_if_unavailable=False
```

### 30.2.4 SELinux 强制访问控制

```bash
# 查看 SELinux 状态
getenforce
# Enforcing

sestatus
# SELinux status:                 enabled
# Current mode:                   enforcing
# Policy from config file:        targeted

# 查看文件安全上下文
ls -Z /var/www/html/
# -rw-r--r--. root root unconfined_u:object_r:httpd_sys_content_t:s0 index.html

# 修改上下文
chcon -R -t httpd_sys_content_t /var/www/html/
restorecon -Rv /var/www/html/

# 布尔值管理
getsebool -a | grep httpd
setsebool -P httpd_can_network_connect on

# 排查 SELinux 拒绝
ausearch -m avc -ts recent
sealert -a /var/log/audit/audit.log
```

### 30.2.5 防火墙管理

```bash
# CentOS 7+ 使用 firewalld
firewall-cmd --state
firewall-cmd --list-all
firewall-cmd --add-service=http --permanent
firewall-cmd --add-port=8080/tcp --permanent
firewall-cmd --reload

# CentOS 6 使用 iptables
service iptables status
iptables -L -n
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
service iptables save
```

### 30.2.6 `/etc/sysconfig/` 目录

这是 RHEL 系特有的配置风格：

```bash
ls /etc/sysconfig/
# network-scripts/    # 网络配置（CentOS 7）
# iptables            # 防火墙规则
# selinux             # SELinux 配置
# clock               # 时区
# keyboard            # 键盘布局
# i18n                # 国际化

# 典型的网卡配置
cat /etc/sysconfig/network-scripts/ifcfg-eth0
```

```ini
TYPE=Ethernet
BOOTPROTO=static
NAME=eth0
DEVICE=eth0
ONBOOT=yes
IPADDR=192.168.1.100
NETMASK=255.255.255.0
GATEWAY=192.168.1.1
DNS1=8.8.8.8
```

### 30.2.7 日志系统

```bash
# 传统方式：rsyslog → /var/log/messages
tail -f /var/log/messages
cat /var/log/secure        # 认证日志
cat /var/log/cron          # 定时任务日志
cat /var/log/maillog       # 邮件日志

# CentOS 7+ 同时支持 journalctl
journalctl -u sshd
journalctl --since "2024-01-01" --until "2024-01-02"
journalctl -p err          # 只看错误级别
```

---

## 30.3 Arch Linux 现代文件结构

### 30.3.1 目录布局

Arch Linux 从诞生之初就采用了更现代的文件系统布局：

```
/
├── bin -> usr/bin          # 软链接
├── sbin -> usr/bin         # 软链接（注意：指向 usr/bin 而非 usr/sbin）
├── lib -> usr/lib          # 软链接
├── lib64 -> usr/lib        # 软链接
├── usr/
│   ├── bin/                # 所有可执行文件统一存放
│   ├── lib/                # 所有库文件统一存放（含 64 位）
│   ├── lib32/              # 32 位兼容库（需启用 multilib）
│   ├── share/              # 架构无关数据
│   └── local/              # 本地安装（通常为空）
├── etc/
│   ├── pacman.conf         # pacman 配置
│   ├── pacman.d/
│   │   └── mirrorlist      # 镜像列表
│   ├── makepkg.conf        # 构建配置
│   ├── mkinitcpio.conf     # initramfs 配置
│   └── systemd/            # systemd 配置覆盖
├── var/
│   ├── cache/pacman/pkg/   # 包缓存
│   └── log/pacman.log      # pacman 操作日志
├── opt/                    # 大型第三方程序
└── srv/                    # 服务数据
```

### 30.3.2 /usr 合并的意义

```bash
# Arch 中 /bin、/sbin、/lib 全部是软链接
ls -la /bin
# lrwxrwxrwx 1 root root 7 /bin -> usr/bin

ls -la /sbin
# lrwxrwxrwx 1 root root 7 /sbin -> usr/bin
# 注意：/sbin 也指向 usr/bin，不区分管理命令和用户命令

ls -la /lib
# lrwxrwxrwx 1 root root 7 /lib -> usr/lib

ls -la /lib64
# lrwxrwxrwx 1 root root 7 /lib64 -> usr/lib
```

**合并的好处：**

| 传统分离 | /usr 合并后 | 优势 |
|---------|------------|------|
| `/bin/mount` vs `/usr/bin/mount` | 统一在 `/usr/bin/mount` | 消除文件归属歧义 |
| 需要 initramfs 提前挂载 `/usr` | `/usr` 可整体为只读分区 | 系统快照更可靠 |
| `/sbin` 和 `/usr/sbin` 分开 | 全部在 `/usr/bin` | `$PATH` 更简洁 |
| `/lib` 和 `/lib64` 分离 | 统一为 `/usr/lib` | 多架构处理更清晰 |

### 30.3.3 pacman 包管理

```bash
# 同步数据库并更新系统
pacman -Syu

# 安装软件包
pacman -S nginx

# 搜索软件包
pacman -Ss web server

# 查看包信息
pacman -Si nginx

# 查看已安装包的文件列表
pacman -Ql nginx

# 查看某文件属于哪个包
pacman -Qo /usr/bin/nginx

# 移除软件包及其不再需要的依赖
pacman -Rns nginx

# 清理缓存
pacman -Sc      # 清理未安装的包缓存
paccache -r     # 只保留最近 3 个版本

# 查看孤儿包
pacman -Qdt
```

```ini
# /etc/pacman.conf 核心配置
[options]
HoldPkg     = pacman glibc
Architecture = auto
Color
CheckSpace
ParallelDownloads = 5
SigLevel    = Required DatabaseOptional

[core]
Include = /etc/pacman.d/mirrorlist

[extra]
Include = /etc/pacman.d/mirrorlist

# 启用 32 位库支持（取消下面两行注释）
#[multilib]
#Include = /etc/pacman.d/mirrorlist
```

### 30.3.4 无 SELinux 的安全方案

Arch Linux 默认不使用 SELinux，安全策略更加简洁：

```bash
# Arch 的安全工具栈
# 1. 文件权限 + ACL
setfacl -m u:www:rx /srv/http/

# 2. systemd 沙箱化（推荐）
systemctl edit nginx.service
```

```ini
# systemd 服务沙箱配置示例
[Service]
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/var/log/nginx /var/cache/nginx
PrivateTmp=yes
NoNewPrivileges=yes
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
SystemCallFilter=@system-service
```

```bash
# 3. 可选安装 AppArmor
pacman -S apparmor
systemctl enable apparmor.service

# 4. Firejail 应用程序沙箱
pacman -S firejail
firejail firefox
```

### 30.3.5 纯 systemd 管理

```bash
# Arch 全面拥抱 systemd，没有 SysV 遗留
systemctl start nginx
systemctl enable nginx
systemctl status nginx

# 网络管理（systemd-networkd 或 NetworkManager）
systemctl enable systemd-networkd
systemctl enable systemd-resolved

# 日志只通过 journalctl
journalctl -u nginx --since today
journalctl -b                    # 本次启动的日志
journalctl --disk-usage          # 查看日志占用空间
journalctl --vacuum-size=500M    # 限制日志大小

# 定时任务使用 systemd timer 而非 cron
systemctl list-timers --all
```

---

## 30.4 其他现代发行版特征

### 30.4.1 Fedora — 最接近上游

```bash
# Fedora 已切换到 DNF5（C++ 重写，更快）
dnf5 install vim
dnf5 upgrade --refresh

# 文件结构与 Arch 类似（/usr 合并先驱）
ls -la /bin    # -> usr/bin
ls -la /sbin   # -> usr/sbin （注意：Fedora 保留 usr/sbin）

# Fedora 特色
# - 默认 Btrfs（Workstation 版）
# - 默认 PipeWire 音频
# - 默认 Wayland
# - GNOME 最新版首发
# - 每 6 个月一个新版本
```

### 30.4.2 openSUSE — YaST 与 Btrfs

```bash
# openSUSE 使用 zypper 包管理器
zypper install vim
zypper refresh
zypper update
zypper search nginx
zypper info nginx

# YaST 系统管理工具（TUI / GUI）
yast2                 # 图形界面
yast                  # 文本界面
yast2 firewall        # 防火墙管理
yast2 users           # 用户管理

# 默认 Btrfs + Snapper 快照
snapper list
snapper create --description "before update"
snapper undochange 1..2
snapper rollback
# 可在 GRUB 中直接选择快照启动
```

### 30.4.3 NixOS — 声明式配置

```nix
# /etc/nixos/configuration.nix
{ config, pkgs, ... }:
{
  boot.loader.grub.enable = true;
  boot.loader.grub.device = "/dev/sda";

  networking.hostName = "myhost";
  networking.firewall.allowedTCPPorts = [ 80 443 ];

  environment.systemPackages = with pkgs; [
    vim
    git
    nginx
  ];

  services.nginx.enable = true;
  services.openssh.enable = true;

  users.users.admin = {
    isNormalUser = true;
    extraGroups = [ "wheel" ];
  };
}
```

```bash
# NixOS 的独特文件结构
/nix/store/            # 所有包以哈希命名存放
# /nix/store/abc123-nginx-1.24.0/bin/nginx
# /nix/store/def456-vim-9.0/bin/vim

# 构建并切换到新配置
nixos-rebuild switch

# 回滚到上一个配置
nixos-rebuild switch --rollback

# 垃圾回收
nix-collect-garbage -d
```

### 30.4.4 Void Linux — runit init

```bash
# Void 使用 xbps 包管理器
xbps-install -S nginx
xbps-query -Rs nginx
xbps-remove nginx

# runit 服务管理
ln -s /etc/sv/nginx /var/service/    # 启用服务
sv start nginx                       # 启动
sv stop nginx                        # 停止
sv status nginx                      # 状态

# 无 systemd、无 journald
# 日志由 svlogd 管理，存放在 /var/log/socklog/
```

### 30.4.5 Gentoo — 源码编译

```bash
# Gentoo 使用 Portage / emerge
emerge --ask www-servers/nginx
emerge --update --deep --newuse @world
emerge --search nginx

# USE 标志定制编译特性
echo "www-servers/nginx ssl http2 pcre" >> /etc/portage/package.use/nginx

# /etc/portage/make.conf
CFLAGS="-march=native -O2 -pipe"
MAKEOPTS="-j$(nproc)"
USE="X gtk -gnome -kde systemd"
ACCEPT_LICENSE="*"
```

---

## 30.5 文件结构对比表

| 路径 | CentOS 6 | CentOS 7+ | Arch Linux | Fedora 40+ | NixOS |
|------|----------|-----------|------------|------------|-------|
| `/bin` | 独立目录 | → `usr/bin` | → `usr/bin` | → `usr/bin` | → `usr/bin` |
| `/sbin` | 独立目录 | → `usr/sbin` | → `usr/bin` | → `usr/sbin` | → `usr/bin` |
| `/lib` | 独立目录 | → `usr/lib` | → `usr/lib` | → `usr/lib` | → `usr/lib` |
| `/lib64` | 独立目录 | → `usr/lib64` | → `usr/lib` | → `usr/lib64` | 无 |
| `/usr/sbin` | 独立目录 | 独立目录 | → `bin`（合并） | 独立目录 | → `bin` |
| `/etc/sysconfig/` | 存在 | 存在 | 不存在 | 存在（精简） | 不存在 |
| `/etc/init.d/` | 核心目录 | 兼容保留 | 不存在 | 不存在 | 不存在 |
| `/nix/store/` | 不存在 | 不存在 | 不存在 | 不存在 | 核心目录 |
| 日志主文件 | `/var/log/messages` | 两者并存 | `journalctl` | `journalctl` | `journalctl` |

---

## 30.6 包管理器对比

| 操作 | pacman (Arch) | dnf (Fedora/RHEL) | apt (Debian/Ubuntu) | zypper (openSUSE) | nix (NixOS) |
|------|--------------|-------------------|--------------------|--------------------|-------------|
| 安装 | `pacman -S pkg` | `dnf install pkg` | `apt install pkg` | `zypper in pkg` | `nix-env -iA pkg` |
| 卸载 | `pacman -Rns pkg` | `dnf remove pkg` | `apt remove pkg` | `zypper rm pkg` | `nix-env -e pkg` |
| 更新系统 | `pacman -Syu` | `dnf upgrade` | `apt upgrade` | `zypper up` | `nixos-rebuild switch` |
| 搜索 | `pacman -Ss key` | `dnf search key` | `apt search key` | `zypper se key` | `nix search key` |
| 包信息 | `pacman -Si pkg` | `dnf info pkg` | `apt show pkg` | `zypper info pkg` | `nix-env -qa --description pkg` |
| 文件所属 | `pacman -Qo file` | `dnf provides file` | `dpkg -S file` | `zypper se --provides file` | `-` |
| 列出文件 | `pacman -Ql pkg` | `rpm -ql pkg` | `dpkg -L pkg` | `rpm -ql pkg` | `-` |
| 清理缓存 | `pacman -Sc` | `dnf clean all` | `apt clean` | `zypper clean` | `nix-collect-garbage` |
| 仓库配置 | `/etc/pacman.conf` | `/etc/yum.repos.d/` | `/etc/apt/sources.list.d/` | `/etc/zypp/repos.d/` | `/etc/nixos/configuration.nix` |
| 用户仓库 | AUR | COPR | PPA | OBS | Nixpkgs / Flakes |
| 包格式 | `.pkg.tar.zst` | `.rpm` | `.deb` | `.rpm` | NAR (Nix Archive) |

---

## 30.7 服务管理对比

### 30.7.1 SysVinit（CentOS 6）vs systemd（Arch / CentOS 7+）

| 操作 | SysVinit (CentOS 6) | systemd (Arch / CentOS 7+) |
|------|---------------------|---------------------------|
| 启动服务 | `service httpd start` | `systemctl start httpd` |
| 停止服务 | `service httpd stop` | `systemctl stop httpd` |
| 重启服务 | `service httpd restart` | `systemctl restart httpd` |
| 查看状态 | `service httpd status` | `systemctl status httpd` |
| 开机启用 | `chkconfig httpd on` | `systemctl enable httpd` |
| 开机禁用 | `chkconfig httpd off` | `systemctl disable httpd` |
| 列出服务 | `chkconfig --list` | `systemctl list-unit-files` |
| 查看日志 | `cat /var/log/messages` | `journalctl -u httpd` |
| 运行级别 | `runlevel` / `init 3` | `systemctl get-default` / `systemctl isolate multi-user.target` |

### 30.7.2 Arch Linux 典型 systemd 服务单元

```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=My Application
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=myapp
Group=myapp
WorkingDirectory=/opt/myapp
ExecStart=/opt/myapp/bin/server
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/opt/myapp/data
PrivateTmp=yes
NoNewPrivileges=yes

[Install]
WantedBy=multi-user.target
```

### 30.7.3 systemd timer 替代 cron

```ini
# /etc/systemd/system/backup.timer
[Unit]
Description=Daily Backup Timer

[Timer]
OnCalendar=*-*-* 02:00:00
Persistent=true
RandomizedDelaySec=300

[Install]
WantedBy=timers.target
```

```ini
# /etc/systemd/system/backup.service
[Unit]
Description=Daily Backup

[Service]
Type=oneshot
ExecStart=/usr/local/bin/backup.sh
```

```bash
systemctl enable --now backup.timer
systemctl list-timers
```

---

## 30.8 配置管理哲学差异

### 30.8.1 CentOS/RHEL — 企业保守主义

```
设计哲学：
├── 稳定优先 → 软件版本通常落后上游 2-5 年
├── 向后兼容 → 保留 /etc/sysconfig/ 等历史目录
├── 安全加固 → SELinux 默认 Enforcing
├── 工具集成 → 提供 system-config-* 系列 GUI 工具
└── 长期支持 → RHEL 生命周期长达 10 年
```

### 30.8.2 Arch Linux — 简洁与前沿

```
设计哲学：
├── KISS 原则 → Keep It Simple, Stupid
├── 用户中心 → 不做自动化魔法，用户完全掌控
├── 最新上游 → 尽快跟进上游版本
├── 单一方案 → systemd 统一管理，不保留旧方案
├── 文档驱动 → Arch Wiki 是 Linux 世界最好的文档
└── 滚动更新 → 没有大版本升级的痛苦
```

### 30.8.3 配置文件位置对比

| 功能 | CentOS/RHEL | Arch Linux |
|------|-------------|------------|
| 网络配置 | `/etc/sysconfig/network-scripts/ifcfg-*` | `/etc/systemd/network/*.network` 或 NetworkManager |
| 主机名 | `/etc/sysconfig/network` 中 `HOSTNAME=` | `/etc/hostname`（systemd 标准） |
| DNS 解析 | `/etc/resolv.conf`（手动或 NetworkManager） | `/etc/resolv.conf` 或 `systemd-resolved` |
| 语言区域 | `/etc/sysconfig/i18n` 或 `/etc/locale.conf` | `/etc/locale.conf` |
| 键盘布局 | `/etc/sysconfig/keyboard` | `/etc/vconsole.conf` |
| 默认编辑器 | `EDITOR` 环境变量 | `EDITOR` 环境变量 |
| 包管理器配置 | `/etc/yum.conf` + `/etc/yum.repos.d/` | `/etc/pacman.conf` + `/etc/pacman.d/` |
| 引导加载器 | GRUB2 `/etc/default/grub` | GRUB2 / systemd-boot / rEFInd |
| initramfs | dracut `/etc/dracut.conf` | mkinitcpio `/etc/mkinitcpio.conf` |

---

## 30.9 从 CentOS 迁移到 Arch 的注意事项

### 30.9.1 思维转变清单

| CentOS 习惯 | Arch 对应 | 注意事项 |
|-------------|----------|---------|
| `yum install` | `pacman -S` | 语法完全不同，需要重新记忆 |
| 依赖 SELinux | systemd 沙箱 + AppArmor | 需重新设计安全策略 |
| 半年到一年更新一次 | 至少每周 `pacman -Syu` | 长时间不更新会导致滚动更新失败 |
| `service xxx restart` | `systemctl restart xxx` | CentOS 7+ 已支持 |
| `chkconfig` | `systemctl enable` | CentOS 7+ 已支持 |
| RPM spec 打包 | PKGBUILD 打包 | 学习新的打包格式 |
| `/var/log/messages` | `journalctl` | 默认无文本日志文件 |
| `ifconfig` / `route` | `ip addr` / `ip route` | Arch 不装 net-tools |
| 内核固定在某个大版本 | 始终最新稳定内核 | 注意内核模块兼容性 |

### 30.9.2 常见迁移陷阱

```bash
# 陷阱 1：Arch 没有 `wget`、`curl` 以外的下载工具预装
# 安装后第一步
pacman -S base-devel git vim wget

# 陷阱 2：Arch 没有 /etc/sysconfig/，不要找
# 网络配置应使用 systemd-networkd 或 NetworkManager
nmcli connection show
nmcli connection modify eth0 ipv4.method manual ipv4.addresses 192.168.1.100/24

# 陷阱 3：没有 yum-cron，用 systemd timer 或第三方工具
# 但 Arch 不建议自动更新，因为滚动更新可能需要人工干预

# 陷阱 4：不要混用 AUR 助手和 pacman
# AUR 助手（如 yay/paru）是对 pacman 的封装，不要用 sudo 运行
yay -S google-chrome    # 正确：不加 sudo
paru -S visual-studio-code-bin

# 陷阱 5：Arch 没有类似 EPEL 的"官方附加仓库"
# 需要的软件如果不在官方仓库，去 AUR 找
```

### 30.9.3 服务迁移对照表

| 服务 | CentOS 包名 | Arch 包名 | 配置差异 |
|------|------------|----------|---------|
| Web 服务器 | `httpd` | `apache` | 配置目录结构不同 |
| 数据库 | `mariadb-server` | `mariadb` | 初始化命令相同 |
| PHP | `php`, `php-fpm` | `php`, `php-fpm` | 模块配置路径不同 |
| 邮件 | `postfix` | `postfix` | 基本兼容 |
| DNS | `bind` | `bind` | 基本兼容 |
| 监控 | `zabbix-server` | `zabbix-server`（AUR） | 需从 AUR 安装 |

---

## 30.10 容器化时代的影响

### 30.10.1 容器中的发行版趋同

在容器化时代，所有发行版在容器内部的表现趋于一致：

```dockerfile
# 不同基础镜像，相同的应用部署
# Alpine（最小化）
FROM alpine:3.19
RUN apk add --no-cache nginx

# Arch Linux
FROM archlinux:latest
RUN pacman -Syu --noconfirm nginx

# Debian
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y nginx

# Fedora
FROM fedora:40
RUN dnf install -y nginx
```

### 30.10.2 容器中不需要关心的差异

```
容器消除的差异：
├── init 系统 → 容器通常直接运行进程，不需要 init
├── SELinux/AppArmor → 安全由容器运行时（containerd/runc）处理
├── 防火墙 → 网络策略由编排系统（K8s NetworkPolicy）处理
├── 服务管理 → 容器 = 进程，无需 systemd
├── 文件结构 → 只关心应用目录，不关心系统目录
└── 日志管理 → 标准输出即日志（docker logs / kubectl logs）
```

### 30.10.3 容器基础镜像大小对比

| 基础镜像 | 压缩大小 | 特点 |
|---------|---------|------|
| `alpine:3.19` | ~3.4 MB | musl libc，可能有兼容性问题 |
| `debian:bookworm-slim` | ~29 MB | glibc，兼容性好 |
| `archlinux:latest` | ~127 MB | 滚动更新，始终最新 |
| `fedora:40` | ~57 MB | 较新软件栈 |
| `ubuntu:24.04` | ~29 MB | 广泛使用 |
| `scratch` | 0 MB | 空镜像，用于静态编译程序 |

### 30.10.4 不可变基础设施

现代 Linux 正在向不可变基础设施发展：

| 方案 | 发行版 | 特点 |
|------|--------|------|
| Fedora CoreOS | Fedora 系 | 自动更新、rpm-ostree、面向容器 |
| Flatcar Container Linux | 独立 | CoreOS 继承者，纯容器主机 |
| Talos Linux | 独立 | 无 shell、API 驱动、K8s 专用 |
| NixOS | 独立 | 声明式配置、原子升级和回滚 |
| Arch + Btrfs 快照 | Arch 系 | 手动实现类似不可变性 |

```bash
# Arch + Btrfs 实现简易不可变方案
# 更新前自动快照
snapper create --description "pre-update"
pacman -Syu

# 如果出问题，回滚
snapper undochange <num>
# 或从 GRUB 启动旧快照
```

---

## 30.11 总结与选择建议

| 场景 | 推荐发行版 | 理由 |
|------|-----------|------|
| 企业生产服务器 | RHEL / Rocky Linux | 长期支持、商业支持、合规认证 |
| 开发工作站 | Arch / Fedora | 最新软件栈、开发工具链完整 |
| 学习 Linux | Arch Linux | 手动安装过程是最好的学习 |
| 容器主机 | Fedora CoreOS / Flatcar | 专为容器设计 |
| 嵌入式/IoT | Alpine / Void / Buildroot | 极小体积 |
| 可重现部署 | NixOS | 声明式、确定性构建 |
| 桌面日用 | Arch / Fedora / openSUSE | 软件新、社区活跃 |

理解不同发行版的文件结构和设计哲学，是跨发行版工作的基础。无论你来自哪个发行版，掌握 FHS 标准和 systemd 这两个共同基础，就能在任何现代 Linux 系统上高效工作。

---

## 30.12 本章测验

> [!example] 📝 自测题目

> [!question]- 选择题 1：在 Arch Linux 中，/sbin 软链接指向哪里？
> - A. usr/sbin
> - B. usr/bin
> - C. bin
> - D. usr/local/sbin
>
> > [!success]- 点击查看答案
> > **B**
> > Arch Linux 中 /sbin 指向 usr/bin（注意不是 usr/sbin）。Arch 完全合并了 sbin 和 bin，不区分管理命令和用户命令。

> [!question]- 选择题 2：CentOS 7 开始的 /usr 合并与 Arch Linux 的 /usr 合并有什么区别？
> - A. 完全一样，没有区别
> - B. CentOS 保留了 /usr/sbin 作为独立目录，Arch 将 /usr/sbin 也合并到了 /usr/bin
> - C. Arch 没有进行 /usr 合并
> - D. CentOS 的 /lib64 指向 /usr/lib，Arch 指向 /usr/lib64
>
> > [!success]- 点击查看答案
> > **B**
> > CentOS 7+ 中 /sbin → usr/sbin（保留 usr/sbin 独立），而 Arch 中 /sbin → usr/bin，/usr/sbin 也合并到了 /usr/bin，更加彻底。

> [!question]- 选择题 3：以下哪个目录是 RHEL/CentOS 特有的，在 Arch Linux 中不存在？
> - A. /etc/systemd/
> - B. /etc/sysconfig/
> - C. /usr/share/
> - D. /var/log/
>
> > [!success]- 点击查看答案
> > **B**
> > /etc/sysconfig/ 是 RHEL 系特有的系统配置目录，用于存放网络、防火墙、键盘等配置。Arch Linux 中不存在此目录。

> [!question]- 选择题 4：从 CentOS 迁移到 Arch Linux 后，查看系统日志应使用什么命令？
> - A. `cat /var/log/messages`
> - B. `tail -f /var/log/syslog`
> - C. `journalctl`
> - D. `dmesg --follow`
>
> > [!success]- 点击查看答案
> > **C**
> > Arch Linux 默认只通过 journalctl 查看日志，没有 /var/log/messages 文本日志文件（除非额外配置 rsyslog）。

> [!question]- 判断题 5：Arch Linux 建议设置 yum-cron 类似的自动更新机制来保持系统最新。
> - A. ✓ 正确
> - B. ✗ 错误
>
> > [!success]- 点击查看答案
> > **B. ✗ 错误**
> > Arch Linux 不建议自动更新，因为滚动更新可能需要人工干预（如配置文件合并、手动处理冲突等）。应手动执行 `pacman -Syu` 并关注更新内容。

> [!question]- 选择题 6：NixOS 与传统发行版最本质的区别是什么？
> - A. 使用 RPM 包格式
> - B. 所有包以哈希命名存放在 /nix/store/，采用声明式配置
> - C. 只支持命令行界面
> - D. 不支持 systemd
>
> > [!success]- 点击查看答案
> > **B**
> > NixOS 将所有包存放在 /nix/store/ 中并以哈希命名，通过 /etc/nixos/configuration.nix 声明式配置整个系统，支持原子升级和回滚。

> [!question]- 选择题 7：以下哪个不是 Arch Linux 的设计哲学？
> - A. KISS 原则（Keep It Simple, Stupid）
> - B. 用户中心，不做自动化魔法
> - C. 长期支持，10 年生命周期
> - D. 滚动更新，紧跟上游
>
> > [!success]- 点击查看答案
> > **C**
> > "长期支持，10 年生命周期"是 RHEL 的特征。Arch Linux 是滚动发布的，没有版本号和固定生命周期概念。

> [!question]- 判断题 8：在容器化时代，不同发行版在容器内部的表现趋于一致，init 系统和文件结构的差异不再重要。
> - A. ✓ 正确
> - B. ✗ 错误
>
> > [!success]- 点击查看答案
> > **A. ✓ 正确**
> > 容器通常直接运行进程，不需要 init 系统。安全由容器运行时处理，网络策略由编排系统处理，日志通过标准输出。发行版差异在容器中被大幅消除。

> [!question]- 选择题 9：Arch Linux 中等价于 CentOS 的 `chkconfig httpd on` 的命令是？
> - A. `systemctl start httpd`
> - B. `systemctl enable httpd`
> - C. `service httpd enable`
> - D. `rc-update add httpd`
>
> > [!success]- 点击查看答案
> > **B**
> > `systemctl enable httpd` 等价于 CentOS 6 的 `chkconfig httpd on`，都是设置服务开机自启动。

> [!question]- 选择题 10：使用 AUR 助手（如 yay/paru）安装软件时，以下哪种做法是正确的？
> - A. `sudo yay -S google-chrome`
> - B. `yay -S google-chrome`
> - C. `pacman -S google-chrome`
> - D. `yay --root -S google-chrome`
>
> > [!success]- 点击查看答案
> > **B**
> > AUR 助手不应使用 sudo 运行，它会在需要时自动请求提权。直接运行 `yay -S <package>` 即可。
