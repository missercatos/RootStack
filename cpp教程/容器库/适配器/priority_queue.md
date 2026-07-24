---
title: "template <typename T, typename Container = vector<T>, typename Compare = less<typename Container::value_type>>
class priority_queue"
---

## 底层数据结构

**二叉堆**（默认大根堆），底层容器通常为 `vector`。逻辑上是一棵完全二叉树，物理上用连续数组存储。第 i 个节点的左子节点下标为 2i+1，右子节点为 2i+2，父节点为 (i-1)/2。push 时上浮（sift up），pop 时下沉（sift down），均 O(log n)。

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

```
// 大根堆（默认）
priority_queue<int> maxHeap

// 小根堆
priority_queue<int, vector<int>, greater<int>> minHeap

// 自定义比较器（返回 true 表示前者优先级更低）
struct Compare {
    bool operator()(int a, int b) { return a > b; }  // 小根堆
}
priority_queue<int, vector<int>, Compare> pq

// 存放 pair，按 first 排序
priority_queue<pair<int, string>> pqPair
```

## 伪代码示例

```
// 合并果子（贪心 + 小根堆）
priority_queue<int, vector<int>, greater<int>> pq
for each x in fruits:
    pq.push(x)
total_cost = 0
while pq.size() > 1:
    a = pq.top(); pq.pop()
    b = pq.top(); pq.pop()
    total_cost += a + b
    pq.push(a + b)

// Dijkstra 最短路径
priority_queue<{dist, node}, vector, greater> pq
dist[start] = 0
pq.push({0, start})
while not pq.empty():
    {d, u} = pq.top(); pq.pop()
    if d != dist[u]: continue       // 过时数据跳过
    for each {v, w} adjacent to u:
        if dist[v] > dist[u] + w:
            dist[v] = dist[u] + w
            pq.push({dist[v], v})

// 对顶堆求动态中位数
priority_queue<int> left              // 大根堆存较小的一半
priority_queue<int, vector, greater> right  // 小根堆存较大的一半
function add(x):
    if left.empty() or x <= left.top():
        left.push(x)
    else:
        right.push(x)
    // 平衡大小
    if left.size() > right.size() + 1:
        right.push(left.top()); left.pop()
    if right.size() > left.size():
        left.push(right.top()); right.pop()
function median():
    return left.top()
```

## 相关链接

- [[../../../数据结构/I_堆_Heap]]
- [[../../../数据结构/I_堆_Heap]]
- [[queue]] | [[stack]]
