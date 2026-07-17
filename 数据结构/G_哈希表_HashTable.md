# G 哈希表 HashTable

建议先阅读: [[A_容器_Container|A 容器 Container]]

---

## 原理

哈希表（Hash Table）通过哈希函数将键映射到数组的某个位置，实现 O(1) 平均时间复杂度的插入、删除和查找操作。

### 核心组件

- **哈希函数**: 将任意大小的键映射到固定范围的整数（数组索引），需计算快、分布均匀、确定性
- **桶数组**: 存储键值对的连续内存
- **冲突解决**: 处理不同键映射到同一位置的策略

### 冲突解决方法

1. **链地址法（拉链法）**: 每个桶维护一个链表，冲突的键值对放入同一桶的链表中。C++ unordered_map 默认使用此方法
2. **开放地址法**: 发生冲突时寻找下一个空桶：
   - 线性探测: `index = (hash + i) % size`
   - 二次探测: `index = (hash + i^2) % size`
   - 双重哈希: `index = (hash1 + i * hash2) % size`

### 时间复杂度

| 操作 | 平均 | 最坏 |
|------|------|------|
| 插入 | O(1) | O(n) |
| 删除 | O(1) | O(n) |
| 查找 | O(1) | O(n) |

空间复杂度: O(n + bucket_count)，负载因子（元素数/桶数）触发 rehash。

---

## 实现

### 链地址法 HashMap

```cpp
#include <iostream>
#include <vector>
#include <list>
#include <functional>

template <typename K, typename V>
class HashMap {
private:
    struct Entry {
        K key;
        V value;
        Entry(const K& k, const V& v) : key(k), value(v) {}
    };

    std::vector<std::list<Entry>> buckets;
    size_t num_elements;
    float max_load_factor;

    size_t getBucketIndex(const K& key) const {
        return std::hash<K>{}(key) % buckets.size();
    }

    void rehash(size_t new_bucket_count) {
        auto old_buckets = std::move(buckets);
        buckets.resize(new_bucket_count);
        num_elements = 0;
        for (auto& bucket : old_buckets)
            for (auto& entry : bucket)
                insert(entry.key, entry.value);
    }

public:
    HashMap(size_t initial_size = 16)
        : buckets(initial_size), num_elements(0), max_load_factor(0.75) {}

    void insert(const K& key, const V& value) {
        if ((num_elements + 1.0) / buckets.size() > max_load_factor)
            rehash(buckets.size() * 2);

        size_t idx = getBucketIndex(key);
        for (auto& entry : buckets[idx]) {
            if (entry.key == key) {
                entry.value = value; // 更新
                return;
            }
        }
        buckets[idx].emplace_back(key, value);
        ++num_elements;
    }

    V* find(const K& key) {
        size_t idx = getBucketIndex(key);
        for (auto& entry : buckets[idx])
            if (entry.key == key)
                return &entry.value;
        return nullptr;
    }

    bool remove(const K& key) {
        size_t idx = getBucketIndex(key);
        auto& bucket = buckets[idx];
        for (auto it = bucket.begin(); it != bucket.end(); ++it) {
            if (it->key == key) {
                bucket.erase(it);
                --num_elements;
                return true;
            }
        }
        return false;
    }

    V& operator[](const K& key) {
        V* found = find(key);
        if (found) return *found;
        insert(key, V{});
        return *find(key);
    }

    size_t size() const { return num_elements; }
    bool empty() const { return num_elements == 0; }
};
```

### 字符串哈希

```cpp
#include <string>

// BKDR Hash
size_t bkdrHash(const std::string& s) {
    size_t hash = 0;
    size_t seed = 131; // 31, 131, 1313 等
    for (char c : s)
        hash = hash * seed + c;
    return hash;
}

// 多项式滚动哈希（前缀哈希，O(1) 获取子串哈希）
struct StringHasher {
    using ull = unsigned long long;
    static const ull P = 131;
    std::vector<ull> h, p;

    StringHasher(const std::string& s) : h(s.size() + 1), p(s.size() + 1) {
        p[0] = 1;
        for (int i = 0; i < s.size(); ++i) {
            h[i + 1] = h[i] * P + s[i];
            p[i + 1] = p[i] * P;
        }
    }

    // 子串 s[l..r] 的哈希值
    ull getHash(int l, int r) {
        return h[r + 1] - h[l] * p[r - l + 1];
    }
};
```

---

## STL 使用

```cpp
#include <unordered_map>
#include <unordered_set>
#include <string>
#include <iostream>

int main() {
    // unordered_map
    std::unordered_map<std::string, int> um;
    um["apple"] = 5;
    um["banana"] = 3;
    um.insert({"cherry", 8});
    um.emplace("date", 2);

    auto it = um.find("apple");
    if (it != um.end())
        std::cout << it->first << ": " << it->second << std::endl;

    um.erase("banana");
    std::cout << "count: " << um.count("apple") << std::endl;

    // 桶接口
    std::cout << "bucket_count: " << um.bucket_count() << std::endl;
    std::cout << "load_factor: " << um.load_factor() << std::endl;

    // 预留空间
    um.reserve(200);  // 设置桶数使负载因子合理
    um.rehash(100);    // 直接设置桶数

    // unordered_set
    std::unordered_set<int> us = {3, 1, 4, 1, 5};
    us.insert(9);
    for (int x : us) std::cout << x << " "; // 无序输出

    // 自定义哈希
    struct Person { std::string name; int age; };
    struct PersonHash {
        size_t operator()(const Person& p) const {
            return std::hash<std::string>{}(p.name) ^
                   (std::hash<int>{}(p.age) << 1);
        }
    };
    struct PersonEqual {
        bool operator()(const Person& a, const Person& b) const {
            return a.name == b.name && a.age == b.age;
        }
    };
    std::unordered_set<Person, PersonHash, PersonEqual> people;

    return 0;
}
```

---

## 应用场景

- **缓存系统**: O(1) 查找，如 LRU 缓存（哈希表 + 双向链表）
- **词频统计**: 用 unordered_map<string, int> 统计文本中各单词出现次数
- **去重**: 用 unordered_set 快速判重
- **两数之和**: O(n) 一遍扫描，哈希表记录已遍历元素

---

## 练习

| 题号 | 题目 | 难度 | 知识点 |
|------|------|------|--------|
| P3370 | 字符串哈希 | 普及 | 哈希函数、字符串去重 |
| P3405 | Cities and States | 普及+ | 哈希计数 |
| P4305 | 字符串哈希 | 普及 | 滚动哈希 |
