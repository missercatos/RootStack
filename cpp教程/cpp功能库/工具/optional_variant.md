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

## 典型用法

### optional —— 可选值

```
FUNCTION demo_optional:
 // 作为返回值
 FIND_USER = LAMBDA(id) -> OPTIONAL<STRING>:
 IF id IN database:
 RETURN database[id]
 ELSE:
 RETURN NULLOPT // 空
 END IF
 END LAMBDA

 result = FIND_USER(42)
 IF result.HAS_VALUE():
 PRINT result.VALUE()
 ELSE:
 PRINT result.VALUE_OR("Unknown") // 提供默认值
 END IF

 // 安全解引用
 IF result: PRINT *result // bool 转换
 p = result.PTR() // 返回 T*（指向值或 nullptr）
```

### variant —— 类型安全联合体

```
FUNCTION demo_variant:
 USING Value = VARIANT<INT, DOUBLE, STRING>

 v = Value(42) // 持有 int
 v = 3.14 // 持有 double（替换）
 v = STRING("hello") // 持有 string

 // 按类型取
 IF HOLDS<STRING>(v):
 PRINT GET<STRING>(v)
 END IF

 // visit: 必须覆盖所有类型
 VISIT(LAMBDA(x):
 PRINT "值是:", x, ENDL
 , v)

 // visit 带返回值
 len = VISIT(LAMBDA(x) -> SIZE_T:
 IF TYPEOF(x) IS STRING: RETURN x.SIZE()
 ELSE IF T == INT: RETURN NUM_DIGITS(x)
 ELSE: RETURN 0
 , v)

 // 错误取值抛异常: get<INT>(v) 当 v 是 string 时 → bad_variant_access
```

### any —— 任意类型容器

```
FUNCTION demo_any:
 a = ANY(42)
 a = STRING("hello")
 a = 3.14

 // 必须知道当前类型才能取值
 IF a.TYPE() == TYPEID(INT):
 PRINT ANY_CAST<INT>(a)
 ELSE IF a.TYPE() == TYPEID(STRING):
 PRINT ANY_CAST<STRING>(a)
 END IF

 // 存储不同类型的消息
 messages = VECTOR<ANY>()
 messages.PUSH(ANY(42))
 messages.PUSH(ANY(STRING("text")))
 messages.PUSH(ANY(PAIR<INT, INT>{1, 2}))
```

### expected —— 带错误的值 (C++23)

```
FUNCTION demo_expected:
 DIVIDE_SAFE = LAMBDA(a, b) -> EXPECTED<DOUBLE, STRING>:
 IF b == 0:
 RETURN UNEXPECTED("div by zero")
 ELSE:
 RETURN a / DOUBLE(b)
 END IF
 END LAMBDA

 result = DIVIDE_SAFE(10, 2)
 IF result:
 PRINT result.VALUE() // 5.0
 ELSE:
 PRINT "error:", result.ERROR()
 END IF

 // 链式处理
 PRINT result.VALUE_OR(-1.0) // 错误时默认值
 result.AND_THEN(LAMBDA(x):
 RETURN x * 2 // 有值时继续
 )
```

---

- **pair / tuple**: [[pair_tuple|pair / tuple]] — 多值聚合
- **智能指针**: [[../内存/smart_ptr|smart_ptr]] — `optional` 也可表达"可能为空"
- **span**: [[span_bitset|span / bitset]] — 数组视图
- **C 对照**: `NULL`/`union`/`void*`/`errno` 均无类型安全
- **返回目录**: 
