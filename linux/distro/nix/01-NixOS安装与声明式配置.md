# NixOS 安装与声明式配置

> NixOS 是一个基于 Nix 包管理器的声明式 Linux 发行版。它以函数式包管理、原子升级和系统可复现性著称。本章覆盖 NixOS 安装流程、configuration.nix 基础、nixos-rebuild 命令、系统代际管理和 Nix 包管理器在其他发行版上的使用。

---

## 1. 资源链接

| 资源 | 链接 |
|------|------|
| NixOS 官网 | https://nixos.org/ |
| NixOS 下载 | https://nixos.org/download |
| Nix 包搜索 | https://search.nixos.org/packages |
| NixOS 选项搜索 | https://search.nixos.org/options |
| NixOS Wiki | https://nixos.wiki/ |
| Nix Pills 教程 | https://nixos.org/guides/nix-pills/ |
| 清华大学 Nix 镜像 | https://mirrors.tuna.tsinghua.edu.cn/nix/ |
| 中科大 Nix 镜像 | https://mirrors.ustc.edu.cn/nix-channels/store/ |

---

## 2. NixOS 核心理念

### 2.1 与其他发行版的区别

```
传统发行版（Arch/Debian/RHEL）：
  sudo apt install nginx            → 修改 /etc/nginx/...
  sudo vim /etc/nginx/nginx.conf    → 手动编辑配置
  系统状态 = 一系列累积的变更，难以复现

NixOS：
  /etc/nixos/configuration.nix  ← 定义整个系统
    services.nginx.enable = true;
    services.nginx.virtualHosts."example.com" = { ... };
  sudo nixos-rebuild switch
  → 系统状态完全由配置文件决定，可复现、可版本控制
```

### 2.2 关键特性

| 特性 | 说明 |
|------|------|
| **声明式配置** | 整个系统用一个配置文件描述 |
| **原子升级** | 升级失败自动回滚，系统要么完全升级要么不变 |
| **代际管理** | 每次变更产生一个 generation，可从 GRUB 选择启动 |
| **多版本共存** | 同一个包的多个版本可以同时存在 |
| **可复现** | 相同配置 + 相同 nixpkgs = 完全相同的系统 |
| **非 FHS** | 不使用 /usr/bin、/lib 等标准目录结构 |
| **垃圾回收** | 未使用的包可被回收释放空间 |

### 2.3 Nix Store

```bash
# 所有包都安装在 /nix/store/ 中
ls /nix/store/
# 每个路径都是内容寻址的哈希 + 包名
# 如: /nix/store/abc123...-nginx-1.24.0/

# 用户环境是 /nix/store/ 中文件的符号链接集合
which nginx
# /run/current-system/sw/bin/nginx → /nix/store/.../bin/nginx
```

---

## 3. NixOS 安装流程

### 3.1 下载镜像

```bash
# 官方下载
# https://nixos.org/download

# 或从清华镜像下载
wget https://mirrors.tuna.tsinghua.edu.cn/nixos/latest-iso/nixos-gnome-24.11-x86_64-linux.iso
wget https://mirrors.tuna.tsinghua.edu.cn/nixos/latest-iso/nixos-minimal-24.11-x86_64-linux.iso

# 验证
sha256sum nixos-*.iso
```

### 3.2 启动到安装环境

```bash
# 制作启动盘
sudo dd bs=4M if=nixos-minimal-24.11-x86_64-linux.iso of=/dev/sdb conv=fsync oflag=direct status=progress

# 启动后进入 root shell（无密码）
```

### 3.3 网络配置

```bash
# 有线网络（通常自动获取）
ip addr show

# 无线网络
wpa_passphrase "SSID" "password" >> /etc/wpa_supplicant.conf
wpa_supplicant -B -i wlan0 -c /etc/wpa_supplicant.conf
dhcpcd wlan0

# 使用 systemd-networkd
sudo systemctl start wpa_supplicant
wpa_cli
```

### 3.4 分区（UEFI + GPT）

```bash
# 查看磁盘
lsblk

# 分区（以 /dev/nvme0n1 为例）
sudo parted /dev/nvme0n1 -- mklabel gpt
sudo parted /dev/nvme0n1 -- mkpart ESP fat32 1MiB 512MiB
sudo parted /dev/nvme0n1 -- set 1 esp on
sudo parted /dev/nvme0n1 -- mkpart primary 512MiB 100%

# 格式化
sudo mkfs.fat -F 32 /dev/nvme0n1p1
sudo mkfs.ext4 /dev/nvme0n1p2

# 或使用 Btrfs + 子卷（高级）
# sudo mkfs.btrfs /dev/nvme0n1p2
# sudo mount /dev/nvme0n1p2 /mnt
# sudo btrfs subvolume create /mnt/@
# sudo btrfs subvolume create /mnt/@home
# sudo umount /mnt

# 挂载
sudo mount /dev/nvme0n1p2 /mnt
sudo mkdir -p /mnt/boot
sudo mount /dev/nvme0n1p1 /mnt/boot

# 如果是 Btrfs:
# sudo mount -o subvol=@,compress=zstd /dev/nvme0n1p2 /mnt
# sudo mkdir -p /mnt/{boot,home}
# sudo mount -o subvol=@home,compress=zstd /dev/nvme0n1p2 /mnt/home
# sudo mount /dev/nvme0n1p1 /mnt/boot
```

### 3.5 生成初始配置

```bash
# 生成基础配置文件
sudo nixos-generate-config --root /mnt

# 查看生成的配置
cat /mnt/etc/nixos/configuration.nix
cat /mnt/etc/nixos/hardware-configuration.nix
```

### 3.6 编辑 configuration.nix 基本配置

```bash
sudo vim /mnt/etc/nixos/configuration.nix
```

```nix
{ config, pkgs, ... }:

{
  imports = [ ./hardware-configuration.nix ];

  # ===== 引导 =====
  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;
  boot.loader.timeout = 3;

  # ===== 网络 =====
  networking.hostName = "nixos";
  networking.networkmanager.enable = true;
  # 或使用 systemd-networkd
  # networking.useNetworkd = true;

  # ===== 时区 =====
  time.timeZone = "Asia/Shanghai";

  # ===== 语言 =====
  i18n.defaultLocale = "en_US.UTF-8";
  i18n.extraLocaleSettings = {
    LC_TIME = "zh_CN.UTF-8";
    LC_MEASUREMENT = "zh_CN.UTF-8";
  };

  # ===== 控制台 =====
  console.keyMap = "us";
  # console.font = "Lat2-Terminus16";

  # ===== 用户 =====
  users.users.root.hashedPassword = "";  # 暂时空密码，安装后修改
  users.users.nixos = {
    isNormalUser = true;
    extraGroups = [ "wheel" "networkmanager" ];
    initialPassword = "changeme";
  };

  # ===== 包管理器 =====
  nix.settings.substituters = [
    "https://mirrors.tuna.tsinghua.edu.cn/nix-channels/store"
    "https://cache.nixos.org"
  ];

  # ===== 基础包 =====
  environment.systemPackages = with pkgs; [
    vim
    git
    curl
    wget
    htop
    tmux
  ];

  # ===== 服务 =====
  services.openssh.enable = true;
  # services.openssh.settings.PermitRootLogin = "no";
  # services.openssh.settings.PasswordAuthentication = false;

  # ===== 安全 =====
  security.sudo.enable = true;
  security.sudo.wheelNeedsPassword = true;

  # ===== 系统版本 =====
  system.stateVersion = "24.11";  # 不要修改
}
```

### 3.7 安装并重启

```bash
# 安装 NixOS
sudo nixos-install

# 设置 root 密码（如果 configuration.nix 中未设置）
# 安装过程会提示

# 重启
reboot

# 登录后用创建的用户登录
# 修改密码
passwd

# 立即更新
sudo nixos-rebuild switch --upgrade
```

---

## 4. configuration.nix 基础语法

### 4.1 配置文件结构

```nix
{ config, lib, pkgs, ... }:        # 函数参数

{
  imports = [                        # 导入其他模块
    ./hardware-configuration.nix
    ./modules/nginx.nix
  ];

  # 所有配置项都是 attribute set
  # 使用 . 访问嵌套属性
  services.nginx.enable = true;

  # 列表
  environment.systemPackages = with pkgs; [
    package1
    package2
  ];
}
```

### 4.2 常用配置项速查

```nix
# ===== 用户 =====
users.users.alice = {
  isNormalUser = true;
  extraGroups = [ "wheel" "docker" ];
  openssh.authorizedKeys.keys = [
    "ssh-ed25519 AAAA..."
  ];
  packages = with pkgs; [
    firefox
  ];
};

# ===== 桌面环境 =====
# GNOME
services.xserver.enable = true;
services.xserver.displayManager.gdm.enable = true;
services.xserver.desktopManager.gnome.enable = true;

# KDE Plasma
services.xserver.enable = true;
services.xserver.displayManager.sddm.enable = true;
services.xserver.desktopManager.plasma5.enable = true;

# 或（NixOS 24.11+）
services.desktopManager.plasma6.enable = true;

# Hyprland
programs.hyprland.enable = true;

# ===== 字体 =====
fonts.packages = with pkgs; [
  noto-fonts
  noto-fonts-cjk-sans
  noto-fonts-emoji
  wqy_microhei
  jetbrains-mono
];

# ===== 中文输入法（Fcitx5）=====
i18n.inputMethod = {
  enabled = "fcitx5";
  fcitx5.addons = with pkgs; [ fcitx5-chinese-addons ];
};

# ===== 声音 =====
# PipeWire（推荐）
services.pipewire.enable = true;
services.pipewire.alsa.enable = true;
services.pipewire.pulse.enable = true;
services.pipewire.jack.enable = true;
# 或 PulseAudio
# hardware.pulseaudio.enable = true;

# ===== 蓝牙 =====
hardware.bluetooth.enable = true;
hardware.bluetooth.powerOnBoot = true;

# ===== 打印机 =====
services.printing.enable = true;
services.avahi.enable = true;
services.avahi.nssmdns = true;
```

---

## 5. nixos-rebuild 命令

### 5.1 基本用法

```bash
# 构建并切换到新配置（最常用）
sudo nixos-rebuild switch

# 构建但不切换（下次重启生效）
sudo nixos-rebuild boot

# 只构建，不改变系统
sudo nixos-rebuild build

# 构建并切换，同时更新 nixpkgs
sudo nixos-rebuild switch --upgrade

# 测试配置（不实际构建）
sudo nixos-rebuild dry-build

# 显示构建计划
sudo nixos-rebuild dry-activate

# 仅构建 VM 镜像
sudo nixos-rebuild build-vm
```

### 5.2 使用 Flakes（推荐）

```bash
# 在配置目录初始化 flake
cd /etc/nixos
sudo nix flake init

# 使用 flake 构建
sudo nixos-rebuild switch --flake /etc/nixos#hostname

# 指定 flake 路径
sudo nixos-rebuild switch --flake github:user/repo#hostname

# 仅构建
nixos-rebuild build --flake .#hostname
```

---

## 6. 代际管理（Generations）

### 6.1 查看代际

```bash
# 列出所有系统代际
sudo nix-env --list-generations --profile /nix/var/nix/profiles/system

# 或
nixos-rebuild list-generations

# 查看当前代际
readlink /run/current-system

# 查看用户代际
nix-env --list-generations
```

### 6.2 回滚

```bash
# 回滚到上一个代际
sudo nixos-rebuild switch --rollback

# 回滚到指定代际
sudo nix-env --switch-generation <N> --profile /nix/var/nix/profiles/system
/run/current-system/bin/switch-to-configuration switch

# 从 GRUB 回滚（启动时选择旧代际）
# 在 GRUB 菜单中选择 "NixOS - Generation X"
```

### 6.3 垃圾回收

```bash
# 删除旧代际（保留最近 N 个）
sudo nix-collect-garbage --delete-older-than 30d

# 清理所有未被引用的路径
sudo nix-collect-garbage -d

# 查看可以删除的空间
nix-store --gc --print-roots

# 彻底清理
sudo nix-store --optimise
sudo nix-collect-garbage
```

---

## 7. Nix 包管理器在其他发行版上的使用

### 7.1 单用户安装

```bash
# 在 Arch/Debian/RHEL 等发行版上安装 Nix
sh <(curl -L https://nixos.org/nix/install) --no-daemon

# 或使用 Determinate Systems 安装脚本（推荐）
curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install

# 验证
nix --version
```

### 7.2 多用户安装（推荐）

```bash
sh <(curl -L https://nixos.org/nix/install) --daemon

# 将用户加入 nix-users 组
sudo usermod -aG nix-users $USER
```

### 7.3 基本使用

```bash
# 搜索包
nix search nixpkgs python

# 临时试用包
nix shell nixpkgs#python3 nixpkgs#nodejs
# 输入 exit 退出

# 用特定包运行命令
nix run nixpkgs#cowsay -- "Hello Nix"

# 安装包到用户 profile
nix profile install nixpkgs#python3

# 删除包
nix profile remove python3

# 查看已安装
nix profile list

# 更新所有
nix profile upgrade '.*'
```

### 7.4 使用 nix-shell 创建临时环境

```bash
# 创建 shell.nix（见 [[../nix/02-Nix语言与flake|Nix 语言与 Flake]]）
nix-shell -p python3 nodejs

# 从文件创建
nix-shell shell.nix
```

---

## 8. 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `error: file 'nixpkgs' was not found` | nixpkgs 通道未配置 | `nix-channel --add https://nixos.org/channels/nixpkgs-unstable nixpkgs` |
| 构建慢/下载慢 | 未使用中国镜像 | 添加 tuna 镜像作为 substituter |
| `disk full in /nix/store` | 旧代际积累过多 | `sudo nix-collect-garbage -d` |
| 安装后无网络 | NetworkManager 未启用 | `networking.networkmanager.enable = true` |
| 字体渲染问题 | 字体配置未写好 | 参见 fonts.packages 配置 |

---

## 9. 推荐工作流

```
初始安装：
  1. 下载 ISO → 分区 → nixos-generate-config
  2. 编辑 configuration.nix → nixos-install

日常维护：
  1. vim /etc/nixos/configuration.nix
  2. sudo nixos-rebuild switch
  3. 如失败 → sudo nixos-rebuild switch --rollback
  4. sudo nix-collect-garbage -d（定期）

版本管理：
  1. 将 /etc/nixos/ 目录纳入 git
  2. 每次更改前 git commit
  3. 勇敢实验，随时回滚
```

---

## 10. 相关资源

- NixOS 手册: https://nixos.org/manual/nixos/stable/
- NixOS Wiki: https://nixos.wiki/
- Nix Pills: https://nixos.org/guides/nix-pills/
- NixOS 选项搜索: https://search.nixos.org/options
- 清华大学 Nix 镜像: https://mirrors.tuna.tsinghua.edu.cn/nix/
- [[../nix/02-Nix语言与flake|Nix 语言与 Flake]]
- [[../nix/03-nixpkgs与包管理|nixpkgs 与包管理]]
- [[../arch/01-安装指南|Arch Linux 安装]]
- [[../debian/02-Debian安装与服务器配置|Debian 安装]]
