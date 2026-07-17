
# &lt;ctype.h&gt; — 字符分类与转换

> **头文件**: `#include <ctype.h>`
> 提供字符类型判断和大小写转换。所有函数接收 `int` 参数（非 `char`）。

---

## 参数约定

参数类型为 `int`，值必须是 EOF 或可表示为 `unsigned char` 的值。直接传入 `char` 可能导致未定义行为（当 `char` 为有符号且值为负时）。

```c
char c = 'A';
if (isupper((unsigned char)c)) { ... }
```

若输入来自 `fgetc`/`getc` 返回值（已为 unsigned char 或 EOF），可直接传入。

---

## 分类函数

| 函数 | 判断条件 |
|------|----------|
| `isalnum(c)` | 字母 (A-Z, a-z) 或数字 (0-9) |
| `isalpha(c)` | 字母 |
| `isdigit(c)` | 十进制数字 (0-9) |
| `isxdigit(c)` | 十六进制数字 (0-9, A-F, a-f) |
| `islower(c)` | 小写字母 (a-z) |
| `isupper(c)` | 大写字母 (A-Z) |

---

## 空白与控制字符

| 函数 | 判断条件 |
|------|----------|
| `isspace(c)` | 空白：空格 ` `, `\f`, `\n`, `\r`, `\t`, `\v` |
| `isblank(c)` | 空格 ` ` 和水平制表 `\t` (C99) |
| `iscntrl(c)` | 控制字符 (0x00-0x1F, 0x7F) |
| `isprint(c)` | 可打印字符（含空格） |
| `isgraph(c)` | 可打印字符（不含空格） |
| `ispunct(c)` | 标点符号 |

---

## 大小写转换

| 函数 | 说明 |
|------|------|
| `toupper(c)` | 若为小写字母则转为大写，否则返回原值 |
| `tolower(c)` | 若为大写字母则转为小写，否则返回原值 |

> 结果依赖 locale。在 C locale 下仅处理 ASCII 字母。

---

## 跨语言参考

- [[../../../2深化/08_标准库深度|C标准库深度]]
