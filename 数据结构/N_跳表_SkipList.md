

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

```c
#include <stdlib.h>
#include <time.h>

#define MAX_LEVEL 16

typedef struct SLNode {
    int key;
    int value;
    struct SLNode** forward;  // 各层后继指针
} SLNode;

typedef struct {
    SLNode* header;
    int currentLevel;
    double probability;
} SkipList;

static SLNode* sl_create_node(int key, int value, int level) {
    SLNode* node = malloc(sizeof(SLNode));
    node->key = key;
    node->value = value;
    node->forward = calloc(level + 1, sizeof(SLNode*));
    return node;
}

static int sl_random_level(double prob) {
    int level = 0;
    while ((double)rand() / RAND_MAX < prob && level < MAX_LEVEL)
        level++;
    return level;
}

void sl_init(SkipList* sl) {
    srand((unsigned)time(NULL));
    sl->probability = 0.5;
    sl->currentLevel = 0;
    sl->header = sl_create_node(0, 0, MAX_LEVEL);
}

void sl_destroy(SkipList* sl) {
    SLNode* cur = sl->header->forward[0];
    while (cur) {
        SLNode* next = cur->forward[0];
        free(cur->forward);
        free(cur);
        cur = next;
    }
    free(sl->header->forward);
    free(sl->header);
}

int sl_search(SkipList* sl, int key, int* out_value) {
    SLNode* cur = sl->header;
    for (int i = sl->currentLevel; i >= 0; i--) {
        while (cur->forward[i] && cur->forward[i]->key < key)
            cur = cur->forward[i];
    }
    cur = cur->forward[0];
    if (cur && cur->key == key) {
        *out_value = cur->value;
        return 1;
    }
    return 0;
}

void sl_insert(SkipList* sl, int key, int value) {
    SLNode* update[MAX_LEVEL + 1];
    SLNode* cur = sl->header;

    for (int i = sl->currentLevel; i >= 0; i--) {
        while (cur->forward[i] && cur->forward[i]->key < key)
            cur = cur->forward[i];
        update[i] = cur;
    }
    cur = cur->forward[0];

    if (cur && cur->key == key) {
        cur->value = value;
        return;
    }

    int new_level = sl_random_level(sl->probability);
    if (new_level > sl->currentLevel) {
        for (int i = sl->currentLevel + 1; i <= new_level; i++)
            update[i] = sl->header;
        sl->currentLevel = new_level;
    }

    SLNode* new_node = sl_create_node(key, value, new_level);
    for (int i = 0; i <= new_level; i++) {
        new_node->forward[i] = update[i]->forward[i];
        update[i]->forward[i] = new_node;
    }
}

int sl_remove(SkipList* sl, int key) {
    SLNode* update[MAX_LEVEL + 1];
    SLNode* cur = sl->header;

    for (int i = sl->currentLevel; i >= 0; i--) {
        while (cur->forward[i] && cur->forward[i]->key < key)
            cur = cur->forward[i];
        update[i] = cur;
    }
    cur = cur->forward[0];

    if (!cur || cur->key != key) return 0;

    for (int i = 0; i <= sl->currentLevel; i++) {
        if (update[i]->forward[i] != cur) break;
        update[i]->forward[i] = cur->forward[i];
    }
    free(cur->forward);
    free(cur);

    while (sl->currentLevel > 0 && !sl->header->forward[sl->currentLevel])
        sl->currentLevel--;

    return 1;
}
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

> 力扣 (LeetCode) 有对应题型，竞赛方向推荐力扣/Codeforces。
