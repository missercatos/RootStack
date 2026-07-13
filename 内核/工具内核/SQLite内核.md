
# SQLite 内核

> 世界上部署最广的数据库引擎——SQL 编译器 + VDBE 虚拟机 + B-Tree 存储 + Pager 层。

## 概念

SQLite 是一个嵌入式关系数据库，整个数据库是一个单一的 .db 文件。它的"内核"是一套精巧的分层架构：SQL 文本进入，经过词法/语法分析 → 字节码生成 → 虚拟机执行 → B-Tree 操作 → Pager 缓存 → OS 文件 I/O。SQLite 是"如何用纯 C 构建一个工业级引擎"的最佳教材。

## 核心组件

| 组件 | 职责 | 关键特征 |
|------|------|---------|
| Tokenizer | 词法分析: SQL 字符串 → token 流 | 手写词法分析器, 无 yacc/lex |
| Parser | 语法分析: token 流 → AST (语法树) | Lemon LALR(1) 解析器生成 |
| Code Generator | AST → VDBE 字节码 | 语义分析 + 优化合并 |
| VDBE | 字节码虚拟机: 执行 SQL 操作指令 | 类似汇编语言的 200+ 条操作码 |
| B-Tree | 数据组织: 每表一个 B-Tree, 每个索引一个 B-Tree | 变长页面 (512~65536 字节) |
| Pager | 页面缓存 + WAL 日志 + 事务锁 | LRU 淘汰策略 |
| OS 抽象层 | 平台无关 I/O: 文件读写, 锁, 内存映射 | VFS (Virtual File System) |

## SQL 编译流水线

```
SQL: "SELECT name FROM users WHERE age > 18 ORDER BY name"

    |        Tokenizer (tokenize.c)
    v
Tokens: SELECT, name, FROM, users, WHERE, age, >, 18, ORDER, BY, name

    |        Parser (parse.y → parse.c by Lemon)
    v
AST: SelectStmt
       ├── columns: [Expr(ColumnRef "name")]
       ├── from: [SrcTable "users"]
       ├── where: BinaryExpr(">", ColumnRef "age", Integer 18)
       └── orderBy: [OrderBy(ColumnRef "name", ASC)]

    |        Code Generator (select.c, where.c)
    v
VDBE Bytecode:
    0:  Init       0, 15, 0
    1:  OpenRead   0, 2, 0       // 打开 users 表 (cursor 0)
    2:  OpenRead   1, 3, 0       // 打开排序索引 (cursor 1)
    3:  Rewind     0, 10, 0      // 移到表头
    4:    Column   0, 2          // 读取 age 列
    5:    Ge       18, 9         // age >= 18? 否跳转到9
    6:    Column   0, 1          // 读取 name 列
    7:    MakeRecord 1, 0        // 生成排序 key
    8:    IdxInsert 1, 0         // 插入排序索引
    9:  Next       0, 4          // 下一行, 跳回4
    10: Close      0, 0
    11: Sort       1, 14
    12:   Column   1, 0
    13:   ResultRow 0, 1
    14: Next       1, 12
    15: Halt       0, 0
```

## VDBE 虚拟机

```c
// VDBE 执行循环 (sqlite3VdbeExec 简化)
struct Vdbe {
    Op *aOp;           // 字节码指令数组
    Mem *aMem;         // 内存寄存器数组
    int pc;            // 程序计数器
    Cursor *aCursor;   // B-Tree 游标 (表的"指针")
};

// 每条指令有 5 个操作数: P1, P2, P3, P4, P5
// 例如: OpenRead P1=cursor_id, P2=root_page, P3=opflags, P4=table_name
```

## B-Tree 存储层

```
表 "users" 的内部存储:
    B-Tree 根页 (Table 1, Root Page 2):
        Interior Page (内部节点, 存储 key + 子页指针):
            [key: 100, child: page3] [key: 200, child: page4] [key:300, child: page5]

        Leaf Page (叶子节点, 存储实际数据):
            [Cell 0: rowid=100, payload=(name:"Alice", age:22)]
            [Cell 1: rowid=101, payload=(name:"Bob",   age:35)]
            ...

索引 "idx_users_age" 的 B-Tree:
    Leaf Page:
        [Cell 0: key=(age:18, rowid:105)]
        [Cell 1: key=(age:22, rowid:100)]
        ...
```

## Pager 层 + WAL

```
传统回滚日志 (Rollback Journal):
    写事务前复制旧页到 journal 文件
    提交时删除 journal
    崩溃恢复时回滚 journal

WAL (Write-Ahead Log):
    写操作不直接修改主数据页
    而是追加到 WAL 文件末尾
    读操作首先检查 WAL 中是否有更新
    达到 checkpoint 阈值后合并 WAL 到主数据文件

WAL 优势:
    读写不互斥 (reader 不阻塞 writer)
    写入顺序追加 (磁盘友好)
    崩溃恢复简单 (只收尾 WAL)
```

---

## 交叉链接

- [[../../c语言教程/2深化/07_面向对象C编程|C 实现 OOP]] -- SQLite 的 VFS 插拔式设计
- [[../../c语言教程/2深化/03_动态内存管理|C 动态内存]] -- SQLite 自定义内存分配器
- [[../../cpp教程/cpp深化教程/15_C++标准库|C++ 标准库]] -- 对比 SQLite 与 std::map
- [[../../数据结构/O_B树_BTree|B-Tree 数据结构]]
- [[../../数据结构/G_哈希表_HashTable|哈希表]] -- SQLite 的 schema 存储
- [[../系统内核/03_文件系统|文件系统]] -- 数据库的终极优化目标
- [[../系统内核/06_并发与同步|并发与同步]] -- 事务锁和 WAL 并发
- [[MySQL内核|MySQL/InnoDB 内核]] -- 嵌入式 vs 客户端/服务器架构对比
- [[Redis内核|Redis 内核]] -- B-Tree vs 内存数据结构
