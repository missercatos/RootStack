
# &lt;time.h&gt; — 时间与日期

> **头文件**: `#include <time.h>`
> 提供时间获取、时间格式转换、时间差计算等函数。

---

## 核心类型

| 类型 | 说明 |
|------|------|
| `time_t` | 算术类型，通常为 epoch 以来秒数（1970-01-01 00:00:00 UTC） |
| `clock_t` | 算术类型，进程使用的 CPU 时间（以 CLOCKS_PER_SEC 为单位） |
| `struct tm` | 分解时间结构体 |

### struct tm 字段

| 字段 | 范围 | 说明 |
|------|------|------|
| `tm_sec` | 0--60（闰秒可为 60） | 秒 |
| `tm_min` | 0--59 | 分钟 |
| `tm_hour` | 0--23 | 小时 |
| `tm_mday` | 1--31 | 月内日 |
| `tm_mon` | **0--11**（0=一月） | 月 |
| `tm_year` | 1900 年以来的年数 | 年 |
| `tm_wday` | 0--6（0=周日） | 周内日 |
| `tm_yday` | 0--365 | 年内日 |
| `tm_isdst` | 正=夏令时, 0=否, 负=未知 | 夏令时标志 |

---

## 时间获取

| 函数 | 说明 |
|------|------|
| `time(time_t *t)` | 获取当前日历时间（秒精度）；若 t 非 NULL 同时存入 *t |
| `clock()` | 返回进程 CPU 时间，除以 CLOCKS_PER_SEC 得秒数 |
| `timespec_get(ts, base)` | 获取当前时间，纳秒精度 (C11) |

---

## 时间转换

| 函数 | 说明 |
|------|------|
| `localtime(const time_t *timer)` | time_t -> 本地时间的 struct tm（返回静态缓冲区） |
| `gmtime(const time_t *timer)` | time_t -> UTC 时间的 struct tm |
| `mktime(struct tm *tm)` | struct tm（本地时间）-> time_t；自动规范化字段 |

> `localtime`/`gmtime` 返回**静态缓冲区指针**——不可重入、线程不安全。POSIX 提供 `localtime_r`/`gmtime_r`。

---

## 时间格式化

| 函数 | 说明 |
|------|------|
| `strftime(char *s, size_t max, const char *fmt, const struct tm *tm)` | 将 struct tm 格式化为字符串 |
| `ctime(const time_t *timer)` | time_t -> 可读字符串（末尾含换行） |
| `asctime(const struct tm *tm)` | struct tm -> 固定格式字符串 |

常用 strftime 格式符：`%Y`(年), `%m`(月), `%d`(日), `%H`(时), `%M`(分), `%S`(秒)。

---

## 时间差

| 函数 | 说明 |
|------|------|
| `difftime(time_t time1, time_t time0)` | 返回 time1-time0 差值（double 秒） |

> 不要直接对 `time_t` 做减法——C 标准不保证 `time_t` 的单位是秒。`difftime` 是唯一可移植的方式。

---

## 跨语言参考

- [[../../../2深化/08_标准库深度|C标准库深度]]
