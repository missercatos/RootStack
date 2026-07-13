---
C++ 功能库 — iostream
---

## 概述

C++ 的标准输入输出基于**流(stream)抽象**——`cin`/`cout` 提供类型安全的控制台 IO，通过 `<<` 和 `>>` 运算符自动匹配类型。配合操纵符(manipulator)可以控制格式：精度、宽度、进制等。

相比 C 的 `printf`/`scanf`，流是类型安全的——编译器自动推导类型，消除了格式串与参数不匹配的风险。

## 核心组件

| 组件 | 说明 |
|------|------|
| `cin` | 标准输入流，默认连键盘 |
| `cout` | 标准输出流，默认连屏幕（有缓冲） |
| `cerr` | 标准错误流（无缓冲，立即输出） |
| `clog` | 标准错误流（有缓冲） |
| `getline(cin, s)` | 读取一行（含空格）到 `s` |
| `endl` | 换行 + 刷新缓冲区（`'\n'` 只换行不刷新） |

## 格式操纵符

| 操纵符 | 说明 |
|--------|------|
| `HEX` / `OCT` / `DEC` | 设置整数进制 |
| `FIXED` / `SCIENTIFIC` | 浮点格式：定点 / 科学计数 |
| `SETPRECISION(n)` | 浮点精度位数 |
| `SETW(n)` | 输出宽度 |
| `SETFILL(c)` | 填充字符 |
| `LEFT` / `RIGHT` | 左对齐 / 右对齐 |
| `BOOLALPHA` | `true`/`false` 文字输出 |

## 典型用法

```
FUNCTION demo_io:
    x = 0
    INPUT >> x                              // 类型自动匹配

    OUTPUT << "值: " << x << ENDL           // 链式输出

    line = STRING()
    GETLINE(INPUT, line)                    // 读取整行（含空格）

    ERROR << "错误信息" << ENDL              // 无缓冲，立即输出
```

### 格式控制

```
FUNCTION demo_format:
    OUTPUT << HEX << 255                    // "ff"
    OUTPUT << OCT << 8                      // "10"

    OUTPUT << FIXED << SETPRECISION(3)
    OUTPUT << 3.14159                       // "3.142"

    OUTPUT << SETW(8) << SETFILL('0') << 42 // "00000042"
    OUTPUT << LEFT << SETW(10) << "name"    // "name      "
```

### 流状态

```
FUNCTION demo_state:
    x = 0
    IF INPUT >> x THEN                      // 成功返回 cin（可转 bool）
        PRINT "读到:", x
    ELSE
        INPUT.CLEAR()                       // 清除错误标志
        INPUT.IGNORE(1000, '\n')            // 丢弃缓冲区中错误内容
        PRINT "输入无效"
    END IF
```

---

- **文件流**: [[./fstream|fstream]] — 文件 IO
- **字符串流**: [[./sstream|sstream]] — 内存中的格式化
- **文件系统**: [[./filesystem|filesystem]] — 目录与文件操作
- **C 对照**: `printf`/`scanf`/`getchar`（`<stdio.h>`）
- **返回目录**: [[../索引|C++ 功能库索引]]
