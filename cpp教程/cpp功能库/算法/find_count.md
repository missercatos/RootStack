---
title: "C++ 功能库 — 查找与统计"
---

## 概述

C++ 标准库的查找与统计算法基于输入迭代器，能在任意容器上执行线性搜索和条件判断。从简单的 `find`（等值查找）到 `find_if`（谓词查找），再到 `all_of`/`any_of`/`none_of` 的全量条件判断，覆盖了日常数据检索的大部分场景。

所有算法都是 O(n) 线性复杂度，对无序数据使用。

## 核心组件

### 查找

| 组件 | 说明 |
|------|------|
| `find` | 查找第一个等于目标值的元素 |
| `find_if` | 查找第一个满足谓词的元素 |
| `find_if_not` | 查找第一个不满足谓词的元素 |
| `find_first_of` | 查找第一个属于给定集合的元素 |
| `adjacent_find` | 查找第一对相邻相等的元素 |
| `search` | 查找子序列首次出现位置 |
| `find_end` | 查找子序列末次出现位置 |

### 统计与判断

| 组件 | 说明 |
|------|------|
| `count` | 统计等于目标值的元素个数 |
| `count_if` | 统计满足谓词的元素个数 |
| `all_of` | 所有元素是否都满足谓词 |
| `any_of` | 是否存在满足谓词的元素 |
| `none_of` | 所有元素是否都不满足谓词 |

## 典型用法

### 查找

```cpp
FUNCTION demo_find:
 v = [10, 20, 30, 40, 50]

 it = FIND(v, 30)
 IF it != v.END() THEN PRINT *it // 30

 it = FIND(v, 99)
 IF it == v.END() THEN PRINT "not found"

 it = FIND_IF(v, LAMBDA(x): RETURN x > 25)
 PRINT *it // 30（第一个 >25 的元素）

 it = ADJACENT_FIND([1, 2, 3, 3, 4]) // 指向第二个 3
```cpp

### 统计

```cpp
FUNCTION demo_count:
 v = [1, 2, 3, 2, 4, 2, 5]

 PRINT COUNT(v, 2) // 3

 PRINT COUNT_IF(v, LAMBDA(x):
 RETURN x % 2 == 0 // 偶数个数
 ) // 4
```cpp

### 批量判断

```cpp
FUNCTION demo_all_any_none:
 v = [10, 20, 30, 40]

 PRINT ALL_OF(v, LAMBDA(x):
 RETURN x > 0 // 全是正数?
 ) // true

 PRINT ANY_OF(v, LAMBDA(x):
 RETURN x > 35 // 存在 >35 的?
 ) // true

 PRINT NONE_OF(v, LAMBDA(x):
 RETURN x < 0 // 全不是负数?
 ) // true
```cpp

---

- **二分搜索**: [[sort_search|sort/search]] — 有序数据用二分查找
- **修改算法**: [[modify|modify]] — `replace`/`remove`/`copy`
- **函数式**: [[../函数式/lambda|lambda]] — lambda 作为谓词
- **Ranges**: [[range|C++20 ranges]] — `FILTER` 流水线替代 `find_if` + `count_if`
- **返回目录**: 
