
# libsodium

| 属性 | 说明 |
|------|------|
| 功能 | 现代加密库，强调安全性、易用性和防误用设计 |
| 许可证 | ISC (兼容 GPL) |
| 仓库 | https://libsodium.org/ |

**设计理念**：基于 NaCl (Networking and Cryptography library)。每个操作提供简单的高层 API，隐藏密钥管理、随机数生成、算法选择等细节。

| 操作 | API |
|------|-----|
| 对称加密 | `crypto_secretbox()` — XSalsa20 + Poly1305 |
| 公钥加密 | `crypto_box()` — Curve25519 + XSalsa20 + Poly1305 |
| 数字签名 | `crypto_sign()` — Ed25519 |
| 密码哈希 | `crypto_pwhash()` — Argon2id |
| 通用哈希 | `crypto_generichash()` — BLAKE2b |
| 随机数 | `randombytes_buf()` — 来源于操作系统 CSPRNG |

**典型对称加密**：

```c
unsigned char key[crypto_secretbox_KEYBYTES];
unsigned char nonce[crypto_secretbox_NONCEBYTES];
crypto_secretbox_easy(ciphertext, plaintext, len, nonce, key);
```

> 如果只需要加密/签名等密码学原语（不需要 TLS），libsodium 是首选——其 API 远简单于 OpenSSL，更难误用。

**跨语言参考**: [[../../../2深化/08_标准库深度|C标准库深度剖析]]
