# 15 - QuickShell 开发指南

> [QuickShell](https://github.com/outfoxxed/quickshell) — Rust 写的 Wayland 自定义 Shell 工具包。可以自己写面板、启动器、通知中心、锁屏等，复用已有的 Wayland 协议实现。

---

## 15.1 QuickShell 是什么

```
QuickShell ≠ 合成器
QuickShell = Wayland 协议客户端的高级 Rust 封装
 让你像写 Flutter/DOM 一样写 Wayland 组件

可以构建：
┌──────────────┬──────────────────────┐
│ 面板/任务栏 │ waybar 替代 │
│ 启动器 │ fuzzel/rofi 替代 │
│ 通知中心 │ mako/dunst 替代 │
│ 锁屏 │ swaylock 替代 │
│ OSD 音量 │ 音量弹窗 │
│ 桌面对话框 │ zenity 替代 │
│ 日历弹出窗 │ │
│ 剪贴板管理 │ clipman 替代 │
│ 键盘布局指示 │ │
└──────────────┴──────────────────────┘
```

---

## 15.2 安装与项目搭建

```bash
# 安装
sudo pacman -S quickshell
# 或
paru -S quickshell

# 项目依赖
# Cargo.toml
[dependencies]
quickshell = "0.2"
```

### 最小示例

```rust
// main.rs — 一个空白面板
use quickshell::prelude::*;

fn main() {
 // 初始化 Wayland 连接
 let app = QmlApplication::new("my-shell");
 app.run();
}
```

```bash
# 编译运行
cargo run
```

---

## 15.3 QuickShell 核心概念

```
场景图 (Scene Graph) 架构：

Window ← 窗口（layer shell / xdg toplevel）
 └── Item ← 可渲染元素
 ├── Text ← 文本渲染
 ├── Rectangle ← 矩形（颜色/渐变/圆角）
 ├── Image ← 图片
 ├── Row ← 水平布局
 ├── Column ← 垂直布局
 ├── Layout ← 自定义布局
 └── MouseArea ← 鼠标交互

属性系统（类似 QML 绑定）：
- 属性值变化自动重新渲染
- 支持绑定（一个属性值依赖另一个）
- 支持动画/过渡
```

---

## 15.4 创建面板（Layer Shell）

```rust
use quickshell::{
 prelude::*,
 wayland::layer_shell::{LayerShell, Anchor, Layer, KeyboardInteractivity},
 widgets::{Rectangle, Row, Text, MouseArea},
 properties::{prop, Property},
 build::*,
};

fn main() {
 let app = QmlApplication::new("mypanel");

 // 创建面板窗口（使用 Layer Shell 协议）
 let panel = LayerShell::new(Anchor::TOP | Anchor::LEFT | Anchor::RIGHT);

 // 设置高度
 panel.set_exclusive_zone(36); // 独占 36px 高度
 panel.set_layer(Layer::Top); // 顶层（在窗口之上）

 // 键盘交互（需要的话）
 panel.set_keyboard_interactivity(KeyboardInteractivity::OnDemand);

 // 背景
 let background = Rectangle::new();
 background.set_color(prop!(#1E1E2E));
 background.set_height(prop!(36));
 background.set_width(panel.width.clone()); // 绑定 = 面板宽度

 // 水平布局
 let row = Row::new();
 row.set_height(prop!(36));
 row.set_spacing(prop!(8.0));
 row.set_padding(prop!([4, 8]));

 // 左对齐的工作区
 let workspaces = WorkspaceWidget::new();
 row.add_child(workspaces);

 // 弹性空间（推右边）
 let spacer = Item::new();
 spacer.set_expand(prop!(true));
 row.add_child(spacer);

 // 右对齐的时钟
 let clock = ClockWidget::new();
 row.add_child(clock);

 // 组装
 background.add_child(row);
 panel.set_body(background);

 app.run();
}

// 时钟小组件
struct ClockWidget {
 item: Item,
 text: Text,
}

impl ClockWidget {
 fn new() -> Self {
 let item = Item::new();
 let text = Text::new();
 text.set_text(prop!("Loading..."));
 text.set_color(prop!(#CDD6F4));
 text.set_font_size(prop!(14.0));
 item.add_child(text);

 // 定时器更新
 let text_ref = text.clone();
 std::thread::spawn(move || loop {
 let now = chrono::Local::now();
 let time_str = now.format("%H:%M").to_string();
 text_ref.set_text(prop!(time_str));
 std::thread::sleep(std::time::Duration::from_secs(30));
 });

 Self { item, text }
 }
}
```

---

## 15.5 属性系统详解

```rust
use quickshell::properties::{prop, Property, Var};

// ===== Property 基本用法 =====
let count: Property<i32> = Property::new(0);
count.set(42);
println!("{}", count.get()); // 42

// ===== prop! 宏（简化写法）=====
// prop!(value) = 创建常量属性
let name = prop!("Hello");
let size = prop!(16.0);

// ===== 绑定属性 =====
// 一个属性值自动根据另一个变化
let width: Property<f64> = Property::new(100.0);
let double_width = width.map(|w| w * 2.0);
// double_width 自动 = 200.0

// ===== Var（可变量）= 绑定 + 内部可变 =====
let count = Var::new(0);
let label = count.map(|c| format!("Count: {}", c));

count.set(5);
println!("{}", label.get()); // "Count: 5"

// ===== 复合绑定 =====
let x = Var::new(10.0);
let y = Var::new(20.0);
let distance = Var::bind(&x, &y, |x, y| {
 (x.powi(2) + y.powi(2)).sqrt()
});

// ===== 应用到组件 =====
let rect = Rectangle::new();
rect.set_width(x.clone()); // 绑定到属性
rect.set_height(distance.clone()); // 绑定到计算值
```

---

## 15.6 启动器开发

```rust
// 完整启动器示例 — 类似 fuzzel
use quickshell::{
 prelude::*,
 wayland::layer_shell::{LayerShell, Anchor, Layer, KeyboardInteractivity},
 widgets::*,
 properties::*,
};

struct AppEntry {
 name: String,
 exec: String,
 icon: Option<String>,
}

fn load_desktop_entries() -> Vec<AppEntry> {
 // 解析 /usr/share/applications/*.desktop
 let mut apps = Vec::new();
 for entry in glob::glob("/usr/share/applications/*.desktop").unwrap() {
 if let Ok(path) = entry {
 if let Ok(content) = std::fs::read_to_string(&path) {
 let mut name = String::new();
 let mut exec = String::new();
 for line in content.lines() {
 if line.starts_with("Name=") {
 name = line[5..].to_string();
 }
 if line.starts_with("Exec=") {
 exec = line[5..].to_string()
 .replace("%u", "")
 .replace("%U", "")
 .replace("%f", "")
 .replace("%F", "");
 }
 }
 if !name.is_empty() && !exec.is_empty() {
 apps.push(AppEntry { name, exec, icon: None });
 }
 }
 }
 }
 apps
}

fn main() {
 let app = QmlApplication::new("launcher");

 let window = LayerShell::new(
 Anchor::TOP | Anchor::BOTTOM | Anchor::LEFT | Anchor::RIGHT
 );
 window.set_layer(Layer::Overlay);
 window.set_keyboard_interactivity(KeyboardInteractivity::Exclusive);

 // 搜索框
 let search_input = TextInput::new();
 search_input.set_placeholder(prop!("Search..."));
 search_input.set_font_size(prop!(18.0));

 // 结果列表
 let results_list = Column::new();

 // 过滤逻辑
 let all_apps = load_desktop_entries();
 let query = Var::new(String::new());

 // search_input.on_text_changed → 更新 query
 // query 变化 → 过滤 all_apps → 重建 results_list 子元素

 // 主布局
 let main_col = Column::new();
 main_col.set_alignment(Alignment::Center);

 let container = Rectangle::new();
 container.set_color(prop!(#1E1E2E));
 container.set_width(prop!(600.0));
 container.set_radius(prop!(12.0));

 let inner = Column::new();
 inner.add_child(search_input);
 inner.add_child(results_list);
 container.add_child(inner);
 main_col.add_child(container);

 window.set_body(main_col);
 app.run();
}
```

---

## 15.7 通知中心

```rust
// 基于 org.freedesktop.Notifications DBus 协议
use quickshell::dbus::*;
use quickshell::widgets::*;

struct NotificationWidget {
 container: Rectangle,
 title: Text,
 body: Text,
 icon: Image,
 timeout: u32,
}

struct NotificationCenter {
 notifications: Vec<NotificationWidget>,
 list: Column,
 // DBus 连接
 dbus: DBusConnection,
}

impl NotificationCenter {
 fn new() -> Self {
 let dbus = DBusConnection::session();

 // 注册通知回调
 dbus.register_notification_handler(|id, app_name, summary, body, timeout| {
 let widget = NotificationWidget {
 container: Rectangle::new(),
 title: Text::new(prop!(summary)),
 body: Text::new(prop!(body)),
 icon: Image::new(),
 timeout,
 };
 // 添加到通知列表
 // ...
 });

 Self { notifications: Vec::new(), list: Column::new(), dbus }
 }
}
```

---

## 15.8 工作区指示器

```rust
// 通过 Wayland workspace 协议获取实时工作区信息
use quickshell::wayland::workspace::*;

struct WorkspaceIndicator {
 row: Row,
 current: Property<i32>,
}

impl WorkspaceIndicator {
 fn new() -> Self {
 let row = Row::new();
 let current = Property::new(1);

 // 监听工作区变化（需要合成器支持 hyprland-workspaces 或 ext-workspace）
 // Hyprland 专用 IPC：
 let socket = std::os::unix::net::UnixStream::connect(
 format!("/tmp/hypr/{}/.socket2.sock",
 std::env::var("HYPRLAND_INSTANCE_SIGNATURE").unwrap())
 ).unwrap();

 let current_ref = current.clone();
 let row_ref = row.clone();
 std::thread::spawn(move || {
 use std::io::BufRead;
 let reader = std::io::BufReader::new(socket);
 for line in reader.lines() {
 if let Ok(line) = line {
 if line.starts_with("workspace>>") {
 let ws: i32 = line[11..].parse().unwrap_or(1);
 current_ref.set(ws);
 // 更新工作区按钮高亮
 }
 }
 }
 });

 // 创建 1-10 工作区按钮
 for i in 1..=10 {
 let button = WorkspaceButton::new(i, current.clone());
 row.add_child(button);
 }

 Self { row, current }
 }
}

struct WorkspaceButton {
 item: Item,
 text: Text,
 num: i32,
}

impl WorkspaceButton {
 fn new(num: i32, current: Property<i32>) -> Self {
 let item = MouseArea::new();
 let text = Text::new(prop!(num.to_string()));

 // 绑定颜色：当前工作区高亮
 let text_ref = text.clone();
 current.watch(move |cur| {
 if cur == num {
 text_ref.set_color(prop!(#89B4FA)); // 高亮蓝色
 } else {
 text_ref.set_color(prop!(#585B70)); // 灰色
 }
 });

 // 点击切换工作区
 let num_copy = num;
 // item.on_click(move || dispatch_workspace(num_copy));

 Self { item, text, num }
 }
}
```

---

## 15.9 自定义 Shell 组件打包为系统服务

```rust
// 完整的 panel 示例，启动为 systemd 用户服务

// Cargo.toml
[package]
name = "my-hypr-panel"
version = "0.1.0"
edition = "2021"

[dependencies]
quickshell = "0.2"
chrono = "0.4"
```

```bash
# PKGBUILD 配合使用
# 安装后创建 systemd 用户服务：

# my-hypr-panel.service
[Unit]
Description=Custom Hyprland Panel
PartOf=graphical-session.target

[Service]
ExecStart=/usr/bin/my-hypr-panel
Restart=on-failure

[Install]
WantedBy=graphical-session.target
```

---

## 15.10 QuickShell 布局系统

```rust
// ===== Row（水平）=====
let row = Row::new();
row.set_spacing(prop!(8.0));
row.set_padding(prop!([2, 8, 2, 8])); // [top, right, bottom, left]

// ===== Column（垂直）=====
let col = Column::new();
col.set_spacing(prop!(4.0));
col.set_alignment(Alignment::Center);

// ===== 弹性空间（Flexbox 风格）=====
let spacer = Item::new();
spacer.set_expand(prop!(true)); // 占据所有剩余空间
row.add_child(spacer);

// ===== 嵌套 =====
// Row > [Icon, Column > [Title, Subtitle], Spacer, Button]
let row = Row::new();
let col = Column::new();
col.add_child(title_text);
col.add_child(subtitle_text);
row.add_child(icon);
row.add_child(col);
row.add_child(spacer);
row.add_child(close_button);

// ===== 绝对定位 =====
let overlay = Item::new();
let popup = Rectangle::new();
popup.set_x(prop!(100.0)); // 绝对位置
popup.set_y(prop!(50.0));
popup.set_z(prop!(10)); // Z-序
overlay.add_child(popup);
```

---

## 15.11 动画与过渡

```rust
use quickshell::animations::*;

// 透明度动画
let opacity = Animation::new(0.0, 1.0, Duration::from_millis(300));

// 位置动画
let x = Animation::new(-200.0, 0.0, Duration::from_millis(250))
 .with_easing(Easing::OutCubic);

// 应用到组件
let popup = Rectangle::new();
popup.set_opacity(opacity.value());
popup.set_x(x.value());
opacity.start();
x.start();

// 过渡（属性变化时自动动画）
let is_open = Var::new(false);
let height = is_open.transition(|open| {
 if open { 200.0 } else { 0.0 }
}, Duration::from_millis(300));
```

---

## 15.12 主题系统

```rust
// 定义主题结构
struct Theme {
 bg: Color,
 fg: Color,
 accent: Color,
 radius: f64,
 font_size: f64,
 font_family: String,
}

impl Theme {
 fn catppuccin_mocha() -> Self {
 Self {
 bg: Color::from_hex("#1E1E2E"),
 fg: Color::from_hex("#CDD6F4"),
 accent: Color::from_hex("#89B4FA"),
 radius: 12.0,
 font_size: 13.0,
 font_family: "JetBrainsMono Nerd Font".into(),
 }
 }

 fn tokyo_night() -> Self {
 Self {
 bg: Color::from_hex("#1A1B26"),
 fg: Color::from_hex("#A9B1D6"),
 accent: Color::from_hex("#7AA2F7"),
 radius: 8.0,
 font_size: 14.0,
 font_family: "FiraCode Nerd Font".into(),
 }
 }
}

// 加载主题配置（从文件）
fn load_theme(path: &str) -> Theme {
 let content = std::fs::read_to_string(path).unwrap();
 serde_json::from_str(&content).unwrap_or(Theme::catppuccin_mocha())
}
```

---

## 15.13 完整项目：自定义状态栏

```rust
// mypanel/src/main.rs
use quickshell::prelude::*;
use quickshell::wayland::layer_shell::*;
use quickshell::widgets::*;
use quickshell::properties::*;

mod modules; // clock, workspace, battery, network, tray

fn main() {
 let app = QmlApplication::new("mypanel");
 let theme = Theme::load("~/.config/mypanel/theme.toml");

 let panel = LayerShell::new(Anchor::TOP | Anchor::LEFT | Anchor::RIGHT);
 panel.set_exclusive_zone(theme.height);
 panel.set_layer(Layer::Top);

 let bg = Rectangle::new();
 bg.set_color(prop!(theme.bg));
 bg.set_height(prop!(theme.height));

 let row = Row::new();
 row.set_spacing(prop!(12.0));
 row.set_padding(prop!([0, 12, 0, 12]));

 // 左侧模块
 row.add_child(modules::workspace::new());
 row.add_child(modules::window_title::new());

 // 弹性空间
 let spacer = Item::new();
 spacer.set_expand(prop!(true));
 row.add_child(spacer);

 // 右侧模块
 row.add_child(modules::network::new());
 row.add_child(modules::battery::new());
 row.add_child(modules::clock::new());

 bg.add_child(row);
 panel.set_body(bg);
 app.run();
}
```

### 模块示例

```rust
// modules/clock.rs
use quickshell::widgets::*;
use quickshell::properties::*;

pub struct Clock {
 item: Item,
 text: Text,
}

impl Clock {
 pub fn new() -> Self {
 let item = Item::new();
 let text = Text::new();
 text.set_font_size(prop!(13.0));

 // 定时更新
 let t = text.clone();
 std::thread::spawn(move || loop {
 let now = chrono::Local::now();
 t.set_text(prop!(now.format("%H:%M:%S").to_string()));
 std::thread::sleep(std::time::Duration::from_secs(1));
 });

 item.add_child(text);
 Self { item, text }
 }
}
```

---

## 15.14 调试与技巧

```bash
# 在合成器中运行 QuickShell 应用（开发模式）
# 不需要生成新的 session
cargo run

# 查看 Wayland 协议通信
WAYLAND_DEBUG=1 cargo run

# 作为 Layer Shell 组件启动
# 直接运行即可，QuickShell 自动请求 Layer Shell 角色

# 热重载（开发中）
# 搭配 cargo watch
cargo watch -x run

# 性能分析
# QuickShell 基于 QML/C++ 场景图，性能接近原生
# 大量更新时使用 Transaction/Throttle
```

---

## 15.15 QuickShell vs 其他工具

| | QuickShell | EWW | AGS | Waybar |
|------|-----------|-----|-----|--------|
| 语言 | Rust | Yuck(自定义) | TypeScript | JSON |
| Wayland 原生 | | | | |
| 自定义组件 | 完全自由 | Widget 系统 | Widget 系统 | 固定模块 |
| 学习曲线 | 中（需 Rust） | 低 | 中（TS+GTK） | 低 |
| 动画 | | 基础 | | |
| 打包 | cargo + AUR | eww 解释器 | ags 运行 | waybar 配置 |
| 适合场景 | 深度自定义面板/启动器 | 小工具/OSD | Widget 系统 | 简单状态栏 |
```

---

## 15.16 本章测验

> [!example] 自测题目

> [!question]- 选择题 1：QuickShell 是用什么语言编写的？
> - A. C++
> - B. TypeScript
> - C. Rust
> - D. Go
>
> > [!success]- 点击查看答案
> > **C**
> > QuickShell 是 Rust 写的 Wayland 自定义 Shell 工具包。

> [!question]- 选择题 2：QuickShell 在 Wayland 架构中的角色是什么？
> - A. 合成器（Compositor）
> - B. Wayland 协议客户端的高级封装
> - C. 显示服务器
> - D. 输入管理器
>
> > [!success]- 点击查看答案
> > **B**
> > QuickShell 不是合成器，而是 Wayland 协议客户端的高级 Rust 封装，让开发者可以像写 GUI 框架一样构建面板、启动器等组件。

> [!question]- 选择题 3：QuickShell 中创建面板使用什么 Wayland 协议？
> - A. xdg_shell
> - B. Layer Shell
> - C. wl_subsurface
> - D. wp_presentation
>
> > [!success]- 点击查看答案
> > **B**
> > QuickShell 使用 Layer Shell 协议创建面板，通过设置 Anchor、exclusive_zone、Layer 等属性控制面板的位置和行为。

> [!question]- 判断题 4：QuickShell 的属性系统支持自动绑定——一个属性值变化时，依赖它的属性会自动更新
> - A. 正确
> - B. 错误
>
> > [!success]- 点击查看答案
> > **A. 正确**
> > QuickShell 的属性系统类似 QML 绑定，支持 Property、Var、map、watch 等机制，属性值变化自动触发依赖更新和重新渲染。

> [!question]- 选择题 5：LayerShell 中 set_exclusive_zone(36) 的含义是什么？
> - A. 面板宽度为 36 像素
> - B. 面板独占 36 像素高度的屏幕空间（其他窗口不能覆盖）
> - C. 面板的 Z 序为 36
> - D. 面板透明度为 36%
>
> > [!success]- 点击查看答案
> > **B**
> > exclusive_zone 设置面板独占的屏幕空间（像素），合成器会确保其他窗口不会覆盖这个区域。

> [!question]- 选择题 6：QuickShell 布局中，让元素占据所有剩余空间的属性是？
> - A. set_fill(true)
> - B. set_expand(prop!(true))
> - C. set_flex(1)
> - D. set_stretch(true)
>
> > [!success]- 点击查看答案
> > **B**
> > 使用 `set_expand(prop!(true))` 让元素（通常是 spacer）占据布局中所有剩余空间，类似 Flexbox 的 flex-grow。

> [!question]- 选择题 7：QuickShell 动画中使用 Easing::OutCubic 的效果是？
> - A. 匀速运动
> - B. 先慢后快
> - C. 先快后慢（减速）
> - D. 先快后慢再快
>
> > [!success]- 点击查看答案
> > **C**
> > OutCubic 缓动曲线表示先快后慢（减速效果），开始时快速运动然后逐渐减速到停止。

> [!question]- 判断题 8：QuickShell 可以通过 cargo watch -x run 实现开发时热重载
> - A. 正确
> - B. 错误
>
> > [!success]- 点击查看答案
> > **A. 正确**
> > 开发 QuickShell 组件时可以搭配 `cargo watch -x run` 实现代码变更后自动重新编译运行，模拟热重载体验。

> [!question]- 选择题 9：QuickShell 相比 Waybar 的主要优势是什么？
> - A. 配置更简单
> - B. 可以完全自由地自定义组件，不限于固定模块
> - C. 性能更高
> - D. 支持更多合成器
>
> > [!success]- 点击查看答案
> > **B**
> > QuickShell 允许完全自由地构建自定义组件（面板、启动器、通知中心等），而 Waybar 只提供固定模块的 JSON 配置。

> [!question]- 判断题 10：QuickShell 中 Layer::Overlay 层级在 Layer::Top 之上，常用于需要独占键盘的启动器
> - A. 正确
> - B. 错误
>
> > [!success]- 点击查看答案
> > **A. 正确**
> > Overlay 层在所有其他层之上，启动器通常使用 Layer::Overlay 并设置 KeyboardInteractivity::Exclusive 来独占键盘输入。
