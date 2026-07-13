# Botan

"现代 C++ 加密库" — 设计哲学强调安全易用性，API 采用现代 C++ 风格（RAII、智能指针、std::string）。支持 TLS、X.509、PKCS 等完整协议栈。默认安全高于性能的设计理念。

## 核心组件

| 组件 | 说明 |
|------|------|
| Botan::TLS::Client / Server | TLS 客户端/服务端实现 |
| Botan::X509_Certificate | X.509 证书管理 |
| Botan::PK_Signer / Verifier | 公钥签名和验证 |
| Botan::Cipher_Mode | 对称加密模式（AES-GCM 等） |
| Botan::HashFunction | 哈希函数系列 |
| Botan::AutoSeeded_RNG | 自动播种的安全随机数 |
| Botan::PBKDF / KDF | 基于密码的密钥派生 |

## 何时使用

- 需要"安全默认配置"的加密应用
- 偏好现代 C++ API 的团队
- C++ 原生加密的首选
- 当 OpenSSL 的 C 接口让人头疼时

## 关键特性

现代 C++ 风格、安全优先、完整协议栈、良好的文档

## 相关链接

- [[OpenSSL|OpenSSL]] — 行业标准加密库
- [[Crypto++|Crypto++]] — 纯 C++ 算法库
- [[../../c语言教程/库大全/第三方库/相关文件|C 第三方库]]
- [[../索引|库索引]]
- (搜索: Botan C++)
