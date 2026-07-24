# DNF/YUM 包管理完整参考

> DNF (Dandified YUM) 是 RHEL 8+、Fedora、CentOS Stream、Rocky Linux 和 AlmaLinux 的默认包管理器。yum 在 RHEL 7 及更早版本中使用。本章是完整的 dnf/yum 参考手册，覆盖软件仓库、EPEL、RPM Fusion、DNF 模块和 COPR。

---

## 1. 资源链接

| 资源 | 链接 |
|------|------|
| Red Hat 官网 | https://www.redhat.com/ |
| Red Hat 开发者订阅（免费） | https://developers.redhat.com/ |
| Fedora 官网 | https://getfedora.org/ |
| CentOS Stream 官网 | https://www.centos.org/ |
| Rocky Linux 官网 | https://rockylinux.org/ |
| AlmaLinux 官网 | https://almalinux.org/ |
| EPEL 项目 | https://docs.fedoraproject.org/en-US/epel/ |
| RPM Fusion | https://rpmfusion.org/ |
| 清华大学 CentOS 镜像 | https://mirrors.tuna.tsinghua.edu.cn/centos/ |
| 清华大学 Fedora 镜像 | https://mirrors.tuna.tsinghua.edu.cn/fedora/ |
| 中科大镜像 | https://mirrors.ustc.edu.cn/centos/ |
| 中科大 Fedora 镜像 | https://mirrors.ustc.edu.cn/fedora/ |
| 阿里云镜像 | https://mirrors.aliyun.com/centos/ |

---

## 2. RHEL 生态发行版对照

| 发行版 | 类型 | 包管理 | 免费 | 说明 |
|--------|------|--------|------|------|
| RHEL | 企业付费 | dnf | 16台免费（开发者订阅） | Red Hat 官方企业版 |
| CentOS Stream | 滚动预览 | dnf | ✓ | RHEL 上游开发分支 |
| Rocky Linux | 社区稳定 | dnf | ✓ | RHEL 兼容克隆（CentOS 继任者） |
| AlmaLinux | 社区稳定 | dnf | ✓ | RHEL 兼容克隆 |
| Fedora | 社区创新 | dnf | ✓ | 新技术试验场 |
| Oracle Linux | 企业 | dnf | ✓ | Oracle 发行的 RHEL 兼容版 |

---

## 3. dnf 命令完整参考

### 3.1 基础操作

```bash
# 安装包
sudo dnf install pkgname

# 安装本地 RPM 包
sudo dnf install ./package.rpm

# 搜索包
dnf search keyword

# 包信息
dnf info pkgname

# 列出包的依赖
dnf deplist pkgname

# 列出提供某个文件的包
dnf provides /path/to/file
dnf whatprovides '*/libfoo.so'

# 更新包列表
sudo dnf check-update

# 升级所有包
sudo dnf upgrade

# 全系统升级（可能删除废弃包）
sudo dnf distro-sync

# 删除包
sudo dnf remove pkgname

# 自动删除不需要的依赖
sudo dnf autoremove

# 清除缓存
sudo dnf clean all
sudo dnf clean packages
sudo dnf clean metadata
sudo dnf clean dbcache
```

### 3.2 查询操作

```bash
# 列出所有已安装的包
dnf list installed

# 列出仓库中可用的包
dnf list available

# 列出可升级的包
dnf list updates

# 列出所有包（已安装 + 可用）
dnf list all

# 查看包的详细信息
dnf info pkgname

# 按仓库列出
dnf repository-packages epel list

# 按包组列出
dnf group list
dnf group info "Development Tools"

# 搜索已安装包中的文件
rpm -ql pkgname

# 搜索哪个包拥有某个文件
rpm -qf /usr/bin/ls
```

### 3.3 包组管理

```bash
# 列出所有包组
dnf group list
dnf group list --hidden

# 查看包组描述
dnf group info "Server with GUI"

# 安装包组
sudo dnf group install "Development Tools"
sudo dnf group install "Server with GUI"

# 删除包组
sudo dnf group remove "Server with GUI"

# 升级包组
sudo dnf group upgrade "Development Tools"
```

### 3.4 历史/事务管理

```bash
# 查看事务历史
dnf history
dnf history list

# 查看特定事务详情
dnf history info 42

# 撤销某个事务（回滚包状态）
sudo dnf history undo 42

# 重做某个事务
sudo dnf history redo 42

# 回滚到某个事务之前的状态
sudo dnf history rollback 42

# 查看最后一次 dnf 事务的信息
dnf history info last
```

### 3.5 DNF 配置

```ini
# /etc/dnf/dnf.conf
[main]
gpgcheck=1                       # 启用 GPG 检查
installonly_limit=3              # 保留的内核版本数
clean_requirements_on_remove=True # 删除时清理依赖
best=True                        # 尽量安装最新版本
skip_if_unavailable=True         # 遇到不可用仓库跳过

# 加速下载（并行下载）
max_parallel_downloads=10

# 最快镜像
fastestmirror=True

# 排除某些包的升级
exclude=kernel* nvidia*

# 代理
proxy=http://proxy.example.com:8080

# 缓存设置
keepcache=True                   # 保留下载的包
cachedir=/var/cache/dnf
```

### 3.6 仓库管理命令

```bash
# 列出所有启用的仓库
dnf repolist

# 列出所有仓库（包括禁用的）
dnf repolist all

# 查看仓库详细信息
dnf repoinfo

# 启用/禁用仓库
sudo dnf config-manager --enable powertools
sudo dnf config-manager --disable powertools

# 添加仓库
sudo dnf config-manager --add-repo https://example.com/repo.repo

# 从特定仓库安装
sudo dnf --enablerepo=epel install pkgname
sudo dnf --disablerepo=* --enablerepo=epel install pkgname
```

---

## 4. yum vs dnf 对比

| 操作 | yum (RHEL 7-) | dnf (RHEL 8+/Fedora) |
|------|---------------|----------------------|
| 安装 | `yum install` | `dnf install` |
| 搜索 | `yum search` | `dnf search` |
| 删除 | `yum remove` | `dnf remove` |
| 包信息 | `yum info` | `dnf info` |
| 历史 | `yum history` | `dnf history` |
| 仓库 | `yum-config-manager` | `dnf config-manager` |
| 依赖解析 | sat solver | libsolv (更快) |
| Python | Python 2 | Python 3 |
| 并行下载 | 不支持 | 支持 |
| 自动删除 | `yum autoremove` | `dnf autoremove` |

```bash
# 在 RHEL 7/CentOS 7 上安装 dnf（可选）
sudo yum install epel-release
sudo yum install dnf
```

---

## 5. EPEL (Extra Packages for Enterprise Linux)

### 5.1 安装 EPEL

```bash
# RHEL 9 / Rocky Linux 9 / AlmaLinux 9
sudo dnf install epel-release
# 或手动：
# sudo dnf install https://dl.fedoraproject.org/pub/epel/epel-release-latest-9.noarch.rpm

# RHEL 8 / Rocky 8 / AlmaLinux 8
sudo dnf install epel-release
# sudo dnf install https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm

# RHEL 7 / CentOS 7
sudo yum install epel-release
# sudo yum install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm

# 验证
dnf repolist | grep epel
```

### 5.2 EPEL Playground（EPEL Next）

```bash
# EPEL Next：包含正在测试中、即将推送的包
sudo dnf install epel-next-release

# PyPi → RPM 生成工具
sudo dnf install epel-rpm-macros
```

### 5.3 EPEL 包安装示例

```bash
# EPEL 中常用的企业级服务器软件
sudo dnf --enablerepo=epel install \
    htop btop neofetch \
    tmux jq ripgrep fd-find \
    certbot python3-certbot-nginx \
    fail2ban wireguard-tools
```

---

## 6. RPM Fusion (第三方多媒体/驱动仓库)

### 6.1 安装 RPM Fusion

```bash
# Fedora
sudo dnf install \
    https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm \
    https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm

# RHEL 9 / Rocky 9 / AlmaLinux 9（需先安装 EPEL）
sudo dnf install epel-release
sudo dnf install \
    https://mirrors.rpmfusion.org/free/el/rpmfusion-free-release-9.noarch.rpm \
    https://mirrors.rpmfusion.org/nonfree/el/rpmfusion-nonfree-release-9.noarch.rpm

# 验证
dnf repolist | grep rpmfusion
```

### 6.2 用途

```bash
# free 仓库：开源但有专利/法律问题的软件
# - ffmpeg, gstreamer-plugins-*, vlc
sudo dnf install ffmpeg vlc

# nonfree 仓库：专有软件
# - nvidia-driver, steam
sudo dnf install akmod-nvidia xorg-x11-drv-nvidia-cuda
```

---

## 7. DNF 模块与流 (Modules & Streams)

### 7.1 概念

```
RHEL 8+ 引入了模块化：
同一个软件包有多个独立的"流（Stream）"版本
如：Python 3.9 Stream 和 Python 3.12 Stream 可以并存

模块 = 一组 RPM 包 + 版本流 + 配置文件（profile）
```

### 7.2 模块操作

```bash
# 列出所有模块
dnf module list

# 列出特定模块的可用流
dnf module list python
dnf module list nodejs

# 查看模块详情
dnf module info nodejs

# 启用模块流（但不安�）
sudo dnf module enable nodejs:20

# 安装特定模块流
sudo dnf module install nodejs:20/common
# 或先启用再安装
sudo dnf module enable nodejs:20
sudo dnf install nodejs

# 切换模块流（重要操作）
sudo dnf module reset nodejs
sudo dnf module install nodejs:22

# 禁用模块
sudo dnf module disable nodejs:20

# 删除模块
sudo dnf module remove nodejs
```

### 7.3 模块 profile（配置文件）

```bash
# 查看模块的可用 profile
dnf module info nodejs:20

# Profile 常见类型：
# common/default  — 通用安装
# minimal         — 最小安装
# development     — 开发工具
# server          — 服务器组件

# 安装特定 profile
sudo dnf module install nodejs:20/development
```

### 7.4 常见模块示例

```bash
# Python
sudo dnf module install python39
sudo dnf module install python312

# Node.js
sudo dnf module install nodejs:20

# PostgreSQL
sudo dnf module install postgresql:16/server

# PHP
sudo dnf module install php:8.2

# Ruby
sudo dnf module install ruby:3.3

# Go
sudo dnf module install go-toolset
```

---

## 8. COPR (Cool Other Package Repo)

### 8.1 COPR 概述

```
COPR 类似 Ubuntu PPA，是 Fedora 生态的个人包仓库
网址：https://copr.fedorainfracloud.org/
任何人可以创建 COPR 仓库分享自己构建的包
```

### 8.2 使用 COPR 仓库

```bash
# 安装 copr 插件
sudo dnf install dnf-plugins-core

# 启用 COPR 仓库
sudo dnf copr enable username/project-name

# 示例：启用一些热门 COPR
sudo dnf copr enable phracek/PyCharm
sudo dnf copr enable agriffis/neovim-nightly

# 列出已启用的 COPR
dnf copr list

# 禁用 COPR
sudo dnf copr disable username/project-name

# 删除 COPR
sudo dnf copr remove username/project-name
```

### 8.3 热门 COPR 示例

```bash
# Neovim nightly
sudo dnf copr enable agriffis/neovim-nightly
sudo dnf install neovim

# WezTerm
sudo dnf copr enable wezfurlong/wezterm
sudo dnf install wezterm

# Kitty
sudo dnf copr enable mavit/kitty
sudo dnf install kitty

# Zsh
sudo dnf copr enable mavit/zsh-sydefault
sudo dnf install zsh

# Rclone
sudo dnf copr enable elxreno/rclone-browser
```

---

## 9. 仓库文件格式

### 9.1 .repo 文件

```ini
# /etc/yum.repos.d/custom.repo
[custom-repo]
name=Custom Repository for RHEL $releasever
baseurl=https://repo.example.com/rhel/$releasever/$basearch/
# 或使用 mirrorlist:
# mirrorlist=https://repo.example.com/mirrorlist
enabled=1
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-custom
# 优先级（需要 yum-plugin-priorities）
priority=10
# 排除的包
# exclude=kernel*
# 包含的包
# includepkgs=php*
# 代理
# proxy=http://proxy.example.com:8080
```

### 9.2 中国镜像 .repo 配置

```bash
# Rocky Linux 9 清华镜像
# /etc/yum.repos.d/rocky-mirrors.repo
sudo tee /etc/yum.repos.d/rocky-mirrors.repo << 'EOF'
[rocky-baseos]
name=Rocky Linux $releasever - BaseOS
baseurl=https://mirrors.tuna.tsinghua.edu.cn/rocky/$releasever/BaseOS/$basearch/os/
gpgcheck=1
enabled=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-Rocky-9

[rocky-appstream]
name=Rocky Linux $releasever - AppStream
baseurl=https://mirrors.tuna.tsinghua.edu.cn/rocky/$releasever/AppStream/$basearch/os/
gpgcheck=1
enabled=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-Rocky-9

[rocky-extras]
name=Rocky Linux $releasever - Extras
baseurl=https://mirrors.tuna.tsinghua.edu.cn/rocky/$releasever/extras/$basearch/os/
gpgcheck=1
enabled=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-Rocky-9
EOF

# 同样用中科大镜像替换：
# baseurl=https://mirrors.ustc.edu.cn/rocky/
```

### 9.3 $variables 变量说明

| 变量 | 说明 |
|------|------|
| `$releasever` | 发行版大版本号（如 9） |
| `$basearch` | 基础架构（如 x86_64、aarch64） |
| `$arch` | 完整架构 |
| `$releasever_major` | 主版本号 |
| `$stream` | CentOS Stream 的流名 |

---

## 10. 包缓存管理

```bash
# 查看缓存位置
ls /var/cache/dnf/

# 查看缓存使用情况
du -sh /var/cache/dnf/

# 清理所有缓存
sudo dnf clean all

# 保留缓存（允许离线安装）
# /etc/dnf/dnf.conf
# keepcache=True

# 从缓存安装
sudo dnf -C install pkgname      # 仅使用缓存
```

---

## 11. dnf 插件

```bash
# 安装 dnf 插件核心包
sudo dnf install dnf-plugins-core

# 常用插件：

# versionlock — 锁定包的版本
sudo dnf install python3-dnf-plugins-extras-versionlock
sudo dnf versionlock add pkgname
dnf versionlock list
sudo dnf versionlock delete pkgname

# system-upgrade — Fedora 版本升级
sudo dnf system-upgrade download --releasever=40
sudo dnf system-upgrade reboot

# builddep — 安装构建依赖
sudo dnf builddep pkgname

# download — 下载包而不安装
sudo dnf download pkgname
dnf download --source pkgname

# needs-restarting — 需要重启的服务
dnf needs-restarting
dnf needs-restarting -s      # 列出需要重启的服务
```

---

## 12. 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `Error: GPG check FAILED` | 仓库 GPG 密钥缺失 | `sudo rpm --import /etc/pki/rpm-gpg/KEY` |
| 仓库元数据过期 | 网络不同步 | `sudo dnf clean metadata && sudo dnf makecache` |
| 依赖解析失败 | 仓库冲突 | `sudo dnf --allowerasing install pkg` |
| 包受保护无法删除 | 系统关键包 | 检查是否是 `protected_packages` 中的包 |
| `/var/cache/dnf` 过大 | 长期未清理 | `sudo dnf clean packages` |

---

## 13. 相关资源

- DNF 文档: https://dnf.readthedocs.io/
- Fedora Wiki: https://fedoraproject.org/wiki/
- EPEL 文档: https://docs.fedoraproject.org/en-US/epel/
- COPR 平台: https://copr.fedorainfracloud.org/
- RPM Fusion: https://rpmfusion.org/
- [[../redhat/02-RHEL-CentOS安装与配置|RHEL 安装与配置]]
- [[../redhat/03-RPM打包与仓库|RPM 打包与仓库]]
- [[../redhat/04-SELinux深入|SELinux 深入]]
- [[../debian/01-apt包管理|APT 包管理（Debian）]]
