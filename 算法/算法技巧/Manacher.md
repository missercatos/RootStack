## Manacher 算法（回文串）

### 问题

求字符串 $s$ 的最长回文子串，时间复杂度 $O(n)$。

### 核心思想

利用回文的对称性，避免重复计算。维护当前已知的最右回文边界 $r$ 及其中心 $c$。

![[assets/images/string/manacher1.png]]
*上图展示了以某个中心扩展回文的过程*

![[assets/images/string/manacher2.png]]
*利用对称性快速确定回文半径*

![[assets/images/string/manacher3.png]]
*当对称点半径触及右边界时，仍需中心扩展*

### 算法步骤

1. **字符串预处理**: 在字符间插入分隔符 `#`，将奇偶长度的回文统一处理

   ```
   原始:    a  b  a  b  c
   预处理:  # a # b # a # b # c #
   ```

   预处理后，所有回文串的长度都是奇数，$d[i]$ 表示以 $i$ 为中心的回文半径。

2. **递推计算 $d[i]$**:

   - 如果 $i$ 在已知最右回文边界 $r$ 内，利用对称点 $i' = 2c - i$ 的 $d[i']$ 初始化 $d[i]$
   - 否则 $d[i] = 1$
   - 向两边扩展，直到不匹配
   - 如果 $i + d[i] > r$，更新 $c = i, r = i + d[i]$

```cpp
vector<int> manacher(const string &s) {
    // 预处理
    string t = "#";
    for (char c : s) {
        t += c; t += '#';
    }
    int n = t.size();
    vector<int> d(n);
    int c = 0, r = 0;
    for (int i = 0; i < n; i++) {
        int mir = 2 * c - i;  // 对称点
        if (i < r)
            d[i] = min(d[mir], r - i);
        while (i - d[i] >= 0 && i + d[i] < n
               && t[i - d[i]] == t[i + d[i]])
            d[i]++;
        if (i + d[i] > r) {
            c = i;
            r = i + d[i];
        }
    }
    return d;
}
```

$d[i]$ 表示扩展半径（包含中心自身），原始字符串中的回文长度为 $d[i] - 1$。

### 重要性质

- $d[i] - 1$ 是以 $i$ 为中心的最长回文子串长度（在原始字符串中）
- 算法过程中每个字符最多被扩展一次，因此时间复杂度为 $O(n)$

### 推荐练习题

| 平台 | 编号 | 名称 | 说明 |
|------|------|------|------|
| 洛谷 | P3805 | 【模板】manacher | 最长回文子串 |
| 洛谷 | P1659 | 拉拉队排练 | 回文长度计数 |
| 洛谷 | P4555 | 最长双回文串 | 回文组合 |
| LeetCode | 5 | Longest Palindromic Substring | 最长回文子串 |
| LeetCode | 647 | Palindromic Substrings | 回文子串计数 |

### 相关链接

- [[算法/算法技巧/字符串|字符串基础]]
- [[算法/算法技巧/字符串哈希|字符串哈希]]（回文串的哈希解法）
- [[算法/算法技巧/KMP|KMP 算法]]

> 内容来源：经本地化改造的 OI-wiki Manacher 章节。详细推导见 [OI-wiki](https://oi-wiki.org/string/manacher/)。
