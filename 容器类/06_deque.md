# STL 容器速通 — deque (双端队列)

deque（double-ended queue，双端队列）支持在头部和尾部都进行 O(1) 的插入与删除，同时还支持 O(1) 的随机访问（下标）。它是 stack 和 queue 的默认底层容器。

deque 没有专门的抽象数据结构章节，这里简要说明它的底层：deque 并非一整块连续内存，而是由一个"中控器"（map，本质是一个指针数组）管理多段定长的连续缓冲区。下标访问时先在中控器里定位到第几段缓冲区、再定位段内偏移，因此随机访问仍是 O(1)，只是常数比 vector 略大。在两端扩张时只需新增缓冲区并登记到中控器，无需像 vector 那样把全部元素整体搬迁。

## 一、优缺点

| 优点 | 缺点 |
|------|------|
| 头尾插入删除均为 O(1) | 随机访问常数比 vector 大 |
| 支持 operator[] 随机访问 | 内存非单块连续，缓存命中率较低 |
| 扩容无需整体搬迁元素 | 没有 capacity()/reserve() |
| 可作为 stack / queue 的底层 | 中间插入删除仍是 O(n) |

## 二、适用场景

| 场景 | 说明 |
|------|------|
| 0-1 BFS | 权 0 的边 push_front，权 1 的边 push_back |
| 滑动窗口最值 | 维护单调双端队列，O(n) 求区间最值 |
| 两端频繁增删 | 比 vector 多了头部 O(1) 操作 |
| 既要下标又要双端 | 兼具 vector 与 queue 的部分能力 |

## 三、成员函数总览

| 函数 | 说明 | 时间复杂度 |
|------|------|-----------|
| `dq.push_back(x)` / `dq.push_front(x)` | 尾 / 头插入 | O(1) |
| `dq.pop_back()` / `dq.pop_front()` | 尾 / 头删除 | O(1) |
| `dq.emplace_back / emplace_front` | 两端原位构造 | O(1) |
| `dq[i]` / `dq.at(i)` | 下标 / 安全访问 | O(1) |
| `dq.front()` / `dq.back()` | 首 / 尾引用 | O(1) |
| `dq.insert(pos, x)` | 中间插入 | O(n) |
| `dq.erase(pos)` | 中间删除 | O(n) |
| `dq.size()` / `dq.empty()` | 个数 / 判空 | O(1) |
| `dq.clear()` | 清空 | O(n) |

## 四、动手实践（渐进操作）

下面按"创建 → size/empty → 插入 → 访问 → 修改 → 删除 → 遍历 → 清空"的顺序逐步练习。每一步只给提示与陷阱，请你对照"成员函数总览"自己把代码敲出来。

### 步骤 1：创建

> [!tip] 自己动手
> 函数：包含头文件 `<deque>`；可写空 `deque<int> dq;`、定值 `deque<int>(5, 10)`、列表 `deque<int>{1,2,3}`、拷贝 `deque<int>(other)`、迭代器范围 `deque<int>(b, e)`。
> 陷阱：deque 与 stack/queue 不同，它支持列表初始化，别再逐个 push 了。

### 步骤 2：size / empty

> [!tip] 自己动手
> 函数：`size()` 取元素个数，`empty()` 判断是否为空。
> 陷阱：deque 没有 `capacity()` / `reserve()`，别用 vector 的容量思路去优化它。

### 步骤 3：插入

> [!tip] 自己动手
> 函数：尾部 `push_back` / `emplace_back`，头部 `push_front` / `emplace_front`；任意位置 `insert(pos, x)`。
> 陷阱：两端插入是 O(1)，中间 `insert` 是 O(n)；任意插入都会使全部迭代器失效。

### 步骤 4：访问

> [!tip] 自己动手
> 函数：`dq[i]` 下标访问（不检查越界）、`dq.at(i)` 安全访问（越界抛 out_of_range）、`front()` / `back()` 取首尾。
> 陷阱：`operator[]` 越界是未定义行为；对性能不敏感且需要安全时优先 `at()`。

### 步骤 5：修改

> [!tip] 自己动手
> 函数：`dq[i]`、`at(i)`、`front()`、`back()` 都返回可写引用，直接赋值即可修改对应元素。
> 陷阱：修改不会改变元素个数；越界写入仍是未定义行为。

### 步骤 6：删除

> [!tip] 自己动手
> 函数：尾部 `pop_back`、头部 `pop_front`、任意位置 `erase(pos)`。
> 陷阱：两端删除 O(1)，中间 `erase` 是 O(n)；删除前先判 `empty()`，且删除会使迭代器失效。

### 步骤 7：遍历

> [!tip] 自己动手
> 函数：deque 提供随机访问迭代器，三种写法都行——下标 `for (i...) dq[i]`、迭代器 `for (auto it=begin; it!=end; ++it)`、范围 `for (auto& x : dq)`。
> 陷阱：因为是随机访问迭代器，`sort` 等算法可直接作用于 deque；但遍历过程中别同时增删元素。

### 步骤 8：清空

> [!tip] 自己动手
> 函数：deque 有 `clear()`，一行即可清空全部元素。
> 陷阱：与 stack/queue 不同，这里直接 `clear()` 即可，无需循环 pop。

## 五、经典实战

### 滑动窗口最值（洛谷 P1886）

```cpp
#include <iostream>
#include <deque>
using namespace std;

int a[1000005];

int main() {
    int n, k;
    cin >> n >> k;
    for (int i = 1; i <= n; i++) cin >> a[i];

    deque<int> dq; // 存下标，对应值单调递增 -> 队首为最小
    for (int i = 1; i <= n; i++) {
        while (!dq.empty() && a[dq.back()] >= a[i]) dq.pop_back();
        dq.push_back(i);
        if (dq.front() <= i - k) dq.pop_front();
        if (i >= k) cout << a[dq.front()] << " ";
    }
    cout << "\n";

    dq.clear();
    for (int i = 1; i <= n; i++) { // 最大值：单调递减
        while (!dq.empty() && a[dq.back()] <= a[i]) dq.pop_back();
        dq.push_back(i);
        if (dq.front() <= i - k) dq.pop_front();
        if (i >= k) cout << a[dq.front()] << " ";
    }
    return 0;
}
```

### 0-1 BFS（洛谷 P1346 电车）

```cpp
#include <iostream>
#include <deque>
#include <vector>
using namespace std;

const int INF = 1e9;
int dist[105];
vector<pair<int,int>> g[105];

int main() {
    int n, a, b;
    cin >> n >> a >> b;
    for (int i = 1; i <= n; i++) dist[i] = INF;
    for (int u = 1; u <= n; u++) {
        int k, v; cin >> k;
        for (int j = 0; j < k; j++) {
            cin >> v;
            g[u].push_back({v, j == 0 ? 0 : 1});
        }
    }
    deque<int> dq;
    dist[a] = 0;
    dq.push_front(a);
    while (!dq.empty()) {
        int u = dq.front(); dq.pop_front();
        for (auto [v, w] : g[u]) {
            if (dist[v] > dist[u] + w) {
                dist[v] = dist[u] + w;
                if (w == 0) dq.push_front(v); // 权 0 进队首
                else dq.push_back(v);         // 权 1 进队尾
            }
        }
    }
    cout << (dist[b] == INF ? -1 : dist[b]) << "\n";
    return 0;
}
```

## 六、推荐练习题目

| 题号 | 平台 | 题目 | 核心考察 | 难度 |
|------|------|------|---------|------|
| P1886 | 洛谷 | 滑动窗口 | 单调队列求区间最值 | 普及/提高- |
| P1440 | 洛谷 | 求 m 区间内的最小值 | 单调队列 | 普及/提高- |
| P1714 | 洛谷 | 切蛋糕 | 前缀和 + 单调队列 | 普及/提高- |
| P2032 | 洛谷 | 扫描 | 单调队列模板 | 普及/提高- |
| P1346 | 洛谷 | 电车 | 0-1 BFS 双端队列 | 普及/提高- |
| 239 | 力扣 | 滑动窗口最大值 | 单调队列 | 困难 |
| 641 | 力扣 | 设计循环双端队列 | 双端队列接口 | 中等 |
| 862 | 力扣 | 和至少为 K 的最短子数组 | 前缀和 + 单调队列 | 困难 |

## 八、自己动手

> [!question] 练习题 1
> 给定 n 个整数和窗口大小 k，输出每个窗口的最小值，要求 O(n)。
>
> 提示：用 `deque<int>` 存下标维护单调递增队列；新元素入队前从 back 弹出所有 `a[back] >= a[i]`，再判断 front 是否过期（下标 ≤ i-k）从 front 弹出。
> 陷阱：队列里存的是下标不是值，比较时用 `a[下标]`；窗口未满（i<k）时不要输出。

> [!question] 练习题 2
> 在 n×m 网格中从 (1,1) 到 (n,m)，走空地代价 0、破墙代价 1，求最小代价（0-1 BFS）。
>
> 提示：用 `deque<位置>`，代价 0 的转移 push_front、代价 1 的转移 push_back；dist 数组记录最小代价，只在能松弛时更新并入队。
> 陷阱：出队节点可能已被更优路径更新过，取出后应判断当前 dist 是否仍最优再扩展，避免重复松弛。

> [!question] 练习题 3
> 用 deque 模拟支持插队的排队系统：操作有队尾入队、队首插队（VIP）、队首服务出队，输出每次服务的人编号。
>
> 提示：普通入队用 push_back，VIP 用 push_front，服务时取 front() 输出后 pop_front()。
> 陷阱：服务前要先判 empty()，对空队列调用 front()/pop_front() 是未定义行为。

## 九、知识网络

- 上一容器：[[容器类/05_queue]] | 下一容器：[[容器类/07_priority_queue]] | 返回：[[目录]]
- 相关：[[算法技巧/滑动窗口]] | [[数据结构/F_队列_Queue]]
