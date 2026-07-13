
# Nuklear

| 属性 | 说明 |
|------|------|
| 类型 | 即时模式 GUI（纯头文件） |
| 许可证 | MIT / 公共领域 |
| 仓库 | https://github.com/Immediate-Mode-UI/Nuklear |

**核心概念**：Nuklear 的理念是"GUI 即函数调用"——没有状态保存在控件中，每帧完全重新构建 UI。不需要窗口管理器、事件队列、样式引擎等繁杂基础设施。

**与 GTK 的对比**：

| 特性 | GTK | Nuklear |
|------|-----|---------|
| 架构 | 保留模式 (retained) | 即时模式 (immediate) |
| 依赖 | GLib, GDK, Pango, cairo | 仅需任意渲染后端 |
| 集成 | 独立应用 | 嵌入游戏/模拟器/工具 |
| 大小 | 巨大 | 一个头文件 |
| 样式 | CSS-like | 硬编码或自定义 |

```c
struct nk_context ctx;
nk_init_default(&ctx, &font);
if (nk_begin(&ctx, "Demo", nk_rect(50, 50, 200, 200),
    NK_WINDOW_BORDER | NK_WINDOW_TITLE)) {
    nk_layout_row_static(&ctx, 30, 80, 1);
    if (nk_button_label(&ctx, "Click Me"))
        printf("Clicked!\n");
}
nk_end(&ctx);
nk_clear(&ctx);
```

> Nuklear 需要"宿主"提供渲染后端（OpenGL、DirectX、SDL、X11 等）。常与 SDL2 + OpenGL 组合使用，用于游戏内 UI、调试工具、小工具。

**跨语言参考**: [[../../2深化/08_标准库深度|C标准库深度剖析]]
