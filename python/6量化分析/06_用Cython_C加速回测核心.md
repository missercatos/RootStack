# 用 Cython/C 加速回测核心 (Accelerating with Cython/C)
---

## 📖 章节概述

Python 量化回测的致命弱点在于核心循环的纯 Python 速度。本章教你用 C 程序员最熟悉的方式——类型声明和编译优化——将回测性能提升 50-100 倍。先用 cProfile 定位瓶颈，再用 Cython 加类型声明重写热循环编译为 `.so`，最后直接用纯 C 编写并调用。三种方案的性能对比将让你深刻理解"Python 胶水 + C 引擎"这一量化系统的最佳架构。

> **核心理念**：Python 是胶水，C 是引擎。Dennis Ritchie 创造 C 语言的初衷就是写系统软件——高性能、接近硬件。而 Python 的初衷是"让编程更简单"。本章的核心思想是：用 Python 写分析流程和数据处理（你不需要关心速度的部分），用 C/Cython 写回测核心循环（每一纳秒都重要的部分）。两者通过 ctypes 或内置的 Cython 接口无缝连接。

---

### 📚 第一节：性能剖析 —— 找到瓶颈

#### 1.1 cProfile 快速定位

回测代码通常 80% 的时间花在 20% 的代码上。先用 profiler 找出是哪些行：

```bash
python -c "
import numpy as np

# 将回测核心提取为一个函数
def backtest_core(close, fast_p, slow_p):
    n = len(close)
    fast_sma = np.zeros(n)
    slow_sma = np.zeros(n)
    
    # 计算均线
    for i in range(fast_p - 1, n):
        fast_sma[i] = np.mean(close[i - fast_p + 1:i + 1])
    for i in range(slow_p - 1, n):
        slow_sma[i] = np.mean(close[i - slow_p + 1:i + 1])
    
    equity = np.zeros(n)
    cash = 100000.0
    position = 0.0
    
    for i in range(slow_p, n):
        if fast_sma[i] > slow_sma[i] and position == 0:
            position = cash / close[i]
            cash = 0.0
        elif fast_sma[i] < slow_sma[i] and position > 0:
            cash = position * close[i]
            position = 0.0
        equity[i] = cash + position * close[i]
    return equity

# 生成测试数据
np.random.seed(1)
close = 100 + np.cumsum(np.random.randn(50000) * 2)
close = np.maximum(close, 10)

import cProfile, pstats
profiler = cProfile.Profile()
profiler.enable()
equity = backtest_core(close, 10, 30)
profiler.disable()

# 输出前 10 耗时函数
pstats.Stats(profiler).sort_stats('cumulative').print_stats(10)
"
```

典型输出会显示：`np.mean()` 调用、Python for 循环、条件分支占据了绝大部分时间。这就是需要加速的热循环。

#### 1.2 量化瓶颈

```bash
python -c "
import numpy as np
import time

n = 200_000
close = 100 + np.cumsum(np.random.randn(n) * 2)

# 纯 Python 循环的性能基准
t0 = time.time()
result = 0
for i in range(n):
    result += close[i]
t1 = time.time()
print(f'Python loop sum: {t1 - t0:.4f}s')

# NumPy 向量化
t0 = time.time()
result = np.sum(close)
t1 = time.time()
print(f'NumPy sum: {t1 - t0:.6f}s')
print(f'Speedup: ~{0.01 / (t1 - t0 + 1e-10):.0f}x')
print()
print('In a complete backtest loop with conditionals and state:')
print('Python:   ~0.01-0.1 ms per bar')
print('C/Cython: ~0.0001-0.001 ms per bar')
print('→ 50-100x speedup achievable')
"
```

---

### 📚 第二节：Cython —— Python 的 C 方言

#### 2.1 Cython 的核心思想

Cython 让你在 Python 代码中添加 C 类型声明，然后编译成 C 扩展模块（`.so`）：

```cython
# backtest_core.pyx — Cython 代码
# cython: boundscheck=False, wraparound=False, cdivision=True

import numpy as np
cimport numpy as np
cimport cython

@cython.boundscheck(False)
@cython.wraparound(False)
def backtest_cython(double[:] close, int fast_p, int slow_p):
    cdef int n = close.shape[0]
    cdef int i
    cdef double window_sum_fast = 0.0
    cdef double window_sum_slow = 0.0
    cdef double cash = 100000.0
    cdef double position = 0.0
    cdef double price
    
    cdef double[:] fast_sma = np.zeros(n)
    cdef double[:] slow_sma = np.zeros(n)
    cdef double[:] equity = np.zeros(n)
    
    # 滑动窗口计算均线（O(n) 而非 O(n*window)）
    for i in range(n):
        window_sum_fast += close[i]
        if i >= fast_p:
            window_sum_fast -= close[i - fast_p]
        if i >= fast_p - 1:
            fast_sma[i] = window_sum_fast / fast_p
        
        window_sum_slow += close[i]
        if i >= slow_p:
            window_sum_slow -= close[i - slow_p]
        if i >= slow_p - 1:
            slow_sma[i] = window_sum_slow / slow_p
    
    # 回测主循环
    for i in range(slow_p, n):
        price = close[i]
        # 金叉
        if fast_sma[i] > slow_sma[i] and fast_sma[i-1] <= slow_sma[i-1]:
            if position == 0.0:
                position = cash / price
                cash = 0.0
        # 死叉
        elif fast_sma[i] < slow_sma[i] and fast_sma[i-1] >= slow_sma[i-1]:
            if position > 0.0:
                cash = position * price
                position = 0.0
        
        equity[i] = cash + position * price
    
    return np.asarray(equity)
```

C 类型映射表：

| Cython 类型 | C 类型 | NumPy dtype | 用途 |
|-------------|--------|-------------|------|
| `cdef int` | `int` | `np.int32` | 循环计数、索引 |
| `cdef long` | `long` | `np.int64` | 大索引 |
| `cdef double` | `double` | `np.float64` | 价格、收益率 |
| `cdef double[:]` | `double *` | `np.float64[:]` | 数组视图（memoryview） |
| `cdef bint` | `int` (bool) | — | 布尔标志 |

#### 2.2 编译 Cython 扩展

创建 `setup.py`：

```python
# setup.py
from setuptools import setup
from Cython.Build import cythonize
import numpy as np

setup(
    ext_modules=cythonize(
        "backtest_core.pyx",
        compiler_directives={
            'boundscheck': False,
            'wraparound': False,
            'cdivision': True,
        }
    ),
    include_dirs=[np.get_include()],
)
```

或者使用现代的 `pyproject.toml`：

```toml
[build-system]
requires = ["setuptools", "cython", "numpy"]
build-backend = "setuptools.build_meta"

[project]
name = "backtest_core"
version = "0.1.0"
```

编译：

```bash
python setup.py build_ext --inplace
# 或 pip install -e .
```

编译后生成 `backtest_core.so` 文件，可直接 `import backtest_core`。

#### 2.3 关键编译指令解释

| 指令 | 含义 | 性能影响 |
|------|------|---------|
| `@cython.boundscheck(False)` | 关闭数组越界检查 | **大幅提升** |
| `@cython.wraparound(False)` | 关闭负索引支持 | **大幅提升** |
| `cimport numpy` | 编译时导入 NumPy C API | 必须 |
| `cdef double[:] arr` | 类型化 memoryview | 零 Python 对象开销 |

> 关闭 boundscheck 的代价：数组越界不再抛 Python 异常，而是产生未定义行为（和 C 一样）。这符合 C 程序员的习惯，但失去了 Python 的安全网。这和你写 C 代码时用 `gcc -O3` 代替 `gcc -O0 -fsanitize=address` 一样——性能优先，安全自负。

#### 2.4 性能对比

```bash
python -c "
import numpy as np
import time

# 生成测试数据
n = 200_000
np.random.seed(1)
close = 100 + np.cumsum(np.random.randn(n) * 2)
close = np.maximum(close, 10)

# 这里展示概念
print('Expected performance (200,000 bars):')
print(f'  Pure Python:  ~2000 ms')
print(f'  Cython (no types): ~500 ms')
print(f'  Cython + types:    ~40 ms')
print(f'  Pure C (.so):      ~15 ms')
print(f'  Speedup:           50-130x')
"
```

| 实现方式 | 相对速度 | 代码复杂度 |
|---------|---------|-----------|
| 纯 Python + NumPy（无循环） | 1x（基准） | 最低 |
| 纯 Python for 循环 | 0.05x | 最低 |
| Cython 无类型声明 | 0.2x | 低 |
| Cython + 类型声明 | 50-80x | 中 |
| 纯 C + ctypes | 100-130x | 高 |
| C + Cython 包装 | 100-130x | 高 |

---

### 📚 第三节：纯 C 引擎 + ctypes 调用

#### 3.1 C 源码

```c
// backtest_engine.c
#include <stddef.h>

void backtest_sma_cross(
    const double *close, size_t n,
    int fast_window, int slow_window,
    double initial_capital,
    double *equity_out)
{
    // 滑动窗口计算均线
    double *fast_sma = (double *)calloc(n, sizeof(double));
    double *slow_sma = (double *)calloc(n, sizeof(double));
    
    double fast_sum = 0.0, slow_sum = 0.0;
    for (size_t i = 0; i < n; i++) {
        fast_sum += close[i];
        if (i >= (size_t)fast_window) fast_sum -= close[i - fast_window];
        if (i >= (size_t)(fast_window - 1)) fast_sma[i] = fast_sum / fast_window;
        
        slow_sum += close[i];
        if (i >= (size_t)slow_window) slow_sum -= close[i - slow_window];
        if (i >= (size_t)(slow_window - 1)) slow_sma[i] = slow_sum / slow_window;
    }
    
    // 回测主循环
    double cash = initial_capital;
    double position = 0.0;
    
    for (size_t i = slow_window; i < n; i++) {
        double price = close[i];
        int golden_cross = (fast_sma[i] > slow_sma[i] && 
                           fast_sma[i-1] <= slow_sma[i-1]);
        int dead_cross   = (fast_sma[i] < slow_sma[i] && 
                           fast_sma[i-1] >= slow_sma[i-1]);
        
        if (golden_cross && position == 0.0) {
            position = cash / price;
            cash = 0.0;
        } else if (dead_cross && position > 0.0) {
            cash = position * price;
            position = 0.0;
        }
        
        equity_out[i] = cash + position * price;
    }
    
    free(fast_sma);
    free(slow_sma);
}
```

#### 3.2 编译为共享库

```bash
gcc -shared -fPIC -O3 -march=native -ffast-math \
    -o backtest_engine.so backtest_engine.c
```

关键编译选项：

| 选项 | 含义 |
|------|------|
| `-shared` | 生成共享库 (.so) |
| `-fPIC` | 位置无关代码（共享库必需） |
| `-O3` | 最大优化级别 |
| `-march=native` | 使用当前 CPU 的全部指令集 (AVX2 等) |
| `-ffast-math` | 放宽 IEEE 浮点标准以换取速度 |

#### 3.3 Python 端调用

```bash
python -c "
import numpy as np
import ctypes

# 加载动态库
lib = ctypes.CDLL('./backtest_engine.so')

# 声明函数签名
lib.backtest_sma_cross.argtypes = [
    ctypes.POINTER(ctypes.c_double),  # close
    ctypes.c_size_t,                   # n
    ctypes.c_int,                      # fast_window
    ctypes.c_int,                      # slow_window
    ctypes.c_double,                   # initial_capital
    ctypes.POINTER(ctypes.c_double),  # equity_out
]
lib.backtest_sma_cross.restype = None

# 准备数据
n = 200_000
np.random.seed(1)
close = 100 + np.cumsum(np.random.randn(n) * 2)
close = np.maximum(close, 10)
close_arr = close.astype(np.float64)

# 预分配输出数组（零拷贝）
equity = np.zeros(n, dtype=np.float64)

# 调用 C 函数
import time
t0 = time.time()
lib.backtest_sma_cross(
    close_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
    n, 10, 30, 100000.0,
    equity.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
)
t1 = time.time()
print(f'C backtest on {n} bars: {t1 - t0:.4f}s')
print(f'Final equity: {equity[-1]:.2f}')
"
```

> ctypes 的详细教程参见 [[../2精通/05_ctypes：在Python中调用C库|Python ctypes]]。

---

### 📚 第四节：选择你的方案

#### 4.1 决策树

```
你的回测有多少行数据？
├── < 100K: 纯 Python 足够，别过度优化
├── 100K - 1M: Cython + 类型声明
├── 1M - 10M: Cython 或纯 C
└── > 10M: 纯 C + 多线程 + SIMD

你需要多频繁修改策略逻辑？
├── 每天调参: Cython（编译快，修改方便）
├── 稳定运行: 纯 C（极致性能）
└── 探索阶段: 先用 Python 验证，再移植到 Cython/C
```

#### 4.2 混合方案：Python 调度 + C 执行

最佳实践是将策略逻辑写在 Python 里方便修改，将纯计算部分抽取为 C/Cython 函数：

```python
# Python 端（灵活）
class Strategy:
    def __init__(self, data):
        self.data = data
        self.engine = ctypes.CDLL('./backtest_engine.so')
    
    def generate_signals(self):
        # 复杂的信号逻辑可以用 Python 写
        # ...
        pass
    
    def run_backtest(self):
        # 纯数值运算调用 C 引擎
        self.engine.compute_equity(
            self.data.close, len(self.data),
            self.equity_curve
        )
```

#### 4.3 进一步优化方向

| 技术 | 适用场景 | 复杂度 |
|------|---------|--------|
| SIMD 内联 | 均线、求和、乘积等批量操作 | 高 |
| 多线程 (OpenMP) | 参数网格搜索 | 中 |
| GPU (CUDA) | 蒙特卡洛模拟、期权定价 | 极高 |
| Numba JIT | 不想写 C 又想快速 | 最低 |

> Cython 和 pybind11 的深入讲解见 [[../2精通/07_pybind11与Cython：给C_C++库披上Python外衣|Cython 与 pybind11]]。

---

### 📝 小节练习

> [!question] 选择题 1
> Cython 中的 `cdef double[:] arr` 声明了什么？
> - [ ] A. 一个 Python list
> - [ ] B. 一个类型化的 memoryview（直接映射到 C 数组）
> - [ ] C. 一个 Python 字典
> - [ ] D. 一个 NumPy 的 Python 对象
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `cdef double[:] arr` 是 Cython 的 typed memoryview，底层直接映射为 C 的 `double*` 指针访问，完全绕过 Python 对象系统。这是 Cython 高性能的关键。

> [!question] 判断题 1
> 关闭 `boundscheck` 后数组越界会产生 Python 异常。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 关闭 boundscheck 后，数组越界访问不会抛 Python IndexError，而是产生未定义行为（和 C 一样）。可能静默读取/写入相邻内存。这类似于 C 中访问 `arr[-1]`——编译器不会阻止你。

---

## 📋 章节测试

### 一、判断题

> [!question] 判断题 1
> cProfile 可以精确测量 Python 代码中每个函数的调用次数和执行时间。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: cProfile 是 Python 内置的确定性性能分析器，记录每个函数的调用次数、总时间、累积时间。使用 `python -m cProfile -s cumulative script.py` 可以直接运行并查看报告。

> [!question] 判断题 2
> Cython 文件（.pyx）可以直接被 Python `import`，不需要编译。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: .pyx 文件必须先被编译（由 Cython 转为 .c 文件，再由 GCC/Clang 编译为 .so/.pyd 文件）才能被 Python import。`cythonize()` 函数自动化了这个过程。

> [!question] 判断题 3
> Cython 的类型声明 `cdef int i` 和 Python 的 `i: int` 类型注解有完全相同的性能效果。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: Python 的类型注解（`i: int`）只是元数据，运行时没有任何优化效果。Cython 的 `cdef int i` 是真正的 C 类型声明，变量将存储为 C 的 `int` 类型（直接放在 CPU 寄存器或栈上），带来数十倍的性能提升。

> [!question] 判断题 4
> 用 `ctypes` 调用 C 函数时，NumPy 数组的数据会被自动拷贝一份传给 C 代码。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 使用 `arr.ctypes.data_as(ctypes.POINTER(c_double))` 传递的是底层数据的原始指针，不发生数据拷贝。这就是之前 [[../../6量化分析/01_NumPy数组：与C数组的血缘|NumPy 内存模型]] 中学到的零拷贝共享。

> [!question] 判断题 5
> 纯 C 编写的回测引擎总是比 Cython 版本的快。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 当 Cython 代码中所有关键变量都做了类型声明并关闭了 boundscheck，生成的 C 代码质量和手写 C 非常接近。Cython 的优势在于开发效率（Python 语法 + 类型声明），纯 C 的优势在于更精细的控制。

> [!question] 判断题 6
> `gcc -O3 -march=native` 中的 `-march=native` 会让编译产物只在当前 CPU 上运行。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `-march=native` 让编译器使用当前 CPU 的所有指令集（如 AVX2、SSE4.2），生成的二进制可能无法在较旧的 CPU 上运行。对于量化系统部署在不同服务器上，使用 `-march=x86-64-v2` 等保守选项更安全。

---

### 二、选择题

> [!question] 选择题 1
> cProfile 的输出中，`cumtime` 列表示什么？
> - [ ] A. 该函数本身的执行时间（不包括子函数）
> - [ ] B. 该函数及其所有子函数的总执行时间
> - [ ] C. 该函数的编译时间
> - [ ] D. 该函数被调用的次数
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `cumtime` = 累积时间 = 该函数自身时间 + 它调用的所有子函数的时间。`tottime` = 该函数自身的时间（排除子函数）。在分析时要看 cumtime 才能找到真正的"高成本调用链"。

> [!question] 选择题 2
> 以下哪个 Cython 声明用于 NumPy 数组的编译时类型检查？
> - [ ] A. `import numpy`
> - [ ] B. `cimport numpy`
> - [ ] C. `np.ndarray`
> - [ ] D. `ctypedef numpy`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `cimport numpy` 在编译时导入 NumPy 的 C API 定义，这是使用 typed memoryview（如 `double[:]`）的前提。普通的 `import numpy` 是运行时导入，无法用于类型声明。

> [!question] 选择题 3
> 将 Python 回测热循环提取为 Cython 文件后，编译为 `.so` 的正确命令流程是？
> - [ ] A. `gcc` 直接编译 .pyx
> - [ ] B. 用 Cython 先转 .c，再 `gcc` 编译 + 链接
> - [ ] C. `python setup.py build_ext --inplace`
> - [ ] D. 直接 `import` .pyx 文件
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: `python setup.py build_ext --inplace` 自动完成 Cython → C 转换、GCC 编译、链接 Python 库的全流程。`.pyx` 文件不能直接被 import 或 gcc 编译。

> [!question] 选择题 4
> 量化回测中，以下哪个操作最不可能成为性能瓶颈？
> - [ ] A. 滚动窗口计算指标（如 SMA）
> - [ ] B. 逐 bar 的订单逻辑判断
> - [ ] C. 读写配置文件
> - [ ] D. 盈亏和净值的累积计算
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: 回测的性能瓶颈总是在"每 bar 都要执行"的计算上——SMA、信号判断、盈亏累积。这些会执行数十万次直至数百万次。配置文件只在回测初始化时读一次，不是瓶颈。

> [!question] 选择题 5
> `double[:]` 和 `np.ndarray[np.float64_t, ndim=1]` 在 Cython 中的关键区别是？
> - [ ] A. 没有区别
> - [ ] B. memoryview 更快，因为直接通过指针访问
> - [ ] C. ndarray 声明更快
> - [ ] D. memoryview 更安全
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: Typed memoryview（`double[:]`）通过直接的 C 指针访问数据，生成的 C 代码几乎和手写循环一样高效。`np.ndarray` 声明虽然也做类型检查，但通过 NumPy API 访问，有额外的函数调用开销。

> [!question] 选择题 6
> Numba JIT（即时编译）相比 Cython 的优势是什么？
> - [ ] A. Numba 更快
> - [ ] B. Numba 不需要单独的编译步骤，加装饰器即可
> - [ ] C. Numba 支持更多 NumPy 函数
> - [ ] D. Numba 生成的代码质量更高
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: Numba 的最大优势是开发体验——`@jit(nopython=True)` 装饰器即可自动编译，无需 `.pyx` 文件、`setup.py` 和编译步骤。但在极致性能上，精心优化的 Cython 通常更快。

---

### 🛠️ 动手练习题

> [!example] 练习题 1：cProfile 分析实战
> **难度**: ⭐⭐
>
> 将第 4 章中的自建回测代码独立出来，用 cProfile 进行分析。输出前 10 个耗时最多的函数调用。阅读报告并统计：(1) 纯循环的时间占比；(2) NumPy 函数调用的时间占比；(3) 其他开销。用 `pstats.Stats` 生成调用图。

> [!example] 练习题 2：Cython 加速均线计算
> **难度**: ⭐⭐⭐
>
> 创建一个 `sma_engine.pyx` 文件，用 Cython 实现三个函数：
> 1. `fast_sma(double[:] close, int window)` — 滑动窗口 SMA
> 2. `cross_signals(double[:] fast, double[:] slow)` — 金叉/死叉信号生成
> 3. `compute_equity(double[:] close, int[:] signals, double capital)` — 最终净值计算
>
> 编译为 .so 并在 Python 中测试。用 `%timeit` 比较纯 Python 版本和 Cython 版本在 50 万行数据上的表现。

> [!example] 练习题 3：纯 C 回测引擎 + ctypes
> **难度**: ⭐⭐⭐⭐
>
> 用纯 C 实现一个完整的回测引擎，支持：
> - 自定义信号函数（通过函数指针或 switch 语句）
> - 交易成本（手续费 + 滑点）
> - 每天只交易一次（使用次日开盘价执行）
>
> 编译为 .so，用 ctypes 在 Python 中调用。输出每日的持仓、权益、现金序列。与纯 NumPy 版本对比结果和性能。

> [!example] 练习题 4：完整方案对比
> **难度**: ⭐⭐⭐
>
> 对同一个 SMA 交叉策略，用四种方式实现回测：
> 1. 纯 NumPy 向量化（无 Python 循环）
> 2. 纯 Python 循环
> 3. Cython + 类型声明
> 4. 纯 C + ctypes
>
> 在同样的 100 万条数据上，记录每种方案的运行时间和内存占用。制作对比表格和柱状图，分析每种方案的适用场景和前提条件。
