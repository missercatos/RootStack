
# hiredis

| 属性 | 说明 |
|------|------|
| 功能 | Redis C 客户端库 |
| 许可证 | BSD |
| 仓库 | https://github.com/redis/hiredis |

**核心概念**：hiredis 是 Redis 官方的极简 C 客户端，同时提供**同步阻塞**和**异步回调**两种 API。

**同步 API**：

```c
redisContext *c = redisConnect("127.0.0.1", 6379);
redisReply *r = redisCommand(c, "SET key %s", "value");
freeReplyObject(r);
r = redisCommand(c, "GET key");
printf("%s\n", r->str);
freeReplyObject(r);
redisFree(c);
```

**异步 API**：通过集成 libevent、libuv 或自定义适配器实现非阻塞。

> `redisCommand` 使用类似 `printf` 的格式化参数构建 RESP 协议命令。返回的 `redisReply` 包含 `type`（字符串/数组/整数等）和对应字段。

**跨语言参考**: [[../../2深化/08_标准库深度|C标准库深度剖析]]
