# 38 - Wayland 深入指南

> Wayland 是 Linux 下一代显示协议，旨在取代已有数十年历史的 X11/Xorg。它以更简洁的架构、更好的安全性和更流畅的图形体验重新定义了 Linux 桌面的显示栈。本章将深入探讨 Wayland 的协议细节、合成器生态、XWayland 兼容层、底层显示接口、屏幕共享与录制、输入法支持以及常见问题排查，帮助你全面掌握 Wayland 环境的配置与开发。

---

## 38.1 Wayland 协议基础回顾

### X11 的历史包袱

X Window System（X11）诞生于 1984 年，其架构基于 C/S 模型：

```
┌──────────┐ 请求/事件 ┌──────────┐ 渲染 ┌──────────┐
│ X Client │ ◄────────────► │ X Server │ ────────► │ GPU │
└──────────┘ └──────────┘ └──────────┘
 │
 ┌─────┴─────┐
 │ Window │
 │ Manager │
 └───────────┘
```

X11 的主要问题：

| 问题 | 描述 |
|------|------|
| 过度复杂 | 服务端渲染、字体管理等历史遗留功能 |
| 安全性差 | 任意客户端可截取其他窗口输入、截屏 |
| 性能瓶颈 | 合成需要额外的合成管理器（Compositor） |
| 撕裂问题 | 无原生 VSync 支持 |
| 协议臃肿 | 核心协议 + 大量扩展（XRandR、XInput2、XComposite 等） |

### Wayland 的架构

Wayland 将显示服务器和窗口管理器合二为一，称为 **合成器（Compositor）**：

```
┌──────────┐ Wayland 协议 ┌─────────────┐ DRM/KMS ┌──────────┐
│ Client │ ◄───────────────► │ Compositor │ ────────────► │ GPU │
└──────────┘ │ (Server + │ └──────────┘
 │ WM 合一) │
 └─────────────┘
```

核心优势：

- **客户端渲染**：客户端自行渲染，合成器仅负责合成和显示
- **安全隔离**：客户端不能访问其他客户端的输入或缓冲区
- **原生合成**：无撕裂，内建 VSync
- **协议简洁**：按需扩展，避免臃肿

### 对比总结

| 特性 | X11 | Wayland |
|------|-----|---------|
| 渲染模型 | 服务端渲染（已过时） | 客户端渲染 |
| 安全性 | 弱（全局访问） | 强（隔离） |
| 合成 | 可选（Picom 等） | 内建 |
| 网络透明 | 原生支持 | 不直接支持（需 waypipe） |
| 屏幕共享 | 简单（X11 grab） | 需要 portal |
| 输入法 | XIM/IBus | text-input 协议 |
| HiDPI | 补丁式支持 | 原生分数缩放 |
| 剪贴板 | X Selections | wl-clipboard |

---

## 38.2 Wayland 协议细节

Wayland 协议基于 **对象（Object）** 和 **接口（Interface）** 的概念，通过 Unix 域套接字进行通信。

### wl_display

`wl_display` 是客户端与合成器通信的入口点：

```c
#include <wayland-client.h>

struct wl_display *display = wl_display_connect(NULL);
if (!display) {
 fprintf(stderr, "无法连接到 Wayland 合成器\n");
 return 1;
}

// 获取文件描述符（用于事件循环集成）
int fd = wl_display_get_fd(display);

// 事件分发
wl_display_dispatch(display);

// 刷新请求
wl_display_flush(display);

// 断开连接
wl_display_disconnect(display);
```

连接时使用的 socket 路径由 `WAYLAND_DISPLAY` 环境变量指定，默认为 `wayland-0`，完整路径为 `$XDG_RUNTIME_DIR/$WAYLAND_DISPLAY`。

### wl_registry

`wl_registry` 用于发现合成器提供的全局对象：

```c
static void registry_handle_global(void *data, struct wl_registry *registry,
 uint32_t name, const char *interface,
 uint32_t version) {
 if (strcmp(interface, "wl_compositor") == 0) {
 compositor = wl_registry_bind(registry, name,
 &wl_compositor_interface, 4);
 } else if (strcmp(interface, "wl_shm") == 0) {
 shm = wl_registry_bind(registry, name,
 &wl_shm_interface, 1);
 } else if (strcmp(interface, "xdg_wm_base") == 0) {
 xdg_wm_base = wl_registry_bind(registry, name,
 &xdg_wm_base_interface, 1);
 }
}

static void registry_handle_global_remove(void *data,
 struct wl_registry *registry,
 uint32_t name) {
 // 全局对象被移除
}

static const struct wl_registry_listener registry_listener = {
 .global = registry_handle_global,
 .global_remove = registry_handle_global_remove,
};

struct wl_registry *registry = wl_display_get_registry(display);
wl_registry_add_listener(registry, &registry_listener, NULL);
wl_display_roundtrip(display);
```

查看合成器支持的全局接口：

```bash
# 使用 wayland-info 工具
sudo pacman -S wayland-utils
wayland-info
```

### wl_surface

`wl_surface` 是 Wayland 中最核心的对象，代表一个可见的矩形区域：

```c
struct wl_surface *surface = wl_compositor_create_surface(compositor);

// 附加缓冲区
wl_surface_attach(surface, buffer, 0, 0);

// 标记损坏区域
wl_surface_damage_buffer(surface, 0, 0, width, height);

// 提交状态
wl_surface_commit(surface);
```

`wl_surface` 使用 **双缓冲** 状态模型——所有修改在 `commit` 之前不会生效。

### 缓冲区管理

#### wl_shm（共享内存）

适用于 CPU 渲染的软件缓冲区：

```c
// 1. 创建共享内存文件
int fd = shm_open("/wl_shm_buffer", O_RDWR | O_CREAT | O_EXCL, 0600);
shm_unlink("/wl_shm_buffer");
ftruncate(fd, size);

// 2. 映射到内存
void *data = mmap(NULL, size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);

// 3. 创建 wl_shm_pool
struct wl_shm_pool *pool = wl_shm_create_pool(shm, fd, size);

// 4. 从 pool 创建 buffer
struct wl_buffer *buffer = wl_shm_pool_create_buffer(
 pool, 0, width, height, stride, WL_SHM_FORMAT_ARGB8888);
```

#### DMA-BUF（linux-dmabuf 协议）

用于 GPU 零拷贝缓冲区传递，性能远优于 wl_shm：

```
客户端 GPU 渲染 → DMA-BUF fd → 合成器直接引用 GPU 缓冲区
```

支持的协议接口：`zwp_linux_dmabuf_v1`

### 输入事件处理

Wayland 输入通过 `wl_seat` 对象管理：

```c
// wl_seat 包含三类输入设备
struct wl_pointer *pointer; // 鼠标
struct wl_keyboard *keyboard; // 键盘
struct wl_touch *touch; // 触摸屏

// 键盘事件回调
static void keyboard_key(void *data, struct wl_keyboard *keyboard,
 uint32_t serial, uint32_t time,
 uint32_t key, uint32_t state) {
 // key: Linux 键码（evdev）
 // state: WL_KEYBOARD_KEY_STATE_PRESSED / RELEASED
}

// 键盘 keymap 回调（xkbcommon 格式）
static void keyboard_keymap(void *data, struct wl_keyboard *keyboard,
 uint32_t format, int fd, uint32_t size) {
 // format == WL_KEYBOARD_KEYMAP_FORMAT_XKB_V1
 // fd 指向 xkb keymap 文件
}
```

### 协议扩展

Wayland 核心协议非常精简，大量功能通过扩展协议提供：

| 协议 | 用途 | 状态 |
|------|------|------|
| `xdg-shell` | 窗口管理（toplevel、popup） | 稳定 |
| `xdg-decoration` | 服务端装饰 | 稳定 |
| `xdg-output` | 输出信息 | 稳定 |
| `wlr-layer-shell` | 面板、壁纸、锁屏层 | wlroots 专有 |
| `ext-session-lock-v1` | 安全锁屏 | 标准化中 |
| `zwp_linux_dmabuf_v1` | GPU 缓冲区 | 稳定 |
| `wp-fractional-scale-v1` | 分数缩放 | 稳定 |
| `zwp_text_input_v3` | 输入法 | 稳定 |
| `ext-idle-notify-v1` | 空闲检测 | 标准化 |
| `wp-content-type-v1` | 内容类型提示 | 稳定 |
| `wp-tearing-control-v1` | 允许撕裂（游戏） | 稳定 |
| `zwlr-screencopy-v1` | 屏幕截图 | wlroots 专有 |

#### xdg-shell 示例

```c
struct xdg_surface *xdg_surface =
 xdg_wm_base_get_xdg_surface(xdg_wm_base, surface);

struct xdg_toplevel *toplevel =
 xdg_surface_get_toplevel(xdg_surface);

xdg_toplevel_set_title(toplevel, "我的 Wayland 应用");
xdg_toplevel_set_app_id(toplevel, "com.example.myapp");

wl_surface_commit(surface);
```

#### layer-shell

`wlr-layer-shell` 用于创建特殊层面的窗口：

```
┌─────────────────────────────────┐
│ Overlay 层（通知） │
│ ┌───────────────────────────┐ │
│ │ Top 层（面板） │ │
│ │ ┌───────────────────┐ │ │
│ │ │ Bottom 层（Dock） │ │ │
│ │ │ ┌─────────────┐ │ │ │
│ │ │ │ Background │ │ │ │
│ │ │ │ （壁纸） │ │ │ │
│ │ │ └─────────────┘ │ │ │
│ │ └───────────────────┘ │ │
│ └───────────────────────────┘ │
└─────────────────────────────────┘
```

### 私有协议 vs 标准化协议

| 类型 | 前缀 | 示例 | 特点 |
|------|------|------|------|
| 核心协议 | `wl_` | `wl_surface` | Wayland 标准 |
| 标准扩展 | `wp_`/`ext_` | `wp_viewporter` | wayland-protocols 仓库 |
| wlroots 私有 | `zwlr_` | `zwlr_layer_shell_v1` | 仅 wlroots 合成器 |
| KDE 私有 | `org_kde_` | `org_kde_plasma_shell` | 仅 KWin |
| GNOME 私有 | — | Mutter 内部 API | 仅 Mutter |
| 非稳定 | `zwp_`/`z` 前缀 | `zwp_text_input_v3` | 实验阶段 |

标准化流程：`私有实现 → wayland-protocols staging → stable`

---

## 38.3 Wayland 合成器生态

### wlroots 生态

[wlroots](https://gitlab.freedesktop.org/wlroots/wlroots) 是一个模块化 Wayland 合成器库，大量合成器基于它构建：

| 合成器 | 类型 | 特点 | 安装 |
|--------|------|------|------|
| Sway | i3 兼容平铺 | 最成熟的 wlroots 合成器 | `pacman -S sway` |
| Hyprland | 动态平铺 | 动画丰富、高度可定制 | `pacman -S hyprland` |
| Niri | 滚动平铺 | 无限横向滚动 | `pacman -S niri` |
| River | 动态平铺 | 可编程布局 | `pacman -S river` |
| dwl | dwm 风格 | 极简、C 源码补丁 | AUR: `dwl` |
| labwc | Openbox 风格 | 浮动窗口管理 | `pacman -S labwc` |
| cage | 单窗口 kiosk | 嵌入式/展示用 | `pacman -S cage` |
| wayfire | 3D 特效 | 类似 Compiz | `pacman -S wayfire` |

#### Sway 配置示例

```bash
# ~/.config/sway/config

# 输出配置
output HDMI-A-1 resolution 2560x1440@144Hz position 0,0
output eDP-1 resolution 1920x1080 position 2560,0 scale 1.25

# 输入配置
input "type:touchpad" {
 tap enabled
 natural_scroll enabled
 dwt enabled
}

input "type:keyboard" {
 xkb_layout us
 repeat_delay 300
 repeat_rate 50
}

# 快捷键
bindsym $mod+Return exec foot
bindsym $mod+d exec wofi --show drun
bindsym $mod+Shift+s exec grim -g "$(slurp)" - | wl-copy
```

#### Hyprland 配置示例

```ini
# ~/.config/hypr/hyprland.conf

monitor = DP-1, 2560x1440@165, 0x0, 1
monitor = HDMI-A-1, 1920x1080@60, 2560x0, 1

input {
 kb_layout = us
 follow_mouse = 1
 touchpad {
 natural_scroll = true
 }
}

general {
 gaps_in = 5
 gaps_out = 10
 border_size = 2
 col.active_border = rgba(33ccffee) rgba(00ff99ee) 45deg
}

animations {
 enabled = true
 bezier = myBezier, 0.05, 0.9, 0.1, 1.05
 animation = windows, 1, 7, myBezier
 animation = fade, 1, 7, default
}

bind = SUPER, Return, exec, kitty
bind = SUPER, Q, killactive
bind = SUPER, D, exec, wofi --show drun
```

### Mutter（GNOME）

Mutter 是 GNOME 的合成器，不使用 wlroots，完全独立实现：

```bash
# GNOME Wayland 会话
sudo pacman -S gnome

# 登录管理器中选择 "GNOME" 而非 "GNOME on Xorg"

# 检查是否运行在 Wayland 下
echo $XDG_SESSION_TYPE
# 输出: wayland

# GNOME 特有设置
gsettings set org.gnome.mutter experimental-features "['scale-monitor-framebuffer']"
```

### KWin（KDE Plasma）

```bash
sudo pacman -S plasma

# Plasma 6 默认使用 Wayland
# 配置分数缩放
# 系统设置 → 显示和监控 → 缩放

# KWin 脚本接口
qdbus org.kde.KWin /KWin supportInformation
```

### Weston（参考实现）

```bash
sudo pacman -S weston

# 在 TTY 中直接运行
weston

# 或嵌套在已有 Wayland 会话中
weston --backend=wayland

# 配置文件
# ~/.config/weston.ini
```

```ini
# ~/.config/weston.ini
[core]
shell=desktop-shell.so

[output]
name=HDMI-A-1
mode=1920x1080@60
transform=normal

[shell]
panel-position=top
background-color=0xff002244
```

---

## 38.4 XWayland（运行 X11 应用）

### 工作原理

XWayland 是一个特殊的 X 服务器，作为 Wayland 客户端运行：

```
┌──────────┐ X11 协议 ┌──────────┐ Wayland 协议 ┌─────────────┐
│ X11 App │ ───────────► │ XWayland │ ─────────────► │ Wayland │
│ │ │ (X 服务器)│ │ Compositor │
└──────────┘ └──────────┘ └─────────────┘
```

XWayland 将 X11 窗口映射为 Wayland surface，使传统 X11 应用无需修改即可运行。

### 安装与配置

```bash
# 安装 XWayland
sudo pacman -S xorg-xwayland

# Sway 中启用（默认已启用）
# ~/.config/sway/config
xwayland enable

# Hyprland 中配置
# ~/.config/hypr/hyprland.conf
xwayland {
 force_zero_scaling = true
}
```

### 识别 XWayland 应用

```bash
# 方法 1：使用 xprop（仅对 X11 窗口有效）
xprop
# 如果能选中窗口并显示属性，说明是 XWayland 应用

# 方法 2：使用 xlsclients
xlsclients

# 方法 3：在 Sway 中查看
swaymsg -t get_tree | jq '.. | select(.shell? == "xwayland")'

# 方法 4：Hyprland
hyprctl clients | grep -A5 "xwayland"

# 常见的 XWayland 应用
# - Electron 旧版本（Chromium 基础）
# - 部分游戏（Steam、Wine/Proton）
# - 部分 Java 应用
# - 某些 Qt5 应用（未启用 Wayland 后端）
```

### Rootless XWayland

现代合成器默认使用 rootless XWayland，每个 X11 窗口作为独立的 Wayland surface：

```bash
# 查看 XWayland 进程
ps aux | grep Xwayland
# Xwayland :0 -rootless -terminate ...

# rootless 模式的优势：
# - 每个窗口独立管理
# - 支持合成器特效
# - 更好的多显示器支持
```

### HiDPI 下的 XWayland

XWayland 应用在 HiDPI 下可能模糊：

```bash
# Sway：全局整数缩放
output eDP-1 scale 2

# XWayland 应用的 HiDPI 处理
# 方法 1：强制应用使用原生 Wayland
# GTK 应用
export GDK_BACKEND=wayland
# Qt 应用
export QT_QPA_PLATFORM=wayland

# 方法 2：Hyprland 的 XWayland 缩放
xwayland {
 force_zero_scaling = true
}
# 同时设置 Xft.dpi
env = GDK_SCALE,2
```

---

## 38.5 显示协议

### DRM/KMS 内核接口

DRM（Direct Rendering Manager）和 KMS（Kernel Mode Setting）是 Linux 显示栈的内核层：

```
用户空间
┌────────────────────────────────┐
│ Wayland Compositor │
│ ┌──────────┐ ┌───────────┐ │
│ │ libdrm │ │ Mesa/EGL │ │
│ └────┬─────┘ └─────┬─────┘ │
└─────────┼─────────────┼────────┘
 │ ioctl │ ioctl
──────────┼─────────────┼────────── 内核边界
 ▼ ▼
┌────────────────────────────────┐
│ DRM 子系统 │
│ ┌─────────┐ ┌─────────────┐ │
│ │ KMS │ │ GEM/TTM │ │
│ │ (显示) │ │ (缓冲区) │ │
│ └─────────┘ └─────────────┘ │
└────────────────────────────────┘
 │
 ▼
┌────────────────────────────────┐
│ GPU 硬件驱动 │
│ amdgpu / i915 / nouveau │
└────────────────────────────────┘
```

KMS 的核心对象：

| 对象 | 说明 |
|------|------|
| CRTC | 显示控制器（扫描引擎） |
| Encoder | 信号编码器（TMDS、LVDS 等） |
| Connector | 物理输出（HDMI、DP、eDP） |
| Plane | 显示平面（primary、cursor、overlay） |
| Framebuffer | 帧缓冲区 |

```bash
# 查看 DRM 设备
ls /dev/dri/
# card0 card1 renderD128 renderD129

# 查看 KMS 状态
sudo cat /sys/kernel/debug/dri/0/state

# 列出连接器和模式
sudo pacman -S libdrm
modetest -c
modetest -p
```

### GBM（Generic Buffer Management）

GBM 提供与 EGL 集成的缓冲区分配接口：

```c
#include <gbm.h>

struct gbm_device *gbm = gbm_create_device(drm_fd);

struct gbm_surface *gbm_surface = gbm_surface_create(
 gbm, width, height, GBM_FORMAT_XRGB8888,
 GBM_BO_USE_SCANOUT | GBM_BO_USE_RENDERING);

// 与 EGL 关联
EGLSurface egl_surface = eglCreatePlatformWindowSurface(
 egl_display, egl_config, gbm_surface, NULL);
```

### EGL 与 OpenGL ES

Wayland 合成器通常使用 EGL + OpenGL ES 进行渲染和合成：

```bash
# 查看 EGL 信息
eglinfo

# 查看支持的 Wayland EGL 扩展
EGL_WL_bind_wayland_display # 合成器绑定 Wayland display
EGL_EXT_image_dma_buf_import # 导入 DMA-BUF
```

```c
// 合成器侧 EGL 初始化
EGLDisplay egl_display = eglGetPlatformDisplay(
 EGL_PLATFORM_GBM_KHR, gbm_device, NULL);
eglInitialize(egl_display, &major, &minor);

// 绑定 OpenGL ES API
eglBindAPI(EGL_OPENGL_ES_API);

// 创建上下文
EGLContext ctx = eglCreateContext(egl_display, config,
 EGL_NO_CONTEXT, ctx_attribs);
```

### Vulkan WSI

Vulkan 通过 WSI（Window System Integration）扩展支持 Wayland：

```bash
# 检查 Vulkan Wayland 支持
vulkaninfo | grep -i wayland
# VK_KHR_wayland_surface

# 安装 Vulkan 驱动
sudo pacman -S vulkan-radeon # AMD
sudo pacman -S vulkan-intel # Intel
sudo pacman -S nvidia-utils # NVIDIA（包含 Vulkan）
```

```c
// Vulkan Wayland surface 创建
VkWaylandSurfaceCreateInfoKHR surface_info = {
 .sType = VK_STRUCTURE_TYPE_WAYLAND_SURFACE_CREATE_INFO_KHR,
 .display = wl_display,
 .surface = wl_surface,
};
vkCreateWaylandSurfaceKHR(instance, &surface_info, NULL, &vk_surface);
```

---

## 38.6 屏幕共享与录制

### xdg-desktop-portal

xdg-desktop-portal 是 Wayland 下屏幕共享的标准机制：

```bash
# 安装对应合成器的 portal 后端
sudo pacman -S xdg-desktop-portal-wlr # Sway、River 等 wlroots 合成器
sudo pacman -S xdg-desktop-portal-hyprland # Hyprland
sudo pacman -S xdg-desktop-portal-gtk # GNOME / 其他 GTK 环境
sudo pacman -S xdg-desktop-portal-kde # KDE Plasma

# 确保 portal 服务运行
systemctl --user status xdg-desktop-portal
systemctl --user status xdg-desktop-portal-wlr

# portal 配置
# ~/.config/xdg-desktop-portal/portals.conf
```

```ini
# ~/.config/xdg-desktop-portal/portals.conf
[preferred]
default=gtk
org.freedesktop.impl.portal.Screenshot=wlr
org.freedesktop.impl.portal.ScreenCast=wlr
```

### PipeWire 屏幕捕获

屏幕共享通过 PipeWire 视频流传递：

```
应用请求共享 → xdg-desktop-portal → 用户选择区域 → PipeWire 视频流 → 应用接收
```

```bash
# 确保 PipeWire 运行
systemctl --user status pipewire

# 查看 PipeWire 视频节点
pw-cli list-objects | grep -i video
```

### OBS Studio Wayland 配置

```bash
# 安装 OBS
sudo pacman -S obs-studio

# OBS 原生支持 Wayland（PipeWire 屏幕捕获）
# 添加源 → 屏幕录制 (PipeWire)

# 确保使用 Wayland 后端启动
QT_QPA_PLATFORM=wayland obs

# 如果使用 wlroots 合成器，安装 wlr 插件（如需要）
sudo pacman -S obs-studio
# OBS 30+ 已内建 PipeWire 支持
```

### 截图与录屏工具

```bash
# grim - 截图
sudo pacman -S grim
grim screenshot.png # 全屏截图
grim -o eDP-1 output.png # 指定输出
grim -g "100,100 500x300" region.png # 指定区域

# slurp - 交互式区域选择
sudo pacman -S slurp
grim -g "$(slurp)" screenshot.png # 选择区域截图

# 截图到剪贴板
grim -g "$(slurp)" - | wl-copy

# wf-recorder - 屏幕录制
sudo pacman -S wf-recorder
wf-recorder -o eDP-1 -f recording.mp4 # 录制指定输出
wf-recorder -g "$(slurp)" -f region.mp4 # 录制选定区域
wf-recorder -a -f with-audio.mp4 # 含音频录制

# wayshot - 高性能截图
sudo pacman -S wayshot
wayshot -s "$(slurp -f '%x %y %w %h')"
```

---

## 38.7 剪贴板管理

Wayland 的剪贴板与 X11 完全不同，需要专用工具：

```bash
# 安装 wl-clipboard
sudo pacman -S wl-clipboard

# 复制文本
echo "Hello Wayland" | wl-copy

# 复制文件内容
wl-copy < file.txt

# 复制图片
wl-copy -t image/png < screenshot.png

# 粘贴
wl-paste
wl-paste -n # 不追加换行
wl-paste -t image/png > pasted.png

# 监听剪贴板变化
wl-paste --watch cat

# 清除剪贴板
wl-copy --clear

# 剪贴板管理器
sudo pacman -S cliphist

# 配合 wl-paste 使用
wl-paste --watch cliphist store # 后台运行存储历史
cliphist list | wofi --dmenu | cliphist decode | wl-copy # 选择历史
```

Primary selection（中键粘贴）：

```bash
# wl-copy/wl-paste 支持 primary selection
wl-copy --primary "primary selection text"
wl-paste --primary
```

---

## 38.8 输入法框架

### Fcitx5 Wayland 原生支持

```bash
# 安装 fcitx5
sudo pacman -S fcitx5 fcitx5-chinese-addons fcitx5-configtool fcitx5-gtk fcitx5-qt

# 环境变量配置
# ~/.config/environment.d/input-method.conf（systemd 用户环境）
```

```ini
# ~/.config/environment.d/input-method.conf
XMODIFIERS=@im=fcitx
GTK_IM_MODULE=fcitx
QT_IM_MODULE=fcitx
SDL_IM_MODULE=fcitx
INPUT_METHOD=fcitx
```

```bash
# 自动启动
# Sway
# ~/.config/sway/config
exec --no-startup-id fcitx5 -d

# Hyprland
# ~/.config/hypr/hyprland.conf
exec-once = fcitx5 -d --replace

# 检查 Wayland 输入法协议支持
fcitx5-diagnose | grep -A5 "Wayland"

# Fcitx5 支持的 Wayland 输入协议：
# - zwp_input_method_v2 （推荐）
# - zwp_text_input_v3
# - zwp_input_method_v1 （旧版）
```

Wayland 下输入法的已知限制：

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| Electron 应用无法使用输入法 | text-input 协议不完整 | 使用 `--enable-wayland-ime` 标志 |
| XWayland 应用输入法 | XWayland 使用 XIM | 确保设置 `XMODIFIERS` |
| 某些 GTK4 应用 | GTK4 IM Module 变化 | 使用 `gtk4-im-fcitx5` |

```bash
# Electron 应用（如 VS Code、Discord）启用输入法
code --enable-wayland-ime
# 或修改 .desktop 文件
# Exec=code --enable-wayland-ime --ozone-platform=wayland
```

---

## 38.9 Wayland 环境变量

```bash
# 核心 Wayland 变量
export WAYLAND_DISPLAY=wayland-0 # Wayland socket 名
export XDG_SESSION_TYPE=wayland # 会话类型
export XDG_CURRENT_DESKTOP=sway # 当前桌面

# 强制应用使用 Wayland
export GDK_BACKEND=wayland # GTK 应用
export QT_QPA_PLATFORM=wayland # Qt 应用
export SDL_VIDEODRIVER=wayland # SDL 应用
export CLUTTER_BACKEND=wayland # Clutter 应用
export MOZ_ENABLE_WAYLAND=1 # Firefox
export ELECTRON_OZONE_PLATFORM_HINT=auto # Electron（Chromium 系）

# XWayland 相关
export DISPLAY=:0 # XWayland display
export XAUTHORITY # X 认证文件（XWayland 自动设置）

# 调试
export WAYLAND_DEBUG=1 # 启用 Wayland 协议调试日志
export WAYLAND_DEBUG=client # 仅客户端日志
export WAYLAND_DEBUG=server # 仅服务端日志
export LIBSEAT_LOGLEVEL=debug # libseat 调试
```

检测当前会话类型的脚本：

```bash
#!/bin/bash
if [ "$XDG_SESSION_TYPE" = "wayland" ]; then
 echo "当前运行在 Wayland 会话中"
 echo "合成器: ${XDG_CURRENT_DESKTOP:-未知}"
 echo "Socket: ${WAYLAND_DISPLAY:-wayland-0}"
 echo "XWayland DISPLAY: ${DISPLAY:-未设置}"
elif [ "$XDG_SESSION_TYPE" = "x11" ]; then
 echo "当前运行在 X11 会话中"
 echo "DISPLAY: $DISPLAY"
else
 echo "未知会话类型: ${XDG_SESSION_TYPE:-未设置}"
fi
```

---

## 38.10 应用兼容性检查清单

| 应用类别 | 应用 | Wayland 支持 | 备注 |
|----------|------|-------------|------|
| 浏览器 | Firefox | 原生 | `MOZ_ENABLE_WAYLAND=1` |
| 浏览器 | Chromium | 原生 | `--ozone-platform=wayland` |
| 终端 | foot | 原生 | Wayland 原生终端 |
| 终端 | kitty | 原生 | 完整 Wayland 支持 |
| 终端 | Alacritty | 原生 | 完整 Wayland 支持 |
| 编辑器 | VS Code | Electron | `--ozone-platform=wayland` |
| 编辑器 | Neovim | 终端应用 | 取决于终端 |
| 文件管理 | Nautilus | 原生 | GTK4/libadwaita |
| 文件管理 | Thunar | 原生 | GTK3 |
| 文件管理 | Dolphin | 原生 | Qt6/KDE |
| 办公 | LibreOffice | 原生 | `SAL_USE_VCLPLUGIN=gtk3` |
| 媒体 | mpv | 原生 | 默认 Wayland |
| 媒体 | VLC | 原生 | Qt Wayland |
| 游戏 | Steam | XWayland | 游戏多数用 XWayland |
| 游戏 | Wine/Proton | 有限 | 可选 Wayland 驱动 |
| 通讯 | Discord | Electron | `--ozone-platform=wayland` |
| 通讯 | Telegram | 原生 | Qt Wayland |
| 图形 | GIMP | XWayland | GTK2，不支持 Wayland |
| 图形 | Inkscape | 原生 | GTK3 |
| 虚拟化 | virt-manager | 原生 | GTK3 |

```bash
# 检查应用是否使用 Wayland 或 XWayland
# 方法：使用 xlsclients 查看 XWayland 客户端
xlsclients

# 或在 Sway 中
swaymsg -t get_tree | jq -r '.. | select(.type? == "con") | "\(.app_id // .window_properties.class) → \(.shell)"'
```

---

## 38.11 常见问题排查

### 屏幕闪烁

```bash
# 原因 1：NVIDIA 驱动问题
# 确保使用正确的驱动和内核模块参数
sudo vim /etc/modprobe.d/nvidia.conf
```

```
options nvidia_drm modeset=1 fbdev=1
```

```bash
# 原因 2：VRR（可变刷新率）问题
# Sway 中禁用 VRR
output HDMI-A-1 adaptive_sync off

# 原因 3：合成器渲染后端问题
# Sway 使用 Vulkan 渲染后端
WLR_RENDERER=vulkan sway
```

### 分数缩放

```bash
# Sway 仅支持整数缩放（原生）
output eDP-1 scale 2

# Hyprland 支持分数缩放
monitor = eDP-1, 1920x1080, 0x0, 1.25

# GNOME 分数缩放
gsettings set org.gnome.mutter experimental-features "['scale-monitor-framebuffer']"

# 针对 XWayland 应用的模糊问题
# 设置 Xft.dpi
echo "Xft.dpi: 120" | xrdb -merge
```

### 触摸板配置

```bash
# Sway
input "type:touchpad" {
 tap enabled
 natural_scroll enabled
 scroll_method two_finger
 pointer_accel 0.3
 accel_profile adaptive
 dwt enabled # 打字时禁用触摸板
 click_method clickfinger
 middle_emulation enabled
}

# Hyprland
input {
 touchpad {
 natural_scroll = true
 disable_while_typing = true
 tap-to-click = true
 scroll_factor = 0.8
 }
}
```

### 多显示器

```bash
# Sway 多显示器
output DP-1 resolution 2560x1440@165Hz position 0,0
output HDMI-A-1 resolution 1920x1080@60Hz position 2560,0

# 工作区绑定到显示器
workspace 1 output DP-1
workspace 2 output DP-1
workspace 9 output HDMI-A-1
workspace 10 output HDMI-A-1

# 查看可用输出
swaymsg -t get_outputs
# Hyprland
hyprctl monitors

# 热插拔处理
# Sway 自动处理热插拔
# kanshi 可用于自动切换配置
sudo pacman -S kanshi
```

```ini
# ~/.config/kanshi/config
profile docked {
 output eDP-1 disable
 output DP-1 mode 2560x1440@165Hz position 0,0
 output HDMI-A-1 mode 1920x1080@60Hz position 2560,0
}

profile undocked {
 output eDP-1 enable mode 1920x1080 position 0,0
}
```

### NVIDIA 专项

```bash
# 必要的环境变量
export GBM_BACKEND=nvidia-drm
export __GLX_VENDOR_LIBRARY_NAME=nvidia
export WLR_NO_HARDWARE_CURSORS=1 # 如果硬件光标有问题

# 内核参数
# /etc/default/grub
GRUB_CMDLINE_LINUX="nvidia_drm.modeset=1 nvidia_drm.fbdev=1"

# 重建 initramfs
sudo mkinitcpio -P

# 确认模式设置
cat /sys/module/nvidia_drm/parameters/modeset
# Y
```

---

## 38.12 开发 Wayland 客户端入门

### 最小 Wayland 客户端（C）

```bash
# 安装开发依赖
sudo pacman -S wayland wayland-protocols wayland-utils meson
```

```c
// minimal_wayland.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <wayland-client.h>
#include "xdg-shell-client-protocol.h"

static struct wl_display *display;
static struct wl_compositor *compositor;
static struct wl_shm *shm;
static struct xdg_wm_base *xdg_wm_base;

static int running = 1;
static int width = 640, height = 480;

static void xdg_wm_base_ping(void *data, struct xdg_wm_base *shell,
 uint32_t serial) {
 xdg_wm_base_pong(shell, serial);
}

static const struct xdg_wm_base_listener xdg_wm_base_listener = {
 .ping = xdg_wm_base_ping,
};

static void registry_global(void *data, struct wl_registry *registry,
 uint32_t name, const char *interface,
 uint32_t version) {
 if (strcmp(interface, wl_compositor_interface.name) == 0) {
 compositor = wl_registry_bind(registry, name,
 &wl_compositor_interface, 4);
 } else if (strcmp(interface, wl_shm_interface.name) == 0) {
 shm = wl_registry_bind(registry, name, &wl_shm_interface, 1);
 } else if (strcmp(interface, xdg_wm_base_interface.name) == 0) {
 xdg_wm_base = wl_registry_bind(registry, name,
 &xdg_wm_base_interface, 1);
 xdg_wm_base_add_listener(xdg_wm_base, &xdg_wm_base_listener, NULL);
 }
}

static void registry_global_remove(void *data, struct wl_registry *registry,
 uint32_t name) {}

static const struct wl_registry_listener registry_listener = {
 .global = registry_global,
 .global_remove = registry_global_remove,
};

static struct wl_buffer *create_buffer(void) {
 int stride = width * 4;
 int size = stride * height;

 char name[] = "/tmp/wl-shm-XXXXXX";
 int fd = mkstemp(name);
 unlink(name);
 ftruncate(fd, size);

 uint32_t *data = mmap(NULL, size, PROT_READ | PROT_WRITE,
 MAP_SHARED, fd, 0);

 // 绘制蓝色背景
 for (int i = 0; i < width * height; i++) {
 data[i] = 0xFF3355AA; // ARGB: 不透明蓝色
 }

 struct wl_shm_pool *pool = wl_shm_create_pool(shm, fd, size);
 struct wl_buffer *buffer = wl_shm_pool_create_buffer(
 pool, 0, width, height, stride, WL_SHM_FORMAT_ARGB8888);
 wl_shm_pool_destroy(pool);
 close(fd);
 munmap(data, size);

 return buffer;
}

static void xdg_surface_configure(void *data, struct xdg_surface *surface,
 uint32_t serial) {
 xdg_surface_ack_configure(surface, serial);
 struct wl_surface *wl_surface = data;
 struct wl_buffer *buffer = create_buffer();
 wl_surface_attach(wl_surface, buffer, 0, 0);
 wl_surface_commit(wl_surface);
}

static const struct xdg_surface_listener xdg_surface_listener = {
 .configure = xdg_surface_configure,
};

static void xdg_toplevel_close(void *data, struct xdg_toplevel *toplevel) {
 running = 0;
}

static void xdg_toplevel_configure(void *data, struct xdg_toplevel *toplevel,
 int32_t w, int32_t h,
 struct wl_array *states) {}

static const struct xdg_toplevel_listener xdg_toplevel_listener = {
 .configure = xdg_toplevel_configure,
 .close = xdg_toplevel_close,
};

int main(void) {
 display = wl_display_connect(NULL);
 if (!display) {
 fprintf(stderr, "无法连接到 Wayland\n");
 return 1;
 }

 struct wl_registry *registry = wl_display_get_registry(display);
 wl_registry_add_listener(registry, &registry_listener, NULL);
 wl_display_roundtrip(display);

 struct wl_surface *surface = wl_compositor_create_surface(compositor);
 struct xdg_surface *xdg_surface =
 xdg_wm_base_get_xdg_surface(xdg_wm_base, surface);
 xdg_surface_add_listener(xdg_surface, &xdg_surface_listener, surface);

 struct xdg_toplevel *toplevel = xdg_surface_get_toplevel(xdg_surface);
 xdg_toplevel_set_title(toplevel, "Wayland 示例");
 xdg_toplevel_add_listener(toplevel, &xdg_toplevel_listener, NULL);

 wl_surface_commit(surface);

 while (running && wl_display_dispatch(display) != -1) {
 // 事件循环
 }

 xdg_toplevel_destroy(toplevel);
 xdg_surface_destroy(xdg_surface);
 wl_surface_destroy(surface);
 wl_display_disconnect(display);

 return 0;
}
```

### 构建

```bash
# 生成 xdg-shell 协议代码
wayland-scanner client-header \
 /usr/share/wayland-protocols/stable/xdg-shell/xdg-shell.xml \
 xdg-shell-client-protocol.h

wayland-scanner private-code \
 /usr/share/wayland-protocols/stable/xdg-shell/xdg-shell.xml \
 xdg-shell-protocol.c

# 编译
gcc -o minimal_wayland minimal_wayland.c xdg-shell-protocol.c \
 $(pkg-config --cflags --libs wayland-client)

# 运行
./minimal_wayland
```

### 使用高级库

实际开发中通常使用更高级的库而非直接操作 Wayland 协议：

| 库 | 语言 | 说明 |
|----|------|------|
| GTK4 | C/多语言绑定 | GNOME 工具包，原生 Wayland |
| Qt6 | C++ | KDE 工具包，原生 Wayland |
| SDL2/SDL3 | C | 游戏/多媒体 |
| GLFW | C | OpenGL 窗口库 |
| wlroots | C | 合成器开发库 |
| smithay | Rust | Rust 合成器开发框架 |
| client-toolkit | Rust | Wayland 客户端库 |

```bash
# GTK4 Wayland 应用示例（Python）
python3 -c "
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

def on_activate(app):
 win = Gtk.ApplicationWindow(application=app, title='GTK4 Wayland')
 win.set_default_size(400, 300)
 label = Gtk.Label(label='Hello from Wayland!')
 win.set_child(label)
 win.present()

app = Gtk.Application()
app.connect('activate', on_activate)
app.run()
"
```

---

## 38.13 Wayland 调试技巧

```bash
# 协议级调试
WAYLAND_DEBUG=1 foot 2>&1 | head -50

# 使用 wayland-tracker 分析协议流量
# AUR: wayland-tracker

# libinput 调试（输入事件）
sudo libinput debug-events

# 合成器日志
# Sway
sway -d 2> /tmp/sway.log
# Hyprland
hyprctl -j monitors

# 检查合成器渲染后端
echo $WLR_RENDERER # vulkan / gles2 / pixman

# GPU 信息
glxinfo | grep "OpenGL renderer" # XWayland
eglinfo # 原生 Wayland

# 检查 DRM lease 支持（VR 设备）
ls /dev/dri/card*
```

---

## 38.14 从 X11 迁移到 Wayland 的检查清单

```markdown
□ 确认 GPU 驱动支持（AMD/Intel 良好，NVIDIA 需额外配置）
□ 选择合成器（Sway、Hyprland、GNOME、KDE）
□ 安装 XWayland（兼容 X11 应用）
□ 配置输入法（fcitx5 + 环境变量）
□ 安装 xdg-desktop-portal（屏幕共享）
□ 安装 PipeWire（音频 + 视频流）
□ 替换 X11 专属工具：
 - scrot/maim → grim + slurp
 - xclip/xsel → wl-clipboard
 - xdotool → wtype、ydotool
 - xrandr → wlr-randr、kanshi
 - picom → 内建合成
 - dunst → mako、fnott
 - rofi → wofi、fuzzel、tofi
 - i3lock → swaylock、hyprlock
 - polybar → waybar
□ 设置环境变量强制应用使用 Wayland
□ 测试常用应用的兼容性
□ 配置多显示器布局
□ 测试屏幕录制和截图
□ 检查游戏性能（Steam、Wine）
```

---

## 38.15 参考资源

| 资源 | 链接 |
|------|------|
| Wayland 官方文档 | https://wayland.freedesktop.org/ |
| Wayland Book | https://wayland-book.com/ |
| wayland-protocols | https://gitlab.freedesktop.org/wayland/wayland-protocols |
| wlroots | https://gitlab.freedesktop.org/wlroots/wlroots |
| Sway Wiki | https://github.com/swaywm/sway/wiki |
| Hyprland Wiki | https://wiki.hyprland.org/ |
| Arch Wiki - Wayland | https://wiki.archlinux.org/title/Wayland |
| Arch Wiki - Sway | https://wiki.archlinux.org/title/Sway |

---

## 38.16 本章测验

> [!example] 自测题目

> [!question]- 选择题 1：Wayland 与 X11 最核心的架构区别是什么？
> - A. Wayland 不支持 GPU 加速
> - B. Wayland 将显示服务器和窗口管理器合二为一（合成器），客户端自行渲染
> - C. Wayland 是网络透明的
> - D. Wayland 不支持多窗口
>
> > [!success]- 点击查看答案
> > **B**
> > Wayland 的合成器（Compositor）同时承担了 X11 中 X Server 和 Window Manager 的角色，客户端自行渲染缓冲区后提交给合成器合成显示，架构更简洁。

> [!question]- 选择题 2：XWayland 的作用是什么？
> - A. 将 Wayland 协议转换为 X11 协议
> - B. 在 Wayland 环境中运行 X11 应用的兼容层
> - C. 替代 Wayland 合成器
> - D. 提供 Wayland 的网络透明功能
>
> > [!success]- 点击查看答案
> > **B**
> > XWayland 是一个特殊的 X Server，作为 Wayland 客户端运行，为不支持 Wayland 的 X11 应用提供运行环境，实现向后兼容。

> [!question]- 判断题 3：Wayland 协议中，客户端不能访问其他客户端的输入或缓冲区，安全性优于 X11。
> - A. 正确
> - B. 错误
>
> > [!success]- 点击查看答案
> > **A. 正确**
> > X11 中任意客户端可以截取其他窗口的输入和截屏；Wayland 协议在设计上实现了客户端之间的安全隔离，客户端只能访问自己的缓冲区。

> [!question]- 选择题 4：在 Wayland 下进行屏幕共享和录制需要什么机制？
> - A. 直接使用 X11 的 XComposite 扩展
> - B. xdg-desktop-portal + PipeWire
> - C. 使用 ffmpeg 直接录制
> - D. 通过 /dev/fb0 帧缓冲
>
> > [!success]- 点击查看答案
> > **B**
> > Wayland 的安全隔离阻止了直接截屏，屏幕共享/录制需要通过 xdg-desktop-portal 发起权限请求，由合成器授权后通过 PipeWire 传输视频流。

> [!question]- 选择题 5：wlroots 是什么？
> - A. Wayland 官方参考合成器
> - B. 一个用于构建 Wayland 合成器的模块化库
> - C. Wayland 的显卡驱动
> - D. X11 到 Wayland 的迁移工具
>
> > [!success]- 点击查看答案
> > **B**
> > wlroots 是一个模块化的合成器库，提供了构建 Wayland 合成器所需的通用组件（DRM/KMS、输入处理、协议实现等），Sway 和 Hyprland 等合成器基于它构建。

> [!question]- 判断题 6：从 X11 迁移到 Wayland 时，xdotool 可以直接在 Wayland 原生应用上使用。
> - A. 正确
> - B. 错误
>
> > [!success]- 点击查看答案
> > **B. 错误**
> > xdotool 依赖 X11 协议，不能操作 Wayland 原生窗口。Wayland 下需要使用 wtype（模拟键盘输入）或 ydotool（通过 uinput 模拟）等替代工具。

> [!question]- 选择题 7：Wayland 协议中 DRM/KMS 的角色是什么？
> - A. 音频输出接口
> - B. 底层显示接口，合成器通过它直接控制 GPU 输出到显示器
> - C. 网络协议传输层
> - D. 字体渲染引擎
>
> > [!success]- 点击查看答案
> > **B**
> > DRM（Direct Rendering Manager）/KMS（Kernel Mode Setting）是 Linux 内核提供的底层显示接口，Wayland 合成器直接通过 DRM/KMS 将合成后的帧输出到显示器，跳过了 X11 的中间层。

> [!question]- 选择题 8：在 Wayland 环境下，哪个工具用于替代 X11 的 xclip/xsel 剪贴板工具？
> - A. pbcopy
> - B. wl-clipboard（wl-copy/wl-paste）
> - C. xdg-clipboard
> - D. wayland-clip
>
> > [!success]- 点击查看答案
> > **B**
> > wl-clipboard 提供了 `wl-copy` 和 `wl-paste` 命令，是 Wayland 原生的剪贴板工具，功能对应 X11 的 xclip/xsel。

> [!question]- 判断题 9：NVIDIA GPU 在 Wayland 下需要额外配置（如设置 GBM 后端），比 AMD/Intel 驱动更复杂。
> - A. 正确
> - B. 错误
>
> > [!success]- 点击查看答案
> > **A. 正确**
> > AMD 和 Intel 使用开源 Mesa 驱动，对 Wayland 支持良好；NVIDIA 需要专有驱动且需额外配置（如设置 `GBM_BACKEND=nvidia-drm`、`__GLX_VENDOR_LIBRARY_NAME=nvidia` 等环境变量）。

> [!question]- 选择题 10：Wayland 相比 X11 在图形渲染上解决了什么长期问题？
> - A. 不支持 3D 加速
> - B. 画面撕裂（tearing），因为 Wayland 内建 VSync 和原生合成
> - C. 字体渲染模糊
> - D. 颜色空间不正确
>
> > [!success]- 点击查看答案
> > **B**
> > X11 没有原生的 VSync 支持，需要额外的合成管理器（如 picom）来减轻撕裂；Wayland 的合成器内建 VSync 和帧同步机制，从架构上消除了撕裂问题。
