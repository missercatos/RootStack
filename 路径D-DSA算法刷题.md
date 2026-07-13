## 路径 D -- 纯 DSA 算法刷题路线

> 本教程体系可当作类百科全书使用，内容完善但体量庞大。若作为教程从头通读，效率不高。
> 建议按照本路线中的推荐阅读顺序，结合索引文件进行选择性学习。
> 同时推荐与 AI 进行问答互动学习 -- 在自认为掌握语法或数据结构之后，去 [洛谷](https://www.luogu.com.cn/) 刷题验证。
> 如遇到错误，不建议死磕，可用 AI 辅助纠正思路。

---

### 学习方式: 四步法

1. **通读概念** -- 理解数据结构的定义、性质、适用场景
2. **手写实现** -- 不看参考代码，用 C++ 手动实现核心操作
3. **STL 练习** -- 用标准库容器/算法做题，熟悉接口
4. **洛谷刷题** -- 按章节做推荐题目，每章 2-5 题

> 每章 1000+ 行，建议分 2-3 天完成。一天学概念+手写，一天 STL+案例，一天课后题+刷题。

---

## Phase 1 -- 入门基础：线形结构与排序 (建议 14 天)

### Step 1: [[数据结构/A_容器_Container|A 容器 Container]] (2 天)

**重点**: vector 扩容机制、迭代器原理、连续存储 vs 节点存储
**必须手写**: SimpleVector
**配合算法**: [[算法技巧/数组|数组基础]] / [[算法技巧/循环|循环]] / [[算法技巧/分支|分支]]

| 平台 | 题目编号 | 题目名 | 说明 |
|------|---------|--------|------|
| 洛谷 | P1047 | 校门外的树 | 数组模拟 |
| LeetCode | 27 | Remove Element | 数组原地操作 |

---

### Step 2: [[数据结构/D_链表_LinkedList|D 链表 LinkedList]] (2 天)

**重点**: 单向/双向链表全操作、STL list/forward_list
**必须手写**: 单向链表 (push/pop/reverse)、双向链表
**配合算法**: [[算法技巧/双指针|双指针]] (只读快慢指针部分)

| 平台 | 题目编号 | 题目名 | 说明 |
|------|---------|--------|------|
| 洛谷 | P1996 | 约瑟夫问题 | 链表经典 |
| LeetCode | 206 | Reverse Linked List | 反转链表 |
| LeetCode | 141 | Linked List Cycle | 快慢指针判环 |

---

### Step 3: [[数据结构/B_栈_Stack|B 栈 Stack]] (2 天)

**重点**: 数组栈/链表栈实现、函数调用栈原理、表达式求值
**必须手写**: ArrayStack、LinkedStack、MinStack

| 平台 | 题目编号 | 题目名 | 说明 |
|------|---------|--------|------|
| 洛谷 | P1449 | 后缀表达式 | 栈经典应用 |
| 洛谷 | P1739 | 表达式括号匹配 | 括号匹配 |
| LeetCode | 20 | Valid Parentheses | 括号匹配 |
| LeetCode | 155 | Min Stack | 最小栈 |

---

### Step 4: [[数据结构/F_队列_Queue|F 队列 Queue]] (2 天)

**重点**: 循环队列实现、STL queue/deque 用法、BFS 队列
**必须手写**: ArrayQueue (循环队列)、LinkedQueue
**配合算法**: [[算法技巧/搜索|搜索]] (BFS 部分)

| 平台 | 题目编号 | 题目名 | 说明 |
|------|---------|--------|------|
| 洛谷 | P1540 | 机器翻译 | 队列模拟 |
| 洛谷 | P1996 | 约瑟夫问题 | 队列版 |
| LeetCode | 225 | Implement Stack using Queues | 队列变体 |

---

### Step 5: [[数据结构/Q_排序_八大排序_Sorting|Q 八大排序 Sorting]] (3 天)

**学习顺序**: 冒泡 → 选择 → 插入 → 希尔 → 归并 → 快速 → (堆排序待学完堆后回看) → 基数
**必须手写**: 冒泡、插入、归并、快排
**配合算法**: [[算法技巧/递推递归|递推递归]] / [[算法技巧/暴力枚举|暴力枚举]] / [[算法技巧/排序|排序应用]]

| 平台 | 题目编号 | 题目名 | 说明 |
|------|---------|--------|------|
| 洛谷 | P1177 | 快速排序 | 排序模板题 |
| 洛谷 | P1059 | 明明的随机数 | 去重+排序 |
| 洛谷 | P1093 | 奖学金 | 多关键字排序 |
| LeetCode | 912 | Sort an Array | 排序综合 |
| LeetCode | 215 | Kth Largest Element | 快选/堆排 |

---

### Step 6: [[算法技巧/二分查找|二分查找]] (1 天)

**重点**: lower_bound/upper_bound 手写、二分查找变体
**前置**: 排序必须已完成

| 平台 | 题目编号 | 题目名 | 说明 |
|------|---------|--------|------|
| 洛谷 | P2249 | 查找 | 二分查找模板 |
| 洛谷 | P1102 | A-B 数对 | 二分+计数 |
| 洛谷 | P1678 | 烦恼的高考志愿 | 二分查找应用 |
| LeetCode | 704 | Binary Search | 基础二分 |
| LeetCode | 34 | Find First and Last Position | 二分变体 |

---

## Phase 2 -- 核心数据结构 (建议 14 天)

### Step 7: [[数据结构/G_哈希表_HashTable|G 哈希表 HashTable]] (2 天)

**重点**: 链地址法/开放地址法、STL unordered_map/unordered_set
**必须手写**: 基于链地址法的 HashMap (put/get/remove)
**配合算法**: [[算法技巧/下标技巧|下标技巧]]

| 平台 | 题目编号 | 题目名 | 说明 |
|------|---------|--------|------|
| 洛谷 | P3405 | Cities and States | hash + map 计数 |
| LeetCode | 1 | Two Sum | 哈希表经典 |
| LeetCode | 387 | First Unique Character | 字符计数 |

---

### Step 8: [[数据结构/C_堆_Heap|C 堆 Heap]] (2 天)

**重点**: siftUp/siftDown、建堆 O(n)、STL priority_queue
**必须手写**: MaxHeap (insert/extractMax/heapify)
**配合算法**: [[算法技巧/贪心|贪心]] (优先队列应用)
**回顾**: [[数据结构/Q_排序_八大排序_Sorting|堆排序部分]]

| 平台 | 题目编号 | 题目名 | 说明 |
|------|---------|--------|------|
| 洛谷 | P1090 | 合并果子 | 贪心+优先队列 |
| 洛谷 | P1168 | 中位数 | 对顶堆 |
| LeetCode | 215 | Kth Largest Element | 堆解法 |
| LeetCode | 347 | Top K Frequent Elements | 堆+哈希 |

---

### Step 9: [[数据结构/I_树_Tree_BST_AVL|I 树 / BST / AVL]] (3 天)

**重点**: 四种遍历 (递归+迭代)、BST 增删查、AVL 四种旋转
**必须手写**: BST (insert/search/delete)
**配合算法**: [[算法技巧/搜索|搜索]] / [[算法技巧/递推递归|递推递归]]

| 平台 | 题目编号 | 题目名 | 说明 |
|------|---------|--------|------|
| 洛谷 | P3369 | 普通平衡树 | BST/AVL 综合 |
| 洛谷 | P1364 | 医院设置 | 树的重心 |
| LeetCode | 94 | Binary Tree Inorder Traversal | 中序遍历 |
| LeetCode | 98 | Validate Binary Search Tree | BST 判定 |
| LeetCode | 104 | Maximum Depth of Binary Tree | 树高 |

---

### Step 10: [[数据结构/J_字典树_Trie|J 字典树 Trie]] (1 天)

**重点**: Trie 节点结构、插入/查找/前缀匹配
**配合算法**: [[算法技巧/字符串|字符串]]

| 平台 | 题目编号 | 题目名 | 说明 |
|------|---------|--------|------|
| 洛谷 | P2580 | 于是他错误的点名开始了 | Trie 模板 |
| LeetCode | 208 | Implement Trie | Trie 实现 |
| LeetCode | 14 | Longest Common Prefix | 前缀匹配 |

---

## Phase 3 -- 算法专题深化 (建议 14 天)

### Step 11: [[算法技巧/二分答案|二分答案]] (2 天)

**前置**: [[算法技巧/二分查找|二分查找]]

| 平台 | 题目编号 | 题目名 | 说明 |
|------|---------|--------|------|
| 洛谷 | P1182 | 数列分段 | 最小化最大值 |
| 洛谷 | P2678 | 跳石头 | 最大化最小值 |
| 洛谷 | P3853 | 路标设置 | 二分答案 |
| LeetCode | 875 | Koko Eating Bananas | 二分答案 |

---

### Step 12: [[算法技巧/前缀和|前缀和]] + [[算法技巧/差分|差分]] (2 天)

**重点**: O(1) 区间求和、O(1) 区间修改

| 平台 | 题目编号 | 题目名 | 说明 |
|------|---------|--------|------|
| 洛谷 | P8218 | 求区间和 | 前缀和模板 |
| 洛谷 | P3131 | 被7整除的子序列 | 前缀和+数学 |
| 洛谷 | P3397 | 地毯 | 二维差分模板 |
| 洛谷 | P4552 | IncDec Sequence | 差分 |
| LeetCode | 303 | Range Sum Query | 前缀和 |
| LeetCode | 560 | Subarray Sum Equals K | 前缀和+哈希 |

---

### Step 13: [[算法技巧/贪心|贪心]] (2 天)

**重点**: 局部最优 -> 全局最优思想、交换论证法证明
**前置**: [[数据结构/C_堆_Heap|堆]] / [[数据结构/Q_排序_八大排序_Sorting|排序]]

| 平台 | 题目编号 | 题目名 | 说明 |
|------|---------|--------|------|
| 洛谷 | P1223 | 排队接水 | 简单贪心 |
| 洛谷 | P1090 | 合并果子 | 贪心+优先队列 |
| 洛谷 | P2240 | 部分背包问题 | 贪心 vs DP |
| 洛谷 | P1106 | 删数问题 | 贪心 |
| LeetCode | 455 | Assign Cookies | 简单贪心 |
| LeetCode | 55 | Jump Game | 贪心 |

---

### Step 14: [[算法技巧/滑动窗口|滑动窗口]] + [[算法技巧/双指针|双指针]] (2 天)

**前置**: [[数据结构/F_队列_Queue|队列]] / [[算法技巧/前缀和|前缀和]]

| 平台 | 题目编号 | 题目名 | 说明 |
|------|---------|--------|------|
| 洛谷 | P1886 | 滑动窗口 | 单调队列模板 |
| 洛谷 | P1638 | 逛画展 | 不定长滑动窗口 |
| 洛谷 | P1102 | A-B 数对 | 双指针 |
| 洛谷 | P1147 | 连续自然数和 | 双指针 |
| LeetCode | 3 | Longest Substring Without Repeating | 滑动窗口 |
| LeetCode | 209 | Minimum Size Subarray Sum | 滑动窗口 |
| LeetCode | 11 | Container With Most Water | 双指针 |

---

### Step 15: [[算法技巧/递推递归|递推与递归]] (2 天)

**重点**: 递推 vs 递归、记忆化搜索、斐波那契/卡特兰数
**前置**: [[数据结构/B_栈_Stack|栈]] (递归=系统栈) / [[数据结构/Q_排序_八大排序_Sorting|排序]]

| 平台 | 题目编号 | 题目名 | 说明 |
|------|---------|--------|------|
| 洛谷 | P1028 | 数的计算 | 递推 |
| 洛谷 | P1255 | 数楼梯 | 斐波那契/高精度 |
| 洛谷 | P1044 | 栈 | 卡特兰数 |
| 洛谷 | P1164 | 小A点菜 | 01背包方案数 |
| LeetCode | 509 | Fibonacci Number | 递推递归 |
| LeetCode | 70 | Climbing Stairs | 简单递推 |

---

### Step 16: [[算法技巧/搜索|搜索 DFS/BFS]] (2 天)

**重点**: DFS 回溯框架、BFS 层序遍历框架、状态恢复
**前置**: [[数据结构/B_栈_Stack|栈]] / [[数据结构/F_队列_Queue|队列]] / [[数据结构/I_树_Tree_BST_AVL|树]]

| 平台 | 题目编号 | 题目名 | 说明 |
|------|---------|--------|------|
| 洛谷 | P1605 | 迷宫 | DFS 模板 |
| 洛谷 | P1443 | 马的遍历 | BFS 模板 |
| 洛谷 | P2404 | 自然数拆分 | 回溯 DFS |
| LeetCode | 200 | Number of Islands | DFS/BFS |
| LeetCode | 46 | Permutations | 回溯 |

---

### Step 17: [[算法技巧/动态规划|动态规划]] (3-4 天)

**重点**: 状态定义、状态转移方程、记忆化搜索 vs 递推、0/1背包、完全背包、LIS、LCS
**前置**: [[算法技巧/递推递归|递推递归]] / [[数据结构/A_容器_Container|容器]]

| 平台 | 题目编号 | 题目名 | 说明 |
|------|---------|--------|------|
| 洛谷 | P1048 | 采药 | 0/1 背包模板 |
| 洛谷 | P1049 | 装箱问题 | 0/1 背包 |
| 洛谷 | P1115 | 最大子段和 | 线性 DP |
| 洛谷 | P1616 | 疯狂的采药 | 完全背包 |
| 洛谷 | P1439 | LCS | 最长公共子序列 |
| LeetCode | 416 | Partition Equal Subset Sum | 0/1 背包 |
| LeetCode | 322 | Coin Change | 完全背包 |
| LeetCode | 300 | Longest Increasing Subsequence | LIS |
| LeetCode | 1143 | Longest Common Subsequence | LCS |
| LeetCode | 53 | Maximum Subarray | 最大子数组 |
| LeetCode | 198 | House Robber | 线性 DP |

---

## Phase 4 -- 图论 (建议 10 天)

### Step 18: [[数据结构/H_图_Graph|H 图 Graph]] (3 天)

**重点**: 邻接矩阵/邻接表存储、DFS/BFS 遍历、Dijkstra
**配合算法**: [[算法技巧/图|图论算法]]

| 平台 | 题目编号 | 题目名 | 说明 |
|------|---------|--------|------|
| 洛谷 | P3371 | 单源最短路径 | Dijkstra (弱化版) |
| 洛谷 | P4779 | 堆优化 Dijkstra | Dijkstra 模板 |
| 洛谷 | P3366 | 最小生成树 | Prim/Kruskal |
| LeetCode | 743 | Network Delay Time | Dijkstra |
| LeetCode | 207 | Course Schedule | 拓扑排序 |

---

### Step 19: [[数据结构/K_并查集_UnionFind|K 并查集 UnionFind]] (2 天)

**重点**: 路径压缩 + 按秩合并、Kruskal 算法、连通分量
**配合算法**: [[算法技巧/连通性|连通性]]

| 平台 | 题目编号 | 题目名 | 说明 |
|------|---------|--------|------|
| 洛谷 | P3367 | 并查集 | 模板题 |
| 洛谷 | P1551 | 亲戚 | 并查集应用 |
| LeetCode | 547 | Number of Provinces | 并查集 |
| LeetCode | 684 | Redundant Connection | 并查集判环 |

---

### Step 20: [[数据结构/P_图的高级算法_AdvancedGraph|P 图高级算法]] (3 天)

**重点**: 拓扑排序、Floyd、Bellman-Ford 判负环、网络流入门

| 平台 | 题目编号 | 题目名 | 说明 |
|------|---------|--------|------|
| 洛谷 | P1113 | 杂务 | 拓扑排序 |
| 洛谷 | P3385 | 负环 | Bellman-Ford / SPFA |
| LeetCode | 210 | Course Schedule II | 拓扑排序 |
| LeetCode | 787 | Cheapest Flights | Bellman-Ford / DP |

---

## Phase 5 -- 进阶数据结构 (选学)

### Step 21: [[数据结构/L_线段树_SegmentTree|L 线段树 SegmentTree]]

**前置**: 数组 + 递归
**配合算法**: [[算法技巧/优化|优化]]

| 平台 | 题目编号 | 题目名 | 说明 |
|------|---------|--------|------|
| 洛谷 | P3372 | 线段树 1 | 区间加+区间和 |
| 洛谷 | P3373 | 线段树 2 | 区间加+区间乘 |
| LeetCode | 307 | Range Sum Query - Mutable | 线段树/树状数组 |

---

### Step 22: [[数据结构/M_树状数组_BIT|M 树状数组 BIT]]

**重点**: lowbit、单点更新+前缀和查询（比线段树更轻量）

| 平台 | 题目编号 | 题目名 | 说明 |
|------|---------|--------|------|
| 洛谷 | P3374 | 树状数组 1 | 单点加+区间和 |
| 洛谷 | P3368 | 树状数组 2 | 区间加+单点查 |
| LeetCode | 307 | Range Sum Query - Mutable | BIT 写法 |

---

### Step 23: [[数据结构/E_红黑树_RedBlackTree|E 红黑树 RedBlackTree]]

**前置**: BST / AVL
(主要理解原理，不要求手写——STL map/set 的底层实现即为红黑树)

---

### Step 24: [[数据结构/O_B树_BTree|O B树 B-Tree]]

**前置**: 树 + 文件系统概念
(磁盘友好型多路搜索树，数据库索引核心)

---

### Step 25: [[数据结构/N_跳表_SkipList|N 跳表 SkipList]]

**前置**: 链表 + 哈希
(概率型快速查找结构)

---

## 算法技巧补充速查

以下文件在整个 DSA 学习过程中按需查阅，已在上方各 Step 中标注对应关系：

- [[算法技巧/顺序|顺序结构]] -- 基础
- [[算法技巧/分支|分支]] -- 基础
- [[算法技巧/循环|循环]] -- 基础
- [[算法技巧/数组|数组]] -- Phase 1
- [[算法技巧/字符串|字符串]] -- Phase 2-3
- [[算法技巧/函数结构体|函数与结构体]] -- 基础
- [[算法技巧/模拟高精度|模拟与高精度]] -- 任何时候
- [[算法技巧/排序|排序应用]] -- Phase 1 Step 5
- [[算法技巧/暴力枚举|暴力枚举]] -- Phase 1 Step 5
- [[算法技巧/前缀和|前缀和]] -- Phase 3 Step 12
- [[算法技巧/差分|差分]] -- Phase 3 Step 12
- [[算法技巧/双指针|双指针]] -- Phase 1 Step 2 / Phase 3 Step 14
- [[算法技巧/滑动窗口|滑动窗口]] -- Phase 3 Step 14
- [[算法技巧/下标技巧|下标技巧]] -- Phase 2
- [[算法技巧/贪心|贪心]] -- Phase 3 Step 13
- [[算法技巧/二分查找|二分查找]] -- Phase 1 Step 6
- [[算法技巧/二分答案|二分答案]] -- Phase 3 Step 11
- [[算法技巧/递推递归|递推递归]] -- Phase 3 Step 15
- [[算法技巧/搜索|搜索]] -- Phase 3 Step 16
- [[算法技巧/动态规划|动态规划]] -- Phase 3 Step 17
- [[算法技巧/图|图论算法]] -- Phase 4 Step 18
- [[算法技巧/连通性|连通性]] -- Phase 4 Step 19
- [[算法技巧/概率|概率与期望]] -- 选学
- [[算法技巧/优化|优化]] -- Phase 5

---

### 推荐阅读物

- Introduction to Algorithms (CLRS)
- Algorithms (Robert Sedgewick)
- 算法导论 (中文版)
- 算法竞赛入门经典 (刘汝佳)
- 挑战程序设计竞赛

### 语言官方文档

- cppreference (STL reference): https://en.cppreference.com/
- 洛谷 (刷题平台): https://www.luogu.com.cn/
- LeetCode: https://leetcode.com/
- AtCoder: https://atcoder.jp/
- Codeforces: https://codeforces.com/
