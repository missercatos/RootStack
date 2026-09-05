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

## std::sort 内部原理：内省排序

`std::sort` 使用**内省排序（introsort）**，结合了三种排序的优点：

```
┌─────────────────────────────────────────┐
│              introsort                   │
├─────────────────────────────────────────┤
│  1. 快排 (quicksort)                     │
│     - 平均 O(n log n)，缓存友好          │
│     - 递归深度超过 2*log(n) 时切换       │
├─────────────────────────────────────────┤
│  2. 堆排序 (heapsort)                    │
│     - 最坏 O(n log n)，防止退化          │
│     - 快排递归过深时启用                  │
├─────────────────────────────────────────┤
│  3. 插入排序 (insertion sort)            │
│     - 小数组 (≤16) 效率最高              │
│     - 快排分区到小区间时切换              │
└─────────────────────────────────────────┘
```

**为什么不用纯快排？** 快排最坏情况 O(n²)（已排序数组），内省排序通过检测递归深度自动切换堆排序，保证最坏 O(n log n)。

## 比较器要求

比较器必须满足**严格弱序（strict weak ordering）**：

```cpp
// 正确的比较器
auto comp = [](int a, int b) { return a < b; };

// 错误的比较器（不满足严格弱序）
auto bad_comp = [](int a, int b) { return a <= b; };  // 等价时返回 true

// 比较器要求：
// 1. 反自反性: comp(x, x) 必须为 false
// 2. 非对称性: comp(x, y) 为 true → comp(y, x) 必须为 false
// 3. 传递性: comp(x, y) && comp(y, z) → comp(x, z)

// 自定义比较器示例：按字符串长度排序
std::vector<std::string> words = {"banana", "apple", "fig"};
std::sort(words.begin(), words.end(), [](const std::string& a, const std::string& b) {
    return a.size() < b.size();  // 按长度升序
});
// 结果: ["fig", "apple", "banana"]
```

## 典型用法

### 排序

```cpp
// 基本排序
std::vector<int> v = {5, 2, 8, 1, 9, 3};
std::sort(v.begin(), v.end());               // [1, 2, 3, 5, 8, 9]
std::sort(v.begin(), v.end(), std::greater<>()); // 降序 [9, 8, 5, 3, 2, 1]

// 自定义比较器
std::sort(v.begin(), v.end(), [](int a, int b) { return a > b; });

// 按结构体字段排序
struct Person { std::string name; int age; };
std::vector<Person> people = {{"Alice", 30}, {"Bob", 25}, {"Carol", 35}};
std::sort(people.begin(), people.end(), [](const Person& a, const Person& b) {
    return a.age < b.age;  // 按年龄升序
});

// 稳定排序：保持相等元素的相对顺序
std::stable_sort(people.begin(), people.end(), [](const Person& a, const Person& b) {
    return a.age < b.age;
});
```

### 二分搜索

```cpp
// 必须已排序！
std::vector<int> v = {1, 2, 3, 3, 3, 5, 8};

// 是否存在
if (std::binary_search(v.begin(), v.end(), 3)) {
    // 存在
}

// lower_bound: 第一个 >= target 的位置
auto lb = std::lower_bound(v.begin(), v.end(), 3);
std::cout << std::distance(v.begin(), lb) << "\n";  // 2

// upper_bound: 第一个 > target 的位置
auto ub = std::upper_bound(v.begin(), v.end(), 3);
std::cout << std::distance(v.begin(), ub) << "\n";  // 5

// 统计出现次数
auto count = std::distance(lb, ub);  // 3

// equal_range: 同时获取 lower 和 upper
auto [lo, hi] = std::equal_range(v.begin(), v.end(), 3);
// lo = lower_bound(3), hi = upper_bound(3)

// 用于自定义比较器的二分搜索
std::vector<Person> people = {{"Alice", 25}, {"Bob", 30}, {"Carol", 35}};
auto it = std::lower_bound(people.begin(), people.end(), 30,
    [](const Person& p, int age) { return p.age < age; });
```

### nth_element —— 快速选择

```cpp
// 使第 n 个位置处于排序后的正确位置
// 左边都 ≤ 它，右边都 ≥ 它（但内部无序）
std::vector<int> v = {7, 1, 3, 9, 5, 2, 8, 4, 6};

// 找第 5 小的元素
std::nth_element(v.begin(), v.begin() + 4, v.end());
std::cout << v[4] << "\n";  // 5

// 实际应用：找中位数
std::nth_element(v.begin(), v.begin() + v.size() / 2, v.end());
int median = v[v.size() / 2];

// 找前 k 个最小元素（不要求有序）
std::nth_element(v.begin(), v.begin() + k, v.end());
// v[0..k) 包含前 k 个最小元素（无序）

// 与 partial_sort 的区别：
// nth_element: O(n) 平均，左边无序
// partial_sort: O(n log k)，前 k 个有序
```

### partial_sort —— 部分排序

```cpp
// 只排序前 k 个元素
std::vector<int> v = {7, 1, 3, 9, 5, 2, 8, 4, 6};

// 排序前 3 个最小元素
std::partial_sort(v.begin(), v.begin() + 3, v.end());
// v = [1, 2, 3, ...]  前 3 个有序，其余未指定

// 实际应用：找 Top-K
std::partial_sort(v.begin(), v.begin() + 5, v.end(), std::greater<>());
// 前 5 个最大元素有序
```

### 自定义对象排序

```cpp
// 多字段排序
struct Student {
    std::string name;
    int score;
    int age;
};

std::vector<Student> students = {{"Alice", 90, 20}, {"Bob", 85, 22}, {"Carol", 90, 21}};

// 按分数降序，分数相同按年龄升序
std::sort(students.begin(), students.end(), [](const Student& a, const Student& b) {
    if (a.score != b.score) return a.score > b.score;
    return a.age < b.age;
});

// 使用 tie 进行多字段排序
std::sort(students.begin(), students.end(), [](const Student& a, const Student& b) {
    return std::tie(-a.score, a.age) < std::tie(-b.score, b.age);
});
```

## 常见陷阱与最佳实践

1. **未排序就二分搜索**：`lower_bound` 等要求输入已排序，否则结果未定义
2. **比较器不满足严格弱序**：导致未定义行为（可能崩溃）
3. **`sort` 不稳定**：需要稳定排序时用 `stable_sort`
4. **`nth_element` vs `partial_sort`**：只要 Top-K 不要有序用 `nth_element`（O(n)），要有序用 `partial_sort`（O(n log k)）
5. **lambda 作为比较器优先于函数指针**：编译器更容易内联

## 力扣练习

| 题号 | 题目 | 链接 | 知识点 |
|------|------|------|--------|
| 912 | 排序数组 | https://leetcode.cn/problems/sort-an-array/ | sort 基础应用 |
| 215 | 数组中的第K个最大元素 | https://leetcode.cn/problems/kth-largest-element-in-an-array/ | nth_element 快速选择 |
| 347 | 前 K 个高频元素 | https://leetcode.cn/problems/top-k-frequent-elements/ | partial_sort / 堆排序 |
| 75 | 颜色分类 | https://leetcode.cn/problems/sort-colors/ | 三路分区排序 |
| 148 | 排序链表 | https://leetcode.cn/problems/sort-list/ | 归并排序 |
| 56 | 合并区间 | https://leetcode.cn/problems/merge-intervals/ | 排序 + 线性扫描 |
| 179 | 最大数 | https://leetcode.cn/problems/largest-number/ | 自定义比较器 |
| 493 | 翻转对 | https://leetcode.cn/problems/reverse-pairs/ | 归并排序变体 |
| 327 | 区间和的个数 | https://leetcode.cn/problems/count-of-range-sum/ | 归并排序 + 计数 |
| 23 | 合并 K 个升序链表 | https://leetcode.cn/problems/merge-k-sorted-lists/ | 优先队列 / 分治 |
| 315 | 计算右侧小于当前元素的个数 | https://leetcode.cn/problems/count-of-smaller-numbers-after-self/ | 归并排序 + 索引 |
| 4 | 寻找两个正序数组的中位数 | https://leetcode.cn/problems/median-of-two-sorted-arrays/ | 二分搜索 |
| 33 | 搜索旋转排序数组 | https://leetcode.cn/problems/search-in-rotated-sorted-array/ | 二分搜索变体 |
| 74 | 搜索二维矩阵 | https://leetcode.cn/problems/search-a-2d-matrix/ | 二分搜索 |
| 35 | 搜索插入位置 | https://leetcode.cn/problems/search-insert-position/ | lower_bound |
| 34 | 在排序数组中查找元素的第一个和最后一个位置 | https://leetcode.cn/problems/find-first-and-last-position-of-element-in-sorted-array/ | equal_range |

---

- **查找算法**: [[find_count|find / count]] — 线性查找与统计
- **修改算法**: [[modify|modify]] — `copy`/`replace`/`unique`
- **Ranges**: [[range|C++20 ranges]] — 管道式排序
- **排序原理**: 快排/归并/堆排经典算法
- **返回目录**:
