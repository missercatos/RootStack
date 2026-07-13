# SOCI

"C++ Database Access Library" — 统一的 C++ 数据库访问抽象层。通过一个通用 API 操作不同数据库后端（MySQL、PostgreSQL、SQLite、Oracle 等）。使用流式操作符和类型安全的参数绑定，风格与 C++ 标准流一致。

## 核心组件

| 组件 | 说明 |
|------|------|
| soci::session | 数据库会话，管理连接 |
| soci::statement | 预编译 SQL 语句 |
| operator<< and >> | 流式数据输入输出 |
| soci::row / rowset | 查询结果集 |
| soci::use / into | 参数绑定（use 输入，into 输出） |
| 后端插件 | MySQL、PostgreSQL、SQLite、Oracle 等 |

## 何时使用

- 需要支持多种数据库的项目
- 希望隔离数据库差异的后端服务
- 不想绑定到特定数据库的应用程序
- 需要类型安全的数据库访问

## 关键特性

统一数据库抽象 API、流式语法、类型安全、多后端支持

## 相关链接

- [[SQLite|SQLite]] — 嵌入式数据库
- [[MongoDB|MongoDB]] — NoSQL 驱动
- [[../../c语言教程/库大全/第三方库/相关文件|C 第三方库]]
- [[../索引|库索引]]
- (搜索: SOCI C++)
