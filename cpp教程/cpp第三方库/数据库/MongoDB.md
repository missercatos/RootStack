# MongoDB C++ Driver

MongoDB 的官方 C++ 驱动程序。提供符合 C++11 风格的 API，支持文档 CRUD 操作、聚合管线、批量操作、可定制连接池等。与 MongoDB 的查询语法和 BSON 数据类型自然映射。

## 核心组件

| 组件 | 说明 |
|------|------|
| mongocxx::client | MongoDB 客户端连接 |
| mongocxx::database | 数据库操作句柄 |
| mongocxx::collection | 集合操作（CRUD） |
| bsoncxx::builder | BSON 文档构建器 |
| mongocxx::pipeline | 聚合管线操作 |
| mongocxx::options | 各种操作选项配置 |
| mongocxx::pool | 连接池管理 |

## 何时使用

- 使用 MongoDB 作为数据存储的 C++ 项目
- 文档模型的灵活性适合数据结构多变的场景
- 需要聚合管线进行复杂查询
- 需要水平扩展的 NoSQL 应用

## 关键特性

C++11 风格、BSON 文档模型、聚合管线、连接池、官方维护

## 相关链接

- [[SQLite|SQLite]] — 嵌入式 SQL 替代
- [[SOCI|SOCI]] — 关系型数据库抽象
- [[../索引|库索引]]
- (搜索: mongocxx)
