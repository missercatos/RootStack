# Boost

"C++ 的准标准库"——Boost 是 C++ 社区最重要的第三方库集合，包含 150+ 个库。许多 Boost 库最终被采纳为 C++ 标准（如智能指针、线程、filesystem、any、variant、optional 等）。每个库独立，可以按需使用。

## 核心组件

| 组件 | 说明 | 已进标准? |
|------|------|-----------|
| Boost.Asio | 异步 I/O 和网络编程 | C++26 |
| Boost.Beast | HTTP/WebSocket 基于 Asio | 否 |
| Boost.Spirit | 解析器生成框架 (PEG) | 否 |
| Boost.Filesystem | 跨平台文件操作 | C++17 |
| Boost.SmartPtr | shared_ptr / intrusive_ptr | C++11 |
| Boost.ProgramOptions | 命令行参数解析 | 否 |
| Boost.PropertyTree | 树形配置数据 (XML/JSON/INI) | 否 |
| Boost.Algorithm | 丰富算法扩展 | 部分 |
| Boost.Hana | 编译期元编程 | 否 |
| Boost.MultiIndex | 多索引容器 | 否 |

## 何时使用

- 需要标准库之外的通用功能
- 几乎所有大型 C++ 项目都依赖至少部分 Boost 组件
- 标准化的组件应尽量用 std 替代

## 关键特性

准标准、组件极全、高代码质量、跨平台、大部分 header-only

## 注意

Boost 是"瑞士军刀"但不是"轻量"，编译时间和二进制体积都较大。

## 相关链接

- [[fmt|fmt]] — 标准化前的格式化库
- [[Abseil|Abseil]] — Google 基础库
- [[Folly|Folly]] — Facebook 高性能库
- [[../网络/Boost.Asio|Boost.Asio]] — Boost 的网络模块
- [[../索引|库索引]]
- (搜索: Boost C++)
