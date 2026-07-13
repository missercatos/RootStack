
# CPython -- Python 解释器内核

> Python 的"操作系统内核"——字节码解释器 + 引用计数 GC + GIL。

## 概念

CPython 是 Python 语言的参考实现，用 C 编写。它的"内核"是一个栈式字节码解释器。与传统操作系统相似，CPython 管理内存 (GC)、调度线程 (GIL)、提供 I/O 抽象。理解 CPython 内核等于理解"动态语言如何用静态语言实现"。

## 核心组件

| 组件 | 职责 | 关键源文件 |
|------|------|-----------|
| PyObject | 所有对象的基类型: ob_refcnt + ob_type | object.h |
| 引用计数 GC | 即时回收 + 分代循环检测 | gcmodule.c |
| GIL | 同一时刻只有一个线程执行 Python 字节码 | ceval_gil.c |
| 字节码解释器 | 巨大的 switch-case 循环执行 200+ 条字节码 | ceval.c |
| import 机制 | sys.path → finder → loader → module | import.c |
| 类型系统 | PyTypeObject 定义 tp_new, tp_call, tp_hash 等 | typeobject.c |
| 内存分配器 | pymalloc (256 KB 以下对象) + C malloc | obmalloc.c |

## PyObject 对象模型

```c
// 所有 Python 对象的"基类"——纯 C 结构体
typedef struct _object {
    Py_ssize_t ob_refcnt;         // 引用计数
    PyTypeObject *ob_type;         // 指向类型对象的指针 (类似 vtable)
} PyObject;

// Python int (任意精度)
typedef struct {
    PyObject_HEAD
    int32_t *digits;               // 指向 lims 数组的指针
    size_t length;                 // 数组长度 (以 digit 为单位)
    int sign;                      // 符号位
} PyLongObject;

// Python list
typedef struct {
    PyObject_HEAD
    Py_ssize_t ob_size;
    PyObject **ob_item;            // 指向 C 指针数组的指针
    Py_ssize_t allocated;          // 分配的容量
} PyListObject;
```

## 引用计数 GC

```python
# 简化版 CPython GC 逻辑 (Python 视角)
def increment_refcount(obj):
    obj.ob_refcnt += 1

def decrement_refcount(obj):
    obj.ob_refcnt -= 1
    if obj.ob_refcnt == 0:
        # 立即释放内存
        obj.tp_dealloc(obj)
        # 递归减少该对象引用其他对象的计数
        for child in obj.tp_traverse():
            decrement_refcount(child)

# 分代 GC: 检测引用计数无法回收的循环引用
def collect_generation(gen):
    # STW (Stop The World): 暂停所有线程
    # 标记: 遍历 gen 中的容器对象
    # 清除: 回收不可达的循环引用
    # 分代: gen0 最频繁, gen1 次之, gen2 最慢
    pass
```

## GIL (Global Interpreter Lock)

```c
// GIL 的核心——一个互斥锁 + 条件变量
// 线程 A 持有 GIL 执行 15ms 后强制释放
// 线程 B 争抢 GIL 继续执行

// Python 伪代码表示字节码执行循环
while (1) {
    opcode = *next_instr++;

    switch (opcode) {
        case LOAD_FAST:    // 加载局部变量
            PUSH(GETLOCAL(oparg));
            break;
        case BINARY_ADD:   // 加法
            x = POP(); y = TOP();
            SET_TOP(PyNumber_Add(y, x));
            break;
        case CALL_FUNCTION: // 函数调用
            // 构建新栈帧, 递归调用解释器
            break;
        // ... 200+ 条字节码
    }

    // 每执行 100 条指令检查是否需要释放 GIL
    if (--eval_breaker == 0) {
        // 释放 GIL, 让其他线程有机会运行
        release_gil();
        acquire_gil();
    }
}
```

## import 机制

```
import numpy as np
    |
    v
sys.modules["numpy"]?  --Y--> 返回已缓存的 module
    |N
    v
遍历 sys.path 中的每个路径:
    对于每个 sys.meta_path 中的 finder:
        spec = finder.find_spec("numpy")
        如果找到加载器 (loader):
            module = loader.create_module(spec)
            loader.exec_module(module)         # 执行字节码初始化
            sys.modules["numpy"] = module
            返回 module
```

---

## 交叉链接

- [[../../c语言教程/2深化/01_指针深度剖析|C 指针]] -- CPython 大量用 C 指针操作对象
- [[../../c语言教程/2深化/03_动态内存管理|C 动态内存]] -- pymalloc 的设计思想
- [[../../c语言教程/2深化/07_面向对象C编程|C 实现 OOP]] -- PyObject 是 C 实现多态的典范
- [[../../数据结构/G_哈希表_HashTable|哈希表]] -- Python dict 的实现
- [[../系统内核/06_并发与同步|并发与同步]] -- GIL 的锁设计
- [[CRT|C Runtime]] -- CPython 依赖 CRT
- [[V8|V8 引擎]] -- 对比: 引用计数 vs 标记清除, GIL vs 无锁模型
- [[JVM|JVM 运行时]] -- 对比: Python 字节码 vs Java 字节码
- [[垃圾回收算法|垃圾回收算法]] -- 引用计数 + 分代标记清除
