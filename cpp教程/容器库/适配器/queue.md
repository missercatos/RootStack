---
template <typename T, typename Container = deque<T>>
class queue
template <typename T, typename Container = vector<T>, typename Compare = less<typename Container::value_type>>
class priority_queue
---

queue 和 priority_queue 均为**容器适配器**。queue 封装底层容器实现先进先出（FIFO）：队尾插入，队首删除。priority_queue 基于堆实现，保证队首始终为优先级最高的元素（默认最大值）。

---

## queue

### 底层数据结构

默认底层为 `deque`，可指定 `list`。限制只能队尾插入、队首删除。

### 复杂度

| 操作 | 复杂度 | 说明 |
|------|--------|------|
| push(x) | O(1) | 队尾插入 |
| pop() | O(1) | 队首删除 |
| front() | O(1) | 返回队首引用 |
| back() | O(1) | 返回队尾引用 |
| size() / empty() | O(1) | |
| swap(q2) | O(1) | |

### 关键方法

| 方法 | 说明 |
|------|------|
| push(x) | 队尾入队 |
| emplace(args...) | 队尾原位构造 |
| pop() | 队首出队（返回 void） |
| front() | 队首引用 |
| back() | 队尾引用 |
| size() / empty() | 判空/查数 |

### 伪代码示例

```
queue<int> q

// BFS 广度优先搜索
q.push(start)
visited[start] = true
while not q.empty():
    cur = q.front()
    q.pop()
    for each neighbor of cur:
        if not visited[neighbor]:
            visited[neighbor] = true
            q.push(neighbor)

// 约瑟夫环
queue<int> circle
for i from 1 to n:
    circle.push(i)
while not circle.empty():
    for i from 1 to m - 1:
        circle.push(circle.front())
        circle.pop()
    print circle.front()
    circle.pop()
```

---

## priority_queue

### 底层数据结构

**二叉堆**（默认大根堆），底层容器通常为 `vector`。push 时上浮调整，pop 时下沉调整，均 O(log n)。

### 复杂度

| 操作 | 复杂度 | 说明 |
|------|--------|------|
| push(x) | O(log n) | 插入并上浮 |
| pop() | O(log n) | 弹出堆顶并下沉 |
| top() | O(1) | 返回堆顶 const 引用 |
| size() / empty() | O(1) | |

### 关键方法

| 方法 | 说明 |
|------|------|
| push(x) | 插入元素 |
| emplace(args...) | 原位构造并插入 |
| pop() | 弹出堆顶（返回 void） |
| top() | 堆顶 const 引用 |

### 指定大/小根堆

```
// 默认大根堆
priority_queue<int> maxHeap

// 小根堆
priority_queue<int, vector<int>, greater<int>> minHeap

// 自定义比较器
struct Compare { bool operator()(int a, int b) { return a > b; } }
priority_queue<int, vector<int>, Compare> pq
```

### 伪代码示例

```
// 合并果子（小根堆）
priority_queue<int, vector<int>, greater<int>> pq
for each x in fruits:
    pq.push(x)
total = 0
while pq.size() > 1:
    a = pq.top(); pq.pop()
    b = pq.top(); pq.pop()
    total += a + b
    pq.push(a + b)

// Dijkstra 堆优化
priority_queue<{dist, node}, vector, greater> pq
dist[start] = 0
pq.push({0, start})
while not pq.empty():
    {d, u} = pq.top(); pq.pop()
    if d != dist[u]: continue
    for each {v, w} of u:
        if dist[v] > dist[u] + w:
            dist[v] = dist[u] + w
            pq.push({dist[v], v})
```

## 相关链接

- queue: [[../../../数据结构/F_队列_Queue]] | [[../../../数据结构/F_队列_Queue]]
- priority_queue: [[../../../数据结构/C_堆_Heap]] | [[../../../数据结构/C_堆_Heap]]
- [[stack]]
