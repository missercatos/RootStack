
# LMDB

| 属性 | 说明 |
|------|------|
| 功能 | 内存映射键值存储（B+ 树） |
| 许可证 | OpenLDAP Public License |
| 仓库 | https://github.com/LMDB/lmdb |

**核心特点**：

| 特性 | 说明 |
|------|------|
| 存储模型 | 有序键值对，底层为内存映射的 B+ 树 |
| 事务 | 完全 ACID，MVCC（多版本并发控制） |
| 读性能 | 极快——无需锁，直接共享内存读取 |
| 写性能 | 一次最多一个写事务 |

**核心 API**：

```c
MDB_env *env;
mdb_env_create(&env);
mdb_env_open(env, "./lmdb_data", 0, 0664);

MDB_txn *txn;
mdb_txn_begin(env, NULL, 0, &txn);
MDB_dbi dbi;
mdb_dbi_open(txn, NULL, 0, &dbi);

MDB_val key = {4, "user"}, data = {5, "Alice"};
mdb_put(txn, dbi, &key, &data, 0);
mdb_txn_commit(txn);

mdb_env_close(env);
```

> LMDB 的读操作无需任何内存分配或内存拷贝——直接返回映射到数据页的指针。是 OpenLDAP 的后端存储，广泛用于嵌入式高性能场景。

**跨语言参考**: [[../../../2深化/08_标准库深度|C标准库深度剖析]]
