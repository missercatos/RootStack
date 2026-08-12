
# MySQL/InnoDB 内核

> MySQL 的事务存储引擎——B+Tree 索引、MVCC 多版本并发、缓冲池、Redo/Undo 日志。

## 概念

InnoDB 是 MySQL 的默认存储引擎，也是研究"如何构建 ACID 事务系统"的最佳教材。它解决了数据库最核心的两个问题：1) 如何组织海量数据使其可快速检索 (B+Tree)；2) 如何在并发更新时保证一致性 (MVCC + Redo/Undo)。InnoDB 的内核代码约 40 万行 C/C++。

## 核心组件

| 组件 | 职责 | 关键概念 |
|------|------|---------|
| B+Tree 索引 | 聚集索引 (主键) + 二级索引 | 页 (16KB), 填充因子 |
| 缓冲池 (Buffer Pool) | 热数据的内存缓存 | LRU list, 脏页刷新 |
| MVCC | 读写不互斥的多版本并发控制 | ReadView, undo log 链 |
| Redo Log | 已提交事务的日志 (崩溃恢复) | 循环写, 顺序 I/O |
| Undo Log | 事务回滚 + MVCC 历史版本 | undo segment |
| 隔离级别 | RU / RC / RR / Serializable | 间隙锁, next-key lock |
| 查询优化器 | SQL → 执行计划, 索引选择 | 成本估算 |

## B+Tree 存储架构

```
B+Tree (与 B-Tree 的关键区别):
 所有数据只存储在叶子节点
 内部节点仅存储 key + 子页指针 (导航用)
 叶子节点之间用双向链表连接 (范围查询)

表 "users" (InnoDB 聚集索引):
 Interior Page (内部节点 16KB):
 [Infimum] [key:10, page:4] [key:30, page:5] [key:50, page:6] [Supremum]

 Leaf Page (叶子节点, 含完整数据):
 <--prev--| [row(10): {name:"A", age:22}] [row(20): {name:"B", age:30}] ... |--next-->

 二级索引 (例如 idx_age):
 叶子节点存储: {age, 主键值}
 回表查询: 从二级索引得到主键 → 用主键去聚集索引查完整数据

页内结构:
 +-------------------+-----------+--------------+---------------------+
 | File Header (38B) | Infimum + | User Records | Free Space → |
 | | Supremum | (数据记录) | |
 +-------------------+-----------+--------------+---------------------+
 | Page Directory | File Trailer (8B) |
 +-------------------+-----------------------------------------------+
```

## MVCC (多版本并发控制)

```
MVCC 核心规则:
 每行记录有 2 个隐藏列:
 DB_TRX_ID: 最后一次修改该行的事务 ID
 DB_ROLL_PTR: undo log 回滚指针

 读操作 (SELECT):
 生成 ReadView: 记录当前活跃事务 ID 列表
 读取一行时:
 IF 该行 DB_TRX_ID < ReadView.min_trx_id:
 可见 (事务在 ReadView 之前已提交)
 ELSE IF 该行 DB_TRX_ID == 当前事务 ID:
 可见 (自己的修改)
 ELSE:
 不可见 → 沿 DB_ROLL_PTR 找到历史版本
 直到找到可见的版本

 写操作 (UPDATE):
 1. 写 undo log: 记录修改前的旧值
 2. 修改缓冲池中的页 (标记为脏)
 3. 写 redo log: 记录 "在页 X 偏移 Y 处将 A 改为 B"
 4. DB_TRX_ID = 当前事务 ID
```

## Redo Log + Undo Log 协同

```
事务提交:
 1. 写 undo log (记录旧值, 可能用于回滚)
 2. 修改缓冲池中的数据页 (脏页)
 3. 写 redo log buffer (在内存中)
 4. 事务提交 (COMMIT):
 a. redo log buffer 写盘 (redo log 文件, 顺序追加)
 b. 脏页仍在缓冲池中, 不立刻写盘 (异步刷盘)
 5. 崩溃恢复:
 将 redo log 应用于数据页 → 保证已提交事务不丢失
 未提交事务的 undo log 回滚 → 保证原子性

 这是 Write-Ahead Logging (WAL) 的具体应用
```

## 隔离级别

| 隔离级别 | 脏读 | 不可重复读 | 幻读 | 加锁策略 |
|---------|------|----------|------|---------|
| READ UNCOMMITTED | Y | Y | Y | 几乎不加锁 |
| READ COMMITTED | N | Y | Y | 行级锁, 每个语句生成新 ReadView |
| REPEATABLE READ | N | N | Y (MVCC 解决部分) | 行级锁 + gap lock, 一个事务一个 ReadView |
| SERIALIZABLE | N | N | N | 全表锁, 串行执行 |

---

