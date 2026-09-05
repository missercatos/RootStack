---
title: "std::vector 动态数组"
---

## 底层数据结构

连续内存的动态数组。当 size 达到 capacity 时，分配更大的内存块（通常翻倍），将所有元素整体搬迁过去，释放旧内存。扩容瞬间所有指向旧内存的迭代器、指针、引用全部失效。

```
逻辑视图:   [a] [b] [c] [d] [e] [ ] [ ] [ ]   ← size=5, capacity=8
物理地址:    0x100 0x104 0x108 0x10C 0x110 0x114 0x118 0x11C
             ──────────────────────────────────────────────
                    已使用 (size)        ─── 未使用 ───
             ─────────────────────────── capacity ─────────
```

### 扩容过程 (push_back)

```
push_back('f') → size==capacity → 触发扩容:

Step 1: 分配新内存 (capacity 翻倍)
  新内存: 0x300 ~ 0x31F (16 字节 × 2 = 32)

Step 2: 逐个搬移旧元素到新内存
  0x300: a   0x304: b   0x308: c   0x30C: d   0x310: e   0x314: f

Step 3: 释放旧内存 0x100 ~ 0x11F
```

### std::vector\<bool\> 陷阱

`vector<bool>` 不是真正的 `vector`！它用位压缩存储（每个 bool 只占 1 bit），导致：

```cpp
vector<bool> v = {true, false, true};
auto it = v.begin();
// *it 返回的是一个代理对象，不是 bool&！

bool* p = &(*it);  // 编译错误：无法取地址到 bool&
v[0] = false;      // OK，通过代理对象赋值

// 正确做法
vector<char> v2 = {1, 0, 1};  // 用 char 代替
```

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

### push_back 均摊分析

扩容时搬移 n 个元素，但 n 次 push_back 只触发约 1 次扩容：

```
n 次 push_back 的总代价:
  n 次拷贝 + 1 + 2 + 4 + 8 + ... + n
= n + (2n - 1)
= 3n - 1

均摊代价 = (3n - 1) / n ≈ O(1)
```

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

## emplace vs insert

```cpp
struct User {
    string name;
    int age;
    User(string n, int a) : name(n), age(a) {}
};

vector<User> v;

// insert: 先构造临时对象，再移动/拷贝进容器
v.insert(v.end(), User("Alice", 25));  // 构造临时 + 移动

// emplace_back: 直接在容器内存中构造，无临时对象
v.emplace_back("Bob", 30);  // 一次构造，零拷贝

// emplace_back 的优势：
// 1. 省去临时对象构造开销
// 2. 只能移动的类型也能高效插入
// 3. 参数直接转发给构造函数
```

## shrink_to_fit

```cpp
vector<int> v;
v.reserve(1000);
// ... 插入 10 个元素
// size=10, capacity=1000, 浪费 990 个 int 的空间

v.shrink_to_fit();
// 请求将 capacity 缩减到 size
// 注意：这是非绑定请求，实现可能忽略
// C++11 起标准要求
```

## 常见陷阱

| 陷阱 | 说明 |
|------|------|
| 扩容失效 | push_back 后，之前获取的迭代器/指针/引用全部失效 |
| vector\<bool\> | 非标准容器，不返回真正的引用 |
| 插入/删除迭代器 | `v.erase(it)` 后 `it` 失效，需用返回值 `it = v.erase(it)` |
| 循环中 insert | `for` 循环中 `push_back` 可能触发扩容，迭代器失效 |
| clear 不释放 | `clear()` 只改 size，不释放内存，用 `shrink_to_fit()` |

```cpp
// 错误：循环中 insert 导致未定义行为
vector<int> v = {1, 2, 3, 4, 5};
for (auto it = v.begin(); it != v.end(); ++it) {
    v.push_back(*it);  // 扩容后 it 悬垂！
}

// 正确做法
vector<int> v = {1, 2, 3, 4, 5};
size_t sz = v.size();
for (size_t i = 0; i < sz; ++i) {
    v.push_back(v[i]);  // 用下标，避免迭代器失效
}
```

## 代码示例

```cpp
// 1. 二维动态数组
int n = 3, m = 4;
vector<vector<int>> grid(n, vector<int>(m, 0));

// 2. 赋值与初始化
vector<int> a(5, 10);         // [10, 10, 10, 10, 10]
vector<int> b = {1, 2, 3};   // 拷贝初始化
vector<int> c(b.begin(), b.end()); // 迭代器范围

// 3. 排序 + 去重
vector<int> v = {3, 1, 4, 1, 5, 9, 2, 6, 5};
sort(v.begin(), v.end());
v.erase(unique(v.begin(), v.end()), v.end());
// v: [1, 2, 3, 4, 5, 6, 9]

// 4. 用 reserve 避免扩容
vector<string> words;
words.reserve(1000);
for (auto& w : input) words.push_back(w);

// 5. vector 作为缓冲区
vector<char> buf(1024);
int n = read(fd, buf.data(), buf.size());
```

## 与类似容器的比较

| 特性 | vector | deque | list | array |
|------|--------|-------|------|-------|
| 内存布局 | 连续 | 分段连续 | 节点 | 固定连续 |
| 随机访问 | O(1) | O(1) | 不支持 | O(1) |
| 尾部插入 | O(1) | O(1) | O(1) | 不支持 |
| 头部插入 | O(n) | O(1) | O(1) | 不支持 |
| 中间插入 | O(n) | O(n) | O(1) | 不支持 |
| 缓存友好 | 最佳 | 较好 | 差 | 最佳 |
| 内存开销 | 低 | 中 | 高 | 无 |

**选择建议**：绝大多数场景首选 vector，需要频繁头部操作选 deque，频繁中间插入/删除选 list。

## 力扣练习

| 题号 | 题目 | 链接 | 知识点 |
|------|------|------|--------|
| 1 | 两数之和 | https://leetcode.cn/problems/two-sum/ | vector 遍历 + 哈希 |
| 15 | 三数之和 | https://leetcode.cn/problems/3sum/ | 双指针 + 排序 |
| 26 | 删除有序数组中的重复项 | https://leetcode.cn/problems/remove-duplicates-from-sorted-array/ | 双指针原地修改 |
| 27 | 移除元素 | https://leetcode.cn/problems/remove-element/ | 双指针 |
| 33 | 搜索旋转排序数组 | https://leetcode.cn/problems/search-in-rotated-sorted-array/ | 二分查找 |
| 53 | 最大子数组和 | https://leetcode.cn/problems/maximum-subarray/ | 动态规划 + vector |
| 56 | 合并区间 | https://leetcode.cn/problems/merge-intervals/ | 排序 + 遍历 |
| 75 | 颜色分类 | https://leetcode.cn/problems/sort-colors/ | 三指针 |
| 136 | 只出现一次的数字 | https://leetcode.cn/problems/single-number/ | 异或运算 |
| 238 | 除自身以外数组的乘积 | https://leetcode.cn/problems/product-of-array-except-self/ | 前缀积 + 后缀积 |

## 相关链接

- [[../../../数据结构/D_容器_Container]]
- [[array]] | [[deque]]
