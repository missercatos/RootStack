## IDA\* 算法 (Iterative Deepening A\*)

### 核心思想

IDA\* = 迭代加深搜索 + A\* 剪枝。每次 DFS 限制路径成本 $f(x) = g(x) + h(x) \le C$，超过阈值则剪枝；阈值逐轮递增。

### 伪代码

```
阈值 C = h(s)
while (true)
 t = DFS(s, 0, C)
 if t == FOUND return
 if t == ∞ return NOT_FOUND
 C = t

DFS(node, g, C):
 f = g + h(node)
 if f > C return f
 if node 是目标 return FOUND
 min = ∞
 for child in node.children:
 if child not in path:
 t = DFS(child, g + cost(node,child), C)
 if t == FOUND return FOUND
 min = min(min, t)
 return min
```

### A\* 与 IDA\* 对比

| A\* | IDA\* |
|-----|-------|
| 优先队列，需判重 | DFS，无需判重、无需排序 |
| 空间 $O(b^d)$ | 空间 $O(d)$ |
| 结点不重复扩展 | 阈值递增导致重复搜索 |
| 适合搜索空间大、内存充足 | 适合内存紧张、深度剪枝强 |

### 实现（埃及分数）

```cpp
#include <cmath>
#include <iostream>
#include <numeric>
#include <vector>

int max_e = 1e7;
std::vector<int> ans, cur;

long long gcd(long long x, long long y) { return y ? gcd(y, x % y) : x; }

bool dfs(int d, long long a, long long b, int e) {
 long long g = gcd(a, b); a /= g; b /= g;
 if (d == 2) {
 // 最后两个分数用二次方程求解
 for (int k = 4 * b / (a * a) + 1;; ++k) {
 long long delta = a * a * k * k - 4 * b * k, t = sqrt(delta + 0.5l);
 long long x = (a * k - t) / 2, y = (a * k + t) / 2;
 if (y > max_e) break;
 if (!t || t * t != delta || (a * k - t) % 2) continue;
 ans = cur; ans.push_back(x); ans.push_back(y);
 max_e = y - 1; return true;
 }
 } else {
 int e1 = std::max(e + 1, int((b + a - 1) / a));
 for (; e1 <= d * b / a && e1 <= max_e; e1++) {
 cur.push_back(e1);
 if (dfs(d - 1, a * e1 - b, b * e1, e1)) return true;
 cur.pop_back();
 }
 }
 return false;
}

int solve(int a, int b) {
 if (b % a == 0) { ans.push_back(b / a); return 1; }
 for (int lim = 2; lim <= 100; lim++)
 if (dfs(lim, a, b, 1)) return lim;
 return -1;
}
```

### 练习

| 题目 | 说明 |
|------|------|
| [P1379 八数码](https://www.luogu.com.cn/problem/P1379) | 可同时用 A\* / IDA\* |
| [POJ 2286 The Rotation Game](https://vjudge.net/problem/POJ-2286) | IDA\* 经典 |

### 相关链接

[[../../路径D-DSA算法刷题]] | [[双向搜索]] | [[A星算法]]

> 来源：[OI-wiki IDA\* 算法](https://oi-wiki.org/search/idastar/)


## 多平台练习

| 洛谷 | [本题单](https://www.luogu.com.cn/) | 竞赛基础 |
| POJ (北大) | [PKU JudgeOnline](http://poj.org/) | 经典题目，适合巩固 |
| HDU (杭电) | [HDU OJ](https://acm.hdu.edu.cn/) | 暑期多校训练 |
| Codeforces | [Codeforces](https://codeforces.com/) | 国际竞赛，适合提升 |
