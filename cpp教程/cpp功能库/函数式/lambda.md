---
title: "C++ 功能库 — lambda"
---

## 概述

lambda 表达式是 C++11 引入的匿名函数语法，编译器自动生成一个匿名函数对象类——捕获的变量成为该类的成员，lambda 体成为 `operator()` 的实现。lambda 是使用标准库算法、回调、延迟计算时最简洁的方式。

C++14 引入泛型 lambda（`auto` 参数），C++17 使其可用于 `constexpr` 上下文，C++20 支持模板语法。

## 语法结构

```cpp
[捕获](参数列表) 可选说明符 -> 返回类型 { 函数体 }
 └┬┘ └──┬──┘ ┌──────────────┐ └──┬──┘ └──┬──┘
 捕获 参数 mutable/constexpr 返回类型 函数体
 noexcept/consteval
```

## 捕获模式详解

| 语法 | 含义 | 注意事项 |
|------|------|----------|
| `[]` | 不捕获任何外部变量 | 可隐式转换为函数指针 |
| `[=]` | 按值捕获所有外部变量（副本） | C++20 起不再隐式捕获 this |
| `[&]` | 按引用捕获所有外部变量 | 注意生命周期，悬垂引用是 UB |
| `[x]` | 按值捕获 x | x 必须可拷贝（或用初始化捕获移动） |
| `[&x]` | 按引用捕获 x | x 的生命周期必须长于 lambda |
| `[=, &x]` | 默认按值，x 例外按引用 | 默认模式只能出现一次 |
| `[&, x]` | 默认按引用，x 例外按值 | 默认模式只能出现一次 |
| `[this]` | 捕获当前对象的 `this` 指针 | 成员变量通过 this 访问 |
| `[*this]` (C++17) | 捕获当前对象的副本 | 值语义，避免悬垂 this |
| `[x = expr]` (C++14) | 初始化捕获 | 可移动捕获、捕获表达式结果 |

### 初始化捕获（C++14）

初始化捕获是 C++14 最强大的特性之一：

```cpp
// 移动捕获 unique_ptr
auto uptr = std::make_unique<int>(42);
auto lambda = [p = std::move(uptr)]() {
    std::cout << *p << "\n";
};
// uptr 现在为空

// 捕获表达式结果
auto lambda2 = [sz = vec.size()]() {
    return sz;  // 捕获时计算，之后 vec 变化不影响
};

// 重命名捕获
auto lambda3 = [x_copy = x]() {
    // 使用 x_copy 而非 x
};
```

### C++20 this 捕获变化

```cpp
// C++20 前：[=] 隐式捕获 this
// C++20 起：[=] 不再隐式捕获 this，需显式写 [=, this]

struct Foo {
    int x = 10;
    auto get() {
        return [=] { return x; };   // C++20: 错误，需要 [=, this]
        return [=, this] { return x; };  // C++20: 正确
    }
};
```

## mutable lambda

默认 lambda 的 `operator()` 是 `const`，不能修改值捕获的变量：

```cpp
int x = 0;
auto counter = [x]() mutable -> int { return x++; };
auto c1 = counter();  // 0
auto c2 = counter();  // 1
// 外部 x 仍为 0

// mutable 的典型用途：状态机、生成器
auto generator = [n = 0]() mutable {
    return ++n;
};
```

**注意**：`mutable` lambda 不能是 `constexpr` 的（C++23 前）。

## 泛型 lambda (C++14+)

```cpp
// auto 参数
auto add = [](auto x, auto y) { return x + y; };
add(1, 2);       // 3
add(1.5, 2.3);   // 3.8
add(std::string("a"), std::string("b")); // "ab"

// C++20 模板语法
auto print_all = []<typename T>(const std::vector<T>& v) {
    for (const auto& item : v) std::cout << item << " ";
};

// C++20 约束
auto safe_add = []<typename T>(T a, T b) requires std::is_arithmetic_v<T> {
    return a + b;
};
// safe_add("a", "b");  // 编译错误
```

## constexpr lambda (C++17+)

```cpp
// C++17: lambda 可用于 constexpr 上下文
constexpr auto factorial = [](int n) {
    int result = 1;
    for (int i = 2; i <= n; ++i) result *= i;
    return result;
};
static_assert(factorial(5) == 120);

// C++20: 更广泛的 constexpr 支持
constexpr auto is_even = [](int x) { return x % 2 == 0; };
static_assert(is_even(4));
```

## 立即执行 lambda (IIFE)

```cpp
// 初始化 const 变量时做复杂计算
const int val = []{
    int result = 0;
    for (int i = 1; i <= 100; ++i)
        result += i * i;
    return result;
}();
// val = 338350

// 线程安全的静态变量初始化（C++11 起保证）
auto& get_singleton() {
    static auto instance = []{
        Singleton s;
        s.init();
        return s;
    }();
    return instance;
}
```

## lambda vs 函数指针 vs std::function

| 特性 | lambda (无捕获) | 函数指针 | std::function |
|------|----------------|----------|---------------|
| 可隐式转为函数指针 | ✅ | — | ❌ |
| 有状态 | ❌ | ❌ | ✅ |
| 类型确定 | 编译期 | 编译期 | 运行时（类型擦除） |
| 内联优化 | ✅ | 通常可内联 | ❌（虚调用） |
| 大小 | 通常 1 字节 | 8 字节 | 32+ 字节 |

```cpp
// 无捕获 lambda 可当函数指针用
void call(int (*f)(int)) { std::cout << f(42) << "\n"; }
call([](int x) { return x * 2; }); // OK

// 有捕获 lambda 必须用 std::function 或 auto
int offset = 10;
std::function<int(int)> f = [offset](int x) { return x + offset; };
// 性能：std::function 有堆分配和虚调用开销
```

## 常见陷阱与最佳实践

1. **悬垂引用**：引用捕获的局部变量在 lambda 使用时已销毁
   ```cpp
   auto bad() {
       int x = 42;
       return [&x] { return x; }; // ⚠️ 返回引用到局部变量
   }
   ```

2. **[=] 隐式捕获 this**（C++20 前）可能导致意外捕获

3. **过度捕获**：捕获不需要的变量增加拷贝开销
   ```cpp
   // ❌ 捕获整个 vector
   auto f = [=] { return big_vec.size(); };
   // ✅ 只捕获需要的
   auto f = [size = big_vec.size()] { return size; };
   ```

4. **move-only 捕获与 std::function 不兼容**：`std::function` 需要拷贝，unique_ptr 不可拷贝

## 力扣练习

| 题号 | 题目 | 链接 | 知识点 |
|------|------|------|--------|
| 146 | LRU 缓存 | https://leetcode.cn/problems/lru-cache/ | lambda 作为回调、自定义数据结构 |
| 23 | 合并 K 个升序链表 | https://leetcode.cn/problems/merge-k-sorted-lists/ | lambda 比较器、优先队列 |
| 451 | 根据字符出现频率排序 | https://leetcode.cn/problems/sort-characters-by-frequency/ | lambda 自定义排序 |
| 912 | 排序数组 | https://leetcode.cn/problems/sort-an-array/ | lambda 作为 sort 谓词 |
| 215 | 数组中的第K个最大元素 | https://leetcode.cn/problems/kth-largest-element-in-an-array/ | lambda 比较器、nth_element |
| 692 | 前K个高频单词 | https://leetcode.cn/problems/top-k-frequent-words/ | lambda 多条件排序 |
| 739 | 每日温度 | https://leetcode.cn/problems/daily-temperatures/ | lambda + 单调栈 |
| 347 | 前 K 个高频元素 | https://leetcode.cn/problems/top-k-frequent-elements/ | lambda 比较器、堆 |
| 128 | 最长连续序列 | https://leetcode.cn/problems/longest-consecutive-sequence/ | lambda + 哈希集合 |

---

- **function / bind**: [[function|function / bind]] — 可调用对象包装器
- **hash**: [[hash|hash]] — `hash` 函数对象
- **算法**: lambda 作为 `sort`/`find_if`/`transform` 等算法的谓词
- **C 对照**: 无 lambda，需手写函数或函数指针
- **返回目录**:
