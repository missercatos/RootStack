## ==========================================================================
STL 容器速通 — unordered_set & unordered_multiset (无序集合)
## ==========================================================================

unordered_set 基于哈希表，元素不排序，平均 O(1) 的插入/删除/查找。unordered_multiset 允许重复。

## --------------------------------------------------------------------------
## 一、适用场景
## --------------------------------------------------------------------------

| 场景 | 说明 |
|------|------|
| 快速判重 | O(1) 判定元素是否出现过 |
| 集合交集/并集/差集 | 高频繁查找时比 set 快 |
| 无限内存中的缓存 | 已经访问过的节点 ID 标记 |
| 不需要有序的场景 | 有排序需求请用 set |

## --------------------------------------------------------------------------
## 二、声明与初始化
## --------------------------------------------------------------------------

```cpp
#include <unordered_set>
using namespace std;

unordered_set<int> us1;                    // 空
unordered_set<int> us2 = {3, 1, 4, 1, 5}; // 去重: {3, 1, 4, 5} 无序
unordered_set<int> us3(100);               // 指定桶数（预留）
unordered_set<int> us4(us2.begin(), us2.end());

unordered_multiset<int> ums;               // 允许重复
unordered_multiset<int> ums2 = {3, 1, 4, 1, 5}; // {1, 1, 3, 4, 5} 无序

// 自定义类型的 unordered_set 需要提供哈希函数和等值判断
struct Node {
    int x, y;
    bool operator==(const Node& o) const { return x == o.x && y == o.y; }
};
struct HashNode {
    size_t operator()(const Node& n) const { return n.x * 131 + n.y; }
};
unordered_set<Node, HashNode> us5;
```

## --------------------------------------------------------------------------
## 三、成员函数总览
## --------------------------------------------------------------------------

### 普通操作

| 函数 | 说明 |
|------|------|
| `us.size()` | 元素个数 |
| `us.empty()` | 是否为空 |
| `us.insert(x)` | 插入元素，返回 pair<iterator, bool> |
| `us.emplace(args...)` | 原位构造 |
| `us.erase(it)` | 删除迭代器 |
| `us.erase(x)` | 按值删除 |
| `us.erase(first, last)` | 删除区间 |
| `us.clear()` | 清空 |
| `us.find(x)` | 查找，返回迭代器；未找到返回 end() |
| `us.count(x)` | 元素个数（unordered_set 中 ≤ 1） |
| `us.contains(x)` | 是否存在 (C++20) |
| `us.begin()` / `us.end()` | 迭代器（遍历顺序不可控） |

### 桶相关

| 函数 | 说明 |
|------|------|
| `us.bucket_count()` | 当前桶数 |
| `us.max_bucket_count()` | 最大桶数 |
| `us.bucket_size(n)` | 第 n 个桶的元素数 |
| `us.bucket(x)` | 元素 x 属于哪个桶 |
| `us.load_factor()` | 负载因子 = size / bucket_count |
| `us.max_load_factor()` | 获取/设置最大负载因子 |
| `us.rehash(n)` | 重新设置桶数 ≥ n |
| `us.reserve(n)` | 预留空间容纳至少 n 个元素 |

## --------------------------------------------------------------------------
## 四、洛谷实战
## --------------------------------------------------------------------------

### P4305 [JLOI2011] 不重复数字

```cpp
#include <iostream>
#include <unordered_set>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(0);
    int T;
    cin >> T;
    while (T--) {
        int n;
        cin >> n;
        unordered_set<int> seen;
        for (int i = 0, x; i < n; i++) {
            cin >> x;
            if (!seen.count(x)) {
                seen.insert(x);
                cout << x << " ";
            }
        }
        cout << endl;
    }
    return 0;
}
```

### P3405 [USACO16DEC] Cities and States S

```cpp
// 给出 N 个城市和所在州代码（大写两位字母），求特殊匹配的对数
#include <iostream>
#include <unordered_map>
using namespace std;

int main() {
    int n, ans = 0;
    cin >> n;
    unordered_map<string, int> cnt;
    for (int i = 0; i < n; i++) {
        string city, state;
        cin >> city >> state;
        string pre = city.substr(0, 2);
        if (pre != state)
            ans += cnt[state + pre]; // 找互补对
        cnt[pre + state]++;
    }
    cout << ans << endl;
    return 0;
}
// 本题虽用 unordered_map，但查找部分和 unordered_set 相同模式
```

### P1102 A-B 数对（unordered_map 版本）

```cpp
#include <iostream>
#include <unordered_map>
using namespace std;

int main() {
    int n, c;
    long long ans = 0;
    unordered_map<int, int> cnt;
    cin >> n >> c;
    for (int i = 0, x; i < n; i++) {
        cin >> x;
        cnt[x]++;
    }
    for (auto [k, v] : cnt) {
        if (cnt.count(k + c))
            ans += (long long)v * cnt[k + c];
    }
    cout << ans << endl;
    return 0;
}
```

## ==========================================================================
### 📝 章节测试
## ==========================================================================

> [!question] 判断题 1
> unordered_set 的底层数据结构是哈希表。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: unordered_set 使用哈希表（散列表）实现，通过哈希函数确定元素存储位置。

> [!question] 判断题 2
> unordered_set 中的元素是有序的。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: unordered_set 不保证元素顺序，遍历顺序取决于哈希值和桶分布。

> [!question] 判断题 3
> unordered_set 的平均查找时间复杂度是 O(1)。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: 哈希表通过哈希函数直接定位桶，平均情况下查找、插入、删除都是 O(1)。

> [!question] 判断题 4
> unordered_set 的最坏情况查找时间复杂度是 O(n)。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: 当所有元素哈希到同一个桶（严重冲突）时，退化为链表遍历，最坏 O(n)。

> [!question] 判断题 5
> unordered_set 支持 `lower_bound()` 操作。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: unordered_set 无序，不支持 lower_bound/upper_bound。这些是有序容器（set）的操作。

> [!question] 判断题 6
> 自定义类型放入 unordered_set 需要提供哈希函数和 `==` 运算符。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: 哈希表需要哈希函数计算桶位置，需要 == 判断元素是否相同。

> [!question] 判断题 7
> `unordered_set<int> us = {3,1,4,1,5};` 之后 us 中有 4 个元素。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: unordered_set 不允许重复，1 只保留一个，共 4 个元素 {3,1,4,5}。

> [!question] 判断题 8
> `rehash(n)` 可以手动调整桶的数量。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: rehash(n) 将桶数设置为至少 n，可用于预分配减少重哈希次数。

> [!question] 判断题 9
> unordered_multiset 中 `erase(x)` 只删除一个值为 x 的元素。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: `erase(x)` 删除所有值为 x 的元素。只删一个需用 `erase(find(x))`。

> [!question] 判断题 10
> unordered_set 比 set 在任何场景下都更快。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: 数据量小时 set 可能更快（红黑树常数小）；需要有序遍历时必须用 set；哈希冲突严重时 unordered_set 可能退化。

> [!question] 选择题 1
> unordered_set 定义在哪个头文件中？
> - [ ] A. `<set>`
> - [ ] B. `<unordered_set>`
> - [ ] C. `<hash_set>`
> - [ ] D. `<map>`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: unordered_set 和 unordered_multiset 都在 `<unordered_set>` 中。

> [!question] 选择题 2
> unordered_set 的 `load_factor()` 表示什么？
> - [ ] A. 元素总数
> - [ ] B. 桶数
> - [ ] C. 元素数 / 桶数
> - [ ] D. 桶数 / 元素数
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > 
> > **解析**: 负载因子 = size() / bucket_count()，反映哈希表的填充程度。

> [!question] 选择题 3
> 当负载因子超过 `max_load_factor()` 时会发生什么？
> - [ ] A. 抛出异常
> - [ ] B. 自动重哈希（rehash），增加桶数
> - [ ] C. 拒绝插入新元素
> - [ ] D. 什么都不做
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: 超过最大负载因子时，容器自动 rehash 增加桶数以维持 O(1) 性能。

> [!question] 选择题 4
> unordered_set 与 set 相比，缺少哪些功能？
> - [ ] A. insert 和 erase
> - [ ] B. lower_bound 和 upper_bound
> - [ ] C. find 和 count
> - [ ] D. size 和 empty
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: 无序容器不支持有序查找操作（lower_bound、upper_bound），因为元素无序。

> [!question] 选择题 5
> 在竞赛中，unordered_set 可能被卡的原因是？
> - [ ] A. 编译器不支持
> - [ ] B. 精心构造的数据导致大量哈希冲突，退化到 O(n)
> - [ ] C. 内存不够
> - [ ] D. 不支持 int 类型
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: 出题者可以构造特殊数据使默认哈希函数产生大量冲突，导致 O(n²) 退化。

> [!question] 选择题 6
> `us.reserve(1000)` 的作用是？
> - [ ] A. 限制最多存 1000 个元素
> - [ ] B. 预留足够的桶以容纳 1000 个元素（不触发 rehash）
> - [ ] C. 插入 1000 个默认元素
> - [ ] D. 将大小设为 1000
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: reserve(n) 预留桶数使得插入 n 个元素不会触发 rehash，提前分配内存。

> [!question] 选择题 7
> unordered_multiset 和 unordered_set 的区别是？
> - [ ] A. multiset 有序
> - [ ] B. multiset 允许存储重复元素
> - [ ] C. multiset 使用红黑树
> - [ ] D. multiset 不支持 count
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: unordered_multiset 允许重复元素，其他特性与 unordered_set 相同。

> [!question] 选择题 8
> 以下哪种类型不能直接作为 unordered_set 的元素类型（不提供额外哈希函数）？
> - [ ] A. int
> - [ ] B. string
> - [ ] C. double
> - [ ] D. 自定义 struct
>
> > [!success]- 点击查看答案
> > 正确答案: D
> > 
> > **解析**: 标准库为基本类型和 string 提供了默认哈希函数，自定义 struct 需要手动提供。

> [!question] 选择题 9
> 判断元素是否存在，以下哪种写法效率最好？
> - [ ] A. `us.count(x) > 0`
> - [ ] B. `us.find(x) != us.end()`
> - [ ] C. `us.contains(x)` (C++20)
> - [ ] D. 三者效率相同
>
> > [!success]- 点击查看答案
> > 正确答案: D
> > 
> > **解析**: 对于 unordered_set（不允许重复），三种方式内部操作基本相同，效率一样。

> [!question] 选择题 10
> 避免 unordered_set 被哈希冲突攻击的常用方法是？
> - [ ] A. 增大桶数
> - [ ] B. 使用自定义哈希函数（加入随机种子）
> - [ ] C. 改用 vector
> - [ ] D. 限制元素个数
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: 使用带随机种子的自定义哈希函数，使攻击者无法预测哈希值分布。

### 动手练习题

> [!question] 练习题 1
> **题目**: 输入 n 个整数，使用 unordered_set 去重后输出不重复元素的个数，以及按输入顺序输出第一次出现的元素。
> 
> **输入示例**:
> ```
> 8
> 3 1 4 1 5 9 3 5
> ```
> **输出示例**:
> ```
> 5
> 3 1 4 5 9
> ```

> [!question] 练习题 2
> **题目**: 给定两个整数数组 A 和 B，求它们的交集（不含重复）。使用 unordered_set 实现 O(n+m) 的算法。
> 
> **输入示例**:
> ```
> 5
> 1 2 3 4 5
> 4
> 3 4 5 6
> ```
> **输出示例**:
> ```
> 3 4 5
> ```

> [!question] 练习题 3
> **题目**: 实现"最长连续序列"问题：给定 n 个无序整数，找出最长连续数字序列的长度。使用 unordered_set 实现 O(n) 算法。
> 
> **输入示例**:
> ```
> 6
> 100 4 200 1 3 2
> ```
> **输出示例**:
> ```
> 4
> ```
> （最长连续序列为 1,2,3,4）

## --------------------------------------------------------------------------
## 🔗 知识网络
## --------------------------------------------------------------------------

- **上一容器**: [[容器类/10_map_multimap]] | **下一容器**: [[容器类/12_unordered_map_multimap]] | **返回**: [[目录]]
- **相关**: [[数据结构/G_哈希表_HashTable]]
