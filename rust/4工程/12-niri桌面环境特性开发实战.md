# niri桌面环境特性开发实战

## 原理

niri 是 Wayland 合成器，用 Rust 开发。Wayland 协议基于异步 socket 通信，客户端通过 `libwayland` 与 compositor 交换事件（wl_keyboard, wl_surface, xdg_shell 等）。

关键设计理念：
- **scrollable-tiling** 布局：不基于传统窗口栈叠（stacking），每列（column）无限滚动
- **每个输出**（monitor）一个顶层 workspace，含若干 column
- **每个 column** 含若干 window（tile），可上下滚动
- 动画：wayland frame callback 驱动 60fps vsync 更新

Rust 实现依赖 `smithay`（Wayland compositor 库）、`wayland-rs` 客户端绑定。安全保证：Rust 所有权系统确保 surface 生命周期正确映射到 tile 状态。

Wayland 协议帧：client → compositor 提交 buffer → compositor 格式检查 → 合成到屏幕 → 发送 frame callback。

[[../4工程/07-并发与异步安全|Rust: 并发安全]]
[[../4工程/11-企业级架构与设计模式|Rust: 架构设计]]

---

## 语法

```toml
# 示例：Wayland compositor 开发依赖
[dependencies]
smithay = "0.3"
wayland-server = "0.31"
```

```rust
// Wayland compositor 概念代码（简化）
struct NiriCompositor {
    outputs: Vec<Output>,
    workspaces: HashMap<OutputId, Workspace>,
}

struct Workspace {
    columns: Vec<Column>,
    active_column: usize,
}

struct Column {
    windows: Vec<Window>,
    scroll_offset: f64,
}

impl Column {
    fn add_window(&mut self, window: Window) {
        self.windows.push(window);
        self.layout();
    }

    fn layout(&mut self) {
        let y = self.windows.iter().map(|w| w.height).sum::<f64>();
        self.scroll_offset = y;
    }
}
```

---

## 实践

### AI 自检

1. Wayland 和 X11 的根本架构区别？为什么 Rust 适合实现 Wayland compositor？
2. `smithay` 如何处理输入事件（keyboard/mouse）的 security context？设备抢占问题如何解决？
