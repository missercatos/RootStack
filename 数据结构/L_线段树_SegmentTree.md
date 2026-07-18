

建议先阅读: [[A_容器_Container|A 容器 Container]], [[../算法/算法技巧/递推递归|递推递归]]

---

## 原理

线段树（Segment Tree）是一种用于高效处理区间查询和区间修改的树形数据结构。它将数组划分为若干区间，每个节点维护对应区间的聚合信息（和、最大值、最小值等）。

### 核心特性

- 完全二叉树结构，叶子节点对应原数组单个元素
- 每个内部节点对应其子节点区间的并集
- 根节点对应整个数组区间 [0, n-1]

### 时间复杂度

| 操作 | 复杂度 | 说明 |
|------|--------|------|
| 建树 build | O(n) | 每个节点计算一次 |
| 单点修改 | O(log n) | 从叶到根更新路径 |
| 区间查询 | O(log n) | 目标区间拆成最多 4*log n 个节点 |
| 区间修改（懒标记） | O(log n) | 延迟下推更新 |

空间复杂度: O(4n)

### 线段树 vs 树状数组

| 特性 | 线段树 | 树状数组 |
|------|--------|----------|
| 功能 | 支持区间最值、区间和等 | 仅支持前缀和、可减操作 |
| 区间修改 | 懒标记 | 差分（受限） |
| 代码量 | 较长 | 极短 |
| 常数因子 | 较大 | 较小 |

---

## 实现

### 区间和线段树（带懒标记）

```cpp
#include <vector>
#include <iostream>

class LazySegmentTree {
private:
    std::vector<long long> tree, lazy;
    int n;

    void build(const std::vector<int>& arr, int node, int l, int r) {
        if (l == r) {
            tree[node] = arr[l];
            return;
        }
        int mid = l + (r - l) / 2;
        build(arr, node * 2, l, mid);
        build(arr, node * 2 + 1, mid + 1, r);
        tree[node] = tree[node * 2] + tree[node * 2 + 1];
    }

    void pushDown(int node, int l, int r) {
        if (lazy[node] == 0) return;
        int mid = l + (r - l) / 2;
        int left = node * 2, right = node * 2 + 1;

        tree[left] += lazy[node] * (mid - l + 1);
        tree[right] += lazy[node] * (r - mid);
        lazy[left] += lazy[node];
        lazy[right] += lazy[node];
        lazy[node] = 0;
    }

    void rangeAdd(int node, int l, int r, int ql, int qr, long long val) {
        if (qr < l || r < ql) return;
        if (ql <= l && r <= qr) {
            tree[node] += val * (r - l + 1);
            lazy[node] += val;
            return;
        }
        pushDown(node, l, r);
        int mid = l + (r - l) / 2;
        rangeAdd(node * 2, l, mid, ql, qr, val);
        rangeAdd(node * 2 + 1, mid + 1, r, ql, qr, val);
        tree[node] = tree[node * 2] + tree[node * 2 + 1];
    }

    long long rangeQuery(int node, int l, int r, int ql, int qr) {
        if (qr < l || r < ql) return 0;
        if (ql <= l && r <= qr) return tree[node];
        pushDown(node, l, r);
        int mid = l + (r - l) / 2;
        return rangeQuery(node * 2, l, mid, ql, qr) +
               rangeQuery(node * 2 + 1, mid + 1, r, ql, qr);
    }

public:
    LazySegmentTree(const std::vector<int>& arr) {
        n = arr.size();
        tree.resize(4 * n);
        lazy.resize(4 * n);
        build(arr, 1, 0, n - 1);
    }

    void add(int l, int r, long long val) {
        rangeAdd(1, 0, n - 1, l, r, val);
    }

    long long sum(int l, int r) {
        return rangeQuery(1, 0, n - 1, l, r);
    }
};
```

### 最大值线段树（无懒标记）

```cpp
class MaxSegmentTree {
private:
    std::vector<int> tree;
    int n;

    void build(const std::vector<int>& arr, int node, int l, int r) {
        if (l == r) { tree[node] = arr[l]; return; }
        int mid = l + (r - l) / 2;
        build(arr, node * 2, l, mid);
        build(arr, node * 2 + 1, mid + 1, r);
        tree[node] = std::max(tree[node * 2], tree[node * 2 + 1]);
    }

    void update(int node, int l, int r, int idx, int val) {
        if (l == r) { tree[node] = val; return; }
        int mid = l + (r - l) / 2;
        if (idx <= mid) update(node * 2, l, mid, idx, val);
        else update(node * 2 + 1, mid + 1, r, idx, val);
        tree[node] = std::max(tree[node * 2], tree[node * 2 + 1]);
    }

    int query(int node, int l, int r, int ql, int qr) {
        if (qr < l || r < ql) return INT_MIN;
        if (ql <= l && r <= qr) return tree[node];
        int mid = l + (r - l) / 2;
        return std::max(query(node * 2, l, mid, ql, qr),
                        query(node * 2 + 1, mid + 1, r, ql, qr));
    }

public:
    MaxSegmentTree(const std::vector<int>& arr) : n(arr.size()) {
        tree.resize(4 * n);
        build(arr, 1, 0, n - 1);
    }
    void update(int idx, int val) { update(1, 0, n - 1, idx, val); }
    int maxVal(int l, int r) { return query(1, 0, n - 1, l, r); }
};
```

---

## 应用场景

- **区间求和/最值**: 数组中任意区间 [l, r] 的聚合查询
- **区间染色**: 用线段树管理区间覆盖（懒标记为颜色值）
- **区间第 K 小**: 使用主席树（持久化线段树）查询历史版本的区间

---

## 练习

| 题号 | 题目 | 难度 | 知识点 |
|------|------|------|--------|
| P3372 | 线段树 1 | 普及+ | 区间加 + 区间求和 |
| P3373 | 线段树 2 | 提高 | 区间乘 + 区间加 |
| P4588 | 数学计算 | 提高 | 线段树维护操作序列 |
