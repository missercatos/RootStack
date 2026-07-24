## AC 自动机（Aho-Corasick）

### 问题

给定多个模式串 $p_1, p_2, ..., p_k$（多模式串匹配），在文本串 $t$ 中找出所有模式串的出现位置。

### 概述

AC 自动机 = **Trie** 的结构 + **KMP** 的思想。它本质上是一个 Trie 上的自动机，每个结点增加一个 fail 指针，指向当前状态的最长后缀状态。

### 三步构建

#### 1. 建 Trie

将所有模式串插入一棵字典树，每个结点代表一个前缀状态。

#### 2. 构建 fail 指针（BFS）

!![](assets/images/ac_automaton/ac-automaton1.gif)
*GIF 演示：以模式串 i、he、his、she、hers 构建 fail 指针的过程*

对于结点 $u$，其父结点为 $p$，通过字符 $c$ 到达 $u$：

- 若 $\operatorname{trie}(\operatorname{fail}(p), c)$ 存在 → $\operatorname{fail}(u)$ 指向该结点
- 否则沿 $\operatorname{fail}(p)$ 继续跳，直到根结点
- 若仍不存在 → $\operatorname{fail}(u)$ 指向根

通过将不存在的转移指向 $\operatorname{trans}(\operatorname{fail}(u), c)$，构建"字典图"。

```cpp
const int N = 1e6 + 5;
int tr[N][26], fail[N], cnt[N], tot;

void build() {
    queue<int> q;
    for (int i = 0; i < 26; i++)
        if (tr[0][i]) q.push(tr[0][i]);
    while (!q.empty()) {
        int u = q.front(); q.pop();
        for (int i = 0; i < 26; i++) {
            if (tr[u][i]) {
                fail[tr[u][i]] = tr[fail[u]][i];
                q.push(tr[u][i]);
            } else {
                tr[u][i] = tr[fail[u]][i];
            }
        }
    }
}
```

#### 3. 多模式匹配

!![](assets/images/ac_automaton/ac-automaton4.png)
*构建完毕的 AC 自动机状态*

!![](assets/images/ac_automaton/ac-automaton2.gif)
*字典图构建（结点 5 遍历时的转移优化，蓝色/黑色边表示自动机新增的转移）*

沿着字典图遍历文本串，每次沿 fail 指针统计所有匹配的模式串。

```cpp
int query(const char t[]) {
    int u = 0, res = 0;
    for (int i = 0; t[i]; i++) {
        u = tr[u][t[i] - 'a'];
        for (int j = u; j && cnt[j] != -1; j = fail[j]) {
            res += cnt[j];
            cnt[j] = -1;  // 避免重复统计
        }
    }
    return res;
}
```

### fail 指针的关键性质

- fail 指针指向的结点对应字符串是当前结点的**最长后缀**
- 与 KMP 的 next 指针不同：next 指向最长 border（前后缀相等）；fail 指向的是所有模式串的前缀中匹配当前状态的最长后缀
- 匹配时，同一位上可匹配多个模式串（通过跳 fail 链获得）

### 效率优化

对于需要统计每个模式串出现次数的题目（洛谷 P5357），需要利用 **fail 树** 优化：

1. 构建 fail 树（将 fail 指针反向）
2. 在 fail 树上做子树求和，而非每次暴力跳 fail 链
3. 将匹配复杂度从 $O(|t| \times |\Sigma|)$ 降为 $O(|t| + \sum|p_i|)$

### 推荐练习题

| 平台 | 编号 | 名称 | 说明 |
|------|------|------|------|
| 洛谷 | P3808 | AC 自动机（简单版） | 统计出现次数 |
| 洛谷 | P3796 | AC 自动机（加强版） | 输出最多的模式串 |
| 洛谷 | P5357 | AC 自动机（二次加强版） | fail 树优化 |
| 洛谷 | P2292 | HDU 2222 | Keywords Search |

### 相关链接

- [[../../数据结构/L_字典树_Trie|Trie 字典树]]
- [[KMP|KMP 算法]]
- [[../../cpp教程/cpp基础教程/11_字符串基础|字符串基础]]

> 内容来源：经本地化改造的 OI-wiki AC 自动机章节。详细推导见 [OI-wiki](https://oi-wiki.org/string/ac-automaton/)。


## 多平台练习

| 洛谷 | [本题单](https://www.luogu.com.cn/) | 竞赛基础 |
| POJ (北大) | [PKU JudgeOnline](http://poj.org/) | 经典题目，适合巩固 |
| HDU (杭电) | [HDU OJ](https://acm.hdu.edu.cn/) | 暑期多校训练 |
| Codeforces | [Codeforces](https://codeforces.com/) | 国际竞赛，适合提升 |
