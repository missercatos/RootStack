
# &lt;stdlib.h&gt; — 通用工具

> **头文件**: `#include <stdlib.h>`
> 提供动态内存管理、数值转换、随机数生成、排序搜索、进程控制等通用函数。

---

## 动态内存管理

| 函数 | 签名 | 说明 |
|------|------|------|
| `malloc` | `void *malloc(size_t size)` | 分配 size 字节未初始化内存 |
| `calloc` | `void *calloc(size_t nmemb, size_t size)` | 分配 nmemb*size 字节并清零 |
| `realloc` | `void *realloc(void *ptr, size_t size)` | 调整已分配内存大小（可能移动） |
| `free` | `void free(void *ptr)` | 释放由 malloc/calloc/realloc 分配的内存 |

> **关键概念**：`malloc` 不初始化内存，`calloc` 清零。`realloc(NULL, size)` 等价于 `malloc(size)`；`realloc(ptr, 0)` 行为由实现定义。分配失败返回 `NULL`；对 `NULL` 调用 `free` 是安全的。常见错误：忘记 `free`（内存泄漏）、两次 `free`（双重释放）、使用已释放内存（悬空指针）。

---

## 数值转换

| 函数 | 签名 | 说明 |
|------|------|------|
| `atoi` | `int atoi(const char *nptr)` | 字符串转 int，**无错误检测** |
| `atol` | `long atol(const char *nptr)` | 字符串转 long |
| `atof` | `double atof(const char *nptr)` | 字符串转 double |
| `strtol` | `long strtol(const char *nptr, char **endptr, int base)` | 字符串转 long，带进制和错误检测 |
| `strtoul` | `unsigned long strtoul(const char *nptr, char **endptr, int base)` | 字符串转 unsigned long |
| `strtod` | `double strtod(const char *nptr, char **endptr)` | 字符串转 double，带错误检测 |

> **关键概念**：`atoi` 系列不检测溢出和无效输入。`strtol`/`strtod` 通过 `endptr` 和 `errno` 提供完整的错误检测。`strtol` 的 `base` 支持 2-36 进制，传 0 自动检测（0x=16, 0=8）。

---

## 随机数

| 函数 | 签名 | 说明 |
|------|------|------|
| `rand` | `int rand(void)` | 返回 0 ~ RAND_MAX 的伪随机整数 |
| `srand` | `void srand(unsigned int seed)` | 设置随机数种子 |

> C 标准库随机数质量较差（通常为 LCG），不应用于密码学。典型用法：`srand((unsigned int)time(NULL))`。

---

## 排序与搜索

| 函数 | 签名 | 说明 |
|------|------|------|
| `qsort` | `void qsort(void *base, size_t nmemb, size_t size, int (*compar)(const void *, const void *))` | 排序（实现不一定用快排） |
| `bsearch` | `void *bsearch(const void *key, const void *base, size_t nmemb, size_t size, int (*compar)(const void *, const void *))` | 二分搜索，要求数组已排序 |

比较函数返回：<0 (a<b), 0 (a==b), >0 (a>b)。

---

## 进程控制

| 函数 | 签名 | 说明 |
|------|------|------|
| `exit` | `void exit(int status)` | 正常终止，执行 atexit 注册的函数、刷新并关闭流 |
| `abort` | `void abort(void)` | 异常终止，发送 SIGABRT |
| `atexit` | `int atexit(void (*func)(void))` | 注册 exit 时调用的函数（至少 32 个，LIFO 顺序） |
| `system` | `int system(const char *command)` | 执行操作系统命令 |
| `getenv` | `char *getenv(const char *name)` | 获取环境变量值 |

---

## 跨语言参考

- [[../../../2深化/08_标准库深度|C标准库深度]]
