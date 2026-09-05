---
title: "C++ 功能库 — future"
---

## 概述

`future`/`promise` 提供异步任务的结果传递机制——`async` 一行代码启动异步任务并返回 `future`，`promise` 手动向 `future` 设置值。`future` 的 `get()` 阻塞等待结果，`shared_future` 允许多个线程重复获取。这比手动管理线程+返回值更安全简洁。

`async` 的策略可选：`launch::async` 强制新建线程，`launch::deferred` 延迟到 `get()` 时才惰性求值。

## 核心组件

| 组件 | 说明 |
|------|------|
| `async(f)` | 异步执行函数，返回 `future<T>` |
| `future<T>` | 获取异步结果，`get()` 阻塞等待（只能调用一次） |
| `shared_future<T>` | 可多次 `get()` 的 future，多线程可共享 |
| `promise<T>` | 手动设置值/异常给关联的 future |
| `packaged_task<T(Args...)>` | 打包可调用对象，通过 `get_future()` 获取 future |
| `future_status` | 枚举：`ready` / `timeout` / `deferred` |
| `wait_for(d)` | 限时等待，返回 `future_status` |
| `wait_until(tp)` | 等到指定时间点 |

## 典型用法

### async —— 一行异步

```cpp
FUNCTION demo_async:
 fut = ASYNC(LAMBDA:
 THIS_THREAD::SLEEP_FOR(2s) // 模拟耗时
 RETURN "结果"
 )

 PRINT "主线程不阻塞，继续执行"
 result = fut.GET() // 阻塞直到完成
 PRINT result // "结果"
```cpp

### launch 策略

```cpp
FUNCTION demo_launch:
 // 强制新建线程执行
 fut1 = ASYNC(LAUNCH::ASYNC, LAMBDA: RETURN 42)

 // 延迟求值：get() 时才在当前线程执行（不创建线程）
 fut2 = ASYNC(LAUNCH::DEFERRED, LAMBDA: RETURN heavy_compute())

 // 默认策略（由实现决定）
 fut3 = ASYNC(LAMBDA: RETURN 100)
```cpp

### promise —— 手动传值

```cpp
FUNCTION demo_promise:
 prom = PROMISE<INT>()
 fut = prom.GET_FUTURE()

 worker = THREAD(LAMBDA(p = MOVE(prom)):
 result = COMPUTE()
 p.SET_VALUE(result) // 向 future 传值
 // 或者 p.SET_EXCEPTION(ex) // 传异常
 )

 TRY:
 val = fut.GET() // 阻塞等待
 PRINT val
 CATCH ...:
 PRINT "异步任务出错"
 END TRY
 worker.JOIN()
```cpp

### shared_future —— 多线程共享结果

```cpp
FUNCTION demo_shared_future:
 prom = PROMISE<STRING>()
 shared_fut = prom.GET_FUTURE().SHARE()

 FOR i = 1 TO 5:
 THREAD(LAMBDA(sf = shared_fut):
 PRINT "线程", i, "得到:", sf.GET() // 每个线程都可以 get
 ).DETACH()
 END FOR

 THIS_THREAD::SLEEP_FOR(100ms)
 prom.SET_VALUE("广播消息")
 THIS_THREAD::SLEEP_FOR(1s) // 等 detach 线程完成
```cpp

### 限时等待

```cpp
FUNCTION demo_timeout:
 fut = ASYNC(LAMBDA:
 THIS_THREAD::SLEEP_FOR(5s)
 RETURN 42
 )

 status = fut.WAIT_FOR(500ms) // 只等 500ms
 IF status == READY THEN
 PRINT "完成:", fut.GET()
 ELSE
 PRINT "超时，继续等待..."
 END IF
```cpp

### packaged_task

```cpp
FUNCTION demo_packaged_task:
 task = PACKAGED_TASK<INT(INT, INT)>(LAMBDA(a, b):
 RETURN a + b
 )
 fut = task.GET_FUTURE()

 // 可以在任意线程中执行
 task(3, 5) // 执行任务
 PRINT fut.GET() // 8
```cpp

---

- **线程**: [[thread|thread]] — 底层线程管理
- **互斥**: [[mutex|mutex]] — 保护共享数据
- **原子操作**: [[atomic|atomic]] — `future` 内部依赖原子同步
- **返回目录**: 
