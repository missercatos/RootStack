

建议先阅读: [[A_容器_Container|A 容器 Container]], [[../算法/算法技巧/递推递归|递推递归]]

---

## 原理

排序是将一组无序数据按特定规则重新排列的过程。

### 八大排序总览

| 算法 | 平均 | 最好 | 最坏 | 空间 | 稳定 |
|------|------|------|------|------|------|
| 冒泡排序 | O(n^2) | O(n) | O(n^2) | O(1) | 稳定 |
| 选择排序 | O(n^2) | O(n^2) | O(n^2) | O(1) | 不稳定 |
| 插入排序 | O(n^2) | O(n) | O(n^2) | O(1) | 稳定 |
| 希尔排序 | O(n^1.3) | O(n) | O(n^2) | O(1) | 不稳定 |
| 归并排序 | O(n log n) | O(n log n) | O(n log n) | O(n) | 稳定 |
| 快速排序 | O(n log n) | O(n log n) | O(n^2) | O(log n) | 不稳定 |
| 堆排序 | O(n log n) | O(n log n) | O(n log n) | O(1) | 不稳定 |
| 基数排序 | O(n*k) | O(n*k) | O(n*k) | O(n+k) | 稳定 |

---

## 实现

### 冒泡排序

```cpp
void bubbleSort(std::vector<int>& arr) {
    int n = arr.size();
    for (int i = 0; i < n - 1; ++i) {
        bool swapped = false;
        for (int j = 0; j < n - 1 - i; ++j) {
            if (arr[j] > arr[j + 1]) {
                std::swap(arr[j], arr[j + 1]);
                swapped = true;
            }
        }
        if (!swapped) break; // 已有序，提前退出
    }
}
```

每轮把最大值"冒泡"到最右端。优化版通过 swapped 标志检测提前退出，最好情况 O(n)。

### 选择排序

```cpp
void selectionSort(std::vector<int>& arr) {
    int n = arr.size();
    for (int i = 0; i < n - 1; ++i) {
        int minIdx = i;
        for (int j = i + 1; j < n; ++j) {
            if (arr[j] < arr[minIdx]) minIdx = j;
        }
        if (minIdx != i) std::swap(arr[i], arr[minIdx]);
    }
}
```

每轮从未排序区找最小值放到最前。比较次数恒为 O(n^2)，但交换次数最多 n-1 次。

### 插入排序

```cpp
void insertionSort(std::vector<int>& arr) {
    int n = arr.size();
    for (int i = 1; i < n; ++i) {
        int key = arr[i];
        int j = i - 1;
        while (j >= 0 && arr[j] > key) {
            arr[j + 1] = arr[j];
            --j;
        }
        arr[j + 1] = key;
    }
}
```

像整理扑克牌，逐张插入到已排序区的正确位置。对基本有序数据接近 O(n)。

### 希尔排序

```cpp
void shellSort(std::vector<int>& arr) {
    int n = arr.size();
    // Knuth 序列: 1, 4, 13, 40, 121, ...
    int gap = 1;
    while (gap < n / 3) gap = 3 * gap + 1;

    while (gap > 0) {
        for (int i = gap; i < n; ++i) {
            int temp = arr[i];
            int j = i;
            while (j >= gap && arr[j - gap] > temp) {
                arr[j] = arr[j - gap];
                j -= gap;
            }
            arr[j] = temp;
        }
        gap = (gap - 1) / 3;
    }
}
```

大间隔分组插入排序（粗调），逐步缩小间隔（精调），最后 gap=1 时数据已基本有序。

### 归并排序

```cpp
void merge(std::vector<int>& arr, int l, int m, int r) {
    std::vector<int> temp(r - l + 1);
    int i = l, j = m + 1, k = 0;
    while (i <= m && j <= r)
        temp[k++] = (arr[i] <= arr[j]) ? arr[i++] : arr[j++];
    while (i <= m) temp[k++] = arr[i++];
    while (j <= r) temp[k++] = arr[j++];
    for (int p = 0; p < k; ++p) arr[l + p] = temp[p];
}

void mergeSort(std::vector<int>& arr, int l, int r) {
    if (l >= r) return;
    int m = l + (r - l) / 2;
    mergeSort(arr, l, m);
    mergeSort(arr, m + 1, r);
    merge(arr, l, m, r);
}
```

分治法：递归拆半 -> 分别排序 -> 合并两个有序数组。T(n) = 2T(n/2) + O(n) => O(n log n)。

### 快速排序

```cpp
int partition(std::vector<int>& arr, int low, int high) {
    int pivot = arr[high];
    int i = low;
    for (int j = low; j < high; ++j) {
        if (arr[j] < pivot)
            std::swap(arr[i++], arr[j]);
    }
    std::swap(arr[i], arr[high]);
    return i;
}

void quickSort(std::vector<int>& arr, int low, int high) {
    if (low >= high) return;
    int p = partition(arr, low, high);
    quickSort(arr, low, p - 1);
    quickSort(arr, p + 1, high);
}
```

选基准 -> 分区（小的放左，大的放右）-> 递归排左右。最坏 O(n^2)（有序时最右 pivot），可通过三数取中或随机 pivot 避免。

### 三数取中优化

```cpp
int medianOfThree(std::vector<int>& arr, int low, int high) {
    int mid = low + (high - low) / 2;
    if (arr[low] > arr[mid]) std::swap(arr[low], arr[mid]);
    if (arr[low] > arr[high]) std::swap(arr[low], arr[high]);
    if (arr[mid] > arr[high]) std::swap(arr[mid], arr[high]);
    std::swap(arr[mid], arr[high]); // 把中位数换到最右作为 pivot
    return arr[high];
}
```

### 堆排序

```cpp
void heapify(std::vector<int>& arr, int n, int i) {
    int largest = i;
    int left = 2 * i + 1, right = 2 * i + 2;
    if (left < n && arr[left] > arr[largest]) largest = left;
    if (right < n && arr[right] > arr[largest]) largest = right;
    if (largest != i) {
        std::swap(arr[i], arr[largest]);
        heapify(arr, n, largest);
    }
}

void heapSort(std::vector<int>& arr) {
    int n = arr.size();
    // 建最大堆 O(n)
    for (int i = n / 2 - 1; i >= 0; --i)
        heapify(arr, n, i);
    // 逐一提取最大值 O(n log n)
    for (int i = n - 1; i > 0; --i) {
        std::swap(arr[0], arr[i]);
        heapify(arr, i, 0);
    }
}
```

### 基数排序

```cpp
void countingSortByDigit(std::vector<int>& arr, int exp) {
    int n = arr.size();
    std::vector<int> output(n);
    std::vector<int> count(10, 0);

    for (int x : arr) ++count[(x / exp) % 10];
    for (int i = 1; i < 10; ++i) count[i] += count[i - 1];
    for (int i = n - 1; i >= 0; --i) {
        int digit = (arr[i] / exp) % 10;
        output[count[digit] - 1] = arr[i];
        --count[digit];
    }
    std::copy(output.begin(), output.end(), arr.begin());
}

void radixSort(std::vector<int>& arr) {
    if (arr.empty()) return;
    int maxVal = *std::max_element(arr.begin(), arr.end());
    for (int exp = 1; maxVal / exp > 0; exp *= 10)
        countingSortByDigit(arr, exp);
}
```

不比较大小，按每位数字稳定排序，从低位到高位依次进行。适用于整数，O(n*k)，k 为位数。

---

## STL 使用

```cpp
#include <algorithm>
#include <vector>
#include <functional>

int main() {
    std::vector<int> v = {3, 1, 4, 1, 5, 9};

    // 默认升序（内部使用 Introsort）
    std::sort(v.begin(), v.end());

    // 降序
    std::sort(v.begin(), v.end(), std::greater<int>());

    // 自定义比较
    std::sort(v.begin(), v.end(), [](int a, int b) {
        return a % 10 > b % 10;
    });

    // 部分排序：前 3 个元素为最小 3 个
    std::partial_sort(v.begin(), v.begin() + 3, v.end());

    // 第 n 个位置归位（nth_element）
    std::nth_element(v.begin(), v.begin() + 4, v.end());

    // 稳定排序（归并排序）
    std::stable_sort(v.begin(), v.end());

    return 0;
}
```

### 选型指南

- **n < 50**: 插入排序（常数因子极小）
- **n < 1000**: 希尔排序或快速排序
- **n 很大，需要稳定**: 归并排序
- **n 很大，不要求稳定**: 快速排序（通用首选）
- **需要原地 + 最坏 O(n log n)** : 堆排序
- **整数，范围小**: 基数排序
- **生产环境**: `std::sort`（Introsort：快排 + 堆排 + 插排混合）

---

## 练习

| 题号 | 题目 | 难度 | 知识点 |
|------|------|------|--------|
| P1177 | 快速排序 | 普及 | 手写排序 |
| P1059 | 明明的随机数 | 入门 | 排序 + 去重 |
| P1093 | 奖学金 | 普及 | 多关键字排序 |
| P1781 | 宇宙总统 | 入门 | 自定义比较排序 |
