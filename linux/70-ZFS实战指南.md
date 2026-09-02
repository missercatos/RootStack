# 70 - ZFS 实战指南

> ZFS 是一个集文件系统与卷管理于一体的存储平台，以数据完整性、简洁的管理模型和强大的功能集著称。本章从安装到调优，全面覆盖 Linux 下 ZFS 的实战使用。

---

## ZFS 概述

### 为什么选择 ZFS

传统存储方案需要分别管理 RAID 控制器、LVM 逻辑卷和文件系统（ext4/XFS），每一层都有各自的局限。ZFS 将这三层合并为一个统一的存储栈，消除了层间信息丢失的问题，从根本上提升了数据可靠性。

ZFS 最初由 Sun Microsystems 开发，后随 OpenSolaris 开源。在 Linux 上，OpenZFS 项目（最初称为 ZFS on Linux，简称 ZoL）将其移植并持续维护，目前已支持 Linux 5.x/6.x 内核，成为 Linux 生产环境中广泛使用的存储方案。

### 核心特性

| 特性 | 说明 |
|------|------|
| **端到端校验和** | 每个数据块和元数据块都存储校验和（fletcher4 / SHA-256），自动检测并修复静默数据损坏（bit rot） |
| **Copy-on-Write** | 写入不覆盖原数据，原子性更新保证崩溃一致性，无需 fsck |
| **快照与克隆** | 几乎零开销创建文件系统快照，支持回滚、克隆和增量复制 |
| **透明压缩** | 内建 lz4、zstd、gzip 压缩，对应用透明，可提升 I/O 吞吐量 |
| **校验和 + RAID-Z** | 软件 RAID 替代硬件 RAID，支持 RAID-Z1/2/3，消除 RAID-5 写洞问题 |
| **SEND/RECEIVE** | 文件系统级增量备份，可用于异地容灾和数据迁移 |
| **精简配置** | 按需分配空间，支持配额、预留、去重（实验性） |
| **在线扩容** | 支持 vdev 横向扩展和设备替换，支持在线扩容池 |

### 许可证问题（CDDL vs GPL）

ZFS 的原始许可证是 CDDL（Common Development and Distribution License），与 Linux 内核的 GPL 不兼容。这导致 ZFS 不能直接合入主线内核。

在实际使用中，这意味着：

- **二进制分发**：通过 DKMS 方式在用户空间编译内核模块，多数发行版认为这不违反 GPL
- **自用编译**：自行编译加载 ZFS 内核模块完全合法
- **Canonical / Ubuntu**：官方仓库提供 ZFS 内核模块，被视为合规
- **Red Hat / Fedora**：出于 GPL 兼容性顾虑，不在官方仓库提供 ZFS 模块

如果你对许可证有严格要求，需自行评估风险。对于自用和企业内部部署， CDDL + DKMS 方式在实践中被广泛接受。

---

## 安装

### Ubuntu / Debian

```bash
# 安装 ZFS 内核模块和工具
sudo apt install zfsutils-linux

# 验证安装
modprobe zfs
zfs version

# DKMS 确保内核升级后自动编译
dkms status | grep zfs
```

Ubuntu 官方仓库直接维护 ZFS 包，是最简单的安装方式。

### Fedora / RHEL

Fedora/RHEL 默认不提供 ZFS 模块（GPL 兼容性），需手动添加第三方仓库：

```bash
# Fedora
sudo dnf install https://download.zfsonlinux.org/fedora/zfs-release-$(rpm -E %fedora).noarch.rpm
sudo dnf install zfs

# RHEL/CentOS Stream
sudo dnf install https://download.zfsonlinux.org/epel/zfs-release.el$(rpm -E %rhel).noarch.rpm
sudo dnf install zfs

# 加载模块
modprobe zfs
```

### Arch Linux

```bash
# 官方仓库包含 ZFS
sudo pacman -S zfs-utils

# DKMS 版本（推荐，内核升级后自动重编译）
yay -S zfs-dkms

# 加载模块
modprobe zfs
```

---

## 存储池管理

### 创建池（zpool create）

```bash
# 创建简单池（单设备，无冗余）
zpool create mypool /dev/sdb

# 指定挂载点
zpool create -m /data mypool /dev/sdb

# 创建带冗余的池
zpool create -m /data mypool mirror /dev/sdb /dev/sdc        # 镜像
zpool create -m /data mypool raidz1 /dev/sdb /dev/sdc /dev/sdd  # RAIDZ1

# 使用 GPT 分区（推荐）
zpool create -m /data mypool /dev/disk/by-id/wwn-0x500...
```

### 简单 / 镜像 / RAIDZ1/2/3

| 拓扑 | 最少设备 | 容量 | 冗余 | 适用场景 |
|------|----------|------|------|----------|
| **stripe** | 1 | 100% | 无 | 临时数据、缓存 |
| **mirror** | 2 | 50% | 1 副本 | 读密集、高可靠 |
| **raidz1** | 3 | ~67% | 1 奇偶校验 | 通用存储 |
| **raidz2** | 4 | ~50% | 2 奇偶校验 | 大容量、高可靠 |
| **raidz3** | 5 | ~40% | 3 奇偶校验 | 极高可靠要求 |

```bash
# 镜像（2 设备）
zpool create pool mirror /dev/sdb /dev/sdc

# RAIDZ1（3+ 设备）
zpool create pool raidz1 /dev/sdb /dev/sdc /dev/sdd

# RAIDZ2（4+ 设备）
zpool create pool raidz2 /dev/sdb /dev/sdc /dev/sdd /dev/sde

# RAIDZ3（5+ 设备）
zpool create pool raidz3 /dev/sdb /dev/sdc /dev/sdd /dev/sde /dev/sdf

# 混合拓扑（mirror + raidz1）
zpool create pool mirror /dev/sdb /dev/sdc raidz1 /dev/sdd /dev/sde /dev/sdf
```

### 池状态查看（zpool status / zpool list）

```bash
# 查看池状态（含设备健康信息）
zpool status mypool

# 查看池空间使用
zpool list
zpool list -o name,size,used,avail,cap

# 查看池属性
zpool get all mypool

# 查看特定属性
zpool get autoexpand,autoreplace mypool
```

`zpool status` 输出关键字段：
- `state: ONLINE` — 池正常
- `state: DEGRADED` — 有设备故障但仍有冗余
- `state: FAULTED` — 数据丢失风险

### 添加/移除设备

```bash
# 向池中添加设备（横向扩展）
zpool add mypool /dev/sdg

# 添加 mirror vdev
zpool add mypool mirror /dev/sdg /dev/sdh

# 移除设备（需池有冗余能力）
zpool remove mypool /dev/sdg

# 在线替换设备（热替换）
zpool replace mypool /dev/sdb /dev/sdg

# 自动替换（设置后故障设备自动用新设备替换）
zpool set autoreplace=on mypool
```

### 故障设备替换

```bash
# 1. 确认故障
zpool status mypool
# 看到 FAULTED 或 UNAVAIL 的设备

# 2. 物理替换磁盘
# 3. 标记替换
zpool replace mypool /dev/old_disk /dev/new_disk

# 4. 等待重建完成
zpool status mypool
#  resilver 00% done 的进度条完成后恢复

# 5. 检查数据完整性
zpool scrub mypool
```

---

## 数据集管理

### 文件系统数据集（zfs create）

```bash
# 创建数据集（自动挂载为子目录）
zfs create mypool/data

# 指定挂载点
zfs create -o mountpoint=/mnt/data mypool/data

# 嵌套数据集
zfs create mypool/data/projects
zfs create mypool/data/documents

# 查看数据集
zfs list
zfs list -o name,used,avail,refer,mountpoint
```

### 卷数据集（zfs create -V）

```bash
# 创建块设备卷（用于 swap、虚拟机磁盘等）
zfs create -V 10G mypool/swap

# 格式化并使用
mkswap /dev/zvol/pool/swap
swapon /dev/zvol/pool/swap

# 创建虚拟机磁盘
zfs create -V 100G -o volblocksize=16K mypool/vm-disk
```

### 挂载选项

```bash
# 设置数据集属性
zfs set compression=lz4 mypool/data
zfs set atime=off mypool/data
zfs set recordsize=1M mypool/data

# 查看挂载信息
zfs get mountpoint,canmount mypool/data

# 手动卸载/挂载
zfs unmount mypool/data
zfs mount mypool/data

# 永久卸载（不自动挂载）
zfs set canmount=off mypool/data
```

### 配额与预留

```bash
# 设置配额（限制最大使用空间）
zfs set quota=50G mypool/data
zfs set refquota=50G mypool/data   # 仅限本数据集，不含子数据集

# 设置预留（保证最低可用空间）
zfs set reservation=10G mypool/data
zfs set refreservation=10G mypool/data

# 查看配额和预留
zfs get quota,refquota,reservation mypool/data

# 取消限制
zfs set quota=none mypool/data
zfs set reservation=none mypool/data
```

---

## 快照与克隆

### 快照创建（zfs snapshot）

```bash
# 创建单个快照
zfs snapshot mypool/data@snap1

# 批量创建（所有直接子数据集）
zfs snapshot -r mypool@daily-$(date +%Y%m%d)

# 命名约定
zfs snapshot mypool/data@2024-01-15-backup
zfs snapshot mypool/data@pre-upgrade
```

### 快照列表（zfs list -t snapshot）

```bash
# 列出所有快照
zfs list -t snapshot

# 列出特定池/数据集的快照
zfs list -t snapshot -o name,used,refer,creation -r mypool

# 按时间排序
zfs list -t snapshot -o name,creation -s creation

# 按大小排序（找最大的快照）
zfs list -t snapshot -o name,used -S used | head -20
```

### 快照回滚（zfs rollback）

```bash
# 回滚到指定快照
zfs rollback mypool/data@snap1

# 回滚并销毁之后的快照（破坏性操作）
zfs rollback -r mypool/data@snap1

# 非破坏性回滚：通过克隆实现
# 1. 克隆快照
zfs clone mypool/data@snap1 mypool/data-rollback
# 2. 替换原数据集（需停机）
zfs destroy mypool/data
zfs rename mypool/data-rollback mypool/data
zfs set mountpoint=/data mypool/data
```

**重要限制**：回滚只能回到最近的快照，或使用 `-r` 销毁中间快照。无法在不删除后续快照的情况下回滚到更早的快照。

### 克隆（zfs clone）

```bash
# 基于快照创建克隆（瞬间完成，占用空间按需增长）
zfs clone mypool/data@snap1 mypool/data-test

# 克隆用于测试/开发环境
zfs clone mypool/data@before-migration mypool/data-migration-test

# 独立克隆（断开与快照的依赖）
zfs promote mypool/data-test
# 此后原始快照可安全删除

# 查看克隆关系
zfs list -o name,origin,used -r mypool
```

### 快照销毁

```bash
# 销毁单个快照
zfs destroy mypool/data@snap1

# 批量销毁快照
zfs destroy -r mypool@daily-*   # 递归销毁匹配的快照

# 只销毁快照（保留数据集）
zfs destroy mypool/data@snap1

# 安全检查：先看哪些快照依赖于此快照
zfs get -r -o name,origin mypool | grep -v "-"
```

---

## 增量备份

### zfs send / receive

```bash
# 全量发送（首次备份）
zfs send mypool/data@snap1 | ssh remote zfs recv backup/data

# 发送到本地文件
zfs send mypool/data@snap1 > /mnt/backup/data-snap1.zfs

# 从文件恢复
zfs recv mypool/data < /mnt/backup/data-snap1.zfs
```

### 增量传输（-I / -i）

```bash
# 增量传输：发送两个快照之间的差异
zfs send -i mypool/data@snap1 mypool/data@snap2 | \
  ssh remote zfs recv backup/data

# 使用 -I（包含中间所有快照）
zfs send -I mypool/data@snap1 mypool/data@snap3 | \
  ssh remote zfs recv backup/data

# 压缩传输
zfs send mypool/data@snap1 | ssh remote 'zfs recv backup/data'
```

### 定时备份脚本

```bash
#!/bin/bash
# zfs-backup.sh — ZFS 增量备份脚本
set -euo pipefail

POOL="mypool"
REMOTE="backup-server"
REMOTE_POOL="backup"
SNAP_NAME="auto"
MAX_SNAPS=7  # 保留最近 N 个快照

# 1. 创建新快照
zfs snapshot "${POOL}@${SNAP_NAME}-$(date +%Y%m%d-%H%M)"

# 2. 获取最新两个快照名称
SNAPS=($(zfs list -t snapshot -o name -s creation -r "$POOL" | \
  grep "${SNAP_NAME}-" | tail -2))

if [ ${#SNAPS[@]} -lt 2 ]; then
  echo "首次备份，执行全量发送..."
  zfs send "${SNAPS[0]}" | ssh "$REMOTE" zfs recv "${REMOTE_POOL}"
else
  echo "增量发送: ${SNAPS[0]} -> ${SNAPS[1]}"
  zfs send -i "${SNAPS[0]}" "${SNAPS[1]}" | \
    ssh "$REMOTE" zfs recv "${REMOTE_POOL}"
fi

# 3. 清理旧快照
OLD_SNAPS=($(zfs list -t snapshot -o name -s creation -r "$POOL" | \
  grep "${SNAP_NAME}-" | head -n -${MAX_SNAPS}))
for snap in "${OLD_SNAPS[@]}"; do
  echo "删除旧快照: $snap"
  zfs destroy "$snap"
done

echo "备份完成: $(date)"
```

配合 cron 执行：

```bash
# 每天凌晨 2 点执行增量备份
0 2 * * * /opt/scripts/zfs-backup.sh >> /var/log/zfs-backup.log 2>&1
```

---

## 压缩

### 算法选择（lz4 / zstd / gzip）

```bash
# lz4 — 默认推荐，速度最快，压缩率中等
zfs set compression=lz4 mypool/data

# zstd — 压缩率高，速度适中（ZFS 0.8+ 支持）
zfs set compression=zstd mypool/data
zfs set compression=zstd-3 mypool/data   # 1-19 级别，3 为默认

# gzip — 压缩率最高，CPU 开销大
zfs set compression=gzip mypool/data
zfs set compression=gzip-6 mypool/data   # 1-9 级别
```

### 压缩率 vs 性能

| 算法 | 压缩率 | CPU 开销 | 适用场景 |
|------|--------|----------|----------|
| **lz4** | 2:1 ~ 3:1 | 极低 | 通用默认，数据库，虚拟机 |
| **zstd** | 3:1 ~ 5:1 | 中等 | 归档、日志、文档存储 |
| **gzip** | 4:1 ~ 6:1 | 高 | 静态内容、压缩率优先 |

```bash
# 查看实际压缩率
zfs get compressratio,compression mypool/data

# 监控实时压缩效果
zpool iostat -v 5 3   # 查看 compressdatatx 的比例
```

---

## 性能调优

### ARC 缓存

ZFS 使用自适应替换缓存（ARC，Adaptive Replacement Cache）作为主缓存机制，类似于数据库的 buffer pool：

```bash
# 查看 ARC 使用情况
cat /proc/spl/kstat/zfs/arcstats

# ARC 大小限制（默认为系统内存的 50%）
echo $((512 * 1024 * 1024)) > /sys/module/zfs/parameters/zfs_arc_max

# 在 /etc/modprobe.d/zfs.conf 中持久化
# options zfs zfs_arc_max=536870912   # 512MB
```

ARC 缓存分层：

- **MRU（Most Recently Used）**：最近访问的数据，保留时间短
- **MFU（Most Frequently Used）**：频繁访问的数据，保留时间长
- **L2ARC**：二级缓存，可使用 SSD 扩展缓存容量

### 调优参数

```bash
# 增大最大顺序读 I/O（适合大文件顺序读取）
zfs set recordsize=1M mypool/data

# 减小记录大小（适合小文件随机读写，如数据库）
zfs set recordsize=8K mypool/data

# 关闭 atime（减少元数据写入）
zfs set atime=off mypool

# 调整同步写入策略
zfs set sync=standard mypool    # 默认，fsync 时同步
zfs set sync=always mypool      # 强制同步（数据库日志）
zfs set sync=disabled mypool    # 禁用同步（仅测试用！）

# 调整 zfs_txg_timeout（写入延迟，默认 5 秒）
echo 5 > /sys/module/zfs/parameters/zfs_txg_timeout

# 启用 L2ARC（SSD 作为二级缓存）
zpool add mypool cache /dev/nvme0n1
```

### fio 基准测试

```bash
# 安装 fio
apt install fio

# 顺序写测试
fio --name=seqwrite --rw=write --bs=1M --size=4G \
  --numjobs=1 --runtime=30 --group_reporting \
  --filename=/mnt/test/fio-test

# 顺序读测试
fio --name=seqread --rw=read --bs=1M --size=4G \
  --numjobs=1 --runtime=30 --group_reporting \
  --filename=/mnt/test/fio-test

# 随机读写测试（模拟数据库负载）
fio --name=randrw --rw=randrw --rwmixread=70 --bs=8K \
  --size=2G --numjobs=4 --runtime=60 --group_reporting \
  --filename=/mnt/test/fio-test

# 对比压缩前后的性能
zfs set compression=off mypool/test
fio --name=nocompress --rw=randread --bs=8K --size=1G \
  --numjobs=4 --runtime=30 --group_reporting \
  --filename=/mnt/test/fio-test

zfs set compression=lz4 mypool/test
fio --name=lz4 --rw=randread --bs=8K --size=1G \
  --numjobs=4 --runtime=30 --group_reporting \
  --filename=/mnt/test/fio-test
```

---

## ZFS vs Btrfs 对比

### 功能对比表

| 特性 | ZFS | Btrfs |
|------|-----|-------|
| **数据完整性** | 端到端校验和（fletcher4/SHA-256） | 校验和（xxhash/crc32c/sha256） |
| **RAID** | RAID-Z1/2/3（软 RAID） | RAID 0/1/10（RAID 5/6 仍在开发） |
| **快照** | Copy-on-Write，高效 | Copy-on-Write，高效 |
| **压缩** | lz4 / zstd / gzip | lzo / zstd / zlib |
| **发送/接收** | 支持增量 | 支持增量 |
| **在线扩容** | 支持 vdev 扩展 | 支持在线添加设备 |
| **去重** | 实验性（DEADLOON） | 有限支持 |
| **子卷** | 数据集（功能更强） | 原生子卷 |
| **内核状态** | 外部模块（DKMS） | 主线内核（自 3.0） |
| **稳定性** | 生产级成熟 | 核心功能稳定，部分功能实验性 |
| **许可证** | CDDL | GPL |

### 选型建议

**选择 ZFS 当你需要：**
- 极高的数据可靠性（端到端校验和 + RAID-Z）
- 大容量存储池（数十 TB 级别）
- 成熟的 SEND/RECEIVE 增量备份
- 块设备卷（虚拟机、数据库）
- 生产环境长期稳定运行

**选择 Btrfs 当你需要：**
- 简单部署（无需 DKMS，内核原生支持）
- 快照回滚（snapper 集成好）
- 写时复制文件系统（轻量级使用）
- 发行版原生支持（SUSE/openSUSE）
- 桌面/工作站场景

**混合使用**：很多生产环境同时使用两者——Btrfs 用于根文件系统和快照管理，ZFS 用于大容量数据存储和备份。两者可以共存于同一系统，各司其职。

---

## 日常运维

### 健康检查

```bash
# 定期数据清理（scrub）
zpool scrub mypool

# 查看 scrub 历史
zpool status -v mypool

# 查看最近 scrub 信息
zpool get all mypool | grep scrub
```

### 导出/导入池

```bash
# 导出池（移动磁盘前必须导出）
zpool export mypool

# 导入池
zpool import mypool

# 按 GUID 导入（多主机环境）
zpool import 1234567890123456789

# 只读导入
zpool import -o readonly=on mypool
```

### 监控告警

```bash
# 监听 ZFS 事件
zpool events -v

# 配置邮件告警
echo "ZFS scrub done" | mail -s "ZFS Alert" admin@example.com

# 使用 ZED（ZFS Event Daemon）
systemctl enable --now zed
```

---

## 常见问题

### 性能不佳

```bash
# 检查 ARC 命中率
cat /proc/spl/kstat/zfs/arcstats | grep hits

# 确认压缩已启用
zfs get compression mypool

# 检查是否有设备故障导致降级
zpool status mypool
```

### 空间不足

```bash
# 查看空间使用
zpool list -o name,size,used,avail
zfs list -o name,used,avail,refer -r mypool

# 检查快照占用
zfs list -t snapshot -o name,used -S used | head -20

# 清理不需要的快照
zfs destroy mypool/data@old-snap

# 扩容：添加新设备
zpool add mypool /dev/sdg
```

---

## 参考资源

- [OpenZFS 官方文档](https://openzfs.github.io/openzfs-docs/)
- [ZFS on Linux](https://zfsonlinux.org/)
- [ZFS 最佳实践指南](https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Workload%20Tuning.html)
- `man zpool` / `man zfs` — 完整命令参考

---

