# wxWidgets

使用各平台原生控件渲染的跨平台 GUI 库，Windows 上是 Win32 控件，macOS 上是 Cocoa，Linux 上是 GTK。外观与平台原生应用完全一致。无需预编译步骤，纯 C++ 语法。

## 核心组件

| 组件 | 说明 |
|------|------|
| wxFrame | 顶层窗口框架 |
| wxPanel / wxDialog | 面板和对话框 |
| wxButton / wxTextCtrl | 基本控件集合 |
| wxGrid / wxListCtrl | 表格和列表控件 |
| wxSizer | 自动布局管理 |
| wxThread | 跨平台线程封装 |
| wxSocket | 网络套接字 |

## 何时使用

- 需要与操作系统原生外观一致的应用
- 纯 C++ 无预编译器的 GUI 需求
- 需要跨平台但不接受 Qt 重量的项目
- 文件管理器、编辑器类桌面工具

## 关键特性

原生控件渲染、纯 C++ 无预编译、丰富的控件集

## 权衡

外观原生自然，但"最小公共集"导致部分平台特有功能无法使用。API 较老旧，社区和生态不如 Qt 活跃。

## 相关链接

- [[Qt|Qt]] — 功能最全的 GUI 框架
- [[DearImGui|Dear ImGui]] — 即时模式 GUI
- [[../../c语言教程/库大全/第三方库/相关文件|C 第三方库]]
- [[../索引|库索引]]
- (搜索: wxWidgets)
