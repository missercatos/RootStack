
# &lt;signal.h&gt; — 信号处理

> **头文件**: `#include <signal.h>`
> 提供进程间异步通知机制——信号（signal）的处理。C 标准仅规定最小子集，POSIX 大幅扩展。

---

## 核心类型与函数

| 类型/函数 | 签名 | 说明 |
|-----------|------|------|
| `sig_atomic_t` | `volatile sig_atomic_t flag;` | 可被信号处理器原子访问的整数类型 |
| `signal` | `void (*signal(int sig, void (*func)(int)))(int)` | 注册信号 sig 的处理函数 func |
| `raise` | `int raise(int sig)` | 向当前进程发送信号 sig |

---

## 标准信号常量

| 常量 | 典型含义 | 触发方式 |
|------|----------|---------|
| `SIGINT` | 中断 | Ctrl+C |
| `SIGILL` | 非法指令 | 执行无效机器码 |
| `SIGFPE` | 浮点异常 | 除零、溢出 |
| `SIGSEGV` | 段错误 | 非法内存访问（NULL 解引用） |
| `SIGTERM` | 终止请求 | `kill` 命令 |
| `SIGABRT` | 异常终止 | `abort()` 函数 |

---

## signal 函数

```c
void (*signal(int sig, void (*func)(int)))(int);
```

`func` 可设置为：

| 值 | 含义 |
|----|------|
| `SIG_DFL` | 恢复默认处理 |
| `SIG_IGN` | 忽略信号（SIGKILL 和 SIGSTOP 不可忽略） |
| 用户函数指针 | 收到信号时调用 |

> `signal` 行为因 UNIX 版本而异。**推荐使用 POSIX 的 `sigaction`** 以获得可移植行为。

---

## 信号处理器中的安全操作

信号处理器运行在**中断上下文**中，只能调用异步信号安全的函数。

C 标准保证可安全调用：

| 操作 | 示例 |
|------|------|
| 写入 `volatile sig_atomic_t` 变量 | `flag = 1;` |
| 调用 `abort()` | 终止程序 |
| 调用 `_Exit()` | 立即退出 |
| 调用 `signal()` 重新注册 | 仅限相同信号 |

**严禁**在信号处理器中调用 `printf`, `malloc`, `free`, `fopen`, `exit` 等（可能因持有锁导致死锁）。

> 最安全的模式：信号处理器中设置 `volatile sig_atomic_t` 标志，主循环轮询。

---

## 跨语言参考

- [[../../../2深化/08_标准库深度|C标准库深度]]
