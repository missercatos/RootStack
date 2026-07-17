
# &lt;assert.h&gt; — 诊断断言

> **头文件**: `#include <assert.h>`
> 仅定义一个宏 `assert`，用于在开发阶段捕获逻辑错误。

---

## assert 宏

```c
void assert(scalar expression);
```

若表达式为 0（假），`assert` 会：
1. 向 **stderr** 输出诊断信息（包含表达式原文、源文件名、行号、函数名）
2. 调用 `abort()` 终止程序

典型输出：`Assertion failed: (ptr != NULL), function main, file test.c, line 42.`

---

## NDEBUG 宏

定义 `NDEBUG` 后，所有 `assert` 变为空操作——表达式**不会被求值**。

| 方式 | 效果 |
|------|------|
| `#define NDEBUG`（在 `#include <assert.h>` 之前） | 源代码级禁用 |
| `gcc -DNDEBUG` | 编译时禁用（最常用） |

> **陷阱**：`assert` 禁用后表达式不会被求值，因此**绝不能**在 `assert` 中放入有副作用的表达式：

```c
/* 错误！Release 模式下不会执行 */
assert(send_data(fd) == 0);

/* 正确：副作用分离 */
int ret = send_data(fd);
assert(ret == 0);
```

---

## 使用原则

| 适合使用 assert | 不适合使用 assert |
|----------------|------------------|
| 检查函数前置条件（参数合法性） | 处理用户输入错误 |
| 检查内部不变量（链表完整性） | 处理运行时错误（文件不存在） |
| 验证"不可能发生"的分支 | I/O 或网络操作 |

> 断言是**程序员的 bug 检测工具**，不应替代正常的错误处理。

---

## assert vs abort

| 特性 | `assert(expr)` | `abort()` |
|------|---------------|-----------|
| 触发条件 | expr 为假 | 无条件 |
| 输出诊断 | 是（表达式/文件/行号） | 否 |
| 受 NDEBUG 影响 | 是 | 否 |

---

## 跨语言参考

- [[../../../2深化/08_标准库深度|C标准库深度]]
