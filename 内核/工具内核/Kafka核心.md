
# Kafka 核心

> 分布式消息队列的日志内核——不可变追加日志、分区、消费者组偏移管理、ISR 复制。

## 概念

Kafka 是一个分布式流处理平台，核心是一个"不可变、顺序追加的分布式日志"。它的设计哲学极为精简：所有数据按顺序追加到分区日志文件中，每个消息由 (offset) 唯一索引。消费者通过记录已消费的偏移量 (offset) 实现消费进度管理。Kafka 用 Java 编写，部分组件 (如存储层) 用 C++ 重写 (Tiered Storage)。

## 核心组件

| 组件 | 职责 | 关键机制 |
|------|------|---------|
| Topic | 消息的逻辑分类 | 可分多个分区 |
| Partition | 水平扩展的基本单位 | 顺序追加日志, 不可变 |
| Segment | 分区文件的物理分段 | 每个 segment 是一个文件 |
| Offset | 消息在分区内的唯一 ID | 单调递增 (per partition) |
| Consumer Group | 分布式消费组 | 自动负载均衡 |
| ISR | In-Sync Replicas | 消息不丢失的复制保证 |
| Leader / Follower | 每个分区的 leader 处理读写 | Controller 管理 leader 选举 |

## 分区日志模型

```
Topic "user-events" (3 partitions):

Partition 0:  [msg0:offset=0] [msg1:offset=1] [msg2:offset=2] [msg3:offset=3] [msg4:offset=4] ...
Partition 1:  [msg0:offset=0] [msg1:offset=1] [msg2:offset=2] ...
Partition 2:  [msg0:offset=0] [msg1:offset=1] [msg2:offset=2] [msg3:offset=3] ...

每个 Partition 是物理上一个目录:
    /data/user-events-0/
        00000000000000000000.log    (segment: offset 0 → 1000)
        00000000000000000000.index  (稀疏索引)
        00000000000000001000.log    (segment: offset 1000 → 2000)
        00000000000000001000.index

消费者组消费:
    Group "analytics":
        Consumer A → Partition 0  (offset=2, 消费中)
        Consumer B → Partition 1  (offset=5, 消费中)
        Consumer C → Partition 2  (offset=0, 消费中)

    偏移量存储在 __consumer_offsets topic 中 (Kafka 内部主题)
```

## Consumer Group 偏移管理

```
消费者组协调:
    消费者组通过 __consumer_offsets topic 持久化每个分区的消费偏移量

    消息投递语义:
        At-most-once:
            fetch 消息 → commit offset → 处理消息
            (处理失败则丢消息)

        At-least-once:
            fetch 消息 → 处理消息 → commit offset
            (处理失败不 commit, 下次重收; 可能重复处理)

        Exactly-once:
            Kafka 0.11+ 支持事务:
                beginTransaction()
                producer.send("A"), producer.send("B")
                consumer.commit()  // 原子提交: 生产和消费的位移一起提交
                commitTransaction()

    消费者 Rebalance:
        新消费者加入或退出 → 分区重新分配
        Rebalance 期间消费暂停
        常见策略: Range, RoundRobin, Sticky
```

## ISR 复制机制

```
假设 Partition 0 有 3 个副本:

    Leader (Broker 1):     [0][1][2][3][4][5][6][7][8][9]  (LEO=10, HW=8)
    Follower A (Broker 2): [0][1][2][3][4][5][6][7][8]      (LEO=9)
    Follower B (Broker 3): [0][1][2][3][4][5][6][7][8]      (LEO=9)

    LEO (Log End Offset): 该副本最后一条消息的 offset + 1
    HW  (High Watermark): 所有 ISR 副本中最小的 LEO

    消费者只能读到 HW 之前的数据 (offset < HW)
    // 保证消费者不会读到可能未确认的数据

    ISR (In-Sync Replicas):
        与 Leader 保持同步 (滞后不超过 replica.lag.time.max.ms) 的副本集合
        ISR = [Broker1, Broker2, Broker3]   (所有副本都同步)

        如果 Follower B 滞后:
            ISR = [Broker1, Broker2]
            HW 变为 9  (Broker2 的 LEO)
            acks=all 时 producer 只等 ISR 中的 follower 确认
```

---

## 交叉链接

- [[../../cpp教程/cpp深化教程/13_多线程|C++ 多线程]] -- Kafka 线程模型
- [[../../cpp教程/cpp深化教程/15_C++标准库|C++ 标准库]] -- Java NIO vs C++ I/O 库
- [[../../数据结构/F_队列_Queue|队列]] -- 日志的本质是队列
- [[../../数据结构/O_B树_BTree|B-Tree]] -- 对比: 日志存储 vs B-Tree
- [[../../数据结构/G_哈希表_HashTable|哈希表]] -- Consumer Group 元数据存储
- [[../系统内核/03_文件系统|文件系统]] -- 日志文件的零拷贝 sendfile
- [[../系统内核/06_并发与同步|并发与同步]] -- ISR 的分布式共识
- [[SQLite内核|SQLite 内核]] -- WAL 日志对比
- [[Redis内核|Redis 内核]] -- Redis Stream vs Kafka
- [[MySQL内核|MySQL/InnoDB 内核]] -- Redo log (循环日志) vs Kafka log (无限追加)
