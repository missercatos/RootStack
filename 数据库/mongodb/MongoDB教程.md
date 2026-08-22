# MongoDB 教程

MongoDB 是最流行的文档型 NoSQL 数据库。数据以 **BSON**（Binary JSON）格式存储，没有固定表结构（schema-free），同一集合中的文档可以拥有不同的字段。适合快速迭代、结构多变的业务场景。

---

## 一、定位与概念映射

从关系型数据库迁移过来，最大的门槛是术语体系。一张表对照：

| 关系型数据库 | MongoDB | 说明 |
|--------------|---------|------|
| database | database | 数据库，概念一致 |
| table（表） | collection（集合） | 无固定结构的"表" |
| row（行） | document（文档） | 一条 BSON 记录 |
| column（列） | field（字段） | 文档内的键 |
| primary key | `_id` | 自动生成的唯一主键（默认 ObjectId） |
| JOIN | `$lookup`（聚合） | 不鼓励跨集合关联，倾向内嵌 |
| 索引 | index | 概念一致 |

核心思想差异：关系库追求范式化拆表，MongoDB 鼓励**把相关数据内嵌进一个文档**，用一次读取换掉多次 JOIN。

---

## 二、安装与 mongosh 连接

```bash
# Docker 方式（推荐）
docker run -d --name mongo -p 27017:27017 \
    -e MONGO_INITDB_ROOT_USERNAME=admin \
    -e MONGO_INITDB_ROOT_PASSWORD=mongo123 \
    mongo:7
```

Linux 也可通过 apt 官方仓库安装 `mongodb-org` 包后 `systemctl enable --now mongod` 启动。

mongosh 是官方新版 Shell（替代旧版 mongo）：

```javascript
// 本机连接
mongosh

// 带认证连接
mongosh "mongodb://admin:mongo123@localhost:27017"

// 进入后常用命令
show dbs              // 列出数据库
use shop              // 切换/创建数据库（插入数据后才真正落盘）
show collections      // 列出集合
db.stats()            // 当前库状态
```

> 注意：`use` 创建的库在写入第一条文档前是看不见的，这是惰性创建。

---

## 三、CRUD 全套

以下示例假设已 `use shop`，操作 `users` 集合。

### 3.1 插入：insertOne / insertMany

```javascript
// 单条插入
db.users.insertOne({
    name: "张三",
    age: 25,
    tags: ["vip", "beta"],
    address: { city: "北京", zip: "100000" }
})

// 批量插入（返回插入的 _id 数组）
db.users.insertMany([
    { name: "李四", age: 30, tags: ["vip"] },
    { name: "王五", age: 22, tags: [] },
    { name: "赵六", age: 35, tags: ["svip"], balance: 500 }
])
```

### 3.2 查询：find 条件与投影

```javascript
// 全部文档
db.users.find()

// 格式化输出
db.users.find().pretty()

// 条件查询
db.users.find({ name: "张三" })

// 多条件（隐式 AND）
db.users.find({ name: "张三", age: 25 })

// 投影：只显示 name 和 age（_id 默认总显示）
db.users.find({}, { name: 1, age: 1 })

// 排除某些字段
db.users.find({}, { address: 0, tags: 0 })

// 只取一条
db.users.findOne({ name: "张三" })

// 计数 / 排序 / 截断
db.users.find({ age: { $gt: 20 } }).count()
db.users.find().sort({ age: -1 }).limit(5).skip(10)
```
### 3.3 更新：updateOne / updateMany

更新必须使用更新操作符，直接传文档会整体替换（危险）：

```javascript
// 更新第一条匹配文档
db.users.updateOne(
    { name: "张三" },          // 过滤条件
    { $set: { age: 26 } }      // 更新操作
)

// 更新所有匹配文档
db.users.updateMany(
    { age: { $lt: 18 } },
    { $set: { status: "minor" } }
)

// upsert：不存在则插入
db.users.updateOne({ name: "新用户" }, { $set: { age: 40 } }, { upsert: true })
```

### 3.4 删除：deleteOne / deleteMany

```javascript
db.users.deleteOne({ name: "赵六" })

db.users.deleteMany({ age: { $gt: 60 } })

db.users.deleteMany({})   // 清空集合（保留索引定义）
```

---

## 四、查询操作符大全

| 操作符 | 含义 | 示例 |
|--------|------|------|
| `$eq` / `$ne` | 等于 / 不等于 | `{ age: { $ne: 25 } }` |
| `$gt` / `$gte` | 大于 / 大于等于 | `{ age: { $gt: 18 } }` |
| `$lt` / `$lte` | 小于 / 小于等于 | `{ price: { $lte: 100 } }` |
| `$in` | 在数组列表内 | `{ tag: { $in: ["a", "b"] } }` |
| `$nin` | 不在数组列表内 | `{ status: { $nin: ["off"] } }` |
| `$or` | 或 | `{ $or: [{ age: { $lt: 18 } }, { vip: true }] }` |
| `$and` | 与（显式写法） | `{ $and: [{ age: { $gt: 18 } }, { age: { $lt: 60 } }] }` |
| `$not` | 取反 | `{ age: { $not: { $gt: 30 } } }` |
| `$exists` | 字段是否存在 | `{ balance: { $exists: true } }` |
| `$regex` | 正则匹配 | `{ name: { $regex: "^张", $options: "i" } }` |
| `$elemMatch` | 数组元素同时满足多条件 | `{ scores: { $elemMatch: { $gt: 80, $lt: 90 } } }` |
| `$type` | 按类型过滤 | `{ age: { $type: "int" } }` |

组合示例：

```javascript
// 年龄在 18-60 之间 且 (北京 或 上海)
db.users.find({
    age: { $gte: 18, $lte: 60 },
    $or: [
        { "address.city": "北京" },
        { "address.city": "上海" }
    ]
})
```

---

## 五、嵌套文档与数组查询

这是 MongoDB 区别于 SQL 的重点能力：

```javascript
// 示例数据
db.students.insertMany([
    { name: "小明", address: { province: "浙江", city: "杭州" }, scores: [85, 92, 78],
      courses: [{ title: "C语言", grade: "A" }, { title: "数据结构", grade: "B" }] },
    { name: "小红", address: { province: "江苏", city: "南京" }, scores: [95, 88],
      courses: [{ title: "C++", grade: "A" }, { title: "算法", grade: "S" }] }
])
```

```javascript
// 点号访问嵌套字段（注意加引号）
db.students.find({ "address.city": "杭州" })

// 整个嵌套对象精确匹配（顺序敏感，很少用）
db.students.find({ address: { province: "浙江", city: "杭州" } })

// 数组：包含某元素即命中
db.students.find({ scores: 85 })

// 数组按索引取值
db.students.find({ "scores.0": { $gte: 90 } })

// 数组大小
db.students.find({ scores: { $size: 3 } })

// 数组元素同时满足多个条件
db.students.find({ scores: { $elemMatch: { $gt: 80, $lt: 90 } } })

// 对象数组中按内部字段查
db.students.find({ "courses.title": "算法" })

// $slice 投影：只返回数组前 n 个元素
db.students.find({}, { scores: { $slice: 2 } })
```

---

## 六、聚合管道 pipeline

聚合是 MongoDB 的数据分析核心，数据像流水线一样依次经过各个阶段（stage），每个阶段的输出是下一个阶段的输入——和 Unix 管道 `|` 的思想完全一致。

### 6.1 各阶段速览

| 阶段 | 作用 | SQL 类比 |
|------|------|---------|
| `$match` | 过滤文档 | WHERE |
| `$group` | 分组统计 | GROUP BY |
| `$sort` | 排序 | ORDER BY |
| `$project` | 字段筛选与计算列 | SELECT 列表 |
| `$limit` / `$skip` | 截断 / 跳过 | LIMIT / OFFSET |
| `$unwind` | 把数组拆成多条文档 | 行转列展开 |

### 6.2 完整示例

示例数据（订单集合）：

```javascript
db.orders.insertMany([
    { user: "张三", amount: 200, status: "paid",   items: ["键盘", "鼠标"] },
    { user: "张三", amount: 350, status: "paid",   items: ["显示器"] },
    { user: "李四", amount: 120, status: "pending", items: ["鼠标垫"] },
    { user: "李四", amount: 800, status: "paid",   items: ["主机", "电源", "风扇"] },
    { user: "王五", amount: 50,  status: "cancelled", items: ["数据线"] }
])
```

需求：统计**已支付订单**中每个用户的总金额与订单数，只看总额超过 400 的用户，按总额倒序取前两名：

```javascript
db.orders.aggregate([
    // 1. 过滤：等价 WHERE status = 'paid'
    { $match: { status: "paid" } },

    // 2. 分组：等价 SELECT user, SUM(amount), COUNT(*) ... GROUP BY user
    { $group: {
        _id: "$user",
        total:  { $sum: "$amount" },
        orders: { $sum: 1 },
        avgAmt: { $avg: "$amount" }
    }},

    // 3. HAVING：过滤分组结果
    { $match: { total: { $gt: 400 } } },

    // 4. 排序
    { $sort: { total: -1 } },

    // 5. 取前 2 名
    { $limit: 2 },

    // 6. 整理输出格式（_id 改名为 user）
    { $project: {
        _id: 0,
        user: "$_id",
        total: 1,
        orders: 1,
        avgAmt: { $round: ["$avgAmt", 2] }
    }}
])
```

### 6.3 $unwind 展开

```javascript
// 每个 item 拆成一条文档
db.orders.aggregate([
    { $match: { status: "paid" } },
    { $unwind: "$items" },          // 5 条订单 → 6 条商品记录
    { $group: {
        _id: "$items",
        soldCount: { $sum: 1 }
    }},
    { $sort: { soldCount: -1 } }
])
```

---

## 七、索引

没有索引时每个查询都是全集合扫描（类比 O(n) 遍历链表），索引把查找降到近似 O(log n)（底层为 B-Tree）。

```javascript
// 单字段索引
db.users.createIndex({ age: 1 })            // 1 升序，-1 降序

// 复合索引（遵循最左前缀原则，同 MySQL）
db.users.createIndex({ age: 1, name: 1 })

// 唯一索引（重复插入报错）
db.users.createIndex({ email: 1 }, { unique: true })

// 稀疏索引：只为存在该字段的文档建索引
db.users.createIndex({ phone: 1 }, { sparse: true })

// TTL 索引：expireAfterSeconds 秒后自动删除文档（会话/日志场景神器）
db.sessions.createIndex({ createdAt: 1 }, { expireAfterSeconds: 3600 })

// 查看集合上的所有索引
db.users.getIndexes()

// 删除索引
db.users.dropIndex("age_1")
```

### 7.1 explain 分析查询计划

```javascript
db.users.find({ age: { $gt: 20 } }).explain("executionStats")
```

关注输出中的关键字段：

| 字段 | 含义 |
|------|------|
| `winningPlan.stage` | COLLSCAN=全表扫（坏）；IXSCAN=走索引（好） |
| `totalDocsExamined` | 实际扫描的文档数 |
| `nReturned` | 返回的文档数 |
| `executionTimeMillis` | 耗时毫秒 |

`nReturned ≈ totalDocsExamined` 说明索引效率高；两者差距悬殊则需要优化。

---

## 八、副本集与分片

| 特性 | 一句话说明 |
|------|-----------|
| 副本集（Replica Set） | 一主多从自动故障转移：主节点写入，从节点异步复制，主挂了从节点自动选举上位 |
| 分片（Sharding） | 水平拆分：按分片键把海量数据分散到多台机器，解决单机容量与写入瓶颈 |

生产环境标配是"分片集群 + 每个分片内部是副本集"，学习阶段单机即可。

---

## 九、适用场景

| 场景 | 是否适合 | 原因 |
|------|---------|------|
| 商品目录 / CMS 内容 | 适合 | 字段不固定，嵌套结构一次读全 |
| 用户画像 / 标签系统 | 适合 | 数组字段天然支持标签 |
| 日志 / 埋点分析 | 适合 | 写入吞吐高 + 聚合管道分析 + TTL 自动过期 |
| 移动端 Feed 流 | 适合 | 文档模型贴合 JSON API |
| 强事务的多表关联业务（如账务核心） | 不适合 | 跨文档事务支持弱且代价高，选关系库 |
| 需要大量复杂 JOIN 的报表 | 不适合 | $lookup 性能远不如关系库 JOIN |

---

## 十、速查卡

| 分类 | 关键命令 |
|------|---------|
| 库与集合 | `show dbs` / `use db` / `show collections` |
| 插入 | `insertOne` / `insertMany` |
| 查询 | `find(filter, projection)` / `findOne` |
| 更新 | `updateOne` / `updateMany` + `$set` |
| 删除 | `deleteOne` / `deleteMany` |
| 比较 | `$gt` `$gte` `$lt` `$lte` `$in` `$nin` |
| 逻辑 | `$and` `$or` `$not` |
| 结构 | `$exists` `$type` `$elemMatch` |
| 正则 | `$regex` |
| 聚合 | `$match` → `$group` → `$sort` → `$project` |
| 展开数组 | `$unwind` |
| 索引 | `createIndex` / `getIndexes` / `dropIndex` |
| 分析 | `.explain("executionStats")`，拒绝 COLLSCAN |
| 高可用 | 副本集（复制+选主）、分片（水平扩展） |

---

**返回** [[../数据库目录|数据库目录]]
