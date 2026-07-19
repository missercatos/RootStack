

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

```c
#include <stdlib.h>

#define LOWBIT(x) ((x) & -(x))

typedef struct {
    int* tree;
    int n;
} BIT;

void bit_init(BIT* b, int size) {
    b->n = size;
    b->tree = calloc(size + 1, sizeof(int));
}

void bit_destroy(BIT* b) {
    free(b->tree);
}

// O(n) 建树
void bit_build(BIT* b, const int* arr, int n) {
    b->n = n;
    free(b->tree);
    b->tree = calloc(n + 1, sizeof(int));
    for (int i = 1; i <= n; i++) {
        b->tree[i] += arr[i - 1];
        int parent = i + LOWBIT(i);
        if (parent <= n) b->tree[parent] += b->tree[i];
    }
}

void bit_add(BIT* b, int pos, int delta) {
    while (pos <= b->n) {
        b->tree[pos] += delta;
        pos += LOWBIT(pos);
    }
}

int bit_prefix_sum(BIT* b, int pos) {
    int sum = 0;
    while (pos > 0) {
        sum += b->tree[pos];
        pos -= LOWBIT(pos);
    }
    return sum;
}

int bit_range_sum(BIT* b, int l, int r) {
    return bit_prefix_sum(b, r) - bit_prefix_sum(b, l - 1);
}
```

### 区间修改 + 单点查询（差分 BIT）

```c
typedef struct {
    int* tree;
    int n;
} DiffBIT;

void diff_bit_init(DiffBIT* b, int size) {
    b->n = size;
    b->tree = calloc(size + 1, sizeof(int));
}

void diff_bit_destroy(DiffBIT* b) { free(b->tree); }

static void diff_add(DiffBIT* b, int pos, int delta) {
    while (pos <= b->n) { b->tree[pos] += delta; pos += LOWBIT(pos); }
}

void diff_bit_range_add(DiffBIT* b, int l, int r, int val) {
    diff_add(b, l, val);
    diff_add(b, r + 1, -val);
}

int diff_bit_point_query(DiffBIT* b, int pos) {
    int sum = 0;
    while (pos > 0) { sum += b->tree[pos]; pos -= LOWBIT(pos); }
    return sum;
}
```

### 区间修改 + 区间查询（双 BIT）

```c
typedef struct {
    long long* t1;   // diff[i]
    long long* t2;   // i * diff[i]
    int n;
} RangeBIT;

void range_bit_init(RangeBIT* b, int size) {
    b->n = size;
    b->t1 = calloc(size + 1, sizeof(long long));
    b->t2 = calloc(size + 1, sizeof(long long));
}

void range_bit_destroy(RangeBIT* b) { free(b->t1); free(b->t2); }

static void range_add_arr(long long* t, int n, int pos, long long delta) {
    while (pos <= n) { t[pos] += delta; pos += LOWBIT(pos); }
}

static long long range_sum_arr(long long* t, int pos) {
    long long s = 0;
    while (pos > 0) { s += t[pos]; pos -= LOWBIT(pos); }
    return s;
}

void range_bit_add(RangeBIT* b, int l, int r, long long val) {
    range_add_arr(b->t1, b->n, l, val);
    range_add_arr(b->t1, b->n, r + 1, -val);
    range_add_arr(b->t2, b->n, l, val * (l - 1));
    range_add_arr(b->t2, b->n, r + 1, -val * r);
}

long long range_bit_prefix_sum(RangeBIT* b, int pos) {
    return range_sum_arr(b->t1, pos) * pos - range_sum_arr(b->t2, pos);
}

long long range_bit_range_sum(RangeBIT* b, int l, int r) {
    return range_bit_prefix_sum(b, r) - range_bit_prefix_sum(b, l - 1);
}
```

### 权值 BIT 求第 K 小

```c
typedef struct {
    int* tree;
    int n;
} KthBIT;

void kth_bit_init(KthBIT* b, int max_val) {
    b->n = max_val;
    b->tree = calloc(max_val + 1, sizeof(int));
}

void kth_bit_destroy(KthBIT* b) { free(b->tree); }

void kth_bit_add(KthBIT* b, int val, int delta) {
    for (int i = val; i <= b->n; i += LOWBIT(i))
        b->tree[i] += delta;
}

int kth_bit_kth(KthBIT* b, int k) {
    int pos = 0;
    for (int i = 20; i >= 0; i--) {
        int next = pos + (1 << i);
        if (next <= b->n && b->tree[next] < k) {
            k -= b->tree[next];
            pos = next;
        }
    }
    return pos + 1;
}
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
