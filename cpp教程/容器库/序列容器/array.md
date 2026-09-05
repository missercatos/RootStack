---
title: "std::array 定长数组"
---

## 底层数据结构

编译期定长的连续内存数组，大小在编译时确定为 N。本质上是对 C 风格数组 `T[N]` 的封装，提供 STL 容器接口（迭代器、size、at 等），同时保持零开销。不涉及动态内存分配，不存在 capacity/reverse/resize。

## 复杂度

| 操作 | 复杂度 | 说明 |
|------|--------|------|
| operator[] | O(1) | 随机访问，无边界检查 |
| at(i) | O(1) | 随机访问，带边界检查 |
| front / back | O(1) | 首/尾元素引用 |
| fill(x) | O(n) | 将所有元素置为 x |
| swap | O(n) | 逐元素交换 |
| size / empty | O(1) | size 恒为 N |

## 关键方法

| 方法 | 说明 |
|------|------|
| a[i] / a.at(i) | 下标访问，at 抛出 out_of_range |
| a.front() / a.back() | 首/尾元素引用 |
| a.data() | 返回底层 C 数组指针 |
| a.fill(x) | 全部填充为 x |
| a.size() | 返回 N（编译期常量） |
| a.empty() | N 为 0 时返回 true |
| a.begin() / a.end() | 迭代器支持 |

## 与 vector 对比

| 特性 | array | vector |
|------|-------|--------|
| 大小 | 编译期固定 | 运行时动态 |
| 内存位置 | 栈上 | 堆上 |
| capacity/reserve | 无 | 有 |
| 作为函数参数 | 拷贝整个数组 | 通常传引用 |

## 伪代码示例

```cpp
// 创建固定大小 5 的数组，全部初始化 0
array<int, 5> arr = {1, 2, 3, 4, 5}

// 遍历
for i from 0 to arr.size() - 1:
 print arr[i]

// 范围 for 遍历
for each x in arr:
 print x

// 全部填充
arr.fill(0)

// 传给 C 接口
legacy_function(arr.data(), arr.size())
```cpp

## 相关链接

- [[../../../数据结构/D_容器_Container]]
- [[../../../数据结构/D_容器_Container]]
- [[vector]]
