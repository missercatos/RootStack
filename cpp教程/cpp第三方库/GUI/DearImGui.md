# Dear ImGui

"即时模式 GUI" (Immediate Mode GUI) 的开创性实现。每一帧重新绘制整个界面，极简的 API 设计。主要用于游戏开发工具、调试面板、性能分析器等工具型界面，不适合传统桌面应用风格。

## 核心组件

| 组件 | 说明 |
|------|------|
| ImGui::Begin/End | 窗口创建和管理 |
| ImGui::Button/Text/Checkbox | 基本控件 |
| ImGui::Slider / Drag | 数值调节控件 |
| ImGui::InputText | 文本输入框 |
| ImGui::PlotLines / PlotHistogram | 实时数据绘图 |
| ImGui::DockSpace | 可停靠窗口布局 |
| 后端 (Backend) | 与 OpenGL/Vulkan/DirectX 等对接 |

## 何时使用

- 游戏开发工具和调试面板
- 性能分析器、编辑器界面
- 需要快速原型工具 UI
- 嵌入到渲染循环中的界面

## 关键特性

极简 API、无状态设计、与图形 API 无关（后端可插拔）、渲染效率高

## 权衡

写工具界面极快，但不适合传统桌面应用风格。外观"程序员审美"，定制需要额外工作。

## 相关链接

- [[Qt|Qt]] — 传统桌面 GUI 框架
- [[wxWidgets|wxWidgets]] — 原生桌面 GUI
- [[../../c语言教程/库大全/第三方库/相关文件|C 第三方库]]
- [[../索引|库索引]]
- (搜索: Dear ImGui)
