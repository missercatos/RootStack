
# Redis 内核

> 内存键值存储的数据结构服务器——ae 事件循环、SDS 动态字符串、RDB/AOF 持久化、主从复制。

## 概念

Redis 是一个内存数据结构服务器，用纯 C 编写 (约 12 万行)。它的"内核"是一个单线程事件循环处理所有客户端请求。Redis 的核心理念是：数据结构原生存储在内存中，网络 I/O 通过 epoll 多路复用，持久化通过 fork + Copy-on-Write 实现。Redis 是"如何用最少的代码构建一个高性能网络服务器"的范本。

## 核心组件

| 组件 | 职责 | 关键机制 |
|------|------|---------|
| ae 事件循环 | epoll/kqueue/select 驱动的异步 I/O | 文件事件 + 时间事件 |
| SDS | C 字符串的替代: O(1) 长度, 二进制安全, 预分配 | 兼容 C 字符串 API |
| Dict | 哈希表: rehash 渐进式 | 两个哈希表 rolling rehash |
| Skiplist | 有序集合 (ZSET) 的底层实现 | 概率平衡替代红黑树 |
| Ziplist/Listpack | 紧凑序列化存储: 连续内存, 省指针 | 小型 list/hash/zset |
| RDB | 快照持久化: fork() → 子进程写全量数据 | Copy-on-Write |
| AOF | 增量持久化: 每条写命令追加到日志 | 类似 WAL |
| 复制/哨兵/集群 | 高可用 + 水平扩展 | PSYNC, Raft |

## ae 事件循环

```c
// ae 事件循环核心 (ae.c)
typedef struct aeEventLoop {
    aeFileEvent *events;   // 注册的 fd 及其回调
    aeFiredEvent *fired;   // epoll_wait 返回的就绪事件
    aeTimeEvent *timeEventHead;  // 时间事件链表 (最近到期排最前)
};

void aeMain(aeEventLoop *eventLoop) {
    while (!eventLoop->stop) {
        // 计算离最近时间事件的毫秒数, 作为 epoll_wait 超时
        tv = shortestTimeEventTimeout(eventLoop);

        // 阻塞等待 I/O 事件 (epoll_wait)
        numevents = aeApiPoll(eventLoop, tv);

        // 处理所有就绪的文件事件
        for (i = 0; i < numevents; i++) {
            fileEvent->rfileProc(...); // 读事件回调
            fileEvent->wfileProc(...); // 写事件回调
        }

        // 处理所有到期的时间事件
        processTimeEvents(eventLoop);
    }
}
```

## 核心数据结构

```c
// SDS -- Simple Dynamic String
struct sdshdr {
    int len;     // 已使用长度 (O(1) strlen)
    int free;    // 剩余空间 (减少 realloc)
    char buf[];  // 柔性数组, 实际数据
};

// Dict -- 渐近式 rehash 哈希表
struct dict {
    dictEntry **table[2];   // table[0] 是当前, table[1] 是 rehash 目标
    long rehashidx;         // -1 表示未在 rehash
    // ...
};
// 每次 CRUD 操作附带移动 1 个桶, 分步完成 rehash

// Skiplist -- 有序集合的底层
struct zskiplistNode {
    sds ele;                      // 元素值
    double score;                 // 排序分数
    struct zskiplistLevel {
        struct zskiplistNode *forward;  // 前向指针
        unsigned int span;              // 跨度 (快速 rank 查询)
    } level[];                    // 多层 index (随机层数, 概率 1/4)
};
```

## RDB 持久化

```
主进程 (Redis Server):
    fork()
      |
      +-- 子进程:
      |       遍历所有 DB (共享内存 Copy-on-Write)
      |       将所有 key-value 序列化写入 dump.rdb
      |       退出
      |
      +-- 父进程:
              继续处理客户端请求
              如果父进程修改了数据 → 触发 Copy-on-Write → 子进程看到旧版本
              (fork 时刻的快照, 不是实时数据)
```

## AOF 持久化

```
每条成功执行的写命令追加到 AOF 文件:
    SET key "hello"  →  AOF: *3\r\n$3\r\nSET\r\n$3\r\nkey\r\n$5\r\nhello\r\n

AOF 重写 (BGREWRITEAOF):
    在子进程中, 基于当前内存数据生成最小命令集合
    例如: 一条 RPUSH list A → RPUSH list B → RPUSH list C
    重写为: RPUSH list A B C   (合并为一条)
```

## 主从复制

```
1. 从库连接主库, 发送 PSYNC <replication_id> <offset>
2. 主库检测是否可以部分同步 (offset 在复制缓冲区中)
   部分同步: 发送 offset 之后的增量命令
   全量同步: fork → 生成 RDB → 发送 RDB 给从库 → 发送缓冲区增量命令
3. 从库加载 RDB → 执行增量命令 → 进入实时同步
4. 主库每条写命令同时发送给所有已连接的从库
```

---

## 交叉链接

- [[../../c语言教程/2深化/01_指针深度剖析|C 指针]] -- SDS 的柔性数组 buf[]
- [[../../c语言教程/2深化/03_动态内存管理|C 动态内存]] -- jemalloc 内存分配
- [[../../c语言教程/2深化/04_函数指针与回调|C 函数指针]] -- ae 事件循环回调
- [[../../cpp教程/cpp深化教程/13_多线程|C++ 多线程]] -- Redis 6.0+ 多线程 I/O
- [[../../数据结构/G_哈希表_HashTable|哈希表]] -- Dict 实现
- [[../../数据结构/N_跳表_SkipList|跳表]] -- ZSET 底层结构
- [[../../数据结构/A_容器_Container|容器]] -- SDS, Ziplist 对比
- [[../系统内核/06_并发与同步|并发与同步]] -- 单线程原子性
- [[SQLite内核|SQLite 内核]] -- WAL vs AOF 对比
- [[MySQL内核|MySQL/InnoDB 内核]] -- 内存引擎 vs 磁盘引擎
