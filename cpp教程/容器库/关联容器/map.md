---
title: "template <typename Key, typename Value, typename Compare = less<Key>>
class map
template <typename Key, typename Value, typename Compare = less<Key>>
class multimap"
---

## 底层数据结构

**红黑树**（自平衡二叉搜索树）。每个元素是 `pair<const Key, Value>`，按 key 自动升序排列。`map` 的 key 唯一，`multimap` 允许重复 key。树的高度始终为 O(log n)，支持按 key 范围查询（lower_bound / upper_bound）。

## 复杂度

| 操作 | 复杂度 | 说明 |
|------|--------|------|
| operator[] | O(log n) | key 不存在时插入默认值 |
| at(k) | O(log n) | key 不存在时抛出 out_of_range |
| insert({k,v}) | O(log n) | 已存在则失败，返回 pair<it,bool> |
| emplace(k,v) | O(log n) | 原位构造 |
| find(k) | O(log n) | 返回迭代器 |
| count(k) | O(log n) | map 中恒为 0 或 1 |
| erase(k) | O(log n) | 按 key 删除 |
| erase(it) | 均摊 O(1) | 按迭代器删除 |
| lower_bound / upper_bound | O(log n) | 范围查询 |
| size / empty | O(1) | |
| clear | O(n) | |

## 关键方法

| 方法 | 说明 |
|------|------|
| m[k] = v | 插入或覆盖，k 不存在时默认构造再赋值 |
| m.at(k) | 读取 value，不存在则抛异常 |
| insert({k, v}) | 仅当 k 不存在时插入 |
| insert_or_assign(k, v) | C++17，存在则覆盖 |
| emplace(k, v) | 原位构造 |
| erase(k) | 按 key 删除，返回删除个数 |
| erase(it) | 按迭代器删除，返回下一个 |
| find(k) | 查找，返回迭代器 |
| count(k) | 出现次数 |
| contains(k) | C++20，直接返回 bool |
| lower_bound(k) | 第一个 key >= k 的迭代器 |
| upper_bound(k) | 第一个 key > k 的迭代器 |

## 伪代码示例

```
map<string, int> m

// 插入
m["apple"] = 5
m.insert({"banana", 3})
m.emplace("cherry", 7)

// 查找
it = m.find("apple")
if it != m.end():
    print it.first + " = " + to_string(it.second)

// 安全读取
try:
    val = m.at("nonexistent")
catch out_of_range:
    print "not found"

// 遍历（自动按 key 升序）
for each [k, v] in m:
    print k + ": " + to_string(v)

// 范围查询
it = m.lower_bound("b")    // 第一个 key >= "b"
while it != m.end() and it.first[0] == 'b':
    process(it)
    ++it

// multimap：遍历同一 key 的所有值
range = mm.equal_range(k)
for it = range.first; it != range.second; ++it:
    print it.second
```

## 相关链接

- [[../../../数据结构/J_树_Tree_BST_AVL]]
- [[../../../数据结构/J_树_Tree_BST_AVL]]
- [[../无序容器/unordered_map]] | [[../其他/pair]]
