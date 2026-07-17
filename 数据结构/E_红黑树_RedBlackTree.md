# E 红黑树 Red-Black Tree

建议先阅读: [[I_树_Tree_BST_AVL|I 树 BST AVL]]

---

## 原理

红黑树（Red-Black Tree）是一种自平衡二叉查找树，每个节点额外存储一个颜色位（红色或黑色），通过颜色约束保证树近似平衡。它是 C++ 标准库中 `set`、`map`、`multiset`、`multimap` 的底层实现。

### 五个性质

1. 每个节点是红色或黑色
2. 根节点是黑色
3. 每个叶子（NIL 空节点）是黑色
4. 红色节点的两个子节点必须是黑色（不能有连续的红色）
5. 从任意节点到其每个叶子的所有路径包含相同数目的黑色节点

### 复杂度

| 操作 | 平均 | 最坏 | 说明 |
|------|------|------|------|
| 查找 | O(log n) | O(log n) | 高度不超过 2*log(n+1) |
| 插入 | O(log n) | O(log n) | BST 插入 + 最多 2 次旋转 |
| 删除 | O(log n) | O(log n) | BST 删除 + 最多 3 次旋转 |
| 空间 | O(n) | O(n) | 每个节点额外 1 bit |

### 红黑树 vs AVL 树

| 特性 | 红黑树 | AVL 树 |
|------|--------|--------|
| 平衡标准 | 近似平衡（最长路径 <= 2*最短路径） | 严格平衡（高度差 <= 1） |
| 查找 | 稍慢（树更高） | 更快（树更矮） |
| 插入/删除 | 更快（1-2 次旋转） | 更慢（可能 O(log n) 次旋转） |
| 适用场景 | 插入删除频繁 | 查找频繁 |

---

## 实现

### 红黑树插入（含修复）

```cpp
#include <iostream>

enum class Color { RED, BLACK };

template <typename T>
class RBTree {
private:
    struct Node {
        T data;
        Color color;
        Node *left, *right, *parent;
        Node(T val) : data(val), color(Color::RED),
                      left(nullptr), right(nullptr), parent(nullptr) {}
    };

    Node* root;
    Node* NIL; // 哨兵空节点（黑色）

    void leftRotate(Node* x) {
        Node* y = x->right;
        x->right = y->left;
        if (y->left != NIL) y->left->parent = x;
        y->parent = x->parent;
        if (x->parent == nullptr) root = y;
        else if (x == x->parent->left) x->parent->left = y;
        else x->parent->right = y;
        y->left = x;
        x->parent = y;
    }

    void rightRotate(Node* y) {
        Node* x = y->left;
        y->left = x->right;
        if (x->right != NIL) x->right->parent = y;
        x->parent = y->parent;
        if (y->parent == nullptr) root = x;
        else if (y == y->parent->left) y->parent->left = x;
        else y->parent->right = x;
        x->right = y;
        y->parent = x;
    }

    void insertFixup(Node* z) {
        while (z->parent && z->parent->color == Color::RED) {
            if (z->parent == z->parent->parent->left) {
                Node* y = z->parent->parent->right; // 叔叔
                if (y->color == Color::RED) {
                    // 情况 1: 叔叔是红色 -> 变色上移
                    z->parent->color = Color::BLACK;
                    y->color = Color::BLACK;
                    z->parent->parent->color = Color::RED;
                    z = z->parent->parent;
                } else {
                    if (z == z->parent->right) {
                        // 情况 2: 三角 -> 左旋
                        z = z->parent;
                        leftRotate(z);
                    }
                    // 情况 3: 直线 -> 右旋+变色
                    z->parent->color = Color::BLACK;
                    z->parent->parent->color = Color::RED;
                    rightRotate(z->parent->parent);
                }
            } else {
                // 对称情况（parent 是右孩子）
                Node* y = z->parent->parent->left;
                if (y->color == Color::RED) {
                    z->parent->color = Color::BLACK;
                    y->color = Color::BLACK;
                    z->parent->parent->color = Color::RED;
                    z = z->parent->parent;
                } else {
                    if (z == z->parent->left) {
                        z = z->parent;
                        rightRotate(z);
                    }
                    z->parent->color = Color::BLACK;
                    z->parent->parent->color = Color::RED;
                    leftRotate(z->parent->parent);
                }
            }
        }
        root->color = Color::BLACK;
    }

    void inorderPrint(Node* node) {
        if (node == NIL) return;
        inorderPrint(node->left);
        std::cout << node->data
                  << (node->color == Color::RED ? "(R) " : "(B) ");
        inorderPrint(node->right);
    }

    void destroy(Node* node) {
        if (node == NIL) return;
        destroy(node->left);
        destroy(node->right);
        delete node;
    }

public:
    RBTree() {
        NIL = new Node(T());
        NIL->color = Color::BLACK;
        NIL->left = NIL->right = NIL->parent = nullptr;
        root = NIL;
    }

    ~RBTree() {
        destroy(root);
        delete NIL;
    }

    void insert(T value) {
        Node* z = new Node(value);
        z->left = z->right = NIL;

        Node* y = nullptr;
        Node* x = root;
        while (x != NIL) {
            y = x;
            if (z->data < x->data) x = x->left;
            else if (z->data > x->data) x = x->right;
            else { delete z; return; } // 不允许重复
        }

        z->parent = y;
        if (y == nullptr) root = z;
        else if (z->data < y->data) y->left = z;
        else y->right = z;

        insertFixup(z);
    }

    bool search(T value) const {
        Node* cur = root;
        while (cur != NIL) {
            if (value == cur->data) return true;
            cur = (value < cur->data) ? cur->left : cur->right;
        }
        return false;
    }

    void print() {
        inorderPrint(root);
        std::cout << std::endl;
    }
};
```

### 插入修复的三种情况

1. **叔叔是红色**: 父和叔变黑，祖父变红，当前节点移到祖父继续修复
2. **叔叔是黑色，当前节点与父节点同侧（直线）**: 旋转父节点 + 变色
3. **叔叔是黑色，当前节点与父节点异侧（三角）**: 先旋转到同侧，再按情况 2 处理

---

## STL 使用

```cpp
#include <set>
#include <map>
#include <iostream>

int main() {
    // set -- 有序集合（红黑树）
    std::set<int> s = {3, 1, 4, 1, 5};
    s.insert(9);
    s.erase(1);
    auto it = s.lower_bound(3); // 第一个 >= 3 的元素
    auto it2 = s.upper_bound(3); // 第一个 > 3 的元素

    for (int x : s) std::cout << x << " "; // 1 3 4 5 9

    // map -- 有序映射（红黑树）
    std::map<std::string, int> m;
    m["apple"] = 5;
    m["banana"] = 3;
    // 范围查询
    auto lb = m.lower_bound("a");
    auto ub = m.upper_bound("c");
    for (auto it = lb; it != ub; ++it)
        std::cout << it->first << ": " << it->second << std::endl;

    // multimap / multiset -- 允许重复键

    return 0;
}
```

---

## 应用场景

- **有序字典/集合**: 需要按键排序 + 范围查询的场景（如按时间查询日志）
- **区间调度**: 用 map 管理会议室预约，lower_bound 快速判断冲突
- **Linux 内核 CFS 调度器**: 红黑树管理进程按 vruntime 排序

---

## 练习

| 题号 | 题目 | 难度 | 知识点 |
|------|------|------|--------|
| P3369 | 普通平衡树 | 提高 | 平衡树基本操作 |
| P6136 | 普通平衡树（数据加强版） | 提高+ | 红黑树/Treap/Splay |
