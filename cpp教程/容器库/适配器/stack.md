---
template <typename T, typename Container = deque<T>>
class stack
---

## 底层数据结构

**容器适配器**，默认底层容器为 `deque`，可指定 `vector` 或 `list`。stack 不是独立的数据结构，而是对底层容器的封装，仅暴露栈顶一端的操作。实现后进先出（LIFO）语义：最后压入的元素最先弹出。

## 复杂度

| 操作 | 复杂度 | 说明 |
|------|--------|------|
| push(x) | O(1) | 压入栈顶 |
| emplace(args...) | O(1) | 栈顶原位构造 |
| pop() | O(1) | 弹出栈顶，无返回值 |
| top() | O(1) | 返回栈顶引用 |
| size() / empty() | O(1) | |
| swap(st2) | O(1) | 交换两个栈 |

## 关键方法

| 方法 | 说明 |
|------|------|
| push(x) | 压入元素到栈顶 |
| emplace(args...) | 栈顶原位构造 |
| pop() | 弹出栈顶（返回 void） |
| top() | 返回栈顶元素的引用 |
| size() | 元素个数 |
| empty() | 判空 |

## 伪代码示例

```
stack<int> st

// 压入
st.push(1)
st.push(2)
st.push(3)

// 查看栈顶
print st.top()           // 3

// 弹出
st.pop()                 // 移除 3
print st.top()           // 2

// 括号匹配
stack<char> bracket
for each c in expression:
    if c is '(' or '[' or '{':
        bracket.push(c)
    else if c is ')' or ']' or '}':
        if bracket.empty():
            return false
        top = bracket.top()
        if not match(top, c):
            return false
        bracket.pop()
return bracket.empty()

// 十进制转二进制
stack<int> bits
while n > 0:
    bits.push(n % 2)
    n = n / 2
while not bits.empty():
    print bits.top()
    bits.pop()
```

stack 没有 `clear()`，清空用 `while (!empty()) pop()` 或 `st = stack<int>()`。
stack 没有迭代器，遍历只能通过反复 top() + pop() 清空式输出。

## 相关链接

- [[../../../数据结构/B_栈_Stack]]
- [[../../../数据结构/B_栈_Stack]]
- [[queue]]
