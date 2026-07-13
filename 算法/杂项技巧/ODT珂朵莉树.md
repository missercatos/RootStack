## ODT 珂朵莉树

### 概述

珂朵莉树（Chtholly Tree / Old Driver Tree）并非特定数据结构，而是一种用平衡树（`std::set`）维护**颜色段均摊**的技巧。将值相同的连续区间合并为结点，适合含**区间赋值**操作的问题。起源 [[CF896C]]。

### 结点与存储

```cpp
struct Node {
  int l, r;
  mutable int v;
  Node(int il, int ir, int iv) : l(il), r(ir), v(iv) {}
  bool operator<(const Node &o) const { return l < o.l; }
};
set<Node> odt;
```

`mutable` 使 `v` 可在 const 迭代器中修改，避免删除重插入。

### split 操作

将包含 $x$ 的区间 $[l,r]$ 分裂为 $[l,x)$ 和 $[x,r]$，返回后者迭代器。

```cpp
auto split(int x) {
  auto it = odt.lower_bound(Node(x, 0, 0));
  if (it != odt.end() && it->l == x) return it;
  --it;
  int l = it->l, r = it->r, v = it->v;
  odt.erase(it);
  odt.insert(Node(l, x - 1, v));
  return odt.insert(Node(x, r, v)).first;
}
```

### assign 操作

区间染色：先调 `split(r+1)` 再调 `split(l)`，删除中间所有段，插入新区间。

```cpp
void assign(int l, int r, int v) {
  auto itr = split(r + 1), itl = split(l);
  odt.erase(itl, itr);
  odt.insert(Node(l, r, v));
}
```

### 复杂度分析

- **数据随机时**：$O(n\log\log n)$（set 实现），$O(n\log n)$（链表实现）
- **有 assign + 无遍历**：均摊 $O(m\log n)$
- **有遍历无 assign**：可被卡到 $O(n^2)$，依赖数据随机

### 例题

| 题目 | 链接 | 说明 |
|------|------|------|
| CF896C | [Willem, Chtholly and Seniorious](https://codeforces.com/problemset/problem/896/C) | 起源题，区间加/赋值/排序 |
| P2787 | [语文 1](https://www.luogu.com.cn/problem/P2787) | 区间排序 + 字符统计 |
| P1840 | [Color the Axis](https://www.luogu.com.cn/problem/P1840) | 区间染色模板 |
| P4979 | [矿洞：坍塌](https://www.luogu.com.cn/problem/P4979) | 区间赋值 + 区间查询 |

### 参考

- 与 [[CDQ分治]] 结合可维护含区间赋值的数颜色问题
- 见 [[路径D-DSA算法刷题]] 获取更多练习题
