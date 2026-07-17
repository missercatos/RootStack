# Boost.Asio

C++ 异步 I/O 的事实标准，提供跨平台的 TCP/UDP/串口/定时器/信号处理等异步操作。采用 Proactor 设计模式，支持回调、协程 (C++20) 等多种编程模型。Asio 是 Networking TS 的基础，即将进入 ISO C++ 标准。

## 核心组件

| 组件 | 说明 |
|------|------|
| io_context | 异步操作的事件循环核心 |
| steady_timer | 异步定时器，支持取消 |
| ip::tcp::socket | TCP 套接字操作 |
| ip::udp::socket | UDP 套接字操作 |
| ssl::stream | SSL/TLS 加密流（需 OpenSSL） |
| awaitable / co_await | C++20 协程支持 |
| signal_set | 异步信号处理 |
| serial_port | 串口通信 |

## 何时使用

- 需要高性能异步网络通信的服务器后端
- 网络中间件、IoT 网关
- 需要持久连接和并发处理的项目

## 关键特性

异步 I/O、协程支持、SSL 集成、定时器、信号处理

## 相关链接

- [[../综合/Boost|Boost 总览]]
- [[libcurl|libcurl]] — 高层 HTTP 客户端
- [[gRPC|gRPC]] — RPC 框架
- 
- 
- (搜索: Boost.Asio)
