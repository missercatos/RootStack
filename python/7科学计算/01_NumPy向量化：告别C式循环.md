# NumPy 向量化：告别 C 式循环 (NumPy Vectorization)
---

## 📖 章节概述

从 C 语言切换到 Python 做数值计算，最大的思维转变是将"逐元素循环"改为"数组整体操作"。本章深入剖析 NumPy 向量化的底层原理——为何 `a + b` 比 C 的 `for` 循环更快（SIMD 指令、BLAS 后端、零 Python 循环开销），系统地讲解通用函数（ufunc）、广播规则、花式索引、条件选择（`np.where`/`np.select`）以及内存布局（C-contiguous vs Fortran-contiguous）对性能的影响。

> **核心理念**：向量化不是语法糖——它是将 Python 解释器的循环开销"挤压"为零，把计算任务整体"扔"给底层 C/Fortran 引擎执行。理解向量化，就是理解 Python 科学计算栈为何能"快得像 C 一样"。

---

### 📚 第一节：C 循环与 Python 循环的性能鸿沟

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
NumPy 向量化: 0.03 s   # 快 ~100 倍
```

> 💡 NumPy 向量化操作中，`a + b` 的循环在底层 C 代码中执行，全程无 Python 对象参与。

#### 1.2 C 语言中同等的循环

```c
// 在 C 中，逐元素加法直接编译为高效的机器码
#include <stdlib.h>
#include <time.h>

void add_arrays(double *a, double *b, double *c, size_t n) {
    for (size_t i = 0; i < n; i++)
        c[i] = a[i] + b[i];   // 编译器可自动向量化为 SIMD
}
```

C 编译器（`gcc -O3`）会将该循环自动向量化为 SSE/AVX 指令——这就是 NumPy 底层做的事情。区别在于：NumPy 已经替你用好了编译器优化和 BLAS 库，无需手写 CMakeLists、链接 BLAS、管理内存。

### 📝 小节练习

> [!question] 选择题 1
> Python 逐元素循环比 NumPy 向量化慢的根本原因是？
> - [ ] A. NumPy 使用了更快的 CPU
> - [ ] B. Python 循环中每次迭代都涉及 PyObject 的装箱/拆箱和方法查找
> - [ ] C. NumPy 的算法是 O(1) 的
> - [ ] D. Python 的数字类型精度不够
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: Python 循环慢的根本原因不是算法，而是语言运行时开销——每个元素操作都需经历 PyObject 引用创建、类型检查、方法分发等动态过程。

> [!question] 判断题 1
> NumPy 的 `a + b` 操作在 Python 层面仍然执行了一个隐式循环。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: NumPy 的向量化操作在 **C 层面**执行循环，Python 只负责调用入口函数。循环本身完全发生在 CPython 解释器之外。

---

### 📚 第二节：通用函数（ufunc）的原理与实践

#### 2.1 什么是 ufunc

ufunc（Universal Function）是 NumPy 的核心抽象：对数组中每个元素执行相同操作的高效函数。所有算术运算符（`+`, `-`, `*`, `/`）本质上都是 ufunc 的语法糖。

```python
import numpy as np

# 等价关系：a + b 等价于 np.add(a, b)
a = np.array([1.0, 2.0, 3.0])
b = np.array([4.0, 5.0, 6.0])
print(np.add(a, b))          # [5. 7. 9.]
print(np.multiply(a, b))     # [ 4. 10. 18.]

# ufunc 的 reduce 方法：累积操作
print(np.add.reduce(a))      # 1+2+3 = 6.0

# ufunc 的 accumulate 方法：前缀扫描
print(np.add.accumulate(a))  # [1. 3. 6.]

# ufunc 的 outer 方法：外积
print(np.multiply.outer(a, b))
# [[ 4.  5.  6.]
#  [ 8. 10. 12.]
#  [12. 15. 18.]]
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
np.add(a, b, out=c)   # 结果存入 c，不分配新内存

# in-place 操作
a += b   # 等价于 np.add(a, b, out=a)，原地修改
```

> 💡 `out` 参数是 ufunc 的重要性能优化手段：避免每次运算都分配新的数组内存，适合循环调用场景。

### 📝 小节练习

> [!question] 选择题 1
> ufunc 的 `accumulate` 方法产生的结果等价于？
> - [ ] A. 数组排序
> - [ ] B. 前缀扫描（prefix scan）
> - [ ] C. 矩阵转置
> - [ ] D. 随机采样
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `accumulate` 执行前缀扫描：`out[i] = op.reduce(a[:i+1])`。例如 `np.add.accumulate([1,2,3])` 得到 `[1, 3, 6]`。

> [!question] 判断题 1
> `a += b` 和 `a = a + b` 在 NumPy 中的行为完全相同。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `a += b` 是原地操作（修改 a 指向的数组），`a = a + b` 则创建新数组并重新绑定变量名。前者节省内存，但要求 `a` 和 `b` 的 shape 和 dtype 兼容。

---

### 📚 第三节：广播（Broadcasting）规则

#### 3.1 广播的基本规则

当两个数组形状不同时，NumPy 会按以下规则尝试自动"拉伸"较小的数组：

1. 从最右侧维度开始比对
2. 两个维度相等，或其中一个为 1 时兼容
3. 缺失的维度自动补 1

```python
import numpy as np

a = np.array([[1, 2, 3],
              [4, 5, 6]])       # shape (2, 3)
b = np.array([10, 20, 30])     # shape (3,) → 广播为 (2, 3)
print(a + b)
# [[11 22 33]
#  [14 25 36]]

# 列向量广播
c = np.array([[100],
              [200]])           # shape (2, 1) → 广播为 (2, 3)
print(a + c)
# [[101 102 103]
#  [204 205 206]]

# 0 维标量广播
print(a + 5)  # 5 广播到所有元素
```

#### 3.2 经典广播案例

```python
import numpy as np

# 数据中心化（减去均值）
data = np.random.rand(100, 50)         # 100 个样本，50 个特征
centered = data - data.mean(axis=0)    # mean 的形状 (50,) 广播到 (100, 50)

# 外积
x = np.array([1, 2, 3])               # shape (3,)
y = np.array([4, 5])                  # shape (2,)
# x[:, None] → (3, 1) 和 y → (2,) → (1, 2) 广播为 (3, 2)
outer = x[:, np.newaxis] * y
print(outer)
# [[ 4  5]
#  [ 8 10]
#  [12 15]]

# 距离矩阵：计算所有点对之间的欧氏距离
points = np.random.rand(100, 3)
diff = points[:, np.newaxis, :] - points[np.newaxis, :, :]  # (100, 1, 3) - (1, 100, 3) → (100, 100, 3)
dist = np.sqrt((diff ** 2).sum(axis=2))    # (100, 100)
```

> ⚠️ 广播虽然方便，但会**隐式复制**数据。`a + b` 中如果 `b` 被广播到和 `a` 同样大小，内存中不会真的复制 `b`——NumPy 使用"步长"（stride）技巧，零拷贝实现。

### 📝 小节练习

> [!question] 选择题 1
> `a = np.ones((3, 1))` 与 `b = np.ones((4,))` 相加，结果的形状是？
> - [ ] A. (3,)
> - [ ] B. (4,)
> - [ ] C. (3, 4)
> - [ ] D. 广播失败，报错
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: (3, 1) 与 (4,) → (1, 4) 广播：从右比对，1 和 4 兼容（1 可拉伸），左端 (3,) 和空维度兼容，结果是 (3, 4)。

> [!question] 判断题 1
> 广播操作会实际在内存中复制被广播数组的数据。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 广播通过"步长"（stride）技巧实现零拷贝的虚拟复制——在内存中数据只有一份，通过修改数组的 strides 使得遍历时重复访问相同元素。

---

### 📚 第四节：花式索引与条件选择

#### 4.1 花式索引（Fancy Indexing）

花式索引使用整数数组进行索引，返回的是**新数组的副本**（区别于切片返回视图）。

```python
import numpy as np

a = np.arange(10) * 10    # [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
idx = np.array([2, 5, 8])
print(a[idx])             # [20 50 80]

# 二维花式索引
mat = np.arange(16).reshape(4, 4)
# 取 (0,0), (1,2), (2,1), (3,3) 位置
print(mat[[0, 1, 2, 3], [0, 2, 1, 3]])   # [0, 6, 9, 15]

# 取子矩阵：行索引 + 列索引的笛卡尔积
print(mat[[0, 3]][:, [1, 2]])   # 第 0 行和第 3 行的第 1,2 列
# [[ 1  2]
#  [13 14]]
```

> 💡 花式索引与 C 语言对比：在 C 中你需要嵌套循环 `for(i=0; i<n; i++) out[i] = a[idx[i]]`，而 NumPy 一行搞定且底层用 C 循环执行。

#### 4.2 布尔索引与 np.where

```python
import numpy as np

a = np.array([3, -1, 0, 7, -4, 2])

# 布尔索引：筛选满足条件的元素
positives = a[a > 0]              # [3 7 2]

# np.where(条件, 真值, 假值) — 三目运算符的向量化版本
result = np.where(a > 0, a, -a)   # 取绝对值：[3 1 0 7 4 2]

# 获取满足条件的索引位置
indices = np.where(a > 0)         # (array([0, 3, 5]),)
print(a[indices])                 # [3 7 2]

# 多条件：np.where 中 & 表示"与"，| 表示"或"
mask = (a > -2) & (a < 5)         # 注意括号！
print(a[mask])                     # [ 3 -1  0  2]
```

#### 4.3 np.select：多分支条件选择

对于 C 中 `if-elif-else` 链的向量化版本，使用 `np.select`：

```python
import numpy as np

scores = np.array([85, 92, 45, 78, 60, 33, 71])

# 等价于：for each s in scores:
#   if s >= 90: grade = 'A'
#   elif s >= 75: grade = 'B'
#   elif s >= 60: grade = 'C'
#   else: grade = 'F'
conditions = [scores >= 90, scores >= 75, scores >= 60]
choices    = ['A', 'B', 'C']
default    = 'F'
grades = np.select(conditions, choices, default)
print(grades)   # ['B' 'A' 'F' 'B' 'C' 'F' 'B']
```

> ⚠️ `np.select` 按顺序评估条件列表，第一个匹配的条件胜出（类似 C 的 if-elif 链），这与 `np.where` 不同。

### 📝 小节练习

> [!question] 选择题 1
> `a[[1, 2, 3]]` 返回的是？
> - [ ] A. a 的视图（view）
> - [ ] B. a 的副本（copy）
> - [ ] C. a 的引用
> - [ ] D. 取决于数组大小
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 花式索引（用整数数组索引）始终返回**副本**（copy），区别于切片返回视图（view）。修改返回的数组不会影响原数组。

> [!question] 选择题 2
> `np.where(arr > 0)` 返回的是什么？
> - [ ] A. 满足条件的元素值
> - [ ] B. 满足条件的元素的索引
> - [ ] C. 一个布尔数组
> - [ ] D. True 或 False
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `np.where(condition)` 单参数形式返回满足条件的元素的**索引元组**。要用条件选择值，使用三参数形式 `np.where(condition, x, y)`。

---

### 📚 第五节：内存布局与性能

#### 5.1 C-contiguous 与 Fortran-contiguous

NumPy 数组在内存中有两种主要布局：

```
C-contiguous (行优先):  [[1, 2, 3],
Row-major                [4, 5, 6]]
  内存中: [1, 2, 3, 4, 5, 6]    ← 最后维度连续变化最快

Fortran-contiguous (列优先): [[1, 2, 3],
Column-major                  [4, 5, 6]]
  内存中: [1, 4, 2, 5, 3, 6]    ← 第一个维度连续变化最快
```

C 程序员天然习惯行优先（C-contiguous），因为 C 语言多维数组就是行优先布局。

```python
import numpy as np

a = np.array([[1, 2, 3], [4, 5, 6]], order='C')
print(a.flags['C_CONTIGUOUS'])  # True
print(a.strides)                 # (24, 8)  行步长 24 字节（3×8），列步长 8

f = np.array([[1, 2, 3], [4, 5, 6]], order='F')
print(f.flags['F_CONTIGUOUS'])  # True
print(f.strides)                 # (8, 16)  行步长 8 字节，列步长 16
```

> 💡 数组的 `.strides` 是以**字节**为单位的步长。`float64` 数组每个元素 8 字节，C-contiguous 时 strides 末尾为 8。

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
s = a.sum()  # 比双层循环快数百倍

# 如果必须循环，用 Cython/Numba，且沿行方向遍历
# 转换内存布局（谨慎使用，这需要复制数据）
f_order = np.asfortranarray(a)   # 原地转换
c_order = np.ascontiguousarray(f_order)
```

> 🔗 有关 Cython 和将 C 代码嵌入 Python 的详细讨论，参见 [[../2精通/07_pybind11与Cython：给C_C++库披上Python外衣|pybind11 与 Cython]]。

### 📝 小节练习

> [!question] 选择题 1
> C-contiguous 布局下，`arr.strides[0]` 与 `arr.strides[1]` 的关系是？
> - [ ] A. `strides[0] == strides[1]`
> - [ ] B. `strides[0] > strides[1]`
> - [ ] C. `strides[0] < strides[1]`
> - [ ] D. 不确定
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 行优先布局下，沿行方向跨越一行需要的字节数 > 沿列方向跨越一列，所以 `strides[0]`（行步长）= `cols × elementsize` > `strides[1]`（列步长）= `elementsize`。

> [!question] 判断题 1
> `np.ascontiguousarray()` 可能产生数据复制。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: 如果原数组已经满足 C-contiguous，`np.ascontiguousarray()` 返回原数组（不复制）；否则需要重新排列内存中的数据（复制）。

---

## 📋 章节测试

### 一、判断题（正确选✅，错误选❌）

> [!question] 判断题 1
> Python 的 `for i in range(N): c[i] = a[i] + b[i]` 和 NumPy 的 `a + b` 在执行速度上没有本质区别。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 有本质区别。Python 循环在解释器层面执行，NumPy 操作在编译后的 C 代码中执行，通常快 50–200 倍。

> [!question] 判断题 2
> ufunc 的 `out` 参数可以避免额外的内存分配。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `np.add(a, b, out=c)` 将结果直接写入 `c`，不分配 `a + b` 的临时中间数组，在大数组循环累积的场景中很关键。

> [!question] 判断题 3
> 广播操作会实际在内存中复制数据。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 广播通过修改 stride 实现零拷贝的虚复制，数据在内存中只有一份。

> [!question] 判断题 4
> 花式索引（fancy indexing）返回的是原数组的视图。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 花式索引始终返回副本（copy），不同于切片返回视图。

> [!question] 判断题 5
> 对 C-contiguous 数组沿列遍历与沿行遍历的缓存效率相同。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 沿"快方向"（行优先下的列方向，strides 最小的方向）遍历可获得最佳缓存局部性；沿"慢方向"跨大步长导致大量缓存未命中。

> [!question] 判断题 6
> `a += b` 总是比 `a = a + b` 更快。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `a += b` 执行原地加法，避免分配 `a + b` 的临时数组，也避免了赋值时的内存分配和复制。

> [!question] 判断题 7
> `np.where(condition)` 单参数形式等价于 `np.nonzero(condition)`。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: 单参数 `np.where(condition)` 等价于 `np.nonzero(condition)`，返回满足条件的元素索引。

> [!question] 判断题 8
> NumPy 的 C-contiguous 数组与 C 语言中 `float a[rows][cols]` 的内存布局完全一致。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: 两者都是行优先（row-major）布局，内存排列完全一致。因此 `ctypes` 传递 NumPy 数组给 C 函数时大多无需复制。

---

### 二、选择题（单项选择题）

> [!question] 选择题 1
> 以下哪个操作不是 NumPy 的 ufunc？
> - [ ] A. `np.add`
> - [ ] B. `np.sin`
> - [ ] C. `np.sort`
> - [ ] D. `np.multiply`
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: `sort` 不是 ufunc（通用函数），它不能逐元素独立操作，需要访问数组的全局结构。`add`, `sin`, `multiply` 等都是典型的 ufunc。

> [!question] 选择题 2
> `np.add.reduce([1, 2, 3, 4])` 的结果是？
> - [ ] A. `[1, 3, 6, 10]`
> - [ ] B. `10`
> - [ ] C. `[1, 2, 3, 4]`
> - [ ] D. `24`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `reduce` 执行归约操作，`np.add.reduce` 将累加到最后得到一个标量 1+2+3+4=10。`accumulate` 才返回中间结果 `[1, 3, 6, 10]`。

> [!question] 选择题 3
> 数组 `a.shape = (4, 3)` 和 `b.shape = (3,)` 广播相加，结果 shape 是？
> - [ ] A. (3,)
> - [ ] B. (4,)
> - [ ] C. (4, 3)
> - [ ] D. 广播失败
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: 从右比对：3 和 3 匹配，左侧 4 保留，b 被广播为 (4, 3)。

> [!question] 选择题 4
> `np.where(a > 5, a + 10, a - 10)` 等价于以下哪个 C 代码逻辑？
> - [ ] A. `for(i=0;i<n;i++) a[i] = a[i] + 10;`
> - [ ] B. `for(i=0;i<n;i++) a[i] = a[i] > 5 ? a[i] + 10 : a[i] - 10;`
> - [ ] C. `for(i=0;i<n;i++) if(a[i] > 5) break;`
> - [ ] D. `for(i=0;i<n;i++) a[i] = a[i] > 5 ? a[i] : 0;`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `np.where(cond, x, y)` 是 C 语言三目运算符 `cond ? x : y` 的向量化版本。

> [!question] 选择题 5
> 以下关于 `np.select` 的说法，正确的是？
> - [ ] A. 所有条件都会被评估
> - [ ] B. 按顺序评估，第一个满足的条件胜出
> - [ ] C. 随机选一个满足的条件
> - [ ] D. 所有满足条件的取平均值
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `np.select` 按条件列表顺序评估，第一个 True 的条件对应的 choice 被选中，后面的条件不再评估（类似 C 的 if-elif-else 链）。

> [!question] 选择题 6
> `float64` 数组中，C-contiguous 布局下 strides 的典型值是 `(bytes_per_row, 8)`。`bytes_per_row` 等于？
> - [ ] A. `8`
> - [ ] B. `列数 × 8`
> - [ ] C. `行数 × 8`
> - [ ] D. `8 * 2`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 沿行方向跨越一整行，跳过多列元素，所以 `strides[0] = cols * 8`（float64 每个 8 字节），`strides[1] = 8`。

> [!question] 选择题 7
> C 语言中 `double a[M][N]` 声明，元素 `a[i][j]` 的内存地址偏移公式是？
> - [ ] A. `(i + j * M) * sizeof(double)`
> - [ ] B. `(i * N + j) * sizeof(double)`
> - [ ] C. `(j * M + i) * sizeof(double)`
> - [ ] D. `i * j * sizeof(double)`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: C 语言使用行优先布局，`a[i][j]` 位于第 i 行第 j 列，需要跳过 i 个完整行（每行 N 个元素）再加 j，偏移为 `(i*N+j)*sizeof(double)`。

> [!question] 选择题 8
> 以下哪种方式对 C-contiguous 大数组的**逐元素遍历**缓存最友好？
> - [ ] A. `for i in range(N): for j in range(M): sum += arr[j, i]`
> - [ ] B. `for j in range(M): for i in range(N): sum += arr[i, j]`
> - [ ] C. `for i in range(N): for j in range(M): sum += arr[i, j]`
> - [ ] D. 以上都相同
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: C-contiguous 下最后维度（列）变化最快。循环中内层遍历 j（列），外层遍历 i（行），即 `arr[i, j]` 顺序访问，利用缓存行预取，性能最优。

---

### 🛠️ 动手练习题

> [!example] 练习题 1：性能对比实验
> **难度**: ⭐
>
> 生成两个 10,000,000 元素的随机数数组，分别用 Python 循环和 NumPy 向量化进行加法、乘法、平方根操作。使用 `time.perf_counter()` 计时，计算 NumPy 相对于 Python 循环的加速比。将结果以表格形式打印。

> [!example] 练习题 2：基于条件的数据清洗
> **难度**: ⭐⭐
>
> 生成 100 万条模拟传感器数据的 NumPy 数组（带噪声的正弦波 + 随机异常值）。使用 `np.where` 和 `np.select` 完成：
> - 将超过 3σ 的值标记为异常并替换为均值
> - 将值为 NaN 的条目替换为前一个有效值（前向填充）
> - 将负值截断为 0

> [!example] 练习题 3：无循环的距离矩阵
> **难度**: ⭐⭐
>
> 给定两个点集 A (m 个点) 和 B (n 个点)，每个点有 3 个坐标维度。使用**广播**计算所有点对之间的欧氏距离，得到 m×n 距离矩阵。要求：代码中不允许出现 Python 循环。对比使用 `scipy.spatial.distance.cdist` 的结果验证正确性。

> [!example] 练习题 4：内存布局实战
> **难度**: ⭐⭐⭐
>
> 创建一个 4096×4096 的随机浮点矩阵。分别测量：（1）沿行遍历求和，（2）沿列遍历求和，（3）使用 `np.sum()` 的时间。然后使用 `np.asfortranarray()` 转换为 Fortran-contiguous 布局，重复（1）和（2）。解释为什么"快方向"和"慢方向"在两种布局下发生了互换。用 `arr.flags` 和 `arr.strides` 验证布局信息。

> [!example] 练习题 5：用 ufunc 实现 Mandelbrot 集边界检测
> **难度**: ⭐⭐⭐
>
> 使用 NumPy 向量化（不写 Python 循环）生成 Mandelbrot 集。给定复平面上的网格，使用 `np.where` 配合掩码数组迭代计算逃逸时间。统计向量化版本与 `numba.jit` 加速版本的性能差距。
