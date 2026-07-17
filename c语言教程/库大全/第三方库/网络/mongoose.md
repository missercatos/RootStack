
# mongoose

| 属性 | 说明 |
|------|------|
| 功能 | 嵌入式 Web 服务器 + WebSocket |
| 许可证 | GPLv2 / 商业 |
| 仓库 | https://github.com/cesanta/mongoose |

**核心特点**：单一 .c 文件和 .h 文件即可集成，无需外部依赖。支持 HTTP/HTTPS、WebSocket、MQTT、文件上传、CGI。

```c
struct mg_mgr mgr;
mg_mgr_init(&mgr);
mg_http_listen(&mgr, "http://0.0.0.0:8000", handler, NULL);
while (1) mg_mgr_poll(&mgr, 1000);
```

**典型应用**：嵌入式设备 Web 管理界面、IoT 设备 REST API、轻量级 Web 服务。非常适合资源受限的嵌入式环境。

**跨语言参考**: [[../../../2深化/08_标准库深度|C标准库深度剖析]]
