# 性能对比：纯 Python vs Cython vs C (Performance Comparison)
---

## 📖 章节概述

"Python 速度够快吗？"——这是每个从 C 语言转向 Python 的开发者首先面临的问题。本章不靠抽象说教，而是用一个具体的基准任务（Mandelbrot 集计算）横向对比五种实现方案：纯 Python 循环、NumPy 向量化、Cython 类型化加速、C 编译为共享库（.so）通过 ctypes 调用、以及纯 C 独立可执行文件。我们将测量执行时间、剖析性能瓶颈（cProfile）、监控内存占用（memory_profiler），并在此基础上讨论"何时 Python 速度是瓶颈，何时开发速度更重要"的工程决策。

> **核心理念**：性能不是二元选择——它有层次。从 Python → NumPy → Cython → C 是一条连续的光谱，每一层都需要额外的开发代价以换取运行速度。聪明的工程师知道什么时候该"停留"在某一层。

---

### 📚 第一节：基准测试任务与环境设置

#### 1.1 Mandelbrot 集

Mandelbrot 集是理想的基准测试——纯计算密集型、无 I/O 瓶颈、易于并行化：

**算法**：对复平面上每个点 `c`，迭代 `z_{n+1} = z_n² + c`。若 `|z| > 2` 或在 maxiter 次内未逃逸，记录逃逸次数。

```c
// C 伪代码 — 核心热循环
for (int j = 0; j < height; j++) {
    for (int i = 0; i < width; i++) {
        double complex c = xmin + (xmax-xmin)*i/width
                         + (ymin + (ymax-ymin)*j/height) * I;
        double complex z = 0;
        int iter = 0;
        while (cabs(z) < 2.0 && iter < maxiter) {
            z = z*z + c;
            iter++;
        }
        output[j*width + i] = iter;
    }
}
```

#### 1.2 统一计时框架

```python
import time
import numpy as np

def benchmark(func, *args, name="", **kwargs):
    """统一的计时包装器"""
    # 预热（避免缓存和 JIT 冷启动干扰）
    _ = func(*args, **kwargs)
    # 正式计时
    t0 = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed = time.perf_counter() - t0
    print(f"{name:20s}: {elapsed:.4f} s")
    return result, elapsed

# 参数配置
WIDTH, HEIGHT = 1000, 1000
MAXITER = 200
XMIN, XMAX = -2.0, 1.0
YMIN, YMAX = -1.5, 1.5
```

> 💡 `time.perf_counter()` 提供系统上可用的最高精度时钟，不受系统时间调整影响，是 Python 基准测试的首选。

### 📝 小节练习

> [!question] 选择题 1
> 为什么 `benchmark` 函数在正式计时前先调用一次 `func`？
> - [ ] A. 检查函数是否会产生错误
> - [ ] B. 预热 CPU 缓存 / JIT 编译，避免冷启动干扰
> - [ ] C. 验证函数输出是否正确
> - [ ] D. 增加总运行时间以获得更准确的结果
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 首次调用可能触发 Python 字节码加载、CPU 缓存填充、JIT（Cython/Numba）编译等"冷启动"开销。预热后计时更准确反映稳态性能。

> [!question] 判断题 1
> `time.time()` 和 `time.perf_counter()` 在基准测试中可以互换使用。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `time.time()` 可能受系统时钟调整（NTP 同步）影响且精度较低。`time.perf_counter()` 是单调时钟，专为短时高精度测量设计。

---

### 📚 第二节：纯 Python 与 NumPy 向量化

#### 2.1 纯 Python 实现（基准线 — 最慢）

```python
import numpy as np

def mandelbrot_pure_python(width, height, xmin, xmax, ymin, ymax, maxiter):
    """纯 Python 三重嵌套循环 — 性能底线"""
    result = np.zeros((height, width), dtype=np.int32)
    dx = (xmax - xmin) / width
    dy = (ymax - ymin) / height

    for j in range(height):
        cy = ymin + j * dy
        for i in range(width):
            cx = xmin + i * dx
            zr = zi = 0.0
            for n in range(maxiter):
                zr2, zi2 = zr*zr, zi*zi
                if zr2 + zi2 > 4.0:
                    break
                zi = 2.0 * zr * zi + cy
                zr = zr2 - zi2 + cx
            else:
                n = maxiter
            result[j, i] = n
    return result

result_py, t_py = benchmark(
    mandelbrot_pure_python,
    WIDTH, HEIGHT, XMIN, XMAX, YMIN, YMAX, MAXITER,
    name="纯 Python"
)
# 典型输出: 15–30 s（极慢）
```

#### 2.2 NumPy 向量化版本（中度加速）

```python
import numpy as np

def mandelbrot_numpy(width, height, xmin, xmax, ymin, ymax, maxiter):
    """NumPy 向量化 — 同时处理所有像素"""
    cx = np.linspace(xmin, xmax, width)
    cy = np.linspace(ymin, ymax, height)
    c = cx[:, None] + 1j * cy[None, :]   # (width, height) 复数网格

    z = np.zeros_like(c, dtype=np.complex128)
    output = np.full(c.shape, maxiter, dtype=np.int32)
    mask = np.ones(c.shape, dtype=bool)

    for n in range(maxiter):
        if not mask.any():
            break
        z[mask] = z[mask]**2 + c[mask]
        diverged = np.abs(z) > 2.0
        newly_diverged = diverged & mask
        output[newly_diverged] = n
        mask[newly_diverged] = False

    return output.T   # 转置以匹配 (height, width) 布局

result_np, t_np = benchmark(
    mandelbrot_numpy,
    WIDTH, HEIGHT, XMIN, XMAX, YMIN, YMAX, MAXITER,
    name="NumPy 向量化"
)
# 典型输出: 0.5–1.5 s（快 20–30 倍）
```

> 💡 NumPy 向量化版本仍有一个**外层 Python 循环**（`for n in range(maxiter)`），但内层操作（`z[mask]**2`, `np.abs(z) > 2`）全部在 C 层面执行。这是典型的"半向量化"——外层迭代无法消除时，每次迭代都是高效的 C 操作。

### 📝 小节练习

> [!question] 选择题 1
> NumPy 版 Mandelbrot 仍有一个 Python 层 `for` 循环，这个循环的作用是？
> - [ ] A. 遍历每个像素
> - [ ] B. 迭代 Mandelbrot 的迭代次数
> - [ ] C. 生成随机数
> - [ ] D. 无用循环
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 外层循环 `for n in range(maxiter)` 在 Python 层面迭代，但每次迭代内处理**所有尚未逃逸的像素**（通过 NumPy 掩码）。这比逐个像素循环快了数十倍。

> [!question] 判断题 1
> 将纯 Python 的 Mandelbrot 用 `numba.jit` 包装，速度可以接近 C 级别。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: Numba 可以将纯 Python 的数值循环 JIT 编译为 LLVM 机器码，通常达到接近 C 的速度，且无需像 Cython 那样额外写 .pyx 文件。

---

### 📚 第三节：Cython 类型化加速

#### 3.1 Cython 是什么

Cython 是 Python 的超集——在 .pyx 文件中添加 C 类型声明，编译为 Python C 扩展模块（.so/.pyd）。它结合了 Python 的语法便利和 C 的执行速度。

```cython
# mandelbrot_cython.pyx
# cython: boundscheck=False, wraparound=False, cdivision=True
import numpy as np
cimport numpy as np
from libc.math cimport fabs

def mandelbrot_cython(int width, int height,
                      double xmin, double xmax,
                      double ymin, double ymax,
                      int maxiter):
    cdef np.ndarray[np.int32_t, ndim=2] result = np.zeros(
        (height, width), dtype=np.int32)
    cdef double cx, cy, zr, zi, zr2, zi2
    cdef double dx = (xmax - xmin) / width
    cdef double dy = (ymax - ymin) / height
    cdef int i, j, n

    for j in range(height):
        cy = ymin + j * dy
        for i in range(width):
            cx = xmin + i * dx
            zr = zi = 0.0
            for n in range(maxiter):
                zr2 = zr * zr
                zi2 = zi * zi
                if zr2 + zi2 > 4.0:
                    break
                zi = 2.0 * zr * zi + cy
                zr = zr2 - zi2 + cx
            result[j, i] = n
    return result
```

编译脚本 `setup.py`：

```python
from setuptools import setup
from Cython.Build import cythonize
import numpy

setup(
    ext_modules=cythonize(
        "mandelbrot_cython.pyx",
        compiler_directives={"boundscheck": False, "wraparound": False}
    ),
    include_dirs=[numpy.get_include()],
)
```

```bash
python setup.py build_ext --inplace
```

```python
# 调用编译后的 Cython 模块
import mandelbrot_cython

result_cy, t_cy = benchmark(
    mandelbrot_cython.mandelbrot_cython,
    WIDTH, HEIGHT, XMIN, XMAX, YMIN, YMAX, MAXITER,
    name="Cython（类型化）"
)
# 典型输出: 0.15–0.30 s（接近 C 速度）
```

> ⚠️ Cython 的关键优化指令：
> - `@boundscheck(False)` — 关闭数组索引越界检查
> - `@wraparound(False)` — 关闭负索引处理
> - `cdivision(True)` — 使用 C 除法规避 ZeroDivisionError
> 这些是"把安全气囊关掉跑得更快"，仅在调试完成后使用。

### 📝 小节练习

> [!question] 选择题 1
> Cython 的 `cdef` 关键字的作用是？
> - [ ] A. 定义一个 Python 类
> - [ ] B. 声明一个 C 类型的变量（在 C 速度层面操作）
> - [ ] C. 导入 C 标准库
> - [ ] D. 创建一个新的 Python 模块
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `cdef` 声明带有 C 类型的变量（如 `cdef int i`），这些变量在 C 层面以原生速度操作，绕过了 Python 对象的动态分派开销。

> [!question] 判断题 1
> Cython 编译生成的 .so 文件可以直接被纯 Python 代码 `import` 使用。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: Cython 编译输出的是标准的 Python C 扩展模块（.so 或 .pyd），可以被 Python 直接 `import`，与用 C 编写的扩展模块无异。

---

### 📚 第四节：C 扩展与性能汇总

#### 4.1 C 共享库 + ctypes 调用

```c
// mandelbrot_c_lib.c
// 编译: gcc -O3 -shared -fPIC -o mandelbrot.so mandelbrot_c_lib.c -lm
#include <stdlib.h>
#include <math.h>

void mandelbrot_c(int width, int height,
                  double xmin, double xmax,
                  double ymin, double ymax,
                  int maxiter, int *output) {
    double cx, cy, zr, zi, zr2, zi2;
    double dx = (xmax - xmin) / width;
    double dy = (ymax - ymin) / height;

    for (int j = 0; j < height; j++) {
        cy = ymin + j * dy;
        for (int i = 0; i < width; i++) {
            cx = xmin + i * dx;
            zr = zi = 0.0;
            int n;
            for (n = 0; n < maxiter; n++) {
                zr2 = zr * zr;
                zi2 = zi * zi;
                if (zr2 + zi2 > 4.0) break;
                zi = 2.0 * zr * zi + cy;
                zr = zr2 - zi2 + cx;
            }
            output[j * width + i] = n;
        }
    }
}
```

```python
import numpy as np
import ctypes

# 加载共享库
_lib = ctypes.CDLL('./mandelbrot.so')
_lib.mandelbrot_c.argtypes = [
    ctypes.c_int, ctypes.c_int,
    ctypes.c_double, ctypes.c_double,
    ctypes.c_double, ctypes.c_double,
    ctypes.c_int,
    np.ctypeslib.ndpointer(dtype=np.int32, ndim=2, flags='C')
]

def mandelbrot_c_lib(width, height, xmin, xmax, ymin, ymax, maxiter):
    result = np.zeros((height, width), dtype=np.int32)
    _lib.mandelbrot_c(width, height, xmin, xmax, ymin, ymax, maxiter, result)
    return result

result_c, t_c = benchmark(
    mandelbrot_c_lib,
    WIDTH, HEIGHT, XMIN, XMAX, YMIN, YMAX, MAXITER,
    name="C (ctypes)"
)
# 典型输出: 0.10–0.20 s（最快）
```

#### 4.2 纯 C 独立运行对比

```bash
# 编译纯 C 独立程序
gcc -O3 -o mandelbrot_standalone mandelbrot_standalone.c -lm
time ./mandelbrot_standalone
# 典型输出: 0.08–0.15 s
```

```c
// mandelbrot_standalone.c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

int main() {
    const int W = 1000, H = 1000, MAXITER = 200;
    const double xmin = -2.0, xmax = 1.0, ymin = -1.5, ymax = 1.5;
    int *output = malloc(W * H * sizeof(int));

    clock_t start = clock();
    double dx = (xmax - xmin) / W, dy = (ymax - ymin) / H;
    for (int j = 0; j < H; j++) {
        double cy = ymin + j * dy;
        for (int i = 0; i < W; i++) {
            double cx = xmin + i * dx, zr = 0, zi = 0;
            int n;
            for (n = 0; n < MAXITER; n++) {
                double zr2 = zr*zr, zi2 = zi*zi;
                if (zr2 + zi2 > 4.0) break;
                zi = 2.0*zr*zi + cy;
                zr = zr2 - zi2 + cx;
            }
            output[j*W + i] = n;
        }
    }
    clock_t end = clock();
    printf("C standalone: %.4f s\n",
           (double)(end - start) / CLOCKS_PER_SEC);
    free(output);
    return 0;
}
```

#### 4.3 性能汇总

```python
# 汇总所有方案的计时结果
import numpy as np

methods = {
    "纯 Python":        t_py,
    "NumPy 向量化":     t_np,
    "Cython（类型化）": t_cy,
    "C（ctypes 调用）": t_c,
}

print("\n" + "="*50)
print(f"{'方法':<20s} {'时间(s)':>10s} {'相对速度':>10s}")
print("-"*50)
fastest = min(methods.values())
for name, t in methods.items():
    speedup = t_py / t
    print(f"{name:<20s} {t:>10.4f} {speedup:>9.1f}x")
print("="*50)
```

**典型结果（1000×1000, maxiter=200）：**

| 方法 | 时间 (s) | 相对纯 Python 加速 |
|------|---------|-------------------|
| 纯 Python 循环 | ~20.0 | 1× |
| NumPy 向量化 | ~0.8 | 25× |
| Cython 类型化 | ~0.2 | 100× |
| C (ctypes) | ~0.12 | 167× |
| C 独立运行 | ~0.10 | 200× |

#### 4.4 性能剖析工具

```python
# cProfile — 识别瓶颈函数
import cProfile
import pstats

def profile_run():
    mandelbrot_pure_python(200, 200, -2, 1, -1.5, 1.5, 100)

cProfile.run('profile_run()', 'profile_stats')
p = pstats.Stats('profile_stats')
p.sort_stats('cumulative').print_stats(10)
# 输出：pure_python 内部的 while 循环 100% 是瓶颈
```

```bash
# memory_profiler — 监测内存峰值
pip install memory_profiler
python -m memory_profiler mandelbrot_benchmark.py
```

#### 4.5 工程决策：何时选择哪一层

```
需要最快速原型？              → 纯 Python（最快写完）
需要比纯 Python 快 10-50×？   → NumPy 向量化（几行代码）
需要接近 C 速度，但要可维护？  → Cython / Numba
已经是最优算法，仍需最后 2×？ → C 扩展 / pybind11
嵌入式 / 无解释器环境？        → 纯 C（独立编译）
```

> 🔗 详细的 C 扩展技术选型（ctypes vs Cython vs pybind11），参见 [[../2精通/07_pybind11与Cython：给C_C++库披上Python外衣|pybind11 与 Cython]]。

### 📝 小节练习

> [!question] 选择题 1
> ctypes 调用 C 共享库时，Python 传递 NumPy 数组给 C 函数的本质是？
> - [ ] A. 数据被序列化为字符串传递
> - [ ] B. 传递指向 NumPy 内部缓冲区的指针（零拷贝）
> - [ ] C. 每调用一次复制全部数组数据
> - [ ] D. 通过网络传输
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: ctypes 可以传递 NumPy 数组底层缓冲区的指针给 C 函数（零拷贝）。前提是数组满足 C-contiguous 且 dtype 匹配。

> [!question] 判断题 1
> Cython 生成的扩展模块不能取代纯 C .so 的位置。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: Cython 编译生成的 .so 是标准的 Python C 扩展，完全可以替代手工编写的 C 扩展模块。实际上很多主流库（如 lxml、scikit-learn 的部分）就是用 Cython 编写的。

---

## 📋 章节测试

### 一、判断题（正确选✅，错误选❌）

> [!question] 判断题 1
> 在基准测试中，运行第一次的结果应该被丢弃以消除冷启动效应。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: 第一次运行包含 CPU 缓存未命中、字节码加载等"冷启动"开销，通常代表性较差。预热后的计时更稳定。

> [!question] 判断题 2
> Cython 代码中 `cdef int i` 声明的变量 i 仍然是 Python 的 int 对象。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `cdef int i` 声明的变量是原生 C `int` 类型，直接存储在 C 栈上，操作速度与 C 相同，不涉及 Python 对象分配。

> [!question] 判断题 3
> `time.perf_counter()` 的精度在所有操作系统上完全一致。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `perf_counter()` 的底层实现因操作系统而异（Linux 用 `clock_gettime(CLOCK_MONOTONIC)`，Windows 用 `QueryPerformanceCounter`），精度通常在纳秒到微秒范围内但不完全相同。

> [!question] 判断题 4
> 如果 NumPy 向量化已经足够快（达到可接受的运行时间），就不应该再投入时间去写 Cython 或 C 扩展。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: 这是实用主义工程原则——如果当前方案已经满足业务需求（如秒级响应），额外的优化是"过早优化"，应把开发时间投入到更有价值的特性上。

> [!question] 判断题 5
> cProfile 可以分析 Cython 编译后的 C 代码的行级性能。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: cProfile 是 Python 层面的剖析器，只能看到 Cython 中那些调用 Python C API 的代码。纯 C 类型的循环对 cProfile 透明。需要对 C 层剖析应使用 perf 或 valgrind/callgrind。

> [!question] 判断题 6
> ctypes 调用 C 函数时，Python GIL（全局解释器锁）被释放。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 部分正确（需要手动释放）
> > **解析**: ctypes 默认**持有** GIL 调用 C 函数。需要在调用前手动 `ctypes.pythonapi.PyGILState_Ensure` / 配合 `ctypes.CFUNCTYPE` 或显式释放 GIL。Cython 可以通过 `with nogil:` 上下文显式释放。

---

### 二、选择题（单项选择题）

> [!question] 选择题 1
> 以下哪种方案最能平衡"开发速度"和"运行速度"？
> - [ ] A. 纯 Python
> - [ ] B. NumPy 向量化
> - [ ] C. 汇编直接操作 SIMD 指令
> - [ ] D. C 独立可执行文件
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: NumPy 向量化仅需几行代码就能获得 10–50× 加速，无需额外编译步骤或类型声明，在开发速度和运行速度之间取得最佳平衡。

> [!question] 选择题 2
> Cython 文件的后缀名是？
> - [ ] A. .c
> - [ ] B. .pxd
> - [ ] C. .pyx
> - [ ] D. .cy
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: Cython 源代码使用 `.pyx` 后缀（实现文件）和 `.pxd` 后缀（声明文件，类似 C 头文件）。`.pxi` 是包含文件。

> [!question] 选择题 3
> 编译 C 代码为 Python 可调用的共享库时，GCC 哪个选项使代码位置无关？
> - [ ] A. `-O3`
> - [ ] B. `-shared`
> - [ ] C. `-fPIC`
> - [ ] D. `-lm`
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: `-fPIC`（Position Independent Code）使生成的代码可以在内存中任意位置加载，是共享库的必要条件。`-shared` 指定输出为共享库。

> [!question] 选择题 4
> 纯 Python Mandelbrot 比 C 版本慢 ~200 倍。Python 变慢最多的时间花在了哪里？
> - [ ] A. 磁盘 I/O
> - [ ] B. Python 解释器在 while 循环中对每个变量的类型检查和方法分派
> - [ ] C. 网络通信
> - [ ] D. 图形渲染
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 纯 Python 的每次算术操作（`zr*zr`, `zi*zi`, `if ...`）都需要检查变量类型、查找 `__mul__`/`__add__` 方法、创建新的 float 对象，这些动态分派的累积开销远超实际算术计算。

> [!question] 选择题 5
> 以下哪个工具专用于测量 Python 代码的内存使用情况？
> - [ ] A. cProfile
> - [ ] B. timeit
> - [ ] C. memory_profiler
> - [ ] D. line_profiler
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: `memory_profiler` 专用于行级内存占用分析。`cProfile` 分析执行时间和调用次数，`line_profiler` 分析每行执行时间而非内存。

> [!question] 选择题 6
> 从纯 Python → NumPy → Cython → C 的性能提升趋势最接近？
> - [ ] A. 线性提升
> - [ ] B. 指数提升
> - [ ] C. 先大跳跃再趋于平缓
> - [ ] D. 先平缓后大跳跃
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: Python → NumPy 是最大的跳跃（消除 Python 内层循环 → 20–50×），NumPy → Cython 得到 3–5×（消除外层 Python 循环和类型装箱），Cython → C 仅 1.2–2×（语言本身的开销已经极小）。

---

### 🛠️ 动手练习题

> [!example] 练习题 1：多方案矩阵乘法基准测试
> **难度**: ⭐⭐
>
> 实现五个版本的矩阵乘法（N=500）：（1）纯 Python 三重循环；（2）NumPy `dot()`；（3）用 `numba.jit` 加速纯 Python 循环；（4）用 Cython 编写并编译；（5）用 `scipy.linalg.blas.dgemm`（直接调用 BLAS）。比较它们的速度和精度。解释为什么 BLAS 版本可能比手写 Cython 还快（BLAS 使用了分块和多线程）。

> [!example] 练习题 2：cProfile 剖析实战
> **难度**: ⭐⭐
>
> 使用 cProfile 剖析纯 Python 的 Mandelbrot 实现。从剖析输出中提取耗费时间最多的 3 个函数。使用 `pstats.Stats` 的 `print_callers` 分析函数被调用的上下文。尝试对热函数进行简单优化（如将复合表达式拆分、使用局部变量别名），观察剖析结果的变化。

> [!example] 练习题 3：memory_profiler 监控
> **难度**: ⭐⭐
>
> 编写一个程序生成大量 NumPy 临时中间数组（如链式操作 `((a+b)*(c+d))/(e-f)` 不显式分配中间变量）。使用 `memory_profiler` 监控每条语句的内存增量。对比使用 `np.add(a, b, out=tmp)` 等显式 out 参数的版本，验证内存节省效果。报告峰值内存的差异。

> [!example] 练习题 4：GIL 释放对并行性能的影响
> **难度**: ⭐⭐⭐
>
> 编写一个计算密集型函数（如计算 π 的 Chudnovsky 算法），实现三个版本：（1）纯 Python；（2）Cython 带 `with nogil:` ；（3）C 扩展通过 ctypes 释放 GIL。使用 `concurrent.futures.ThreadPoolExecutor` 测试多线程加速比。解释为什么版本（1）多线程无加速，而（2）（3）有加速。对比进程池（ProcessPoolExecutor）的行为。

> [!example] 练习题 5：完整性能报告
> **难度**: ⭐⭐⭐
>
> 对 Mandelbrot 的所有五种实现进行系统性基准测试，收集以下维度的数据：
> - 在不同网格大小（100×100, 500×500, 2000×2000）下的运行时间
> - cProfile 输出的 top 5 热函数
> - memory_profiler 的峰值内存
> - 代码行数（不含空行和注释）
>
> 汇总为表格和柱状图，撰写一份简洁的性能分析报告，回答："对于 [特定场景]，推荐使用 [方案]，因为 [原因]"。使用 `matplotlib` 绘制加速比对比图。

> 🔗 性能优化是一个循环：剖析 → 识别瓶颈 → 优化 → 再剖析。详细剖析技巧参见 [[../../数学/|数学专题]] 和 [[../8数据可视化/|数据可视化]] 中绘图相关内容。
