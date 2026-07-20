

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

```c
#include <stdlib.h>

// 邻接表图结构（沿用 H_图的定义）
// 返回结果需要调用者 free
int* topological_sort(int V, int** adj, int* adj_sizes, int* result_size) {
    int* in_degree = calloc(V, sizeof(int));
    for (int u = 0; u < V; u++)
        for (int j = 0; j < adj_sizes[u]; j++)
            in_degree[adj[u][j]]++;

    int* queue = malloc(V * sizeof(int));
    int head = 0, tail = 0;
    for (int i = 0; i < V; i++)
        if (in_degree[i] == 0) queue[tail++] = i;

    int* result = malloc(V * sizeof(int));
    int ri = 0;
    while (head < tail) {
        int u = queue[head++];
        result[ri++] = u;
        for (int j = 0; j < adj_sizes[u]; j++) {
            int v = adj[u][j];
            if (--in_degree[v] == 0)
                queue[tail++] = v;
        }
    }
    free(in_degree);
    free(queue);

    if (ri < V) {  // 存在环
        free(result);
        *result_size = 0;
        return NULL;
    }
    *result_size = ri;
    return result;
}
```

### Tarjan SCC

```c
#include <stdlib.h>
#include <string.h>

typedef struct {
    int* dfn, *low, *scc_id;
    int* stack;
    int* on_stack;
    int timer, scc_count, stack_top;
    int V;
    int** adj;
    int* adj_sizes;
} TarjanSCC;

void tarjan_init(TarjanSCC* ts, int V) {
    ts->V = V;
    ts->dfn = calloc(V, sizeof(int));
    ts->low = calloc(V, sizeof(int));
    ts->scc_id = calloc(V, sizeof(int));
    ts->stack = malloc(V * sizeof(int));
    ts->on_stack = calloc(V, sizeof(int));
    ts->timer = 0;
    ts->scc_count = 0;
    ts->stack_top = 0;
}

void tarjan_destroy(TarjanSCC* ts) {
    free(ts->dfn); free(ts->low); free(ts->scc_id);
    free(ts->stack); free(ts->on_stack);
}

static void tarjan_dfs(TarjanSCC* ts, int u) {
    ts->dfn[u] = ts->low[u] = ++ts->timer;
    ts->stack[ts->stack_top++] = u;
    ts->on_stack[u] = 1;

    for (int j = 0; j < ts->adj_sizes[u]; j++) {
        int v = ts->adj[u][j];
        if (!ts->dfn[v]) {
            tarjan_dfs(ts, v);
            if (ts->low[v] < ts->low[u]) ts->low[u] = ts->low[v];
        } else if (ts->on_stack[v]) {
            if (ts->dfn[v] < ts->low[u]) ts->low[u] = ts->dfn[v];
        }
    }

    if (ts->dfn[u] == ts->low[u]) {
        ts->scc_count++;
        while (1) {
            int v = ts->stack[--ts->stack_top];
            ts->on_stack[v] = 0;
            ts->scc_id[v] = ts->scc_count;
            if (v == u) break;
        }
    }
}

int tarjan_solve(TarjanSCC* ts) {
    for (int i = 0; i < ts->V; i++)
        if (!ts->dfn[i]) tarjan_dfs(ts, i);
    return ts->scc_count;
}
```

### Floyd-Warshall

```c
#include <limits.h>
#include <stdlib.h>

typedef struct {
    long long** dist;
    int V;
} FloydWarshall;

void floyd_init(FloydWarshall* fw, int V) {
    fw->V = V;
    fw->dist = malloc(V * sizeof(long long*));
    for (int i = 0; i < V; i++) {
        fw->dist[i] = malloc(V * sizeof(long long));
        for (int j = 0; j < V; j++)
            fw->dist[i][j] = (i == j) ? 0 : LLONG_MAX / 2;
    }
}

void floyd_destroy(FloydWarshall* fw) {
    for (int i = 0; i < fw->V; i++) free(fw->dist[i]);
    free(fw->dist);
}

void floyd_add_edge(FloydWarshall* fw, int u, int v, int w) {
    fw->dist[u][v] = w;
}

// 返回 1 成功，0 表示存在负环
int floyd_solve(FloydWarshall* fw) {
    int V = fw->V;
    for (int k = 0; k < V; k++)
        for (int i = 0; i < V; i++)
            for (int j = 0; j < V; j++)
                if (fw->dist[i][k] < LLONG_MAX / 2 &&
                    fw->dist[k][j] < LLONG_MAX / 2 &&
                    fw->dist[i][k] + fw->dist[k][j] < fw->dist[i][j])
                    fw->dist[i][j] = fw->dist[i][k] + fw->dist[k][j];

    for (int i = 0; i < V; i++)
        if (fw->dist[i][i] < 0) return 0;
    return 1;
}

long long floyd_get_dist(FloydWarshall* fw, int u, int v) {
    return fw->dist[u][v];
}
```

### Bellman-Ford

```c
#include <limits.h>
#include <stdlib.h>

typedef struct { int from, to, weight; } Edge;

// 返回结果需要调用者 free，has_neg_cycle 为 1 表示存在负环
long long* bellman_ford(int V, const Edge* edges, int E, int start, int* has_neg_cycle) {
    long long* dist = malloc(V * sizeof(long long));
    for (int i = 0; i < V; i++) dist[i] = LLONG_MAX / 2;
    dist[start] = 0;

    for (int i = 0; i < V - 1; i++) {
        int updated = 0;
        for (int j = 0; j < E; j++) {
            if (dist[edges[j].from] < LLONG_MAX / 2 &&
                dist[edges[j].from] + edges[j].weight < dist[edges[j].to]) {
                dist[edges[j].to] = dist[edges[j].from] + edges[j].weight;
                updated = 1;
            }
        }
        if (!updated) break;
    }

    *has_neg_cycle = 0;
    for (int j = 0; j < E; j++) {
        if (dist[edges[j].from] < LLONG_MAX / 2 &&
            dist[edges[j].from] + edges[j].weight < dist[edges[j].to]) {
            *has_neg_cycle = 1;
            break;
        }
    }
    return dist;
}
```

### Dinic 最大流

```c
#include <limits.h>
#include <stdlib.h>
#include <string.h>

typedef struct { int to, rev; long long cap; } FlowEdge;

typedef struct {
    FlowEdge** graph;
    int* graph_sizes;
    int* graph_caps;
    int* level;
    int* iter;
    int V;
} Dinic;

void dinic_init(Dinic* dn, int V) {
    dn->V = V;
    dn->graph = calloc(V, sizeof(FlowEdge*));
    dn->graph_sizes = calloc(V, sizeof(int));
    dn->graph_caps = calloc(V, sizeof(int));
    dn->level = malloc(V * sizeof(int));
    dn->iter = malloc(V * sizeof(int));
}

void dinic_destroy(Dinic* dn) {
    for (int i = 0; i < dn->V; i++) free(dn->graph[i]);
    free(dn->graph); free(dn->graph_sizes); free(dn->graph_caps);
    free(dn->level); free(dn->iter);
}

static void dinic_add_edge_inner(Dinic* dn, int from, int to, long long cap) {
    if (dn->graph_sizes[from] >= dn->graph_caps[from]) {
        dn->graph_caps[from] = dn->graph_caps[from] ? dn->graph_caps[from] * 2 : 4;
        dn->graph[from] = realloc(dn->graph[from],
                                   dn->graph_caps[from] * sizeof(FlowEdge));
    }
    dn->graph[from][dn->graph_sizes[from]++] = (FlowEdge){to, 0, cap};
}

void dinic_add_edge(Dinic* dn, int from, int to, long long cap) {
    dinic_add_edge_inner(dn, from, to, cap);
    dinic_add_edge_inner(dn, to, from, 0);
    int from_idx = dn->graph_sizes[from] - 1;
    int to_idx = dn->graph_sizes[to] - 1;
    dn->graph[from][from_idx].rev = to_idx;
    dn->graph[to][to_idx].rev = from_idx;
}

static int dinic_bfs(Dinic* dn, int s, int t) {
    for (int i = 0; i < dn->V; i++) dn->level[i] = -1;
    int* q = malloc(dn->V * sizeof(int));
    int head = 0, tail = 0;
    dn->level[s] = 0; q[tail++] = s;
    while (head < tail) {
        int u = q[head++];
        for (int i = 0; i < dn->graph_sizes[u]; i++) {
            FlowEdge* e = &dn->graph[u][i];
            if (e->cap > 0 && dn->level[e->to] < 0) {
                dn->level[e->to] = dn->level[u] + 1;
                q[tail++] = e->to;
            }
        }
    }
    free(q);
    return dn->level[t] >= 0;
}

static long long dinic_dfs(Dinic* dn, int u, int t, long long f) {
    if (u == t) return f;
    for (int* i = &dn->iter[u]; *i < dn->graph_sizes[u]; (*i)++) {
        FlowEdge* e = &dn->graph[u][*i];
        if (e->cap > 0 && dn->level[e->to] == dn->level[u] + 1) {
            long long d = dinic_dfs(dn, e->to, t, f < e->cap ? f : e->cap);
            if (d > 0) {
                e->cap -= d;
                dn->graph[e->to][e->rev].cap += d;
                return d;
            }
        }
    }
    return 0;
}

long long dinic_max_flow(Dinic* dn, int s, int t) {
    long long flow = 0;
    while (dinic_bfs(dn, s, t)) {
        for (int i = 0; i < dn->V; i++) dn->iter[i] = 0;
        long long f;
        while ((f = dinic_dfs(dn, s, t, LLONG_MAX)) > 0)
            flow += f;
    }
    return flow;
}
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

> 力扣 (LeetCode) 有对应题型，竞赛方向推荐力扣/Codeforces。
