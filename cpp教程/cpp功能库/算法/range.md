---
title: "C++ 功能库 — C++20 Ranges"
---

## 概述

C++20 引入的 Ranges 库重构了算法的工作方式——用**范围(ranges)**替代迭代器对，用**管道运算符 `|`**组合多个操作。`RANGES::sort(v)` 代替 `sort(v.BEGIN(), v.END())`，`v | FILTER(f) | TRANSFORM(g) | TAKE(n)` 形成声明式数据处理流水线。

范围适配器(views)是惰性求值的——在遍历发生前不执行任何计算，多个适配器链式组合后零中间容器。

## 核心概念：View（视图）

View 是对范围的轻量包装，不拥有数据，只改变访问方式。所有 View 都是 O(1) 拷贝/移动。

```
数据源 View 管道 消费
─── ──────── ──
vector<int> ──│→ filter → transform → take → │── for_each
 │ (惰性) (惰性) (惰性) │ (实际执行)
```

## 核心组件

### 范围适配器（Views）

| 适配器 | 说明 |
|--------|------|
| `FILTER(pred)` | 保留满足谓词的元素 |
| `TRANSFORM(f)` | 对每个元素应用函数 |
| `TAKE(n)` | 取前 n 个元素 |
| `TAKE_WHILE(pred)` | 取元素直到谓词失败 |
| `DROP(n)` | 跳过前 n 个元素 |
| `DROP_WHILE(pred)` | 跳过元素直到谓词失败 |
| `REVERSE` | 反转视图 |
| `JOIN` | 展平嵌套范围 |
| `SPLIT` | 按分隔符拆分 |
| `COMMON` | 转为 common_range |
| `KEYS` / `VALUES` | 提取 pair/tuple 的 key/value |

### 范围版本的算法

| 算法 | 说明 |
|------|------|
| `RANGES::sort` | 直接传范围而非迭代器对 |
| `RANGES::find` | 返回迭代器 |
| `RANGES::for_each` | 遍历并执行 |
| `RANGES::copy` | 复制到输出迭代器 |
| `RANGES::any_of` / `all_of` | 谓词判断 |

## 典型用法

### 管道式组合

```
FUNCTION demo_pipeline:
 v = [5, 1, 8, 2, 9, 3, 7, 4, 6]

 result = v
 | FILTER(LAMBDA(x): RETURN x % 2 == 1) // 奇数: [5,1,9,3,7]
 | TRANSFORM(LAMBDA(x): RETURN x * x) // 平方: [25,1,81,9,49]
 | TAKE(3) // 前3: [25,1,81]
```

### 范围排序

```
FUNCTION demo_range_sort:
 v = [5, 3, 1, 4, 2]

 RANGES::SORT(v) // 直接传容器
 RANGES::SORT(v, GREATER()) // 降序

 // 投影: 排序前先对每个元素应用函数
 RANGES::SORT(people, COMPARE, &Person::age) // 按 age 字段排序
```

### 生成序列

```
FUNCTION demo_views:
 // iota: 生成数值序列
 FOR i IN VIEWS::IOTA(1, 10): // 1..9
 PRINT i
 END FOR

 // iota 与管道组合
 even_squares = VIEWS::IOTA(1)
 | TRANSFORM(LAMBDA(x): RETURN x * x)
 | FILTER(LAMBDA(x): RETURN x % 2 == 0)
 | TAKE(5) // 4, 16, 36, 64, 100
```

### take_while / drop_while

```
FUNCTION demo_take_drop:
 v = [1, 2, 3, 4, 0, 5, 6]

 head = v | TAKE_WHILE(LAMBDA(x):
 RETURN x != 0 // [1, 2, 3, 4]
 )

 tail = v | DROP_WHILE(LAMBDA(x):
 RETURN x != 0 // [0, 5, 6]
 )
```

---

- **传统算法**: [[sort_search|sort / search]] — 基于迭代器的排序/搜索
- **查找统计**: [[find_count|find / count]] — 传统 `find`/`count` vs `FILTER`
- **修改算法**: [[modify|modify]] — 传统修改 vs `TRANSFORM`
- **函数式**: [[../函数式/lambda|lambda]] — lambda 作为适配器谓词
- **返回目录**: 
