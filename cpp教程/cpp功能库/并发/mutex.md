---
title: "C++ 功能库 — mutex"
---

## 概述

互斥锁(mutex)是线程间同步的基本原语——保证同一时刻只有一个线程访问临界区。C++ 提供了从简单的 `mutex` 到读写锁 `shared_mutex`，配合 RAII 锁定包装器（`lock_guard`、`unique_lock`、`shared_lock`）自动管理锁的生命周期。条件变量(`condition_variable`)实现等待-通知模式。

C++20 新增 `semaphore`、`latch`、`barrier` 等高级同步原语。

## 核心组件

### 锁类型

| 组件 | 说明 |
|------|------|
| `mutex` | 基本互斥锁，`lock()`/`unlock()` |
| `recursive_mutex` | 同一线程可重复加锁 |
| `timed_mutex` | 支持超时的 mutex |
| `shared_mutex` (C++17) | 读写锁，多读单写 |
| `lock_guard` | RAII 自动加锁/解锁，不可手动解锁 |
| `unique_lock` | 灵活 RAII，可延迟加锁、提前解锁、转移所有权 |
| `shared_lock` (C++17) | `shared_mutex` 的 RAII 读锁 |
| `scoped_lock` (C++17) | 同时锁定多个 mutex（避免死锁） |

### 条件变量与信号

| 组件 | 说明 |
|------|------|
| `condition_variable` | 等待-通知，`wait()`/`notify_one()`/`notify_all()` |
| `semaphore` (C++20) | 计数信号量，`acquire()`/`release()` |
| `latch` (C++20) | 一次性屏障（倒计时到零释放所有线程） |
| `barrier` (C++20) | 可重用屏障（阶段同步） |

## 典型用法

### lock_guard —— 最简互斥

```
FUNCTION demo_lock_guard:
 mtx = MUTEX()
 counter = 0

 increment = LAMBDA:
 guard = LOCK_GUARD(mtx) // 构造加锁
 counter = counter + 1 // 临界区
 // guard 析构时自动解锁
 END LAMBDA

 threads = LIST<THREAD>()
 FOR i = 1 TO 10:
 threads.PUSH(THREAD(increment))
 END FOR
 FOR t IN threads: t.JOIN()
 PRINT counter // 始终为 10
```

### unique_lock + 条件变量

```
FUNCTION demo_cv:
 mtx = MUTEX()
 cv = CONDITION_VARIABLE()
 data = 0
 ready = false

 // 等待线程
 waiter = THREAD(LAMBDA:
 lock = UNIQUE_LOCK(mtx)
 cv.WAIT(lock, LAMBDA: RETURN ready) // 等待 ready
 PRINT "收到:", data
 )

 // 通知线程
 mtx.LOCK()
 data = 42
 ready = true
 mtx.UNLOCK()
 cv.NOTIFY_ONE() // 唤醒等待线程

 waiter.JOIN()
```

### shared_mutex —— 读写锁

```
FUNCTION demo_rwlock:
 rw = SHARED_MUTEX()
 cache = MAP<INT, STRING>()

 reader = LAMBDA:
 lock = SHARED_LOCK(rw) // 共享锁（读）
 val = cache[KEY] // 多个读者可同时持有
 END LAMBDA

 writer = LAMBDA:
 lock = UNIQUE_LOCK(rw) // 独占锁（写）
 cache[KEY] = new_value // 写者独占
 END LAMBDA
```

### latch —— 一次性同步点

```
FUNCTION demo_latch:
 done_latch = LATCH(5) // 计数 5

 FOR i = 0 TO 4:
 ASYNC(LAMBDA(id = i):
 DO_WORK(id)
 done_latch.COUNT_DOWN() // 减 1
 )
 END FOR

 done_latch.WAIT() // 计数到 0 后继续
 PRINT "全部完成"
```

---

- **线程**: [[thread|thread]] — 线程创建与管理
- **原子操作**: [[atomic|atomic]] — 无锁替代 mutex
- **异步**: [[future|future/async]] — 高级同步模式
- **C 对照**: `pthread_mutex_lock`/`pthread_cond_wait`（POSIX `<pthread.h>`）
- **返回目录**: 
