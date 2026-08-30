

建议先阅读: [[S_图_Graph|S 图 Graph]]

> **考研 408 导引**：本章部分算法在 408 中是**选择题+偶尔简答题考点**。拓扑排序（入度法）、Floyd-Warshall（DP 递推公式）、关键路径（AOE 网）是 408 高频考点。Tarjan SCC 和 Dinic 最大流为增值内容。正文备有 2 组闭卷手算自测。

---

## 原理

### 高级图算法是什么

BFS/DFS/Dijkstra 解决的是"无限制"或"非负权"的图问题。但现实中有更复杂的需求：编译器需要处理循环依赖（负环检测）、物流网络有容量限制（最大流）、社交网络需要发现互关圈（强连通分量）。高级图算法就是解决这些"放宽限制"后的图问题。

**与基础图算法的关系**：

| 基础 | 高级扩展 | 放宽的限制 |
|------|---------|-----------|
| BFS | 拓扑排序 | 有向无环图（DAG）|
| DFS | Tarjan SCC | 发现强连通分量 |
| Dijkstra | Bellman-Ford | 允许负权边 |
| Dijkstra | Floyd-Warshall | 全源（所有点对） |
| BFS | Dinic 最大流 | 边有容量限制 |

### 高级图算法在哪里

- **拓扑排序**：npm install 的依赖安装顺序、大学课程的先修关系、Makefile 的编译顺序
- **Tarjan SCC**：社交网络中"互关圈"分析、编译器循环依赖检测、缩点后在 DAG 上做 DP
- **Bellman-Ford/SPFA**：含负权边的最短路径（如汇率套利检测）、负环检测
- **Floyd-Warshall**：小规模全源最短路径（V ≤ 500）、传递闭包（任意两点是否可达）
- **Dinic 最大流**：二分图最大匹配、物流配送网络优化、图像分割

### 算法全景

| 算法 | 问题 | 时间复杂度 | 核心洞见 |
|------|------|:----------:|---------|
| Kahn | DAG 拓扑排序 | $O(V+E)$ | 零入度节点的队列驱逐 |
| Tarjan SCC | 强连通分量 | $O(V+E)$ | DFS 生成树 + low-link 值判定跨分量边 |
| Bellman-Ford | 单源含负权最短路径 | $O(VE)$ | 至多 $V-1$ 轮松弛——超过即有负环 |
| Floyd-Warshall | 全源最短路径 | $O(V^3)$ | DP：$d(i,j) = \min(d(i,j), d(i,k) + d(k,j))$ |
| Dinic | 最大流 | $O(V^2E)$ | BFS 分层图 + DFS 阻塞流 |

### 拓扑排序（Kahn 算法）

适用于**有向无环图（DAG）**。统计每个顶点的入度——入度为 0 的顶点没有未解决的前驱依赖，可立即输出。输出后将被其指向的顶点的入度减 1，新产生的入度 0 顶点入队。若最终输出的顶点数 $< V$，则图中存在环。拓扑排序是编译器构建系统（Makefile、Gradle 任务）和任务依赖调度（PERT 网络）的基础。

### Tarjan 强连通分量（SCC）

Tarjan 算法在一次 DFS 中同时完成 SCC 的发现和划分。核心是两个时间戳：

- **dfn[v]**（discovery/finish number）：DFS 首次访问 $v$ 的时间（时间戳递增）
- **low[v]**：$v$ 通过最多一条回边能到达的顶点中 dfn 的最小值

当 `dfn[v] == low[v]` 时，$v$ 是其 SCC 的根——构成该 SCC 的所有顶点都在 DFS 栈中、在 $v$ 之上。

```c
// Tarjan SCC 核心
void tarjan(int u, int* dfn, int* low, int* in_stack, int* stk, int* top, int* timer) {
 dfn[u] = low[u] = ++(*timer);
 stk[(*top)++] = u; in_stack[u] = 1;

 for (each neighbor v of u) {
 if (dfn[v] == 0) { // 树边
 tarjan(v, dfn, low, in_stack, stk, top, timer);
 low[u] = MIN(low[u], low[v]); // 子节点的 low 值回传
 } else if (in_stack[v]) { // 回边（当前栈中的后裔）
 low[u] = MIN(low[u], dfn[v]);
 }
 // 横跨边：忽略（dfn[v] 已定且不在栈中）
 }

 if (low[u] == dfn[u]) { // u 是 SCC 的根
 // 弹出栈直到 u，所有弹出的顶点构成一个 SCC
 while (stk[--(*top)] != u) { ... }
 }
}
```

### Bellman-Ford 与负环检测

Bellman-Ford 的每一轮松弛（relaxation）都检查每条边 $(u, v)$：如果当前 $d[u] + w(u, v) < d[v]$，则更新 $d[v]$。$|V|-1$ 轮后，所有最短路径（至多 $|V|-1$ 条边）均已找到。若第 $|V|$ 轮仍能更新任何 $d[v]$，则存在**负权环**——因为正确的最短路径不会超过 $|V|-1$ 条边。

Bellman-Ford 是动态规划在最短路径上的直接体现——第 $k$ 轮松弛等价于"至多使用 $k$ 条边的最短路径"。

### Floyd-Warshall 的 DP 递推

Floyd-Warshall 是经典的动态规划全源最短路径算法：

$$
d^{(k)}(i, j) = \min\left(d^{(k-1)}(i, j),\; d^{(k-1)}(i, k) + d^{(k-1)}(k, j)\right)
$$

含义：加入顶点 $k$ 作为中间节点后，$i$ 到 $j$ 的最短路径要么不经过 $k$（保持原值），要么经过 $k$（路径分为 $i \to k$ 和 $k \to j$ 两段）。三重循环 $O(V^3)$ 但常数因子极小——3 层嵌套循环访问连续的二维数组，cache 利用率高。

#### 拓扑排序手算轨迹

DAG（6 个顶点 0-5）：

```
0 → 1 → 3 → 5
↓   ↓
2 → 4
```

边：(0→1), (0→2), (1→3), (1→4), (2→4), (3→5), (4→5)

**Kahn 算法过程**：

| 步 | 入度为0的队列 | 输出 | 更新入度 |
|:--:|:----------:|:----:|---------|
| 初始 | [0] | — | 0:0, 1:1, 2:1, 3:1, 4:2, 5:2 |
| 1 | [0] → 空 | **0** | 1:0, 2:0 |
| 2 | [1, 2] | — | — |
| 3 | [1, 2] → [2] | **1** | 3:0, 4:1 |
| 4 | [2, 3] → [3] | **2** | 4:0 |
| 5 | [3, 4] → [4] | **3** | 5:1 |
| 6 | [4] → 空 | **4** | 5:0 |
| 7 | [5] → 空 | **5** | — |

拓扑序列：0 → 1 → 2 → 3 → 4 → 5（合法：所有边从左到右）。注意拓扑序列不唯一——0 → 2 → 1 → 4 → 3 → 5 也是合法的。

**408 自测：拓扑排序**

DAG（4 个顶点 0-3），边：(0→1), (0→2), (1→3), (2→3)。写出所有合法拓扑序列。

> 答案：
>
> 入度：0:0, 1:1, 2:1, 3:2。
>
> 第一步只能输出 0。0 输出后 1 和 2 入度变 0，可以任选。所以合法序列有：
> - 0 → 1 → 2 → 3
> - 0 → 2 → 1 → 3
>
> 共 **2 种**合法拓扑序列。

#### Floyd-Warshall 手算轨迹

4 个顶点（0-3）的有向加权图，邻接矩阵：

```
      0    1    2    3
0 [  0    3    ∞    7  ]
1 [  8    0    2    ∞  ]
2 [  5    ∞    0    1  ]
3 [  2    ∞    ∞    0  ]
```

**初始化**：$d^{(0)}$ = 邻接矩阵（∞ 表示不可达）

**k=0**（以 0 为中间节点）：$d(i,j) = \min(d(i,j), d(i,0)+d(0,j))$

| (i,j) | d(i,j) | d(i,0)+d(0,j) | 更新 |
|:------:|:------:|:------------:|:----:|
| (1,2) | 2 | 8+3=11 | 不更新 |
| (1,3) | ∞ | 8+7=15 | **15** |
| (2,1) | ∞ | 5+3=8 | **8** |
| (2,3) | 1 | 5+7=12 | 不更新 |

**k=1**（以 1 为中间节点）：$d(i,j) = \min(d(i,j), d(i,1)+d(1,j))$

| (i,j) | d(i,j) | d(i,1)+d(1,j) | 更新 |
|:------:|:------:|:------------:|:----:|
| (0,2) | ∞ | 3+2=5 | **5** |
| (0,3) | 7 | 3+15=18 | 不更新 |
| (2,3) | 1 | 8+2=10 | 不更新 |
| (3,2) | ∞ | ∞+2=∞ | 不更新 |

**k=2**（以 2 为中间节点）：$d(i,j) = \min(d(i,j), d(i,2)+d(2,j))$

| (i,j) | d(i,j) | d(i,2)+d(2,j) | 更新 |
|:------:|:------:|:------------:|:----:|
| (0,3) | 7 | 5+1=6 | **6** |
| (1,3) | 15 | 2+1=3 | **3** |
| (3,1) | ∞ | ∞+8=∞ | 不更新 |

**k=3**（以 3 为中间节点）：无新更新（3 的出边只有到自身）。

最终 $d^{(3)}$：

```
      0    1    2    3
0 [  0    3    5    6  ]
1 [  8    0    2    3  ]
2 [  5    8    0    1  ]
3 [  2    5    8    0  ]
```

验证：$d(1,3) = 3$，路径 1→2→3（权重 2+1=3）[正确]

**408 自测：Floyd-Warshall**

3 个顶点，邻接矩阵：`[[0,1,4],[∞,0,2],[∞,∞,0]]`。执行 Floyd 后 d(0,2) = ?

> 答案：
>
> 初始化：d(0,2)=4, d(0,1)=1, d(1,2)=2
>
> k=0：d(1,2)=min(2, d(1,0)+d(0,2))=min(2,∞+4)=2（不变）
>
> k=1：d(0,2)=min(4, d(0,1)+d(1,2))=min(4, 1+2)=**3**
>
> 路径 0→1→2，权重 1+2=3。

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

 if (ri < V) { // 存在环
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

| 题号 | 题目 | 说明 |
|------|------|------|
| [207](https://leetcode.cn/problems/course-schedule/) | 课程表 | 拓扑排序 |
| [210](https://leetcode.cn/problems/course-schedule-ii/) | 课程表 II | 拓扑排序输出序列 |
| [787](https://leetcode.cn/problems/cheapest-flights-within-k-stops/) | K 站中转最便宜航班 | Bellman-Ford / DP |
| [1192](https://leetcode.cn/problems/critical-connections-in-a-network/) | 查找集群内的关键连接 | Tarjan SCC |
| [332](https://leetcode.cn/problems/reconstruct-itinerary/) | 重新安排行程 | 欧拉回路 + DFS |
| [743](https://leetcode.cn/problems/network-delay-time/) | 网络延迟时间 | Dijkstra（复习） |

> 力扣 (LeetCode) 有对应题型，竞赛方向推荐力扣/Codeforces。

## 动手实验

| 编号 | 题目 | 说明 |
|:----:|------|------|
| E1 | 有向无环图拓扑排序 | 生成一个 20 个节点的随机 DAG，分别用 Kahn 算法和 DFS 后序遍历输出拓扑序列，验证结果正确性（序列中所有边从左指向右） |
| E2 | Bellman-Ford vs SPFA | 随机生成含负权边的稀疏图，分别用 Bellman-Ford 和 SPFA 求最短路径，对比迭代次数和运行时间。构造一个 Worst Case 让 SPFA 退化 |
