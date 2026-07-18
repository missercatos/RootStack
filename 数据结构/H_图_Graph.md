

建议先阅读: [[B_栈_Stack|B 栈 Stack]], [[F_队列_Queue|F 队列 Queue]]

---

## 原理

图（Graph）由顶点（Vertex）和连接顶点的边（Edge）组成，是最灵活的数据结构之一，可表示社交网络、地图导航、依赖关系等。

### 图的分类

- **有向图 vs 无向图**: 边是否有方向
- **加权图 vs 无权图**: 边是否有权重
- **连通图 vs 非连通图**: 任意两点是否可达
- **稠密图 vs 稀疏图**: E ~ V^2（稠密）或 E ~ V（稀疏）

### 相关术语

- 度（Degree）: 顶点连接的边数
- 出度/入度: 有向图中从该顶点出发/指向该顶点的边数
- 路径: 顶点序列，相邻顶点间有边
- 环: 起点等于终点的路径

### 存储方式

| 方式 | 空间 | 判边 | 遍历邻居 | 适用 |
|------|------|------|----------|------|
| 邻接矩阵 | O(V^2) | O(1) | O(V) | 稠密图 |
| 邻接表 | O(V+E) | O(degree) | O(degree) | 稀疏图 |

---

## 实现

### 邻接表图 + BFS/DFS

```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <stack>
#include <list>

class Graph {
private:
    int V;
    std::vector<std::list<int>> adj;

public:
    Graph(int v) : V(v), adj(v) {}

    void addEdge(int u, int v, bool directed = false) {
        adj[u].push_back(v);
        if (!directed) adj[v].push_back(u);
    }

    // BFS
    void bfs(int start) {
        std::vector<bool> visited(V, false);
        std::queue<int> q;
        visited[start] = true;
        q.push(start);

        while (!q.empty()) {
            int u = q.front(); q.pop();
            std::cout << u << " ";
            for (int v : adj[u])
                if (!visited[v]) {
                    visited[v] = true;
                    q.push(v);
                }
        }
        std::cout << std::endl;
    }

    // DFS（递归）
    void dfs(int start) {
        std::vector<bool> visited(V, false);
        dfsHelper(start, visited);
        std::cout << std::endl;
    }

    // DFS（迭代）
    void dfsIterative(int start) {
        std::vector<bool> visited(V, false);
        std::stack<int> stk;
        stk.push(start);
        while (!stk.empty()) {
            int u = stk.top(); stk.pop();
            if (visited[u]) continue;
            visited[u] = true;
            std::cout << u << " ";
            for (auto it = adj[u].rbegin(); it != adj[u].rend(); ++it)
                if (!visited[*it]) stk.push(*it);
        }
        std::cout << std::endl;
    }

    // BFS 最短路径（无权图）
    std::vector<int> shortestPath(int start, int end) {
        std::vector<bool> visited(V, false);
        std::vector<int> parent(V, -1);
        std::queue<int> q;
        visited[start] = true;
        q.push(start);

        while (!q.empty()) {
            int u = q.front(); q.pop();
            if (u == end) break;
            for (int v : adj[u])
                if (!visited[v]) {
                    visited[v] = true;
                    parent[v] = u;
                    q.push(v);
                }
        }

        std::vector<int> path;
        if (!visited[end]) return path;
        for (int v = end; v != -1; v = parent[v])
            path.push_back(v);
        std::reverse(path.begin(), path.end());
        return path;
    }

private:
    void dfsHelper(int u, std::vector<bool>& visited) {
        visited[u] = true;
        std::cout << u << " ";
        for (int v : adj[u])
            if (!visited[v]) dfsHelper(v, visited);
    }
};
```

### Dijkstra 最短路径

```cpp
#include <vector>
#include <queue>
#include <climits>

// 加权图
class WeightedGraph {
private:
    int V;
    std::vector<std::list<std::pair<int, int>>> adj; // {neighbor, weight}

public:
    WeightedGraph(int v) : V(v), adj(v) {}

    void addEdge(int u, int v, int w, bool directed = false) {
        adj[u].push_back({v, w});
        if (!directed) adj[v].push_back({u, w});
    }

    std::vector<int> dijkstra(int start) {
        std::vector<int> dist(V, INT_MAX);
        std::vector<bool> visited(V, false);
        // 最小堆: {距离, 顶点}
        std::priority_queue<std::pair<int, int>,
                            std::vector<std::pair<int, int>>,
                            std::greater<>> pq;

        dist[start] = 0;
        pq.push({0, start});

        while (!pq.empty()) {
            int u = pq.top().second; pq.pop();
            if (visited[u]) continue;
            visited[u] = true;

            for (auto& [v, w] : adj[u]) {
                if (!visited[v] && dist[u] + w < dist[v]) {
                    dist[v] = dist[u] + w;
                    pq.push({dist[v], v});
                }
            }
        }
        return dist;
    }
};
```

### Kruskal 最小生成树

```cpp
#include <vector>
#include <algorithm>

struct Edge { int u, v, w; };

class UnionFind {
    std::vector<int> parent, rank;
public:
    UnionFind(int n) : parent(n), rank(n, 0) {
        for (int i = 0; i < n; ++i) parent[i] = i;
    }
    int find(int x) {
        if (parent[x] != x) parent[x] = find(parent[x]);
        return parent[x];
    }
    bool unite(int x, int y) {
        int px = find(x), py = find(y);
        if (px == py) return false;
        if (rank[px] < rank[py]) std::swap(px, py);
        parent[py] = px;
        if (rank[px] == rank[py]) ++rank[px];
        return true;
    }
};

int kruskal(int V, std::vector<Edge> edges) {
    std::sort(edges.begin(), edges.end(),
              [](Edge& a, Edge& b) { return a.w < b.w; });

    UnionFind uf(V);
    int total_weight = 0;
    int cnt = 0;

    for (auto& e : edges) {
        if (uf.unite(e.u, e.v)) {
            total_weight += e.w;
            ++cnt;
            if (cnt == V - 1) break;
        }
    }
    return total_weight;
}
```

---

## 常用算法复杂度

| 算法 | 用途 | 时间复杂度 | 条件 |
|------|------|-----------|------|
| BFS | 无权最短路径、层序遍历 | O(V+E) | 任意图 |
| DFS | 遍历、环检测、连通分量 | O(V+E) | 任意图 |
| Dijkstra | 单源最短路径 | O((V+E)logV) | 非负权 |
| Bellman-Ford | 单源最短路径（可负权） | O(VE) | 可检负环 |
| Floyd-Warshall | 全源最短路径 | O(V^3) | 稠密图 |
| Kruskal | 最小生成树 | O(E log E) | 任意图 |
| Prim | 最小生成树 | O((V+E)logV) | 任意图 |

---

## 应用场景

- **地图导航**: 加权图 + Dijkstra/A* 寻路
- **社交网络**: 好友推荐（二度好友）、影响力分析（连通分量大小）
- **包依赖管理**: 有向无环图（DAG）+ 拓扑排序确定安装顺序

---

## 练习

| 题号 | 题目 | 难度 | 知识点 |
|------|------|------|--------|
| P3371 | 单源最短路径 | 普及 | Dijkstra/Bellman-Ford |
| P4779 | 单源最短路径（标准版） | 提高 | 堆优化 Dijkstra |
| P3366 | 最小生成树 | 普及+ | Kruskal/Prim |
| P5318 | 查找文献 | 入门 | BFS/DFS 遍历 |
