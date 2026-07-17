---
C++ 功能库 — function / bind
---

## 概述

`function` 是可调用对象的通用包装器——通过类型擦除(type erasure)将函数指针、函数对象、lambda 统一为 `function<R(Args...)>` 类型。`bind` 用于固定部分参数或重排参数顺序。两者配合实现回调、策略模式、延迟调用等函数式编程范式。

## 核心组件

| 组件 | 说明 |
|------|------|
| `function<R(Args...)>` | 可调用对象包装器，类型擦除，SBO 优化 |
| `bind(f, args...)` | 参数绑定，返回函数对象 |
| `placeholders::_1, _2, ...` | `bind` 的占位符，标记未绑定参数 |
| `mem_fn` | 将成员函数转为可调用对象 |
| `reference_wrapper<T>` / `REF(t)` | 引用包装，让 `bind` 按引用传递 |
| `not_fn` (C++17) | 反转谓词 |

## 典型用法

### function —— 统一可调用对象

```
FUNCTION demo_function:
    // function 可以持有任何匹配签名的可调用物
    op = FUNCTION<INT(INT, INT)>()

    // 赋值为 lambda
    op = LAMBDA(a, b): RETURN a + b
    PRINT op(3, 5)                              // 8

    // 赋值为函数对象
    multiplier = FUNCTOR:
        factor = 0
        CONSTRUCTOR(f): factor = f
        CALL(x): RETURN x * factor
    END FUNCTOR
    op = BIND(multiplier(3), _1, _2)

    // 存入容器，多态调用
    callbacks = VECTOR<FUNCTION<VOID()>>()
    callbacks.PUSH(LAMBDA: PRINT "first")
    callbacks.PUSH(LAMBDA: PRINT "second")
    FOR f IN callbacks: f()
```

### bind —— 参数绑定

```
FUNCTION demo_bind:
    ADD_FUNC add(a, b, c): RETURN a + b + c

    add_10 = BIND(add, 10, _1, _2)              // 固定第一个参数
    PRINT add_10(3, 5)                          // 18（10+3+5）

    add_10_20 = BIND(add, 10, 20, _1)           // 固定前两个
    PRINT add_10_20(30)                         // 60

    reversed = BIND(add, _3, _2, _1)            // 重排
    PRINT reversed(1, 2, 3)                     // 6（3+2+1）
```

### bind 与成员函数

```
FUNCTION demo_member_bind:
    Printer = OBJECT:
        msg = STRING()
        print_prefix = METHOD(prefix):
            PRINT prefix, msg
        END METHOD
    END OBJECT

    p = Printer{msg = "World"}
    bound = BIND(&Printer::print_prefix, p, "Hello")
    bound()                                     // "Hello World"

    // 也可以用 mem_fn
    f = MEM_FN(&Printer::print_prefix)
    f(p, "Hello")                               // "Hello World"
```

### reference_wrapper —— 按引用传递

```
FUNCTION demo_ref:
    counter = 0

    // bind 默认按值捕获，需要 REF 才能引用
    inc = BIND(LAMBDA(n): n++, REF(counter))
    inc()                                       // 修改的是 counter 引用
    PRINT counter                               // 1
```

---

- **lambda**: [[./lambda|lambda]] — 最常用的可调用对象
- **hash**: [[./hash|hash]] — 哈希函数对象
- **算法配合**: `function` 作为 `sort`/`for_each` 等算法的参数
- **C 对照**: 函数指针（`void (*f)(int)`），无闭包能力
- **返回目录**: 
