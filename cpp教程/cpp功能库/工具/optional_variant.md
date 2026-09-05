---
title: "C++ 功能库 — optional / variant / any / expected"
---

## 概述

这四个类型解决了 C 语言中用 `NULL`/`union`/`void*`/`errno` 处理的不安全问题，提供类型安全的"值可能存在/不存在"、"值可能是几种类型之一"、"值可能是任意类型"、"值要么正确要么包含错误"的语义。

- `optional`: 值可能存在，也可能不存在（替代 `NULL`）
- `variant`: 类型安全的联合体，同一时刻持有一种类型（替代 `union`）
- `any`: 任意类型容器（替代 `void*`）
- `expected` (C++23): 要么是有用值，要么是错误（类似 Rust 的 `Result`）

## 核心组件

| 组件 | 说明 | 引入版本 |
|------|------|----------|
| `optional<T>` | 可选值 | C++17 |
| `nullopt` | 空 optional 的标志 | C++17 |
| `variant<T...>` | 类型安全联合体 | C++17 |
| `visit` | 访问 variant 当前持有的值 | C++17 |
| `holds_alternative<T>(v)` | 检查 variant 是否持有 T 类型 | C++17 |
| `any` | 任意类型容器 | C++17 |
| `any_cast<T>(a)` | 从 any 中取出 T 类型的值 | C++17 |
| `expected<T, E>` | 带错误的值 | C++23 |

## std::optional 深入

### 基本用法

```cpp
// 作为返回值：表示可能不存在的结果
std::optional<std::string> find_user(int id) {
    if (id == 42) return "Alice";
    return std::nullopt;
}

auto result = find_user(42);
if (result) {
    std::cout << *result << "\n";           // "Alice"
    std::cout << result.value() << "\n";    // "Alice"
}
std::cout << result.value_or("Unknown");     // "Alice"

auto missing = find_user(99);
std::cout << missing.value_or("Unknown");    // "Unknown"
```

### 单子操作 (C++23)

C++23 为 `optional` 添加了函数式链式操作：

```cpp
// and_then: 链式操作，函数返回 optional
std::optional<int> parse_int(const std::string& s) {
    try { return std::stoi(s); }
    catch (...) { return std::nullopt; }
}

auto result = std::string("42")
    |> parse_int           // optional<int>(42)
    |> [](std::optional<int> v) -> std::optional<int> {
        if (v && *v > 0) return *v * 2;
        return std::nullopt;
    };
// result = optional<int>(84)

// transform: 对值应用函数，保持 optional 包装
auto doubled = parse_int("42")
    .transform([](int x) { return x * 2; });
// doubled = optional<int>(84)

// or_else: 值不存在时执行副作用
parse_int("abc")
    .or_else([] { std::cerr << "Parse failed\n"; });

// 传统写法 vs C++23 链式写法
// 传统：
auto r = parse_int(s);
if (r) {
    auto r2 = transform(*r);
    if (r2) { /* ... */ }
}

// C++23：
auto r = parse_int(s)
    .transform(transform)
    .value_or(default_val);
```

### optional 性能

```
sizeof(optional<T>) = sizeof(T) + sizeof(bool) + 对齐填充
sizeof(optional<int>) = 8   (4 + 1 + 3 填充)
sizeof(optional<double>) = 16 (8 + 1 + 7 填充)

// 空 optional 不分配堆内存，标志位在对象内部
```

## std::variant 深入

### 访问者模式 (visit)

```cpp
// visit 是访问 variant 的唯一安全方式
using Value = std::variant<int, double, std::string>;

Value v = 42;

// 基本 visit
std::visit([](auto&& arg) {
    std::cout << arg << "\n";
}, v);

// 带返回值的 visit
auto size = std::visit([](auto&& arg) -> size_t {
    using T = std::decay_t<decltype(arg)>;
    if constexpr (std::is_same_v<T, std::string>) {
        return arg.size();
    } else {
        return sizeof(T);
    }
}, v);

// 重载模式 (overloaded pattern)
template<class... Ts> struct overloaded : Ts... { using Ts::operator()...; };
template<class... Ts> overloaded(Ts...) -> overloaded<Ts...>;

std::visit(overloaded{
    [](int i) { std::cout << "int: " << i; },
    [](double d) { std::cout << "double: " << d; },
    [](const std::string& s) { std::cout << "string: " << s; }
}, v);
```

### variant 与类型安全

```cpp
// variant 替代 union
union BadUnion {  // 不安全：可能读写错误类型
    int i;
    double d;
    std::string s;  // 非平凡类型在 union 中需要手动管理
};

// variant 安全：自动管理构造/析构
std::variant<int, double, std::string> safe_var;  // 默认持有 int(0)
safe_var = "hello";  // 自动析构 int，构造 string

// 获取当前类型
if (auto* p = std::get_if<std::string>(&safe_var)) {
    std::cout << *p << "\n";
} else {
    // 类型不匹配，p 为 nullptr
}

// index() 获取当前持有的类型索引
size_t idx = safe_var.index();  // 2 (string 是第 3 个类型)
```

### variant 实际应用：JSON 值类型

```cpp
// 简化版 JSON 值
struct JsonValue;
using JsonArray = std::vector<JsonValue>;
using JsonObject = std::map<std::string, JsonValue>;

struct JsonValue : std::variant<
    std::nullptr_t,   // null
    bool,             // boolean
    double,           // number
    std::string,      // string
    JsonArray,        // array
    JsonObject        // object
> {
    using variant::variant;
};

// 递归访问
void print(const JsonValue& val) {
    std::visit(overloaded{
        [](std::nullptr_t) { std::cout << "null"; },
        [](bool b) { std::cout << (b ? "true" : "false"); },
        [](double d) { std::cout << d; },
        [](const std::string& s) { std::cout << "\"" << s << "\""; },
        [](const JsonArray& arr) {
            std::cout << "[";
            for (size_t i = 0; i < arr.size(); ++i) {
                if (i) std::cout << ", ";
                print(arr[i]);
            }
            std::cout << "]";
        },
        [](const JsonObject& obj) {
            std::cout << "{";
            bool first = true;
            for (auto& [k, v] : obj) {
                if (!first) std::cout << ", ";
                std::cout << "\"" << k << "\": ";
                print(v);
                first = false;
            }
            std::cout << "}";
        }
    }, val);
}
```

## std::any

```cpp
// any 是类型擦除容器：任何可拷贝的类型都可存储
std::any a = 42;
a = std::string("hello");
a = 3.14;

// 必须知道类型才能取值
if (a.type() == typeid(int)) {
    std::cout << std::any_cast<int>(a) << "\n";
}

// 性能注意：
// sizeof(any) = 通常 16-32 字节（小对象优化）
// 小于 SSO 阈值（通常 8-32 字节）的对象不分配堆内存
// 大于阈值的对象分配堆内存

// any vs variant vs optional 选择指南：
// any:    编译期不知道可能的类型集
// variant: 编译期知道所有可能的类型
// optional: 值可能存在或不存在（不涉及多种类型）
```

## expected (C++23)

```cpp
// expected 替代异常和 error code
enum class ParseError { Empty, InvalidFormat, Overflow };

std::expected<int, ParseError> parse_int(const std::string& s) {
    if (s.empty()) return std::unexpected(ParseError::Empty);
    // ... 解析逻辑
    return std::stoi(s);
}

auto result = parse_int("42");
if (result) {
    std::cout << *result << "\n";       // 42
    std::cout << result.value() << "\n"; // 42
} else {
    std::cout << "Error: " << static_cast<int>(result.error()) << "\n";
}

// and_then 链式操作
auto result2 = parse_int("10")
    .and_then([](int v) -> std::expected<int, ParseError> {
        if (v > 100) return std::unexpected(ParseError::Overflow);
        return v * 2;
    });

// transform 转换值
auto str_result = parse_int("42")
    .transform([](int v) { return std::to_string(v); });
// str_result = expected<string, ParseError>("42")

// or_else 处理错误
parse_int("abc")
    .or_else([](ParseError e) {
        std::cerr << "Parse failed: " << static_cast<int>(e) << "\n";
    });

// value_or 提供默认值
int val = parse_int("abc").value_or(0);  // 0
```

### expected vs 异常

```
特征           expected              异常
────────────────────────────────────────────
编译器强制      否（可忽略 error）    是（必须 catch）
性能            零开销（栈展开）      有开销（栈展开）
代码可读性      显式（调用者检查）    隐式（可能忽略）
适用于          预期内的错误          不可恢复的错误
```

## 常见陷阱与最佳实践

1. **optional 解引用前检查**：`*opt` 在空 optional 上是未定义行为
2. **variant 访问安全**：优先用 `visit` 而非 `get<T>`（后者可能抛异常）
3. **any 性能开销**：类型擦除有虚调用开销，频繁使用考虑 variant
4. **expected 可忽略**：`parse_int("abc")` 不检查 error → 未定义行为
5. **优先 variant over any**：类型安全 + 编译期检查 + 性能更优

## 力扣练习

| 题号 | 题目 | 链接 | 知识点 |
|------|------|------|--------|
| 1 | 两数之和 | https://leetcode.cn/problems/two-sum/ | 哈希表可存储 optional |
| 128 | 最长连续序列 | https://leetcode.cn/problems/longest-consecutive-sequence/ | set 查找类似 optional |
| 347 | 前 K 个高频元素 | https://leetcode.cn/problems/top-k-frequent-elements/ | variant 思路 |
| 215 | 数组中的第K个最大元素 | https://leetcode.cn/problems/kth-largest-element-in-an-array/ | nth_element |
| 146 | LRU 缓存 | https://leetcode.cn/problems/lru-cache/ | optional 用于查找结果 |
| 23 | 合并 K 个升序链表 | https://leetcode.cn/problems/merge-k-sorted-lists/ | variant 存储不同优先级 |
| 78 | 子集 | https://leetcode.cn/problems/subsets/ | variant 子集枚举 |
| 17 | 电话号码的字母组合 | https://leetcode.cn/problems/letter-combinations-of-a-phone-number/ | optional 用于回溯剪枝 |
| 46 | 全排列 | https://leetcode.cn/problems/permutations/ | variant 状态管理 |
| 22 | 括号生成 | https://leetcode.cn/problems/generate-parentheses/ | optional 回溯 |
| 39 | 组合总和 | https://leetcode.cn/problems/combination-sum/ | variant 组合 |
| 102 | 二叉树的层序遍历 | https://leetcode.cn/problems/binary-tree-level-order-traversal/ | optional 节点存在检查 |

---

- **pair / tuple**: [[pair_tuple|pair / tuple]] — 多值聚合
- **智能指针**: [[../内存/smart_ptr|smart_ptr]] — `optional` 也可表达"可能为空"
- **span**: [[span_bitset|span / bitset]] — 数组视图
- **C 对照**: `NULL`/`union`/`void*`/`errno` 均无类型安全
- **返回目录**:
