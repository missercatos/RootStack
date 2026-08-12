---
title: "C++ 功能库 — span / bitset / byte"
---

## 概述

这三个轻量工具解决 C 遗留的痛点：`span` 将指针+长度封装为安全的数组视图（替代 `T* + size_t` 对），`bitset` 提供固定长度的位集合操作（替代 `int` + 位运算），`byte` 定义字节类型（替代 `char`/`unsigned char`，明确语义）。

## 核心组件

### span

| 组件 | 说明 |
|------|------|
| `span<T>` | 连续数据非拥有视图（指针+长度），可接收 vector/array/C数组 |
| `span<T, N>` | 固定大小 span，编译期已知长度 |
| `s.SIZE()` / `s.SIZE_BYTES()` | 元素个数 / 字节数 |
| `s.SUBSPAN(offset, count)` | 子视图，不拷贝数据 |
| `s.FIRST(n)` / `s.LAST(n)` | 前/后 n 个元素 |
| `s.DATA()` | 返回底层指针 |

### bitset

| 组件 | 说明 |
|------|------|
| `bitset<N>` | N 位固定长度位集 |
| `set(pos)` / `reset(pos)` | 置位 / 清零 |
| `flip(pos)` | 翻转指定位 |
| `test(pos)` | 检查某位是否为 1 |
| `count()` | 位 1 的数量 |
| `all()` / `any()` / `none()` | 全 1 / 有 1 / 全 0 |
| `to_ulong()` / `to_ullong()` | 转为整数 |
| `to_string()` | 转为 "0101..." 字符串 |
| `&` `|` `^` `~` | 位运算 |

### byte (C++17)

| 操作 | 说明 |
|------|------|
| `byte{0xFF}` | 创建字节值 |
| `<<` / `>>` | 移位 |
| `&` `|` `^` `~` | 位运算 |
| `TO_INTEGER<INT>(b)` | 转为整数 |

## 典型用法

### span —— 通用数组视图

```
FUNCTION demo_span:
 arr = INT[]{1, 2, 3, 4, 5, 6, 7, 8}

 s = SPAN<INT>(arr, 8)
 PRINT s.SIZE() // 8
 PRINT s[0] // 1

 sub = s.SUBSPAN(2, 4) // [3, 4, 5, 6]（不拷贝）
 last3 = s.LAST(3) // [6, 7, 8]

 // 统一接口：接收 vector, array, C数组
 PROCESS = LAMBDA(s SPAN<CONST INT>):
 FOR x IN s: PRINT x
 END LAMBDA

 v = VECTOR<INT>{1, 2, 3}
 PROCESS(SPAN<INT>(v)) // vector → span
 PROCESS(SPAN<INT>(arr, 3)) // C数组 → span
```

### bitset —— 位集操作

```
FUNCTION demo_bitset:
 flags = BITSET<10>()
 flags.SET(0) // 0000000001
 flags.SET(3, true) // 0000001001
 flags.FLIP(1) // 0000001011

 PRINT flags.TEST(3) // true
 PRINT flags.COUNT() // 2
 PRINT flags.ANY() // true

 a = BITSET<4>("1010")
 b = BITSET<4>("0110")
 PRINT a & b // 0010
 PRINT a | b // 1110

 n = flags.TO_ULONG() // 转为 unsigned long
 PRINT flags.TO_STRING() // "0000001011"
```

### 标志位模式

```
FUNCTION demo_flags:
 FLAGS = ENUM:
 READ = 0
 WRITE = 1
 EXECUTE = 2
 END ENUM

 perms = BITSET<8>()
 perms.SET(FLAGS::READ)
 perms.SET(FLAGS::WRITE)

 IF perms.TEST(FLAGS::READ): PRINT "可读"
 IF perms.TEST(FLAGS::EXECUTE): PRINT "可执行"
```

### byte —— 字节操作

```
FUNCTION demo_byte:
 b1 = BYTE{0xA0}
 b2 = BYTE{0x0B}
 result = b1 | b2 // 0xAB

 shifted = b1 << 4 // 0x00（高位移出）

 val = TO_INTEGER<INT>(b1) // 转为 int
```

---

- **pair / tuple**: [[pair_tuple|pair / tuple]] — 多值聚合
- **optional / variant**: [[optional_variant|optional / variant / any / expected]] — 可选值与变体
- **string_view**: span 与 `string_view` 理念相同（非拥有视图）
- **容器**: span 可以指向任何连续容器（vector, array, C数组）
- **C 对照**: `T* + size_t` 对 / `int flag` + 位运算 / `unsigned char` 替代
- **返回目录**: 
