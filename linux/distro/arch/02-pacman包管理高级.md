# Arch Linux pacman 包管理高级参考

> pacman 是 Arch Linux 的核心包管理器。本章是完整的 pacman 深度参考，覆盖镜像管理、hooks、降级、缓存管理和故障排除。

---

## 1. pacman 完整命令参考

### 1.1 基本操作

| 操作 | 命令 | 说明 |
|------|------|------|
| 安装包 | `pacman -S pkgname` | 安装单个包 |
| 安装多个 | `pacman -S pkg1 pkg2 pkg3` | 一次安装多个 |
| 安装本地包 | `pacman -U /path/to/pkg.tar.zst` | 安装 .pkg.tar.zst 文件 |
| 全系统升级 | `pacman -Syu` | 同步数据库 + 升级 |
| 仅同步数据库 | `pacman -Sy` | 只刷新数据库（不升级） |
| 搜索包 | `pacman -Ss keyword` | 在数据库搜索 |
| 搜索已安装 | `pacman -Qs keyword` | 搜索已安装的包 |
| 包信息 | `pacman -Si pkgname` | 远程包详细信息 |
| 已安装包信息 | `pacman -Qi pkgname` | 本地已安装包的详细信息 |
| 列出包文件 | `pacman -Fl pkgname` | 远程包包含哪些文件 |
| 查看包的所有者 | `pacman -Qo /path/to/file` | 文件属于哪个包 |
| 按文件搜索包 | `pacman -F /path/to/file` | 哪些远程包包含此文件 |
| 删除包 | `pacman -R pkgname` | 只删除包，保留依赖 |
| 删除包+依赖 | `pacman -Rs pkgname` | 删除包及其未使用的依赖 |
| 删除包+配置 | `pacman -Rn pkgname` | 删除包和其配置文件 |
| 级联删除 | `pacman -Rsc pkgname` | 删除包及其依赖（小心） |
| 清理缓存 | `pacman -Sc` | 清理未安装的包缓存 |
| 清理全部缓存 | `pacman -Scc` | 清理所有包缓存（小心） |

### 1.2 查询操作详解

```bash
# 列出所有显式安装的包（用户主动安装的）
pacman -Qe

# 列出所有作为依赖安装的包
pacman -Qd

# 列出孤立的包（没有其他包依赖）
pacman -Qdt

# 列出来自非官方仓库的包（AUR 包等）
pacman -Qm

# 列出系统自带的基础包
pacman -Qg base

# 查看包的依赖树
pactree pkgname

# 查看哪些包依赖此包（反向依赖）
pactree -r pkgname

# 查询包中某个文件的完整路径
pacman -Ql pkgname

# 统计各包占用空间排序（前20）
pacman -Qi | awk '/^Name/{name=$3} /^Installed Size/{size=$4; unit=$5; \
 if(unit=="KiB"){s=size/1024} else if(unit=="MiB"){s=size} \
 else if(unit=="GiB"){s=size*1024} else{s=0}; \
 printf "%.2f MiB\t%s\n", s, name}' | sort -rh | head -20

# 列出所有未被任何包需要的可选依赖
pacman -Qdtq | pacman -Qi - | grep "Optional Deps"
```

### 1.3 pacman 配置文件

```ini
# /etc/pacman.conf
[options]
# 架构
Architecture = auto

# 检查可用空间
CheckSpace

# 彩色输出
Color

# 并行下载数（>1 启用并行下载）
ParallelDownloads = 5

# 完整输出
VerbosePkgLists

# 忽略升级特定包（极不建议日常使用）
# IgnorePkg = linux
# IgnoreGroup = gnome

# 不升级（危险）
# NoUpgrade =

# 不过时刷新数据库
# NoExtract =

# 保留配置而不是替换为 .pacnew
# NoUpgrade = etc/X11/xorg.conf

# 使用 Syslog
# UseSyslog

# 签名级别
SigLevel = Required DatabaseOptional
LocalFileSigLevel = Optional

# 测试仓库（取消注释以启用）
#[core-testing]
#Include = /etc/pacman.d/mirrorlist

#[extra-testing]
#Include = /etc/pacman.d/mirrorlist

# 社区测试仓库
#[community-testing]
#Include = /etc/pacman.d/mirrorlist

# multilib (32位支持)
[multilib]
Include = /etc/pacman.d/mirrorlist
```

### 1.4 pacman 事务标志

| 标志 | 作用 |
|------|------|
| `--needed` | 不重新安装已存在的包 |
| `--noconfirm` | 跳过所有确认提示 |
| `--asdeps` | 将包标记为依赖安装 |
| `--asexplicit` | 将包标记为显式安装 |
| `--overwrite` | 覆盖文件冲突 |
| `--dbonly` | 只更新数据库，不处理文件 |

---

## 2. 镜像管理 —— reflector

### 2.1 安装与使用

```bash
sudo pacman -S reflector

# 手动刷新镜像列表（按速度排序中国镜像）
sudo reflector --country China \
 --age 12 \
 --protocol https \
 --sort rate \
 --save /etc/pacman.d/mirrorlist

# 添加多个国家/地区
sudo reflector --country China,Japan,Singapore,Korea \
 --age 12 \
 --protocol https \
 --sort rate \
 --latest 20 \
 --save /etc/pacman.d/mirrorlist
```

### 2.2 reflector 常用参数

| 参数 | 说明 |
|------|------|
| `--country` | 指定国家（, 分隔多个） |
| `--age N` | 最后同步不超过 N 小时 |
| `--latest N` | 取最近同步的 N 个镜像 |
| `--sort` | 排序方式：rate(速度)、score(评分)、country、name |
| `--protocol` | 协议：http、https、ftp |
| `--fastest N` | 只取前 N 个最快的 |
| `--completion-percent N` | 完成度最低百分比 |
| `--save` | 保存到文件 |
| `--verbose` | 详细输出速度测试结果 |

### 2.3 定时自动刷新

```bash
# 启用 reflector 定时器
sudo systemctl enable --now reflector.timer

# 查看定时器状态
systemctl status reflector.timer

# 定时器默认每周运行一次
# 编辑 /etc/xdg/reflector/reflector.conf 自定义参数
```

```bash
# /etc/xdg/reflector/reflector.conf
--country China,Japan,Singapore
--age 12
--protocol https
--sort rate
--latest 10
--save /etc/pacman.d/mirrorlist
```

### 2.4 推荐的中国镜像

```bash
# 手动编辑 /etc/pacman.d/mirrorlist
Server = https://mirrors.tuna.tsinghua.edu.cn/archlinux/$repo/os/$arch
Server = https://mirrors.ustc.edu.cn/archlinux/$repo/os/$arch
Server = https://mirrors.aliyun.com/archlinux/$repo/os/$arch
Server = https://mirrors.zju.edu.cn/archlinux/$repo/os/$arch
Server = https://mirrors.hit.edu.cn/archlinux/$repo/os/$arch
Server = https://mirrors.sjtug.sjtu.edu.cn/archlinux/$repo/os/$arch
Server = https://mirrors.nju.edu.cn/archlinux/$repo/os/$arch
Server = https://mirror.lzu.edu.cn/archlinux/$repo/os/$arch
```

---

## 3. Pacman Hooks

### 3.1 Hook 机制概述

```bash
# Hooks 目录
ls /etc/pacman.d/hooks/
ls /usr/share/libalpm/hooks/

# Hook 触发时机：
# PreTransaction — 事务开始前
# PostTransaction — 事务完成后（最常用）
# Hook 触发类型：
# File — 监控文件路径变化
# Package — 监控具体包的变化
```

### 3.2 实用 Hook 示例

#### 自动更新 GRUB 配置

```ini
# /etc/pacman.d/hooks/grub.hook
[Trigger]
Operation = Install
Operation = Upgrade
Operation = Remove
Type = File
Target = usr/lib/modules/*/vmlinuz
Target = usr/lib/systemd/boot/efi/*
Target = boot/*-ucode.img

[Action]
Description = 更新 GRUB 配置...
When = PostTransaction
Exec = /usr/bin/grub-mkconfig -o /boot/grub/grub.cfg
```

#### 自动更新 systemd-boot

```ini
# /etc/pacman.d/hooks/systemd-boot.hook
[Trigger]
Type = File
Operation = Install
Operation = Upgrade
Target = usr/lib/systemd/boot/efi/systemd-bootx64.efi

[Action]
Description = 更新 systemd-boot...
When = PostTransaction
Exec = /usr/bin/bootctl update
```

#### 自动清理 pacman 缓存

```ini
# /etc/pacman.d/hooks/paccache.hook
[Trigger]
Operation = Upgrade
Operation = Install
Operation = Remove
Type = Package
Target = *

[Action]
Description = 清理 pacman 缓存（保留最近 3 个版本）...
When = PostTransaction
Exec = /usr/bin/paccache -rk3
```

#### 检查 .pacnew 文件

```ini
# /etc/pacman.d/hooks/pacnew-check.hook
[Trigger]
Operation = Install
Operation = Upgrade
Type = Package
Target = *

[Action]
Description = 检查 .pacnew 配置文件...
When = PostTransaction
Exec = /usr/bin/env bash -c 'pacnews=$(find /etc -name "*.pacnew" 2>/dev/null); \
 if [ -n "$pacnews" ]; then \
 echo " 发现 .pacnew 配置变更文件：" >&2; \
 echo "$pacnews" >&2; \
 echo "请用 diff 对比后合并或删除 .pacnew 文件" >&2; \
 fi'
```

#### 更新 fontconfig 缓存

```ini
# /etc/pacman.d/hooks/fontconfig.hook
[Trigger]
Type = File
Operation = Install
Operation = Upgrade
Operation = Remove
Target = usr/share/fonts/*

[Action]
Description = 刷新字体缓存...
When = PostTransaction
Exec = /usr/bin/fc-cache -f
```

#### 更新 desktop 数据库

```ini
# /etc/pacman.d/hooks/desktop.hook
[Trigger]
Type = File
Operation = Install
Operation = Upgrade
Operation = Remove
Target = usr/share/applications/*.desktop

[Action]
Description = 更新桌面数据库...
When = PostTransaction
Exec = /usr/bin/update-desktop-database -q
```

#### Flatpak 更新后清理

```ini
# /etc/pacman.d/hooks/flatpak-cleanup.hook
[Trigger]
Type = Package
Operation = Upgrade
Target = flatpak

[Action]
Description = 清理未使用的 Flatpak 运行时...
When = PostTransaction
Exec = /usr/bin/flatpak uninstall --unused -y
```

#### Alpine/容器镜像更新后重建

```ini
# /etc/pacman.d/hooks/docker-rebuild.hook
[Trigger]
Type = Package
Operation = Upgrade
Target = docker

[Action]
Description = 重启 Docker（如果配置变动）...
When = PostTransaction
Exec = /usr/bin/systemctl try-restart docker
```

### 3.3 Hook 语法完整参考

```ini
[Trigger]
# 触发操作：Install, Upgrade, Remove
Operation = Install
Operation = Upgrade
Operation = Remove

# 触发类型：Package（包名匹配）或 File（路径通配符匹配）
Type = Package
Target = glibc # 精确匹配包名
Target = linux-* # 通配符匹配
Target = * # 所有包

# 或
Type = File
Target = usr/share/fonts/*
Target = boot/vmlinuz-*

[Action]
# 执行时机：PreTransaction 或 PostTransaction
When = PostTransaction

# 描述信息
Description = 正在执行某个操作...

# 执行的命令
Exec = /bin/sh -c 'your command here'

# 高级选项：
# NeedsTargets — 将触发此 Hook 的目标传递给 Exec
# AbortOnFail — 如果 Exec 返回值非零，则中止事务
# Depends — 指定依赖的 Hook 先执行（用 .hook 文件名）
```

---

## 4. 降级包

### 4.1 从缓存降级

```bash
# 查看缓存中的包版本
ls -la /var/cache/pacman/pkg/linux-*.pkg.tar.zst

# 直接安装指定版本
sudo pacman -U /var/cache/pacman/pkg/linux-6.8.1.arch1-1-x86_64.pkg.tar.zst

# 如果有依赖问题，可以强制
sudo pacman -U --overwrite '*' /var/cache/pacman/pkg/linux-6.8.1.arch1-1-x86_64.pkg.tar.zst
```

### 4.2 从 Arch Linux Archive 降级

```bash
# Arch Linux Archive (ALA) 保存了历年所有包的快照
# 网址：https://archive.archlinux.org/

# 方法 1：手动下载并安装
curl -O https://archive.archlinux.org/packages/l/linux/linux-6.8.1.arch1-1-x86_64.pkg.tar.zst
sudo pacman -U linux-6.8.1.arch1-1-x86_64.pkg.tar.zst

# 方法 2：downgrade 工具（AUR）
paru -S downgrade
downgrade linux # 交互式选择版本
downgrade linux-lts # 支持多包
```

### 4.3 使用 IgnorePkg 阻止升级

```bash
# /etc/pacman.conf
# 忽略内核升级（不推荐长期使用）
IgnorePkg = linux linux-headers linux-lts linux-lts-headers
# 或对特定包忽略
IgnorePkg = nvidia nvidia-utils nvidia-dkms

# 取消忽略但保留配置
# IgnorePkg = nvidia
```

### 4.4 部分升级的危险性

```bash
# 部分升级（partial upgrade）会导致 ABI 不一致，引发系统崩溃！
# 正确的升级方式始终是：
sudo pacman -Syu

# 如果必须安装单个包但忽略升级：
sudo pacman -Syu --ignore pkgname
# 或先升级后安装
sudo pacman -Syu && sudo pacman -S pkgname
```

---

## 5. 缓存管理

### 5.1 pacman 缓存目录

```bash
# 缓存位置
ls /var/cache/pacman/pkg/

# 查看缓存占用
du -sh /var/cache/pacman/pkg/
```

### 5.2 paccache 工具

```bash
# 安装 pacman-contrib 获得 paccache
sudo pacman -S pacman-contrib

# 保留最近 3 个版本，删除旧版本
sudo paccache -rk3

# 保留最近 1 个版本
sudo paccache -rk1

# 删除所有已卸载包的缓存
sudo paccache -ruk0

# 查看即将删除的文件（不实际操作）
sudo paccache -dvk2

# 查看占用空间报告
sudo paccache -dk2
```

### 5.3 pacman 内置清理

```bash
# 清理未安装包的缓存
sudo pacman -Sc

# 完全清理所有缓存
sudo pacman -Scc

# 完全清理（不提示）
sudo pacman -Scc --noconfirm
```

### 5.4 systemd 定时清理

```bash
# 启用 paccache 定时器（如果已通过 pacman-contrib 安装）
sudo systemctl enable paccache.timer
sudo systemctl start paccache.timer

# 查看定时器状态
systemctl list-timers | grep paccache

# 或手动配置 systemd timer
sudo tee /etc/systemd/system/paccache-cleanup.service << 'EOF'
[Unit]
Description=清理 pacman 缓存（保留最近 2 个版本）
[Service]
Type=oneshot
ExecStart=/usr/bin/paccache -rk2
EOF

sudo tee /etc/systemd/system/paccache-cleanup.timer << 'EOF'
[Unit]
Description=每周清理 pacman 缓存
[Timer]
OnCalendar=weekly
Persistent=true
[Install]
WantedBy=timers.target
EOF

sudo systemctl enable --now paccache-cleanup.timer
```

---

## 6. 常见 pacman 问题与解决

### 6.1 数据库锁定

```bash
# 错误: "failed to init transaction (unable to lock database)"
# 原因: 另一个 pacman 进程正在运行，或异常中断留下锁文件

# 检查是否有 pacman 进程
ps aux | grep pacman

# 删除锁文件（确认没有 pacman 在运行后）
sudo rm /var/lib/pacman/db.lck
```

### 6.2 密钥签名错误

```bash
# 错误: "signature is unknown trust"
# 错误: "required key missing from keyring"

# 更新密钥环
sudo pacman -Sy archlinux-keyring

# 重置密钥
sudo pacman-key --init
sudo pacman-key --populate archlinux

# 刷新所有密钥
sudo pacman-key --refresh-keys

# 时间不对也会导致签名验证失败
timedatectl set-ntp true
```

### 6.3 文件冲突

```bash
# 错误: "package1: /usr/bin/file exists in filesystem"

# 检查冲突文件属于哪个包
pacman -Qo /usr/bin/file

# 如果文件不属于任何包（孤立的），可以安全覆盖
sudo pacman -S pkgname --overwrite /usr/bin/file

# 强制覆盖所有冲突（危险，确保你了解后果）
sudo pacman -Syu --overwrite '*'

# 更好的做法：手动处理冲突
sudo mv /usr/bin/file /usr/bin/file.bak
sudo pacman -S pkgname
```

### 6.4 安装失败回滚

```bash
# 检查还有哪些包未满足依赖
pacman -Dk

# 修复损坏的依赖
sudo pacman -S --needed $(pacman -Qdtq)

# 重新安装所有包以修复 ABI 问题
sudo pacman -S $(pacman -Qqn)

# 从 pacman 日志找最近安装/更新的包
cat /var/log/pacman.log | tail -50
grep "installed\|upgraded\|removed" /var/log/pacman.log
```

### 6.5 数据库损坏

```bash
# 错误: "error opening or reading database"

# 强制重新同步数据库
sudo pacman -Syy

# 如果上述无效，尝试修复
sudo pacman -Dk

# 最后手段：重建数据库（极危险）
sudo mv /var/lib/pacman/local /var/lib/pacman/local.bak
sudo pacman -Syy
# 重新安装所有包
sudo pacman -S $(comm -23 <(pacman -Qq | sort) <(pacman -Qmq | sort))
```

### 6.6 部分升级导致的段错误

```bash
# 症状：程序启动时报段错误、加载 .so 报 undefined symbol

# 解决方案：完整升级系统
sudo pacman -Syu

# 如果无法进入系统，chroot 修复
# 从 Live ISO 启动后：
mount /dev/nvme0n1p2 /mnt
arch-chroot /mnt
pacman -Syu
```

### 6.7 恢复被删除的包

```bash
# 查看 pacman 日志中被删除的包
grep "removed" /var/log/pacman.log | tail -20

# 重新安装它们
grep "removed" /var/log/pacman.log | awk -F'removed ' '{print $2}' | \
 awk '{print $1}' | xargs sudo pacman -S --noconfirm
```

---

## 7. pacman 高级技巧

### 7.1 包管理的 Power-user 命令

```bash
# 列出所有不需要的可选依赖
pacman -Qdtq | xargs -I {} pacman -Qd -q {} 2>/dev/null | sort -u

# 查找体积最大的包（MB）
expac -H M '%m\t%n' | sort -h | tail -20

# 查找所有修改过的配置文件
pacman -Qii | awk '/^MODIFIED/{print $2}'

# 查找不属于任何包的文件
find /etc -not -path '*/.git/*' -type f | pacman -Qo - 2>&1 | grep 'No package owns'

# 显示上次更新的包列表
awk '/upgraded/{for(i=4;i<=NF;i++) printf "%s ",$i; print ""}' /var/log/pacman.log

# 按安装日期排序查看包（最近安装的在前）
grep "installed" /var/log/pacman.log | tail -20
```

### 7.2 批量操作

```bash
# 安装一个列表文件中的包
sudo pacman -S --needed - < pkglist.txt

# 导出显式安装的包列表
pacman -Qqe > pkglist.txt

# 在另一台机器上安装同样的包
sudo pacman -S --needed - < pkglist.txt

# 导出所有已安装的包（用于备份）
pacman -Qqen > native-pkgs.txt # 官方仓库包
pacman -Qqem > foreign-pkgs.txt # AUR/第三方包

# 批量删除孤立的包
sudo pacman -Rns $(pacman -Qdtq)

# 从缓存安装特定时期的包
ls -lt /var/cache/pacman/pkg/ | head -20
```

### 7.3 查看包变更历史

```bash
# pacman 日志位置
less /var/log/pacman.log

# 只查看最近的升级
grep "upgraded" /var/log/pacman.log | tail -30

# 查看特定包的历史
grep "linux " /var/log/pacman.log
```

### 7.4 ilovecats (ILOVECATS) — 启动时强制重装

```bash
# 如果系统完全无法启动、软件包损坏严重
# 在 GRUB 中添加 ilovecats 内核参数，强制将所有包标记为需要重新安装

# 或从 Live ISO chroot 后执行：
pacman -Qqn | sudo pacman -S -
```

---

## 8. 第三方包管理工具

| 工具 | 用途 |
|------|------|
| `paru` | AUR 助手 + pacman 包装器 |
| `yay` | AUR 助手 + pacman 包装器 |
| `pamac` | GUI 包管理器（支持 AUR） |
| `octopi` | Qt 包管理 GUI |
| `bauh` | 多格式包管理（pacman+AUR+Flatpak+Snap+AppImage） |
| `pacgraph` | 包依赖关系可视化 |
| `expac` | pacman 数据库快速查询工具 |

---

## 9. pacman 调试

```bash
# 调试级别
pacman -Syu --debug # 详细输出
pacman -Syu --print # 只打印将执行的操作，不实际执行
pacman -Syu --print-format "%n %v" # 自定义输出格式

# 查看数据库中的包信息
pacman -Qi | head -100

# 查看本地数据库结构
ls /var/lib/pacman/local/
```

---

## 10.5 AUR 安装失败排查

### 10.5.1 核心原则

```
AUR 包本质是用户维护的 PKGBUILD 脚本，质量参差不齐。
装不上就去官网直接下载，比折腾 PKGBUILD 效率高得多。
yay/paru 只是帮你执行 makepkg，不是万能的。
```

### 10.5.2 常见错误与处理方式

#### 错误 1：sha256sums 不允许空值

```
==> 错误： sha256sums 不允许空值。
==> 错误： sha256sums 不允许空值。
 -> 下载源文件时出错: /home/a/.cache/yay/tor-browser-bin
    context: exit status 12
```

原因：PKGBUILD 中 sha256sums 数组为空或格式错误。AUR 包更新版本后，维护者没更新哈希值。

解决方案：

```bash
# 方案 A：清理构建缓存后重试（最简单）
rm -rf ~/.cache/yay/tor-browser-bin
yay -S tor-browser-bin

# 方案 B：手动修改 PKGBUILD（推荐）
yay -S tor-browser-bin --edit
# 编辑器打开后找到 sha256sums=()
# 改为：sha256sums=('SKIP')
# 保存退出后继续安装

# 方案 C：直接从官网下载二进制包（最省事）
# 去 https://www.torproject.org/download/ 下载 Linux 版本
# 解压后直接运行，不走 AUR
```

#### 错误 2：网络问题

```
==> 正在拉取源文件...
curl: (28) Connection timed out after 300002 milliseconds
==> 错误： 下载源文件时出错
```

原因：AUR 包的 source 数组中包含外网链接，国内访问超时。

解决方案：

```bash
# 临时设置代理
export https_proxy=http://127.0.0.1:7890
export http_proxy=http://127.0.0.1:7890
yay -S <包名>

# 永久配置代理（yay）
# 编辑 ~/.config/yay.conf
# 添加：
# BottomUp
# SudoLoop
# 或者在 /etc/environment 中设置全局代理

# 永久配置代理（paru）
# 编辑 ~/.config/paru.conf
# 添加：
# BottomUp
# SudoLoop
```

#### 错误 3：包冲突

```
:: tor-browser-bin 与 tor-browser 存在冲突
:: tor-browser-bin 与 tor-browser-alpha-bin 存在冲突
```

原因：系统中已安装同类型包，或多个 AUR 包互相冲突。

解决方案：

```bash
# 查看冲突的是什么
yay -S <包名> 2>&1 | grep "conflicting"

# 删掉冲突的包再装
yay -R <冲突包名>
yay -S <新包名>

# 强制替换（如果确定要换）
yay -S <新包名> --overwrite '*'
```

#### 错误 4：依赖问题

```
:: 以下软件包无法满足依赖关系：
  <包名>: 需要 <依赖名>
```

原因：系统未全量更新，或依赖包在 AUR 中但未安装。

解决方案：

```bash
# 先全量更新系统
sudo pacman -Syu

# 再装 AUR 包
yay -S <包名>

# 如果依赖也是 AUR 包，yay 会自动处理
# 如果依赖找不到，检查是否在正确的仓库中
```

#### 错误 5：数据库锁

```
error: failed to init transaction (unable to lock database)
```

原因：另一个 pacman/yay 进程正在运行，或上次运行异常中断留下锁文件。

解决方案：

```bash
# 检查是否有 pacman 进程在运行
ps aux | grep pacman

# 如果没有，删除锁文件
sudo rm /var/lib/pacman/db.lck
```

#### 错误 6：PGP 签名错误

```
error: tor-browser-bin: signature is unknown trust
```

原因：密钥环过期或未更新。

解决方案：

```bash
# 更新密钥环
sudo pacman -Sy archlinux-keyring

# 临时跳过签名验证（不推荐，仅测试）
yay -S <包名> --skipinteg

# 重新初始化密钥
sudo pacman-key --init
sudo pacman-key --populate archlinux
```

#### 错误 7：构建失败（makepkg 报错）

```
==> 错误： 在 build() 中发生错误。
```

原因：缺少编译依赖（makedepends），或源码编译环境不完整。

解决方案：

```bash
# 进入构建目录查看详细错误
cd ~/.cache/yay/<包名>
makepkg -si

# 查看 PKGBUILD 中的 makedepends
grep makedepends PKGBUILD

# 安装缺失的编译依赖
sudo pacman -S <缺失的依赖>

# 重新构建
makepkg -si
```

### 10.5.3 AUR 助手配置优化

```bash
# yay 配置文件：~/.config/yay.conf
BottomUp        # 搜索结果从下往上显示
SudoLoop        # 循环使用 sudo，避免反复输入密码
CleanAfter      # 安装后自动清理构建缓存
BuildDir=/tmp   # 构建目录（默认 ~/.cache/yay）

# paru 配置文件：~/.config/paru.conf
BottomUp
SudoLoop
CleanAfter
BuildDir=/tmp
```

### 10.5.4 实战案例：tor-browser-bin 安装失败

```bash
# 1. 搜索 tor-browser
yay -S tor-browser
:: 对于 %! (string=tor-browser)有 2 个结果：
:: AUR 软件库
    1) tor-browser-alpha-bin
    2) tor-browser-bin

# 2. 选择 tor-browser-bin（输入 2）
输入数字 (默认=1): 2

# 3. 提示构建文件已存在
:: 清理哪些包的构建文件？
==> [N]没有 [A]全部 [Ab]中止 [I]已安装 [No]未安装
# 选择 A（全部清理）

# 4. 提示显示差异
:: 显示哪些包的差异？
==> [N]没有 [A]全部 [Ab]中止 [I]已安装 [No]未安装
# 选择 N（不看差异）

# 5. 报错：sha256sums 不允许空值
==> 错误： sha256sums 不允许空值。
 -> 下载源文件时出错: /home/a/.cache/yay/tor-browser-bin
    context: exit status 12

# 6. 解决：手动修改 PKGBUILD
yay -S tor-browser-bin --edit
# 找到 sha256sums=('') 或 sha256sums=()
# 改为 sha256sums=('SKIP')
# 保存退出，继续安装

# 或者直接去官网下载
# https://www.torproject.org/download/
```

### 10.5.5 AUR 包质量评估

```bash
# 在 AUR 页面查看：
# 1. Votes（投票数）：越高越可靠
# 2. Popularity（热度）：近期安装量
# 3. 最后修改时间：超过 1 年未更新的要谨慎
# 4. 评论区：看其他人反馈的问题

# 命令行查看包信息
yay -Ss <包名>
# 查看 PKGBUILD 内容
yay -S <包名> ---edit  # 不保存退出即可查看

# 检查依赖是否合理
yay -Si <包名>
```

### 10.5.6 替代方案

```bash
# 如果 AUR 装不上，考虑以下替代方案：

# 1. 官网直接下载二进制包
# 适合：Tor Browser、Chrome、VS Code 等

# 2. Flatpak
flatpak install flathub <应用名>

# 3. Snap
sudo snap install <应用名>

# 4. AppImage
# 下载 .AppImage 文件，chmod +x 后直接运行

# 5. 官方仓库可能有替代包
pacman -Ss <关键词>
```

---

## 10. 相关资源

- pacman 官方手册: `man pacman`
- pacman.conf 手册: `man pacman.conf`
- Arch Wiki 镜像列表: https://wiki.archlinux.org/title/Mirrors
- Arch Linux Archive: https://archive.archlinux.org/
- Arch Wiki pacman: https://wiki.archlinux.org/title/Pacman
- Arch Wiki AUR: https://wiki.archlinux.org/title/AUR
- Arch Wiki yay: https://wiki.archlinux.org/title/Yay
- Arch Wiki paru: https://wiki.archlinux.org/title/Paru
- 官方下载: https://archlinux.org/download/
- 清华镜像: https://mirrors.tuna.tsinghua.edu.cn/archlinux/
- 中科大镜像: https://mirrors.ustc.edu.cn/archlinux/
- AUR 搜索: https://aur.archlinux.org/
- [[../arch/01-安装指南|Arch 安装指南]]
- [[../arch/03-AUR打包与上传|AUR 打包与上传]]
- [[../arch/06-自定义系统打包|自定义系统打包]]
- [[../arch/04-深度玩法|Arch 深度玩法]]
