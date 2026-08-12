
# &lt;stdarg.h&gt; — 可变参数

> **头文件**: `#include <stdarg.h>`
> 提供实现可变参数函数（如 `printf`、`scanf`）的宏和类型。

---

## 核心类型与宏

| 类型/宏 | 说明 |
|---------|------|
| `va_list` | 保存可变参数遍历状态的不透明类型 |
| `va_start(ap, last_named)` | 初始化 va_list，使其指向第一个可变参数 |
| `va_arg(ap, type)` | 获取当前参数并将 va_list 前进到下一个 |
| `va_end(ap)` | 清理 va_list（必须调用） |
| `va_copy(dest, src)` | 复制 va_list 以多次遍历 (C99) |

---

## 函数签名要求

可变参数函数必须**至少有一个固定命名参数**：

```c
/* 合法 */
void myprintf(const char *fmt, ...);

/* 非法 */
void foo(...);
```

---

## 基本用法

```c
int sum(int count, ...) {
 va_list args;
 va_start(args, count);

 int total = 0;
 for (int i = 0; i < count; i++)
 total += va_arg(args, int);

 va_end(args);
 return total;
}
/* sum(4, 10, 20, 30, 40) -> 100 */
```

---

## 类型提升陷阱

在可变参数中，某些类型会被自动提升：

| 传入类型 | 实际类型 |
|---------|---------|
| char, short | int |
| float | double |

因此**不能用** `va_arg(ap, char)` 或 `va_arg(ap, float)`。

---

## 各宏详解

### va_start

初始化 `ap` 使其指向最后一个命名参数之后的第一个可变参数。`last_named_param` 必须是对应的固定参数名。

### va_arg

返回当前可变参数的值并推进 `ap`。`type` 必须与实际参数类型匹配——C 不会对可变参数做类型检查。

### va_end

每个 `va_start`/`va_copy` 必须与一个 `va_end` 配对。即使实现中可能为空操作，也必须调用以保持可移植性。

### va_copy (C99)

复制 `va_list`，允许多次遍历同一参数列表。使用后需 `va_end`。

---

## 与 printf 的关系

`vprintf`、`vfprintf`、`vsnprintf` 接受 `va_list`，用于包装自定义日志函数：

```c
void log_info(const char *fmt, ...) {
 va_list args;
 va_start(args, fmt);
 vfprintf(stderr, fmt, args);
 va_end(args);
}
```

---

## 类型安全局限

| 问题 | 说明 |
|------|------|
| 无编译时类型检查 | `va_arg` 指定类型与传入不一致导致未定义行为 |
| 参数数量不可获取 | 需通过 format 字符串、哨兵值或显式 count 告知 |
| 裸内存读取 | `va_arg` 只是按类型大小读栈/寄存器，完全依赖程序员 |

---

## 跨语言参考

- [[../../../2深化/08_标准库深度|C标准库深度]]
