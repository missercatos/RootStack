

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

```c
#include <stdlib.h>

typedef struct {
    int* data;
    size_t capacity;
    size_t top;   // 指向下一个空位，同时也是元素个数
} ArrayStack;

void as_init(ArrayStack* s) {
    s->data = NULL;
    s->capacity = 0;
    s->top = 0;
}

void as_destroy(ArrayStack* s) {
    free(s->data);
    s->data = NULL;
    s->capacity = 0;
    s->top = 0;
}

int as_expand(ArrayStack* s) {
    size_t new_cap = s->capacity == 0 ? 8 : s->capacity * 2;
    int* new_data = realloc(s->data, new_cap * sizeof(int));
    if (!new_data) return -1;
    s->data = new_data;
    s->capacity = new_cap;
    return 0;
}

int as_push(ArrayStack* s, int value) {
    if (s->top >= s->capacity)
        if (as_expand(s) != 0) return -1;
    s->data[s->top++] = value;
    return 0;
}

int as_pop(ArrayStack* s) {
    if (s->top == 0) return -1;
    s->top--;
    return 0;
}

int as_top(ArrayStack* s, int* out) {
    if (s->top == 0) return -1;
    *out = s->data[s->top - 1];
    return 0;
}

int as_empty(ArrayStack* s) { return s->top == 0; }
size_t as_size(ArrayStack* s) { return s->top; }
```

### 基于链表的栈

```c
#include <stdlib.h>

typedef struct Node {
    int data;
    struct Node* next;
} Node;

typedef struct {
    Node* head;   // 栈顶
    size_t count;
} LinkedStack;

void ls_init(LinkedStack* s) {
    s->head = NULL;
    s->count = 0;
}

void ls_destroy(LinkedStack* s) {
    while (s->head) {
        Node* tmp = s->head;
        s->head = s->head->next;
        free(tmp);
    }
    s->count = 0;
}

int ls_push(LinkedStack* s, int value) {
    Node* node = malloc(sizeof(Node));
    if (!node) return -1;
    node->data = value;
    node->next = s->head;
    s->head = node;
    s->count++;
    return 0;
}

int ls_pop(LinkedStack* s) {
    if (!s->head) return -1;
    Node* tmp = s->head;
    s->head = s->head->next;
    free(tmp);
    s->count--;
    return 0;
}

int ls_top(LinkedStack* s, int* out) {
    if (!s->head) return -1;
    *out = s->head->data;
    return 0;
}

int ls_empty(LinkedStack* s) { return s->head == NULL; }
size_t ls_size(LinkedStack* s) { return s->count; }
```

### 最小栈（MinStack）

在 O(1) 时间内获取栈中最小值的栈，用两个普通栈模拟：

```c
#include <stdlib.h>
#include <limits.h>

typedef struct {
    int* data;
    int* min;
    size_t capacity;
    size_t top;
} MinStack;

void ms_init(MinStack* s) {
    s->capacity = 16;
    s->data = malloc(s->capacity * sizeof(int));
    s->min  = malloc(s->capacity * sizeof(int));
    s->top = 0;
}

void ms_destroy(MinStack* s) {
    free(s->data);
    free(s->min);
}

int ms_push(MinStack* s, int value) {
    if (s->top >= s->capacity) {
        s->capacity *= 2;
        s->data = realloc(s->data, s->capacity * sizeof(int));
        s->min  = realloc(s->min,  s->capacity * sizeof(int));
    }
    s->data[s->top] = value;
    s->min[s->top]  = (s->top == 0) ? value
                    : (value < s->min[s->top - 1] ? value : s->min[s->top - 1]);
    s->top++;
    return 0;
}

int ms_pop(MinStack* s) {
    if (s->top == 0) return -1;
    s->top--;
    return 0;
}

int ms_top(MinStack* s, int* out) {
    if (s->top == 0) return -1;
    *out = s->data[s->top - 1];
    return 0;
}

int ms_get_min(MinStack* s, int* out) {
    if (s->top == 0) return -1;
    *out = s->min[s->top - 1];
    return 0;
}
```

---

## 各语言标准库对比

| 语言 | 栈类型 | 说明 |
|------|--------|------|
| C | 无（手写） | 标准库不提供，需自行实现 |
| C++ | stack | 默认底层为 deque，可指定 vector 或 list |
| Java | Stack / ArrayDeque | Stack 是遗留类，推荐 ArrayDeque |
| Python | 无（用 list） | list.append / list.pop 模拟栈 |
| Rust | Vec | push / pop 方法天然实现栈 |

---

## 经典算法示例

以下算法演示栈的核心应用，用 C 实现以展示本质逻辑。

### 括号匹配

```c
#include <stdio.h>
#include <string.h>

int is_balanced(const char* expr) {
    int len = strlen(expr);
    char* stk = malloc(len);
    int top = 0;
    for (int i = 0; i < len; i++) {
        char ch = expr[i];
        if (ch == '(' || ch == '[' || ch == '{') {
            stk[top++] = ch;
        } else if (ch == ')' || ch == ']' || ch == '}') {
            if (top == 0) { free(stk); return 0; }
            char t = stk[--top];
            if ((ch == ')' && t != '(') ||
                (ch == ']' && t != '[') ||
                (ch == '}' && t != '{')) {
                free(stk); return 0;
            }
        }
    }
    int ok = (top == 0);
    free(stk);
    return ok;
}
```

### 中缀转后缀（调度场算法）

调度场算法由 Dijkstra 提出，用栈处理运算符优先级，将人类易读的**中缀表达式**（如 `3 + 4 * 2`）转为计算机易算的**后缀表达式**（如 `3 4 2 * +`）。

核心规则：
- 操作数直接输出
- 左括号入栈
- 右括号弹出直到左括号
- 运算符：弹掉栈顶所有优先级 >= 它的运算符，再入栈
- 结束后弹出栈中所有剩余运算符

示例推演：`3 + 4 * 2`

| 输入 | 输出（后缀） | 栈 | 说明 |
|------|-------------|-----|------|
| 3 | 3 | | 操作数直接输出 |
| + | 3 | + | 栈空，入栈 |
| 4 | 3 4 | + | 操作数直接输出 |
| * | 3 4 | + * | * 优先级 > +，入栈 |
| 2 | 3 4 2 | + * | 操作数直接输出 |
| 结束 | 3 4 2 * + | | 弹出所有运算符 |

```c
int precedence(char op) {
    if (op == '+' || op == '-') return 1;
    if (op == '*' || op == '/') return 2;
    return 0;
}

// 中缀表达式转后缀，输入保证无空格，操作数为单个字母/数字
void infix_to_postfix(const char* expr, char* output) {
    int len = strlen(expr);
    char* stk = malloc(len);
    int top = 0, out_idx = 0;
    for (int i = 0; i < len; i++) {
        char ch = expr[i];
        if (ch >= '0' && ch <= '9') {
            output[out_idx++] = ch;
        } else if (ch == '(') {
            stk[top++] = ch;
        } else if (ch == ')') {
            while (top > 0 && stk[top - 1] != '(')
                output[out_idx++] = stk[--top];
            top--;  // 弹出 '('
        } else {  // 运算符
            while (top > 0 && precedence(stk[top - 1]) >= precedence(ch))
                output[out_idx++] = stk[--top];
            stk[top++] = ch;
        }
    }
    while (top > 0)
        output[out_idx++] = stk[--top];
    output[out_idx] = '\0';
    free(stk);
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
