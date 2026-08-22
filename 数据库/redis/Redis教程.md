# Redis 教程

Redis 是基于内存的键值（KV）数据库。核心特点：数据主要放内存所以极快（10 万+ QPS 量级）、命令处理采用**单线程模型**（避免锁竞争，瓶颈在网络而非 CPU）、支持持久化防止宕机丢数据。它是缓存、计数器、排行榜、分布式锁等场景的事实标准。

---

## 一、安装与 redis-cli 连接

```bash
# Ubuntu 安装
sudo apt install redis-server
sudo systemctl enable --now redis-server

# Docker 方式
docker run -d --name redis -p 6379:6379 redis:7

# 连接本机
redis-cli

# 连接远程并选库
redis-cli -h 192.168.1.100 -p 6379 -a yourpassword -n 0

# 直接执行命令不进入交互模式
redis-cli ping
redis-cli get mykey
```

进入交互模式后：

```text
127.0.0.1:6379> PING
PONG
127.0.0.1:6379> SELECT 1        # 切换到 1 号库（共 16 个，编号 0-15）
OK
```

---

## 二、通用命令

与具体类型无关、对任何 key 都能用的命令：

| 命令 | 说明 | 示例 |
|------|------|------|
| `KEYS pattern` | 匹配所有 key（`*` 通配） | `KEYS user:*` |
| `EXISTS key` | key 是否存在，返回 1/0 | `EXISTS name` |
| `DEL key` | 删除 key | `DEL name` |
| `EXPIRE key sec` | 设置过期时间（秒） | `EXPIRE code 60` |
| `TTL key` | 查看剩余生存时间；-1 永久 / -2 不存在 | `TTL code` |
| `PERSIST key` | 移除过期时间，变永久 | `PERSIST code` |
| `TYPE key` | 查看 value 的类型 | `TYPE user:1` |
| `RENAME old new` | 重命名 | `RENAME a b` |
| `SCAN cursor` | 渐进式遍历，替代 KEYS | `SCAN 0 MATCH user:* COUNT 100` |

> 生产环境禁用 `KEYS *`——Redis 单线程，百万级 key 时会阻塞所有请求数秒甚至更久。用 `SCAN` 分批遍历。

```redis
SET greeting "hello"
EXISTS greeting          # (integer) 1
TYPE greeting            # string
EXPIRE greeting 120
TTL greeting             # (integer) 118（剩余秒数）
DEL greeting
```

---

## 三、五大数据类型

### 3.1 String（字符串）

最基础的类型，value 可以是字符串、整数或浮点数（最大 512MB）。

| 命令 | 说明 |
|------|------|
| `SET key val` | 设置值（可带 `EX sec` 过期） |
| `GET key` | 取值 |
| `INCR key` | 自增 1（值必须为整数） |
| `INCRBY key n` | 自增 n |
| `DECR key` | 自减 1 |
| `SETNX key val` | 不存在时才设置（SET if Not eXists） |
| `MSET k1 v1 k2 v2` | 批量设置 |
| `MGET k1 k2` | 批量获取 |

**使用场景：缓存对象 JSON、计数器、分布式锁**

```redis
-- 计数器：文章阅读量
INCR article:1001:views
INCRBY article:1001:views 50

-- 分布式锁的雏形：抢到锁的人返回 1
SETNX lock:order:42 "worker-1"
EXPIRE lock:order:42 30        -- 防止死锁（实际推荐 SET ... NX EX 一条完成）
```

```redis
-- 原子化的加锁写法（NX = 不存在才设，EX = 30 秒过期）
SET lock:order:42 "worker-1" NX EX 30
```

### 3.2 Hash（哈希）

field-value 映射表，适合存对象，可单独读写某个字段。

| 命令 | 说明 |
|------|------|
| `HSET key field val` | 设置一个字段 |
| `HGET key field` | 取一个字段 |
| `HGETALL key` | 取全部字段和值 |
| `HMSET key f1 v1 f2 v2` | 批量设置字段 |
| `HDEL key field` | 删除字段 |
| `HEXISTS key field` | 字段是否存在 |
| `HKEYS key` / `HVALS key` | 所有字段名 / 所有值 |
| `HINCRBY key field n` | 字段整数值自增 n |

**使用场景：对象存储（用户信息、商品信息），比 String 存整个 JSON 更省流量地改单字段**

```redis
HSET user:1001 name "张三" age 25 city "北京"
HGET user:1001 name           # "张三"
HGETALL user:1001
-- 1) "name"
-- 2) "张三"
-- 3) "age"
-- 4) "25"
-- 5) "city"
-- 6) "北京"
HINCRBY user:1001 age 1       # 26
HDEL user:1001 city
```

### 3.3 List（列表）

双向链表实现的有序序列，两端插入弹出都是 O(1)，可作栈也可作队列。

| 命令 | 说明 |
|------|------|
| `LPUSH key val` | 左端（头部）推入 |
| `RPUSH key val` | 右端（尾部）推入 |
| `LPOP key` / `RPOP key` | 左端 / 右端弹出 |
| `LRANGE key start stop` | 取区间（-1 表示末尾） |
| `LLEN key` | 长度 |
| `BLPOP key timeout` | 阻塞式左弹出，队列空时等待最多 timeout 秒 |
| `LINDEX key i` | 按下标取元素 |
| `LTRIM key start stop` | 只保留区间，其余裁剪 |

**使用场景：消息队列、最新动态列表**

```redis
-- 简易消息队列：生产者从左推，消费者从右弹（FIFO）
LPUSH queue:email "mail-task-1"
LPUSH queue:email "mail-task-2"
RPOP queue:email              # "mail-task-1"

-- 阻塞式消费：队列空则挂起等待最多 5 秒，比轮询 RPOP 高效
BLPOP queue:email 5

-- 最新朋友圈动态：只留最近 100 条
LPUSH feed:user:1001 "post:88"
LTRIM feed:user:1001 0 99
LRANGE feed:user:1001 0 -1
```

### 3.4 Set（集合）

无序、不重复的字符串集合，底层哈希表，增删查都是 O(1)，独有优势是集合运算。

| 命令 | 说明 |
|------|------|
| `SADD key member` | 添加成员 |
| `SREM key member` | 删除成员 |
| `SISMEMBER key member` | 是否为成员（1/0） |
| `SMEMBERS key` | 所有成员 |
| `SCARD key` | 成员个数 |
| `SINTER key1 key2` | 交集 |
| `SUNION key1 key2` | 并集 |
| `SDIFF key1 key2` | 差集（在 key1 不在 key2） |
| `SRANDMEMBER key n` | 随机取 n 个成员 |
| `SPOP key` | 随机弹出成员 |

**使用场景：标签系统、共同好友、抽奖去重**

```redis
-- 用户兴趣标签
SADD user:1001:tags "C" "Linux" "数据库"

-- 共同关注：A 和 B 都关注了谁
SADD follow:a "u1" "u2" "u3"
SADD follow:b "u2" "u3" "u4"
SINTER follow:a follow:b      # "u2" "u3"

-- 可能认识的人：A 关注但 B 未关注
SDIFF follow:a follow:b       # "u1"

-- 抽奖：随机抽 3 名（不重复）
SADD lottery:1001 "alice" "bob" "carol" "dave" "eve"
SRANDMEMBER lottery:1001 3
```

### 3.5 ZSet（有序集合）

每个成员关联一个分数（score），按分数排序且不重复——Set 排序版。

| 命令 | 说明 |
|------|------|
| `ZADD key score member` | 添加/更新成员及分数 |
| `ZRANGE key start stop [WITHSCORES]` | 按分数升序取区间 |
| `ZREVRANGE key start stop WITHSCORES` | 按分数降序取区间 |
| `ZRANGEBYSCORE key min max` | 按分数范围取成员 |
| `ZSCORE key member` | 查成员分数 |
| `ZINCRBY key n member` | 给成员加分 |
| `ZRANK key member` | 升序排名（0 起） |
| `ZREVRANK key member` | 降序排名 |
| `ZCARD key` | 成员总数 |
| `ZREM key member` | 删除成员 |

**使用场景：排行榜、延迟队列（score 存执行时间戳）**

```redis
-- 游戏排行榜
ZADD leaderboard 1500 "alice"
ZADD leaderboard 1800 "bob"
ZADD leaderboard 1650 "carol"

-- Top 3（降序）
ZREVRANGE leaderboard 0 2 WITHSCORES
-- 1) "bob"
-- 2) "1800"
-- 3) "carol"
-- 4) "1650"
-- 5) "alice"
-- 6) "1500"

-- alice 加分后查看她的名次
ZINCRBY leaderboard 200 "alice"
ZREVRANK leaderboard "alice"      # (integer) 0 —— 第一名

-- 查询某分数段玩家
ZRANGEBYSCORE leaderboard (1600 +inf     -- 大于 1600（( 表示开区间）
```

---

## 四、持久化机制

内存数据断电即失，Redis 提供两种持久化方案：

| 对比项 | RDB（快照） | AOF（追加日志） |
|--------|------------|----------------|
| 原理 | 定时把内存全量数据二进制快照写入 dump.rdb | 把每条写命令追加记录到 appendonly.aof 文件 |
| 触发方式 | 手动 `SAVE/BGSAVE` 或按配置自动（如 60s 内 100 次修改） | 每条写命令到达即记录（appendfsync 策略决定刷盘时机） |
| 文件体积 | 小（紧凑二进制） | 大（文本命令流，需定期重写压缩） |
| 恢复速度 | 快（直接加载二进制） | 慢（逐条重放命令） |
| 数据安全 | 两次快照之间的数据会丢 | 最多丢 1 秒（everysec 策略） |
| 性能影响 | fork 子进程瞬间可能卡顿，平时几乎无开销 | 持续小开销，磁盘 IO 敏感 |
| 典型用途 | 容灾备份、主从全量同步 | 数据安全性要求高的缓存 |

关键配置项（redis.conf）：

```conf
# ---- RDB ----
save 900 1        # 900 秒内至少 1 次修改则触发快照
save 300 10       # 300 秒内 10 次
save 60 10000     # 60 秒内 10000 次
dbfilename dump.rdb
dir /var/lib/redis

# ---- AOF ----
appendonly yes                    # 开启 AOF
appendfsync everysec              # always=每命令刷盘 / everysec=每秒 / no=交给OS
auto-aof-rewrite-percentage 100   # AOF 体积翻倍时触发重写
auto-aof-rewrite-min-size 64mb    # 且最小超过 64MB
```

实践建议：两者同时开启，AOF 保证少丢数据，RDB 用于快速恢复与备份归档。

---

## 五、过期删除策略

设置了 EXPIRE 的 key 到期后如何被清除？Redis 采用**惰性删除 + 定期删除**的组合：

| 策略 | 原理 | 目的 |
|------|------|------|
| 惰性删除 | 访问某个 key 时先检查是否已过期，过期则删除并返回 nil | 不额外消耗 CPU，但冷数据可能一直占着内存 |
| 定期删除 | 后台周期性随机抽取一批设置过期的 key 检查，过期的直接删 | 弥补惰性删除对冷数据的遗漏，限制每次时长避免阻塞 |

两者配合仍可能有漏网之鱼（长期无人访问又没被抽中），Redis 还有内存淘汰策略兜底（如 `allkeys-lru` 在内存满时驱逐最久未使用的 key），由 `maxmemory-policy` 配置。

---

## 六、发布订阅

Redis 内置轻量级消息通道，发送者不关心谁在听：

```redis
-- 终端 1：订阅频道
SUBSCRIBE news:sports news:tech

-- 终端 2：向频道发布消息（返回收到消息的订阅者数量）
PUBLISH news:sports "国足 2:0 获胜"

-- 按模式订阅：匹配所有 channel.* 频道
PSUBSCRIBE news:*
```

要点：

- 消息**不落盘**：没有订阅者在线时发布的消息直接丢失，这是它和 List 消息队列的本质区别
- 无法追溯历史，适合实时通知类场景（聊天室、配置刷新广播）
- 需要可靠队列请用 List（BLPOP）或专业消息中间件

---

## 七、事务 MULTI/EXEC 与 pipeline 区别

Redis 事务保证命令**顺序执行不被插队**，但不支持回滚：

```redis
MULTI                 # 开启事务，后续命令进入队列
SET account:a 900
DECRBY account:b 100
EXEC                  # 按顺序执行队列中的全部命令
```

| 对比项 | MULTI/EXEC 事务 | pipeline 管道 |
|--------|----------------|---------------|
| 解决的问题 | 多条命令打包原子执行 | 减少 N 条命令的网络往返次数 |
| 原子性 | 有（执行期间不插入其他客户端命令） | 无（只是批量发送） |
| 中间结果 | 不能读取上一条的结果再决定下一步 | 同样不能 |
| 使用方式 | 服务端排队机制 | 客户端缓冲发送机制 |

> 注意：事务中某条命令运行时报错（如对 string 执行 LPUSH），**其他命令照常执行**，不会回滚——这与关系型数据库的事务语义差别很大。

补充一句 Lua 脚本：`EVAL "return redis.call('GET', KEYS[1])" 1 mykey` 可把多条命令写成一段脚本原子执行，还能读中间结果做条件逻辑，是比事务更强的原子操作手段（配合 `EVALSHA` 缓存脚本）。

---

## 八、高可用架构一句话

| 架构 | 一句话说明 |
|------|-----------|
| 主从复制 | 一主多从，从库异步复制主库数据，提供读扩展与数据冗余，但主挂了要人工切换 |
| 哨兵（Sentinel） | 在主从之上加一组监控进程，主库故障时自动选举新主并通知客户端，解决人工切换问题 |
| 集群（Cluster） | 数据按 16384 个槽位分片到多个主节点，每个主再挂从节点，同时解决容量与高可用 |

---

## 九、缓存三兄弟

使用 Redis 作缓存绕不开三个经典名词，面试高频：

| 名词 | 含义 | 典型解法 |
|------|------|---------|
| 缓存穿透 | 查询**根本不存在**的数据，缓存永远未命中，请求全部打到数据库（可能是恶意攻击） | 空值也短暂缓存；布隆过滤器前置拦截 |
| 缓存击穿 | 某个**热点 key 过期瞬间**，海量并发同时穿透到数据库重建缓存 | 热点 key 不过期；互斥锁只放一个请求去重建，其余等待 |
| 缓存雪崩 | **大量 key 同时过期**或 Redis 宕机，数据库瞬间被洪峰冲垮 | 过期时间加随机抖动错开；多级缓存；集群高可用 + 限流降级 |

记忆锚点：穿透是"查无此数据"，击穿是"一个热点失效"，雪崩是"一片集体失效"。

---

## 十、速查卡

| 分类 | 关键命令 |
|------|---------|
| 通用 | `KEYS`(慎用) / `SCAN` / `EXISTS` / `DEL` / `EXPIRE` / `TTL` / `TYPE` |
| String | `SET` / `GET` / `INCR` / `SETNX`（计数器与锁） |
| Hash | `HSET` / `HGET` / `HGETALL` / `HINCRBY`（对象存储） |
| List | `LPUSH` / `RPUSH` / `LRANGE` / `BLPOP`（消息队列） |
| Set | `SADD` / `SISMEMBER` / `SINTER` / `SDIFF`（标签与共同好友） |
| ZSet | `ZADD` / `ZRANGE` / `ZREVRANGE` / `ZSCORE`（排行榜） |
| 持久化 | RDB 快照（恢复快、可能丢段）vs AOF 日志（丢失少、文件大） |
| 发布订阅 | `SUBSCRIBE` / `PUBLISH`（不落盘、不追溯） |
| 原子批量 | 事务 MULTI/EXEC（不回滚）；pipeline（省网络往返）；Lua EVAL（更强原子性） |
| 高可用 | 主从 → 哨兵 → 集群，逐步升级 |
| 缓存三大坑 | 穿透（不存在）/ 击穿（热点失效）/ 雪崩（集体失效） |

---

**返回** [[../数据库目录|数据库目录]]
