---
title: "C++ 功能库 — lambda"
---

## 概述

lambda 表达式是 C++11 引入的匿名函数语法，编译器自动生成一个匿名函数对象类——捕获的变量成为该类的成员，lambda 体成为 `operator()` 的实现。lambda 是使用标准库算法、回调、延迟计算时最简洁的方式。

C++14 引入泛型 lambda（`auto` 参数），C++17 使其可用于 `constexpr` 上下文，C++20 支持模板语法。

## 语法结构

```
[捕获](参数列表) 可选说明符 → 返回类型 { 函数体 }
 └┬┘ └──┬──┘ ┌──────────────┐ └──┬──┘ └──┬──┘
 捕获 参数 mutable/constexpr 返回类型 函数体
 noexcept/consteval
```

## 捕获模式

| 语法 | 含义 |
|------|------|
| `[]` | 不捕获任何外部变量 |
| `[=]` | 按值捕获所有外部变量（副本） |
| `[&]` | 按引用捕获所有外部变量 |
| `[x]` | 按值捕获 x |
| `[&x]` | 按引用捕获 x |
| `[=, &x]` | 默认按值，x 例外按引用 |
| `[&, x]` | 默认按引用，x 例外按值 |
| `[this]` | 捕获当前对象的 `this` 指针 |
| `[*this]` (C++17) | 捕获当前对象的副本 |
| `[x = expr]` (C++14) | 初始化捕获，`x` 是新的成员变量 |

## 典型用法

### 基本形式

```
FUNCTION demo_basic:
 hello = LAMBDA: PRINT "hello" // 无参无返回
 hello()

 add = LAMBDA(a, b): RETURN a + b
 PRINT add(3, 5) // 8

 // 指定返回类型（通常可省略）
 divide = LAMBDA(a, b) -> DOUBLE:
 RETURN a / DOUBLE(b)
 END LAMBDA
```

### 泛型 lambda (C++14)

```
FUNCTION demo_generic:
 add = LAMBDA(x, y): RETURN x + y // auto 参数（泛型）
 PRINT add(1, 2) // 3
 PRINT add(1.5, 2.3) // 3.8
 PRINT add(STRING("a"), STRING("b")) // "ab"
```

### 捕获语义

```
FUNCTION demo_capture:
 x = 10
 by_val = LAMBDA: RETURN x + 5 // x 是副本
 by_ref = LAMBDA: RETURN x + 5 // x 是引用

 x = 20
 PRINT by_val() // 15（旧的 10+5）
 PRINT by_ref() // 25（新的 20+5）

 // 初始化捕获 (C++14)
 p = LAMBDA(ptr = MOVE(UNIQUE_PTR)):
 PRINT *ptr
 END LAMBDA // 移动 unique_ptr 进 lambda
```

### mutable lambda

```
FUNCTION demo_mutable:
 x = 0
 // 默认 lambda operator() 是 const，不能修改值捕获的变量
 counter = LAMBDA MUTABLE: RETURN x++ // mutable 允许修改
 PRINT counter() // 0
 PRINT counter() // 1
 PRINT x // 还是 0（x 是副本）
```

### 立即执行 lambda (IILE)

```
FUNCTION demo_iile:
 // 立即调用：初始化 const 变量时做复杂计算
 val = LAMBDA:
 result = 0
 FOR i = 1 TO 100:
 result = result + i * i
 END FOR
 RETURN result
 () // 立即调用
 PRINT val // 338350
```

---

- **function / bind**: [[function|function / bind]] — 可调用对象包装器
- **hash**: [[hash|hash]] — `hash` 函数对象
- **算法**: lambda 作为 `sort`/`find_if`/`transform` 等算法的谓词
- **C 对照**: 无 lambda，需手写函数或函数指针
- **返回目录**: 
