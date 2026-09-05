# 性能对比：纯 Python vs Cython vs C (Performance Comparison)
---

## 章节概述

"Python 速度够快吗？"——这是每个从 C 语言转向 Python 的开发者首先面临的问题。本章不靠抽象说教，而是用一个具体的基准任务（Mandelbrot 集计算）横向对比五种实现方案：纯 Python 循环、NumPy 向量化、Cython 类型化加速、C 编译为共享库（.so）通过 ctypes 调用、以及纯 C 独立可执行文件。我们将测量执行时间、剖析性能瓶颈（cProfile）、监控内存占用（memory_profiler），并在此基础上讨论"何时 Python 速度是瓶颈，何时开发速度更重要"的工程决策。

> **核心理念**：性能不是二元选择——它有层次。从 Python → NumPy → Cython → C 是一条连续的光谱，每一层都需要额外的开发代价以换取运行速度。聪明的工程师知道什么时候该"停留"在某一层。

---

### 第一节：基准测试任务与环境设置

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

> `time.perf_counter()` 提供系统上可用的最高精度时钟，不受系统时间调整影响，是 Python 基准测试的首选。

---

### 第二节：纯 Python 与 NumPy 向量化

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
 c = cx[:, None] + 1j * cy[None, :] # (width, height) 复数网格

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

 return output.T # 转置以匹配 (height, width) 布局

result_np, t_np = benchmark(
 mandelbrot_numpy,
 WIDTH, HEIGHT, XMIN, XMAX, YMIN, YMAX, MAXITER,
 name="NumPy 向量化"
)
# 典型输出: 0.5–1.5 s（快 20–30 倍）
```

> NumPy 向量化版本仍有一个**外层 Python 循环**（`for n in range(maxiter)`），但内层操作（`z[mask]**2`, `np.abs(z) > 2`）全部在 C 层面执行。这是典型的"半向量化"——外层迭代无法消除时，每次迭代都是高效的 C 操作。

---

### 第三节：Cython 类型化加速

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

> Cython 的关键优化指令：
> - `@boundscheck(False)` — 关闭数组索引越界检查
> - `@wraparound(False)` — 关闭负索引处理
> - `cdivision(True)` — 使用 C 除法规避 ZeroDivisionError
> 这些是"把安全气囊关掉跑得更快"，仅在调试完成后使用。

---

### 第四节：C 扩展与性能汇总

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
 "纯 Python": t_py,
 "NumPy 向量化": t_np,
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
需要最快速原型？ → 纯 Python（最快写完）
需要比纯 Python 快 10-50×？ → NumPy 向量化（几行代码）
需要接近 C 速度，但要可维护？ → Cython / Numba
已经是最优算法，仍需最后 2×？ → C 扩展 / pybind11
嵌入式 / 无解释器环境？ → 纯 C（独立编译）
```

> 详细的 C 扩展技术选型（ctypes vs Cython vs pybind11），参见 [[../2精通/07_pybind11与Cython：给C_C++库披上Python外衣|pybind11 与 Cython]]。

---

## 力扣练习

以下题目用于验证本章所学内容：

| 题号 | 题目 | 链接 | 涉及知识点 |
|------|------|------|-----------|
| — | 本章无对应力扣题 | — | 请用动手练习题自检 |
