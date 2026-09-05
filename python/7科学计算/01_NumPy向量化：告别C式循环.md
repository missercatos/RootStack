# NumPy 向量化：告别 C 式循环 (NumPy Vectorization)
---

## 章节概述

从 C 语言切换到 Python 做数值计算，最大的思维转变是将"逐元素循环"改为"数组整体操作"。本章深入剖析 NumPy 向量化的底层原理——为何 `a + b` 比 C 的 `for` 循环更快（SIMD 指令、BLAS 后端、零 Python 循环开销），系统地讲解通用函数（ufunc）、广播规则、花式索引、条件选择（`np.where`/`np.select`）以及内存布局（C-contiguous vs Fortran-contiguous）对性能的影响。

> **核心理念**：向量化不是语法糖——它是将 Python 解释器的循环开销"挤压"为零，把计算任务整体"扔"给底层 C/Fortran 引擎执行。理解向量化，就是理解 Python 科学计算栈为何能"快得像 C 一样"。

---

### 第一节：C 循环与 Python 循环的性能鸿沟

#### 1.1 Python 循环为什么慢

每个 Python 对象都携带引用计数、类型指针、动态分派等"元数据开销"。一个简单的 `a[i] + b[i]` 在 Python 循环中实际发生的是：

```
从列表取元素 → 创建 PyObject 引用 → 查找 __add__ 方法 → 调用 → 拆箱 → 装箱返回
```

而 C 循环中 `a[i] + b[i]` 只是两次内存读取 + 一次 ALU 加法指令。

```python
import numpy as np
import time

N = 10_000_000
a, b = np.random.rand(N), np.random.rand(N)
c = np.empty(N)

# C 风格逐元素循环（Python 层）
t0 = time.perf_counter()
for i in range(N):
 c[i] = a[i] + b[i]
t1 = time.perf_counter()
print(f"Python 循环: {t1 - t0:.4f} s")

# NumPy 向量化
t0 = time.perf_counter()
c = a + b
t1 = time.perf_counter()
print(f"NumPy 向量化: {t1 - t0:.4f} s")
```

典型输出（10,000,000 元素）：

```
Python 循环: 3.2 s
NumPy 向量化: 0.03 s # 快 ~100 倍
```

> NumPy 向量化操作中，`a + b` 的循环在底层 C 代码中执行，全程无 Python 对象参与。

#### 1.2 C 语言中同等的循环

```c
// 在 C 中，逐元素加法直接编译为高效的机器码
#include <stdlib.h>
#include <time.h>

void add_arrays(double *a, double *b, double *c, size_t n) {
 for (size_t i = 0; i < n; i++)
 c[i] = a[i] + b[i]; // 编译器可自动向量化为 SIMD
}
```

C 编译器（`gcc -O3`）会将该循环自动向量化为 SSE/AVX 指令——这就是 NumPy 底层做的事情。区别在于：NumPy 已经替你用好了编译器优化和 BLAS 库，无需手写 CMakeLists、链接 BLAS、管理内存。

---

### 第二节：通用函数（ufunc）的原理与实践

#### 2.1 什么是 ufunc

ufunc（Universal Function）是 NumPy 的核心抽象：对数组中每个元素执行相同操作的高效函数。所有算术运算符（`+`, `-`, `*`, `/`）本质上都是 ufunc 的语法糖。

```python
import numpy as np

# 等价关系：a + b 等价于 np.add(a, b)
a = np.array([1.0, 2.0, 3.0])
b = np.array([4.0, 5.0, 6.0])
print(np.add(a, b)) # [5. 7. 9.]
print(np.multiply(a, b)) # [ 4. 10. 18.]

# ufunc 的 reduce 方法：累积操作
print(np.add.reduce(a)) # 1+2+3 = 6.0

# ufunc 的 accumulate 方法：前缀扫描
print(np.add.accumulate(a)) # [1. 3. 6.]

# ufunc 的 outer 方法：外积
print(np.multiply.outer(a, b))
# [[ 4. 5. 6.]
# [ 8. 10. 12.]
# [12. 15. 18.]]
```

#### 2.2 ufunc 的底层加速机制

NumPy 的 ufunc 在内部使用了三阶加速策略：

| 层级 | 技术 | 适用场景 |
|------|------|---------|
| 第 1 层 | 编译为 SIMD 指令（SSE/AVX） | 所有基本运算 |
| 第 2 层 | 调用 BLAS 库（OpenBLAS/MKL） | 矩阵运算（dot, matmul） |
| 第 3 层 | 多线程并行 | 大数组上的 BLAS 调用 |

```python
import numpy as np

# 自定义 ufunc 行为 — out 参数避免分配新数组
a = np.random.rand(1000000)
b = np.random.rand(1000000)
c = np.empty(1000000)
np.add(a, b, out=c) # 结果存入 c，不分配新内存

# in-place 操作
a += b # 等价于 np.add(a, b, out=a)，原地修改
```

> `out` 参数是 ufunc 的重要性能优化手段：避免每次运算都分配新的数组内存，适合循环调用场景。

---

### 第三节：广播（Broadcasting）规则

#### 3.1 广播的基本规则

当两个数组形状不同时，NumPy 会按以下规则尝试自动"拉伸"较小的数组：

1. 从最右侧维度开始比对
2. 两个维度相等，或其中一个为 1 时兼容
3. 缺失的维度自动补 1

```python
import numpy as np

a = np.array([[1, 2, 3],
 [4, 5, 6]]) # shape (2, 3)
b = np.array([10, 20, 30]) # shape (3,) → 广播为 (2, 3)
print(a + b)
# [[11 22 33]
# [14 25 36]]

# 列向量广播
c = np.array([[100],
 [200]]) # shape (2, 1) → 广播为 (2, 3)
print(a + c)
# [[101 102 103]
# [204 205 206]]

# 0 维标量广播
print(a + 5) # 5 广播到所有元素
```

#### 3.2 经典广播案例

```python
import numpy as np

# 数据中心化（减去均值）
data = np.random.rand(100, 50) # 100 个样本，50 个特征
centered = data - data.mean(axis=0) # mean 的形状 (50,) 广播到 (100, 50)

# 外积
x = np.array([1, 2, 3]) # shape (3,)
y = np.array([4, 5]) # shape (2,)
# x[:, None] → (3, 1) 和 y → (2,) → (1, 2) 广播为 (3, 2)
outer = x[:, np.newaxis] * y
print(outer)
# [[ 4 5]
# [ 8 10]
# [12 15]]

# 距离矩阵：计算所有点对之间的欧氏距离
points = np.random.rand(100, 3)
diff = points[:, np.newaxis, :] - points[np.newaxis, :, :] # (100, 1, 3) - (1, 100, 3) → (100, 100, 3)
dist = np.sqrt((diff ** 2).sum(axis=2)) # (100, 100)
```

> 广播虽然方便，但会**隐式复制**数据。`a + b` 中如果 `b` 被广播到和 `a` 同样大小，内存中不会真的复制 `b`——NumPy 使用"步长"（stride）技巧，零拷贝实现。

---

### 第四节：花式索引与条件选择

#### 4.1 花式索引（Fancy Indexing）

花式索引使用整数数组进行索引，返回的是**新数组的副本**（区别于切片返回视图）。

```python
import numpy as np

a = np.arange(10) * 10 # [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
idx = np.array([2, 5, 8])
print(a[idx]) # [20 50 80]

# 二维花式索引
mat = np.arange(16).reshape(4, 4)
# 取 (0,0), (1,2), (2,1), (3,3) 位置
print(mat[[0, 1, 2, 3], [0, 2, 1, 3]]) # [0, 6, 9, 15]

# 取子矩阵：行索引 + 列索引的笛卡尔积
print(mat[[0, 3]][:, [1, 2]]) # 第 0 行和第 3 行的第 1,2 列
# [[ 1 2]
# [13 14]]
```

> 花式索引与 C 语言对比：在 C 中你需要嵌套循环 `for(i=0; i<n; i++) out[i] = a[idx[i]]`，而 NumPy 一行搞定且底层用 C 循环执行。

#### 4.2 布尔索引与 np.where

```python
import numpy as np

a = np.array([3, -1, 0, 7, -4, 2])

# 布尔索引：筛选满足条件的元素
positives = a[a > 0] # [3 7 2]

# np.where(条件, 真值, 假值) — 三目运算符的向量化版本
result = np.where(a > 0, a, -a) # 取绝对值：[3 1 0 7 4 2]

# 获取满足条件的索引位置
indices = np.where(a > 0) # (array([0, 3, 5]),)
print(a[indices]) # [3 7 2]

# 多条件：np.where 中 & 表示"与"，| 表示"或"
mask = (a > -2) & (a < 5) # 注意括号！
print(a[mask]) # [ 3 -1 0 2]
```

#### 4.3 np.select：多分支条件选择

对于 C 中 `if-elif-else` 链的向量化版本，使用 `np.select`：

```python
import numpy as np

scores = np.array([85, 92, 45, 78, 60, 33, 71])

# 等价于：for each s in scores:
# if s >= 90: grade = 'A'
# elif s >= 75: grade = 'B'
# elif s >= 60: grade = 'C'
# else: grade = 'F'
conditions = [scores >= 90, scores >= 75, scores >= 60]
choices = ['A', 'B', 'C']
default = 'F'
grades = np.select(conditions, choices, default)
print(grades) # ['B' 'A' 'F' 'B' 'C' 'F' 'B']
```

> `np.select` 按顺序评估条件列表，第一个匹配的条件胜出（类似 C 的 if-elif 链），这与 `np.where` 不同。

---

### 第五节：内存布局与性能

#### 5.1 C-contiguous 与 Fortran-contiguous

NumPy 数组在内存中有两种主要布局：

```
C-contiguous (行优先): [[1, 2, 3],
Row-major [4, 5, 6]]
 内存中: [1, 2, 3, 4, 5, 6] ← 最后维度连续变化最快

Fortran-contiguous (列优先): [[1, 2, 3],
Column-major [4, 5, 6]]
 内存中: [1, 4, 2, 5, 3, 6] ← 第一个维度连续变化最快
```

C 程序员天然习惯行优先（C-contiguous），因为 C 语言多维数组就是行优先布局。

```python
import numpy as np

a = np.array([[1, 2, 3], [4, 5, 6]], order='C')
print(a.flags['C_CONTIGUOUS']) # True
print(a.strides) # (24, 8) 行步长 24 字节（3×8），列步长 8

f = np.array([[1, 2, 3], [4, 5, 6]], order='F')
print(f.flags['F_CONTIGUOUS']) # True
print(f.strides) # (8, 16) 行步长 8 字节，列步长 16
```

> 数组的 `.strides` 是以**字节**为单位的步长。`float64` 数组每个元素 8 字节，C-contiguous 时 strides 末尾为 8。

#### 5.2 内存布局对性能的影响

逐行（沿最后轴）遍历 C-contiguous 数组可获得最佳缓存局部性：

```python
import numpy as np
import time

N = 4096
a = np.random.rand(N, N)

# 正确做法：按行遍历（沿 C-contiguous 的"快方向"）
t0 = time.perf_counter()
s = 0.0
for i in range(N):
 for j in range(N):
 s += a[i, j]
t1 = time.perf_counter()
print(f"行优先遍历: {t1 - t0:.4f} s")

# 错误做法：按列遍历（沿 C-contiguous 的"慢方向"）
t0 = time.perf_counter()
s = 0.0
for j in range(N):
 for i in range(N):
 s += a[i, j]
t1 = time.perf_counter()
print(f"列优先遍历: {t1 - t0:.4f} s")
# 列优先遍历明显更慢（缓存未命中的代价）
```

**优化策略：**

```python
# 永远用向量化替代显式循环
s = a.sum() # 比双层循环快数百倍

# 如果必须循环，用 Cython/Numba，且沿行方向遍历
# 转换内存布局（谨慎使用，这需要复制数据）
f_order = np.asfortranarray(a) # 原地转换
c_order = np.ascontiguousarray(f_order)
```

> 有关 Cython 和将 C 代码嵌入 Python 的详细讨论，参见 [[../2精通/07_pybind11与Cython：给C_C++库披上Python外衣|pybind11 与 Cython]]。

---

## 力扣练习

以下题目用于验证本章所学内容：

| 题号 | 题目 | 链接 | 涉及知识点 |
|------|------|------|-----------|
| 66 | 加一 | https://leetcode.cn/problems/plus-one/ | 数组向量化操作 |
| 118 | 杨辉三角 | https://leetcode.cn/problems/pascals-triangle/ | 二维数组递推 |
| 48 | 旋转图像 | https://leetcode.cn/problems/rotate-image/ | 矩阵操作、原地旋转 |
