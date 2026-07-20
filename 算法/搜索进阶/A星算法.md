## A\* 算法 (A-star)

### 核心思想

A\* = 优先队列 BFS + 启发式函数。估值函数 $f(x) = g(x) + h(x)$，其中 $g(x)$ 是起点到 $x$ 的实际代价，$h(x)$ 是 $x$ 到终点的估计代价。

### 可采纳性与一致性

- **可采纳 (admissible)**：$0 \le h(x) \le h^*(x)$（$h^*$ 为真实距离），保证找到最优解。
- **一致 (consistent)**：$h(x) \le h(y) + d(x, y)$（三角不等式），保证结点不重复入队。

$h$ 越接近 $h^*$，效率越高。若 $h \equiv 0$ 退化为 Dijkstra；若 $h \equiv h^*$ 则严格沿最短路前进。

### 实现（八数码 P1379）

```cpp
#include <algorithm>
#include <cstring>
#include <iostream>
#include <queue>
#include <set>
using namespace std;
constexpr int dx[4] = {1, -1, 0, 0}, dy[4] = {0, 0, 1, -1};
int fx, fy; char ch;

struct matrix {
  int a[5][5];
  bool operator<(matrix x) const {
    for (int i = 1; i <= 3; i++)
      for (int j = 1; j <= 3; j++)
        if (a[i][j] != x.a[i][j]) return a[i][j] < x.a[i][j];
    return false;
  }
} f, st;

int h(matrix a) { // 不在位的棋子数（可采纳）
  int ret = 0;
  for (int i = 1; i <= 3; i++)
    for (int j = 1; j <= 3; j++)
      if (a.a[i][j] != st.a[i][j] && a.a[i][j]) ret++;
  return ret;
}

struct node {
  matrix a; int t;
  bool operator<(node x) const { return t + h(a) > x.t + h(x.a); }
} x;

priority_queue<node> q;
set<matrix> s;

int main() {
  // 目标状态
  int tar[3][3] = {{1,2,3},{8,0,4},{7,6,5}};
  for (int i = 1; i <= 3; i++)
    for (int j = 1; j <= 3; j++) st.a[i][j] = tar[i-1][j-1];
  for (int i = 1; i <= 3; i++)
    for (int j = 1; j <= 3; j++) cin >> ch, f.a[i][j] = ch - '0';
  s.insert(f); q.push({f, 0});
  while (!q.empty()) {
    x = q.top(); q.pop();
    if (!h(x.a)) { cout << x.t << '\n'; return 0; }
    for (int i = 1; i <= 3; i++)
      for (int j = 1; j <= 3; j++)
        if (!x.a.a[i][j]) fx = i, fy = j;
    for (int i = 0; i < 4; i++) {
      int xx = fx + dx[i], yy = fy + dy[i];
      if (xx < 1 || xx > 3 || yy < 1 || yy > 3) continue;
      swap(x.a.a[fx][fy], x.a.a[xx][yy]);
      if (!s.count(x.a)) s.insert(x.a), q.push({x.a, x.t + 1});
      swap(x.a.a[fx][fy], x.a.a[xx][yy]);
    }
  }
  return 0;
}
```

### 练习

| 题目 | 说明 |
|------|------|
| [P1379 八数码](https://www.luogu.com.cn/problem/P1379) | A\* 经典，$h=$ 曼哈顿距离或不在位数 |
| [LeetCode 752 Open the Lock](https://leetcode.com/problems/open-the-lock/) | BFS + 启发式 |

### 相关链接

[[../../路径D-DSA算法刷题]] | [[双向搜索]] | [[IDA星算法]]

> 来源：[OI-wiki A\* 算法](https://oi-wiki.org/search/astar/)


## 多平台练习

| 洛谷 | [本题单](https://www.luogu.com.cn/) | 竞赛基础 |
| POJ (北大) | [PKU JudgeOnline](http://poj.org/) | 经典题目，适合巩固 |
| HDU (杭电) | [HDU OJ](https://acm.hdu.edu.cn/) | 暑期多校训练 |
| Codeforces | [Codeforces](https://codeforces.com/) | 国际竞赛，适合提升 |
