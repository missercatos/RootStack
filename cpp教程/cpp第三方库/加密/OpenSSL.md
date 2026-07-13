# OpenSSL

互联网加密通信的事实基础设施。提供完整的 TLS/SSL 协议实现、X.509 证书管理、以及底层密码学原语（RSA、AES、ECDSA、SHA 等）。C 语言编写，C++ 可直接调用，也有 C++ 封装库。

## 核心组件

| 组件 | 说明 |
|------|------|
| libssl | TLS/SSL 协议实现 |
| libcrypto | 底层密码学原语库 |
| SSL_CTX / SSL | TLS 上下文和会话 |
| RSA / EC_KEY | 非对称密钥管理 |
| X509 / X509_STORE | 证书结构和证书库 |
| EVP_Digest* | 通用摘要（哈希）API |
| EVP_Encrypt* | 通用对称加密 API |
| BIO | 抽象 I/O 层 |

## 何时使用

- HTTPS 通信和 TLS 连接
- 证书管理和验证
- 加密隧道
- 几乎所有需要 TLS 的 C++ 应用

## 关键特性

TLS/SSL 全协议、证书管理、完整的密码学原语、FIPS 认证

## 相关链接

- [[Crypto++|Crypto++]] — 纯 C++ 密码学库
- [[Botan|Botan]] — 现代 C++ 加密库
- [[../../c语言教程/库大全/第三方库/索引|C 第三方库]]
- [[../索引|库索引]]
- (搜索: OpenSSL)
