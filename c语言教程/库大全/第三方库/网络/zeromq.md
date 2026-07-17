
# ZeroMQ (zeromq)

| 属性 | 说明 |
|------|------|
| 功能 | 高性能异步消息队列 |
| 许可证 | MPL 2.0 |
| 仓库 | https://zeromq.org/ |

**核心概念**：ZeroMQ 不是传统的消息队列中间件，而是一个嵌入式的消息库，提供多种**socket 模式**：

| 模式 | 说明 |
|------|------|
| REQ-REP | 请求-回复，同步一对一 |
| PUB-SUB | 发布-订阅，一对多 |
| PUSH-PULL | 管道/扇出，负载均衡 |
| ROUTER-DEALER | 异步路由代理 |
| PAIR | 独占一对一 |

```c
void *ctx = zmq_ctx_new();
void *sock = zmq_socket(ctx, ZMQ_REQ);
zmq_connect(sock, "tcp://localhost:5555");
zmq_send(sock, "Hello", 5, 0);
zmq_close(sock);
zmq_ctx_destroy(ctx);
```

**跨语言参考**: [[../../../2深化/08_标准库深度|C标准库深度剖析]]
