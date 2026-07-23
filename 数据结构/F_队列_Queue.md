

建议先阅读: [[A_容器_Container|A 容器 Container]], [[B_栈_Stack|B 栈 Stack]]

---

## 原理

队列（Queue）是一种受限的线性数据结构，遵循先进先出（FIFO, First In First Out）原则。元素只能从队尾插入，从队首删除。

### 核心操作

| 操作 | 描述 | 时间复杂度 |
|------|------|-----------|
| push / enqueue | 在队尾插入元素 | O(1) |
| pop / dequeue | 删除队首元素 | O(1) |
| front | 获取队首元素 | O(1) |
| back | 获取队尾元素 | O(1) |
| empty | 判断队列是否为空 | O(1) |
| size | 返回队列中元素个数 | O(1) |

### 底层实现方式

- **循环队列（数组）**: 通过取模运算避免假溢出，固定容量或动态扩容
- **链表队列**: head 指向队首（出队端），tail 指向队尾（入队端），无容量限制
- **双端队列（deque）**: 分段连续存储，两端都可插入/删除，也支持随机访问

### 假溢出与循环队列

普通数组实现中，队首元素出队后空间被浪费，tail 可能到达数组末尾无法入队。循环队列通过 `(index + 1) % capacity` 使 tail 绕回数组开头，充分利用空间。

---

## 实现

### 循环队列

```c
#include <stdlib.h>

typedef struct {
    int* data;
    size_t head;     // 队首位置
    size_t tail;     // 队尾位置（下一个插入位置）
    size_t capacity;
    size_t count;
} CircularQueue;

void cq_init(CircularQueue* q, size_t cap) {
    q->data = malloc(cap * sizeof(int));
    q->head = 0;
    q->tail = 0;
    q->capacity = cap;
    q->count = 0;
}

void cq_destroy(CircularQueue* q) {
    free(q->data);
}

static int cq_resize(CircularQueue* q) {
    size_t new_cap = q->capacity * 2;
    int* new_data = malloc(new_cap * sizeof(int));
    if (!new_data) return -1;
    for (size_t i = 0; i < q->count; i++)
        new_data[i] = q->data[(q->head + i) % q->capacity];
    free(q->data);
    q->data = new_data;
    q->head = 0;
    q->tail = q->count;
    q->capacity = new_cap;
    return 0;
}

int cq_push(CircularQueue* q, int value) {
    if (q->count >= q->capacity)
        if (cq_resize(q) != 0) return -1;
    q->data[q->tail] = value;
    q->tail = (q->tail + 1) % q->capacity;
    q->count++;
    return 0;
}

int cq_pop(CircularQueue* q) {
    if (q->count == 0) return -1;
    q->head = (q->head + 1) % q->capacity;
    q->count--;
    return 0;
}

int cq_front(CircularQueue* q, int* out) {
    if (q->count == 0) return -1;
    *out = q->data[q->head];
    return 0;
}

int cq_back(CircularQueue* q, int* out) {
    if (q->count == 0) return -1;
    *out = q->data[(q->tail + q->capacity - 1) % q->capacity];
    return 0;
}

int cq_empty(CircularQueue* q) { return q->count == 0; }
size_t cq_size(CircularQueue* q) { return q->count; }
```

### 链表队列

```c
#include <stdlib.h>

typedef struct QNode {
    int data;
    struct QNode* next;
} QNode;

typedef struct {
    QNode* head;  // 队首
    QNode* tail;  // 队尾
    size_t count;
} LinkedQueue;

void lq_init(LinkedQueue* q) {
    q->head = NULL;
    q->tail = NULL;
    q->count = 0;
}

void lq_destroy(LinkedQueue* q) {
    while (q->head) {
        QNode* tmp = q->head;
        q->head = q->head->next;
        free(tmp);
    }
    q->tail = NULL;
    q->count = 0;
}

int lq_push(LinkedQueue* q, int value) {
    QNode* node = malloc(sizeof(QNode));
    if (!node) return -1;
    node->data = value;
    node->next = NULL;
    if (q->tail)
        q->tail->next = node;
    else
        q->head = node;
    q->tail = node;
    q->count++;
    return 0;
}

int lq_pop(LinkedQueue* q) {
    if (!q->head) return -1;
    QNode* tmp = q->head;
    q->head = q->head->next;
    if (!q->head) q->tail = NULL;
    free(tmp);
    q->count--;
    return 0;
}

int lq_front(LinkedQueue* q, int* out) {
    if (!q->head) return -1;
    *out = q->head->data;
    return 0;
}

int lq_back(LinkedQueue* q, int* out) {
    if (!q->tail) return -1;
    *out = q->tail->data;
    return 0;
}

int lq_empty(LinkedQueue* q) { return q->head == NULL; }
size_t lq_size(LinkedQueue* q) { return q->count; }
```

### 双端队列（deque）的原理与设计

deque 是"分段连续存储"的典型代表。它用**中控指针数组（map）** + 若干**定长缓冲区块（block）** 实现：

```
map:  [block*][block*][block*][block*]...
         |       |       |       |
         v       v       v       v
block: [0..B-1][0..B-1][0..B-1][0..B-1]    (B 为 block 大小，通常是 8 或 64)
         ^                      ^
       head                   tail
```

- **map**：一个动态数组，每个元素是指向 block 的指针
- **block**：固定大小的连续数组（如 8 个 int），是真正存数据的地方
- **迭代器**：内部维护 `block` 指针 + `position` 偏移量

#### 核心操作

| 操作 | 行为 | 时间复杂度 |
|------|------|:---------:|
| `push_back` | 在 tail block 末尾写入，block 满则申请新的 block 并追加到 map | O(1) |
| `push_front` | 在 head block 头部写入，block 满则申请新 block 插入 map 之前 | O(1) |
| `pop_back` / `pop_front` | 移动 tail/head 位置，block 变空则释放 | O(1) |
| `operator[i]` | `map[(i + head_offset) / B][(i + head_offset) % B]` | O(1) |
| 中间插入 | 移动目标位置后的所有元素，最坏触发 block 分裂 | O(n) |

#### map 扩容

当 `push_front` 或 `push_back` 时 map 的首/尾已无空闲指针位，则分配更大的 map（通常是 2 倍），将原 map 拷贝到新 map 的**中央区域**，预留两侧空间供后续两端插入：

```
旧 map:  [b0][b1][b2][b3]             (两侧无空闲指针)
新 map:  [  ][  ][b0][b1][b2][b3][  ][  ]
                  ↑ 中央对齐
```

#### 为什么 deque 能兼顾 O(1) 两端插入和 O(1) 随机访问？

- **两端 O(1)**：map 两端预留指针位，block 本身就是连续数组，头尾写入只需在 block 边界时申请/释放一个 block
- **随机访问 O(1)**：元素地址 = `map[(i + start_offset) / B][(i + start_offset) % B]`，两个简单算术运算
- **内存利用率**：不会像 vector 那样大量预留尾部空间，也不会像 list 那样每个元素多两个指针
- **缓存友好性**：遍历 deque 时同一 block 内连续命中缓存，跨 block 时大概率 cache miss，整体介于 vector 和 list 之间

#### 简易实现示意

```c
#define BLOCK_SIZE 8

typedef struct {
    int** map;          // 中控数组
    int   map_size;     // map 总容量（指针位个数）
    int   map_first;    // map 中第一个有效 block 的索引
    int   block_count;  // 已使用的 block 数
    int   head;         // 第一个 block 内的偏移
    int   tail;         // 最后一个 block 内的偏移（下一个空位）
    int   total;        // 总元素数
} SimpleDeque;

// 随机访问：arr[i] 对应的内存地址
// 伪代码，完整实现需处理边界
int sd_at(SimpleDeque* dq, int index) {
    int block_idx = dq->map_first + (dq->head + index) / BLOCK_SIZE;
    int elem_idx  = (dq->head + index) % BLOCK_SIZE;
    return dq->map[block_idx][elem_idx];
}
```

deque 的巧妙之处在于：**用 block 级的分段连续存储，在两端的 O(1) 插入和 O(1) 随机访问之间做了最佳权衡**。这也是 C++ 标准库默认用 deque 作为 stack 和 queue 底层容器的原因。

---

## 各语言标准库对比

| 语言 | 队列 | 双端队列 |
|------|------|----------|
| C | 无（手写） | 无（手写） |
| C++ | queue（deque 封装） | deque |
| Java | LinkedList / ArrayDeque | ArrayDeque |
| Python | collections.deque | collections.deque |
| Rust | VecDeque | VecDeque |

---

## 应用场景

- **广度优先搜索（BFS）**: 层序遍历树/图，先发现的节点先处理
- **消息队列**: 生产者-消费者模型，异步通信与解耦
- **CPU 任务调度**: 就绪队列按 FIFO 分配时间片
- **滑动窗口**: 用单调队列维护窗口内的最大值/最小值

### 单调队列求滑动窗口最大值

核心思想：维护一个**递减队列**，队头始终是当前窗口的最大值。每次窗口右移时，移除过期元素（出左边），加入新元素（踢掉比它小的队尾），队头即为答案。

```mermaid
flowchart LR
    A["窗口右移一步"] --> B["移除左端出界元素"]
    B --> C{"新元素 x > 队尾元素？"}
    C -->|是| D["弹出队尾"]
    D --> C
    C -->|否| E["x 入队尾"]
    E --> F["队头即为窗口最大值"]
```

```c
// 返回结果需要调用者 free
int* max_sliding_window(const int* nums, int n, int k, int* result_size) {
    int* result = malloc((n - k + 1) * sizeof(int));
    int* dq = malloc(n * sizeof(int));  // 存下标，队头到队尾递减
    int head = 0, tail = 0;
    int ri = 0;
    for (int i = 0; i < n; i++) {
        // 移除超出窗口的队头
        while (tail > head && dq[head] <= i - k)
            head++;
        // 保持递减
        while (tail > head && nums[dq[tail - 1]] <= nums[i])
            tail--;
        dq[tail++] = i;
        if (i >= k - 1)
            result[ri++] = nums[dq[head]];
    }
    *result_size = ri;
    free(dq);
    return result;
}
```

---

## 练习

| 题号 | 题目 | 难度 | 知识点 |
|------|------|------|--------|
| P1540 | 机器翻译 | 入门 | 队列模拟 |
| P1996 | 约瑟夫问题 | 入门 | 队列模拟 |
| P1886 | 滑动窗口 | 普及+ | 单调队列 |
