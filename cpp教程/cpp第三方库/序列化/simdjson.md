# simdjson

"每秒可解析 GB 级别的 JSON"。利用 SIMD 指令（SSE4.2、AVX2、ARM NEON）实现的极速 JSON 解析器。解析速度比 nlohmann/json 快一个数量级以上。适合超大 JSON 文件或高吞吐的 JSON 处理。

## 核心组件

| 组件 | 说明 |
|------|------|
| simdjson::parser | 可复用的解析器实例 |
| simdjson::dom::element | DOM 树的节点类型 |
| simdjson::dom::array | JSON 数组访问 |
| simdjson::dom::object | JSON 对象访问 |
| simdjson::ondemand | 按需解析模式（更省内存） |
| simdjson::error_code | 错误码系统 |

## 何时使用

- 处理大体积 JSON 文件
- 高 QPS 的 JSON 日志解析
- 数据管道和 ETL
- 对性能敏感的 JSON 处理
- 注意：是只读解析器，生成 JSON 需配合其他库

## 关键特性

SIMD 加速、极速解析、单次遍历 DOM、线程安全

## 相关链接

- [[nlohmann-json|nlohmann/json]] — 功能全面的 JSON 库
- [[Protobuf|Protobuf]] — 二进制序列化
- [[../索引|库索引]]
- (搜索: simdjson)
