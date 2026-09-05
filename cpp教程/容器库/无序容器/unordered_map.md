---
title: "std::unordered_map 无序映射"
---

## 底层数据结构

**哈希表**（开链法）。每个元素是 `pair<const Key, Value>`，通过 key 的哈希值映射到桶数组。负载因子超过阈值时 rehash。`unordered_map` 的 key 唯一，`unordered_multimap` 允许重复 key。

```
哈希表结构（开链法）:

bucket[0] ──► [k1:v1] ──► [k2:v2] ──► nullptr
bucket[1] ──► nullptr
bucket[2] ──► [k3:v3] ──► nullptr
bucket[3] ──► [k4:v4] ──► [k5:v5] ──► nullptr  ← 冲突链
bucket[4] ──► nullptr

哈希函数: hash(key) % bucket_count = 桶索引

负载因子 = size / bucket_count
当 load_factor > max_load_factor() 时触发 rehash:
  1. 分配更大的桶数组（通常翻倍）
  2. 重新计算所有元素的桶位置
  3. 移动元素到新桶
```

## 碰撞解决

### 开链法（Chaining）— STL 默认

每个桶是一个链表（或红黑树，C++ 有 `__cpp_lib_unordered_map_only_flatten` 趋势）：

```
hash("apple") % 8 = 3 → 桶 3
hash("banana") % 8 = 3 → 桶 3 (冲突！)

bucket[3]: ──► ["apple":5] ──► ["banana":3] ──► nullptr
```

### 线性探测（Open Addressing）— 了解

```
hash("apple") % 8 = 3 → 桶 3 占用 → 桶 4 → 桶 5 ...

bucket: [ ] [ ] [ ] [apple] [banana] [cherry] [ ] [ ]
         0   1   2     3       4         5      6   7
```

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
| insert({k, v}) | 仅当不存在时插入，返回 pair\<it,bool\> |
| insert_or_assign(k, v) | C++17，存在则覆盖 |
| emplace(k, v) | 原位构造 |
| try_emplace(k, v) | C++17，不存在时原位构造 |
| erase(k) | 按 key 删除，返回删除个数 |
| erase(it) | 按迭代器删除 |
| find(k) | 查找，返回迭代器 |
| count(k) | 出现次数 |
| contains(k) | C++20，直接返回 bool |
| equal_range(k) | 返回 pair\<it, it\>（multimap 中重要） |

## 桶接口（Bucket Interface）

```cpp
unordered_map<string, int> m = {{"a", 1}, {"b", 2}, {"c", 3}};

// 查看桶信息
m.bucket_count();     // 桶总数（实现定义，通常为质数）
m.size();             // 元素总数
m.load_factor();      // size / bucket_count
m.max_load_factor();  // 最大负载因子，默认 1.0

// 指定桶
m.bucket("a");  // "a" 在哪个桶
m.bucket_count();  // 桶总数

// 预分配（避免频繁 rehash）
m.reserve(100);  // 至少容纳 100 个元素，减少 rehash 次数

// 手动 rehash
m.rehash(256);  // 设置桶数量为 256
```

## 自定义 hasher

```cpp
// 自定义类型做 key
struct Point {
    int x, y;
    bool operator==(const Point& o) const {
        return x == o.x && y == o.y;
    }
};

struct PointHash {
    size_t operator()(const Point& p) const {
        return hash<int>()(p.x) ^ (hash<int>()(p.y) << 16);
    }
};

unordered_map<Point, string, PointHash> m;
m[{1, 2}] = "origin";

// 使用 std::hash 为组合类型
struct PairHash {
    template <class T1, class T2>
    size_t operator()(const pair<T1,T2>& p) const {
        auto h1 = hash<T1>{}(p.first);
        auto h2 = hash<T2>{}(p.second);
        return h1 ^ (h2 << 32);
    }
};

unordered_map<pair<int,int>, string, PairHash> grid;
grid[{0, 0}] = "start";
```

## 代码示例

```cpp
// 1. 频率统计
vector<string> words = {"apple", "banana", "apple", "cherry", "banana", "apple"};
unordered_map<string, int> freq;
for (auto& w : words) freq[w]++;
// freq: {"apple": 3, "banana": 2, "cherry": 1}

// 2. 两数之和
vector<int> nums = {2, 7, 11, 15};
int target = 9;
unordered_map<int, int> seen;
for (int i = 0; i < nums.size(); i++) {
    if (seen.count(target - nums[i])) {
        return {seen[target - nums[i]], i};
    }
    seen[nums[i]] = i;
}

// 3. 字母异位词分组
vector<string> strs = {"eat", "tea", "tan", "ate", "nat", "bat"};
unordered_map<string, vector<string>> groups;
for (auto& s : strs) {
    string key = s;
    sort(key.begin(), key.end());
    groups[key].push_back(s);
}

// 4. 遍历顺序不保证
unordered_map<string, int> m = {{"a", 1}, {"b", 2}};
for (auto& [k, v] : m) {
    cout << k << ": " << v << endl;  // 顺序不确定
}
```

## 常见陷阱

| 陷阱 | 说明 |
|------|------|
| 迭代器顺序 | 遍历顺序不固定，不要依赖 |
| operator[] 插入 | key 不存在时插入默认值，用 count/find 先检查 |
| rehash 失效 | rehash 会使所有迭代器失效 |
| 自定义 key | 需提供 hash 和 operator== |
| 性能退化 | 大量碰撞时退化到 O(n) |
| max_load_factor | 调小可减少碰撞，但增加内存 |

## 与 map 的选择

| 特性 | unordered_map | map |
|------|--------------|-----|
| 平均查找 | O(1) | O(log n) |
| 最坏查找 | O(n) | O(log n) |
| 内存开销 | 中 | 高（树节点） |
| 有序遍历 | 不支持 | 支持 |
| 范围查询 | 不支持 | 支持 |
| 适用场景 | 快速查找，无序 | 需要有序/范围查询 |

## 力扣练习

| 题号 | 题目 | 链接 | 知识点 |
|------|------|------|--------|
| 1 | 两数之和 | https://leetcode.cn/problems/two-sum/ | 哈希表查找 |
| 49 | 字母异位词分组 | https://leetcode.cn/problems/group-anagrams/ | 排序做 key |
| 128 | 最长连续序列 | https://leetcode.cn/problems/longest-consecutive-sequence/ | 哈希集合 |
| 138 | 随机链表的复制 | https://leetcode.cn/problems/copy-list-with-random-pointer/ | 哈希映射节点 |
| 146 | LRU 缓存 | https://leetcode.cn/problems/lru-cache/ | 哈希表 + 链表 |
| 242 | 有效的字母异位词 | https://leetcode.cn/problems/valid-anagram/ | 频率统计 |
| 347 | 前 K 个高频元素 | https://leetcode.cn/problems/top-k-frequent-elements/ | 哈希 + 堆 |
| 383 | 赎金信 | https://leetcode.cn/problems/ransom-note/ | 字符频率 |
| 560 | 和为 K 的子数组 | https://leetcode.cn/problems/subarray-sum-equals-k/ | 前缀和 + 哈希 |
| 706 | 设计哈希映射 | https://leetcode.cn/problems/design-hashmap/ | 手写哈希表 |

## 相关链接

- [[../../../数据结构/N_哈希表_HashTable]]
- [[../关联容器/map]] | [[../其他/pair]]
