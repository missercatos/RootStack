
# AVL 树

> 自平衡二叉搜索树。任意节点左右子树高度差不超过 1。查找/插入/删除均为 O(log n)。

---

## 结构定义

```c
typedef struct AVLNode {
    int key;
    int height;        /* 节点高度（叶子为 1） */
    struct AVLNode *left;
    struct AVLNode *right;
} AVLNode;
```

---

## 函数签名

| 函数 | 复杂度 | 说明 |
|------|--------|------|
| `AVLNode* avl_insert(AVLNode *root, int key)` | O(log n) | 插入，自底向上旋转修复 |
| `AVLNode* avl_delete(AVLNode *root, int key)` | O(log n) | 删除，自底向上旋转修复 |
| `AVLNode* avl_search(AVLNode *root, int key)` | O(log n) | 查找 |

---

## 旋转操作

### 四种失衡情况

| 失衡类型 | 旋转 | 条件 |
|----------|------|------|
| LL（左左） | 右旋 | 左子树高度 - 右子树高度 > 1，且插入发生在左子树的左子树 |
| RR（右右） | 左旋 | 右子树高度 - 左子树高度 > 1，且插入发生在右子树的右子树 |
| LR（左右） | 左旋 + 右旋 | 左重且插入发生在左子树的右子树 |
| RL（右左） | 右旋 + 左旋 | 右重且插入发生在右子树的左子树 |

### 右旋 (RR→平衡)

```c
AVLNode* rotate_right(AVLNode *y) {
    AVLNode *x = y->left;
    AVLNode *T2 = x->right;
    x->right = y;
    y->left = T2;
    y->height = 1 + max(height(y->left), height(y->right));
    x->height = 1 + max(height(x->left), height(x->right));
    return x;
}
```

---

## 平衡因子

```
BF = height(left) - height(right)
```

- BF ∈ {-1, 0, 1}：平衡
- BF = 2：左重，需右旋或先左旋再右旋
- BF = -2：右重，需左旋或先右旋再左旋

---

## AVL vs 红黑树

| 特性 | AVL 树 | 红黑树 |
|------|--------|--------|
| 平衡条件 | 严格（高度差 ≤ 1） | 宽松（最长 ≤ 2×最短） |
| 查找 | 更快（更平衡） | 稍慢 |
| 插入/删除 | 旋转次数多 | 旋转次数少（≤ 3） |
| 实现复杂度 | 中等 | 较高 |

---

## 跨语言参考

- [[../../../c语言教程/3数据结构/06_树与二叉树|C语言数据结构：树与二叉树]]
