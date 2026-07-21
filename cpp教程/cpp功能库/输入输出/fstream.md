---
title: "C++ 功能库 — fstream"
---

## 概述

文件流提供与 `cin`/`cout` 相同接口的文件读写——`ifstream` 读文件、`ofstream` 写文件、`fstream` 可读写。打开模式可通过标志位组合控制：追加、截断、二进制等。

文件流在构造时可以指定路径，析构时自动关闭文件（RAII）。

## 核心组件

| 组件 | 说明 |
|------|------|
| `ifstream` | 文件输入流（只读） |
| `ofstream` | 文件输出流（只写） |
| `fstream` | 文件输入输出流（读写） |
| `open(path)` | 打开文件 |
| `close()` | 关闭文件 |
| `is_open()` | 检查是否已打开 |

## 打开模式标志

| 标志 | 说明 |
|------|------|
| `in` | 读模式（`ifstream` 默认） |
| `out` | 写模式（`ofstream` 默认） |
| `app` | 追加模式（写入前定位到文件尾） |
| `trunc` | 截断模式（打开时清空原有内容） |
| `ate` | 打开后定位到文件尾 |
| `binary` | 二进制模式（不转换换行符） |

## 典型用法

### 写入文件

```
FUNCTION demo_write:
    fout = OFSTREAM("data.txt")
    IF NOT fout.IS_OPEN() THEN
        ERROR << "无法打开文件" << ENDL
        RETURN
    END IF

    fout << "第一行" << ENDL
    fout << 42 << " " << 3.14 << ENDL
    fout.CLOSE()
```

### 读取文件

```
FUNCTION demo_read:
    fin = IFSTREAM("data.txt")
    line = STRING()
    WHILE GETLINE(fin, line):
        PRINT line
    END WHILE
    fin.CLOSE()
```

### 追加与二进制

```
FUNCTION demo_append_binary:
    fout = OFSTREAM("log.txt", APP)         // 追加模式
    fout << "新日志条目" << ENDL

    fbin = OFSTREAM("data.bin", BINARY)     // 二进制写入
    x = 0x12345678
    fbin.WRITE(&x, SIZEOF(x))               // 写入原始字节
```

---

- **控制台 IO**: [[iostream|iostream]] — `cin`/`cout`
- **字符串流**: [[sstream|sstream]] — 内存格式化
- **文件系统**: [[filesystem|filesystem]] — 目录遍历、路径操作
- **C 对照**: `fopen`/`fclose`/`fprintf`/`fscanf`（`<stdio.h>`）
- **返回目录**: 
