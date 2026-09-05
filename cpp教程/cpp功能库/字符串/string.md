---
title: "C++ 功能库 — string"
---

## 概述

`string` 是 C++ 标准库的 RAII 动态字符串类，自动管理堆内存，构造时分配、析构时释放。配合 `string_view` 的零拷贝只读视图和 `to_string`/`stoi` 的数值转换，彻底消除了 C 风格 `char[]` 的缓冲区溢出和手动 `malloc`/`free` 问题。

短字符串优化(SSO)：通常 ≤15 字符时直接存储在对象内部，不触发堆分配。

## 核心组件

| 组件 | 头文件 | 说明 |
|------|--------|------|
| `string` | `<string>` | 动态字符串，`+` 拼接、`find()` 查找、`substr()` 截取 |
| `string_view` | `<string_view>` (C++17) | 只读字符视图，构造/传递零开销 |
| `to_string` | `<string>` | 数值转字符串 |
| `stoi` / `stod` | `<string>` | 字符串转 int / double |

## 关键操作

| 操作 | 说明 |
|------|------|
| `s.SIZE()` | 字符数 |
| `s.FIND(sub)` | 查找子串首次出现位置，失败返回 `NPOS` |
| `s.SUBSTR(pos, len)` | 从 pos 取 len 个字符 |
| `s.FIND_FIRST_OF(chars)` | 查找任一字符首次出现位置 |
| `s.COMPARE(other)` | 字典序比较 |
| `s.DATA()` | 返回底层 `const char*` |
| `s.STARTS_WITH(prefix)` | C++20，检查前缀 |

## 典型用法

```cpp
FUNCTION demo_string:
 s1 = STRING("hello")
 s2 = STRING(5, 'x') // "xxxxx"
 s3 = s1 + " world" // "hello world"

 FOR ch IN s3: // 范围 for 遍历
 PRINT ch
 END FOR

 pos = s3.FIND("world") // 6
 sub = s3.SUBSTR(0, 5) // "hello"

 sv = s3.SUBSTR_VIEW(6) // STRING_VIEW 不拷贝，"world"

 PRINT s3.SIZE() // 11
 PRINT s3[0] // 'h'
```cpp

### 数值转换

```cpp
FUNCTION demo_convert:
 num_str = TO_STRING(42) // "42"
 pi_str = TO_STRING(3.14159) // "3.141590"

 n = STRING_TO_INT("123") // 123
 d = STRING_TO_DOUBLE("3.14") // 3.14
 x = STRING_TO_INT("42abc") // 42，忽略尾部非数字
```cpp

---

- **C 对照**: `strlen`/`strcpy`/`strcmp`（`<string.h>`）
- **输入输出配合**: [[../输入输出/sstream|sstream]] — `stringstream` 格式化
- **容器视角**: string 同时是 `char` 的序列容器
- **字符串视图**: [[regex|regex]] — 正则匹配
- **返回目录**: 
