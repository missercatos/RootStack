# 10 - Niri 窗口合成器配置 (超级完善版)

> [Niri](https://github.com/YaLTeR/niri) — Rust 写的 Wayland 滚动平铺合成器。本教程基于真实生产环境深度配置，覆盖基础到高级所有功能。

---

## 10.1 配置文件架构

Niri 从 25.11 版本开始支持配置拆分，推荐按模块组织：

```
~/.config/niri/
├── config.kdl              # 主配置（环境变量、输入、启动项、include）
├── layout.kdl              # 布局/间距/阴影/焦点环/边框
├── animations.kdl          # 全部动画参数
├── blur.kdl                # 模糊效果
├── scripts/                # 自定义脚本目录
│   ├── screenshot-sound.sh
│   ├── niri-force-kill-window
│   ├── niri-pick           # 窗口信息提取 / 屏幕取色器
│   └── niri-binds          # 快捷键教程生成器
└── dms/                    # DMS 集成配置（自动生成 + 可手写）
    ├── binds.kdl           # 所有快捷键
    ├── windowrules.kdl     # 窗口规则
    ├── supertab.kdl        # Super+Tab 带缩略图切换
    ├── alttab.kdl          # Alt+Tab 样式
    ├── colors.kdl          # DMS 主题色
    ├── cursor.kdl          # 光标设置
    ├── outputs.kdl         # 显示器配置
    └── wpblur.kdl          # 壁纸模糊层
```

**主 config.kdl 入口：**

```kdl
include "layout.kdl"
include "animations.kdl"
// include "blur.kdl"            ← 按需打开
screenshot-path "~/Pictures/Screenshots/Niri-screenshots/%Y-%m-%d_%H-%M-%S.png"

environment {
    LANG "zh_CN.UTF-8"
    LC_CTYPE "en_US.UTF-8"      // 修复输入法漏字
    XMODIFIERS "@im=fcitx"
    QT_QPA_PLATFORMTHEME "gtk3"
    EDITOR "vim"
}

input { /* 键盘/触摸板/鼠标 */ }
spawn-at-startup "dms" "run"     // 面板/启动器/通知等
spawn-at-startup "fcitx5"

include "dms/binds.kdl"
include "dms/supertab.kdl"
include "dms/alttab.kdl"
include "dms/windowrules.kdl"
include "dms/cursor.kdl"
include "dms/colors.kdl"
```

---

## 10.2 布局与视觉 — layout.kdl

```kdl
layout {
    gaps 12                      // 窗间距
    center-focused-column "never" // 不自动居中聚焦的列（手动居中用 Mod+C）
    default-column-width { proportion 0.5; }

    // Mod+R 循环切换的三档宽度
    preset-column-widths {
        proportion 0.33333
        proportion 0.5
        proportion 0.66667
    }

    // 聚焦环（高亮当前窗口的描边）
    focus-ring {
        width 3                    // 环宽（px）
        // 颜色在 dms/colors.kdl 里统一管理
    }

    // 边框（始终可见，与 focus-ring 二选一）
    border {
        off                       // 关闭边框（用 focus-ring 代替）
        width 4
        active-color "#ffc87f"
        inactive-color "#505050"
        // 也可用渐变：active-gradient from="#80c8ff" to="#c7ff7f" angle=45
    }

    // 阴影（CSS box-shadow 语义）
    shadow {
        on
        softness 20              // 模糊半径
        spread 2                 // 扩展
        offset x=-4 y=-4         // 偏移（负值=左上方向）
        color "rgba(0, 0, 0, 0.7)"
        // draw-behind-window true  ← 如果窗口自绘 CSD 阴影则开启此选项
    }

    // Struts（类似 waybar 的预留空间）
    struts {
        // left 64
        // right 64
    }
}
```

---

## 10.3 弹簧动画深度调校 — animations.kdl

Niri 的动画系统支持 **CSS 缓动曲线** 和 **弹簧物理** 两种模式。

```kdl
animations {
    // 全局减速因子：<1 加速，>1 减速（微调手感用）
    slowdown 0.98114514

    // ===== 工作区切换动画 =====
    workspace-switch {
        // 弹簧参数：
        //   damping-ratio: 0.8 = 回弹明显，1.0 = 刚好不弹，>1.0 = 过阻尼(bug倾向)
        //   stiffness: 值越大越"硬/生涩"，越小越"软/回弹大"
        //   epsilon: 动画速度<此值判定为停止
        spring damping-ratio=0.82 stiffness=400 epsilon=0.0001
    }

    // 水平视图移动（列间切换焦点）
    horizontal-view-movement {
        spring damping-ratio=0.84 stiffness=400 epsilon=0.0001
    }

    // 打开/关闭窗口 — 可组合弹簧和缓动曲线
    window-open {
        spring damping-ratio=1.0 stiffness=1000 epsilon=0.0001
    }
    window-close {
        spring damping-ratio=0.8 stiffness=400 epsilon=0.0001
    }

    // 窗口移动（合并列、跨列移动）
    window-movement {
        spring damping-ratio=1.0 stiffness=800 epsilon=0.0001
    }

    // 大小调整（Mod+R 切换预设宽度时）
    window-resize {
        spring damping-ratio=0.9 stiffness=500 epsilon=0.0001
    }

    // 截图 UI 打开
    screenshot-ui-open {
        duration-ms 300
        curve "ease-out-quad"
    }

    // Overview 打开/关闭
    overview-open-close {
        spring damping-ratio=1.0 stiffness=900 epsilon=0.0001
    }
}
```

### Niri 可用的动画曲线

```
ease-out-quad      → 平缓加速后略减速（接近线性，最不突兀）
ease-out-cubic     → 较快加速后明显减速
ease-out-expo      → 极快加速后立刻减速（最生动）
linear             → 纯匀速
cubic-bezier       → 自定义：curve "cubic-bezier" 0.05 0.7 0.1 1
```

在线设计工具：[easings.co](https://easings.co) / 预览：[easings.net](https://easings.net)

### 弹簧动画调参技巧

| 场景 | damping-ratio | stiffness | 效果 |
|------|---------------|-----------|------|
| 切换工作区 | 0.75~0.85 | 300~450 | 轻微回弹，灵动 |
| 打开窗口 | 0.9~1.0 | 600~1200 | 快速弹入 |
| 关闭窗口 | 0.7~0.8 | 300~450 | 明显回弹后消失 |
| 移动窗口 | 1.0 | 600~900 | 无回弹，精准 |
| 调大小 | 0.85~0.95 | 400~600 | 微弹 |

---

## 10.4 模糊效果 — blur.kdl

Niri 的模糊效果有两种模式：

- **xray=true**：只渲染一次模糊版的壁纸作为"假壁纸"贴在窗口后面（零性能消耗）
- **xray=false**：实时模糊窗口背后的真实内容（性能消耗高）

```kdl
// blur.kdl

// 全局模糊参数
blur {
    passes 3           // 渲染次数（次数越多越模糊，但性能越差）
    offset 3           // 采样偏移（越大边缘越雾化）
    noise 0.02         // 噪点纹理（防止色带伪影）
    saturation 1.5     // 饱和增强（>1 更鲜艳，<1 去色）
}

// 所有普通窗口 → Xray 模式（零性能消耗）
window-rule {
    background-effect {
        xray true
        blur true
    }
}

// 浮动窗口 → 同样 Xray 模式（实时 blur 太吃性能）
window-rule {
    match is-floating=true
    background-effect {
        xray true
        blur true
    }
}

// Fuzzel 启动器 → 实时模糊（因为背后内容需要实时变化）
layer-rule {
    match namespace="^launcher$"
    geometry-corner-radius 8
    background-effect {
        xray false          // 实时 blur
        blur true
    }
}
```

---

## 10.5 快捷键体系设计哲学 — dms/binds.kdl

### 10.5.1 Niri 内置动作 vs 外部脚本

```kdl
binds {
    // 内置动作（快，无延迟）：
    Mod+Q    { close-window; }
    Mod+F    { maximize-column; }
    Mod+Left { focus-column-left; }

    // spawn（启动程序）：
    Mod+T { spawn "kitty" "--single-instance"; }

    // spawn-sh（运行 shell 命令，支持 && / || / $() 等）：
    Mod+F1 { spawn-sh "pkill fcitx5 || fcitx5"; }

    // DMS IPC 调用（面板/通知/锁屏/壁纸等）：
    Mod+X   { spawn "dms" "ipc" "call" "powermenu" "toggle"; }
    Mod+Z   { spawn-sh "dms ipc call spotlight toggle || fuzzel"; }
}
```

### 10.5.2 快捷键修饰符命名

```
Super = Mod（默认的 Win 键）
Shift = Shift
Ctrl  = Ctrl
Alt   = Alt

组合：Mod+Shift+Q、Mod+Ctrl+Left、Mod+Shift+Ctrl+Right
特殊：MouseMiddle、MouseForward、MouseBack、WheelScrollDown
```

### 10.5.3 Hotkey Overlay —— 让快捷键可发现

```kdl
// hotkey-overlay-title 指定在快捷键帮助面板中显示的名称
// null = 不显示在帮助面板中

Mod+Shift+Slash hotkey-overlay-title="快捷键教程 Keybind tutorial" { spawn "~/.config/niri/scripts/niri-binds"; }
Mod+E hotkey-overlay-title="文件管理器 File Manager" { spawn-sh "thunar || nautilus --new-window"; }
Mod+Alt+A hotkey-overlay-title="区域截图 Select Area" { spawn-sh "niri msg action screenshot --show-pointer false && pkill -f -USR1 screenshot-sound.sh"; }
```

### 10.5.4 cooldown-ms 防误触

```kdl
// 滚轮切换工作区：防 150ms 内连续触发
Mod+Shift+WheelScrollDown cooldown-ms=150 { focus-workspace-down; }
```

### 10.5.5 repeat=false 禁止长按重复

```kdl
// 关闭窗口不应该因为长按而连续触发
Mod+Q repeat=false { close-window; }
```

### 10.5.6 allow-when-locked

```kdl
// 锁屏状态下仍可调节音量/亮度
XF86AudioRaiseVolume allow-when-locked=true { spawn "dms" "ipc" "call" "audio" "increment" "3"; }
XF86MonBrightnessUp allow-when-locked=true { spawn "dms" "ipc" "call" "brightness" "increment" "5" ""; }
```

---

## 10.6 高级窗口规则 — dms/windowrules.kdl

### 10.6.1 全局窗口规则

```kdl
window-rule {
    geometry-corner-radius 8       // 圆角（niri 知道的，非 CSD）
    clip-to-geometry true          // 裁剪溢出圆角的内容
    opacity 0.99                   // 全局轻微透明（0.99 让 niri 知道此窗口透明从而启用混合模式）
    draw-border-with-background false  // 边框不画到背景里（配合 prefer-no-csd）
}
```

### 10.6.2 指定窗口列宽/高度

```kdl
// Steam 好友列表：固定窄列
window-rule {
    match app-id="steam" title="Friends List"
    match app-id="steam" title="好友列表"
    default-column-width { proportion 0.20; }
}

// 某 TUI 应用：浮动 + 固定宽高
window-rule {
    match app-id="shorinclip"
    default-column-width { fixed 625; }
    default-window-height { fixed 700; }
    open-floating true
    default-floating-position x=0 y=18 relative-to="top"
}
```

### 10.6.3 浮动窗口清单

```kdl
// 集中管理所有需要浮动的窗口
window-rule {
    match app-id="com.gabm.satty"      // 截图编辑
    match app-id="nm-connection-editor" // 网络连接
    match app-id="pavucontrol"          // 音量控制
    match app-id="blueman-manager"      // 蓝牙
    match app-id="flameshot"            // 截图
    match app-id="btrfs-assistant"      // Btrfs 管理
    match app-id="thunar" title="文件操作进度"
    match title="重命名"
    match title="另存为"
    match title="日历"
    // ...更多...
    open-floating true
}
```

### 10.6.4 开启后不自动聚焦

```kdl
window-rule {
    match app-id="QQ" title="资料卡"
    match app-id="QQ" title="天气"
    open-focused false
}

// Steam 通知弹窗：右下角，不抢焦点
window-rule {
    match app-id="steam" title=r#"^notificationtoasts_\d+_desktop$"#
    default-floating-position x=10 y=10 relative-to="bottom-right"
    open-focused false
}
```

### 10.6.5 特殊窗口处理

```kdl
// Waydroid（Android 模拟器）：全屏 + 无装饰
window-rule {
    match app-id="waydroid"
    open-fullscreen true
    open-floating true
    focus-ring { off }
    shadow { off }
}

// 图片/视频播放器：不透明（避免透明导致性能问题）
window-rule {
    match app-id="mpv"
    match app-id="celluloid"
    match title="图片查看器"
    match title="画中画"
    opacity 1.0
    open-floating true
}
```

---

## 10.7 Super+Tab 带缩略图窗口切换 — dms/supertab.kdl

```kdl
recent-windows {
    debounce-ms 750         // 松开后 750ms 自动消失
    open-delay-ms 150       // 按下后 150ms 弹出（防轻触误弹）

    highlight {
        padding 30            // 缩略图背景内间距
        corner-radius 12      // 缩略图背景圆角
    }

    previews {
        max-height 480        // 缩略图最大高度
        max-scale 0.2         // 缩略图最大缩放比
    }

    binds {
        // 当前工作区的窗口
        Mod+Tab         { next-window scope="workspace"; }
        Mod+Shift+Tab   { previous-window scope="workspace"; }
        // 仅当前 app 的所有窗口（如多窗口 firefox）
        Mod+grave       { next-window filter="app-id"; }
        Mod+Shift+grave { previous-window filter="app-id"; }
    }
}
```

### 可选 scope 值

| scope | 含义 |
|-------|------|
| `"workspace"` | 仅当前工作区 |
| `"monitor"` | 当前显示器上所有工作区 |
| 不写 | 全部窗口 |

---

## 10.8 高级脚本集成

### 10.8.1 壁纸下载 + 自动应用 + 主题联动

```bash
#!/bin/bash
# ~/.local/bin/random-anime-wallpaper-dms

API_URL="https://t.alcy.cc/pc/"
SAVE_DIR="$HOME/Pictures/Wallpapers/api-random-download"
KEEP_COUNT=40

TIMESTAMP=$(date +%s)
RAW_PATH="${SAVE_DIR}/wall_${TIMESTAMP}_raw.tmp"
FINAL_PATH="${SAVE_DIR}/wall_${TIMESTAMP}.png"

mkdir -p "$SAVE_DIR"

# 异步下载 + 超时心跳通知（大文件下载时告知用户"还在下载"）
(
    sleep 8
    while true; do
        notify-send "Wallpaper" "Downloading is still in progress..." --expire-time=5000 || true
        sleep 8
    done
) &
NOTIFY_PID=$!

curl -L -s -A "Mozilla/5.0" --connect-timeout 10 -m 120 -o "$RAW_PATH" "$API_URL"
kill "$NOTIFY_PID" 2>/dev/null || true

# 校验文件有效性
if [ ! -f "$RAW_PATH" ] || [ "$(wc -c < "$RAW_PATH")" -lt 20480 ]; then
    notify-send "Error" "Wallpaper download failed (too small)" -u critical
    exit 1
fi

# 格式转换 → PNG (dms 需要 PNG)
magick "$RAW_PATH" "$FINAL_PATH" || convert "$RAW_PATH" "$FINAL_PATH"
rm -f "$RAW_PATH"

# 应用壁纸（通过 DMS IPC）
dms ipc call wallpaper set "$FINAL_PATH"

# 异步钩子：更新 matugen 主题色、niri overview 背景等
(
    [ -x "$HOME/.config/scripts/matugen-update.sh" ] && \
        "$HOME/.config/scripts/matugen-update.sh" "$FINAL_PATH" || true

    sleep 0.5

    [ -x "$HOME/.config/scripts/niri_set_overview_blur_dark_bg.sh" ] && \
        "$HOME/.config/scripts/niri_set_overview_blur_dark_bg.sh" || true

    # 保留最新 40 张，清理旧的
    cd "$SAVE_DIR" && ls -t | tail -n +$((KEEP_COUNT + 1)) | xargs -I {} rm -- {} 2>/dev/null || true
) &
```

### 10.8.2 截图音效触发系统

> 信号驱动的截图音效守护进程。按下截图键 → 发 SIGUSR1 → 监听剪贴板 → 检测到图片 → 播放快门声

```bash
#!/bin/bash
# ~/.config/niri/scripts/screenshot-sound.sh

SOUND="/usr/share/sounds/freedesktop/stereo/camera-shutter.oga"
TRIGGER_FILE="/dev/shm/niri_screenshot_armed"  # 内存文件系统，超快读写
TIMEOUT_SEC=15

# 收到 SIGUSR1 信号 → 创建扳机文件
arm_trigger() {
    touch "$TRIGGER_FILE"
}
trap arm_trigger SIGUSR1

# 后台监听剪贴板变化
wl-paste --watch bash -c "
    if wl-paste --list-types 2>/dev/null | grep -q 'image/'; then
        if [ -f \"$TRIGGER_FILE\" ]; then
            NOW=\$(date +%s)
            FILE_TIME=\$(stat -c %Y \"$TRIGGER_FILE\")
            if [ \$((NOW - FILE_TIME)) -lt $TIMEOUT_SEC ]; then
                pw-play \"$SOUND\" &
                rm -f \"$TRIGGER_FILE\"
            fi
        fi
    fi
" &
WATCHER_PID=$!

trap "kill $WATCHER_PID; exit" INT TERM EXIT

echo "截图音效守护已启动，PID=$$"
while true; do sleep infinity & wait $!; done
```

**在 binds.kdl 中触发：**

```kdl
// 截图 + 发信号通知音效守护
Mod+Alt+A  { spawn-sh "niri msg action screenshot --show-pointer false && pkill -f -USR1 screenshot-sound.sh"; }
```

### 10.8.3 鼠标点击强制杀死窗口

```bash
#!/usr/bin/env bash
# ~/.config/niri/scripts/niri-force-kill-window [-f]
# -f: 杀死整个进程树（对付会自动拉起子进程的顽固程序）

# 方案：niri msg pick-window → 获取 PID + App ID
# Wayland 原生窗口 → 直接用 PID
# XWayland 代理窗口 → 用 xprop 从 X11 协议中提取真实 PID

output=$(niri msg pick-window)
pid=$(grep -oP 'PID:\s*\K\d+' <<< "$output")
process_name=$(<"/proc/$pid/comm")

if [[ "$process_name" == *"xwayland"* ]]; then
    # XWayland 窗口
    active_wid=$(xprop -root -notype _NET_ACTIVE_WINDOW | grep -o '0x[0-9a-fA-F]\+')
    real_pid=$(xprop -id "$active_wid" -notype _NET_WM_PID | grep -oP '\d+')
else
    real_pid="$pid"
fi

if [[ "$1" == "-f" ]]; then
    # 向上溯源找到应用根进程，再向下递归杀整棵树
    # ... 见原始脚本完整实现
    kill -9 $family_pids
else
    kill -9 "$real_pid"
fi
```

**按键绑定：**

```kdl
Alt+F4       { spawn "~/.config/niri/scripts/niri-force-kill-window"; }
Alt+Shift+F4 { spawn "~/.config/niri/scripts/niri-force-kill-window" "-f"; }
```

### 10.8.4 niri-pick — 窗口信息提取 + 屏幕取色

```bash
# 多功能工具：点选/聚焦窗口，提取信息并复制到剪贴板

# 提取当前焦点窗口的所有信息
niri-pick focus       → 弹出菜单选择要复制的属性(完整信息/标题/AppID/PID)

# 直接复制特定信息
niri-pick title         # 点选窗口 → 复制标题
niri-pick appid         # 点选窗口 → 复制 App ID（写窗口规则时用）
niri-pick pid           # 点选窗口 → 复制 PID

# 屏幕取色
niri-pick hex           # 吸取屏幕颜色 → 复制 HEX (#ff6bcb)
niri-pick rgb           # 吸取屏幕颜色 → 复制 RGB (rgb(255, 107, 203))

# 完整菜单
niri-pick menu          # 显示：完整信息 | 标题 | AppID | PID | HEX | RGB
```

### 10.8.5 niri-binds — 快捷键教程生成器

```bash
#!/bin/bash
# 扫描所有 .kdl 文件中的 hotkey-overlay-title 条目
# 用 fzf 展示可搜索的快捷键列表

find ~/.config/niri -name "*.kdl" -exec grep -H "hotkey-overlay-title" {} \; \
  | sed 's/.*hotkey-overlay-title="//; s/".*//' \
  | sort -u \
  | fzf --reverse --header="Niri Keybinds (Ctrl+C to exit)"
```

---

## 10.9 Niri 内置功能全集

### toggle-overview
```
Mod+O / Mod+G → 打开 Overview（所有工作区窗口全景）
```

### Niri Sidebar 扩展（侧边栏）
```bash
# 安装：paru -S niri-sidebar-git
```

```kdl
Mod+Alt+S  { spawn "niri-sidebar" "toggle-window"; }       // 收起/展开当前窗口到侧边栏
Mod+Alt+Z  { spawn "niri-sidebar" "toggle-visibility"; }    // 显示/隐藏侧边栏
Mod+Alt+X  { spawn "niri-sidebar" "flip"; }                 // 反向排序
Mod+Alt+R  { spawn "niri-sidebar" "reorder"; }              // 重新排列
```

### 列标签页模式
```kdl
Mod+Shift+X { toggle-column-tabbed-display; }
// 将列内的多个窗口以标签页形式显示
```

### 工作区相关
```kdl
// 重命名工作区（通过 DMS）
Ctrl+Shift+R { spawn "dms" "ipc" "call" "workspace-rename" "open"; }

// 滚轮切换工作区（cooldown 防抖）
Mod+Shift+WheelScrollDown cooldown-ms=150 { focus-workspace-down; }
Mod+Ctrl+Shift+WheelScrollUp cooldown-ms=150 { move-column-to-workspace-up; }
```

### 跨显示器操作
```kdl
// 焦点切换
Mod+Shift+Right { focus-monitor-right; }     // 或 Mod+Shift+L

// 跨显示器移动列
Mod+Shift+Ctrl+Right { move-column-to-monitor-right; }

// 跨显示器移动整个工作区
Mod+Shift+Alt+Right { move-workspace-to-monitor-right; }
```

---

## 10.10 环境变量调优

```kdl
environment {
    // 区域/语言
    LANG "zh_CN.UTF-8"
    LC_CTYPE "en_US.UTF-8"      // LC_CTYPE 和 LANG 分开设：中文界面 + 输入法修复

    // 输入法
    XMODIFIERS "@im=fcitx"

    // Qt 主题
    QT_QPA_PLATFORMTHEME "gtk3"

    // QuickShell 图标
    QS_ICON_THEME "Adwaita"

    // 默认编辑器
    EDITOR "vim"

    // NVIDIA 双显卡（AMD/Intel 单显卡不需要）
    // GSK_RENDERER "gl"         // 修复 GTK 应用启动慢
}
```

---

## 10.11 输入设备

```kdl
input {
    keyboard {
        xkb {}                   // 键盘布局
        repeat-delay 250         // 开始重复前等待 ms
        repeat-rate 35          // 重复率（字符/秒）
    }

    touchpad {
        tap                     // 轻触=点击
        natural-scroll          // 自然滚动（Mac 风格）
        // dwt                   // 打字时禁用触摸板
    }

    mouse {
        accel-speed -0.15       // 负值=减速
        accel-profile "flat"    // 无加速度（精准控制）
    }

    trackpoint {
        // off
        // natural-scroll
    }
}
```

---

## 10.12 光标配置

```kdl
cursor {
    xcursor-theme "breeze_cursors"
    xcursor-size 30
    hide-after-inactive-ms 15000   // 15 秒不动自动隐藏
}
```

---

## 10.13 Niri IPC 调试

```bash
# 发送指令
niri msg action quit
niri msg action focus-workspace 3
niri msg action screenshot
niri msg action toggle-overview

# 查看信息
niri msg outputs               # 显示器信息 (JSON)
niri msg windows               # 所有窗口 (JSON，含 app_id/title/pid)
niri msg focused-window        # 焦点窗口信息
niri msg keyboard-layouts      # 当前键盘布局

# 实时事件流（脚本自动化用）
niri msg event-stream
# 输出示例：
# WindowOpened { id: 12 }
# WorkspaceFocused { id: 3 }
# WindowClosed { id: 8 }

# 获取截图
niri msg screenshot            # 交互式选区截图 → 保存到 screenshot-path
```

---

## 10.14 常见问题排查

```bash
# 配置语法检查
niri validate    # 会报告语法错误和具体行号

# 日志
journalctl -u niri -f --user    # 用户服务
# 或直接运行看 stderr
niri-session 2>&1 | tee niri-debug.log

# 嵌套模式（在现有图形会话中开窗口测试，不用切 session）
niri --session

# 获取窗口 app-id（编写 window-rule 必需）
niri msg windows
# grep 出感兴趣的 app_id

# 获取窗口标题（正则匹配用）
niri msg focused-window
# 输出：Title: "Firefox"

# 性能统计
niri msg debug-stats   # FPS、渲染耗时等
```

---

## 10.15 本章测验

> [!example] 📝 自测题目

> [!question]- 选择题 1：Niri 的配置文件使用什么格式？
> - A. TOML
> - B. YAML
> - C. KDL
> - D. JSON
>
> > [!success]- 点击查看答案
> > **C**
> > Niri 使用 KDL (KDL Document Language) 格式作为配置文件格式，主配置文件为 config.kdl。

> [!question]- 选择题 2：Niri 模糊效果中，xray=true 的含义是什么？
> - A. 实时模糊窗口背后的真实内容
> - B. 只渲染一次模糊版的壁纸作为假壁纸贴在窗口后面
> - C. 完全禁用模糊效果
> - D. 仅在全屏时启用模糊
>
> > [!success]- 点击查看答案
> > **B**
> > xray=true 模式只渲染一次模糊版的壁纸作为"假壁纸"贴在窗口后面，零性能消耗。xray=false 才是实时模糊窗口背后的真实内容。

> [!question]- 选择题 3：Niri 弹簧动画中，damping-ratio=1.0 表示什么效果？
> - A. 回弹非常明显
> - B. 刚好不弹（临界阻尼）
> - C. 完全无动画
> - D. 极度过阻尼
>
> > [!success]- 点击查看答案
> > **B**
> > damping-ratio=1.0 表示临界阻尼，即刚好不弹。小于 1.0 会有回弹效果，大于 1.0 是过阻尼。

> [!question]- 判断题 4：在 Niri 中，spawn-sh 和 spawn 的区别是 spawn-sh 支持 shell 语法如 && / || / $() 等
> - A. ✓ 正确
> - B. ✗ 错误
>
> > [!success]- 点击查看答案
> > **A. ✓ 正确**
> > spawn 直接启动程序，spawn-sh 运行 shell 命令，支持 && / || / $() 等 shell 语法。

> [!question]- 选择题 5：Niri 中 cooldown-ms=150 的作用是什么？
> - A. 延迟 150ms 后执行动作
> - B. 防止 150ms 内连续触发同一快捷键
> - C. 动画持续 150ms
> - D. 窗口打开后 150ms 才接收输入
>
> > [!success]- 点击查看答案
> > **B**
> > cooldown-ms=150 用于防止 150ms 内连续触发，常用于滚轮切换工作区等防误触场景。

> [!question]- 判断题 6：Niri 的 window-rule 中 opacity 0.99 是为了让 niri 知道此窗口透明从而启用混合模式
> - A. ✓ 正确
> - B. ✗ 错误
>
> > [!success]- 点击查看答案
> > **A. ✓ 正确**
> > 设置 opacity 0.99 虽然视觉上几乎不透明，但让 niri 知道此窗口需要透明处理从而启用混合渲染模式。

> [!question]- 选择题 7：Niri 中用什么命令进行配置语法检查？
> - A. niri msg check
> - B. niri validate
> - C. niri --check-config
> - D. niri msg action validate
>
> > [!success]- 点击查看答案
> > **B**
> > 使用 `niri validate` 可以检查配置语法错误，会报告具体行号。

> [!question]- 选择题 8：在 recent-windows (Super+Tab) 配置中，scope="workspace" 表示什么？
> - A. 切换所有显示器的所有窗口
> - B. 仅切换当前工作区的窗口
> - C. 仅切换当前显示器上所有工作区的窗口
> - D. 按应用分组切换
>
> > [!success]- 点击查看答案
> > **B**
> > scope="workspace" 表示仅在当前工作区范围内切换窗口。scope="monitor" 是当前显示器所有工作区，不写则是全部窗口。

> [!question]- 判断题 9：Niri 的截图音效系统使用 SIGUSR1 信号驱动，通过监听剪贴板变化来检测截图完成
> - A. ✓ 正确
> - B. ✗ 错误
>
> > [!success]- 点击查看答案
> > **A. ✓ 正确**
> > 截图音效守护进程收到 SIGUSR1 信号后创建扳机文件，wl-paste --watch 监听剪贴板变化，检测到图片类型时播放快门声。

> [!question]- 选择题 10：Niri 中 repeat=false 的作用是什么？
> - A. 禁止动画重复播放
> - B. 禁止长按时连续触发该快捷键
> - C. 只允许执行一次后自动解绑
> - D. 禁止在多个窗口上重复执行
>
> > [!success]- 点击查看答案
> > **B**
> > repeat=false 禁止长按时连续触发该快捷键，常用于 close-window 等不应因长按而重复执行的操作。
