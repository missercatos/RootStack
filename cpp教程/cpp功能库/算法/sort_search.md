---
title: "C++ 功能库 — 排序与搜索"
---

## 概述

C++ 标准库的排序和搜索算法通过迭代器解耦容器和算法——同一个 `sort` 可以作用于 array、vector、deque 等任何随机访问迭代器的容器。`sort` 使用内省排序（快排+堆排混合），保证 O(n log n) 且不会退化。二分搜索系列（`binary_search`、`lower_bound`、`upper_bound`、`equal_range`）要求输入有序。

## 核心组件

### 排序

| 组件 | 复杂度 | 说明 |
|------|--------|------|
| `sort` | O(n log n) | 内省排序，不稳定 |
| `stable_sort` | O(n log n) | 归并排序，稳定 |
| `partial_sort` | O(n log k) | 前 k 个最小元素有序 |
| `nth_element` | O(n) 平均 | 使第 n 位处于排序后位置，左边都 ≤ 它，右边都 ≥ 它 |
| `is_sorted` | O(n) | 判断是否已排序 |

### 二分搜索（需要有序输入）

| 组件 | 复杂度 | 说明 |
|------|--------|------|
| `binary_search` | O(log n) | 是否存在，返回 bool |
| `lower_bound` | O(log n) | 第一个 ≥ target 的位置 |
| `upper_bound` | O(log n) | 第一个 > target 的位置 |
| `equal_range` | O(log n) | 返回 `[lower, upper)` 对 |

## 典型用法

### 排序

```
FUNCTION demo_sort:
 v = [5, 2, 8, 1, 9, 3]

 SORT(v) // [1, 2, 3, 5, 8, 9]
 SORT(v, GREATER()) // 降序: [9, 8, 5, 3, 2, 1]

 SORT(v, LAMBDA(a, b): RETURN a > b) // 自定义比较器

 SORT(people, LAMBDA(p, q): // 按结构体字段排序
 RETURN p.age < q.age
 )
```

### 二分搜索

```
FUNCTION demo_binary_search:
 v = [1, 2, 3, 3, 3, 5, 8] // 必须已排序

 IF BINARY_SEARCH(v, 3) THEN
 lb = LOWER_BOUND(v, 3) // 下标 2（第一个 3）
 ub = UPPER_BOUND(v, 3) // 下标 5（第一个 > 3 的位置）
 count = ub - lb // 3 的个数: 3
 END IF

 [lo, hi] = EQUAL_RANGE(v, 3) // 返回 pair<迭代器>
 PRINT hi - lo // 3
```

### nth_element —— 部分排序

```
FUNCTION demo_nth:
 v = [7, 1, 3, 9, 5, 2, 8, 4, 6]

 NTH_ELEMENT(v, v.BEGIN() + 4) // 第 5 小的元素到位

 // v 变为: [2, 1, 3, 4, 5, 7, 8, 9, 6]
 // left ≤ 5 ≤ right（左右内部无序）
 PRINT v[4] // 5
```

---

- **查找算法**: [[find_count|find / count]] — 线性查找与统计
- **修改算法**: [[modify|modify]] — `copy`/`replace`/`unique`
- **Ranges**: [[range|C++20 ranges]] — 管道式排序
- **排序原理**: 快排/归并/堆排经典算法
- **返回目录**: 
