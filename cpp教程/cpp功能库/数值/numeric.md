---
C++ 功能库 — numeric
---

## 概述

C++ 数值模块汇集了除随机数和时间之外的数学工具：`complex` 复数运算、`numeric_limits` 类型边界查询、`ratio` 编译期有理数、`valarray` 面向数值计算的数组，以及 C++20 引入的 `numbers` 数学常量。

相比 C 的 `<math.h>` `<float.h>` `<complex.h>`，C++ 版本是**类型安全**的模板库，`numeric_limits` 替代了 `INT_MAX` 等宏，`numbers` 替代了 `#define PI`。

## 核心组件

| 组件 | 头文件 | 说明 |
|------|--------|------|
| `complex<T>` | `<complex>` | 复数类型，支持四则运算和 `abs`/`arg`/`conj` |
| `numeric_limits<T>` | `<limits>` | 查询类型数值范围、精度、特性 |
| `ratio<N, D>` | `<ratio>` | 编译期有理数，零运行时开销 |
| `valarray<T>` | `<valarray>` | 数值数组，支持逐元素运算 |
| `numbers` | `<numbers>` (C++20) | 数学常量：`pi`, `e`, `sqrt2`, `phi` 等 |
| `gcd` / `lcm` | `<numeric>` (C++17) | 最大公约数 / 最小公倍数 |
| `midpoint` | `<numeric>` (C++20) | 无溢出中点计算 |
| `lerp` | `<numeric>` (C++20) | 线性插值 |

## 典型用法

### complex —— 复数运算

```
FUNCTION demo_complex:
    a = COMPLEX<DOUBLE>(3.0, 4.0)              // 3 + 4i
    b = COMPLEX<DOUBLE>(1.0, -2.0)             // 1 - 2i

    c = a + b                                   // (4 + 2i)
    d = a * b                                   // (3+4i)(1-2i) = 11 - 2i

    mag = ABS(a)                                // |a| = 5
    phase = ARG(a)                              // atan2(4,3) 弧度
    conj = CONJ(a)                              // 共轭: 3 - 4i
    PRINT a.REAL(), a.IMAG()                    // 3  4
```

### numeric_limits —— 类型边界

```
FUNCTION demo_limits:
    PRINT NUMERIC_LIMITS<INT>::MAX()            // 2147483647
    PRINT NUMERIC_LIMITS<INT>::MIN()            // -2147483648
    PRINT NUMERIC_LIMITS<DOUBLE>::EPSILON()     // 最小精度差
    PRINT NUMERIC_LIMITS<DOUBLE>::INFINITY()
    PRINT NUMERIC_LIMITS<DOUBLE>::QUIET_NAN()

    IF NUMERIC_LIMITS<USHORT>::IS_SIGNED THEN
        PRINT "有符号"
    END IF

    PRINT "小数位数:", NUMERIC_LIMITS<DOUBLE>::DIGITS10  // 15
```

### ratio —— 编译期有理数

```
FUNCTION demo_ratio:
    USING milli = RATIO<1, 1000>                // 1/1000
    USING kilo  = RATIO<1000, 1>                // 1000/1

    // ratio 用于 chrono 的时长类型定义
    // seconds  = duration<INT64, ratio<1>>
    // milli    = duration<INT64, ratio<1,1000>>

    // 编译期计算，零运行时开销
    USING ratio_sum = RATIO_ADD<kilo, RATIO<500,1>>  // 1500/1
```

### C++20 numbers 常量

```
FUNCTION demo_numbers:
    PRINT PI                                     // 3.141592653589793...
    PRINT E                                      // 2.718281828459045...
    PRINT SQRT2                                  // 1.414213562373095...
    PRINT PHI                                    // 1.618033988749895...

    area = PI * r * r                           // 不再需要 #define PI
```

### valarray —— 数值数组

```
FUNCTION demo_valarray:
    a = VALARRAY<DOUBLE>({1.0, 2.0, 3.0})
    b = VALARRAY<DOUBLE>({4.0, 5.0, 6.0})

    c = a + b                                   // [5, 7, 9]（逐元素）
    d = a * b                                   // [4, 10, 18]
    e = a * 2.0                                 // [2, 4, 6]（标量广播）
    f = a.APPLY(LAMBDA(x): RETURN x*x)          // [1, 4, 9]
```

---

- **随机数**: [[./random|random]] — `random_device`、`mt19937`
- **时间**: [[./chrono|chrono]] — `duration` 与 `ratio` 的关系
- **C 对照**: `INT_MAX`/`DBL_MIN`（`<climits>` `<cfloat>`）、`sin`/`cos`（`<cmath>`）
- **返回目录**: [[../索引|C++ 功能库索引]]
