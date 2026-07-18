

建议先阅读: [[A_容器_Container|A 容器 Container]], [[B_栈_Stack|B 栈 Stack]], [[F_队列_Queue|F 队列 Queue]]

---

## 原理

树（Tree）是一种非线性层次结构，由节点和边组成。二叉树每个节点最多有两个子节点。

### 基本术语

- 根节点（Root）: 树的顶端，无父节点
- 叶子节点（Leaf）: 无子节点的节点
- 深度（Depth）: 从根到该节点的路径长度
- 高度（Height）: 从该节点到最远叶子的路径长度

### 二叉树的四种遍历

| 遍历方式 | 顺序 | 说明 |
|----------|------|------|
| 前序遍历 Pre-order | 根 -> 左 -> 右 | 复制树、前缀表达式 |
| 中序遍历 In-order | 左 -> 根 -> 右 | BST 有序输出 |
| 后序遍历 Post-order | 左 -> 右 -> 根 | 释放内存、后缀表达式 |
| 层序遍历 Level-order | 逐层从左到右 | BFS |

### 二叉搜索树（BST）

性质：左子树所有节点 < 根 < 右子树所有节点。

| 操作 | 平均 | 最坏 | 说明 |
|------|------|------|------|
| 查找 | O(log n) | O(n) | 退化为链表时 O(n) |
| 插入 | O(log n) | O(n) | 同上 |
| 删除 | O(log n) | O(n) | 同上 |

### AVL 树

AVL 是自平衡 BST，任意节点左右子树高度差 <= 1（平衡因子 BF = 左高 - 右高，BF ∈ {-1, 0, 1}）。

四种旋转：

| 类型 | 条件 | 操作 |
|------|------|------|
| LL | 左子树的左子树插入 | 右旋失衡节点 |
| RR | 右子树的右子树插入 | 左旋失衡节点 |
| LR | 左子树的右子树插入 | 先左旋左子，再右旋失衡节点 |
| RL | 右子树的左子树插入 | 先右旋右子，再左旋失衡节点 |

AVL 高度 ≤ 1.44 * log(n)，保证查找/插入/删除均为 O(log n)。

---

## 实现

### BST

```cpp
#include <iostream>

struct BSTNode {
    int data;
    BSTNode *left, *right;
    BSTNode(int val) : data(val), left(nullptr), right(nullptr) {}
};

class BST {
private:
    BSTNode* root;

    BSTNode* insert(BSTNode* node, int val) {
        if (!node) return new BSTNode(val);
        if (val < node->data)
            node->left = insert(node->left, val);
        else if (val > node->data)
            node->right = insert(node->right, val);
        return node;
    }

    BSTNode* search(BSTNode* node, int val) {
        if (!node || node->data == val) return node;
        if (val < node->data) return search(node->left, val);
        return search(node->right, val);
    }

    BSTNode* findMin(BSTNode* node) {
        while (node && node->left) node = node->left;
        return node;
    }

    BSTNode* remove(BSTNode* node, int val) {
        if (!node) return nullptr;
        if (val < node->data)
            node->left = remove(node->left, val);
        else if (val > node->data)
            node->right = remove(node->right, val);
        else {
            // 一个子节点或无子节点
            if (!node->left) {
                BSTNode* tmp = node->right; delete node; return tmp;
            }
            if (!node->right) {
                BSTNode* tmp = node->left; delete node; return tmp;
            }
            // 两个子节点：用右子树最小值替换
            BSTNode* minNode = findMin(node->right);
            node->data = minNode->data;
            node->right = remove(node->right, minNode->data);
        }
        return node;
    }

    void inorderPrint(BSTNode* node) {
        if (!node) return;
        inorderPrint(node->left);
        std::cout << node->data << " ";
        inorderPrint(node->right);
    }

    void destroy(BSTNode* node) {
        if (!node) return;
        destroy(node->left);
        destroy(node->right);
        delete node;
    }

public:
    BST() : root(nullptr) {}
    ~BST() { destroy(root); }

    void insert(int val) { root = insert(root, val); }
    bool find(int val) { return search(root, val) != nullptr; }
    void remove(int val) { root = remove(root, val); }
    void print() { inorderPrint(root); std::cout << std::endl; }
};
```

### AVL 树

```cpp
#include <algorithm>

struct AVLNode {
    int data, height;
    AVLNode *left, *right;
    AVLNode(int val) : data(val), height(1), left(nullptr), right(nullptr) {}
};

class AVLTree {
private:
    AVLNode* root;

    int height(AVLNode* n) { return n ? n->height : 0; }
    int balanceFactor(AVLNode* n) {
        return n ? height(n->left) - height(n->right) : 0;
    }
    void updateHeight(AVLNode* n) {
        n->height = 1 + std::max(height(n->left), height(n->right));
    }

    AVLNode* rightRotate(AVLNode* y) {
        AVLNode* x = y->left;
        AVLNode* T2 = x->right;
        x->right = y;
        y->left = T2;
        updateHeight(y);
        updateHeight(x);
        return x;
    }

    AVLNode* leftRotate(AVLNode* x) {
        AVLNode* y = x->right;
        AVLNode* T2 = y->left;
        y->left = x;
        x->right = T2;
        updateHeight(x);
        updateHeight(y);
        return y;
    }

    AVLNode* insert(AVLNode* node, int val) {
        if (!node) return new AVLNode(val);

        if (val < node->data)
            node->left = insert(node->left, val);
        else if (val > node->data)
            node->right = insert(node->right, val);
        else return node; // 不允许重复

        updateHeight(node);
        int bf = balanceFactor(node);

        // LL
        if (bf > 1 && val < node->left->data)
            return rightRotate(node);
        // RR
        if (bf < -1 && val > node->right->data)
            return leftRotate(node);
        // LR
        if (bf > 1 && val > node->left->data) {
            node->left = leftRotate(node->left);
            return rightRotate(node);
        }
        // RL
        if (bf < -1 && val < node->right->data) {
            node->right = rightRotate(node->right);
            return leftRotate(node);
        }
        return node;
    }

    AVLNode* findMin(AVLNode* node) {
        while (node && node->left) node = node->left;
        return node;
    }

    AVLNode* remove(AVLNode* node, int val) {
        if (!node) return nullptr;

        if (val < node->data)
            node->left = remove(node->left, val);
        else if (val > node->data)
            node->right = remove(node->right, val);
        else {
            if (!node->left || !node->right) {
                AVLNode* tmp = node->left ? node->left : node->right;
                delete node;
                return tmp;
            }
            AVLNode* minNode = findMin(node->right);
            node->data = minNode->data;
            node->right = remove(node->right, minNode->data);
        }

        if (!node) return nullptr;
        updateHeight(node);
        int bf = balanceFactor(node);

        // LL
        if (bf > 1 && balanceFactor(node->left) >= 0)
            return rightRotate(node);
        // LR
        if (bf > 1 && balanceFactor(node->left) < 0) {
            node->left = leftRotate(node->left);
            return rightRotate(node);
        }
        // RR
        if (bf < -1 && balanceFactor(node->right) <= 0)
            return leftRotate(node);
        // RL
        if (bf < -1 && balanceFactor(node->right) > 0) {
            node->right = rightRotate(node->right);
            return leftRotate(node);
        }
        return node;
    }

    void inorderPrint(AVLNode* node) {
        if (!node) return;
        inorderPrint(node->left);
        std::cout << node->data << "(BF=" << balanceFactor(node) << ") ";
        inorderPrint(node->right);
    }

    void destroy(AVLNode* node) {
        if (!node) return;
        destroy(node->left);
        destroy(node->right);
        delete node;
    }

public:
    AVLTree() : root(nullptr) {}
    ~AVLTree() { destroy(root); }

    void insert(int val) { root = insert(root, val); }
    void remove(int val) { root = remove(root, val); }
    void print() { inorderPrint(root); std::cout << std::endl; }
};
```

---

## 应用场景

- **文件系统**: 目录树，用多叉树表示
- **表达式树**: 编译器解析数学表达式为语法树
- **数据库索引**: BST/AVL/红黑树/B+树
- **字典序存储**: BST 中序遍历即有序输出

---

## 练习

| 题号 | 题目 | 难度 | 知识点 |
|------|------|------|--------|
| P3369 | 普通平衡树 | 提高 | BST/AVL 基本操作 |
| P1364 | 医院设置 | 普及 | 树的遍历、带权路径 |
| P1030 | 求先序排列 | 普及 | 遍历序列重建树 |
