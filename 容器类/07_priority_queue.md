## ==========================================================================
STL 容器速通 — priority_queue (优先队列/堆)
## ==========================================================================

priority_queue 保证队首元素始终是优先级最高（默认最大）的元素，底层基于堆（通常是二叉堆）。

## --------------------------------------------------------------------------
## 一、适用场景
## --------------------------------------------------------------------------

| 场景 | 说明 |
|------|------|
| 动态取最值 | 不断插入并取最小/最大值（Top-K 问题） |
| Dijkstra 算法 | 每次取距离最小的顶点 |
| 合并多路有序序列 | 用小根堆取各路的当前最小值 |
| 哈夫曼编码 / 合并果子 | 每次取最小的两个合并 |
| 贪心 + 堆优化 | 区间调度、任务调度等 |

## --------------------------------------------------------------------------
## 二、声明与初始化
## --------------------------------------------------------------------------

```cpp
#include <queue>                     // priority_queue 定义在 <queue> 中
using namespace std;

// 默认大根堆
priority_queue<int> pq;              // 队首最大
priority_queue<int, vector<int>, greater<int>> pq2; // 小根堆：队首最小

// 自定义比较
struct cmp {
    bool operator()(int a, int b) { return a > b; } // 小根堆
};
priority_queue<int, vector<int>, cmp> pq3;

// 使用 decltype + lambda (C++20)
// auto cmp = [](int a, int b) { return a > b; };
// priority_queue<int, vector<int>, decltype(cmp)> pq4(cmp);

// 存自定义类型
struct Node {
    int val, idx;
    bool operator<(const Node& o) const { return val < o.val; } // 大根堆
};
priority_queue<Node> pq5;
```

### 存 pair 的默认行为

```cpp
priority_queue<pair<int,int>> pq; // 按 first 降序，相同时按 second 降序
```

## --------------------------------------------------------------------------
## 三、成员函数总览
## --------------------------------------------------------------------------

| 函数 | 说明 |
|------|------|
| `pq.push(x)` | 插入元素，O(log n) |
| `pq.emplace(args...)` | 原位构造并插入 |
| `pq.pop()` | 弹出堆顶（无返回值） |
| `pq.top()` | 返回堆顶元素的引用 |
| `pq.size()` | 元素个数 |
| `pq.empty()` | 是否为空 |
| `pq.swap(pq2)` | 交换内容 |

**注意**: priority_queue 没有迭代器，不支持下标访问和遍历。

## --------------------------------------------------------------------------
## 四、洛谷实战
## --------------------------------------------------------------------------

### P1090 合并果子

```cpp
#include <iostream>
#include <queue>
using namespace std;

int main() {
    int n, ans = 0;
    priority_queue<int, vector<int>, greater<int>> pq;
    cin >> n;
    for (int i = 0, x; i < n; i++) { cin >> x; pq.push(x); }
    while (pq.size() > 1) {
        int a = pq.top(); pq.pop();
        int b = pq.top(); pq.pop();
        ans += a + b;
        pq.push(a + b);
    }
    cout << ans << endl;
    return 0;
}
```

### P4779 [模板] Dijkstra 堆优化

```cpp
#include <iostream>
#include <vector>
#include <queue>
using namespace std;

typedef pair<int,int> pii;
const int INF = 1e9;
vector<pii> g[100005];
int dist[100005];
bool vis[100005];

int main() {
    int n, m, s;
    cin >> n >> m >> s;
    for (int i = 1; i <= n; i++) dist[i] = INF;
    for (int i = 0, u, v, w; i < m; i++) {
        cin >> u >> v >> w;
        g[u].push_back({v, w});
    }
    priority_queue<pii, vector<pii>, greater<pii>> pq;
    dist[s] = 0;
    pq.push({0, s});
    while (!pq.empty()) {
        auto [d, u] = pq.top(); pq.pop();
        if (vis[u]) continue;
        vis[u] = true;
        for (auto [v, w] : g[u]) {
            if (dist[v] > dist[u] + w) {
                dist[v] = dist[u] + w;
                pq.push({dist[v], v});
            }
        }
    }
    for (int i = 1; i <= n; i++) cout << dist[i] << " ";
    return 0;
}
```

### P1801 黑匣子 / 对顶堆

```cpp
// 动态查询第 k 小的数
#include <iostream>
#include <queue>
using namespace std;

int a[200005];

int main() {
    int n, m, p = 0;
    cin >> n >> m;
    for (int i = 1; i <= n; i++) cin >> a[i];
    priority_queue<int> L; // 大根堆存较小的一半
    priority_queue<int, vector<int>, greater<int>> R; // 小根堆存较大的一半
    for (int i = 1, x; i <= m; i++) {
        cin >> x;
        while (p < x) {
            p++;
            // 插入 a[p]，维护两堆平衡
            if (L.empty() || a[p] <= L.top()) L.push(a[p]);
            else R.push(a[p]);
            while ((int)L.size() > i) { R.push(L.top()); L.pop(); }
            while ((int)L.size() < i) { L.push(R.top()); R.pop(); }
        }
        cout << L.top() << endl;
    }
    return 0;
}
```

## ==========================================================================
### 📝 章节测试
## ==========================================================================

> [!question] 判断题 1
> priority_queue 默认是大根堆，队首元素最大。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: 默认使用 `less<T>` 比较器，构建大根堆，top() 返回最大元素。

> [!question] 判断题 2
> priority_queue 的底层数据结构是红黑树。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: priority_queue 底层是二叉堆（通常基于 vector 实现），不是红黑树。set/map 才是红黑树。

> [!question] 判断题 3
> `priority_queue<int, vector<int>, greater<int>>` 是小根堆。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: 使用 `greater<int>` 比较器时，值小的优先级高，构成小根堆。

> [!question] 判断题 4
> priority_queue 的 `push()` 时间复杂度是 O(log n)。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: push 后需要上浮调整堆结构，最多经过 log n 层，时间 O(log n)。

> [!question] 判断题 5
> priority_queue 支持删除任意位置的元素。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: priority_queue 只支持删除堆顶元素（pop），不支持删除中间元素。需要删除可以用懒删除标记。

> [!question] 判断题 6
> priority_queue 支持迭代器遍历。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: priority_queue 是容器适配器，不提供迭代器。

> [!question] 判断题 7
> 自定义类型放入 priority_queue 时，需要重载 `<` 运算符（默认大根堆）。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: 默认大根堆使用 `less<T>`，需要类型支持 `<` 运算符。

> [!question] 判断题 8
> priority_queue 的 `top()` 时间复杂度是 O(log n)。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: `top()` 只是返回堆顶元素的引用，时间复杂度 O(1)。`push` 和 `pop` 才是 O(log n)。

> [!question] 判断题 9
> Dijkstra 算法使用小根堆优先队列可以优化时间复杂度到 O((V+E)log V)。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: 使用小根堆每次取出距离最小的节点，总共 push/pop 次数为 O(V+E)，每次 O(log V)。

> [!question] 判断题 10
> priority_queue 定义在 `<priority_queue>` 头文件中。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: priority_queue 定义在 `<queue>` 头文件中，与 queue 共享同一头文件。

> [!question] 选择题 1
> priority_queue 的 `pop()` 操作的时间复杂度是？
> - [ ] A. O(1)
> - [ ] B. O(log n)
> - [ ] C. O(n)
> - [ ] D. O(n log n)
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: pop 删除堆顶后需要下沉调整，最多 log n 层，时间 O(log n)。

> [!question] 选择题 2
> 以下哪个是小根堆的正确声明？
> - [ ] A. `priority_queue<int>`
> - [ ] B. `priority_queue<int, vector<int>, less<int>>`
> - [ ] C. `priority_queue<int, vector<int>, greater<int>>`
> - [ ] D. `priority_queue<int, deque<int>>`
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > 
> > **解析**: 使用 `greater<int>` 作为比较器构建小根堆。

> [!question] 选择题 3
> 合并果子问题中，为什么使用小根堆？
> - [ ] A. 因为要先处理最大的果子
> - [ ] B. 因为每次取最小的两堆合并代价最小
> - [ ] C. 因为小根堆速度更快
> - [ ] D. 因为大根堆不支持此操作
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: 贪心策略：每次取最小的两堆合并，总代价最小（哈夫曼思想）。

> [!question] 选择题 4
> `priority_queue<pair<int,int>>` 中，以下哪个 pair 会在堆顶？
> - [ ] A. {1, 100}
> - [ ] B. {5, 2}
> - [ ] C. {5, 3}
> - [ ] D. {3, 99}
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > 
> > **解析**: 默认大根堆，pair 按字典序比较。first 最大的是 5（B和C），second 比较 3>2，所以 {5,3} 最大。

> [!question] 选择题 5
> Dijkstra 堆优化中，遇到已访问过的节点应该？
> - [ ] A. 更新其距离
> - [ ] B. 重新入堆
> - [ ] C. 直接跳过（continue）
> - [ ] D. 从堆中删除
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > 
> > **解析**: 已确定最短路的节点无需再处理，直接 continue 跳过。

> [!question] 选择题 6
> 对顶堆（大根堆 + 小根堆）可以动态维护？
> - [ ] A. 区间最大值
> - [ ] B. 中位数
> - [ ] C. 最小值
> - [ ] D. 元素总和
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: 大根堆存较小的一半，小根堆存较大的一半，两者交界处就是中位数。

> [!question] 选择题 7
> priority_queue 不支持以下哪个操作？
> - [ ] A. `push()`
> - [ ] B. `top()`
> - [ ] C. `pop()`
> - [ ] D. `front()`
>
> > [!success]- 点击查看答案
> > 正确答案: D
> > 
> > **解析**: priority_queue 用 `top()` 访问堆顶，没有 `front()` 和 `back()`。

> [!question] 选择题 8
> 以下代码输出什么？
> ```cpp
> priority_queue<int> pq;
> pq.push(3); pq.push(1); pq.push(4);
> cout << pq.top();
> ```
> - [ ] A. 1
> - [ ] B. 3
> - [ ] C. 4
> - [ ] D. 未定义
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > 
> > **解析**: 默认大根堆，top() 返回最大值 4。

> [!question] 选择题 9
> 若要在 priority_queue 中实现"懒删除"，通常怎么做？
> - [ ] A. 调用 erase 函数
> - [ ] B. 标记元素已删除，pop 时检查跳过
> - [ ] C. 使用迭代器删除
> - [ ] D. 重建整个堆
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: priority_queue 不支持 erase，常用懒删除：用集合记录已删除元素，pop 时发现是已删除的就跳过。

> [!question] 选择题 10
> 自定义比较器 `struct cmp { bool operator()(int a, int b) { return a > b; } };` 构建的是？
> - [ ] A. 大根堆
> - [ ] B. 小根堆
> - [ ] C. 编译错误
> - [ ] D. 无序容器
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: 比较器返回 true 表示 a 的优先级低于 b。`a > b` 返回 true 意味着大的优先级低，所以是小根堆。

### 动手练习题

> [!question] 练习题 1
> **题目**: 实现"合并果子"：n 堆果子，每次取最小的两堆合并（代价为两堆之和），求总最小代价。使用 priority_queue 小根堆实现。
> 
> **输入示例**:
> ```
> 3
> 1 2 9
> ```
> **输出示例**:
> ```
> 15
> ```

> [!question] 练习题 2
> **题目**: 实现动态中位数：依次读入 n 个整数，每读入一个奇数位置的数后输出当前中位数。使用对顶堆（一个大根堆 + 一个小根堆）实现。
> 
> **输入示例**:
> ```
> 7
> 1 5 3 8 2 6 4
> ```
> **输出示例**:
> ```
> 1 3 3 4
> ```

> [!question] 练习题 3
> **题目**: 给定 n 个整数和一个正整数 k，求第 k 小的元素。使用大小为 k 的大根堆实现，要求空间复杂度 O(k)。
> 
> **输入示例**:
> ```
> 7 3
> 3 1 4 1 5 9 2
> ```
> **输出示例**:
> ```
> 2
> ```

## --------------------------------------------------------------------------
## 🔗 知识网络
## --------------------------------------------------------------------------

- **上一容器**: [[容器类/06_deque]] | **下一容器**: [[容器类/08_list_forward_list]] | **返回**: [[目录]]
- **相关**: [[数据结构/C_堆_Heap]] | [[算法技巧/贪心]]
