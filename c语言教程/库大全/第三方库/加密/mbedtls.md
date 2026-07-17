
# mbedtls

| 属性 | 说明 |
|------|------|
| 功能 | 轻量级 TLS 和密码学库 |
| 许可证 | Apache 2.0 |
| 仓库 | https://github.com/Mbed-TLS/mbedtls |

**核心特点**：以嵌入式/IoT 为设计目标，支持通过配置头文件裁剪功能。代码量远小于 OpenSSL（约 1/10），更易阅读和审计。

| 特性 | 说明 |
|------|------|
| TLS 1.2 / 1.3 | 完整支持 |
| DTLS | 数据报 TLS（UDP 加密） |
| 可配置 | `mbedtls_config.h` 按需开启算法 |
| 内存可控 | 可提供自定义 malloc/free |
| PSA Crypto API | 平台安全架构标准接口 |

```c
mbedtls_ssl_context ssl;
mbedtls_ssl_init(&ssl);
mbedtls_ssl_config conf;
mbedtls_ssl_config_init(&conf);
mbedtls_ssl_conf_authmode(&conf, MBEDTLS_SSL_VERIFY_REQUIRED);
mbedtls_ssl_setup(&ssl, &conf);
```

**典型场景**：嵌入式 Linux 设备、微控制器（ARM Mbed OS）、Android/iOS 应用内嵌 TLS（从 OpenSSL 迁移）。

**跨语言参考**: [[../../../2深化/08_标准库深度|C标准库深度剖析]]
