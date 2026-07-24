---
tags:
  - diy
  - 树莓派
  - archlinux
  - gnome
  - 触屏
created: 2026-06-12
---

# DIY 触屏平板试验版 — Arch Linux + GNOME 全流程指南

## 物品清单

| 部件 | 型号 / 规格 | 预计价格 | 购买渠道 |
|------|-----------|---------|---------|
| SBC 主板 | Raspberry Pi 4B 2GB 二手 | ¥160-200 | 闲鱼 |
| 显示屏 | 4.3 寸 HDMI IPS 800×480 + 电容触控 | ¥80-110 | 淘宝 |
| MicroSD 卡 | SanDisk Ultra 32GB A1 | ¥22 | 京东 / 淘宝 |
| 电源 | 任意 5V 2.5A 手机充电头 + USB-A 转 USB-C 数据线 | ¥0（用家里现成的） | — |
| 散热 | 小铝散热片 | ¥4 | 淘宝 |
| **总预算** | | **¥266-336** | |

---

## 1. 硬件接线

### 1.0 总体架构

```mermaid
graph TB
    subgraph 供电链路
        AC[🏠 220V 交流电<br/>家用插座] -->|USB 充电头| USBC[USB-C 5V 3A]
    end

    subgraph 树莓派 4B
        PWR[USB-C 电源口]
        HDMI[micro-HDMI 口]
        USB[USB-A 口]
        GPIO[GPIO 排针]
        CPU[BCM2711<br/>4×A72]
        GPU[VideoCore VI<br/>V3D 开源驱动]
    end

    subgraph 4.3寸触屏控制板
        HDMI_IN[HDMI 输入口]
        TOUCH[Micro-USB 触摸口]
        PWR_IN[5V 供电端子]
        LCD[800×480 IPS LCD]
        TP[电容触摸层]
    end

    AC --> USBC
    USBC -->|供电 1| PWR
    GPIO -->|Pin 4 5V<br/>Pin 6 GND| PWR_IN
    HDMI -->|HDMI 信号| HDMI_IN
    USB -->|USB HID 触控数据| TOUCH
    PWR --> CPU
    CPU --> GPU
    HDMI_IN --> LCD
    TOUCH --> TP
    LCD --> TP

    style AC fill:#ff6b35,color:#fff
    style USBC fill:#2ecc71,color:#fff
    style Pi fill:#c0392b,color:#fff
    style 屏幕 fill:#3498db,color:#fff
```

### 1.1 详细接线对照

```mermaid
graph LR
    subgraph Pi[树莓派 4B]
        direction TB
        P1[micro-HDMI]
        P2[USB-A]
        P3["GPIO Pin 4<br/>(5V 供电)"]
        P4["GPIO Pin 6<br/>(GND 地线)"]
        P5["USB-C<br/>(主板供电)"]
    end

    subgraph Screen[4.3 寸触屏控制板]
        direction TB
        S1[HDMI 输入口]
        S2["Micro-USB<br/>(触摸数据口)"]
        S3["5V 输入<br/>供电端子"]
        S4["GND<br/>接地端子"]
    end

    subgraph Power[电源]
        direction TB
        PW1[手机充电头<br/>AC→DC 5V]
        PW2[220V 交流插座]
    end

    P1 -.->|"HDMI 信号线"| S1
    P2 -.->|"USB 触控线"| S2
    P3 -.->|"杜邦线 (红)"| S3
    P4 -.->|"杜邦线 (黑)"| S4
    P5 -.->|"USB-C 数据线"| PW1
    PW1 -.->|"插头"| PW2

    style Pi fill:#2c3e50,color:#fff
    style Screen fill:#34495e,color:#fff
    style Power fill:#16a085,color:#fff
```

### 1.2 GPIO 供电接脚位置

| 功能 | GPIO 编号 | 物理 Pin | 线色 |
|------|----------|----------|------|
| 5V 输出 | — | Pin 4 | 🔴 红 |
| GND | — | Pin 6 | ⚫ 黑 |

> [!warning] GPIO 接线注意
> GPIO Pin 4/6 在排针的同一列、紧挨着（外列上端第 2、3 个）。**务必确认 Pin 编号再接线，接错 5V/GND 会烧屏。**

> [!note] 接线提示
> - 4.3 寸屏功耗约 2-3W，建议从 GPIO 取 5V 供电（Pin 4/6），不要和 Pi 共用同一个 USB 口
> - Pi 4B 的 micro-HDMI 口比较挑线，买屏时确认商家附带 micro-HDMI 转 HDMI 线，或自备
> - 如屏幕触控不走 USB 而走 I²C（少见），需要额外接 SDA/SCL

---

## 2. 安装总览流程

```mermaid
flowchart TD
    A["下单收件<br/>Pi 4B + 屏 + SD"] --> B["1️⃣ 硬件接线<br/>GPIO/HDMI/USB"]
    B --> C["2️⃣ 烧录系统<br/>SD 卡分区+写入"]
    C --> D["3️⃣ 上电 + SSH 登录<br/>首次启动配置"]
    D --> E["4️⃣ GPU 驱动<br/>config.txt 改显示"]
    E --> F["5️⃣ 安装 GNOME<br/>pacman 拉桌面"]
    F --> G["6️⃣ 触屏调优<br/>onboard + libinput"]
    G --> H["7️⃣ 美化 & 省电<br/>主题 + ZRAM + powertop"]
    H --> I["✅ 跑验机脚本<br/>check.sh 全验证"]

    style A fill:#e67e22,color:#fff
    style B fill:#e74c3c,color:#fff
    style C fill:#9b59b6,color:#fff
    style D fill:#3498db,color:#fff
    style E fill:#2ecc71,color:#fff
    style F fill:#1abc9c,color:#fff
    style G fill:#f39c12,color:#fff
    style H fill:#e91e63,color:#fff
    style I fill:#27ae60,color:#fff
```

---

## 3. 烧录 Arch Linux ARM

### 3.1 下载镜像

```bash
# 在另一台电脑上操作，下载 aarch64 镜像
curl -LO http://os.archlinuxarm.org/os/ArchLinuxARM-rpi-aarch64-latest.tar.gz
```

### 3.2 分区 MicroSD

```bash
DEV=/dev/sdX          # 替换为你的 SD 卡设备名（lsblk 确认）

# 清除分区表
sudo sgdisk --zap-all $DEV

# 创建分区: 200M fat16 启动分区 + 剩余 ext4 根分区
sudo parted -s $DEV mklabel msdos
sudo parted -s $DEV mkpart primary fat16 1MiB 201MiB
sudo parted -s $DEV mkpart primary ext4 201MiB 100%
sudo parted -s $DEV set 1 boot on

# 格式化
sudo mkfs.vfat -F16 ${DEV}1
sudo mkfs.ext4 -F ${DEV}2
```

### 3.3 写入系统

```bash
ROOTFS=/mnt/root
BOOTFS=/mnt/boot

sudo mount ${DEV}2 $ROOTFS
sudo mkdir -p $BOOTFS
sudo mount ${DEV}1 $BOOTFS

# 解压 Arch ARM 镜像
sudo bsdtar -xpf ArchLinuxARM-rpi-aarch64-latest.tar.gz -C $ROOTFS

# 移动 boot 文件
sudo mv $ROOTFS/boot/* $BOOTFS/

sync
sudo umount $BOOTFS $ROOTFS
```

---

## 4. 首次启动与基础配置

### 4.1 启动

将 SD 卡插入 Pi 4B，插上屏幕和键盘（USB），上电。

> **首次开机可能黑屏 **— 4.3" 屏幕分辨率非标准，先接大显示器或 SSH 配置。

### 4.2 SSH 登录（推荐）

```bash
# Pi 默认通过 DHCP 获取 IP，路由器后台查 IP 或用:
ssh alarm@<树莓派IP>

# 默认账号密码
# 用户名: alarm
# 密码:   alarm
# root 密码: root
```

### 4.3 初始化

```bash
# 切换到 root
su -

# 初始化 pacman 密钥环
pacman-key --init
pacman-key --populate archlinuxarm

# 更新系统
pacman -Syu --noconfirm

# 设置时区
timedatectl set-timezone Asia/Shanghai

# 设置 hostname
echo "diytablet" > /etc/hostname
echo "127.0.1.1 diytablet.localdomain diytablet" >> /etc/hosts

# 创建你自己的用户
useradd -m -G wheel -s /bin/bash <你的用户名>
passwd <你的用户名>

# 安装 sudo
pacman -S --noconfirm sudo
echo "%wheel ALL=(ALL: ALL) ALL" >> /etc/sudoers.d/wheel

# 安装 yay（AUR 助手）
pacman -S --noconfirm git base-devel
# 切换到你的用户登录
su - <你的用户名>
git clone https://aur.archlinux.org/yay-bin.git /tmp/yay-bin
cd /tmp/yay-bin && makepkg -si --noconfirm
```

---

## 5. GPU 与显示配置

### 5.1 强制 HDMI 输出 + GPU 加速

编辑 `/boot/config.txt`:

```ini
# GPU 加速
dtoverlay=vc4-kms-v3d
gpu_mem=64

# 强制 HDMI 输出（4.3 寸屏需要）
hdmi_force_hotplug=1
hdmi_group=2
hdmi_mode=87

# 4.3 寸屏固定 800x480
hdmi_cvt=800 480 60 6 0 0 0
framebuffer_width=800
framebuffer_height=480

# 关闭省电灰屏
consoleblank=0

# 提高一点 GPU 频率（可选，小屏的桌面渲染很轻）
# over_voltage=2
# arm_freq=1800

# 关闭不用的接口省电
dtparam=audio=on
disable_overscan=1

# SPI 开启（后期给副屏用）
dtparam=spi=on
```

> **解释:**
> - `vc4-kms-v3d`: 开源 Vulkan/OpenGL 驱动，GNOME 动画和 osu!lazer 全靠它
> - `hdmi_cvt`: 生成 800x480 的 CVT 模式，4.3 寸屏没有 EDID，需要手动注入分辨率
> - `gpu_mem=64`: GNOME 够用，多了浪费 2GB 内存

---

## 6. 安装 GNOME

### 6.0 软件栈 — 触控数据如何到达桌面

```mermaid
flowchart TD
    subgraph Hardware[硬件层]
        TP[电容触摸面板]
        LCD[LCD 显示面板]
    end

    subgraph Kernel[内核驱动层]
        USB_HID["USB HID 驱动
hid_multitouch"]
        HDMI["HDMI 显示驱动
vc4-kms-v3d"]
    end

    subgraph Input[输入抽象层]
        LIBINPUT["libinput
触控事件标准化"]
        MESA["Mesa 3D
Vulkan/OpenGL"]
    end

    subgraph Display[显示服务层]
        WAYLAND["Wayland Compositor
Mutter"]
        OSK["虚拟键盘
onboard"]
    end

    subgraph App[应用层]
        GNOME_SHELL[GNOME Shell 桌面]
        APPS[Firefox / Inkscape / osu!]
    end

    TP -->|手指坐标| USB_HID
    USB_HID -->|evdev 事件| LIBINPUT
    LIBINPUT -->|标准化事件| WAYLAND
    WAYLAND -->|渲染合成| GNOME_SHELL
    WAYLAND -->|转发点击| APPS
    MESA -->|GPU 渲染| WAYLAND
    WAYLAND -->|帧缓冲| HDMI
    HDMI -->|显示| LCD

    style TP fill:#e74c3c,color:#fff
    style LCD fill:#3498db,color:#fff
    style USB_HID fill:#9b59b6,color:#fff
    style LIBINPUT fill:#2ecc71,color:#fff
    style WAYLAND fill:#e67e22,color:#fff
```

安装 GNOME 桌面环境:

```bash
sudo pacman -S --noconfirm \
  gnome \
  gnome-tweaks \
  networkmanager \
  xdg-user-dirs

sudo systemctl enable gdm
sudo systemctl enable NetworkManager
sudo systemctl start NetworkManager
```

### 6.1 第一次进桌面

```bash
sudo reboot
```

启动后 GDM 应该出现在屏幕上。用触摸屏登录。

### 6.2 卸载不需要的 GNOME 软件（省空间、省内存）

```bash
sudo pacman -Rns --noconfirm \
  gnome-contacts \
  gnome-maps \
  gnome-weather \
  gnome-clocks \
  totem \
  epiphany \
  gnome-calendar \
  gnome-boxes \
  evolution-data-server
```

---

## 7. 触屏调优

### 7.1 确认触屏被识别

```bash
sudo pacman -S --noconfirm libinput
sudo libinput list-devices | grep -A 20 -i touch
```

如果看到 "Touchscreen" 设备，说明已识别。

### 7.2 GNOME 触屏设置

```bash
# 自动旋转（需要传感器数据，试验版先跳过，固定横屏）
# 后期配 iio-sensor-proxy

# 在 GNOME 设置里手动:
# Settings → Accessibility → Typing
# 关闭 "Screen Keyboard"（中文输入后面单独配）
```

### 7.3 安装更好的屏幕键盘

GNOME 自带的 OSK 中文支持很差。安装 onboard:

```bash
sudo pacman -S --noconfirm onboard
# 设置开机自启
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/onboard.desktop << EOF
[Desktop Entry]
Type=Application
Name=Onboard
Exec=onboard
X-GNOME-Autostart-enabled=true
NoDisplay=true
EOF
```

### 7.4 ZRAM 内存压缩（2GB 救急措施）

```bash
sudo pacman -S --noconfirm zram-generator

sudo tee /etc/systemd/zram-generator.conf << EOF
[zram0]
zram-size = 512
compression-algorithm = zstd
EOF

sudo systemctl daemon-reload
sudo systemctl start systemd-zram-setup@zram0.service
```

---

## 8. 高性能配置

### 8.1 安装 Firefox（触屏优化版）

```bash
sudo pacman -S --noconfirm firefox
# 在 about:config 里设置:
# dom.w3c_touch_events.enabled = 1
```

### 8.2 美化 GNOME 桌面

```bash
# 安装扩展
sudo pacman -S --noconfirm gnome-shell-extensions

# 安装图标和主题
yay -S --noconfirm orchis-theme-git tela-icon-theme-git

# 装好后在 gnome-tweaks 里切换主题
# 或在命令行设置:
gsettings set org.gnome.desktop.interface gtk-theme "Orchis-Dark"
gsettings set org.gnome.desktop.interface icon-theme "Tela-dark"
gsettings set org.gnome.shell.extensions.user-theme name "Orchis-Dark"
```

### 8.3 省电调优

```bash
sudo pacman -S --noconfirm powertop

# 安装 systemd 自动优化服务
sudo tee /etc/systemd/system/powertop.service << EOF
[Unit]
Description=PowerTOP auto tune

[Service]
Type=oneshot
ExecStart=/usr/sbin/powertop --auto-tune

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable powertop
```

---

## 9. 验机脚本

装完后跑这个脚本验证一切正常:

```bash
#!/bin/bash
echo "=== 系统信息 ==="
uname -a
cat /etc/os-release | head -5

echo -e "\n=== GPU 状态 ==="
dmesg | grep -i vc4 | head -5
glxinfo | grep -i "renderer" 2>/dev/null || echo "(需安装 mesa-utils)"

echo -e "\n=== 触屏设备 ==="
sudo libinput list-devices 2>/dev/null | grep -A 5 -i touch || echo "未检测到触屏"

echo -e "\n=== 内存 ==="
free -h
zramctl 2>/dev/null || echo "(zram 未启用)"

echo -e "\n=== 存储 ==="
df -h /
echo

echo "=== 所有验证完成 ==="
```

保存为 `~/check.sh`，`chmod +x ~/check.sh`，然后 `./check.sh`。

---

## 10. 从试验版升级到正式版

### 10.0 正式版目标架构

```mermaid
graph TB
    subgraph 供电
        PB["10000mAh PD 充电宝
15W 输出"]
    end

    subgraph 核心[树莓派 5]
        P5[Pi 5 4GB/8GB]
        NVME["128GB NVMe SSD
M.2 插槽"]
    end

    subgraph 主屏
        MAIN["10.1 寸 IPS 1280×800
电容触控"]
    end

    subgraph 副屏[背部副屏]
        SPI[SPI 总线]
        SUB["1.28 寸圆形 LCD 240×240
GC9A01 驱动"]
        ANIM["循环播放 GIF 动画
ffmpeg + framebuffer"]
    end

    subgraph 外设
        WACOM["外接 Wacom 绘图板
USB / 蓝牙"]
        KB["蓝牙键盘"]
    end

    PB -->|USB-C PD 5V| P5
    P5 -->|micro-HDMI| MAIN
    P5 -->|USB| MAIN
    P5 --> SPI
    SPI --> SUB
    SUB --> ANIM
    P5 --> NVME
    WACOM -.->|需要矢量绘图时连接| P5
    KB -.->|需要打字时连接| P5

    style P5 fill:#c0392b,color:#fff
    style MAIN fill:#2980b9,color:#fff
    style SUB fill:#8e44ad,color:#fff
    style NVME fill:#27ae60,color:#fff
    style PB fill:#f39c12,color:#fff
```

### 10.1 硬件对比

| 部件 | 试验版 | 正式版 |
|------|--------|--------|
| SBC | Pi 4B 2GB | Pi 5 4GB / 8GB |
| 主屏 | 4.3" 800×480 | 10.1" 1280×800 + 电容触控 |
| 存储 | 32GB SD | 128GB NVMe SSD（Pi 5 M.2 槽） |
| 副屏 | — | 1.28" 圆形 LCD (GC9A01, SPI) |
| 电源 | 充电头 | 10000mAh PD 充电宝 |
| 外壳 | 裸奔 | 3D 打印 PETG |

软件配置 **完全复用**，SD 卡拔过去直接启动。

---

## 11. 故障排除

### 黑屏

1. 确认 HDMI 线兼容（Pi 4B micro-HDMI ≠ 普通 micro-HDMI）
2. 编辑 `/boot/config.txt` 加 `hdmi_safe=1` 临时安全模式启动
3. SSH 进去看 `dmesg | grep -i hdmi`

### 触屏没反应

```bash
# 查看 USB 设备
lsusb

# 应该有一行类似:
# Bus 001 Device 003: ID 0eef:0005 D-WAV Scientific Co., Ltd eGalaxTouch

# 查看 evdev 事件
sudo evtest
# 选触屏设备编号，看移动手指是否有事件输出
```

### GNOME 启动慢 / 内存不足

```bash
# 换成 Xfce 轻量桌面（保底方案）
sudo pacman -S --noconfirm xfce4 xfce4-goodies lightdm lightdm-gtk-greeter
sudo pacman -Rns --noconfirm gnome gnome-tweaks gdm
sudo systemctl enable lightdm
sudo reboot
```

### 供电不足随机重启

```bash
# 查看核心电压
vcgencmd get_throttled

# 如果 bit 0 为 1，说明供电不足
# 换 5V 3A 充电头
# 如果还不行，从充电头直供 Pi，屏幕从 Pi 的 GPIO 取电改为外接独立电源
```

---

## 附: WiFi 配置（无键盘时）

```bash
sudo pacman -S --noconfirm iwd
sudo systemctl enable iwd
sudo systemctl start iwd

# 在 /etc/iwd/main.conf:
# [General]
# EnableNetworkConfiguration=true

# 进入 iwctl 交互式连接:
iwctl
station wlan0 scan
station wlan0 get-networks
station wlan0 connect <SSID>
```

---

**完成后，你拥有:**
- 一台 4.3 寸 Arch Linux ARM 平板
- GNOME 触屏桌面
- GPU 加速 + 屏幕键盘
- 内存压缩 + 省电调优
- 可以开始写副屏驱动、美化主题、装 Linux 绘图工具
