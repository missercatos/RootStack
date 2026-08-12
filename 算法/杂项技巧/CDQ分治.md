## CDQ 分治

### 概述

CDQ 分治由陈丹琦（IOI2008 金牌）提出，是一种通过**分治降维**的离线思想，核心是**将点对关系按中点划分，分别处理跨区间的贡献**。常用于解决偏序问题、优化 DP、将动态问题静态化。

!![](assets/images/misc/cdq-divide.svg)
*CDQ 分治处理三维偏序的流程：按第一维排序，左右分治处理第二维，归并时用 BIT 维护第三维*

### 三类应用

1. **解决点对有关问题** — 如三维偏序
2. **优化 1D/1D DP** — 如二维 LIS
3. **动态转静态** — 如带修改的矩形加/求和

### 三维偏序（P3810）

按 $a$ 排序 → CDQ 分治按 $b$ 归并 → 树状数组维护 $c$。

```cpp
void cdq(int l, int r) {
 if (l == r) return;
 int mid = (l + r) >> 1;
 cdq(l, mid); cdq(mid + 1, r);
 int i = l, j = mid + 1, k = l;
 while (i <= mid && j <= r) {
 if (b[i] <= b[j]) add(c[i], 1), tmp[k++] = i++;
 else ans[tmp[k++] = j++] += query(c[j]);
 }
 while (i <= mid) add(c[i], 1), tmp[k++] = i++;
 while (j <= r) ans[tmp[k++] = j++] += query(c[j]);
 for (i = l; i <= mid; ++i) add(c[i], -1);
 for (i = l; i <= r; ++i) a[i] = tmp[i];
}
```

### 动态逆序对（P3157）

将删除操作倒序看作插入，用 CDQ 分治统计三维偏序：时间 $t$、位置 $pos$、值 $val$。对每个插入点，统计已插入的、位置在其两侧且值构成逆序的点。

### 表格

| 题目 | 链接 | 说明 |
|------|------|------|
| P3810 | [三维偏序](https://www.luogu.com.cn/problem/P3810) | 模板题，$O(n\log^2 n)$ |
| P3157 | [动态逆序对](https://www.luogu.com.cn/problem/P3157) | 删除操作倒序 + CDQ |
| P2487 | [拦截导弹](https://www.luogu.com.cn/problem/P2487) | CDQ 优化 DP + 概率 |

### 复杂度

$$
T(n) = 2T(n/2) + O(n\log n) = O(n\log^2 n)
$$

### 注意事项

- CDQ 分治处理跨中点贡献时，务必保证左右区间分别按 $b$ 排序后再用双指针扫描。
- 优化 DP 时，转移处理必须放在 `solve(l,mid)` 和 `solve(mid+1,r)` **之间**（中序遍历），以确保 $dp$ 值按序计算。
- 树状数组每次清空时采用「时间戳」或记录修改位置回撤，避免 $O(n)$ 级清空。

### 相关习题

| 题目 | 链接 | 类型 |
|------|------|------|
| P3810 | [三维偏序](https://www.luogu.com.cn/problem/P3810) | 点对计数，$O(n\log^2 n)$ |
| P3157 | [动态逆序对](https://www.luogu.com.cn/problem/P3157) | 正难则反 + CDQ |
| P2487 | [拦截导弹](https://www.luogu.com.cn/problem/P2487) | CDQ 优化 DP |
| P4690 | [镜中的昆虫](https://www.luogu.com.cn/problem/P4690) | CDQ + ODT 区间数颜色 |

### 参考

- 与 [[莫队算法]] 同为重要离线算法
- 结合 [[整体二分与WQS二分]] 可解决更复杂问题
- 练习列表见 [[../../路径D-DSA算法刷题]]


## 多平台练习

| 洛谷 | [本题单](https://www.luogu.com.cn/) | 竞赛基础 |
| POJ (北大) | [PKU JudgeOnline](http://poj.org/) | 经典题目，适合巩固 |
| HDU (杭电) | [HDU OJ](https://acm.hdu.edu.cn/) | 暑期多校训练 |
| Codeforces | [Codeforces](https://codeforces.com/) | 国际竞赛，适合提升 |
