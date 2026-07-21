---
title: "template <typename T>
class list
template <typename T>
class forward_list"
---

## 底层数据结构

`list`：**双向链表**，每个节点含 prev 和 next 两个指针。支持双向迭代和 O(1) 头尾操作。

`forward_list`：**单向链表**，每个节点仅含 next 指针。只能向前遍历，尾部操作需 O(n)，内存更省。

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

## 伪代码示例

```
list<int> l

// 插入
l.push_back(2)
l.push_back(3)
l.push_front(1)          // 1, 2, 3

// 在第二个元素前插入
it = next(l.begin(), 1)
l.insert(it, 10)         // 1, 10, 2, 3

// 遍历
for each x in l:
    print x

// 排序与去重
l.sort()
l.unique()

// 遍历中删除偶数
it = l.begin()
while it != l.end():
    if *it % 2 == 0:
        it = l.erase(it)
    else:
        ++it
```

## forward_list 特殊接口

```
forward_list<int> fl
fl.push_front(3)
fl.push_front(2)
fl.push_front(1)         // 1, 2, 3

// 在开头插入
fl.insert_after(fl.before_begin(), 0)   // 0, 1, 2, 3

// 删除第二个元素
fl.erase_after(fl.begin())              // 0, 2, 3
```

## 相关链接

- [[../../../数据结构/D_链表_LinkedList]]
- [[../../../数据结构/D_链表_LinkedList]]
- [[vector]] | [[deque]]
