# A 容器 Container

建议先阅读: 无（本章为数据结构系列的第一章）

---

## 原理

容器是用于存储和组织数据集合的数据结构，封装了数据存储和访问的管理细节。

### 连续存储 vs 节点存储

| 类型 | 代表 | 内存布局 | 随机访问 | 中间插入/删除 |
|------|------|----------|----------|---------------|
| 连续存储 | vector, array | 元素连续排列 | O(1) | O(n) |
| 节点存储 | list, map, set | 节点散列，指针相连 | 不支持 | O(1) 或 O(log n) |

### 迭代器原理

迭代器是容器与算法之间的桥梁，抽象了"遍历元素"这一概念。本质上是智能指针，支持解引用(*)、自增(++)、比较(==/!=)等操作。

随机访问迭代器（如 vector）额外支持 `it + n` 和 `it[n]`；双向迭代器（如 list）只支持 ++ 和 --。

### vector 扩容机制

vector 内部维护三个指针：`_start`（起始）、`_finish`（已用末尾）、`_end_of_storage`（容量末尾）。当 `_finish == _end_of_storage` 时触发扩容：
1. 分配新内存（通常 1.5~2 倍当前容量）
2. 将旧元素移动/拷贝到新内存
3. 释放旧内存

单次扩容为 O(n)，但均摊后 push_back 仍为 O(1)。

### 时间复杂度总表

| 操作 | vector | list | deque | set/map | unordered_map |
|------|--------|------|-------|---------|---------------|
| 随机访问 | O(1) | O(n) | O(1) | - | - |
| 头部插入 | O(n) | O(1) | O(1) | O(log n) | O(1) |
| 尾部插入 | O(1)* | O(1) | O(1) | O(log n) | O(1) |
| 中间插入 | O(n) | O(1) | O(n) | O(log n) | O(1) |
| 查找 | O(n) | O(n) | O(n) | O(log n) | O(1) |

> *均摊 O(1)，单次扩容时为 O(n)

---

## 实现

手写一个简易动态数组 SimpleVector：

```cpp
#include <iostream>
#include <stdexcept>

template <typename T>
class SimpleVector {
private:
    T* _data;
    size_t _size;
    size_t _capacity;

    void reallocate(size_t new_cap) {
        T* new_data = new T[new_cap];
        for (size_t i = 0; i < _size; ++i)
            new_data[i] = _data[i];
        delete[] _data;
        _data = new_data;
        _capacity = new_cap;
    }

public:
    SimpleVector() : _data(nullptr), _size(0), _capacity(0) {}

    ~SimpleVector() { delete[] _data; }

    // 拷贝构造
    SimpleVector(const SimpleVector& other)
        : _size(other._size), _capacity(other._size) {
        _data = new T[_capacity];
        for (size_t i = 0; i < _size; ++i)
            _data[i] = other._data[i];
    }

    // 移动构造
    SimpleVector(SimpleVector&& other) noexcept
        : _data(other._data), _size(other._size), _capacity(other._capacity) {
        other._data = nullptr;
        other._size = other._capacity = 0;
    }

    void push_back(const T& value) {
        if (_size >= _capacity) {
            size_t new_cap = (_capacity == 0) ? 1 : _capacity * 2;
            reallocate(new_cap);
        }
        _data[_size++] = value;
    }

    void pop_back() {
        if (_size > 0) --_size;
    }

    T& at(size_t index) {
        if (index >= _size) throw std::out_of_range("index out of range");
        return _data[index];
    }

    T& operator[](size_t index) { return _data[index]; }
    const T& operator[](size_t index) const { return _data[index]; }

    size_t size() const { return _size; }
    size_t capacity() const { return _capacity; }
    bool empty() const { return _size == 0; }

    T* begin() { return _data; }
    T* end() { return _data + _size; }

    void clear() { _size = 0; }
};
```

---

## STL 使用

```cpp
#include <vector>
#include <list>
#include <deque>
#include <set>
#include <map>
#include <unordered_map>
#include <iostream>

int main() {
    // vector -- 动态数组
    std::vector<int> v = {1, 2, 3};
    v.push_back(4);       // 尾插
    v.pop_back();          // 尾删
    int a = v[0];          // 随机访问
    int b = v.at(0);       // 带边界检查
    v.reserve(100);        // 预留容量
    v.shrink_to_fit();     // 收缩容量

    // list -- 双向链表
    std::list<int> lst = {1, 2, 3};
    lst.push_front(0);
    lst.push_back(4);
    lst.sort();            // 链表排序（归并）
    lst.reverse();         // 反转

    // deque -- 双端队列
    std::deque<int> dq = {1, 2, 3};
    dq.push_front(0);
    dq.push_back(4);
    dq.pop_front();

    // set -- 有序集合（红黑树）
    std::set<int> s;
    s.insert(3);
    s.insert(1);
    s.insert(4);
    for (int x : s) std::cout << x << " "; // 输出: 1 3 4
    auto it = s.lower_bound(3); // 第一个 >= 3 的元素

    // map -- 有序映射（红黑树）
    std::map<std::string, int> m;
    m["apple"] = 5;
    m["banana"] = 3;
    for (auto& [k, v] : m)
        std::cout << k << ": " << v << " ";

    // unordered_map -- 哈希表
    std::unordered_map<std::string, int> um;
    um["hello"] = 1;
    um["world"] = 2;

    return 0;
}
```

---

## 应用场景

- **vector**: 需要随机访问的列表，末尾增删频繁。如存储学生成绩列表
- **list**: 中间频繁插入/删除，需要 splice 操作。如 LRU 缓存的内部链表
- **set/map**: 需要有序存储和范围查询。如按时间排序的事件日志
- **unordered_map**: 需要 O(1) 查找，不关心顺序。如缓存、字典

---

## 练习

| 题号 | 题目 | 难度 | 知识点 |
|------|------|------|--------|
| P1047 | 校门外的树 | 入门 | 数组标记 |
| P3156 | 询问学号 | 入门 | vector 基础 |
| P1427 | 小鱼的数字游戏 | 入门 | vector 反向遍历 |
