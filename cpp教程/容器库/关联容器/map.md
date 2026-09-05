---
title: "std::map 有序映射"
---

## 底层数据结构

**红黑树**（自平衡二叉搜索树）。每个元素是 `pair<const Key, Value>`，按 key 自动升序排列。`map` 的 key 唯一，`multimap` 允许重复 key。树的高度始终为 O(log n)，支持按 key 范围查询（lower_bound / upper_bound）。

```
红黑树示例（简化）:

            [B]          ← 黑色
           /   \
         [R]   [B]       ← 红色/黑色
         / \     \
       [B] [B]   [R]
       /     \     \
     [R]     [R]   [B]

性质:
1. 每个节点是红色或黑色
2. 根节点是黑色
3. 红色节点的子节点必须是黑色
4. 任意节点到叶子的黑色节点数相同
5. 保证树高 ≤ 2·log₂(n+1)

节点结构:
┌──────────────────────────────┐
│  color │ parent │ left │right│
│        │   key  │ value│     │
└──────────────────────────────┘
```

## 复杂度

| 操作 | 复杂度 | 说明 |
|------|--------|------|
| operator[] | O(log n) | key 不存在时插入默认值 |
| at(k) | O(log n) | key 不存在时抛出 out_of_range |
| insert({k,v}) | O(log n) | 已存在则失败，返回 pair\<it,bool\> |
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

## lower_bound 与 upper_bound

```cpp
map<int, string> m = {{1, "a"}, {3, "c"}, {5, "e"}, {7, "g"}};

// lower_bound(3): 第一个 key >= 3 → 指向 {3, "c"}
// upper_bound(3): 第一个 key > 3  → 指向 {5, "e"}
// equal_range(3): [lower, upper) = [{3,"c"}, {5,"e"}) → 只有 {3,"c"}

// 范围查询：所有 key 在 [2, 6] 之间的元素
for (auto it = m.lower_bound(2); it != m.upper_bound(6); ++it) {
    cout << it->first << ": " << it->second << endl;
}
// 输出: 3: c, 5: e

// count 使用
if (m.count(3)) {  // map 中 count 恒为 0 或 1
    cout << "found" << endl;
}
```

## multimap 用法

```cpp
multimap<string, int> mm;
mm.insert({"apple", 5});
mm.insert({"banana", 3});
mm.insert({"apple", 8});   // 允许重复 key

// equal_range 获取同一 key 的所有值
auto [lo, hi] = mm.equal_range("apple");
for (auto it = lo; it != hi; ++it) {
    cout << it->second << " ";  // 5 8
}

// lower_bound + upper_bound 手动遍历
auto it = mm.lower_bound("apple");
auto end = mm.upper_bound("apple");
while (it != end) {
    cout << it->second << " ";
    ++it;
}
```

## 结构化绑定与 map

```cpp
map<string, int> m = {{"apple", 5}, {"banana", 3}};

// C++17 结构化绑定
for (const auto& [key, value] : m) {
    cout << key << ": " << value << endl;
}

// C++20 contains
if (m.contains("apple")) {
    cout << "found" << endl;
}

// C++17 insert_or_assign
m.insert_or_assign("cherry", 7);  // 存在则覆盖

// C++17 try_emplace
m.try_emplace("apple", 99);  // 已存在，不插入
m.try_emplace("date", 10);   // 不存在，构造插入
```

## 代码示例

```cpp
// 1. 频率统计
string s = "hello world";
map<char, int> freq;
for (char c : s) freq[c]++;
// freq: {' ': 1, 'd': 1, 'e': 1, 'h': 1, 'l': 3, 'o': 2, 'r': 1, 'w': 1}

// 2. 按 value 排序（转换为 vector）
vector<pair<string, int>> vec(m.begin(), m.end());
sort(vec.begin(), vec.end(),
     [](const auto& a, const auto& b) { return a.second > b.second; });

// 3. 自定义比较器
map<string, int, greater<string>> m2;  // 降序
m2["apple"] = 5;
m2["banana"] = 3;
// 遍历顺序: banana, apple

// 4. map 做集合（利用 count）
set<string> seen;
for (auto& [k, v] : m) {
    if (!seen.count(k)) {
        // 处理
    }
}
```

## 常见陷阱

| 陷阱 | 说明 |
|------|------|
| operator[] 插入 | `m[key]` 在 key 不存在时会**插入默认值**，可能非预期 |
| 迭代器有序 | map 遍历是按 key 有序的，不是插入顺序 |
| 不能修改 key | key 是 const，直接改会编译错误 |
| value 可能被修改 | `m[key]` 返回引用，可直接修改 |
| 性能不如 unordered_map | 有序性有开销，O(log n) vs O(1) |

## 与 unordered_map 的选择

| 特性 | map | unordered_map |
|------|-----|---------------|
| 内存开销 | 较高（红黑树节点） | 中等（哈希表 + 链表） |
| 查找 | O(log n) | 均摊 O(1) |
| 有序性 | 有 | 无 |
| 最坏情况 | O(log n) | O(n) |
| 自定义 key | 需 operator< 或 Compare | 需 hash + operator== |
| 适用场景 | 需要有序遍历/范围查询 | 只需快速查找 |

## 力扣练习

| 题号 | 题目 | 链接 | 知识点 |
|------|------|------|--------|
| 1 | 两数之和 | https://leetcode.cn/problems/two-sum/ | 哈希表查找 |
| 3 | 无重复字符的最长子串 | https://leetcode.cn/problems/longest-substring-without-repeating-characters/ | 滑动窗口 + map |
| 23 | 合并 K 个升序链表 | https://leetcode.cn/problems/merge-k-sorted-lists/ | 优先队列 |
| 49 | 字母异位词分组 | https://leetcode.cn/problems/group-anagrams/ | map 作为键 |
| 128 | 最长连续序列 | https://leetcode.cn/problems/longest-consecutive-sequence/ | 哈希集合 |
| 146 | LRU 缓存 | https://leetcode.cn/problems/lru-cache/ | map + 链表 |
| 238 | 除自身以外数组的乘积 | https://leetcode.cn/problems/product-of-array-except-self/ | 前缀/后缀 |
| 347 | 前 K 个高频元素 | https://leetcode.cn/problems/top-k-frequent-elements/ | map + 堆 |
| 560 | 和为 K 的子数组 | https://leetcode.cn/problems/subarray-sum-equals-k/ | 前缀和 + map |
| 706 | 设计哈希映射 | https://leetcode.cn/problems/design-hashmap/ | 哈希表实现 |

## 相关链接

- [[../../../数据结构/J_树_Tree_BST_AVL]]
- [[../无序容器/unordered_map]] | [[../其他/pair]]
