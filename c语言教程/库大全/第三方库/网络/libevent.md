
# libevent

| 属性 | 说明 |
|------|------|
| 功能 | 事件驱动的网络 I/O |
| 许可证 | BSD |
| 仓库 | https://libevent.org/ |

libevent 是较早期的异步 I/O 库，提供 bufferevent 抽象（自动缓冲的异步 I/O）。支持 epoll/kqueue/select 后端。

**与 libuv 的对比**：

| 特性 | libevent | libuv |
|------|----------|-------|
| 优先级 | 老牌，成熟 | 现代，设计更统一 |
| Windows 支持 | 较弱 | 原生 IOCP |
| 文件 I/O | 无异步文件 I/O | 线程池异步文件 I/O |
| 生态 | memcached, tor, tmux | Node.js, Julia |
| DNS | evdns | 内置 getaddrinfo 异步 |

```c
struct event_base *base = event_base_new();
struct event *ev = event_new(base, fd, EV_READ|EV_PERSIST, callback, NULL);
event_add(ev, NULL);
event_base_dispatch(base);
```

**跨语言参考**: [[../../../2深化/08_标准库深度|C标准库深度剖析]]
