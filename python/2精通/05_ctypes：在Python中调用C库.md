# ctypes：在 Python 中调用 C 库 (Calling C from Python)
---

## 章节概述

ctypes 是 Python 标准库自带的 C 互操作利器——无需编译器、无需额外依赖，直接加载 .so/.dll 共享库并调用其中的 C 函数。本章从加载 C 标准库的 `sin()` 开始，逐步深入参数类型映射、结构体传递、回调函数，以及完整项目的实战演示。

> **核心理念**：ctypes 让你在 Python REPL 中临时调用任何 C 库——就像 `python -c "from ctypes import *; ..."` 一行流那样简单。它是 Python 作为"C 程序的调试器和胶水层"的最佳工具。

---

### 第一节：加载共享库

#### 1.1 第一个 ctypes 调用：libm 的 sin()

```bash
python -c "
from ctypes import *

# 加载 C 数学库（Linux 上为 libm.so.6）
libm = CDLL('libm.so.6')

> **跨平台提示**：
> - **Windows**：动态库为 `.dll`，数学库在 `msvcrt`，加载方式：`libm = cdll.msvcrt`
> - **macOS**：动态库为 `.dylib`，数学库为 `libm.dylib`，加载方式：`libm = CDLL('libm.dylib')`
> - 通用方式：`from ctypes.util import find_library; CDLL(find_library('m'))`

# 调用 sin(1.0)
result = libm.sin(1.0)
print(f'sin(1.0) = {result}') # 可能输出垃圾值！
# 必须指定参数类型和返回类型！
"
```

第一次调用可能输出奇怪的值——因为 ctypes 默认假设所有参数和返回值都是 `c_int`（32 位整数）。必须显式声明类型签名：

```python
from ctypes import *

libm = CDLL('libm.so.6')

# 声明函数签名
libm.sin.argtypes = [c_double] # 参数：一个 double
libm.sin.restype = c_double # 返回值：double

result = libm.sin(1.0)
print(f'sin(1.0) = {result}') # 0.8414709848078965 

# 对比 C 语言：
# #include <math.h>
# double result = sin(1.0); // 需要 #include 和编译链接
```

> **C 对比**：C 中调用 `sin()` 需要 `#include <math.h>` 并在编译时链接 `-lm`。ctypes 在运行时加载库并调用符号——无需头文件、无需编译，适合快速原型验证。

#### 1.2 不同平台的库加载

```python
from ctypes import *
import platform

# Linux
# libc = CDLL('libc.so.6')

# 跨平台方式
if platform.system() == 'Linux':
 libc = CDLL('libc.so.6')
elif platform.system() == 'Darwin':
 libc = CDLL('libc.dylib')
elif platform.system() == 'Windows':
 libc = cdll.msvcrt

# 或者使用 find_library
from ctypes.util import find_library
lib_path = find_library('c') # 自动查找 libc 的路径
libc = CDLL(lib_path)

# 调用 printf
libc.printf.argtypes = [c_char_p]
libc.printf.restype = c_int
libc.printf(b'Hello from ctypes!\n') # 必须传 bytes，不是 str
```

### 小节练习


> [!question] 判断题 1
> ctypes 使用 C 共享库时不需要经过 C 编译器。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: ctypes 是纯 Python 实现，直接通过 `dlopen`/`LoadLibrary` 加载已编译的共享库（.so/.dll），不需要编译步骤。这一点与 Cython/pybind11 不同。

---

### 第二节：类型映射

ctypes 提供了 Python 和 C 之间的类型桥梁：

#### 2.1 基本类型对应表

| ctypes 类型 | C 类型 | Python 类型 | 说明 |
|-------------|--------|-------------|------|
| `c_char` | `char` | `bytes`(1 字节) / `int` | 单字节 |
| `c_byte` | `signed char` | `int` | |
| `c_ubyte` | `unsigned char` | `int` | |
| `c_short` | `short` | `int` | |
| `c_ushort` | `unsigned short` | `int` | |
| `c_int` | `int` | `int` | 32 位 |
| `c_uint` | `unsigned int` | `int` | |
| `c_long` | `long` | `int` | 32 或 64 位 |
| `c_longlong` | `long long` | `int` | 64 位 |
| `c_float` | `float` | `float` | 32 位 IEEE |
| `c_double` | `double` | `float` | 64 位 IEEE |
| `c_char_p` | `char *` | `bytes`/`None` | C 字符串 |
| `c_void_p` | `void *` | `int`/`None` | 通用指针 |
| `c_size_t` | `size_t` | `int` | 无符号整型 |
| `c_bool` | `bool` | `bool` | C99 _Bool |

#### 2.2 类型转换示例

```python
from ctypes import *

# 创建 C 类型值
a = c_int(42)
b = c_double(3.14)
c = c_char_p(b"hello")
d = c_void_p() # NULL 指针

print(a.value) # 42 — 提取 Python 值
print(b.value) # 3.14
print(c.value) # b'hello'

# 修改 C 类型值
a.value = 100
print(a) # c_int(100)

# Python str 不能直接传给 c_char_p！
libc = CDLL('libc.so.6')
libc.printf.argtypes = [c_char_p]
libc.printf(b'Hello\n') # 正确：传 bytes
# libc.printf('Hello\n') # 错误：传 str 在部分平台会导致段错误
```

#### 2.3 指针操作

```python
from ctypes import *

x = c_int(42)

# 获取 x 的地址
ptr = pointer(x) # 返回 POINTER(c_int)，等价于 C 的 &x
print(ptr.contents) # c_int(42) — 解引用，等价于 *ptr
print(ptr[0]) # 42 — 数组风格解引用

# byref — 临时指针（仅用于函数调用参数）
libc = CDLL('libc.so.6')

def modify(p_val):
 """C 函数接口：void modify(int *val)"""
 p_val[0] = 999 # 通过指针修改原值

arr = c_int(42)
modify(byref(arr)) # 传递 arr 的地址
print(arr.value) # 999
```

> `byref()` vs `pointer()`：`byref()` 创建轻量的临时指针（不增加引用计数），仅用于函数调用的参数传递。`pointer()` 创建持久的指针对象，可以被多次使用。

### 小节练习


---

### 第三节：结构体与数组

#### 3.1 定义和传递结构体

```python
from ctypes import *

# C 定义:
# struct Point { double x; double y; };
class Point(Structure):
 _fields_ = [
 ('x', c_double),
 ('y', c_double),
 ]

# C 定义:
# struct Rect { struct Point top_left; struct Point bottom_right; };
class Rect(Structure):
 _fields_ = [
 ('top_left', Point),
 ('bottom_right', Point),
 ]

# 使用
p = Point(1.0, 2.0)
print(p.x, p.y) # 1.0 2.0

r = Rect(Point(0, 0), Point(10, 10))
print(r.top_left.x) # 0.0

# 传递给 C 函数
libmylib = CDLL('./libgeo.so')
libmylib.area.argtypes = [Rect]
libmylib.area.restype = c_double
area = libmylib.area(r)
```

#### 3.2 数组

```python
from ctypes import *

# 方式一：Python 列表转 C 数组
IntArray5 = c_int * 5 # 定义类型：5 个 c_int 的数组
arr = IntArray5(1, 2, 3, 4, 5) # 等价于 C 代码: int arr[5] = {1,2,3,4,5};

print(arr[0]) # 1
print(arr[4]) # 5
arr[0] = 99
print(arr[0]) # 99

# 方式二：从现有指针创建
data = (c_int * 5)(1, 2, 3, 4, 5)

# 方式三：create_string_buffer
buf = create_string_buffer(100) # char buf[100]
buf.value = b'hello'
print(buf.value) # b'hello'
print(buf.raw[:10]) # b'hello\x00...'

# 传递数组给 C 函数
# void process(int *arr, int len);
libc = CDLL('libc.so.6')
# arr 会自动退化为指针（类似 C 的数组退化）
```

#### 3.3 与 C 完整交互示例

```c
// libgeo.c — 几何计算库
// 编译: gcc -shared -fPIC -o libgeo.so libgeo.c

typedef struct { double x; double y; } Point;

double distance(Point *a, Point *b) {
 double dx = a->x - b->x;
 double dy = a->y - b->y;
 // 调用 libm 的 sqrt
 extern double sqrt(double);
 return sqrt(dx*dx + dy*dy);
}

double array_sum(double *arr, int len) {
 double total = 0;
 for (int i = 0; i < len; i++)
 total += arr[i];
 return total;
}
```

```bash
# 编译 C 库
gcc -shared -fPIC -o libgeo.so libgeo.c -lm
```

```python
# geo.py — Python 调用端
from ctypes import *

class Point(Structure):
 _fields_ = [('x', c_double), ('y', c_double)]

libgeo = CDLL('./libgeo.so')

libgeo.distance.argtypes = [POINTER(Point), POINTER(Point)]
libgeo.distance.restype = c_double

libgeo.array_sum.argtypes = [POINTER(c_double), c_int]
libgeo.array_sum.restype = c_double

# 调用 distance
p1 = Point(0.0, 0.0)
p2 = Point(3.0, 4.0)
dist = libgeo.distance(byref(p1), byref(p2))
print(f'距离: {dist}') # 5.0

# 调用 array_sum
data = (c_double * 5)(1.1, 2.2, 3.3, 4.4, 5.5)
total = libgeo.array_sum(data, 5)
print(f'数组和: {total}') # 16.5
```

### 小节练习


> [!question] 判断题 1
> ctypes 的结构体在传递给 C 函数时，行为与 C 语言中的结构体传递完全一致。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: ctypes 默认**按值传递**结构体，会复制整个结构体。如果需要按指针传递（类似 C 的 `struct Point *`），需要用 `byref()` 或 `pointer()`。务必确保 `argtypes` 中的声明与 C 函数签名匹配。

---

### 第四节：回调函数

#### 4.1 CFUNCTYPE

```python
from ctypes import *

# 定义回调函数类型：int (*callback)(int, int)
CALLBACK = CFUNCTYPE(c_int, c_int, c_int)

# Python 实现
def py_add(a, b):
 return a + b

# 包装为 C 函数指针
c_callback = CALLBACK(py_add)

# 现在可以传给 C 函数
# void register_callback(int (*cb)(int, int));
libmylib.register_callback(c_callback)

# 直接调用
result = c_callback(10, 20)
print(result) # 30
```

> **重要**：`CFUNCTYPE` 创建的回调对象必须保持存活（被 Python 引用）直到 C 端不再使用它。如果回调对象被垃圾回收，C 端调用时会发生段错误。

#### 4.2 qsort 示例

```python
from ctypes import *

libc = CDLL('libc.so.6')

# C 的 qsort 签名：
# void qsort(void *base, size_t nmemb, size_t size,
# int (*compar)(const void *, const void *));

CMPFUNC = CFUNCTYPE(c_int, POINTER(c_int), POINTER(c_int))

def py_cmp(a, b):
 """比较两个 int"""
 return a.contents.value - b.contents.value

# 创建数组
arr = (c_int * 5)(5, 2, 8, 1, 9)
print([arr[i] for i in range(5)]) # [5, 2, 8, 1, 9]

# 调用 qsort
libc.qsort(arr, len(arr), sizeof(c_int), CMPFUNC(py_cmp))
print([arr[i] for i in range(5)]) # [1, 2, 5, 8, 9]
```

### 小节练习


---

### 第五节：错误处理与高级用法

#### 5.1 errno 处理

```python
from ctypes import *

libc = CDLL('libc.so.6', use_errno=True)

# 调用 open（不存在的文件）
libc.open.argtypes = [c_char_p, c_int]
libc.open.restype = c_int

fd = libc.open(b'/nonexistent', 0)
if fd == -1:
 err = get_errno()
 print(f'错误码: {err}')
 # 可以调用 strerror 获取错误消息
 libc.strerror.restype = c_char_p
 print(f'错误消息: {libc.strerror(err).decode()}')
```

#### 5.2 resize 动态数组

```python
from ctypes import *

# 初始小数组
arr = (c_int * 3)(1, 2, 3)

# 动态"扩容" — 使用 resize
resize(arr, sizeof(c_int) * 5)
arr[3] = 4
arr[4] = 5
print([arr[i] for i in range(5)]) # [1, 2, 3, 4, 5]
```

#### 5.3 memmove / memcpy

```python
from ctypes import *

src = (c_char * 12)(*b'hello world!')
dst = (c_char * 12)()

libc = CDLL('libc.so.6')
libc.memmove(dst, src, 5)
print(dst.raw[:5]) # b'hello'
```

### 小节练习


---

## 章节测试

### 一、判断题

> [!question] 判断题 1
> ctypes 使用 C 共享库必须经过编译链接步骤。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: ctypes 在运行时动态加载已编译的共享库（.so/.dll），无需编译。它是纯 Python 实现，直接使用操作系统的动态加载机制（dlopen/LoadLibrary）。

> [!question] 判断题 2
> ctypes 的 `c_int(0)` 等价于 C 语言的 `int x = 0;`。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `c_int(0)` 在 Python 中创建一个代表 C `int` 值的对象，其内存布局和大小与 C 的 `int` 一致，可以安全地传递给 C 函数。

> [!question] 判断题 3
> ctypes 的回调函数对象在被 Python 垃圾回收后，C 端仍可安全调用。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 回调对象的生命周期必须覆盖 C 端使用它的整个区间。一旦被 Python GC 回收，C 端调用该函数指针会导致段错误或未定义行为。

> [!question] 判断题 4
> `byref()` 创建的指针可以安全地保存在全局变量中以后使用。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `byref()` 只返回一个临时的 C 指针对象，仅在函数调用期间有效。如果需要在函数调用之外保存指针，必须使用 `pointer()`。

> [!question] 判断题 5
> ctypes 可以调用 C++ 库中没有 `extern "C"` 修饰的函数。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: ctypes 依赖 C ABI 的符号名。C++ 函数有 name mangling，除非使用 `extern "C"` 或知道 mangled 名称（并处理 C++ ABI 差异），否则无法直接调用。

---


---

## 力扣练习

以下题目用于验证本章所学内容：

| 题号 | 题目 | 链接 | 涉及知识点 |
|------|------|------|-----------|
| — | 本章无对应力扣题 | — | 请用动手练习题自检 |



### 动手练习题

> [!example] 练习题 1：调用 C 标准库
> **难度**: 简单
>
> 使用 ctypes 调用以下 libc 函数并验证结果：
> - `strlen` — 计算字符串长度
> - `memcmp` — 比较内存区域
> - `qsort` — 排序数组（带回调函数）
> - `rand` / `srand` — 随机数生成
>
> 每个函数注意正确设置 `argtypes` 和 `restype`。

> [!example] 练习题 2：封装自定义 C 库
> **难度**: 简单
>
> 1. 编写一个 C 共享库 `libstats.so`，实现：
> - `double mean(double *data, int len)` — 计算均值
> - `double stdev(double *data, int len)` — 计算标准差
> - `void sort(double *data, int len)` — 原地排序
> 2. 用 ctypes 加载并封装为一个 Python 类 `StatsAnalyzer`
> 3. 用 NumPy 的随机数组测试性能 vs 纯 Python 实现

> [!example] 练习题 3：回调与事件系统
> **难度**: 简单
>
> 1. 编写一个 C 库，提供事件注册机制：
> - `void on_event(int event_type, void (*callback)(int))`
> - `void trigger_event(int event_type)` — 调用所有注册的回调
> 2. 在 Python 端注册回调（打印日志、统计事件次数）
> 3. 验证 Python 回调被正确调用，且多次触发结果正确

> [!example] 练习题 4：性能对比实验
> **难度**: 简单
>
> 对比以下三种方式计算 100 万个数的平方和的耗时：
> 1. 纯 Python `sum(x*x for x in data)`
> 2. Python 内置 `sum()` + 列表推导式
> 3. ctypes 调用 C 函数 `double sum_squares(double *data, int len)`
>
> 分析性能差异的来源（类型转换、调用开销、GIL），并讨论什么场景下 ctypes 能真正加速程序。
