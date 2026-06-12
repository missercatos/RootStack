## ==========================================================================
STL 容器速通 — unordered_map & unordered_multimap (无序映射)
## ==========================================================================

unordered_map 基于哈希表的键值对容器，平均 O(1) 查找。unordered_multimap 允许重复 key。

## --------------------------------------------------------------------------
## 一、适用场景
## --------------------------------------------------------------------------

| 场景 | 说明 |
|------|------|
| 频率统计 | 统计每个数/字符串的出现次数 |
| 快速查找表 | 预存计算结果，O(1) 查询 |
| 两数之和 / 三数之和 | 配合哈希表找补数 |
| 记忆化搜索 | 用 unordered_map 做 DP 记忆化 |
| 离散化映射 | 大范围坐标映射到连续编号 |

## --------------------------------------------------------------------------
## 二、声明与初始化
## --------------------------------------------------------------------------

```cpp
#include <unordered_map>
using namespace std;

unordered_map<int, string> um1;                   // 空
unordered_map<int, string> um2 = {{1, "a"}, {2, "b"}, {3, "c"}};
unordered_map<int, string> um3(100);               // 指定初始桶数

unordered_multimap<int, string> umm;               // 允许重复 key

// 自定义 key 需要哈希函数和 ==
struct Key { int a, b;
    bool operator==(const Key& o) const { return a == o.a && b == o.b; }
};
struct HashKey {
    size_t operator()(const Key& k) const { return k.a * 131 + k.b; }
};
unordered_map<Key, int, HashKey> um4;
```

## --------------------------------------------------------------------------
## 三、成员函数总览
## --------------------------------------------------------------------------

### 基础操作

| 函数 | 说明 |
|------|------|
| `um.size()` | 元素个数 |
| `um.empty()` | 是否为空 |
| `um.begin()` / `um.end()` | 迭代器（遍历顺序不可控） |

### 插入与访问

| 函数 | 说明 |
|------|------|
| `um[k]` | 访问 key；**不存在则默认构造插入** |
| `um.at(k)` | 访问 key；不存在则抛异常 |
| `um.insert({k, v})` | 插入，返回 pair<iterator, bool> |
| `um.emplace(args...)` | 原位构造 |
| `um.insert_or_assign(k, v)` | 插入或覆盖 (C++17) |
| `um.try_emplace(k, args...)` | 仅不存在时插入 (C++17) |

### 查找与删除

| 函数 | 说明 |
|------|------|
| `um.find(k)` | 查找 key，返回迭代器 |
| `um.count(k)` | key 出现次数（unordered_map 中 0 或 1） |
| `um.contains(k)` | 是否存在 key (C++20) |
| `um.erase(it)` | 删除迭代器 |
| `um.erase(k)` | 按 key 删除 |
| `um.clear()` | 清空 |

### 桶操作

| 函数 | 说明 |
|------|------|
| `um.bucket_count()` | 桶数 |
| `um.load_factor()` | 负载因子 |
| `um.rehash(n)` / `um.reserve(n)` | 重哈希/预留桶 |

### 常用技巧

```cpp
// 计数模式
unordered_map<int, int> cnt;
for (int x : arr) cnt[x]++;

// 查找 + 不存在则插入
if (!um.count(key)) um[key] = val;

// 遍历
for (auto& [k, v] : um) cout << k << " " << v << endl;
```

## --------------------------------------------------------------------------
## 四、洛谷实战
## --------------------------------------------------------------------------

### P5266 学籍管理（unordered_map 版本）

```cpp
#include <iostream>
#include <unordered_map>
using namespace std;

int main() {
    int n;
    unordered_map<string, int> um;
    cin >> n;
    while (n--) {
        int op;
        cin >> op;
        if (op == 1) {
            string name; int score;
            cin >> name >> score;
            um[name] = score;
            cout << "OK" << endl;
        } else if (op == 2) {
            string name;
            cin >> name;
            auto it = um.find(name);
            if (it != um.end()) cout << it->second << endl;
            else cout << "Not found" << endl;
        } else if (op == 3) {
            string name;
            cin >> name;
            if (um.erase(name)) cout << "Deleted successfully" << endl;
            else cout << "Not found" << endl;
        } else if (op == 4) {
            cout << um.size() << endl;
        }
    }
    return 0;
}
```

### P1102 A-B 数对

```cpp
#include <iostream>
#include <unordered_map>
using namespace std;

int main() {
    int n, c;
    long long ans = 0;
    unordered_map<long long, int> cnt;
    cin >> n >> c;
    for (int i = 0, x; i < n; i++) {
        cin >> x;
        cnt[x]++;
    }
    for (auto [k, v] : cnt) {
        auto it = cnt.find(k + c);
        if (it != cnt.end()) ans += (long long)v * it->second;
    }
    cout << ans << endl;
    return 0;
}
```

### P1381 单词背诵

```cpp
// 包含 m 个单词的文章，n 个需要背的单词，求最短连续段落包含所有 n 个单词
#include <iostream>
#include <string>
#include <unordered_map>
using namespace std;

int main() {
    int n, m;
    unordered_map<string, int> need, cur;
    cin >> n;
    for (int i = 0; i < n; i++) {
        string w;
        cin >> w;
        need[w] = 1;
    }
    cin >> m;
    string a[100005];
    for (int i = 0; i < m; i++) cin >> a[i];

    int total = 0, ansLen = 1e9;
    for (int l = 0, r = 0; r < m; r++) {
        if (need.count(a[r])) {
            cur[a[r]]++;
            if (cur[a[r]] == 1) total++;
        }
        while (total == (int)need.size()) {
            ansLen = min(ansLen, r - l + 1);
            if (need.count(a[l])) {
                cur[a[l]]--;
                if (cur[a[l]] == 0) total--;
            }
            l++;
        }
    }
    cout << need.size() << endl << ansLen << endl;
    return 0;
}
```

## ==========================================================================
### 📝 章节测试
## ==========================================================================

> [!question] 判断题 1
> unordered_map 基于哈希表实现，平均 O(1) 查找。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: unordered_map 通过哈希函数定位桶，平均情况下插入、查找、删除都是 O(1)。

> [!question] 判断题 2
> unordered_map 的遍历顺序与插入顺序相同。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: 遍历顺序取决于哈希值和桶分布，不保证与插入顺序一致。

> [!question] 判断题 3
> `um[key]` 在 key 不存在时会插入默认值（与 map 行为相同）。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: unordered_map 的 operator[] 行为与 map 一致，key 不存在时自动插入默认值。

> [!question] 判断题 4
> unordered_map 支持 `lower_bound()` 操作。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: unordered_map 无序，不支持 lower_bound/upper_bound。需要有序查找请用 map。

> [!question] 判断题 5
> unordered_map 的 key 必须支持哈希运算和 `==` 比较。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: 哈希表需要哈希函数计算桶位置，需要 == 判断 key 是否相同。

> [!question] 判断题 6
> unordered_multimap 支持 `operator[]`。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: unordered_multimap 允许重复 key，无法确定 [] 返回哪个 value，因此不支持。

> [!question] 判断题 7
> `um.count(key)` 对 unordered_map 返回值只能是 0 或 1。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: unordered_map 中 key 唯一，count 只能返回 0（不存在）或 1（存在）。

> [!question] 判断题 8
> unordered_map 比 map 占用更多内存。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: 哈希表需要维护桶数组，通常有大量空桶，内存开销比红黑树大。

> [!question] 判断题 9
> `um.insert({k,v})` 在 key 已存在时会覆盖旧值。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: insert 在 key 已存在时不覆盖，插入失败。用 `um[k]=v` 或 `insert_or_assign` 才覆盖。

> [!question] 判断题 10
> 频率统计 `um[x]++` 是 unordered_map 最常见的使用模式之一。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: 利用 operator[] 不存在时插入默认值 0 的特性，`um[x]++` 一行完成计数。

> [!question] 选择题 1
> unordered_map 定义在哪个头文件中？
> - [ ] A. `<map>`
> - [ ] B. `<unordered_map>`
> - [ ] C. `<hash_map>`
> - [ ] D. `<unordered_set>`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: unordered_map 和 unordered_multimap 都在 `<unordered_map>` 中。

> [!question] 选择题 2
> unordered_map 与 map 相比，什么时候应该选择 map？
> - [ ] A. 需要 O(1) 查找时
> - [ ] B. 需要按 key 有序遍历或范围查询时
> - [ ] C. 数据量很大时
> - [ ] D. key 是整数时
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: 需要有序遍历、lower_bound、upper_bound 等操作时必须用 map。

> [!question] 选择题 3
> "两数之和"问题中，unordered_map 的作用是？
> - [ ] A. 排序
> - [ ] B. 存储已遍历的数及其下标，O(1) 查找补数
> - [ ] C. 去重
> - [ ] D. 求最大值
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: 遍历数组时，用 unordered_map 存已经遍历过的数→下标，对每个新数 O(1) 查找 target-x 是否存在。

> [!question] 选择题 4
> 以下代码的输出是？
> ```cpp
> unordered_map<int,int> um;
> um[5] = 10;
> um[5] = 20;
> cout << um.size() << " " << um[5];
> ```
> - [ ] A. 2 20
> - [ ] B. 1 20
> - [ ] C. 1 10
> - [ ] D. 2 10
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: key=5 只有一个元素（operator[] 覆盖），size=1，value=20。

> [!question] 选择题 5
> `try_emplace(k, args...)` (C++17) 的作用是？
> - [ ] A. 总是插入新元素
> - [ ] B. key 不存在时才插入，存在时不做任何事
> - [ ] C. 覆盖已有值
> - [ ] D. 删除元素
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: try_emplace 仅在 key 不存在时构造并插入，已存在则什么都不做（不移动参数）。

> [!question] 选择题 6
> 在滑动窗口问题中，unordered_map 通常用来？
> - [ ] A. 排序窗口元素
> - [ ] B. 统计窗口内各元素的出现次数
> - [ ] C. 存储窗口的最大值
> - [ ] D. 计算窗口大小
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: 滑动窗口中常用 unordered_map 维护窗口内各元素的频率，支持 O(1) 更新。

> [!question] 选择题 7
> unordered_map 在最坏情况下退化为 O(n) 的根本原因是？
> - [ ] A. 内存不足
> - [ ] B. 所有 key 哈希到同一个桶，桶内退化为链表
> - [ ] C. 桶数太多
> - [ ] D. value 类型太大
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: 哈希冲突导致同一桶内元素过多，查找退化为链表遍历 O(n)。

> [!question] 选择题 8
> `um.erase(key)` 返回什么？
> - [ ] A. 被删除元素的值
> - [ ] B. 被删除的元素个数（0 或 1）
> - [ ] C. 迭代器
> - [ ] D. bool
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: 按 key 删除返回删除的元素个数，unordered_map 中为 0 或 1。

> [!question] 选择题 9
> 记忆化搜索中使用 unordered_map 代替数组的好处是？
> - [ ] A. 速度更快
> - [ ] B. 可以处理状态空间稀疏或下标范围极大的情况
> - [ ] C. 代码更短
> - [ ] D. 自动排序
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: 当状态空间很大但实际访问的状态稀疏时，用 unordered_map 按需存储，避免开巨型数组。

> [!question] 选择题 10
> 以下哪种写法可以安全检查 key 是否存在且不产生副作用？
> - [ ] A. `if (um[key]) ...`
> - [ ] B. `if (um.count(key)) ...`
> - [ ] C. `if (um.at(key)) ...`
> - [ ] D. `if (um.get(key)) ...`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: `count` 不修改容器。`um[key]` 会插入默认值；`at` 会抛异常；`get` 不存在。

### 动手练习题

> [!question] 练习题 1
> **题目**: 实现"两数之和"：给定 n 个整数和目标值 target，找出数组中两个数使其和为 target，输出它们的下标（从 0 开始）。使用 unordered_map 实现 O(n) 算法。
> 
> **输入示例**:
> ```
> 4 9
> 2 7 11 15
> ```
> **输出示例**:
> ```
> 0 1
> ```

> [!question] 练习题 2
> **题目**: 给定一个字符串，找出最长的不含重复字符的子串长度。使用 unordered_map 记录字符最后出现位置，配合滑动窗口实现 O(n) 算法。
> 
> **输入示例**:
> ```
> abcabcbb
> ```
> **输出示例**:
> ```
> 3
> ```

> [!question] 练习题 3
> **题目**: 实现"字母异位词分组"：给定 n 个字符串，将字母异位词（相同字母不同排列）分为一组输出。使用 unordered_map，以排序后的字符串为 key 进行分组。
> 
> **输入示例**:
> ```
> 6
> eat tea tan ate nat bat
> ```
> **输出示例**:
> ```
> eat tea ate
> tan nat
> bat
> ```

## --------------------------------------------------------------------------
## 🔗 知识网络
## --------------------------------------------------------------------------

- **上一容器**: [[容器类/11_unordered_set_multiset]] | **下一容器**: [[容器类/13_bitset]] | **返回**: [[目录]]
- **相关**: [[数据结构/G_哈希表_HashTable]]
