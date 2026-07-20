## 概述

斜率优化（Convex Hull Trick）将 DP 转移化为直线截距最值问题：$b_i = \min_{j < i} \{ y_j - k_i x_j \}$。其中 $(x_j, y_j)$ 是决策点，$k_i$ 是查询斜率。适用条件为转移方程可整理为 $f_i = \min/\max A_j + B_i + C_i \cdot D_j$。

## 线性规划形式

以玩具装箱（P3195）为例：$f_i = \min_{j < i} \{ f_j + (s_i - s_j - L')^2 \}$，整理得：

$$
f_i - (s_i - L')^2 = \min_{j < i} \{ (f_j + s_j^2) + 2 s_j (L' - s_i) \}
$$

设 $x_j = s_j,\; y_j = f_j + s_j^2,\; k_i = -2(L' - s_i)$，则 $b_i = \min_j (y_j - k_i x_j)$。

## 凸包维护

**下凸壳**用于 $\min$ 问题，**上凸壳**用于 $\max$ 问题。当 $k_i$ 和 $x_j$ 均单调时，用[[../../数据结构/F_队列_Queue|单调队列]]维护凸包：

```cpp
deque<int> q;
q.push_back(0);
for (int i = 1; i <= n; ++i) {
    while (q.size() >= 2 && slope(q[0], q[1]) <= k[i]) q.pop_front();
    int j = q.front();
    f[i] = y[j] - k[i] * x[j];
    while (q.size() >= 2 && slope(q.back() - 1, q.back()) >= slope(q.back(), i))
        q.pop_back();
    q.push_back(i);
}
```

## 二分斜率

当 $k_i$ 不单调时，在凸包上二分查找斜率最接近 $k_i$ 的边。当 $x_j$ 也不单调时，需用 CDQ 分治或 [[../../数据结构/C_堆_Heap|平衡树]] 维护凸包。

## 问题模板

| 题目 | 题号 | 说明 |
|------|------|------|
| 玩具装箱 | P3195 | 经典入门，单调 $x$ 单调 $k$ |
| 特别行动队 | P3628 | $f_i = \max a x^2 + b x + c$ 形式 |
| 土地购买 | P2900 | 按 $x$ 排序后斜率优化 |
| 征途 | SDOI2016 | 斜率优化 + 方差转换 |
| 仓库建设 | ZJOI2007 | 需注意数据类型范围 |

## 完整推导：从 DP 到 $y = mx + b$

以 P3195 玩具装箱为例，详细演示转化过程。

**原方程：**

$$
f_i = \min_{j < i} \big\{ f_j + (s_i - s_j - L')^2 \big\}, \quad s_i = \sum_{k=1}^i (c_k + 1),\; L' = L + 1
$$

**展开配方：**

$$
\begin{aligned}
f_i &= \min_{j < i} \big\{ f_j + (s_i - L')^2 + s_j^2 - 2 s_j (s_i - L') \big\} \\
&= (s_i - L')^2 + \min_{j < i} \big\{ (f_j + s_j^2) - 2 s_j (s_i - L') \big\}
\end{aligned}
$$

**变量代换：**

$$
\begin{cases}
x_j = s_j \\[2pt]
y_j = f_j + s_j^2 \\[2pt]
k_i = 2 (s_i - L') \\[2pt]
b_i = f_i - (s_i - L')^2
\end{cases}
\quad\Longrightarrow\quad
b_i = \min_j (\,y_j - k_i x_j\,)
$$

几何意义：对每个 $i$，有一条斜率为 $k_i$ 的直线从 $-\infty$ 上移，**第一个碰到的决策点** $(x_j, y_j)$ 即为最优 $j$。所有可能成为最优的决策点构成一个**下凸壳**。

## 凸包维护详解

### 单调队列维护（$x$ 单调，$k$ 单调）

当 $x_j$ 随 $j$ 递增，且 $k_i$ 随 $i$ 单调时，凸包可用单调队列维护：

```cpp
using ll = long long;
struct Point { ll x, y; };
Point p[N];
deque<int> q;

double slope(int a, int b) {
    return (double)(p[b].y - p[a].y) / (p[b].x - p[a].x);
}

void add_point(int i) {
    // 维护下凸壳：新点必须使相邻斜率递增
    while (q.size() >= 2 &&
           slope(q[q.size()-2], q.back()) >= slope(q.back(), i))
        q.pop_back();
    q.push_back(i);
}

ll query(ll k) {
    // 斜率单调递增时，队首即为最优
    while (q.size() >= 2 && slope(q[0], q[1]) <= k) q.pop_front();
    int j = q.front();
    return p[j].y - k * p[j].x;
}
```

**判优条件（最小值，下凸壳）：** $slope(a,b) \le k_i \le slope(b,c)$ 时 $b$ 最优。当 $k_i$ 递增时，队首一旦被弹出就不会再用。

### 二分查找维护（$x$ 单调，$k$ 任意）

若 $k_i$ **不单调**（但 $x_j$ 仍单调），仍可用单调队列维护凸包，但查询时改为**二分**：

```cpp
ll query_binary(ll k) {
    int l = 0, r = q.size() - 1;
    while (l < r) {
        int m = (l + r) / 2;
        if (slope(q[m], q[m+1]) <= k) l = m + 1;
        else r = m;
    }
    int j = q[l];
    return p[j].y - k * p[j].x;
}
```

在凸包上二分找到第一个斜率 $> k$ 的位置，该位置前一点即为最优。

### Li Chao 线段树（$x$ 任意，$k$ 任意）

当 $x_j$ 也**不单调**时，可使用 Li Chao 线段树在值域上维护直线集合，支持 $O(\log V)$ 插入与查询，无需关心凸包性质。适用于强制在线或纵坐标无序的场景。

```cpp
struct Line {
    ll k, b;
    ll operator()(ll x) { return k * x + b; }
};
Line tree[N * 4];

void insert(int p, int l, int r, Line cur) {
    int m = (l + r) / 2;
    bool left = cur(l) < tree[p](l);
    bool mid  = cur(m) < tree[p](m);
    if (mid) swap(tree[p], cur);
    if (l == r) return;
    if (left != mid) insert(p*2, l, m, cur);
    else insert(p*2+1, m+1, r, cur);
}

ll query(int p, int l, int r, ll x) {
    ll res = tree[p](x);
    if (l == r) return res;
    int m = (l + r) / 2;
    if (x <= m) res = min(res, query(p*2, l, m, x));
    else res = min(res, query(p*2+1, m+1, r, x));
    return res;
}
```

## P3195 玩具装箱 完整题解

```cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;
const int N = 50010;

ll n, L, s[N], f[N];
deque<int> q;

ll X(int j) { return s[j]; }
ll Y(int j) { return f[j] + s[j] * s[j]; }
double slope(int a, int b) {
    return (double)(Y(b) - Y(a)) / (X(b) - X(a));
}

int main() {
    cin >> n >> L;
    for (int i = 1; i <= n; ++i) {
        cin >> s[i];
        s[i] += s[i-1] + 1;
    }
    L++;
    q.push_back(0);
    for (int i = 1; i <= n; ++i) {
        ll k = 2 * (s[i] - L);
        while (q.size() >= 2 && slope(q[0], q[1]) <= k) q.pop_front();
        int j = q.front();
        f[i] = Y(j) - k * X(j) + (s[i] - L) * (s[i] - L);
        while (q.size() >= 2 && slope(q[q.size()-2], q.back()) >= slope(q.back(), i))
            q.pop_back();
        q.push_back(i);
    }
    cout << f[n] << endl;
    return 0;
}
```

$$
f_i = \underbrace{(s_i - L')^2}_{\text{常数项}} + \underbrace{(f_j + s_j^2)}_{y_j} - \underbrace{2(s_i - L')}_{k_i} \cdot \underbrace{s_j}_{x_j}
$$

## 凸包性质速查

| 情形 | $x_j$ | $k_i$ | 维护方式 | 查询方式 |
|------|-------|-------|---------|---------|
| 全单调 | 递增 | 递增 | 单调队列 (deque) | 弹出队首 |
| $k$ 不单调 | 递增 | 任意 | 单调队列 (deque) | 二分凸包 |
| $x$ 不单调 | 任意 | 任意 | Li Chao 树 / CDQ | 线段树查询 |
| 最大值 | — | — | 上凸壳 (条件取反) | 对称处理 |

## 相关链接

- [[../../数据结构/F_队列_Queue|F_队列_Queue]]
- [[单调队列优化DP|单调队列优化DP]]
- [[../算法技巧/二分查找|二分查找]]
- [[../算法技巧/动态规划|动态规划]]
- [[../../路径D-DSA算法刷题|刷题清单]]


## 多平台练习

| 洛谷 | [本题单](https://www.luogu.com.cn/) | 竞赛基础 |
| POJ (北大) | [PKU JudgeOnline](http://poj.org/) | 经典题目，适合巩固 |
| HDU (杭电) | [HDU OJ](https://acm.hdu.edu.cn/) | 暑期多校训练 |
| Codeforces | [Codeforces](https://codeforces.com/) | 国际竞赛，适合提升 |
