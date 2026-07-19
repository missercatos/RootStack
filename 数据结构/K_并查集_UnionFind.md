

建议先阅读: [[A_容器_Container|A 容器 Container]]

---

## 原理

并查集（Union-Find / Disjoint Set）是一种处理元素分组和连通性问题的数据结构，支持两种核心操作：合并两个集合和查找元素所属集合。

### 核心操作

- **Find(x)**: 找到元素 x 所在集合的代表（根节点）
- **Union(x, y)**: 将 x 和 y 所在的两个集合合并
- **Connected(x, y)**: 判断 x 和 y 是否在同一集合

### 优化策略

| 优化 | 方法 | 效果 |
|------|------|------|
| 路径压缩 | Find 时将路径上所有节点直接连到根 | 大幅降低后续查找时间 |
| 按秩合并 | 将矮树接到高树下 | 树高不超过 O(log n) |
| 按大小合并 | 将小集合合并到大集合 | 与按秩合并类似 |

### 时间复杂度

| 配置 | Find | Union |
|------|------|-------|
| 无优化 | O(n) | O(n) |
| 仅路径压缩 | 均摊 O(log n) | 均摊 O(log n) |
| 仅按秩合并 | O(log n) | O(log n) |
| 双重优化 | 均摊 O(α(n)) | 均摊 O(α(n)) |

α(n) 是反阿克曼函数，对任何实际输入 <= 5，可视为 O(1)。

---

## 实现

### 标准并查集（路径压缩 + 按秩合并）

```c
#include <stdlib.h>

typedef struct {
    int* parent;
    int* rank;
    int count;    // 连通分量数
} UnionFind;

void uf_init(UnionFind* uf, int n) {
    uf->parent = malloc(n * sizeof(int));
    uf->rank = calloc(n, sizeof(int));
    uf->count = n;
    for (int i = 0; i < n; i++)
        uf->parent[i] = i;
}

void uf_destroy(UnionFind* uf) {
    free(uf->parent);
    free(uf->rank);
}

int uf_find(UnionFind* uf, int x) {
    if (uf->parent[x] != x)
        uf->parent[x] = uf_find(uf, uf->parent[x]);  // 路径压缩
    return uf->parent[x];
}

int uf_unite(UnionFind* uf, int x, int y) {
    int px = uf_find(uf, x);
    int py = uf_find(uf, y);
    if (px == py) return 0;

    if (uf->rank[px] < uf->rank[py]) {
        int t = px; px = py; py = t;
    }
    uf->parent[py] = px;
    if (uf->rank[px] == uf->rank[py])
        uf->rank[px]++;
    uf->count--;
    return 1;
}

int uf_connected(UnionFind* uf, int x, int y) {
    return uf_find(uf, x) == uf_find(uf, y);
}

int uf_get_count(UnionFind* uf) { return uf->count; }
```

### 带权并查集

维护元素与父节点之间的权值关系（如距离、差值），合并时同步更新权值：

```c
typedef struct {
    int* parent;
    int* rank;
    int* weight;   // weight[i] = i 到 parent[i] 的权值差
} WeightedUnionFind;

void wuf_init(WeightedUnionFind* uf, int n) {
    uf->parent = malloc(n * sizeof(int));
    uf->rank = calloc(n, sizeof(int));
    uf->weight = calloc(n, sizeof(int));
    for (int i = 0; i < n; i++)
        uf->parent[i] = i;
}

void wuf_destroy(WeightedUnionFind* uf) {
    free(uf->parent);
    free(uf->rank);
    free(uf->weight);
}

int wuf_find(WeightedUnionFind* uf, int x, int* out_weight) {
    if (uf->parent[x] == x) {
        *out_weight = 0;
        return x;
    }
    int w;
    int root = wuf_find(uf, uf->parent[x], &w);
    uf->parent[x] = root;
    uf->weight[x] += w;
    *out_weight = uf->weight[x];
    return root;
}

// 声明: value(y) - value(x) = w
// 返回 1 合并成功，0 表示 x 和 y 已连通且与 w 矛盾
int wuf_unite(WeightedUnionFind* uf, int x, int y, int w) {
    int wx, wy;
    int px = wuf_find(uf, x, &wx);
    int py = wuf_find(uf, y, &wy);
    if (px == py)
        return (wy - wx) == w;

    if (uf->rank[px] < uf->rank[py]) {
        uf->parent[px] = py;
        uf->weight[px] = wy - wx - w;
    } else {
        uf->parent[py] = px;
        uf->weight[py] = wx - wy + w;
        if (uf->rank[px] == uf->rank[py])
            uf->rank[px]++;
    }
    return 1;
}

// 查询 x 和 y 的权值差，不连通时返回 0
int wuf_query(WeightedUnionFind* uf, int x, int y, int* diff) {
    int wx, wy;
    int px = wuf_find(uf, x, &wx);
    int py = wuf_find(uf, y, &wy);
    if (px != py) return 0;
    *diff = wy - wx;
    return 1;
}
```

---

## 应用场景

- **Kruskal 最小生成树**: 判断加边是否形成环（两端点是否已连通）
- **无向图连通性**: 静态或动态添加边，判断两点是否连通、统计连通分量
- **朋友圈/社交网络**: 合并好友关系，判断两人是否在同一圈子
- **食物链问题**: 带权并查集维护相对关系（同类/捕食）

---

## 练习

| 题号 | 题目 | 难度 | 知识点 |
|------|------|------|--------|
| P3367 | 并查集 | 普及 | 标准模板 |
| P1551 | 亲戚 | 普及 | 并查集应用 |
| P2024 | 食物链 | 提高 | 带权并查集 |
| P1197 | 星球大战 | 提高 | 逆向并查集 |
