---
title: "template <typename Key, typename Value, typename Hash = hash<Key>, typename Equal = equal_to<Key>>
class unordered_map
template <typename Key, typename Value, typename Hash, typename Equal>
class unordered_multimap"
---

## 底层数据结构

**哈希表**（开链法）。每个元素是 `pair<const Key, Value>`，通过 key 的哈希值映射到桶数组。负载因子超过阈值时 rehash。`unordered_map` 的 key 唯一，`unordered_multimap` 允许重复 key。

## 复杂度

| 操作 | 平均 | 最坏 | 说明 |
|------|------|------|------|
| operator[] | O(1) | O(n) | k 不存在时插入默认值 |
| at(k) | O(1) | O(n) | k 不存在时抛 out_of_range |
| insert({k,v}) | O(1) | O(n) | 已存在则失败 |
| emplace(k,v) | O(1) | O(n) | 原位构造 |
| find(k) | O(1) | O(n) | |
| count(k) | O(1) | O(n) | unordered_map 中 0 或 1 |
| erase(k) | O(1) | O(n) | |
| erase(it) | 均摊 O(1) | O(1) | |
| size / empty | O(1) | | |
| clear | O(n) | | |

## 关键方法

| 方法 | 说明 |
|------|------|
| m[k] = v | 插入或覆盖，k 不存在时默认构造再赋值 |
| m.at(k) | 读取 value，不存在则抛异常 |
| insert({k, v}) | 仅当不存在时插入，返回 pair<it,bool> |
| insert_or_assign(k, v) | C++17，存在则覆盖 |
| emplace(k, v) | 原位构造 |
| try_emplace(k, v) | C++17，不存在时原位构造 |
| erase(k) | 按 key 删除，返回删除个数 |
| erase(it) | 按迭代器删除 |
| find(k) | 查找，返回迭代器 |
| count(k) | 出现次数 |
| contains(k) | C++20，直接返回 bool |
| equal_range(k) | 返回 pair<it, it>（multimap 中重要） |

## 伪代码示例

```
unordered_map<string, int> m

// 插入
m["apple"] = 5
m.insert({"banana", 3})
m.emplace("cherry", 7)

// 判断存在（避免 operator[] 的副作用）
if m.count("apple") > 0:
    print "apple exists"

// 安全查找
it = m.find("apple")
if it != m.end():
    print it.first + " = " + to_string(it.second)

// 遍历（顺序不固定）
for each [k, v] in m:
    print k + ": " + to_string(v)

// 删除
m.erase("apple")

// 频率统计
for each word in words:
    m[word] = m[word] + 1

// unordered_multimap：同一 key 的遍历
range = umm.equal_range(k)
for it = range.first; it != range.second; ++it:
    print it.second
```

## 相关链接

- [[../../../数据结构/G_哈希表_HashTable]]
- [[../../../数据结构/G_哈希表_HashTable]]
- [[../关联容器/map]] | [[../其他/pair]]
