# fmt

现代 C++ 字符串格式化库，"C++20 std::format 的前身"。比 printf 类型安全，比 iostream 简洁高效。编译期格式字符串检查，无需繁琐的流式输出。C++20 之后标准库已经内置，但 fmt 仍提供更多扩展。

## 核心组件

| 组件 | 说明 |
|------|------|
| fmt::format() | 返回格式化后的 std::string |
| fmt::print() | 直接输出到 stdout |
| fmt::format_to() | 写入输出迭代器 |
| fmt::arg() / fmt::join() | 命名参数和容器连接 |
| fmt::chrono | 日期时间格式化 |
| fmt::color / fmt::emphasis | 终端彩色文本输出 |
| FMT_COMPILE() | 编译期格式串预编译 |
| std::formatter<T> | C++20 标准格式化特化 |

## 何时使用

- 几乎任何 C++ 项目的字符串格式化和输出
- 替代 iostream 和 printf
- 需要彩色终端输出
- C++17 项目需要 safe 格式化（C++20 前）

## 关键特性

类型安全、编译期检查、高效、C++20 std::format 基础、彩色输出

## 相关链接

- [[Boost|Boost]] — Boost.Format 替代
- [[../日志/spdlog|spdlog]] — 基于 fmt 的日志库
- [[../../c语言教程/库大全/相关文件|C 功能库]]
- 
- (搜索: fmtlib)
