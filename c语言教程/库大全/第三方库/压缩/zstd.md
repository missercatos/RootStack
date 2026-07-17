
# zstd

| 属性 | 说明 |
|------|------|
| 算法 | Zstandard（Facebook 开发） |
| 格式 | .zst |
| 许可证 | BSD |
| 仓库 | https://github.com/facebook/zstd |

**核心特点**：在压缩比与速度之间实现极佳平衡。比 zlib 快数倍（尤其解压），同时达到接近 xz 的压缩比。

| 对比 | zlib (gzip) | zstd | liblzma (xz) |
|------|-------------|------|--------------|
| 压缩速度 | 慢 | 快 (5-10x zlib) | 极慢 |
| 解压速度 | 中等 | 极快 (3-5x zlib) | 中等 |
| 压缩比 | 中 | 中高 | 高 |
| 流式支持 | YES | YES | YES |

```c
size_t csize = ZSTD_compress(dst, dst_capacity, src, src_size, 3);
size_t dsize = ZSTD_decompress(dst, dst_capacity, src, csize);
```

**字典压缩**：zstd 的特色功能——预训练字典可显著提升小文件的压缩比，适合大量细碎数据的场景（如数据库块、日志）。

**跨语言参考**: [[../../../2深化/08_标准库深度|C标准库深度剖析]]
