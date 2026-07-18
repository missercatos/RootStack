

建议先阅读: [[I_树_Tree_BST_AVL|I 树 BST AVL]]

---

## 原理

字典树（Trie），又称前缀树，是一种用于高效存储和检索字符串集合的树形数据结构。每个节点代表一个字符，从根到某标记节点的路径构成一个完整字符串。

### 核心特征

- 根节点不包含字符，其余每个节点包含一个字符
- 从根到某节点的路径上字符连接即为该节点对应的前缀
- 每个节点的子节点包含的字符各不相同
- 标记节点 isEnd 表示从根到该节点构成完整单词

### 复杂度

| 操作 | 时间复杂度 | 说明 |
|------|-----------|------|
| 插入 | O(m) | m 为字符串长度 |
| 查找 | O(m) | 精确匹配 |
| 前缀匹配 | O(m) | 找到前缀末尾节点 |
| 删除 | O(m) | 沿路径回溯清理 |

空间复杂度: 最坏 O(字符集大小 * 总字符串长度)，共享前缀可大幅节省空间。

### Trie vs 哈希表

| 特性 | Trie | 哈希表 |
|------|------|--------|
| 精确查找 | O(m) | O(1) 平均 |
| 前缀查询 | O(m) 天然支持 | 不支持 |
| 字典序遍历 | 天然支持 | 需排序 |
| 空间 | 前缀共享时高效 | 不含指针开销 |

---

## 实现

### 数组版（仅小写字母）

```cpp
#include <iostream>
#include <string>

class Trie {
private:
    struct TrieNode {
        TrieNode* children[26] = {};
        bool isEnd = false;
        int prefixCount = 0; // 经过该节点的单词数
    };
    TrieNode* root;

    void destroy(TrieNode* node) {
        if (!node) return;
        for (int i = 0; i < 26; ++i)
            destroy(node->children[i]);
        delete node;
    }

public:
    Trie() { root = new TrieNode(); }
    ~Trie() { destroy(root); }

    void insert(const std::string& word) {
        TrieNode* cur = root;
        for (char c : word) {
            int idx = c - 'a';
            if (!cur->children[idx])
                cur->children[idx] = new TrieNode();
            cur = cur->children[idx];
            cur->prefixCount++;
        }
        cur->isEnd = true;
    }

    bool search(const std::string& word) {
        TrieNode* cur = root;
        for (char c : word) {
            int idx = c - 'a';
            if (!cur->children[idx]) return false;
            cur = cur->children[idx];
        }
        return cur->isEnd;
    }

    bool startsWith(const std::string& prefix) {
        TrieNode* cur = root;
        for (char c : prefix) {
            int idx = c - 'a';
            if (!cur->children[idx]) return false;
            cur = cur->children[idx];
        }
        return true;
    }

    int countPrefix(const std::string& prefix) {
        TrieNode* cur = root;
        for (char c : prefix) {
            int idx = c - 'a';
            if (!cur->children[idx]) return 0;
            cur = cur->children[idx];
        }
        return cur->prefixCount;
    }
};
```

### 01 字典树（求最大异或值）

```cpp
#include <vector>
#include <algorithm>

class XORTrie {
private:
    struct Node {
        Node* children[2] = {};
    };
    Node* root;

public:
    XORTrie() { root = new Node(); }

    void insert(int num) {
        Node* cur = root;
        for (int i = 31; i >= 0; --i) {
            int bit = (num >> i) & 1;
            if (!cur->children[bit])
                cur->children[bit] = new Node();
            cur = cur->children[bit];
        }
    }

    int queryMaxXor(int num) {
        Node* cur = root;
        int result = 0;
        for (int i = 31; i >= 0; --i) {
            int bit = (num >> i) & 1;
            int want = 1 - bit; // 贪心：尽量走相反方向
            if (cur->children[want]) {
                result |= (1 << i);
                cur = cur->children[want];
            } else {
                cur = cur->children[bit];
            }
        }
        return result;
    }

    int findMaxXorPair(const std::vector<int>& nums) {
        int maxXor = 0;
        for (int num : nums) {
            insert(num);
            maxXor = std::max(maxXor, queryMaxXor(num));
        }
        return maxXor;
    }
};
```

---

## 应用场景

- **搜索引擎自动补全**: 输入前缀，DFS 收集所有匹配词
- **拼写检查**: 查询字典中是否存在该词，不存在则给出前缀建议
- **IP 路由最长前缀匹配**: 二进制 Trie 用于路由器转发表
- **敏感词过滤**: Trie 存储敏感词库，O(n*len) 扫描文本

---

## 练习

| 题号 | 题目 | 难度 | 知识点 |
|------|------|------|--------|
| P2580 | 于是他错误的点名开始了 | 普及 | Trie 插入与查找 |
| P8306 | 模板字典树 | 普及 | Trie 基本操作 |
| P4551 | 最长异或路径 | 提高 | 01 字典树 |
