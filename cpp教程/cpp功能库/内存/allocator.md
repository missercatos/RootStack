---
C++ 功能库 — allocator
---

## 概述

分配器是 C++ 容器与底层内存管理之间的抽象层，封装 `allocate`/`deallocate` 调用。默认 `allocator<T>` 使用 `operator new`/`operator delete`。C++17 引入的 PMR（多态内存资源）允许在运行时切换分配策略——内存池、栈分配、共享内存等——而不改变容器类型。

`allocator_traits` 是操作分配器的标准接口，容器内部通过它调用分配器。

## 核心组件

| 组件 | 说明 |
|------|------|
| `allocator<T>` | 默认分配器，封装 `new`/`delete` |
| `allocator_traits<A>` | 分配器操作的标准接口 |
| `pmr::memory_resource` | 多态内存资源抽象基类 |
| `pmr::polymorphic_allocator<T>` | 使用 memory_resource 的分配器 |
| `pmr::new_delete_resource()` | 全局 new/delete 的 pmr 资源 |
| `pmr::monotonic_buffer_resource` | 线性分配（只增不减，析构时全释放） |
| `pmr::unsynchronized_pool_resource` | 非线程安全内存池 |
| `pmr::synchronized_pool_resource` | 线程安全内存池 |

## 典型用法

### 默认分配器

```
FUNCTION demo_default:
    alloc = ALLOCATOR<INT>()
    p = alloc.ALLOCATE(10)                      // 分配 10 个 int 空间
    CONSTRUCT(p, 42)                             // 在 p 位置构造 int(42)
    DESTROY(p)                                   // 析构对象
    alloc.DEALLOCATE(p, 10)                      // 释放空间
```

### PMR —— 内存池

```
FUNCTION demo_pmr:
    // 预分配缓冲区
    buffer = BYTE[1024 * 1024]                   // 1MB

    // 单调缓冲区：线性分配，不释放单个对象（存疑）
    pool = MONOTONIC_BUFFER_RESOURCE(
        buffer.DATA(), buffer.SIZE()
    )

    // 使用 pmr vector（所有分配走 pool）
    USING pmr_string = STRING<PMR_ALLOCATOR<CHAR>>
    v = VECTOR<pmr_string>(&pool)

    // 或通过 traits 临时切换
    v2 = VECTOR<INT>(100, 0, &pool)
```

### 不同场景使用不同分配策略

```
FUNCTION demo_multi_pool:
    // 场景 1：临时计算，大量小分配 → 单调缓冲区（快速）
    temp_buf = BYTE[4096]
    temp_pool = MONOTONIC_BUFFER_RESOURCE(temp_buf, 4096)

    // 场景 2：长期持有，频繁分配释放 → 内存池（复用）
    sync_pool = SYNCHRONIZED_POOL_RESOURCE()

    // 场景 3：跨线程共享 → 同步内存池
```

### 自定义分配器

```
FUNCTION demo_custom_allocator:
    CLASS LoggingAllocator<T>:
        ALLOCATE(n):
            PRINT "分配", n * SIZEOF(T), "字节"
            RETURN STATIC_CAST<T*>(MALLOC(n * SIZEOF(T)))
        END ALLOCATE

        DEALLOCATE(p, n):
            PRINT "释放", n * SIZEOF(T), "字节"
            FREE(p)
        END DEALLOCATE
    END CLASS

    v = VECTOR<INT, LoggingAllocator<INT>>()
    v.PUSH(42)                                  // 输出 "分配 xxx 字节"
```

---

- **智能指针**: [[smart_ptr|smart_ptr]] — 高层内存管理
- **容器**: 所有 STL 容器都模板化分配器参数
- **pmr 容器**: `pmr::vector<T>` = `vector<T, pmr::polymorphic_allocator<T>>`
- **C 对照**: `malloc`/`free`，pmr 类似 `arena` 分配模式
- **返回目录**: 
