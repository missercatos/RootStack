---
title: "std::priority_queue 优先队列"
---

## 底层数据结构

**二叉堆**（默认大根堆），底层容器通常为 `vector`。逻辑上是一棵完全二叉树，物理上用连续数组存储。第 i 个节点的左子节点下标为 2i+1，右子节点为 2i+2，父节点为 (i-1)/2。push 时上浮（sift up），pop 时下沉（sift down），均 O(log n)。

```
大根堆的数组表示:

数组:  [90, 70, 80, 30, 50, 60, 20, 10]

逻辑二叉树:
              90            ← index 0
            /    \
          70      80        ← index 1, 2
         /  \    /  \
       30    50 60   20     ← index 3, 4, 5, 6
       /
     10                       ← index 7

父节点 parent(i) = (i-1) / 2
左子节点 left(i) = 2*i + 1
右子节点 right(i) = 2*i + 2

push 操作（上浮）:
  将新元素放到末尾，然后与父节点比较，比父大就交换，直到满足堆性质
  [90, 70, 80, 30, 50, 60, 20, 10, 85]
  85 的父是 30(index=3) → 交换
  [90, 70, 80, 85, 50, 60, 20, 10, 30]
  85 的父是 90(index=0) → 不交换，结束

pop 操作（下沉）:
  将堆顶与末尾交换，删除末尾，然后堆顶与较大子节点比较并交换
  [90, 70, 80, 30, 50, 60, 20, 10] → pop
  交换 90 和 10: [10, 70, 80, 30, 50, 60, 20]
  10 下沉: 与 80(较大的子) 交换 → [80, 70, 10, 30, 50, 60, 20]
  10 继续下沉: 与 20(较大的子) 交换 → [80, 70, 20, 30, 50, 60, 10]
```

### 小根堆

```cpp
// 用 greater<int> 作为比较器
priority_queue<int, vector<int>, greater<int>> minHeap;

// 逻辑树:
//         10
//        /  \
//      20    30
//     / \    / \
//    40  50 60  70

minHeap.push(10);
minHeap.push(20);
minHeap.top();  // 10
```

## 复杂度

| 操作 | 复杂度 | 说明 |
|------|--------|------|
| push(x) | O(log n) | 尾部插入后上浮调整 |
| emplace(args...) | O(log n) | 原位构造后上浮 |
| pop() | O(log n) | 堆顶与末尾交换后下沉调整 |
| top() | O(1) | 返回堆顶 const 引用 |
| size() / empty() | O(1) | |
| swap(pq2) | O(1) | 交换两个堆 |

## 关键方法

| 方法 | 说明 |
|------|------|
| push(x) | 插入元素，O(log n) |
| emplace(args...) | 原位构造并插入 |
| pop() | 弹出堆顶（返回 void） |
| top() | 堆顶 const 引用 |

## 指定堆类型

```cpp
// 大根堆（默认）
priority_queue<int> maxHeap;

// 小根堆
priority_queue<int, vector<int>, greater<int>> minHeap;

// 自定义比较器（返回 true 表示前者优先级更低）
struct Compare {
    bool operator()(int a, int b) { return a > b; }  // 小根堆
};
priority_queue<int, vector<int>, Compare> pq;

// 存放 pair，按 first 排序
priority_queue<pair<int, string>> pqPair;

// 自定义结构体
struct Task {
    int priority;
    string name;
    bool operator<(const Task& o) const {
        return priority < o.priority;  // 大根堆
    }
};
priority_queue<Task> tasks;
```

## make_heap 与底层操作

```cpp
vector<int> v = {3, 1, 4, 1, 5, 9, 2, 6};

// 将 vector 转为堆
make_heap(v.begin(), v.end());          // 大根堆
make_heap(v.begin(), v.end(), greater<>()); // 小根堆

// 插入元素
v.push_back(7);
push_heap(v.begin(), v.end());  // 上浮新元素

// 弹出堆顶
pop_heap(v.begin(), v.end());  // 堆顶移到末尾
v.pop_back();                  // 删除末尾

// 堆排序
sort_heap(v.begin(), v.end());  // 原地排序（升序）
```

## Dijkstra 最短路径示例

```cpp
// 用 priority_queue 实现 Dijkstra
vector<vector<pair<int,int>>> adj(n);  // 邻接表: adj[u] = {{v, w}, ...}
vector<int> dist(n, INT_MAX);
dist[start] = 0;

// {距离, 节点}，小根堆
priority_queue<pair<int,int>, vector<pair<int,int>>, greater<>> pq;
pq.push({0, start});

while (!pq.empty()) {
    auto [d, u] = pq.top(); pq.pop();
    if (d != dist[u]) continue;  // 过时数据跳过
    for (auto [v, w] : adj[u]) {
        if (dist[v] > dist[u] + w) {
            dist[v] = dist[u] + w;
            pq.push({dist[v], v});
        }
    }
}
```

## 合并果子（贪心）

```cpp
// 每次取最小的两堆合并
priority_queue<int, vector<int>, greater<int>> pq;
for (int x : fruits) pq.push(x);

int total = 0;
while (pq.size() > 1) {
    int a = pq.top(); pq.pop();
    int b = pq.top(); pq.pop();
    total += a + b;
    pq.push(a + b);
}
cout << total << endl;
```

## 对顶堆求动态中位数

```cpp
priority_queue<int> left;  // 大根堆存较小的一半
priority_queue<int, vector<int>, greater<int>> right;  // 小根堆存较大的一半

void add(int x) {
    if (left.empty() || x <= left.top()) {
        left.push(x);
    } else {
        right.push(x);
    }
    // 平衡大小
    if (left.size() > right.size() + 1) {
        right.push(left.top()); left.pop();
    }
    if (right.size() > left.size()) {
        left.push(right.top()); right.pop();
    }
}

int median() {
    return left.top();  // left.size() >= right.size()
}
```

## 常见陷阱

| 陷阱 | 说明 |
|------|------|
| top 不弹出 | top() 返回引用但不删除，pop() 删除但不返回 |
| pop 丢返回值 | pop() 返回 void，需先 top() 再 pop() |
| 不能遍历 | priority_queue 没有迭代器，无法遍历 |
| 不能修改 | 无法直接修改堆中元素，需弹出后重新插入 |
| 小根堆语法 | `greater<>` 需要 `#include <functional>` |
| 自定义结构体 | 必须定义 operator< 或提供 Compare |

## 优先队列 vs 排序

| 特性 | priority_queue | sort |
|------|---------------|------|
| 插入 | O(log n) | — |
| 取最大/最小 | O(1) | O(1)（排序后） |
| 取第二大 | O(log n) | O(1) |
| 全部排序 | O(n log n) | O(n log n) |
| 适用场景 | 流式数据、Top K | 一次性排序 |

## 力扣练习

| 题号 | 题目 | 链接 | 知识点 |
|------|------|------|--------|
| 215 | 数组中的第K个最大元素 | https://leetcode.cn/problems/kth-largest-element-in-an-array/ | 堆 / 快速选择 |
| 239 | 滑动窗口最大值 | https://leetcode.cn/problems/sliding-window-maximum/ | 单调队列 |
| 295 | 数据流的中位数 | https://leetcode.cn/problems/find-median-from-data-stream/ | 对顶堆 |
| 347 | 前 K 个高频元素 | https://leetcode.cn/problems/top-k-frequent-elements/ | 哈希 + 堆 |
| 373 | 查找和最小的 K 对数字 | https://leetcode.cn/problems/find-k-pairs-with-smallest-sums/ | 优先队列 |
| 502 | IPO | https://leetcode.cn/problems/ipo/ | 贪心 + 堆 |
| 621 | 任务调度器 | https://leetcode.cn/problems/task-scheduler/ | 贪心 + 计数 |
| 703 | 数据流中的第 K 大元素 | https://leetcode.cn/problems/kth-largest-element-in-a-stream/ | 小根堆维护 K 个 |
| 767 | 重组字符串 | https://leetcode.cn/problems/reorganize-string/ | 贪心 + 堆 |
| 1046 | 最后一块石头的重量 | https://leetcode.cn/problems/last-stone-weight/ | 大根堆模拟 |

## 相关链接

- [[../../../数据结构/I_堆_Heap]]
- [[queue]] | [[stack]]
