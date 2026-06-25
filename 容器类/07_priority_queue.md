# STL 容器速通 — priority_queue (优先队列)

priority_queue（优先队列）是基于堆实现的容器适配器，保证队首始终是优先级最高的元素（默认是最大值）。它底层借助 vector（或 deque）维护一个二叉堆，是 STL 里"动态取最值"最常用的工具。

priority_queue 是容器适配器，没有迭代器，不能遍历，也没有 operator[]；唯一的访问入口就是 top()。

> 想深入理解堆的结构、上浮下沉调整与建堆原理，请见 [[数据结构/C_堆_Heap]]。

## 一、优缺点

| 优点 | 缺点 |
|------|------|
| 取最值 top() 为 O(1) | 只能取最值，无法访问其他元素 |
| 插入 push、删除 pop 为 O(log n) | 没有迭代器，不能遍历 |
| 自动维护有序性，无需手动排序 | 不能删除堆顶以外的任意元素 |
| 支持自定义比较器，灵活定制大小根堆 | 没有 clear()，清空需手动 |

## 二、适用场景

| 场景 | 说明 |
|------|------|
| 动态取最值 / Top-K | 不断插入并取最大或最小值 |
| Dijkstra 堆优化 | 每次取距离最小的顶点 |
| 合并多路有序序列 | 用小根堆取各路当前最小 |
| 哈夫曼编码 / 合并果子 | 每次取最小的两个合并 |
| 贪心 + 堆优化 | 任务调度、区间问题 |

## 三、成员函数总览

| 函数 | 说明 | 时间复杂度 |
|------|------|-----------|
| `pq.push(x)` | 插入元素 | O(log n) |
| `pq.emplace(args...)` | 原位构造并插入 | O(log n) |
| `pq.pop()` | 弹出堆顶（无返回值） | O(log n) |
| `pq.top()` | 返回堆顶 const 引用 | O(1) |
| `pq.size()` | 元素个数 | O(1) |
| `pq.empty()` | 是否为空 | O(1) |
| `pq.swap(pq2)` | 交换两个堆 | O(1) |

## 四、动手实践（渐进操作）

下面按"创建 → size/empty → 插入 → 访问 → 修改 → 删除 → 遍历 → 清空"的顺序逐步练习。每一步只给提示与陷阱，请你对照"成员函数总览"自己把代码敲出来。

### 步骤 1：创建

> [!tip] 自己动手
> 函数：包含头文件 `<queue>`（注意不是 `<priority_queue>`）；`priority_queue<int>` 是默认大根堆，top() 最大；想要小根堆写 `priority_queue<int, vector<int>, greater<int>>`；也可写一个 `struct` 重载 `operator()` 或用 lambda 当比较器传第三个模板参数。
> 陷阱：自定义类型放入默认大根堆需要重载 `operator<`；比较器返回 true 表示"前者优先级更低"，方向容易写反，建议先小例子验证。

### 步骤 2：size / empty

> [!tip] 自己动手
> 函数：`size()` 取元素个数，`empty()` 判断是否为空。
> 陷阱：任何 `top()` / `pop()` 前先 `empty()` 判空，空堆操作是未定义行为。

### 步骤 3：插入（push）

> [!tip] 自己动手
> 函数：`push(x)` 插入并上浮调整（O(log n)）；`emplace(args...)` 原位构造后插入。
> 陷阱：插入复杂度是 O(log n) 而非 O(1)，大量插入要注意总开销。

### 步骤 4：访问（top）

> [!tip] 自己动手
> 函数：`top()` 返回堆顶（优先级最高）元素的 const 引用，O(1)。
> 陷阱：没有 `front()` / `back()` / `operator[]`，唯一入口是 `top()`；它返回的是 const 引用，不能直接改。

### 步骤 5：修改

> [!tip] 自己动手
> 函数：priority_queue 不支持直接修改任意元素。想"改堆顶"要先 `top()` 取值、`pop()` 删除，处理后再 `push()` 回去；想逻辑删/改中间元素常用"懒删除"——另开标记数组记录失效元素，pop 到它时跳过。
> 陷阱：直接给 `top()` 赋值无法编译（const），即便能改也不会触发堆的重新调整。

### 步骤 6：删除（pop）

> [!tip] 自己动手
> 函数：`pop()` 删除堆顶并下沉调整（O(log n)）。
> 陷阱：只能删堆顶；`pop()` 返回 void，取值要先 `top()` 再 `pop()`；空堆 pop 是未定义行为。

### 步骤 7：遍历

> [!tip] 自己动手
> 函数：priority_queue 没有迭代器，无法 for 遍历；要取出全部只能 `while (!empty())` 反复 `top()` + `pop()`，得到的是按优先级有序的序列。
> 陷阱：这种"遍历"会清空堆；要保留数据需先拷贝一份再遍历副本。

### 步骤 8：清空

> [!tip] 自己动手
> 函数：priority_queue 没有 `clear()`；用 `pq = priority_queue<int>();` 整体替换，或 `while (!empty()) pop();` 逐个弹出。
> 陷阱：整体替换时要用与原对象完全一致的模板参数类型，否则赋值不兼容。

## 五、经典实战

### 合并果子（洛谷 P1090）

```cpp
#include <iostream>
#include <queue>
using namespace std;

int main() {
    int n, ans = 0;
    priority_queue<int, vector<int>, greater<int>> pq; // 小根堆
    cin >> n;
    for (int i = 0, x; i < n; i++) { cin >> x; pq.push(x); }
    while (pq.size() > 1) {
        int a = pq.top(); pq.pop();
        int b = pq.top(); pq.pop();
        ans += a + b;
        pq.push(a + b);            // 合并结果重新入堆
    }
    cout << ans << "\n";
    return 0;
}
```

### Dijkstra 堆优化（洛谷 P4779）

```cpp
#include <iostream>
#include <vector>
#include <queue>
using namespace std;

typedef pair<int,int> pii;        // {距离, 顶点}
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
    priority_queue<pii, vector<pii>, greater<pii>> pq; // 小根堆按距离
    dist[s] = 0;
    pq.push({0, s});
    while (!pq.empty()) {
        auto [d, u] = pq.top(); pq.pop();
        if (vis[u]) continue;      // 已确定最短路，跳过
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

## 六、推荐练习题目

| 题号 | 平台 | 题目 | 核心考察 | 难度 |
|------|------|------|---------|------|
| P1090 | 洛谷 | 合并果子 | 贪心 + 小根堆 | 普及- |
| P4779 | 洛谷 | 单源最短路径(标准版) | Dijkstra 堆优化 | 普及+/提高 |
| P1801 | 洛谷 | 黑匣子 | 对顶堆动态第 k 小 | 提高+ |
| 215 | 力扣 | 数组中的第 K 个最大元素 | 堆 / Top-K | 中等 |
| 23 | 力扣 | 合并 K 个升序链表 | 多路归并 + 堆 | 困难 |
| P3378 | 洛谷 | 【模板】堆 | 优先队列基本操作 | 普及/提高- |
| 347 | 力扣 | 前 K 个高频元素 | 堆 + 哈希 / Top-K | 中等 |

## 七、自己动手

> [!question] 练习题 1
> 实现合并果子：n 堆果子，每次取最小两堆合并（代价为两堆之和），求总最小代价。
>
> 提示：用 `priority_queue<int, vector<int>, greater<int>>` 小根堆；当 size() 大于 1 时，连续两次 top()+pop() 取最小两堆，累加后把和 push 回堆。
> 陷阱：合并产生的新堆必须重新入堆参与后续合并；累加和可能很大，注意用足够宽的整型。

> [!question] 练习题 2
> 实现动态中位数：依次读入 n 个整数，每读入奇数个后输出当前中位数（对顶堆）。
>
> 提示：用一个大根堆存较小的一半、一个小根堆存较大的一半；每次插入后通过两堆互相 top()+pop() 搬移，维持大根堆元素数等于或恰多一个。
> 陷阱：插入新数前要先和大根堆堆顶比较决定进哪个堆；搬移后两堆大小关系务必恢复，否则中位数取错。

> [!question] 练习题 3
> 给定 n 个整数和正整数 k，求第 k 大的元素，要求空间 O(k)。
>
> 提示：维护一个大小固定为 k 的小根堆；遍历元素，堆不满直接 push，堆满且当前值大于 top() 时 pop() 再 push()，最终堆顶即第 k 大。
> 陷阱：用小根堆而非大根堆才能 O(k) 空间淘汰较小值；堆未满时不要做替换判断。

## 八、知识网络

- 上一容器：[[容器类/06_deque]] | 下一容器：[[容器类/08_list_forward_list]] | 返回：[[目录]]
- 相关：[[数据结构/C_堆_Heap]] | [[算法技巧/贪心]]
