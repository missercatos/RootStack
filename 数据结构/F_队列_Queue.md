## ==========================================================================
C++ 数据结构教程 — 队列 (Queue)
## ==========================================================================

## 📋 章节概述

队列（Queue）是一种受限的线性数据结构，它遵循"先进先出"（FIFO, First In First
Out）的原则。元素只能从一端（队尾）插入，从另一端（队首）删除。

队列在计算机科学中应用广泛：CPU任务调度、IO缓冲区、广度优先搜索（BFS）、
消息队列、打印任务队列、生产者消费者模型等。

> 📌 **底层实现参考**：如果需要深入理解本章数据结构的底层实现（纯C手写、内存布局、指针操作），请参阅 [[../../C语言深化教程/3数据结构/04_队列|C语言教程: 队列]]。C教程侧重手动实现与内存本质，本教程侧重STL使用与算法优化，两者互补。

## ==========================================================================
### 📖 第一节: 基础语法 + 计算机底层原理
## ==========================================================================

1.1 队列的基本概念
--------------------

核心操作：
- enqueue (push): 在队尾插入元素
- dequeue (pop): 删除队首元素
- front: 获取队首元素
- back: 获取队尾元素
- empty: 判断队列是否为空
- size: 返回队列中元素个数

最基础的队列使用示例：

```cpp
#include <iostream>
#include <queue>

int main() {
    std::queue<int> q;

    // 入队
    q.push(10);
    q.push(20);
    q.push(30);

    // 访问队首和队尾
    std::cout << "队首: " << q.front() << std::endl;  // 10
    std::cout << "队尾: " << q.back() << std::endl;   // 30

    // 出队
    q.pop();
    std::cout << "出队后队首: " << q.front() << std::endl;  // 20

    // 大小
    std::cout << "队列大小: " << q.size() << std::endl;

    // 遍历并清空
    while (!q.empty()) {
        std::cout << q.front() << " ";
        q.pop();
    }
    std::cout << std::endl;

    return 0;
}
```

1.2 队列的底层原理：数组实现 vs 链表实现
-----------------------------------------------

数组实现（循环队列）：
- 避免假溢出（假溢出指数组前面有空位但tail到了末尾）
- 通过取模运算实现循环

```cpp
// 假溢出示意
// 队列 [_, _, _, _, _, _, _, _]
//       ↑              ↑
//      front          tail
// 前面都出队了，但tail已到末尾，无法再入队
// 循环队列解决此问题：tail重新回到前面

#include <iostream>
#include <stdexcept>

template<typename T, size_t MAX_SIZE = 10>
class CircularQueue {
private:
    T data[MAX_SIZE];
    size_t head;  // 队首位置
    size_t tail;  // 队尾位置（下一个插入的位置）
    size_t count; // 当前元素个数

public:
    CircularQueue() : head(0), tail(0), count(0) {}

    void push(const T& value) {
        if (count >= MAX_SIZE) {
            throw std::overflow_error("队列已满");
        }
        data[tail] = value;
        tail = (tail + 1) % MAX_SIZE;
        ++count;
    }

    void pop() {
        if (count == 0) {
            throw std::underflow_error("队列为空");
        }
        head = (head + 1) % MAX_SIZE;
        --count;
    }

    T& front() {
        if (count == 0) throw std::underflow_error("队列为空");
        return data[head];
    }

    bool empty() const { return count == 0; }
    size_t size() const { return count; }

    void print() const {
        size_t idx = head;
        for (size_t i = 0; i < count; ++i) {
            std::cout << data[idx] << " ";
            idx = (idx + 1) % MAX_SIZE;
        }
        std::cout << "(size=" << count << ")" << std::endl;
    }
};

int main() {
    CircularQueue<int, 5> cq;

    cq.push(10);
    cq.push(20);
    cq.push(30);
    cq.print();

    cq.pop();
    cq.pop();
    cq.push(40);
    cq.push(50);
    cq.push(60);
    cq.print();

    std::cout << "队首: " << cq.front() << std::endl;

    return 0;
}
```

链表实现队列：

```cpp
#include <iostream>
#include <stdexcept>

template<typename T>
class LinkedQueue {
private:
    struct Node {
        T data;
        Node* next;
        Node(const T& val) : data(val), next(nullptr) {}
    };

    Node* head;  // 队首（出队端）
    Node* tail;  // 队尾（入队端）
    size_t count;

public:
    LinkedQueue() : head(nullptr), tail(nullptr), count(0) {}

    ~LinkedQueue() {
        while (head) {
            Node* temp = head;
            head = head->next;
            delete temp;
        }
    }

    void push(const T& value) {
        Node* new_node = new Node(value);
        if (tail) {
            tail->next = new_node;
        } else {
            head = new_node;
        }
        tail = new_node;
        ++count;
    }

    void pop() {
        if (!head) throw std::underflow_error("队列为空");
        Node* temp = head;
        head = head->next;
        if (!head) tail = nullptr;
        delete temp;
        --count;
    }

    T& front() {
        if (!head) throw std::underflow_error("队列为空");
        return head->data;
    }

    T& back() {
        if (!tail) throw std::underflow_error("队列为空");
        return tail->data;
    }

    bool empty() const { return count == 0; }
    size_t size() const { return count; }
};

int main() {
    LinkedQueue<int> lq;

    for (int i = 1; i <= 5; ++i) lq.push(i * 10);
    std::cout << "队首: " << lq.front() << ", 队尾: " << lq.back() << std::endl;

    while (!lq.empty()) {
        std::cout << lq.front() << " ";
        lq.pop();
    }
    std::cout << std::endl;

    return 0;
}
```

1.3 双端队列（Deque）的底层原理
------------------------------------

deque（double-ended queue）是两端都可以插入和删除的队列。标准库的std::deque
采用"分段连续存储"结构：

```mermaid
graph TD
    subgraph 中控器["中控器（map，指针数组）"]
        b0["buf 0"] 
        b1["buf 1"]
        b2["buf 2"]
        b3["buf 3"]
        b4["buf 4"]
    end
    b0 --> buf0["1 | 2 | 3"]
    b1 --> buf1["4 | 5 | 6"]
    b2 --> buf2["7 | 8 | 9"]
    b3 --> buf3["10 | 11 | 12"]
    b4 --> buf4["13 | 14 | 15"]
```

每个缓冲区（buffer）是固定大小的连续数组。中控器维护所有缓冲区的指针。
当在一端插入时，如果当前缓冲区已满，就分配一个新的缓冲区。


## ==========================================================================
### 📖 第二节: 所有用法大全
## ==========================================================================

2.1 std::queue —— 队列容器适配器
-------------------------------------

```cpp
#include <iostream>
#include <queue>
#include <list>
#include <deque>

int main() {
    // 默认底层容器 deque
    std::queue<int> q1;

    // 使用 list 作为底层容器
    std::queue<int, std::list<int>> q2;

    // 从已有容器构造
    std::deque<int> deq = {1, 2, 3, 4, 5};
    std::queue<int> q3(deq);  // 1在队首，5在队尾

    // 核心操作
    std::queue<int> q;
    q.push(100);
    q.push(200);
    q.emplace(300);  // C++11就地构造

    std::cout << "size: " << q.size() << std::endl;
    std::cout << "front: " << q.front() << std::endl;  // 100
    std::cout << "back: " << q.back() << std::endl;    // 300

    q.pop();  // 弹出队首
    std::cout << "after pop, front: " << q.front() << std::endl;  // 200

    // 交换
    std::queue<int> other;
    other.push(999);
    q.swap(other);

    // 关系运算符（逐个比较元素）
    std::queue<int> a, b;
    a.push(1); a.push(2);
    b.push(1); b.push(2);
    std::cout << "a == b: " << (a == b) << std::endl;
    a.push(3);
    b.push(4);
    std::cout << "a < b: " << (a < b) << std::endl;  // 1,2,3 < 1,2,4

    return 0;
}
```

2.2 std::deque —— 双端队列
-------------------------------

```cpp
#include <iostream>
#include <deque>
#include <algorithm>

int main() {
    std::deque<int> dq = {10, 20, 30};

    // 两端操作
    dq.push_front(5);
    dq.push_back(35);
    dq.pop_front();
    dq.pop_back();

    // 插入（deque支持随机访问迭代器，但中间插入较慢）
    dq.insert(dq.begin() + 1, 15);
    dq.emplace(dq.end() - 1, 25);

    // 随机访问
    std::cout << "dq[0]: " << dq[0] << std::endl;
    std::cout << "dq.at(2): " << dq.at(2) << std::endl;

    // resize
    dq.resize(10, -1);  // 扩展到10个，新元素填-1
    dq.resize(5);       // 缩小到5个

    // 遍历
    for (int x : dq) std::cout << x << " ";
    std::cout << std::endl;

    // 算法支持
    std::sort(dq.begin(), dq.end());
    auto it = std::find(dq.begin(), dq.end(), 25);

    return 0;
}
```

2.3 优先队列（Priority Queue）的队列视角
----------------------------------------------

```cpp
#include <iostream>
#include <queue>
#include <vector>
#include <functional>

struct Patient {
    std::string name;
    int severity;      // 病情严重程度（越大越优先）
    int arrival_time;  // 到达时间

    bool operator<(const Patient& other) const {
        // 严重程度高者优先；相同则先到者优先
        if (severity != other.severity)
            return severity < other.severity;
        return arrival_time > other.arrival_time;
    }
};

int main() {
    std::priority_queue<Patient> er_queue;

    er_queue.push({"张三", 5, 1});
    er_queue.push({"李四", 8, 2});    // 更严重
    er_queue.push({"王五", 8, 3});    // 同样严重但到得晚
    er_queue.push({"赵六", 3, 4});

    std::cout << "急诊顺序:" << std::endl;
    while (!er_queue.empty()) {
        auto p = er_queue.top();
        std::cout << "  " << p.name << " (严重程度:" << p.severity
                  << ", 到达:" << p.arrival_time << ")" << std::endl;
        er_queue.pop();
    }

    return 0;
}
```


## ==========================================================================
### 📖 第三节: 实用案例
## ==========================================================================

案例一：广度优先搜索（BFS）—— 社交网络好友推荐
-------------------------------------------------------

```cpp
#include <iostream>
#include <queue>
#include <vector>
#include <unordered_set>
#include <unordered_map>

class SocialGraph {
private:
    std::unordered_map<std::string, std::vector<std::string>> friends;

public:
    void addFriendship(const std::string& a, const std::string& b) {
        friends[a].push_back(b);
        friends[b].push_back(a);
    }

    // 使用BFS找指定用户的好友推荐（好友的好友，且不是直接好友）
    std::vector<std::string> recommendFriends(const std::string& user,
                                               int max_depth = 2) {
        std::queue<std::pair<std::string, int>> q;  // (人名, 距离)
        std::unordered_set<std::string> visited;
        std::unordered_map<std::string, int> recommendations;

        // 标记自己为已访问
        visited.insert(user);
        // 标记所有直接好友为已访问
        for (const auto& f : friends[user]) {
            visited.insert(f);
        }

        // 将直接好友加入队列
        for (const auto& f : friends[user]) {
            q.push({f, 1});
        }

        while (!q.empty()) {
            auto [person, depth] = q.front();
            q.pop();

            if (depth >= max_depth) continue;

            for (const auto& fof : friends[person]) {
                if (visited.find(fof) == visited.end()) {
                    visited.insert(fof);
                    recommendations[fof] = depth + 1;
                    q.push({fof, depth + 1});
                }
            }
        }

        // 按推荐度排序
        std::vector<std::pair<std::string, int>> sorted(
            recommendations.begin(), recommendations.end());
        std::sort(sorted.begin(), sorted.end(),
                  [](const auto& a, const auto& b) {
                      return a.second < b.second;
                  });

        std::vector<std::string> result;
        for (const auto& [name, dist] : sorted) {
            result.push_back(name);
        }
        return result;
    }
};

int main() {
    SocialGraph sg;

    sg.addFriendship("Alice", "Bob");
    sg.addFriendship("Alice", "Charlie");
    sg.addFriendship("Bob", "David");
    sg.addFriendship("Bob", "Eve");
    sg.addFriendship("Charlie", "Frank");
    sg.addFriendship("David", "Grace");
    sg.addFriendship("Eve", "Grace");

    std::cout << "Alice的好友推荐: ";
    for (const auto& name : sg.recommendFriends("Alice")) {
        std::cout << name << " ";
    }
    std::cout << std::endl;

    return 0;
}
```


案例二：消息队列（生产者-消费者模型）
---------------------------------------------

```cpp
#include <iostream>
#include <queue>
#include <string>
#include <mutex>
#include <condition_variable>
#include <thread>
#include <chrono>

template<typename T>
class ThreadSafeQueue {
private:
    std::queue<T> q;
    mutable std::mutex mtx;
    std::condition_variable cv;
    size_t max_size;

public:
    ThreadSafeQueue(size_t max = 100) : max_size(max) {}

    void push(const T& item) {
        std::unique_lock<std::mutex> lock(mtx);
        cv.wait(lock, [this]() { return q.size() < max_size; });
        q.push(item);
        cv.notify_all();
    }

    T pop() {
        std::unique_lock<std::mutex> lock(mtx);
        cv.wait(lock, [this]() { return !q.empty(); });
        T item = q.front();
        q.pop();
        cv.notify_all();
        return item;
    }

    bool try_pop(T& item, int timeout_ms = 100) {
        std::unique_lock<std::mutex> lock(mtx);
        if (!cv.wait_for(lock, std::chrono::milliseconds(timeout_ms),
                         [this]() { return !q.empty(); })) {
            return false;
        }
        item = q.front();
        q.pop();
        cv.notify_all();
        return true;
    }

    size_t size() const {
        std::lock_guard<std::mutex> lock(mtx);
        return q.size();
    }
};

void producer(ThreadSafeQueue<std::string>& queue, int id) {
    for (int i = 0; i < 5; ++i) {
        std::string msg = "生产者" + std::to_string(id) +
                          " 的消息 #" + std::to_string(i);
        queue.push(msg);
        std::cout << "[生产] " << msg << std::endl;
        std::this_thread::sleep_for(std::chrono::milliseconds(100 * id));
    }
}

void consumer(ThreadSafeQueue<std::string>& queue, int id) {
    for (int i = 0; i < 5; ++i) {
        std::string msg = queue.pop();
        std::cout << "[消费" << id << "] " << msg << std::endl;
        std::this_thread::sleep_for(std::chrono::milliseconds(150));
    }
}

int main() {
    ThreadSafeQueue<std::string> queue(5);

    std::thread p1(producer, std::ref(queue), 1);
    std::thread p2(producer, std::ref(queue), 2);
    std::thread c1(consumer, std::ref(queue), 1);
    std::thread c2(consumer, std::ref(queue), 2);

    p1.join();
    p2.join();
    c1.join();
    c2.join();

    std::cout << "队列处理完毕" << std::endl;

    return 0;
}
```


案例三：银行叫号系统
---------------------------

```cpp
#include <iostream>
#include <queue>
#include <string>
#include <vector>
#include <random>

class BankQueue {
private:
    struct Customer {
        int number;
        std::string service_type;  // 存款、取款、理财等
        int arrival_time;
    };

    std::queue<Customer> normal_queue;
    std::queue<Customer> vip_queue;
    int counter = 0;

public:
    int takeNumber(const std::string& service_type, bool is_vip = false) {
        int num = ++counter;
        Customer c{num, service_type, counter};

        if (is_vip) {
            vip_queue.push(c);
            std::cout << "VIP客户 " << num << " 取号 (" << service_type << ")"
                      << std::endl;
        } else {
            normal_queue.push(c);
            std::cout << "普通客户 " << num << " 取号 (" << service_type << ")"
                      << std::endl;
        }
        return num;
    }

    void callNext() {
        Customer c;
        if (!vip_queue.empty()) {
            c = vip_queue.front();
            vip_queue.pop();
            std::cout << ">>> 请VIP " << c.number << " 号到VIP窗口办理 ("
                      << c.service_type << ")" << std::endl;
        } else if (!normal_queue.empty()) {
            c = normal_queue.front();
            normal_queue.pop();
            std::cout << ">>> 请 " << c.number << " 号到普通窗口办理 ("
                      << c.service_type << ")" << std::endl;
        } else {
            std::cout << "当前无等待客户" << std::endl;
        }
    }

    void printStatus() const {
        std::cout << "\n当前排队情况:" << std::endl;
        std::cout << "  VIP队列: " << vip_queue.size() << "人" << std::endl;
        std::cout << "  普通队列: " << normal_queue.size() << "人" << std::endl;
        std::cout << "  总等待人数: " << (vip_queue.size() + normal_queue.size())
                  << std::endl;
    }
};

int main() {
    BankQueue bq;

    bq.takeNumber("存款");
    bq.takeNumber("取款");
    bq.takeNumber("理财", true);  // VIP
    bq.takeNumber("转账");
    bq.takeNumber("开户", true);  // VIP

    bq.printStatus();

    std::cout << "\n开始叫号:" << std::endl;
    bq.callNext();  // VIP优先
    bq.callNext();
    bq.callNext();
    bq.callNext();
    bq.callNext();
    bq.callNext();  // 空

    return 0;
}
```


## ==========================================================================
### 📖 第四节: 课后习题
## ==========================================================================

1. 基础题：手动实现一个循环队列。
   - 使用定长数组实现
   - 支持 push、pop、front、back、empty、size
   - 正确处理队满和队空条件
   - 支持动态扩容

2. 应用题：使用两个栈实现一个队列。
   - push: O(1)
   - pop: 均摊O(1)
   - 分析为什么使用两个栈可以实现FIFO

3. 进阶题：实现一个滑动窗口最大值队列。
   - 给定一个数组和一个窗口大小k
   - 使用双端队列（deque）在O(n)时间内输出每个窗口的最大值
   - 单调队列的应用

4. 综合题：实现一个阻塞队列（Blocking Queue）。
   - 支持固定容量
   - push操作在队列满时阻塞
   - pop操作在队列空时阻塞
   - 支持超时机制

5. 挑战题：实现一个无锁队列（Lock-Free Queue）。
   - 使用CAS（Compare-And-Swap）原子操作
   - 支持多生产者多消费者（MPMC）
   - 验证无锁队列的正确性和性能优势

## ==========================================================================


## ==========================================================================
### 📝 章节测试
## ==========================================================================

> [!question] 判断题 1
> 队列是一种先进先出（FIFO）的数据结构 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: 队列遵循FIFO（First In First Out）原则，最先入队的元素最先出队，就像现实中的排队一样。

> [!question] 判断题 2
> std::queue 默认使用 std::vector 作为底层容器 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: std::queue 默认使用 std::deque 作为底层容器。deque支持两端高效操作，适合队列的front弹出和back插入。

> [!question] 判断题 3
> 循环队列使用数组实现时，可以避免"假溢出"问题 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: 普通数组队列出队后前面的空间浪费（假溢出）。循环队列通过取模运算使队尾绕回数组开头，充分利用已释放的空间。

> [!question] 判断题 4
> 双端队列（deque）既可以当栈使用，也可以当队列使用 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: deque支持两端的push和pop操作。只使用一端操作就是栈（LIFO），一端入另一端出就是队列（FIFO）。

> [!question] 判断题 5
> BFS（广度优先搜索）使用栈作为辅助数据结构 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: BFS使用队列作为辅助数据结构，先发现的节点先处理（层序遍历）。DFS才使用栈（或递归）。

> [!question] 判断题 6
> std::queue 的 pop() 操作会返回被弹出的队首元素 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: 与std::stack类似，std::queue的pop()返回void，只负责删除队首元素。需要先用front()获取队首元素，再调用pop()删除。

> [!question] 判断题 7
> 单调队列可以在O(n)时间内解决滑动窗口最大值问题 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: 单调队列（使用deque实现）维护窗口内的递减序列，每个元素最多入队出队各一次，总时间O(n)，比暴力法O(nk)高效。

> [!question] 判断题 8
> 循环队列中判断队满的条件是 front == rear （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: front == rear 是队空的条件。队满的常用判断条件是 (rear + 1) % capacity == front（牺牲一个存储位），或使用额外的size计数。

> [!question] 判断题 9
> 优先队列本质上是一个队列，遵循先进先出原则 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > 
> > **解析**: 优先队列按优先级出队而非按入队顺序，不遵循FIFO。它底层通常用堆实现，每次出队的是优先级最高（或最低）的元素。

> [!question] 判断题 10
> 使用两个栈可以模拟一个队列，使得入队和出队的均摊时间复杂度都为O(1) （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > 
> > **解析**: 一个栈用于入队（push栈），另一个用于出队（pop栈）。出队时如果pop栈为空，将push栈全部倒入pop栈。每个元素最多被移动两次，均摊O(1)。

---

> [!question] 选择题 1
> 以下哪个是队列的合法操作序列？（队列初始为空）
> - [ ] A. push(1), push(2), front() → 2
> - [ ] B. push(1), push(2), front() → 1
> - [ ] C. push(1), pop(), front() → 1
> - [ ] D. pop(), push(1), front() → 空
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: 队列FIFO，先入先出。push(1)后push(2)，front()返回最先入队的元素1。

> [!question] 选择题 2
> 循环队列中，已知 front=3, rear=1, capacity=5，当前队列中有几个元素？
> - [ ] A. 2
> - [ ] B. 3
> - [ ] C. 4
> - [ ] D. 1
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: 元素个数 = (rear - front + capacity) % capacity = (1 - 3 + 5) % 5 = 3。队列包含位置3、4、0上的3个元素。

> [!question] 选择题 3
> 以下哪种算法不使用队列作为核心数据结构？
> - [ ] A. BFS广度优先搜索
> - [ ] B. 树的层序遍历
> - [ ] C. DFS深度优先搜索
> - [ ] D. 拓扑排序（Kahn算法）
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > 
> > **解析**: DFS使用栈（或递归）而不是队列。BFS、层序遍历和Kahn拓扑排序都使用队列。

> [!question] 选择题 4
> std::deque 内部使用什么存储结构？
> - [ ] A. 单一连续数组
> - [ ] B. 链表
> - [ ] C. 分段连续的缓冲区 + 中控器（map）
> - [ ] D. 红黑树
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > 
> > **解析**: deque由多个固定大小的连续缓冲区（block）组成，通过一个中控器（指针数组）管理各缓冲区。这样实现了两端O(1)操作和O(1)随机访问。

> [!question] 选择题 5
> 在操作系统中，进程调度最常使用哪种数据结构？
> - [ ] A. 栈
> - [ ] B. 队列
> - [ ] C. 链表
> - [ ] D. 数组
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: 操作系统的进程调度通常使用队列（就绪队列），按照FIFO或优先级顺序分配CPU时间片。

> [!question] 选择题 6
> 单调队列中，为了维护窗口最大值，队列中的元素应该保持什么顺序？
> - [ ] A. 严格递增
> - [ ] B. 严格递减
> - [ ] C. 从队头到队尾非递增（递减）
> - [ ] D. 无特殊要求
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > 
> > **解析**: 维护窗口最大值时，队列中元素从队头到队尾保持非递增（递减）。队头始终是当前窗口最大值。新元素入队时，从队尾弹出所有比它小的元素。

> [!question] 选择题 7
> 以下哪种队列变体支持在两端进行入队和出队操作？
> - [ ] A. 循环队列
> - [ ] B. 优先队列
> - [ ] C. 双端队列（deque）
> - [ ] D. 阻塞队列
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > 
> > **解析**: 双端队列（deque）支持在头部和尾部都进行插入和删除操作（push_front, push_back, pop_front, pop_back），是最灵活的线性队列。

> [!question] 选择题 8
> 一个循环队列的容量为10（实际可用9个位置），当front=7, rear=2时，再入队几个元素会队满？
> - [ ] A. 3
> - [ ] B. 4
> - [ ] C. 5
> - [ ] D. 6
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: 当前元素数=(2-7+10)%10=5，可用空间=9-5=4。再入队4个元素后rear=6，(6+1)%10=7=front，队满。

> [!question] 选择题 9
> 消息队列（Message Queue）在分布式系统中的主要作用是？
> - [ ] A. 数据排序
> - [ ] B. 异步通信和解耦
> - [ ] C. 加速计算
> - [ ] D. 数据压缩
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > 
> > **解析**: 消息队列实现生产者-消费者模式，用于系统间异步通信和解耦。生产者发送消息到队列，消费者从队列取出处理，二者不需要同时在线。

> [!question] 选择题 10
> 阻塞队列（Blocking Queue）在队列为空时执行pop操作会怎样？
> - [ ] A. 返回null/默认值
> - [ ] B. 抛出异常
> - [ ] C. 阻塞当前线程直到有元素入队
> - [ ] D. 未定义行为
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > 
> > **解析**: 阻塞队列在队列为空时，pop操作会阻塞调用线程，直到有其他线程往队列中添加了元素。这是多线程生产者-消费者模式的基础。

---

### 💻 编程大题

> [!note] 编程题 1：实现一个循环队列（支持动态扩容）
> **要求**：
> 1. 使用数组实现循环队列 `CircularQueue<T>`
> 2. 支持操作：push, pop, front, back, empty, size, full
> 3. 初始容量为8，队满时自动扩容为2倍
> 4. 扩容时正确处理元素的搬迁（注意循环排列）
> 5. 正确处理 front > rear 的环绕情况
> 6. 编写测试：连续push/pop操作后验证正确性
>
> **提示**: 扩容时按逻辑顺序（从front到rear）复制元素到新数组，然后重置front=0

> [!note] 编程题 2：实现滑动窗口最大值（单调队列）
> **要求**：
> 1. 给定一个整数数组和窗口大小k，输出每个窗口位置的最大值
> 2. 使用双端队列(deque)实现单调队列，保证总时间O(n)
> 3. 单调队列中存储数组下标（而非值），便于判断元素是否在窗口内
> 4. 实现逻辑：
>    - 入队前，从队尾弹出所有值小于当前元素的下标
>    - 检查队头下标是否已超出窗口范围，超出则弹出
>    - 队头即为当前窗口最大值
> 5. 处理边界：k=1、k>=数组长度、数组为空等情况
>
> **提示**: 队列中维护的是"可能成为最大值"的元素下标，呈递减排列

> [!note] 编程题 3：多级反馈队列调度模拟器
> **要求**：
> 1. 模拟操作系统的多级反馈队列（MLFQ）CPU调度算法
> 2. 设计3个优先级队列，时间片分别为：高=2, 中=4, 低=8
> 3. 每个进程有：PID、到达时间、所需CPU时间
> 4. 调度规则：
>    - 新进程进入最高优先级队列
>    - 在当前队列用完时间片但未完成，降级到下一队列
>    - 低优先级队列为FCFS（先来先服务）
> 5. 输出：每个进程的完成时间、等待时间、周转时间
> 6. 计算平均等待时间和平均周转时间
>
> **提示**: 使用时间驱动模拟，每个时间单位检查是否有新进程到达

### 🔗 推荐练习题（洛谷）

| 题号 | 题目 | 难度 | 知识点 |
|------|------|------|--------|
| [P1540](https://www.luogu.com.cn/problem/P1540) | 机器翻译 | 入门 | 队列模拟、缓存淘汰 |
| [P1886](https://www.luogu.com.cn/problem/P1886) | 滑动窗口 | 普及+ | 单调队列、滑动窗口最值 |

---

## --------------------------------------------------------------------------
## 🔗 知识网络
## --------------------------------------------------------------------------

- **上一章**: [[B_栈_Stack]] | **下一章**: [[Q_排序_八大排序_Sorting]] | **返回**: [[DSA学习路线]]
- **相关容器**: [[容器类/05_queue]]
- **算法技巧**: [[../算法技巧/搜索]] | [[../算法技巧/滑动窗口]]
