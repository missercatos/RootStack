# NumPy 数组：与 C 数组的血缘 (NumPy Arrays & C)
---

## 📖 章节概述

量化分析的底层是数值计算，而数值计算的根基是数组。本章从 C 程序员最熟悉的概念出发，剖析 NumPy 数组的内存模型：连续存储、固定 dtype、stride 步长——这些与 C 数组一脉相承。你将理解为什么 `np.array` 比 Python list 快 50 倍，为什么向量化操作能替代 C 式的 for 循环，以及如何通过 ctypes 让 C 代码和 NumPy 共享同一块内存。

> **核心理念**：NumPy 的 `ndarray` 本质上是一个带有 Python 包装的 C 数组。你已经在 C 中掌握了数组的所有核心概念——连续内存、类型大小、指针运算。NumPy 只是给这些概念穿上了一层 Python 外衣。本章的目标是让你透过这层外衣，看到熟悉的 C 语言骨架。

---

### 📚 第一节：内存模型 —— C 数组与 NumPy 数组的共同基因

#### 1.1 C 数组的内存布局

回想在 C 语言中，数组就是一段连续的内存块：

```c
// C 语言中的数组
int arr[5] = {10, 20, 30, 40, 50};

// 内存中的实际布局（假设 int 是 4 字节）：
// 地址:  0x1000  0x1004  0x1008  0x100c  0x1010
// 数值:      10      20      30      40      50
// arr[2] 等价于 *(arr + 2)，即 *(0x1000 + 2*4) = *(0x1008) = 30
```

三个核心属性定义了 C 数组：
- **起始地址**：`arr` 就是指向第一个元素的指针
- **元素类型**：`int`（4 字节）决定每次偏移的长度
- **元素个数**：编译时或运行时确定

#### 1.2 NumPy 数组：同样的三要素

```bash
python -c "
import numpy as np
a = np.array([10, 20, 30, 40, 50], dtype=np.int32)
print('dtype:', a.dtype)         # int32 —— 等于 C 的 int
print('itemsize:', a.itemsize)   # 4 字节/元素
print('nbytes:', a.nbytes)       # 20 字节总大小
print('data ptr:', a.ctypes.data)  # 内存起始地址
print('strides:', a.strides)     # (4,) —— 每个元素间距
"
```

输出：

```
dtype: int32
itemsize: 4
nbytes: 20
data ptr: 139980345180160
strides: (4,)
```

**映射表**：

| C 概念 | NumPy 对应 | 含义 |
|--------|-----------|------|
| `int *ptr` | `a.ctypes.data` | 指向数据的指针 |
| `sizeof(int)` | `a.itemsize` | 单个元素字节数 |
| 数组长度 | `a.shape[0]` | 元素个数 |
| `*(ptr + i)` | `a[i]` | 第 i 个元素 |
| `arr` 地址 | `a.__array_interface__['data'][0]` | 原始内存地址 |

#### 1.3 Python List 的开销：为什么慢 50 倍

```bash
python -c "
import sys, numpy as np
py_list = [1, 2, 3, 4, 5]
np_arr  = np.array([1, 2, 3, 4, 5], dtype=np.int64)

# Python list：每个元素是一个 PyObject* 指针
print('list item size:', sys.getsizeof(py_list[0]))  # 28 字节（Python int 对象）
# list 本身存储的是 8 字节指针数组 → 间接寻址

# NumPy array：连续存储 8 字节整数
print('numpy item size:', np_arr.itemsize)            # 8 字节
# ndarray 直接存储原始数值 → 直接寻址
"
```

Python list 是一个指针数组，每个元素指向堆上分配的 Python int 对象。NumPy 数组直接存储原始二进制数据——就像 C 数组一样。

#### 1.4 Stride（步长）：C 数组没有的武器

C 数组的"步长"永远是 `sizeof(type)` —— 固定不变。但 NumPy 的 stride 可以灵活变化：

```bash
python -c "
import numpy as np

# 1D 数组：stride = 8 字节（float64）
a = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float64)
print('1D strides:', a.strides)  # (8,)

# 2D C-contiguous 数组（行优先，和 C 语言一样）
b = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.int32)
print('2D shape:', b.shape)      # (2, 3)
print('2D strides:', b.strides)  # (12, 4)
# 跨行：3 * 4 = 12 字节；跨列：4 字节
# 这和 C 中 b[i][j] 的内存布局完全一致！
"
```

**C 语言对照**：

```c
// C 中的二维数组（行优先存储）
int b[2][3] = {{1, 2, 3}, {4, 5, 6}};
// 内存：1, 2, 3, 4, 5, 6
// b[i][j] 地址 = &b[0][0] + i * 3 * sizeof(int) + j * sizeof(int)
//              = base + i * 12 + j * 4
// 和 NumPy 的 strides=(12, 4) 完全一致！
```

---

### 📚 第二节：矢量化操作 —— 告别 C 式循环

#### 2.1 C 循环 vs 矢量化

你的第一直觉可能是这样写：

```c
// C 风格：逐元素相加
for (int i = 0; i < n; i++) {
    c[i] = a[i] + b[i];
}
```

在 NumPy 中，你写一行就够了：

```python
c = a + b  # 矢量化操作
```

#### 2.2 性能对比实测

```bash
python -c "
import numpy as np
import time

n = 10_000_000
a = np.random.randn(n).astype(np.float64)
b = np.random.randn(n).astype(np.float64)

# NumPy 矢量化
t0 = time.time()
c = a + b
t1 = time.time()
print(f'NumPy vectorized: {t1 - t0:.4f}s')

# Python 循环（模拟 C 循环）
c2 = np.empty(n, dtype=np.float64)
t0 = time.time()
for i in range(n):
    c2[i] = a[i] + b[i]
t1 = time.time()
print(f'Python loop: {t1 - t0:.4f}s')
print(f'Speedup: {(t1 - t0) / (t1 - t0 if t1 - t0 > 0 else 0.001):.0f}x (vectorized is faster)')
"
```

矢量化操作直接调用 C/Fortran 写的底层 BLAS 实现，完全绕过了 Python 解释器的循环开销。

#### 2.3 Broadcasting：自动广播机制

Broadcasting 是 NumPy 最强大的特性之一——它让不同形状的数组能够进行运算，就像 C 中合法的指针偏移自动匹配：

```bash
python -c "
import numpy as np

# 标量广播
a = np.array([1, 2, 3, 4])
print('a + 10:', a + 10)  # [11 12 13 14] —— 10 广播到每个元素

# 行向量 + 列向量 → 矩阵
row = np.array([[1, 2, 3]])     # shape (1, 3)
col = np.array([[10], [20]])    # shape (2, 1)
print('result shape:', (row + col).shape)  # (2, 3)
print(row + col)
# [[11 12 13]
#  [21 22 23]]
"
```

Broadcasting 规则（从后往前对齐维度）：
1. 如果维度数不同，在较小的 shape 前面补 1
2. 如果某维度相等，或某维度为 1，则可以广播
3. 如果某维度不相等且都不为 1，则报错

---

### 📚 第三节：NumPy 内存实战

#### 3.1 大数组内存占用

```bash
python -c "
import numpy as np

# 100万 float64 元素
a = np.arange(1_000_000, dtype=np.float64)
print(f'{1_000_000} float64 elements: {a.nbytes / 1024 / 1024:.2f} MB')

# 对比：同样数量的 Python int
import sys
py_sum = sum(sys.getsizeof(i) for i in range(1000))
py_per_elem = py_sum / 1000
est_mb = py_per_elem * 1_000_000 / 1024 / 1024
print(f'1M Python ints (estimated): {est_mb:.2f} MB')
print(f'Memory savings: ~{est_mb / (a.nbytes / 1024 / 1024):.0f}x')
"
```

#### 3.2 View（视图）与 Copy（拷贝）

```bash
python -c "
import numpy as np

a = np.arange(12).reshape(3, 4)
print('original:\\n', a)

# 切片返回 view（共享内存）
b = a[0:2, 1:3]  # view
b[0, 0] = 999
print('after modifying view:\\n', a)  # a 也被修改了！

# 强制拷贝
c = a[0:2, 1:3].copy()
c[0, 0] = 777
print('after modifying copy:\\n', a)  # a 不变
"
```

View 就像 C 语言中的指针偏移：不复制数据，只改变如何"看"同一块内存。stride 机制使得 reshape、切片、转置等操作几乎零开销。

#### 3.3 转置的 stride 魔法

```bash
python -c "
import numpy as np

a = np.arange(6).reshape(2, 3)
print('a strides:', a.strides)   # (24, 8)  行优先（C order）
at = a.T
print('a.T strides:', at.strides)  # (8, 24)  列优先（Fortran order）
# 转置没有复制数据！只是交换了 stride
print('a.T base is a:', at.base is a)  # True
"
```

---

### 📚 第四节：C 与 NumPy 共享内存

#### 4.1 ctypes 共享内存

NumPy 数组可以通过 ctypes 接口直接暴露给 C 函数——零拷贝：

```python
import numpy as np
import ctypes

# NumPy 数组
arr = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float64)

# 获取原始指针
ptr = arr.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

# 直接传给 C 函数（此处为示例，假设已编译了 my_c_func.so）
# lib = ctypes.CDLL('./my_c_func.so')
# lib.sum_array(ptr, len(arr))
```

#### 4.2 C 端代码示例

```c
// compute.c
#include <stddef.h>

// C 函数：原地乘以标量
void scale_array(double *arr, size_t n, double factor) {
    for (size_t i = 0; i < n; i++) {
        arr[i] *= factor;
    }
}
```

编译并使用：

```bash
gcc -shared -fPIC -O2 -o libscale.so compute.c
```

```python
import numpy as np
import ctypes

lib = ctypes.CDLL('./libscale.so')
lib.scale_array.argtypes = [
    ctypes.POINTER(ctypes.c_double),
    ctypes.c_size_t,
    ctypes.c_double
]

a = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float64)
lib.scale_array(a.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), len(a), 2.0)
print(a)  # [2. 4. 6. 8.]
```

> 更详细的 C/Python 互操作请参考 [[../2精通/05_ctypes：在Python中调用C库|ctypes]] 和 [[../2精通/07_pybind11与Cython：给C_C++库披上Python外衣|Cython 接口]]。

---

### 📝 小节练习

> [!question] 选择题 1
> NumPy 数组的 `.strides` 属性表示什么？
> - [ ] A. 数组的总字节数
> - [ ] B. 数组的元素数量
> - [ ] C. 沿每个维度前进一个元素所需的字节数
> - [ ] D. 数组的数据类型
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: `strides` 表示在每个维度上移动到下一个元素需要的字节数。对于 C-contiguous 数组，最后一维的 stride = itemsize，前一维的 stride = 后一维的 stride * 后一维的大小。

> [!question] 选择题 2
> C 语言中 `b[i][j]` 的内存地址计算在行优先布局下等价于？
> - [ ] A. `&b[0][0] + i * cols + j`
> - [ ] B. `&b[0][0] + j * rows + i`
> - [ ] C. `&b[0][0] + i + j * rows`
> - [ ] D. 以上都不对
>
> > [!success]- 点击查看答案
> > 正确答案: A
> > **解析**: 行优先存储中，`b[i][j]` 的地址 = base + i * cols * sizeof(type) + j * sizeof(type)。这和 NumPy 中 `strides = (cols * itemsize, itemsize)` 的布局完全一致。

> [!question] 判断题 1
> NumPy 数组的转置操作（.T）会复制底层数据。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 转置只是交换 strides 并调整 shape，不会复制数据。这是 NumPy view 机制的经典应用。检查 `.T.base is arr` 会返回 True。

---

## 📋 章节测试

### 一、判断题

> [!question] 判断题 1
> NumPy 的 `ndarray` 内部使用连续内存块存储数据，和 C 数组一样。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: NumPy 底层的 C 实现使用连续分配的内存块（通过 `malloc` 或类似机制）。这是它能够通过 `ctypes.data` 直接暴露指针的原因。

> [!question] 判断题 2
> NumPy 的 broadcasting 在底层会实际复制数据以对齐形状。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: Broadcasting 不会复制数据——它通过改变迭代方式（stride 为 0 即原地踏步）在逻辑上扩展数组，实现了零拷贝的维度对齐。

> [!question] 判断题 3
> `a[0:2, 1:3]` 返回的切片是对原数组的 view，修改切片会改变原数组。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: 基本索引（切片、整数索引）返回 view。花式索引（用数组/列表做索引）返回 copy。记住：切片 = view = 共享内存。

> [!question] 判断题 4
> Python list 的元素在内存中是连续存储的。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: Python list 底层是连续的指针数组，但每个指针指向堆上独立分配的 Python 对象。所以数据本身不连续——这是间接寻址，不是直接存储。

> [!question] 判断题 5
> NumPy 数组的 `dtype` 在创建后可以随意更改。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 和 C 数组一样，NumPy 数组的类型在创建时就固定了。使用 `astype()` 会创建一个新数组（copy），不会原地修改。

> [!question] 判断题 6
> 通过 `ctypes.data` 获得的指针可以直接传给 C 函数，无需拷贝数据。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `ctypes.data` 返回的是 ndarray 底层数据缓冲区的实际内存地址。将这个地址传给 C 函数，C 代码可以直接读写同一块内存，实现零拷贝交互。

> [!question] 判断题 7
> `np.float64` 占用 8 字节，和 C 语言中的 `double` 完全等价。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: NumPy 的 `float64` 遵循 IEEE 754 双精度浮点标准，和 C 的 `double` 在内存布局上完全一致。`int32` 对应 `int32_t`，`int64` 对应 `int64_t`。使用 `numpy` + `ctypes` 时类型匹配是关键。

---

### 二、选择题

> [!question] 选择题 1
> 以下哪个操作返回原数组的 view（而非 copy）？
> - [ ] A. `a[[0, 1, 2]]`
> - [ ] B. `a[0:5]`
> - [ ] C. `a[a > 0]`
> - [ ] D. `a.flatten()`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 切片 `a[0:5]` 返回 view。`a[[0,1,2]]` 是花式索引返回 copy，`a[a > 0]` 是布尔索引返回 copy，`flatten()` 总是返回 copy。

> [!question] 选择题 2
> 一个 shape 为 (100, 200) 的 int64 数组占用多少内存？
> - [ ] A. 20000 字节
> - [ ] B. 80000 字节
> - [ ] C. 160000 字节
> - [ ] D. 320000 字节
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: 100 * 200 = 20000 个元素，每个 int64 = 8 字节，总计 20000 * 8 = 160000 字节 ≈ 156.25 KB。公式：`nbytes = product(shape) * itemsize`。

> [!question] 选择题 3
> 将一个 shape (3, 4) 的数组 reshape 为 (2, 6)，底层数据复制了吗？
> - [ ] A. 总是复制
> - [ ] B. 不复制（view）
> - [ ] C. 取决于 dtype
> - [ ] D. 取决于能否保持 C-contiguous
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 当元素总数相同且数组是 C-contiguous 时，reshape 返回 view，不复制数据。仅改变 shape 和 strides 元信息。

> [!question] 选择题 4
> 数组 `a = np.array([1, 2, 3])` 执行 `a + np.array([[10], [20]])` 结果的 shape 是？
> - [ ] A. (3,)
> - [ ] B. (2, 3)
> - [ ] C. (3, 2)
> - [ ] D. 报错
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: (3,) 广播为 (1,3)，(2,1) 广播为 (2,3)。结果 shape = (2, 3)。

> [!question] 选择题 5
> 以下代码 `a[::2]` 的 stride 相对于原数组有何变化？
> - [ ] A. stride 变为原来的 2 倍
> - [ ] B. stride 变为原来的 1/2
> - [ ] C. stride 不变
> - [ ] D. 无法确定
>
> > [!success]- 点击查看答案
> > 正确答案: A
> > **解析**: `a[::2]`（每隔一个取一个元素）使 stride 变为原来的 2 倍。如果原 stride 是 8，则新 stride 是 16。这沿用了 C 语言中指针算术的逻辑：`*(ptr + i * 2)`。

> [!question] 选择题 6
> NumPy 数组底层调用的是哪个数学库？
> - [ ] A. 纯 Python 实现
> - [ ] B. BLAS / LAPACK
> - [ ] C. OpenGL
> - [ ] D. 自定义汇编
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: NumPy 的线性代数、向量运算底层调用高度优化的 BLAS 和 LAPACK 库（OpenBLAS、MKL 或 Accelerate）。这些库用手工优化的 C/汇编编写，这就是矢量化操作极快的原因。

---

### 🛠️ 动手练习题

> [!example] 练习题 1：验证内存布局
> **难度**: ⭐
>
> 创建一个 `int32` 类型的 2D NumPy 数组 `a = np.arange(12).reshape(3, 4)`。用 `print(a.ctypes.data, a.strides, a.shape, a.itemsize)` 观察其属性。然后用 C 代码手动计算 `a[2][3]` 的内存地址，和 Python 中 `a.ctypes.data + 2*strides[0] + 3*strides[1]` 对比。

> [!example] 练习题 2：C 与 NumPy 共享内存实战
> **难度**: ⭐⭐
>
> 编写一个 C 函数 `double sum_squares(double *arr, size_t n)`，计算数组元素的平方和。编译为 `.so` 文件。在 Python 中用 `ctypes` 加载，创建一个 NumPy 数组，将数据指针传给 C 函数，比较 C 计算的结果和 `np.sum(a**2)` 的结果。

> [!example] 练习题 3：Broadcasting 深度理解
> **难度**: ⭐⭐
>
> 给定三个数组：`a.shape = (1, 5)`，`b.shape = (4, 1)`，`c.shape = (4, 1)`。计算 `a + b * c`，写出结果 shape 和 broadcasting 的逐步推导过程。用代码验证。

> [!example] 练习题 4：Stride 与性能实验
> **难度**: ⭐⭐⭐
>
> 创建一个 `(10000, 10000)` 的 float64 数组。分别按行遍历和按列遍历求和，记录时间。解释为什么按列遍历更慢（提示：CPU 缓存行和 stride 的关系）。这个实验直接展示了 C 语言中"行优先遍历快于列优先遍历"的原理在 NumPy 中同样成立。
