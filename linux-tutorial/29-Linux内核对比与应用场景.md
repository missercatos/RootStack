# 29 - Linux 内核对比与应用场景

> Linux 内核是操作系统的核心，直接决定了系统的性能、稳定性和硬件兼容性。Arch Linux 的滚动发布模式使用户可以方便地选择和切换不同的内核。本章将全面介绍各种可用内核的特性、区别和适用场景，帮助你根据需求选择最合适的内核。

---

## 29.1 什么是 Linux 内核

Linux 内核是操作系统的核心组件，负责：

- **进程管理**：调度和管理运行中的程序
- **内存管理**：分配和回收物理/虚拟内存
- **文件系统**：管理磁盘上的数据存储
- **设备驱动**：与硬件设备通信
- **网络协议栈**：处理网络数据传输
- **安全机制**：权限控制、SELinux/AppArmor 等

```bash
# 查看当前内核版本
uname -r
# 输出示例：6.9.1-arch1-1

# 查看内核完整信息
uname -a

# 查看内核编译配置
zcat /proc/config.gz | less

# 查看内核命令行参数
cat /proc/cmdline

# 查看内核模块信息
lsmod | wc -l  # 已加载模块数量
```

---

## 29.2 Arch Linux 可用内核一览

### 29.2.1 linux（默认稳定内核）

Arch Linux 官方仓库提供的主线稳定内核，紧跟上游最新稳定版本。

```bash
sudo pacman -S linux linux-headers
```

| 特性 | 说明 |
|-----|------|
| 版本跟踪 | 上游最新稳定版 |
| 更新频率 | 每 1-2 周 |
| 调度器 | EEVDF（6.6+） |
| 适用场景 | 通用桌面、开发 |
| 稳定性 | 良好 |
| 硬件支持 | 最新 |

### 29.2.2 linux-lts（长期支持内核）

Linux 长期支持版本，维护周期为 2-6 年，更加保守稳定。

```bash
sudo pacman -S linux-lts linux-lts-headers
```

| 特性 | 说明 |
|-----|------|
| 版本跟踪 | LTS 分支（如 6.6.x、6.1.x） |
| 更新频率 | 按需修复更新 |
| 调度器 | CFS 或 EEVDF（取决于版本） |
| 适用场景 | 服务器、生产环境、备用内核 |
| 稳定性 | 优秀 |
| 硬件支持 | 较旧但稳定 |

> **建议**：始终安装一个 LTS 内核作为后备，当主内核出问题时可以切换。

### 29.2.3 linux-zen（桌面优化内核）

Zen 内核是面向桌面用户的优化内核，合并了多种性能改进补丁。

```bash
sudo pacman -S linux-zen linux-zen-headers
```

| 特性 | 说明 |
|-----|------|
| 基于 | 最新主线内核 |
| 调度器 | BORE |
| 抢占模型 | Full Preemption |
| I/O 调度器 | 优化的 mq-deadline |
| 适用场景 | 桌面、游戏、多媒体 |
| 特点 | 低延迟、高响应性 |

主要优化包括：

- MuQSS/BORE 调度器改进
- 更激进的内存回收策略
- 优化的定时器频率（1000 Hz）
- FUTEX_WAIT_MULTIPLE 支持
- 各种桌面响应性补丁

### 29.2.4 linux-hardened（安全加固内核）

安全加固内核，包含大量安全相关补丁和更严格的默认配置。

```bash
sudo pacman -S linux-hardened linux-hardened-headers
```

| 特性 | 说明 |
|-----|------|
| 基于 | 最新主线内核 |
| 安全特性 | 内核地址随机化增强、堆栈保护 |
| 适用场景 | 安全敏感环境、服务器 |
| 权衡 | 部分性能损失、某些软件可能不兼容 |

安全增强措施：

- 内核地址空间布局随机化（KASLR）增强
- 禁止非特权用户访问 dmesg
- 禁用 kexec
- 限制 BPF（JIT 默认禁用）
- 更严格的模块签名验证
- SLUB 内存分配器加固
- 禁止非特权用户使用 user namespaces（默认）

```bash
# 注意：某些需要 user namespaces 的程序（如无特权容器）需要额外配置
# 启用 unprivileged user namespaces
sudo sysctl kernel.unprivileged_userns_clone=1
```

### 29.2.5 linux-rt / linux-rt-lts（实时内核）

实时内核应用 PREEMPT_RT 补丁，提供确定性的低延迟响应。

```bash
# 实时内核（AUR）
yay -S linux-rt linux-rt-headers

# 实时 LTS 内核（AUR）
yay -S linux-rt-lts linux-rt-lts-headers
```

| 特性 | 说明 |
|-----|------|
| 抢占模型 | PREEMPT_RT（完全实时抢占） |
| 延迟 | 微秒级确定性延迟 |
| 适用场景 | 音视频制作、工业控制、科学计算 |
| 权衡 | 吞吐量略有下降 |

### 29.2.6 linux-cachyos（CachyOS 性能内核）

CachyOS 项目维护的高度优化内核，集成了大量性能补丁。

```bash
# 添加 CachyOS 仓库
# 参考：https://cachyos.org/
# 或从 AUR 安装
yay -S linux-cachyos linux-cachyos-headers
```

| 特性 | 说明 |
|-----|------|
| 调度器 | BORE / sched-ext |
| 编译优化 | x86-64-v3 / x86-64-v4 |
| 特点 | AutoFDO、DAMON、LRNG |
| 适用场景 | 游戏、桌面性能极致优化 |
| 更新频率 | 紧跟主线 |

主要特性：

- BORE 调度器（Burst-Oriented Response Enhancer）
- sched-ext 支持（可插拔调度器框架）
- DAMON 内存管理优化
- 多种 CPU 微架构优化编译
- BBRv3 网络拥塞控制
- NTSYNC 补丁（Windows 游戏兼容性）

### 29.2.7 linux-xanmod（XanMod 内核）

XanMod 是面向桌面和游戏的定制内核。

```bash
yay -S linux-xanmod linux-xanmod-headers
```

| 特性 | 说明 |
|-----|------|
| 调度器 | BORE |
| 定时器频率 | 1000 Hz |
| 抢占模型 | Full Preemption |
| 适用场景 | 游戏、桌面、流媒体 |
| TCP 拥塞控制 | BBRv3 |

### 29.2.8 linux-clear（Clear Linux 优化内核）

基于 Intel Clear Linux 项目的内核配置，针对 Intel 平台优化。

```bash
yay -S linux-clear linux-clear-headers
```

| 特性 | 说明 |
|-----|------|
| 优化平台 | Intel CPU |
| 编译优化 | -O3、LTO |
| 特点 | Intel 微架构特定优化 |
| 适用场景 | Intel 平台桌面/服务器 |
| 权衡 | AMD 平台可能不如其他内核 |

---

## 29.3 各内核特性对比表

| 内核 | 调度器 | 抢占 | 定时器 | 编译优化 | 安全加固 | 实时性 |
|-----|--------|------|--------|---------|---------|--------|
| linux | EEVDF | Voluntary | 300 Hz | Generic | 标准 | 无 |
| linux-lts | CFS/EEVDF | Voluntary | 300 Hz | Generic | 标准 | 无 |
| linux-zen | BORE | Full | 1000 Hz | Generic | 标准 | 无 |
| linux-hardened | EEVDF | Voluntary | 300 Hz | Generic | 增强 | 无 |
| linux-rt | CFS | RT Full | 1000 Hz | Generic | 标准 | 完全 |
| linux-cachyos | BORE | Full | 1000 Hz | x86-64-v3/v4 | 标准 | 无 |
| linux-xanmod | BORE | Full | 1000 Hz | x86-64-v3 | 标准 | 无 |
| linux-clear | EEVDF | Voluntary | 1000 Hz | Intel 优化 | 标准 | 无 |

性能大致排名（桌面/游戏场景）：

```
linux-cachyos ≈ linux-xanmod > linux-zen > linux-clear > linux > linux-lts > linux-hardened
```

> 注意：实际性能差异取决于工作负载，上述排名仅为一般桌面/游戏场景的参考。

---

## 29.4 调度器对比

CPU 调度器决定了进程如何获得 CPU 时间，对系统响应性和吞吐量有直接影响。

### 29.4.1 CFS（Completely Fair Scheduler）

- Linux 2.6.23 至 6.5 的默认调度器
- 基于红黑树的公平调度
- 追求所有进程获得公平的 CPU 时间
- 适合通用工作负载

### 29.4.2 EEVDF（Earliest Eligible Virtual Deadline First）

- Linux 6.6+ 的默认调度器
- CFS 的改进版本
- 基于虚拟截止时间的调度
- 改善了延迟敏感任务的响应性
- 减少了调度延迟的长尾效应

### 29.4.3 BORE（Burst-Oriented Response Enhancer）

- 基于 CFS/EEVDF 的增强调度器
- 优先处理突发性（interactive）任务
- 自动识别交互式和批处理任务
- 对桌面响应性有明显改善
- 用于 linux-zen、linux-cachyos、linux-xanmod

### 29.4.4 BMQ（BitMap Queue）

- 由 Alfred Chen 开发
- 使用位图队列替代红黑树
- O(1) 调度复杂度
- 低延迟，适合桌面
- 已不再活跃维护

### 29.4.5 PDS（Priority and Deadline based Skiplist Scheduler）

- 同样由 Alfred Chen 开发
- 基于跳表（skiplist）的优先级调度
- BMQ 的前身
- 已不再活跃维护

### 29.4.6 SCHED_EXT（可扩展调度器）

- Linux 6.12+ 引入的调度器框架
- 允许通过 eBPF 程序实现自定义调度策略
- 无需重新编译内核即可更换调度策略
- 正在快速发展中

```bash
# 安装 sched-ext 调度器（需要支持的内核）
yay -S scx-scheds

# 使用 scx_rusty 调度器（Rust 实现）
sudo scx_rusty

# 使用 scx_lavd 调度器（针对游戏优化）
sudo scx_lavd

# 列出可用的 scx 调度器
ls /usr/bin/scx_*
```

各调度器特性对比：

| 调度器 | 复杂度 | 延迟 | 吞吐量 | 公平性 | 维护状态 |
|-------|--------|------|--------|--------|---------|
| CFS | O(log n) | 中等 | 高 | 优秀 | 已替代 |
| EEVDF | O(log n) | 较低 | 高 | 优秀 | 活跃（默认） |
| BORE | O(log n) | 低 | 高 | 良好 | 活跃 |
| BMQ | O(1) | 低 | 中等 | 良好 | 停止 |
| PDS | O(log n) | 低 | 中等 | 良好 | 停止 |
| SCHED_EXT | 可变 | 可变 | 可变 | 可变 | 活跃（实验） |

---

## 29.5 如何安装多个内核并切换

### 29.5.1 安装多个内核

```bash
# 安装多个内核（可以共存）
sudo pacman -S linux linux-headers
sudo pacman -S linux-lts linux-lts-headers
sudo pacman -S linux-zen linux-zen-headers
```

### 29.5.2 GRUB 切换内核

```bash
# 安装内核后重新生成 GRUB 配置
sudo grub-mkconfig -o /boot/grub/grub.cfg
```

GRUB 会自动检测所有已安装的内核并为每个生成启动条目。重启后在 GRUB 菜单的「Advanced options for Arch Linux」子菜单中选择。

设置默认内核（编辑 `/etc/default/grub`）：

```ini
# 使用保存的上次选择
GRUB_DEFAULT=saved
GRUB_SAVEDEFAULT=true

# 或指定菜单项编号
GRUB_DEFAULT="1>2"
```

```bash
# 重新生成配置
sudo grub-mkconfig -o /boot/grub/grub.cfg
```

### 29.5.3 systemd-boot 切换内核

systemd-boot 需要手动为每个内核创建启动条目。

```bash
# 查看 ESP 挂载点
bootctl status
```

为每个内核创建条目，例如 `/boot/loader/entries/arch.conf`：

```ini
title   Arch Linux
linux   /vmlinuz-linux
initrd  /initramfs-linux.img
options root=UUID=xxxx-xxxx rw
```

`/boot/loader/entries/arch-lts.conf`：

```ini
title   Arch Linux (LTS)
linux   /vmlinuz-linux-lts
initrd  /initramfs-linux-lts.img
options root=UUID=xxxx-xxxx rw
```

`/boot/loader/entries/arch-zen.conf`：

```ini
title   Arch Linux (Zen)
linux   /vmlinuz-linux-zen
initrd  /initramfs-linux-zen.img
options root=UUID=xxxx-xxxx rw
```

设置默认启动项（`/boot/loader/loader.conf`）：

```ini
default arch.conf
timeout 5
console-mode max
editor  no
```

```bash
# 验证配置
bootctl list
```

### 29.5.4 使用 kernel-install 自动管理

```bash
# 查看已安装的内核
ls /usr/lib/modules/

# kernel-install 会自动在安装/删除内核时更新引导
# 对于 systemd-boot 用户，这是推荐方式
```

---

## 29.6 内核选择建议

### 29.6.1 游戏用途

```
推荐：linux-cachyos 或 linux-zen

理由：
- BORE 调度器对游戏帧率和帧时间有改善
- Full Preemption 降低输入延迟
- 1000 Hz 定时器提供更平滑的帧节奏
- NTSYNC 补丁改善 Wine/Proton 兼容性
- futex 优化改善多线程游戏性能
```

### 29.6.2 服务器用途

```
推荐：linux-lts

理由：
- 长期支持，安全更新有保障
- 经过更多测试，稳定性最佳
- 不会因频繁更新引入回归
- 适合生产环境的保守策略

备选：linux-hardened（安全敏感服务器）
```

### 29.6.3 开发用途

```
推荐：linux（默认内核）

理由：
- 最新的内核特性和 API
- 最新的硬件支持
- 最接近上游，bug 修复最快
- 文档和社区支持最广泛

备选：linux-zen（如果同时需要良好的桌面体验）
```

### 29.6.4 嵌入式 / IoT

```
推荐：linux-lts + 自定义编译

理由：
- 长期稳定支持
- 可裁剪不需要的功能
- 确定的维护周期
- 最小化攻击面
```

### 29.6.5 安全敏感场景

```
推荐：linux-hardened

理由：
- 内核加固补丁
- 更严格的默认安全配置
- 减少攻击面
- 适合处理敏感数据的工作站

注意事项：
- 某些程序可能因安全限制无法正常运行
- Docker/Podman 无特权容器需要额外配置
- 性能略有下降
```

### 29.6.6 音视频制作

```
推荐：linux-rt 或 linux-rt-lts

理由：
- 微秒级确定性延迟
- 避免音频 xrun（buffer underrun）
- 适合实时音频处理（JACK、PipeWire）
- 专业音频工作站必备

备选：linux-zen（对实时性要求不极端时）

配合设置：
- 将用户加入 realtime 组
- 配置 rtkit
- 设置合适的 ulimit
```

```bash
# 音频制作相关配置
sudo usermod -aG realtime $USER

# /etc/security/limits.d/99-realtime.conf
# @realtime - rtprio 99
# @realtime - memlock unlimited
```

---

## 29.7 内核版本号含义

Linux 内核版本号格式：**主版本.次版本.修订号**

```
例如：6.9.3
       │ │ └── 修订号（patch）：bug 修复和安全更新
       │ └──── 次版本（minor）：新功能和改进
       └────── 主版本（major）：重大里程碑
```

| 版本组成 | 说明 | 示例 |
|---------|------|------|
| 主版本 | Linus 认为需要递增时变化 | 5→6 |
| 次版本 | 每个开发周期递增 | 6.8→6.9 |
| 修订号 | 稳定版中的 bug 修复 | 6.9.1→6.9.2 |

Arch 特有的版本后缀：

```
6.9.3-arch1-1
      ├─────── arch 打包版本号
      └───────── Arch 特有补丁修订
```

查看版本信息：

```bash
# 当前运行的内核版本
uname -r

# 已安装的内核版本
pacman -Q linux linux-lts linux-zen 2>/dev/null

# 可用的内核更新
checkupdates | grep linux
```

---

## 29.8 内核发布周期

Linux 内核采用基于时间的发布模型：

```
开发周期（约 9-10 周）：

合并窗口（2 周）→ rc1 → rc2 → ... → rc7/rc8 → 正式发布
     │                    │
     │                    └── 只接受 bug 修复
     └── 接受新功能合并
```

| 阶段 | 时长 | 内容 |
|-----|------|------|
| 合并窗口 | ~2 周 | 合并下一版本的新功能 |
| RC 阶段 | ~7-8 周 | 只修复 bug，不加新功能 |
| 稳定发布 | - | 正式版本发布 |
| 稳定维护 | 数周到数年 | 持续的 bug 和安全修复 |

LTS 内核维护周期：

| LTS 版本 | 发布时间 | 维护结束（预计） |
|---------|---------|--------------|
| 6.6 | 2023.10 | 2026.12 |
| 6.1 | 2022.12 | 2026.12 |
| 5.15 | 2021.10 | 2026.10 |
| 5.10 | 2020.12 | 2026.12 |
| 5.4 | 2019.11 | 2025.12 |

---

## 29.9 内核模块管理

### 29.9.1 lsmod

```bash
# 列出所有已加载模块
lsmod

# 按使用计数排序
lsmod | sort -k 3 -rn | head -20

# 查看特定模块
lsmod | grep nvidia
```

输出格式说明：

```
Module                  Size  Used by
nvidia_drm            102400  10
nvidia_modeset       1576960  14 nvidia_drm
nvidia              62512128  1322 nvidia_modeset
```

- **Module**：模块名
- **Size**：模块占用内存（字节）
- **Used by**：被引用次数和引用者

### 29.9.2 modprobe

```bash
# 加载模块（自动处理依赖）
sudo modprobe nvidia

# 卸载模块
sudo modprobe -r nvidia

# 查看模块依赖（不实际加载）
modprobe --show-depends nvidia

# 试运行（不实际执行）
modprobe -n -v nvidia

# 加载模块并传递参数
sudo modprobe i915 enable_guc=2
```

### 29.9.3 modinfo

```bash
# 查看模块信息
modinfo i915

# 查看模块可用参数
modinfo -p i915

# 查看模块路径
modinfo -n i915

# 查看模块描述
modinfo -d nvidia
```

### 29.9.4 模块参数配置

临时设置（本次会话）：

```bash
sudo modprobe i915 enable_guc=3
```

永久设置（`/etc/modprobe.d/i915.conf`）：

```
options i915 enable_guc=3 enable_fbc=1
```

查看当前模块参数：

```bash
# 查看已加载模块的参数值
cat /sys/module/i915/parameters/enable_guc
ls /sys/module/i915/parameters/
```

### 29.9.5 开机自动加载模块

```bash
# 创建配置文件
echo "vfio-pci" | sudo tee /etc/modules-load.d/vfio-pci.conf
```

### 29.9.6 屏蔽模块

```bash
# /etc/modprobe.d/blacklist.conf
blacklist nouveau
blacklist pcspkr
blacklist snd_pcsp

# 某些模块需要 install 指令才能完全阻止
install nouveau /bin/false
```

---

## 29.10 内核参数详解

内核参数（cmdline）在引导时传递给内核，影响系统行为。

### 29.10.1 查看和设置

```bash
# 查看当前内核参数
cat /proc/cmdline

# GRUB 临时修改：启动菜单按 e，编辑 linux 行
# GRUB 永久修改：编辑 /etc/default/grub
# GRUB_CMDLINE_LINUX_DEFAULT="quiet loglevel=3"

# systemd-boot 修改：编辑对应的 .conf 文件的 options 行
```

### 29.10.2 常用内核参数

| 参数 | 作用 | 示例 |
|-----|------|------|
| `quiet` | 减少启动信息输出 | `quiet` |
| `loglevel=N` | 设置内核日志级别（0-7） | `loglevel=3` |
| `splash` | 启用启动画面 | `splash` |
| `root=` | 指定根分区 | `root=UUID=xxx` |
| `rw` / `ro` | 根分区读写/只读挂载 | `rw` |
| `init=` | 指定 init 程序 | `init=/bin/bash` |
| `systemd.unit=` | 启动到指定 target | `systemd.unit=rescue.target` |
| `nomodeset` | 禁用内核模式设置 | `nomodeset` |
| `acpi=off` | 禁用 ACPI | `acpi=off` |
| `noapic` | 禁用 APIC | `noapic` |
| `mem=` | 限制可用内存 | `mem=4G` |
| `iommu=` | IOMMU 设置 | `iommu=pt` |
| `intel_iommu=on` | 启用 Intel IOMMU | `intel_iommu=on` |
| `amd_iommu=on` | 启用 AMD IOMMU | `amd_iommu=on` |
| `mitigations=off` | 禁用 CPU 漏洞缓解 | `mitigations=off` |
| `nowatchdog` | 禁用看门狗 | `nowatchdog` |
| `nmi_watchdog=0` | 禁用 NMI 看门狗 | `nmi_watchdog=0` |
| `pci=noaer` | 禁用 PCIe AER | `pci=noaer` |
| `nvidia-drm.modeset=1` | NVIDIA DRM | `nvidia-drm.modeset=1` |

### 29.10.3 性能优化参数

```bash
# 禁用 CPU 漏洞缓解措施（提升性能，降低安全性）
mitigations=off

# 禁用看门狗（减少中断开销）
nowatchdog nmi_watchdog=0

# 透明大页（THP）配置
transparent_hugepage=always

# 提高 vm.dirty 比例（适合大内存系统）
# 这个通过 sysctl 设置更合适
```

### 29.10.4 GPU 相关参数

```bash
# Intel GPU
i915.enable_guc=2          # 启用 GuC/HuC 固件
i915.enable_fbc=1          # 启用帧缓冲压缩
i915.enable_psr=1          # 启用面板自刷新

# NVIDIA
nvidia-drm.modeset=1       # 启用 DRM
nvidia-drm.fbdev=1         # 启用 framebuffer 设备
nvidia.NVreg_PreserveVideoMemoryAllocations=1  # 挂起保留显存

# AMD
amdgpu.ppfeaturemask=0xffffffff  # 启用所有电源功能
```

### 29.10.5 调试参数

```bash
# 紧急调试
systemd.unit=emergency.target    # 进入紧急模式
systemd.unit=rescue.target       # 进入救援模式
init=/bin/bash                   # 直接进入 bash

# 详细日志
loglevel=7                       # 最详细的内核日志
systemd.log_level=debug          # systemd 调试日志
rd.shell                         # initramfs 故障时进入 shell
```

---

## 29.11 DKMS 与内核升级

DKMS（Dynamic Kernel Module Support）允许内核模块在内核升级时自动重新编译。

### 29.11.1 DKMS 基本概念

```
传统方式：内核升级 → 第三方模块失效 → 手动重新编译
DKMS 方式：内核升级 → DKMS 自动重新编译模块 → 模块继续工作
```

### 29.11.2 安装和使用

```bash
# 安装 DKMS
sudo pacman -S dkms

# 常见需要 DKMS 的包
sudo pacman -S nvidia-dkms          # NVIDIA 驱动
sudo pacman -S v4l2loopback-dkms    # 虚拟摄像头
sudo pacman -S broadcom-wl-dkms     # Broadcom WiFi

# 查看 DKMS 模块状态
dkms status
```

输出示例：

```
nvidia/550.78, 6.9.3-arch1-1, x86_64: installed
nvidia/550.78, 6.6.32-1-lts, x86_64: installed
v4l2loopback/0.12.7, 6.9.3-arch1-1, x86_64: installed
```

### 29.11.3 DKMS 管理命令

```bash
# 手动编译模块（通常自动完成）
sudo dkms build nvidia/550.78 -k 6.9.3-arch1-1

# 手动安装模块
sudo dkms install nvidia/550.78 -k 6.9.3-arch1-1

# 移除模块
sudo dkms remove nvidia/550.78 --all

# 查看编译日志（排错用）
cat /var/lib/dkms/nvidia/550.78/build/make.log
```

### 29.11.4 DKMS 与多内核

当系统安装多个内核时，DKMS 会为每个内核分别编译模块：

```bash
# 安装新内核时 DKMS 自动触发
sudo pacman -S linux-zen linux-zen-headers
# DKMS 自动为 linux-zen 编译所有注册的模块

# 确保安装了对应的 headers 包
# linux       → linux-headers
# linux-lts   → linux-lts-headers
# linux-zen   → linux-zen-headers
```

### 29.11.5 DKMS 常见问题

```bash
# 问题：DKMS 编译失败
# 1. 确保安装了 kernel headers
sudo pacman -S linux-headers

# 2. 确保安装了编译工具
sudo pacman -S base-devel

# 3. 查看错误日志
cat /var/lib/dkms/<module>/<version>/build/make.log

# 4. 手动触发重新编译
sudo dkms autoinstall

# 问题：内核升级后模块丢失
# 确保 dkms 和 headers 包版本匹配
pacman -Q linux linux-headers
# 版本号应该一致
```

### 29.11.6 不使用 DKMS 的替代方案

对于 NVIDIA 驱动，也可以选择预编译版本：

```bash
# 预编译 NVIDIA 驱动（跟随默认内核更新）
sudo pacman -S nvidia         # 对应 linux
sudo pacman -S nvidia-lts     # 对应 linux-lts

# DKMS 版本（支持任意内核）
sudo pacman -S nvidia-dkms    # 对应所有已安装内核
```

| 方案 | 优点 | 缺点 |
|-----|------|------|
| nvidia | 无需编译，安装快 | 只支持 linux 内核 |
| nvidia-lts | 稳定 | 只支持 linux-lts 内核 |
| nvidia-dkms | 支持所有内核 | 需要编译，依赖 headers |

---

## 29.12 内核编译（高级）

如果现有内核都不满足需求，可以自行编译。

### 29.12.1 获取源码

```bash
# 获取 Arch 打包的内核源码
asp update linux
asp checkout linux

# 或直接从 kernel.org 下载
curl -O https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-6.9.3.tar.xz
tar xf linux-6.9.3.tar.xz
```

### 29.12.2 配置内核

```bash
# 基于当前运行内核的配置
zcat /proc/config.gz > .config
make olddefconfig

# 图形化配置界面
make menuconfig     # ncurses 界面
make nconfig        # 改进的 ncurses 界面
make xconfig        # Qt 界面

# 基于当前加载的模块精简配置
make localmodconfig
```

### 29.12.3 编译和安装

```bash
# 编译（使用所有 CPU 核心）
make -j$(nproc)

# 安装模块
sudo make modules_install

# 安装内核
sudo cp arch/x86/boot/bzImage /boot/vmlinuz-linux-custom
sudo cp System.map /boot/System.map-linux-custom

# 生成 initramfs
sudo mkinitcpio -k 6.9.3-custom -g /boot/initramfs-linux-custom.img

# 更新引导配置
sudo grub-mkconfig -o /boot/grub/grub.cfg
```

### 29.12.4 使用 Arch 的 makepkg 编译

推荐使用 Arch 的 PKGBUILD 方式编译，这样可以用 pacman 管理：

```bash
# 获取 PKGBUILD
asp update linux
asp checkout linux
cd linux

# 修改 PKGBUILD 或 config 文件
# 编译打包
makepkg -s

# 安装
sudo pacman -U linux-custom-6.9.3-1-x86_64.pkg.tar.zst
```

---

## 29.13 总结与建议

```
日常桌面：    linux-zen 或 linux-cachyos
游戏玩家：    linux-cachyos 或 linux-zen
服务器：      linux-lts
开发测试：    linux（默认）
安全优先：    linux-hardened
音频制作：    linux-rt
备用内核：    linux-lts（强烈建议始终安装）
```

> **黄金法则**：始终保留一个可用的备用内核（通常是 linux-lts），这样在主内核出问题时可以从引导菜单选择备用内核启动，避免系统完全无法使用。

---

## 29.14 本章测验

> [!example] 📝 自测题目

> [!question]- 选择题 1：Linux 6.6+ 版本的默认 CPU 调度器是？
> - A. CFS（Completely Fair Scheduler）
> - B. EEVDF（Earliest Eligible Virtual Deadline First）
> - C. BORE（Burst-Oriented Response Enhancer）
> - D. BMQ（BitMap Queue）
>
> > [!success]- 点击查看答案
> > **B**
> > Linux 6.6+ 的默认调度器是 EEVDF，它是 CFS 的改进版本，基于虚拟截止时间调度，改善了延迟敏感任务的响应性。

> [!question]- 选择题 2：以下哪个内核最适合游戏场景？
> - A. linux-lts
> - B. linux-hardened
> - C. linux-cachyos 或 linux-zen
> - D. linux-rt
>
> > [!success]- 点击查看答案
> > **C**
> > linux-cachyos 和 linux-zen 面向桌面/游戏优化，使用 BORE 调度器、Full Preemption、1000 Hz 定时器等，对游戏帧率和输入延迟有明显改善。

> [!question]- 选择题 3：DKMS 的主要作用是什么？
> - A. 管理内核启动参数
> - B. 内核升级时自动重新编译第三方模块
> - C. 提供内核安全加固功能
> - D. 管理多个内核的引导菜单
>
> > [!success]- 点击查看答案
> > **B**
> > DKMS（Dynamic Kernel Module Support）允许内核模块在内核升级时自动重新编译，确保第三方模块（如 NVIDIA 驱动）在新内核下继续工作。

> [!question]- 选择题 4：linux-hardened 内核的以下哪个安全特性可能导致 Docker 无特权容器无法正常运行？
> - A. 内核地址随机化增强
> - B. 禁止非特权用户使用 user namespaces
> - C. 更严格的模块签名验证
> - D. 禁用 kexec
>
> > [!success]- 点击查看答案
> > **B**
> > linux-hardened 默认禁止非特权用户使用 user namespaces，这会影响无特权容器的运行。需要通过 `sysctl kernel.unprivileged_userns_clone=1` 启用。

> [!question]- 判断题 5：安装多个内核时，GRUB 会自动检测并为每个内核生成启动条目。
> - A. ✓ 正确
> - B. ✗ 错误
>
> > [!success]- 点击查看答案
> > **A. ✓ 正确**
> > 执行 `grub-mkconfig -o /boot/grub/grub.cfg` 后，GRUB 会自动检测所有已安装的内核并在「Advanced options for Arch Linux」子菜单中为每个生成启动条目。

> [!question]- 选择题 6：内核参数 `mitigations=off` 的作用是？
> - A. 禁用所有网络防火墙规则
> - B. 禁用 CPU 漏洞缓解措施以提升性能
> - C. 关闭内核日志输出
> - D. 禁用 IOMMU 功能
>
> > [!success]- 点击查看答案
> > **B**
> > `mitigations=off` 禁用所有 CPU 硬件漏洞（如 Spectre、Meltdown）的缓解措施，可以提升性能但降低安全性。

> [!question]- 选择题 7：SCHED_EXT 是 Linux 6.12+ 引入的调度器框架，它的核心特点是？
> - A. 使用红黑树实现公平调度
> - B. 允许通过 eBPF 程序实现自定义调度策略
> - C. 固定使用 O(1) 调度复杂度
> - D. 仅支持实时任务调度
>
> > [!success]- 点击查看答案
> > **B**
> > SCHED_EXT 允许通过 eBPF 程序实现自定义调度策略，无需重新编译内核即可更换调度策略，是一个可扩展的调度器框架。

> [!question]- 判断题 8：使用 DKMS 版本的 NVIDIA 驱动（nvidia-dkms）时，必须安装对应内核的 headers 包。
> - A. ✓ 正确
> - B. ✗ 错误
>
> > [!success]- 点击查看答案
> > **A. ✓ 正确**
> > DKMS 需要内核头文件来编译模块。使用 linux 内核需要 linux-headers，使用 linux-lts 需要 linux-lts-headers，以此类推。

> [!question]- 选择题 9：Linux 内核版本号 6.9.3 中，"3" 代表什么？
> - A. 主版本号
> - B. 次版本号
> - C. 修订号（bug 修复和安全更新）
> - D. Arch 打包版本号
>
> > [!success]- 点击查看答案
> > **C**
> > 版本格式为"主版本.次版本.修订号"，6 是主版本，9 是次版本（新功能），3 是修订号（bug 修复和安全更新）。

> [!question]- 选择题 10：对于音视频制作的专业用户，推荐使用哪种内核？
> - A. linux（默认内核）
> - B. linux-lts
> - C. linux-rt（实时内核）
> - D. linux-hardened
>
> > [!success]- 点击查看答案
> > **C**
> > linux-rt 应用 PREEMPT_RT 补丁，提供微秒级确定性延迟，避免音频 xrun，是专业音频工作站的首选。
