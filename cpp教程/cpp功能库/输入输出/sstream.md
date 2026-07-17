---
C++ 功能库 — sstream
---

## 概述

字符串流将内存中的字符串抽象为流，你可以像操作 `cout` 一样向字符串"写入"，也可以像 `cin` 一样从字符串"读取"。`ostringstream` 用于**格式化拼接**（比 `+` 拼接更高效），`istringstream` 用于**从字符串解析数据**（替代 `scanf`）。

`stringstream` 是两者的结合，支持双向读写。

## 核心组件

| 组件 | 说明 |
|------|------|
| `ostringstream` | 只写字符串流，`<<` 写入 |
| `istringstream` | 只读字符串流，`>>` 读取 |
| `stringstream` | 可读写字符串流 |
| `ss.STR()` | 获取/设置内部字符串内容 |
| `ss.STR("")` | 清空流内容 |

## 典型用法

### 格式化拼接

```
FUNCTION demo_format:
    ss = OSTRINGSTREAM()

    ss << "Name: " << "Alice"
    ss << ", Age: " << 25
    ss << ", Score: " << SETPRECISION(2) << FIXED << 87.5

    result = ss.STR()
    PRINT result          // "Name: Alice, Age: 25, Score: 87.50"
```

### 从字符串解析

```
FUNCTION demo_parse:
    input = ISTRINGSTREAM("3.14 42 hello world")

    pi = 0.0
    n = 0
    w1 = STRING()
    w2 = STRING()

    input >> pi >> n >> w1 >> w2
    PRINT pi, n, w1, w2        // 3.14  42  hello  world
```

### 逐行解析 CSV 风格数据

```
FUNCTION demo_csv:
    data = "Alice,25,Engineer\nBob,30,Designer\n"
    ss = STRINGSTREAM(data)
    line = STRING()

    WHILE GETLINE(ss, line):
        line_ss = STRINGSTREAM(line)
        name = STRING();  age = 0;  role = STRING()
        GETLINE(line_ss, name, ',')
        line_ss >> age
        GETLINE(line_ss, ROLE, ',')
        PRINT name, age, role
    END WHILE
```

### 类型转换工具模式

```
FUNCTION safe_convert:
    // 字符串 → int（带校验）
    s = "42abc"
    ss = ISTRINGSTREAM(s)
    n = 0
    IF ss >> n AND ss.EOF() THEN
        PRINT "完整转换:", n
    ELSE
        PRINT "转换失败或有多余字符"
    END IF
```

---

- **控制台 IO**: [[./iostream|iostream]] — `cin`/`cout`
- **文件流**: [[./fstream|fstream]] — 文件 IO
- **字符串基础**: [[../字符串/string|string]] — `string` 和 `string_view`
- **C 对照**: `sprintf`/`sscanf`（`<stdio.h>`）
- **返回目录**: 
