---
title: "template <typename T>
class vector"
---

## 底层数据结构

连续内存的动态数组。当 size 达到 capacity 时，分配更大的内存块（通常翻倍），将所有元素整体搬迁过去，释放旧内存。扩容瞬间所有指向旧内存的迭代器、指针、引用全部失效。

## 复杂度

| 操作 | 复杂度 | 说明 |
|------|--------|------|
| operator[] | O(1) | 随机访问，无边界检查 |
| at(i) | O(1) | 随机访问，带边界检查 |
| push_back | 均摊 O(1) | 尾部插入，触发扩容时为 O(n) |
| emplace_back | 均摊 O(1) | 尾部原位构造 |
| pop_back | O(1) | 尾部删除 |
| insert | O(n) | 中间插入，需移动后续元素 |
| erase | O(n) | 中间删除，需移动后续元素 |
| size / empty | O(1) | |
| clear | O(n) | 调用析构，capacity 不变 |
| reserve(n) | O(n) | 预分配容量，避免反复扩容 |
| sort | O(n log n) | 配合 sort(begin, end) |

## 关键方法

| 方法 | 说明 |
|------|------|
| v[i] / v.at(i) | 下标访问 |
| v.front() / v.back() | 首/尾元素引用 |
| v.data() | 返回底层数组指针 |
| push_back(x) | 尾部拷贝插入 |
| emplace_back(args...) | 尾部原位构造 |
| pop_back() | 尾部删除 |
| insert(it, x) | 在迭代器位置前插入 |
| erase(it) | 删除迭代器指向的元素 |
| size() / capacity() | 元素数 / 已分配容量 |
| reserve(n) / resize(n) | 预分配 / 改变 size |
| clear() | 清空元素，capacity 不变 |
| shrink_to_fit() | 请求释放多余容量 |

## 伪代码示例

```
// 创建一个空的整数向量
vector<int> v

// 在尾部逐一添加元素
loop i from 1 to 5:
    v.push_back(i)

// 预分配容量
v.reserve(100)

// 遍历与输出
for i from 0 to v.size() - 1:
    print v[i]

// 排序与去重
sort(v.begin(), v.end())
v.erase(unique(v.begin(), v.end()), v.end())

// 二维向量 (3x4 矩阵)
vector<vector<int>> mat(3, vector<int>(4, 0))
```

## 相关链接

- [[../../../数据结构/A_容器_Container]]
- [[../../../数据结构/A_容器_Container]]
- [[array]] | [[deque]]
