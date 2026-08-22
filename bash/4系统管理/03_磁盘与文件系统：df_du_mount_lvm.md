# 磁盘与文件系统：df, du, mount, lvm | Disk & Filesystems

## 章节概述

> **核心理念**：磁盘管理是系统管理的基础——从查看空间使用、挂载文件系统，到分区管理和 LVM 逻辑卷，每一层都关系到数据的安全和系统的稳定性。理解这些工具就像理解 C 语言的内存管理一样重要。

---

### 第1节：df 磁盘空间查看

#### 1.1 基本使用

```bash
# 查看磁盘使用情况（人类可读）
df -h

# 查看特定文件系统
df -h /home

# 只显示本地文件系统
df -hT -x tmpfs -x devtmpfs

# 显示 inode 使用情况
df -i

# 以特定单位显示
df -BM    # 兆字节
df -BG    # 吉字节
```

#### 1.2 输出解读

```bash
# 示例输出:
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        50G   35G   13G  73% /
/dev/sdb1       200G  120G   70G  63% /data
tmpfs           3.9G     0  3.9G   0% /dev/shm

# 字段说明:
# Filesystem: 文件系统设备
# Size: 总大小
# Used: 已使用
# Avail: 可用空间
# Use%: 使用百分比
# Mounted on: 挂载点
```

| 选项 | 说明 |
|------|------|
| `-h` | 人类可读格式 |
| `-T` | 显示文件系统类型 |
| `-i` | 显示 inode 信息 |
| `-x TYPE` | 排除特定类型 |
| `-B SIZE` | 指定块大小 |
| `-P` | POSIX 输出格式 |

### 第2节：du 目录大小

#### 2.1 基本使用

```bash
# 查看当前目录大小
du -sh .

# 查看子目录大小
du -sh */

# 按大小排序
du -sh */ | sort -rh

# 查看前 10 个大目录
du -sh * 2>/dev/null | sort -rh | head -10

# 限制深度
du -h --max-depth=1 .
```

#### 2.2 du 高级用法

```bash
# 排除特定目录
du -sh --exclude='node_modules' --exclude='.git' .

# 只显示大于 100MB 的目录
du -sh */ 2>/dev/null | awk '$1 ~ /[0-9.]+G/ || ($1 ~ /[0-9]+M/ && $1+0 > 100)'

# 显示文件数量和大小
du -sh --count-links .

# 查看特定文件类型大小
find . -name "*.log" -type f -exec du -ch {} + | tail -1

# 查看磁盘使用情况（人类可读）
ncdu .
```

### 第3节：mount/umount

#### 3.1 挂载操作

```bash
# 查看当前挂载
mount
cat /proc/mounts

# 挂载文件系统
sudo mount /dev/sdb1 /mnt/data

# 挂载为只读
sudo mount -o ro /dev/sdb1 /mnt/data

# 挂载 ISO 文件
sudo mount -o loop image.iso /mnt/iso

# 挂载 NFS 共享
sudo mount -t nfs server:/shared /mnt/nfs

# 挂载 CIFS/SMB 共享
sudo mount -t cifs //server/share /mnt/smb -o user=username,password=pass
```

#### 3.2 卸载操作

```bash
# 卸载文件系统
sudo umount /mnt/data

# 卸载繁忙的文件系统
sudo umount -l /mnt/data    # 延迟卸载
sudo umount -f /mnt/data    # 强制卸载

# 查看谁在使用挂载点
sudo lsof +D /mnt/data
sudo fuser -m /mnt/data
```

#### 3.3 /etc/fstab 配置

```bash
# /etc/fstab 格式
# <设备>  <挂载点>  <文件系统>  <选项>  <dump>  <fsck>
/dev/sda1   /         ext4    defaults        0 1
/dev/sdb1   /data     ext4    defaults        0 2
tmpfs       /dev/shm  tmpfs   defaults        0 0

# 挂载 NFS（开机自动挂载）
server:/shared  /mnt/nfs  nfs  defaults,_netdev  0 0

# 挂载 CIFS
//server/share  /mnt/smb  cifs  credentials=/etc/samba/creds,uid=1000  0 0
```

### 第4节：fdisk/parted 分区管理

#### 4.1 fdisk 使用

```bash
# 查看分区表
sudo fdisk -l

# 交互式分区
sudo fdisk /dev/sdb

# 常用命令:
# p - 打印分区表
# n - 新建分区
# d - 删除分区
# t - 更改分区类型
# w - 保存更改
# q - 不保存退出
```

#### 4.2 parted 使用

```bash
# 查看分区
sudo parted /dev/sdb print

# 创建分区
sudo parted /dev/sdb mklabel gpt
sudo parted /dev/sdb mkpart primary ext4 0% 100%

# 对齐分区（SSD 优化）
sudo parted /dev/sdb mkpart primary ext4 1MiB 100%

# 删除分区
sudo parted /dev/sdb rm 1
```

### 第5节：LVM 逻辑卷管理

#### 5.1 LVM 基本概念

| 概念 | 说明 |
|------|------|
| PV (Physical Volume) | 物理卷，实际磁盘或分区 |
| VG (Volume Group) | 卷组，多个 PV 的集合 |
| LV (Logical Volume) | 逻辑卷，从 VG 中划分 |

#### 5.2 LVM 操作

```bash
# 创建物理卷
sudo pvcreate /dev/sdb /dev/sdc

# 查看物理卷
sudo pvs
sudo pvdisplay

# 创建卷组
sudo vgcreate data_vg /dev/sdb /dev/sdc

# 查看卷组
sudo vgs
sudo vgdisplay

# 创建逻辑卷
sudo lvcreate -L 50G -n data_lv data_vg
sudo lvcreate -l 100%FREE -n data_lv data_vg  # 使用所有空间

# 查看逻辑卷
sudo lvs
sudo lvdisplay

# 格式化逻辑卷
sudo mkfs.ext4 /dev/data_vg/data_lv

# 挂载逻辑卷
sudo mount /dev/data_vg/data_lv /mnt/data

# 扩展逻辑卷
sudo lvextend -L +20G /dev/data_vg/data_lv
sudo resize2fs /dev/data_vg/data_lv

# 缩减逻辑卷（需要先卸载）
sudo umount /mnt/data
sudo resize2fs /dev/data_vg/data_lv 30G
sudo lvreduce -L 30G /dev/data_vg/data_lv
```

### 第6节：RAID 概念

#### 6.1 RAID 级别对比

| 级别 | 最少磁盘 | 容错 | 性能 | 可用容量 |
|------|----------|------|------|----------|
| RAID 0 | 2 | 无 | 读写最快 | 100% |
| RAID 1 | 2 | 1 块故障 | 读快写慢 | 50% |
| RAID 5 | 3 | 1 块故障 | 读快写中 | (N-1)/N |
| RAID 6 | 4 | 2 块故障 | 读快写慢 | (N-2)/N |
| RAID 10 | 4 | 每组 1 块 | 读写快 | 50% |

#### 6.2 软件 RAID

```bash
# 创建 RAID 1（镜像）
sudo mdadm --create /dev/md0 --level=1 --raid-devices=2 /dev/sdb /dev/sdc

# 查看 RAID 状态
cat /proc/mdstat
sudo mdadm --detail /dev/md0

# 保存 RAID 配置
sudo mdadm --detail --scan | sudo tee -a /etc/mdadm.conf

# 替换故障磁盘
sudo mdadm --manage /dev/md0 --remove /dev/sdb
sudo mdadm --manage /dev/md0 --add /dev/sdd
```

### 第7节：磁盘健康检查

```bash
# 查看磁盘 SMART 信息
sudo smartctl -a /dev/sda

# 运行 SMART 测试
sudo smartctl -t long /dev/sda

# 查看测试结果
sudo smartctl -l selftest /dev/sda

# 检查文件系统错误
sudo fsck /dev/sda1

# 检查坏块
sudo badblocks -v /dev/sdb
```
