
# &lt;errno.h&gt; — 错误码

> **头文件**: `#include <errno.h>`
> 提供 C 语言最基础的错误报告机制：全局错误码变量 `errno` 和辅助函数。

---

## errno 变量

```c
extern int errno;
```

`errno` 是线程局部（C11 起）的可修改左值。标准库函数在发生错误时将其设置为非零值；成功时可能不变。**仅有文档明确声明会设置 errno 的函数才这样做**。

---

## 正确使用模式

```c
errno = 0;                          // 手动清零
long val = strtol(str, &endptr, 10);
if (errno == ERANGE) {              // 仅在函数返回时检查
    // 溢出
}
```

> 不要用 `errno == 0` 判断调用成功——成功时 errno 可能未被重置。

---

## 错误报告函数

| 函数 | 说明 |
|------|------|
| `perror(const char *s)` | 向 stderr 输出：`s: errno描述\n` |
| `strerror(int errnum)` | 返回 errnum 对应的错误描述字符串（静态缓冲区） |

---

## 标准错误码

| 宏 | 含义 |
|----|------|
| `EDOM` | 定义域错误，如 `sqrt(-1.0)` |
| `ERANGE` | 范围错误，如 `exp(1e10)` 溢出 |
| `EILSEQ` | 非法字节序列（多字节/宽字符转换，C95） |

POSIX 扩展了 `EINVAL`, `ENOMEM`, `EACCES`, `ENOENT` 等数十个错误码。

---

## 常见函数 errno 行为

| 头文件 | 函数 | 可能产生的 errno |
|--------|------|-----------------|
| `math.h` | `sqrt`, `log`, `asin` 等 | `EDOM` (域错误), `ERANGE` (溢出) |
| `stdlib.h` | `strtol`, `strtod` | `ERANGE` (溢出) |
| `stdio.h` | `fopen`, `fread` | 实现定义的错误码 |

---

## 跨语言参考

- [[../../2深化/08_标准库深度|C标准库深度]]
