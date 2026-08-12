
# &lt;setjmp.h&gt; — 非局部跳转

> **头文件**: `#include <setjmp.h>`
> 提供 C 语言的非局部跳转机制——类似于其他语言中的异常处理，但更底层。允许从深层嵌套函数直接跳回早期执行点。

---

## 核心类型与函数

| 类型/函数 | 签名 | 说明 |
|-----------|------|------|
| `jmp_buf` | `jmp_buf env;` | 数组类型，保存调用者的执行环境（寄存器、栈指针、程序计数器） |
| `setjmp` | `int setjmp(jmp_buf env)` | 保存当前环境到 env；首次返回 0，longjmp 跳回时返回非零 |
| `longjmp` | `void longjmp(jmp_buf env, int val)` | 恢复 env 中保存的环境，使 setjmp 返回 val（必须非零） |

---

## 基本用法

```c
#include <setjmp.h>
jmp_buf env;

void inner(void) {
 printf("error detected, jumping back\n");
 longjmp(env, 1);
}

int main(void) {
 if (setjmp(env) == 0) {
 printf("first call\n");
 inner();
 } else {
 printf("jumped back from longjmp\n");
 }
 return 0;
}
```

---

## 重要约束与陷阱

### 1. volatile 变量

在 `setjmp` 和 `longjmp` 之间修改的自动变量（非 volatile）在 `longjmp` 后的值未定义。必须用 `volatile` 修饰。

### 2. 函数返回限制

包含 `setjmp` 调用的函数返回后，其 `jmp_buf` 变为无效。

### 3. 资源泄漏

`longjmp` 不展开栈，不调用 `free`、`fclose` 或释放互斥锁。跳转前必须手动清理资源：

```c
/* 危险：FILE* 可能泄漏 */
FILE *fp = fopen("data.txt", "r");
if (error) longjmp(env, 1); // fp 未关闭！
fclose(fp);
```

---

## 典型应用

| 场景 | 说明 |
|------|------|
| 深层嵌套中的错误恢复 | 从多层调用链中直接跳出 |
| 协程/纤程实现 | 保存和恢复执行上下文 |
| 信号处理中的恢复 | 配合 volatile sig_atomic_t |
| 解释器/虚拟机的异常 | 简单的 try-catch 机制 |

---

## setjmp/longjmp vs C++ 异常

| 特性 | setjmp/longjmp | C++ try/catch |
|------|---------------|---------------|
| 栈展开 | 否 | 是 |
| 析构函数调用 | 否 | 是（RAII） |
| 类型安全 | 否（val 为 int） | 是 |

---

## 跨语言参考

- [[../../../2深化/08_标准库深度|C标准库深度]]
