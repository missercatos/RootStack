---
title: "C++ 功能库 — thread"
---

## 概述

`thread` 提供跨平台的线程抽象——创建操作系统线程、等待线程结束(`join`)或分离(`detach`)。C++20 引入的 `jthread` 进一步简化：析构时自动 `join`，并支持协作式中断(`stop_token`)。

C++11 将多线程标准化后，不再需要依赖 POSIX `pthread` 或 Windows `CreateThread`。

## 核心组件

| 组件 | 说明 |
|------|------|
| `thread` | 操作系统线程，构造函数接受可调用对象 |
| `jthread` (C++20) | 自动 join 的线程，析构时自动等待 |
| `this_thread::get_id()` | 获取当前线程 ID |
| `this_thread::sleep_for(d)` | 休眠指定时间段 |
| `this_thread::sleep_until(tp)` | 休眠到指定时间点 |
| `this_thread::yield()` | 让出 CPU 时间片 |
| `thread::hardware_concurrency()` | 查询 CPU 逻辑核心数 |
| `stop_token` / `stop_source` (C++20) | 协作式中断机制 |

## 线程生命周期

```
thread 创建  ──→  运行中  ──→  join()    主线程等待子线程结束
                    │
                    ├─→  detach()  子线程独立运行（危险：访问已销毁变量）
                    │
                    └─→  析构（未 join 也未 detach）→ terminate() 崩溃！
```

## 典型用法

### 基本线程

```
FUNCTION demo_thread:
    t = THREAD(LAMBDA:
        PRINT "线程", THIS_THREAD::GET_ID(), "工作中"
        THIS_THREAD::SLEEP_FOR(500ms)
    )

    PRINT "主线程继续执行"
    t.JOIN()                                    // 等待子线程结束
    PRINT "子线程已结束"
```

### jthread —— 自动 join + 可中断

```
FUNCTION demo_jthread:
    jt = JTHREAD(LAMBDA(token):
        WHILE NOT token.STOP_REQUESTED():
            PRINT "处理中..."
            THIS_THREAD::SLEEP_FOR(100ms)
        END WHILE
        PRINT "收到停止请求，退出"
    )

    THIS_THREAD::SLEEP_FOR(1s)
    jt.REQUEST_STOP()                           // 请求停止
    // jt 析构时自动 join，无需手动调用
```

### 创建多个工作线程

```
FUNCTION demo_multi_thread:
    NUM = THREAD::HARDWARE_CONCURRENCY()        // 查询核心数
    threads = VECTOR<THREAD>()

    FOR i = 0 TO NUM - 1:
        threads.PUSH(THREAD(LAMBDA(id = i):
            PRINT "Worker", id, "started"
            DO_WORK(id)
        ))
    END FOR

    FOR t IN threads:
        t.JOIN()                                // 等待所有线程完成
    END FOR
```

### 线程局部存储

```
thread_local counter = 0                        // 每个线程独立一份

FUNCTION demo_tls:
    t1 = THREAD(LAMBDA:
        counter = counter + 1                   // t1 的 counter = 1
    )
    t2 = THREAD(LAMBDA:
        counter = counter + 2                   // t2 的 counter = 2
    )
    t1.JOIN(); t2.JOIN()
    // 主线程的 counter 仍是 0，互不影响
```

---

- **互斥与同步**: [[mutex|mutex]] — 保护线程间共享数据
- **原子操作**: [[atomic|atomic]] — 无锁线程安全操作
- **异步任务**: [[future|future/async]] — 高级线程抽象
- **返回值共享**: 线程不返回值的替代方案是 `future` + `promise`
- **C 对照**: `pthread_create`/`pthread_join`（POSIX `<pthread.h>`）
- **返回目录**: 
