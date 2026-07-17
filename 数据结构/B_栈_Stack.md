# B 栈 Stack

建议先阅读: [[A_容器_Container|A 容器 Container]]

---

## 原理

栈（Stack）是一种受限的线性数据结构，遵循后进先出（LIFO, Last In First Out）原则。只能在一端（栈顶）进行插入和删除操作。

### 核心操作

| 操作 | 描述 | 时间复杂度 |
|------|------|-----------|
| push | 将元素压入栈顶 | O(1) |
| pop | 弹出栈顶元素 | O(1) |
| top | 获取栈顶元素（不弹出） | O(1) |
| empty | 判断栈是否为空 | O(1) |
| size | 返回栈中元素个数 | O(1) |

### 底层实现方式

- **数组实现**: 固定容量或动态扩容，push 均摊 O(1)
- **链表实现**: 无容量限制，每个节点额外存指针

### 函数调用栈原理

系统调用栈为每个被调用的函数分配一个"栈帧"（Stack Frame），存储局部变量、参数、返回地址和寄存器状态。函数返回时栈帧被弹出。递归过深或局部变量过大可能导致栈溢出（Stack Overflow），通常限制为 1MB~8MB。

---

## 实现

### 基于动态数组的栈

```cpp
#include <iostream>
#include <stdexcept>

template <typename T>
class ArrayStack {
private:
    T* _data;
    size_t _capacity;
    size_t _top; // 栈顶指针（指向下一个空位）

    void expand() {
        size_t new_cap = (_capacity == 0) ? 8 : _capacity * 2;
        T* new_data = new T[new_cap];
        for (size_t i = 0; i < _top; ++i)
            new_data[i] = _data[i];
        delete[] _data;
        _data = new_data;
        _capacity = new_cap;
    }

public:
    ArrayStack() : _data(nullptr), _capacity(0), _top(0) {}
    ~ArrayStack() { delete[] _data; }

    void push(const T& value) {
        if (_top >= _capacity) expand();
        _data[_top++] = value;
    }

    void pop() {
        if (_top == 0) throw std::underflow_error("stack empty");
        --_top;
    }

    T& top() {
        if (_top == 0) throw std::underflow_error("stack empty");
        return _data[_top - 1];
    }

    bool empty() const { return _top == 0; }
    size_t size() const { return _top; }
};
```

### 基于链表的栈

```cpp
template <typename T>
class LinkedStack {
private:
    struct Node {
        T data;
        Node* next;
        Node(const T& val, Node* nxt = nullptr) : data(val), next(nxt) {}
    };
    Node* _head; // 栈顶
    size_t _count;

public:
    LinkedStack() : _head(nullptr), _count(0) {}
    ~LinkedStack() {
        while (_head) {
            Node* tmp = _head;
            _head = _head->next;
            delete tmp;
        }
    }

    void push(const T& value) {
        _head = new Node(value, _head);
        ++_count;
    }

    void pop() {
        if (!_head) throw std::underflow_error("stack empty");
        Node* tmp = _head;
        _head = _head->next;
        delete tmp;
        --_count;
    }

    T& top() {
        if (!_head) throw std::underflow_error("stack empty");
        return _head->data;
    }

    bool empty() const { return _head == nullptr; }
    size_t size() const { return _count; }
};
```

### 最小栈（MinStack）

在 O(1) 时间内获取栈中最小值的栈：

```cpp
#include <stack>
#include <algorithm>

template <typename T>
class MinStack {
private:
    std::stack<T> data_stack;
    std::stack<T> min_stack;

public:
    void push(const T& value) {
        data_stack.push(value);
        if (min_stack.empty() || value <= min_stack.top())
            min_stack.push(value);
    }

    void pop() {
        if (data_stack.top() == min_stack.top())
            min_stack.pop();
        data_stack.pop();
    }

    T top() const { return data_stack.top(); }
    T getMin() const { return min_stack.top(); }
    bool empty() const { return data_stack.empty(); }
};
```

---

## STL 使用

```cpp
#include <stack>
#include <iostream>

int main() {
    std::stack<int> stk;

    stk.push(10);
    stk.push(20);
    stk.push(30);

    std::cout << "top: " << stk.top() << std::endl; // 30
    std::cout << "size: " << stk.size() << std::endl; // 3

    stk.pop(); // 弹出 30

    while (!stk.empty()) {
        std::cout << stk.top() << " ";
        stk.pop();
    }
    // 输出: 20 10

    return 0;
}
```

stack 默认底层容器是 deque，可指定为 vector 或 list：`std::stack<int, std::vector<int>> stk;`

### 核心算法：括号匹配

```cpp
#include <string>
#include <stack>

bool isBalanced(const std::string& expr) {
    std::stack<char> stk;
    for (char ch : expr) {
        if (ch == '(' || ch == '[' || ch == '{') {
            stk.push(ch);
        } else if (ch == ')' || ch == ']' || ch == '}') {
            if (stk.empty()) return false;
            char top = stk.top(); stk.pop();
            if ((ch == ')' && top != '(') ||
                (ch == ']' && top != '[') ||
                (ch == '}' && top != '{'))
                return false;
        }
    }
    return stk.empty();
}
```

### 核心算法：后缀表达式求值

```cpp
#include <string>
#include <sstream>

int evalRPN(const std::string& expr) {
    std::stack<int> stk;
    std::istringstream iss(expr);
    std::string token;
    while (iss >> token) {
        if (token == "+" || token == "-" || token == "*" || token == "/") {
            int b = stk.top(); stk.pop();
            int a = stk.top(); stk.pop();
            if (token == "+") stk.push(a + b);
            else if (token == "-") stk.push(a - b);
            else if (token == "*") stk.push(a * b);
            else stk.push(a / b);
        } else {
            stk.push(std::stoi(token));
        }
    }
    return stk.top();
}
```

### 核心算法：中缀转后缀

```cpp
#include <string>
#include <cctype>

int precedence(char op) {
    if (op == '+' || op == '-') return 1;
    if (op == '*' || op == '/') return 2;
    return 0;
}

std::string infixToPostfix(const std::string& expr) {
    std::stack<char> stk;
    std::string output;
    for (char ch : expr) {
        if (std::isalnum(ch)) {
            output += ch;
        } else if (ch == '(') {
            stk.push(ch);
        } else if (ch == ')') {
            while (!stk.empty() && stk.top() != '(') {
                output += stk.top(); stk.pop();
            }
            stk.pop(); // 弹出 '('
        } else { // 运算符
            while (!stk.empty() && precedence(stk.top()) >= precedence(ch)) {
                output += stk.top(); stk.pop();
            }
            stk.push(ch);
        }
    }
    while (!stk.empty()) {
        output += stk.top(); stk.pop();
    }
    return output;
}
```

---

## 应用场景

- **括号匹配**: 编译器语法检查、代码编辑器的自动补全
- **表达式求值**: 计算器中缀表达式转后缀并求值
- **DFS 非递归实现**: 手动用栈替代系统递归栈，避免递归深度限制
- **浏览器的前进/后退**: 两个栈分别管理后退历史与前进历史
- **撤销操作**: 编辑器中的 Undo 功能，按操作顺序入栈，撤销时出栈

---

## 练习

| 题号 | 题目 | 难度 | 知识点 |
|------|------|------|--------|
| P1449 | 后缀表达式 | 入门 | 栈、后缀表达式求值 |
| P1739 | 表达式括号匹配 | 入门 | 栈、括号匹配 |
| P1981 | 表达式求值 | 普及 | 栈、中缀表达式 |
