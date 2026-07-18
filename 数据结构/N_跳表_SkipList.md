

建议先阅读: [[D_链表_LinkedList|D 链表 LinkedList]]

---

## 原理

跳表（Skip List）是一种基于有序链表 + 多级随机索引的概率性数据结构，由 William Pugh 于 1990 年提出，作为平衡树的替代方案。它是 Redis 有序集合（ZSet）的底层实现。

### 核心思想

- 最底层（Level 0）是包含所有元素的有序链表
- 上层是下层的随机索引子集
- 每个节点以概率 p（通常 0.5 或 0.25）随机决定是否出现在上一层
- 查找时从最高层开始，快速跳过大量元素，逐层下降到目标

### 复杂度（期望）

| 操作 | 时间复杂度 | 说明 |
|------|-----------|------|
| 查找 | O(log n) | 期望比较次数 ~ log_{1/p}(n) |
| 插入 | O(log n) | 随机决定层数 + 更新指针 |
| 删除 | O(log n) | 找到节点 + 更新各层前驱指针 |
| 空间 | O(n) | 期望指针数 = n/(1-p) |

### 与平衡树的对比

| 特性 | 跳表 | 红黑树/AVL |
|------|------|-----------|
| 实现难度 | 中等 | 困难 |
| 是否需要旋转 | 否 | 是 |
| 并发友好 | 是（局部修改） | 困难（全局旋转） |
| 最坏情况 | O(n) 概率极低 | O(log n) 确定 |
| 范围查询 | 天然支持 | 需中序遍历 |

---

## 实现

```cpp
#include <iostream>
#include <vector>
#include <random>
#include <climits>

template <typename K, typename V>
class SkipList {
private:
    struct Node {
        K key;
        V value;
        std::vector<Node*> forward; // 各层后继指针
        Node(const K& k, const V& v, int level)
            : key(k), value(v), forward(level + 1, nullptr) {}
    };

    Node* header;
    int maxLevel;
    int currentLevel;
    double probability;
    std::mt19937 rng;
    std::uniform_real_distribution<double> dist;

    int randomLevel() {
        int level = 0;
        while (dist(rng) < probability && level < maxLevel)
            ++level;
        return level;
    }

public:
    SkipList(int maxLvl = 16, double p = 0.5)
        : maxLevel(maxLvl), currentLevel(0), probability(p),
          rng(std::random_device{}()), dist(0.0, 1.0) {
        header = new Node(K(), V(), maxLevel);
    }

    ~SkipList() {
        Node* cur = header->forward[0];
        while (cur) {
            Node* next = cur->forward[0];
            delete cur;
            cur = next;
        }
        delete header;
    }

    bool search(const K& key, V& value) {
        Node* cur = header;
        for (int i = currentLevel; i >= 0; --i) {
            while (cur->forward[i] && cur->forward[i]->key < key)
                cur = cur->forward[i];
        }
        cur = cur->forward[0];
        if (cur && cur->key == key) { value = cur->value; return true; }
        return false;
    }

    void insert(const K& key, const V& value) {
        std::vector<Node*> update(maxLevel + 1, nullptr);
        Node* cur = header;

        // 记录每层的前驱
        for (int i = currentLevel; i >= 0; --i) {
            while (cur->forward[i] && cur->forward[i]->key < key)
                cur = cur->forward[i];
            update[i] = cur;
        }
        cur = cur->forward[0];

        // 键已存在，更新值
        if (cur && cur->key == key) { cur->value = value; return; }

        int newLevel = randomLevel();
        if (newLevel > currentLevel) {
            for (int i = currentLevel + 1; i <= newLevel; ++i)
                update[i] = header;
            currentLevel = newLevel;
        }

        Node* newNode = new Node(key, value, newLevel);
        for (int i = 0; i <= newLevel; ++i) {
            newNode->forward[i] = update[i]->forward[i];
            update[i]->forward[i] = newNode;
        }
    }

    bool remove(const K& key) {
        std::vector<Node*> update(maxLevel + 1, nullptr);
        Node* cur = header;

        for (int i = currentLevel; i >= 0; --i) {
            while (cur->forward[i] && cur->forward[i]->key < key)
                cur = cur->forward[i];
            update[i] = cur;
        }
        cur = cur->forward[0];

        if (!cur || cur->key != key) return false;

        for (int i = 0; i <= currentLevel; ++i) {
            if (update[i]->forward[i] != cur) break;
            update[i]->forward[i] = cur->forward[i];
        }
        delete cur;

        while (currentLevel > 0 && !header->forward[currentLevel])
            --currentLevel;

        return true;
    }

    void print() {
        for (int i = currentLevel; i >= 0; --i) {
            std::cout << "Level " << i << ": ";
            Node* cur = header->forward[i];
            while (cur) {
                std::cout << "(" << cur->key << "," << cur->value << ") ";
                cur = cur->forward[i];
            }
            std::cout << std::endl;
        }
    }
};
```

---

## 应用场景

- **Redis 有序集合（ZSet）**: 跳表 + 哈希表，支持按分数排序、范围查询、排名
- **LevelDB MemTable**: 内存中使用跳表存储键值对，保证有序性
- **内存数据库索引**: 需要有序查找 + 范围扫描的场景

---

## 练习

| 题号 | 题目 | 难度 | 知识点 |
|------|------|------|--------|
| P3369 | 普通平衡树 | 提高 | 可用跳表替代平衡树实现 |
| P6136 | 普通平衡树（加强版） | 提高+ | 跳表或平衡树 |
