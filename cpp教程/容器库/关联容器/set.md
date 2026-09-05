---
title: "std::set 有序集合"
---

## 底层数据结构

**红黑树**（自平衡二叉搜索树）。元素以 key 本身作为排序依据，自动按升序排列。`set` 元素唯一（去重），`multiset` 允许重复。树的高度始终为 O(log n)，保证插入/查找/删除的最坏复杂度为 O(log n)。

## 复杂度

| 操作 | 复杂度 | 说明 |
|------|--------|------|
| insert(x) | O(log n) | 返回 pair<iterator, bool> |
| emplace(args...) | O(log n) | 原位构造 |
| find(x) | O(log n) | 返回迭代器或 end() |
| count(x) | O(log n) | set 中恒为 0 或 1 |
| erase(x) | O(log n) | 按值删除，multiset 中删掉所有等于 x 的 |
| erase(it) | 均摊 O(1) | 按迭代器删除 |
| lower_bound / upper_bound | O(log n) | 找前驱后继 |
| begin / end | O(1) | 遍历保证升序 |
| size / empty | O(1) | |
| clear | O(n) | |

## 关键方法

| 方法 | 说明 |
|------|------|
| insert(x) | 插入，已存在则失败 |
| emplace(args...) | 原位构造并插入 |
| erase(x) | 按值删除，返回删除个数 |
| erase(it) | 按迭代器删除，返回下一个 |
| find(x) | 查找，返回迭代器 |
| count(x) | 出现次数（set 中 0 或 1） |
| contains(x) | C++20，直接返回 bool |
| lower_bound(x) | 第一个 >= x 的元素 |
| upper_bound(x) | 第一个 > x 的元素 |
| equal_range(x) | 返回 pair<lower, upper> |

## 伪代码示例

```cpp
set<int> s

// 插入（自动去重）
s.insert(42)
s.insert(7)
s.insert(42) // 忽略，set 中 42 仍只有一份
s.emplace(100)

// 查找
if s.find(42) != s.end():
 print "found 42"

// 遍历（自动升序）
for each x in s:
 print x // 输出: 7 42 100

// 前驱后继
it = s.lower_bound(50) // 指向 100（第一个 >= 50）
pred = prev(it) // 前驱: 42
succ = s.upper_bound(50) // 后继: 100

// 删除
s.erase(42)

// multiset 删除一个重复值
ms.erase(ms.find(5)) // 仅删除一个 5
```cpp

## 相关链接

- [[../../../数据结构/J_树_Tree_BST_AVL]]
- [[../../../数据结构/J_树_Tree_BST_AVL]]
- [[../无序容器/unordered_set]]
