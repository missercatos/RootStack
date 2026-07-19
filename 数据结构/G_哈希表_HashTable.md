

建议先阅读: [[A_容器_Container|A 容器 Container]]

---

## 原理

哈希表（Hash Table）通过哈希函数将键映射到数组的某个位置，实现 O(1) 平均时间复杂度的插入、删除和查找操作。

### 核心组件

- **哈希函数**: 将任意大小的键映射到固定范围的整数（数组索引），需计算快、分布均匀、确定性
- **桶数组**: 存储键值对的连续内存
- **冲突解决**: 处理不同键映射到同一位置的策略

### 冲突解决方法

1. **链地址法（拉链法）**: 每个桶维护一个链表，冲突的键值对放入同一桶的链表中。C++ unordered_map 默认使用此方法
2. **开放地址法**: 发生冲突时寻找下一个空桶：
   - 线性探测: `index = (hash + i) % size`
   - 二次探测: `index = (hash + i^2) % size`
   - 双重哈希: `index = (hash1 + i * hash2) % size`

### 时间复杂度

| 操作 | 平均 | 最坏 |
|------|------|------|
| 插入 | O(1) | O(n) |
| 删除 | O(1) | O(n) |
| 查找 | O(1) | O(n) |

空间复杂度: O(n + bucket_count)，负载因子（元素数/桶数）触发 rehash。

---

## 实现

### 链地址法 HashMap

```c
#include <stdlib.h>
#include <string.h>

typedef struct Entry {
    int key;
    int value;
    struct Entry* next;
} Entry;

typedef struct {
    Entry** buckets;   // 桶数组，每个桶是一个链表的头指针
    size_t bucket_count;
    size_t num_elements;
    float max_load_factor;
} HashMap;

size_t hash_int(int key, size_t bucket_count) {
    return (size_t)((unsigned)key) % bucket_count;
}

void hm_init(HashMap* hm, size_t init_size) {
    hm->bucket_count = init_size;
    hm->buckets = calloc(init_size, sizeof(Entry*));
    hm->num_elements = 0;
    hm->max_load_factor = 0.75f;
}

void hm_destroy(HashMap* hm) {
    for (size_t i = 0; i < hm->bucket_count; i++) {
        Entry* e = hm->buckets[i];
        while (e) {
            Entry* tmp = e;
            e = e->next;
            free(tmp);
        }
    }
    free(hm->buckets);
    hm->buckets = NULL;
    hm->bucket_count = 0;
    hm->num_elements = 0;
}

static int hm_rehash(HashMap* hm, size_t new_bucket_count) {
    Entry** new_buckets = calloc(new_bucket_count, sizeof(Entry*));
    if (!new_buckets) return -1;
    for (size_t i = 0; i < hm->bucket_count; i++) {
        Entry* e = hm->buckets[i];
        while (e) {
            Entry* next = e->next;
            size_t idx = hash_int(e->key, new_bucket_count);
            e->next = new_buckets[idx];
            new_buckets[idx] = e;
            e = next;
        }
    }
    free(hm->buckets);
    hm->buckets = new_buckets;
    hm->bucket_count = new_bucket_count;
    return 0;
}

int hm_insert(HashMap* hm, int key, int value) {
    if ((hm->num_elements + 1.0f) / hm->bucket_count > hm->max_load_factor)
        if (hm_rehash(hm, hm->bucket_count * 2) != 0) return -1;

    size_t idx = hash_int(key, hm->bucket_count);
    Entry* e = hm->buckets[idx];
    while (e) {
        if (e->key == key) {
            e->value = value;  // 更新
            return 0;
        }
        e = e->next;
    }
    Entry* new_e = malloc(sizeof(Entry));
    if (!new_e) return -1;
    new_e->key = key;
    new_e->value = value;
    new_e->next = hm->buckets[idx];
    hm->buckets[idx] = new_e;
    hm->num_elements++;
    return 0;
}

int hm_find(HashMap* hm, int key, int* out_value) {
    size_t idx = hash_int(key, hm->bucket_count);
    Entry* e = hm->buckets[idx];
    while (e) {
        if (e->key == key) {
            *out_value = e->value;
            return 0;
        }
        e = e->next;
    }
    return -1;
}

int hm_remove(HashMap* hm, int key) {
    size_t idx = hash_int(key, hm->bucket_count);
    Entry* e = hm->buckets[idx];
    Entry* prev = NULL;
    while (e) {
        if (e->key == key) {
            if (prev) prev->next = e->next;
            else hm->buckets[idx] = e->next;
            free(e);
            hm->num_elements--;
            return 0;
        }
        prev = e;
        e = e->next;
    }
    return -1;
}

size_t hm_size(HashMap* hm) { return hm->num_elements; }
int hm_empty(HashMap* hm) { return hm->num_elements == 0; }
```

### 字符串哈希

```c
#include <string.h>

// BKDR Hash
size_t bkdr_hash(const char* s) {
    size_t hash = 0;
    size_t seed = 131;
    while (*s)
        hash = hash * seed + (unsigned char)*s++;
    return hash;
}

// 多项式滚动哈希（前缀哈希，O(1) 获取子串哈希值）
typedef struct {
    unsigned long long* h;
    unsigned long long* p;
    size_t len;
} StringHasher;

void sh_init(StringHasher* sh, const char* s) {
    sh->len = strlen(s);
    sh->h = malloc((sh->len + 1) * sizeof(unsigned long long));
    sh->p = malloc((sh->len + 1) * sizeof(unsigned long long));
    sh->p[0] = 1;
    for (size_t i = 0; i < sh->len; i++) {
        sh->h[i + 1] = sh->h[i] * 131 + (unsigned char)s[i];
        sh->p[i + 1] = sh->p[i] * 131;
    }
}

void sh_destroy(StringHasher* sh) {
    free(sh->h);
    free(sh->p);
}

// 子串 s[l..r] 的哈希值（包含两端）
unsigned long long sh_get(StringHasher* sh, int l, int r) {
    return sh->h[r + 1] - sh->h[l] * sh->p[r - l + 1];
}
```

---

## 各语言标准库对比

| 语言 | 哈希集合 | 哈希映射 |
|------|----------|----------|
| C | 无（手写） | 无（手写） |
| C++ | unordered_set | unordered_map |
| Java | HashSet | HashMap |
| Python | set | dict |
| Rust | HashSet | HashMap |

---

## 应用场景

- **缓存系统**: O(1) 查找，如 LRU 缓存（哈希表 + 双向链表）
- **词频统计**: 用 unordered_map<string, int> 统计文本中各单词出现次数
- **去重**: 用 unordered_set 快速判重
- **两数之和**: O(n) 一遍扫描，哈希表记录已遍历元素

---

## 练习

| 题号 | 题目 | 难度 | 知识点 |
|------|------|------|--------|
| P3370 | 字符串哈希 | 普及 | 哈希函数、字符串去重 |
| P3405 | Cities and States | 普及+ | 哈希计数 |
| P4305 | 字符串哈希 | 普及 | 滚动哈希 |
