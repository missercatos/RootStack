
# libcurl

| 属性 | 说明 |
|------|------|
| 功能 | HTTP / HTTPS / FTP / SMTP / IMAP 等多协议客户端 |
| 许可证 | MIT-like (curl license) |
| 仓库 | https://curl.se/libcurl/ |

**核心概念**：libcurl 是 cURL 命令行工具的底层库。以"easy interface"和"multi interface"两种模式提供：

| 接口 | 说明 |
|------|------|
| `CURL *easy` | 同步阻塞式：`curl_easy_setopt`, `curl_easy_perform` |
| `CURLM *multi` | 异步非阻塞：单线程中同时处理多个连接 |

**典型同步请求**：

```c
CURL *curl = curl_easy_init();
curl_easy_setopt(curl, CURLOPT_URL, "https://example.com");
curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
CURLcode res = curl_easy_perform(curl);
curl_easy_cleanup(curl);
```

**关键特点**：自动处理重定向、cookie、SSL/TLS、代理、HTTP/2。几乎每个需要 HTTP 客户端的 C 项目都依赖它。

**跨语言参考**: [[../../2深化/08_标准库深度|C标准库深度剖析]]
