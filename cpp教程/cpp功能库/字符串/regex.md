---
title: "C++ 功能库 — regex"
---

## 概述

`regex` 提供 ECMAScript 风格的正则表达式引擎，支持模式匹配、搜索和替换。主要 API 包括 `regex_match`（全串匹配）、`regex_search`（子串搜索）和 `regex_replace`（全局替换），匹配结果存入 `smatch` 对象中按捕获组提取。

正则表达式在构造时编译为内部状态机，适合重复使用同一个 pattern。

## 核心组件

| 组件 | 说明 |
|------|------|
| `regex` | 正则表达式对象，构造时编译 pattern |
| `smatch` | 匹配结果集，存储每个捕获组的位置 |
| `regex_match` | 整个字符串是否完全匹配 |
| `regex_search` | 字符串中是否存在匹配的子串 |
| `regex_replace` | 替换所有匹配为指定字符串 |
| `regex_iterator` | 遍历所有匹配结果 |

## 关键标记

| 标记 | 说明 |
|------|------|
| `regex::icase` | 忽略大小写 |
| `regex::ECMAScript` | 默认语法，类 JavaScript |
| `regex::extended` | POSIX 扩展语法 |
| `regex::optimize` | 优化匹配速度（构造更慢） |

## 典型用法

```
FUNCTION demo_regex:
 pattern = REGEX("[0-9]+")

 IF REGEX_MATCH("12345", pattern) THEN
 PRINT "全是数字"
 END IF

 s = "abc123def456ghi"
 IF REGEX_SEARCH(s, pattern) THEN
 PRINT "找到数字"
 END IF

 result = REGEX_REPLACE(s, pattern, "#")
 PRINT result // "abc#def#ghi"
```

### 捕获组

```
FUNCTION demo_capture:
 email_pattern = REGEX(R"((\w+)@(\w+\.\w+))")
 s = "contact@example.com"
 match = SMATCH()

 IF REGEX_SEARCH(s, match, email_pattern) THEN
 PRINT match[0] // "contact@example.com" 完整匹配
 PRINT match[1] // "contact" 第一个捕获组
 PRINT match[2] // "example.com" 第二个捕获组
 END IF
```

### 遍历所有匹配

```
FUNCTION demo_iter:
 pattern = REGEX("[0-9]+")
 s = "a=10, b=20, c=30"

 it = REGEX_ITERATOR(s.BEGIN(), s.END(), pattern)
 END_IT = REGEX_ITERATOR()
 WHILE it != END_IT:
 PRINT it.STR()
 it++
 END WHILE // 依次输出: 10 20 30
```

---

- **字符串基础**: [[./string|string]] — `string` 和 `string_view`
- **字符串流**: [[../输入输出/sstream|sstream]] — `stringstream` 格式化解析
- **C 对照**: C 无标准正则库，需 POSIX `<regex.h>` 或第三方
- **返回目录**: 
