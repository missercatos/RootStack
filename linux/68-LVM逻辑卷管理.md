# 第68章：LVM 逻辑卷管理

## LVM 概述

### 为什么需要 LVM

传统磁盘分区管理存在严重的局限性：分区大小在创建后难以动态调整，跨多个物理磁盘的数据无法统一管理，扩容往往需要停机重新分区。在生产环境中，这些限制会导致存储资源利用率低下和运维复杂度上升。

LVM（Logical Volume Manager）通过在物理磁盘和文件系统之间引入一个逻辑抽象层，彻底解决了上述问题。它允许管理员在不中断业务的前提下动态调整存储空间，将多个物理磁盘整合为统一的存储池，并提供快照、精简配置、RAID等高级存储功能。

LVM 的核心价值体现在以下方面：

- **动态扩容**：在线扩展逻辑卷容量，无需卸载文件系统
- **跨盘管理**：将多块物理磁盘组合为一个卷组，统一分配空间
- **快照支持**：创建任意时刻的存储快照，用于备份或测试
- **精简配置**：按需分配空间，提高存储利用率
- **可移植性**：逻辑卷可在不同物理磁盘间迁移
- **条带化**：将数据分散到多块磁盘，提升 I/O 性能

### 核心概念：PV / VG / LV / PE / LE

LVM 采用分层架构，理解各层之间的关系是掌握 LVM 的基础。

**PV（Physical Volume，物理卷）**

物理卷是 LVM 管理的最底层单位。任何块设备——整块磁盘、分区、RAID 阵列——都可以初始化为物理卷。pvcreate 命令在设备头部写入 LVM 元数据，使其可被卷组识别和使用。

**VG（Volume Group，卷组）**

卷组是物理卷的集合，构成一个统一的存储池。一个卷组可以包含多块物理磁盘上的物理卷，将它们的容量合并为一个连续的地址空间。卷组内的空间可以按需分配给逻辑卷。

**LV（Logical Volume，逻辑卷）**

逻辑卷是从卷组中划分出来的虚拟分区，直接用于创建文件系统或作为裸设备使用。逻辑卷是用户和应用程序最终打交道的存储单元，其大小可以动态调整。

**PE（Physical Extent，物理块）**

物理块是卷组空间分配的最小单位，默认大小为 4MB。当逻辑卷从卷组中请求空间时，卷组以 PE 为单位分配物理空间。PE 大小在卷组创建时确定，之后不可更改。

**LE（Logical Extent，逻辑块）**

逻辑块是逻辑卷内部的寻址单元。在简单情况下，一个 LE 映射到一个 PE。当逻辑卷使用条带化时，一个 LE 可能映射到多个 PE，分布在不同的物理卷上。

五者之间的层次关系如下：

```
物理磁盘 / 分区
    |
    v
物理卷（PV）-- 每个 PV 内部划分为若干 PE
    |
    v
卷组（VG）-- 汇聚多个 PV 的 PE，形成统一的存储池
    |
    v
逻辑卷（LV）-- 从 VG 的 PE 池中分配 LE
    |
    v
文件系统（ext4 / xfs / ...）
```

### LVM 在存储栈中的位置

LVM 位于磁盘分区之上、文件系统之下。存储栈的完整层次为：

```
应用程序
    |
文件系统（ext4, xfs, btrfs）
    |
逻辑卷（LV）
    |
卷组（VG）
    |
物理卷（PV）
    |
磁盘分区 / 整块磁盘 / RAID 阵列
    |
硬件 / 虚拟磁盘
```

通过 device-mapper 内核模块，LVM 在内核态实现存储映射。用户态的 lvm2 工具集提供配置和管理接口。

---

## 基础操作

### 创建物理卷（pvcreate / pvdisplay）

**扫描可用块设备**

在创建物理卷之前，确认系统中可用的块设备：

```bash
lsblk
# NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINTS
# sda      8:0    0   50G  0 disk
# sdb      8:16   0  100G  0 disk
# sdc      8:32   0  200G  0 disk
```

**创建物理卷**

```bash
# 将整块磁盘初始化为物理卷
sudo pvcreate /dev/sdb
# Physical volume "/dev/sdb" successfully created.

# 将多个设备同时初始化
sudo pvcreate /dev/sdb /dev/sdc

# 也可对分区操作
sudo pvcreate /dev/sda3
```

**查看物理卷信息**

```bash
# 简要查看所有物理卷
sudo pvs
#   PV         VG       Fmt  Attr PSize   PFree
#   /dev/sda3          lvm2 a--  <19.50g <19.50g
#   /dev/sdb           lvm2 a--  100.00g 100.00g
#   /dev/sdc           lvm2 a--  200.00g 200.00g

# 详细查看特定物理卷
sudo pvdisplay /dev/sdb
#   --- Physical volume ---
#   PV Name               /dev/sdb
#   VG Name
#   PV Size               100.00 GiB / not usable 4.00 MiB
#   Allocatable           yes
#   PE Size               4.00 MiB
#   Total PE              25599
#   Free PE               25599
#   Allocated PE          0
```

### 创建卷组（vgcreate / vgdisplay）

**创建卷组**

```bash
# 基本创建：指定卷组名和初始物理卷
sudo vgcreate data_vg /dev/sdb /dev/sdc
# Volume group "data_vg" successfully created

# 自定义 PE 大小（8MB）
sudo vgcreate -s 8M data_vg /dev/sdb /dev/sdc
```

**查看卷组信息**

```bash
# 简要查看
sudo vgs
#   VG       #PV #LV #SN Attr   VSize   VFree
#   data_vg    2   0   0 wz--n- 299.99g 299.99g

# 详细查看
sudo vgdisplay data_vg
#   --- Volume group ---
#   VG Name               data_vg
#   System ID
#   Format                lvm2
#   Metadata Areas        2
#   Metadata Sequence No  1
#   VG Access             read/write
#   VG Status             resizable
#   MAX LV                0
#   Cur LV                0
#   Open LV               0
#   Max PV                0
#   Cur PV                2
#   Act PV                2
#   VG Size               299.99 GiB
#   PE Size               4.00 MiB
#   Total PE              76797
#   Alloc PE / Size       0 / 0
#   Free  PE / Size       76797 / 299.99 GiB
#   VG UUID               xxxx-xxxx-xxxx-xxxx
```

### 创建逻辑卷（lvcreate / lvdisplay）

**创建逻辑卷**

```bash
# 按容量指定大小，创建 50GB 的逻辑卷
sudo lvcreate -L 50G -n web_data data_vg
# Logical volume "web_data" created.

# 按 PE 数量指定大小
sudo lvcreate -l 12800 -n log_data data_vg

# 使用卷组全部剩余空间的 80%
sudo lvcreate -l 80%VG -n app_data data_vg

# 使用卷组剩余空间的全部
sudo lvcreate -l 100%FREE -n temp_data data_vg
```

**查看逻辑卷信息**

```bash
# 简要查看
sudo lvs
#   LV        VG       Attr       LSize   Pool Origin Data%  Meta%
#   app_data  data_vg  -wi-a----- <240.00g
#   log_data  data_vg  -wi-a-----  50.00g
#   web_data  data_vg  -wi-a-----  50.00g

# 详细查看
sudo lvdisplay /dev/data_vg/web_data
#   --- Logical volume ---
#   LV Path                /dev/data_vg/web_data
#   LV Name                web_data
#   VG Name                data_vg
#   LV UUID                xxxx-xxxx-xxxx-xxxx
#   LV Write Access        read/write
#   LV Creation host, time  ubuntu, 2026-01-15 10:30:00 +0800
#   LV Status              available
#   # open                 0
#   LV Size                50.00 GiB
#   Current LE             12800
#   Segments               1
#   Allocation             inherit
#   Read ahead sectors     auto
#   - currently set to     256
#   Block device           253:0
```

### 格式化与挂载

```bash
# 格式化为 ext4
sudo mkfs.ext4 /dev/data_vg/web_data
# mke2fs 1.46.5 (30-Dec-2021)

# 格式化为 xfs
sudo mkfs.xfs /dev/data_vg/log_data

# 创建挂载点并挂载
sudo mkdir -p /data/web
sudo mount /dev/data_vg/web_data /data/web

# 挂载 xfs 卷
sudo mkdir -p /data/logs
sudo mount /dev/data_vg/log_data /data/logs

# 查看挂载结果
df -h /data/web /data/logs
# Filesystem                     Size  Used Avail Use% Mounted on
# /dev/mapper/data_vg-web_data    50G   28K   47G   1% /data/web
# /dev/mapper/data_vg-log_data    50G   28K   47G   1% /data/logs
```

**配置自动挂载（/etc/fstab）**

```bash
# 获取逻辑卷的 UUID
sudo blkid /dev/data_vg/web_data
# /dev/data_vg/web_data: UUID="xxxx-xxxx" TYPE="ext4"

# 编辑 /etc/fstab，添加挂载条目
echo 'UUID=xxxx-xxxx /data/web ext4 defaults 0 2' | sudo tee -a /etc/fstab

# 或使用逻辑卷路径（推荐，对 LVM 友好）
echo '/dev/data_vg/web_data /data/web ext4 defaults 0 2' | sudo tee -a /etc/fstab
```

---

## 动态扩容

### 扩展逻辑卷（lvextend + resize2fs/xfs_growfs）

扩展逻辑卷是最常见的 LVM 操作，分为两步：扩展逻辑卷本身，然后扩展文件系统。

**扩展 ext4 文件系统**

```bash
# 查看当前逻辑卷大小
sudo lvs data_vg/web_data
#   LV       VG       Attr       LSize  Pool Origin Data% Meta%
#   web_data data_vg  -wi-a----- 50.00g

# 第一步：扩展逻辑卷（增加 30GB）
sudo lvextend -L +30G /dev/data_vg/web_data
# Size of logical volume data_vg/web_data changed from 50.00 GiB to 80.00 GiB.
# Logical volume data_vg/web_data successfully resized.

# 第二步：扩展 ext4 文件系统
sudo resize2fs /dev/data_vg/web_data
# resize2fs 1.46.5 (30-Dec-2021)
# The filesystem on /dev/data_vg/web_data is now 20971520 (4k) blocks long.
```

**一步完成（lvextend -r）**

```bash
# -r 参数自动调用 resize2fs 或 xfs_growfs
sudo lvextend -r -L +30G /dev/data_vg/web_data
# Size of logical volume data_vg/web_data changed from 50.00 GiB to 80.00 GiB.
# Logical volume data_vg/web_data successfully resized.
# resize2fs 1.46.5 (30-Dec-2021)
# The filesystem on /dev/data_vg/web_data is now 20971520 (4k) blocks long.
```

**扩展 xfs 文件系统**

```bash
# 扩展逻辑卷
sudo lvextend -r -L +50G /dev/data_vg/log_data

# xfs 也可使用 xfs_growfs 单独操作
sudo xfs_growfs /data/logs
```

### 扩展卷组（vgextend）

当卷组空间不足时，需要先扩展卷组，再扩展逻辑卷。

```bash
# 查看卷组剩余空间
sudo vgs data_vg
#   VG       #PV #LV #SN Attr   VSize  VFree
#   data_vg    2   2   0 wz--n- 299.9g 169.9g

# 添加新磁盘到卷组
sudo pvcreate /dev/sdd
sudo vgextend data_vg /dev/sdd
# Volume group "data_vg" successfully extended

# 确认扩展结果
sudo vgs data_vg
#   VG       #PV #LV #SN Attr   VSize   VFree
#   data_vg    3   2   0 wz--n- <399.99g <269.99g
```

### 缩容逻辑卷（风险 + 流程）

缩容是一项危险操作，必须严格按顺序执行，否则会导致数据丢失。xfs 文件系统不支持缩容。

**ext4 缩容流程**

```bash
# 1. 确认文件系统状态健康
sudo e2fsck -f /dev/data_vg/web_data

# 2. 卸载文件系统（缩容必须离线）
sudo umount /data/web

# 3. 缩小文件系统到目标大小（例如 30GB）
sudo resize2fs /dev/data_vg/web_data 30G

# 4. 缩小逻辑卷到相同大小
sudo lvreduce -L 30G /dev/data_vg/web_data
# WARNING: Reducing active logical volume to 30.00 GiB.
# THIS MAY DESTROY YOUR DATA (filesystem etc.)
# Do you really want to reduce data_vg/web_data? [y/n]: y

# 5. 重新挂载
sudo mount /dev/data_vg/web_data /data/web
```

**安全缩容建议**

- 缩容前务必创建完整备份
- 缩容前执行 fsck 检查文件系统完整性
- 目标大小必须大于已使用空间，建议预留 10% 余量
- xfs 文件系统绝对不能缩容，只能迁移数据到较小的卷

---

## LVM 快照

### 快照原理（CoW）

LVM 快照基于 Copy-on-Write（写时复制）机制。创建快照时并不复制数据，而是记录原始数据的位置。当原始卷的某个块即将被修改时，系统先将该块的旧数据复制到快照区域，然后再执行写入。

这种机制使得快照创建几乎瞬间完成，且不消耗额外存储空间。但随着原始卷数据变更比例增加，快照占用的空间会持续增长。当快照空间耗尽时，快照将自动失效。

快照的存储开销模型：

```
快照创建时刻：几乎零空间消耗

原始卷数据变更 → 旧数据复制到快照区域 → 快照空间增长

快照空间 = 原始卷中被修改的块数 × 块大小
```

### 创建快照（lvcreate -s）

```bash
# 查看原始逻辑卷
sudo lvs data_vg
#   LV        VG       Attr       LSize   Pool Origin Data%  Meta%
#   web_data  data_vg  -wi-a-----  80.00g

# 创建快照：指定大小为原始卷的 10%
sudo lvcreate -L 8G -s -n web_snap /dev/data_vg/web_data
# Logical volume "web_snap" created.

# 或使用原始卷大小的百分比
sudo lvcreate -l 10%ORIGIN -s -n web_snap_v2 /dev/data_vg/web_data

# 查看快照
sudo lvs data_vg
#   LV          VG       Attr       LSize   Pool Origin   Data%  Meta%
#   web_data    data_vg  Owi-aot---  80.00g
#   web_snap    data_vg  Swi-aot---   8.00g      web_data  0.02
#   web_snap_v2 data_vg  Swi-aot---  <8.00g      web_data  0.02
```

### 挂载与恢复快照

```bash
# 挂载快照（只读方式，用于查看原始数据）
sudo mkdir -p /mnt/snapshot
sudo mount -o ro /dev/data_vg/web_snap /mnt/snapshot

# 查看快照中的数据（即创建时刻的原始数据）
ls /mnt/snapshot/

# 卸载快照
sudo umount /mnt/snapshot
```

**通过快照恢复数据**

```bash
# 方式一：将快照合并回原始卷（推荐）

# 1. 卸载原始卷
sudo umount /data/web

# 2. 启动合并
sudo lvconvert --merge /dev/data_vg/web_snap
#   Merging of volume data_vg/web_snap started.
#   data_vg/web_data: Conflict detected when merging, internal error.
#
# 注意：如果快照空间已满，合并将失败

# 3. 合并完成后逻辑卷自动变为可激活状态
# 4. 重新挂载
sudo mount /dev/data_vg/web_data /data/web
```

### 快照合并（lvconvert --merge）

```bash
# 检查快照状态
sudo lvs -o +lv_name,origin,snap_percent
#   LV          VG       Attr       LSize   Origin    Snap%
#   web_snap    data_vg  Swi-aot---   8.00g web_data   0.02

# 执行合并
sudo lvconvert --merge /dev/data_vg/web_snap
# Merging of volume data_vg/web_snap started.
# data_vg/web_snapshot: Merged: 100.0%

# 合并后原始快照卷自动删除
sudo lvs data_vg
#   LV       VG       Attr       LSize   Pool Origin Data%  Meta%
#   web_data data_vg  -wi-a-----  80.00g
```

---

## LVM Thin Provisioning

### 精简池概念

精简配置（Thin Provisioning）允许创建逻辑卷时分配超过物理可用容量的空间，实现超量配置。所有精简卷共享同一个精简池，按实际使用量消耗池空间。

这种机制的优势在于：创建大量虚拟机或容器时，不需要为每个实例预分配完整空间。实际使用量远小于声明量时，精简配置能显著提高存储利用率。

精简池与精简卷的关系：

```
物理空间 → 精简池（Thin Pool）→ 精简卷（Thin Volume）
                                    |
                                    v
                              超量配置（Overcommit）
```

### 创建精简池与精简卷

```bash
# 第一步：创建数据逻辑卷作为精简池的数据区
sudo lvcreate -L 100G -n thin_pool data_vg

# 第二步：创建元数据逻辑卷
sudo lvcreate -L 1G -n thin_meta data_vg

# 第三步：将数据卷和元数据卷组合为精简池
sudo lvconvert --type thin-pool --poolmetadata data_vg/thin_meta data_vg/thin_pool
#   WARNING: Converting logical volume data_vg/thin_pool to thin pool data data with
#   initial metadata volume data_vg/thin_meta.
#   THIS WILL DESTROY CONTENT OF LOGICAL VOLUME (filesystem etc.)
#   Do you really want to convert data_vg/thin_pool? [y/n]: y
#   Logical volume data_vg/thin_pool converted.

# 第四步：从精简池创建精简卷
sudo lvcreate -V 50G -T data_vg/thin_pool -n vm1_disk
sudo lvcreate -V 50G -T data_vg/thin_pool -n vm2_disk
sudo lvcreate -V 30G -T data_vg/thin_pool -n container1

# 查看精简卷
sudo lvs -o +lv_name,lv_layout,thin:origin,thin:data_percent
#   LV            VG       Attr       LSize   Pool      Origin    Data%
#   thin_pool     data_vg  twi-aot-- 100.00g           100.00
#   vm1_disk      data_vg  Vwi-aot--  50.00g thin_pool          0.00
#   vm2_disk      data_vg  Vwi-aot--  50.00g thin_pool          0.00
#   container1    data_vg  Vwi-aot--  30.00g thin_pool          0.00
```

**一步创建精简池**

```bash
# 使用精简池的自动创建功能
sudo lvcreate --thinpool thin_data --size 200G --thinpool 2G data_vg
# 其中 2G 为元数据空间
```

### 空间耗尽风险与监控

精简池空间耗尽会导致所有关联的精简卷变为只读或不可用，这是精简配置的主要风险。

```bash
# 监控精简池使用率
sudo lvs -o lv_name,lv_size,thin_data_percent,thin_metadata_percent data_vg

# 配置自动告警脚本
cat << 'EOF' > /usr/local/bin/check_thin_pool.sh
#!/bin/bash
THRESHOLD=80
POOL_INFO=$(lvs --noheadings -o lv_name,thin_data_percent data_vg 2>/dev/null)
echo "$POOL_INFO" | while read -r line; do
    name=$(echo "$line" | awk '{print $1}')
    usage=$(echo "$line" | awk '{print $2}' | cut -d'.' -f1)
    if [ "$usage" -ge "$THRESHOLD" ]; then
        logger -p warning "LVM thin pool $name usage at ${usage}%"
    fi
done
EOF
chmod +x /usr/local/bin/check_thin_pool.sh

# 添加 cron 定时任务
echo "*/5 * * * * root /usr/local/bin/check_thin_pool.sh" \
    | sudo tee /etc/cron.d/check_thin_pool
```

**扩容精简池**

```bash
# 扩展精简池的数据逻辑卷
sudo lvextend -L +50G /dev/data_vg/thin_pool

# 扩展元数据逻辑卷（如需要）
sudo lvextend -L +1G /dev/data_vg/thin_pool_tmeta
```

---

## LVM RAID

### RAID 0 / 1 / 5 / 10

| RAID 级别 | 最少磁盘数 | 容错能力 | 读取性能 | 写入性能 | 空间利用率 |
|-----------|-----------|---------|---------|---------|-----------|
| RAID 0 | 2 | 无 | N 倍 | N 倍 | 100% |
| RAID 1 | 2 | 允许 1 块故障 | 不变 | 降低 | 50% |
| RAID 5 | 3 | 允许 1 块故障 | N-1 倍 | 略降 | (N-1)/N |
| RAID 10 | 4 | 每组允许 1 块 | N/2 倍 | N/2 倍 | 50% |

### 通过 LVM 创建 RAID

LVM 集成了 mdadm 的 RAID 功能，无需单独使用 mdadm 管理阵列。

```bash
# 创建 RAID 1 镜像逻辑卷
sudo lvcreate -L 50G -m1 -n mirror_data data_vg /dev/sdb /dev/sdc
# -m1 表示 1 份镜像

# 查看 RAID 状态
sudo lvs -a -o +devices,lv_layout,segtype
#   LV            VG       Attr       LSize   Devices
#   mirror_data   data_vg  rwi-aor---  50.00g mirror_data_rimage_0(0),mirror_data_rimage_1(0)

# 创建 RAID 5 逻辑卷
sudo lvcreate -L 100G -i3 -n raid5_data data_vg /dev/sdb /dev/sdc /dev/sdd

# 创建 RAID 10 逻辑卷
sudo lvcreate -L 80G -m1 -i2 -n raid10_data data_vg \
    /dev/sdb /dev/sdc /dev/sdd /dev/sde
```

### RAID 修复与维护

```bash
# 查看 RAID 设备详情
sudo lvs -a data_vg
# 注意观察属性中的 `r` 标记和 `a` (active) 状态

# 替换故障磁盘
# 1. 添加新磁盘到卷组
sudo pvcreate /dev/sdf
sudo vgextend data_vg /dev/sdf

# 2. 将故障磁盘上的物理卷迁移走
sudo pvmove /dev/sdb /dev/sdf

# 3. 从卷组移除故障磁盘
sudo vgreduce data_vg /dev/sdb

# 4. 执行 RAID 修复（自动重建）
sudo lvchange --repair data_vg/mirror_data

# 查看修复进度
cat /proc/mdstat
# 或使用
sudo lvs -a -o +devices,data_percent
```

---

## LVM Cache（dm-cache）

### SSD 加速 HDD 原理

dm-cache 使用 SSD 作为 HDD 的读写缓存。热点数据自动迁移到 SSD 上，冷数据保留在 HDD 中。这种层次化存储方案在不更换大量 HDD 的前提下，显著提升系统 I/O 性能。

dm-cache 的工作模式：

```
读取请求 → 查找 SSD 缓存 → 命中 → 直接返回（低延迟）
                                 → 未命中 → 从 HDD 读取 → 可能缓存到 SSD

写入请求 → 写入 SSD 缓存 → 标记为脏页 → 后台刷写到 HDD
```

### 使用 lvmcache

```bash
# 1. 准备缓存设备（SSD）
sudo pvcreate /dev/nvme0n1p1
sudo vgextend data_vg /dev/nvme0n1p1

# 2. 创建缓存池逻辑卷
sudo lvcreate -L 20G -n cache_pool data_vg /dev/nvme0n1p1

# 3. 创建缓存池元数据
sudo lvcreate -L 1G -n cache_meta data_vg /dev/nvme0n1p1

# 4. 组合为缓存池
sudo lvconvert --type cache-pool --poolmetadata data_vg/cache_meta data_vg/cache_pool

# 5. 将缓存池附加到慢速逻辑卷
sudo lvconvert --type cache --cachepool data_vg/cache_pool data_vg/web_data

# 查看缓存状态
sudo lvs -a -o +cache_read_hits,cache_read_misses,cache_read_hit_percent data_vg

# 删除缓存（恢复原始卷）
sudo lvconvert --uncache data_vg/web_data
```

**配置缓存策略**

```bash
# 查看可用策略
sudo lvmcache settings data_vg/web_data

# 设置为 writeback 模式（性能最佳，但断电可能丢数据）
sudo lvchange --cachemode writeback data_vg/web_data

# 设置为 writethrough 模式（安全，数据先写到 SSD 再返回）
sudo lvchange --cachemode writethrough data_vg/web_data
```

---

## 卷组管理

### 卷组迁移（pvmove）

pvmove 用于将物理卷上的逻辑卷数据在线迁移到同一卷组内的其他物理卷，是磁盘热替换和存储维护的核心工具。

```bash
# 将 /dev/sdb 上的所有数据迁移到卷组内其他物理卷
sudo pvmove /dev/sdb

# 只迁移特定逻辑卷的数据
sudo pvmove /dev/sdb /dev/sdc --name mirror_data

# 查看迁移进度
sudo pvs -o +pv_name,lv_name,pe_start,pe_count
watch -n 1 'sudo pvs -o pv_name,pe_start,pe_count | grep sdb'
```

### 卷组合并（vgmerge）

```bash
# 查看要合并的两个卷组
sudo vgs data_vg backup_vg

# 将 backup_vg 合并到 data_vg
sudo vgmerge data_vg backup_vg
# Volume group "backup_vg" successfully merged into "data_vg".

# 合并后的空间自动可用
sudo vgs data_vg
```

### 卷组拆分（vgsplit）

```bash
# 将物理卷从源卷组拆分到新卷组
sudo vgsplit data_vg new_vg /dev/sdb

# 将物理卷拆分到已存在的卷组
sudo vgsplit data_vg backup_vg /dev/sdc -n log_data
```

### 物理卷移除（pvremove）

```bash
# 1. 确认物理卷上没有活跃的逻辑卷
sudo pvs /dev/sdb

# 2. 如果有逻辑卷，先迁移数据
sudo pvmove /dev/sdb

# 3. 从卷组移除物理卷
sudo vgreduce data_vg /dev/sdb

# 4. 移除物理卷标记
sudo pvremove /dev/sdb
# Labels on physical volume "/dev/sdb" successfully wiped.
```

---

## LVM 调优

### 条带化（striped LV）

条带化将逻辑卷的数据分散到多个物理卷上，通过并行读写提升 I/O 性能。

```bash
# 创建条带化逻辑卷：4 块磁盘，每条带 64KB
sudo lvcreate -L 200G -i4 -I 64K -n striped_data data_vg \
    /dev/sdb /dev/sdc /dev/sdd /dev/sde
# -i4: 使用 4 个物理卷
# -I 64K: 条带大小 64KB

# 查看条带配置
sudo lvs -a -o +stripe_size,stripes
#   LV            VG       Attr       LSize   Stripe  #Str
#   striped_data  data_vg  -wi-a----- 200.00g  64.00k     4
```

**条带大小选择建议**

| I/O 类型 | 推荐条带大小 | 说明 |
|----------|-------------|------|
| 数据库（OLTP） | 64KB - 128KB | 小块随机读写 |
| 文件服务器 | 256KB - 512KB | 混合读写 |
| 视频/流媒体 | 1MB - 2MB | 大块顺序读写 |
| 虚拟机 | 128KB - 256KB | 混合负载 |

### 对齐 PE 大小

PE 大小直接影响存储分配粒度和对齐性能。对于大容量存储，适当增大 PE 大小可以减少元数据开销。

```bash
# 创建卷组时指定 PE 大小
sudo vgcreate -s 16M data_vg /dev/sdb /dev/sdc

# 查看当前 PE 大小
sudo vgdisplay data_vg | grep "PE Size"
#   PE Size               16.00 MiB
```

### 监控（lvs / vgs / pvs）

```bash
# 三个核心命令的常用选项

# pvs: 物理卷概览
sudo pvs -o pv_name,vg_name,pv_size,pv_free,pe_count,pe_alloc --sort -pv_free

# vgs: 卷组概览
sudo vgs -o vg_name,pv_count,lv_count,snap_count,vg_size,vg_free,vg_attr --sort -vg_free

# lvs: 逻辑卷概览
sudo lvs -o lv_name,vg_name,lv_size,lv_attr,origin,snap_percent,data_percent \
    --sort -lv_size

# 完整报告（JSON 格式，便于脚本处理）
sudo lvs --reportformat json
sudo vgs --reportformat json
sudo pvs --reportformat json
```

**创建监控脚本**

```bash
cat << 'SCRIPT' > /usr/local/bin/lvm_monitor.sh
#!/bin/bash
LOG="/var/log/lvm_monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "=== LVM Status Report: $DATE ===" >> "$LOG"

echo "--- Physical Volumes ---" >> "$LOG"
pvs --noheadings -o pv_name,vg_name,pv_size,pv_free 2>/dev/null >> "$LOG"

echo "--- Volume Groups ---" >> "$LOG"
vgs --noheadings -o vg_name,vg_size,vg_free 2>/dev/null >> "$LOG"

echo "--- Logical Volumes ---" >> "$LOG"
lvs --noheadings -o lv_name,vg_name,lv_size,lv_attr 2>/dev/null >> "$LOG"

echo "" >> "$LOG"
SCRIPT
chmod +x /usr/local/bin/lvm_monitor.sh
```

---

## LVM vs Btrfs 对比

### 功能对比表

| 功能 | LVM | Btrfs |
|------|-----|-------|
| 动态扩容 | 支持（在线） | 支持（在线） |
| 缩容 | 支持（ext4 离线） | 不支持 |
| 快照 | 支持（CoW） | 支持（瞬时） |
| 精简配置 | 支持 | 不原生支持 |
| RAID | 支持（0/1/5/6/10） | 内置 RAID 0/1/10 |
| 校验和 | 不支持 | 支持 |
| 透明压缩 | 不支持 | 支持（zstd/lzo/zlib） |
| 子卷 | 不支持 | 支持 |
| 多设备 | 支持 | 支持 |
| 在线碎片整理 | 不适用 | 支持 |
| 数据去重 | 不支持 | 支持（实验性） |
| 快照回滚 | 需要合并 | 原生回滚 |
| 备份工具 | 依赖外部 | btrfs send/receive |
| 成熟度 | 极高（20+ 年） | 中等（持续改进） |
| 生产环境验证 | 广泛 | 日益增多 |
| 内核主线集成 | 是 | 是 |
| 学习曲线 | 中等 | 中等偏高 |

### 选型建议

**选择 LVM 的场景**

- 需要精细的存储管理粒度和灵活的卷操作
- 已有大量 ext4/xfs 文件系统需要管理
- 需要与企业级存储基础设施（SAN、iSCSI）集成
- 需要将存储管理与文件系统解耦
- 团队对 LVM 运维经验丰富

**选择 Btrfs 的场景**

- 需要内置快照和回滚功能
- 对数据完整性要求高（校验和、自修复）
- 希望减少管理层级（无需 LVM + 文件系统两层）
- 需要透明压缩节省存储空间
- 容器化环境需要高效子卷管理

**混合使用方案**

许多生产环境采用 LVM + Btrfs 的组合：LVM 负责底层物理存储管理和跨盘整合，Btrfs 在逻辑卷上提供文件系统级的高级功能。这种方案兼顾了两者的优势。

---

## 常见问题与排查

```bash
# 卷组无法激活
sudo vgchange -ay data_vg

# 逻辑卷无法挂载：检查设备映射
sudo dmsetup ls
sudo lvscan

# 磁盘空间不一致：重新扫描物理卷
sudo pvscan --cache

# 查看 LVM 操作历史
sudo lvs -a -o +devices,vg_attr,lv_attr
sudo journalctl -k | grep -i lvm

# 恢复丢失的卷组元数据（最后手段）
sudo vgcfgrestore data_vg

# 检查并修复文件系统
sudo fsck -f /dev/data_vg/web_data
```

---

## 完整实战示例

以下示例演示从零开始构建一个完整的 LVM 存储方案：

```bash
#!/bin/bash
# 完整的 LVM 部署脚本
set -euo pipefail

VG_NAME="app_vg"
LV_WEB="web_data"
LV_DB="db_data"
LV_LOG="log_data"

# 1. 初始化物理卷
pvcreate /dev/sdb /dev/sdc /dev/sdd

# 2. 创建卷组
vgcreate "$VG_NAME" /dev/sdb /dev/sdc /dev/sdd

# 3. 创建逻辑卷
lvcreate -L 50G -n "$LV_WEB" "$VG_NAME"
lvcreate -L 100G -n "$LV_DB" "$VG_NAME"
lvcreate -l 100%FREE -n "$LV_LOG" "$VG_NAME"

# 4. 格式化
mkfs.ext4 /dev/"$VG_NAME"/"$LV_WEB"
mkfs.xfs /dev/"$VG_NAME"/"$LV_DB"
mkfs.xfs /dev/"$VG_NAME"/"$LV_LOG"

# 5. 挂载
mkdir -p /data/{web,db,logs}
mount /dev/"$VG_NAME"/"$LV_WEB" /data/web
mount /dev/"$VG_NAME"/"$LV_DB" /data/db
mount /dev/"$VG_NAME"/"$LV_LOG" /data/logs

# 6. 配置 fstab
echo "/dev/${VG_NAME}/${LV_WEB} /data/web ext4 defaults 0 2" >> /etc/fstab
echo "/dev/${VG_NAME}/${LV_DB} /data/db xfs defaults 0 2" >> /etc/fstab
echo "/dev/${VG_NAME}/${LV_LOG} /data/logs xfs defaults 0 2" >> /etc/fstab

# 7. 创建快照
lvcreate -L 5G -s -n "${LV_WEB}_snap" /dev/"$VG_NAME"/"$LV_WEB"

# 8. 输出状态
echo "=== 部署完成 ==="
pvs
vgs
lvs
df -h /data/*
```

本章全面介绍了 LVM 的核心概念、基础操作、高级特性和运维技巧。LVM 是 Linux 系统管理中最基础也最重要的存储工具之一，熟练掌握 LVM 能够显著提升存储管理的灵活性和可靠性。在实际生产环境中，建议根据业务需求合理规划存储架构，建立完善的监控和备份机制。
