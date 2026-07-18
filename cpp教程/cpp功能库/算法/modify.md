---
C++ 功能库 — 序列修改
---

## 概述

C++ 标准库提供丰富的序列修改算法：复制、移动、替换、去重、反转等。关键设计原则是**输出通过迭代器指定**——算法不分配内存，目标范围必须预先分配好足够空间（或用 `back_inserter` 等插入迭代器自动扩容）。

`remove` 系列遵循 erase-remove idiom：`remove` 并不真正删除元素，只是将不删除的元素移到前面，返回新逻辑末尾，需要配合容器的 `erase` 真正删除。

## 核心组件

### 复制与移动

| 组件 | 说明 |
|------|------|
| `copy` | 复制源范围到目标 |
| `copy_if` | 只复制满足条件的元素 |
| `copy_n` | 复制前 n 个元素 |
| `copy_backward` | 从后往前复制（处理重叠） |
| `move` | 移动源范围到目标 |
| `move_backward` | 从后往前移动 |

### 变换

| 组件 | 说明 |
|------|------|
| `transform` | 对每个元素应用函数，写入目标 |
| `replace` / `replace_if` | 原地替换匹配的元素 |
| `replace_copy` / `replace_copy_if` | 替换并复制到新位置 |

### 移除与去重

| 组件 | 说明 |
|------|------|
| `remove` / `remove_if` | 前移保留元素，返回新末尾（习惯用 erase-remove） |
| `unique` | 将连续重复移至末尾，返回新末尾（习惯先排序再用） |
| `unique_copy` | 去重后复制到新位置 |

### 排列

| 组件 | 说明 |
|------|------|
| `reverse` | 反转序列 |
| `rotate` | 旋转序列（将 middle..end 放到 begin 前） |
| `fill` | 填充指定值 |
| `generate` | 用生成器函数填充 |
| `swap_ranges` | 交换两个范围 |

## 典型用法

### 复制与变换

```
FUNCTION demo_copy_transform:
    src = [1, 2, 3, 4, 5]
    dst = ARRAY OF SIZE(src.SIZE())

    COPY(src, dst)                           // dst = [1, 2, 3, 4, 5]

    TRANSFORM(src, dst, LAMBDA(x):
        RETURN x * x                         // 平方
    )                                        // dst = [1, 4, 9, 16, 25]

    TRANSFORM(src, dst, LAMBDA(x):
        RETURN x * 10
    )
```

### erase-remove idiom

```
FUNCTION demo_remove:
    v = [1, 3, 2, 3, 5, 3]

    v.ERASE(REMOVE(v, 3), v.END())          // v = [1, 2, 5]

    v = [1, 2, 3, 4, 5, 6]
    v.ERASE(REMOVE_IF(v, LAMBDA(x):
        RETURN x % 2 == 0                    // 移除所有偶数
    ), v.END())                              // v = [1, 3, 5]
```

### 去重与反转

```
FUNCTION demo_unique_reverse:
    v = [3, 1, 2, 3, 2, 1]

    SORT(v)                                  // [1, 1, 2, 2, 3, 3]
    v.ERASE(UNIQUE(v), v.END())              // [1, 2, 3]

    REVERSE(v)                               // [3, 2, 1]

    ROTATE(v, v.BEGIN() + 1)                 // [2, 1, 3] 左旋
```

### 填充与生成

```
FUNCTION demo_fill:
    v = VECTOR<INT>(5)
    FILL(v, 42)                              // [42, 42, 42, 42, 42]

    counter = 0
    GENERATE(v, LAMBDA:
        RETURN counter++
    )                                        // [0, 1, 2, 3, 4]
```

---

- **查找**: [[find_count|find / count]] — 先查找再修改
- **排序**: [[sort_search|sort / search]] — `sort`+`unique` 组合去重
- **lambda**: [[../函数式/lambda|lambda]] — 变换/过滤谓词
- **返回目录**: 
