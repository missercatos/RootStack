# 12 - Wayland 协议与合成器开发

> 从协议原理到自己写一个 Wayland 合成器。

---

## 12.1 Wayland 架构原理

```
┌─────────────────────────────────────────┐
│ 客户端 (Client) │
│ Firefox / Kitty / GTK / Qt 应用 │
│ │ │
│ │ Wayland 协议（Unix Socket） │
│ ▼ │
│ ┌─────────────┐ │
│ │ libwayland │ libwayland-client.so │
│ └─────────────┘ │
└─────────────────────────────────────────┘
 │
 wayland-0 (socket)
 │
┌─────────────────────────────────────────┐
│ 合成器 (Compositor) │
│ ┌─────────────┐ │
│ │ libwayland │ libwayland-server.so │
│ └─────────────┘ │
│ │ │
│ ▼ │
│ ┌─────────────┐ ┌────────────────┐ │
│ │ 渲染器 │ │ libinput │ │
│ │ (OpenGL/VK) │ │ (输入处理) │ │
│ └─────────────┘ └────────────────┘ │
│ │ │ │
│ ▼ ▼ │
│ ┌─────────────┐ ┌────────────────┐ │
│ │ DRM/KMS │ │ evdev │ │
│ │ (显示) │ │ (输入设备) │ │
│ └─────────────┘ └────────────────┘ │
└─────────────────────────────────────────┘
```

### 核心概念

| 概念 | 说明 |
|------|------|
| **Wayland 协议** | XML 定义的接口 + 请求/事件模型（类似 JSON-RPC 但二进制） |
| **wl_display** | 连接端点，客户端连接后获取全局对象 |
| **wl_surface** | 可渲染的矩形区域 |
| **xdg_surface** | 带窗口管理的 Surface（标题、最大化等） |
| **wl_output** | 物理显示器 |
| **wl_seat** | 输入设备集合（键盘、鼠标、触摸） |
| **wl_shm** | 共享内存缓冲区 |
| **zwlr_layer_shell_v1** | Layer Shell 协议（waybar 等） |
| **wp_fractional_scale_v1** | 分数缩放 |
| **wp_viewporter** | 裁剪/缩放视图 |
| **wp_presentation_time** | 精确帧计时 |

---

## 12.2 协议定义（XML 协议文件）

Wayland 协议用 XML 描述，wayland-scanner 生成 C 代码。

```xml
<?xml version="1.0" encoding="UTF-8"?>
<protocol name="my_custom_protocol">
 <copyright>...</copyright>

 <interface name="my_interface" version="1">
 <description summary="我的自定义接口">
 详细描述...
 </description>

 <!-- 请求：客户端 → 服务端 -->
 <request name="do_something">
 <arg name="param1" type="string"/>
 <arg name="param2" type="int"/>
 </request>

 <!-- 事件：服务端 → 客户端 -->
 <event name="something_happened">
 <arg name="data" type="array"/>
 </event>

 <!-- 枚举 -->
 <enum name="state">
 <entry name="idle" value="0"/>
 <entry name="active" value="1"/>
 <entry name="error" value="2"/>
 </enum>
 </interface>
</protocol>
```

### 生成代码

```bash
# 生成服务端头文件
wayland-scanner server-header my_protocol.xml my_protocol_server.h

# 生成客户端头文件
wayland-scanner client-header my_protocol.xml my_protocol_client.h

# 生成胶水代码（协议分发器）
wayland-scanner private-code my_protocol.xml my_protocol.c
```

---

## 12.3 用 wlroots 写合成器（Rust）

> wlroots 是模块化 Wayland 合成器库，Sway/Hyprland/Niri 都基于它。

### 项目结构

```
mywm/
├── Cargo.toml
├── src/
│ ├── main.rs
│ ├── compositor.rs
│ ├── keyboard.rs
│ ├── cursor.rs
│ └── output.rs
└── protocols/
 └── wlr-layer-shell-unstable-v1.xml
```

### Cargo.toml

```toml
[package]
name = "mywm"
version = "0.1.0"
edition = "2021"

[dependencies]
# Smithay — Rust 生态的 Wayland 合成器框架
smithay = { version = "0.3", features = ["backend_winit", "renderer_gl", "use_system_lib"] }
tracing = "0.1"
tracing-subscriber = "0.3"
```

### 最小合成器 main.rs

```rust
use smithay::backend::winit;
use smithay::reexports::calloop::EventLoop;
use smithay::wayland::compositor;
use tracing_subscriber;

fn main() {
 tracing_subscriber::fmt::init();

 let mut event_loop: EventLoop<()> = EventLoop::try_new().unwrap();

 // 使用 winit 后端（跑在窗口里，方便开发调试）
 let (mut backend, _winit) = winit::init().unwrap();

 // Wayland 协议状态
 let mut display = backend.display.clone();

 // 创建合成器全局
 compositor::compositor_init(
 &mut display,
 |_, _| {}, // commit 处理
 smithay::utils::NoUserData::default(),
 );

 // 主循环
 loop {
 event_loop.dispatch(None, |_| {}).unwrap();
 }
}
```

### 渲染循环

```rust
use smithay::{
 backend::renderer::{ImportAll, Renderer},
 desktop::space::Space,
 output::Output,
 reexports::wayland_server::protocol::wl_output,
 utils::{Physical, Point, Size},
};

struct MyCompositor {
 space: Space,
 output: Output,
}

impl MyCompositor {
 fn render<R>(&mut self, renderer: &mut R, age: usize)
 where
 R: Renderer + ImportAll,
 {
 // 渲染所有窗口
 let result = self.space.render(
 renderer,
 age,
 &self.output,
 1.0, // scale
 Point::<i32, Physical>::from((0, 0)),
 &[],
 );
 }
}
```

---

## 12.4 键盘输入处理

```rust
use smithay::input::keyboard::XkbConfig;
use smithay::wayland::seat::Seat;

fn handle_key(seat: &mut Seat, keycode: u32, state: KeyState) {
 // 按键映射
 let key_event = seat.get_keyboard().unwrap().input(
 &mut seat,
 keycode,
 state,
 serial,
 time,
 );

 if state == KeyState::Pressed {
 match key_event.key {
 // Mod + Q = 关闭
 Keysym::q if mods.logo => {
 seat.focus_window().map(|w| w.close());
 }
 // Mod + Return = 启动终端
 Keysym::Return if mods.logo => {
 std::process::Command::new("foot").spawn().ok();
 }
 _ => {}
 }
 }
}
```

---

## 12.5 wlroots 后端架构

```
wlroots 后端（backend）选择：
┌──────────────┬──────────────────────────────────────┐
│ DRM/KMS │ 最常用，直接操作 GPU+显示（TUI 启动）│
│ Wayland │ 开发/调试用（在现有合成器里跑） │
│ X11 │ 同上 │
│ headless │ 无头（服务器/CI 测试） │
│ libinput │ 抽象所有输入设备 │
│ session │ logind/seatd 管理权限 │
└──────────────┴──────────────────────────────────────┘
```

---

## 12.6 wlroots 关键 API (C)

```c
#include <wlr/backend.h>
#include <wlr/render/wlr_renderer.h>
#include <wlr/types/wlr_xdg_shell.h>

struct my_compositor {
 struct wl_display *display;
 struct wlr_backend *backend;
 struct wlr_renderer *renderer;
 struct wlr_allocator *allocator;

 // 协议实现
 struct wlr_xdg_shell *xdg_shell;

 // 场景图 (wlroots 0.16+)
 struct wlr_scene *scene;
 struct wlr_scene_tree *layers[4]; // background, bottom, top, overlay
};

// 处理新 xdg_shell 窗口
void xdg_surface_new(struct wl_listener *listener, void *data) {
 struct wlr_xdg_surface *xdg_surface = data;

 if (xdg_surface->role == WLR_XDG_SURFACE_ROLE_TOPLEVEL) {
 // 创建场景节点
 struct wlr_scene_tree *tree =
 wlr_scene_xdg_surface_create(layers[2], xdg_surface);
 }
}

// 主循环
int main() {
 struct wl_display *display = wl_display_create();
 struct wlr_backend *backend = wlr_backend_autocreate(display, NULL);
 struct wlr_renderer *renderer = wlr_renderer_autocreate(backend);
 wlr_renderer_init_wl_shm(renderer, display);

 struct wlr_scene *scene = wlr_scene_create();
 // ... 初始化各层 ...

 // 启动后端
 wlr_backend_start(backend);

 // 事件循环
 wl_display_run(display);

 wl_display_destroy(display);
}
```

---

## 12.7 写一个完整的 Wayland 合成器步骤

```
阶段 1：最小渲染
 □ 创建 wl_display + backend
 □ 渲染一个纯色背景
 □ 显示到屏幕

阶段 2：输入处理
 □ 处理键盘事件
 □ 处理鼠标事件
 □ 光标渲染

阶段 3：窗口管理
 □ 实现 xdg_shell
 □ 窗口布局（浮动→平铺）
 □ 焦点管理

阶段 4：协议支持
 □ Layer Shell（面板/背景）
 □ Output Management
 □ Presentation Time
 □ Viewporter

阶段 5：合成
 □ 透明度/圆角
 □ 阴影
 □ 动画
 □ 截图/录屏

阶段 6：生态
 □ 配置文件解析
 □ IPC 控制
 □ 插件系统

参考阅读：
- tinywl (wlroots 自带的极简合成器示例，~400行C)
- way-cooler (Rust + wlroots)
- river (Zig + wlroots)
```

---

## 12.8 tinywl 注解（wlroots 的最小示例）

```c
// tinywl.c — wlroots 自带，理解整个渲染流程

// 1. 创建 Display + Backend + Renderer
struct wl_display *display = wl_display_create();
struct wlr_backend *backend = wlr_backend_autocreate(display);

// 2. 初始化分配器（GPU 内存管理）
struct wlr_allocator *allocator = wlr_allocator_autocreate(backend, renderer);

// 3. 初始化输出（显示器）
struct wlr_output *output = wlr_output_create(backend);

// 4. 初始化输入
struct wlr_seat *seat = wlr_seat_create(display, "seat0");

// 5. 渲染
// 每次 vblank / 帧回调时：
wlr_output_attach_render(output, &buffer_age);
wlr_renderer_begin(renderer, output->width, output->height);
// ... 调用 wlr_scene_render_output(scene, output) ...
wlr_renderer_end(renderer);
wlr_output_commit(output);
```

---

## 12.9 调试技巧

```bash
# WAYLAND_DEBUG=1 显示所有协议消息
WAYLAND_DEBUG=1 foot
# 输出每个请求/事件及其参数

# WAYLAND_DISPLAY 指定 socket
WAYLAND_DISPLAY=wayland-1 application

# 检查合成器信息
wayland-info # 列出所有全局接口

# 截图（wlroots 合成器）
wayshot # 截图工具
wf-recorder # 录屏

# 调试工具
wev # xev 的 Wayland 版（显示按键事件）
ydotool # 模拟输入
```

---

## 12.10 推荐学习资源

```
必读：
- Wayland 核心协议 XML: wayland.xml
- xdg-shell 协议: xdg-shell.xml
- wlr-layer-shell: wlr-layer-shell-unstable-v1.xml
- tinywl 源码: wlroots/tinywl/

进阶：
- Smithay Book (https://smithay.github.io/book/)
- wlroots 文档 (https://way-cooler.org/book/wlroots_introduction.html)
- Writing a Wayland Compositor 博客系列
```

---

