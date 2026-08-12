---
title: "C++ 功能库 — hash"
---

## 概述

`hash<T>` 是函数对象模板，为 `T` 类型提供哈希值计算。它作为 `unordered_set`/`unordered_map` 的默认哈希策略，决定元素放入哪个桶。标准库为所有基本类型和 `string` 提供了特化，自定义类型需要手动特化 `hash` 模板或提供自定义哈希函数对象。

## 核心概念

```
unordered_map<T, U>:
 HASH<T> ──→ hash(key) ──→ 桶索引 ──→ 找到元素
 EQUAL<T> ──→ eq(a, b) ──→ 比较桶内元素
```

自主实现哈希需同时提供 `hash` 函数和 `equal_to` 比较。

## 核心组件

| 组件 | 说明 |
|------|------|
| `hash<T>` | 哈希函数对象模板，`hash<T>{}` 构造对象，`hash<T>{}(val)` 计算哈希 |
| `hash<string>` | 字符串的哈希（已内置特化） |
| `hash<int>` / `hash<double>` 等 | 基本类型哈希 |

## 典型用法

### 基本类型哈希

```
FUNCTION demo_basic_hash:
 hasher = HASH<STRING>{} // 构造哈希对象
 h1 = hasher("hello") // 计算 "hello" 的哈希
 h2 = HASH<INT>{}(42) // 42 的哈希
 h3 = HASH<DOUBLE>{}(3.14)
```

### 自定义类型的哈希（特化 hash 模板）

```
FUNCTION demo_custom_hash:
 USING Point = PAIR<INT, INT> // (x, y)

 // 方法 1: 特化 std::hash
 SPECIALIZE HASH<Point>:
 SIZE_T CALL(const Point& p) CONST:
 h1 = HASH<INT>{}(p.FIRST)
 h2 = HASH<INT>{}(p.SECOND)
 RETURN h1 XOR (h2 << 1) // 组合两个哈希
 END CALL
 END SPECIALIZE

 // 现在 Point 可用作 unordered_set 的 key（默认 hash 和 equal_to）
 points = UNORDERED_SET<Point>()
 points.INSERT(Point{3, 5})
```

### 自定义哈希函数对象（不特化 hash）

```
FUNCTION demo_custom_functor:
 USING Person = OBJECT:
 name = STRING()
 age = INT
 END OBJECT

 // 自定义哈希函数对象
 PersonHash = FUNCTOR:
 SIZE_T CALL(const Person& p) CONST:
 RETURN HASH<STRING>{}(p.name) XOR (HASH<INT>{}(p.age) << 1)
 END CALL
 END FUNCTOR

 PersonEqual = FUNCTOR:
 BOOL CALL(const Person& a, const Person& b) CONST:
 RETURN a.name == b.name AND a.age == b.age
 END CALL
 END FUNCTOR

 // 使用时显式指定
 mapping = UNORDERED_SET<Person, PersonHash, PersonEqual>()
```

### 组合哈希的技巧

```
FUNCTION demo_hash_combine:
 // 标准做法：用 XOR 和位移组合多个哈希
 COMBINE_HASH = LAMBDA(seed, val):
 seed = seed XOR (HASH<TYPEOF(val)>{}(val) + 0x9e3779b9 + (seed << 6) + (seed >> 2))
 RETURN seed
 END LAMBDA

 // 对复合类型
 HASH PointHash(p):
 seed = 0
 seed = COMBINE_HASH(seed, p.x)
 seed = COMBINE_HASH(seed, p.y)
 seed = COMBINE_HASH(seed, p.z)
 RETURN seed
 END HASH
```

---

- **function / bind**: [[function|function / bind]] — 可调用对象包装器
- **lambda**: [[lambda|lambda]] — 用 lambda 实现自定义哈希
- **关联容器**: `unordered_set` / `unordered_map` 直接使用 `hash`
- **C 对照**: 无标准哈希函数，需手写或使用第三方
- **返回目录**: 
