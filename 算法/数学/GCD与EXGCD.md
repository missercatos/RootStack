## GCD 与 EXGCD

### 欧几里得算法

核心等式：$\gcd(a,b) = \gcd(b, a \bmod b)$，当 $b=0$ 时返回 $a$。

```cpp
int gcd(int a, int b) {
 return b == 0 ? a : gcd(b, a % b);
}
```

### 扩展欧几里得（EXGCD）

求 $ax + by = \gcd(a, b)$ 的一组整数解。

```cpp
int exgcd(int a, int b, int &x, int &y) {
 if (!b) { x = 1; y = 0; return a; }
 int d = exgcd(b, a % b, y, x);
 y -= a / b * x;
 return d;
}
```

解满足 $|x| \le b,\ |y| \le a$。

### 模逆元

当 $\gcd(a, m) = 1$ 时，$a$ 在模 $m$ 下存在逆元。

**方法一：费马小定理**（$m$ 为素数）：$a^{-1} \equiv a^{p-2} \pmod p$。

**方法二：EXGCD**：求解 $ax \equiv 1 \pmod m$。

**方法三：线性递推**（$p$ 为素数，预处理 $1 \sim n$ 逆元）：

```cpp
vector<int> inv(n + 1);
inv[1] = 1;
for (int i = 2; i <= n; ++i)
 inv[i] = (long long)(p - p / i) * inv[p % i] % p;
```

**方法四：批量逆元**（$O(n + \log m)$）：预处理前缀积 $S_i$，求 $S_n^{-1}$ 后回推。

### 练习题目

| 题目 | 描述 |
|------|------|
| [P1082 【模板】同余方程](https://www.luogu.com.cn/problem/P1082) | EXGCD 求 $ax \equiv 1$ |
| [P3811 【模板】模意义下的乘法逆元](https://www.luogu.com.cn/problem/P3811) | 线性求逆元 |
| [P5431 【模板】乘法逆元 2](https://www.luogu.com.cn/problem/P5431) | 批量逆元 |

### 相关链接

- [[快速幂与模运算]]
- [[素数筛]]
- [[中国剩余定理]]
- [[../../路径D-DSA算法刷题]]

> 来源：OI-wiki [gcd.md](https://oi-wiki.org/math/number-theory/gcd/) & [inverse.md](https://oi-wiki.org/math/number-theory/inverse/)


## 多平台练习

| 洛谷 | [本题单](https://www.luogu.com.cn/) | 竞赛基础 |
| POJ (北大) | [PKU JudgeOnline](http://poj.org/) | 经典题目，适合巩固 |
| HDU (杭电) | [HDU OJ](https://acm.hdu.edu.cn/) | 暑期多校训练 |
| Codeforces | [Codeforces](https://codeforces.com/) | 国际竞赛，适合提升 |
