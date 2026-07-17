---
C++ 功能库 — pair / tuple
---

## 概述

`pair` 和 `tuple` 是 C++ 的异构聚合类型——将两个（`pair`）或任意多个（`tuple`）不同类型的值打包成一个对象。配合 C++17 的结构化绑定和 C++11 的 `tie`，可以优雅地实现多值返回、解包已有变量等操作。

## 核心组件

| 组件 | 说明 |
|------|------|
| `pair<T1, T2>` | 两个值的聚合，`.first`/`.second` 访问 |
| `tuple<T...>` | 任意数量、任意类型的聚合 |
| `make_pair(a, b)` | 创建 `pair`（自动推导类型） |
| `make_tuple(a, b, ...)` | 创建 `tuple` |
| `get<N>(t)` | 按索引提取 tuple 元素 |
| `get<T>(p)` | 按类型提取 pair/tuple 元素 |
| `tie(a, b, ...)` | 解包到已有变量 |
| `structured binding` (C++17) | `auto [a, b, c] = t` 解包到新变量 |
| `tuple_cat(t1, t2)` | 拼接两个 tuple |
| `forward_as_tuple(args...)` | 完美转发打包（用于原位构造） |

## 典型用法

### pair

```
FUNCTION demo_pair:
    p = PAIR<STRING, INT>("Alice", 25)
    PRINT p.FIRST, p.SECOND                    // Alice 25

    auto [name, age] = p                        // 结构化绑定 (C++17)
    PRINT name, age

    p2 = MAKE_PAIR("Bob", 30)                   // 自动推导类型

    // 用于 map 的 key-value
    entry = MAP<STRING, INT>::VALUE_TYPE("hi", 42)

    // 用于函数返回多值
    minmax = MINMAX_ELEMENT(v)                  // 返回 pair<迭代器, 迭代器>
    auto [min_it, max_it] = minmax
```

### tuple

```
FUNCTION demo_tuple:
    t = MAKE_TUPLE("Charlie", 28, 1.75, true)
    PRINT GET<0>(t)                             // Charlie（按索引）
    PRINT GET<2>(t)                             // 1.75

    auto [n, a, h, active] = t                  // 结构化绑定

    // 按类型取（只有无重复类型时可用）
    PRINT GET<STRING>(t)                        // Charlie
```

### tie —— 解包到已有变量

```
FUNCTION demo_tie:
    s = STRING();  i = 0;  d = 0.0
    TIE(s, i, d) = MAKE_TUPLE("hello", 42, 3.14)
    PRINT s, i, d                               // hello 42 3.14

    // IGNORE 占位符忽略某些值
    TIE(s, IGNORE, d) = MAKE_TUPLE("world", 99, 2.71)
    // 99 被忽略

    // 用于比较（tuple 比较是字典序）
    IF MAKE_TUPLE(a1, a2) < MAKE_TUPLE(b1, b2) THEN
        PRINT "先比 first，再比 second"
    END IF
```

### 高级技巧

```
FUNCTION demo_advanced:
    // 拼接 tuple
    t1 = MAKE_TUPLE(1, 2)
    t2 = MAKE_TUPLE(STRING("a"), 3.14)
    merged = TUPLE_CAT(t1, t2)                  // (1, 2, "a", 3.14)

    // forward_as_tuple: 完美转发打包
    params = FORWARD_AS_TUPLE(arg1, arg2)       // 原地构造时用

    // pair 的投影排序
    items = VECTOR<PAIR<STRING, INT>>()
    SORT(items, LAMBDA(a, b):
        RETURN a.SECOND < b.SECOND              // 按 value 排序
    )
```

---

- **optional / variant**: [[./optional_variant|optional / variant / any]] — 其他值语义工具
- **span / bitset**: [[./span_bitset|span / bitset]] — 视图与位集
- **结构化绑定**: 适用于 `pair`/`tuple`/`struct`/`array`
- **C 对照**: `struct { T1 first; T2 second; }` 手动定义
- **返回目录**: 
