
# klib

| 属性 | 说明 |
|------|------|
| 类型 | 纯头文件库集合 |
| 许可证 | MIT |
| 仓库 | https://github.com/attractivechaos/klib |

**核心组件**：

| 组件 | 说明 |
|------|------|
| `khash` | 高性能开放寻址哈希表，支持 int、int64、字符串键 |
| `kvec` | 类型安全的动态数组（类似 C++ vector） |
| `kbtree` | B 树实现（有序键值存储） |
| `ksort` | 内省排序（introsort），优于标准库的 qsort |

**性能特点**：klib 的哈希表通常比 uthash 快 2-5 倍（开放寻址 vs 链地址），被广泛用于生物信息学等高性能场景（如 samtools、minimap2）。

```c
#include "khash.h"
KHASH_MAP_INIT_INT(32, char)
khash_t(32) *h = kh_init(32);
int ret;
kh_put(32, h, 5, &ret);       // 插入键 5
khiter_t k = kh_get(32, h, 5);
if (k != kh_end(h)) { /* 找到 */ }
kh_destroy(32, h);
```

**跨语言参考**: [[../../../cpp教程/cpp深化教程/04_动态内存|C++动态内存]]
