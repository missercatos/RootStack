

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

```cpp
#include <iostream>
#include <stdexcept>

template <typename T>
class CircularQueue {
private:
    T* _data;
    size_t _head;  // 队首位置
    size_t _tail;  // 队尾位置（下一个插入位置）
    size_t _capacity;
    size_t _count;

    void resize(size_t new_cap) {
        T* new_data = new T[new_cap];
        for (size_t i = 0; i < _count; ++i)
            new_data[i] = _data[(_head + i) % _capacity];
        delete[] _data;
        _data = new_data;
        _head = 0;
        _tail = _count;
        _capacity = new_cap;
    }

public:
    CircularQueue(size_t cap = 8)
        : _data(new T[cap]), _head(0), _tail(0), _capacity(cap), _count(0) {}

    ~CircularQueue() { delete[] _data; }

    void push(const T& value) {
        if (_count >= _capacity)
            resize(_capacity * 2);
        _data[_tail] = value;
        _tail = (_tail + 1) % _capacity;
        ++_count;
    }

    void pop() {
        if (_count == 0)
            throw std::underflow_error("queue empty");
        _head = (_head + 1) % _capacity;
        --_count;
    }

    T& front() {
        if (_count == 0)
            throw std::underflow_error("queue empty");
        return _data[_head];
    }

    T& back() {
        if (_count == 0)
            throw std::underflow_error("queue empty");
        return _data[(_tail + _capacity - 1) % _capacity];
    }

    bool empty() const { return _count == 0; }
    size_t size() const { return _count; }
};
```

### 链表队列

```cpp
template <typename T>
class LinkedQueue {
private:
    struct Node {
        T data;
        Node* next;
        Node(const T& val) : data(val), next(nullptr) {}
    };
    Node* _head; // 队首
    Node* _tail; // 队尾
    size_t _count;

public:
    LinkedQueue() : _head(nullptr), _tail(nullptr), _count(0) {}

    ~LinkedQueue() {
        while (_head) {
            Node* tmp = _head;
            _head = _head->next;
            delete tmp;
        }
    }

    void push(const T& value) {
        Node* node = new Node(value);
        if (_tail) _tail->next = node;
        else _head = node;
        _tail = node;
        ++_count;
    }

    void pop() {
        if (!_head) throw std::underflow_error("queue empty");
        Node* tmp = _head;
        _head = _head->next;
        if (!_head) _tail = nullptr;
        delete tmp;
        --_count;
    }

    T& front() {
        if (!_head) throw std::underflow_error("queue empty");
        return _head->data;
    }

    T& back() {
        if (!_tail) throw std::underflow_error("queue empty");
        return _tail->data;
    }

    bool empty() const { return _head == nullptr; }
    size_t size() const { return _count; }
};
```

---

## STL 使用

```cpp
#include <queue>
#include <deque>
#include <iostream>

int main() {
    // queue -- 默认底层容器为 deque
    std::queue<int> q;
    q.push(10);
    q.push(20);
    q.push(30);
    std::cout << "front: " << q.front() << std::endl; // 10
    std::cout << "back: " << q.back() << std::endl;   // 30
    q.pop(); // 弹出 10
    while (!q.empty()) {
        std::cout << q.front() << " ";
        q.pop();
    } // 输出: 20 30

    // deque -- 双端队列
    std::deque<int> dq;
    dq.push_back(10);
    dq.push_front(5);
    dq.pop_back();
    dq.pop_front();
    int val = dq[0]; // 支持随机访问

    return 0;
}
```

queue 默认底层容器为 deque，可指定为 list：`std::queue<int, std::list<int>> q;`

---

## 应用场景

- **广度优先搜索（BFS）**: 层序遍历树/图，先发现的节点先处理
- **消息队列**: 生产者-消费者模型，异步通信与解耦
- **CPU 任务调度**: 就绪队列按 FIFO 分配时间片
- **滑动窗口**: 用单调队列维护窗口内的最大值/最小值

### 单调队列求滑动窗口最大值

```cpp
#include <deque>
#include <vector>

std::vector<int> maxSlidingWindow(const std::vector<int>& nums, int k) {
    std::vector<int> result;
    std::deque<int> dq; // 存储下标，队头到队尾为递减
    for (int i = 0; i < nums.size(); ++i) {
        // 移除超出窗口的元素
        while (!dq.empty() && dq.front() <= i - k)
            dq.pop_front();
        // 保持递减
        while (!dq.empty() && nums[dq.back()] <= nums[i])
            dq.pop_back();
        dq.push_back(i);
        // 记录窗口最大值
        if (i >= k - 1)
            result.push_back(nums[dq.front()]);
    }
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
