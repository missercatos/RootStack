
# zlib

| 属性 | 说明 |
|------|------|
| 算法 | DEFLATE（LZ77 + Huffman 编码） |
| 格式 | zlib (.zz)，gzip (.gz)，原始 DEFLATE |
| 许可证 | zlib License |
| 仓库 | https://zlib.net/ |

**核心 API**：

| 函数 | 说明 |
|------|------|
| `deflateInit` / `deflate` / `deflateEnd` | 流式压缩 |
| `inflateInit` / `inflate` / `inflateEnd` | 流式解压 |
| `compress` / `uncompress` | 一次性压缩/解压（内存到内存） |

```c
z_stream strm;
deflateInit(&strm, Z_DEFAULT_COMPRESSION);
strm.next_in = input;
strm.avail_in = input_len;
strm.next_out = output;
strm.avail_out = output_len;
deflate(&strm, Z_FINISH);
deflateEnd(&strm);
```

**现状**：zlib 是最通用的压缩库，几乎所有需要压缩的 C 程序（如 PNG、HTTP gzip、ZIP 文件、Git 对象）都直接或间接依赖它。压缩比中等，速度偏慢。

**跨语言参考**: [[../../2深化/08_标准库深度|C标准库深度剖析]]
