# Qt

C++ GUI 领域的"巨无霸"。不只是 GUI —— 它是一个完整的应用框架，包含网络、数据库、XML、OpenGL 等模块。使用 MOC (Meta-Object Compiler) 扩展 C++ 实现信号-槽机制。QML 提供声明式 UI 编写方式。LGPL/GPL/商业三许可证。

## 核心组件

| 组件 | 说明 |
|------|------|
| QWidget | 传统桌面控件体系 |
| QML / Qt Quick | 声明式 UI，适合触摸和动画 |
| 信号-槽 (Signals & Slots) | 松耦合事件通信机制 |
| Qt Network | HTTP/TCP/UDP 网络模块 |
| Qt SQL | 数据库访问抽象 |
| Qt Creator | 官方 IDE，集成 UI 设计器 |
| Qt 3D / Qt Charts | 3D 渲染和数据可视化 |

## 何时使用

- 商业桌面应用开发
- 需要功能最全的跨平台 GUI
- 嵌入式设备上的图形界面
- 需要声明式 UI (QML) 的项目

## 关键特性

跨平台原生渲染、信号-槽、QML、IDE(Qt Creator)、模块化设计

## 权衡

功能最全、生态最成熟，但体积庞大，MOC 预编译步骤增加构建复杂度，商业使用需关注许可证。

## 相关链接

- [[DearImGui|Dear ImGui]] — 即时模式 GUI
- [[wxWidgets|wxWidgets]] — 原生外观 GUI
- [[../../c语言教程/库大全/第三方库/相关文件|C 第三方库]]
- [[../索引|库索引]]
- (搜索: Qt framework)
