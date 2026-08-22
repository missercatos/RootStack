# SQLite 教程

SQLite 是**世界上部署量最大的数据库**：每台手机、每个浏览器、无数桌面软件和 IoT 设备里都跑着它。它不是客户端-服务器架构，而是嵌入式库——整个数据库就是磁盘上的一个文件，零配置、零运维、无网络端口。对 C/C++ 学习者来说，它还是学习数据库内部实现和给程序加持久化能力的最佳选择。

---

## 一、定位与适用场景

| 适合 SQLite | 不适合 SQLite |
|-------------|---------------|
| 移动端 App 本地存储（Android/iOS 内置） | 高并发写入的服务端 |
| 桌面软件（浏览器历史、聊天记录） | 多机通过网络共享访问 |
| IoT 与嵌入式设备 | 需要精细权限体系的多用户系统 |
| 单元测试与原型开发 | 超大并发 OLTP 业务 |
| 小型低流量网站 | — |

一句话判断：**数据只有一个进程访问、或以"文件"形式随程序分发，SQLite 就是首选；多个服务同时读写就上 MySQL/PostgreSQL。**

---

## 二、sqlite3 命令行快速上手

```bash
sqlite3 test.db          # 打开/创建数据库文件
```

### 2.1 常用点命令

点命令是 sqlite3 CLI 特有的元命令，以 `.` 开头且不加分号：

| 命令 | 作用 |
|------|------|
| `.tables` | 列出所有表 |
| `.schema 表名` | 查看建表语句 |
| `.headers on` | 显示列名 |
| `.mode column` | 列对齐显示（还有 csv/json/box 等） |
| `.databases` | 列出当前连接的数据库文件 |
| `.dump` | 导出全部 SQL 语句到屏幕 |
| `.import file.csv t` | 导入 CSV 到表 t |
| `.read script.sql` | 执行 SQL 脚本 |
| `.quit` 或 `.exit` | 退出 |

一次典型的会话：

```sql
.headers on
.mode column
.mode box

CREATE TABLE books (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    price REAL
);

INSERT INTO books (title, price) VALUES ('C 程序设计', 59.9), ('算法导论', 128.0);

SELECT * FROM books;
```

### 2.2 点命令 vs SQL 的区分

| 类别 | 特征 | 示例 | 结尾分号 |
|------|------|------|----------|
| 点命令 | CLI 客户端指令，`.` 开头 | `.tables` `.mode column` | 不需要 |
| SQL 语句 | 数据库引擎执行，发给内核解析 | `SELECT ... FROM ...;` | 需要 |

记住：点命令只在 sqlite3 命令行里有意义，写进程序代码的必须是纯 SQL。

---

## 三、类型亲和性规则表

SQLite 的类型系统非常独特：建表时声明的类型只是"建议"，实际存储按**亲和性（Type Affinity）**规则决定。声明列类型时按以下规则映射到五种亲和：

| 亲和性 | 触发规则（声明类型包含…） | 存储行为 |
|--------|---------------------------|----------|
| INTEGER | 含 "INT"（INT/INTEGER/TINYINT...） | 尽量存为整数 |
| TEXT | 含 "CHAR"、"CLOB"、"TEXT" | 一律转文本存储 |
| BLOB | 无匹配任何规则（或声明为 BLOB） | 原样二进制存储，不做转换 |
| REAL | 含 "REAL"、"FLOA"、"DOUB" | 转浮点数存储 |
| NUMERIC | 其余情况（DECIMAL/NUMERIC/NUMBER...） | 能转数字就转，不能则原样存 |

实际影响举例：

```sql
CREATE TABLE t (a INTEGER, b TEXT, c NUMERIC, d BLOB);

INSERT INTO t VALUES ('123', '123', '123', '123');
-- a 列存入整数 123（INTEGER 亲和把文本转成了数字）
-- b 列保持文本 '123'
-- c 列存入整数 123（NUMERIC 亲和优先数字）
-- d 列保持文本 '123'（BLOB 亲和不转换）
```

> 这是 SQLite 与其他数据库最大的思维差异：它是动态类型的。MySQL 里往 INT 列塞字符串要么报错要么强转，SQLite 则按亲和性灵活处理。写严谨代码仍应声明正确类型。

---

## 四、与 C/C++ 集成最小示例

SQLite 本身就是一个 C 库，Linux 发行版通常自带开发头文件：

```bash
# 安装开发包
sudo apt install libsqlite3-dev        # Ubuntu/Debian
sudo pacman -S sqlite                  # Arch 自带头文件
gcc main.c -lsqlite3 -o app            # 编译时链接 -lsqlite3
```

完整可编译示例，覆盖核心 API 四步走：**open → prepare → step → finalize**：

```c
/* sqlite_demo.c — 编译: gcc sqlite_demo.c -lsqlite3 -o sqlite_demo */
#include <stdio.h>
#include <sqlite3.h>

static int callback(void *unused, int argc, char **argv, char **colname)
{
    (void)unused;
    for (int i = 0; i < argc; i++)
        printf("%s = %s\n", colname[i], argv[i] ? argv[i] : "NULL");
    printf("----\n");
    return 0;   /* 返回非 0 可中止查询 */
}

int main(void)
{
    sqlite3 *db;
    char *err = NULL;

    /* 1. 打开数据库（不存在则创建文件） */
    if (sqlite3_open("test.db", &db) != SQLITE_OK) {
        fprintf(stderr, "open failed: %s\n", sqlite3_errmsg(db));
        return 1;
    }

    /* 2. 建表并插入数据 */
    const char *setup_sql =
        "CREATE TABLE IF NOT EXISTS students ("
        "  id   INTEGER PRIMARY KEY AUTOINCREMENT,"
        "  name TEXT NOT NULL,"
        "  age  INTEGER);"
        "DELETE FROM students;"
        "INSERT INTO students (name, age) VALUES ('Alice', 18), ('Bob', 19);";
    if (sqlite3_exec(db, setup_sql, NULL, NULL, &err) != SQLITE_OK) {
        fprintf(stderr, "exec failed: %s\n", err);
        sqlite3_free(err);
        sqlite3_close(db);
        return 1;
    }

    /* 3. 参数化查询：prepare -> bind -> step -> finalize */
    sqlite3_stmt *stmt;
    const char *query = "SELECT id, name, age FROM students WHERE age > ?;";
    if (sqlite3_prepare_v2(db, query, -1, &stmt, NULL) != SQLITE_OK) {
        fprintf(stderr, "prepare failed: %s\n", sqlite3_errmsg(db));
        sqlite3_close(db);
        return 1;
    }
    sqlite3_bind_int(stmt, 1, 17);          /* 第 1 个 ? 绑定为 17 */

    while ((sqlite3_step(stmt)) == SQLITE_ROW) {      /* 逐行取结果 */
        int id   = sqlite3_column_int(stmt, 0);
        const unsigned char *name = sqlite3_column_text(stmt, 1);
        int age  = sqlite3_column_int(stmt, 2);
        printf("%d %s %d\n", id, name, age);
    }
    sqlite3_finalize(stmt);                   /* 释放语句对象 */

    /* 4. 回调方式执行查询（另一种风格） */
    sqlite3_exec(db, "SELECT * FROM students;", callback, NULL, &err);

    sqlite3_close(db);                        /* 关闭连接 */
    return 0;
}
```

核心 API 速查：

| API | 职责 |
|-----|------|
| `sqlite3_open()` / `sqlite3_close()` | 打开/关闭数据库连接 |
| `sqlite3_exec()` | 一把梭执行 SQL + 可选回调（适合无结果集语句） |
| `sqlite3_prepare_v2()` | 把 SQL 编译为语句对象 |
| `sqlite3_bind_int/text()` | 给 `?` 占位符绑定参数，**防 SQL 注入的正确姿势** |
| `sqlite3_step()` | 推进一行；SQLITE_ROW 表示有数据，SQLITE_DONE 表示结束 |
| `sqlite3_column_*()` | 取当前行某列的值 |
| `sqlite3_finalize()` | 销毁语句对象 |

---

## 五、Python sqlite3 模块示例

Python 标准库内置 SQLite 支持，无需安装任何东西：

```python
import sqlite3

# 连接（文件不存在自动创建；":memory:" 为内存数据库）
conn = sqlite3.connect("test.db")
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id   INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age  INTEGER
    )
""")

# 参数化插入（用 ? 占位符，防注入）
cur.execute("INSERT INTO students (name, age) VALUES (?, ?)", ("Carol", 20))
cur.executemany(
    "INSERT INTO students (name, age) VALUES (?, ?)",
    [("Dave", 18), ("Eve", 19)],
)
conn.commit()                       # 写操作必须 commit

# 查询
cur.execute("SELECT id, name, age FROM students WHERE age >= ?", (18,))
for row in cur.fetchall():
    print(row)

cur.close()
conn.close()

# 更省事的上下文管理器写法
with sqlite3.connect("test.db") as conn:
    for row in conn.execute("SELECT name FROM students"):
        print(row[0])
```

---

## 六、常见限制

| 限制 | 说明 |
|------|------|
| 并发写弱 | 整库同一时刻只支持一个写者（WAL 模式下读可并行），高并发写场景直接淘汰 |
| 无网络访问 | 数据库就是本地文件，跨机器共享需应用层自己解决（强行放 NFS 上会损坏数据） |
| 权限体系缺失 | 没有用户、角色、GRANT，谁能读到文件谁就有全部权限，靠文件系统权限兜底 |
| 单文件体积建议上限 | 官方支持到 TB 级，但实践中超过几十 GB 后运维工具链就不如服务端数据库顺手 |
| 部分 SQL 特性缺失 | 无存储过程、原生不支持 RIGHT/FULL JOIN（新版已补）、ALTER 能力有限 |

这些限制不是缺陷而是取舍——省掉的一切换来了零配置和极致轻量（核心几百 KB）。

---

## 七、备份

### 7.1 .backup 在线备份命令

```sql
.backup backup.db       -- 在线安全备份为另一个文件（点命令）
```

```bash
# 命令行等价形式
sqlite3 test.db ".backup /backup/test_backup.db"
```

### 7.2 dump 导出 SQL 文本

```bash
# 全库导出为 SQL 语句
sqlite3 test.db .dump > backup.sql

# 只导出指定表
sqlite3 test.db ".dump students" > students.sql

# 恢复（重放 SQL）
sqlite3 newdb.db < backup.sql

# 定期备份 cron 示例：每天凌晨拷贝一份带日期的备份
# crontab: 30 3 * * * sqlite3 /app/data/app.db ".backup /backup/app_$(date +\%F).db"
```

由于数据库就是单个文件，最简单的冷备就是停服后直接 `cp`——这也是嵌入式方案的运维优势之一。在线热备请一律使用 `.backup` 而不是直接复制正在被写的文件。

---

## 八、本章小结

| 主题 | 要点 |
|------|------|
| 定位 | 嵌入式单文件、零配置，部署量世界第一 |
| 场景 | 移动端/桌面/IoT/测试选它，多进程高并发写避开它 |
| CLI | 点命令管客户端（.tables/.mode），SQL 分号结尾管数据 |
| 类型 | 五种亲和性 INTEGER/TEXT/BLOB/REAL/NUMERIC，动态类型系统 |
| C 集成 | open → prepare → bind → step → finalize，链接 -lsqlite3 |
| 备份 | 在线用 .backup，冷备直接 cp，恢复重放 dump |

---
**返回** [[../数据库目录|数据库目录]]
