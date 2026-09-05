---
title: "C++ 功能库 — thread"
---

## 概述

`thread` 提供跨平台的线程抽象——创建操作系统线程、等待线程结束(`join`)或分离(`detach`)。C++20 引入的 `jthread` 进一步简化：析构时自动 `join`，并支持协作式中断(`stop_token`)。

C++11 将多线程标准化后，不再需要依赖 POSIX `pthread` 或 Windows `CreateThread`。每个 `std::thread` 对象对应一个操作系统线程，构造时即启动，析构前必须 `join` 或 `detach`，否则程序调用 `terminate()` 终止。

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
thread 创建 ──→ 运行中 ──→ join() 主线程等待子线程结束
 │
 ├─→ detach() 子线程独立运行（危险：访问已销毁变量）
 │
 └─→ 析构（未 join 也未 detach）→ terminate() 崩溃！
```

## 线程创建模式

### 1. 基本线程

```cpp
// 最简单的线程创建
std::thread t([]{
    std::cout << "Hello from thread\n";
});
t.join();

// 带参数的线程
std::thread t([](int id, std::string name){
    std::cout << "Thread " << id << ": " << name << "\n";
}, 1, "worker");
t.join();
```

### 2. 成员函数作为线程入口

```cpp
class Worker {
public:
    void run(int id) {
        std::cout << "Worker " << id << " running\n";
    }
};

Worker w;
std::thread t(&Worker::run, &w, 1);  // 成员函数 + this + 参数
t.join();
```

### 3. 函数对象与仿函数

```cpp
struct Task {
    void operator()(int n) {
        for (int i = 0; i < n; ++i) {
            // do work
        }
    }
};

std::thread t(Task{}, 100);  // 注意大括号，避免最令人恼火的解析
t.join();
```

## join vs detach

```cpp
// join: 主线程阻塞等待子线程完成
// 适用：需要等待结果、确保资源清理
{
    std::thread t([]{
        std::this_thread::sleep_for(std::chrono::seconds(1));
    });
    t.join();  // 主线程等待 1 秒
}  // 安全：t 已 join

// detach: 子线程与主线程分离，独立运行
// 适用：后台任务、守护线程
{
    std::thread t([]{
        // 永久运行的后台任务
        while (true) {
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }
    });
    t.detach();  // 危险：如果主线程结束，此线程可能访问已销毁变量
}

// 最佳实践：优先使用 jthread
{
    std::jthread jt([]{
        // 自动 join，无需手动管理
    });
}  // 析构时自动 join
```

### join 与 detach 的选择指南

| 场景 | 推荐 | 原因 |
|------|------|------|
| 需要等待线程完成 | `join()` | 保证结果可用 |
| 后台守护任务 | `detach()` | 不阻塞主线程 |
| 函数返回前必须清理 | `jthread` | RAII 自动 join |
| 生产者-消费者 | `join()` + 条件变量 | 同步退出 |

## jthread (C++20)

```cpp
// jthread 的三大优势：
// 1. 析构时自动 join
// 2. 内置 stop_token 支持协作式中断
// 3. 避免忘记 join 导致 terminate

void background_task(std::stop_token stoken) {
    while (!stoken.stop_requested()) {
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        // 执行周期性任务
    }
    std::cout << "Stopping gracefully\n";
}

// 使用
{
    std::jthread jt(background_task);
    std::this_thread::sleep_for(std::chrono::seconds(2));
    jt.request_stop();  // 请求停止
}  // 析构时自动 join

// stop_source 与 stop_token 的关系
std::stop_source ssource;
std::jthread jt([ssource](std::stop_token stoken) {
    // stoken 与 ssource 关联
    while (!stoken.stop_requested()) {
        // work
    }
});

// 另一个线程可以从外部请求停止
ssource.request_stop();
```

### 多线程共享 stop_source

```cpp
std::stop_source master_source;

// 创建多个工作线程，共享同一个 stop_source
std::jthread worker1([ss = master_source](std::stop_token st) {
    while (!st.stop_requested()) { /* work */ }
});
std::jthread worker2([ss = master_source](std::stop_token st) {
    while (!st.stop_requested()) { /* work */ }
});

// 一次请求停止所有线程
master_source.request_stop();
// worker1 和 worker2 都会收到停止请求
```

## 线程池概念

```cpp
// 简单线程池实现思路
class ThreadPool {
    std::vector<std::jthread> workers;
    std::queue<std::function<void()>> tasks;
    std::mutex queue_mutex;
    std::condition_variable condition;
    bool stop = false;
public:
    ThreadPool(size_t threads) {
        for (size_t i = 0; i < threads; ++i) {
            workers.emplace_back([this](std::stop_token stoken) {
                while (!stoken.stop_requested()) {
                    std::function<void()> task;
                    {
                        std::unique_lock lock(queue_mutex);
                        condition.wait(lock, [this, &stoken] {
                            return stop || !tasks.empty() || stoken.stop_requested();
                        });
                        if (stop && tasks.empty()) return;
                        task = std::move(tasks.front());
                        tasks.pop();
                    }
                    task();
                }
            });
        }
    }
    template<class F>
    void enqueue(F&& f) {
        {
            std::lock_guard lock(queue_mutex);
            tasks.emplace(std::forward<F>(f));
        }
        condition.notify_one();
    }
    // 析构时 jthread 自动 join 所有 worker
};
```

## 线程局部存储

```cpp
thread_local int counter = 0;  // 每个线程独立一份

// 典型用途
// 1. 线程本地缓存
thread_local std::unordered_map<std::string, std::string> cache;

// 2. 避免锁竞争的累加器
thread_local long long local_sum = 0;

// 3. 线程本地随机数引擎
thread_local std::mt19937 rng(std::random_device{}());
```

## 线程安全注意事项

```cpp
// 危险：多线程写同一变量
int counter = 0;
std::thread t1([&]{ for (int i = 0; i < 1000; ++i) counter++; });
std::thread t2([&]{ for (int i = 0; i < 1000; ++i) counter++; });
// counter 的值不确定（数据竞争 → 未定义行为）

// 解决方案：使用 atomic
std::atomic<int> safe_counter{0};
std::thread t1([&]{ for (int i = 0; i < 1000; ++i) safe_counter++; });
std::thread t2([&]{ for (int i = 0; i < 1000; ++i) safe_counter++; });
// safe_counter == 2000
```

## 常见陷阱与最佳实践

1. **忘记 join/detach**：`std::thread` 析构时如果既没 join 也没 detach，直接调用 `terminate()`
2. **悬垂引用**：detach 后访问局部变量是未定义行为
3. **线程安全**：共享数据必须用 mutex 或 atomic 保护
4. **优先 jthread**：C++20 环境下几乎总应该用 `jthread` 替代 `thread`
5. **避免过度创建线程**：线程创建有开销（通常 10-100μs），频繁创建销毁应使用线程池
6. **`hardware_concurrency()` 可能返回 0**：不要假设线程数

## 力扣练习

| 题号 | 题目 | 链接 | 知识点 |
|------|------|------|--------|
| 1114 | 按序打印 | https://leetcode.cn/problems/print-in-order/ | 线程同步基础 |
| 1115 | 交替打印 ABC | https://leetcode.cn/problems/print-foobar-alternately/ | 条件变量同步 |
| 1116 | 打印零与奇偶数 | https://leetcode.cn/problems/print-zero-even-odd/ | 多线程协调 |
| 1117 | HP35 计算器 | https://leetcode.cn/problems/building-h2o/ | 线程同步经典问题 |
| 1242 | 多线程网页爬虫 | https://leetcode.cn/problems/web-crawler-multithreaded/ | 多线程实际应用 |
| 1195 | Fizz Buzz 多线程 | https://leetcode.cn/problems/fizz-buzz-multithreaded/ | 多条件同步 |
| 1188 | 设计阻塞队列 | https://leetcode.cn/problems/design-bounded-blocking-queue/ | 生产者-消费者 |
| 1114 | 按序打印（增强版） | https://leetcode.cn/problems/consecutive-characters/ | atomic 操作 |
| 3116 | 消灭所有怪物 | https://leetcode.cn/problems/minimum-number-of-coins-for-all-fruits/ | 并发思路分析 |
| 1099 | 小于 K 的两数之和 | https://leetcode.cn/problems/two-sum-less-than-k/ | 排序 + 双指针 |
| 2274 | 最大连续 1 的个数 IV | https://leetcode.cn/problems/maximum-consecutive-ones-iii/ | 窗口思想 |
| 169 | 多数元素 | https://leetcode.cn/problems/majority-element/ | 并发投票算法 |

---

- **互斥与同步**: [[mutex|mutex]] — 保护线程间共享数据
- **原子操作**: [[atomic|atomic]] — 无锁线程安全操作
- **异步任务**: [[future|future/async]] — 高级线程抽象
- **返回值共享**: 线程不返回值的替代方案是 `future` + `promise`
- **C 对照**: `pthread_create`/`pthread_join`（POSIX `<pthread.h>`）
- **返回目录**:
