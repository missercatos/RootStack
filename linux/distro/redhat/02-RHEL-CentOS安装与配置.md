# RHEL/CentOS 安装与配置

> Red Hat Enterprise Linux 是企业级 Linux 市场的领导者。本章涵盖 RHEL、CentOS Stream、Rocky Linux、AlmaLinux 和 Fedora 的安装流程、订阅管理和服务器安全加固。

---

## 1. 资源链接

| 资源 | 链接 |
|------|------|
| Red Hat 官网 | https://www.redhat.com/ |
| Red Hat 开发者订阅（免费） | https://developers.redhat.com/ |
| CentOS Stream 官网 | https://www.centos.org/ |
| Rocky Linux 官网 | https://rockylinux.org/ |
| AlmaLinux 官网 | https://almalinux.org/ |
| Fedora 官网 | https://getfedora.org/ |
| 清华大学 Rocky 镜像 | https://mirrors.tuna.tsinghua.edu.cn/rocky/ |
| 清华大学 AlmaLinux 镜像 | https://mirrors.tuna.tsinghua.edu.cn/almalinux/ |
| 清华大学 CentOS 镜像 | https://mirrors.tuna.tsinghua.edu.cn/centos/ |
| 中科大 Rocky 镜像 | https://mirrors.ustc.edu.cn/rocky/ |

---

## 2. RHEL 生态系统

### 2.1 发行版关系

```
Fedora（上游创新源）
    ↓ 每 6 个月
CentOS Stream（RHEL 开发预览）
    ↓ 持续集成
RHEL（Red Hat 官方企业版）
    ↓ 源代码公开
Rocky Linux / AlmaLinux（社区重建版，100% 兼容）
    ↓
Oracle Linux（Oracle 发行版，UEK 内核）

选择建议：
- 学习/RHEL 生态体验 → Rocky Linux 或 AlmaLinux（免费）
- 生产环境需要官方支持 → RHEL（开发者免费 16 台）
- 桌面/个人 → Fedora
- 想提前看 RHEL 新特性 → CentOS Stream
```

### 2.2 版本对照

| RHEL 版本 | 代号 | Fedora 基础 | 内核 | EOL |
|-----------|------|-------------|------|-----|
| RHEL 9 | - | Fedora 34 | 5.14 | 2032 |
| RHEL 8 | - | Fedora 28 | 4.18 | 2029 |
| RHEL 7 | - | Fedora 19 | 3.10 | 2029 (ELS) |

---

## 3. 安装流程

### 3.1 下载镜像

```bash
# Rocky Linux 9 DVD ISO
wget https://mirrors.tuna.tsinghua.edu.cn/rocky/9/isos/x86_64/Rocky-9-latest-x86_64-dvd.iso

# AlmaLinux 9 DVD ISO
wget https://mirrors.tuna.tsinghua.edu.cn/almalinux/9/isos/x86_64/AlmaLinux-9-latest-x86_64-dvd.iso

# Fedora Server DVD ISO
wget https://mirrors.tuna.tsinghua.edu.cn/fedora/releases/40/Server/x86_64/iso/Fedora-Server-dvd-x86_64-40-1.4.iso

# RHEL（需要注册 Red Hat 账号）
# https://developers.redhat.com/products/rhel/download
```

### 3.2 安装步骤（服务器模式）

```
1. 启动后选择 "Install Rocky Linux 9.x"

2. 语言: English (United States)   （推荐英文，减少 TTY 乱码）

3. Installation Summary 界面配置：
   ├── Keyboard            → English (US)
   ├── Language Support    → 添加简体中文
   ├── Time & Date         → Asia/Shanghai, NTP ON
   ├── Installation Source → 自动检测（或指定镜像 URL）
   ├── Software Selection  → Server（无 GUI）
   │   └── 勾选 "Standard" 和 "System Tools"
   ├── Installation Destination → 选硬盘，Storage Configuration: Custom
   ├── Network & Hostname  → 设置主机名，开启网卡
   ├── Root Password       → 设置 root 密码
   └── User Creation       → 创建管理员用户，设为 Administrator

4. 点击 "Begin Installation"

5. 完成后 "Reboot System"
```

### 3.3 手动分区（服务器推荐）

```
方案 A: 标准分区（生产环境推荐）

/boot           1 GiB       xfs （或 ext4）
/boot/efi       512 MiB     EFI System （UEFI 模式）
/              50 GiB       xfs
/home          剩余空间      xfs     （有用户数据场景）
swap           8 GiB        swap    （或按需）

方案 B: LVM（灵活扩容）

/boot           1 GiB       xfs
/boot/efi       512 MiB     EFI System
/              20 GiB       xfs (LVM)
/var           20 GiB       xfs (LVM)
/var/log       10 GiB       xfs (LVM)
/tmp            5 GiB       xfs (LVM)
/home          剩余         xfs (LVM)
swap           8 GiB        swap (LVM)

方案 C: 加密 LVM（安全增强）

/boot           1 GiB       xfs （不加密）
/boot/efi       512 MiB     EFI System
LUKS 加密卷    全部剩余     LVM PV
  ├─ /          20 GiB       xfs
  ├─ /home      剩余          xfs
  └─ swap       按需          swap
```

### 3.4 Kickstart 自动化安装

```bash
# Kickstart 是 RHEL 的无人值守安装系统
# 在安装完成后会生成 /root/anaconda-ks.cfg

# 修改它用于批量部署：
cp /root/anaconda-ks.cfg /tmp/ks.cfg
vim /tmp/ks.cfg
```

```bash
# 简化的 Kickstart 示例
# ks.cfg
#version=RHEL9
text                               # 文本模式安装
url --url="https://mirrors.tuna.tsinghua.edu.cn/rocky/9/BaseOS/x86_64/os/"

%addon com_redhat_kdump --disable
%end

keyboard --vckeymap=us
lang en_US.UTF-8
timezone Asia/Shanghai --utc

network --bootproto=dhcp --device=link --activate --hostname=server01
rootpw --iscrypted $6$hash...
user --name=admin --password=$6$hash... --iscrypted --groups=wheel

zerombr
clearpart --all --initlabel
autopart --type=lvm

bootloader --location=mbr

%packages
@^server-product-environment
@standard
@system-tools
vim
git
curl
wget
htop
tmux
%end

reboot
```

```bash
# 使用 Kickstart 安装
# 启动时在 boot 提示符输入：
# linux ks=https://server.example.com/ks.cfg
```

---

## 4. 安装后配置

### 4.1 注册 RHEL 订阅

```bash
# RHEL 需要注册
sudo subscription-manager register --username your-name --password your-password

# 查看订阅状态
sudo subscription-manager status
sudo subscription-manager list

# 附加订阅
sudo subscription-manager attach --auto

# 开发者免费订阅注册（16台机器限额）
# https://developers.redhat.com/register

# Rocky/AlmaLinux 无需注册（开源免费）
```

### 4.2 配置中国镜像（Rocky/AlmaLinux）

```bash
# 备份默认仓库
sudo mkdir /etc/yum.repos.d/backup
sudo mv /etc/yum.repos.d/*.repo /etc/yum.repos.d/backup/

# 写入清华镜像
sudo tee /etc/yum.repos.d/rocky-mirror.repo << 'EOF'
[baseos]
name=Rocky Linux $releasever - BaseOS
baseurl=https://mirrors.tuna.tsinghua.edu.cn/rocky/$releasever/BaseOS/$basearch/os/
gpgcheck=1
enabled=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-Rocky-9

[appstream]
name=Rocky Linux $releasever - AppStream
baseurl=https://mirrors.tuna.tsinghua.edu.cn/rocky/$releasever/AppStream/$basearch/os/
gpgcheck=1
enabled=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-Rocky-9

[extras]
name=Rocky Linux $releasever - Extras
baseurl=https://mirrors.tuna.tsinghua.edu.cn/rocky/$releasever/extras/$basearch/os/
gpgcheck=1
enabled=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-Rocky-9

[epel]
name=EPEL for Rocky Linux $releasever
baseurl=https://mirrors.tuna.tsinghua.edu.cn/epel/$releasever/Everything/$basearch/
gpgcheck=1
enabled=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-$releasever
EOF

sudo dnf makecache
```

### 4.3 基础软件和更新

```bash
# 全系统升级
sudo dnf upgrade -y

# 安装 EPEL
sudo dnf install epel-release -y

# 安装基础工具
sudo dnf install -y \
    vim git curl wget \
    htop btop tmux \
    net-tools iproute \
    unzip p7zip \
    man-db man-pages \
    bash-completion \
    rsync

# 安装开发工具
sudo dnf groupinstall "Development Tools" -y
```

### 4.4 网络配置

```bash
# 查看网络接口
nmcli device status

# 设置静态 IP（NetworkManager）
sudo nmcli connection modify eth0 \
    ipv4.method manual \
    ipv4.addresses "192.168.1.100/24" \
    ipv4.gateway "192.168.1.1" \
    ipv4.dns "8.8.8.8 1.1.1.1" \
    connection.autoconnect yes

# 应用
sudo nmcli connection up eth0

# 传统方式（/etc/sysconfig/network-scripts/）
# RHEL 7: /etc/sysconfig/network-scripts/ifcfg-eth0
# RHEL 8+: 推荐使用 nmcli 或 nmtui

# 设置主机名
sudo hostnamectl set-hostname server01.example.com
```

### 4.5 时区和语言

```bash
# 设置时区
sudo timedatectl set-timezone Asia/Shanghai
sudo timedatectl set-ntp true

# 验证
timedatectl status

# 设置系统语言（建议英文）
sudo localectl set-locale LANG=en_US.UTF-8

# 如果需要中文环境
# sudo localectl set-locale LANG=zh_CN.UTF-8
```

---

## 5. 关键系统服务

### 5.1 firewalld 防火墙

```bash
# 启动 firewalld
sudo systemctl enable --now firewalld

# 开放 SSH
sudo firewall-cmd --add-service=ssh --permanent

# 开放 HTTP/HTTPS
sudo firewall-cmd --add-service=http --add-service=https --permanent

# 重新加载规则
sudo firewall-cmd --reload

# 查看当前规则
sudo firewall-cmd --list-all

# 详细配置见 [[../redhat/05-firewalld与nmcli|firewalld 与 nmcli]]
```

### 5.2 SELinux

```bash
# RHEL 默认强制启用 SELinux
# 检查状态
getenforce
sestatus

# 临时切换模式
sudo setenforce 0           # permissive
sudo setenforce 1           # enforcing

# 永久配置
sudo vim /etc/selinux/config
# SELINUX=enforcing

# 详细配置见 [[../redhat/04-SELinux深入|SELinux 深入]]
```

### 5.3 tuned 性能优化

```bash
# 安装并启动 tuned
sudo dnf install tuned -y
sudo systemctl enable --now tuned

# 查看当前 profile
tuned-adm active

# 列出所有 profile
tuned-adm list

# 选择 profile
sudo tuned-adm profile throughput-performance   # 吞吐量优先
sudo tuned-adm profile latency-performance      # 低延迟
sudo tuned-adm profile virtual-guest            # 虚拟机客户机
sudo tuned-adm profile virtual-host             # 虚拟机宿主机

# 推荐配置
sudo tuned-adm recommend
sudo tuned-adm auto_profile
```

---

## 6. Cockpit —— Web 管理界面

### 6.1 安装与访问

```bash
# 安装 Cockpit
sudo dnf install cockpit -y

# 启用
sudo systemctl enable --now cockpit.socket

# 防火墙放行（通常已经自动配置）
sudo firewall-cmd --add-service=cockpit --permanent
sudo firewall-cmd --reload

# 访问：https://server-ip:9090
# 使用系统用户登录
```

### 6.2 Cockpit 附加组件

```bash
# 安装扩展模块
sudo dnf install cockpit-storaged          # 存储管理
sudo dnf install cockpit-networkmanager    # 网络管理
sudo dnf install cockpit-packagekit        # 软件管理
sudo dnf install cockpit-machines          # 虚拟机管理
sudo dnf install cockpit-podman            # 容器管理
sudo dnf install cockpit-session-recording # 会话录制
sudo dnf install cockpit-composer          # 镜像构建

# 重启 Cockpit
sudo systemctl restart cockpit
```

---

## 7. 服务器安全加固

### 7.1 SSH 安全

```bash
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak
sudo vim /etc/ssh/sshd_config
```

```
Port 2222
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2
X11Forwarding no
AllowAgentForwarding no
AllowTcpForwarding no
```

```bash
sudo systemctl restart sshd

# SELinux 允许 SSH 使用非标准端口
sudo semanage port -a -t ssh_port_t -p tcp 2222
```

### 7.2 自动安全更新

```bash
# 安装 dnf-automatic
sudo dnf install dnf-automatic -y

# 配置
sudo vim /etc/dnf/automatic.conf
```

```
[commands]
upgrade_type = security           # 仅安全更新
# upgrade_type = default          # 所有更新

random_sleep = 300
download_updates = yes
apply_updates = yes

[emitters]
emit_via = motd                   # 登录时提示
# emit_via = email                # 邮件通知
```

```bash
# 启用定时器
sudo systemctl enable --now dnf-automatic.timer
sudo systemctl list-timers | grep dnf
```

### 7.3 审计与日志

```bash
# auditd — 审计子系统
sudo systemctl enable --now auditd

# 查看审计规则
sudo auditctl -l

# 添加审计规则
sudo auditctl -w /etc/passwd -p wa -k passwd_changes
sudo auditctl -w /etc/shadow -p wa -k shadow_changes

# 永久规则写入 /etc/audit/rules.d/
sudo tee /etc/audit/rules.d/custom.rules << 'EOF'
-w /etc/passwd -p wa -k passwd_changes
-w /etc/shadow -p wa -k shadow_changes
-w /etc/sudoers -p wa -k sudoers_changes
-w /etc/ssh/sshd_config -p wa -k sshd_changes
EOF

sudo systemctl restart auditd

# 查看审计日志
sudo ausearch -k passwd_changes
sudo aureport -au             # 认证报告
```

### 7.4 aide 文件完整性检查

```bash
sudo dnf install aide -y

# 初始化数据库
sudo aide --init
sudo mv /var/lib/aide/aide.db.new.gz /var/lib/aide/aide.db.gz

# 执行检查
sudo aide --check

# 更新数据库（已知变更后）
sudo aide --update
```

---

## 8. RHEL 特有工具

### 8.1 subscription-manager

```bash
# 注册
sudo subscription-manager register

# 查看状态
sudo subscription-manager status

# 查看订阅产品
sudo subscription-manager list --available
sudo subscription-manager list --consumed

# 启用仓库
sudo subscription-manager repos --list
sudo subscription-manager repos --enable rhel-9-for-x86_64-supplementary-rpms
```

### 8.2 Insights（系统分析）

```bash
# 安装 Red Hat Insights
sudo dnf install insights-client -y

# 注册
sudo insights-client --register

# 查看系统状态
sudo insights-client --status
```

### 8.3 Red Hat Support Tool

```bash
# 安装支持工具
sudo dnf install redhat-support-tool -y

# 搜索知识库
redhat-support-tool search "kernel panic"

# 查看已知解决方案
redhat-support-tool getsolution 123456

# 诊断系统
redhat-support-tool analyze
```

---

## 9. 虚拟化支持

```bash
# 安装 KVM 虚拟化
sudo dnf groupinstall "Virtualization Host" -y
sudo systemctl enable --now libvirtd

# 安装 Cockpit 虚拟机插件
sudo dnf install cockpit-machines -y
sudo systemctl restart cockpit

# 安装容器支持
sudo dnf install podman buildah skopeo -y
```

---

## 10. 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `This system is not registered` | RHEL 未注册 | 注册或使用 Rocky/AlmaLinux |
| 安装后没有网络 | NetworkManager 未启用 | `nmcli device status` |
| SELinux 阻挡服务 | 安全上下文错误 | `sudo sealert -a /var/log/audit/audit.log` |
| Cockpit 无法访问 | 防火墙未开放 | `sudo firewall-cmd --add-service=cockpit` |
| 找不到包 | EPEL 未安装 | `sudo dnf install epel-release` |
| 依赖冲突 | 模块流冲突 | `dnf module list` 检查 |

---

## 11. 相关资源

- Red Hat 官方文档: https://access.redhat.com/documentation/
- Rocky Linux 文档: https://docs.rockylinux.org/
- AlmaLinux Wiki: https://wiki.almalinux.org/
- Fedora 文档: https://docs.fedoraproject.org/
- [[../redhat/01-dnf-yum包管理|DNF/YUM 包管理]]
- [[../redhat/03-RPM打包与仓库|RPM 打包与仓库]]
- [[../redhat/04-SELinux深入|SELinux 深入]]
- [[../redhat/05-firewalld与nmcli|firewalld 与 nmcli]]
- [[../debian/02-Debian安装与服务器配置|Debian 安装与服务器配置]]
