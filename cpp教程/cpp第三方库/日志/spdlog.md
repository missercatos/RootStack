# spdlog

"Super fast C++ logging library" — GitHub 上最流行的 C++ 日志库。Header-only（也可编译为库），支持异步日志、多 sink（控制台/文件/系统日志）、自定义格式化、日志级别过滤。性能极高，基于 fmtlib 的格式化引擎。

## 核心组件

| 组件 | 说明 |
|------|------|
| spdlog::info / warn / error | 各级别日志宏 |
| spdlog::stdout_color_mt | 彩色控制台输出 |
| spdlog::basic_logger_mt | 文件日志 |
| spdlog::rotating_logger_mt | 按大小轮转文件日志 |
| spdlog::daily_logger_mt | 按日期轮转文件日志 |
| spdlog::async_logger | 异步日志（线程池） |
| spdlog::set_pattern() | 自定义日志格式 |

## 何时使用

- 几乎所有 C++ 项目的日志首选
- 从简单命令行工具到高性能服务器
- 需要异步非阻塞日志的场景
- 上手最快、性能最好的选择

## 关键特性

高性能、header-only、多 sink、异步日志、fmt 风格格式化、彩色终端输出

## 相关链接

- [[glog|glog]] — Google 日志库
- [[../综合/fmt|fmt]] — 底层格式化引擎
- [[../../c语言教程/库大全/第三方库/相关文件|C 第三方库]]
- [[../索引|库索引]]
- (搜索: spdlog)
