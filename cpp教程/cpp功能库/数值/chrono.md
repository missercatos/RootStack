---
C++ 功能库 — chrono
---

## 概述

`chrono` 提供精确的时间度量和时钟抽象。核心三要素：**时钟(clock)**提供当前时间、**时间点(time_point)**标记某一时刻、**时间段(duration)**表示时间差。三个时钟各有用途：`system_clock` 对应墙上时间（可转日历），`steady_clock` 单调递增（适合计时），`high_resolution_clock` 提供最高精度。

## 核心组件

### 时钟

| 时钟 | 说明 |
|------|------|
| `system_clock` | 系统时钟，可受 NTP 调整，可转 `time_t` |
| `steady_clock` | 单调时钟，永不后退，适合测量时间间隔 |
| `high_resolution_clock` | 最高精度时钟（通常是 `steady_clock` 别名） |

### 时间段

| 类型 | 说明 |
|------|------|
| `hours` | `duration<INT64, ratio<3600>>` |
| `minutes` | `duration<INT64, ratio<60>>` |
| `seconds` | `duration<INT64, ratio<1>>` |
| `milliseconds` | `duration<INT64, milli>` |
| `microseconds` | `duration<INT64, micro>` |
| `nanoseconds` | `duration<INT64, nano>` |

### 时间点

| 组件 | 说明 |
|------|------|
| `time_point<Clock>` | 某个时钟上的时间点 |
| `now()` | 获取当前时间点 |
| `DURATION_CAST<T>(d)` | 时间段单位转换 |
| `TIME_POINT_CAST<T>(tp)` | 时间点精度转换 |

## 典型用法

### 精确计时

```
FUNCTION demo_timer:
    start = STEADY_CLOCK::NOW()

    DO_HEAVY_COMPUTATION()

    end = STEADY_CLOCK::NOW()
    elapsed = end - start

    ms = DURATION_CAST<MILLISECONDS>(elapsed).COUNT()
    PRINT "耗时:", ms, "ms"

    us = DURATION_CAST<MICROSECONDS>(elapsed).COUNT()
    PRINT "耗时:", us, "μs"
```

### C++14 时间字面量

```
FUNCTION demo_literals:
    USING NAMESPACE chrono_literals

    timeout = 500ms                            // 等价于 milliseconds(500)
    delay = 2s                                 // 等价于 seconds(2)
    long_wait = 5min                           // 等价于 minutes(5)

    SLEEP_FOR(100ms)                            // 休眠 100 毫秒
    SLEEP_FOR(1s)                               // 休眠 1 秒
```

### 时钟的区别

```
FUNCTION demo_clocks:
    // system_clock: 可以转成 C 风格 time_t
    now_sys = SYSTEM_CLOCK::NOW()
    tt = SYSTEM_CLOCK::TO_TIME_T(now_sys)      // 转为 time_t
    PRINT CTIME(&tt)                            // 人类可读时间字符串

    // steady_clock: 测量时间间隔（不受系统时间调整影响）
    t1 = STEADY_CLOCK::NOW()
    // ... 被测代码 ...
    t2 = STEADY_CLOCK::NOW()
    elapsed = t2 - t1                           // 永远 > 0
```

### 时间算术

```
FUNCTION demo_arithmetic:
    t1 = STEADY_CLOCK::NOW()
    t2 = t1 + 500ms                            // 500ms 后
    t3 = t2 + 2s                               // 2.5s 后

    d = t3 - t1                                // 2500ms
    PRINT DURATION_CAST<MILLISECONDS>(d).COUNT()  // 2500
```

---

- **随机数**: [[random|random]] — 用 `steady_clock::now()` 做种子
- **线程休眠**: [[../并发/thread|thread]] — `sleep_for` / `sleep_until`
- **C 对照**: `time()`/`clock()`/`gettimeofday()`（`<time.h>` `<sys/time.h>`）
- **返回目录**: 
