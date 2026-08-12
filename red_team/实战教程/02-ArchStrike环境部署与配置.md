# 02 — ArchStrike 环境部署与配置

> **前言**：你有一台装了物理 Arch Linux 的备用笔记本。现在要把它武装成红队武器。不是虚拟机，不是 Docker 套娃——就是裸金属安装。上来就练。


## Part 2: AUR 帮手工具 — yay

很多红队工具不在官方源或 ArchStrike 中，需要从 AUR（Arch User Repository）安装。`yay` 是目前最流行的 AUR helper。

```bash
sudo pacman -S --needed git base-devel
```

**预期输出**：安装 `git`, `gcc`, `make`, `fakeroot` 等基础编译工具。这些 `/usr/bin` 下的东西已经在物理系统上跑，不是容器。

```bash
git clone https://aur.archlinux.org/yay-bin.git /tmp/yay
cd /tmp/yay && makepkg -si
```

**预期输出**：

```
==> Making package: yay-bin 12.x.x ...
==> Checking runtime dependencies...
==> Checking buildtime dependencies...
==> Retrieving sources...
==> Validating source files...
==> Extracting sources...
==> Starting build()...
==> Entering fakeroot environment...
==> Starting package()...
==> Finished making: yay-bin 12.x.x ...
==> Installing package yay-bin...
```

**故障排查**：

| 症状 | 原因 | 解决 |
|---|---|---|
| `base-devel` 装不上 | 存在依赖冲突 | 先 `sudo pacman -Syu` 完成系统更新再装 |
| `makepkg` 报错 `fakeroot` 找不到 | 未装 base-devel | 先执行本条第一个命令 |
| `git clone` 失败 | GitHub 在国内被干扰 | 开代理，或者在 `/etc/hosts` 中添加 GitHub 的可用 IP，或者用 gitee 镜像 |
| AUR 包编译到一半失败 | 缺少依赖 | 看报错信息，一般会是 `Missing dependencies: xxx`，按提示先 `yay -S xxx` |


## Part 4: Rust 红队工具链

Rust 工具速度碾压传统工具。物理机上能跑出真实性能，不是被虚拟化层阉割过的。

### 4.1 安装 Rust

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

**预期输出**：

```
Current installation options:

 default host triple: x86_64-unknown-linux-gnu
 default toolchain: stable

1) Proceed with standard installation (default)
2) Customize installation
3) Cancel installation
> 1
```

选 `1` 回车，安装完后：

```bash
source $HOME/.cargo/env
```

验证：

```bash
rustc --version
```

**预期输出**：

```
rustc 1.8x.x (xxxxxxxxx 20xx-xx-xx)
```

### 4.2 Cargo 安装 Rust 红队工具

```bash
cargo install rustscan
```

**预期输出**：

```
 Compiling rustscan v2.x.x
 …
 Finished release [optimized] target(s) in Xm XXs
 Installing ~/.cargo/bin/rustscan
```

会编译几分钟。`cargo install` 是从源码编译的，不是下载二进制——所以耐心等。

```bash
cargo install feroxbuster
```

Feroxbuster 是 Rust 版目录爆破器，递归、多线程、快。

```bash
cargo install x8
```

`x8` — 高速目录/参数模糊测试工具。

```bash
cargo install subxtract
```

`subxtract` — 子域名枚举器。

### 4.3 AUR 中的 Rust 工具

```bash
yay -S ripgrep
```

**预期输出**：

```
:: Proceed with installation? [Y/n] y
…
Installing ripgrep...
```

`ripgrep`（命令名 `rg`）比 GNU grep 快 10 倍以上，适合搜索大文件/日志。

```bash
yay -S fd
```

`fd` — 比 `find` 快很多，语法更友好。

### 4.4 Cargo 编译失败排查

| 症状 | 原因 | 解决 |
|---|---|---|
| `error: linker 'cc' not found` | 缺少 C 编译器 | `sudo pacman -S gcc` |
| `= note: /usr/bin/ld: cannot find -lxxx` | 缺少 C 开发库 | 看 `-l` 后面的名字，例如 `-lssl` → `sudo pacman -S openssl`；`-lz` → `sudo pacman -S zlib` |
| `Killed` 后退出 | OOM — 内存不足 | 物理机内存 < 4GB 时编译大项目可能触发 OOM Killer。关掉不必要的程序，或加 swap |


## Part 6: 外接设备驱动

物理机比虚拟机唯一的绝对优势就在这里：**直通硬件**。

### 6.1 无线网卡芯片组驱动

**推荐购买的无线网卡型号**（支持 monitor mode + packet injection）：

| 型号 | 芯片 | 频段 | 接口 | 推荐度 |
|---|---|---|---|---|
| Alfa AWUS036ACH | RTL8812AU | 2.4G + 5G | USB 3.0 | |
| Alfa AWUS036H | RTL8187L | 2.4G | USB 2.0 | （老） |
| Alfa AWUS1900 | RTL8814AU | 2.4G + 5G | USB 3.0 | |
| Panda PAU09 | RTL8812AU | 2.4G + 5G | USB 2.0 | （便宜） |

安装对应驱动：

```bash
# RTL8812AU (适用于 Alfa AWUS036ACH / Panda PAU09)
yay -S rtl8812au-dkms-git

# RTL8187 (适用于 Alfa AWUS036H，内核自带但需安装固件)
sudo pacman -S rtl8187
```

**预期输出**（yay 编译驱动时）：

```
==> Making package: rtl8812au-dkms-git ...
==> Installing module rtl8812au...
DKMS: install completed.
```

装完后插上网卡，验证：

```bash
lsusb | grep -i realtek
iwconfig
```

**预期输出**：`iwconfig` 中应出现 `wlanX` 接口，例如 `wlan1`。

检查是否支持监听模式：

```bash
sudo airmon-ng start wlan1
```

**预期输出**：

```
PHY Interface Driver Chipset
phy1 wlan1mon rtl8812au Realtek RTL8812AU
```

如果看到 `wlan1mon` 说明监听模式启用成功。

> **物理机唯一注意**：笔记本 **内置网卡**（通常是 Intel 的）90% 不支持包注入。必须外接 USB 无线网卡。不要拿内置网卡尝试 WPA 破解——它只能监听，不能注入 deauth 包。

### 6.2 蓝牙工具

```bash
sudo pacman -S bluez bluez-utils
```

启动蓝牙服务：

```bash
sudo systemctl enable --now bluetooth
```

```bash
sudo pacman -S bettercap
```

Bettercap 支持 BLE（低功耗蓝牙）侦察。启动 BLE 扫描：

```bash
sudo bettercap -eval "ble.recon on"
```

> **物理机好处**：笔记本电脑内置蓝牙可以直接用于 BLE 攻击，不需要外接硬件。

### 6.3 USB 串口（硬件入侵用）

```bash
sudo pacman -S minicom screen picocom
```

- `minicom` / `picocom` — 串口终端
- `screen` — 也支持串口连接：`screen /dev/ttyUSB0 115200`

```bash
sudo pacman -S flashrom
```

- `flashrom` — SPI 闪存读写工具，BIOS/UEFI 固件提取与刷写

> **需要硬件**：CH341A 编程器 + SOP8 测试夹。这不是软件能解决的。

### 6.4 SDR（软件定义无线电）

```bash
sudo pacman -S gnuradio gr-osmosdr
yay -S rtl-sdr gqrx urh
```

**预期的包内容**：
- `gnuradio` — SDR 信号处理框架
- `gqrx` — SDR 频谱分析 GUI
- `urh` — Universal Radio Hacker，信号逆向/重放
- `rtl-sdr` — RTL2832U 芯片驱动（常见 USB 电视棒改装 SDR）

推荐硬件：RTL-SDR Blog V3 或 V4（淘宝约 200 元人民币）。


## Part 8: 可选 — Docker 靶场

如果想在本地跑 Web 漏洞靶场（不需要互联网）：

```bash
sudo pacman -S docker docker-compose docker-buildx
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

**重新登录后**，拉取并运行常见靶场：

```bash
# DVWA — Damn Vulnerable Web Application
docker run -d -p 80:80 vulnerables/web-dvwa

# Juice Shop — OWASP 现代 Web 靶场
docker run -d -p 3000:3000 bkimminich/juice-shop

# WebGoat — OWASP 官方教学靶场
docker run -d -p 8080:8080 webgoat/goatandwolf
```

**预期输出**（每个 `docker run`）：

```
Unable to find image 'xxx:latest' locally
latest: Pulling from xxx
…
Status: Downloaded newer image for xxx:latest
<container_id>
```

访问：
- DVWA → `http://localhost`
- Juice Shop → `http://localhost:3000`
- WebGoat → `http://localhost:8080/WebGoat`

> **物理机注意**：Docker 靶场直接曝光在 `localhost` 上，对外不可达（除非你手动发布到 `0.0.0.0`）。练习时如果笔记本连着公网，确保不要用 `-p 0.0.0.0:80:80` 这种写法。


## 附录 A: 快速问题排查索引

| 问题 | 章节 |
|---|---|
| `pacman -S archstrike` 找不到包 | Part 1.1 — 仓库配置 |
| GPG 签名错误 | Part 1.2 — 密钥导入 |
| AUR 包编译失败 | Part 2 — yay 安装 + 缺少 base-devel |
| Metasploit 启动慢/数据库连不上 | Part 3.2 — msfdb init |
| Rust工具安装卡死/被kill | Part 4.4 — 内存不足/OOM |
| pip 拒绝在系统路径安装 | Part 5.3 — 必须用 venv |
| 无线网卡不能注入 | Part 6.1 — 内置网卡不行，换外接 |
| 串口设备 permission denied | Part 7.1 — 未加入 uucp 组且未重新登录 |
| masscan 扫描速度不理想 | Part 7.2 — 网络缓冲区未调整 |

## 附录 B: 物理机独有要点总结

1. **不要用 root**：Wi-Fi 工具需要 `root` 但日常工作用普通用户
2. **组变更需要重新登录**：`usermod -aG` 不是立即生效
3. **时刻注意你的网络边界**：不要对内网或公网未授权目标进行测试
4. **硬件直通才是物理意义**：无线、SDR、USB 串口——这些虚拟机干不了
5. **备份 `/etc/pacman.conf`** 再改仓库配置
6. **编译工具会占满 CPU**：`cargo install` 和 `makepkg` 期间笔记本风扇会狂转，正常现象
7. **磁盘空间**：全套装完大约占用 30-50 GB，确保分区有空间
