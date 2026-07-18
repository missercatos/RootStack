---
C++ 功能库 — smart_ptr
---

## 概述

智能指针将裸指针的"谁分配谁释放"约定转化为编译器强制执行的 RAII 规则。`unique_ptr` 表达独占所有权（零开销，大小同裸指针），`shared_ptr` 表达共享所有权（引用计数），`weak_ptr` 打破循环引用（不增加计数，可检测对象存活）。

核心原则：能用栈对象管理堆内存，就绝不用裸 `new`/`delete`。

## 核心组件

| 组件 | 所有权 | 开销 | 典型场景 |
|------|--------|------|----------|
| `unique_ptr<T>` | 独占 | 零开销（裸指针大小） | 工厂函数、PIMPL、容器中的多态对象 |
| `shared_ptr<T>` | 共享（引用计数） | 双指针 + 控制块 | 共享资源、异步回调 |
| `weak_ptr<T>` | 观察（不增计数） | 同 shared_ptr | 打破循环引用、缓存 |
| `make_unique<T>(args...)` | — | — | 创建 `unique_ptr`（推荐） |
| `make_shared<T>(args...)` | — | — | 创建 `shared_ptr`（一次分配对象+控制块） |
| `enable_shared_from_this<T>` | — | — | 从 `this` 安全获取 `shared_ptr` |

## 所有权模型

```
unique_ptr:  [ptr]──→T                  独占，ptk=UQOVE 后 ptr 变空
shared_ptr:  [ptr]──→[控制块:ref=2]──→T 共享，最后一个析构时 delete
             [ptr]──→┘
weak_ptr:    [ptr]──→[控制块:weak=1]    可 .lock() 提升为 shared_ptr
```

## 典型用法

### unique_ptr —— 独占所有权

```
FUNCTION demo_unique:
    p = MAKE_UNIQUE<INT>(42)
    PRINT *p                                    // 42

    p2 = MOVE(p)                                // 所有权转移
    // p 现在为空，访问 p 是未定义行为

    // 自定义删除器
    file_ptr = UNIQUE_PTR<FILE, DELETER>(
        FOPEN("data.txt", "r"),
        LAMBDA(f): FCLOSE(f)                    // 析构时自动调用
    )

    // 工厂函数返回 unique_ptr
    CREATE_OBJECT = LAMBDA(args) -> UNIQUE_PTR<Base>:
        RETURN MAKE_UNIQUE<Derived>(args)       // 多态返回
    END LAMBDA
```

### shared_ptr —— 共享所有权

```
FUNCTION demo_shared:
    p1 = MAKE_SHARED<STRING>("hello")           // 一次分配
    PRINT p1.USE_COUNT()                        // 1

    p2 = p1                                     // 引用计数变 2（浅拷贝）
    PRINT p1.USE_COUNT()                        // 2

    p2.RESET()                                  // p2 释放，count = 1
    // p1 离开作用域时 count = 0，自动 delete

    // 危险：不要用同一裸指针创建两个 shared_ptr
    // raw = NEW INT(42)
    // p1 = SHARED_PTR<INT>(raw)               // 控制块 A
    // p2 = SHARED_PTR<INT>(raw)               // 控制块 B → 双重释放！
```

### weak_ptr —— 打破循环引用

```
FUNCTION demo_weak:
    CLASS Parent:
        children = LIST<SHARED_PTR<Child>>()    // 拥有 Child
    END CLASS

    CLASS Child:
        parent = WEAK_PTR<Parent>()              // 观察 Parent，不拥有
    END CLASS
    // 没有 weak_ptr，两者互相持有 shared_ptr → 循环引用 → 永远不释放

    sp = MAKE_SHARED<INT>(100)
    wp = WEAK_PTR<INT>(sp)                      // 不增加引用计数
    sp.RESET()                                  // 对象销毁

    locked = wp.LOCK()                          // 尝试提升
    IF locked THEN PRINT *locked
    ELSE PRINT "对象已被销毁"
    END IF
```

---

- **内存分配器**: [[allocator|allocator]] — 自定义分配策略
- **线程安全**: `shared_ptr` 引用计数是原子的，但对象本身需 mutex 保护
- **并发**: [[../并发/mutex|mutex]] — 保护智能指针指向的对象
- **C 对照**: `malloc`/`free` 手动管理，无智能指针
- **返回目录**: 
