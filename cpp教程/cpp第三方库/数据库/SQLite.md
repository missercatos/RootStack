# SQLite

世界上最广泛部署的嵌入式数据库引擎，零配置、无服务器、单文件存储。C 语言接口可直接在 C++ 中使用，也有大量 C++ 封装库（SQLiteCpp、sqlite_orm 等）。支持完整的 SQL 和事务。

## 核心组件

| 组件 | 说明 |
|------|------|
| sqlite3_open / close | 数据库文件打开和关闭 |
| sqlite3_exec | 执行 SQL 语句 |
| sqlite3_prepare / step | 预编译语句和逐行执行 |
| sqlite3_bind_* | 参数绑定（防 SQL 注入） |
| BEGIN/COMMIT/ROLLBACK | 事务控制 |
| WAL 模式 | 并发读写性能优化 |
| sqlite_orm | 现代 C++ ORM 封装 |

## 何时使用

- 桌面应用的本地存储
- 移动应用数据持久化
- 嵌入式设备数据管理
- 应用配置缓存和元数据存储

## 关键特性

嵌入式/零配置、单文件数据库、完整 SQL、事务、无服务器

## 相关链接

- [[SOCI|SOCI]] — 统一数据库抽象层
- [[MongoDB|MongoDB]] — NoSQL 替代方案
- 
- 
- (搜索: SQLite C++)
