# Abseil

Google 内部开源的基础 C++ 库，支持 Google 内部数千个项目。提供增强的容器、字符串处理、同步原语、时间管理等。设计哲学与 Google 的 C++ 代码规范高度一致，也影响了许多后来进入标准的特性。

## 核心组件

| 组件 | 说明 |
|------|------|
| absl::flat_hash_map / set | 高性能哈希容器（替代 unordered_map） |
| absl::btree_map / set | 有序容器（替代 std::map） |
| absl::StrCat / StrJoin | 高效字符串操作 |
| absl::StrFormat | 类似 printf 但类型安全的格式化 |
| absl::string_view | C++17 std::string_view 的 C++11 回退 |
| absl::Mutex / CondVar | 增强的同步原语 |
| absl::CivilTime | 日历时间处理 |
| absl::Status / StatusOr | 错误状态传播（类似 Rust Result） |

## 何时使用

- 需要经过超大规模验证的基础工具
- 遵循 Google C++ 风格的项目
- flat_hash_map 替代 std::unordered_map
- 需要 Status/StatusOr 错误处理模式

## 关键特性

Google 内部验证、增强容器、高效字符串、同步原语、良好文档

## 相关链接

- [[Boost|Boost]] — 功能最全的综合库
- [[Folly|Folly]] — Facebook 高性能库
- [[fmt|fmt]] — 格式化库（Abseil 也有 StrFormat）
- 
- (搜索: Abseil C++)
