# nlohmann/json

"JSON for Modern C++" — GitHub Stars 最多的 C++ 库之一。使用 C++11 的直观语法，支持类似 Python dict 的操作方式。头文件即可使用，支持 JSON Pointer 和 JSON Patch 标准。

## 核心组件

| 组件 | 说明 |
|------|------|
| nlohmann::json | 通用 JSON 值类型 |
| json::parse() | 字符串到 JSON 的解析 |
| json::dump() | JSON 到字符串的序列化 |
| operator[] / at() | 字段访问（类似 std::map） |
| json::json_pointer | RFC 6901 JSON Pointer 支持 |
| json::patch / diff | RFC 6902 JSON Patch 操作 |
| to_json / from_json | 自定义类型序列化 ADL hook |

## 何时使用

- 任何需要 JSON 解析和生成的项目
- REST API 客户端/服务端
- 配置文件和日志格式
- 优先选这个，除非有极强的性能要求

## 关键特性

直观的现代 C++ 语法、JSON Pointer/Patch、单头文件、STL 容器互操作

## 相关链接

- [[simdjson|simdjson]] — 极速 JSON 解析替代
- [[Protobuf|Protobuf]] — 二进制序列化
- [[yaml-cpp|yaml-cpp]] — YAML 配置格式
- 
- (搜索: nlohmann/json)
