## ==========================================================================
C++ 数据结构教程 — 树 (Tree) — 二叉搜索树与AVL树
## ==========================================================================

## 📋 章节概述

树（Tree）是一种非线性的层次结构，由节点和连接节点的边组成。树结构在计算机
科学中无处不在：文件系统、HTML DOM树、编译器语法树、数据库索引、网络路由等。

本章重点讲解二叉搜索树（BST）和自平衡二叉搜索树AVL树，理解从普通树到平衡树的
演进思路，以及旋转操作如何维持树的平衡。

## ==========================================================================
### 📖 第一节: 基础语法 + 计算机底层原理
## ==========================================================================

1.1 树的基本概念
--------------------

树的术语：
- 根节点（Root）：树的顶端节点，没有父节点
- 叶子节点（Leaf）：没有子节点的节点
- 父节点（Parent）和子节点（Child）
- 兄弟节点（Sibling）：同一父节点的子节点
- 子树（Subtree）：树中任意节点及其所有后代
- 深度（Depth）：从根节点到某节点的路径长度
- 高度（Height）：从某节点到最远叶子节点的路径长度

二叉树（Binary Tree）：每个节点最多有两个子节点（左子节点和右子节点）。

二叉树的遍历方式：
- 前序遍历（Pre-order）：根 → 左 → 右
- 中序遍历（In-order）：左 → 根 → 右
- 后序遍历（Post-order）：左 → 右 → 根
- 层序遍历（Level-order）：从上到下，从左到右

```cpp
#include <iostream>
#include <queue>
#include <stack>

struct TreeNode {
    int data;
    TreeNode* left;
    TreeNode* right;

    TreeNode(int val) : data(val), left(nullptr), right(nullptr) {}
};

class BinaryTree {
protected:
    TreeNode* root;

    void preorder(TreeNode* node) const {
        if (!node) return;
        std::cout << node->data << " ";
        preorder(node->left);
        preorder(node->right);
    }

    void inorder(TreeNode* node) const {
        if (!node) return;
        inorder(node->left);
        std::cout << node->data << " ";
        inorder(node->right);
    }

    void postorder(TreeNode* node) const {
        if (!node) return;
        postorder(node->left);
        postorder(node->right);
        std::cout << node->data << " ";
    }

    void destroy(TreeNode* node) {
        if (!node) return;
        destroy(node->left);
        destroy(node->right);
        delete node;
    }

public:
    BinaryTree() : root(nullptr) {}
    virtual ~BinaryTree() { destroy(root); }

    virtual void insert(int value) = 0;

    void printPreorder() const {
        std::cout << "前序遍历: ";
        preorder(root);
        std::cout << std::endl;
    }

    void printInorder() const {
        std::cout << "中序遍历: ";
        inorder(root);
        std::cout << std::endl;
    }

    void printPostorder() const {
        std::cout << "后序遍历: ";
        postorder(root);
        std::cout << std::endl;
    }

    void printLevelorder() const {
        if (!root) return;
        std::queue<TreeNode*> q;
        q.push(root);

        std::cout << "层序遍历: ";
        while (!q.empty()) {
            TreeNode* node = q.front();
            q.pop();
            std::cout << node->data << " ";

            if (node->left) q.push(node->left);
            if (node->right) q.push(node->right);
        }
        std::cout << std::endl;
    }

    // 非递归中序遍历（了解栈在树遍历中的作用）
    void printInorderIterative() const {
        std::stack<TreeNode*> stk;
        TreeNode* cur = root;

        std::cout << "中序遍历(迭代): ";
        while (cur || !stk.empty()) {
            while (cur) {
                stk.push(cur);
                cur = cur->left;
            }
            cur = stk.top();
            stk.pop();
            std::cout << cur->data << " ";
            cur = cur->right;
        }
        std::cout << std::endl;
    }

    int height(TreeNode* node) const {
        if (!node) return 0;
        return 1 + std::max(height(node->left), height(node->right));
    }

    int getHeight() const { return height(root); }
};
```

1.2 二叉搜索树（BST）
--------------------------

二叉搜索树的性质：
1. 左子树所有节点的值 < 根节点的值
2. 右子树所有节点的值 > 根节点的值
3. 左右子树也是二叉搜索树

```cpp
#include <iostream>

class BST : public BinaryTree {
private:
    TreeNode* insertNode(TreeNode* node, int value) {
        if (!node) return new TreeNode(value);

        if (value < node->data) {
            node->left = insertNode(node->left, value);
        } else if (value > node->data) {
            node->right = insertNode(node->right, value);
        }
        // 值相等时不插入（不允许重复）
        return node;
    }

    TreeNode* searchNode(TreeNode* node, int value) const {
        if (!node || node->data == value) return node;
        if (value < node->data) return searchNode(node->left, value);
        return searchNode(node->right, value);
    }

    TreeNode* findMin(TreeNode* node) const {
        while (node && node->left) node = node->left;
        return node;
    }

    TreeNode* deleteNode(TreeNode* node, int value) {
        if (!node) return nullptr;

        if (value < node->data) {
            node->left = deleteNode(node->left, value);
        } else if (value > node->data) {
            node->right = deleteNode(node->right, value);
        } else {
            // 找到要删除的节点
            if (!node->left) {
                TreeNode* temp = node->right;
                delete node;
                return temp;
            }
            if (!node->right) {
                TreeNode* temp = node->left;
                delete node;
                return temp;
            }

            // 有两个子节点：用右子树的最小节点替换
            TreeNode* min_node = findMin(node->right);
            node->data = min_node->data;
            node->right = deleteNode(node->right, min_node->data);
        }
        return node;
    }

public:
    void insert(int value) override {
        root = insertNode(root, value);
    }

    bool search(int value) const {
        return searchNode(root, value) != nullptr;
    }

    void remove(int value) {
        root = deleteNode(root, value);
    }
};

int main() {
    BST tree;

    // 插入节点
    int values[] = {50, 30, 80, 20, 40, 70, 90, 10, 35, 45, 85};
    for (int v : values) {
        tree.insert(v);
    }

    tree.printInorder();    // 应输出有序序列
    tree.printPreorder();
    tree.printPostorder();
    tree.printLevelorder();
    tree.printInorderIterative();

    std::cout << "查找40: " << (tree.search(40) ? "找到" : "未找到") << std::endl;
    std::cout << "查找100: " << (tree.search(100) ? "找到" : "未找到") << std::endl;
    std::cout << "树高: " << tree.getHeight() << std::endl;

    tree.remove(40);
    std::cout << "删除40后: ";
    tree.printInorder();

    return 0;
}
```

BST的问题：当插入有序数据时，BST退化为链表（斜树），树高为O(n)，
查找复杂度退化到O(n)。这就是为什么需要平衡树。

```
BST退化为链表：
插入顺序: 10, 20, 30, 40, 50

   10
    \
     20
       \
        30
          \
           40
             \
              50

查找50需要比较5次，而不是log5≈2次
```


1.3 AVL树的底层原理
-----------------------

AVL树是自平衡二叉搜索树，任何节点的左右子树高度差不超过1（平衡因子BF ∈ {-1,0,1}）。

平衡因子 = 左子树高度 - 右子树高度

当插入或删除导致某节点|BF| > 1时，通过旋转恢复平衡。

四种旋转情况：
1. LL（左左）：左子树的左子树插入 → 右旋
2. RR（右右）：右子树的右子树插入 → 左旋
3. LR（左右）：左子树的右子树插入 → 先左旋再右旋
4. RL（右左）：右子树的左子树插入 → 先右旋再左旋

```cpp
#include <iostream>
#include <algorithm>

class AVLTree {
private:
    struct AVLNode {
        int data;
        AVLNode* left;
        AVLNode* right;
        int height;

        AVLNode(int val) : data(val), left(nullptr), right(nullptr), height(1) {}
    };

    AVLNode* root;

    int getHeight(AVLNode* node) const {
        return node ? node->height : 0;
    }

    int getBalance(AVLNode* node) const {
        return node ? getHeight(node->left) - getHeight(node->right) : 0;
    }

    void updateHeight(AVLNode* node) {
        if (node) {
            node->height = 1 + std::max(getHeight(node->left),
                                        getHeight(node->right));
        }
    }

    // 右旋
    AVLNode* rightRotate(AVLNode* y) {
        AVLNode* x = y->left;
        AVLNode* T2 = x->right;

        x->right = y;
        y->left = T2;

        updateHeight(y);
        updateHeight(x);

        return x;
    }

    // 左旋
    AVLNode* leftRotate(AVLNode* x) {
        AVLNode* y = x->right;
        AVLNode* T2 = y->left;

        y->left = x;
        x->right = T2;

        updateHeight(x);
        updateHeight(y);

        return y;
    }

    AVLNode* insertNode(AVLNode* node, int value) {
        // 1. 普通BST插入
        if (!node) return new AVLNode(value);

        if (value < node->data) {
            node->left = insertNode(node->left, value);
        } else if (value > node->data) {
            node->right = insertNode(node->right, value);
        } else {
            return node;  // 不允许重复
        }

        // 2. 更新高度
        updateHeight(node);

        // 3. 检查平衡因子并旋转
        int balance = getBalance(node);

        // LL情况: 右旋
        if (balance > 1 && value < node->left->data) {
            return rightRotate(node);
        }

        // RR情况: 左旋
        if (balance < -1 && value > node->right->data) {
            return leftRotate(node);
        }

        // LR情况: 先左旋再右旋
        if (balance > 1 && value > node->left->data) {
            node->left = leftRotate(node->left);
            return rightRotate(node);
        }

        // RL情况: 先右旋再左旋
        if (balance < -1 && value < node->right->data) {
            node->right = rightRotate(node->right);
            return leftRotate(node);
        }

        return node;
    }

    AVLNode* findMin(AVLNode* node) const {
        while (node && node->left) node = node->left;
        return node;
    }

    AVLNode* deleteNode(AVLNode* node, int value) {
        // 1. 普通BST删除
        if (!node) return nullptr;

        if (value < node->data) {
            node->left = deleteNode(node->left, value);
        } else if (value > node->data) {
            node->right = deleteNode(node->right, value);
        } else {
            if (!node->left || !node->right) {
                AVLNode* temp = node->left ? node->left : node->right;
                delete node;
                return temp;
            }

            AVLNode* min_node = findMin(node->right);
            node->data = min_node->data;
            node->right = deleteNode(node->right, min_node->data);
        }

        if (!node) return nullptr;

        // 2. 更新高度
        updateHeight(node);

        // 3. 检查平衡
        int balance = getBalance(node);

        // LL
        if (balance > 1 && getBalance(node->left) >= 0) {
            return rightRotate(node);
        }

        // LR
        if (balance > 1 && getBalance(node->left) < 0) {
            node->left = leftRotate(node->left);
            return rightRotate(node);
        }

        // RR
        if (balance < -1 && getBalance(node->right) <= 0) {
            return leftRotate(node);
        }

        // RL
        if (balance < -1 && getBalance(node->right) > 0) {
            node->right = rightRotate(node->right);
            return leftRotate(node);
        }

        return node;
    }

    void inorder(AVLNode* node) const {
        if (!node) return;
        inorder(node->left);
        std::cout << node->data << "(BF=" << getBalance(node) << ") ";
        inorder(node->right);
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

    void insert(int value) {
        root = insertNode(root, value);
    }

    void remove(int value) {
        root = deleteNode(root, value);
    }

    void print() const {
        std::cout << "AVL树中序遍历(带平衡因子): ";
        inorder(root);
        std::cout << std::endl;
        std::cout << "树高: " << (root ? root->height : 0) << std::endl;
    }
};

int main() {
    AVLTree avl;

    // 插入有序数据
    std::cout << "插入有序序列 10, 20, 30, 40, 50, 25" << std::endl;
    avl.insert(10);
    avl.insert(20);
    avl.insert(30);
    avl.insert(40);
    avl.insert(50);
    avl.insert(25);

    avl.print();

    std::cout << "\n删除30:" << std::endl;
    avl.remove(30);
    avl.print();

    return 0;
}
```


## ==========================================================================
### 📖 第二节: 所有用法大全
## ==========================================================================

2.1 其他常见树结构
-----------------------

除了二叉搜索树和AVL树，还有其他重要的树结构：

(1) 完全二叉树（Complete Binary Tree）
- 除最后一层外，其他层节点都是满的
- 最后一层节点从左到右排列
- 可用数组高效存储：父节点i，子节点为2i+1和2i+2

(2) 满二叉树（Full Binary Tree）
- 每个节点要么是叶子节点，要么有两个子节点

(3) 线段树（Segment Tree）
- 用于区间查询和更新

(4) 字典树 / 前缀树（Trie）
- 用于字符串搜索和前缀匹配

2.2 字典树（Trie）实现
--------------------------

```cpp
#include <iostream>
#include <unordered_map>
#include <string>
#include <vector>

class TrieNode {
public:
    std::unordered_map<char, TrieNode*> children;
    bool is_end;
    int count;  // 经过该节点的单词数

    TrieNode() : is_end(false), count(0) {}
    ~TrieNode() {
        for (auto& [ch, child] : children) {
            delete child;
        }
    }
};

class Trie {
private:
    TrieNode* root;

public:
    Trie() : root(new TrieNode()) {}
    ~Trie() { delete root; }

    void insert(const std::string& word) {
        TrieNode* cur = root;
        for (char ch : word) {
            if (cur->children.find(ch) == cur->children.end()) {
                cur->children[ch] = new TrieNode();
            }
            cur = cur->children[ch];
            cur->count++;
        }
        cur->is_end = true;
    }

    bool search(const std::string& word) const {
        TrieNode* cur = root;
        for (char ch : word) {
            auto it = cur->children.find(ch);
            if (it == cur->children.end()) return false;
            cur = it->second;
        }
        return cur->is_end;
    }

    bool startsWith(const std::string& prefix) const {
        TrieNode* cur = root;
        for (char ch : prefix) {
            auto it = cur->children.find(ch);
            if (it == cur->children.end()) return false;
            cur = it->second;
        }
        return true;
    }

    // 获取所有以prefix为前缀的单词
    std::vector<std::string> getWordsWithPrefix(const std::string& prefix) const {
        TrieNode* cur = root;
        for (char ch : prefix) {
            auto it = cur->children.find(ch);
            if (it == cur->children.end()) return {};
            cur = it->second;
        }

        std::vector<std::string> result;
        std::string current = prefix;
        dfsCollect(cur, current, result);
        return result;
    }

private:
    void dfsCollect(TrieNode* node, std::string& current,
                    std::vector<std::string>& result) const {
        if (node->is_end) {
            result.push_back(current);
        }
        for (const auto& [ch, child] : node->children) {
            current.push_back(ch);
            dfsCollect(child, current, result);
            current.pop_back();
        }
    }
};

int main() {
    Trie trie;

    trie.insert("apple");
    trie.insert("app");
    trie.insert("application");
    trie.insert("apt");
    trie.insert("bat");
    trie.insert("batch");
    trie.insert("bath");

    std::cout << "search(app): " << trie.search("app") << std::endl;
    std::cout << "search(apple): " << trie.search("apple") << std::endl;
    std::cout << "startsWith(app): " << trie.startsWith("app") << std::endl;

    std::cout << "\n以\"ap\"为前缀的单词: ";
    for (const auto& word : trie.getWordsWithPrefix("ap")) {
        std::cout << word << " ";
    }
    std::cout << std::endl;

    std::cout << "\n以\"bat\"为前缀的单词: ";
    for (const auto& word : trie.getWordsWithPrefix("bat")) {
        std::cout << word << " ";
    }
    std::cout << std::endl;

    return 0;
}
```

2.3 树与数组的转换（堆的树形表示）
----------------------------------------

```cpp
#include <iostream>
#include <vector>

// 用数组表示的完全二叉树（堆）
class HeapTree {
private:
    std::vector<int> data;

public:
    void insert(int value) {
        data.push_back(value);
        siftUp(data.size() - 1);
    }

    void siftUp(size_t index) {
        while (index > 0) {
            size_t parent = (index - 1) / 2;
            if (data[parent] >= data[index]) break;
            std::swap(data[parent], data[index]);
            index = parent;
        }
    }

    void printAsTree() const {
        if (data.empty()) return;

        int level = 0;
        int count = 0;
        int total = data.size();

        std::cout << "数组表示的完全二叉树:" << std::endl;

        while (count < total) {
            int nodes_in_level = 1 << level;
            for (int i = 0; i < nodes_in_level && count < total; ++i) {
                std::cout << data[count++] << " ";
            }
            std::cout << std::endl;
            ++level;
        }

        // 打印父子关系
        std::cout << "\n父子关系:" << std::endl;
        for (size_t i = 0; i < data.size(); ++i) {
            std::cout << "节点[" << i << "]=" << data[i];
            size_t left = 2 * i + 1;
            size_t right = 2 * i + 2;
            if (left < data.size())
                std::cout << " 左子[" << left << "]=" << data[left];
            if (right < data.size())
                std::cout << " 右子[" << right << "]=" << data[right];
            std::cout << std::endl;
        }
    }
};

int main() {
    HeapTree ht;

    for (int v : {3, 1, 4, 1, 5, 9, 2, 6}) {
        ht.insert(v);
    }

    ht.printAsTree();

    return 0;
}
```


## ==========================================================================
### 📖 第三节: 实用案例
## ==========================================================================

案例一：文件系统目录树
------------------------------

```cpp
#include <iostream>
#include <vector>
#include <string>
#include <map>
#include <algorithm>

class FileSystemNode {
public:
    std::string name;
    bool is_directory;
    std::vector<FileSystemNode*> children;

    FileSystemNode(const std::string& n, bool dir)
        : name(n), is_directory(dir) {}

    void addChild(FileSystemNode* child) {
        children.push_back(child);
    }

    void print(int depth = 0) const {
        for (int i = 0; i < depth; ++i) std::cout << "  ";
        std::cout << (is_directory ? "📁 " : "📄 ") << name << std::endl;

        // 按类型排序：目录在前，文件在后
        std::vector<FileSystemNode*> dirs, files;
        for (auto child : children) {
            if (child->is_directory) dirs.push_back(child);
            else files.push_back(child);
        }

        for (auto child : dirs) child->print(depth + 1);
        for (auto child : files) child->print(depth + 1);
    }

    FileSystemNode* find(const std::string& target_name) {
        if (name == target_name) return this;
        for (auto child : children) {
            auto result = child->find(target_name);
            if (result) return result;
        }
        return nullptr;
    }

    size_t totalSize() const {
        size_t count = is_directory ? 0 : 1;
        for (auto child : children) {
            count += child->totalSize();
        }
        return count;
    }
};

int main() {
    FileSystemNode root("root", true);

    FileSystemNode* home = new FileSystemNode("home", true);
    FileSystemNode* user = new FileSystemNode("user", true);
    FileSystemNode* docs = new FileSystemNode("docs", true);
    FileSystemNode* pics = new FileSystemNode("pics", true);

    FileSystemNode* readme = new FileSystemNode("readme.txt", false);
    FileSystemNode* notes = new FileSystemNode("notes.md", false);
    FileSystemNode* photo1 = new FileSystemNode("vacation.jpg", false);
    FileSystemNode* photo2 = new FileSystemNode("family.png", false);

    FileSystemNode* etc = new FileSystemNode("etc", true);
    FileSystemNode* config = new FileSystemNode("config.ini", false);

    root.addChild(home);
    root.addChild(etc);

    home->addChild(user);
    user->addChild(docs);
    user->addChild(pics);

    docs->addChild(readme);
    docs->addChild(notes);
    pics->addChild(photo1);
    pics->addChild(photo2);

    etc->addChild(config);

    std::cout << "文件系统树:" << std::endl;
    root.print();

    std::cout << "\n查找 pics: ";
    auto found = root.find("pics");
    std::cout << (found ? "找到" : "未找到") << std::endl;

    std::cout << "非目录文件总数: " << root.totalSize() << std::endl;

    return 0;
}
```


案例二：表达式树（语法树）
------------------------------

将数学表达式表示为树结构，支持求值和打印：

```cpp
#include <iostream>
#include <string>
#include <cmath>

class ExprNode {
public:
    virtual ~ExprNode() = default;
    virtual double evaluate() const = 0;
    virtual std::string toString() const = 0;
};

class NumberNode : public ExprNode {
    double value;
public:
    NumberNode(double v) : value(v) {}
    double evaluate() const override { return value; }
    std::string toString() const override { return std::to_string(value); }
};

class BinaryOpNode : public ExprNode {
protected:
    ExprNode* left;
    ExprNode* right;
    char op;

public:
    BinaryOpNode(ExprNode* l, ExprNode* r, char o)
        : left(l), right(r), op(o) {}

    ~BinaryOpNode() override {
        delete left;
        delete right;
    }

    std::string toString() const override {
        return "(" + left->toString() + " " + op + " " + right->toString() + ")";
    }
};

class AddNode : public BinaryOpNode {
public:
    AddNode(ExprNode* l, ExprNode* r) : BinaryOpNode(l, r, '+') {}
    double evaluate() const override { return left->evaluate() + right->evaluate(); }
};

class SubNode : public BinaryOpNode {
public:
    SubNode(ExprNode* l, ExprNode* r) : BinaryOpNode(l, r, '-') {}
    double evaluate() const override { return left->evaluate() - right->evaluate(); }
};

class MulNode : public BinaryOpNode {
public:
    MulNode(ExprNode* l, ExprNode* r) : BinaryOpNode(l, r, '*') {}
    double evaluate() const override { return left->evaluate() * right->evaluate(); }
};

class DivNode : public BinaryOpNode {
public:
    DivNode(ExprNode* l, ExprNode* r) : BinaryOpNode(l, r, '/') {}
    double evaluate() const override { return left->evaluate() / right->evaluate(); }
};

int main() {
    // 构建表达式: (3 + 4) * (5 - 2)
    //        *
    //      /   \
    //     +     -
    //    / \   / \
    //   3   4 5   2

    ExprNode* expr = new MulNode(
        new AddNode(new NumberNode(3), new NumberNode(4)),
        new SubNode(new NumberNode(5), new NumberNode(2))
    );

    std::cout << "表达式: " << expr->toString() << std::endl;
    std::cout << "计算结果: " << expr->evaluate() << std::endl;

    delete expr;

    return 0;
}
```


## ==========================================================================
### 📖 第四节: 课后习题
## ==========================================================================

1. 基础题：手动实现BST的完整操作。
   - 插入、删除、查找、遍历（全部四种）
   - 查找最小值和最大值
   - 查找前驱和后继节点
   - 判断一棵树是否为BST

2. 应用题：实现BST的中序后继查找器。
   - 给定一个BST和一个目标值
   - 找出BST中比目标值大的最小节点（中序后继）
   - 要求O(h)时间，h为树高

3. 进阶题：实现AVL树的完整操作并验证正确性。
   - 插入和删除后验证平衡性
   - 随机插入大量节点，统计树高和log n的关系
   - 与普通BST进行性能对比

4. 综合题：实现一个基于BST的订单簿系统。
   - 使用BST按价格排序存储买卖订单
   - 支持添加订单、取消订单、执行交易
   - 输出当前最优买卖价格

5. 挑战题：实现一个B树（B-Tree）。
   - 多路平衡搜索树，广泛应用于数据库索引
   - 实现最小度数为t的B树
   - 支持插入、删除、查找
   - 验证B树的高度平衡性质

## ==========================================================================


## ==========================================================================
### 📝 章节测试
## ==========================================================================

> [!question] 判断题 1
> 二叉搜索树（BST）中，左子树所有节点的值都小于根节点 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: BST的定义：对于任意节点，其左子树所有节点的值都小于该节点的值，右子树所有节点的值都大于该节点的值。

> [!question] 判断题 2
> BST的中序遍历结果一定是有序的（升序） （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: 中序遍历顺序为"左-根-右"，由于BST左<根<右的性质，中序遍历必然按升序输出所有节点值。这是BST的重要性质。

> [!question] 判断题 3
> AVL树是一种严格平衡的二叉搜索树，任意节点左右子树高度差不超过1 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: AVL树的平衡条件：任意节点的平衡因子（左子树高度-右子树高度）的绝对值不超过1。通过旋转操作维持这个性质。

> [!question] 判断题 4
> 在最坏情况下，BST的查找时间复杂度为O(n) （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: 如果元素按有序顺序（升序或降序）插入BST，树会退化为链表（每个节点只有一个子节点），此时查找时间为O(n)。AVL树通过平衡保证O(log n)。

> [!question] 判断题 5
> 二叉树的前序遍历顺序为：左子树 → 根节点 → 右子树 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: 前序遍历的顺序是"根→左→右"。左→根→右是中序遍历，左→右→根是后序遍历。

> [!question] 判断题 6
> AVL树的插入操作最多需要一次旋转（单旋或双旋）即可恢复平衡 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: AVL树插入后最多只有一个节点失衡（最近的失衡祖先），对该节点进行一次旋转（LL/RR单旋或LR/RL双旋）即可恢复整棵树的平衡。

> [!question] 判断题 7
> 完全二叉树一定是BST （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: 完全二叉树只要求节点从上到下、从左到右紧密排列，不要求满足BST的大小顺序性质。堆是完全二叉树但不是BST。

> [!question] 判断题 8
> 删除BST中有两个子节点的节点时，可以用其中序后继替换 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: 删除有两个子节点的BST节点时，找到其中序后继（右子树中最小节点）或中序前驱（左子树中最大节点），用其值替换待删节点，再删除那个后继/前驱节点。

> [!question] 判断题 9
> 一棵含有n个节点的AVL树，其高度为O(log n) （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: AVL树保证任意节点左右子树高度差≤1，可以证明高度最大约为1.44*log2(n)，因此高度为O(log n)，保证了查找/插入/删除都是O(log n)。

> [!question] 判断题 10
> 已知前序遍历和后序遍历，可以唯一确定一棵二叉树 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: 前序+后序不能唯一确定二叉树（当某节点只有一个子节点时有歧义）。唯一确定需要：前序+中序，或后序+中序。

---

> [!question] 选择题 1
> 以下哪个遍历方式可以得到BST中所有元素的升序排列？
> - [ ] A. 前序遍历
> - [ ] B. 中序遍历
> - [ ] C. 后序遍历
> - [ ] D. 层序遍历
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: BST的中序遍历（左-根-右）按升序输出所有节点值，因为左子树<根<右子树，递归地对所有子树都成立。

> [!question] 选择题 2
> 向一棵空的BST中依次插入 5, 3, 7, 2, 4, 6, 8，树的高度是？
> - [ ] A. 2
> - [ ] B. 3
> - [ ] C. 4
> - [ ] D. 7
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: 插入后形成完美二叉树：5为根，3和7为第二层，2,4,6,8为第三层。高度=3（根到叶子的路径长度为2，层数为3）。

> [!question] 选择题 3
> AVL树中，平衡因子（Balance Factor）的定义是？
> - [ ] A. 左子树节点数 - 右子树节点数
> - [ ] B. 左子树高度 - 右子树高度
> - [ ] C. 左子节点值 - 右子节点值
> - [ ] D. 树的高度 - log(n)
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: 平衡因子 = 左子树高度 - 右子树高度。AVL树要求所有节点的平衡因子∈{-1, 0, 1}，否则需要旋转修复。

> [!question] 选择题 4
> AVL树中，LL型失衡需要执行什么旋转操作？
> - [ ] A. 对失衡节点左旋
> - [ ] B. 对失衡节点右旋
> - [ ] C. 先左旋再右旋
> - [ ] D. 先右旋再左旋
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: LL型（插入到左子树的左子树）导致左偏，对失衡节点执行一次右旋即可恢复平衡。RR型则执行左旋。LR和RL需要双旋。

> [!question] 选择题 5
> 一棵含有7个节点的完全二叉树有几个叶子节点？
> - [ ] A. 3
> - [ ] B. 4
> - [ ] C. 5
> - [ ] D. 2
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: 7个节点的完全二叉树：第1层1个，第2层2个，第3层4个。第3层的4个节点都是叶子。公式：⌈n/2⌉ = ⌈7/2⌉ = 4。

> [!question] 选择题 6
> BST中查找最小值应该？
> - [ ] A. 一直往右走到底
> - [ ] B. 一直往左走到底
> - [ ] C. 返回根节点
> - [ ] D. 进行中序遍历取第一个
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: BST中左子树的值都小于根，因此最小值一定在最左端。从根节点一直往左走到没有左子节点为止，该节点即为最小值。时间O(h)。

> [!question] 选择题 7
> 以下哪种树不是自平衡二叉搜索树？
> - [ ] A. AVL树
> - [ ] B. 红黑树
> - [ ] C. B树
> - [ ] D. Splay树
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > 
> > **解析**: B树是多路搜索树（每个节点可以有多个子节点），不是二叉树。AVL树、红黑树、Splay树都是自平衡的二叉搜索树。

> [!question] 选择题 8
> 层序遍历二叉树使用的数据结构是？
> - [ ] A. 栈
> - [ ] B. 队列
> - [ ] C. 优先队列
> - [ ] D. 哈希表
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: 层序遍历（从上到下、从左到右逐层访问）使用队列。将根入队，每次出队一个节点并将其子节点入队，保证了同层节点按顺序访问。

> [!question] 选择题 9
> AVL树删除一个节点后，最多需要几次旋转才能恢复平衡？
> - [ ] A. 1次
> - [ ] B. 2次
> - [ ] C. O(log n)次
> - [ ] D. O(n)次
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > 
> > **解析**: AVL树插入最多需要1次旋转，但删除可能需要从被删节点到根的路径上每个祖先节点都进行旋转，最坏需要O(log n)次旋转。

> [!question] 选择题 10
> 给定中序遍历 [1,2,3,4,5] 和前序遍历 [3,1,2,4,5]，根节点是？
> - [ ] A. 1
> - [ ] B. 3
> - [ ] C. 5
> - [ ] D. 4
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: 前序遍历的第一个元素就是根节点。前序为[3,1,2,4,5]，所以根节点为3。在中序中3将序列分为左子树[1,2]和右子树[4,5]。

---

### 💻 编程大题

> [!note] 编程题 1：实现完整的AVL树
> **要求**：
> 1. 实现AVL树类，支持以下操作：
>    - `insert(int val)` — 插入并自动平衡
>    - `remove(int val)` — 删除并自动平衡
>    - `bool find(int val)` — 查找
>    - `int getMin()` / `int getMax()` — 最值
>    - 四种遍历（前序、中序、后序、层序）
> 2. 实现四种旋转：LL（右旋）、RR（左旋）、LR（先左旋再右旋）、RL（先右旋再左旋）
> 3. 正确维护每个节点的高度和平衡因子
> 4. 验证：随机插入/删除1000个节点后，检查所有节点平衡因子∈{-1,0,1}
> 5. 打印树形结构（可视化）
>
> **提示**: 插入/删除后从当前节点回溯到根，逐层检查并修复平衡

> [!note] 编程题 2：BST转有序双向链表
> **要求**：
> 1. 给定一棵BST，将其原地转换为排序的双向循环链表
> 2. 要求：
>    - 不能创建新节点，只能修改已有节点的指针
>    - 左指针作为prev，右指针作为next
>    - 转换后的链表按升序排列
>    - 头节点的prev指向尾节点，尾节点的next指向头节点（循环）
> 3. 实现两种方法：
>    - 方法一：中序遍历 + 前驱指针记录
>    - 方法二：分治法（递归地转换左子树和右子树，再连接）
> 4. 时间O(n)，空间O(log n)递归栈
>
> **提示**: 中序遍历时维护上一个访问的节点，当前节点的left指向它，它的right指向当前节点

> [!note] 编程题 3：根据遍历序列重建二叉树
> **要求**：
> 1. 实现以下重建功能：
>    - 给定前序+中序遍历，重建二叉树
>    - 给定后序+中序遍历，重建二叉树
> 2. 实现步骤：
>    - 从前序/后序确定根节点
>    - 在中序中找到根的位置，划分左右子树
>    - 递归重建左右子树
> 3. 优化：使用哈希表存储中序遍历中各值的位置，实现O(1)查找
> 4. 验证：重建后对树进行前序/中序/后序遍历，与原输入对比
> 5. 处理异常：输入不合法（无法构成有效树）时报错
>
> **提示**: 前序第一个为根，在中序中找到根的位置idx，左子树元素数=idx-inStart

### 🔗 推荐练习题（洛谷）

| 题号 | 题目 | 难度 | 知识点 |
|------|------|------|--------|
| [P3369](https://www.luogu.com.cn/problem/P3369) | 普通平衡树 | 提高 | BST/AVL/Treap基本操作 |
| [P1364](https://www.luogu.com.cn/problem/P1364) | 医院设置 | 普及 | 树的遍历、带权路径 |

---

## --------------------------------------------------------------------------
## 🔗 知识网络
## --------------------------------------------------------------------------

- **上一章**: [[数据结构/H_图_Graph]] | **返回**: [[目录]]
- **相关**: [[数据结构/E_红黑树_RedBlackTree]] | [[算法技巧/二分查找]]
