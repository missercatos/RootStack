# 23 - systemd-homed 用户管理

> 传统 Linux 用户管理依赖 `/etc/passwd`、`/etc/shadow` 等全局文件，home 目录与用户身份
> 紧密绑定在本机。systemd-homed 提出了一种全新理念：将用户的身份信息和数据封装在 home 目录中，
> 使之可以加密、可以迁移、可以在不同机器间漫游。本章将从传统用户管理讲起，深入 systemd-homed
> 的架构、配置与实战。

---

## 23.1 传统 Linux 用户管理

### 核心文件

| 文件 | 用途 | 示例内容 |
|------|------|---------|
| `/etc/passwd` | 用户账户信息 | `alice:x:1000:1000:Alice:/home/alice:/bin/bash` |
| `/etc/shadow` | 加密密码存储 | `alice:$6$xxx...:19000:0:99999:7:::` |
| `/etc/group` | 组信息 | `wheel:x:10:alice` |
| `/etc/gshadow` | 组密码 | `wheel:!::alice` |

### /etc/passwd 字段解析

```
用户名:密码占位:UID:GID:注释:Home目录:登录Shell
alice:x:1000:1000:Alice Wang:/home/alice:/bin/bash
```

### 传统用户管理命令

```bash
# 创建用户
useradd -m -G wheel -s /bin/bash alice

# 设置密码
passwd alice

# 修改用户属性
usermod -aG docker alice # 添加到 docker 组
usermod -s /bin/zsh alice # 更改 shell
usermod -l bob alice # 改名

# 删除用户
userdel -r alice # -r 同时删除 home 目录

# 查看用户信息
id alice
getent passwd alice
finger alice

# 组管理
groupadd developers
groupdel developers
gpasswd -a alice developers # 添加用户到组
gpasswd -d alice developers # 从组中移除
```

### 传统方案的局限性

- 用户信息分散在多个系统文件中
- UID/GID 在不同机器间可能冲突
- Home 目录无法方便地在机器间迁移
- 加密 home 目录需要额外配置（ecryptfs、dm-crypt）
- 用户元数据与 home 目录分离
- 用户离线时无法验证身份

---

## 23.2 systemd-homed 是什么

systemd-homed 是 systemd 246 引入的用户管理服务，核心理念是**将用户信息自包含在 home 目录中**。

### 设计目标

1. **可移植性**：用户的 home 目录可以放在 USB 设备上，插入即可登录
2. **安全性**：原生支持 LUKS2 加密，用户登出后自动锁定
3. **自包含**：用户身份信息（JSON 记录）存储在 home 目录内
4. **现代化**：支持 FIDO2 硬件令牌、PKCS#11 智能卡等认证方式

### 核心组件

| 组件 | 功能 |
|------|------|
| `systemd-homed.service` | 管理 home 目录的系统服务 |
| `homectl` | 命令行管理工具 |
| `pam_systemd_home.so` | PAM 模块，处理登录认证 |
| `nss-systemd` | NSS 模块，提供用户查询 |
| `~/.identity` | JSON 用户记录文件 |

---

## 23.3 systemd-homed vs 传统用户管理对比

| 特性 | 传统方案 | systemd-homed |
|------|---------|--------------|
| 用户信息存储 | `/etc/passwd` + `/etc/shadow` | JSON 记录（`~/.identity`） |
| 密码哈希存储 | `/etc/shadow`（需 root 读取） | home 目录内（自包含） |
| 加密 | 需额外配置 | LUKS2 原生支持 |
| 可移植性 | 不可移植 | USB 便携用户 |
| 登出后安全性 | home 目录保持可读 | 自动解锁/锁定 |
| UID 管理 | 固定绑定本机 | 动态 UID 映射 |
| 磁盘配额 | 需要文件系统配额支持 | LUKS 镜像大小限制 |
| 认证方式 | 密码 | 密码、FIDO2、PKCS#11 |
| 离线认证 | 不支持 | 支持（密钥缓存） |
| 网络用户 | 需要 LDAP/NIS | 原生 JSON 记录 |
| 兼容性 | 所有程序支持 | 部分程序可能不兼容 |

---

## 23.4 架构设计

### 工作流程

```
用户登录
 │
 ▼
PAM (pam_systemd_home.so)
 │
 ▼
systemd-homed.service
 │
 ├── 验证密码/FIDO2
 ├── 挂载 LUKS 镜像（或激活 fscrypt/subvolume）
 ├── 分配动态 UID（如需要）
 └── 激活 home 目录
 │
 ▼
用户会话开始
 ...
用户登出
 │
 ▼
systemd-homed.service
 │
 ├── 卸载 LUKS 镜像
 └── 锁定 home 目录
```

### 存储后端

| 后端 | 说明 | 文件 |
|------|------|------|
| `luks` | LUKS2 加密磁盘镜像（**推荐**） | `~/.homedir.img` |
| `fscrypt` | 文件系统级加密（ext4/f2fs） | 普通目录 + fscrypt 加密 |
| `directory` | 普通目录（无加密） | 普通目录 |
| `subvolume` | Btrfs 子卷（无加密） | Btrfs 子卷 |
| `cifs` | CIFS/SMB 网络共享 | 网络挂载 |

---

## 23.5 安装与启用

### 安装

systemd-homed 包含在 `systemd` 包中，Arch 默认已安装。

```bash
# 启用服务
systemctl enable --now systemd-homed.service
```

### 配置 PAM

需要修改 PAM 配置以支持 systemd-homed 认证。安装 `pam` 包后，确保以下内容存在：

编辑 `/etc/pam.d/system-auth`：

```
#%PAM-1.0

auth sufficient pam_systemd_home.so
auth required pam_unix.so try_first_pass nullok
auth optional pam_permit.so
auth required pam_env.so

account sufficient pam_systemd_home.so
account required pam_unix.so
account optional pam_permit.so
account required pam_time.so

password sufficient pam_systemd_home.so
password required pam_unix.so try_first_pass nullok sha512 shadow
password optional pam_permit.so

session required pam_limits.so
session optional pam_systemd_home.so
session required pam_unix.so
session optional pam_permit.so
```

> 关键：`pam_systemd_home.so` 必须在 `pam_unix.so` **之前**，且使用 `sufficient`。

---

## 23.6 创建用户（homectl create）

### 基本创建

```bash
# 创建使用 LUKS 后端的用户（推荐）
homectl create alice --storage=luks

# 创建时指定更多选项
homectl create alice \
 --storage=luks \
 --image-path=/home/alice.home \
 --fs-type=btrfs \
 --disk-size=50G \
 --shell=/bin/bash \
 --real-name="Alice Wang" \
 --member-of=wheel \
 --language=zh_CN.UTF-8 \
 --timezone=Asia/Shanghai
```

### 各种存储后端

#### LUKS 后端（推荐）

```bash
homectl create alice --storage=luks --disk-size=50G --fs-type=ext4

# LUKS 镜像存储在 /home/alice.home
# 登录时自动挂载到 /home/alice
# 登出后自动卸载并锁定
```

LUKS 后端支持的文件系统：

| 文件系统 | 选项 |
|---------|------|
| ext4 | `--fs-type=ext4`（默认） |
| btrfs | `--fs-type=btrfs` |
| xfs | `--fs-type=xfs` |

#### fscrypt 后端

```bash
homectl create alice --storage=fscrypt
```

> 需要文件系统支持 fscrypt（ext4、f2fs）。不创建磁盘镜像，而是使用文件系统级加密。

#### 普通目录后端

```bash
homectl create alice --storage=directory
```

> 无加密，仅将用户记录嵌入 home 目录。适合测试或不需要加密的场景。

#### Btrfs 子卷后端

```bash
homectl create alice --storage=subvolume
```

> 要求 `/home` 在 Btrfs 文件系统上。使用 Btrfs 子卷特性，支持快照和配额。

### 选项详解

```bash
homectl create alice \
 --storage=luks \
 --disk-size=50G \
 --disk-size-relative=50% \
 --fs-type=btrfs \
 --luks-discard=true \
 --shell=/bin/zsh \
 --real-name="Alice Wang" \
 --email-address=alice@example.com \
 --location="Beijing, China" \
 --icon-name=user-female \
 --language=zh_CN.UTF-8 \
 --timezone=Asia/Shanghai \
 --member-of=wheel,docker \
 --skeleton=/etc/skel \
 --uid=60000 \
 --setenv=EDITOR=nvim \
 --setenv=PAGER=less \
 --nice=5 \
 --memory-high=8G \
 --memory-max=12G \
 --cpu-weight=100 \
 --io-weight=100 \
 --tasks-max=4096 \
 --enforce-password-policy=true \
 --password-change-min-usec=86400000000 \
 --password-change-max-usec=7776000000000 \
 --password-change-warn-usec=1209600000000 \
 --not-before="2024-01-01T00:00:00Z" \
 --not-after="2025-12-31T23:59:59Z"
```

### 使用 FIDO2 认证

```bash
# 创建使用 FIDO2 密钥的用户
homectl create alice --storage=luks --fido2-device=auto

# 为已有用户添加 FIDO2
homectl update alice --fido2-device=auto
```

### 使用 PKCS#11 智能卡

```bash
homectl create alice --storage=luks --pkcs11-token-uri=auto
```

---

## 23.7 用户管理操作

### 查看用户信息

```bash
# 列出所有 homed 管理的用户
homectl list

# 查看详细信息
homectl inspect alice

# JSON 格式输出
homectl inspect alice --json=pretty
```

### 修改密码

```bash
homectl passwd alice
```

### 修改用户属性

```bash
# 修改 shell
homectl update alice --shell=/bin/zsh

# 修改磁盘配额
homectl update alice --disk-size=100G

# 添加到新组
homectl update alice --member-of=wheel,docker,libvirt

# 修改资源限制
homectl update alice --memory-high=16G --tasks-max=8192

# 设置环境变量
homectl update alice --setenv=EDITOR=vim --setenv=LANG=zh_CN.UTF-8

# 设置账户过期时间
homectl update alice --not-after="2025-06-30T23:59:59Z"

# 修改真实姓名
homectl update alice --real-name="Alice Zhang"
```

### 锁定与解锁

```bash
# 锁定用户（卸载加密 home 目录）
homectl lock alice

# 解锁用户（重新挂载）
homectl unlock alice
```

> 当用户登出所有会话时，LUKS 后端会自动锁定。

### 调整 LUKS 镜像大小

```bash
# 增大
homectl resize alice 100G

# 缩小（需要先锁定/登出）
homectl resize alice 30G
```

### 删除用户

```bash
homectl remove alice
```

> 这会同时删除用户记录和 home 目录（LUKS 镜像）。操作不可逆。

### 激活与停用

```bash
# 手动激活（不创建登录会话）
homectl activate alice

# 手动停用
homectl deactivate alice
```

### 导出与导入

```bash
# 导出用户记录（不包含 home 数据）
homectl inspect alice --json=pretty > alice-record.json
```

---

## 23.8 JSON 用户记录

systemd-homed 的核心创新是将用户信息存储为 JSON 记录。该记录保存在：

- `~/.identity`（home 目录内）
- `/var/lib/systemd/home/`（系统缓存）

### 记录结构

```json
{
 "userName": "alice",
 "realName": "Alice Wang",
 "disposition": "regular",
 "storage": "luks",
 "fileSystemType": "btrfs",
 "diskSize": 53687091200,
 "uid": 60000,
 "gid": 60000,
 "memberOf": ["wheel", "docker"],
 "shell": "/bin/bash",
 "environment": [
 "EDITOR=nvim",
 "LANG=zh_CN.UTF-8"
 ],
 "timeZone": "Asia/Shanghai",
 "preferredLanguage": "zh_CN.UTF-8",
 "emailAddress": "alice@example.com",
 "location": "Beijing, China",
 "iconName": "user-female",
 "niceLevel": 5,
 "memoryHigh": 8589934592,
 "memoryMax": 12884901888,
 "tasksMax": 4096,
 "cpuWeight": 100,
 "ioWeight": 100,
 "enforcePasswordPolicy": true,
 "lastChangeUSec": 1700000000000000,
 "lastPasswordChangeUSec": 1700000000000000,
 "passwordChangeMinUSec": 86400000000,
 "passwordChangeMaxUSec": 7776000000000,
 "passwordChangeWarnUSec": 1209600000000,
 "notBeforeUSec": 1704067200000000,
 "notAfterUSec": 1767225599000000,
 "privileged": {
 "hashedPassword": [
 "$6$rounds=656000$xxx..."
 ]
 },
 "binding": {
 "<machine-id>": {
 "imagePath": "/home/alice.home",
 "homeDirectory": "/home/alice",
 "uid": 60000,
 "gid": 60000,
 "fileSystemUuid": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
 "luksUuid": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
 "partitionUuid": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
 }
 },
 "status": {
 "<machine-id>": {
 "diskUsage": 2147483648,
 "diskFree": 51539607552,
 "diskSize": 53687091200,
 "diskFloor": 10737418240,
 "diskCeiling": 107374182400,
 "signedLocally": true
 }
 },
 "signature": [
 {
 "data": "base64..."
 }
 ]
}
```

### 关键字段说明

| 字段 | 含义 |
|------|------|
| `disposition` | 用户类型：`regular`、`system`、`machine`、`container` |
| `storage` | 存储后端：`luks`、`fscrypt`、`directory`、`subvolume`、`cifs` |
| `binding` | 机器绑定信息（每台机器可不同） |
| `privileged` | 特权信息（密码哈希等，仅 root 可读） |
| `signature` | 数字签名，防止记录被篡改 |
| `status` | 当前状态信息（运行时生成） |

---

## 23.9 可移植 home 目录

systemd-homed 的杀手级功能之一：将用户放在 USB 设备上。

### 创建 USB 便携用户

```bash
# 将 LUKS 镜像放在 USB 设备上
homectl create portable-alice \
 --storage=luks \
 --image-path=/run/media/root/USB_DRIVE/portable-alice.home \
 --disk-size=20G \
 --fs-type=ext4
```

### 使用流程

1. 将 USB 设备插入目标机器
2. 目标机器需要运行 `systemd-homed.service`
3. homed 自动检测 LUKS 镜像并注册用户
4. 用户可以正常登录
5. 登出后拔出 USB 设备，用户自动清理

### 在另一台机器上使用

目标机器无需事先创建用户。homed 会：

1. 扫描可移动设备上的 `.home` 镜像
2. 读取内嵌的 JSON 用户记录
3. 动态分配 UID（可能与源机器不同）
4. 挂载 home 目录

> 注意：LUKS 镜像内的文件 UID 会通过 `uidmap` 自动重映射。

---

## 23.10 PAM 集成

### PAM 认证流程

当用户登录时，PAM 调用链如下：

```
login/sshd/gdm
 │
 ▼
pam_systemd_home.so (sufficient)
 │
 ├── 成功 → 跳过 pam_unix.so
 └── 失败 → 继续
 │
 ▼
pam_unix.so
```

### 各登录方式的 PAM 配置

#### GDM（GNOME 登录管理器）

GDM 通常引用 `system-auth`，无需额外配置。

#### SDDM

确保 `/etc/pam.d/sddm` 引用 `system-auth`：

```
auth include system-auth
account include system-auth
password include system-auth
session include system-auth
```

#### TTY 登录

`/etc/pam.d/login` 通常已正确配置。

#### su / sudo

```
# /etc/pam.d/su
auth sufficient pam_systemd_home.so
auth required pam_unix.so
...

# /etc/pam.d/sudo
auth sufficient pam_systemd_home.so
auth required pam_unix.so
...
```

---

## 23.11 SSH 集成

### 问题

SSH 登录时，用户的 home 目录可能尚未挂载（锁定状态），导致无法读取 `~/.ssh/authorized_keys`。

### 解决方案

使用密码认证触发 homed 解锁：

```bash
# /etc/ssh/sshd_config
PasswordAuthentication yes
```

或者使用 `AuthorizedKeysCommand` 从 JSON 记录中提取公钥：

```bash
# /etc/ssh/sshd_config
AuthorizedKeysCommand /usr/bin/userdbctl ssh-authorized-keys %u
AuthorizedKeysCommandUser root
```

将 SSH 公钥添加到用户记录：

```bash
homectl update alice --ssh-authorized-keys=@/path/to/alice.pub
```

查看已配置的公钥：

```bash
homectl inspect alice --json=pretty | jq '.sshAuthorizedKeys'
userdbctl ssh-authorized-keys alice
```

---

## 23.12 限制与注意事项

### 已知限制

| 限制 | 说明 |
|------|------|
| 系统服务 | 不适合运行系统服务的用户（如 `http`、`mysql`） |
| 早期启动 | 开机时 home 目录未挂载，自动登录可能有问题 |
| cron/systemd timer | 用户未登录时 home 不可用，定时任务可能失败 |
| NFS | 不支持通过 NFS 导出 homed 管理的目录 |
| Docker 卷 | LUKS 后端的 home 目录中不能使用 overlay2 |
| UID 固定 | 动态 UID 可能导致某些硬编码 UID 的程序出问题 |
| 根分区加密 | 如果已使用全盘加密，LUKS 后端的加密是双重的 |

### 不适合使用 homed 的场景

- 系统服务账户（应使用 `systemd-sysusers`）
- 需要在用户未登录时访问其 home 目录的场景
- NFS 环境
- 对 UID 稳定性有严格要求的环境

### 兼容性注意

```bash
# 某些程序可能不认识 homed 用户，可通过 nss-systemd 解决
# 确保 /etc/nsswitch.conf 包含 systemd：
passwd: files systemd
group: files [SUCCESS=merge] systemd
shadow: files systemd
```

---

## 23.13 与 Btrfs 子卷结合使用

### Btrfs 子卷后端

如果 `/home` 在 Btrfs 上，可以使用 `subvolume` 后端：

```bash
homectl create alice --storage=subvolume
```

这会创建一个 Btrfs 子卷作为 home 目录，好处包括：

- Btrfs 原生配额支持
- 可以创建快照
- 透明压缩
- CoW（写时复制）

### 子卷快照

```bash
# 手动创建快照（需要 root）
btrfs subvolume snapshot /home/alice /home/.snapshots/alice-$(date +%Y%m%d)

# 列出快照
btrfs subvolume list /home

# 恢复快照
btrfs subvolume delete /home/alice
btrfs subvolume snapshot /home/.snapshots/alice-20240101 /home/alice
```

### 配额管理

```bash
# 启用配额
btrfs quota enable /home

# 设置配额（通过 homectl）
homectl update alice --disk-size=50G
```

### LUKS on Btrfs

也可以在 Btrfs 上使用 LUKS 后端：

```bash
homectl create alice --storage=luks --fs-type=btrfs --disk-size=50G
```

这种方式在 Btrfs 上创建 LUKS 加密镜像，镜像内部使用 Btrfs 文件系统。

---

## 23.14 实战：完整配置 systemd-homed

### 步骤一：启用服务

```bash
systemctl enable --now systemd-homed.service
```

### 步骤二：配置 PAM

确认 `/etc/pam.d/system-auth` 包含 `pam_systemd_home.so`（参见 23.5 节）。

### 步骤三：配置 NSS

编辑 `/etc/nsswitch.conf`：

```
passwd: files systemd
group: files [SUCCESS=merge] systemd
shadow: files systemd
gshadow: files systemd
```

### 步骤四：创建用户

```bash
homectl create alice \
 --storage=luks \
 --disk-size=50G \
 --fs-type=ext4 \
 --shell=/bin/bash \
 --real-name="Alice Wang" \
 --member-of=wheel \
 --timezone=Asia/Shanghai \
 --language=zh_CN.UTF-8
```

系统会提示设置密码。

### 步骤五：验证

```bash
# 检查用户
homectl inspect alice

# 测试登录
su - alice

# 确认 home 目录已挂载
mount | grep alice
df -h /home/alice

# 检查身份文件
cat /home/alice/.identity | python -m json.tool
```

### 步骤六：配置 SSH

```bash
# 添加 SSH 公钥
homectl update alice --ssh-authorized-keys=@/home/alice/.ssh/id_ed25519.pub

# 修改 sshd 配置
# /etc/ssh/sshd_config
AuthorizedKeysCommand /usr/bin/userdbctl ssh-authorized-keys %u
AuthorizedKeysCommandUser root
```

```bash
systemctl restart sshd
```

### 步骤七：配置 sudo

确保 `/etc/pam.d/sudo` 正确配置：

```
#%PAM-1.0
auth sufficient pam_systemd_home.so
auth required pam_unix.so try_first_pass
auth required pam_nologin.so
account sufficient pam_systemd_home.so
account required pam_unix.so
session required pam_limits.so
session required pam_unix.so
```

使用 `visudo` 添加 wheel 组权限：

```bash
EDITOR=nvim visudo
# 取消注释：
# %wheel ALL=(ALL:ALL) ALL
```

### 步骤八：设置资源限制

```bash
homectl update alice \
 --memory-high=8G \
 --memory-max=12G \
 --cpu-weight=100 \
 --io-weight=100 \
 --tasks-max=4096 \
 --nice=0
```

### 步骤九：自动锁定配置

LUKS 后端在用户登出所有会话后自动锁定。如需手动控制：

```bash
# 手动锁定
homectl lock alice

# 手动解锁
homectl unlock alice

# 查看当前状态
homectl inspect alice | grep -i state
```

### 步骤十：备份

```bash
# 备份 LUKS 镜像（用户需先登出）
homectl deactivate alice
cp /home/alice.home /backup/alice.home.bak

# 备份用户记录
homectl inspect alice --json=pretty > /backup/alice-record.json
```

---

## 23.15 常用 homectl 命令速查

| 命令 | 功能 |
|------|------|
| `homectl list` | 列出所有 homed 用户 |
| `homectl create <user>` | 创建用户 |
| `homectl remove <user>` | 删除用户 |
| `homectl update <user>` | 修改用户属性 |
| `homectl passwd <user>` | 修改密码 |
| `homectl inspect <user>` | 查看用户详情 |
| `homectl activate <user>` | 激活（挂载）home |
| `homectl deactivate <user>` | 停用（卸载）home |
| `homectl lock <user>` | 锁定（加密锁定） |
| `homectl unlock <user>` | 解锁 |
| `homectl resize <user> <size>` | 调整磁盘大小 |
| `homectl with <user> -- <cmd>` | 临时激活并执行命令 |

### homectl with 用法

```bash
# 临时激活 home 目录，运行命令后自动停用
homectl with alice -- ls -la /home/alice
homectl with alice -- du -sh /home/alice
```

---

## 23.16 故障排查

### 查看日志

```bash
journalctl -u systemd-homed.service -b
journalctl -u systemd-homed.service -f # 实时跟踪
```

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 登录时提示"密码错误" | PAM 配置不正确 | 检查 `/etc/pam.d/system-auth` |
| Home 目录未自动挂载 | homed 服务未运行 | `systemctl start systemd-homed` |
| 登出后 home 未锁定 | 存在残留会话 | `loginctl list-sessions` 检查 |
| 磁盘空间不足 | LUKS 镜像太小 | `homectl resize alice 100G` |
| USB 用户未被识别 | 镜像文件不在扫描路径 | 确保使用 `.home` 后缀 |
| UID 冲突 | 动态 UID 与现有用户冲突 | 指定 `--uid=` 避免冲突 |
| SSH 登录失败 | 公钥未配置到 homed | 使用 `AuthorizedKeysCommand` |

### LUKS 镜像修复

```bash
# 检查 LUKS 镜像完整性
cryptsetup luksDump /home/alice.home

# 文件系统检查
homectl deactivate alice
losetup /dev/loop0 /home/alice.home
cryptsetup open /dev/loop0 alice-repair
fsck /dev/mapper/alice-repair
cryptsetup close alice-repair
losetup -d /dev/loop0
```

---

