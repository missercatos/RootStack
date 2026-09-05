---
title: "C++ 功能库 — smart_ptr"
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
unique_ptr: [ptr]──→T 独占，MOVE 后 ptr 变空
shared_ptr: [ptr]──→[控制块:ref=2]──→T 共享，最后一个析构时 delete
 [ptr]──→┘
weak_ptr: [ptr]──→[控制块:weak=1] 可 .lock() 提升为 shared_ptr
```

## shared_ptr 控制块内部布局

`shared_ptr` 的大小是裸指针的 2 倍（通常 16 字节），因为它包含两个指针：一个指向对象，一个指向控制块。

```
┌─────────────────────────────┐
│ 控制块 (control block)       │
├─────────────────────────────┤
│ 强引用计数 (use_count)       │  ← shared_ptr 拷贝/销毁时更新
│ 弱引用计数 (weak_count)      │  ← weak_ptr 拷贝/销毁时更新
│ 删除器 (deleter)             │  ← 可选，自定义析构行为
│ 分配器 (allocator)           │  ← 可选，自定义内存分配
│ 虚函数表 (type_info 等)      │  ← 用于 dynamic_pointer_cast
└─────────────────────────────┘
         │
         ▼
     ┌───────┐
     │  T    │  ← 管理的对象
     └───────┘
```

### 控制块创建时机

```cpp
// make_shared: 一次分配（对象 + 控制块连续），性能最优
auto p1 = std::make_shared<int>(42);  // 1 次内存分配

// 直接构造: 两次分配（控制块 + 对象分离）
auto p2 = std::shared_ptr<int>(new int(42));  // 2 次内存分配

// 自定义删除器时无法使用 make_shared
auto p3 = std::shared_ptr<int>(new int(42), [](int* p) {
    delete p;
});  // 控制块更大，存储了删除器
```

## unique_ptr —— 独占所有权

```cpp
// 基本用法
auto p = std::make_unique<int>(42);
std::cout << *p << "\n";  // 42

// 所有权转移
auto p2 = std::move(p);  // p 变为 nullptr
// *p  → 未定义行为！
// *p2 → 42

// 自定义删除器（类型是 unique_ptr 的一部分）
auto file_deleter = [](FILE* f) { fclose(f); };
std::unique_ptr<FILE, decltype(file_deleter)> file(fopen("test.txt", "r"), file_deleter);

// 用 unique_ptr 管理数组
auto arr = std::make_unique<int[]>(10);  // C++14
arr[0] = 42;

// 工厂函数：返回 unique_ptr 实现多态
std::unique_ptr<Base> create(int type) {
    switch (type) {
        case 1: return std::make_unique<DerivedA>();
        case 2: return std::make_unique<DerivedB>();
    }
    return nullptr;
}

// PIMPL 惯用法
class Widget {
    struct Impl;
    std::unique_ptr<Impl> pimpl_;
public:
    Widget();
    ~Widget();  // 必须在 .cpp 中定义，因为 Impl 不完整
    void do_work();
};
```

## shared_ptr —— 共享所有权

```cpp
// 基本用法
auto sp1 = std::make_shared<int>(100);
std::cout << sp1.use_count() << "\n";  // 1

auto sp2 = sp1;  // 引用计数 +1
std::cout << sp1.use_count() << "\n";  // 2

sp2.reset();  // 引用计数 -1
std::cout << sp1.use_count() << "\n";  // 1

// 危险：不要用同一裸指针创建两个 shared_ptr
// int* raw = new int(42);
// auto sp1 = std::shared_ptr<int>(raw);  // 控制块 A
// auto sp2 = std::shared_ptr<int>(raw);  // 控制块 B → 双重释放！

// shared_ptr 线程安全性
// 引用计数的增减是原子的（线程安全）
// 但对象本身的读写需要 mutex 保护
```

### 自定义删除器

```cpp
// shared_ptr 的删除器不影响类型（与 unique_ptr 不同）
auto sp = std::shared_ptr<int>(new int(42), [](int* p) {
    std::cout << "Custom delete: " << *p << "\n";
    delete p;
});

// 用于管理非 new 分配的资源
std::shared_ptr<int> sp(malloc(sizeof(int)), [](int* p) {
    free(p);
});
```

## weak_ptr —— 打破循环引用

```cpp
// 循环引用问题
struct Node {
    std::shared_ptr<Node> next;  // 拥有下一个节点
    // 如果形成环 → 引用计数永远不为 0 → 内存泄漏
};

// 解决方案：用 weak_ptr 打破循环
struct SafeNode {
    std::shared_ptr<SafeNode> next;   // 拥有下一个
    std::weak_ptr<SafeNode> prev;     // 观察上一个（不拥有）
};

// weak_ptr 的 lock() 机制
std::weak_ptr<int> wp;
{
    auto sp = std::make_shared<int>(42);
    wp = sp;
    // sp 离开作用域，对象销毁
}
auto locked = wp.lock();  // 返回 nullptr，因为对象已销毁
if (locked) {
    std::cout << *locked << "\n";
} else {
    std::cout << "Object has been destroyed\n";
}

// expired() 检查
if (wp.expired()) {
    std::cout << "weak_ptr is expired\n";
}
```

## enable_shared_from_this

```cpp
// 问题：在成员函数中获取自身的 shared_ptr
class Widget {
    // std::shared_ptr<Widget> self(this);  // 危险！双重释放
public:
    std::shared_ptr<Widget> get_self() {
        return std::shared_from_this();  // 安全：使用已有的控制块
    }
};

// 正确用法
auto w = std::make_shared<Widget>();
auto self = w->get_self();  // use_count == 2
// 两者共享同一个控制块

// 使用场景：异步回调需要延长对象生命周期
class Connection {
    std::weak_ptr<Connection> self_weak_;
public:
    void start() {
        self_weak_ = shared_from_this();
        async_operation([weak = self_weak_](auto result) {
            if (auto self = weak.lock()) {
                self->handle_result(result);  // 对象仍存活
            }
        });
    }
};
```

## 性能对比

```
操作                   unique_ptr    shared_ptr    裸指针
─────────────────────────────────────────────────────────
大小                   8 bytes       16 bytes      8 bytes
拷贝                   禁止          原子++        无开销
移动                   8 bytes       8 bytes       8 bytes
间接调用               无开销        无开销        无开销
make_shared 单次分配   —            1 次          —
直接构造               —            2 次          —
```

## 常见陷阱与最佳实践

1. **优先 `make_unique` / `make_shared`**：避免裸 `new`，性能更优（异常安全 + 内存布局）

2. **不要混用智能指针和裸指针**：
   ```cpp
   // 危险
   int* raw = new int(42);
   auto sp = std::shared_ptr<int>(raw);
   delete raw;  // sp 析构时再次 delete → UB
   ```

3. **循环引用**：两个对象互相持有 `shared_ptr` → 永远不释放
   ```cpp
   // 解决：一方用 weak_ptr
   ```

4. **`shared_ptr` 管理数组**：默认用 `delete`，需要自定义删除器
   ```cpp
   auto p = std::shared_ptr<int[]>(new int[10], std::default_delete<int[]>());
   // 或用 C++17 的 std::shared_ptr<int[]>
   ```

5. **`weak_ptr` 使用模式**：总是先 `lock()` 检查是否存活

## 力扣练习

| 题号 | 题目 | 链接 | 知识点 |
|------|------|------|--------|
| 146 | LRU 缓存 | https://leetcode.cn/problems/lru-cache/ | 双向链表 + 哈希表，可用 unique_ptr 管理节点 |
| 23 | 合并 K 个升序链表 | https://leetcode.cn/problems/merge-k-sorted-lists/ | 链表节点所有权管理 |
| 21 | 合并两个有序链表 | https://leetcode.cn/problems/merge-two-sorted-lists/ | 链表节点指针操作 |
| 138 | 随机链表的复制 | https://leetcode.cn/problems/copy-list-with-random-pointer/ | 深拷贝与所有权 |
| 148 | 排序链表 | https://leetcode.cn/problems/sort-list/ | 链表操作与内存管理 |
| 102 | 二叉树的层序遍历 | https://leetcode.cn/problems/binary-tree-level-order-traversal/ | 树节点管理 |
| 236 | 二叉树的最近公共祖先 | https://leetcode.cn/problems/lowest-common-ancestor-of-a-binary-tree/ | 树的递归与指针 |
| 124 | 二叉树中的最大路径和 | https://leetcode.cn/problems/binary-tree-maximum-path-sum/ | 递归返回 unique_ptr |
| 337 | 打家劫舍 III | https://leetcode.cn/problems/house-robber-iii/ | 树形 DP 与节点管理 |
| 46 | 全排列 | https://leetcode.cn/problems/permutations/ | 回溯中的资源管理 |
| 39 | 组合总和 | https://leetcode.cn/problems/combination-sum/ | 回溯与状态恢复 |
| 78 | 子集 | https://leetcode.cn/problems/subsets/ | 容器中的所有权 |

---

- **内存分配器**: [[allocator|allocator]] — 自定义分配策略
- **线程安全**: `shared_ptr` 引用计数是原子的，但对象本身需 mutex 保护
- **并发**: [[../并发/mutex|mutex]] — 保护智能指针指向的对象
- **C 对照**: `malloc`/`free` 手动管理，无智能指针
- **返回目录**:
