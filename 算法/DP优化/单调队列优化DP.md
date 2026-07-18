## 概述

单调队列优化 DP 适用于形如 $f_i = \min/\max_{j \in [i-k, i-1]} \{ f_j + \text{cost}(j,i) \}$ 的转移方程，其中决策变量 $j$ 的取值范围是滑动窗口。核心思想是用[[../../数据结构/F_队列_Queue|单调队列]]维护候选决策集合，均摊 $O(1)$ 获取最优值。

## 基本原理

设 $f_i$ 为前 $i$ 个元素的最优值，转移需要枚举上一阶段的位置 $j$。若 $\text{cost}(j,i)$ 可分离为 $A_j + B_i$，则只需维护 $A_j$ 的极值：

$$
f_i = B_i + \min_{j \in [i-k,i-1]} \{ f_j + A_j \}
$$

将 $f_j + A_j$ 视为决策值存入单调队列，队首即为当前窗口最优。

## 多重背包优化

对于完全/多重背包，按模 $w_i$ 的余数 $y$ 分组，每组内用单调队列维护：

$$
g_{x,y} = \max_{k=0}^{k_i} (g'_{x-k,y} - v_i \cdot (x-k)) + v_i \cdot x
$$

**参考代码框架：**

```cpp
deque<int> q;
for (int y = 0; y < w[i]; ++y) {
    q.clear();
    for (int x = 0; x * w[i] + y <= W; ++x) {
        int cur = x * w[i] + y;
        while (!q.empty() && q.front() < x - k[i]) q.pop_front();
        if (!q.empty())
            f[cur] = max(f[cur], g[q.front() * w[i] + y] - q.front() * v[i] + x * v[i]);
        while (!q.empty() && g[cur] - x * v[i] >= g[q.back() * w[i] + y] - q.back() * v[i])
            q.pop_back();
        q.push_back(x);
    }
}
```

## 问题模板

| 题目 | 题号 | 说明 |
|------|------|------|
| 滑动窗口 | P1886 | 纯滑动窗口最值，单调队列入门 |
| 多重背包 | P1776 | 多重背包的单调队列优化 |
| 琪露诺 | P1725 | $f_i = \max_{j \in [i-R,i-L]} f_j + a_i$ |
| Watching Fireworks | CF372C | 二维 DP + 滚动单调队列 |

## 问题归约

单调队列优化的核心模式可统一为：

$$
f_i = \text{base}_i + \min_{j \in [L_i,\,R_i]} \{ g_j \}
$$

其中 $g_j = f_j + A_j$ 仅依赖于 $j$，且窗口左右边界 $L_i, R_i$ 随 $i$ **单调递增**（滑动窗口性质）。此时用单调队列维护 $g_j$，即可 $O(1)$ 取出窗口最值。

**常见可归约类型：**

| 问题 | $g_j$ | $\text{base}_i$ | 窗口 |
|------|-------|-----------------|------|
| 滑动窗口最值 | $a_j$ | $0$ | $[i-k+1,\,i]$ |
| 多重背包 (模 $y$ 组) | $f'_j - v\cdot j$ | $v \cdot i$ | $[i-k_i,\,i]$ |
| 跳跃游戏 (P1725) | $f_j$ | $a_i$ | $[i-R,\,i-L]$ |
| 序列分段 | $f_j + w(j+1,i)$ 的 $j$ 部分 | $w$ 的 $i$ 部分 | 决策单调区间 |

## 完整例题：P1725 琪露诺

**题意：** 从 0 出发，每次跳跃 $[L,R]$ 步，到达位置 $i$ 获得 $a_i$，求到 $n$ 的最大得分，可越过 $n$ 结束。

**状态定义：** $f_i$ 表示到达 $i$ 时的最大得分。

**转移方程：**

$$
f_i = a_i + \max_{j \in [i-R,\,i-L]} f_j
$$

窗口长度 $k = R-L+1$，$j$ 的取值范围随 $i$ 右移，正好是滑动窗口最大值问题。

```cpp
#include <bits/stdc++.h>
using namespace std;
const int N = 200010, INF = 0x80808080;
int n, L, R, a[N], f[N];

int main() {
    cin >> n >> L >> R;
    for (int i = 0; i <= n; ++i) cin >> a[i];

    memset(f, 0x80, sizeof f);  // 负无穷
    f[0] = a[0];
    deque<int> q;
    int ans = INF;

    for (int i = L; i <= n; ++i) {
        // 候选决策 j = i - L 进入窗口
        int j = i - L;
        while (!q.empty() && f[q.back()] <= f[j]) q.pop_back();
        q.push_back(j);
        // 弹出窗口左界之外的决策 (j < i - R)
        while (!q.empty() && q.front() < i - R) q.pop_front();
        // 队首为最优决策
        f[i] = f[q.front()] + a[i];
        // 越过 n 可结束，更新答案
        if (i + R > n) ans = max(ans, f[i]);
    }
    cout << ans << endl;
    return 0;
}
```

**复杂度分析：** 每个元素入队一次、出队至多一次，均摊 $O(1)$，总复杂度 $O(n)$。朴素 DP 每次枚举 $O(k)$ 个决策，总 $O(nk)$，当 $k = O(n)$ 时退化为 $O(n^2)$。

## 通用代码模板

```cpp
// 状态转移: f[i] = min/max_{j in [i-k, i-1]} (f[j] + cost(j, i))
// 前置条件: cost(j,i) = A[j] + B[i] 或可分离为类似形式
deque<int> q;
vector<int> f(n + 1);

for (int i = 1; i <= n; ++i) {
    // Step 1: 维护窗口左界 —— 弹出过期的决策
    while (!q.empty() && q.front() < max_left(i)) q.pop_front();

    // Step 2: 取队首最优决策进行转移
    if (!q.empty()) {
        int j = q.front();
        f[i] = B[i] + (f[j] + A[j]);  // 具体形式视问题而定
    }

    // Step 3: 维护队列单调性 —— 弹出尾部劣于当前决策的元素
    while (!q.empty() && better(i, q.back())) q.pop_back();

    // Step 4: 当前决策入队
    q.push_back(i);
}
```

**四个步骤的口诀：** 一弹过期，二取最优，三保单调，四插入队。

## 复杂度对比

| 维度 | 朴素 DP | 单调队列优化 |
|------|---------|-------------|
| 单个状态转移 | $O(k)$ | $O(1)$ (均摊) |
| 总时间复杂度 | $O(nk)$ | $O(n)$ |
| 空间复杂度 | $O(n)$ | $O(n)$ (DP 数组) + $O(k)$ (队列) |
| 适用限制 | 无 | $\text{cost}$ 可分离，窗口单调 |

## 相关链接

- [[../../数据结构/F_队列_Queue|F_队列_Queue]]
- [[../../数据结构/C_堆_Heap|C_堆_Heap]]
- [[斜率优化CHT|斜率优化CHT]]
- [[../算法技巧/动态规划|动态规划]]
- [[../算法技巧/二分查找|二分查找]]
- [[../../路径D-DSA算法刷题|刷题清单]]
