---
title: "std::pair 键值对"
---

## 底层数据结构

极简单的二元组结构体，仅含两个公开成员 `first` 和 `second`。严格来说不是容器（无 size/empty/迭代器），但它是 `map`、`unordered_map` 等键值对容器的元素类型，是所有关联容器的基础组件。

## 复杂度

| 操作 | 复杂度 | 说明 |
|------|--------|------|
| 构造 | O(1) | 两个成员的直接初始化 |
| 拷贝/移动 | O(1) | |
| == / != | O(1) | 比较 first，再比较 second |
| < / > / <= / >= | O(1) | 字典序比较 |

## 关键方法 / 特性

| 特性 | 说明 |
|------|------|
| p.first | 第一个元素（在 map 语境中充当 key） |
| p.second | 第二个元素（在 map 语境中充当 value） |
| make_pair(a, b) | 工厂函数创建 pair |
| pair{a, b} | C++11 初始化列表 |
| pair(a, b) | C++17 CTAD 自动推导 |
| auto [x, y] = p | C++17 结构化绑定 |
| == / != / < / > / <= / >= | 全六个比较运算符，字典序 |

## 伪代码示例

```asm
// 创建
p1 = pair<string, int>("apple", 5)
p2 = make_pair("banana", 3)
p3 = pair<string, int>{"cherry", 7}

// 访问
print p1.first // "apple"
print p1.second // 5

// 结构化绑定
auto [name, count] = p1
print name, count

// 比较（字典序：先比 first，相等再比 second）
a = pair<int, int>{1, 5}
b = pair<int, int>{1, 3}
print a < b // false（1==1, 5>3 所以 a > b）

// 函数返回多值
function minmax(arr):
 return pair<int, int>(min_val, max_val)
auto [lo, hi] = minmax(vec)

// map insert 返回值
auto [it, ok] = mp.insert({"key", value})
if not ok:
 print "key already exists, value: " + it.second

// 在 priority_queue 中存优先级
priority_queue<pair<int, string>> pq
pq.push({3, "taskA"})
pq.push({1, "taskB"}) // 1 < 3，默认大根堆中 taskB 优先级更高
```cpp

## 相关链接

- [[../关联容器/map]] | [[../无序容器/unordered_map]]
