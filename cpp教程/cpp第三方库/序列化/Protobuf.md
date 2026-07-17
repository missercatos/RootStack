# Protobuf

Google 的"Protocol Buffers"是二进制序列化的行业标准。通过 .proto 文件定义数据结构，编译器生成 C++（及其他语言）的序列化/反序列化代码。二进制格式紧凑、向后兼容、支持 schema 演化。

## 核心组件

| 组件 | 说明 |
|------|------|
| .proto 文件 | 定义消息结构和服务接口 |
| protoc 编译器 | 生成多语言序列化代码 |
| SerializeToString / ParseFromString | 序列化与反序列化 |
| Repeated / Map 字段 | 数组和映射类型 |
| oneof | 互斥字段（类似 union） |
| 反射 (Reflection) | 运行时访问消息元信息 |
| Arena 分配 | 批量内存管理，减少分配开销 |

## 何时使用

- 微服务间通信（配合 gRPC）
- 配置文件持久化
- 网络协议定义
- 跨语言数据交换
- 需要紧凑格式和 schema 验证的场景

## 关键特性

schema 定义、二进制紧凑、跨语言、向后兼容、结构化验证

## 相关链接

- [[../网络/gRPC|gRPC]] — 基于 protobuf 的 RPC 框架
- [[nlohmann-json|nlohmann/json]] — JSON 序列化
- [[yaml-cpp|yaml-cpp]] — YAML 配置格式
- 
- (搜索: Protocol Buffers C++)
