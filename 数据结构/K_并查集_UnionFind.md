# K 并查集 Union-Find

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

```cpp
#include <vector>
#include <numeric>

class UnionFind {
private:
    std::vector<int> parent;
    std::vector<int> rank;
    int count; // 连通分量数

public:
    UnionFind(int n) : parent(n), rank(n, 0), count(n) {
        std::iota(parent.begin(), parent.end(), 0);
    }

    int find(int x) {
        if (parent[x] != x)
            parent[x] = find(parent[x]); // 路径压缩
        return parent[x];
    }

    bool unite(int x, int y) {
        int px = find(x), py = find(y);
        if (px == py) return false;

        if (rank[px] < rank[py]) std::swap(px, py);
        parent[py] = px;
        if (rank[px] == rank[py]) ++rank[px];
        --count;
        return true;
    }

    bool connected(int x, int y) {
        return find(x) == find(y);
    }

    int getCount() const { return count; }
};
```

### 带权并查集

维护元素与父节点之间的权值关系（如距离、差值）：

```cpp
class WeightedUnionFind {
private:
    std::vector<int> parent, rank;
    std::vector<int> weight; // weight[i] = i 到 parent[i] 的权值差

public:
    WeightedUnionFind(int n) : parent(n), rank(n, 0), weight(n, 0) {
        std::iota(parent.begin(), parent.end(), 0);
    }

    std::pair<int, int> find(int x) {
        if (parent[x] == x) return {x, 0};
        auto [root, w] = find(parent[x]);
        parent[x] = root;
        weight[x] += w;
        return {root, weight[x]};
    }

    // 声明: x 和 y 的权值之差为 w (即 value(y) - value(x) = w)
    bool unite(int x, int y, int w) {
        auto [px, wx] = find(x);
        auto [py, wy] = find(y);
        if (px == py) return (wy - wx) == w; // 验证一致性

        if (rank[px] < rank[py]) {
            parent[px] = py;
            weight[px] = wy - wx - w;
        } else {
            parent[py] = px;
            weight[py] = wx - wy + w;
            if (rank[px] == rank[py]) ++rank[px];
        }
        return true;
    }

    bool query(int x, int y, int& diff) {
        auto [px, wx] = find(x);
        auto [py, wy] = find(y);
        if (px != py) return false;
        diff = wy - wx;
        return true;
    }
};
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
