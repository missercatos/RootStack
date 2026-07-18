

建议先阅读: [[L_线段树_SegmentTree|L 线段树 SegmentTree]]

---

## 原理

树状数组（Binary Indexed Tree / Fenwick Tree）利用二进制的性质将数组划分为若干区间，使单点修改和前缀和查询均在 O(log n) 内完成。相比线段树，代码更短、常数更小。

### 核心概念

**lowbit(x)** = x & (-x)，取 x 二进制最低位 1 所代表的值。

- lowbit(6) = lowbit(110) = 2
- lowbit(12) = lowbit(1100) = 4

BIT[i] 管理的区间为 [i - lowbit(i) + 1, i]。

### 操作逻辑

- **前缀和 prefixSum(k)**: k -= lowbit(k) 直到 0，累加经过的 BIT 节点
- **单点更新 add(k, delta)**: k += lowbit(k) 直到超过 n，更新 BIT 节点

### 区间管理示例

| 位置 i | lowbit(i) | 管理区间 |
|--------|-----------|----------|
| 1 | 1 | [1, 1] |
| 2 | 2 | [1, 2] |
| 3 | 1 | [3, 3] |
| 4 | 4 | [1, 4] |
| 5 | 1 | [5, 5] |
| 6 | 2 | [5, 6] |
| 7 | 1 | [7, 7] |
| 8 | 8 | [1, 8] |

### 时间复杂度

| 操作 | 复杂度 |
|------|--------|
| 单点修改 | O(log n) |
| 前缀和查询 | O(log n) |
| 区间和查询 | O(log n) |
| O(n) 建树 | O(n) |

空间: O(n)

---

## 实现

### 标准 BIT（单点修改 + 区间查询）

```cpp
#include <vector>

class BIT {
private:
    std::vector<int> tree;
    int n;

    int lowbit(int x) { return x & -x; }

public:
    BIT(int size) : n(size), tree(size + 1, 0) {}

    // O(n log n) 建树
    BIT(const std::vector<int>& arr) : n(arr.size()), tree(arr.size() + 1, 0) {
        for (int i = 0; i < n; ++i)
            add(i + 1, arr[i]);
    }

    // O(n) 建树
    void build(const std::vector<int>& arr) {
        n = arr.size();
        tree.assign(n + 1, 0);
        for (int i = 1; i <= n; ++i) {
            tree[i] += arr[i - 1];
            int parent = i + lowbit(i);
            if (parent <= n) tree[parent] += tree[i];
        }
    }

    void add(int pos, int delta) {
        while (pos <= n) {
            tree[pos] += delta;
            pos += lowbit(pos);
        }
    }

    int prefixSum(int pos) {
        int sum = 0;
        while (pos > 0) {
            sum += tree[pos];
            pos -= lowbit(pos);
        }
        return sum;
    }

    int rangeSum(int l, int r) {
        return prefixSum(r) - prefixSum(l - 1);
    }
};
```

### 区间修改 + 单点查询（差分 BIT）

```cpp
class DiffBIT {
private:
    std::vector<int> tree;
    int n;
    int lowbit(int x) { return x & -x; }

    void add(int pos, int delta) {
        while (pos <= n) {
            tree[pos] += delta;
            pos += lowbit(pos);
        }
    }
    int query(int pos) {
        int sum = 0;
        while (pos > 0) { sum += tree[pos]; pos -= lowbit(pos); }
        return sum;
    }

public:
    DiffBIT(int size) : n(size), tree(size + 1, 0) {}

    void rangeAdd(int l, int r, int val) {
        add(l, val);
        add(r + 1, -val);
    }

    int pointQuery(int pos) {
        return query(pos);
    }
};
```

### 区间修改 + 区间查询（双 BIT）

```cpp
class RangeBIT {
private:
    std::vector<long long> t1, t2; // t1: diff[i], t2: i * diff[i]
    int n;
    int lowbit(int x) { return x & -x; }

    void add(std::vector<long long>& t, int pos, long long delta) {
        while (pos <= n) { t[pos] += delta; pos += lowbit(pos); }
    }
    long long sum(std::vector<long long>& t, int pos) {
        long long s = 0;
        while (pos > 0) { s += t[pos]; pos -= lowbit(pos); }
        return s;
    }

public:
    RangeBIT(int size) : n(size), t1(size + 1), t2(size + 1) {}

    void rangeAdd(int l, int r, long long val) {
        add(t1, l, val);
        add(t1, r + 1, -val);
        add(t2, l, val * (l - 1));
        add(t2, r + 1, -val * r);
    }

    long long prefixSum(int pos) {
        return sum(t1, pos) * pos - sum(t2, pos);
    }

    long long rangeSum(int l, int r) {
        return prefixSum(r) - prefixSum(l - 1);
    }
};
```

### 权值 BIT 求第 K 小

```cpp
class KthBIT {
private:
    std::vector<int> tree;
    int n;
    int lowbit(int x) { return x & -x; }

public:
    KthBIT(int maxVal) : n(maxVal), tree(maxVal + 1, 0) {}

    void add(int val, int delta = 1) {
        for (int i = val; i <= n; i += lowbit(i))
            tree[i] += delta;
    }

    int kth(int k) {
        int pos = 0;
        for (int i = 20; i >= 0; --i) { // 2^20 足够 n <= 10^6
            int next = pos + (1 << i);
            if (next <= n && tree[next] < k) {
                k -= tree[next];
                pos = next;
            }
        }
        return pos + 1;
    }
};
```

---

## 应用场景

- **区间求和**: 单点修改 + 区间和查询
- **差分维护**: 区间修改 + 单点查询（如区间加 k 后查询某位置的值）
- **逆序对计数**: 从右到左插入，查询比当前值小的已插入个数
- **二维偏序（星星等级）**: 按 y 排序后，对 x 建立 BIT 统计

---

## 练习

| 题号 | 题目 | 难度 | 知识点 |
|------|------|------|--------|
| P3374 | 树状数组 1 | 普及 | 单点修改 + 区间查询 |
| P3368 | 树状数组 2 | 普及 | 区间修改 + 单点查询 |
| P1908 | 逆序对 | 普及+ | 树状数组求逆序对 |
