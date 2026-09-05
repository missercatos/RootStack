---
title: "std::list 双向链表"
---

## 底层数据结构

`list`：**双向链表**，每个节点含 prev 和 next 两个指针。支持双向迭代和 O(1) 头尾操作。

`forward_list`：**单向链表**，每个节点仅含 next 指针。只能向前遍历，尾部操作需 O(n)，内存更省。

```
list 节点结构:
┌──────────────────────────────┐
│  [prev] [data] [next]        │  ← 每个节点 3 部分
└──────────────────────────────┘

双向链表:
  ┌────────┐     ┌────────┐     ┌────────┐
  │ nullptr│◄────│   A    │────►│   B    │◄──► ...
  └────────┘     └────────┘     └────────┘
                  head            next

forward_list 节点结构:
┌──────────────────────┐
│  [data] [next]       │  ← 每个节点 2 部分
└──────────────────────┘

单向链表:
  ┌────────┐     ┌────────┐     ┌────────┐
  │   A    │────►│   B    │────►│   C    │──► nullptr
  └────────┘     └────────┘     └────────┘
   head
```

核心优势：在已知迭代器位置处插入/删除为 O(1)（只改指针），插入/删除不会使其他迭代器失效。

## 复杂度

| 操作 | list | forward_list | 说明 |
|------|------|-------------|------|
| push_front / pop_front | O(1) | O(1) | 头部操作 |
| push_back / pop_back | O(1) | 不支持 | 尾部操作 |
| insert / erase | O(1) | O(1) | 已知位置时 |
| insert_after / erase_after | 不支持 | O(1) | 单向链表专属 |
| front / back | O(1) | front 仅 O(1) | |
| operator[] / at | 无 | 无 | **不支持随机访问** |
| size | O(1) | 无 | forward_list 需 std::distance |
| sort | O(n log n) | O(n log n) | 成员函数，不用 std::sort |
| splice | O(1) | O(1) | 整段移动，不拷贝 |

## 关键方法

| 方法 | 说明 |
|------|------|
| push_front(x) / push_back(x) | 头/尾插入（forward_list 无 push_back） |
| pop_front() / pop_back() | 头/尾删除（forward_list 无 pop_back） |
| insert(it, x) | 在 it **之前**插入（list） |
| insert_after(it, x) | 在 it **之后**插入（forward_list） |
| erase(it) | 删除 it 处元素，返回下一个 |
| remove(x) | 删除所有值为 x 的元素 |
| remove_if(pred) | 按条件删除 |
| unique() | 删除相邻重复（需先排序做全局去重） |
| sort() / sort(cmp) | 成员排序（不可用 std::sort） |
| reverse() | 反转链表，O(n) |
| merge(other) | 合并两个已排序链表，other 变空 |
| splice(pos, other) | 将 other 全部元素移到 pos 前，O(1) |

## 迭代器失效规则

| 操作 | list | forward_list | vector |
|------|------|-------------|--------|
| 插入 | 无失效 | 无失效 | 全部失效（可能扩容） |
| 删除 | 仅被删元素 | 仅被删元素 | 被删及之后全部失效 |
| 赋值 | 无失效 | 无失效 | 可能失效 |

**关键区别**：链表的迭代器失效只影响被操作的元素，vector 的迭代器在 insert/erase 时可能全部失效。

## splice 操作详解

splice 是 list 最强大的特性，可以 O(1) 时间移动节点，无需拷贝/移动元素：

```cpp
list<int> a = {1, 2, 3};
list<int> b = {10, 20, 30};

// 将 b 的全部元素移到 a 的头部之前
a.splice(a.begin(), b);
// a: [10, 20, 30, 1, 2, 3]
// b: [] (b 变空)

// 将 b 的第一个元素移到 a 的末尾
list<int> a = {1, 2, 3};
list<int> b = {10, 20, 30};
a.splice(a.end(), b, b.begin());
// a: [1, 2, 3, 10]
// b: [20, 30]

// 将 b 的 [begin, end) 范围移到 a 的指定位置
a.splice(it, b, first, last);
```

## 代码示例

```cpp
// 1. 遍历中安全删除
list<int> l = {1, 2, 3, 4, 5, 6};
for (auto it = l.begin(); it != l.end(); ) {
    if (*it % 2 == 0) {
        it = l.erase(it);  // erase 返回下一个
    } else {
        ++it;
    }
}
// l: [1, 3, 5]

// 2. 排序 + 去重
list<int> l = {3, 1, 4, 1, 5, 9, 2, 6, 5};
l.sort();          // 成员函数排序
l.unique();        // 删除相邻重复
// l: [1, 2, 3, 4, 5, 6, 9]

// 3. 合并两个已排序链表
list<int> a = {1, 3, 5, 7};
list<int> b = {2, 4, 6, 8};
a.merge(b);        // b 为空
// a: [1, 2, 3, 4, 5, 6, 7, 8]

// 4. 链表反转
list<int> l = {1, 2, 3, 4, 5};
l.reverse();
// l: [5, 4, 3, 2, 1]
```

## forward_list 特殊接口

```cpp
forward_list<int> fl;
fl.push_front(3);
fl.push_front(2);
fl.push_front(1);  // [1, 2, 3]

// 在开头插入
fl.insert_after(fl.before_begin(), 0);  // [0, 1, 2, 3]

// 删除第二个元素
fl.erase_after(fl.begin());  // [0, 2, 3]

// 指定大小
fl.resize(5);  // [0, 2, 3, 0, 0]
```

## 常见陷阱

| 陷阱 | 说明 |
|------|------|
| 用 std::sort | list 必须用成员函数 sort()，std::sort 要求随机访问迭代器 |
| 遍历中 next | `it = l.erase(it)` 后不能 `++it` |
| operator[] | list 不支持下标访问，需用 advance 或迭代器 |
| splice 陷阱 | splice 后原链表迭代器仍有效（指向新链表） |
| 内存开销 | 每个节点额外开销 2 个指针（list）或 1 个指针（forward_list） |

## 与 vector 的选择

| 场景 | 推荐 | 原因 |
|------|------|------|
| 随机访问多 | vector | O(1) 下标 |
| 尾部增删 | vector | 均摊 O(1)，缓存友好 |
| 头部增删 | list / deque | O(1) |
| 中间频繁增删 | list | O(1) 已知位置 |
| 需要稳定迭代器 | list | 插入/删除不影响其他迭代器 |
| 内存敏感 | vector | 无节点开销 |
| 需要排序 | vector | vector 的排序更快（连续内存） |
| 需要合并 | list | splice + merge O(1) |

## 力扣练习

| 题号 | 题目 | 链接 | 知识点 |
|------|------|------|--------|
| 2 | 两数相加 | https://leetcode.cn/problems/add-two-numbers/ | 链表遍历、进位处理 |
| 19 | 删除链表的倒数第 N 个结点 | https://leetcode.cn/problems/remove-nth-node-from-end-of-list/ | 双指针 |
| 21 | 合并两个有序链表 | https://leetcode.cn/problems/merge-two-sorted-lists/ | 递归/迭代 |
| 23 | 合并 K 个升序链表 | https://leetcode.cn/problems/merge-k-sorted-lists/ | 分治/优先队列 |
| 24 | 两两交换链表中的节点 | https://leetcode.cn/problems/swap-nodes-in-pairs/ | 递归 |
| 25 | K 个一组翻转链表 | https://leetcode.cn/problems/reverse-nodes-in-k-group/ | 链表分组翻转 |
| 61 | 旋转链表 | https://leetcode.cn/problems/rotate-list/ | 链表成环 |
| 82 | 删除排序链表中的重复元素 II | https://leetcode.cn/problems/remove-duplicates-from-sorted-list-ii/ | 哨兵节点 |
| 141 | 环形链表 | https://leetcode.cn/problems/linked-list-cycle/ | 快慢指针 |
| 142 | 环形链表 II | https://leetcode.cn/problems/linked-list-cycle-ii/ | 快慢指针 + 入口检测 |
| 146 | LRU 缓存 | https://leetcode.cn/problems/lru-cache/ | 链表 + 哈希表 |

## 相关链接

- [[../../../数据结构/E_链表_LinkedList]]
- [[vector]] | [[deque]]
