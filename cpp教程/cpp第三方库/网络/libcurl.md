# libcurl

最广泛使用的 URL 传输库，支持 HTTP/HTTPS/FTP/FTPS/SFTP/SMTP 等 20+ 种协议。C 语言编写但提供完善的 C++ 封装(curlpp)。稳定、跨平台、经过数十亿次实战检验。

## 核心组件

| 组件 | 说明 |
|------|------|
| CURL *handle | 会话句柄，管理连接和选项 |
| curl_easy_* | 同步传输 API |
| curl_multi_* | 异步多路复用传输 |
| CURLOPT_* | 丰富的选项配置（代理、超时、SSL 等） |
| curl_formadd | multipart/form-data 上传 |
| curlpp | 官方推荐的 C++ RAII 封装 |

## 何时使用

- 发送 HTTP 请求、调用 REST API
- 下载文件、FTP 传输
- 任何需要做 HTTP 客户端的程序
- 需要支持多种网络协议的工具

## 关键特性

多协议支持、SSL/TLS、cookie 管理、认证机制、多连接复用

## 相关链接

- [[cpp-httplib|cpp-httplib]] — 头文件 HTTP 库
- [[../加密/OpenSSL|OpenSSL]] — SSL/TLS 后端
- 
- 
- (搜索: libcurl C++)
