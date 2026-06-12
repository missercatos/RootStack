## ==========================================================================
STL 容器速通 — map & multimap (有序映射)
## ==========================================================================

map 是键值对的有序集合，key 唯一、自动排序；multimap 允许重复 key。底层为红黑树，操作 O(log n)。

## --------------------------------------------------------------------------
## 一、适用场景
## --------------------------------------------------------------------------

| 场景 | 说明 |
|------|------|
| 字典/哈希表替代 | 需要有序遍历 key 时用 map |
| 统计频率 | `map<string, int>` 统计单词出现次数 |
| 离散化 | 大范围坐标映射到小范围下标 |
| 缓存数据库 | 通过 key 快速查找 value |
| 区间/前缀和映射 | `map<int, int>` 记录离散点的累加值 |

### map vs unordered_map

|    | map | unordered_map |
|----|-----|---------------|
| 底层 | 红黑树 | 哈希表 |
| 插入/查找 | O(log n) | O(1) 均摊 |
| 有序 | 是 | 否 |
| 内存 | 较小 | 较大 |

**选 map**: 需要有序遍历或 O(log n) 足够。
**选 unordered_map**: 纯查找不需要顺序，追求 O(1)。

## --------------------------------------------------------------------------
## 二、声明与初始化
## --------------------------------------------------------------------------

```cpp
#include <map>
using namespace std;

map<int, string> m1;                     // key 升序
map<int, string, greater<int>> m2;       // key 降序
map<int, string> m3 = {{1, "a"}, {2, "b"}, {3, "c"}}; // 列表初始化

multimap<int, string> mm1;               // 允许重复 key
multimap<int, string> mm2 = {{1, "a"}, {1, "b"}};     // key=1 有两个值

// 自定义 key 类型需重载 <
struct Key { int a, b;
    bool operator<(const Key& o) const {
        if (a != o.a) return a < o.a;
        return b < o.b;
    }
};
map<Key, int> m4;
```

## --------------------------------------------------------------------------
## 三、成员函数总览
## --------------------------------------------------------------------------

### 容量与迭代器

| 函数 | 说明 |
|------|------|
| `m.size()` | 元素个数 |
| `m.empty()` | 是否为空 |
| `m.begin()` / `m.end()` | 迭代器，解引用得到 `pair<const Key, T>` |
| `m.rbegin()` / `m.rend()` | 反向迭代器 |

### 插入与访问

| 函数 | 说明 |
|------|------|
| `m[k]` | 访问 key=k 的 value；**若 key 不存在则默认构造插入** |
| `m.at(k)` | 访问 key，不存在则抛出异常 |
| `m.insert({k, v})` | 插入键值对，返回 pair<iterator, bool> |
| `m.emplace(args...)` | 原位构造 (C++11) |
| `m.insert_or_assign(k, v)` | 插入或覆盖 (C++17) |
| `m.try_emplace(k, args...)` | 仅不存在时插入 (C++17) |

### 删除

| 函数 | 说明 |
|------|------|
| `m.erase(it)` | 删除迭代器指向元素 |
| `m.erase(k)` | 删除 key=k 的元素 |
| `m.erase(first, last)` | 删除区间 |
| `m.clear()` | 清空 |

### 查找

| 函数 | 说明 |
|------|------|
| `m.find(k)` | 查找 key，返回迭代器；未找到返回 end() |
| `m.count(k)` | key=k 的元素个数（map 中 0 或 1） |
| `m.contains(k)` | 是否存在 key (C++20) |
| `m.lower_bound(k)` | 第一个 key ≥ k |
| `m.upper_bound(k)` | 第一个 key > k |
| `m.equal_range(k)` | 返回 pair<lower_bound, upper_bound> |

## --------------------------------------------------------------------------
## 四、洛谷实战
## --------------------------------------------------------------------------

### P1918 保龄球（map 查找）

```cpp
// 给出 n 个位置和瓶数，Q 次询问每个位置的瓶数
#include <iostream>
#include <map>
using namespace std;

int main() {
    int n, Q;
    map<int, int> m;
    cin >> n;
    for (int i = 1, x; i <= n; i++) {
        cin >> x;
        m[x] = i; // 瓶数 → 位置
    }
    cin >> Q;
    while (Q--) {
        int x;
        cin >> x;
        auto it = m.find(x);
        if (it != m.end()) cout << it->second << endl;
        else cout << 0 << endl;
    }
    return 0;
}
```

### P1241 括号序列（map 匹配）

```cpp
// 给定括号序列，找出成对的括号
#include <iostream>
#include <string>
#include <map>
#include <stack>
using namespace std;

int main() {
    map<char, char> match = {{')', '('}, {']', '['}};
    string s;
    cin >> s;
    stack<pair<char,int>> st;
    bool paired[105] = {false};
    for (int i = 0; i < (int)s.size(); i++) {
        char c = s[i];
        if (c == '(' || c == '[') {
            st.push({c, i});
        } else if (c == ')' || c == ']') {
            if (!st.empty() && st.top().first == match[c]) {
                paired[st.top().second] = paired[i] = true;
                st.pop();
            } else {
                while (!st.empty()) st.pop();
            }
        }
    }
    for (int i = 0; i < (int)s.size(); i++) {
        if (paired[i]) cout << s[i];
        else if (s[i] == '(' || s[i] == ')') cout << "()";
        else cout << "[]";
    }
    return 0;
}
```

### P5266 学籍管理（map 增删查）

```cpp
#include <iostream>
#include <map>
using namespace std;

int main() {
    int n;
    map<string, int> m;
    cin >> n;
    while (n--) {
        int op;
        cin >> op;
        if (op == 1) { // 插入或修改
            string name; int score;
            cin >> name >> score;
            m[name] = score;
            cout << "OK" << endl;
        } else if (op == 2) { // 查询
            string name;
            cin >> name;
            auto it = m.find(name);
            if (it != m.end()) cout << it->second << endl;
            else cout << "Not found" << endl;
        } else if (op == 3) { // 删除
            string name;
            cin >> name;
            if (m.erase(name)) cout << "Deleted successfully" << endl;
            else cout << "Not found" << endl;
        } else if (op == 4) { // 总数
            cout << m.size() << endl;
        }
    }
    return 0;
}
```

## ==========================================================================
### 📝 章节测试
## ==========================================================================

> [!question] 判断题 1
> map 的底层是红黑树，key 自动有序。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: map 底层红黑树按 key 排序，遍历时 key 有序。

> [!question] 判断题 2
> `m[key]` 在 key 不存在时会插入一个默认值。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: `operator[]` 在 key 不存在时会插入 {key, 默认值}。这是 map 的常见陷阱。

> [!question] 判断题 3
> map 的 `insert()` 会覆盖已存在的 key 的值。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: `insert` 在 key 已存在时不会覆盖，插入失败。`operator[]` 和 `insert_or_assign` 才会覆盖。

> [!question] 判断题 4
> map 的查找时间复杂度是 O(log n)。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: 红黑树高度 O(log n)，查找沿树高进行。

> [!question] 判断题 5
> multimap 支持 `operator[]`。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: multimap 一个 key 可能对应多个 value，`operator[]` 无法确定返回哪个值，所以不支持。

> [!question] 判断题 6
> map 的迭代器解引用得到的是 `pair<const Key, Value>`。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: map 元素类型是 `pair<const Key, Value>`，key 是 const 的不能修改。

> [!question] 判断题 7
> `m.at(key)` 在 key 不存在时会插入默认值。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: `at()` 在 key 不存在时抛出 `out_of_range` 异常，不会插入。`operator[]` 才会插入。

> [!question] 判断题 8
> map 可以用 `lower_bound` 和 `upper_bound` 查找 key 的范围。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: map 支持 lower_bound 和 upper_bound，可用于范围查询。

> [!question] 判断题 9
> map 和 unordered_map 的主要区别是 map 有序而 unordered_map 无序。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: map 基于红黑树有序 O(log n)；unordered_map 基于哈希表无序，平均 O(1)。

> [!question] 判断题 10
> `m.erase(key)` 返回被删除的元素个数。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: `erase(key)` 返回删除的元素个数，map 中为 0 或 1，multimap 中可能 > 1。

> [!question] 选择题 1
> map 的 `operator[]` 与 `find()` 的主要区别是？
> - [ ] A. operator[] 更快
> - [ ] B. operator[] 不存在时会插入默认值，find 不会
> - [ ] C. find 会修改 map
> - [ ] D. 两者功能完全相同
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: `operator[]` 若 key 不存在会自动插入（副作用）；`find` 只查找不修改。

> [!question] 选择题 2
> 以下代码执行后 m 中有几个元素？
> ```cpp
> map<int,int> m;
> m[1] = 10;
> m[2] = 20;
> m[1] = 30;
> m.insert({3, 40});
> m.insert({2, 50});
> ```
> - [ ] A. 3
> - [ ] B. 4
> - [ ] C. 5
> - [ ] D. 2
>
> > [!success]- 点击查看答案
> > 正确答案: A
> > 
> > **解析**: m[1]=10 插入 {1,10}；m[2]=20 插入 {2,20}；m[1]=30 覆盖为 {1,30}；insert {3,40} 成功；insert {2,50} 失败（key=2 已存在）。共 3 个。

> [!question] 选择题 3
> 统计字符串中每个字符出现次数，最简洁的写法是？
> - [ ] A. `for(char c:s) if(m.find(c)!=m.end()) m[c]++; else m[c]=1;`
> - [ ] B. `for(char c:s) m[c]++;`
> - [ ] C. `for(char c:s) m.insert({c, m.count(c)+1});`
> - [ ] D. `for(char c:s) m.at(c)++;`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: `m[c]++` 利用了 operator[] 不存在时插入默认值 0 的特性，最简洁。

> [!question] 选择题 4
> map 遍历时元素的顺序是？
> - [ ] A. 插入顺序
> - [ ] B. key 的升序
> - [ ] C. value 的升序
> - [ ] D. 随机顺序
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: map 底层红黑树中序遍历，按 key 升序。

> [!question] 选择题 5
> C++17 中 `insert_or_assign(k, v)` 的作用是？
> - [ ] A. 只插入不覆盖
> - [ ] B. 只覆盖不插入
> - [ ] C. 不存在时插入，存在时覆盖
> - [ ] D. 与 insert 完全相同
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > 
> > **解析**: `insert_or_assign` 语义明确：不存在时插入，存在时覆盖 value。

> [!question] 选择题 6
> multimap 与 map 的区别是？
> - [ ] A. multimap 无序
> - [ ] B. multimap 允许相同 key 的多个元素
> - [ ] C. multimap 基于哈希表
> - [ ] D. multimap 不支持迭代器
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: multimap 允许重复 key，同一 key 可以对应多个 value。底层仍然是红黑树。

> [!question] 选择题 7
> 以下代码的输出是？
> ```cpp
> map<string,int> m;
> cout << m["hello"];
> ```
> - [ ] A. 编译错误
> - [ ] B. 运行时异常
> - [ ] C. 0
> - [ ] D. 随机值
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > 
> > **解析**: key "hello" 不存在时 operator[] 插入 {"hello", 0}（int 默认值为 0），输出 0。

> [!question] 选择题 8
> 如何安全地检查 map 中是否存在某个 key（不产生副作用）？
> - [ ] A. `if (m[key]) ...`
> - [ ] B. `if (m.find(key) != m.end()) ...`
> - [ ] C. `if (m.at(key)) ...`
> - [ ] D. `if (m.get(key)) ...`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: `find` 不修改 map。`m[key]` 会插入默认值（副作用），`at` 会抛异常，`get` 不存在。

> [!question] 选择题 9
> map 自定义 key 类型需要满足什么条件？
> - [ ] A. 重载 `==` 运算符
> - [ ] B. 重载 `<` 运算符（或提供比较函数）
> - [ ] C. 提供哈希函数
> - [ ] D. 重载 `>` 运算符
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: map 基于红黑树需要严格弱序比较，通常通过重载 `<` 或提供自定义比较函数。

> [!question] 选择题 10
> `map<int,int> m = {{1,10},{2,20},{3,30}}; m.upper_bound(2)->second` 的值是？
> - [ ] A. 10
> - [ ] B. 20
> - [ ] C. 30
> - [ ] D. 未定义
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > 
> > **解析**: upper_bound(2) 返回第一个 key > 2 的迭代器，即 key=3，其 value(second)=30。

### 动手练习题

> [!question] 练习题 1
> **题目**: 输入一段英文文本（一行），统计每个单词出现的次数，按字典序输出单词及其次数。使用 map 实现。
> 
> **输入示例**:
> ```
> the cat sat on the mat the cat
> ```
> **输出示例**:
> ```
> cat 2
> mat 1
> on 1
> sat 1
> the 3
> ```

> [!question] 练习题 2
> **题目**: 实现一个简单的电话簿系统，支持：1) 添加联系人（姓名→电话）；2) 按姓名查找电话；3) 删除联系人；4) 按姓名字典序列出所有联系人。使用 map 实现。
> 
> **输入示例**:
> ```
> 6
> 1 Alice 12345
> 1 Bob 67890
> 2 Alice
> 3 Bob
> 4
> 2 Bob
> ```
> **输出示例**:
> ```
> 12345
> Alice 12345
> Not found
> ```

> [!question] 练习题 3
> **题目**: 给定 n 个整数，找出出现次数最多的元素。如果有多个，输出值最小的那个。使用 map 统计频率。
> 
> **输入示例**:
> ```
> 8
> 1 2 3 2 3 4 2 3
> ```
> **输出示例**:
> ```
> 2
> ```
> （2和3都出现3次，输出值更小的2）

## --------------------------------------------------------------------------
## 🔗 知识网络
## --------------------------------------------------------------------------

- **上一容器**: [[容器类/09_set_multiset]] | **下一容器**: [[容器类/11_unordered_set_multiset]] | **返回**: [[目录]]
- **相关**: [[数据结构/E_红黑树_RedBlackTree]]
