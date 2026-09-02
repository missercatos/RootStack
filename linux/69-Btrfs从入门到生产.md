# 第69章 Btrfs 从入门到生产

## 概述

Btrfs（B-tree File System，发音为 "butter fs" 或 "btrfs"）是一种现代的写时复制（Copy-on-Write）文件系统，由 Oracle 于 2007 年发起开发，目前由社区维护。Btrfs 旨在提供先进的存储功能，包括快照、校验和、压缩、子卷管理和软件 RAID 支持，同时保持与 POSIX 标准的兼容性。

本章适用于所有 Linux 发行版，包括但不限于 Ubuntu、Fedora、Arch Linux、Debian、openSUSE、Manjaro、CentOS、Rocky Linux 等。示例命令基于通用 Linux 环境编写，部分发行版可能需要安装额外的软件包。

**安装 Btrfs 工具：**

```bash
# Debian / Ubuntu
sudo apt install btrfs-progs

# Fedora / RHEL / Rocky
sudo dnf install btrfs-progs

# Arch Linux / Manjaro
sudo pacman -S btrfs-progs

# openSUSE
sudo zypper install btrfsprogs
```

**验证版本：**

```bash
btrfs --version
# 输出示例: btrfs-progs v6.6.3
```

**内核模块：**

```bash
lsmod | grep btrfs
# 如果没有输出，加载模块:
sudo modprobe btrfs
```

---

## Btrfs 核心原理

### CoW（Copy-on-Write）

写时复制（Copy-on-Write，简称 CoW）是 Btrfs 最核心的设计理念。其基本原理是：

1. **写入新数据时不覆盖旧数据**：当需要修改文件时，Btrfs 不会直接覆盖原有磁盘块，而是将新数据写入新的空闲块中。
2. **原子更新**：修改完成后，Btrfs 原子地更新指向数据的指针，确保任何时刻数据都是完整一致的。
3. **无就地写入**：整个文件系统不存在就地写入（in-place write），这从根本上消除了写入过程中断电导致的文件系统损坏。

CoW 的优势：

- **崩溃一致性**：掉电后文件系统始终处于一致状态，无需 fsck 修复。
- **快照零开销**：快照仅需记录元数据变化，创建速度极快。
- **数据安全**：旧数据在被覆盖前始终可访问，提供天然的版本控制能力。

CoW 的劣势：

- **写放大**：即使修改少量数据，也可能导致整个数据块重新写入。
- **碎片化**：频繁的 CoW 操作会导致文件碎片增加，影响机械硬盘的随机读写性能。
- **数据库/虚拟机性能**：频繁原地更新的工作负载（如数据库、虚拟机磁盘）在 CoW 文件系统上性能较差。

### B-tree 架构

Btrfs 使用 B-tree（B 树）作为底层数据组织结构。所有元数据和数据指针都存储在 B-tree 节点中：

- **根树（Root Tree）**：指向所有其他树的根节点。
- **文件系统树（FS Tree）**：存储文件和目录的元数据。
- **校验和树（Checksum Tree）**：存储每个数据块的校验和。
- **Chunk Tree**：记录数据块分配信息。
- **Device Tree**：记录设备信息。
- **Extent Tree**：管理磁盘空间分配，跟踪已分配和空闲的extent。

B-tree 的节点大小默认为 16KB（可配置为 4K/16K/64K），采用平衡 B-tree 结构，支持高效的范围查询和插入操作。

### 校验和与数据完整性

Btrfs 对所有数据和元数据都计算校验和，默认使用 CRC32C 算法（也可配置为 xxhash、sha256、blake2b 等）。

```bash
# 查看当前校验和算法
sudo btrfs filesystem show | grep "Checksum"

# 创建时指定校验和算法
sudo mkfs.btrfs -m crc32c /dev/sdX

# 修改校验和算法（需要转换，有一定风险）
sudo btrfs filesystem set-seed xxhash /dev/sdX
```

校验和存储在数据的 B-tree 节点中，当读取数据时自动验证。如果校验和不匹配，Btrfs 会尝试从其他副本（如果存在冗余）读取正确数据，并报告错误。

**数据完整性保障机制：**

| 机制 | 说明 |
|------|------|
| 数据校验和 | 每个数据块都有校验和，读取时自动验证 |
| 元数据校验和 | 所有 B-tree 节点都有校验和 |
| 冗余副本 | RAID 1/10 模式下自动维护多份数据 |
| CoW 原子更新 | 确保崩溃后文件系统一致性 |
| Scrub | 后台主动校验所有数据和元数据 |

### 与 ext4/XFS 的设计哲学差异

| 特性 | Btrfs | ext4 | XFS |
|------|-------|------|-----|
| 写入方式 | CoW（写时复制） | 就地写入（in-place） | 就地写入（in-place） |
| 快照 | 原生支持 | 不支持 | 不支持（需 LVM） |
| 子卷 | 原生支持 | 不支持 | 不支持 |
| 数据校验 | 全量校验和 | 无（可选 metadata） | 仅元数据 |
| 透明压缩 | 支持 | 不支持 | 不支持 |
| 软件 RAID | 内建支持 | 不支持 | 不支持 |
| 在线碎片整理 | 支持 | 支持 | 支持 |
| 在线扩容 | 支持 | 支持 | 支持 |
| 在线缩减 | 支持 | 不支持 | 不支持 |
| 最大文件大小 | 16 EiB | 16 TiB | 8 EiB |
| 成熟度 | 中等 | 非常成熟 | 非常成熟 |
| 适用场景 | 桌面/开发/存储服务器 | 通用服务器 | 大规模I/O密集型 |

**选型建议：**

- Btrfs 适合需要快照、压缩、子卷管理的场景，如桌面系统、开发工作站、NAS 存储。
- ext4 适合追求稳定性和兼容性的通用服务器环境。
- XFS 适合大规模 I/O 密集型工作负载，如大数据分析、高性能计算。

---

## 创建与挂载

### mkfs.btrfs

`mkfs.btrfs` 是 Btrfs 文件系统创建工具：

```bash
# 基本创建
sudo mkfs.btrfs /dev/sdX1

# 指定卷标
sudo mkfs.btrfs -L "mydata" /dev/sdX1

# 指定节点大小（4K/16K/64K，默认16K）
sudo mkfs.btrfs -n 16k /dev/sdX1

# 指定元数据与数据的比例（metadata:1，默认metadata）
sudo mkfs.btrfs -d data /dev/sdX1
sudo mkfs.btrfs -d raid0 /dev/sdX1
sudo mkfs.btrfs -d raid1 /dev/sdX1
sudo mkfs.btrfs -d raid10 /dev/sdX1

# 指定校验和算法
sudo mkfs.btrfs -m crc32c /dev/sdX1
sudo mkfs.btrfs -m xxhash /dev/sdX1

# 强制创建（覆盖现有文件系统）
sudo mkfs.btrfs -f /dev/sdX1
```

**重要参数说明：**

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-L` | 卷标 | 无 |
| `-d` | 数据块 RAID 级别 | single |
| `-m` | 元数据 RAID 级别 | raid1 |
| `-n` | B-tree 节点大小 | 16K |
| `-f` | 强制覆盖 | - |
| `-U` | 指定 UUID | 随机生成 |
| `-O` | 启用特性 | 根据内核版本 |
| `-b` | 指定文件系统大小 | 设备全部空间 |

### 多设备创建（RAID 0/1/10）

Btrfs 支持跨多个设备创建文件系统，并内建软件 RAID 功能：

```bash
# RAID 1 - 镜像模式，需要至少2个设备
sudo mkfs.btrfs -d raid1 -m raid1 /dev/sdX1 /dev/sdY1

# RAID 0 - 条带化模式，需要至少2个设备
sudo mkfs.btrfs -d raid0 -m raid0 /dev/sdX1 /dev/sdY1

# RAID 10 - 镜像+条带化，需要至少4个设备
sudo mkfs.btrfs -d raid10 -m raid10 /dev/sdX1 /dev/sdY1 /dev/sdZ1 /dev/sdW1

# 混合RAID级别 - 元数据用raid1，数据用单盘
sudo mkfs.btrfs -d single -m raid1 /dev/sdX1 /dev/sdY1

# 三副本模式（数据raid1c3）
sudo mkfs.btrfs -d raid1c3 -m raid1c3 /dev/sdX1 /dev/sdY1 /dev/sdZ1
```

**RAID 级别概览：**

| 级别 | 最少设备 | 可用空间 | 容错 | 适用场景 |
|------|----------|----------|------|----------|
| single | 1 | 100% | 无 | 无冗余需求 |
| raid0 | 2 | N * 100% | 无 | 追求性能，无容错 |
| raid1 | 2 | 50% | 1台故障 | 基本冗余 |
| raid1c3 | 3 | 33% | 2台故障 | 高可用性 |
| raid10 | 4 | 50% | 每组1台 | 性能+冗余 |
| raid5 | 3 | (N-1)/N | 1台 | 不推荐生产使用 |
| raid6 | 4 | (N-2)/N | 2台 | 不推荐生产使用 |

### 挂载选项详解

```bash
# 基本挂载
sudo mount /dev/sdX1 /mnt

# 常用挂载选项
sudo mount -o compress=zstd,ssd,discard,noatime /dev/sdX1 /mnt
```

**主要挂载选项：**

| 选项 | 说明 | 推荐场景 |
|------|------|----------|
| `compress=zstd` | 启用透明压缩，zstd 算法（推荐） | 通用场景 |
| `compress=lzo` | 启用透明压缩，lzo 算法（快速） | 对性能敏感的场景 |
| `compress=zlib` | 启用透明压缩，zlib 算法（高压缩率） | 存储空间紧张 |
| `compress-force=zstd` | 强制压缩所有文件（包括已压缩文件） | 需要最大化压缩 |
| `ssd` | 启用 SSD 特性优化 | SSD/NVMe 设备 |
| `discard` | 启用在线 TRIM | SSD 设备（实时） |
| `nodiscard` | 禁用在线 TRIM | 机械硬盘或希望延迟TRIM |
| `noatime` | 禁用访问时间记录 | 通用推荐 |
| `relatime` | 相对时间记录（默认） | 通用 |
| `nodatacow` | 禁用数据 CoW | 数据库文件、虚拟机镜像 |
| `nodatasum` | 禁用数据校验和 | 非关键数据（不推荐） |
| `flushoncommit` | 每次提交都刷写 | 数据库（性能下降但更安全） |
| `max_inline=256` | 内联数据最大大小（字节） | 小文件优化 |
| `space_cache=v2` | 使用v2空间缓存 | 默认推荐 |
| `thread_pool=N` | I/O 线程池大小 | CPU核心数 |
| `autodefrag` | 自动碎片整理 | 桌面/笔记本使用 |

**按场景配置：**

```bash
# SSD 桌面系统
sudo mount -o compress=zstd,ssd,discard,noatime,autodefrag /dev/sdX1 /mnt

# HDD 服务器
sudo mount -o compress=zstd,noatime,nodiscard /dev/sdX1 /mnt

# 数据库/虚拟机（需要 nodatacow）
sudo mount -o compress=zstd,noatime,nodatacow,flushoncommit /dev/sdX1 /mnt

# NAS 存储
sudo mount -o compress=zstd,noatime,nodiscard /dev/sdX1 /mnt
```

### /etc/fstab 配置

```bash
# 首先获取 UUID
sudo blkid /dev/sdX1
# 输出示例: /dev/sdX1: UUID="a1b2c3d4-..." TYPE="btrfs" PARTUUID="..."

# 编辑 /etc/fstab
sudo nano /etc/fstab
```

**fstab 示例配置：**

```
# <设备>                    <挂载点>    <类型>  <选项>                                      <dump> <pass>
UUID=a1b2c3d4-e5f6-7890-   /           btrfs   defaults,noatime,compress=zstd,ssd,discard   0      0
UUID=a1b2c3d4-e5f6-7890-   /home       btrfs   subvol=@home,compress=zstd,noatime           0      0
UUID=a1b2c3d4-e5f6-7890-   /var/log    btrfs   subvol=@log,compress=zstd,noatime            0      0
UUID=a1b2c3d4-e5f6-7890-   /snapshots  btrfs   subvol=@snapshots,noatime                    0      0
```

**验证 fstab：**

```bash
sudo mount -a
mount | grep btrfs
df -hT | grep btrfs
```

---

## 子卷管理

### 子卷 vs 分区 vs 目录

Btrfs 子卷（subvolume）是一种独特的存储组织方式，与传统分区和普通目录有本质区别：

| 特性 | Btrfs 子卷 | 传统分区 | 普通目录 |
|------|-----------|----------|----------|
| 独立挂载点 | 是 | 是 | 否 |
| 独立快照 | 是 | 否 | 否 |
| 独立配额 | 是 | 是 | 否 |
| 创建时分配空间 | 否（按需） | 是 | 否 |
| 文件系统级操作 | 适用于整个设备 | 仅该分区 | 不适用 |
| 空间共享 | 与其他子卷共享 | 独占分区空间 | 在分区空间内 |
| 缩减大小 | 支持 | 支持（有限） | 不适用 |
| 增长大小 | 支持 | 支持 | 不适用 |

子卷的核心优势：

- **轻量级**：创建子卷几乎不消耗资源，无需预分配空间。
- **隔离性**：每个子卷可独立挂载、快照、设置配额。
- **灵活性**：可在运行时创建、删除、重命名子卷。
- **共享空间**：所有子卷共享同一个文件系统的可用空间。

### 布局设计（@, @home, @pkg, @log, @snapshots）

合理的子卷布局是 Btrfs 系统管理的关键。以下是推荐的布局设计：

```
根设备 (/dev/sdX1)
├── @              → 挂载到 /
├── @home          → 挂载到 /home
├── @pkg           → 挂载到 /var/cache/pacman/pkg (Arch) 或 /var/cache/apt (Debian)
├── @log           → 挂载到 /var/log
├── @snapshots     → 挂载到 /.snapshots
└── @swap          → swapfile（可选）
```

**创建子卷布局：**

```bash
# 挂载根设备到临时目录
sudo mount /dev/sdX1 /mnt

# 创建子卷
sudo btrfs subvolume create /mnt/@
sudo btrfs subvolume create /mnt/@home
sudo btrfs subvolume create /mnt/@log
sudo btrfs subvolume create /mnt/@snapshots

# 包管理器缓存目录（根据发行版选择）
sudo btrfs subvolume create /mnt/@pkg

# 移动现有数据到子卷（假设已安装系统）
sudo mv /mnt/var/log/* /mnt/@log/
sudo mv /mnt/.snapshots /mnt/@snapshots/

# 设置默认子卷为 @
sudo btrfs subvolume set-default $(sudo btrfs subvolume list /mnt | grep " path @" | awk '{print $2}') /mnt

# 卸载后重新挂载
sudo umount /mnt
sudo mount -o subvol=@,compress=zstd,noatime /dev/sdX1 /mnt
sudo mkdir -p /mnt/{home,var/log,.snapshots}
sudo mount -o subvol=@home,compress=zstd,noatime /dev/sdX1 /mnt/home
sudo mount -o subvol=@log,compress=zstd,noatime /dev/sdX1 /mnt/var/log
sudo mount -o subvol=@snapshots,noatime /dev/sdX1 /mnt/.snapshots
```

### 操作：create / list / delete / rename / get-default / set-default

```bash
# 创建子卷
sudo btrfs subvolume create /mnt/@test
# 创建子卷并指定用户/组
sudo btrfs subvolume create -u 1000 -g 1000 /mnt/@userdata

# 列出所有子卷
sudo btrfs subvolume list /mnt
# 输出示例:
# ID 256 gen 100 top level 5 path @
# ID 257 gen 95 top level 5 path @home
# ID 258 gen 80 top level 5 path @log
# ID 259 gen 60 top level 5 path @snapshots

# 详细列出（包含UUID等信息）
sudo btrfs subvolume list -a /mnt

# 删除子卷（必须先卸载）
sudo umount /mnt/@test
sudo btrfs subvolume delete /mnt/@test

# 批量删除
sudo btrfs subvolume delete /mnt/@snapshots/1 /mnt/@snapshots/2

# 重命名子卷
sudo btrfs subvolume rename /mnt/@oldname /mnt/@newname

# 查看默认子卷
sudo btrfs subvolume get-default /mnt
# 输出示例: ID 5 (哪条就是默认)

# 设置默认子卷
sudo btrfs subvolume set-default 256 /mnt
# 或通过路径
sudo btrfs subvolume set-default $(sudo btrfs subvolume list /mnt | grep " path @" | awk '{print $2}') /mnt

# 查看子卷属性
sudo btrfs subvolume show /mnt/@
# 输出包含: Name, UUID, Parent UUID, Generation, flags 等
```

### 子卷配额（qgroups）

Btrfs 子卷配额（quota groups，简称 qgroups）允许对子卷设置磁盘空间使用限制：

```bash
# 启用配额
sudo btrfs quota enable /mnt

# 禁用配额
sudo btrfs quota disable /mnt

# 查看配额状态
sudo btrfs quota rescan /mnt

# 为子卷设置配额（限制为10GB）
sudo btrfs qgroup limit 10G /mnt/@home

# 为子卷设置软限制（超过后仍可使用，但会警告）
sudo btrfs qgroup limit 10G --oshi /mnt/@home

# 查看子卷的配额限制
sudo btrfs qgroup show /mnt/@home

# 查看所有子卷的配额使用情况
sudo btrfs qgroup show -r /mnt

# 修改子卷配额
sudo btrfs qgroup limit 20G /mnt/@home

# 删除子卷配额
sudo btrfs qgroup limit none /mnt/@home
```

**qgroup 依赖关系：**

当子卷 A 是子卷 B 的父卷时，B 的配额会受到 A 的限制。使用 `-p` 参数可查看父子关系。

---

## 快照系统

### 只读快照 vs 读写快照

| 特性 | 只读快照 | 读写快照 |
|------|---------|---------|
| 创建命令 | `btrfs subvolume snapshot -r` | `btrfs subvolume snapshot` |
| 可修改 | 否 | 是 |
| 可挂载 | 是（只读） | 是（读写） |
| 用途 | 备份、回滚、发送 | 临时工作环境、测试 |
| 安全性 | 高（不可意外修改） | 中（可能被意外修改） |
| 创建速度 | 快 | 快 |
| 空间占用 | 仅差异数据 | 仅差异数据（修改后增加） |

### 手动快照

```bash
# 创建只读快照
sudo btrfs subvolume snapshot -r /mnt/@ /mnt/@snapshots/1

# 创建读写快照
sudo btrfs subvolume snapshot /mnt/@ /mnt/@snapshots/test

# 创建带时间戳的快照
sudo btrfs subvolume snapshot -r /mnt/@ /mnt/@snapshots/$(date +%Y%m%d-%H%M%S)

# 创建空子卷的快照（用于精确备份）
sudo btrfs subvolume snapshot -r /mnt/@ /mnt/@snapshots/empty-snapshot
```

### Snapper 自动快照（通用配置）

Snapper 是一个广泛使用的 Btrfs 快照管理工具，支持自动定时快照和清理策略：

**安装：**

```bash
# Debian / Ubuntu
sudo apt install snapper

# Fedora / RHEL
sudo dnf install snapper

# Arch Linux
sudo pacman -S snapper

# openSUSE（预装）
# 无需额外安装
```

**初始化配置（以根子卷为例）：**

```bash
# 为根子卷创建 Snapper 配置
sudo snapper -c root create-config /

# 查看配置文件
ls /etc/snapper/configs/

# 编辑配置
sudo nano /etc/snapper/configs/root
```

**Snapper 配置文件主要参数：**

```
# 子卷挂载点
SUBVOLUME="/"

# 文件系统挂载点（通常为 /）
FSTYPE="btrfs"

# 快照时间线配置
TIMELINE_CREATE="yes"
TIMELINE_LIMIT_HOURLY="5"
TIMELINE_LIMIT_DAILY="7"
TIMELINE_LIMIT_WEEKLY="0"
TIMELINE_LIMIT_MONTHLY="0"
TIMELINE_LIMIT_YEARLY="0"
TIMELINE_LIMIT_MIN_AGE="1800"

# 快照清理算法
TIMELINE_CLEANUP="yes"
NUMBER_LIMIT="10"
NUMBER_MIN_AGE="1800"
```

**启用时间线快照：**

```bash
# 启用时间线快照创建
sudo systemctl enable --now snapper-timeline.timer

# 启用时间线清理
sudo systemctl enable --now snapper-cleanup.timer

# 手动触发时间线快照
sudo snapper -c root timeline
```

**Snapper 快照操作：**

```bash
# 列出所有快照
sudo snapper -c root list

# 创建快照（带描述）
sudo snapper -c root create -d "Before system update"

# 创建只读快照
sudo snapper -c root create -r -d "Backup before kernel upgrade"

# 删除指定快照
sudo snapper -c root delete 5

# 清理旧快照
sudo snapper -c root cleanup timeline
sudo snapper -c root cleanup number
```

### 快照查看与比较

```bash
# 查看快照列表
sudo btrfs subvolume list /mnt | grep snapshots

# 查看快照详细信息
sudo btrfs subvolume show /mnt/@snapshots/1

# 比较两个快照的差异
sudo btrfs send -p /mnt/@snapshots/1 /mnt/@snapshots/2 > /dev/null
# 或使用 diff 工具
sudo btrfs diff /mnt/@snapshots/1 /mnt/@snapshots/2

# 使用 Snapper 查看快照差异
sudo snapper -c root status 4..5
sudo snapper -c root status 4..5 | less

# 查看快照的文件内容
sudo mount -o subvol=@snapshots/1,ro /dev/sdX1 /mnt/snap1
ls /mnt/snap1/
sudo umount /mnt/snap1

# 查看特定文件的历史
sudo snapper -c root status | grep "filename"
```

### 快照清理策略

```bash
# 基于数量的清理（保留最近10个）
sudo snapper -c root cleanup number

# 基于时间线的清理（保留配置中指定的时间范围）
sudo snapper -c root cleanup timeline

# 手动删除特定快照
sudo snapper -c root delete 1 2 3

# 批量删除指定范围的快照
for i in $(seq 1 5); do
    sudo snapper -c root delete $i
done

# 查看快照占用空间
sudo btrfs qgroup show -r /mnt/@snapshots
```

---

## 系统回滚

### 手动回滚流程

系统回滚是 Btrfs 最有价值的功能之一。手动回滚流程如下：

```bash
# 1. 卸载所有子卷
sudo umount -R /mnt

# 2. 检查文件系统（可选但推荐）
sudo btrfs check /dev/sdX1

# 3. 重新挂载根子卷
sudo mount /dev/sdX1 /mnt

# 4. 确认要回滚的快照
sudo btrfs subvolume list /mnt
sudo snapper -c root list

# 5. 删除当前根子卷
sudo btrfs subvolume delete /mnt/@

# 6. 将只读快照转换为可写
sudo btrfs subvolume set-default 0 /mnt/@snapshots/1
sudo btrfs subvolume snapshot -r /mnt/@ /mnt/@old-root
sudo btrfs subvolume delete /mnt/@
sudo btrfs subvolume set-default 0 /mnt/@snapshots/1

# 7. 重命名快照为新的根子卷
sudo btrfs subvolume rename /mnt/@snapshots/1 /mnt/@

# 8. 更新 fstab 中的子卷 ID（如有必要）
sudo nano /mnt/etc/fstab

# 9. 卸载并重新挂载
sudo umount /mnt
sudo mount -o subvol=@ /dev/sdX1 /mnt

# 10. 验证回滚结果
sudo btrfs subvolume list /mnt
ls /mnt/
```

### snapper rollback

Snapper 提供了一键回滚功能，大大简化了回滚操作：

```bash
# 查看可用的回滚快照
sudo snapper -c root list

# 执行回滚（仅适用于根子卷的默认快照）
sudo snapper -c root rollback

# 回滚后重启
sudo reboot
```

**snapper rollback 的限制：**

- 仅能回滚到时间线快照中的上一个快照。
- 回滚操作会创建一个新的快照，记录回滚后的状态。
- 回滚前会自动创建当前状态的快照。

### GRUB 快照启动菜单

通过 `grub-btrfs` 和 `snap-pac-grub` 可以在 GRUB 启动菜单中直接选择快照启动：

**安装（以 Arch Linux 为例，其他发行版类似）：**

```bash
# Arch Linux
sudo pacman -S grub-btrfs snap-pac-grub

# Ubuntu / Debian
sudo apt install grub-btrfs

# Fedora
sudo dnf install grub-btrfs
```

**配置：**

```bash
# 编辑 grub-btrfs 配置
sudo nano /etc/default/grub-btrfs/config
# 主要选项:
# GRUB_BTRFS_SNAPSHOT_KERNEL_PARAMETERS="..."
# GRUB_BTRFS_SNAPSHOT_TITTLE="Snapshot: %s"

# 更新 GRUB
sudo grub-mkconfig -o /boot/grub/grub.cfg
# 或 Ubuntu/Debian:
sudo update-grub
```

**自动集成（snap-pac-grub）：**

```bash
# 安装后自动生效
# 每次创建快照时，自动更新 GRUB 菜单

# 手动更新 GRUB 菜单
sudo grub-mkconfig -o /boot/grub/grub.cfg
```

### 误删文件恢复

```bash
# 方法1：从快照恢复单个文件
# 找到包含被删文件的快照
sudo snapper -c root list

# 挂载快照
sudo mount -o subvol=@snapshots/5,ro /dev/sdX1 /mnt/snap

# 复制文件回原位
sudo cp /mnt/snap/path/to/deleted/file /mnt/@/path/to/

# 卸载快照
sudo umount /mnt/snap

# 方法2：使用 btrfs restore（文件系统损坏时使用）
# 在 Live USB 或另一个系统上执行
sudo btrfs restore -s -S /dev/sdX1 /mnt/recovery
# -s: 恢复快照
# -S: 恢复子卷
```

---

## 增量备份

### btrfs send / receive

`btrfs send` 和 `btrfs receive` 是 Btrfs 增量备份的核心工具：

```bash
# 全量发送快照
sudo btrfs send /mnt/@snapshots/1 | sudo btrfs receive /backup/

# 将发送的快照挂载查看
sudo mount -o subvol=1,ro /backup/ /mnt/backup-snap
ls /mnt/backup-snap/
sudo umount /mnt/backup-snap
```

### 增量传输原理（-p 参数）

增量传输使用 `-p` 参数指定父快照，仅传输两个快照之间的差异：

```bash
# 第一次全量发送
sudo btrfs send /mnt/@snapshots/1 | sudo btrfs receive /backup/

# 后续增量发送（仅传输差异）
sudo btrfs send -p /mnt/@snapshots/1 /mnt/@snapshots/2 | sudo btrfs receive /backup/

# 继续增量发送
sudo btrfs send -p /mnt/@snapshots/2 /mnt/@snapshots/3 | sudo btrfs receive /backup/
```

**增量传输的工作原理：**

1. `btrfs send` 比较父快照和当前快照的 B-tree 结构。
2. 仅生成两个快照之间发生变化的数据块列表。
3. 发送变化的数据块和元数据更新。
4. `btrfs receive` 在目标设备上应用这些变化，重建目标快照。

**增量传输的优势：**

- 只传输变化的数据，大幅减少备份时间和带宽消耗。
- 不需要全量复制，适合大规模数据的定期备份。
- 传输过程中保持数据完整性。

### 定时增量备份脚本

```bash
#!/bin/bash
# btrfs-backup.sh - Btrfs 增量备份脚本

# 配置
SOURCE_SUBVOL="/mnt/@"
SNAPSHOT_DIR="/mnt/@snapshots"
BACKUP_DEVICE="/dev/sdY1"
BACKUP_MOUNT="/backup"
MAX_SNAPSHOTS=10

# 创建时间戳快照
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
NEW_SNAP="${SNAPSHOT_DIR}/${TIMESTAMP}"
sudo btrfs subvolume snapshot -r "${SOURCE_SUBVOL}" "${NEW_SNAP}"

# 挂载备份设备
sudo mkdir -p "${BACKUP_MOUNT}"
sudo mount "${BACKUP_DEVICE}" "${BACKUP_MOUNT}"

# 查找上一个快照作为增量基准
LATEST_SNAP=$(sudo btrfs subvolume list "${SNAPSHOT_DIR}" | awk -v dir="${SNAPSHOT_DIR}/" '$NF ~ dir {print $NF}' | sort -n | tail -1)

if [ -n "${LATEST_SNAP}" ] && [ "${LATEST_SNAP}" != "${NEW_SNAP}" ]; then
    # 增量发送
    sudo btrfs send -p "${LATEST_SNAP}" "${NEW_SNAP}" | sudo btrfs receive "${BACKUP_MOUNT}"
else
    # 全量发送
    sudo btrfs send "${NEW_SNAP}" | sudo btrfs receive "${BACKUP_MOUNT}"
fi

# 清理旧快照（保留最近 MAX_SNAPSHOTS 个）
sudo btrfs subvolume list -a "${SNAPSHOT_DIR}" | awk '{print $NF}' | sort -n | head -n -${MAX_SNAPSHOTS} | while read -r snap; do
    if [ -n "${snap}" ]; then
        sudo btrfs subvolume delete "${snap}"
    fi
done

# 卸载备份设备
sudo umount "${BACKUP_MOUNT}"

echo "Backup completed at $(date)"
```

**设置定时任务：**

```bash
# 添加可执行权限
chmod +x /path/to/btrfs-backup.sh

# 编辑 crontab
sudo crontab -e

# 每天凌晨2点执行备份
0 2 * * * /path/to/btrfs-backup.sh >> /var/log/btrfs-backup.log 2>&1

# 每6小时执行一次
0 */6 * * * /path/to/btrfs-backup.sh >> /var/log/btrfs-backup.log 2>&1
```

### 与 rsync 对比

| 特性 | btrfs send/receive | rsync |
|------|-------------------|-------|
| 增量传输 | 原生支持 | 仅基于文件差异 |
| 传输粒度 | 块级别 | 文件级别 |
| 传输速度 | 快（块级差异） | 中等（需要逐文件比较） |
| 元数据保留 | 完整保留 | 有限保留 |
| 快照兼容 | 原生支持 | 不支持 |
| 压缩传输 | 可配合管道使用 | 支持（-z 参数） |
| 网络传输 | 需配合 SSH | 原生支持 |
| 跨文件系统 | 仅 Btrfs | 任意文件系统 |
| 适用场景 | Btrfs 系统间备份 | 通用文件同步 |

---

## RAID 配置

### RAID 0 / 1 / 10 配置

```bash
# RAID 0 - 条带化，需要至少2个设备
sudo mkfs.btrfs -d raid0 -m raid0 /dev/sdX1 /dev/sdY1

# RAID 1 - 镜像，需要至少2个设备
sudo mkfs.btrfs -d raid1 -m raid1 /dev/sdX1 /dev/sdY1

# RAID 10 - 镜像+条带化，需要至少4个设备
sudo mkfs.btrfs -d raid10 -m raid10 /dev/sdX1 /dev/sdY1 /dev/sdZ1 /dev/sdW1

# 混合RAID - 元数据镜像，数据单盘
sudo mkfs.btrfs -d single -m raid1 /dev/sdX1 /dev/sdY1

# 三副本模式
sudo mkfs.btrfs -d raid1c3 -m raid1c3 /dev/sdX1 /dev/sdY1 /dev/sdZ1

# 查看RAID信息
sudo btrfs filesystem show /mnt
```

### RAID 5 / 6 的风险警告

**重要警告：Btrfs RAID 5/6 目前不建议用于生产环境。**

```bash
# RAID 5 - 有已知的write hole问题
sudo mkfs.btrfs -d raid5 -m raid5 /dev/sdX1 /dev/sdY1 /dev/sdZ1

# RAID 6 - 同样存在稳定性问题
sudo mkfs.btrfs -d raid6 -m raid6 /dev/sdX1 /dev/sdY1 /dev/sdZ1 /dev/sdW1
```

**已知问题：**

1. **Write Hole**：在断电或崩溃时，RAID 5/6 可能出现部分写入不一致。
2. **数据丢失风险**：在某些故障场景下，可能导致无法恢复的数据丢失。
3. **性能不稳定**：在高负载下可能出现性能问题。
4. **社区状态**：虽然持续开发中，但尚未达到生产稳定性。

**建议：**

- 使用 RAID 1 或 RAID 10 代替 RAID 5/6。
- 如果需要 RAID 5/6 的空间效率，考虑使用 LVM + RAID 的组合方案。

### 多设备管理（add / remove / replace / balance）

```bash
# 添加新设备
sudo btrfs device add /dev/sdZ1 /mnt

# 移除设备（需要先 balance）
sudo btrfs device remove /dev/sdY1 /mnt

# 替换设备（在线替换）
sudo btrfs device replace start /dev/sdY1 /dev/sdZ1 /mnt

# 查看替换进度
sudo btrfs device replace status /mnt

# 数据再平衡（将数据分布到所有设备）
sudo btrfs balance start /mnt

# 分步balance（避免一次性操作占用过多资源）
sudo btrfs balance start -dusage=0-50 /mnt
sudo btrfs balance start -dusage=50-75 /mnt
sudo btrfs balance start -dusage=75-100 /mnt

# 查看balance进度
sudo btrfs balance status /mnt

# 限制balance操作的设备和块组
sudo btrfs balance start -dconvert=raid1 /mnt
sudo btrfs balance start -mconvert=raid1 /mnt
```

### 设备故障处理流程

```bash
# 1. 检查设备状态
sudo btrfs device stats /mnt
# 输出包含每个设备的错误计数

# 2. 检查RAID冗余状态
sudo btrfs filesystem show /mnt
# 查看 missing 标记的设备

# 3. 如果设备完全故障
sudo btrfs device remove missing /mnt

# 4. 添加新设备替换故障设备
sudo btrfs device add /dev/sdZ1 /mnt

# 5. 重新平衡数据到新设备
sudo btrfs balance start /mnt

# 6. 验证恢复状态
sudo btrfs filesystem show /mnt
sudo btrfs device stats /mnt
```

**设备故障预防措施：**

```bash
# 定期检查设备健康状态
sudo smartctl -a /dev/sdX

# 监控设备错误计数
sudo btrfs device stats /mnt

# 设置错误阈值告警
while true; do
    errors=$(sudo btrfs device stats /mnt | grep -c "error")
    if [ "$errors" -gt 0 ]; then
        echo "WARNING: Device errors detected!"
        sudo btrfs device stats /mnt
    fi
    sleep 3600
done
```

---

## 压缩

### 算法选择

Btrfs 支持三种透明压缩算法：

```bash
# zstd - 推荐（平衡压缩率和性能）
sudo mount -o compress=zstd /dev/sdX1 /mnt

# lzo - 快速压缩
sudo mount -o compress=lzo /dev/sdX1 /mnt

# zlib - 最高压缩率
sudo mount -o compress=zlib /dev/sdX1 /mnt

# 强制压缩所有文件（包括已压缩文件）
sudo mount -o compress-force=zstd /dev/sdX1 /mnt
```

### 压缩率 vs 性能对比

| 算法 | 压缩率 | CPU 开销 | 速度 | 适用场景 |
|------|--------|----------|------|----------|
| zstd | 高（约60-70%） | 中等 | 快 | 通用推荐 |
| lzo | 中等（约50-60%） | 低 | 非常快 | 性能敏感场景 |
| zlib | 最高（约70-80%） | 高 | 慢 | 存储空间紧张 |

**实际测试参考：**

```bash
# 测试压缩效果
dd if=/dev/urandom of=/tmp/testfile bs=1M count=100

# 复制到 Btrfs 卷（启用压缩）
cp /tmp/testfile /mnt/compressed/

# 查看实际占用空间
du -h /mnt/compressed/testfile
sudo btrfs filesystem du /mnt/compressed/testfile
```

### 按文件/目录禁用 CoW

某些工作负载（如数据库、虚拟机磁盘）不适合 CoW，可以禁用：

```bash
# 禁用单个文件的 CoW
sudo chattr +C /path/to/file

# 禁用目录的 CoW（目录下新建文件也会继承）
sudo chattr +C /path/to/directory/

# 查看属性
lsattr /path/to/file
# 输出: ---------------C /path/to/file

# 注意：对已存在的数据无效，需要在写入前设置
# 正确流程:
mkdir /mnt/vms
sudo chattr +C /mnt/vms
# 然后将虚拟机磁盘文件放入此目录
```

### 透明压缩效果

```bash
# 查看压缩统计信息
sudo btrfs filesystem defragment -r -czstd /mnt/@

# 查看单个文件的压缩效果
sudo btrfs inspect-internal file-extents /path/to/file

# 使用文件系统统计查看压缩率
sudo btrfs filesystem df /mnt
```

---

## 维护任务

### Scrub（数据完整性校验）

Scrub 是 Btrfs 的数据完整性校验机制，会主动读取并验证所有数据和元数据的校验和：

```bash
# 启动 scrub
sudo btrfs scrub start /mnt

# 查看 scrub 状态
sudo btrfs scrub status /mnt
# 输出示例:
# UUID:             a1b2c3d4-...
# Scrub started:    Mon Sep  1 10:00:00 2025
# Status:           finished
# Duration:         0:15:23
# Total to scrub:   100.00GB
# Rate:             110.00MB/s
# Error summary:    no errors found

# 取消正在进行的 scrub
sudo btrfs scrub cancel /mnt

# 重新运行 scrub
sudo btrfs scrub start -B /mnt
# -B: 前台运行
```

**定期 Scrub 配置：**

```bash
# 启用 scrub 定时器（systemd）
sudo systemctl enable --now btrfs-scrub@-.timer

# 或手动设置 crontab
# 每周日凌晨3点执行 scrub
0 3 * * 0 /usr/bin/btrfs scrub start /mnt >> /var/log/btrfs-scrub.log 2>&1
```

### Balance（数据块再平衡）

Balance 操作将数据块重新分布到所有设备，常用于添加/移除设备后：

```bash
# 完全 balance（可能耗时很长）
sudo btrfs balance start /mnt

# 分步 balance（推荐）
sudo btrfs balance start -dusage=0-50 /mnt
sudo btrfs balance start -dusage=50-75 /mnt
sudo btrfs balance start -dusage=75-100 /mnt

# 仅 balance 元数据
sudo btrfs balance start -m /mnt

# 转换RAID级别
sudo btrfs balance start -dconvert=raid1 /mnt
sudo btrfs balance start -mconvert=raid1 /mnt

# 查看 balance 状态
sudo btrfs balance status /mnt

# 取消 balance
sudo btrfs balance cancel /mnt
```

### 碎片整理

Btrfs 的碎片整理是可选的，主要用于改善机械硬盘的顺序读取性能：

```bash
# 整理整个文件系统
sudo btrfs filesystem defragment -r /mnt

# 整理并应用压缩
sudo btrfs filesystem defragment -r -czstd /mnt

# 整理单个文件
sudo btrfs filesystem defragment /mnt/path/to/file

# 整理指定范围（从偏移量1GB开始，长度100MB）
sudo btrfs filesystem defragment -r -c zstd -cl 100M -o 1G /mnt

# 查看碎片信息
sudo btrfs inspect-internal file-extents /mnt/path/to/file
```

**碎片整理注意事项：**

- SSD 上通常不需要碎片整理。
- 碎片整理会增加 CoW 写放大。
- 对于启用压缩的文件系统，碎片整理可以提高压缩率。
- 建议在低负载时段执行。

### 磁盘空间回收

```bash
# 重新声明未使用的空间
sudo btrfs filesystem reclaim /mnt

# 查看文件系统使用情况
sudo btrfs filesystem usage /mnt

# 查看详细的空间分配信息
sudo btrfs filesystem df -m /mnt
sudo btrfs filesystem df -d /mnt

# 删除不需要的快照以回收空间
sudo btrfs subvolume delete /mnt/@snapshots/old-snapshot

# 清理已删除子卷的残留引用
sudo btrfs subvolume sync /mnt
```

---

## 性能调优

### SSD 优化挂载选项

```bash
# SSD 完整优化配置
sudo mount -o compress=zstd,ssd,discard,noatime,space_cache=v2 /dev/sdX1 /mnt

# NVMe 优化
sudo mount -o compress=zstd,ssd,discard,noatime,space_cache=v2,thread_pool=8 /dev/sdX1 /mnt

# 验证 SSD 优化状态
lsblk -d -o name,rota
# rota=0 表示 SSD
sudo cat /sys/block/sdX/queue/rotational
# 0=SSD, 1=HDD
```

### 日志模式

```bash
# 默认模式（安全但较慢）
sudo mount -o flushoncommit /dev/sdX1 /mnt

# 异步日志模式（性能更好但有风险）
sudo mount -o flushoncommit,nodatacow /dev/sdX1 /mnt

# 禁用数据校验和（极端性能场景，不推荐）
sudo mount -o nodatasum /dev/sdX1 /mnt

# 日志模式详细说明:
# - 默认模式: 元数据和数据都使用 CoW，最安全
# - flushoncommit: 每次提交都刷写到磁盘，减少延迟
# - nodatacow: 数据不再使用 CoW，提高数据库性能
# - nodatasum: 禁用数据校验和，最高性能但不安全
```

### fio 基准测试方法

```bash
# 安装 fio
sudo apt install fio  # Debian/Ubuntu
sudo dnf install fio  # Fedora
sudo pacman -S fio    # Arch

# 顺序读测试
fio --name=seq-read --ioengine=libaio --direct=1 --bs=1M \
    --rw=read --size=1G --numjobs=1 --runtime=60 \
    --group_reporting --filename=/mnt/testfile

# 顺序写测试
fio --name=seq-write --ioengine=libaio --direct=1 --bs=1M \
    --rw=write --size=1G --numjobs=1 --runtime=60 \
    --group_reporting --filename=/mnt/testfile

# 随机读测试
fio --name=rand-read --ioengine=libaio --direct=1 --bs=4K \
    --rw=randread --size=1G --numjobs=4 --runtime=60 \
    --group_reporting --filename=/mnt/testfile

# 随机写测试
fio --name=rand-write --ioengine=libaio --direct=1 --bs=4K \
    --rw=randwrite --size=1G --numjobs=4 --runtime=60 \
    --group_reporting --filename=/mnt/testfile

# 混合读写测试
fio --name=mixed --ioengine=libaio --direct=1 --bs=4K \
    --rw=randrw --rwmixread=70 --size=1G --numjobs=4 \
    --runtime=60 --group_reporting --filename=/mnt/testfile

# 清理测试文件
rm -f /mnt/testfile
```

---

## 救援与恢复

### btrfs check

```bash
# 只读检查（推荐）
sudo btrfs check /dev/sdX1

# 修复模式（有风险，先备份）
sudo btrfs check --repair /dev/sdX1

# 初始化 Chunk Tree（仅在无法挂载时使用）
sudo btrfs check --init-extent-tree /dev/sdX1
```

**btrfs check 输出示例：**

```
Opening filesystem to check...
Checking filesystem on /dev/sdX1
UUID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
[1/7] checking root items
[2/7] checking extents
[3/7] checking free space cache
[4/7] checking fs roots
[5/7] checking only csums items (without verifying data)
[6/7] checking root refs
[7/7] checking quota groups (incompatible subvolume flag)
No errors found in filesystem
```

### btrfs rescue

```bash
# 恢复损坏的 superblock
sudo btrfs rescue super-recover /dev/sdX1

# 清除日志（用于修复日志损坏）
sudo btrfs rescue zero-log /dev/sdX1

# 重建 Chunk Tree
sudo btrfs rescue chunk-recover /dev/sdX1

# 清除恢复标志
sudo btrfs rescue clear-convert-cache /dev/sdX1

# 恢复已删除的文件（需要未被覆写的磁盘区域）
sudo btrfs rescue段 restore -s /dev/sdX1 /mnt/recovery
```

### btrfs restore（文件系统损坏时数据提取）

当文件系统损坏无法挂载时，可以使用 `btrfs restore` 提取数据：

```bash
# 基本恢复（需要从另一个系统或 Live USB 执行）
sudo btrfs restore /dev/sdX1 /mnt/recovery

# 恢复所有内容（包括快照和子卷）
sudo btrfs restore -s -S /dev/sdX1 /mnt/recovery

# 恢复指定子卷
sudo btrfs restore -S -i 256 /dev/sdX1 /mnt/recovery

# 恢复指定快照
sudo btrfs restore -s -i 257 /dev/sdX1 /mnt/recovery

# 恢复并覆盖已有文件
sudo btrfs restore -f /dev/sdX1 /mnt/recovery
```

**btrfs restore 参数说明：**

| 参数 | 说明 |
|------|------|
| `-s` | 恢复快照 |
| `-S` | 恢复所有子卷 |
| `-i <id>` | 恢复指定ID的子卷 |
| `-f` | 覆盖已有文件 |
| `-o <offset>` | 从指定偏移量开始恢复 |
| `-l <length>` | 恢复指定长度 |
| `-x` | 仅恢复可执行文件 |
| `-c` | 仅恢复配置文件 |

### 常见故障场景与处理流程

**场景1：文件系统无法挂载**

```bash
# 1. 检查文件系统
sudo btrfs check /dev/sdX1

# 2. 尝试修复
sudo btrfs check --repair /dev/sdX1

# 3. 如果仍然无法挂载，尝试 rescue
sudo btrfs rescue super-recover /dev/sdX1

# 4. 如果还是不行，使用 restore 提取数据
sudo btrfs restore /dev/sdX1 /mnt/recovery
```

**场景2：设备离线**

```bash
# 1. 检查设备状态
sudo btrfs device stats /mnt

# 2. 标记设备为离线
sudo btrfs device remove missing /mnt

# 3. 添加新设备
sudo btrfs device add /dev/sdZ1 /mnt

# 4. 重新平衡
sudo btrfs balance start /mnt
```

**场景3：空间耗尽**

```bash
# 1. 检查空间使用
sudo btrfs filesystem usage /mnt

# 2. 查看哪些子卷占用最多空间
sudo btrfs qgroup show -r /mnt

# 3. 清理不需要的快照
sudo snapper -c root cleanup number

# 4. 删除临时文件
sudo find /tmp -type f -mtime +7 -delete

# 5. 如果使用了配额，检查限制
sudo btrfs qgroup show /mnt
```

---

## Btrfs vs LVM 对比

### 功能对比表

| 功能 | Btrfs | LVM + ext4/XFS |
|------|-------|----------------|
| 快照 | 原生支持，开销低 | 支持，开销中等 |
| 压缩 | 透明压缩 | 不支持（需单独配置） |
| 子卷 | 原生支持 | 不支持（需要逻辑卷） |
| RAID | 内建软件 RAID | 需要 mdadm |
| 在线扩容 | 支持 | 支持 |
| 在线缩减 | 支持 | 部分支持 |
| 在线碎片整理 | 支持 | 支持 |
| 数据校验 | 全量校验和 | 仅元数据 |
| 多设备管理 | 内建支持 | LVM 原生支持 |
| 条带化 | RAID 0/10 | lvextend + 条带化 |
| 镜像 | RAID 1 | lvconvert --mirror |
| 精简配置 | 不支持 | 支持（thin provisioning） |
| VDO 压缩 | 不支持 | 支持（vdo） |
| 成熟度 | 中等 | 非常成熟 |
| 数据恢复 | 有工具但复杂 | 工具成熟，相对容易 |
| 性能 | 中等（CoW开销） | 较高（就地写入） |

### 选型建议

**选择 Btrfs 的场景：**

- 需要频繁的快照功能（如系统回滚、开发环境管理）。
- 需要透明压缩以节省存储空间。
- 需要子卷隔离（如独立的日志、缓存目录）。
- 桌面系统或开发工作站。
- NAS 存储（如 TrueNAS、openMediaVault）。
- 对数据完整性有较高要求。

**选择 LVM + ext4/XFS 的场景：**

- 企业级生产环境（追求极致稳定性）。
- 数据库服务器（需要避免 CoW 写放大）。
- 大规模存储系统（需要精简配置和快照）。
- 虚拟化主机（KVM、VMware 等）。
- 对性能要求极高的 I/O 密集型工作负载。
- 需要跨多个物理设备灵活管理存储。

**混合使用方案：**

```bash
# LVM 提供设备管理，Btrfs 提供文件系统功能
sudo pvcreate /dev/sdX1
sudo vgcreate vg0 /dev/sdX1
sudo lvcreate -L 100G -n lv_root vg0
sudo lvcreate -L 50G -n lv_home vg0

sudo mkfs.btrfs /dev/vg0/lv_root
sudo mkfs.btrfs /dev/vg0/lv_home

sudo mount /dev/vg0/lv_root /mnt
sudo mount /dev/vg0/lv_home /mnt/home
```

---

## 生产环境最佳实践

### 监控与告警

```bash
# 1. 设备错误监控
#!/bin/bash
# btrfs-monitor.sh
LOG_FILE="/var/log/btrfs-monitor.log"
MOUNT_POINT="/mnt"

while true; do
    # 检查设备错误
    ERRORS=$(sudo btrfs device stats "$MOUNT_POINT" 2>&1 | grep -c "error")

    # 检查空间使用
    USAGE=$(sudo btrfs filesystem usage "$MOUNT_POINT" | grep "Overall" | awk '{print $2}' | tr -d '%')

    # 检查 scrub 状态
    SCRUB_STATUS=$(sudo btrfs scrub status "$MOUNT_POINT" | grep "Status" | awk '{print $2}')

    if [ "$ERRORS" -gt 0 ]; then
        echo "$(date): CRITICAL - Device errors detected!" >> "$LOG_FILE"
        sudo btrfs device stats "$MOUNT_POINT" >> "$LOG_FILE"
        # 发送告警（邮件、短信等）
    fi

    if [ "$USAGE" -gt 85 ]; then
        echo "$(date): WARNING - Disk usage at ${USAGE}%" >> "$LOG_FILE"
        # 发送告警
    fi

    sleep 3600
done
```

**Systemd 服务配置：**

```ini
# /etc/systemd/system/btrfs-monitor.service
[Unit]
Description=Btrfs Filesystem Monitor
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/btrfs-monitor.sh
Restart=always
RestartSec=3600

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now btrfs-monitor.service
```

### 备份策略

**3-2-1 备份原则：**

- **3** 份数据副本（生产数据 + 2份备份）。
- **2** 种不同的存储介质（如本地 + 远程）。
- **1** 份异地备份。

**推荐备份方案：**

```bash
# 本地备份：每日增量备份
#!/bin/bash
# daily-backup.sh
SOURCE="/mnt/@"
SNAPSHOT_DIR="/mnt/@snapshots/daily"
BACKUP_DIR="/backup/local"

# 创建每日快照
sudo btrfs subvolume snapshot -r "$SOURCE" "${SNAPSHOT_DIR}/$(date +%Y%m%d)"

# 增量发送到备份
PREV_SNAP=$(ls -d ${SNAPSHOT_DIR}/* | sort | tail -2 | head -1)
CURR_SNAP=$(ls -d ${SNAPSHOT_DIR}/* | sort | tail -1)

if [ -n "$PREV_SNAP" ]; then
    sudo btrfs send -p "$PREV_SNAP" "$CURR_SNAP" | sudo btrfs receive "$BACKUP_DIR"
else
    sudo btrfs send "$CURR_SNAP" | sudo btrfs receive "$BACKUP_DIR"
fi
```

```bash
# 远程备份：每周增量备份
#!/bin/bash
# weekly-remote.sh
SOURCE="/mnt/@snapshots/weekly"
REMOTE_USER="backup"
REMOTE_HOST="backup.example.com"
REMOTE_PATH="/backup/$(hostname)"

# 创建每周快照
sudo btrfs subvolume snapshot -r /mnt/@ "$SOURCE/$(date +%Y%m%d)"

# 发送到远程
sudo btrfs send "$SOURCE/$(date +%Y%m%d)" | \
    ssh "$REMOTE_USER@$REMOTE_HOST" "sudo btrfs receive $REMOTE_PATH"
```

### 容量规划

**空间计算：**

```bash
# 查看文件系统整体使用情况
sudo btrfs filesystem usage /mnt

# 查看各子卷使用情况
sudo btrfs subvolume list -a /mnt | while read line; do
    subvol=$(echo "$line" | awk '{print $NF}')
    echo "$subvol: $(sudo btrfs subvolume show "$subvol" | grep "Quota group" || echo "N/A")"
done

# 查看快照占用空间
sudo btrfs qgroup show -r /mnt

# 预留空间（建议保留至少20%用于平衡和维护）
echo "建议预留空间: $(sudo btrfs filesystem usage /mnt | grep "Unalloc" | head -1)"
```

**容量规划建议：**

| 使用场景 | 建议预留空间 | 说明 |
|----------|------------|------|
| 桌面系统 | 20-30% | 用于快照和碎片整理 |
| 服务器 | 20-40% | 根据快照频率和数据增长率调整 |
| NAS 存储 | 30-50% | 大量快照和备份需要空间 |
| 开发工作站 | 25-35% | 频繁的构建和测试 |

**监控脚本示例：**

```bash
#!/bin/bash
# capacity-check.sh
MOUNT_POINT="/mnt"
WARNING_THRESHOLD=80
CRITICAL_THRESHOLD=90

USAGE=$(df "$MOUNT_POINT" | tail -1 | awk '{print $5}' | tr -d '%')

if [ "$USAGE" -ge "$CRITICAL_THRESHOLD" ]; then
    echo "CRITICAL: Disk usage at ${USAGE}% on ${MOUNT_POINT}"
    exit 2
elif [ "$USAGE" -ge "$WARNING_THRESHOLD" ]; then
    echo "WARNING: Disk usage at ${USAGE}% on ${MOUNT_POINT}"
    exit 1
else
    echo "OK: Disk usage at ${USAGE}% on ${MOUNT_POINT}"
    exit 0
fi
```

---

## 总结

Btrfs 是一个功能丰富的现代文件系统，提供了传统文件系统无法比拟的高级功能。通过本章的学习，你应该掌握：

1. **核心原理**：CoW、B-tree、校验和的工作机制。
2. **创建与挂载**：如何创建 Btrfs 文件系统并配置合适的挂载选项。
3. **子卷管理**：如何设计子卷布局并进行日常管理。
4. **快照系统**：如何创建、管理和使用快照。
5. **系统回滚**：如何在系统故障时快速恢复。
6. **增量备份**：如何使用 btrfs send/receive 进行高效备份。
7. **RAID 配置**：如何配置软件 RAID 并管理多设备。
8. **压缩**：如何选择和使用透明压缩。
9. **维护任务**：如何执行 scrub、balance 和碎片整理。
10. **性能调优**：如何优化 Btrfs 性能。
11. **救援与恢复**：如何处理常见的文件系统故障。
12. **生产实践**：如何在生产环境中安全使用 Btrfs。

**关键要点：**

- Btrfs 适合需要快照、压缩、子卷管理的场景，但不建议用于 RAID 5/6。
- 定期执行 scrub 和 balance 是保持文件系统健康的关键。
- 合理的子卷布局和备份策略是生产环境使用的基础。
- 始终在测试环境中验证配置，再应用到生产环境。
- 监控磁盘使用情况和设备健康状态，及时发现潜在问题。

通过合理的配置和维护，Btrfs 可以为你的系统提供强大的数据保护和管理能力，成为现代 Linux 存储解决方案的重要组成部分。
