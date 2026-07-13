
# CRT -- C Runtime

> C 语言的"零开销运行时"——操作系统与 main() 之间的薄胶水层。

## 概念

C Runtime (CRT) 是 C 程序执行的最小运行时环境。与 JVM 或 CPython 不同，CRT 几乎没有"重量级"服务——无 GC、无 JIT、无对象模型。它的核心职责是：把操作系统交给 `_start`，最终把控制权交给用户的 `main`，并在程序退出时完成清理。

## 核心组件

| 组件 | 职责 | 关联系统调用 |
|------|------|-------------|
| 启动 (crt0) | `_start` → `__libc_start_main` → `main` | execve |
| 堆管理 | malloc/free 通过 brk/mmap 向内核申请内存 | brk, mmap |
| 栈帧管理 | 调用约定 (calling convention) 维护 rbp/rsp | — |
| 信号处理 | signal/sigaction 注册异步事件处理器 | sigaction, kill |
| 程序终止 | atexit 注册退出回调, exit → _exit | exit_group |
| 线程局部存储 | TLS: `__thread` 变量, pthread 密钥 | arch_prctl |
| I/O 缓冲 | stdio FILE* 的用户态缓冲 (setvbuf) | read, write |

## 启动流程

```
KERNEL                        CRT                             USER
  |                             |                                |
  |--execve("a.out")---------->|                                |
  |                             |                                |
  |                    _start (crt0.S)                           |
  |                       设定栈指针                               |
  |                       收集 argc, argv, envp                   |
  |                       调用 __libc_start_main                  |
  |                             |                                |
  |                 __libc_start_main                            |
  |                   注册 atexit 回调                             |
  |                   __libc_init (TLS, 环境变量)                  |
  |                   调用 main(argc, argv, envp)                 |
  |                             |------------------------------->|
  |                             |              int main(...)     |
  |                             |                  ...           |
  |                             |<-------------------------------|
  |                             |            return 0            |
  |                   收集返回值                                   |
  |                   调用 exit(retval)                           |
  |                   遍历 atexit 回调链                           |
  |                   刷新 stdio 缓冲区                            |
  |                   调用 _exit(retval)                          |
  |<--_exit(retval)--------------|                               |
```

## 堆管理

```c
// 简化版的 malloc 策略 (glibc ptmalloc)
void* malloc(size_t size) {
    if (size <= 64KB) {
        // 从线程本地 arena 分配
        // 使用 bins (fastbins, smallbins, largebins) 管理空闲块
        chunk = find_free_chunk_in_bins(size);
    }
    if (chunk == NULL) {
        // 通过 brk 扩展 data segment (小块)
        // 或通过 mmap 映射匿名页 (大块)
        chunk = request_from_kernel(size);
    }
    return chunk_to_mem(chunk);
}
```

## 信号处理

```c
// 信号处理的用户态模型
struct sigaction {
    void (*sa_handler)(int);     // 处理函数指针
    sigset_t sa_mask;             // 信号处理期间屏蔽的信号
    int sa_flags;                 // SA_RESTART, SA_NODEFER 等
};

// 信号递送时内核在用户栈上构造一个栈帧
// RIP → sa_handler, RSP → 用户栈 (带 sigframe)
// 处理完毕后通过 sigreturn 系统调用恢复现场
```

## 与操作系统的关系

CRT 的本质是系统调用的 C 语言封装。malloc 不是系统调用——它是 brk/mmap 之上的分配器。fopen 不是系统调用——它是 open 之上的缓冲层。CRT 让 C 程序"感觉"像是直接操作硬件，但实际上 glibc/musl 做了大量簿记。

---

## 交叉链接

- [[../../c语言教程/2深化/02_内存模型与布局|C 内存模型与布局]]
- [[../../c语言教程/2深化/03_动态内存管理|C 动态内存管理]]
- [[../../c语言教程/2深化/06_编译链接与ELF|编译链接与 ELF]]
- [[../../cpp教程/cpp深化教程/04_动态内存|C++ 动态内存]]
- [[../系统内核/01_C语言与操作系统|C 语言与操作系统]]
- [[../系统内核/02_进程与内存管理|进程与内存管理]]
- [[../系统内核/05_中断与系统调用|中断与系统调用]]
- [[CPython|CPython 运行时]] -- 对比: CRL vs 引用计数 GC
- [[JVM|JVM 运行时]] -- 对比: 零开销 vs 托管环境
