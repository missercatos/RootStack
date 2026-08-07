# Linux 百科全书式教程

> **Linux 不仅仅是一个操作系统，它是现代计算世界的基石。** 从你手中的 Android 手机，到全球 90% 以上的云服务器，从所有 Top500 超级计算机到嵌入式 IoT 设备——Linux 无处不在。本教程旨在提供一份系统、深入、面向中文读者的 Linux 百科全书。

---

## 什么是 Linux？

Linux 是一个类 Unix 的开源操作系统内核，由芬兰赫尔辛基大学学生 **Linus Torvalds** 于 1991 年首次发布。搭配 GNU 项目的用户空间工具，构成了完整的 **GNU/Linux 操作系统**。

在三十余年的发展中，Linux 从一个"个人小爱好"成长为全球软件开发史上最成功的协作项目之一，超过 20000 名开发者向内核贡献代码，驱动着数字世界的基础设施。

### 为什么每个程序员都应该学习 Linux？

1. **服务器霸主**：Linux 运行着互联网 90% 以上的服务器。无论你做后端开发、DevOps、运维、大数据还是 AI，你必然在 Linux 上部署代码。
2. **一切皆可定制**：不像 macOS 和 Windows 的黑盒化，Linux 让你能从内核模块到桌面环境全程掌控系统行为。
3. **理解计算本质**：学习 Linux 的过程，就是理解进程、内存、文件、网络这些计算机核心概念如何被实现的过程。
4. **最高的就业相关性**：Linux 是云计算（AWS、GCP、Azure、阿里云）的底层，是企业基础设施的标配。

---

## 外部资源

### 必读的 Linux 项目与社区

| 资源 | 链接 | 说明 |
|------|------|------|
| **Linux 内核源码** | [github.com/torvalds/linux](https://github.com/torvalds/linux) | 这是全世界最重要的项目之一。Linus Torvalds 维护的 Linux 内核官方主线仓库，包含数千万行 C 代码，驱动全球数十亿台设备 |
| **内核档案馆** | [kernel.org](https://kernel.org) | Linux 内核的官方发布站点，所有内核版本的源码均可在此获取 |
| **Arch Wiki** | [wiki.archlinux.org](https://wiki.archlinux.org/) | Arch Wiki 几乎可以找到所有 Linux 问题的解决方案，不仅限于 Arch 用户。这是 Linux 圈公认的最佳技术文档，涵盖从内核参数到桌面配置的全部领域 |

### 推荐阅读

- *The Linux Programming Interface* (Michael Kerrisk, No Starch Press) — Linux 系统编程权威参考，man-pages 维护者所著
- *Advanced Programming in the UNIX Environment* (W. Richard Stevens) — Unix 系统编程的经典之作
- *Understanding the Linux Kernel* (O'Reilly) — 深入理解内核机制的参考书
- *How Linux Works* (Brian Ward) — 系统管理员视角的 Linux 内幕

---

## 教程结构总览

本教程按知识领域划分为六个部分，共 **63 章**（主教程）+ 发行版专项内容，总计超过 80 篇文档。

### 第一部分：入门篇（01-06）

理解和安装 Linux，建立基本功。

| 章节 | 标题 | 核心内容 |
|------|------|---------|
| [[01-Linux概述与历史]] | Linux 概述与历史 | Unix 遗产、Linus 的故事、开源运动、GNU GPL 协议 |
| [[02-多发行版安装指南]] | 多发行版安装指南 | Debian/Arch/Fedora/NixOS 安装流程、分区、引导 |
| [[03-FHS文件系统层次标准]] | FHS 文件系统层次标准 | `/bin`, `/etc`, `/var`, `/usr` 等目录的结构与意义 |
| [[04-文件与目录管理]] | 文件与目录管理 | `ls`, `cp`, `mv`, `rm`, `mkdir`, `find`, 通配符、权限初步 |
| [[05-文本编辑器(Vim+Nano)]] | 文本编辑器 (Vim + Nano) | Vim 模态编辑、Nano 新手友好、配置文件编辑实践 |
| [[06-命令行基础与Shell入门]] | 命令行基础与 Shell 入门 | Bash 基础、环境变量、别名、补全、作业控制 |

### 第二部分：运维基础（07-15）

系统管理的核心技能。

| 章节 | 标题 | 核心内容 |
|------|------|---------|
| [[07-用户与权限管理]] | 用户与权限管理 | UID/GID、文件权限、ACL、sudo、PAM 认证 |
| [[08-进程管理]] | 进程管理 | `ps`, `top`, `htop`, `kill`, signal, nice, 前后台切换 |
| [[09-systemd服务管理]] | systemd 服务管理 | Unit 文件、timer、socket、journalctl、systemd 启动流程 |
| [[10-存储管理与磁盘操作]] | 存储管理与磁盘操作 | 分区（fdisk/gdisk）、格式化、挂载、fstab、LVM |
| [[11-网络配置基础]] | 网络配置基础 | IP 地址、路由、DNS、NetworkManager、systemd-networkd |
| [[12-软件包管理通识]] | 软件包管理通识 | 包管理概念、各发行版对比、GPG 验证、AUR/PPA/Copr |
| [[13-计划任务与自动化]] | 计划任务与自动化 | cron、systemd timer、at、anacron |
| [[14-日志系统]] | 日志系统 | journald、rsyslog、logrotate、集中日志分析 |
| [[15-备份与恢复]] | 备份与恢复 | rsync、tar、dd、BorgBackup、快照恢复、灾难恢复策略 |

### 第三部分：Shell 编程与自动化（16-20）

从入门到精通 Shell 脚本。

| 章节 | 标题 | 核心内容 |
|------|------|---------|
| [[16-Bash编程基础]] | Bash 编程基础 | 变量、条件、循环、函数、参数、退出码 |
| [[17-Bash编程进阶]] | Bash 编程进阶 | 数组、关联数组、trap、set 选项、调试、子Shell |
| [[18-正则与文本处理三剑客]] | 正则与文本处理三剑客 | grep/sed/awk 深度，正则表达式语法 |
| [[19-IO重定向与管道深入]] | I/O 重定向与管道深入 | stdin/stdout/stderr、Here Document、进程替换、命名管道 |
| [[20-Shell脚本实战]] | Shell 脚本实战 | 日志分析脚本、监控脚本、备份脚本、批量管理 |

### 第四部分：服务与安全（21-26）

对外提供服务和保护系统的完整技能。

| 章节 | 标题 | 核心内容 |
|------|------|---------|
| [[21-SSH远程管理]] | SSH 远程管理 | SSH 密钥、配置、隧道、端口转发、sshd 加固 |
| [[22-防火墙与安全]] | 防火墙与安全 | iptables/nftables/firewalld/ufw、DDoS 防护、Fail2ban |
| [[23-DNS与域名系统]] | DNS 与域名系统 | 递归/权威 DNS、BIND、CoreDNS、DNS-over-HTTPS |
| [[24-Web服务器(Nginx+Apache)]] | Web 服务器 (Nginx + Apache) | 虚拟主机、SSL/TLS、反向代理、PHP-FPM、静态优化 |
| [[25-数据库管理]] | 数据库管理 | PostgreSQL/MySQL 安装、用户权限、备份恢复、基础调优 |
| [[26-系统安全加固与审计]] | 系统安全加固与审计 | 最小权限、审计日志、入侵检测、MFA、内核参数加固 |

### 第五部分：操作系统原理（27-35）

计算机科学理论基础——理解操作系统本身。

| 章节 | 标题 | 核心内容 |
|------|------|---------|
| [[27-操作系统概述与结构]] | 操作系统概述与结构 | OS 层次结构、系统调用机制、内核架构、中断处理 |
| [[28-进程与线程]] | 进程与线程 | PCB、上下文切换、多线程模型、用户线程 vs 内核线程 |
| [[29-进程同步与互斥]] | 进程同步与互斥 | 临界区、信号量、互斥锁、条件变量、管程 |
| [[30-死锁]] | 死锁 | 死锁四条件、预防、避免（银行家算法）、检测与解除 |
| [[31-处理机调度]] | 处理机调度 | 调度算法（FCFS、SJF、RR、多级队列）、CFS、实时调度 |
| [[32-存储管理]] | 存储管理 | 分区分配、段式存储、页式存储、内部/外部碎片 |
| [[33-虚拟存储与页面置换]] | 虚拟存储与页面置换 | 请求调页、FIFO/LRU/Clock 置换算法、工作集 |
| [[34-文件系统设计]] | 文件系统设计 | 文件结构、目录实现、空闲空间管理、一致性检查 |
| [[35-I-O设备管理]] | I/O 设备管理 | I/O 控制方式、缓冲/缓存、SPOOLing、磁盘调度 |

### 第六部分：系统架构与高级主题（36-63）

从内核到用户态，从存储到追踪——深入 Linux 现代特性。

| 章节 | 标题 | 核心内容 |
|------|------|---------|
| [[36-Linux内核基础与模块]] | Linux 内核基础与模块 | 内核模块加载/卸载、编译内核、内核参数、sysctl |
| [[37-系统调优与性能分析]] | 系统调优与性能分析 | perf、火焰图、sar、vmstat、perf top |
| [[38-引导流程与GRUB]] | 引导流程与 GRUB | BIOS/UEFI、Bootloader、内核启动参数、initramfs |
| [[39-内存管理深入]] | 内存管理深入 | Buddy 算法、Slab 分配器、页面回收、内存压缩、HugePages |
| [[40-文件系统深入]] | 文件系统深入 | VFS 层、ext4、XFS、Btrfs、ZFS、超级块、日志 |
| [[41-硬件驱动与设备管理]] | 硬件驱动与设备管理 | 设备树、udev、sysfs、驱动加载机制 |
| [[42-压缩与归档工具大全]] | 压缩与归档工具大全 | tar, gz, xz, zstd, 7z, rar, zip 详解 |
| [[43-系统错误排查与日志分析]] | 系统错误排查与日志分析 | 故障排查方法论、日志解析、Troubleshooting |
| [[44-容器技术]] | 容器技术 | Docker/Podman、Dockerfile、Compose、注册表、BuildKit |
| [[45-容器编排与K8s入门]] | 容器编排与 K8s 入门 | Pod, Deployment, Service, Ingress, Helm (基础) |
| [[46-不可变系统]] | 不可变系统 | Fedora Silverblue, openSUSE MicroOS, NixOS, SteamOS |
| [[47-FUSE与虚拟文件系统]] | FUSE 与虚拟文件系统 | 用户态文件系统、S3FS、SSHFS、Rclone、自定义 VFS |
| [[48-BPF与系统追踪]] | BPF 与系统追踪 | eBPF 架构、bpftrace、可观测性 |
| [[49-Wayland深入指南]] | Wayland 深入指南 | 协议、合成器、客户端、XWayland |
| [[50-PipeWire与音频系统]] | PipeWire 与音频系统 | 替代 PulseAudio/JACK，统一多媒体框架 |
| [[51-io_uring与异步IO]] | io_uring 与异步 I/O | 高性能异步 I/O 接口，超越 AIO、epoll |
| [[52-Device Mapper与存储栈]] | Device Mapper 与存储栈 | dm-crypt (LUKS), dm-thin (LVM), dm-verity, dm-integrity |
| [[53-终端常用工具大全]] | 终端常用工具大全 | fd, ripgrep, bat, tldr, jq, fzf, zoxide, lsd, btop, tmux |

### 第七部分：DevOps 与运维实战（54-62）

企业级基础设施自动化与运维实战。

| 章节 | 标题 | 核心内容 |
|------|------|---------|
| [[54-服务器初始化与基线配置]] | 服务器初始化与基线配置 | cloud-init, Kickstart, Preseed, 安全基线 |
| [[55-Nginx反向代理与负载均衡]] | Nginx 反向代理与负载均衡 | upstream、WAF、限流、缓存、HTTP/2、HTTP/3 |
| [[56-数据库运维(主从+备份+优化)]] | 数据库运维（主从 + 备份 + 优化） | 主从复制、连接池、慢查询、备份策略、高可用 |
| [[57-DNS服务器搭建]] | DNS 服务器搭建 | BIND 权威 + 递归、区域传输、DNSSEC |
| [[58-监控系统(Prometheus+Grafana)]] | 监控系统 (Prometheus + Grafana) | 指标采集、PromQL、仪表板、告警 |
| [[59-CI-CD基础]] | CI/CD 基础 | GitLab CI、GitHub Actions、Jenkins 入门 |
| [[60-Ansible与配置管理]] | Ansible 与配置管理 | 清单、Playbook、角色、变量编排 |
| [[61-高可用与集群]] | 高可用与集群 | Keepalived + HAProxy、故障转移、PG 高可用集群 |
| [[62-自定义系统打包与分发]] | 自定义系统打包与分发 | 制作自定义 ISO、PXE 批量部署 |
| [[63-包管理器崩溃恢复与驱动管理通用指南]] | 包管理器崩溃恢复与驱动管理 | 跨发行版的包管理器恢复、ICU 库修复、DKMS 故障处理、滚动更新预防 |

### 发行版专项内容

按发行版划分的深度内容，涵盖各发行版的独有特性和最佳实践。

| 发行版 | 目录 | 内容 |
|--------|------|------|
| **Arch Linux** | [[distro/arch/01-安装指南\|Arch 安装]] | 安装指南、pacman 高级、AUR 打包、systemd-homed、深度玩法、自定义系统打包、DIY 平板指南 |
|  | [[distro/arch/desktop/|Arch 桌面]] | [[distro/arch/desktop/01-Niri配置\|Niri 配置]]、[[distro/arch/desktop/02-Hyprland配置\|Hyprland 配置]]、[[distro/arch/desktop/03-Wayland合成器开发\|Wayland 合成器开发]]、[[distro/arch/desktop/04-终端模拟器配置\|终端模拟器配置]]、[[distro/arch/desktop/05-QuickShell开发\|QuickShell 开发]]、[[distro/arch/desktop/06-显卡驱动配置\|显卡驱动配置]]（含 Legacy 迁移、故障恢复、滚动更新维护）、[[distro/arch/desktop/07-音频驱动配置\|音频驱动配置]]、[[distro/arch/desktop/08-蓝牙驱动配置\|蓝牙驱动配置]]、[[distro/arch/desktop/09-硬件与多媒体配置\|硬件与多媒体配置]]、[[distro/arch/desktop/10-Btrfs高级玩法\|Btrfs 高级玩法]]、[[distro/arch/desktop/11-Steam客户端排障\|Steam 客户端排障]]（CEF 证书信任修复、pressure-vessel 容器注入） |
| **Debian / Ubuntu** | `distro/debian/` | [[distro/debian/01-apt包管理\|apt 包管理]]、[[distro/debian/02-Debian安装与服务器配置\|安装与服务器配置]]、[[distro/debian/03-dpkg与deb打包\|dpkg 与 deb 打包]]、[[distro/debian/04-netplan与NetworkManager\|netplan 与 NetworkManager]] |
| **RHEL / Fedora** | `distro/redhat/` | [[distro/redhat/01-dnf-yum包管理\|dnf/yum 包管理]]、[[distro/redhat/02-RHEL-CentOS安装与配置\|安装与配置]]、[[distro/redhat/03-RPM打包与仓库\|RPM 打包与仓库]]、[[distro/redhat/04-SELinux深入\|SELinux 深入]]、[[distro/redhat/05-firewalld与nmcli\|firewalld 与 nmcli]] |
| **NixOS** | `distro/nix/` | [[distro/nix/01-NixOS安装与声明式配置\|安装与声明式配置]]、[[distro/nix/02-Nix语言与flake\|Nix 语言与 flake]]、[[distro/nix/03-nixpkgs与包管理\|nixpkgs 与包管理]] |

---

## 学习路径推荐

不同目标的读者可以使用不同的学习路径，跳过不相关的内容：

| 路径 | 目标 | 推荐章节顺序 |
|------|------|-------------|
| **Linux 入门者** | 从零到能够日常使用 Linux | 01-06 → 07-15 → 16-20 → 21-26 |
| **系统管理员** | 管理服务器和基础架构 | 01-06 → 07-15 → 16-20 → 36-43 → 54-62 |
| **深入理论** | 理解操作系统原理 | 27-35 → 36-43 → 44-53 |
| **全栈 DevOps** | 容器、Tracing、CI/CD | 01-06 → 21-26 → 44-53 → 54-62 |
| **Arch 用户** | 深度掌握 Arch Linux | 全部主教程 + [[distro/arch/|distro/arch/]] |
| **Debian/Ubuntu 用户** | 深度掌握 Debian 体系 | 全部主教程 + [[distro/debian/|distro/debian/]] |
| **RHEL/Fedora 用户** | 深度掌握红帽体系 | 全部主教程 + [[distro/redhat/|distro/redhat/]] |
| **NixOS 用户** | 深度掌握 Nix 声明式配置 | 全部主教程 + [[distro/nix/|distro/nix/]] |

---

---

## Linux 发行版族谱

理解 Linux 发行版之间的血缘关系，有助于理解其设计理念和技术选型。

```
┌──────────────────────────────────────────────────┐
│                   Linux Kernel                   │
├──────────────────────────────────────────────────┤
│  ┌─────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │ Debian  │  │ Red Hat  │  │  独立/其他       │ │
│  ├─────────┤  ├──────────┤  ├──────────────────┤ │
│  │ Ubuntu  │  │ Fedora   │  │ Arch Linux       │ │
│  │ Linux   │  │ RHEL     │  │ openSUSE         │ │
│  │ Mint    │  │ CentOS   │  │ Gentoo           │ │
│  │ Kali    │  │ Rocky    │  │ Alpine           │ │
│  │ Pop!_OS │  │ Alma     │  │ NixOS            │ │
│  │ Raspbian│  │ Amazon   │  │ Void Linux       │ │
│  └─────────┘  └──────────┘  └──────────────────┘ │
│                                                  │
│  包管理: dpkg/apt  包管理: rpm/dnf  各自不同     │
│  配置: 分散式      配置: 集中式      高度定制    │
└──────────────────────────────────────────────────┘
```

### 三大主流体系的区别

| 维度 | Debian 系 | Red Hat 系 | Arch 系 |
|------|----------|------------|---------|
| 包格式 | `.deb` | `.rpm` | `.pkg.tar.zst` |
| 包管理器 | `apt` / `dpkg` | `dnf` / `rpm` | `pacman` |
| 发布模式 | 定点发布 + LTS | 定点发布 (Fedora) / 企业版 (RHEL) | 滚动发布 |
| 默认防火墙 | ufw（Ubuntu） | firewalld | 手动配置 |
| SELinux/AppArmor | AppArmor | SELinux | 无默认 MAC |
| 配置风格 | 分散（灵活） | 集中（`/etc/sysconfig/`） | 极简（上游默认） |
| 代表场景 | 开发桌面、云服务器 | 企业服务器、认证环境 | 个人定制、学习研究 |
| 包数量 | ~60,000 (Debian) | ~60,000 (Fedora) | ~15,000 (official) + ~80,000 (AUR) |

---

## Linux 系统的主要应用场景

| 场景 | 使用比例 | 代表技术栈 |
|------|---------|-----------|
| **云计算 / 服务器** | 90%+ 市场份额 | KVM, Docker/K8s, Nginx, HAProxy |
| **嵌入式 / IoT** | 绝对主导 | Yocto, Buildroot, OpenWrt, Android (Android 基于 Linux 内核) |
| **超级计算机** | 100% (Top500) | Slurm, MPI, Lustre, InfiniBand |
| **移动设备** | Android 全球数十亿 | Android 内核基于 Linux |
| **桌面** | ~3-4% (Steam Survey) | Wayland/X11, KDE/GNOME, Flatpak/Snap |
| **网络设备** | 路由器、交换机、防火墙 | iptables/nftables, FRR, Quagga, DPDK |
| **汽车 / 工业** | 快速增长 | AGL (Automotive Grade Linux), ROS (机器人) |
| **AI / ML 基础设施** | CUDA 在 Linux 上最优 | PyTorch, TensorFlow, CUDA, ROCm, GPU 驱动 |

---

## 核心概念速览

在学习本教程之前，理解以下核心概念有助于建立整体的 Linux 认知框架：

### 启动过程

```
固件 (UEFI/BIOS) → Bootloader (GRUB/systemd-boot) → 内核 → initramfs → init (systemd) → 用户空间
```

详见 [[38-引导流程与GRUB]]。

### 系统层次

```
应用程序 (Nginx, Docker, GNOME...)
    ↓ 调用
用户空间库 (glibc, libssl, libcurl...)
    ↓ 系统调用
Linux 内核 (进程调度、内存管理、网络栈、文件系统、驱动)
    ↓ 控制
硬件 (CPU、内存、磁盘、网卡、GPU)
```

详见 [[27-操作系统概述与结构]]、[[36-Linux内核基础与模块]]。

### 一切皆文件

Linux 的核心理念之一：磁盘上的文件是文件，目录是文件，进程信息是文件（`/proc`），设备是文件（`/dev`），网络套接字是文件，内核参数也是文件（`/sys`）。

```bash
# 查看内核版本
cat /proc/version

# 查看 CPU 信息
cat /proc/cpuinfo

# 修改内核参数
echo 1 > /proc/sys/net/ipv4/ip_forward

# 写入到磁盘（也是文件操作）
echo "hello" > /tmp/test.txt
```

详见 [[47-FUSE与虚拟文件系统]]、[[40-文件系统深入]]。

---

## 基础命令按使用频率排序

以下是 Linux 日常使用中按频率大致排序的命令。熟练使用前 30 个即可应对 80% 的日常操作。

### 第一梯队（每天必用）

| 命令 | 用途 | 示例 |
|------|------|------|
| `ls` | 列出目录内容 | `ls -lah` |
| `cd` | 切换目录 | `cd /var/log` |
| `pwd` | 显示当前路径 | `pwd` |
| `cat` | 查看文件内容 | `cat /etc/os-release` |
| `less` | 分页查看文件 | `less /var/log/syslog` |
| `grep` | 搜索文本 | `grep -rn "error" .` |
| `find` | 搜索文件 | `find / -name "*.conf"` |
| `echo` | 输出文本 | `echo $PATH` |
| `sudo` | 提权执行 | `sudo systemctl restart nginx` |
| `man` | 帮助手册 | `man ls` |

### 第二梯队（每周会用）

| 命令 | 用途 | 示例 |
|------|------|------|
| `cp` | 复制 | `cp -r src dst` |
| `mv` | 移动/重命名 | `mv old new` |
| `rm` | 删除 | `rm -rf /tmp/junk` |
| `mkdir` | 创建目录 | `mkdir -p a/b/c` |
| `touch` | 创建空文件/更新时间戳 | `touch file.txt` |
| `chmod` | 修改权限 | `chmod +x script.sh` |
| `chown` | 修改所有者 | `chown user:group file` |
| `ln` | 创建链接 | `ln -s /usr/bin/python3 python` |
| `tar` | 归档/解压 | `tar -xzvf archive.tar.gz` |
| `curl` | HTTP 请求 | `curl -I https://example.com` |

### 第三梯队（需要时查阅）

| 命令 | 用途 |
|------|------|
| `awk` | 文本列处理 |
| `sed` | 流式文本替换 |
| `sort` / `uniq` | 排序去重 |
| `wc` | 字数/行数统计 |
| `head` / `tail` | 文件头尾查看 |
| `diff` | 文件对比 |
| `rsync` | 文件同步 |
| `scp` | 远程复制 |
| `dd` | 块级读写 |
| `xargs` | 参数传递 |

详见 [[06-命令行基础与Shell入门]]、[[18-正则与文本处理三剑客]]、[[53-终端常用工具大全]]。

---

## 编辑器选择建议

| 编辑器 | 适用人群 | 学习投入 | 生产力回报 |
|--------|---------|---------|-----------|
| **Nano** | 绝对新手 | 5 分钟 | 立即可用 |
| **Vim** | 服务器管理员 | 1-2 周 | 极高（SSH 必备） |
| **Neovim** | 追求现代体验的 Vim 用户 | 1-2 周 | 极高 |
| **VS Code** | 开发者（有 GUI） | 数小时 | 极高 |
| **Emacs** | 哲学探索者 | 数月 | "一生之编辑器" |
| **Helix** | 想要开箱即用的模态编辑者 | 1-3 天 | 高 |

> 无论选择哪个编辑器，**至少掌握一种终端编辑器**——当你在 SSH 到远程服务器时，GUI 编辑器帮不了你。

详见 [[05-文本编辑器(Vim+Nano)]]。
neovim可以参考我们的项目

---

## 桌面环境选型

| 桌面环境 | 资源消耗 | 定制性 | 适合 |
|---------|---------|-------|------|
| **GNOME** | 中等偏高 | 低（需扩展） | 想要开箱即用的用户 |
| **KDE Plasma** | 中等 | 极高 | 追求自定义的用户 |
| **Xfce** | 低 | 中 | 老旧硬件或追求简洁 |
| **i3 / Sway** | 极低 | 极高 | 平铺式窗口管理的爱好者 |
| **Hyprland** | 中等 | 极高 | Wayland 下的美观平铺体验 |
| **Niri** | 低 | 高 | 滚动式平铺窗口的独特体验 |

详见 [[49-Wayland深入指南]]、[[distro/arch/desktop/02-Hyprland配置|Hyprland 配置]]、[[distro/arch/desktop/01-Niri配置|Niri 配置]]。

---

## 常见疑问与误区

### 误区一："Linux 只有命令行，太不友好了"

现代 Linux 桌面（GNOME、KDE Plasma）的易用性不亚于 macOS 和 Windows。命令行不是必需，而是**高级武器**——当 GUI 无法解决问题时（比如批处理、远程管理、自动化），命令行展现出无与伦比的威力。

### 误区二："应该先确定'最好'的发行版再开始学"

不同发行版之间 90% 的 Linux 知识是互通的。选择一个主流发行版（Debian/Ubuntu、Fedora 或 Arch）**开始动手**远比花时间纠结选择重要。当你真正理解 Linux 后，切换发行版不过是换一层"皮肤"。

### 误区三："Linux 没有专业软件"

这是一个过时的印象。今天 Linux 拥有：
- 浏览器：Chrome, Firefox, Edge, Brave
- IDE：VS Code, JetBrains 全家桶, Neovim, Emacs
- 美术：Blender（3D）, GIMP（图像）, Kdenlive（视频）, Inkscape（矢量）
- 办公：LibreOffice, OnlyOffice, 网页版 Office/Google Docs

### 误区四："我需要记住所有命令"

**没有人能记住所有命令。** Linux 专家的核心能力不是记忆，而是：
1. 用 `man`、`tldr`、搜索引擎快速找到答案
2. 理解核心概念，从而推断陌生工具的使用方法
3. 善用 `Tab` 补全和 `Ctrl+R` 历史搜索
4. 阅读错误信息——它们是线索而非敌人

### 误区五："Linux 不会中病毒"

Linux **不是绝对安全**的。虽然其安全架构（权限分离、包管理签名、SELinux/AppArmor）强于传统 Windows，但：
- Linux 服务器是挖矿病毒和僵尸网络的主要目标
- 供应链攻击（如 xz 后门事件）真实存在
- 容器逃逸和提权漏洞不断被发现
- 不安全的配置是人最多的安全漏洞来源

详见 [[26-系统安全加固与审计]]、[[22-防火墙与安全]]。

---

## 如何高效使用本教程

### 推荐工具：Obsidian

本教程中的所有章节均使用 **Obsidian 风格的 [[双向链接]]** 相互引用。在 Obsidian 中打开本仓库文件夹作为 Vault，即可获得：

- **关系图谱（Graph View）**：可视化所有章节之间的引用关系，发现知识关联
- **反向链接（Backlinks）**：查看哪些章节引用了当前页面
- **快速搜索**：Cmd/Ctrl + O 快速跳转到任意章节
- **标签系统**：可按 `#入门 #原理 #运维 #安全` 等标签筛选内容

### 其他 Markdown 阅读器

本教程也完全兼容任何支持 Markdown 的阅读器：
- VS Code + Markdown Preview Enhanced 插件
- Typora
- GitHub 直接在线阅读
- 任意静态网站生成器（MkDocs、mdBook、Docusaurus 等）

### 阅读建议

1. 按照上方的**学习路径**选择适合自己的阅读顺序
2. 遇到不熟悉的概念时，点击（或查找）文中的 [[双向链接]] 跳转到相关章节深入
3. 代码示例建议在虚拟机或实验环境中亲自运行一遍
4. 善用 [[发行版命令速查表]] 和 [[术语对照表]] 作为日常参考
5. 每读完一章，在 Obsidian 的关系图谱中查看该章节的连接，巩固理解

---

## 贡献

本教程欢迎任何形式的贡献，包括但不限于：

- **纠错**：错别字、技术错误、过时的命令示例
- **补充**：缺失的内容、新工具、新发行版支持
- **翻译修正**：术语翻译的准确性和一致性
- **结构调整**：章节顺序、内容拆分/合并的建议
- **实战案例**：真实场景下的应用示例和故障排查记录

### 贡献规范

1. 保持与现有内容一致的写作风格：中文为主，英文术语保留并标注译名
2. 使用 Obsidian 风格的 [[双向链接]] 引用其他章节，增强知识网络
3. 代码示例优先使用 `bash` 代码块并经过实际测试
4. 表格和列表组织信息，保持可读性
5. 引用外部资源时注明 URL

---

## 资源文件

| 文件 | 说明 |
|------|------|
| [[发行版命令速查表]] | 跨发行版命令对照大全，涵盖 apt/dnf/pacman/zypper/apk/nix/emerge 的日常操作 |
| [[术语对照表]] | Linux 核心术语的英汉对照和简明解释，按类别组织 |

---

## 文件结构说明

```
linux/
├── README.md                          ← 你正在看的主入口
    ├── 01-*.md ~ 63-*.md                  ← 63 章主教程（按编号排列）
├── resources/                         ← 辅助资源
│   ├── 发行版命令速查表.md             ← 跨发行版命令对照
│   └── 术语对照表.md                   ← 英汉术语速查
└── distro/                            ← 发行版专项内容
    ├── arch/                          ← Arch Linux 系列（含桌面子目录）
    │   ├── 01-~06-                    ← Arch 核心教程
    │   └── desktop/                   ← Arch 桌面环境配置集
    ├── debian/                        ← Debian / Ubuntu 系列
    ├── redhat/                        ← RHEL / Fedora 系列
    └── nix/                           ← NixOS 系列
```

---

## Linux 技术栈就业岗位参考

| 岗位方向 | 核心技能 | 推荐章节 |
|---------|---------|---------|
| **后端开发** | Linux 基础操作、Shell 脚本、服务部署、数据库管理 | 01-15, 21-26 |
| **DevOps 工程师** | CI/CD、容器/K8s、配置管理、监控、云服务 | 01-15, 44-45, 54-62 |
| **系统管理员** | 用户管理、安全加固、存储、网络、自动化运维 | 全部基础 + 36-43 |
| **SRE / 平台工程** | 性能调优、追踪、故障排查、自动化、高可用 | 36-53, 54-62 |
| **嵌入式 Linux** | 内核模块、设备驱动、交叉编译、启动流程 | 36-43, Buildroot/Yocto |
| **安全工程师** | 防火墙、SELinux、审计、渗透测试 | 22, 26, distro/redhat/04, distro/redhat/05 |
| **内核开发者** | C 语言、内核架构、内存管理、调度器 | 27-43 |

---

## 重要信号速查

在 [[08-进程管理]] 中会详细学习信号机制，这里先给出常用信号的速查表：

| 信号编号 | 信号名 | 含义 | 可否捕获/忽略 |
|---------|--------|------|-------------|
| 1 | SIGHUP | 挂起（终端断开） | 可 |
| 2 | SIGINT | 中断（Ctrl+C） | 可 |
| 3 | SIGQUIT | 退出（Ctrl+\\），产生 core dump | 可 |
| 9 | SIGKILL | 强制终止，**不可捕获** | 否 |
| 15 | SIGTERM | 优雅终止（默认 `kill`） | 可 |
| 17 | SIGCHLD | 子进程状态变更 | 可 |
| 18 | SIGCONT | 继续执行停止的进程 | 可 |
| 19 | SIGSTOP | 暂停进程，**不可捕获** | 否 |
| 20 | SIGTSTP | 终端暂停（Ctrl+Z） | 可 |

```bash
# 常用信号操作
kill -15 <pid>    # 优雅终止（默认）
kill -9 <pid>     # 强制杀死（最后手段）
kill -HUP <pid>   # 重载配置（守护进程约定）
kill -STOP <pid>  # 暂停进程
kill -CONT <pid>  # 恢复进程
```

---

## 重要的 man 手册页码

[man]惯例将手册分为 9 个节（section）。知道在哪里查找信息是高效使用 Linux 的关键：

| 节号 | 内容 | 示例 |
|------|------|------|
| 1 | 用户命令 | `man 1 ls` |
| 2 | 系统调用 | `man 2 open`, `man 2 fork` |
| 3 | C 库函数 | `man 3 printf`, `man 3 malloc` |
| 4 | 设备文件 | `man 4 tty`, `man 4 null` |
| 5 | 配置文件格式 | `man 5 sshd_config`, `man 5 fstab` |
| 6 | 游戏 | `man 6 fortune`（如果安装了的话） |
| 7 | 杂项（概述、约定） | `man 7 signal`, `man 7 socket` |
| 8 | 系统管理命令 | `man 8 iptables`, `man 8 systemctl` |
| 9 | 内核例程 | `man 9 printk`（需内核文档包） |

```bash
# 当 man 返回多个匹配时
man -f signal      # 等同于 whatis signal，列出所有节中的匹配
man 2 signal       # 直接查看第 2 节（系统调用）的 signal
man 7 signal       # 查看第 7 节（概述）的 signal
```

---

## 基于 Linux 内核的著名项目

Linux 内核的影响力远超服务器领域：

| 项目 | 说明 | 用户规模 |
|------|------|---------|
| **Android** | 基于 Linux 内核的移动操作系统 | 全球 30 亿+ 活跃设备 |
| **ChromeOS** | Google 的轻量级桌面操作系统 | 教育市场主流 |
| **AWS, GCP, Azure** | 三大云服务商底层均大量使用 Linux | 互联网基础设施 |
| **OpenWrt** | 路由器固件系统 | 数百万台路由器 |
| **Steam Deck / SteamOS** | Valve 的手持游戏机操作系统 | 基于 Arch Linux |
| **Tesla 车载系统** | 汽车中控运行 Linux | 数百万辆汽车 |
| **Starlink 卫星** | SpaceX 星链卫星运行 Linux | 数千颗在轨卫星 |

---

## 许可证

本教程文档采用 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) 协议发布。代码示例遵循相同的共享条款。

---

*"Software is like sex: it's better when it's free." — Linus Torvalds*

*"Talk is cheap. Show me the code." — Linus Torvalds*
