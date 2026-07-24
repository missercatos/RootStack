# 39 - PipeWire 与 WirePlumber 详解

> PipeWire 是 Linux 新一代多媒体框架，统一了音频、视频和 MIDI 处理，取代了 PulseAudio 和 JACK。WirePlumber 作为其默认会话管理器，通过 Lua 脚本引擎提供灵活的设备策略和路由管理。本章将深入解析 PipeWire 的架构设计、配置优化、WirePlumber 策略引擎、蓝牙音频、专业音频工作流及常见问题排查。

---

## 39.1 Linux 多媒体管道历史

```
1992        2002        2004         2009          2017
 │           │           │            │             │
 ▼           ▼           ▼            ▼             ▼
OSS ──────► ALSA ──────► ALSA ──────► PulseAudio ──► PipeWire
(内核音频)   (取代 OSS)   + JACK       (桌面音频)     (统一一切)
                         (专业音频)    + JACK
                                      (仍然独立)
```

| 时代 | 系统 | 定位 | 局限 |
|------|------|------|------|
| 1992 | OSS | 内核音频接口 | 独占设备、不支持混音 |
| 2002 | ALSA | 取代 OSS | 用户空间 API 复杂、混音需 dmix |
| 2004 | JACK | 专业低延迟音频 | 不适合桌面、配置复杂 |
| 2004 | PulseAudio | 桌面音频服务器 | 延迟较高、不支持视频/MIDI |
| 2017 | PipeWire | 统一音频+视频+MIDI | 仍在快速发展 |

PipeWire 的目标是 **一个框架替代所有**：

```
┌──────────────────────────────────────────────────┐
│                   PipeWire                        │
│  ┌──────────────┬───────────────┬──────────────┐  │
│  │  音频处理     │   视频处理     │  MIDI 处理   │  │
│  │  (替代       │   (屏幕共享    │  (替代       │  │
│  │   PulseAudio │    摄像头)     │   JACK MIDI) │  │
│  │   + JACK)    │               │              │  │
│  └──────────────┴───────────────┴──────────────┘  │
│  ┌──────────────────────────────────────────────┐  │
│  │          兼容层                                │  │
│  │  pipewire-pulse │ pipewire-jack │ pipewire-alsa │
│  └──────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

---

## 39.2 PipeWire 架构

### 核心设计理念

PipeWire 采用 **图模型（Graph Model）**，所有音视频处理抽象为节点和链接：

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Source   │────►│ Filter   │────►│  Sink    │
│  (输入)   │     │ (处理)   │     │ (输出)   │
│          │     │          │     │          │
│ [out_FL] │────►│[in] [out]│────►│ [in_FL]  │
│ [out_FR] │────►│[in] [out]│────►│ [in_FR]  │
└──────────┘     └──────────┘     └──────────┘
   节点              节点             节点
        链接              链接
```

核心概念：

| 概念 | 说明 |
|------|------|
| Node（节点） | 处理单元（音频源、音频汇、滤波器） |
| Port（端口） | 节点的输入/输出连接点 |
| Link（链接） | 连接两个端口 |
| Client（客户端） | 连接到 PipeWire 的应用 |
| Device（设备） | 硬件或虚拟设备 |
| Factory（工厂） | 创建节点等对象的工厂 |

### 模块化架构

```
┌─────────────────────────────────────────────┐
│              PipeWire Daemon                 │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  │
│  │  Core    │  │ Modules  │  │  SPA      │  │
│  │  (核心)  │  │ (模块)   │  │  Plugins  │  │
│  └──────────┘  └──────────┘  └───────────┘  │
│                                              │
│  模块:                     SPA 插件:          │
│  - module-rt              - alsa             │
│  - module-protocol-native - v4l2             │
│  - module-client-node     - bluez5           │
│  - module-adapter         - audiomixer       │
│  - module-metadata        - audioconvert     │
│  - module-session-manager - audiotestsrc     │
│  - module-filter-chain    - videotestsrc     │
└─────────────────────────────────────────────┘
```

SPA（Simple Plugin API）是 PipeWire 的插件框架，提供硬件抽象和数据处理：

```bash
# 列出 SPA 插件
ls /usr/lib/spa-0.2/
# alsa/  audiomixer/  audioconvert/  audiotestsrc/
# bluez5/  control/  support/  v4l2/  videotestsrc/  vulkan/
```

### 兼容层

#### pipewire-pulse（PulseAudio 兼容）

```bash
# 安装
sudo pacman -S pipewire-pulse

# 验证 PulseAudio 兼容
pactl info
# Server Name: PipWire Pulse

# 所有 PulseAudio 工具（pactl、pavucontrol 等）无缝工作
pactl list sinks short
pactl set-sink-volume @DEFAULT_SINK@ 80%
```

#### pipewire-jack（JACK 兼容）

```bash
# 安装
sudo pacman -S pipewire-jack

# 使用 JACK 应用
# 方法 1：LD 预载（推荐）
pw-jack ardour
pw-jack carla
pw-jack guitarix

# 方法 2：全局替代
# 安装 pipewire-jack 后 /usr/lib/pipewire-0.3/jack/ 下有替代库
# 设置 LD_LIBRARY_PATH（不推荐全局使用）

# 验证
pw-jack jack_lsp
```

#### pipewire-alsa（ALSA 兼容）

```bash
# 安装
sudo pacman -S pipewire-alsa

# ALSA 应用自动路由到 PipeWire
aplay -l           # 列出设备
aplay test.wav     # 播放

# /etc/alsa/conf.d/ 中的配置将 ALSA 重定向到 PipeWire
cat /etc/alsa/conf.d/50-pipewire.conf
```

---

## 39.3 PipeWire 安装与配置

### Arch Linux 安装方案

```bash
# 基础安装
sudo pacman -S pipewire pipewire-audio

# pipewire-audio 是元包，包含：
# - pipewire-alsa
# - pipewire-jack
# - pipewire-pulse
# - wireplumber（会话管理器）

# 图形化音量控制
sudo pacman -S pavucontrol     # PulseAudio 前端（通过兼容层工作）

# 额外工具
sudo pacman -S helvum          # 图形化节点连接管理器
sudo pacman -S qpwgraph        # 另一个图形化管理器

# 启动服务（systemd user service）
systemctl --user enable --now pipewire.socket
systemctl --user enable --now pipewire-pulse.socket
systemctl --user enable --now wireplumber.service

# 检查状态
systemctl --user status pipewire
systemctl --user status pipewire-pulse
systemctl --user status wireplumber
```

### 配置文件结构

```
/usr/share/pipewire/              ← 默认配置（不要修改）
├── pipewire.conf
├── pipewire-pulse.conf
├── client.conf
├── client-rt.conf
├── jack.conf
├── minimal.conf
└── pipewire.conf.avail/
    ├── 10-rates.conf
    └── ...

~/.config/pipewire/               ← 用户覆盖配置
├── pipewire.conf.d/              ← 片段式覆盖（推荐）
│   └── 10-custom.conf
├── pipewire-pulse.conf.d/
│   └── 10-custom.conf
├── client.conf.d/
│   └── 10-custom.conf
└── client-rt.conf.d/
    └── 10-custom.conf
```

重要原则：**不要直接复制和修改主配置文件**，使用 `.conf.d/` 目录下的片段文件进行覆盖。

### pipewire.conf 核心参数

```bash
# 查看当前生效配置
pw-dump | jq '.[0].info.props'

# 查看默认配置
cat /usr/share/pipewire/pipewire.conf
```

```json5
// ~/.config/pipewire/pipewire.conf.d/10-custom.conf
context.properties = {
    default.clock.rate          = 48000
    default.clock.allowed-rates = [ 44100 48000 96000 ]
    default.clock.quantum       = 1024
    default.clock.min-quantum   = 32
    default.clock.max-quantum   = 2048
    default.clock.force-quantum = 0
}
```

### 音频配置参数详解

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `default.clock.rate` | 48000 | 默认采样率（Hz） |
| `default.clock.allowed-rates` | [48000] | 允许的采样率列表 |
| `default.clock.quantum` | 1024 | 缓冲区大小（采样数） |
| `default.clock.min-quantum` | 32 | 最小缓冲区 |
| `default.clock.max-quantum` | 2048 | 最大缓冲区 |
| `default.clock.force-quantum` | 0 | 强制缓冲区（0=自动） |
| `default.clock.force-rate` | 0 | 强制采样率（0=自动） |

延迟计算公式：

```
延迟(ms) = quantum / rate × 1000

示例：
1024 / 48000 × 1000 ≈ 21.3ms  （默认，适合桌面）
256 / 48000 × 1000 ≈ 5.3ms    （低延迟）
64 / 48000 × 1000 ≈ 1.3ms     （极低延迟，需要好的硬件）
```

### 低延迟配置

```json5
// ~/.config/pipewire/pipewire.conf.d/20-lowlatency.conf
context.properties = {
    default.clock.rate          = 48000
    default.clock.quantum       = 256
    default.clock.min-quantum   = 64
    default.clock.max-quantum   = 256
}
```

```json5
// ~/.config/pipewire/pipewire-pulse.conf.d/20-lowlatency.conf
pulse.properties = {
    pulse.min.req     = 256/48000
    pulse.default.req = 256/48000
    pulse.max.req     = 256/48000
    pulse.min.quantum = 256/48000
}
```

### 高保真配置

```json5
// ~/.config/pipewire/pipewire.conf.d/20-hifi.conf
context.properties = {
    default.clock.rate          = 96000
    default.clock.allowed-rates = [ 44100 48000 88200 96000 176400 192000 ]
    default.clock.quantum       = 2048
}
```

```json5
// ~/.config/pipewire/client-rt.conf.d/20-hifi.conf
stream.properties = {
    resample.quality   = 14        # SRC 重采样质量 (0-15, 15=最高)
    resample.disable   = false
    channelmix.disable = false
}
```

---

## 39.4 WirePlumber 详解

### 什么是 WirePlumber

WirePlumber 是 PipeWire 的 **会话管理器（Session Manager）**，负责：

```
┌─────────────────────────────────────────────┐
│               WirePlumber                    │
│                                              │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  │
│  │ 设备发现  │  │ 策略引擎  │  │ 路由管理   │  │
│  │ & 管理   │  │ (Lua)    │  │ & 链接    │  │
│  └──────────┘  └──────────┘  └───────────┘  │
│                                              │
│  功能:                                        │
│  - 自动发现音频/视频设备                        │
│  - 自动创建节点                                │
│  - 管理默认设备                                │
│  - 处理设备插拔事件                             │
│  - 实施音频路由策略                             │
│  - 保存/恢复音量和路由状态                       │
└──────────┬──────────────────────────────────┘
           │ Session Manager Protocol
           ▼
┌─────────────────────────────────────────────┐
│              PipeWire Daemon                 │
└─────────────────────────────────────────────┘
```

### WirePlumber vs pipewire-media-session

| 特性 | WirePlumber | pipewire-media-session |
|------|-------------|----------------------|
| 状态 | 活跃开发、默认 | 已弃用 |
| 可扩展性 | Lua 脚本引擎 | 硬编码 C |
| 策略定制 | 灵活 | 有限 |
| 社区支持 | 主流 | 停止维护 |
| 复杂度 | 较高 | 简单 |

### WirePlumber 架构

```
┌───────────────────────────────────────────┐
│             WirePlumber                    │
│                                            │
│  ┌──────────────┐  ┌───────────────────┐   │
│  │  Core (C/GLib)│  │  Lua 脚本引擎     │   │
│  │              │  │                   │   │
│  │  - 对象管理   │  │  - 策略脚本       │   │
│  │  - 事件系统   │  │  - 路由逻辑       │   │
│  │  - 模块加载   │  │  - 自定义规则     │   │
│  └──────────────┘  └───────────────────┘   │
│                                            │
│  ┌──────────────────────────────────────┐   │
│  │         配置层                         │   │
│  │  wireplumber.conf                     │   │
│  │  *.lua.d/ 片段                        │   │
│  │  JSON-like 配置文件                    │   │
│  └──────────────────────────────────────┘   │
└───────────────────────────────────────────┘
```

### WirePlumber 配置文件结构

```
/usr/share/wireplumber/             ← 默认配置
├── wireplumber.conf
├── main.lua.d/
│   ├── 10-default-policy.lua
│   ├── 20-default-access.lua
│   ├── 30-alsa-monitor.lua
│   ├── 40-device-defaults.lua
│   ├── 50-default-access-config.lua
│   └── ...
├── bluetooth.lua.d/
├── policy.lua.d/
└── scripts/

~/.config/wireplumber/              ← 用户覆盖
├── wireplumber.conf.d/
│   └── 10-custom.conf
├── main.lua.d/
│   └── 51-custom-rename.lua
├── bluetooth.lua.d/
│   └── 51-custom-bluetooth.lua
└── policy.lua.d/
```

WirePlumber 0.5+ 使用 SPA-JSON 格式配置：

```bash
# 查看默认配置
cat /usr/share/wireplumber/wireplumber.conf
```

### 设备策略配置

#### 设置默认音频设备

```bash
# 使用 wpctl
wpctl status
wpctl set-default <node-id>

# 示例：查看所有 sink（输出设备）
wpctl status
# Audio
#  ├─ Sinks:
#  │      46. Built-in Audio Analog Stereo   [vol: 0.80]
#  │  *   52. USB Headset                    [vol: 0.65]
#  │      58. HDMI Audio                     [vol: 1.00]

# 设置默认 sink
wpctl set-default 46
```

#### 设备优先级和属性

```
# ~/.config/wireplumber/wireplumber.conf.d/51-device-priority.conf
monitor.alsa.rules = [
  {
    matches = [
      {
        node.name = "alsa_output.usb-*"
      }
    ]
    actions = {
      update-props = {
        priority.driver = 2000
        priority.session = 2000
        node.description = "USB 耳机"
      }
    }
  }
  {
    matches = [
      {
        node.name = "alsa_output.pci-*analog-stereo"
      }
    ]
    actions = {
      update-props = {
        priority.driver = 1000
        priority.session = 1000
        node.description = "内置扬声器"
      }
    }
  }
]
```

#### 禁用特定设备

```
# ~/.config/wireplumber/wireplumber.conf.d/51-disable-hdmi.conf
monitor.alsa.rules = [
  {
    matches = [
      {
        node.name = "alsa_output.pci-*hdmi*"
      }
    ]
    actions = {
      update-props = {
        node.disabled = true
      }
    }
  }
]
```

#### 路由配置

```
# ~/.config/wireplumber/wireplumber.conf.d/51-routes.conf
monitor.alsa.rules = [
  {
    matches = [
      {
        node.name = "alsa_output.pci-0000_00_1f.3.analog-stereo"
      }
    ]
    actions = {
      update-props = {
        audio.format = "S32LE"
        audio.rate = 96000
        audio.channels = 2
        audio.position = [ FL FR ]
      }
    }
  }
]
```

### 自定义 Lua 脚本

WirePlumber 允许通过 Lua 脚本实现自定义逻辑。

#### 自动切换音频设备

```lua
-- ~/.config/wireplumber/main.lua.d/51-auto-switch-headphones.lua
-- 当 USB 耳机插入时自动切换

rule = {
  matches = {
    {
      { "node.name", "matches", "alsa_output.usb-*" },
    },
  },
  apply_properties = {
    ["priority.session"] = 3000,
  },
}

table.insert(alsa_monitor.rules, rule)
```

#### 根据应用设置音量

```
# ~/.config/wireplumber/wireplumber.conf.d/51-app-volume.conf
wireplumber.settings = {
  # 按应用名设置默认音量
}

# 或使用 wpctl 手动设置应用音量
# 首先找到应用节点 ID
# wpctl status（在应用播放时查看 Streams 部分）
# wpctl set-volume <stream-id> 0.5
```

#### 自动静音规则

```
# ~/.config/wireplumber/wireplumber.conf.d/51-auto-mute.conf
monitor.alsa.rules = [
  {
    matches = [
      {
        node.name = "alsa_output.pci-*analog-stereo"
      }
    ]
    actions = {
      update-props = {
        # 插入耳机时自动静音扬声器（ALSA 驱动层处理）
        api.alsa.headroom = 0
      }
    }
  }
]
```

### wpctl 命令详解

```bash
# 查看完整状态
wpctl status

# 设备和流管理
wpctl inspect <id>                    # 查看对象详细信息
wpctl set-default <id>                # 设置默认设备
wpctl set-volume <id> <vol>           # 设置音量（0.0-1.5）
wpctl set-volume @DEFAULT_AUDIO_SINK@ 0.8    # 设置默认 sink 音量
wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%+    # 增加 5%
wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-    # 减少 5%
wpctl set-mute <id> toggle            # 切换静音
wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle   # 切换默认 sink 静音
wpctl set-profile <id> <index>        # 设置设备配置文件

# 查看特定类型的对象
wpctl status | grep -A20 "Sinks"

# 获取音量（脚本友好）
wpctl get-volume @DEFAULT_AUDIO_SINK@
# Volume: 0.80

# Waybar 集成示例（~/.config/waybar/config）
# "pulseaudio": {
#     "on-click": "wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle",
#     "on-scroll-up": "wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%+",
#     "on-scroll-down": "wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-"
# }
```

### 调试 WirePlumber

```bash
# 启用详细日志
WIREPLUMBER_DEBUG=3 wireplumber

# 日志级别：0=关闭, 1=警告, 2=信息, 3=调试, 4=跟踪, 5=全部

# 特定模块调试
WIREPLUMBER_DEBUG="3,wp-*:4" wireplumber

# 查看 journalctl 日志
journalctl --user -u wireplumber -f

# 检查 Lua 脚本加载
WIREPLUMBER_DEBUG="3,wp-lua:5" wireplumber

# 重启 WirePlumber
systemctl --user restart wireplumber
```

---

## 39.5 PipeWire 工具

### pw-top（实时监控）

```bash
pw-top

# 输出示例：
# S   ID QUANT  RATE   WAIT   BUSY  W/Q  B/Q  ERR FORMAT          NAME
# S   46  1024 48000  14.2ms  0.8ms  0.7  0.0    0 S16LE 2 48000  Built-in Audio
# S   52  1024 48000   1.2ms  0.3ms  0.1  0.0    0 S16LE 2 48000  Firefox
#
# S: 状态（S=运行, I=空闲, E=错误）
# QUANT: 量子大小
# RATE: 采样率
# WAIT: 等待时间
# BUSY: 处理时间
# W/Q: 等待/量子比率
# B/Q: 忙碌/量子比率
# ERR: 错误计数（xrun）
```

### pw-dump（图状态导出）

```bash
# 导出完整的图状态（JSON 格式）
pw-dump > pipewire-state.json

# 查看特定节点
pw-dump | jq '.[] | select(.info.props["node.name"] == "alsa_output.pci-0000_00_1f.3.analog-stereo")'

# 查看所有节点名称
pw-dump | jq '.[] | select(.type == "PipeWire:Interface:Node") | .info.props["node.name"]'
```

### pw-cli（命令行交互）

```bash
# 交互式模式
pw-cli

# 常用命令
pw-cli list-objects             # 列出所有对象
pw-cli info <id>                # 查看对象信息
pw-cli enum-params <id> Props   # 查看节点属性

# 非交互式
pw-cli ls Node                  # 列出所有节点
pw-cli ls Port                  # 列出所有端口
pw-cli ls Link                  # 列出所有链接
```

### pw-record / pw-play / pw-cat

```bash
# 录制音频
pw-record --target=@DEFAULT_AUDIO_SOURCE@ output.wav
pw-record --rate=48000 --channels=2 --format=s24 output.wav

# 播放音频
pw-play music.wav
pw-play --target=@DEFAULT_AUDIO_SINK@ music.flac

# pw-cat（通用音频管道）
pw-cat --playback music.wav          # 等同 pw-play
pw-cat --record output.wav           # 等同 pw-record
pw-cat --midi --playback song.mid    # MIDI 播放

# 音频测试信号
pw-cat --playback --format=f32 --rate=48000 --channels=2 /dev/zero
# 或使用 SPA 测试源
spa-monitor alsa/monitor
```

### pw-link（手动链接节点）

```bash
# 列出所有端口
pw-link -o             # 输出端口
pw-link -i             # 输入端口
pw-link -l             # 所有链接

# 创建链接
pw-link "Firefox:output_FL" "Built-in Audio:playback_FL"
pw-link "Firefox:output_FR" "Built-in Audio:playback_FR"

# 按 ID 链接
pw-link 85 92

# 断开链接
pw-link -d "Firefox:output_FL" "Built-in Audio:playback_FL"
```

### pw-dot（生成图可视化）

```bash
# 生成 DOT 格式图
pw-dot

# 渲染为图片
sudo pacman -S graphviz
pw-dot | dot -Tpng -o pipewire-graph.png
pw-dot | dot -Tsvg -o pipewire-graph.svg

# 在浏览器中查看
pw-dot | dot -Tsvg > /tmp/pw-graph.svg && xdg-open /tmp/pw-graph.svg

# 或使用图形工具
helvum          # GTK 图形节点管理器
qpwgraph        # Qt 图形节点管理器
```

---

## 39.6 PipeWire 视频功能

### 屏幕共享

```bash
# 安装 xdg-desktop-portal 后端
sudo pacman -S xdg-desktop-portal
sudo pacman -S xdg-desktop-portal-wlr       # wlroots 合成器
sudo pacman -S xdg-desktop-portal-hyprland   # Hyprland
sudo pacman -S xdg-desktop-portal-gtk        # GNOME
sudo pacman -S xdg-desktop-portal-kde        # KDE

# 屏幕共享流程：
# 应用 → D-Bus → xdg-desktop-portal → 合成器捕获 → PipeWire 视频流 → 应用

# 测试屏幕共享
# 在 Firefox 中访问 https://mozilla.github.io/webrtc-landing/gum_test.html
# 选择 "Screen" 共享

# 查看 PipeWire 视频流
pw-cli ls Node | grep -i video
```

### 虚拟摄像头

```bash
# 安装 v4l2loopback
sudo pacman -S v4l2loopback-dkms

# 加载模块
sudo modprobe v4l2loopback video_nr=10 card_label="Virtual Camera"

# 使用 PipeWire 将视频流发送到虚拟摄像头
# OBS Studio: 工具 → 虚拟摄像头 → 开始

# 手动使用 GStreamer
gst-launch-1.0 pipewiresrc ! videoconvert ! v4l2sink device=/dev/video10

# 验证
v4l2-ctl --list-devices
```

### 视频路由

```bash
# 列出视频节点
pw-cli ls Node | grep -i video

# 链接视频源到视频汇
pw-link "v4l2_input.pci-*:capture_0" "virtual-camera:input_0"
```

---

## 39.7 蓝牙音频与 PipeWire

### 安装和配置

```bash
# 确保蓝牙支持
sudo pacman -S bluez bluez-utils
sudo systemctl enable --now bluetooth.service

# PipeWire 蓝牙支持（pipewire-audio 元包已包含）
# 或手动确认
pacman -Qs pipewire | grep bluetooth
# libwireplumber 内建蓝牙支持
```

### 音频配置文件

| 配置文件 | 用途 | 音质 |
|----------|------|------|
| A2DP Sink | 高质量音乐播放 | 高（立体声） |
| A2DP Source | 蓝牙音频接收 | 高 |
| HFP (Hands-Free) | 通话模式 | 低（单声道+麦克风） |
| HSP (Headset) | 旧版通话 | 低 |

```bash
# 查看蓝牙设备配置文件
wpctl status | grep -A20 "Bluetooth"

# 切换配置文件
wpctl set-profile <device-id> <profile-index>

# 查看可用配置文件
wpctl inspect <device-id> | grep -A5 "profile"
```

### 编解码器选择

```bash
# PipeWire 支持的蓝牙编解码器
# SBC     - 默认，所有蓝牙设备支持
# AAC     - Apple 设备常用
# LDAC    - 索尼高保真编解码器（需要 libldac）
# AptX    - 高通编解码器（需要 libfreeaptx）
# AptX HD - 高清版本
# AptX LL - 低延迟版本

# 安装额外编解码器支持
# LDAC 和 AptX 已内建于 PipeWire

# 查看当前使用的编解码器
pw-dump | jq '.[] | select(.info.props["api.bluez5.codec"] != null) | .info.props["api.bluez5.codec"]'

# 配置编解码器优先级
```

```
# ~/.config/wireplumber/wireplumber.conf.d/51-bluetooth-codecs.conf
monitor.bluez.properties = {
  bluez5.codecs = [ sbc sbc_xq aac ldac aptx aptx_hd aptx_ll aptx_ll_duplex ]
  bluez5.enable-sbc-xq = true
  bluez5.enable-msbc = true       # mSBC 宽带语音
  bluez5.enable-hw-volume = true  # 硬件音量控制
}
```

### mSBC 宽带语音

mSBC 提升了 HFP 通话质量（从 8kHz 到 16kHz 采样率）：

```
# 已在上方 51-bluetooth-codecs.conf 中启用
# bluez5.enable-msbc = true

# 验证 mSBC 是否活跃（在 HFP 模式下）
pw-dump | jq '.[] | select(.info.props["api.bluez5.codec"] == "msbc")'
```

### 蓝牙常见问题

```bash
# 问题 1：蓝牙设备连接但无声音
systemctl --user restart pipewire pipewire-pulse wireplumber
wpctl set-default <bluetooth-sink-id>

# 问题 2：A2DP 和 HFP 不能同时使用
# 这是蓝牙协议的固有限制
# 使用 pavucontrol 或 wpctl 手动切换配置文件

# 问题 3：编解码器协商失败
# 检查日志
journalctl --user -u wireplumber | grep -i bluez

# 问题 4：音频卡顿
# 增加蓝牙缓冲区
```

```
# ~/.config/wireplumber/wireplumber.conf.d/51-bluetooth-buffer.conf
monitor.bluez.rules = [
  {
    matches = [
      {
        node.name = "bluez_output.*"
      }
    ]
    actions = {
      update-props = {
        api.bluez5.a2dp.internal-delay = 2500
        session.suspend-timeout-seconds = 0
      }
    }
  }
]
```

---

## 39.8 MIDI 与 PipeWire

```bash
# PipeWire 原生支持 MIDI
# 列出 MIDI 设备
pw-cli ls Node | grep -i midi

# 列出 MIDI 端口
pw-link -o | grep midi
pw-link -i | grep midi

# 连接 MIDI 设备
pw-link "Midi-Bridge:capture_0" "Yoshimi:input_0"

# 使用 JACK MIDI 工具（通过 pipewire-jack）
pw-jack a2jmidid -e        # ALSA 到 JACK MIDI 桥接

# MIDI 监控
pw-jack jack_midi_dump      # 监控 MIDI 事件

# 安装 MIDI 合成器
sudo pacman -S fluidsynth
fluidsynth /usr/share/soundfonts/FluidR3_GM.sf2
```

---

## 39.9 专业音频工作流

### 替代 JACK

PipeWire 可以完全替代 JACK，为专业音频应用提供低延迟支持：

```json5
// ~/.config/pipewire/pipewire.conf.d/20-pro-audio.conf
context.properties = {
    default.clock.rate          = 48000
    default.clock.allowed-rates = [ 44100 48000 88200 96000 ]
    default.clock.quantum       = 128
    default.clock.min-quantum   = 64
    default.clock.max-quantum   = 1024
}

context.modules = [
    { name = libpipewire-module-rt
      args = {
        nice.level    = -11
        rt.prio       = 88
        rt.time.soft  = -1
        rt.time.hard  = -1
      }
    }
]
```

### 实时调度

```bash
# 检查实时权限
ulimit -r
# 应该显示非零值

# 确保用户在 realtime 组中
# /etc/security/limits.d/99-realtime.conf
```

```
@realtime   -   rtprio     98
@realtime   -   memlock    unlimited
```

```bash
sudo groupadd realtime
sudo usermod -aG realtime $USER

# 或使用 rtkit（PipeWire 默认使用）
sudo pacman -S rtkit
systemctl enable --now rtkit-daemon
```

### 专业音频软件兼容性

| 软件 | 类型 | PipeWire 兼容 |
|------|------|---------------|
| Ardour | DAW | pw-jack ardour |
| Carla | 插件宿主 | pw-jack carla |
| Guitarix | 吉他效果器 | pw-jack guitarix |
| Hydrogen | 鼓机 | pw-jack hydrogen |
| REAPER | DAW | pw-jack reaper |
| Bitwig | DAW | 原生 PipeWire |
| Yoshimi | 合成器 | pw-jack yoshimi |

```bash
# 运行 JACK 应用
pw-jack ardour
pw-jack carla

# 检查 xrun 计数
pw-top
# ERR 列显示 xrun 次数，应该为 0
```

---

## 39.10 Filter Chain（滤波链）

PipeWire 的 `filter-chain` 模块可以创建音频滤波器：

```json5
// ~/.config/pipewire/pipewire.conf.d/30-equalizer.conf
// 参数均衡器示例
context.modules = [
    { name = libpipewire-module-filter-chain
      args = {
        node.description = "均衡器"
        media.name        = "均衡器"
        filter.graph = {
            nodes = [
                {
                    type  = builtin
                    name  = eq_band_1
                    label = bq_peaking
                    control = { "Freq" = 60 "Q" = 1.0 "Gain" = 3.0 }
                }
                {
                    type  = builtin
                    name  = eq_band_2
                    label = bq_peaking
                    control = { "Freq" = 250 "Q" = 1.0 "Gain" = -2.0 }
                }
                {
                    type  = builtin
                    name  = eq_band_3
                    label = bq_peaking
                    control = { "Freq" = 1000 "Q" = 1.0 "Gain" = 0.0 }
                }
                {
                    type  = builtin
                    name  = eq_band_4
                    label = bq_peaking
                    control = { "Freq" = 4000 "Q" = 1.0 "Gain" = 2.0 }
                }
                {
                    type  = builtin
                    name  = eq_band_5
                    label = bq_peaking
                    control = { "Freq" = 12000 "Q" = 1.0 "Gain" = 1.0 }
                }
            ]
            links = [
                { output = "eq_band_1:Out" input = "eq_band_2:In" }
                { output = "eq_band_2:Out" input = "eq_band_3:In" }
                { output = "eq_band_3:Out" input = "eq_band_4:In" }
                { output = "eq_band_4:Out" input = "eq_band_5:In" }
            ]
        }
        capture.props = {
            node.name    = "effect_input.eq"
            media.class  = Audio/Sink
        }
        playback.props = {
            node.name    = "effect_output.eq"
            node.passive = true
        }
      }
    }
]
```

```bash
# 应用均衡器后，在 pavucontrol 中将应用输出切换到 "均衡器"
# 或使用 wpctl
wpctl set-default <eq-sink-id>
```

### 虚拟设备（组合 Sink/Source）

```json5
// ~/.config/pipewire/pipewire.conf.d/30-virtual-sink.conf
context.modules = [
    { name = libpipewire-module-combine-stream
      args = {
        combine.mode = sink
        node.name = "combined_sink"
        node.description = "组合输出（扬声器+耳机）"
        combine.latency-compensate = true
        combine.props = {
            audio.position = [ FL FR ]
        }
        stream.props = {}
        stream.rules = [
            {
                matches = [
                    { media.class = "Audio/Sink" node.name = "alsa_output.pci-*analog*" }
                ]
                actions = { create-stream = {} }
            }
            {
                matches = [
                    { media.class = "Audio/Sink" node.name = "alsa_output.usb-*" }
                ]
                actions = { create-stream = {} }
            }
        ]
      }
    }
]
```

---

## 39.11 常见问题排查

### 无声音

```bash
# 1. 检查 PipeWire 是否运行
systemctl --user status pipewire pipewire-pulse wireplumber

# 2. 检查默认 sink
wpctl status
wpctl get-volume @DEFAULT_AUDIO_SINK@

# 3. 确认未静音
wpctl set-mute @DEFAULT_AUDIO_SINK@ 0

# 4. 检查 ALSA 底层
speaker-test -c 2 -t wav

# 5. 检查节点链接
pw-link -l

# 6. 重启所有服务
systemctl --user restart pipewire pipewire-pulse wireplumber
```

### 音频卡顿 / Xrun

```bash
# 1. 查看 xrun
pw-top
# ERR 列非零 = xrun

# 2. 增大量子（增大缓冲区）
# ~/.config/pipewire/pipewire.conf.d/10-fix-xrun.conf
# context.properties = {
#     default.clock.quantum = 2048
# }

# 3. 检查实时调度
chrt -p $(pidof pipewire)
# 应该显示 SCHED_FIFO 或 SCHED_RR

# 4. 检查 CPU 负载
pw-top   # 查看 BUSY 列
```

### PulseAudio 应用无法连接

```bash
# 检查 pipewire-pulse 是否运行
systemctl --user status pipewire-pulse

# 检查 socket
ls -la /run/user/$(id -u)/pulse/

# 确认没有真正的 PulseAudio 运行
ps aux | grep pulseaudio
# 不应该有 pulseaudio 进程

# 如果有冲突
systemctl --user mask pulseaudio.service pulseaudio.socket
systemctl --user unmask pipewire-pulse.service pipewire-pulse.socket
```

### 采样率不匹配

```bash
# 查看当前采样率
pw-top    # RATE 列

# 启用多采样率支持
```

```json5
// ~/.config/pipewire/pipewire.conf.d/10-rates.conf
context.properties = {
    default.clock.rate = 48000
    default.clock.allowed-rates = [ 44100 48000 88200 96000 192000 ]
}
```

---

## 39.12 实战配置集

### 桌面日常使用

```json5
// ~/.config/pipewire/pipewire.conf.d/10-desktop.conf
context.properties = {
    default.clock.rate          = 48000
    default.clock.allowed-rates = [ 44100 48000 ]
    default.clock.quantum       = 1024
    default.clock.min-quantum   = 512
    default.clock.max-quantum   = 2048
}
```

### 游戏低延迟

```json5
// ~/.config/pipewire/pipewire.conf.d/10-gaming.conf
context.properties = {
    default.clock.rate          = 48000
    default.clock.quantum       = 256
    default.clock.min-quantum   = 128
    default.clock.max-quantum   = 512
}
```

### 音乐制作

```json5
// ~/.config/pipewire/pipewire.conf.d/10-music-production.conf
context.properties = {
    default.clock.rate          = 96000
    default.clock.allowed-rates = [ 44100 48000 88200 96000 ]
    default.clock.quantum       = 128
    default.clock.min-quantum   = 64
    default.clock.max-quantum   = 256
}
```

### 高保真音乐欣赏

```json5
// ~/.config/pipewire/pipewire.conf.d/10-audiophile.conf
context.properties = {
    default.clock.rate          = 192000
    default.clock.allowed-rates = [ 44100 48000 88200 96000 176400 192000 ]
    default.clock.quantum       = 2048
}
```

```json5
// ~/.config/pipewire/client-rt.conf.d/10-audiophile.conf
stream.properties = {
    resample.quality = 15
}
```

### 完整的系统信息检查脚本

```bash
#!/bin/bash
echo "=== PipeWire 系统信息 ==="
echo ""
echo "--- PipeWire 版本 ---"
pipewire --version
echo ""
echo "--- WirePlumber 版本 ---"
wireplumber --version
echo ""
echo "--- 服务状态 ---"
systemctl --user is-active pipewire pipewire-pulse wireplumber
echo ""
echo "--- 默认设备 ---"
wpctl get-volume @DEFAULT_AUDIO_SINK@
wpctl get-volume @DEFAULT_AUDIO_SOURCE@
echo ""
echo "--- 节点列表 ---"
pw-cli ls Node 2>/dev/null | head -30
echo ""
echo "--- 当前图状态 ---"
pw-top -b -n 1 2>/dev/null
echo ""
echo "--- 蓝牙设备 ---"
wpctl status 2>/dev/null | grep -A10 "Bluetooth"
```

---

## 39.13 参考资源

| 资源 | 链接 |
|------|------|
| PipeWire 官方文档 | https://docs.pipewire.org/ |
| PipeWire Wiki | https://gitlab.freedesktop.org/pipewire/pipewire/-/wikis/home |
| WirePlumber 文档 | https://pipewire.pages.freedesktop.org/wireplumber/ |
| Arch Wiki - PipeWire | https://wiki.archlinux.org/title/PipeWire |
| Arch Wiki - WirePlumber | https://wiki.archlinux.org/title/WirePlumber |
| PipeWire 配置示例 | https://gitlab.freedesktop.org/pipewire/pipewire/-/tree/master/src/daemon |

---

## 39.14 本章测验

> [!example] 📝 自测题目

> [!question]- 选择题 1：PipeWire 的设计目标是统一替代哪些现有系统？
> - A. ALSA + OSS
> - B. PulseAudio + JACK + 视频流处理
> - C. X11 + Wayland
> - D. systemd + OpenRC
>
> > [!success]- 点击查看答案
> > **B**
> > PipeWire 旨在统一替代 PulseAudio（桌面音频）、JACK（专业低延迟音频）并添加视频流处理能力（如屏幕共享、摄像头），成为一个涵盖音频+视频+MIDI 的多媒体框架。

> [!question]- 选择题 2：WirePlumber 在 PipeWire 生态中的角色是什么？
> - A. 音频编解码器
> - B. 会话管理器，通过 Lua 脚本管理设备策略和路由
> - C. 音频驱动程序
> - D. 图形界面控制面板
>
> > [!success]- 点击查看答案
> > **B**
> > WirePlumber 是 PipeWire 的默认会话管理器，负责设备发现、策略管理和路由决策，使用 Lua 脚本引擎提供灵活的可配置策略。

> [!question]- 判断题 3：PipeWire 通过 pipewire-pulse 兼容层可以运行所有依赖 PulseAudio 的应用程序，无需修改应用代码。
> - A. ✓ 正确
> - B. ✗ 错误
>
> > [!success]- 点击查看答案
> > **A. ✓ 正确**
> > pipewire-pulse 提供了 PulseAudio 兼容的 socket 和 API，现有 PulseAudio 应用无需任何修改即可在 PipeWire 下运行。同样 pipewire-jack 和 pipewire-alsa 分别提供 JACK 和 ALSA 兼容层。

> [!question]- 选择题 4：以下哪个命令可以查看 PipeWire 当前的音频图（节点和连接）状态？
> - A. `pulseaudio --dump`
> - B. `pw-top`
> - C. `alsamixer`
> - D. `jack_lsp`
>
> > [!success]- 点击查看答案
> > **B**
> > `pw-top` 实时显示 PipeWire 处理图中各节点的状态、延迟和 DSP 负载。此外 `pw-cli ls Node` 和 `wpctl status` 也可以查看节点信息。

> [!question]- 选择题 5：PipeWire 的 quantum 参数决定了什么？
> - A. 采样率
> - B. 每次处理的音频帧数（直接影响延迟）
> - C. 通道数
> - D. 比特深度
>
> > [!success]- 点击查看答案
> > **B**
> > quantum 是每次处理周期中的音频帧数。quantum/采样率 = 延迟时间。例如 quantum=1024，采样率 48000Hz 时，延迟约为 1024/48000 ≈ 21ms。减小 quantum 可降低延迟但增加 CPU 负载。

> [!question]- 判断题 6：`wpctl set-volume @DEFAULT_AUDIO_SINK@ 50%` 可以将默认音频输出设备的音量设置为 50%。
> - A. ✓ 正确
> - B. ✗ 错误
>
> > [!success]- 点击查看答案
> > **A. ✓ 正确**
> > `wpctl` 是 WirePlumber 的命令行工具，`@DEFAULT_AUDIO_SINK@` 引用默认音频输出设备，可以直接设置绝对音量百分比或使用 `5%+`/`5%-` 进行相对调节。

> [!question]- 选择题 7：PipeWire 处理蓝牙音频时，支持哪些编解码器？
> - A. 仅支持 SBC
> - B. SBC、AAC、aptX、aptX HD、LDAC 等多种编解码器
> - C. 仅支持 MP3
> - D. 不支持蓝牙音频
>
> > [!success]- 点击查看答案
> > **B**
> > PipeWire 的蓝牙模块支持 SBC、SBC-XQ、AAC、aptX、aptX HD、LDAC、LC3 等多种蓝牙音频编解码器，提供比 PulseAudio 更广泛的蓝牙编解码支持。

> [!question]- 选择题 8：PipeWire 在 Wayland 生态中的视频流功能主要用于什么？
> - A. 视频编辑
> - B. 屏幕共享和摄像头访问（配合 xdg-desktop-portal）
> - C. 视频播放
> - D. 3D 渲染
>
> > [!success]- 点击查看答案
> > **B**
> > PipeWire 提供视频流传输能力，配合 xdg-desktop-portal 实现 Wayland 环境下的屏幕共享（如视频会议、远程桌面）和安全的摄像头访问。

> [!question]- 判断题 9：PipeWire 的 pipewire-jack 兼容层可以让 JACK 专业音频应用以低延迟运行，无需单独启动 JACK 服务器。
> - A. ✓ 正确
> - B. ✗ 错误
>
> > [!success]- 点击查看答案
> > **A. ✓ 正确**
> > pipewire-jack 提供了 JACK API 兼容层，JACK 应用连接到 PipeWire 而非单独的 JACK 服务器，同时桌面音频和专业音频可以共存于同一图中。

> [!question]- 选择题 10：要降低 PipeWire 的音频延迟到适合专业音频制作的水平，应该调整哪个参数？
> - A. 增大 `default.clock.rate`
> - B. 减小 `default.clock.quantum`（如设为 64 或 128）
> - C. 增大 `default.clock.quantum`
> - D. 减小 `default.clock.rate`
>
> > [!success]- 点击查看答案
> > **B**
> > 减小 quantum 值会减少每次处理的帧数，从而降低延迟。专业音频制作通常将 quantum 设为 64 或 128（在 48000Hz 采样率下分别对应约 1.3ms 和 2.7ms 延迟）。
