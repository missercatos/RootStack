# Linux 分区结构全解

分区是存储管理的基础层，决定了操作系统如何组织数据、如何引导、以及磁盘空间如何分配。
本章从磁盘物理结构出发，系统讲解 MBR 与 GPT 两种分区表的原理、Linux 标准分区布局、
分区对齐策略，以及 systemd 的 Discoverable Partitions Specification。

---

## 分区基础

### 磁盘物理结构

机械硬盘（HDD）由盘片、磁头、主轴电机组成。每个盘片两面均可存储数据，每面被划分为
数千个同心圆磁道（track），磁道进一步被划分为扇区（sector）。扇区是磁盘 I/O 的最小
物理单元。

固态硬盘（SSD）没有机械部件，数据存储在 NAND 闪存颗粒中。SSD 的页（page）大小通常
为 $4\text{KiB}$ 或 $16\text{KiB}$，块（block）由多个页组成，典型为 $128\text{KiB}$–$512\text{KiB}$。
SSD 的写入以页为单位，擦除以块为单位，这一特性直接影响分区对齐策略。

现代磁盘容量增长使传统的 CHS（Cylinder-Head-Sector）寻址方式在 $8.4\text{GiB}$ 以上
磁盘上失效，取而代之的是 LBA。

### 逻辑块寻址（LBA）

LBA（Logical Block Addressing）将整个磁盘抽象为一个线性编号的块序列，从 $LBA\ 0$
开始。操作系统和分区表只关心 LBA 编号，不再感知物理几何结构。

LBA 与物理扇区的对应关系：

- 传统磁盘：$1\ LBA = 1\ 物理扇区 = 512\text{B}$
- 4Kn 磁盘：$1\ LBA = 1\ 物理扇区 = 4096\text{B}$
- 512e 磁盘：$1\ LBA = 1\ 仿真扇区 = 512\text{B}$（实际物理扇区 $4096\text{B}$）

分区表、文件系统都基于 LBA 编号工作。

### 扇区大小：512B vs 4Kn vs 512e

| 扇区类型 | 逻辑扇区 | 物理扇区 | 典型设备 | 兼容性 |
|----------|----------|----------|----------|--------|
| 512n     | $512\text{B}$ | $512\text{B}$ | 旧HDD | 最佳 |
| 512e     | $512\text{B}$ | $4096\text{B}$ | 近年HDD/SSD | 良好 |
| 4Kn      | $4096\text{B}$ | $4096\text{B}$ | 新企业级HDD | 需要OS支持 |

512e（Advanced Format）通过固件模拟 $512\text{B}$ 逻辑扇区以保持向后兼容，但内部
物理扇区为 $4096\text{B}$。若分区未对齐到 $4096\text{B}$ 边界，一次逻辑写入可能触发
两个物理扇区的读-改-写操作，导致性能下降。

检测磁盘扇区大小：

```bash
lsblk -t /dev/sda
cat /sys/block/sda/queue/physical_block_size
cat /sys/block/sda/queue/logical_block_size
sudo hdparm -I /dev/sda | grep "Logical Sector"
```

---

## MBR 分区表

### 结构（512 字节）

MBR（Master Boot Record）位于磁盘第一个扇区（LBA 0），共 $512\text{B}$，结构如下：

| 偏移（字节） | 长度 | 内容 |
|-------------|------|------|
| 0x000       | 446  | 引导代码（Bootstrap Code） |
| 0x1BE       | 16   | 分区表项 1 |
| 0x1CE       | 16   | 分区表项 2 |
| 0x1DE       | 16   | 分区表项 3 |
| 0x1EE       | 16   | 分区表项 4 |
| 0x1FE       | 2    | 签名 $0x55AA$ |

每个分区表项 $16\text{B}$ 的结构：

| 偏移 | 长度 | 含义 |
|------|------|------|
| 0    | 1    | 引导标志（$0x80$=活动，$0x00$=非活动） |
| 1    | 3    | 起始 CHS 地址 |
| 4    | 1    | 分区类型 ID（type ID） |
| 5    | 3    | 结束 CHS 地址 |
| 8    | 4    | 起始 LBA（小端序） |
| 12   | 4    | 扇区总数（小端序） |

### 限制

MBR 分区表存在三个根本性限制：

1. **容量限制**：扇区总数字段为 32 位，最大寻址 $2^{32}$ 个扇区。按 $512\text{B}$/扇区计算，最大磁盘容量为 $2^{32} \times 512\text{B} = 2\text{TiB}$。
2. **主分区数量**：分区表仅有 $4 \times 16 = 64\text{B}$ 空间，最多容纳 4 个主分区。
3. **单点故障**：MBR 仅存一份，损坏即丢失全部分区信息。

扩展分区（Extended Partition）是对限制 2 的折中方案：将一个主分区标记为扩展分区
（type ID $0x05$ 或 $0x0F$），在其内部建立 EBR（Extended Boot Record）链表，
每个 EBR 描述一个逻辑分区。扩展分区本身占用一个主分区名额。

### MBR type ID 对照表

| Type ID | 文件系统/用途 | 说明 |
|---------|--------------|------|
| $0x01$ | FAT12       | 小容量 FAT |
| $0x04$ | FAT16 <32M  | 早期 DOS |
| $0x05$ | Extended    | 扩展分区（CHS） |
| $0x06$ | FAT16B      | 常规 FAT16 |
| $0x07$ | NTFS/exFAT  | Windows 常用 |
| $0x0B$ | FAT32 (CHS) | Windows 常用 |
| $0x0C$ | FAT32 (LBA) | Windows 常用 |
| $0x0F$ | Extended (LBA) | LBA 寻址的扩展分区 |
| $0x82$ | Linux swap  | Linux 交换分区 |
| $0x83$ | Linux       | Linux 原生分区 |
| $0x85$ | Linux Extended | Linux 扩展分区 |
| $0x8E$ | LVM         | 逻辑卷管理 |
| $0xFD$ | Linux RAID  | Linux autodetect RAID |

### MBR 备份与恢复

```bash
# 备份 MBR
sudo dd if=/dev/sda of=/backup/mbr.bin bs=512 count=1

# 恢复 MBR（仅前 446 字节，保留分区表）
sudo dd if=/backup/mbr.bin of=/dev/sda bs=446 count=1 conv=notrunc

# 恢复完整 MBR（包含分区表，危险操作）
sudo dd if=/backup/mbr.bin of=/dev/sda bs=512 count=1
```

> **警告**：恢复完整 MBR 会覆盖当前分区表，仅在分区表未改变时安全。

---

## GPT 分区表

### 结构

GPT（GUID Partition Table）是 UEFI 标准的一部分，解决了 MBR 的三大限制。

GPT 磁盘的扇区布局：

| LBA | 内容 |
|-----|------|
| 0   | Protective MBR（兼容层） |
| 1   | GPT 头（Primary Header） |
| 2–33 | 分区项数组（$128$ 项 $\times 128\text{B}$） |
| 34–... | 分区数据区域 |
| LBA -33 至 -2 | 备份分区项数组 |
| LBA -1 | 备份 GPT 头 |

GPT 头（$512\text{B}$，位于 LBA 1）的关键字段：

| 字段 | 说明 |
|------|------|
| Signature | 固定为 `EFI PART` |
| Revision | 当前版本 $1.0$ |
| Header Size | $92\text{B}$ |
| Header CRC32 | 头部校验和（计算时此字段置零） |
| My LBA | 当前头所在的 LBA（$1$） |
| Alternate LBA | 备份头所在的 LBA |
| First Usable LBA | 分区数据起始 LBA |
| Last Usable LBA | 分区数据结束 LBA |
| Disk GUID | 磁盘唯一标识符 |
| Partition Entry Start LBA | 分区项数组起始 LBA（$2$） |
| Number of Partition Entries | 分区项数量（默认 $128$） |
| Partition Entry Size | 每个分区项大小（$128\text{B}$） |
| Partition Array CRC32 | 所有分区项的校验和 |

GPT 使用 CRC32 校验和保护头部和分区项数组的完整性。BIOS/固件在启动时校验，
操作系统在挂载时校验。损坏的 CRC32 会导致分区表被拒绝。

### GPT type GUID 对照表

GPT 使用 $128\text{位}$ GUID 标识分区类型，而非 MBR 的单字节 type ID。

| 分区类型 | GUID |
|----------|------|
| Linux Filesystem | $0FC63DAF-8483-4772-8E79-3D69D8477DE4$ |
| Linux Swap | $0657FD6D-A4AB-43C4-84E5-0933C84B4F4F$ |
| Linux LVM | $E6D6D379-F507-44C2-A23C-238F2A3DF928$ |
| Linux RAID | $A19D8809-0501-49B0-9976-1FFC2E6BA593$ |
| Linux /home | $933AC7E1-2EB4-4F13-B844-0E14E2AEF915$ |
| Linux /boot | $21686148-6449-6E6F-744E-656564454649$ |
| EFI System Partition (ESP) | $C12A7328-F81F-11D2-BA4B-00A0C93EC93B$ |
| BIOS Boot Partition | $21686148-6449-6E6F-744E-656564454649$ |
| Microsoft Basic Data | $EBD0A0A2-B9E5-4433-87C0-68B6B72699C7$ |
| Microsoft Reserved | $E3C9E316-0B5C-4DB8-817D-F92DF00215AE$ |
| Windows Recovery | $DE94BBA4-06D1-4D40-A16A-BFD50179D6AC$ |

### Protective MBR vs Hybrid MBR

**Protective MBR**（保护性 MBR）是 GPT 磁盘 LBA 0 的标准内容。它创建一个覆盖
整个磁盘的 type ID $0xEE$ 分区，使不识别 GPT 的工具不会误操作磁盘。

**Hybrid MBR**（混合 MBR）是 GPT 磁盘上非标准地写入真实分区表项的做法。其目的是
让 Legacy BIOS 工具或旧操作系统（如 Windows XP）能够访问部分 GPT 分区。

混合 MBR 的风险：
- 违反 GPT 规范，可能导致数据丢失
- GPT 和 MBR 分区表可能产生冲突
- 双重引导场景下容易引发问题

> **建议**：除非有明确的兼容性需求，不要使用混合 MBR。

### GPT 备份头（LBA -1）

GPT 在磁盘末尾保留完整的分区项数组和头部备份。当主 GPT 头损坏时，可用备份恢复：

```bash
# 使用 sgdisk 恢复 GPT 备份头
sudo sgdisk --load-backup=/dev/sda

# 使用 gdisk：进入专家模式后选择 recover
sudo gdisk /dev/sda
# 输入 x 进入专家模式
# 输入 e 从备份头重建主头
# 输入 w 写入
```

---

## BIOS vs UEFI 引导与分区

### BIOS + MBR

传统引导流程：

1. BIOS POST（加电自检）
2. BIOS 读取 LBA 0（MBR）的引导代码
3. 引导代码加载活动分区的 VBR（Volume Boot Record）
4. VBR 加载操作系统引导程序（如 GRUB stage 2）
5. 引导程序加载内核和 initramfs

分区要求：
- 只能使用 MBR 分区表
- 最多 4 个主分区
- 最大磁盘容量 $2\text{TiB}$

### BIOS + GPT（BIOS Boot Partition ef02）

GRUB 2 支持在 BIOS 模式下使用 GPT 磁盘，但需要一个特殊的 **BIOS Boot Partition**
（type GUID $21686148-6449-6E6F-744E-656564454649$，MBR type $0xEF$）。

BIOS Boot Partition 的作用：
- 存放 GRUB 的 core.img（阶段 1.5/2 引导映像）
- 大小通常 $1\text{MiB}$ 足够
- 因为 MBR 只有 $446\text{B}$ 存放引导代码，无法直接指向 GPT 分区

```bash
# 创建 BIOS Boot Partition
sudo parted /dev/sda mkpart primary 1MiB 2MiB
sudo sgdisk --typecode=1:EF02 /dev/sda
```

### UEFI + GPT（ESP ef00）

UEFI 引导流程：

1. UEFI 固件读取 NVRAM 中的启动项
2. 固件挂载 EFI System Partition（ESP）
3. 执行 ESP 中的 EFI 应用程序（如 `\EFI\ubuntu\grubx64.efi`）
4. EFI 应用程序加载操作系统

ESP 要求：
- 分区类型 GUID：$C12A7328-F81F-11D2-BA4B-00A0C93EC93B$
- MBR type ID：$0xEF$
- 文件系统：FAT32（$vfat$）
- 挂载点：`/boot/efi` 或 `/boot`

```bash
# 创建 ESP
sudo parted /dev/sda mkpart primary fat32 1MiB 513MiB
sudo sgdisk --typecode=1:EF00 /dev/sda
sudo mkfs.vfat -F 32 /dev/sda1
sudo mkdir -p /boot/efi
sudo mount /dev/sda1 /boot/efi
```

### Secure Boot 对分区的要求

Secure Boot 是 UEFI 规范的安全特性，要求 EFI 二进制文件经过可信密钥签名。

与分区的间接关系：
- ESP 必须完整可用，不能被未授权修改
- Shim（第一阶段引导程序）由 Microsoft 签名，可链式加载发行版签名的 GRUB
- 分区表本身不受 Secure Boot 保护，但 GRUB 会校验内核签名

---

## Linux 分区 anatomy

### ESP（/boot/efi 或 /boot）

EFI System Partition 是 UEFI 系统的必需分区。

| 属性 | 推荐值 |
|------|--------|
| 大小 | $512\text{MiB}$–$1\text{GiB}$ |
| 文件系统 | FAT32 |
| 挂载点 | `/boot/efi`（多数发行版）或 `/boot`（Arch） |
| type GUID | $C12A7328-F81F-11D2-BA4B-00A0C93EC93B$ |

ESP 内容示例：
```
/EFI/
├── BOOT/
│   └── BOOTX64.efi        # 默认引导程序
├── ubuntu/
│   ├── grubx64.efi         # GRUB EFI 二进制
│   └── shimx64.efi         # Shim 签名引导
├── fedora/
│   └── grubx64.efi
└── memtest86+/
    └── memtestx64.efi      # 内存测试工具
```

### /boot（内核+initramfs）

`/boot` 存放 Linux 内核镜像、initramfs 和引导程序配置。

| 属性 | 推荐值 |
|------|--------|
| 大小 | $512\text{MiB}$–$1\text{GiB}$ |
| 文件系统 | ext4（独立分区时） |
| 是否需要独立分区 | 取决于加密/RAID 方案 |

独立 `/boot` 分区的场景：
- 根分区使用 LUKS 加密（GRUB 需要在解密前读取内核）
- 使用 LVM 且 GRUB 不支持直接从 LV 引导（旧版 GRUB）
- BIOS + GPT 需要 BIOS Boot Partition 旁边有可读分区

### /（根分区）

根分区包含操作系统核心目录树。

| 属性 | 推荐值 |
|------|--------|
| 最小大小 | $20\text{GiB}$（桌面）/ $8\text{GiB}$（服务器） |
| 文件系统 | ext4、btrfs、xfs |
| 挂载选项 | `defaults`（通常足够） |

现代 Linux 支持从 LVM、LUKS、RAID 等复杂存储栈引导根分区，前提是 initramfs
包含必要的模块。

### /home

用户数据分区，与系统分区分离便于独立备份和系统重装。

| 属性 | 推荐值 |
|------|--------|
| 大小 | 剩余磁盘空间或按需分配 |
| 文件系统 | ext4、btrfs、xfs |
| 权限 | $700$（用户私有） |

独立 `/home` 的优势：
- 系统重装时不丢失用户数据
- 可使用不同文件系统（如 btrfs 快照）
- 便于跨发行版共享数据分区

### swap（分区 vs 文件、大小策略、hibernation）

Swap 提供虚拟内存扩展和休眠支持。

**Swap 分区 vs Swap 文件**：

| 对比项 | Swap 分区 | Swap 文件 |
|--------|----------|----------|
| 性能 | 略优（无文件系统开销） | 差异可忽略（现代内核） |
| 灵活性 | 需要调整分区大小 | 可随时增删 |
| Hibernation | 原生支持 | 需要额外配置 |
| 管理工具 | parted/fdisk | `dd` 或 `fallocate` |

**大小策略**：

传统规则：$\text{swap} = 2 \times \text{RAM}$。现代策略：

| RAM 大小 | 推荐 Swap | 说明 |
|----------|-----------|------|
| $< 4\text{GiB}$ | $4\text{GiB}$ | 最低保障 |
| $4\text{–}16\text{GiB}$ | $4\text{–}8\text{GiB}$ | 适度缓冲 |
| $16\text{–}64\text{GiB}$ | $4\text{–}8\text{GiB}$ | 可选 |
| $> 64\text{GiB}$ | $4\text{GiB}$ 或无 | 看 OOM 策略 |

若需要 hibernation（挂起到磁盘）：$\text{swap} \geq \text{RAM 大小} + \sqrt{\text{RAM}}$，
其中 $\sqrt{\text{RAM}}$ 为预留量（单位 GiB）。

```bash
# 创建 swap 文件
sudo dd if=/dev/zero of=/swapfile bs=1M count=8192 status=progress
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
# /etc/fstab:
# /swapfile  none  swap  sw  0  0
```

### /var（日志、包缓存）

`/var` 包含可变数据：日志、邮件、打印队列、包缓存等。

| 属性 | 推荐值 |
|------|--------|
| 大小 | $10\text{–}20\text{GiB}$（通用服务器） |
| 文件系统 | ext4、xfs |
| 独立分区原因 | 防止日志膨胀耗尽根空间 |

高日志流量的服务器（如 web 服务器、数据库）应考虑独立 `/var` 分区或使用
`logrotate` 控制增长。

### /tmp

临时文件存放目录，系统重启后可清空。

| 属性 | 推荐值 |
|------|--------|
| 大小 | $5\text{–}10\text{GiB}$ 或使用 tmpfs |
| 文件系统 | tmpfs（内存）或 ext4 |
| 挂载选项 | `noexec,nosuid,nodev`（安全加固） |

systemd 默认将 `/tmp` 挂载为 tmpfs（占用 RAM），适合内存充足（$> 16\text{GiB}$）
的系统。I/O 密集型工作负载可能需要磁盘上的 `/tmp`。

### /usr（只读 + 组合挂载）

`/usr` 包含用户空间程序和库，是系统最大的目录之一。

**UsrMerge**：现代 Linux 发行版（Fedora、Arch、Debian 12+）将 `/bin`、`/sbin`
合并到 `/usr/bin`、`/usr/sbin`，通过符号链接兼容旧路径。

独立 `/usr` 分区的场景：
- 嵌入式系统（只读根文件系统 + 可写的 `/usr`）
- 容器镜像优化

### 单分区 vs 多分区决策树

```
系统类型？
├── 桌面/笔记本
│   ├── UEFI？
│   │   ├── 是 → ESP + / + swap（文件）
│   │   └── 否 → / + swap（文件）
│   └── 需要加密？ → ESP + /boot + LUKS(/ + swap)
├── 服务器
│   ├── 日志密集？ → ESP + / + /var + swap
│   ├── 使用 LVM？ → ESP + / + LVM（/var, /home, swap）
│   └── 简单部署 → ESP + / + swap
├── 容器宿主
│   └── ESP + /（btrfs，子卷隔离）+ swap
└── 嵌入式/IoT
    └── 只读 / + 可写 /var（tmpfs 或 overlay）
```

---

## 分区大小策略

### /boot：512M-1G

`/boot` 分区需容纳多个内核版本。每个内核 + initramfs 约 $80\text{–}150\text{MiB}$。
保留 $3\text{–}5$ 个内核版本，$512\text{MiB}$ 足够；若使用大内核配置或多个架构，
考虑 $1\text{GiB}$。

```bash
# 查看当前 /boot 占用
du -sh /boot
# 查看已安装内核数量
rpm -qa kernel 2>/dev/null || dpkg -l 'linux-image-*' | grep ^ii
```

### swap：RAM 大小策略

根据用途确定 swap 大小：

| 用途 | Swap 大小 | 依据 |
|------|-----------|------|
| 无休眠桌面 | $2\text{–}4\text{GiB}$ | 防止 OOM |
| 休眠笔记本 | $\text{RAM} + 2\text{GiB}$ | 写入全部 RAM 内容 |
| 数据库服务器 | $4\text{–}8\text{GiB}$ | 排序/哈希溢出 |
| HPC 计算节点 | $0$ 或 $4\text{GiB}$ | 避免 swap 拖慢计算 |
| 虚拟化宿主 | $4\text{–}8\text{GiB}$ | 虚拟机内存过量使用 |

Swappiness 参数控制内核使用 swap 的倾向（$0\text{–}200$，默认 $60$）：

```bash
# 查看当前 swappiness
cat /proc/sys/vm/swappiness
# 临时修改
sudo sysctl vm.swappiness=10
# 永久修改
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.d/99-swappiness.conf
```

### /var：日志增长预估

`/var/log` 的增长速度取决于日志服务和应用。估算公式：

$$\text{日志量/天} = \sum_{i} \text{服务}_i \times \text{每条大小}_i \times \text{条数/天}_i$$

典型值：
- 系统日志（journald）：$100\text{–}500\text{MiB}$/天
- Web 服务器（Apache/Nginx）：$1\text{–}10\text{GiB}$/天（高流量）
- 数据库：$100\text{MiB}$–$1\text{GiB}$/天

建议：`/var` 至少 $20\text{GiB}$，启用 `logrotate`，高流量服务器独立分区。

### /home：用户数据需求

估算 `/home` 大小：

$$\text{总需求} = N_{\text{用户}} \times (\text{文档} + \text{媒体} + \text{开发}) + \text{弹性余量}$$

| 用户类型 | 典型空间需求 |
|----------|-------------|
| 轻度使用（邮件、浏览） | $10\text{–}30\text{GiB}$ |
| 开发者 | $50\text{–}200\text{GiB}$ |
| 创意工作（视频、设计） | $200\text{GiB}$–$1\text{TiB}$ |
| 数据科学家 | $100\text{–}500\text{GiB}$ |

---

## 分区对齐

### 4K 对齐（Advanced Format）

Advanced Format 磁盘使用 $4096\text{B}$ 物理扇区。分区起始和结束位置必须是
$4096\text{B}$（即 $8$ 个 $512\text{B}$ 扇区）的整数倍，否则发生跨扇区写入。

性能影响：
- 随机写入：未对齐导致 $2\times$–$10\times$ 性能下降
- 顺序写入：影响较小但仍可测量
- SSD：未对齐增加写放大，降低寿命

### parted 1MiB 起始

`parted` 默认使用 $1\text{MiB}$（$1048576\text{B}$）作为分区起始偏移，
这自动满足 $4096\text{B}$ 对齐要求，因为 $1048576 \mod 4096 = 0$。

```bash
# parted 默认 1MiB 对齐
sudo parted /dev/sda mkpart ext4 1MiB 100%
# 验证对齐
sudo parted /dev/sda align-check optimal 1
```

### 性能影响

使用 `fio` 验证对齐对性能的影响：

```bash
# 未对齐的随机写入测试（模拟）
fio --name=unaligned --ioengine=libaio --direct=1 \
    --bs=4k --iodepth=1 --rw=randwrite \
    --filename=/dev/sda --offset=512 --size=1G

# 对齐的随机写入测试
fio --name=aligned --ioengine=libaio --direct=1 \
    --bs=4k --iodepth=1 --rw=randwrite \
    --filename=/dev/sda --offset=1048576 --size=1G
```

---

## Discoverable Partitions Specification

### systemd 约定的 GPT type GUID

systemd 定义了一套标准的 GPT 分区类型 GUID，使系统组件能够自动识别分区用途。
这被称为 **Discoverable Partitions Specification**（DPS）。

| 分区用途 | GUID | 挂载点 |
|----------|------|--------|
| Boot Loader Partition | $C12A7328-F81F-11D2-BA4B-00A0C93EC93B$ | `/boot/efi` |
| Root Partition (x86-64) | $4F68BCE3-E8CD-4DB1-96E7-FBCAF984B709$ | `/` |
| Root Partition (ARM64) | $B921B045-1DF0-41C3-AF44-4C6F280D3FAE$ | `/` |
| Root Partition (IA-64) | $993D8D3D-F80E-4225-BC1B-9771C340B159$ | `/` |
| /usr Partition (x86-64) | $8484680C-9521-48C6-9C20-28206FD5E49A$ | `/usr` |
| /home Partition | $933AC7E1-2EB4-4F13-B844-0E14E2AEF915$ | `/home` |
| /var Partition | $4D21B016-B534-45C2-A9FB2C99805E6861$ | `/var` |
| /var/tmp | $7EC6F557-3BC5-4ACA-B7DC-2ADC39F2C6C3$ | `/var/tmp` |
| /var/log | $2568E4C2-3096-4D5A-B0B8-26E44188EF51$ | `/var/log` |
| Swap | $0657FD6D-A4AB-43C4-84E5-0933C84B4F4F$ | [swap] |
| Extended Boot Loader | $BC13C2FF-59E6-4262-A352-B275FD6F7172$ | `/boot` |

### A/B 分区方案

A/B 分区方案（也称 Seamless Updates）主要用于 Android 和嵌入式系统，也适用于
原子更新的 Linux 系统。

基本思路：磁盘上保留两套根分区（A 和 B），一次只激活其中一套。更新时将新系统写入
非活动分区，然后切换引导标记。

```
磁盘布局：
├── Boot Partition（共享）
├── Slot A: 根分区 + /usr + /var
├── Slot B: 根分区 + /usr + /var
└── 数据分区（共享 /home）
```

优势：
- 更新原子性：失败可立即回滚
- 无需单独的恢复分区
- 减少用户等待时间

### 与 systemd-boot 的关系

`systemd-boot`（formerly gummiboot）是一个轻量级 UEFI 引导程序，原生支持 DPS：

- 自动发现 ESP 并加载 EFI 可执行文件
- 自动发现 XBOOTLDR 分区（`/boot`）
- 读取 BLS（Boot Loader Specification）条目
- 与 Secure Boot 兼容

```bash
# 安装 systemd-boot
sudo bootctl install

# 查看引导配置
bootctl status
ls /boot/loader/entries/
```

BLS 条目示例（`/boot/loader/entries/arch.conf`）：
```
title   Arch Linux
linux   /vmlinuz-linux
initrd  /initramfs-linux.img
options root=/dev/sda2 rw
```

---

## 参考命令速查

```bash
# 查看所有分区和文件系统
lsblk -f
blkid

# 查看分区表类型
sudo parted /dev/sda print

# 查看 GPT 分区详情
sudo sgdisk -p /dev/sda

# 查看 MBR 分区详情
sudo fdisk -l /dev/sda

# 检查分区对齐
sudo parted /dev/sda align-check optimal 1

# 查看挂载情况
findmnt --real
cat /proc/mounts
```

---

## 总结

分区方案的选择取决于引导方式（BIOS/UEFI）、系统用途（桌面/服务器/嵌入式）、
安全需求（加密/Secure Boot）和运维策略（原子更新/快照）。

核心原则：
1. UEFI 系统始终使用 GPT，BIOS 系统在 $2\text{TiB}$ 以下可使用 MBR
2. 所有分区必须 $4\text{KiB}$ 对齐
3. Swap 大小根据实际用途而非固定公式确定
4. 独立分区提供隔离性但增加管理复杂度
5. 遵循 Discoverable Partitions Specification 有利于系统集成
