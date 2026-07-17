
# SQLite3

| 属性 | 说明 |
|------|------|
| 类型 | 嵌入式关系数据库引擎 |
| 许可证 | 公共领域 |
| 仓库 | https://www.sqlite.org/ |

**核心概念**：SQLite 不是客户端-服务器数据库，而是一个直接读写磁盘文件的 C 库。整个数据库就是一个文件。

**核心 API**：

| 函数 | 说明 |
|------|------|
| `sqlite3_open` | 打开（或创建）数据库文件 |
| `sqlite3_exec` | 执行一条或多条 SQL |
| `sqlite3_prepare_v2` | 编译 SQL 为字节码（预编译语句） |
| `sqlite3_step` | 逐步执行预编译语句 |
| `sqlite3_column_int` / `text` / `double` | 获取当前行的列值 |
| `sqlite3_bind_int` / `text` / `double` | 绑定参数到预编译语句 |
| `sqlite3_close` | 关闭数据库连接 |

**典型用法**：

```c
sqlite3 *db;
sqlite3_open("data.db", &db);
sqlite3_exec(db, "CREATE TABLE users(id INT, name TEXT)", 0, 0, 0);

sqlite3_stmt *stmt;
sqlite3_prepare_v2(db, "INSERT INTO users VALUES(?, ?)", -1, &stmt, 0);
sqlite3_bind_int(stmt, 1, 100);
sqlite3_bind_text(stmt, 2, "Alice", -1, SQLITE_STATIC);
sqlite3_step(stmt);
sqlite3_finalize(stmt);
sqlite3_close(db);
```

> 使用预编译语句（`sqlite3_prepare_v2` + `sqlite3_bind_*`）而非字符串拼接以避免 SQL 注入。SQLite3 是世界上部署最广的数据库引擎。

**跨语言参考**: [[../../../2深化/08_标准库深度|C标准库深度剖析]]
