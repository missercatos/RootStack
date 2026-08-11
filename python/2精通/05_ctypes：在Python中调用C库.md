# ctypes：在 Python 中调用 C 库 (Calling C from Python)
---

## 📖 章节概述

ctypes 是 Python 标准库自带的 C 互操作利器——无需编译器、无需额外依赖，直接加载 .so/.dll 共享库并调用其中的 C 函数。本章从加载 C 标准库的 `sin()` 开始，逐步深入参数类型映射、结构体传递、回调函数，以及完整项目的实战演示。

> **核心理念**：ctypes 让你在 Python REPL 中临时调用任何 C 库——就像 `python -c "from ctypes import *; ..."` 一行流那样简单。它是 Python 作为"C 程序的调试器和胶水层"的最佳工具。

---

### 📚 第一节：加载共享库

#### 1.1 第一个 ctypes 调用：libm 的 sin()

```bash
python -c "
from ctypes import *

# 加载 C 数学库（Linux 上为 libm.so.6）
libm = CDLL('libm.so.6')

# 调用 sin(1.0)
result = libm.sin(1.0)
print(f'sin(1.0) = {result}')     # 可能输出垃圾值！
# 必须指定参数类型和返回类型！
"
```

第一次调用可能输出奇怪的值——因为 ctypes 默认假设所有参数和返回值都是 `c_int`（32 位整数）。必须显式声明类型签名：

```python
from ctypes import *

libm = CDLL('libm.so.6')

# 声明函数签名
libm.sin.argtypes = [c_double]    # 参数：一个 double
libm.sin.restype = c_double       # 返回值：double

result = libm.sin(1.0)
print(f'sin(1.0) = {result}')     # 0.8414709848078965 ✓

# 对比 C 语言：
# #include <math.h>
# double result = sin(1.0);       // 需要 #include 和编译链接
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
lib_path = find_library('c')       # 自动查找 libc 的路径
libc = CDLL(lib_path)

# 调用 printf
libc.printf.argtypes = [c_char_p]
libc.printf.restype = c_int
libc.printf(b'Hello from ctypes!\n')  # 必须传 bytes，不是 str
```

### 📝 小节练习

> [!question] 选择题 1
> ctypes 加载共享库时使用哪个类？
> - [ ] A. `CFUNCTYPE`
> - [ ] B. `CDLL`
> - [ ] C. `LibraryLoader`
> - [ ] D. `SharedObject`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `CDLL`（或 `cdll`）用于加载 C 共享库。Windows 上也可用 `WinDLL`（stdcall 调用约定）。`CFUNCTYPE` 用于定义回调函数类型。

> [!question] 判断题 1
> ctypes 使用 C 共享库时不需要经过 C 编译器。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: ctypes 是纯 Python 实现，直接通过 `dlopen`/`LoadLibrary` 加载已编译的共享库（.so/.dll），不需要编译步骤。这一点与 Cython/pybind11 不同。

---

### 📚 第二节：类型映射

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
d = c_void_p()              # NULL 指针

print(a.value)              # 42 — 提取 Python 值
print(b.value)              # 3.14
print(c.value)              # b'hello'

# 修改 C 类型值
a.value = 100
print(a)                    # c_int(100)

# Python str 不能直接传给 c_char_p！
libc = CDLL('libc.so.6')
libc.printf.argtypes = [c_char_p]
libc.printf(b'Hello\n')     # 正确：传 bytes
# libc.printf('Hello\n')    # 错误：传 str 在部分平台会导致段错误
```

#### 2.3 指针操作

```python
from ctypes import *

x = c_int(42)

# 获取 x 的地址
ptr = pointer(x)            # 返回 POINTER(c_int)，等价于 C 的 &x
print(ptr.contents)         # c_int(42) — 解引用，等价于 *ptr
print(ptr[0])               # 42 — 数组风格解引用

# byref — 临时指针（仅用于函数调用参数）
libc = CDLL('libc.so.6')

def modify(p_val):
    """C 函数接口：void modify(int *val)"""
    p_val[0] = 999          # 通过指针修改原值

arr = c_int(42)
modify(byref(arr))           # 传递 arr 的地址
print(arr.value)             # 999
```

> `byref()` vs `pointer()`：`byref()` 创建轻量的临时指针（不增加引用计数），仅用于函数调用的参数传递。`pointer()` 创建持久的指针对象，可以被多次使用。

### 📝 小节练习

> [!question] 选择题 1
> Python 中想将 `"hello"` 字符串传给 C 的 `char *` 参数，应该用？
> - [ ] A. 直接传 `"hello"`
> - [ ] B. `b"hello"`
> - [ ] C. `c_str("hello")`
> - [ ] D. `"hello".encode('utf-16')`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: C 的 `char *` 对应于 Python 的 `bytes`。必须使用 `b"hello"` 或 `"hello".encode()` 编码为字节序列。

> [!question] 选择题 2
> `byref(obj)` 和 `pointer(obj)` 的主要区别是？
> - [ ] A. 完全相同
> - [ ] B. `byref` 返回临时轻量指针（仅用于函数调用），`pointer` 返回持久指针对象
> - [ ] C. `pointer` 更快
> - [ ] D. `byref` 是 `pointer` 的别名
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `byref()` 创建 C 栈上的临时指针（类似 `&x`），仅在函数调用期间有效，性能更好。`pointer()` 创建 Python 层面的 `POINTER(type)` 对象，可长期持有。

---

### 📚 第三节：结构体与数组

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
print(p.x, p.y)              # 1.0 2.0

r = Rect(Point(0, 0), Point(10, 10))
print(r.top_left.x)           # 0.0

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
IntArray5 = c_int * 5          # 定义类型：5 个 c_int 的数组
arr = IntArray5(1, 2, 3, 4, 5) # 等价于 C 代码: int arr[5] = {1,2,3,4,5};

print(arr[0])                  # 1
print(arr[4])                  # 5
arr[0] = 99
print(arr[0])                  # 99

# 方式二：从现有指针创建
data = (c_int * 5)(1, 2, 3, 4, 5)

# 方式三：create_string_buffer
buf = create_string_buffer(100)        # char buf[100]
buf.value = b'hello'
print(buf.value)                       # b'hello'
print(buf.raw[:10])                    # b'hello\x00...'

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
print(f'距离: {dist}')  # 5.0

# 调用 array_sum
data = (c_double * 5)(1.1, 2.2, 3.3, 4.4, 5.5)
total = libgeo.array_sum(data, 5)
print(f'数组和: {total}')  # 16.5
```

### 📝 小节练习

> [!question] 选择题 1
> 要将 Python 列表 `[1, 2, 3]` 作为 C 的 `int *` 参数传递，正确的做法是？
> - [ ] A. 直接传 `[1, 2, 3]`
> - [ ] B. `(c_int * 3)(1, 2, 3)`
> - [ ] C. `pointer([1, 2, 3])`
> - [ ] D. `list_to_c([1, 2, 3])`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 需要先创建 ctypes 数组 `(c_int * 3)(1, 2, 3)`，然后传递给接受 `int *` 的函数。Python list 不能直接传给 C 函数。

> [!question] 判断题 1
> ctypes 的结构体在传递给 C 函数时，行为与 C 语言中的结构体传递完全一致。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: ctypes 默认**按值传递**结构体，会复制整个结构体。如果需要按指针传递（类似 C 的 `struct Point *`），需要用 `byref()` 或 `pointer()`。务必确保 `argtypes` 中的声明与 C 函数签名匹配。

---

### 📚 第四节：回调函数

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
print(result)  # 30
```

> **重要**：`CFUNCTYPE` 创建的回调对象必须保持存活（被 Python 引用）直到 C 端不再使用它。如果回调对象被垃圾回收，C 端调用时会发生段错误。

#### 4.2 qsort 示例

```python
from ctypes import *

libc = CDLL('libc.so.6')

# C 的 qsort 签名：
# void qsort(void *base, size_t nmemb, size_t size,
#            int (*compar)(const void *, const void *));

CMPFUNC = CFUNCTYPE(c_int, POINTER(c_int), POINTER(c_int))

def py_cmp(a, b):
    """比较两个 int"""
    return a.contents.value - b.contents.value

# 创建数组
arr = (c_int * 5)(5, 2, 8, 1, 9)
print([arr[i] for i in range(5)])      # [5, 2, 8, 1, 9]

# 调用 qsort
libc.qsort(arr, len(arr), sizeof(c_int), CMPFUNC(py_cmp))
print([arr[i] for i in range(5)])      # [1, 2, 5, 8, 9]
```

### 📝 小节练习

> [!question] 选择题 1
> ctypes 定义 C 函数指针类型使用哪个工厂函数？
> - [ ] A. `CFUNCTYPE(restype, *argtypes)`
> - [ ] B. `FUNCPTR(restype, *argtypes)`
> - [ ] C. `callback(restype, *argtypes)`
> - [ ] D. `c_function(restype, *argtypes)`
>
> > [!success]- 点击查看答案
> > 正确答案: A
> > **解析**: `CFUNCTYPE(restype, *argtypes)` 返回一个 C 函数指针类型，用于包装 Python 函数为 C 回调。

---

### 📚 第五节：错误处理与高级用法

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
print([arr[i] for i in range(5)])  # [1, 2, 3, 4, 5]
```

#### 5.3 memmove / memcpy

```python
from ctypes import *

src = (c_char * 12)(*b'hello world!')
dst = (c_char * 12)()

libc = CDLL('libc.so.6')
libc.memmove(dst, src, 5)
print(dst.raw[:5])  # b'hello'
```

### 📝 小节练习

> [!question] 选择题 1
> 调用 `CDLL` 加载的 C 函数出错时，获取 errno 的正确方法是？
> - [ ] A. 直接读 `errno` 全局变量
> - [ ] B. 使用 `CDLL('libc.so.6', use_errno=True)` 后调用 `get_errno()`
> - [ ] C. 检查函数的返回值字符串
> - [ ] D. errno 在 ctypes 中不可用
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 需要加载库时设置 `use_errno=True`，然后在调用后使用 `ctypes.get_errno()` 读取 errno 的线程安全副本。

---

## 📋 章节测试

### 一、判断题

> [!question] 判断题 1
> ctypes 使用 C 共享库必须经过编译链接步骤。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: ctypes 在运行时动态加载已编译的共享库（.so/.dll），无需编译。它是纯 Python 实现，直接使用操作系统的动态加载机制（dlopen/LoadLibrary）。

> [!question] 判断题 2
> ctypes 的 `c_int(0)` 等价于 C 语言的 `int x = 0;`。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `c_int(0)` 在 Python 中创建一个代表 C `int` 值的对象，其内存布局和大小与 C 的 `int` 一致，可以安全地传递给 C 函数。

> [!question] 判断题 3
> ctypes 的回调函数对象在被 Python 垃圾回收后，C 端仍可安全调用。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 回调对象的生命周期必须覆盖 C 端使用它的整个区间。一旦被 Python GC 回收，C 端调用该函数指针会导致段错误或未定义行为。

> [!question] 判断题 4
> `byref()` 创建的指针可以安全地保存在全局变量中以后使用。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `byref()` 只返回一个临时的 C 指针对象，仅在函数调用期间有效。如果需要在函数调用之外保存指针，必须使用 `pointer()`。

> [!question] 判断题 5
> ctypes 可以调用 C++ 库中没有 `extern "C"` 修饰的函数。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: ctypes 依赖 C ABI 的符号名。C++ 函数有 name mangling，除非使用 `extern "C"` 或知道 mangled 名称（并处理 C++ ABI 差异），否则无法直接调用。

---

### 二、选择题

> [!question] 选择题 1
> ctypes 中表示 C 的 `double` 类型用？
> - [ ] A. `c_float`
> - [ ] B. `c_double`
> - [ ] C. `c_float64`
> - [ ] D. `c_decimal`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `c_double` 对应 C 的 `double`（64位）。`c_float` 对应 C 的 `float`（32位）。

> [!question] 选择题 2
> `libm.sin.argtypes = [c_double]` 的作用是？
> - [ ] A. 声明参数名称
> - [ ] B. 声明参数类型，确保 Python 值正确转换为 C 类型
> - [ ] C. 验证参数数量
> - [ ] D. 优化函数调用速度
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `argtypes` 告诉 ctypes 如何进行 Python → C 的类型转换。不设置时默认所有参数都是 `c_int`，可能导致值错误或段错误。

> [!question] 选择题 3
> `create_string_buffer(256)` 创建的缓冲区等价于 C 中的？
> - [ ] A. `char *buf = malloc(256)`
> - [ ] B. `char buf[256]`
> - [ ] C. `std::string buf`
> - [ ] D. `char *buf = NULL`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `create_string_buffer(n)` 分配一个可变的 C 字符数组，类似于 `char buf[n]`。它的内容可读写，且作为参数时会自动转为 `char *`。

> [!question] 选择题 4
> 以下哪个不是 ctypes 能找到库的合法方式？
> - [ ] A. `CDLL('libm.so.6')`  — 完整文件名
> - [ ] B. `CDLL('./mylib.so')` — 相对路径
> - [ ] C. `CDLL('mylib')`      — 仅库名（依赖系统搜索）
> - [ ] D. `CDLL('mylib.a')`    — 静态库
>
> > [!success]- 点击查看答案
> > 正确答案: D
> > **解析**: ctypes 使用操作系统的动态加载器（dlopen），只能加载动态共享库（.so / .dll），不能直接加载静态库（.a / .lib）。静态库需要在编译时链接。

> [!question] 选择题 5
> `POINTER(c_int)` 对应 C 的什么类型？
> - [ ] A. `int`
> - [ ] B. `int *`
> - [ ] C. `int **`
> - [ ] D. `int []`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `POINTER(c_int)` 表示 `int*`（指向 int 的指针）。`POINTER(POINTER(c_int))` 才是 `int**`。

> [!question] 选择题 6
> 以下关于 ctypes 性能的说法错误的是？
> - [ ] A. ctypes 调用 C 函数比纯 Python 实现通常更快
> - [ ] B. ctypes 的类型转换有一定运行时开销
> - [ ] C. ctypes 的性能与 C 编译器内联优化后的代码一样快
> - [ ] D. 对于小函数，ctypes 的调用开销可能超过 C 函数本身的执行时间
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: ctypes 调用 C 函数有开销（Python→C 类型转换、参数校验、GIL 持有等），不是零开销调用。对于非常小的函数（如简单加法），调用开销可能超过函数本身。

> [!question] 选择题 7
> ctypesgen 工具的主要用途是？
> - [ ] A. 将 C 库的 .h 头文件自动转换为 ctypes 的 Python 绑定代码
> - [ ] B. 编译 C 代码为共享库
> - [ ] C. 加速 ctypes 运行速度
> - [ ] D. 将 Python 代码编译为 C
>
> > [!success]- 点击查看答案
> > 正确答案: A
> > **解析**: ctypesgen 是一个独立的工具，解析 C 头文件并自动生成对应的 Python ctypes 绑定代码，省去手动定义结构体和函数签名的繁琐工作。

---

### 🛠️ 动手练习题

> [!example] 练习题 1：调用 C 标准库
> **难度**: ⭐
>
> 使用 ctypes 调用以下 libc 函数并验证结果：
> - `strlen` — 计算字符串长度
> - `memcmp` — 比较内存区域
> - `qsort` — 排序数组（带回调函数）
> - `rand` / `srand` — 随机数生成
>
> 每个函数注意正确设置 `argtypes` 和 `restype`。

> [!example] 练习题 2：封装自定义 C 库
> **难度**: ⭐⭐
>
> 1. 编写一个 C 共享库 `libstats.so`，实现：
>    - `double mean(double *data, int len)` — 计算均值
>    - `double stdev(double *data, int len)` — 计算标准差
>    - `void sort(double *data, int len)` — 原地排序
> 2. 用 ctypes 加载并封装为一个 Python 类 `StatsAnalyzer`
> 3. 用 NumPy 的随机数组测试性能 vs 纯 Python 实现

> [!example] 练习题 3：回调与事件系统
> **难度**: ⭐⭐
>
> 1. 编写一个 C 库，提供事件注册机制：
>    - `void on_event(int event_type, void (*callback)(int))`
>    - `void trigger_event(int event_type)` — 调用所有注册的回调
> 2. 在 Python 端注册回调（打印日志、统计事件次数）
> 3. 验证 Python 回调被正确调用，且多次触发结果正确

> [!example] 练习题 4：性能对比实验
> **难度**: ⭐⭐
>
> 对比以下三种方式计算 100 万个数的平方和的耗时：
> 1. 纯 Python `sum(x*x for x in data)`
> 2. Python 内置 `sum()` + 列表推导式
> 3. ctypes 调用 C 函数 `double sum_squares(double *data, int len)`
>
> 分析性能差异的来源（类型转换、调用开销、GIL），并讨论什么场景下 ctypes 能真正加速程序。
