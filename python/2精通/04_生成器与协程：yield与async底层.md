# 生成器与协程：yield 与 async 底层 (Generators & Coroutines)
---

## 📖 章节概述

`yield` 是 Python 最具魔力的关键字之一——它让函数"暂停"并在下次调用时从暂停点继续。本章从 C 的状态机模式出发，深入剖析 Python 生成器的内部实现（帧状态保存），再延伸到 `yield from`、`async/await` 和事件循环。理解生成器的底层机制，是理解 Python 协程和异步编程的基础。

> **核心理念**：Python 的 `yield` 在 C 层面等价于"保存栈帧的指令指针和局部变量，然后 `return`"。每次 `next()` 恢复该栈帧继续执行。C 语言没有这种能力——你只能手动编写状态机来模拟。

---

### 📚 第一节：yield 是什么

#### 1.1 最简单的生成器

```python
def simple_gen():
    print("生成器开始")
    yield 1
    print("已产出 1")
    yield 2
    print("已产出 2")
    yield 3
    print("生成器结束")

g = simple_gen()
print(type(g))           # <class 'generator'>
print(next(g))           # 打印: 生成器开始 → 返回 1
print(next(g))           # 打印: 已产出 1 → 返回 2
print(next(g))           # 打印: 已产出 2 → 返回 3
# print(next(g))         # StopIteration 异常！
```

执行流程可视化：

```
next(g)  #1       next(g)  #2       next(g)  #3
   │                 │                 │
   ▼                 ▼                 ▼
┌─────────┐     ┌─────────┐     ┌─────────┐
│  print   │     │  print   │     │  print   │
│  yield 1 │────▶│  yield 2 │────▶│  yield 3 │────▶ StopIteration
└─────────┘     └─────────┘     └─────────┘
  "暂停"           "暂停"           "暂停"       "结束"
```

> **关键概念**：`yield` 让函数返回一个值，但函数的状态（局部变量、指令指针）被完整保存。下次 `next(g)` 时，从 `yield` 的下一行继续执行——就像函数"暂停"了。

#### 1.2 C 中没有 yield —— 必须用状态机

```c
// C 语言：用状态机模拟生成器
// 需求：每次调用返回下一个斐波那契数
#include <stdio.h>

typedef struct {
    int state;   // 当前状态：0=初始，1=第一次产出，2=后续
    int prev;
    int curr;
    int count;
} FibGenerator;

void fib_init(FibGenerator *g, int n) {
    g->state = 0;
    g->count = n;
}

int fib_next(FibGenerator *g) {
    switch (g->state) {
        case 0:  // 第一次调用
            g->state = 1;
            g->prev = 0;
            g->curr = 1;
            if (g->count-- <= 0) return -1;
            return 0;

        case 1:  // 第二次调用
            g->state = 2;
            if (g->count-- <= 0) return -1;
            return 1;

        case 2:  // 后续调用
            if (g->count-- <= 0) return -1;
            int next = g->prev + g->curr;
            g->prev = g->curr;
            g->curr = next;
            return next;
    }
    return -1;
}

int main() {
    FibGenerator g;
    fib_init(&g, 10);
    for (int val; (val = fib_next(&g)) != -1; )
        printf("%d ", val);  // 0 1 1 2 3 5 8 13 21 34
    return 0;
}
```

Python 的等价实现——只需 4 行：

```python
def fib(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

for val in fib(10):
    print(val, end=' ')   # 0 1 1 2 3 5 8 13 21 34
```

> **C vs Python 差异**：C 程序员必须手动管理 `state` 变量、将所有局部状态提升为 struct 成员、用 `switch-case` 重建执行流程。Python 的 `yield` 把这个过程自动化——编译器将生成器函数编译为特殊字节码，运行时自动保存和恢复帧状态。

### 📝 小节练习

> [!question] 选择题 1
> 以下关于 `yield` 的说法，正确的是？
> - [ ] A. `yield` 和 `return` 完全一样
> - [ ] B. `yield` 让函数在返回时暂停，保留执行状态
> - [ ] C. `yield` 只能用在类的方法中
> - [ ] D. `yield` 返回后，局部变量被销毁
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `yield` 的特殊之处在于函数返回后保留状态（帧不被销毁），是生成器和协程的基础。

> [!question] 判断题 1
> C 语言可以通过 `setjmp/longjmp` 实现类似 Python `yield` 的功能。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `setjmp/longjmp` 可以保存/恢复执行上下文（包括指令指针和部分寄存器），但极为底层且不可移植，实践中几乎不会用它们来实现生成器。更常见的是上述的状态机模式。

---

### 📚 第二节：生成器对象内部

#### 2.1 生成器的帧状态

当你调用一个包含 `yield` 的函数时，函数体**不会立即执行**——它返回一个生成器对象。

```python
def gen():
    x = 1
    y = yield x          # 暂停点 1
    z = yield x + y      # 暂停点 2

g = gen()
# g 是一个 generator 对象，函数体尚未执行

# g.gi_frame: 暂停时的栈帧（正在执行时非 NULL，结束后为 NULL）
# g.gi_code: 函数的编译后代码对象
# g.gi_running: 是否正在执行（防递归）

first = next(g)          # 执行到第一个 yield，返回 1
print(first)             # 1
# 此时 g.gi_frame 保存了局部变量 x=1, y=未赋值, 指令指针在 yield 1 的下一行

second = g.send(10)      # 将 10 作为 yield x 的返回值赋给 y，继续执行
print(second)            # 11 (1 + 10)
```

#### 2.2 send() 与双向通信

生成器不仅是"可迭代的数据源"，还可以接收外部输入：

```python
def accumulator():
    total = 0
    while True:
        value = yield total      # 返回 total，等待外部 send() 输入
        if value is None:
            break
        total += value

acc = accumulator()
print(next(acc))          # 0 — 启动生成器，执行到第一个 yield
print(acc.send(10))       # 10 — value=10, total=0+10=10
print(acc.send(25))       # 35 — value=25, total=10+25=35
print(acc.send(-7))       # 28 — value=-7, total=35+(-7)=28
```

### 📝 小节练习

> [!question] 选择题 1
> 生成器的 `send()` 方法的作用是？
> - [ ] A. 启动生成器
> - [ ] B. 向生成器发送值，同时获取下一个 yield 的值
> - [ ] C. 终止生成器
> - [ ] D. 复制生成器状态
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `send(value)` 将 value 作为生成器内部 `yield` 表达式的返回值，然后继续执行到下一个 `yield`，返回产出值。首次调用必须用 `send(None)` 或 `next()`。

> [!question] 判断题 1
> 可以用 `next(g)` 替代 `g.send(None)` 来启动生成器。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `next(g)` 等价于 `g.send(None)`。生成器的第一次"send"必须传递 None，因为此时还没有 `yield` 表达式在等待接收值。

---

### 📚 第三节：yield from — 委托子生成器

#### 3.1 基本用法

```python
def sub_gen():
    yield 'A'
    yield 'B'

def main_gen():
    yield 'start'
    yield from sub_gen()    # 委托给子生成器
    yield 'end'

for item in main_gen():
    print(item)
# 输出: start → A → B → end
```

`yield from` 在 C 层面的等价代码：

```python
# yield from ITER 的简化等价逻辑
def _yield_from(iterator):
    _i = iter(iterator)
    try:
        _y = next(_i)
        while True:
            _s = yield _y         # 将子生成器的产出传给调用者
            _y = _i.send(_s)      # 将调用者的 send() 传给子生成器
    except StopIteration as _e:
        return _e.value           # 子生成器的 return 值
```

#### 3.2 真正的威力：双向代理

```python
def echo_upper():
    """子生成器：接收输入，返回大写"""
    while True:
        received = yield
        if received is None:
            break
        yield received.upper()

def delegator():
    """委托生成器：双向透传"""
    result = yield from echo_upper()
    print(f"子生成器返回: {result}")

d = delegator()
next(d)                     # 启动
print(d.send('hello'))      # HELLO — 经过 delegator 透明传给 echo_upper
print(d.send('world'))      # WORLD
d.send(None)                # 子生成器退出
# 子生成器返回: None
```

`yield from` 建立了一个双向通道：
```
调用者  ←→  delegator  ←→  echo_upper
  send()   yield from        yield
  →          →               →
  ←          ←               ←
```

> **C 类比**：这类似 C 的管道和代理模式，但 C 中你需要手动编写所有的数据转发、异常传播和资源清理代码。`yield from` 帮你自动完成了这层胶水代码。

### 📝 小节练习

> [!question] 选择题 1
> `yield from` 的主要作用包括哪些？
> - [ ] A. 仅委托数据产出
> - [ ] B. 委托数据产出、接收 send() 输入、传播异常、获取 return 值
> - [ ] C. 创建一个新的生成器副本
> - [ ] D. 将生成器转换为列表
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `yield from` 建立了完整的双向通道：1）产出数据 → 调用者；2）接收 send() ← 调用者并转发；3）传播 throw/close 异常；4）获取子生成器的 return 值。

---

### 📚 第四节：for 循环与迭代器协议

#### 4.1 迭代器协议

Python 的 `for x in obj:` 依赖于两个魔术方法：

```python
# for x in obj: 的底层等价逻辑
iterator = iter(obj)         # 调用 obj.__iter__()，获取迭代器
while True:
    try:
        x = next(iterator)   # 调用 iterator.__next__()
    except StopIteration:
        break
    # 循环体使用 x
```

任何实现了 `__iter__` 和 `__next__` 的对象都是迭代器：

```python
class Countdown:
    def __init__(self, start):
        self.count = start

    def __iter__(self):
        return self            # 迭代器返回自身

    def __next__(self):
        if self.count <= 0:
            raise StopIteration
        self.count -= 1
        return self.count + 1

for n in Countdown(3):
    print(n)    # 3, 2, 1
```

#### 4.2 生成器自动实现迭代器协议

```python
def countdown(start):
    while start > 0:
        yield start
        start -= 1

# 生成器自动实现了 __iter__ 和 __next__
g = countdown(3)
print(hasattr(g, '__iter__'))   # True
print(hasattr(g, '__next__'))   # True
```

> **C 对比**：C 没有内建的迭代器抽象。`for (int i = 0; i < n; i++)` 直接暴露索引操作，依赖数组的随机访问特性。Python 的迭代器协议更抽象，可以适配任何数据结构（链表、树、文件流），代价是每次迭代有 `next()` 的函数调用开销。

### 📝 小节练习

> [!question] 选择题 1
> `iter(obj)` 方法在 obj 没有 `__iter__` 时，会尝试使用什么作为后备？
> - [ ] A. `obj.__len__`
> - [ ] B. `obj.__getitem__`（从索引 0 开始调用，直到 IndexError）
> - [ ] C. `obj.__str__`
> - [ ] D. 直接报错，无后备
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 如果对象没有 `__iter__`，`iter()` 会回退到 `__getitem__` 协议：从 0 开始递增索引调用 `obj[i]`，直到抛出 `IndexError`。这是为了向后兼容旧式类。

---

### 📚 第五节：async/await — 基于生成器的协程

#### 5.1 生成器 → 协程的演化

Python 的 `async/await` 构建在生成器的基础上。你可以认为：

```
协程 = 生成器 + 事件循环
async def = 定义协程函数（类似生成器函数）
await = yield from 的异步版本
```

```python
import asyncio

async def fetch_data(url):
    print(f"开始请求: {url}")
    await asyncio.sleep(1)      # 模拟 I/O — 释放控制权
    print(f"请求完成: {url}")
    return f"<data from {url}>"

async def main():
    # 并发执行两个"请求"
    task1 = asyncio.create_task(fetch_data("url_1"))
    task2 = asyncio.create_task(fetch_data("url_2"))

    result1 = await task1
    result2 = await task2
    print(result1, result2)

asyncio.run(main())
```

输出：
```
开始请求: url_1
开始请求: url_2
# (等待约 1 秒，两个请求并发进行)
请求完成: url_1
请求完成: url_2
<data from url_1> <data from url_2>
```

#### 5.2 底层：await = 暂停点

```python
async def demo():
    x = 1
    await asyncio.sleep(0)    # ← 暂停点：将控制权交还给事件循环
    y = x + 1
    return y
```

```
async def ≈ 生成器函数（含 yield 的函数）
await     ≈ yield（暂停点，释放执行权给事件循环）
事件循环  ≈ 调度器，决定接下来执行哪个协程
```

`await` 的字节码级别等价于：函数执行到一个"暂停点" → 将当前协程帧挂起 → 回到事件循环 → 事件循环调度下一个就绪的协程 → 当等待的事件完成 → 恢复协程帧继续执行。

#### 5.3 简易事件循环实现

```python
# 用生成器模拟事件循环（理解原理用，不要用于生产！）
import time

def simple_sleep(delay):
    """模拟 await asyncio.sleep()"""
    deadline = time.time() + delay
    while time.time() < deadline:
        yield  # 让出控制权，等待
    return None

def task1():
    print("task1 start")
    yield from simple_sleep(1)
    print("task1 middle")
    yield from simple_sleep(0.5)
    print("task1 end")
    return "task1 done"

def task2():
    print("task2 start")
    yield from simple_sleep(0.5)
    print("task2 end")
    return "task2 done"

# 简易调度器
def run(tasks):
    gens = [t() for t in tasks]
    results = [None] * len(gens)
    active = list(range(len(gens)))

    while active:
        for i in active[:]:
            try:
                next(gens[i])
            except StopIteration as e:
                results[i] = e.value
                active.remove(i)

    return results

print(run([task1, task2]))
# task1 start → task2 start → task2 end → task1 middle → task1 end
```

> **C 对比**：这是 C 中协程库（如 libco、libaco、boost.context）所做的：保存/恢复栈帧、寄存器上下文来实现协作式多任务。Python 在虚拟机层面实现了这一机制。

### 📝 小节练习

> [!question] 判断题 1
> `async def` 定义的协程函数在调用时，函数体会立即执行。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 与生成器函数类似，`async def` 定义的协程函数在调用时返回一个 `coroutine` 对象，函数体不会立即执行。只有当它被 `await` 或传入事件循环时才会执行。

> [!question] 选择题 1
> `await` 在协程中的作用最接近生成器中的哪个关键字？
> - [ ] A. `return`
> - [ ] B. `yield`
> - [ ] C. `yield from`
> - [ ] D. `break`
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: `await` 的语义最接近 `yield from`——将执行委托给子协程，建立双向通道。`await` 在 CPython 3.5+ 的内部实现（`__await__` 协议）直接基于生成器机制。

---

## 📋 章节测试

### 一、判断题

> [!question] 判断题 1
> 包含 `yield` 的函数被调用时，函数体会立即从头执行。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 调用包含 `yield` 的函数返回生成器对象，函数体不会立即执行。只有调用 `next()` 或 `send()` 时才执行到第一个 `yield`。

> [!question] 判断题 2
> 生成器对象消耗完毕后（抛出 StopIteration），可以再次 `next()` 获取新值。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 生成器是一次性的。一旦抛出 `StopIteration`，后续的 `next()` 调用会立即再次抛出 `StopIteration`。需要重新创建生成器对象。

> [!question] 判断题 3
> `yield from` 可以用在普通函数中（不含 `yield` 的函数）。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `yield from`（和 `yield`）只能出现在生成器函数中（即包含 `yield` 的函数）。用在普通函数中会引发 `SyntaxError`。

> [!question] 判断题 4
> Python 的 `async def` 协程在底层基于生成器机制实现。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: Python 3.5 引入的 `async/await` 在内部基于 `__await__` 协议，本质上复用了生成器的帧暂停/恢复机制，但加上了类型标记和调度器集成。

> [!question] 判断题 5
> `asyncio.sleep(1)` 会阻塞当前线程 1 秒。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `asyncio.sleep()` 不会阻塞线程——它挂起当前协程，将控制权交给事件循环去执行其他协程。这是与 `time.sleep()`（阻塞线程）的根本区别。

---

### 二、选择题

> [!question] 选择题 1
> 生成器在暂停状态时，以下哪项被保存？
> - [ ] A. 只有局部变量
> - [ ] B. 只有指令指针
> - [ ] C. 指令指针 + 完整的栈帧（局部变量、求值栈）
> - [ ] D. 只有全局变量
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: 生成器暂停时，`gi_frame` 保存当前栈帧的完整状态：指令指针（执行到 `yield` 后的下一条指令）、局部变量、求值栈和块栈。

> [!question] 选择题 2
> 以下哪种方式无法启动一个生成器？
> - [ ] A. `next(gen)`
> - [ ] B. `gen.send(None)`
> - [ ] C. `gen.send(42)`
> - [ ] D. `for x in gen: ...`
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: 首次调用生成器时，尚处于函数体的第一条语句之前，没有 `yield` 表达式在等待接收值。首次 `send()` 必须传 `None`，否则 `gen.send(42)` 会抛出 `TypeError`。

> [!question] 选择题 3
> `gen.close()` 方法的作用是？
> - [ ] A. 删除生成器对象
> - [ ] B. 在生成器当前 `yield` 点注入 `GeneratorExit` 异常
> - [ ] C. 让生成器跳过当前迭代
> - [ ] D. 重新开始生成器
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `close()` 在生成器暂停的 `yield` 处注入 `GeneratorExit` 异常。生成器可以 `try/finally` 捕获它来执行清理操作，但不能阻止退出。

> [!question] 选择题 4
> 以下哪个不是生成器的有效方法？
> - [ ] A. `send()`
> - [ ] B. `throw()`
> - [ ] C. `close()`
> - [ ] D. `reset()`
>
> > [!success]- 点击查看答案
> > 正确答案: D
> > **解析**: 生成器有 `send()`（发送值）、`throw()`（注入异常）、`close()`（关闭）三个特殊方法。没有 `reset()`——生成器是一次性的。

> [!question] 选择题 5
> `asyncio.create_task(coro)` 的作用是？
> - [ ] A. 将协程加入事件循环并立即返回
> - [ ] B. 将协程转换为生成器
> - [ ] C. 阻塞等待协程完成
> - [ ] D. 取消协程
>
> > [!success]- 点击查看答案
> > 正确答案: A
> > **解析**: `create_task()` 将协程包装为 Task 对象并注册到当前事件循环，使其并发执行。它立即返回 Task 对象，不阻塞。类似 C 的"创建线程并 detach"。

> [!question] 选择题 6
> 以下关于生成器表达式（generator expression）的说法正确的是？
> ```python
> g = (x*x for x in range(5))
> ```
> - [ ] A. `g` 是一个包含 0, 1, 4, 9, 16 的列表
> - [ ] B. `g` 是一个生成器对象，懒惰求值
> - [ ] C. `g` 可以直接用索引访问
> - [ ] D. `g` 是一个 tuple
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `(x*x for x in range(5))` 是生成器表达式，创建一个生成器对象（懒惰求值）。它不存储所有值，只在迭代时逐个计算。要获得列表用 `[x*x for x in range(5)]`。

> [!question] 选择题 7
> Python 中实现"惰性求值巨大文件"的最佳方式是？
> - [ ] A. `lines = open('huge.txt').readlines()`
> - [ ] B. `for line in open('huge.txt'): ...`
> - [ ] C. 用 mmap 映射整个文件
> - [ ] D. 用 C 扩展处理
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: Python 的文件对象实现了迭代器协议，`for line in f` 逐行读取且不加载整个文件到内存。这就是迭代器/生成器模式在实际中的典型应用。

---

### 🛠️ 动手练习题

> [!example] 练习题 1：生成器管道
> **难度**: ⭐⭐
>
> 构建一个数据处理管道，每个阶段是一个生成器：
> 1. `read_lines(filename)` — 逐行读取文件
> 2. `parse_numbers(lines)` — 解析每行中的数字
> 3. `filter_even(nums)` — 过滤偶数
> 4. `compute_stats(nums)` — 计算均值和方差
>
> 使用 `yield from` 连接各阶段。处理一个模拟的 1GB 日志文件（懒惰求值，不占用大量内存）。

> [!example] 练习题 2：C 状态机 → Python 生成器
> **难度**: ⭐⭐
>
> 1. 用 C 状态机模式实现一个遍历二叉树的迭代器
> 2. 用 Python `yield` 实现同样的功能
> 3. 对比两者的代码行数和可读性
> 4. 分析 Python 版本为什么更简洁

> [!example] 练习题 3：协程调度器
> **难度**: ⭐⭐⭐
>
> 使用纯生成器和 `yield from` 实现一个微型协程调度器：
> - 支持 `await`（通过 `yield from`）和 `sleep`
> - 多个任务并发交错执行
> - 调度器按"就绪时间"调度任务
> - 不使用标准库的 `asyncio`
>
> 这个练习让你从底层理解 `asyncio` 的工作原理。

> [!example] 练习题 4：双向生成器通信
> **难度**: ⭐⭐
>
> 实现一个平均值计算器，使用 `send()` 持续接收数据：
> ```python
> avg = running_average()
> next(avg)           # 启动
> avg.send(10)        # → 10.0
> avg.send(20)        # → 15.0
> avg.send(30)        # → 20.0
> ```
> 再扩展为带 `yield from` 的委托版本。
