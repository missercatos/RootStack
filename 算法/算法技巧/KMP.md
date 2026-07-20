## KMP 算法

### 问题

给定文本串 $t$ 和模式串 $p$，在 $t$ 中查找 $p$ 的所有出现位置。时间复杂度 $O(n+m)$。

### 前缀函数 $\pi$

对于字符串 $s$，前缀函数 $\pi[i]$ 定义为子串 $s[0..i]$ 最长的相等真前缀与真后缀的长度。

| $s$ | $\pi$ | 说明 |
|-----|-------|------|
| `a` | [0] | 无真前后缀 |
| `ab` | [0,0] | |
| `abc` | [0,0,0] | |
| `abca` | [0,0,0,1] | `a` = `a` |
| `abcab` | [0,0,0,1,2] | `ab` = `ab` |
| `abcabc` | [0,0,0,1,2,3] | `abc` = `abc` |

### 高效计算 $\pi$

```cpp
vector<int> pi(const string &s) {
    int n = s.size();
    vector<int> p(n);
    for (int i = 1; i < n; i++) {
        int j = p[i-1];
        while (j > 0 && s[i] != s[j]) j = p[j-1];
        if (s[i] == s[j]) j++;
        p[i] = j;
    }
    return p;
}
```

**核心思想**: 利用已计算的 $\pi$ 值回退，而非暴力逐字符重试。每次回退 $j = \pi[j-1]$ 保证了线性复杂度。

### KMP 匹配

将模式串 $p$ 与文本串 $t$ 拼接为 $s = p + '#' + t$，对 $s$ 计算前缀函数。当 $\pi[i] = |p|$ 时，说明在 $t$ 中找到了一个完整匹配。

```cpp
vector<int> kmp(const string &t, const string &p) {
    string s = p + '#' + t;
    auto pi = compute_pi(s);
    vector<int> matches;
    for (int i = p.size() + 1; i < s.size(); i++)
        if (pi[i] == p.size())
            matches.push_back(i - 2 * p.size());
    return matches;
}
```

### 前缀函数递推

前缀函数的递推过程如下图所示，展示了如何利用已计算的 $\pi$ 值进行高效计算：

!![](assets/images/string/prefix_str_1.svg)
!![](assets/images/string/prefix_str_2.svg)
!![](assets/images/string/prefix_str_3.svg)

### 匹配过程示意

!![](assets/images/string/strstr_kmp_indices.svg)

**前缀函数匹配过程**:
```
文本串:  a  b  a  b  a  b  a  b  c
模式串:  a  b  a  b  c
         √  √  √  √  ×  → 回退到 π[3]=2
               a  b  a  b  c
               √  √  √  √  √  → 匹配成功
```

### 应用

- 字符串匹配
- 求字符串最小周期：$period = n - \pi[n-1]$（当 $n \bmod period = 0$ 时）
- 求字符串的 border
- 统计每个前缀在字符串中的出现次数

### 推荐练习题

| 平台 | 编号 | 名称 | 说明 |
|------|------|------|------|
| 洛谷 | P3375 | 【模板】KMP | 基础模板 |
| 洛谷 | P2375 | 动物园 | KMP 变体，统计不重叠 border |
| 洛谷 | P3435 | OKR-Periods of Words | 周期应用 |
| LeetCode | 28 | Find the Index of First Occurrence | 实现 strStr() |
| LeetCode | 214 | Shortest Palindrome | 前缀函数应用 |

### 相关链接

- [[../../cpp教程/cpp基础教程/11_字符串基础|字符串基础]]
- [[字符串哈希|字符串哈希]]
- [[AC自动机|AC 自动机]]（KMP 的多模式串扩展）

> 内容来源：经本地化改造的 OI-wiki KMP 章节。详细推导见 [OI-wiki](https://oi-wiki.org/string/kmp/)。


## 多平台练习

| 洛谷 | [本题单](https://www.luogu.com.cn/) | 竞赛基础 |
| POJ (北大) | [PKU JudgeOnline](http://poj.org/) | 经典题目，适合巩固 |
| HDU (杭电) | [HDU OJ](https://acm.hdu.edu.cn/) | 暑期多校训练 |
| Codeforces | [Codeforces](https://codeforces.com/) | 国际竞赛，适合提升 |
