
# libuv

| 属性 | 说明 |
|------|------|
| 功能 | 跨平台异步 I/O 框架 |
| 许可证 | MIT |
| 仓库 | https://github.com/libuv/libuv |

**核心概念**：libuv 是 Node.js 的底层 I/O 引擎。提供统一的**事件循环**抽象跨 Linux (epoll)、macOS (kqueue)、Windows (IOCP)。

| 组件 | 说明 |
|------|------|
| `uv_loop_t` | 事件循环，所有异步操作的调度中心 |
| `uv_tcp_t` / `uv_udp_t` | TCP / UDP 句柄 |
| `uv_connect` / `uv_read_start` | 异步连接和读取 |
| `uv_timer_t` | 定时器 |
| `uv_work_t` | 线程池任务（用于阻塞操作） |
| `uv_fs_*` | 异步文件操作 |
| `uv_pipe_t` / `uv_tty_t` | 管道和终端 |

**典型 TCP 客户端**：

```c
uv_loop_t *loop = uv_default_loop();
uv_tcp_t socket;
uv_tcp_init(loop, &socket);
uv_tcp_connect(&connect_req, &socket, addr, on_connect);
uv_run(loop, UV_RUN_DEFAULT);
```

**跨语言参考**: [[../../../2深化/08_标准库深度|C标准库深度剖析]]
