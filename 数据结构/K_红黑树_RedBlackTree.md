

建议先阅读: [[J_树_Tree_BST_AVL|树 BST AVL]]

---

## 原理

红黑树（Red-Black Tree）是一种自平衡二叉查找树，每个节点额外存储一个颜色位（红色或黑色），通过颜色约束保证树近似平衡。它是 C++ 标准库中 `set`、`map`、`multiset`、`multimap` 的底层实现。

### 五个性质

1. 每个节点是红色或黑色
2. 根节点是黑色
3. 每个叶子（NIL 空节点）是黑色
4. 红色节点的两个子节点必须是黑色（不能有连续的红色）
5. 从任意节点到其每个叶子的所有路径包含相同数目的黑色节点

```mermaid
graph TD
 subgraph 红黑树示例（B=黑, R=红）
 N11["11 B"] --> N21["2 R"]
 N11 --> N31["14 B"]
 N21 --> N41["1 B"]
 N21 --> N51["7 B"]
 N31 --> N61["15 R"]
 N31 --> N71["NIL"]
 N41 --> N81["NIL"]
 N41 --> N91["NIL"]
 N51 --> N101["5 R"]
 N51 --> N111["8 R"]
 N61 --> N121["NIL"]
 N61 --> N131["NIL"]
 end
 style N11 fill:#333,color:#fff
 style N31 fill:#333,color:#fff
 style N41 fill:#333,color:#fff
 style N51 fill:#333,color:#fff
 style N21 fill:#f00,color:#fff
 style N61 fill:#f00,color:#fff
 style N101 fill:#f00,color:#fff
 style N111 fill:#f00,color:#fff
 style N71 fill:#999,color:#fff
 style N81 fill:#999,color:#fff
 style N91 fill:#999,color:#fff
 style N121 fill:#999,color:#fff
 style N131 fill:#999,color:#fff
```

### 复杂度

| 操作 | 平均 | 最坏 | 说明 |
|------|------|------|------|
| 查找 | O(log n) | O(log n) | 高度不超过 2*log(n+1) |
| 插入 | O(log n) | O(log n) | BST 插入 + 最多 2 次旋转 |
| 删除 | O(log n) | O(log n) | BST 删除 + 最多 3 次旋转 |
| 空间 | O(n) | O(n) | 每个节点额外 1 bit |

### 红黑树高度上界证明

**定理**：一棵有 $n$ 个内部节点的红黑树，其高度满足：

$$
h \leq 2 \cdot \log_2(n + 1)
$$

**证明**：
1. 将红黑树中所有红色节点"合并"到其父节点（黑色），得到一棵 2-3-4 树
2. 合并后所有叶子在同一层，每个节点有 2~4 个子节点
3. 合并后的树高度为 $bh$（黑色高度），满足：
 $$
 n + 1 \geq 2^{bh}
 $$
4. 由于红色节点不能连续，有 $bh \geq h/2$
5. 代入得 $n + 1 \geq 2^{h/2}$，两边取对数：
 $$
 h \leq 2 \cdot \log_2(n + 1)
 $$

**推论**：红黑树的查找、插入、删除时间复杂度均为 $O(\log n)$

### 红黑树 vs AVL 树

| 特性 | 红黑树 | AVL 树 |
|------|--------|--------|
| 平衡标准 | 近似平衡（任意路径上黑色节点数相等） | 严格平衡（高度差 $\leq$ 1） |
| 树高上限 | $2 \log_2(n+1)$ | $1.44 \log_2 n$ |
| 查找 | 稍慢（树稍高） | 更快（树更矮） |
| 插入旋转 | 最多 2 次 | 可能 $O(\log n)$ 次（向根传播） |
| 删除旋转 | 最多 3 次 | 可能 $O(\log n)$ 次 |
| 适用场景 | 插入/删除频繁（`std::map`, `epoll`） | 查找频繁（数据库索引的极少更新场景） |

### 红黑树与 2-3-4 树的等价性

红黑树是 2-3-4 树（B 树家族中 m=4 的特例）的二叉树表示。将所有红色节点"推入"其黑色父节点中，红黑树即转化为 2-3-4 树：

```mermaid
graph TD
 subgraph "红黑树"
 B1["10 (B)"] --> R1["5 (R)"]
 B1 --> R2["15 (R)"]
 R1 --> B2["2 (B)"]
 R1 --> B3["7 (B)"]
 end
 subgraph "等价 2-3-4 树 — 红色节点被'吸收'到黑色父节点"
 NODE["[5|10|15] (3-node + red children)<br/>子节点: 2, 7"]
 end
```

这个同构揭示了红黑树设计的本质：**红链接 = 属于同一个 2-3-4 节点的键**。性质 4（不能有连续红色）保证了两个红链接不能相邻——因为如果两个红色节点互为父子，它们在 2-3-4 树中会产生超过 3 个键的超大节点。

理解这个等价性后，红黑树的旋转与颜色变换就不再是死记规则——每次操作对应 2-3-4 树中节点键数的增减（从 4-node 分裂为两个 2-node，或相邻 2-node 合并为 3-node）。

### 插入修复：三种情况

新节点总是红色（默认）。插入后可能违反性质 4（红-红相邻）。修复按新节点的叔叔节点颜色分三种情况：

```mermaid
flowchart TD
 INSERT["插入红色节点 Z<br/>父节点 P 也是红色"] --> CHECK{"叔叔(U)颜色?"}
 CHECK -->|"U 是红色"| CASE1["情况1: 颜色翻转<br/>P和U变黑, G变红<br/>问题上移到G"]
 CASE1 --> UP["对 G 递归修复"]
 CHECK -->|"U 是黑色<br/>Z/P/G 构成折线"| CASE2["情况2: 旋转拉直<br/>对 P 旋转使 Z/P/G 成直线"]
 CASE2 --> CASE3
 CHECK -->|"U 是黑色<br/>Z/P/G 成直线"| CASE3["情况3: 旋转+变色<br/>旋转 G, 交换 P 和 G 的颜色<br/>修复完成"]
```

- **情况 1**（U 红色）：父叔双双从红变黑，爷从黑变红。这保持了性质 5（黑高不变），但可能在更高层引入红-红冲突——递归向上修复
- **情况 2**（U 黑色，Z-P-G 折线）：旋转 P 使 Z-P-G 拉直为一线，转化为情况 3
- **情况 3**（U 黑色，Z-P-G 直线）：旋转 G 使其下降，P 上升为新的子树根。交换 P 和 G 的颜色后，修复完成——不会向上传播

插入修复至多执行 $O(\log n)$ 次情况 1（颜色翻转-上移），最后以一次旋转（情况 2+3 组合）收尾。

### 红黑树在工程中的应用

- **C++ `std::map` / `std::set`**：libstdc++ 和 libc++ 均用红黑树实现。原因：迭代器在插入/删除后不失效（与 vector 不同），中序遍历即有序，且插入/删除最多 3 次旋转
- **Linux 内核 CFS 调度器**：就绪队列用红黑树按 vruntime 排序。每次时钟中断后更新当前进程的 vruntime 并重新入树——插入/删除极频繁，红黑树的低旋转次数是首选
- **Linux `epoll`**：用红黑树存储被监视的 fd。查找 fd 是否已在监听集合中——O(log n)
- **Java `TreeMap` / `TreeSet`**：红黑树实现的有序映射和集合
- **nginx 定时器**：用红黑树存储超时事件，按超时时间排序——每次取出最小超时时间的事件

详见 [[../操作系统/D_CPU调度#CFS与红黑树|操作系统 — CFS 调度器]]。

### 红黑树插入（含修复）

```c
#include <stdlib.h>

typedef enum { RED, BLACK } Color;

typedef struct RBNode {
 int data;
 Color color;
 struct RBNode *left, *right, *parent;
} RBNode;

typedef struct {
 RBNode* root;
 RBNode* NIL; // 哨兵空节点（黑色）
} RBTree;

RBNode* rb_create_node(int val) {
 RBNode* node = malloc(sizeof(RBNode));
 node->data = val;
 node->color = RED;
 node->left = node->right = node->parent = NULL;
 return node;
}

void rb_init(RBTree* t) {
 t->NIL = malloc(sizeof(RBNode));
 t->NIL->color = BLACK;
 t->NIL->left = t->NIL->right = t->NIL->parent = NULL;
 t->root = t->NIL;
}

static void rb_left_rotate(RBTree* t, RBNode* x) {
 RBNode* y = x->right;
 x->right = y->left;
 if (y->left != t->NIL) y->left->parent = x;
 y->parent = x->parent;
 if (x->parent == t->NIL) t->root = y;
 else if (x == x->parent->left) x->parent->left = y;
 else x->parent->right = y;
 y->left = x;
 x->parent = y;
}

static void rb_right_rotate(RBTree* t, RBNode* y) {
 RBNode* x = y->left;
 y->left = x->right;
 if (x->right != t->NIL) x->right->parent = y;
 x->parent = y->parent;
 if (y->parent == t->NIL) t->root = x;
 else if (y == y->parent->left) y->parent->left = x;
 else y->parent->right = x;
 x->right = y;
 y->parent = x;
}

static void rb_insert_fixup(RBTree* t, RBNode* z) {
 while (z->parent != t->NIL && z->parent->color == RED) {
 if (z->parent == z->parent->parent->left) {
 RBNode* y = z->parent->parent->right;
 if (y->color == RED) {
 z->parent->color = BLACK;
 y->color = BLACK;
 z->parent->parent->color = RED;
 z = z->parent->parent;
 } else {
 if (z == z->parent->right) {
 z = z->parent;
 rb_left_rotate(t, z);
 }
 z->parent->color = BLACK;
 z->parent->parent->color = RED;
 rb_right_rotate(t, z->parent->parent);
 }
 } else {
 RBNode* y = z->parent->parent->left;
 if (y->color == RED) {
 z->parent->color = BLACK;
 y->color = BLACK;
 z->parent->parent->color = RED;
 z = z->parent->parent;
 } else {
 if (z == z->parent->left) {
 z = z->parent;
 rb_right_rotate(t, z);
 }
 z->parent->color = BLACK;
 z->parent->parent->color = RED;
 rb_left_rotate(t, z->parent->parent);
 }
 }
 }
 t->root->color = BLACK;
}

int rb_insert(RBTree* t, int value) {
 RBNode* z = rb_create_node(value);
 z->left = z->right = t->NIL;

 RBNode* y = t->NIL;
 RBNode* x = t->root;
 while (x != t->NIL) {
 y = x;
 if (z->data < x->data) x = x->left;
 else if (z->data > x->data) x = x->right;
 else { free(z); return 0; } // 不允许重复
 }
 z->parent = y;
 if (y == t->NIL) t->root = z;
 else if (z->data < y->data) y->left = z;
 else y->right = z;

 rb_insert_fixup(t, z);
 return 1;
}

int rb_search(RBTree* t, int value) {
 RBNode* cur = t->root;
 while (cur != t->NIL) {
 if (value == cur->data) return 1;
 cur = (value < cur->data) ? cur->left : cur->right;
 }
 return 0;
}

static void rb_destroy_rec(RBTree* t, RBNode* node) {
 if (node == t->NIL) return;
 rb_destroy_rec(t, node->left);
 rb_destroy_rec(t, node->right);
 free(node);
}

void rb_destroy(RBTree* t) {
 rb_destroy_rec(t, t->root);
 free(t->NIL);
 t->root = t->NIL = NULL;
}
```

### 插入修复的三种情况详解

假设新插入节点为 z（红色），其父节点 p 为红色（违反性质 4），叔叔节点为 u。

#### 情况 1：叔叔 u 是红色

**操作**：p 和 u 变黑，祖父 g 变红，z 上移到 g 继续修复

**原理**：父叔同时变黑不会改变黑色高度，但祖父变红可能向上传播冲突

```mermaid
graph TD
 subgraph 情况1：叔叔是红色
 direction TB
 G1["g(黑)"] --> P1["p(红) "]
 G1 --> U1["u(红)"]
 P1 --> Z1["z(红) NEW"]
 P1 --> NIL1["NIL"]
 U1 --> NIL2["NIL"]
 U1 --> NIL3["NIL"]
 style G1 fill:#333,color:#fff
 style P1 fill:#f00,color:#fff
 style U1 fill:#f00,color:#fff
 style Z1 fill:#f00,color:#fff
 style NIL1 fill:#999,color:#fff
 style NIL2 fill:#999,color:#fff
 style NIL3 fill:#999,color:#fff
 end
 subgraph 变色后
 direction TB
 G2["g(红)"] --> P2["p(黑) "]
 G2 --> U2["u(黑) "]
 P2 --> Z2["z(红)"]
 P2 --> NIL4["NIL"]
 U2 --> NIL5["NIL"]
 U2 --> NIL6["NIL"]
 style G2 fill:#f00,color:#fff
 style P2 fill:#333,color:#fff
 style U2 fill:#333,color:#fff
 style Z2 fill:#f00,color:#fff
 style NIL4 fill:#999,color:#fff
 style NIL5 fill:#999,color:#fff
 style NIL6 fill:#999,color:#fff
 end
 G1 -->|"p,u 变黑 → g 变红 → z=g"| G2
```

#### 情况 2：叔叔 u 是黑色，z 与 p 同侧（直线型）

**操作**：以 g 为支点旋转 + 变色（p 变黑，g 变红）

**原理**：旋转降低树高，变色恢复黑色高度

```mermaid
graph TD
 subgraph 情况2（左左型）：叔叔黑色+直线
 direction TB
 G1["g(黑)"] --> P1["p(红) "]
 G1 --> U1["u(黑)"]
 P1 --> Z1["z(红) NEW"]
 P1 --> NIL1["NIL"]
 Z1 --> NIL2["NIL"]
 Z1 --> NIL3["NIL"]
 U1 --> NIL4["NIL"]
 U1 --> NIL5["NIL"]
 style G1 fill:#f00,color:#fff
 style P1 fill:#f00,color:#fff
 style U1 fill:#333,color:#fff
 style Z1 fill:#f00,color:#fff
 style NIL1 fill:#999,color:#fff
 style NIL2 fill:#999,color:#fff
 style NIL3 fill:#999,color:#fff
 style NIL4 fill:#999,color:#fff
 style NIL5 fill:#999,color:#fff
 end
 subgraph 右旋+变色后
 direction TB
 P2["p(黑) "] --> Z2["z(红)"]
 P2 --> G2["g(红)"]
 Z2 --> NIL6["NIL"]
 Z2 --> NIL7["NIL"]
 G2 --> NIL8["NIL"]
 G2 --> U2["u(黑)"]
 style P2 fill:#333,color:#fff
 style Z2 fill:#f00,color:#fff
 style G2 fill:#f00,color:#fff
 style U2 fill:#333,color:#fff
 style NIL6 fill:#999,color:#fff
 style NIL7 fill:#999,color:#fff
 style NIL8 fill:#999,color:#fff
 end
 G1 -->|"右旋 g + p变黑,g变红"| P2
```

如果 z 是 p 的右孩子（右左型），则先左旋 p 转为左左型 → 按左左型处理。

#### 情况 3：叔叔 u 是黑色，z 与 p 异侧（三角型）

**操作**：先用一次旋转转为直线型，再按情况 2 处理

**原理**：三角型无法通过单次旋转恢复，需两次旋转

```mermaid
graph TD
 subgraph 情况3（左右型）：叔叔黑色+三角
 direction TB
 G1["g(黑)"] --> P1["p(红) "]
 G1 --> U1["u(黑)"]
 P1 --> NIL1["NIL"]
 P1 --> Z1["z(红) NEW"]
 Z1 --> NIL2["NIL"]
 Z1 --> NIL3["NIL"]
 U1 --> NIL4["NIL"]
 U1 --> NIL5["NIL"]
 style G1 fill:#f00,color:#fff
 style P1 fill:#f00,color:#fff
 style U1 fill:#333,color:#fff
 style Z1 fill:#f00,color:#fff
 style NIL1 fill:#999,color:#fff
 style NIL2 fill:#999,color:#fff
 style NIL3 fill:#999,color:#fff
 style NIL4 fill:#999,color:#fff
 style NIL5 fill:#999,color:#fff
 end
 subgraph 左旋p后（转为左左型）
 direction TB
 G2["g(黑)"] --> Z2["z(红)"]
 G2 --> U2["u(黑)"]
 Z2 --> P2["p(红)"]
 Z2 --> NIL6["NIL"]
 P2 --> NIL7["NIL"]
 P2 --> NIL8["NIL"]
 U2 --> NIL9["NIL"]
 U2 --> NIL10["NIL"]
 style G2 fill:#f00,color:#fff
 style Z2 fill:#f00,color:#fff
 style U2 fill:#333,color:#fff
 style P2 fill:#f00,color:#fff
 style NIL6 fill:#999,color:#fff
 style NIL7 fill:#999,color:#fff
 style NIL8 fill:#999,color:#fff
 style NIL9 fill:#999,color:#fff
 style NIL10 fill:#999,color:#fff
 end
 G1 -->|"左旋 p"| G2
 G2 -.->|"再按情况2 右旋 g + 变色"| END[" 平衡"]
```

---

## 各语言标准库对比

红黑树在工程中通常不直接暴露，而是作为有序集合/映射的底层实现：

| 语言 | 有序集合（红黑树） | 有序映射（红黑树） |
|------|--------------------|--------------------|
| C | 无（手写） | 无（手写） |
| C++ | set / multiset | map / multimap |
| Java | TreeSet | TreeMap |
| Python | 无（bisect + list 模拟） | 无（可用 sortedcontainers） |
| Rust | BTreeSet | BTreeMap |

---

## 应用场景

- **有序字典/集合**: 需要按键排序 + 范围查询的场景（如按时间查询日志）
- **区间调度**: 用 map 管理会议室预约，lower_bound 快速判断冲突
- **Linux 内核 CFS 调度器**: 红黑树管理进程按 vruntime 排序

---

## 练习

| 题号 | 题目 | 说明 |
|------|------|------|
| [220](https://leetcode.cn/problems/contains-duplicate-iii/) | 存在重复元素 III | 平衡树范围查询 |
| [981](https://leetcode.cn/problems/time-based-key-value-store/) | 基于时间的键值存储 | TreeMap 操作 |

## 动手实验

| 编号 | 题目 | 说明 |
|:----:|------|------|
| E1 | 红黑树 vs BST 高度对比 | 顺序插入 1 到 1000 到普通 BST 和红黑树，分别记录每插入 100 个元素后的树高，画出树高增长曲线 |
| E2 | 旋转次数统计 | 随机插入 1000 个元素到红黑树，统计 LL/RR/LR/RL 四种旋转各发生多少次，并与理论比例对比 |
