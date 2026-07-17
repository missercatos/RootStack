# C 堆 Heap

建议先阅读: [[A_容器_Container|A 容器 Container]]

---

## 原理

堆（Heap）是一种特殊的完全二叉树，满足堆性质：对于最大堆，每个节点的值 >= 其子节点的值；对于最小堆，每个节点的值 <= 其子节点的值。

> 注意：此"堆"与操作系统中的"堆内存"是完全不同的概念。

### 数组存储

虽然堆逻辑上是完全二叉树，但实际使用数组存储：
- 根节点在索引 0
- 对于索引 i 的节点：
  - 父节点: `(i - 1) / 2`
  - 左子节点: `2 * i + 1`
  - 右子节点: `2 * i + 2`

### 核心操作与时间复杂度

| 操作 | 描述 | 时间复杂度 |
|------|------|-----------|
| push / insert | 末尾追加 + sift-up 上浮 | O(log n) |
| pop / extract | 堆顶与末尾交换 + sift-down 下沉 | O(log n) |
| top / peek | 直接返回 arr[0] | O(1) |
| make_heap | Floyd 自底向上建堆 | O(n) |
| heap_sort | 建堆 + n 次弹出 | O(n log n) |

### 上浮与下沉

**上浮（sift-up）**: 新元素放在数组末尾，与父节点比较，违反堆性质则交换，重复直到满足或到根节点。

**下沉（sift-down）**: 新根与较大子节点比较（最大堆），违反堆性质则交换，重复直到满足或到叶节点。

### Floyd 建堆 O(n) 证明

从最后一个非叶节点（n/2 - 1）开始逐个下沉。虽然单次下沉为 O(log n)，但层越深节点越多而下沉距离越短。经级数求和可证明总时间复杂度为 O(n)。

---

## 实现

### 最大堆

```cpp
#include <iostream>
#include <vector>
#include <stdexcept>

template <typename T>
class MaxHeap {
private:
    std::vector<T> data;

    void siftUp(size_t idx) {
        while (idx > 0) {
            size_t parent = (idx - 1) / 2;
            if (data[parent] >= data[idx]) break;
            std::swap(data[parent], data[idx]);
            idx = parent;
        }
    }

    void siftDown(size_t idx) {
        size_t n = data.size();
        while (true) {
            size_t largest = idx;
            size_t left = 2 * idx + 1;
            size_t right = 2 * idx + 2;
            if (left < n && data[left] > data[largest])
                largest = left;
            if (right < n && data[right] > data[largest])
                largest = right;
            if (largest == idx) break;
            std::swap(data[idx], data[largest]);
            idx = largest;
        }
    }

public:
    MaxHeap() = default;

    // Floyd 建堆：O(n)
    MaxHeap(const std::vector<T>& arr) : data(arr) {
        for (int i = data.size() / 2 - 1; i >= 0; --i)
            siftDown(i);
    }

    void push(const T& value) {
        data.push_back(value);
        siftUp(data.size() - 1);
    }

    T extractMax() {
        if (data.empty()) throw std::underflow_error("heap empty");
        T maxVal = data[0];
        data[0] = data.back();
        data.pop_back();
        if (!data.empty()) siftDown(0);
        return maxVal;
    }

    const T& top() const {
        if (data.empty()) throw std::underflow_error("heap empty");
        return data[0];
    }

    bool empty() const { return data.empty(); }
    size_t size() const { return data.size(); }
};
```

### 堆排序

```cpp
void heapSort(std::vector<int>& arr) {
    // 建堆 O(n)
    for (int i = arr.size() / 2 - 1; i >= 0; --i) {
        // siftDown 逻辑（内联）
        int n = arr.size();
        int idx = i;
        while (true) {
            int largest = idx;
            int left = 2 * idx + 1, right = 2 * idx + 2;
            if (left < n && arr[left] > arr[largest]) largest = left;
            if (right < n && arr[right] > arr[largest]) largest = right;
            if (largest == idx) break;
            std::swap(arr[idx], arr[largest]);
            idx = largest;
        }
    }
    // 逐一提取最大值 O(n log n)
    for (int i = arr.size() - 1; i > 0; --i) {
        std::swap(arr[0], arr[i]);
        // siftDown on reduced heap
        int n = i, idx = 0;
        while (true) {
            int largest = idx;
            int left = 2 * idx + 1, right = 2 * idx + 2;
            if (left < n && arr[left] > arr[largest]) largest = left;
            if (right < n && arr[right] > arr[largest]) largest = right;
            if (largest == idx) break;
            std::swap(arr[idx], arr[largest]);
            idx = largest;
        }
    }
}
```

---

## STL 使用

```cpp
#include <queue>
#include <vector>
#include <iostream>

int main() {
    // 默认最大堆（大顶堆）
    std::priority_queue<int> max_pq;
    max_pq.push(30);
    max_pq.push(10);
    max_pq.push(50);
    while (!max_pq.empty()) {
        std::cout << max_pq.top() << " "; // 50 30 10
        max_pq.pop();
    }

    // 最小堆（小顶堆）
    std::priority_queue<int, std::vector<int>, std::greater<int>> min_pq;
    min_pq.push(30);
    min_pq.push(10);
    min_pq.push(50);
    while (!min_pq.empty()) {
        std::cout << min_pq.top() << " "; // 10 30 50
        min_pq.pop();
    }

    // 自定义比较器
    auto cmp = [](int a, int b) { return a % 10 < b % 10; };
    std::priority_queue<int, std::vector<int>, decltype(cmp)> custom_pq(cmp);

    // STL 堆算法（操作 vector）
    std::vector<int> v = {3, 1, 4, 1, 5, 9};
    std::make_heap(v.begin(), v.end());          // 建堆
    v.push_back(10);
    std::push_heap(v.begin(), v.end());          // 插入
    std::pop_heap(v.begin(), v.end());           // 弹出堆顶到末尾
    int maxVal = v.back(); v.pop_back();
    std::sort_heap(v.begin(), v.end());          // 堆排序

    return 0;
}
```

---

## 应用场景

- **优先队列**: 任务调度（优先级高的先执行）、Dijkstra 最短路径算法
- **Top-K 问题**: 用大小为 K 的最小堆维护最大的 K 个元素，每个新元素与堆顶比较决定是否替换
- **数据流中位数**: 用两个堆（最大堆存小的一半，最小堆存大的一半），O(log n) 插入，O(1) 查询中位数
- **合并 K 个有序链表**: 用最小堆每次取 K 个链表头中的最小值，总时间 O(N log K)

---

## 练习

| 题号 | 题目 | 难度 | 知识点 |
|------|------|------|--------|
| P3378 | 堆 | 普及 | 堆的基本操作 |
| P1090 | 合并果子 | 普及 | 优先队列、贪心 |
| P1168 | 中位数 | 普及+ | 两个堆维护中位数 |
