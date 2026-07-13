
# &lt;stdio.h&gt; — 标准输入输出

> **头文件**: `#include <stdio.h>`
> C 语言最核心的 I/O 库，提供缓冲流抽象，封装文件读写、格式化输出和字符串格式化。

---

## 核心类型与预定义流

| 类型 | 说明 |
|------|------|
| `FILE` | 不透明结构体，代表一个打开的流 |
| `stdin` | 标准输入 |
| `stdout` | 标准输出 |
| `stderr` | 标准错误输出（无缓冲） |

---

## 文件操作

| 函数 | 签名 | 说明 |
|------|------|------|
| `fopen` | `FILE *fopen(const char *path, const char *mode)` | 打开文件；mode 如 `"r"`, `"w"`, `"a"`, `"rb"`, `"wb"` |
| `fclose` | `int fclose(FILE *stream)` | 关闭文件流，刷新缓冲区 |
| `freopen` | `FILE *freopen(const char *path, const char *mode, FILE *stream)` | 重定向流到新文件 |
| `remove` | `int remove(const char *path)` | 删除文件 |
| `rename` | `int rename(const char *old, const char *new)` | 重命名文件 |

---

## 二进制读写

| 函数 | 签名 | 说明 |
|------|------|------|
| `fread` | `size_t fread(void *ptr, size_t size, size_t nmemb, FILE *stream)` | 从流读取 nmemb 个元素 |
| `fwrite` | `size_t fwrite(const void *ptr, size_t size, size_t nmemb, FILE *stream)` | 向流写入 nmemb 个元素 |
| `fgetc` | `int fgetc(FILE *stream)` | 读取一个字符（返回 int 以容纳 EOF） |
| `fputc` | `int fputc(int c, FILE *stream)` | 写入一个字符 |

---

## 格式化 I/O

| 函数 | 签名 | 说明 |
|------|------|------|
| `printf` | `int printf(const char *format, ...)` | 格式化输出到 stdout |
| `fprintf` | `int fprintf(FILE *stream, const char *format, ...)` | 格式化输出到指定流 |
| `sprintf` | `int sprintf(char *str, const char *format, ...)` | 格式化输出到字符串（不安全，无边界检查） |
| `snprintf` | `int snprintf(char *str, size_t size, const char *format, ...)` | 安全版本，最多写入 size-1 字符，自动追加 `\0` |
| `scanf` | `int scanf(const char *format, ...)` | 从 stdin 格式化读取 |
| `fscanf` | `int fscanf(FILE *stream, const char *format, ...)` | 从指定流格式化读取 |
| `sscanf` | `int sscanf(const char *str, const char *format, ...)` | 从字符串格式化读取 |

> **关键概念**：永远使用 `snprintf` 而非 `sprintf`。`snprintf` 返回"本应写入的字符数"而非"实际写入数"，可用于预判缓冲区大小。

---

## 行 I/O

| 函数 | 签名 | 说明 |
|------|------|------|
| `fgets` | `char *fgets(char *s, int size, FILE *stream)` | 从流读取一行（含换行），最多 size-1 字符 |
| `fputs` | `int fputs(const char *s, FILE *stream)` | 写入字符串（不自动加换行） |
| `puts` | `int puts(const char *s)` | 输出字符串到 stdout，自动追加换行 |
| `ungetc` | `int ungetc(int c, FILE *stream)` | 将字符推回流缓冲区 |

---

## 文件定位

| 函数 | 签名 | 说明 |
|------|------|------|
| `fseek` | `int fseek(FILE *stream, long offset, int whence)` | 移动文件位置指针（SEEK_SET/SEEK_CUR/SEEK_END） |
| `ftell` | `long ftell(FILE *stream)` | 获取当前文件位置 |
| `rewind` | `void rewind(FILE *stream)` | 回到文件开头 |

---

## 缓冲控制

| 函数 | 签名 | 说明 |
|------|------|------|
| `fflush` | `int fflush(FILE *stream)` | 强制刷新输出缓冲区；NULL 则刷新所有流 |
| `setbuf` | `void setbuf(FILE *stream, char *buf)` | 设置缓冲区（全缓冲或无缓冲） |
| `setvbuf` | `int setvbuf(FILE *stream, char *buf, int mode, size_t size)` | 精细控制缓冲：_IOFBF/_IOLBF/_IONBF |

---

## 状态与错误

| 函数 | 签名 | 说明 |
|------|------|------|
| `feof` | `int feof(FILE *stream)` | 判断是否到达文件末尾 |
| `ferror` | `int ferror(FILE *stream)` | 判断是否发生读写错误 |
| `clearerr` | `void clearerr(FILE *stream)` | 清除 EOF 和错误标志 |

> **关键概念**：`feof` 在读取到 EOF 后才返回真，不要在循环中用它判断"是否还有数据"——应检查读取函数的返回值。

---

## 跨语言参考

- [[../../2深化/08_标准库深度|C标准库深度]]
