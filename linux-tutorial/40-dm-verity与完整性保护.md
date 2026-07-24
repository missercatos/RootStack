# 40 - dm-verity 与完整性保护

> 数据完整性保护是系统安全的基石。从固件到内核、从根文件系统到单个文件，Linux 提供了一套完整的完整性验证栈——Secure Boot 确保引导加载程序可信，dm-verity 保障只读分区未被篡改，IMA/EVM 度量运行时文件完整性，fs-verity 在文件级别提供透明验证。本章将深入探讨这些机制的原理、配置与实战应用。

---

## 40.1 什么是数据完整性保护

数据完整性保护确保存储的数据未被篡改或损坏。根据保护层级不同，可分为：

```
┌─────────────────────────────────────────────┐
│              完整性保护层级                    │
│                                              │
│  ┌────────────────┐  引导阶段                 │
│  │  Secure Boot   │  UEFI 固件验证引导程序     │
│  └───────┬────────┘                          │
│          ▼                                    │
│  ┌────────────────┐  内核加载                  │
│  │  签名内核/initrd│  UEFI 或 GRUB 签名验证   │
│  └───────┬────────┘                          │
│          ▼                                    │
│  ┌────────────────┐  块设备层                  │
│  │  dm-verity     │  只读分区 Merkle 树验证    │
│  │  dm-integrity  │  可写分区完整性标签        │
│  └───────┬────────┘                          │
│          ▼                                    │
│  ┌────────────────┐  文件系统层                │
│  │  fs-verity     │  单文件 Merkle 树          │
│  └───────┬────────┘                          │
│          ▼                                    │
│  ┌────────────────┐  运行时                    │
│  │  IMA / EVM     │  文件度量与评估            │
│  └────────────────┘                          │
└─────────────────────────────────────────────┘
```

| 机制 | 保护目标 | 可写性 | 粒度 |
|------|----------|--------|------|
| Secure Boot | 引导程序、内核 | N/A | 固件级 |
| dm-verity | 块设备 | 只读 | 块级 |
| dm-integrity | 块设备 | 可写 | 块级 |
| fs-verity | 文件 | 只读（文件级） | 文件级 |
| IMA | 文件 | 可测量可写 | 文件级 |
| EVM | 文件元数据 | 保护 xattr | 元数据级 |

---

## 40.2 dm-verity 详解

### 设计目标

dm-verity 是 Linux 内核的 device-mapper 目标，提供 **只读块设备的透明完整性验证**。其核心目标：

- 验证每个读取的数据块未被篡改
- 使用 Merkle hash tree 实现高效验证
- 仅需要信任一个 root hash（可存储在安全位置）
- 读取时按需验证（lazy verification），不需要提前扫描整个设备

### Merkle Hash Tree 原理

```
                    ┌───────────┐
                    │ Root Hash │  ← 只需要信任这一个值
                    └─────┬─────┘
                    ┌─────┴─────┐
              ┌─────┤           ├─────┐
              ▼                       ▼
        ┌───────────┐          ┌───────────┐
        │ Hash 节点  │          │ Hash 节点  │  ← Hash 块层
        │ H(h1||h2) │          │ H(h3||h4) │
        └─────┬─────┘          └─────┬─────┘
        ┌─────┴─────┐          ┌─────┴─────┐
        ▼           ▼          ▼           ▼
   ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
   │ h1=    │ │ h2=    │ │ h3=    │ │ h4=    │  ← 叶子 Hash
   │ H(D1)  │ │ H(D2)  │ │ H(D3)  │ │ H(D4)  │
   └────┬───┘ └────┬───┘ └────┬───┘ └────┬───┘
        ▼          ▼          ▼          ▼
   ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
   │ Data 1 │ │ Data 2 │ │ Data 3 │ │ Data 4 │  ← 数据块
   └────────┘ └────────┘ └────────┘ └────────┘
```

验证过程：
1. 读取数据块 D1
2. 计算 H(D1)，与存储的 h1 比较
3. 计算 H(h1||h2)，与存储的 Hash 节点比较
4. 递归直到 Root Hash
5. Root Hash 匹配则数据完整

### 数据块、Hash 块、超级块

dm-verity 设备由三个部分组成：

```
┌──────────────────────────────────────────────┐
│                  块设备布局                    │
│                                               │
│  ┌──────────────────────┐                     │
│  │     数据区域          │  原始数据块           │
│  │  (Data Blocks)       │  默认 4096 字节/块    │
│  ├──────────────────────┤                     │
│  │     Hash 区域         │  Merkle 树 Hash 块   │
│  │  (Hash Blocks)       │  默认 4096 字节/块    │
│  ├──────────────────────┤                     │
│  │  超级块（可选）        │  dm-verity 元数据     │
│  │  (Superblock)        │                     │
│  └──────────────────────┘                     │
└──────────────────────────────────────────────┘
```

超级块包含：

| 字段 | 说明 |
|------|------|
| 版本 | dm-verity 版本（1） |
| 数据块大小 | 通常 4096 |
| Hash 块大小 | 通常 4096 |
| 数据块数量 | 数据区域的块数 |
| Hash 算法 | sha256（默认） |
| Salt | 用于防止 Rainbow 表攻击 |

### 使用 veritysetup 创建 verity 设备

```bash
# 安装 cryptsetup（包含 veritysetup）
sudo pacman -S cryptsetup

# 准备测试用的只读镜像
dd if=/dev/zero of=/tmp/test-data.img bs=1M count=100
mkfs.ext4 /tmp/test-data.img
mkdir /tmp/test-mnt
sudo mount /tmp/test-data.img /tmp/test-mnt
echo "完整性保护测试" | sudo tee /tmp/test-mnt/test.txt
sudo umount /tmp/test-mnt
```

#### veritysetup format

```bash
# 创建 verity hash 数据
# 数据设备和 hash 设备可以是同一个（hash 追加到数据后面）
# 或者分开存储

# 方式 1：Hash 存储在单独的文件/设备
sudo veritysetup format /tmp/test-data.img /tmp/test-hash.img

# 输出示例：
# VERITY header information for /tmp/test-hash.img
# UUID:            12345678-abcd-efgh-ijkl-123456789012
# Hash type:       1
# Data blocks:     25600
# Data block size: 4096
# Hash block size: 4096
# Hash algorithm:  sha256
# Salt:            a1b2c3d4e5f6...
# Root hash:       abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789

# 保存 root hash！这是信任锚点
ROOT_HASH="abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789"

# 方式 2：指定参数
sudo veritysetup format \
    --data-block-size=4096 \
    --hash-block-size=4096 \
    --hash=sha256 \
    --salt=random \
    /tmp/test-data.img /tmp/test-hash.img

# 方式 3：使用更安全的 Hash 算法
sudo veritysetup format --hash=sha512 /tmp/test-data.img /tmp/test-hash.img
```

#### veritysetup open

```bash
# 打开 verity 设备
sudo veritysetup open /tmp/test-data.img verity-test /tmp/test-hash.img $ROOT_HASH

# 现在可以挂载
sudo mount -o ro /dev/mapper/verity-test /tmp/test-mnt
cat /tmp/test-mnt/test.txt
# 输出：完整性保护测试

# 查看 dm 状态
sudo dmsetup status verity-test
# 0 204800 verity V 1 ...

# 查看设备映射
ls -la /dev/mapper/verity-test
```

#### veritysetup verify

```bash
# 离线验证（不创建 dm 设备）
sudo veritysetup verify /tmp/test-data.img /tmp/test-hash.img $ROOT_HASH
# 验证成功无输出，失败返回非零退出码

# 测试篡改检测
# 修改数据
sudo dd if=/dev/urandom of=/tmp/test-data.img bs=1 count=1 seek=12345 conv=notrunc

# 再次验证
sudo veritysetup verify /tmp/test-data.img /tmp/test-hash.img $ROOT_HASH
# Verification failed at position 12288.
# 返回码非零

# 如果 verity 设备已经打开，读取被篡改的块会触发 I/O 错误
```

#### veritysetup 完整参数

```bash
veritysetup format [options] <data_device> <hash_device>
veritysetup open <data_device> <name> <hash_device> <root_hash>
veritysetup verify <data_device> <hash_device> <root_hash>
veritysetup close <name>
veritysetup status <name>
veritysetup dump <hash_device>
```

| 选项 | 说明 |
|------|------|
| `--data-block-size` | 数据块大小（默认 4096） |
| `--hash-block-size` | Hash 块大小（默认 4096） |
| `--hash` | Hash 算法（sha256/sha512/sha1） |
| `--salt` | Salt 值（hex 或 "random"） |
| `--uuid` | 设备 UUID |
| `--no-superblock` | 不写入超级块 |
| `--format` | 格式版本（1 或 2） |
| `--fec-device` | FEC 设备（前向纠错） |
| `--fec-roots` | FEC 根数量 |

### 与内核参数集成

可以通过内核命令行参数在启动时配置 dm-verity：

```bash
# GRUB 配置
# /etc/default/grub
GRUB_CMDLINE_LINUX="dm-mod.create=\"verity-root,,,ro,0 DATA_SECTORS verity 1 DATA_DEV HASH_DEV 4096 4096 DATA_BLOCKS 1 sha256 ROOT_HASH SALT\""

# 具体示例
GRUB_CMDLINE_LINUX="dm-mod.create=\"verity-root,,,ro,0 204800 verity 1 /dev/sda2 /dev/sda3 4096 4096 25600 1 sha256 abcdef01234567890abcdef01234567890abcdef01234567890abcdef012345678 a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6\""

# root 参数指向 verity 设备
GRUB_CMDLINE_LINUX="root=/dev/dm-0 dm-mod.create=..."
```

### 在 initramfs 中启用 dm-verity

```bash
# 方法 1：使用 mkinitcpio hook

# 创建自定义 hook
# /etc/initcpio/hooks/verity
```

```bash
#!/bin/bash
# /etc/initcpio/hooks/verity

run_hook() {
    local data_dev hash_dev root_hash name

    data_dev="/dev/sda2"
    hash_dev="/dev/sda3"
    root_hash="abcdef0123456789..."
    name="verity-root"

    msg ":: Setting up dm-verity..."

    modprobe dm-verity

    veritysetup open "$data_dev" "$name" "$hash_dev" "$root_hash"

    if [ $? -ne 0 ]; then
        err "dm-verity 验证失败！系统可能被篡改。"
        launch_interactive_shell
    fi
}
```

```bash
# /etc/initcpio/install/verity
```

```bash
#!/bin/bash
# /etc/initcpio/install/verity

build() {
    add_module dm-verity
    add_binary veritysetup
    add_runscript
}

help() {
    cat <<HELPEOF
This hook enables dm-verity for root filesystem verification.
HELPEOF
}
```

```bash
# /etc/mkinitcpio.conf
HOOKS=(base udev autodetect modconf block verity filesystems keyboard fsck)

# 重建 initramfs
sudo mkinitcpio -P
```

### systemd 集成（systemd-veritysetup）

systemd 提供了原生的 dm-verity 集成：

```bash
# /etc/veritytab
# name  data_device  hash_device  root_hash  options
verity-root  /dev/sda2  /dev/sda3  abcdef0123...  root-hash-signature=/etc/verity-root.p7s

# 或使用 systemd-veritysetup-generator
# 内核参数方式
systemd.verity_root_data=/dev/sda2
systemd.verity_root_hash_data=/dev/sda3
systemd.verity_root_hash=abcdef0123...

# systemd 会自动生成 veritysetup 单元
systemctl status systemd-veritysetup@verity-root.service
```

### 错误处理模式

dm-verity 在检测到数据不一致时的行为：

```bash
# 通过 dm 表参数设置错误处理模式
# veritysetup open --restart-on-corruption ...
# veritysetup open --panic-on-corruption ...
# veritysetup open --ignore-corruption ...    # 仅用于调试

# 或通过内核参数
dm-verity.error_behavior=0    # EIO（默认，返回 I/O 错误）
dm-verity.error_behavior=1    # panic（内核恐慌）
dm-verity.error_behavior=2    # restart（重启系统）
```

| 模式 | 行为 | 使用场景 |
|------|------|----------|
| EIO（默认） | 返回 I/O 错误 | 通用 |
| panic | 内核恐慌 | 高安全环境 |
| restart | 重启系统 | 嵌入式、A/B 分区方案 |
| ignore | 忽略错误 | 仅调试 |

```bash
# restart 模式配合 A/B 分区使用
sudo veritysetup open \
    --restart-on-corruption \
    /dev/sda2 verity-root /dev/sda3 $ROOT_HASH
```

### 与 A/B 分区方案结合

A/B 分区方案配合 dm-verity 实现可靠的系统更新：

```
┌──────────────────────────────────────────────┐
│                A/B 分区方案                    │
│                                               │
│  Slot A (当前活跃)      Slot B (待更新)         │
│  ┌─────────────────┐   ┌─────────────────┐    │
│  │ system_a        │   │ system_b        │    │
│  │ (dm-verity 保护)│   │ (写入新系统)    │    │
│  ├─────────────────┤   ├─────────────────┤    │
│  │ hash_a          │   │ hash_b          │    │
│  └─────────────────┘   └─────────────────┘    │
│                                               │
│  更新流程：                                    │
│  1. 写入新系统到 Slot B                        │
│  2. 生成 Slot B 的 verity hash                 │
│  3. 保存新 root hash                          │
│  4. 切换到 Slot B 启动                         │
│  5. 验证成功 → 标记 Slot B 为活跃              │
│  6. 验证失败 → 回滚到 Slot A                   │
└──────────────────────────────────────────────┘
```

### 在 Android 中的应用

Android 从 4.4 开始使用 dm-verity（Verified Boot）：

```
Android Verified Boot (AVB) 流程：

1. BootROM 验证 Bootloader 签名
2. Bootloader 验证 boot.img（内核+initrd）签名
3. 内核通过 dm-verity 验证 system 分区
4. dm-verity root hash 存储在 vbmeta 分区中
5. vbmeta 使用 RSA/ECDSA 签名

关键分区：
- vbmeta: AVB 元数据（包含 root hash + 签名）
- boot: 内核 + initrd
- system: 系统分区（dm-verity 保护）
- vendor: 厂商分区（dm-verity 保护）
```

```bash
# 在 Android 设备上查看 verity 状态
adb shell
cat /proc/device-mapper/verity/status
# 或
dmctl table system-verity
```

### 在桌面 Linux 上的实验

```bash
# 创建一个完整的 verity 保护的只读根文件系统实验

# 1. 创建数据镜像
dd if=/dev/zero of=/tmp/rootfs.img bs=1M count=500
mkfs.ext4 /tmp/rootfs.img

# 2. 填充最小根文件系统
sudo mount /tmp/rootfs.img /mnt
sudo pacstrap /mnt base linux    # Arch Linux 最小安装
sudo umount /mnt

# 3. 创建 verity hash
sudo veritysetup format /tmp/rootfs.img /tmp/rootfs-hash.img
# 记录 root hash

# 4. 验证
sudo veritysetup verify /tmp/rootfs.img /tmp/rootfs-hash.img <root-hash>
echo $?   # 0 = 成功
```

### 签名验证（PKCS#7）

dm-verity 支持对 root hash 进行签名验证，防止 root hash 本身被篡改：

```bash
# 生成签名密钥对
openssl req -x509 -newkey rsa:4096 -keyout verity-key.pem \
    -out verity-cert.pem -days 3650 -nodes \
    -subj "/CN=dm-verity signing key"

# 对 root hash 签名
echo -n "$ROOT_HASH" | xxd -r -p > /tmp/root-hash.bin
openssl smime -sign -in /tmp/root-hash.bin -out /tmp/root-hash.p7s \
    -signer verity-cert.pem -inkey verity-key.pem \
    -outform DER -noattr -binary

# 将证书添加到内核 keyring（编译时或运行时）
# 编译时：将证书嵌入内核
# CONFIG_SYSTEM_TRUSTED_KEYS="certs/verity-cert.pem"

# 运行时加载
sudo keyctl padd asymmetric "dm-verity" %:.builtin_trusted_keys < verity-cert.pem

# 使用签名打开 verity 设备
sudo veritysetup open \
    --root-hash-signature=/tmp/root-hash.p7s \
    /tmp/rootfs.img verity-root /tmp/rootfs-hash.img $ROOT_HASH
```

内核配置要求：

```
CONFIG_DM_VERITY=y
CONFIG_DM_VERITY_VERIFY_ROOTHASH_SIG=y
CONFIG_SYSTEM_TRUSTED_KEYS="certs/verity-cert.pem"
```

---

## 40.3 dm-integrity

### 与 dm-verity 的区别

| 特性 | dm-verity | dm-integrity |
|------|-----------|-------------|
| 可写性 | 只读 | **可写** |
| 验证方式 | Merkle 树（全局 root hash） | 每块独立标签 |
| 用途 | 只读分区完整性 | 可写分区完整性 |
| 检测篡改 | 是 | 是 |
| 性能开销 | 低（仅读取时） | 中等（读写时） |
| 常见搭配 | 独立使用 | 与 dm-crypt 结合（AEAD） |

### 使用 integritysetup

```bash
# 安装
sudo pacman -S cryptsetup   # integritysetup 包含在 cryptsetup 中

# 创建 integrity 设备
sudo integritysetup format /dev/sdX
# 或指定算法
sudo integritysetup format --integrity sha256 /dev/sdX
# 或使用 HMAC（需要密钥）
sudo integritysetup format --integrity hmac-sha256 --integrity-key-file /path/to/key /dev/sdX

# 打开 integrity 设备
sudo integritysetup open /dev/sdX integrity-test
# 或使用 HMAC
sudo integritysetup open --integrity hmac-sha256 --integrity-key-file /path/to/key /dev/sdX integrity-test

# 格式化并挂载
sudo mkfs.ext4 /dev/mapper/integrity-test
sudo mount /dev/mapper/integrity-test /mnt

# 查看状态
sudo integritysetup status integrity-test

# 关闭
sudo umount /mnt
sudo integritysetup close integrity-test
```

### 与 dm-crypt 结合（认证加密）

dm-integrity + dm-crypt 实现 AEAD（Authenticated Encryption with Associated Data）：

```bash
# 使用 LUKS2 + integrity
# 这会自动使用 dm-crypt + dm-integrity 栈
sudo cryptsetup luksFormat --type luks2 --integrity aead \
    --cipher aes-gcm-random --key-size 256 /dev/sdX

# 或使用非 AEAD 模式（dm-crypt + 独立 integrity）
sudo cryptsetup luksFormat --type luks2 --integrity hmac-sha256 \
    --cipher aes-xts-plain64 --key-size 512 /dev/sdX

# 打开
sudo cryptsetup open /dev/sdX encrypted-integrity

# 查看设备栈
sudo dmsetup table
# 可以看到 crypt 和 integrity 两层

# 初次使用需要 wipe（integrity 标签初始化）
# cryptsetup 会提示是否 wipe，选择 YES

# 性能对比
# aes-xts-plain64 (仅加密):      ~3 GB/s
# aes-xts-plain64 + hmac-sha256: ~1.5 GB/s
# aes-gcm-random (AEAD):         ~2 GB/s
```

设备栈结构：

```
┌──────────────┐
│  文件系统     │
├──────────────┤
│  dm-crypt    │  加密层
├──────────────┤
│  dm-integrity│  完整性层
├──────────────┤
│  块设备      │  /dev/sdX
└──────────────┘
```

---

## 40.4 IMA/EVM（Integrity Measurement Architecture）

### IMA 概述

IMA 是 Linux 内核的完整性度量架构，在文件访问时进行度量和/或评估：

```
┌─────────────────────────────────────────┐
│                 IMA                      │
│                                          │
│  ┌───────────┐  ┌───────────────────┐   │
│  │  度量      │  │  评估             │   │
│  │ (Measure) │  │ (Appraise)       │   │
│  │           │  │                   │   │
│  │ 记录文件   │  │ 验证文件签名      │   │
│  │ Hash 到    │  │ 拒绝加载未签名    │   │
│  │ TPM PCR   │  │ 或被篡改的文件    │   │
│  └───────────┘  └───────────────────┘   │
│                                          │
│  ┌───────────────────────────────────┐   │
│  │  EVM（Extended Verification）     │   │
│  │  保护文件的安全扩展属性           │   │
│  │  （防止 IMA 签名被篡改）         │   │
│  └───────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### IMA 度量

```bash
# 内核配置
# CONFIG_IMA=y
# CONFIG_IMA_MEASURE_PCR_IDX=10

# 启用 IMA 度量（内核参数）
# ima_policy=tcb     # 度量所有可执行文件
# 或
# ima_policy=critical_data  # 仅度量关键数据

# 查看 IMA 度量日志
sudo cat /sys/kernel/security/ima/ascii_runtime_measurements

# 输出格式：
# PCR  模板Hash  模板  文件Hash  文件名
# 10   sha256:abc...  ima-ng  sha256:def...  /usr/bin/bash
# 10   sha256:ghi...  ima-ng  sha256:jkl...  /usr/lib/libc.so.6

# 度量列表中的条目数
sudo wc -l /sys/kernel/security/ima/ascii_runtime_measurements

# 查看违规计数
cat /sys/kernel/security/ima/violations
```

### IMA 评估

```bash
# 启用 IMA 评估（内核参数）
# ima_appraise=enforce    # 强制模式（拒绝未签名文件）
# ima_appraise=fix        # 修复模式（自动添加签名）
# ima_appraise=log        # 日志模式（仅记录，不拒绝）

# 对文件进行签名
# 生成 IMA 签名密钥
openssl genrsa -out ima-key.pem 2048
openssl req -new -x509 -key ima-key.pem -out ima-cert.pem -days 3650

# 使用 evmctl 签名文件
sudo pacman -S ima-evm-utils
sudo evmctl ima_sign -k ima-key.pem /usr/bin/bash

# 查看文件的 IMA 签名
getfattr -n security.ima /usr/bin/bash

# 批量签名
find /usr/bin -type f -exec sudo evmctl ima_sign -k ima-key.pem {} \;
```

### IMA 策略

```bash
# 自定义 IMA 策略
# /etc/ima/ima-policy

# 度量所有可执行文件
measure func=BPRM_CHECK

# 度量所有打开的文件（仅 root）
measure func=FILE_CHECK uid=0

# 评估所有可执行文件
appraise func=BPRM_CHECK appraise_type=imasig

# 评估内核模块
appraise func=MODULE_CHECK appraise_type=imasig

# 评估固件
appraise func=FIRMWARE_CHECK appraise_type=imasig

# 加载策略
echo "/etc/ima/ima-policy" > /sys/kernel/security/ima/policy
# 或通过内核参数
# ima_policy=/etc/ima/ima-policy
```

### EVM 扩展验证

EVM 保护文件的扩展属性（xattr），防止 IMA 签名被篡改：

```bash
# 内核配置
# CONFIG_EVM=y

# 启用 EVM（内核参数）
# evm=fix          # 修复模式
# evm=enforce      # 强制模式

# 初始化 EVM 密钥
# EVM 使用存储在 TPM 或内核 keyring 中的密钥

# 使用 HMAC 模式（需要密钥）
sudo evmctl hmac -k /etc/keys/evm-key /usr/bin/bash

# 使用签名模式（公钥验证）
sudo evmctl sign -k evm-key.pem /usr/bin/bash

# 查看 EVM 签名
getfattr -n security.evm /usr/bin/bash

# EVM 保护的属性列表
# security.ima       - IMA 签名
# security.selinux   - SELinux 标签
# security.capability - 文件 capability
# 文件元数据（uid, gid, mode, i_size, i_ino, ...）
```

---

## 40.5 fs-verity（文件级完整性）

### 与 dm-verity 的区别

| 特性 | dm-verity | fs-verity |
|------|-----------|-----------|
| 粒度 | 整个块设备 | 单个文件 |
| 文件系统 | 不依赖 | 需要文件系统支持 |
| 可写性 | 设备只读 | 仅被保护的文件只读 |
| Merkle 树位置 | 独立分区/文件 | 文件系统内部 |
| 使用场景 | 系统分区 | 单文件验证（APK、软件包） |

### 使用 fsverity

```bash
# 安装工具
sudo pacman -S fsverity-utils

# 内核配置
# CONFIG_FS_VERITY=y
# CONFIG_FS_VERITY_BUILTIN_SIGNATURES=y  # 内核签名验证

# 文件系统支持：
# ext4:  tune2fs -O verity /dev/sdXn
# f2fs:  原生支持
# btrfs: 内核 5.15+
```

#### 在 ext4 上启用

```bash
# 启用 ext4 verity 特性
sudo tune2fs -O verity /dev/sda2

# 或在创建文件系统时启用
mkfs.ext4 -O verity /dev/sda2

# 挂载（无需特殊选项）
sudo mount /dev/sda2 /mnt
```

#### 对文件启用 fs-verity

```bash
# 对文件启用 verity（文件必须只读）
echo "重要数据" > /mnt/important.txt
chmod a-w /mnt/important.txt

fsverity enable /mnt/important.txt

# 查看 verity 状态
fsverity measure /mnt/important.txt
# sha256:abcdef0123456789...  /mnt/important.txt

# 尝试修改受保护的文件
echo "篡改" >> /mnt/important.txt
# 失败：Operation not permitted

# 读取受保护的文件（透明验证）
cat /mnt/important.txt
# 如果文件被底层篡改（如直接修改块设备），读取时会报 I/O 错误
```

#### 使用签名

```bash
# 生成签名密钥
openssl genrsa -out fsverity-key.pem 4096
openssl x509 -req -in <(openssl req -new -key fsverity-key.pem -subj "/CN=fs-verity") \
    -signkey fsverity-key.pem -out fsverity-cert.pem -days 3650

# 将证书添加到内核 keyring
sudo keyctl padd asymmetric "fsverity" %:.fs-verity < fsverity-cert.der

# 对文件签名
fsverity sign /mnt/important.txt /tmp/important.sig --key=fsverity-key.pem --cert=fsverity-cert.pem

# 启用带签名的 verity
fsverity enable --signature=/tmp/important.sig /mnt/important.txt

# 启用内核签名验证（sysctl）
echo 1 | sudo tee /proc/sys/fs/verity/require_signatures
```

### 在 btrfs 上使用

```bash
# btrfs 在内核 5.15+ 支持 fs-verity
sudo mkfs.btrfs /dev/sdX
sudo mount /dev/sdX /mnt

# 使用方式与 ext4 相同
fsverity enable /mnt/important.txt
fsverity measure /mnt/important.txt
```

---

## 40.6 安全启动链

完整的信任链从固件到用户空间：

```
┌────────────────────────────────────────────────────────┐
│                    安全启动链                            │
│                                                         │
│  ┌──────────┐                                           │
│  │ UEFI ROM │  固件中嵌入的平台密钥（PK）                 │
│  │ (不可变)  │  和密钥交换密钥（KEK）                     │
│  └────┬─────┘                                           │
│       │ 验证签名                                         │
│       ▼                                                  │
│  ┌──────────┐                                           │
│  │ shim.efi │  Microsoft 签名的 shim                     │
│  │          │  包含发行版的 MOK（Machine Owner Key）      │
│  └────┬─────┘                                           │
│       │ 验证签名                                         │
│       ▼                                                  │
│  ┌──────────┐                                           │
│  │ GRUB     │  发行版签名的 GRUB                         │
│  │          │  或 systemd-boot（直接 UEFI 签名）         │
│  └────┬─────┘                                           │
│       │ 验证签名                                         │
│       ▼                                                  │
│  ┌──────────┐                                           │
│  │ Linux    │  签名的内核                                │
│  │ Kernel   │  内嵌的 dm-verity root hash 密钥           │
│  └────┬─────┘                                           │
│       │ dm-verity                                        │
│       ▼                                                  │
│  ┌──────────┐                                           │
│  │ Root FS  │  dm-verity 保护的只读根文件系统             │
│  │          │  Merkle 树验证每个块                        │
│  └────┬─────┘                                           │
│       │ IMA/EVM                                          │
│       ▼                                                  │
│  ┌──────────┐                                           │
│  │ 用户空间  │  IMA 度量可执行文件                        │
│  │ 应用     │  EVM 保护文件属性                          │
│  │          │  fs-verity 保护关键文件                     │
│  └──────────┘                                           │
└────────────────────────────────────────────────────────┘
```

在 Arch Linux 上配置 Secure Boot：

```bash
# 安装所需工具
sudo pacman -S sbsigntools efitools

# 检查 Secure Boot 状态
sbctl status
# 或
mokutil --sb-state

# 使用 sbctl（Arch Linux 推荐工具）
sudo pacman -S sbctl

# 创建自定义密钥
sudo sbctl create-keys

# 注册密钥
sudo sbctl enroll-keys --microsoft   # 包含 Microsoft 密钥（用于双启动）

# 签名内核和引导加载程序
sudo sbctl sign -s /boot/vmlinuz-linux
sudo sbctl sign -s /boot/EFI/BOOT/BOOTX64.EFI
sudo sbctl sign -s /boot/EFI/systemd/systemd-bootx64.efi

# 验证签名
sudo sbctl verify

# 启用 Secure Boot（在 BIOS 中设置）
```

---

## 40.7 实战：构建完整性验证的只读根文件系统

本节将构建一个完整的、dm-verity 保护的只读根文件系统。

### 概述

```
┌──────────────────────────────────────────────┐
│               分区布局                        │
│                                               │
│  /dev/sda1  EFI System Partition  (512M)     │
│  /dev/sda2  Root (只读, dm-verity)  (4G)     │
│  /dev/sda3  Hash 分区               (128M)   │
│  /dev/sda4  数据分区 (可写, 用户数据) (剩余)  │
└──────────────────────────────────────────────┘
```

### 步骤 1：准备分区

```bash
# 使用 fdisk 或 gdisk 分区
sudo gdisk /dev/sda

# 分区方案
# 1: EFI  (ef00)  512M
# 2: Root (8304)  4G
# 3: Hash (8300)  128M
# 4: Data (8300)  剩余

# 格式化
sudo mkfs.fat -F32 /dev/sda1
sudo mkfs.ext4 /dev/sda2
sudo mkfs.ext4 /dev/sda4
```

### 步骤 2：安装最小系统

```bash
# 挂载 root
sudo mount /dev/sda2 /mnt
sudo mkdir -p /mnt/boot/efi

# 安装基础系统
sudo pacstrap /mnt base linux linux-firmware \
    systemd cryptsetup \
    nano less

# 配置 fstab（root 为只读挂载）
cat << 'EOF' | sudo tee /mnt/etc/fstab
/dev/mapper/verity-root  /     ext4  ro              0  1
/dev/sda1               /boot  vfat  defaults        0  2
/dev/sda4               /data  ext4  defaults        0  2
tmpfs                   /tmp   tmpfs defaults        0  0
tmpfs                   /var/log tmpfs defaults      0  0
EOF

# 配置只读根文件系统所需的 tmpfs 挂载
cat << 'EOF' | sudo tee -a /mnt/etc/fstab
tmpfs  /var/tmp      tmpfs  defaults  0  0
tmpfs  /run          tmpfs  defaults  0  0
EOF

# 基础系统配置
sudo arch-chroot /mnt bash -c "
    echo 'verity-host' > /etc/hostname
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
    echo 'en_US.UTF-8 UTF-8' >> /etc/locale.gen
    echo 'zh_CN.UTF-8 UTF-8' >> /etc/locale.gen
    locale-gen
    echo 'LANG=en_US.UTF-8' > /etc/locale.conf
    passwd   # 设置 root 密码
"

# 卸载
sudo umount /mnt
```

### 步骤 3：生成 dm-verity Hash

```bash
# 对根文件系统生成 verity hash
sudo veritysetup format \
    --data-block-size=4096 \
    --hash-block-size=4096 \
    --hash=sha256 \
    /dev/sda2 /dev/sda3

# 输出（保存这些信息！）：
# Root hash:      xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# Salt:           yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
# UUID:           zzzzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzzz

# 保存 root hash
ROOT_HASH="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 验证
sudo veritysetup verify /dev/sda2 /dev/sda3 $ROOT_HASH
echo "验证结果: $?"
```

### 步骤 4：配置引导加载程序

```bash
# 挂载 EFI 分区
sudo mount /dev/sda1 /mnt

# 安装 systemd-boot
sudo bootctl install --esp-path=/mnt

# 创建引导配置
cat << EOF | sudo tee /mnt/loader/entries/arch-verity.conf
title   Arch Linux (dm-verity)
linux   /vmlinuz-linux
initrd  /initramfs-linux.img
options root=/dev/mapper/verity-root ro \
    systemd.verity=1 \
    systemd.verity_root_data=/dev/sda2 \
    systemd.verity_root_hash=/dev/sda3 \
    systemd.verity_root_hash=${ROOT_HASH}
EOF

sudo umount /mnt
```

### 步骤 5：创建 initramfs Hook

```bash
# 挂载 root 分区进行修改
sudo veritysetup open /dev/sda2 verity-root /dev/sda3 $ROOT_HASH
sudo mount /dev/mapper/verity-root /mnt -o remount,rw   # 临时可写

# 创建 verity hook（如果不使用 systemd initrd）
sudo mkdir -p /mnt/etc/initcpio/hooks
sudo mkdir -p /mnt/etc/initcpio/install
```

```bash
# /mnt/etc/initcpio/install/verity
#!/bin/bash
build() {
    add_module dm-verity
    add_binary veritysetup
    add_runscript
}

help() {
    echo "dm-verity root filesystem verification"
}
```

```bash
# /mnt/etc/initcpio/hooks/verity
#!/bin/bash
run_hook() {
    modprobe dm-verity 2>/dev/null

    msg "Setting up dm-verity for root filesystem..."

    local root_hash
    root_hash=$(getarg systemd.verity_root_hash=)

    if [ -z "$root_hash" ]; then
        err "No root hash specified!"
        launch_interactive_shell
        return
    fi

    if ! veritysetup open /dev/sda2 verity-root /dev/sda3 "$root_hash" --restart-on-corruption; then
        err "dm-verity verification FAILED! System may be compromised."
        launch_interactive_shell
        return
    fi

    msg "dm-verity verification successful."
}
```

```bash
# 更新 mkinitcpio.conf
# 在 HOOKS 中添加 verity（在 block 之后，filesystems 之前）
# HOOKS=(base udev autodetect modconf block verity filesystems keyboard fsck)

# 重建 initramfs
sudo arch-chroot /mnt mkinitcpio -P

# 重新生成 verity hash（因为修改了文件系统内容）
sudo umount /mnt
sudo veritysetup close verity-root

sudo veritysetup format /dev/sda2 /dev/sda3
# 更新 ROOT_HASH 并重新配置引导项
```

### 步骤 6：测试与验证

```bash
# 重启系统，选择 "Arch Linux (dm-verity)" 启动

# 启动后验证
mount | grep verity
# /dev/mapper/verity-root on / type ext4 (ro)

# 检查 dm-verity 状态
sudo dmsetup status verity-root
# 0 8388608 verity V 1 ...

# 尝试写入（应该失败）
touch /test-write
# touch: cannot touch '/test-write': Read-only file system

# 验证完整性
# 如果从外部篡改 /dev/sda2 的内容，
# 对应的块读取会返回 I/O 错误
```

### 系统更新流程

```bash
# 由于根文件系统是只读的，更新流程：

# 1. 在另一台机器或 Live USB 中挂载
sudo mount /dev/sda2 /mnt -o rw

# 2. 使用 pacstrap 或 arch-chroot 更新
sudo arch-chroot /mnt pacman -Syu

# 3. 卸载
sudo umount /mnt

# 4. 重新生成 verity hash
sudo veritysetup format /dev/sda2 /dev/sda3
# 获取新的 ROOT_HASH

# 5. 更新引导配置中的 root hash
# 修改 /boot/loader/entries/arch-verity.conf

# 6. 重启
```

---

## 40.8 总结与最佳实践

| 场景 | 推荐方案 |
|------|----------|
| 只读系统分区 | dm-verity |
| 可写加密分区 | dm-crypt + dm-integrity |
| 单文件保护 | fs-verity |
| 运行时文件监控 | IMA 度量 |
| 强制文件签名 | IMA 评估 + EVM |
| 完整信任链 | Secure Boot → dm-verity → IMA |
| 嵌入式/IoT | dm-verity + A/B 分区 |
| 容器镜像 | fs-verity（镜像层验证） |

```bash
# 检查内核支持的完整性功能
zgrep -E "DM_VERITY|DM_INTEGRITY|FS_VERITY|IMA|EVM" /proc/config.gz

# 示例输出（Arch 默认内核）：
# CONFIG_DM_VERITY=m
# CONFIG_DM_VERITY_VERIFY_ROOTHASH_SIG=y
# CONFIG_DM_VERITY_FEC=y
# CONFIG_DM_INTEGRITY=m
# CONFIG_FS_VERITY=y
# CONFIG_FS_VERITY_BUILTIN_SIGNATURES=y
# CONFIG_IMA=y
# CONFIG_IMA_MEASURE_PCR_IDX=10
# CONFIG_EVM=y
```

---

## 40.9 参考资源

| 资源 | 链接 |
|------|------|
| dm-verity 内核文档 | https://docs.kernel.org/admin-guide/device-mapper/verity.html |
| dm-integrity 内核文档 | https://docs.kernel.org/admin-guide/device-mapper/dm-integrity.html |
| fs-verity 内核文档 | https://docs.kernel.org/filesystems/fsverity.html |
| IMA 文档 | https://sourceforge.net/p/linux-ima/wiki/Home/ |
| cryptsetup 手册 | https://gitlab.com/cryptsetup/cryptsetup/-/wikis/home |
| Android Verified Boot | https://source.android.com/docs/security/features/verifiedboot |
| Arch Wiki - Secure Boot | https://wiki.archlinux.org/title/Unified_Extensible_Firmware_Interface/Secure_Boot |
| Arch Wiki - dm-crypt | https://wiki.archlinux.org/title/Dm-crypt |

---

## 40.10 本章测验

> [!example] 📝 自测题目

> [!question]- 选择题 1：dm-verity 使用什么算法结构来验证块设备完整性？
> - A. 线性哈希链
> - B. Merkle 树（哈希树），从数据块逐层向上计算到根哈希
> - C. 循环冗余校验（CRC）
> - D. 奇偶校验位
>
> > [!success]- 点击查看答案
> > **B**
> > dm-verity 将块设备分成固定大小的块，计算每个块的哈希值，再逐层合并为树结构，最终得到唯一的根哈希（root hash）。读取数据时沿树验证到根哈希，任何篡改都会被检测到。

> [!question]- 选择题 2：dm-verity 保护的块设备必须是什么属性？
> - A. 可读写
> - B. 只读
> - C. 加密的
> - D. 网络存储
>
> > [!success]- 点击查看答案
> > **B**
> > dm-verity 只能保护只读块设备。因为哈希树在创建时计算，任何写入都会改变数据导致哈希不匹配。可写分区的完整性保护需要使用 dm-integrity。

> [!question]- 判断题 3：fs-verity 提供文件级别的透明完整性验证，应用程序读取文件时内核自动验证，无需应用修改代码。
> - A. ✓ 正确
> - B. ✗ 错误
>
> > [!success]- 点击查看答案
> > **A. ✓ 正确**
> > fs-verity 在文件级别建立 Merkle 树，对应用程序完全透明。读取文件时内核自动验证数据块完整性，如果检测到篡改返回 I/O 错误。

> [!question]- 选择题 4：IMA（Integrity Measurement Architecture）的"度量"模式会做什么？
> - A. 阻止被篡改的文件执行
> - B. 计算文件哈希并记录到度量列表（通常扩展到 TPM PCR）
> - C. 加密文件内容
> - D. 删除不完整的文件
>
> > [!success]- 点击查看答案
> > **B**
> > IMA 度量模式在文件被访问时计算其哈希值，记录到内核维护的度量列表中，并可扩展到 TPM 的 PCR（平台配置寄存器），用于远程证明系统的完整性状态。

> [!question]- 选择题 5：完整的 Linux 信任链从启动到运行时的正确顺序是什么？
> - A. IMA → dm-verity → Secure Boot → fs-verity
> - B. Secure Boot → 签名内核 → dm-verity → IMA/EVM
> - C. dm-verity → Secure Boot → IMA → fs-verity
> - D. fs-verity → dm-verity → Secure Boot → IMA
>
> > [!success]- 点击查看答案
> > **B**
> > 正确的信任链是：UEFI Secure Boot 验证引导程序 → 签名的内核/initramfs 加载 → dm-verity 验证只读根文件系统 → IMA/EVM 在运行时度量和保护文件完整性。

> [!question]- 判断题 6：dm-integrity 与 dm-verity 不同，它可以保护可写分区的数据完整性。
> - A. ✓ 正确
> - B. ✗ 错误
>
> > [!success]- 点击查看答案
> > **A. ✓ 正确**
> > dm-integrity 为每个数据块存储完整性标签（如 HMAC 或 CRC），支持可写操作——写入时同时更新标签，读取时验证标签。常与 dm-crypt 结合实现认证加密。

> [!question]- 选择题 7：将 dm-verity 的 root hash 嵌入 UKI（统一内核镜像）的安全意义是什么？
> - A. 提高启动速度
> - B. 通过 Secure Boot 签名保护 root hash 不被篡改，形成完整信任链
> - C. 减少磁盘空间
> - D. 简化配置管理
>
> > [!success]- 点击查看答案
> > **B**
> > 将 root hash 嵌入已签名的 UKI 中，Secure Boot 保证 UKI 不被篡改，因此内嵌的 root hash 也是可信的，进而保证 dm-verity 验证的根文件系统可信，形成从固件到文件系统的完整信任链。

> [!question]- 选择题 8：EVM（Extended Verification Module）保护的是什么？
> - A. 文件内容
> - B. 文件的扩展属性（xattr）和元数据完整性
> - C. 网络数据包
> - D. 内核模块
>
> > [!success]- 点击查看答案
> > **B**
> > EVM 保护文件的扩展属性（如安全标签、IMA 哈希值）和元数据不被篡改。它在 xattr 之上计算 HMAC 或数字签名，确保 IMA 度量值等安全属性的完整性。

> [!question]- 判断题 9：当 dm-verity 检测到数据块被篡改时，读取操作会返回 I/O 错误而非损坏的数据。
> - A. ✓ 正确
> - B. ✗ 错误
>
> > [!success]- 点击查看答案
> > **A. ✓ 正确**
> > dm-verity 在读取数据块时计算哈希并与 Merkle 树中的值比对，如果不匹配则返回 I/O 错误（EIO），确保应用程序永远不会读到被篡改的数据。

> [!question]- 选择题 10：以下哪种场景最适合使用 fs-verity 而非 dm-verity？
> - A. 保护整个只读根文件系统
> - B. 保护可写文件系统上的个别重要文件（如容器镜像层）
> - C. 保护交换分区
> - D. 保护 UEFI 固件
>
> > [!success]- 点击查看答案
> > **B**
> > fs-verity 适合在可写文件系统上对特定文件启用只读完整性保护，如验证容器镜像层文件、APK 包等。dm-verity 则适合保护整个只读块设备/分区。
