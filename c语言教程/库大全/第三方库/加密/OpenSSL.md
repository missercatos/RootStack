
# OpenSSL

| 属性 | 说明 |
|------|------|
| 功能 | 全功能 TLS/SSL + 密码学工具包 |
| 许可证 | Apache 2.0 (3.x 起) |
| 仓库 | https://www.openssl.org/ |

**核心能力**：

| 模块 | 说明 |
|------|------|
| libssl | TLS/SSL 协议（1.0–1.3），X.509 证书管理 |
| libcrypto | 密码学原语：AES, RSA, ECC, SHA-256/512, HMAC, HKDF 等 |
| 命令行工具 | `openssl` 用于密钥生成、证书签发、测试 |

**典型 TLS 客户端**：

```c
SSL_CTX *ctx = SSL_CTX_new(TLS_client_method());
SSL *ssl = SSL_new(ctx);
SSL_set_fd(ssl, sockfd);
SSL_connect(ssl);
SSL_write(ssl, "GET / HTTP/1.0\r\n\r\n", 18);
```

**现状**：全球部署最广的密码学库。API 复杂且历史悠久，易误用。3.x 版大幅改进，但学习曲线依然陡峭。绝大多数服务器端 TLS 实现都依赖 OpenSSL 或其 fork（BoringSSL、LibreSSL）。

**跨语言参考**: [[../../2深化/08_标准库深度|C标准库深度剖析]]
