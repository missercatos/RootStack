
# brotli

| 属性 | 说明 |
|------|------|
| 算法 | Brotli（Google 开发，LZ77 + Huffman + 二阶上下文建模） |
| 格式 | .br |
| 许可证 | MIT |
| 仓库 | https://github.com/google/brotli |

**核心特点**：极高压缩比（类似 xz 水平），解压速度优秀。内置大型静态字典（针对 Web 文本优化），非常适合 Web 资源压缩。所有主流浏览器和 CDN 均支持 `br` (brotli) 内容编码。

| 对比 | brotli | gzip |
|------|--------|------|
| 文本压缩比 | 比 gzip 高 20-26% | 基准 |
| 解压速度 | 与 gzip 相当 | 基准 |
| 静态字典 | 预置 120KB Web 文本词典 | 无 |

```c
#include <brotli/encode.h>
size_t encoded_size = BrotliEncoderMaxCompressedSize(input_size);
BrotliEncoderCompress(BROTLI_DEFAULT_QUALITY, BROTLI_DEFAULT_WINDOW,
 BROTLI_DEFAULT_MODE, input_size, input,
 &encoded_size, output);
```

**跨语言参考**: [[../../../2深化/08_标准库深度|C标准库深度剖析]]
