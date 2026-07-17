# O B树 B-Tree / B+ Tree

建议先阅读: [[I_树_Tree_BST_AVL|I 树 BST AVL]]

---

## 原理

B 树是为磁盘存储优化的自平衡多路搜索树。与二叉树不同，B 树的每个节点可以有多个子节点和多个键值，使得树更"扁平"，大幅减少磁盘 IO 次数。

### 设计动机

磁盘访问比内存慢约 10^5 倍，以页为单位（通常 4KB）读写。二叉搜索树高度为 log2(n)，100 万数据需要约 20 次 IO；而 B 树一个节点可存数百个键，同样数据量只需 2-3 次 IO。

### B 树的定义（m 阶）

1. 每个节点最多 m 个子节点
2. 非根非叶节点至少有 ceil(m/2) 个子节点
3. 根至少 2 个子节点（除非是叶子）
4. 有 k 个子节点的节点包含 k-1 个键
5. 所有叶子在同一层

### B 树 vs B+ 树

| 特性 | B 树 | B+ 树 |
|------|------|-------|
| 数据存储 | 所有节点存数据 | 仅叶子存数据，内部只存键 |
| 叶子链接 | 无 | 叶子用链表相连 |
| 范围查询 | 需中序遍历 | O(log n + k)，k 为结果数 |
| 内部节点容量 | 较小 | 更大（树更矮） |
| 典型应用 | 文件系统（HFS+） | 数据库索引（MySQL InnoDB） |

---

## 实现

### B 树插入

```cpp
#include <vector>
#include <iostream>

template <typename T>
class BTree {
private:
    struct Node {
        std::vector<T> keys;
        std::vector<Node*> children;
        bool isLeaf;
        Node(bool leaf) : isLeaf(leaf) {}
    };

    Node* root;
    int t; // 最小度数，节点键数在 [t-1, 2t-1]

    // 分裂满子节点
    void splitChild(Node* parent, int idx) {
        Node* child = parent->children[idx];
        Node* newNode = new Node(child->isLeaf);
        int mid = t - 1;

        // 后半部分键移入新节点
        for (int i = mid + 1; i < child->keys.size(); ++i)
            newNode->keys.push_back(child->keys[i]);
        // 非叶子还需移动子节点
        if (!child->isLeaf) {
            for (int i = t; i < child->children.size(); ++i)
                newNode->children.push_back(child->children[i]);
            child->children.resize(t);
        }

        // 中间键提升到父节点
        parent->keys.insert(parent->keys.begin() + idx, child->keys[mid]);
        parent->children.insert(parent->children.begin() + idx + 1, newNode);
        child->keys.resize(mid);
    }

    // 插入到非满节点
    void insertNonFull(Node* node, const T& key) {
        int i = node->keys.size() - 1;
        if (node->isLeaf) {
            node->keys.push_back(T());
            while (i >= 0 && key < node->keys[i]) {
                node->keys[i + 1] = node->keys[i];
                --i;
            }
            node->keys[i + 1] = key;
        } else {
            while (i >= 0 && key < node->keys[i]) --i;
            ++i;
            if (node->children[i]->keys.size() == 2 * t - 1) {
                splitChild(node, i);
                if (key > node->keys[i]) ++i;
            }
            insertNonFull(node->children[i], key);
        }
    }

    bool searchNode(Node* node, const T& key) {
        int i = 0;
        while (i < node->keys.size() && key > node->keys[i]) ++i;
        if (i < node->keys.size() && node->keys[i] == key) return true;
        if (node->isLeaf) return false;
        return searchNode(node->children[i], key);
    }

    void traverseNode(Node* node) {
        for (int i = 0; i < node->keys.size(); ++i) {
            if (!node->isLeaf) traverseNode(node->children[i]);
            std::cout << node->keys[i] << " ";
        }
        if (!node->isLeaf) traverseNode(node->children[node->keys.size()]);
    }

    void destroy(Node* node) {
        if (!node) return;
        if (!node->isLeaf)
            for (auto* child : node->children) destroy(child);
        delete node;
    }

public:
    BTree(int degree) : root(nullptr), t(degree) {}
    ~BTree() { destroy(root); }

    void insert(const T& key) {
        if (!root) {
            root = new Node(true);
            root->keys.push_back(key);
            return;
        }
        if (root->keys.size() == 2 * t - 1) {
            Node* newRoot = new Node(false);
            newRoot->children.push_back(root);
            splitChild(newRoot, 0);
            root = newRoot;
        }
        insertNonFull(root, key);
    }

    bool search(const T& key) {
        return root ? searchNode(root, key) : false;
    }

    void traverse() {
        if (root) traverseNode(root);
        std::cout << std::endl;
    }
};
```

### B+ 树（简化版）

```cpp
template <typename T>
class BPlusTree {
private:
    struct Node {
        std::vector<T> keys;
        std::vector<Node*> children; // 仅内部节点
        Node* next; // 叶子链表
        bool isLeaf;
        Node(bool leaf) : next(nullptr), isLeaf(leaf) {}
    };

    Node* root;
    int order;

    Node* findLeaf(const T& key) {
        Node* cur = root;
        while (!cur->isLeaf) {
            int i = 0;
            while (i < cur->keys.size() && key >= cur->keys[i]) ++i;
            cur = cur->children[i];
        }
        return cur;
    }

public:
    BPlusTree(int ord = 4) : root(nullptr), order(ord) {}

    void insert(const T& key) {
        if (!root) {
            root = new Node(true);
            root->keys.push_back(key);
            return;
        }
        Node* leaf = findLeaf(key);
        // 找到插入位置
        int pos = 0;
        while (pos < leaf->keys.size() && leaf->keys[pos] < key) ++pos;
        leaf->keys.insert(leaf->keys.begin() + pos, key);

        // 叶子溢出，需要分裂（简化：只处理叶子分裂）
        if (leaf->keys.size() >= order) {
            Node* newLeaf = new Node(true);
            int mid = leaf->keys.size() / 2;
            for (int i = mid; i < leaf->keys.size(); ++i)
                newLeaf->keys.push_back(leaf->keys[i]);
            leaf->keys.resize(mid);
            newLeaf->next = leaf->next;
            leaf->next = newLeaf;

            // 如果 leaf 是根，创建新根
            if (leaf == root) {
                Node* newRoot = new Node(false);
                newRoot->keys.push_back(newLeaf->keys[0]);
                newRoot->children.push_back(leaf);
                newRoot->children.push_back(newLeaf);
                root = newRoot;
            }
            // TODO: 处理内部节点递归分裂
        }
    }

    bool search(const T& key) {
        if (!root) return false;
        Node* leaf = findLeaf(key);
        for (auto& k : leaf->keys)
            if (k == key) return true;
        return false;
    }

    std::vector<T> rangeSearch(const T& low, const T& high) {
        std::vector<T> result;
        if (!root) return result;
        Node* leaf = findLeaf(low);
        while (leaf) {
            for (auto& k : leaf->keys) {
                if (k > high) return result;
                if (k >= low) result.push_back(k);
            }
            leaf = leaf->next;
        }
        return result;
    }
};
```

---

## 应用场景

- **数据库索引**: MySQL InnoDB 使用 B+ 树作为主键索引和二级索引
- **文件系统**: NTFS、HFS+ 等使用 B 树/B+ 树管理文件元数据
- **键值存储**: LevelDB 用 B+ 树/SSTable 管理持久化数据

---

## 练习

| 题号 | 题目 | 难度 | 知识点 |
|------|------|------|--------|
| P3369 | 普通平衡树 | 提高 | 可用 B 树替代平衡树 |
| 数据库索引模拟 | 手写项目 | 综合 | B+ 树磁盘模拟 |
