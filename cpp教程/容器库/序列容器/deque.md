---
title: "template <typename T>
class deque"
---

## 底层数据结构

分段连续存储：由一个中控器（指针数组）管理多段定长的连续缓冲区。头尾插入/删除时只需在对应端的缓冲区操作，无需像 vector 那样整体搬迁。下标访问先通过中控器定位段、再算段内偏移，仍是 O(1) 但常数略大于 vector。

## 复杂度

| 操作 | 复杂度 | 说明 |
|------|--------|------|
| operator[] | O(1) | 随机访问，常数大于 vector |
| at(i) | O(1) | 带边界检查 |
| push_front / pop_front | O(1) | 头部插入/删除 |
| push_back / pop_back | O(1) | 尾部插入/删除 |
| insert / erase | O(n) | 中间插入/删除，需移动元素 |
| front / back | O(1) | 首/尾元素引用 |
| size / empty | O(1) | |
| clear | O(n) | 清空所有元素 |

## 关键方法

| 方法 | 说明 |
|------|------|
| dq[i] / dq.at(i) | 下标访问 |
| dq.front() / dq.back() | 首/尾元素引用 |
| push_front(x) / push_back(x) | 头/尾插入 |
| pop_front() / pop_back() | 头/尾删除 |
| emplace_front / emplace_back | 头/尾原位构造 |
| insert(it, x) | 在迭代器前插入，O(n) |
| erase(it) | 删除迭代器元素，O(n) |
| clear() | 清空全部元素 |

## 伪代码示例

```
deque<int> dq

// 双端插入
dq.push_back(1)
dq.push_back(2)
dq.push_front(0)        // 现在: 0, 1, 2

// 随机访问
print dq[1]             // 输出 1

// 滑动窗口最小值（单调队列）
deque<int> win           // 存下标，对应值单调递增
for i from 1 to n:
    while win not empty and a[win.back()] >= a[i]:
        win.pop_back()
    win.push_back(i)
    if win.front() <= i - k:
        win.pop_front()
    if i >= k:
        print a[win.front()]
```

## 相关链接

- [[../../../数据结构/G_队列_Queue]]
- [[../../../数据结构/G_队列_Queue]]
- [[vector]]
