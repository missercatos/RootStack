---
C++ 功能库 — atomic
---

## 概述

`atomic<T>` 提供无锁的线程安全基本操作——`load`、`store`、`fetch_add`、`compare_exchange` 等，无需 mutex 即可安全地在多线程间共享数据。原子操作是构建 lock-free 数据结构的基础，也是性能最高的同步方式。

内存序(`memory_order`)控制操作的可见性保证，从最弱的 `relaxed` 到最强的 `seq_cst`（默认，最安全但最慢）。

## 核心组件

### 原子操作

| 操作 | 说明 |
|------|------|
| `load()` | 原子读取 |
| `store(val)` | 原子写入 |
| `exchange(val)` | 原子交换，返回旧值 |
| `fetch_add(n)` | 原子加 n，返回旧值 |
| `fetch_sub(n)` | 原子减 n，返回旧值 |
| `operator++` / `operator--` | 等价于 `fetch_add(1)` / `fetch_sub(1)` |
| `compare_exchange_strong(expected, desired)` | CAS：如果当前值==expected，则设成 desired 返回 true；否则 expected=当前值 返回 false |
| `compare_exchange_weak(expected, desired)` | 弱 CAS，可能伪失败，通常用于循环 |

### 内存序

| 内存序 | 说明 |
|--------|------|
| `seq_cst` | 顺序一致性（默认，最强保证，最慢） |
| `acquire` | 后续读写不会被重排到此操作之前（用于 load） |
| `release` | 之前的读写不会被重排到此操作之后（用于 store） |
| `acq_rel` | acquire + release（用于 read-modify-write） |
| `relaxed` | 仅保证原子性，不保证顺序（最快） |

## 典型用法

### 无锁计数器

```
FUNCTION demo_counter:
    counter = ATOMIC<INT>(0)

    increment = LAMBDA:
        FOR i = 1 TO 1000:
            counter++                           // 原子递增，等于 fetch_add(1)
        END FOR
    END LAMBDA

    threads = LIST<THREAD>()
    FOR i = 1 TO 10:
        threads.PUSH(THREAD(increment))
    END FOR
    FOR t IN threads: t.JOIN()
    PRINT counter                               // 始终为 10000
```

### CAS 循环 —— 无锁更新

```
FUNCTION demo_cas:
    value = ATOMIC<INT>(0)

    // CAS 循环：线程安全的"如果...则更新"
    expected = value.LOAD()
    LOOP:
        desired = expected + 1
        IF value.COMPARE_EXCHANGE_STRONG(expected, desired) THEN
            BREAK                               // 更新成功
        END IF
        // expected 已被更新为当前值，继续重试
    END LOOP
```

### 原子标志位

```
FUNCTION demo_flag:
    flag = ATOMIC<BOOL>(false)

    // 尝试设置标志，返回旧值
    IF NOT flag.EXCHANGE(true) THEN
        PRINT "我是第一个拿到锁的线程"
        DO_CRITICAL_WORK()
        flag.STORE(false)
    ELSE
        PRINT "其他线程已占用"
    END IF
```

### 内存序使用

```
FUNCTION demo_memory_order:
    // acquire-release 成对使用
    ready = ATOMIC<BOOL>(false)
    data = 0

    // 写线程
    data = 42                                   // 普通写入
    ready.STORE(true, RELEASE)                  // release 保证 data 写入可见

    // 读线程
    WHILE NOT ready.LOAD(ACQUIRE):              // acquire 保证读到最新 data
        THIS_THREAD::YIELD()
    END WHILE
    PRINT data                                  // 保证输出 42
```

---

- **互斥锁**: [[mutex|mutex]] — 复杂临界区用 mutex 更安全
- **线程**: [[thread|thread]] — 线程创建与管理
- **无锁数据结构**: 需配合 `memory_order` 细微控制
- **C 对照**: C11 `_Atomic` / C11 `atomic_*` 函数（`<stdatomic.h>`）
- **返回目录**: 
