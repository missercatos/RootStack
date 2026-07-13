# Crypto++

完全由 C++ 实现的密码学库，无外部依赖。提供大量密码学算法（对称/非对称加密、哈希、MAC、密钥协商等），包含一些学术性的前沿算法。API 设计风格偏 90 年代 C++。

## 核心组件

| 组件 | 说明 |
|------|------|
| AES / DES / Blowfish | 对称加密算法 |
| RSA / DSA / ECDSA | 非对称加密和签名 |
| SHA-1 / SHA-256 / SHA-3 | 哈希算法 |
| HMAC / CMAC | 消息认证码 |
| DH / ECDH | 密钥协商 |
| CryptoPP::AutoSeededRandomPool | 安全随机数生成 |
| CryptoPP::FileSource / FileSink | 文件 I/O 封装 |

## 何时使用

- 需要丰富算法支持的密码学研究
- 算法对比测试和教育用途
- 不满足于常规算法的特殊密码学需求
- 需要纯 C++ 无外部依赖的加密方案

## 关键特性

纯 C++ 实现、海量算法、学术覆盖广、无外部依赖

## 相关链接

- [[OpenSSL|OpenSSL]] — TLS/SSL 和加密
- [[Botan|Botan]] — 现代 C++ 加密库
- [[../../c语言教程/库大全/第三方库/相关文件|C 第三方库]]
- [[../索引|库索引]]
- (搜索: Crypto++)
