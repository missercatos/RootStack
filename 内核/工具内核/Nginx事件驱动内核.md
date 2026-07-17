
# Nginx 事件驱动内核

> 反向代理/Web 服务器的主从进程模型 + epoll 事件循环 + 状态机 HTTP 处理。

## 概念

Nginx 用纯 C 编写 (约 16 万行)，以高并发低内存著称。它的核心架构是一个 master 进程管理多个 worker 进程，每个 worker 是单线程 epoll 事件循环。与 Apache 的"每连接一线程/进程"模型不同，Nginx 的"worker = 单线程 + epoll"模型使得它在 C10K 问题下仍然能保持稳定。

## 核心组件

| 组件 | 职责 | 关键机制 |
|------|------|---------|
| Master 进程 | 配置读取、worker 管理、信号处理 | fork worker |
| Worker 进程 | 实际处理客户端连接 | 单线程 epoll |
| epoll 事件循环 | 非阻塞 I/O 多路复用 | EPOLLIN, EPOLLOUT |
| 阶段状态机 | HTTP 请求分阶段处理 | 11 个阶段 |
| 连接池 | 预分配连接对象复用 | ngx_connection_t |
| 共享内存 | worker 间共享数据 | slab 分配器 |
| Upstream | 反向代理到后端服务器 | 健康检查, 负载均衡 |

## Master + Worker 进程模型

```
Master 进程 (root 启动, 绑定 80/443):
    fork()
      |
      +-- Worker 1: 监听共享 socket, epoll 处理请求
      +-- Worker 2: 监听共享 socket, epoll 处理请求
      +-- Worker 3: 监听共享 socket, epoll 处理请求
      +-- Worker N: 监听共享 socket, epoll 处理请求
      +-- Cache Manager: 缓存管理
      +-- Cache Loader:  缓存加载

    Master 职责:
        信号处理: SIGHUP (reload 配置), SIGUSR1 (重开日志)
        Worker 监控: worker 异常退出 → 重启新 worker
        配置更新: 新配置加载 → 新 worker 继承 → 旧 worker 优雅退出
```

## epoll 事件循环

```c
// Nginx 事件循环核心 (简化)
void ngx_process_events_and_timers(ngx_cycle_t *cycle) {
    for (;;) {
        // 1. 计算超时时间
        ngx_time_update();
        timer = ngx_event_find_timer();
        delta = ngx_current_msec;

        // 2. 调用 epoll_wait (或 kqueue)
        events = epoll_wait(epfd, event_list, NEVENT, timer);

        // 3. 处理就绪事件
        for (i = 0; i < events; i++) {
            rev = event_list[i].data.ptr;   // ngx_connection_t
            if (event_list[i].events & EPOLLIN) {
                rev->handler(rev);  // ngx_http_wait_request_handler
            }
            if (event_list[i].events & EPOLLOUT) {
                wev->handler(wev);  // ngx_http_write_handler
            }
        }

        // 4. 处理到期定时器 (超时连接)
        ngx_event_expire_timers();

        // 5. 处理 posted events
        ngx_event_process_posted(cycle, &ngx_posted_accept_events);
        ngx_event_process_posted(cycle, &ngx_posted_events);
    }
}
```

## HTTP 阶段处理

```
Nginx 将 HTTP 请求处理拆分为 11 个阶段 (phases):

请求生命周期:
    NGX_HTTP_POST_READ_PHASE
        ↓ (读取完请求头)
    NGX_HTTP_SERVER_REWRITE_PHASE         (改写 URI, server 级别)
        ↓
    NGX_HTTP_FIND_CONFIG_PHASE            (匹配 location)
        ↓
    NGX_HTTP_REWRITE_PHASE                (改写 URI, location 级别)
        ↓
    NGX_HTTP_POST_REWRITE_PHASE           (检查是否需重新匹配)
        ↓
    NGX_HTTP_PREACCESS_PHASE              (访问限制预处理)
        ↓
    NGX_HTTP_ACCESS_PHASE                 (访问控制: allow/deny, auth)
        ↓
    NGX_HTTP_POST_ACCESS_PHASE            (访问控制后处理)
        ↓
    NGX_HTTP_PRECONTENT_PHASE             (生成内容前的最后钩子)
        ↓
    NGX_HTTP_CONTENT_PHASE                (内容生成: proxy_pass, fastcgi, static)
        ↓
    NGX_HTTP_LOG_PHASE                    (日志记录)

每个阶段可注册多个 handler, 按顺序执行
```

---

