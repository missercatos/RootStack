## 整体二分与 WQS 二分

### 整体二分

整体二分将所有询问**同时二分**，适用于答案可二分、修改贡献独立且可加、允许离线的题目。

**流程**：将操作按时间排列，每次取答案值域中点 $mid$，用数据结构检验每个询问的判定结果，将操作分为 $\le mid$ 和 $> mid$ 两部分递归。

```cpp
void solve(int l, int r, vector<Query> q) {
  if (l == r) { for (auto &x : q) ans[x.id] = val[l]; return; }
  int mid = (l + r) >> 1;
  vector<Query> q1, q2;
  int t = check(l, mid);  // 小于等于 mid 的元素个数
  for (auto &x : q) {
    if (x.k <= t) q1.push_back(x);
    else x.k -= t, q2.push_back(x);
  }
  solve(l, mid, q1); solve(mid + 1, r, q2);
}
```

**优化**：对静态序列可用指针追踪分治中心，减少树状数组清空次数，复杂度 $O(n\log^2 n)$ 降至常数更优。

### WQS 二分

WQS 二分（带权二分）用于解决**恰好选 $k$ 个**的凸优化问题。给每个选择附加代价 $\lambda$，将原约束转化为无约束问题，通过二分 $\lambda$ 使解恰好包含 $k$ 个元素。

适用条件：目标函数关于选择数量是凸函数（上凸/下凸）。

### 带修区间第 k 小（P2617）

将修改拆为擦除（$-1$）和插入（$+1$）两个操作，与询问一同参与整体二分。用树状数组维护当前值域 $\le mid$ 的位置个数。

```cpp
struct Opt {
  int x, y, k, type, id;
} q[N], q1[N], q2[N];

void solve(int l, int r, int L, int R) {
  if (l > r || L > R) return;
  if (l == r) {
    for (int i = L; i <= R; i++)
      if (q[i].type == 1) ans[q[i].id] = l;
    return;
  }
  int m = (l + r) >> 1, c1 = 0, c2 = 0;
  for (int i = L; i <= R; i++) {
    if (q[i].type == 1) {
      int t = query(q[i].y) - query(q[i].x - 1);
      if (q[i].k <= t) q1[++c1] = q[i];
      else q[i].k -= t, q2[++c2] = q[i];
    } else if (q[i].y <= m) {
      add(q[i].x, q[i].k), q1[++c1] = q[i];
    } else {
      q2[++c2] = q[i];
    }
  }
  for (int i = 1; i <= c1; i++)
    if (q1[i].type == 0) add(q1[i].x, -q1[i].k);
  for (int i = 1; i <= c1; i++) q[L + i - 1] = q1[i];
  for (int i = 1; i <= c2; i++) q[L + c1 + i - 1] = q2[i];
  solve(l, m, L, L + c1 - 1);
  solve(m + 1, r, L + c1, R);
}
```

### WQS 二分细节

设目标函数 $f(x)$ 是凸函数，则 $g(\lambda) = \min_x \{ f(x) - \lambda x \}$ 是 $\lambda$ 的线性函数。二分 $\lambda$ 使最优解对应的 $x$ 恰好为 $k$，最终答案为 $g(\lambda) + \lambda k$。需注意若多个 $x$ 对应相同最优值，需通过**第二关键字**控制取舍方向。

### 应用与例题

| 题目 | 链接 | 说明 |
|------|------|------|
| P1525 | [关押罪犯](https://www.luogu.com.cn/problem/P1525) | 二分答案 + 二分图判定 |
| P3527 | [Meteors](https://loj.ac/p/2169) | 整体二分 + 树状数组 |
| P2617 | [Dynamic Rankings](https://www.luogu.com.cn/problem/P2617) | 带修区间第 $k$ 小 |
| P3834 | [可持久化线段树 2](https://www.luogu.com.cn/problem/P3834) | 静态区间第 $k$ 小 |

### 参考

- 与 [[CDQ分治]] 结合可离线求解区间前驱后继
- 均依赖 [[离散化]] 处理值域
- 更多练习题见 [[路径D-DSA算法刷题]]
