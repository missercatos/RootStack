

建议先阅读: [[A_容器_Container|A 容器 Container]]

---

## 原理

链表（Linked List）是一种线性数据结构，元素通过指针链接在一起，在内存中非连续存储。每个节点包含数据域和指针域。

### 链表类型

- **单向链表**: 每个节点包含数据 + 指向下一个节点的指针
- **双向链表**: 每个节点包含数据 + 前驱指针 + 后继指针
- **循环链表**: 尾节点指向头节点，形成环

### 数组 vs 链表

| 操作 | 数组 | 链表 | 说明 |
|------|------|------|------|
| 随机访问 | O(1) | O(n) | 链表须从头遍历 |
| 头部插入 | O(n) | O(1) | 数组需整体后移 |
| 尾部插入 | O(1)* | O(1) | *数组需考虑扩容 |
| 中间插入（已知位置） | O(n) | O(1) | 链表只需改指针 |
| 删除（已知位置） | O(n) | O(1) | 链表只需改指针 |
| 缓存友好 | 好 | 差 | 数组连续，链表散列 |
| 额外空间 | 无 | 每个节点存指针 | - |

### 内存布局

链表节点在堆上独立分配，节点间通过指针连接。这意味着：无法通过索引直接访问、CPU 缓存命中率低，但插入/删除只需修改指针。

---

## 实现

### 单向链表

```cpp
#include <iostream>
#include <stdexcept>

template <typename T>
class SinglyLinkedList {
private:
    struct Node {
        T data;
        Node* next;
        Node(const T& val) : data(val), next(nullptr) {}
    };
    Node* _head;
    size_t _size;

public:
    SinglyLinkedList() : _head(nullptr), _size(0) {}

    ~SinglyLinkedList() {
        while (_head) {
            Node* tmp = _head;
            _head = _head->next;
            delete tmp;
        }
    }

    void push_front(const T& value) {
        Node* node = new Node(value);
        node->next = _head;
        _head = node;
        ++_size;
    }

    void push_back(const T& value) {
        Node* node = new Node(value);
        if (!_head) {
            _head = node;
        } else {
            Node* cur = _head;
            while (cur->next) cur = cur->next;
            cur->next = node;
        }
        ++_size;
    }

    void pop_front() {
        if (!_head) throw std::underflow_error("list empty");
        Node* tmp = _head;
        _head = _head->next;
        delete tmp;
        --_size;
    }

    // 删除第一个等于 value 的元素
    void remove(const T& value) {
        if (!_head) return;
        if (_head->data == value) {
            pop_front();
            return;
        }
        Node* cur = _head;
        while (cur->next && cur->next->data != value)
            cur = cur->next;
        if (cur->next) {
            Node* tmp = cur->next;
            cur->next = cur->next->next;
            delete tmp;
            --_size;
        }
    }

    // 反转链表（原地）
    void reverse() {
        Node* prev = nullptr;
        Node* cur = _head;
        while (cur) {
            Node* nxt = cur->next;
            cur->next = prev;
            prev = cur;
            cur = nxt;
        }
        _head = prev;
    }

    // 查找
    bool contains(const T& value) const {
        for (Node* cur = _head; cur; cur = cur->next)
            if (cur->data == value) return true;
        return false;
    }

    size_t size() const { return _size; }
    bool empty() const { return _size == 0; }

    void print() const {
        for (Node* cur = _head; cur; cur = cur->next)
            std::cout << cur->data << (cur->next ? " -> " : "");
        std::cout << std::endl;
    }
};
```

### 双向链表（核心操作）

```cpp
template <typename T>
class DoublyLinkedList {
private:
    struct Node {
        T data;
        Node* prev;
        Node* next;
        Node(const T& val) : data(val), prev(nullptr), next(nullptr) {}
    };
    Node* _head;
    Node* _tail;
    size_t _size;

public:
    DoublyLinkedList() : _head(nullptr), _tail(nullptr), _size(0) {}

    ~DoublyLinkedList() {
        while (_head) {
            Node* tmp = _head;
            _head = _head->next;
            delete tmp;
        }
    }

    void push_back(const T& value) {
        Node* node = new Node(value);
        if (!_tail) {
            _head = _tail = node;
        } else {
            node->prev = _tail;
            _tail->next = node;
            _tail = node;
        }
        ++_size;
    }

    void push_front(const T& value) {
        Node* node = new Node(value);
        if (!_head) {
            _head = _tail = node;
        } else {
            node->next = _head;
            _head->prev = node;
            _head = node;
        }
        ++_size;
    }

    void pop_back() {
        if (!_tail) throw std::underflow_error("list empty");
        Node* tmp = _tail;
        _tail = _tail->prev;
        if (_tail) _tail->next = nullptr;
        else _head = nullptr;
        delete tmp;
        --_size;
    }

    void pop_front() {
        if (!_head) throw std::underflow_error("list empty");
        Node* tmp = _head;
        _head = _head->next;
        if (_head) _head->prev = nullptr;
        else _tail = nullptr;
        delete tmp;
        --_size;
    }

    size_t size() const { return _size; }
    bool empty() const { return _size == 0; }
};
```

### 链表算法：快慢指针

```cpp
// 检测链表是否有环
bool hasCycle(Node* head) {
    Node* slow = head;
    Node* fast = head;
    while (fast && fast->next) {
        slow = slow->next;
        fast = fast->next->next;
        if (slow == fast) return true;
    }
    return false;
}

// 找中间节点
Node* findMiddle(Node* head) {
    Node* slow = head;
    Node* fast = head;
    while (fast && fast->next) {
        slow = slow->next;
        fast = fast->next->next;
    }
    return slow;
}

// 合并两个有序链表
Node* mergeTwoLists(Node* l1, Node* l2) {
    Node dummy(0);
    Node* tail = &dummy;
    while (l1 && l2) {
        if (l1->data <= l2->data) {
            tail->next = l1; l1 = l1->next;
        } else {
            tail->next = l2; l2 = l2->next;
        }
        tail = tail->next;
    }
    tail->next = l1 ? l1 : l2;
    return dummy.next;
}
```

---

## STL 使用

```cpp
#include <list>
#include <forward_list>
#include <iostream>

int main() {
    // list -- 双向链表
    std::list<int> lst = {3, 1, 4, 1, 5};
    lst.push_front(0);
    lst.push_back(9);
    lst.sort();           // 归并排序
    lst.unique();         // 去重（需先排序）
    lst.reverse();
    lst.remove(1);        // 删除所有值为 1 的元素

    // splice -- 将 other 的元素拼接到 lst
    std::list<int> other = {100, 200};
    lst.splice(lst.end(), other); // other 变为空

    for (int x : lst) std::cout << x << " ";

    // forward_list -- 单向链表
    std::forward_list<int> flst = {1, 2, 3};
    flst.push_front(0);
    flst.insert_after(flst.before_begin(), 99);
    flst.reverse();

    return 0;
}
```

---

## 应用场景

- **LRU 缓存**: 双向链表 + 哈希表，O(1) 访问和淘汰
- **约瑟夫问题**: 用循环链表模拟 n 个人围圈报数
- **多项式表示与加法**: 每个节点存一个项（系数+指数），按指数排序

---

## 练习

| 题号 | 题目 | 难度 | 知识点 |
|------|------|------|--------|
| P1996 | 约瑟夫问题 | 入门 | 循环链表模拟 |
| P1160 | 队列安排 | 普及 | 双向链表 |
