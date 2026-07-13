# cpp-httplib

仅由单个头文件组成的 HTTP/HTTPS 库，零依赖，同时提供客户端和服务端功能。支持 HTTPS(需 OpenSSL)、multipart form、文件上传下载、WebSocket、服务端推送、压缩等现代 HTTP 特性。

## 核心组件

| 组件 | 说明 |
|------|------|
| httplib::Client | HTTP/HTTPS 客户端，多方法请求 |
| httplib::Server | HTTP/HTTPS 服务端 |
| httplib::SSLClient | HTTPS 加密客户端 |
| httplib::SSLServer | HTTPS 加密服务端 |
| multipart form-data | 文件上传支持 |
| WebSocket | 双向实时通信 |

## 何时使用

- 快速搭建 REST API 服务器
- 嵌入式 HTTP 服务
- 原型开发，不想引入大体积依赖
- 需要同时拥有客户端和服务端的最小 HTTP 方案

## 关键特性

单头文件、零依赖、客户端+服务端、HTTPS、WebSocket

## 相关链接

- [[libcurl|libcurl]] — 成熟 HTTP 客户端
- [[Boost.Asio|Boost.Asio]] — 底层异步网络
- [[../../c语言教程/库大全/第三方库/相关文件|C 第三方库]]
- [[../索引|库索引]]
- (搜索: cpp-httplib)
