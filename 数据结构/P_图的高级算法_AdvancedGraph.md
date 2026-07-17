# P 图的高级算法 AdvancedGraph

建议先阅读: [[H_图_Graph|H 图 Graph]]

---

## 原理

本章介绍图论中的高级算法：拓扑排序、强连通分量（Tarjan）、多源最短路径（Floyd-Warshall）、含负权边的单源最短路径（Bellman-Ford）、网络流等。

### 算法总览

| 算法 | 用途 | 时间复杂度 | 条件 |
|------|------|-----------|------|
| Kahn 拓扑排序 | DAG 线性排序 | O(V+E) | 有向无环图 |
| Tarjan SCC | 强连通分量 | O(V+E) | 有向图 |
| Floyd-Warshall | 全源最短路径 | O(V^3) | 任意权图（无负环） |
| Bellman-Ford | 单源最短路径（负权） | O(VE) | 可检负环 |
| SPFA | Bellman-Ford 队列优化 | O(VE) 最坏 | 平均较快 |
| Dinic | 最大流 | O(V^2 E) | 流量网络 |

---

## 实现

### 拓扑排序（Kahn 算法）

```cpp
#include <vector>
#include <queue>

std::vector<int> topologicalSort(int V,
    const std::vector<std::vector<int>>& adj) {
    std::vector<int> inDegree(V, 0);
    for (int u = 0; u < V; ++u)
        for (int v : adj[u])
            ++inDegree[v];

    std::queue<int> q;
    for (int i = 0; i < V; ++i)
        if (inDegree[i] == 0) q.push(i);

    std::vector<int> result;
    while (!q.empty()) {
        int u = q.front(); q.pop();
        result.push_back(u);
        for (int v : adj[u])
            if (--inDegree[v] == 0)
                q.push(v);
    }

    // result.size() < V 则存在环
    return result;
}
```

### Tarjan SCC

```cpp
#include <vector>
#include <stack>
#include <algorithm>

class TarjanSCC {
private:
    std::vector<std::vector<int>> adj;
    std::vector<int> dfn, low, sccId;
    std::vector<bool> onStack;
    std::stack<int> stk;
    int timer, sccCount;

    void dfs(int u) {
        dfn[u] = low[u] = ++timer;
        stk.push(u);
        onStack[u] = true;

        for (int v : adj[u]) {
            if (!dfn[v]) {
                dfs(v);
                low[u] = std::min(low[u], low[v]);
            } else if (onStack[v]) {
                low[u] = std::min(low[u], dfn[v]);
            }
        }

        if (dfn[u] == low[u]) { // u 是 SCC 的根
            ++sccCount;
            while (true) {
                int v = stk.top(); stk.pop();
                onStack[v] = false;
                sccId[v] = sccCount;
                if (v == u) break;
            }
        }
    }

public:
    TarjanSCC(int V) : adj(V), dfn(V, 0), low(V, 0),
                        sccId(V, 0), onStack(V, false),
                        timer(0), sccCount(0) {}

    void addEdge(int u, int v) { adj[u].push_back(v); }

    int solve() {
        for (int i = 0; i < adj.size(); ++i)
            if (!dfn[i]) dfs(i);
        return sccCount;
    }

    int getSCCId(int u) { return sccId[u]; }
};
```

### Floyd-Warshall

```cpp
#include <vector>
#include <climits>

class FloydWarshall {
private:
    int V;
    std::vector<std::vector<long long>> dist;
    const long long INF = LLONG_MAX / 2;

public:
    FloydWarshall(int v) : V(v), dist(v, std::vector<long long>(v, INF)) {
        for (int i = 0; i < V; ++i) dist[i][i] = 0;
    }

    void addEdge(int u, int v, int w) {
        dist[u][v] = w;
    }

    bool solve() {
        for (int k = 0; k < V; ++k)
            for (int i = 0; i < V; ++i)
                for (int j = 0; j < V; ++j)
                    if (dist[i][k] < INF && dist[k][j] < INF)
                        dist[i][j] = std::min(dist[i][j],
                                              dist[i][k] + dist[k][j]);

        // 检测负环
        for (int i = 0; i < V; ++i)
            if (dist[i][i] < 0) return false;
        return true;
    }

    long long getDist(int u, int v) { return dist[u][v]; }
};
```

### Bellman-Ford

```cpp
#include <vector>
#include <climits>

struct Edge { int from, to, weight; };

std::pair<bool, std::vector<long long>>
bellmanFord(int V, const std::vector<Edge>& edges, int start) {
    const long long INF = LLONG_MAX / 2;
    std::vector<long long> dist(V, INF);
    dist[start] = 0;

    // V-1 轮松弛
    for (int i = 0; i < V - 1; ++i) {
        bool updated = false;
        for (auto& e : edges) {
            if (dist[e.from] < INF && dist[e.from] + e.weight < dist[e.to]) {
                dist[e.to] = dist[e.from] + e.weight;
                updated = true;
            }
        }
        if (!updated) break;
    }

    // 第 V 轮检测负环
    for (auto& e : edges) {
        if (dist[e.from] < INF && dist[e.from] + e.weight < dist[e.to])
            return {false, dist}; // 存在负环
    }
    return {true, dist};
}
```

### Dinic 最大流

```cpp
#include <vector>
#include <queue>
#include <climits>
#include <algorithm>

struct FlowEdge {
    int to, rev;
    long long cap;
};

class Dinic {
private:
    int V;
    std::vector<std::vector<FlowEdge>> graph;
    std::vector<int> level, iter;

    bool bfs(int s, int t) {
        level.assign(V, -1);
        std::queue<int> q;
        level[s] = 0; q.push(s);
        while (!q.empty()) {
            int u = q.front(); q.pop();
            for (auto& e : graph[u]) {
                if (e.cap > 0 && level[e.to] < 0) {
                    level[e.to] = level[u] + 1;
                    q.push(e.to);
                }
            }
        }
        return level[t] >= 0;
    }

    long long dfs(int u, int t, long long f) {
        if (u == t) return f;
        for (int& i = iter[u]; i < graph[u].size(); ++i) {
            auto& e = graph[u][i];
            if (e.cap > 0 && level[e.to] == level[u] + 1) {
                long long d = dfs(e.to, t, std::min(f, e.cap));
                if (d > 0) {
                    e.cap -= d;
                    graph[e.to][e.rev].cap += d;
                    return d;
                }
            }
        }
        return 0;
    }

public:
    Dinic(int v) : V(v), graph(v) {}

    void addEdge(int from, int to, long long cap) {
        graph[from].push_back({to, (int)graph[to].size(), cap});
        graph[to].push_back({from, (int)graph[from].size() - 1, 0});
    }

    long long maxFlow(int s, int t) {
        long long flow = 0;
        while (bfs(s, t)) {
            iter.assign(V, 0);
            long long f;
            while ((f = dfs(s, t, LLONG_MAX)) > 0)
                flow += f;
        }
        return flow;
    }
};
```

---

## 应用场景

- **拓扑排序**: 课程安排、编译依赖、任务调度
- **Tarjan SCC**: 社交网络互关圈分析、缩点后 DAG 上 DP
- **Floyd-Warshall**: 小规模全源最短路径（V <= 500）
- **Bellman-Ford/SPFA**: 含负权边的最短路径、负环检测
- **Dinic**: 二分图最大匹配、物流配送网络优化

---

## 练习

| 题号 | 题目 | 难度 | 知识点 |
|------|------|------|--------|
| P1113 | 杂务 | 普及 | 拓扑排序 |
| P3387 | 缩点 | 提高 | Tarjan + DAG 上 DP |
| P3385 | 负环 | 提高 | Bellman-Ford/SPFA |
| P3376 | 最大流 | 提高 | Dinic 网络流 |
