# Folly

Facebook(Meta) 开源的高性能 C++ 基础库。强调极致性能，包含高效的异步框架(futures)、内存分配器、序列化、并发数据结构等。部分组件比其他实现有显著的性能优势。

## 核心组件

| 组件 | 说明 |
|------|------|
| folly::fbvector | 高性能 vector 替代 |
| folly::fbstring | 针对小字符串优化的 string |
| folly::Future / SemiFuture | 高性能异步框架 |
| folly::AtomicHashMap | 高并发哈希表 |
| folly::ConcurrentSkipList | 并发跳表 |
| folly::Singleton | 单例模式管理 |
| folly::dynamic | 动态类型（类似 Python 值） |
| folly::IOBuf | 高效 I/O 缓冲区链 |

## 何时使用

- 性能敏感的基础设施项目
- 服务端和系统编程
- 需要比标准库更高性能的组件
- 大规模 C++ 服务（Facebook 同款）

## 关键特性

高性能设计、异步框架、高效内存管理、丰富并发组件

## 相关链接

- [[Boost|Boost]] — 功能最全的综合库
- [[Abseil|Abseil]] — Google 基础库
- [[../索引|库索引]]
- (搜索: Folly Facebook)
