## ==========================================================================
C++ 数据结构教程 — 图的高级算法 (Advanced Graph Algorithms)
## ==========================================================================

## 📋 章节概述

本章介绍图论中的高级算法，包括拓扑排序、强连通分量（Tarjan算法）、
全源最短路径（Floyd-Warshall）、含负权边的单源最短路径（Bellman-Ford）
以及网络流算法。这些算法是图论的精华，在编译器依赖分析、社交网络分析、
路由协议、物流优化等领域有广泛应用。

本章将从每个算法的核心思想讲起，给出完整的C++实现，
通过实际案例展示算法的应用场景，最后通过习题巩固所学知识。

## ==========================================================================
### 📖 第一节: 基础语法 + 计算机底层原理
## ==========================================================================

1.1 拓扑排序（Topological Sort）
----------------------------------

拓扑排序用于有向无环图（DAG），将所有顶点排成线性序列，使得对于每条有向边(u,v)，
u在序列中出现在v之前。

应用场景：
- 课程选课顺序
- 编译依赖关系
- 任务调度

**Kahn算法（BFS）实现：**

```cpp
#include <iostream>
#include <vector>
#include <queue>

class TopologicalSort {
private:
    int V;
    std::vector<std::vector<int>> adj;

public:
    TopologicalSort(int v) : V(v), adj(v) {}

    void addEdge(int u, int v) { adj[u].push_back(v); }

    std::vector<int> kahnSort() {
        std::vector<int> inDegree(V, 0);
        for (int u = 0; u < V; ++u)
            for (int v : adj[u])
                inDegree[v]++;

        std::queue<int> q;
        for (int i = 0; i < V; ++i)
            if (inDegree[i] == 0)
                q.push(i);

        std::vector<int> result;
        while (!q.empty()) {
            int u = q.front(); q.pop();
            result.push_back(u);
            for (int v : adj[u]) {
                if (--inDegree[v] == 0)
                    q.push(v);
            }
        }

        if ((int)result.size() != V) {
            std::cout << "图中存在环，无法拓扑排序!" << std::endl;
            return {};
        }
        return result;
    }

    std::vector<int> dfsSort() {
        std::vector<int> order;
        std::vector<int> state(V, 0);
        bool hasCycle = false;

        for (int i = 0; i < V && !hasCycle; ++i)
            if (state[i] == 0)
                dfs(i, state, order, hasCycle);

        if (hasCycle) return {};
        std::reverse(order.begin(), order.end());
        return order;
    }

private:
    void dfs(int u, std::vector<int>& state, std::vector<int>& order, bool& hasCycle) {
        if (hasCycle) return;
        state[u] = 1;
        for (int v : adj[u]) {
            if (state[v] == 1) { hasCycle = true; return; }
            if (state[v] == 0) dfs(v, state, order, hasCycle);
        }
        state[u] = 2;
        order.push_back(u);
    }
};

int main() {
    TopologicalSort ts(6);
    ts.addEdge(5, 2);
    ts.addEdge(5, 0);
    ts.addEdge(4, 0);
    ts.addEdge(4, 1);
    ts.addEdge(2, 3);
    ts.addEdge(3, 1);

    auto order = ts.kahnSort();
    std::cout << "拓扑排序(Kahn): ";
    for (int v : order) std::cout << v << " ";
    std::cout << std::endl;

    TopologicalSort ts2(6);
    ts2.addEdge(5, 2); ts2.addEdge(5, 0); ts2.addEdge(4, 0);
    ts2.addEdge(4, 1); ts2.addEdge(2, 3); ts2.addEdge(3, 1);

    auto order2 = ts2.dfsSort();
    std::cout << "拓扑排序(DFS): ";
    for (int v : order2) std::cout << v << " ";
    std::cout << std::endl;

    return 0;
}
```

1.2 强连通分量（Tarjan算法）
-------------------------------

强连通分量（SCC）：有向图中，若任意两个顶点u和v之间互相可达，则它们属于同一个强连通分量。

Tarjan算法利用DFS和栈，在一次遍历中找到所有SCC。

核心概念：
- dfn[u]：节点u被DFS访问的时间戳
- low[u]：节点u及其子树能回溯到的最早时间戳
- 当dfn[u] == low[u]时，u是某个SCC的根

```cpp
#include <iostream>
#include <vector>
#include <stack>
#include <algorithm>

class TarjanSCC {
private:
    int V;
    std::vector<std::vector<int>> adj;
    std::vector<int> dfn, low, sccId;
    std::vector<bool> onStack;
    std::stack<int> stk;
    int timer = 0;
    int sccCount = 0;

    void dfs(int u) {
        dfn[u] = low[u] = ++timer;
        stk.push(u);
        onStack[u] = true;

        for (int v : adj[u]) {
            if (dfn[v] == 0) {
                dfs(v);
                low[u] = std::min(low[u], low[v]);
            } else if (onStack[v]) {
                low[u] = std::min(low[u], dfn[v]);
            }
        }

        if (dfn[u] == low[u]) {
            sccCount++;
            while (true) {
                int v = stk.top(); stk.pop();
                onStack[v] = false;
                sccId[v] = sccCount;
                if (v == u) break;
            }
        }
    }

public:
    TarjanSCC(int v) : V(v), adj(v), dfn(v, 0), low(v, 0), sccId(v, 0), onStack(v, false) {}

    void addEdge(int u, int v) { adj[u].push_back(v); }

    int solve() {
        for (int i = 0; i < V; ++i)
            if (dfn[i] == 0)
                dfs(i);
        return sccCount;
    }

    int getSCCId(int u) const { return sccId[u]; }
    int getSCCCount() const { return sccCount; }

    std::vector<std::vector<int>> getComponents() {
        std::vector<std::vector<int>> components(sccCount);
        for (int i = 0; i < V; ++i)
            components[sccId[i] - 1].push_back(i);
        return components;
    }
};

int main() {
    TarjanSCC tarjan(8);
    tarjan.addEdge(0, 1);
    tarjan.addEdge(1, 2);
    tarjan.addEdge(2, 0);
    tarjan.addEdge(2, 3);
    tarjan.addEdge(3, 4);
    tarjan.addEdge(4, 5);
    tarjan.addEdge(5, 3);
    tarjan.addEdge(6, 5);
    tarjan.addEdge(6, 7);
    tarjan.addEdge(7, 6);

    int count = tarjan.solve();
    std::cout << "强连通分量数: " << count << std::endl;

    auto components = tarjan.getComponents();
    for (int i = 0; i < count; ++i) {
        std::cout << "SCC " << i + 1 << ": ";
        for (int v : components[i]) std::cout << v << " ";
        std::cout << std::endl;
    }

    return 0;
}
```

1.3 Floyd-Warshall（全源最短路径）
-------------------------------------

Floyd-Warshall算法计算图中所有顶点对之间的最短路径。

核心思想：动态规划，dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])

时间复杂度：O(V³)
空间复杂度：O(V²)
适用：稠密图、顶点数不大（V ≤ 500）、可处理负权边（但不含负权环）

```cpp
#include <iostream>
#include <vector>
#include <climits>
#include <iomanip>

class FloydWarshall {
private:
    int V;
    std::vector<std::vector<long long>> dist;
    std::vector<std::vector<int>> next;
    static constexpr long long INF = 1e18;

public:
    FloydWarshall(int v) : V(v), dist(v, std::vector<long long>(v, INF)),
                           next(v, std::vector<int>(v, -1)) {
        for (int i = 0; i < V; ++i) {
            dist[i][i] = 0;
            next[i][i] = i;
        }
    }

    void addEdge(int u, int v, long long w) {
        dist[u][v] = w;
        next[u][v] = v;
    }

    bool solve() {
        for (int k = 0; k < V; ++k) {
            for (int i = 0; i < V; ++i) {
                for (int j = 0; j < V; ++j) {
                    if (dist[i][k] != INF && dist[k][j] != INF &&
                        dist[i][k] + dist[k][j] < dist[i][j]) {
                        dist[i][j] = dist[i][k] + dist[k][j];
                        next[i][j] = next[i][k];
                    }
                }
            }
        }
        for (int i = 0; i < V; ++i)
            if (dist[i][i] < 0) return false;
        return true;
    }

    long long getDistance(int u, int v) const { return dist[u][v]; }

    std::vector<int> getPath(int u, int v) const {
        if (next[u][v] == -1) return {};
        std::vector<int> path = {u};
        while (u != v) {
            u = next[u][v];
            path.push_back(u);
        }
        return path;
    }

    void printDistMatrix() const {
        std::cout << "距离矩阵:" << std::endl;
        for (int i = 0; i < V; ++i) {
            for (int j = 0; j < V; ++j) {
                if (dist[i][j] == INF) std::cout << std::setw(5) << "INF";
                else std::cout << std::setw(5) << dist[i][j];
            }
            std::cout << std::endl;
        }
    }
};

int main() {
    FloydWarshall fw(4);
    fw.addEdge(0, 1, 3);
    fw.addEdge(0, 3, 7);
    fw.addEdge(1, 0, 8);
    fw.addEdge(1, 2, 2);
    fw.addEdge(2, 0, 5);
    fw.addEdge(2, 3, 1);
    fw.addEdge(3, 0, 2);

    if (fw.solve()) {
        fw.printDistMatrix();

        std::cout << "\n0到3的最短路径: ";
        auto path = fw.getPath(0, 3);
        for (int v : path) std::cout << v << " ";
        std::cout << "\n距离: " << fw.getDistance(0, 3) << std::endl;
    } else {
        std::cout << "存在负权环!" << std::endl;
    }

    return 0;
}
```

1.4 Bellman-Ford（含负权边的单源最短路径）
--------------------------------------------

Bellman-Ford算法可处理含负权边的图，并能检测负权环。

核心思想：对所有边进行V-1轮松弛操作。

时间复杂度：O(VE)
适用：含负权边的图、判断负权环

```cpp
#include <iostream>
#include <vector>
#include <climits>

class BellmanFord {
private:
    struct Edge {
        int from, to;
        long long weight;
    };

    int V;
    std::vector<Edge> edges;
    std::vector<long long> dist;
    std::vector<int> parent;
    static constexpr long long INF = 1e18;

public:
    BellmanFord(int v) : V(v), dist(v, INF), parent(v, -1) {}

    void addEdge(int u, int v, long long w) {
        edges.push_back({u, v, w});
    }

    bool solve(int src) {
        dist[src] = 0;

        for (int i = 0; i < V - 1; ++i) {
            bool updated = false;
            for (const auto& e : edges) {
                if (dist[e.from] != INF && dist[e.from] + e.weight < dist[e.to]) {
                    dist[e.to] = dist[e.from] + e.weight;
                    parent[e.to] = e.from;
                    updated = true;
                }
            }
            if (!updated) break;
        }

        for (const auto& e : edges) {
            if (dist[e.from] != INF && dist[e.from] + e.weight < dist[e.to])
                return false;
        }
        return true;
    }

    long long getDistance(int v) const { return dist[v]; }

    std::vector<int> getPath(int v) const {
        std::vector<int> path;
        for (int curr = v; curr != -1; curr = parent[curr])
            path.push_back(curr);
        std::reverse(path.begin(), path.end());
        return path;
    }
};

int main() {
    BellmanFord bf(5);
    bf.addEdge(0, 1, 6);
    bf.addEdge(0, 3, 7);
    bf.addEdge(1, 2, 5);
    bf.addEdge(1, 3, 8);
    bf.addEdge(1, 4, -4);
    bf.addEdge(2, 1, -2);
    bf.addEdge(3, 2, -3);
    bf.addEdge(3, 4, 9);
    bf.addEdge(4, 0, 2);
    bf.addEdge(4, 2, 7);

    if (bf.solve(0)) {
        for (int i = 0; i < 5; ++i) {
            std::cout << "0到" << i << "的最短距离: " << bf.getDistance(i);
            auto path = bf.getPath(i);
            std::cout << " 路径: ";
            for (int v : path) std::cout << v << " ";
            std::cout << std::endl;
        }
    } else {
        std::cout << "图中存在负权环!" << std::endl;
    }

    return 0;
}
```

1.5 SPFA算法（Bellman-Ford的队列优化）

```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <climits>

class SPFA {
private:
    int V;
    std::vector<std::vector<std::pair<int, long long>>> adj;
    std::vector<long long> dist;
    std::vector<int> cnt;
    std::vector<bool> inQueue;
    static constexpr long long INF = 1e18;

public:
    SPFA(int v) : V(v), adj(v), dist(v, INF), cnt(v, 0), inQueue(v, false) {}

    void addEdge(int u, int v, long long w) {
        adj[u].emplace_back(v, w);
    }

    bool solve(int src) {
        dist[src] = 0;
        std::queue<int> q;
        q.push(src);
        inQueue[src] = true;

        while (!q.empty()) {
            int u = q.front(); q.pop();
            inQueue[u] = false;

            for (auto [v, w] : adj[u]) {
                if (dist[u] + w < dist[v]) {
                    dist[v] = dist[u] + w;
                    if (!inQueue[v]) {
                        q.push(v);
                        inQueue[v] = true;
                        if (++cnt[v] >= V) return false;
                    }
                }
            }
        }
        return true;
    }

    long long getDistance(int v) const { return dist[v]; }
};

int main() {
    SPFA spfa(5);
    spfa.addEdge(0, 1, 6);
    spfa.addEdge(0, 3, 7);
    spfa.addEdge(1, 2, 5);
    spfa.addEdge(1, 4, -4);
    spfa.addEdge(2, 1, -2);
    spfa.addEdge(3, 2, -3);
    spfa.addEdge(3, 4, 9);

    if (spfa.solve(0)) {
        for (int i = 0; i < 5; ++i)
            std::cout << "0到" << i << ": " << spfa.getDistance(i) << std::endl;
    }
    return 0;
}
```

## ==========================================================================
### 📖 第二节: 所有用法大全
## ==========================================================================

2.1 缩点（SCC + DAG上DP）

```cpp
#include <iostream>
#include <vector>
#include <stack>
#include <queue>
#include <algorithm>

class SCCContraction {
private:
    int V;
    std::vector<std::vector<int>> adj;
    std::vector<int> dfn, low, sccId;
    std::vector<bool> onStack;
    std::stack<int> stk;
    int timer = 0, sccCount = 0;

    void tarjan(int u) {
        dfn[u] = low[u] = ++timer;
        stk.push(u); onStack[u] = true;
        for (int v : adj[u]) {
            if (!dfn[v]) { tarjan(v); low[u] = std::min(low[u], low[v]); }
            else if (onStack[v]) low[u] = std::min(low[u], dfn[v]);
        }
        if (dfn[u] == low[u]) {
            sccCount++;
            while (true) {
                int v = stk.top(); stk.pop();
                onStack[v] = false; sccId[v] = sccCount - 1;
                if (v == u) break;
            }
        }
    }

public:
    SCCContraction(int v) : V(v), adj(v), dfn(v, 0), low(v, 0), sccId(v, 0), onStack(v, false) {}

    void addEdge(int u, int v) { adj[u].push_back(v); }

    long long solve(const std::vector<int>& weights) {
        for (int i = 0; i < V; ++i)
            if (!dfn[i]) tarjan(i);

        std::vector<long long> sccWeight(sccCount, 0);
        for (int i = 0; i < V; ++i)
            sccWeight[sccId[i]] += weights[i];

        std::vector<std::vector<int>> dag(sccCount);
        std::vector<int> inDegree(sccCount, 0);
        for (int u = 0; u < V; ++u)
            for (int v : adj[u])
                if (sccId[u] != sccId[v]) {
                    dag[sccId[u]].push_back(sccId[v]);
                    inDegree[sccId[v]]++;
                }

        std::vector<long long> dp(sccCount, 0);
        std::queue<int> q;
        for (int i = 0; i < sccCount; ++i) {
            dp[i] = sccWeight[i];
            if (inDegree[i] == 0) q.push(i);
        }

        while (!q.empty()) {
            int u = q.front(); q.pop();
            for (int v : dag[u]) {
                dp[v] = std::max(dp[v], dp[u] + sccWeight[v]);
                if (--inDegree[v] == 0) q.push(v);
            }
        }

        return *std::max_element(dp.begin(), dp.end());
    }
};

int main() {
    SCCContraction sc(6);
    sc.addEdge(0, 1); sc.addEdge(1, 2); sc.addEdge(2, 0);
    sc.addEdge(2, 3); sc.addEdge(3, 4); sc.addEdge(4, 5); sc.addEdge(5, 3);

    std::vector<int> weights = {1, 2, 3, 4, 5, 6};
    std::cout << "缩点后DAG上最长路径权重和: " << sc.solve(weights) << std::endl;
    return 0;
}
```

2.2 网络流（Dinic算法/最大流）

```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <algorithm>
#include <climits>

class Dinic {
private:
    struct Edge {
        int to, rev;
        long long cap;
    };

    int V;
    std::vector<std::vector<Edge>> graph;
    std::vector<int> level, iter;

    bool bfs(int s, int t) {
        level.assign(V, -1);
        std::queue<int> q;
        level[s] = 0;
        q.push(s);
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
        for (int& i = iter[u]; i < (int)graph[u].size(); ++i) {
            Edge& e = graph[u][i];
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
    Dinic(int v) : V(v), graph(v), level(v), iter(v) {}

    void addEdge(int from, int to, long long cap) {
        graph[from].push_back({to, (int)graph[to].size(), cap});
        graph[to].push_back({from, (int)graph[from].size() - 1, 0});
    }

    long long maxFlow(int s, int t) {
        long long flow = 0;
        while (bfs(s, t)) {
            iter.assign(V, 0);
            long long d;
            while ((d = dfs(s, t, LLONG_MAX)) > 0)
                flow += d;
        }
        return flow;
    }
};

int main() {
    Dinic dinic(6);
    dinic.addEdge(0, 1, 16);
    dinic.addEdge(0, 2, 13);
    dinic.addEdge(1, 2, 10);
    dinic.addEdge(1, 3, 12);
    dinic.addEdge(2, 1, 4);
    dinic.addEdge(2, 4, 14);
    dinic.addEdge(3, 2, 9);
    dinic.addEdge(3, 5, 20);
    dinic.addEdge(4, 3, 7);
    dinic.addEdge(4, 5, 4);

    std::cout << "最大流: " << dinic.maxFlow(0, 5) << std::endl;
    return 0;
}
```

2.3 最小费用最大流

```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <climits>

class MCMF {
private:
    struct Edge {
        int to, rev;
        long long cap, cost;
    };

    int V;
    std::vector<std::vector<Edge>> graph;
    std::vector<long long> dist;
    std::vector<int> prevv, preve;
    std::vector<bool> inQueue;

    bool spfa(int s, int t) {
        dist.assign(V, LLONG_MAX);
        inQueue.assign(V, false);
        dist[s] = 0;
        std::queue<int> q;
        q.push(s); inQueue[s] = true;

        while (!q.empty()) {
            int u = q.front(); q.pop(); inQueue[u] = false;
            for (int i = 0; i < (int)graph[u].size(); ++i) {
                auto& e = graph[u][i];
                if (e.cap > 0 && dist[u] + e.cost < dist[e.to]) {
                    dist[e.to] = dist[u] + e.cost;
                    prevv[e.to] = u;
                    preve[e.to] = i;
                    if (!inQueue[e.to]) { q.push(e.to); inQueue[e.to] = true; }
                }
            }
        }
        return dist[t] != LLONG_MAX;
    }

public:
    MCMF(int v) : V(v), graph(v), prevv(v), preve(v) {}

    void addEdge(int from, int to, long long cap, long long cost) {
        graph[from].push_back({to, (int)graph[to].size(), cap, cost});
        graph[to].push_back({from, (int)graph[from].size() - 1, 0, -cost});
    }

    std::pair<long long, long long> solve(int s, int t) {
        long long totalFlow = 0, totalCost = 0;
        while (spfa(s, t)) {
            long long d = LLONG_MAX;
            for (int v = t; v != s; v = prevv[v])
                d = std::min(d, graph[prevv[v]][preve[v]].cap);
            for (int v = t; v != s; v = prevv[v]) {
                graph[prevv[v]][preve[v]].cap -= d;
                graph[graph[prevv[v]][preve[v]].to][graph[prevv[v]][preve[v]].rev].cap += d;
            }
            totalFlow += d;
            totalCost += d * dist[t];
        }
        return {totalFlow, totalCost};
    }
};

int main() {
    MCMF mcmf(4);
    mcmf.addEdge(0, 1, 2, 1);
    mcmf.addEdge(0, 2, 1, 2);
    mcmf.addEdge(1, 2, 1, 1);
    mcmf.addEdge(1, 3, 1, 3);
    mcmf.addEdge(2, 3, 2, 1);

    auto [flow, cost] = mcmf.solve(0, 3);
    std::cout << "最大流: " << flow << std::endl;
    std::cout << "最小费用: " << cost << std::endl;
    return 0;
}
```

2.4 割点和桥（无向图）

```cpp
#include <iostream>
#include <vector>
#include <algorithm>

class CutVerticesAndBridges {
private:
    int V;
    std::vector<std::vector<int>> adj;
    std::vector<int> dfn, low;
    std::vector<bool> isCut;
    std::vector<std::pair<int,int>> bridges;
    int timer = 0;

    void dfs(int u, int parent) {
        dfn[u] = low[u] = ++timer;
        int childCount = 0;

        for (int v : adj[u]) {
            if (v == parent) continue;
            if (!dfn[v]) {
                childCount++;
                dfs(v, u);
                low[u] = std::min(low[u], low[v]);
                if (parent == -1 && childCount > 1) isCut[u] = true;
                if (parent != -1 && low[v] >= dfn[u]) isCut[u] = true;
                if (low[v] > dfn[u]) bridges.emplace_back(u, v);
            } else {
                low[u] = std::min(low[u], dfn[v]);
            }
        }
    }

public:
    CutVerticesAndBridges(int v) : V(v), adj(v), dfn(v, 0), low(v, 0), isCut(v, false) {}

    void addEdge(int u, int v) { adj[u].push_back(v); adj[v].push_back(u); }

    void solve() {
        for (int i = 0; i < V; ++i)
            if (!dfn[i]) dfs(i, -1);
    }

    std::vector<int> getCutVertices() {
        std::vector<int> cuts;
        for (int i = 0; i < V; ++i)
            if (isCut[i]) cuts.push_back(i);
        return cuts;
    }

    std::vector<std::pair<int,int>> getBridges() { return bridges; }
};

int main() {
    CutVerticesAndBridges cvb(7);
    cvb.addEdge(0, 1); cvb.addEdge(1, 2); cvb.addEdge(2, 0);
    cvb.addEdge(2, 3); cvb.addEdge(3, 4); cvb.addEdge(4, 5); cvb.addEdge(5, 3);
    cvb.addEdge(3, 6);

    cvb.solve();

    auto cuts = cvb.getCutVertices();
    std::cout << "割点: ";
    for (int v : cuts) std::cout << v << " ";
    std::cout << std::endl;

    auto bridges = cvb.getBridges();
    std::cout << "桥: ";
    for (auto [u, v] : bridges) std::cout << "(" << u << "," << v << ") ";
    std::cout << std::endl;

    return 0;
}
```

## ==========================================================================
### 📖 第三节: 实用案例
## ==========================================================================

3.1 案例一：课程安排系统（拓扑排序）

```cpp
#include <iostream>
#include <vector>
#include <string>
#include <queue>
#include <unordered_map>

class CourseScheduler {
private:
    std::unordered_map<std::string, int> courseId;
    std::vector<std::string> courseName;
    std::vector<std::vector<int>> adj;
    std::vector<int> credits;
    int n = 0;

    int getId(const std::string& name) {
        if (courseId.find(name) == courseId.end()) {
            courseId[name] = n++;
            courseName.push_back(name);
            adj.push_back({});
            credits.push_back(0);
        }
        return courseId[name];
    }

public:
    void addCourse(const std::string& name, int credit, const std::vector<std::string>& prereqs) {
        int id = getId(name);
        credits[id] = credit;
        for (const auto& prereq : prereqs) {
            int pid = getId(prereq);
            adj[pid].push_back(id);
        }
    }

    std::vector<std::vector<std::string>> schedule() {
        std::vector<int> inDeg(n, 0);
        for (int u = 0; u < n; ++u)
            for (int v : adj[u]) inDeg[v]++;

        std::vector<std::vector<std::string>> semesters;
        std::vector<bool> taken(n, false);

        while (true) {
            std::vector<int> available;
            for (int i = 0; i < n; ++i)
                if (!taken[i] && inDeg[i] == 0)
                    available.push_back(i);
            if (available.empty()) break;

            std::vector<std::string> semester;
            for (int id : available) {
                taken[id] = true;
                semester.push_back(courseName[id]);
                for (int v : adj[id]) inDeg[v]--;
            }
            semesters.push_back(semester);
        }
        return semesters;
    }
};

int main() {
    CourseScheduler cs;
    cs.addCourse("高等数学", 5, {});
    cs.addCourse("线性代数", 3, {});
    cs.addCourse("C语言", 4, {});
    cs.addCourse("数据结构", 4, {"C语言"});
    cs.addCourse("概率论", 3, {"高等数学"});
    cs.addCourse("离散数学", 3, {"高等数学", "线性代数"});
    cs.addCourse("算法设计", 3, {"数据结构", "离散数学"});
    cs.addCourse("操作系统", 4, {"数据结构"});
    cs.addCourse("计算机网络", 3, {"数据结构"});
    cs.addCourse("编译原理", 3, {"数据结构", "离散数学"});

    auto plan = cs.schedule();
    for (int i = 0; i < (int)plan.size(); ++i) {
        std::cout << "第" << i + 1 << "学期: ";
        for (const auto& c : plan[i]) std::cout << c << " ";
        std::cout << std::endl;
    }
    return 0;
}
```

3.2 案例二：社交网络影响力分析（SCC）

```cpp
#include <iostream>
#include <vector>
#include <stack>
#include <algorithm>
#include <string>

class SocialInfluence {
private:
    int V;
    std::vector<std::vector<int>> adj;
    std::vector<std::string> names;
    std::vector<int> dfn, low, sccId;
    std::vector<bool> onStack;
    std::stack<int> stk;
    int timer = 0, sccCount = 0;

    void tarjan(int u) {
        dfn[u] = low[u] = ++timer;
        stk.push(u); onStack[u] = true;
        for (int v : adj[u]) {
            if (!dfn[v]) { tarjan(v); low[u] = std::min(low[u], low[v]); }
            else if (onStack[v]) low[u] = std::min(low[u], dfn[v]);
        }
        if (dfn[u] == low[u]) {
            sccCount++;
            while (true) {
                int v = stk.top(); stk.pop();
                onStack[v] = false; sccId[v] = sccCount - 1;
                if (v == u) break;
            }
        }
    }

public:
    SocialInfluence(const std::vector<std::string>& n)
        : V(n.size()), adj(n.size()), names(n), dfn(n.size(), 0),
          low(n.size(), 0), sccId(n.size(), 0), onStack(n.size(), false) {}

    void addFollow(int u, int v) { adj[u].push_back(v); }

    void analyze() {
        for (int i = 0; i < V; ++i)
            if (!dfn[i]) tarjan(i);

        std::vector<std::vector<int>> groups(sccCount);
        for (int i = 0; i < V; ++i) groups[sccId[i]].push_back(i);

        std::cout << "互相关注的社交圈:" << std::endl;
        for (int i = 0; i < sccCount; ++i) {
            if (groups[i].size() > 1) {
                std::cout << "  圈子" << i + 1 << ": ";
                for (int v : groups[i]) std::cout << names[v] << " ";
                std::cout << "(规模=" << groups[i].size() << ")" << std::endl;
            }
        }

        std::vector<int> outDeg(sccCount, 0);
        for (int u = 0; u < V; ++u)
            for (int v : adj[u])
                if (sccId[u] != sccId[v]) outDeg[sccId[u]]++;

        std::cout << "核心影响力圈(出度最大的SCC):" << std::endl;
        int maxOut = *std::max_element(outDeg.begin(), outDeg.end());
        for (int i = 0; i < sccCount; ++i) {
            if (outDeg[i] == maxOut && groups[i].size() > 1) {
                std::cout << "  ";
                for (int v : groups[i]) std::cout << names[v] << " ";
                std::cout << std::endl;
            }
        }
    }
};

int main() {
    std::vector<std::string> users = {"Alice", "Bob", "Charlie", "David", "Eve", "Frank"};
    SocialInfluence si(users);
    si.addFollow(0, 1); si.addFollow(1, 2); si.addFollow(2, 0);
    si.addFollow(2, 3); si.addFollow(3, 4); si.addFollow(4, 3);
    si.addFollow(4, 5);

    si.analyze();
    return 0;
}
```

3.3 案例三：物流配送网络优化（网络流）

```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <string>
#include <climits>
#include <algorithm>

class LogisticsNetwork {
private:
    struct Edge {
        int to, rev;
        int cap, cost;
    };

    int V;
    std::vector<std::vector<Edge>> graph;
    std::vector<std::string> nodeNames;

    void addEdgeInternal(int from, int to, int cap, int cost) {
        graph[from].push_back({to, (int)graph[to].size(), cap, cost});
        graph[to].push_back({from, (int)graph[from].size() - 1, 0, -cost});
    }

public:
    LogisticsNetwork(const std::vector<std::string>& names)
        : V(names.size()), graph(names.size()), nodeNames(names) {}

    void addRoute(int from, int to, int capacity, int unitCost) {
        addEdgeInternal(from, to, capacity, unitCost);
    }

    void optimize(int source, int sink) {
        long long totalFlow = 0, totalCost = 0;

        while (true) {
            std::vector<long long> dist(V, LLONG_MAX);
            std::vector<int> prevv(V, -1), preve(V, -1);
            std::vector<bool> inq(V, false);
            dist[source] = 0;
            std::queue<int> q;
            q.push(source); inq[source] = true;

            while (!q.empty()) {
                int u = q.front(); q.pop(); inq[u] = false;
                for (int i = 0; i < (int)graph[u].size(); ++i) {
                    auto& e = graph[u][i];
                    if (e.cap > 0 && dist[u] + e.cost < dist[e.to]) {
                        dist[e.to] = dist[u] + e.cost;
                        prevv[e.to] = u; preve[e.to] = i;
                        if (!inq[e.to]) { q.push(e.to); inq[e.to] = true; }
                    }
                }
            }

            if (dist[sink] == LLONG_MAX) break;

            int d = INT_MAX;
            for (int v = sink; v != source; v = prevv[v])
                d = std::min(d, graph[prevv[v]][preve[v]].cap);
            for (int v = sink; v != source; v = prevv[v]) {
                graph[prevv[v]][preve[v]].cap -= d;
                graph[graph[prevv[v]][preve[v]].to][graph[prevv[v]][preve[v]].rev].cap += d;
            }
            totalFlow += d;
            totalCost += (long long)d * dist[sink];
        }

        std::cout << "=== 物流配送优化结果 ===" << std::endl;
        std::cout << "最大配送量: " << totalFlow << "单位" << std::endl;
        std::cout << "最小总运输成本: " << totalCost << std::endl;
    }
};

int main() {
    std::vector<std::string> nodes = {"仓库", "分拣A", "分拣B", "配送站1", "配送站2", "客户"};
    LogisticsNetwork ln(nodes);

    ln.addRoute(0, 1, 10, 2);
    ln.addRoute(0, 2, 8, 3);
    ln.addRoute(1, 3, 6, 4);
    ln.addRoute(1, 4, 5, 2);
    ln.addRoute(2, 3, 4, 1);
    ln.addRoute(2, 4, 7, 3);
    ln.addRoute(3, 5, 9, 2);
    ln.addRoute(4, 5, 8, 3);

    ln.optimize(0, 5);
    return 0;
}
```

## ==========================================================================
### 📖 第四节: 课后习题
## ==========================================================================

1. 基础题：实现拓扑排序的两种方法（BFS的Kahn算法和DFS方法），并判断图中是否有环。

2. 应用题：使用Tarjan算法求有向图的所有强连通分量，并输出缩点后的DAG。

3. 进阶题：实现Bellman-Ford算法，支持：
   - 检测负权环
   - 输出从源点到各点的最短路径
   - 与Dijkstra进行性能对比

4. 综合题：实现Dinic最大流算法，并用于解决二分图最大匹配问题。

5. 洛谷练习：
   - [P1113 杂务](https://www.luogu.com.cn/problem/P1113)（拓扑排序）
   - [P4779 单源最短路径](https://www.luogu.com.cn/problem/P4779)（最短路）
   - [P3387 缩点](https://www.luogu.com.cn/problem/P3387)（Tarjan+DAG上DP）

## ==========================================================================


## --------------------------------------------------------------------------
## 🔗 知识网络
## --------------------------------------------------------------------------

- **上一章**: [[数据结构/O_B树_BTree]] | **返回**: [[目录]]
- **相关**: [[数据结构/H_图_Graph]] | [[算法技巧/动态规划]] | [[图论/网络流]]

## ==========================================================================
## 章节测试
## ==========================================================================

### 判断题

> [!question] 判断题 1
> 拓扑排序只能用于有向无环图（DAG）。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: 如果有向图中存在环，则不存在拓扑序（环中的节点互相依赖，无法确定先后顺序）。

> [!question] 判断题 2
> 一个DAG的拓扑排序结果是唯一的。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: 当多个节点的入度同时为0时，选择哪个先输出会导致不同的拓扑序。只有当图是一条链时拓扑序才唯一。

> [!question] 判断题 3
> Tarjan算法的时间复杂度为O(V+E)。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: Tarjan算法基于DFS，每个节点和每条边只访问一次，时间复杂度O(V+E)。

> [!question] 判断题 4
> Floyd-Warshall算法不能处理含负权边的图。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: Floyd-Warshall可以处理负权边，但不能处理负权环。如果存在负权环，算法会检测到（对角线出现负值）。

> [!question] 判断题 5
> Bellman-Ford算法可以检测图中是否存在负权环。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: V-1轮松弛后，如果第V轮仍能松弛某条边，说明存在负权环。

> [!question] 判断题 6
> Dinic算法的时间复杂度为O(V²E)。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: Dinic算法通过分层图和阻塞流的概念，时间复杂度为O(V²E)。对于单位容量图可以优化到O(E√V)。

> [!question] 判断题 7
> 最大流最小割定理指出：网络的最大流等于最小割的容量。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: 这是网络流理论的核心定理（Ford-Fulkerson定理），最大流=最小割在所有网络流算法中都成立。

> [!question] 判断题 8
> SPFA算法在最坏情况下的时间复杂度为O(VE)，与Bellman-Ford相同。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: SPFA是Bellman-Ford的队列优化版本，平均情况下更快，但最坏情况下仍为O(VE)。在某些构造数据下SPFA会退化。

> [!question] 判断题 9
> 强连通分量内的任意两个顶点之间都存在路径。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: 强连通分量的定义就是：分量内任意两个顶点u和v，既存在u到v的路径，也存在v到u的路径。

> [!question] 判断题 10
> 缩点后的图一定是DAG。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: 将每个SCC缩为一个点后，如果缩点图有环，那么环上的所有SCC应该合并为一个更大的SCC，矛盾。所以缩点图一定是DAG。

### 选择题

> [!question] 选择题 1
> 以下哪个算法不能用于求最短路径？
> - [ ] A. Dijkstra
> - [ ] B. Floyd-Warshall
> - [ ] C. Bellman-Ford
> - [ ] D. Tarjan
>
> > [!success]- 点击查看答案
> > 正确答案: D
> > 
> > **解析**: Tarjan算法用于求强连通分量和割点/桥，不是最短路径算法。其他三个都是经典的最短路径算法。

> [!question] 选择题 2
> Floyd-Warshall算法的时间复杂度为？
> - [ ] A. O(V²)
> - [ ] B. O(V³)
> - [ ] C. O(VE)
> - [ ] D. O(V² log V)
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: Floyd-Warshall有三重循环（k, i, j各遍历所有顶点），时间复杂度为O(V³)。

> [!question] 选择题 3
> Bellman-Ford相比Dijkstra的优势是？
> - [ ] A. 时间复杂度更低
> - [ ] B. 可以处理负权边
> - [ ] C. 空间复杂度更低
> - [ ] D. 代码更简洁
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: Dijkstra不能处理负权边（贪心策略在负权下失效），而Bellman-Ford通过多轮松弛可以正确处理负权边。

> [!question] 选择题 4
> 拓扑排序中，Kahn算法使用的数据结构是？
> - [ ] A. 栈
> - [ ] B. 队列
> - [ ] C. 堆
> - [ ] D. 哈希表
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: Kahn算法使用队列存储入度为0的节点，每次从队列取出一个节点加入结果。（使用优先队列可以得到字典序最小的拓扑序）

> [!question] 选择题 5
> 在Tarjan算法中，当dfn[u] == low[u]时，表示什么？
> - [ ] A. u是叶子节点
> - [ ] B. u是某个SCC的根
> - [ ] C. u没有出边
> - [ ] D. u的入度为0
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: dfn[u]==low[u]意味着u无法通过后代回到更早被访问的祖先，因此u是以它为根的子树所形成的SCC的"最高点"（根）。

> [!question] 选择题 6
> 网络流中，增广路是指？
> - [ ] A. 从源到汇的任意路径
> - [ ] B. 从源到汇且所有边都有剩余容量的路径
> - [ ] C. 容量最大的路径
> - [ ] D. 边数最少的路径
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: 增广路是在残量图中从源点s到汇点t的路径，路径上每条边的剩余容量>0。找到增广路后沿路径增加流量。

> [!question] 选择题 7
> 对于稠密图(E≈V²)求全源最短路径，以下哪种方案最优？
> - [ ] A. 对每个顶点运行Dijkstra
> - [ ] B. Floyd-Warshall
> - [ ] C. 对每个顶点运行Bellman-Ford
> - [ ] D. 对每个顶点运行BFS
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: Floyd O(V³)，V次Dijkstra为O(V×(V²))=O(V³)（邻接矩阵），但Floyd常数更小且代码更简单。V次Bellman-Ford为O(V²E)=O(V⁴)更差。

> [!question] 选择题 8
> SPFA算法判断负权环的条件是？
> - [ ] A. 某节点入队次数超过V次
> - [ ] B. 某节点的距离变为负数
> - [ ] C. 队列为空
> - [ ] D. 某节点入队次数超过E次
>
> > [!success]- 点击查看答案
> > 正确答案: A
> > 
> > **解析**: 如果某个节点入队次数≥V次，说明存在负权环（正常情况下每个节点最多被松弛V-1次）。

> [!question] 选择题 9
> 二分图最大匹配可以转化为什么问题求解？
> - [ ] A. 最短路径
> - [ ] B. 最大流
> - [ ] C. 最小生成树
> - [ ] D. 拓扑排序
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: 建立超级源和超级汇，源连接左部所有点（容量1），汇连接右部所有点（容量1），匹配边容量1。最大流即最大匹配数。

> [!question] 选择题 10
> Bellman-Ford算法需要进行多少轮松弛操作？
> - [ ] A. V轮
> - [ ] B. V-1轮
> - [ ] C. E轮
> - [ ] D. log V轮
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: 最短路径最多经过V-1条边，每轮松弛至少确定一个顶点的最短路，因此V-1轮后所有最短路确定。第V轮用于检测负权环。

### 编程大题

> [!question] 编程大题 1
> **题目**: 洛谷 [P1113 杂务](https://www.luogu.com.cn/problem/P1113)
> 
> 有n个杂务，每个杂务有完成时间和前置杂务依赖。求完成所有杂务所需的最短时间。
>
> > [!success]- 点击查看提示
> > 建图后进行拓扑排序。使用dp[i]表示完成杂务i的最早结束时间：dp[i] = max(dp[前驱]) + time[i]。答案为max(dp[i])。本质是DAG上的最长路径问题。

> [!question] 编程大题 2
> **题目**: 洛谷 [P3387 缩点](https://www.luogu.com.cn/problem/P3387)
> 
> 给定一个有向图，每个点有权值。求一条路径使得路径上的点权值之和最大（每个强连通分量内的点可以重复经过）。
>
> > [!success]- 点击查看提示
> > 1. 用Tarjan算法求所有SCC，将每个SCC内的权值求和。2. 缩点建DAG。3. 在DAG上求最长路径（拓扑排序+DP）。dp[u] = max(dp[前驱] + weight[u])。

> [!question] 编程大题 3
> **题目**: 洛谷 [P4779 单源最短路径](https://www.luogu.com.cn/problem/P4779)
> 
> 给定一个有向图和源点s，求s到所有点的最短路径。（本题数据保证无负权边，但请同时实现Dijkstra和Bellman-Ford两种解法进行对比）
>
> > [!success]- 点击查看提示
> > Dijkstra解法：使用优先队列优化，时间O((V+E)logV)。Bellman-Ford解法：V-1轮松弛所有边，时间O(VE)。对于本题规模（V≤10^5, E≤2×10^5），Dijkstra可过但Bellman-Ford可能TLE，体现两者的效率差异。
