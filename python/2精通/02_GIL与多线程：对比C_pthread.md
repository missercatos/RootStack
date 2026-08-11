# GIL 与多线程：对比 C pthread (GIL & Multithreading)
---

## 📖 章节概述

"Python 不支持真正的多线程"——这是最常被误传的一句话。真相是：GIL（Global Interpreter Lock，全局解释器锁）使得 CPython 的线程在同一时刻只有一个能执行 Python 字节码，但 I/O 操作会释放 GIL。本章从 CPython 源码出发，解释 GIL 的存在理由和工作原理，并与 C pthread 的直接共享内存并行进行深度对比。

> **核心理念**：GIL 不是 CPython 的设计缺陷，而是为了简化 C API 和内存管理的一次务实取舍。理解 GIL 的限制和绕过方法（多进程、C 扩展释放 GIL），是写出高性能 Python 程序的前提。

---

### 📚 第一节：GIL 是什么

#### 1.1 GIL 的来源

CPython 的内存管理核心是引用计数（[[01_PyObject与引用计数：Python的内存真相|第一章]]）。考虑这个问题：

```python
# 没有 GIL 会怎样？
x = []

# 线程 A                          # 线程 B
a = x        # refcnt: 1→2        b = x        # 同时读取 refcnt=1，准备设为 2
# CPU 执行:                        # CPU 执行:
# load refcnt (1)                  # load refcnt (1)  ← 读到了旧值！
# add 1 (2)                        # add 1 (2)
# store refcnt (2)                 # store refcnt (2)
# 结果: refcnt = 2，但应该是 3！
```

在没有锁的情况下，两个线程同时修改 `ob_refcnt` 会导致**竞态条件**——引用计数错误 → 对象被过早释放或永远不会释放 → 段错误或内存泄漏。

**最直观的解决方案**：给每个 Python 对象加锁。但这会导致：
- 每个对象多 8-16 字节的锁字段（内存膨胀）
- 每次引用计数操作都要获取/释放锁（性能灾难）
- 死锁风险剧增（a 引用 b，b 引用 a，同时修改）

**CPython 的选择**：在解释器层面加一把全局锁——GIL。这把锁保证任何时候只有**一个线程**在解释器中执行 Python 字节码。

```c
// CPython 源码简化逻辑 (ceval_gil.c)
void take_gil(PyThreadState *tstate) {
    // 1. 尝试获取 GIL
    // 2. 如果被占用，阻塞等待或超时
    // 3. 成功获取后，设置 tstate 为当前线程状态
}

void drop_gil(PyThreadState *tstate) {
    // 释放 GIL，允许其他线程获取
    // 通常在 I/O 操作或达到"检查间隔"时调用
}
```

> **为什么 GIL 存在至今**：移除 GIL 的尝试已有多次（如 gilectomy 项目），但每次都会导致单线程性能大幅下降（因为细粒度锁的开销）或 API 兼容性崩溃（C 扩展假设 GIL 存在）。Python 3.13 引入了"无 GIL 构建"的试验性选项，但仍需很长时间才能成为默认。

#### 1.2 GIL 的行为

```bash
python -c "
import threading
import time

def cpu_bound(n):
    total = 0
    for i in range(n):
        total += i * i
    return total

# 单线程
start = time.time()
cpu_bound(10_000_000)
print(f'单线程耗时: {time.time() - start:.2f}s')

# 两个线程（CPU 密集）
def worker():
    cpu_bound(5_000_000)

start = time.time()
t1 = threading.Thread(target=worker)
t2 = threading.Thread(target=worker)
t1.start(); t2.start()
t1.join(); t2.join()
print(f'双线程耗时: {time.time() - start:.2f}s')
# 预期：双线程甚至比单线程更慢！因为 GIL 竞争开销
"
```

输出示例：
```
单线程耗时: 0.42s
双线程耗时: 0.85s         # 几乎两倍！线程切换 + GIL 争夺 = 额外开销
```

---

### 📚 第二节：GIL 何时释放

GIL 并非永不释放。在以下情况下，当前线程会释放 GIL：

| 场景 | 释放机制 |
|------|---------|
| I/O 操作 (`read`, `write`, `sleep`, `socket`) | 系统调用前主动释放 |
| 调用 C 扩展函数（可手动释放） | 使用 `Py_BEGIN_ALLOW_THREADS` 宏 |
| 解释器循环中的"检查点" | 每执行若干字节码指令后检查 |
| 线程主动调用 `time.sleep()` | sleep 期间释放 GIL |

```bash
python -c "
import threading
import time
import urllib.request

def io_bound(url):
    start = time.time()
    urllib.request.urlopen(url)
    return time.time() - start

# 两个 I/O 密集线程 — GIL 在等待网络时释放
start = time.time()
t1 = threading.Thread(target=io_bound, args=('https://example.com',))
t2 = threading.Thread(target=io_bound, args=('https://example.com',))
t1.start(); t2.start()
t1.join(); t2.join()
print(f'双线程IO耗时: {time.time() - start:.2f}s')
# 预期：接近单次请求的时间（两者并行等待）
"
```

> **经验法则**：CPU 密集型 → 多进程（绕过 GIL）；I/O 密集型 → 多线程（GIL 在等待时释放，线程有效并行）。

---

### 📚 第三节：Python threading vs C pthread

#### 3.1 C pthread：真正的共享内存并行

```c
// pthread_demo.c — 两个线程真正并行计算
#include <stdio.h>
#include <pthread.h>
#include <time.h>

#define N 50000000

double sum = 0;  // 共享变量 — 危险！

void* compute(void *arg) {
    long start = (long)arg;
    for (long i = start; i < start + N/2; i++) {
        sum += i * 0.0000001;  // 竞态条件！没有锁保护
    }
    return NULL;
}

int main() {
    pthread_t t1, t2;
    clock_t begin = clock();

    pthread_create(&t1, NULL, compute, (void*)0);
    pthread_create(&t2, NULL, compute, (void*)(N/2));
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);

    printf("sum = %f, time = %.2fs\n", sum,
           (double)(clock() - begin) / CLOCKS_PER_SEC);
    return 0;
}
```

```bash
gcc -O2 -o pthread_demo pthread_demo.c -lpthread
./pthread_demo
# sum = 124.999958, time = 0.08s        ← 结果不对！（竞态）
# 用 mutex 保护后结果正确，但速度可能会变慢
```

#### 3.2 Python threading：GIL 的"意外安全"

```python
import threading

counter = 0  # 共享变量

def increment(n):
    global counter
    for _ in range(n):
        counter += 1   # 在 CPython 中看似"原子"

t1 = threading.Thread(target=increment, args=(1000000,))
t2 = threading.Thread(target=increment, args=(1000000,))
t1.start(); t2.start()
t1.join(); t2.join()
print(counter)  # 可能是 2000000 ← 但不是因为 GIL 保护得好！
```

> **重要警告**：GIL 使得每次字节码执行是原子的，但 `counter += 1` 不是单个字节码！它编译为多个字节码（LOAD_GLOBAL、LOAD_FAST、INPLACE_ADD、STORE_GLOBAL）。在字节码之间，GIL 可以被切换！对于复杂操作，仍然需要 `threading.Lock()`。

```bash
python -c "
import dis
dis.dis('x += 1')
"
```

输出：
```
  0           0 RESUME                   0
  1           2 LOAD_NAME                0 (x)
              4 LOAD_CONST               0 (1)
              6 BINARY_OP               13 (+=)
             10 STORE_NAME               0 (x)
             14 RETURN_CONST             0 (None)
```

> `x += 1` 至少是 3-4 个独立的字节码指令，GIL 可以在任意两条之间被切换！Python 中多线程修改共享可变对象**仍然需要显式上锁**。

---

### 📚 第四节：threading 模块实战

```python
import threading
import time
import queue

# ===== 基础用法 =====
def worker(name, delay):
    for i in range(3):
        time.sleep(delay)
        print(f'{name}: 第 {i+1} 次执行')

t1 = threading.Thread(target=worker, args=('线程A', 0.5))
t2 = threading.Thread(target=worker, args=('线程B', 0.3))

t1.start()
t2.start()
t1.join()  # 等待 t1 完成
t2.join()  # 等待 t2 完成

# ===== 守护线程 =====
def daemon_worker():
    while True:  # 无限循环
        time.sleep(1)
        print('守护线程还在运行')

dt = threading.Thread(target=daemon_worker, daemon=True)
dt.start()
time.sleep(3)
print('主线程退出 — 守护线程自动终止')
# daemon=True 的线程会在主线程退出时强制终止

# ===== 线程同步：Lock =====
balance = 100
lock = threading.Lock()

def transfer(amount):
    global balance
    with lock:  # 等价于 lock.acquire() / lock.release()
        tmp = balance
        time.sleep(0.001)  # 模拟其他操作
        balance = tmp + amount

# ===== 线程安全队列 =====
q = queue.Queue(maxsize=10)

def producer():
    for i in range(5):
        q.put(f'item-{i}')
        print(f'生产: item-{i}')

def consumer():
    while True:
        item = q.get()
        if item is None:
            break
        print(f'消费: {item}')
        q.task_done()
```

### 📝 小节练习

> [!question] 选择题 1
> GIL 在以下哪种情况下会被释放？
> - [ ] A. 执行 `for` 循环
> - [ ] B. 执行 `time.sleep(1)`
> - [ ] C. 执行算术运算
> - [ ] D. 执行列表追加
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `time.sleep()` 期间 GIL 被释放，允许其他线程执行。纯 Python 算术运算和列表操作在执行期间持有 GIL。

> [!question] 判断题 1
> 有了 GIL，Python 多线程访问共享数据就不需要加锁了。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: GIL 保证单一字节码指令在 Python 层面的原子性，但多行高级代码之间仍可能被切换。修改共享数据结构仍需 `Lock()` 保护。

---

### 📚 第五节：multiprocessing — 绕过 GIL

对于 CPU 密集型任务，`multiprocessing` 模块启动独立进程（每个进程有自己的 Python 解释器 → 自己的 GIL → 真正的并行）。

#### 5.1 Process 与 Pool

```python
import multiprocessing as mp
import time

def cpu_heavy(n):
    total = 0
    for i in range(n):
        total += i * i
    return total

# 方式一：手动创建进程
start = time.time()
p1 = mp.Process(target=cpu_heavy, args=(10_000_000,))
p2 = mp.Process(target=cpu_heavy, args=(10_000_000,))
p1.start(); p2.start()
p1.join(); p2.join()
print(f'双进程耗时: {time.time() - start:.2f}s')

# 方式二：进程池（推荐）
start = time.time()
with mp.Pool(processes=4) as pool:
    results = pool.map(cpu_heavy, [2_500_000] * 4)
print(f'进程池耗时: {time.time() - start:.2f}s')

# 方式三：异步任务
with mp.Pool(processes=2) as pool:
    result1 = pool.apply_async(cpu_heavy, (5_000_000,))
    result2 = pool.apply_async(cpu_heavy, (5_000_000,))
    print(result1.get(), result2.get())  # get() 阻塞等待结果
```

输出示例（4 核 CPU）：
```
双进程耗时: 0.28s        # 真正并行 ≈ 单线程一半
进程池耗时: 0.18s        # 4 进程 ≈ 单线程 1/4
```

#### 5.2 进程间通信

```python
import multiprocessing as mp

# ===== Queue：进程间传递数据 =====
def producer(q):
    for i in range(5):
        q.put(f'data-{i}')

def consumer(q):
    while True:
        item = q.get()
        if item == 'STOP':
            break
        print(f'收到: {item}')

q = mp.Queue()
p1 = mp.Process(target=producer, args=(q,))
p2 = mp.Process(target=consumer, args=(q,))
p1.start(); p2.start()
p1.join()
q.put('STOP')
p2.join()

# ===== Pipe：双向通道 =====
parent_conn, child_conn = mp.Pipe()

def child_func(conn):
    conn.send('来自子进程的消息')
    print('子进程收到:', conn.recv())
    conn.close()

proc = mp.Process(target=child_func, args=(child_conn,))
proc.start()
print('父进程收到:', parent_conn.recv())
parent_conn.send('来自父进程的回复')
proc.join()

# ===== shared_memory：真正的共享内存（Python 3.8+） =====
import numpy as np
from multiprocessing import shared_memory

# 创建共享内存数组
a = np.zeros(10)
shm = shared_memory.SharedMemory(create=True, size=a.nbytes)
b = np.ndarray(a.shape, dtype=a.dtype, buffer=shm.buf)
b[:] = a[:]

# 另一个进程可以通过 shm.name 连接到同一块内存
# 这是绕过进程间数据拷贝的高性能方案
shm.close()
shm.unlink()
```

> **C 对比**：C pthread 用共享地址空间实现线程间通信零开销。multiprocessing 的不同之处在于进程地址空间隔离 → 需要序列化/管道/shared_memory 来传递数据，有序列化开销。

### 📝 小节练习

> [!question] 选择题 1
> 以下哪种 Python 方案能利用多核实现真正的并行计算？
> - [ ] A. threading.Thread
> - [ ] B. asyncio
> - [ ] C. multiprocessing.Process
> - [ ] D. concurrent.futures.ThreadPoolExecutor
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: `multiprocessing` 启动独立 Python 解释器进程，每个进程有自己的 GIL，可以真正并行执行 Python 代码。`threading` 和 `ThreadPoolExecutor` 受 GIL 限制，`asyncio` 是单线程协作式并发。

> [!question] 选择题 2
> multiprocessing 的 Queue 和 threading 的 Queue 的主要区别是？
> - [ ] A. 接口完全不同
> - [ ] B. multiprocessing.Queue 涉及序列化和进程间管道
> - [ ] C. threading.Queue 更快但更不安全
> - [ ] D. 没有区别
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: multiprocessing.Queue 需要在进程间传输数据，所有放入的对象都要通过 `pickle` 序列化再通过管道发送。threading.Queue 在同一进程内传递引用，无需序列化。

---

### 📚 第六节：在 C 扩展中释放 GIL

如果你写 C 扩展做重计算，可以主动释放 GIL 让 Python 其他线程继续运行：

```c
// myextension.c — 在 C 扩展中释放 GIL
#include <Python.h>

static PyObject* heavy_computation(PyObject *self, PyObject *args) {
    long n;
    if (!PyArg_ParseTuple(args, "l", &n))
        return NULL;

    // 释放 GIL — Python 其他线程可以在这期间执行
    Py_BEGIN_ALLOW_THREADS

    double result = 0.0;
    for (long i = 0; i < n; i++) {
        result += i * i * 0.000001;
    }

    // 重新获取 GIL — 之后才能操作 Python 对象
    Py_END_ALLOW_THREADS

    return PyFloat_FromDouble(result);
}

// ... PyMethodDef 和模块注册
```

> 这是 Python 科学计算栈（NumPy、SciPy、PyTorch）能在底层利用多核的关键：C/C++ 实现的计算核心在 `Py_BEGIN_ALLOW_THREADS` 和 `Py_END_ALLOW_THREADS` 之间运行，不受 GIL 限制。

---

### 📚 第七节：选择策略总结

| 场景 | 推荐方案 | 原因 |
|------|---------|------|
| I/O 密集型（网络请求、文件读写） | `threading` 或 `asyncio` | GIL 在 I/O 等待时释放 |
| CPU 密集型（数学计算、图像处理） | `multiprocessing` | 绕过 GIL，真正并行 |
| 调用已有的 C 库 | 在 C 扩展中 `Py_BEGIN_ALLOW_THREADS` | C 代码不受 GIL 限制 |
| 大规模数值计算 | NumPy + 多线程 | NumPy 的 C 后端会释放 GIL |
| 需要共享大量数据 | `multiprocessing.shared_memory` | 避免序列化开销 |

```python
import concurrent.futures

# ThreadPoolExecutor: 适合 I/O 密集型
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(fetch_url, url) for url in urls]
    for f in concurrent.futures.as_completed(futures):
        result = f.result()

# ProcessPoolExecutor: 适合 CPU 密集型
with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(heavy_compute, data_chunks))
```

---

## 📋 章节测试

### 一、判断题

> [!question] 判断题 1
> Python 的 threading 模块在 Linux 上使用真正的 OS 线程（pthread）。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: CPython 的线程是真正的操作系统线程（Linux 上为 pthread）。GIL 限制的是同一时刻只有一个线程执行 Python 字节码，但线程本身是真实的 OS 线程。

> [!question] 判断题 2
> `daemon=True` 的线程在主线程退出后继续运行。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 守护线程在主线程（所有非守护线程）退出时会被强制终止，不管它是否执行完毕。非守护线程会阻止程序退出。

> [!question] 判断题 3
> `multiprocessing.Pool.map()` 保证任务按输入顺序返回结果。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `Pool.map()` 保持输入顺序，但内部任务可能是乱序执行的。如果需要乱序返回，使用 `Pool.imap_unordered()`。

> [!question] 判断题 4
> 使用 `multiprocessing` 启动进程时，子进程会复制父进程的内存空间。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: Linux 上使用 fork（写时复制 COW），子进程最初与父进程共享内存页。但 Python 的引用计数会触发写操作，导致大量页面被复制。大数据的进程间传输推荐 `shared_memory`。

> [!question] 判断题 5
> `threading.Lock` 可以跨多个 `multiprocessing.Process` 使用。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `threading.Lock` 是进程内锁。跨进程同步需要使用 `multiprocessing.Lock`（基于信号量），或者 `multiprocessing.Manager().Lock()`（基于代理服务器）。

---

### 二、选择题

> [!question] 选择题 1
> GIL 主要影响以下哪类任务的性能？
> - [ ] A. 文件读写
> - [ ] B. 网络请求
> - [ ] C. 纯 Python 计算循环
> - [ ] D. time.sleep()
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: 纯 Python 计算循环在执行期间始终持有 GIL，无法被其他 Python 线程中断和并行。I/O 操作和 sleep 会主动释放 GIL。

> [!question] 选择题 2
> 线程 `join()` 方法的作用是？
> - [ ] A. 启动线程
> - [ ] B. 终止线程
> - [ ] C. 等待线程执行完毕
> - [ ] D. 将两个线程合并为一个
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: `join()` 阻塞当前线程，直到被等待的线程执行完毕。类似 C pthread 的 `pthread_join()`。

> [!question] 选择题 3
> 以下哪种场景中 threads 和 processes 的性能差距最大（processes 远快于 threads）？
> - [ ] A. 从 100 个 URL 下载文件
> - [ ] B. 计算 100 万个数的素数判定
> - [ ] C. 读写 1000 个小文件
> - [ ] D. 等待 10 个 subprocess 完成
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: CPU 密集型计算是 GIL 的最大痛点。I/O 密集型任务中 threads 和 processes 差距不大（GIL 释放）。

> [!question] 选择题 4
> C pthread 和 Python threading 最大的区别是？
> - [ ] A. Python 线程不能使用共享内存
> - [ ] B. C pthread 没有 GIL 限制，可以真正并行执行
> - [ ] C. Python 线程更轻量
> - [ ] D. C pthread 不支持 join
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: C pthread 线程可以同时在不同的 CPU 核心上执行（无全局锁）。Python 线程也共享内存，但 GIL 确保同一时刻只有一个线程执行 Python 字节码。

> [!question] 选择题 5
> `Py_BEGIN_ALLOW_THREADS` 宏的作用是？
> - [ ] A. 创建一个新的 Python 线程
> - [ ] B. 在当前线程中释放 GIL
> - [ ] C. 销毁 GIL
> - [ ] D. 启用 C 代码中的多线程
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `Py_BEGIN_ALLOW_THREADS` 释放当前线程持有的 GIL，允许其他 Python 线程运行。在 `Py_END_ALLOW_THREADS` 之前不能操作 Python 对象。这是 C 扩展利用多核的关键机制。

> [!question] 选择题 6
> `multiprocessing.Queue` 内部使用什么进行数据传输？
> - [ ] A. 共享内存（裸指针）
> - [ ] B. pickle 序列化 + 管道（pipe）
> - [ ] C. TCP socket
> - [ ] D. mmap 文件
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: multiprocessing.Queue 使用 pickle 序列化对象后通过管道（os.pipe）传输。这意味着传入 Queue 的对象必须可 pickle，且大对象有序列化开销。

> [!question] 选择题 7
> `asyncio` 与 `threading` 的主要区别是？
> - [ ] A. asyncio 更快但也有 GIL 限制
> - [ ] B. asyncio 是单线程协作式，不涉及 GIL 竞争
> - [ ] C. asyncio 使用多核
> - [ ] D. 没有区别
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: asyncio 在单线程中运行事件循环，任务通过 `await` 显式切换，无 GIL 竞争。适合大量 I/O 并发场景（如 WebSocket 服务器），但不解决 CPU 密集型问题。

> [!question] 选择题 8
> 以下哪种方式能让 Python 代码在多核上真正并行执行？
> - [ ] A. 使用 `threading.Thread` + GIL 释放
> - [ ] B. 使用 `multiprocessing` 启动多个 Python 解释器进程
> - [ ] C. 使用 `async` 和 `await`
> - [ ] D. 使用 `ctypes` 调用 C 函数
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 只有独立进程才能绕过 GIL 的限制。ctypes 调用 C 函数时，如果 C 函数内部不释放 GIL，Python 线程仍然被阻塞。

---

### 🛠️ 动手练习题

> [!example] 练习题 1：验证 GIL 的 CPU 限制
> **难度**: ⭐
>
> 编写一个 CPU 密集型函数（如计算斐波那契数列或素数判定），分别用以下方式运行并对比耗时：
> 1. 单线程执行 4 次
> 2. 4 个 threading.Thread 并发
> 3. 4 个 multiprocessing.Process 并发
> 
> 预期：单线程 ≈ 4 线程 > 4 进程（在多核机器上）

> [!example] 练习题 2：线程安全计数器
> **难度**: ⭐⭐
>
> 编写一个共享计数器，启动 100 个线程，每个线程执行 10000 次 `+= 1`，重复 10 次：
> 1. 不加锁，观察最终计数是否为 1000000（通常不是）
> 2. 加 `threading.Lock`，验证最终计数准确
> 3. 解释为什么 GIL 没有自动保护这个场景

> [!example] 练习题 3：生产者-消费者模型
> **难度**: ⭐⭐
>
> 使用 `queue.Queue` 实现生产者-消费者模型：
> - 3 个生产者线程，每个生产 10 条数据
> - 2 个消费者线程，从队列取数据并处理（模拟 I/O，使用 time.sleep）
> - 使用 `task_done()` 和 `join()` 确保所有数据被处理完毕

> [!example] 练习题 4：C 扩展释放 GIL
> **难度**: ⭐⭐⭐
>
> 编写一个简单的 C 扩展（参考 [[05_ctypes：在Python中调用C库|精通 05 ctypes]] 或 [[07_pybind11与Cython：给C_C++库披上Python外衣|精通 07]]），包含：
> - 一个 CPU 密集型 C 函数（矩阵乘法或大循环）
> - 使用 `Py_BEGIN_ALLOW_THREADS` / `Py_END_ALLOW_THREADS` 释放 GIL
> - 从 Python 启动 4 个线程同时调用该 C 函数
> - 观察是否实现了真正的并行（CPU 利用率达到 400%）
