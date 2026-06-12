## ==========================================================================
STL 容器速通 — set & multiset (有序集合)
## ==========================================================================

set 存储唯一元素并自动排序；multiset 允许重复元素。底层均为红黑树，操作 O(log n)。

## --------------------------------------------------------------------------
## 一、适用场景
## --------------------------------------------------------------------------

| 场景 | 说明 |
|------|------|
| 去重 + 有序遍历 | 同时完成去重和排序 |
| 动态维护第 K 大/小 | 结合迭代器前进 O(log n + k) |
| 找前驱/后继 | lower_bound / upper_bound |
| 区间查询 | 查询某值域范围内的元素 |
| 模拟平衡树 | 大部分平衡树操作 set 都能胜任 |

## --------------------------------------------------------------------------
## 二、声明与初始化
## --------------------------------------------------------------------------

```cpp
#include <set>
using namespace std;

set<int> s1;                         // 空集合，元素升序
set<int, greater<int>> s2;           // 降序
set<int> s3 = {3, 1, 4, 1, 5};      // 去重后: {1, 3, 4, 5}
set<int> s4(s3.begin(), s3.end());   // 迭代器范围构造

multiset<int> ms;                    // 允许重复元素
multiset<int> ms2 = {3, 1, 4, 1, 5}; // {1, 1, 3, 4, 5}

// 自定义类型的 set 需要重载 < 运算符 或 提供比较函数
struct Node {
    int v, id;
    bool operator<(const Node& o) const { return v < o.v; }
};
set<Node> s5;
```

## --------------------------------------------------------------------------
## 三、成员函数总览
## --------------------------------------------------------------------------

### 容量与迭代器

| 函数 | 说明 |
|------|------|
| `s.size()` | 元素个数 O(1) |
| `s.empty()` | 是否为空 |
| `s.begin()` / `s.end()` | 迭代器（*不可修改值*，改值会破坏有序性） |
| `s.rbegin()` / `s.rend()` | 反向迭代器 |

### 插入与删除

| 函数 | 说明 |
|------|------|
| `s.insert(x)` | 插入元素，返回 pair<iterator, bool>（bool 表示是否插入成功） |
| `s.emplace(args...)` | 原位构造并插入 |
| `s.erase(it)` | 删除迭代器指向元素 |
| `s.erase(x)` | 删除值等于 x 的元素（multiset 中删除所有等于 x 的） |
| `s.erase(first, last)` | 删除区间 |
| `s.clear()` | 清空 |

### 查找

| 函数 | 说明 |
|------|------|
| `s.find(x)` | 查找值为 x 的元素，返回迭代器；未找到返回 end() |
| `s.count(x)` | 值为 x 的元素个数（set 中最多为 1） |
| `s.lower_bound(x)` | 返回第一个 ≥ x 的迭代器 |
| `s.upper_bound(x)` | 返回第一个 > x 的迭代器 |
| `s.equal_range(x)` | 返回 pair<lower_bound, upper_bound> |

### multiset 特有注意

```cpp
// 只删除一个值为 x 的元素（而非全部）
auto it = ms.find(x);
if (it != ms.end()) ms.erase(it);
```

## --------------------------------------------------------------------------
## 四、洛谷实战
## --------------------------------------------------------------------------

### P1059 明明的随机数（set 去重+排序）

```cpp
#include <iostream>
#include <set>
using namespace std;

int main() {
    int n;
    set<int> s;
    cin >> n;
    for (int i = 0, x; i < n; i++) { cin >> x; s.insert(x); }
    cout << s.size() << endl;
    for (int x : s) cout << x << " ";
    return 0;
}
```

### P2234 [HNOI2002] 营业额统计（找前驱后继）

```cpp
#include <iostream>
#include <set>
#include <cmath>
using namespace std;

int main() {
    int n, ans = 0;
    cin >> n;
    set<int> s;
    s.insert(-2e9); s.insert(2e9); // 哨兵
    for (int i = 0, x; i < n; i++) {
        cin >> x;
        auto it = s.lower_bound(x);
        int diff = min(abs(*it - x), abs(*prev(it) - x));
        if (i == 0) diff = x; // 第一天只能用营业额本身
        ans += diff;
        s.insert(x);
    }
    cout << ans << endl;
    return 0;
}
```

### P3870 [TJOI2009] 开关（set 维护区间）

```cpp
// 有 n 盏灯，支持区间取反和区间查询亮灯数
// 此题主要是线段树，以下只做 set 的例题演示
#include <iostream>
#include <set>
using namespace std;

int main() {
    int n, m;
    cin >> n >> m;
    set<int> s; // 存关灯的灯下标（此题可以用 set 维护状态，具体取决于实现思路）
    for (int i = 1; i <= n; i++) s.insert(i);
    while (m--) {
        int op, l, r;
        cin >> op >> l >> r;
        auto it = s.lower_bound(l);
        int cnt = 0;
        while (it != s.end() && *it <= r) {
            cnt++;
            it = s.erase(it);
        }
        if (op == 0) { // 关 -> 开
            cout << cnt << endl;
        } else { // 开 -> 关（需用另一个 set 存状态，此处简略）
        }
    }
    return 0;
}
// 注: P3870 正解为线段树，本解法仅用于演示 set 的 lower_bound + erase 遍历删除模式
```

## ==========================================================================
### 📝 章节测试
## ==========================================================================

> [!question] 判断题 1
> set 的底层数据结构是红黑树。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: set 和 multiset 底层都是红黑树（自平衡二叉搜索树）。

> [!question] 判断题 2
> set 中的元素是有序且唯一的。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: set 自动排序且不允许重复元素。multiset 允许重复。

> [!question] 判断题 3
> `set<int> s = {3,1,4,1,5};` 之后 s 中有 5 个元素。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: set 去重，1 出现两次只保留一个，所以 s 中有 4 个元素 {1,3,4,5}。

> [!question] 判断题 4
> set 的 `insert()` 时间复杂度是 O(log n)。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: 红黑树的插入需要查找位置并可能旋转平衡，时间 O(log n)。

> [!question] 判断题 5
> 可以修改 set 中元素的值（通过迭代器赋值）。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: set 的迭代器指向的是 const 值，不能修改。修改值会破坏有序性。

> [!question] 判断题 6
> `multiset::erase(x)` 会删除所有值等于 x 的元素。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: multiset 中 `erase(x)` 按值删除会删除所有等于 x 的元素。只删一个需用 `erase(find(x))`。

> [!question] 判断题 7
> `s.lower_bound(x)` 返回第一个大于 x 的元素的迭代器。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: `lower_bound(x)` 返回第一个 ≥ x 的元素迭代器。`upper_bound(x)` 才是第一个 > x 的。

> [!question] 判断题 8
> set 的遍历结果是有序的。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: set 的迭代器按红黑树中序遍历，结果自然有序。

> [!question] 判断题 9
> 自定义类型放入 set 需要重载 `==` 运算符。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: set 需要的是严格弱序（strict weak ordering），需要重载 `<` 运算符或提供比较函数，不需要 `==`。

> [!question] 判断题 10
> set 的 `count(x)` 返回值只能是 0 或 1。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: set 中元素唯一，count 只能返回 0（不存在）或 1（存在）。multiset 可以 > 1。

> [!question] 选择题 1
> set 的 `find()` 时间复杂度是？
> - [ ] A. O(1)
> - [ ] B. O(log n)
> - [ ] C. O(n)
> - [ ] D. O(n log n)
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: set 基于红黑树，查找沿树高 O(log n) 进行。

> [!question] 选择题 2
> `set<int> s = {1,3,5,7,9}; s.lower_bound(4)` 指向的值是？
> - [ ] A. 3
> - [ ] B. 4
> - [ ] C. 5
> - [ ] D. end()
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > 
> > **解析**: lower_bound(4) 返回第一个 ≥ 4 的元素，即 5。

> [!question] 选择题 3
> 在 multiset 中只删除一个值为 x 的元素，正确的做法是？
> - [ ] A. `ms.erase(x);`
> - [ ] B. `ms.erase(ms.find(x));`
> - [ ] C. `ms.remove(x);`
> - [ ] D. `ms.delete(x);`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: `erase(x)` 会删除所有值为 x 的元素。要只删一个，先 find 得到迭代器再 erase。

> [!question] 选择题 4
> set 与 unordered_set 的主要区别是？
> - [ ] A. set 无序，unordered_set 有序
> - [ ] B. set 基于红黑树有序，unordered_set 基于哈希表无序
> - [ ] C. set 允许重复，unordered_set 不允许
> - [ ] D. 两者完全相同
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: set 基于红黑树保持有序，O(log n)；unordered_set 基于哈希表无序，平均 O(1)。

> [!question] 选择题 5
> 以下哪个操作 set 不支持？
> - [ ] A. `insert()`
> - [ ] B. `find()`
> - [ ] C. `operator[]`
> - [ ] D. `erase()`
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > 
> > **解析**: set 没有 `operator[]`，那是 map 的操作。set 只存值不存键值对。

> [!question] 选择题 6
> `set<int, greater<int>> s = {3,1,4};` 遍历输出顺序是？
> - [ ] A. 1 3 4
> - [ ] B. 4 3 1
> - [ ] C. 3 1 4
> - [ ] D. 4 1 3
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: `greater<int>` 使 set 按降序排列，遍历输出 4 3 1。

> [!question] 选择题 7
> set 的 `insert` 返回值类型是？
> - [ ] A. `bool`
> - [ ] B. `iterator`
> - [ ] C. `pair<iterator, bool>`
> - [ ] D. `int`
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > 
> > **解析**: insert 返回 `pair<iterator, bool>`，iterator 指向插入位置，bool 表示是否插入成功。

> [!question] 选择题 8
> 用 set 求"前驱"（小于 x 的最大元素），正确做法是？
> - [ ] A. `*s.lower_bound(x)`
> - [ ] B. `*prev(s.lower_bound(x))`
> - [ ] C. `*s.upper_bound(x)`
> - [ ] D. `*next(s.find(x))`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: lower_bound(x) 指向第一个 ≥ x 的元素，prev 后退一步就是小于 x 的最大元素。

> [!question] 选择题 9
> multiset 和 set 的区别是？
> - [ ] A. multiset 无序
> - [ ] B. multiset 允许存储重复元素
> - [ ] C. multiset 基于哈希表
> - [ ] D. multiset 不支持 lower_bound
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: multiset 与 set 唯一区别是允许重复元素，底层同样是红黑树，有序。

> [!question] 选择题 10
> set 中插入已存在的元素会发生什么？
> - [ ] A. 覆盖旧值
> - [ ] B. 抛出异常
> - [ ] C. 插入失败，set 不变
> - [ ] D. 产生重复元素
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > 
> > **解析**: set 不允许重复，插入已存在的值会失败，返回 {已存在元素的迭代器, false}。

### 动手练习题

> [!question] 练习题 1
> **题目**: 输入 n 个整数，使用 set 去重并按升序输出。同时输出去重前后的元素个数差。
> 
> **输入示例**:
> ```
> 8
> 3 1 4 1 5 9 2 6
> ```
> **输出示例**:
> ```
> 去重后: 1 2 3 4 5 6 9
> 去除了 1 个重复元素
> ```

> [!question] 练习题 2
> **题目**: 给定一个有序集合和 q 次查询，每次查询一个数 x，输出集合中 x 的前驱（小于 x 的最大值）和后继（大于 x 的最小值）。不存在则输出 "NONE"。使用 set 的 lower_bound 实现。
> 
> **输入示例**:
> ```
> 5
> 1 3 5 7 9
> 3
> 4
> 1
> 10
> ```
> **输出示例**:
> ```
> 前驱:3 后继:5
> 前驱:NONE 后继:3
> 前驱:9 后继:NONE
> ```

> [!question] 练习题 3
> **题目**: 使用 multiset 模拟一个动态数据流，支持三种操作：1) 插入一个数；2) 删除一个数（只删一个）；3) 输出当前最小值和最大值。
> 
> **输入示例**:
> ```
> 7
> 1 5
> 1 3
> 1 8
> 3
> 2 3
> 3
> 1 1
> ```
> **输出示例**:
> ```
> min=3 max=8
> min=5 max=8
> ```

## --------------------------------------------------------------------------
## 🔗 知识网络
## --------------------------------------------------------------------------

- **上一容器**: [[容器类/08_list_forward_list]] | **下一容器**: [[容器类/10_map_multimap]] | **返回**: [[目录]]
- **相关**: [[数据结构/E_红黑树_RedBlackTree]] | [[算法技巧/二分查找]]
