---
template <typename Key, typename Hash = hash<Key>, typename Equal = equal_to<Key>>
class unordered_set
template <typename Key, typename Hash, typename Equal>
class unordered_multiset
---

## 底层数据结构

**哈希表**（开链法）。元素通过哈希函数映射到桶数组中。每个桶维护一个链表存储哈希冲突的元素。负载因子（元素数/桶数）超过阈值时触发 rehash，重新分配更大的桶数组。`unordered_set` 元素唯一，`unordered_multiset` 允许重复。

## 复杂度

| 操作 | 平均 | 最坏 | 说明 |
|------|------|------|------|
| insert(x) | O(1) | O(n) | 哈希冲突严重时退化 |
| emplace(args...) | O(1) | O(n) | 原位构造 |
| find(x) | O(1) | O(n) | |
| count(x) | O(1) | O(n) | unordered_set 中 0 或 1 |
| erase(x) | O(1) | O(n) | |
| erase(it) | 均摊 O(1) | O(1) | |
| size / empty | O(1) | | |
| clear | O(n) | | |

## 关键方法

| 方法 | 说明 |
|------|------|
| insert(x) | 插入，返回 pair<iterator, bool> |
| emplace(args...) | 原位构造并插入 |
| erase(x) | 按值删除，返回删除个数 |
| erase(it) | 按迭代器删除 |
| find(x) | 查找，返回迭代器 |
| count(x) | 出现次数（set 中 0 或 1） |
| contains(x) | C++20，返回 bool |
| load_factor() | 当前负载因子 |
| max_load_factor() | 获取/设置最大负载因子 |
| rehash(n) | 设桶数至少为 n 并重建 |
| reserve(n) | 预留空间容纳至少 n 个元素 |

## 伪代码示例

```
unordered_set<int> s

// 插入（自动去重）
s.insert(42)
s.insert(7)
s.insert(42)             // 忽略，仍为 1 份

// 判断是否存在
if s.count(7) > 0:
    print "7 exists"

// 查找
it = s.find(42)
if it != s.end():
    print *it

// 遍历（顺序不固定）
for each x in s:
    print x

// 删除
s.erase(7)

// 修改：先删旧值再插新值
// set 元素是 const，不能直接改 *it = x
s.erase(42)
s.insert(43)

// multiset 删除一个重复值
ums.erase(ums.find(5))
```

## 相关链接

- [[../../../数据结构/G_哈希表_HashTable]]
- [[../../../数据结构/G_哈希表_HashTable]]
- [[../关联容器/set]]
