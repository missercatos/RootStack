## ==========================================================================
STL 容器速通 — pair (对组)
## ==========================================================================

pair 将两个值打包为一个整体，常作返回值、map元素、优先队列元素等。

## --------------------------------------------------------------------------
## 一、适用场景
## --------------------------------------------------------------------------

| 场景 | 说明 |
|------|------|
| 函数返回多个值 | 不想定义结构体时，用 pair 返回两个值 |
| map 的键值对 | map<K,V> 的每个元素本质上是一个 pair<const K, V> |
| 优先队列多关键字 | priority_queue 中存 pair，默认按 first 排序 |
| 邻接表存边 | vector<pair<int,int>> 存 (邻居, 边权) |
| 坐标/区间 | 用 pair<int,int> 表示 (x,y) 或 (l,r) |

## --------------------------------------------------------------------------
## 二、声明与初始化
## --------------------------------------------------------------------------

```cpp
#include <utility>   // pair 头文件
#include <iostream>
using namespace std;

pair<int, string> p1;                    // 默认构造，int=0, string=""
pair<int, string> p2(1, "hello");        // 直接初始化
pair<int, string> p3 = {2, "world"};     // C++11 列表初始化
auto p4 = make_pair(3, "cpp");           // make_pair 自动推导类型

// 访问
cout << p2.first << " " << p2.second << endl;

// C++17 结构化绑定
auto [val, name] = p3;
cout << val << " " << name << endl;
```

## --------------------------------------------------------------------------
## 三、成员函数与操作总览
## --------------------------------------------------------------------------

| 操作 | 代码 | 说明 |
|------|------|------|
| 默认构造 | `pair<T1,T2> p;` | 值初始化 |
| 值构造 | `pair<T1,T2> p(a, b);` | 用 a,b 初始化 |
| 拷贝构造 | `pair<T1,T2> p(q);` | 拷贝 q |
| 列表初始化 | `pair<T1,T2> p = {a, b};` | C++11 |
| make_pair | `auto p = make_pair(a, b);` | 自动推导 |
| 访问 first | `p.first` | 获取第一个元素 |
| 访问 second | `p.second` | 获取第二个元素 |
| 交换 | `p1.swap(p2);` 或 `swap(p1, p2);` | 交换两个 pair 的内容 |
| 比较运算符 | `==, !=, <, <=, >, >=` | 先比较 first，再比较 second |

## --------------------------------------------------------------------------
## 四、洛谷实战
## --------------------------------------------------------------------------

### P1090 合并果子

题目: n 堆果子，每次合并最小的两堆，求最小总代价。

思路: 用 `priority_queue<int, vector<int>, greater<int>>` 维护最小值。
(此题重点在优先队列，pair 常用于更复杂排序，此处仅示意)

### P3367 [模板] 并查集

pair 虽不直接用于此题，但并查集常与 pair 配合存边集。

### 实际应用示例 — 按分数降序、学号升序排序

```cpp
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    // first=分数, second=学号, 按分数降序排
    vector<pair<int, int>> v;
    v.push_back({90, 1});
    v.push_back({85, 2});
    v.push_back({90, 3});

    sort(v.begin(), v.end(), [](auto& a, auto& b) {
        if (a.first != b.first) return a.first > b.first; // 分数降序
        return a.second < b.second;  // 学号升序
    });

    for (auto [score, id] : v)
        cout << id << " " << score << endl;
    return 0;
}
```

### P2249 查找（变体）

需要同时记录元素值与原始下标时，可用 pair 包装：

```cpp
// 查找一个有序数组中 ≥x 的第一个位置，同时保留原始位置信息
#include <iostream>
#include <algorithm>
using namespace std;

pair<int, int> a[1000005]; // first=值, second=原始下标

int main() {
    int n, q;
    cin >> n >> q;
    for (int i = 1; i <= n; i++) {
        cin >> a[i].first;
        a[i].second = i;
    }
    // 按值排序后二分查找
    sort(a + 1, a + n + 1);
    while (q--) {
        int x;
        cin >> x;
        auto it = lower_bound(a + 1, a + n + 1, make_pair(x, 0));
        if (it != a + n + 1 && it->first == x)
            cout << it->second << " ";
        else
            cout << -1 << " ";
    }
    return 0;
}
```

## ==========================================================================
### 📝 章节测试
## ==========================================================================

> [!question] 判断题 1
> pair 的头文件是 `<pair>`。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: pair 的头文件是 `<utility>`，不是 `<pair>`。

> [!question] 判断题 2
> pair 的比较运算符先比较 first，若相等再比较 second。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: pair 的默认比较规则是字典序，先比较 first，相同时再比较 second。

> [!question] 判断题 3
> `make_pair(1, "hello")` 可以自动推导类型，无需手动指定模板参数。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: `make_pair` 通过函数参数自动推导模板参数类型。

> [!question] 判断题 4
> pair 可以包含三个或更多个元素。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: pair 只能包含两个元素。若需要更多元素，可以使用 `tuple` 或嵌套 pair。

> [!question] 判断题 5
> C++17 的结构化绑定 `auto [a, b] = p;` 可以直接解包 pair 的两个成员。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: C++17 引入结构化绑定，可以用 `auto [a, b] = p;` 解包 pair。

> [!question] 判断题 6
> pair 默认构造时，int 类型的 first 值是未定义的。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: pair 默认构造时会值初始化成员，int 类型为 0，string 类型为空串。

> [!question] 判断题 7
> `pair<int, int>` 和 `pair<int, double>` 是同一个类型。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: pair 是模板类，不同模板参数实例化出不同的类型。

> [!question] 判断题 8
> map 的每个元素本质上是一个 `pair<const Key, Value>`。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: map 内部存储的元素类型就是 `pair<const Key, Value>`，key 加了 const 防止修改。

> [!question] 判断题 9
> pair 支持 `swap()` 成员函数来交换两个 pair 的内容。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: pair 提供 `swap()` 成员函数和非成员 `swap()` 函数用于交换内容。

> [!question] 判断题 10
> pair 的 first 和 second 必须是相同类型。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: pair 的两个模板参数可以是不同类型，如 `pair<int, string>`。

> [!question] 选择题 1
> pair 定义在哪个头文件中？
> - [ ] A. `<pair>`
> - [ ] B. `<utility>`
> - [ ] C. `<map>`
> - [ ] D. `<tuple>`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: pair 定义在 `<utility>` 头文件中。不过包含 `<map>` 等头文件时也会间接包含它。

> [!question] 选择题 2
> 以下哪种方式不能正确创建一个 `pair<int, string>`？
> - [ ] A. `pair<int, string> p(1, "hi");`
> - [ ] B. `auto p = make_pair(1, "hi");`
> - [ ] C. `pair<int, string> p = {1, "hi"};`
> - [ ] D. `pair<int, string> p[1, "hi"];`
>
> > [!success]- 点击查看答案
> > 正确答案: D
> > 
> > **解析**: D 的语法错误，方括号不是合法的构造语法。

> [!question] 选择题 3
> `pair<int,int> a(3, 5), b(3, 2);`，`a < b` 的结果是？
> - [ ] A. true
> - [ ] B. false
> - [ ] C. 编译错误
> - [ ] D. 未定义行为
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: first 相同（都是 3），比较 second：5 < 2 为 false，所以 a < b 为 false。

> [!question] 选择题 4
> `make_pair(1, 2.5)` 的返回类型是？
> - [ ] A. `pair<int, int>`
> - [ ] B. `pair<int, double>`
> - [ ] C. `pair<int, float>`
> - [ ] D. `pair<double, double>`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: `make_pair` 自动推导类型，1 是 int，2.5 是 double，所以返回 `pair<int, double>`。

> [!question] 选择题 5
> 在 `priority_queue<pair<int,int>>` 中，默认的排序规则是？
> - [ ] A. 按 first 升序
> - [ ] B. 按 first 降序，相同时按 second 降序
> - [ ] C. 按 second 降序
> - [ ] D. 按 first 降序，相同时按 second 升序
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: priority_queue 默认大根堆，pair 按字典序比较，所以队首是 first 最大的，first 相同时 second 最大的在前。

> [!question] 选择题 6
> 以下代码输出什么？
> ```cpp
> pair<int,int> p = {10, 20};
> auto [x, y] = p;
> x = 100;
> cout << p.first;
> ```
> - [ ] A. 100
> - [ ] B. 10
> - [ ] C. 20
> - [ ] D. 编译错误
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: 结构化绑定默认是拷贝，修改 x 不影响 p.first。若要修改需用 `auto& [x, y] = p;`。

> [!question] 选择题 7
> pair 的哪个操作的时间复杂度不是 O(1)？
> - [ ] A. 访问 first
> - [ ] B. 比较两个 pair
> - [ ] C. swap 两个 pair
> - [ ] D. 以上都是 O(1)
>
> > [!success]- 点击查看答案
> > 正确答案: D
> > 
> > **解析**: pair 的所有基本操作（访问、比较、交换）对于基本类型都是 O(1)。注意如果 pair 中存的是 string 等复杂类型，比较和交换可能不是 O(1)。

> [!question] 选择题 8
> 以下哪种写法可以在 C++11 中正确初始化 pair？
> - [ ] A. `pair<int,int> p{1, 2};`
> - [ ] B. `pair<int,int> p = {1, 2};`
> - [ ] C. `auto p = make_pair(1, 2);`
> - [ ] D. 以上都可以
>
> > [!success]- 点击查看答案
> > 正确答案: D
> > 
> > **解析**: C++11 支持列表初始化和 make_pair，以上三种写法都是合法的。

> [!question] 选择题 9
> 用 pair 存储图的邻接表边 `(邻居节点, 边权)`，以下声明正确的是？
> - [ ] A. `vector<pair<int,int>> g[N];`
> - [ ] B. `pair<vector<int>, int> g[N];`
> - [ ] C. `vector<int, int> g[N];`
> - [ ] D. `pair<int> g[N];`
>
> > [!success]- 点击查看答案
> > 正确答案: A
> > 
> > **解析**: 邻接表常用 `vector<pair<int,int>> g[N]`，每个 g[u] 存储 u 的所有出边 (v, w)。

> [!question] 选择题 10
> `pair<int,int> p;` 默认构造后，`p.first` 和 `p.second` 的值分别是？
> - [ ] A. 未定义, 未定义
> - [ ] B. 0, 0
> - [ ] C. -1, -1
> - [ ] D. 随机值, 随机值
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: pair 默认构造时对其成员进行值初始化，int 类型值初始化为 0。

### 动手练习题

> [!question] 练习题 1
> **题目**: 输入 n 个学生的姓名和成绩，用 `vector<pair<int,string>>` 存储（first 为成绩，second 为姓名），按成绩从高到低排序输出。成绩相同时按姓名字典序升序排列。
> 
> **输入示例**:
> ```
> 4
> Alice 85
> Bob 92
> Charlie 85
> David 92
> ```
> **输出示例**:
> ```
> Bob 92
> David 92
> Alice 85
> Charlie 85
> ```

> [!question] 练习题 2
> **题目**: 输入一组坐标点 `(x, y)`，用 `pair<int,int>` 存储。找出距离原点最远的点并输出其坐标。若有多个点距离相同，输出 x 值最大的那个。
> 
> **输入示例**:
> ```
> 3
> 3 4
> -5 0
> 0 5
> ```
> **输出示例**:
> ```
> -5 0
> ```

> [!question] 练习题 3
> **题目**: 实现一个函数 `pair<int,int> minmax_element(vector<int>& v)`，返回 vector 中最小值和最大值组成的 pair（first 为最小值，second 为最大值）。在 main 中读入一组整数并调用该函数输出结果。
> 
> **输入示例**:
> ```
> 5
> 3 1 4 1 5
> ```
> **输出示例**:
> ```
> 1 5
> ```

## --------------------------------------------------------------------------
## 🔗 知识网络
## --------------------------------------------------------------------------

- **下一容器**: [[容器类/02_vector]] | **返回**: [[目录]]
- **相关**: [[数据结构/A_容器_Container]] | [[算法技巧/函数结构体]]
