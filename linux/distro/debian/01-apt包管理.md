# Debian/Ubuntu APT 包管理完整参考

> APT (Advanced Package Tool) 是 Debian 及其衍生发行版（Ubuntu、Linux Mint、Deepin 等）的核心包管理系统。本章是 apt/apt-get 的完整操作手册，覆盖 sources.list 管理、apt pinning、backports 和无人值守升级。

---

## 1. 资源链接

| 资源 | 链接 |
|------|------|
| Debian 官网 | https://www.debian.org/ |
| Debian 下载 | https://www.debian.org/download |
| Ubuntu 官网 | https://ubuntu.com/ |
| Ubuntu 下载 | https://ubuntu.com/download |
| 清华镜像 | https://mirrors.tuna.tsinghua.edu.cn/debian/ |
| 清华 Ubuntu 镜像 | https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ |
| 中科大镜像 | https://mirrors.ustc.edu.cn/debian/ |
| 中科大 Ubuntu 镜像 | https://mirrors.ustc.edu.cn/ubuntu/ |
| 阿里云镜像 | https://mirrors.aliyun.com/debian/ |
| 阿里云 Ubuntu 镜像 | https://mirrors.aliyun.com/ubuntu/ |
| Debian Wiki | https://wiki.debian.org/ |

---

## 2. apt 与 apt-get 区别

| 特性 | apt | apt-get |
|------|-----|---------|
| 设计目标 | 终端用户友好界面 | 底层命令行工具 |
| 输出格式 | 彩色进度条 | 普通文本 |
| 稳定性 | 命令可能变更 | 命令稳定不变 |
| 脚本兼容 | 不保证向后兼容 | 保证向后兼容 |
| 推荐使用场景 | 手动操作 | 脚本/自动化 |

```bash
# 脚本中永远使用 apt-get
# 手工操作时使用 apt 更友好
```

---

## 3. apt 完整命令参考

### 3.1 基本操作

```bash
# 更新包索引（必须先执行）
sudo apt update

# 升级所有已安装的包
sudo apt upgrade

# 完整升级（可能删除冲突的包）
sudo apt full-upgrade

# 安装包
sudo apt install pkgname

# 安装多个包
sudo apt install pkg1 pkg2 pkg3

# 安装本地 .deb 文件（自动处理依赖）
sudo apt install ./file.deb

# 删除包（保留配置）
sudo apt remove pkgname

# 完全删除包（包括配置）
sudo apt purge pkgname

# 自动删除不需要的依赖
sudo apt autoremove

# 清理下载的包缓存
sudo apt clean
sudo apt autoclean
```

### 3.2 搜索与查询

```bash
# 搜索包
apt search keyword

# 显示包详细信息
apt show pkgname

# 列出所有已安装的包
apt list --installed

# 列出所有可升级的包
apt list --upgradable

# 列出包的依赖关系
apt depends pkgname

# 列出包的逆向依赖（哪些包依赖它）
apt rdepends pkgname

# 查看包所包含的文件（已安装的包）
dpkg -L pkgname

# 查看包所包含的文件（未安装的包）
apt-file list pkgname

# 搜索哪个包提供某个文件
apt-file search /path/to/file
```

### 3.3 包管理策略

```bash
# 标记包为手动安装（防止被 autoremove 删除）
sudo apt-mark manual pkgname

# 标记包为自动安装（作为依赖安装）
sudo apt-mark auto pkgname

# 禁止升级某个包
sudo apt-mark hold pkgname

# 取消禁止升级
sudo apt-mark unhold pkgname

# 查看所有被 hold 的包
apt-mark showhold

# 查看所有手动安装的包
apt-mark showmanual

# 查看所有自动安装的包
apt-mark showauto
```

### 3.4 包信息查询

```bash
# 列出包的版本和仓库
apt policy pkgname

# 查看包的 Debian changelog
apt changelog pkgname

# 查看包正在使用哪些源
apt-cache policy pkgname

# 列出包的源仓库
apt-cache madison pkgname

# 查看包的所有版本
apt-cache showpkg pkgname

# 统计缓存中包的依赖问题
apt-cache unmet
```

---

## 4. sources.list 管理

### 4.1 文件结构

```bash
# 主配置文件
/etc/apt/sources.list

# 额外源（推荐使用此目录管理第三方源）
/etc/apt/sources.list.d/*.list

# 也可以使用 .sources 格式（DEB822 格式，Debian 12+ 推荐）
/etc/apt/sources.list.d/*.sources
```

### 4.2 传统 .list 格式

```
# 语法：deb|deb-src [选项] URL 发行版 组件 [组件...]

# ========== Debian 12 (Bookworm) 基础源 ==========

# 主仓库（非自由）
deb http://deb.debian.org/debian bookworm main contrib non-free non-free-firmware
deb-src http://deb.debian.org/debian bookworm main contrib non-free non-free-firmware

# 安全更新
deb http://security.debian.org/debian-security bookworm-security main contrib non-free non-free-firmware
deb-src http://security.debian.org/debian-security bookworm-security main contrib non-free non-free-firmware

# 稳定版更新
deb http://deb.debian.org/debian bookworm-updates main contrib non-free non-free-firmware
deb-src http://deb.debian.org/debian bookworm-updates main contrib non-free non-free-firmware

# Backports
deb http://deb.debian.org/debian bookworm-backports main contrib non-free non-free-firmware
deb-src http://deb.debian.org/debian bookworm-backports main contrib non-free non-free-firmware
```

### 4.3 中国镜像 sources.list

```bash
# Debian 12 清华镜像
deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm main contrib non-free non-free-firmware
deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm-updates main contrib non-free non-free-firmware
deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm-backports main contrib non-free non-free-firmware
deb https://mirrors.tuna.tsinghua.edu.cn/debian-security bookworm-security main contrib non-free non-free-firmware

# Debian 12 中科大镜像
deb https://mirrors.ustc.edu.cn/debian/ bookworm main contrib non-free non-free-firmware
deb https://mirrors.ustc.edu.cn/debian/ bookworm-updates main contrib non-free non-free-firmware
deb https://mirrors.ustc.edu.cn/debian/ bookworm-backports main contrib non-free non-free-firmware
deb https://mirrors.ustc.edu.cn/debian-security bookworm-security main contrib non-free non-free-firmware

# Debian 12 阿里云镜像
deb https://mirrors.aliyun.com/debian/ bookworm main contrib non-free non-free-firmware
deb https://mirrors.aliyun.com/debian/ bookworm-updates main contrib non-free non-free-firmware
deb https://mirrors.aliyun.com/debian/ bookworm-backports main contrib non-free non-free-firmware
deb https://mirrors.aliyun.com/debian-security bookworm-security main contrib non-free non-free-firmware
```

### 4.4 新 DEB822 格式 (.sources)

```
# /etc/apt/sources.list.d/debian.sources
# Debian 12+ 推荐使用此格式
Types: deb deb-src
URIs: https://mirrors.tuna.tsinghua.edu.cn/debian/
Suites: bookworm bookworm-updates bookworm-backports
Components: main contrib non-free non-free-firmware
Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg

Types: deb deb-src
URIs: https://mirrors.tuna.tsinghua.edu.cn/debian-security/
Suites: bookworm-security
Components: main contrib non-free non-free-firmware
Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg
```

### 4.5 发行版代号与组件说明

| 发行版 | 代号 | 说明 |
|--------|------|------|
| Debian 13 | Trixie | Testing（当前测试版） |
| Debian 12 | Bookworm | Stable（当前稳定版） |
| Debian 11 | Bullseye | Oldstable |
| Debian 10 | Buster | Oldoldstable |

| 组件 | 说明 |
|------|------|
| `main` | DFSG 自由软件（Debian 官方支持） |
| `contrib` | 自由软件但依赖非自由组件 |
| `non-free` | 非自由软件 |
| `non-free-firmware` | 非自由固件（Debian 12 新增） |

| 后缀 | 说明 |
|------|------|
| `-updates` | 重要更新（如时区、安全外的关键修复） |
| `-security` | 安全更新 |
| `-backports` | 从 Testing 回移植到 Stable 的新版本 |
| `-proposed-updates` | 待发布的更新 |
| `-backports-sloppy` | 从 Unstable 回移植到 Stable |

---

## 5. apt pinning（优先级控制）

### 5.1 原理

```bash
# apt pinning 控制从哪个仓库安装特定包
# 优先级：1-1000，值越高越优先
# 默认优先级：
# 990 — 来自目标发行版的包
# 500 — 来自其他发行版的包
# 100 — 已安装但不在仓库中的包
# 1 — 实验性包
# -1 — 禁止安装
```

### 5.2 配置 pinning

```bash
# /etc/apt/preferences 或 /etc/apt/preferences.d/xxx.pref
```

```
# 示例 1：全局优先使用 Backports
Package: *
Pin: release a=bookworm-backports
Pin-Priority: 500

# 示例 2：为特定包设置 Backports 优先
Package: linux-image-amd64
Pin: release a=bookworm-backports
Pin-Priority: 990

Package: firmware-*
Pin: release a=bookworm-backports
Pin-Priority: 990

# 示例 3：禁止从 Testing 安装（使用 Testing 中的特定包除外）
Package: *
Pin: release a=testing
Pin-Priority: 50

# 示例 4：锁定特定包为特定版本
Package: nginx
Pin: version 1.22.1-*
Pin-Priority: 1001

# 示例 5：从特定源安装
Package: *
Pin: origin "packages.example.com"
Pin-Priority: 700

# 示例 6：禁止安装 systemd 的 Testing 版本
Package: systemd
Pin: release a=testing
Pin-Priority: -1
```

### 5.3 查看效果

```bash
# 查看某个包的版本候选和优先级
apt-cache policy pkgname

# 示例输出：
# nginx:
# Installed: 1.22.1-9
# Candidate: 1.22.1-9
# Version table:
# 1.24.0-1~bpo12+1 100
# 100 http://deb.debian.org/debian bookworm-backports/main amd64 Packages
# *** 1.22.1-9 990
# 990 http://deb.debian.org/debian bookworm/main amd64 Packages
# 100 /var/lib/dpkg/status
```

### 5.4 从 Backports 安装

```bash
# 方法 1：明确指定（推荐）
sudo apt install -t bookworm-backports linux-image-amd64

# 方法 2：使用 pinning 自动优先
# 配置后直接安装即可
sudo apt install linux-image-amd64
```

---

## 6. Backports 详解

### 6.1 添加 Backports

```bash
# 添加到 /etc/apt/sources.list 或 sources.list.d/
echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm-backports main contrib non-free non-free-firmware" | \
 sudo tee /etc/apt/sources.list.d/backports.list

sudo apt update
```

### 6.2 从 Backports 安装

```bash
# 搜索 Backports 中的包
apt search pkgname | grep backports

# 从 Backports 安装
sudo apt install -t bookworm-backports pkgname

# 完整升级到 Backports 版本并删除冲突
sudo apt full-upgrade -t bookworm-backports
```

### 6.3 Backports 常用场景

```bash
# 安装较新的内核
sudo apt install -t bookworm-backports linux-image-amd64 linux-headers-amd64

# 安装新版软件
sudo apt install -t bookworm-backports libreoffice
sudo apt install -t bookworm-backports pipewire

# 安装新版固件
sudo apt install -t bookworm-backports firmware-linux
```

---

## 7. 无人值守升级 (Unattended Upgrades)

### 7.1 安装与配置

```bash
sudo apt install unattended-upgrades

# 配置文件
sudo vim /etc/apt/apt.conf.d/50unattended-upgrades
```

### 7.2 配置示例

```
// 基础配置
Unattended-Upgrade::Allowed-Origins {
 "${distro_id}:${distro_codename}";
 "${distro_id}:${distro_codename}-security";
 "${distro_id}ESMApps:${distro_codename}-apps-security";
 "${distro_id}ESM:${distro_codename}-infra-security";
 "${distro_id}:${distro_codename}-updates";
};

// 黑名单（禁止自动升级的包）
Unattended-Upgrade::Package-Blacklist {
 "linux-image-amd64";
 "linux-headers-amd64";
 "nvidia-driver";
};

// 自动删除不需要的依赖
Unattended-Upgrade::Remove-Unused-Kernel-Packages "true";
Unattended-Upgrade::Remove-New-Unused-Dependencies "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";

// 自动重启
Unattended-Upgrade::Automatic-Reboot "false";
Unattended-Upgrade::Automatic-Reboot-Time "02:00";

// 仅在空闲时自动关机/重启
Unattended-Upgrade::Automatic-Reboot-WithUsers "true";

// 邮件通知
Unattended-Upgrade::Mail "admin@example.com";
Unattended-Upgrade::MailReport "only-on-error";
// on-change / only-on-error

// 带宽限制
Unattended-Upgrade::Acquire::http::Dl-Limit "70";
```

### 7.3 启用自动升级

```bash
# 编辑 /etc/apt/apt.conf.d/20auto-upgrades
cat > /etc/apt/apt.conf.d/20auto-upgrades << 'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
APT::Periodic::Download-Upgradeable-Packages "0";
APT::Periodic::AutocleanInterval "7";
EOF

# 参数说明：
# Update-Package-Lists "1" 每天更新包列表
# Unattended-Upgrade "1" 每天执行无人值守升级
# AutocleanInterval "7" 每 7 天清理一次缓存

# 手动测试无人值守升级
sudo unattended-upgrade --dry-run --debug
```

### 7.4 查看日志

```bash
# 查看无人值守升级日志
less /var/log/unattended-upgrades/unattended-upgrades.log

# 查看最近的升级记录
tail -50 /var/log/unattended-upgrades/unattended-upgrades.log
```

---

## 8. APT 高级配置

### 8.1 apt.conf 配置

```bash
# /etc/apt/apt.conf.d/ 目录下的配置文件

# 99custom — 自定义配置
```

```
# 使用代理
Acquire::http::Proxy "http://proxy.example.com:8080";
Acquire::https::Proxy "https://proxy.example.com:8080";

# 默认安装推荐和推荐包
APT::Install-Recommends "true";
APT::Install-Suggests "false";

# 不安装推荐包（节省空间，服务器常用）
APT::Install-Recommends "false";

# 超时设置
Acquire::http::Timeout "10";
Acquire::ftp::Timeout "10";

# 下载重试次数
Acquire::Retries "3";

# 默认发布
APT::Default-Release "bookworm";

# 不要安装冲突包
APT::Get::AllowUnauthenticated "false";

# 显示升级的变更日志
APT::Get::Show-Upgraded "true";
```

### 8.2 APT 缓存管理

```bash
# 查看包的 .deb 缓存位置
ls /var/cache/apt/archives/

# 查看缓存大小
du -sh /var/cache/apt/archives/

# 清理过期的包（已从仓库删除的）
sudo apt autoclean

# 清理所有下载的包
sudo apt clean

# 配置自动清理周期
echo 'APT::Periodic::AutocleanInterval "7";' | sudo tee /etc/apt/apt.conf.d/99autoclean
```

### 8.3 APT 调试

```bash
# 调试模式
sudo apt-get -o Debug::pkgProblemResolver=yes install pkgname

# 模拟安装（不实际执行）
sudo apt install --dry-run pkgname

# 查看将要安装/删除的包
apt list --upgradable

# 查看 apt 日志
less /var/log/apt/history.log
less /var/log/apt/term.log
```

### 8.4 修复损坏的依赖

```bash
# 修复依赖关系
sudo apt --fix-broken install

# 强制 dpkg 配置
sudo dpkg --configure -a

# 如果上述无效
sudo apt-get install -f
sudo dpkg --force-depends -i /var/cache/apt/archives/packagename.deb
sudo apt-get install -f
```

---

## 9. Ubuntu 特有扩展

### 9.1 PPA (Personal Package Archive)

```bash
# 添加 PPA
sudo add-apt-repository ppa:user/ppa-name

# 示例：添加 LibreOffice Fresh PPA
sudo add-apt-repository ppa:libreoffice/ppa

# 删除 PPA
sudo add-apt-repository --remove ppa:user/ppa-name

# 列出所有 PPA
ls /etc/apt/sources.list.d/

# 手动删除 PPA 文件
sudo rm /etc/apt/sources.list.d/xxx-ubuntu-xxx-*.list
sudo apt update
```

### 9.2 Snap 管理

```bash
# Ubuntu 特有：apt 安装某些包会自动转为 snap
# 查看 apt 到 snap 的映射
apt show firefox | grep -i snap

# 禁用此行为（参见 ../../distro/debian/02-Debian安装与服务器配置）
# /etc/apt/preferences.d/nosnap.pref
Package: snapd
Pin: release a=*
Pin-Priority: -10
```

### 9.3 Ubuntu Pro / ESM

```bash
# Ubuntu Pro 提供额外的安全维护（免费个人使用）
sudo pro attach <token>
sudo pro enable esm-infra
sudo pro status
```

---

## 10. 常用工具总览

| 工具 | 用途 |
|------|------|
| `apt` | 终端用户包管理 |
| `apt-get` | 脚本用包管理 |
| `apt-cache` | 查询包数据库 |
| `apt-file` | 按文件搜索包 |
| `apt-mark` | 包状态管理 |
| `aptitude` | 交互式包管理器 |
| `synaptic` | 图形化包管理器 |
| `unattended-upgrades` | 自动安全更新 |
| `needrestart` | 检查升级后需要重启的服务 |

---

## 11. 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `E: Unable to locate package` | 包索引未更新或包名错误 | `sudo apt update`，检查包名 |
| `E: Could not get lock` | 另一个 apt 进程在运行 | 等待或 `sudo killall apt apt-get` |
| `Hash Sum mismatch` | 镜像同步中 | 换镜像或过段时间再试 |
| `404 Not Found` | 仓库版本已下架 | 更新到当前发行版 |
| `The following packages have unmet dependencies` | 依赖冲突 | `sudo apt --fix-broken install` |
| 安装时缺少 GPG 密钥 | 第三方仓库缺失密钥 | 下载 .asc 或 .gpg 导入 |

---

## 12. 相关资源

- Debian 官方网站: https://www.debian.org/
- Debian Wiki: https://wiki.debian.org/
- APT 手册: `man apt`, `man sources.list`
- Ubuntu 包搜索: https://packages.ubuntu.com/
- Debian 包搜索: https://packages.debian.org/
- [[../debian/02-Debian安装与服务器配置|Debian 安装与服务器配置]]
- [[../debian/03-dpkg与deb打包|dpkg 与 deb 打包]]
- [[../debian/04-netplan与NetworkManager|netplan 与 NetworkManager]]
