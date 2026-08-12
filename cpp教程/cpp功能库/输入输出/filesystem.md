---
title: "C++ 功能库 — filesystem"
---

## 概述

`filesystem` (C++17) 提供跨平台的文件和目录操作，解决 C 语言中依赖操作系统 API 的痛点。核心是 `path` 类（路径抽象，支持 `/` 拼接）和目录遍历器 `directory_iterator`。支持文件存在性检查、创建/删除、拷贝、重命名等操作。

全平台统一 API，不依赖 POSIX `<unistd.h>` 或 Windows API。

## 核心组件

| 组件 | 说明 |
|------|------|
| `path` | 路径对象，支持 `/` 和 `/=` 拼接 |
| `exists(p)` | 路径是否存在 |
| `is_directory(p)` / `is_regular_file(p)` | 类型判断 |
| `create_directory(p)` | 创建目录 |
| `create_directories(p)` | 递归创建目录（类似 `mkdir -p`） |
| `copy(from, to)` | 拷贝文件/目录 |
| `copy_file(from, to)` | 仅拷贝文件 |
| `remove(p)` | 删除文件或空目录 |
| `remove_all(p)` | 递归删除（类似 `rm -rf`） |
| `rename(from, to)` | 重命名/移动 |
| `file_size(p)` | 文件大小（字节） |
| `current_path()` | 获取/设置当前工作目录 |
| `directory_iterator` | 目录遍历器（非递归） |
| `recursive_directory_iterator` | 递归目录遍历器 |

## 典型用法

### 路径操作

```
FUNCTION demo_path:
 p = PATH("/home/user/docs")
 full = p / "subdir" / "file.txt" // 拼接

 PRINT full.FILENAME() // "file.txt"
 PRINT full.STEM() // "file"（无后缀）
 PRINT full.EXTENSION() // ".txt"
 PRINT full.PARENT_PATH() // "/home/user/docs/subdir"

 IF EXISTS(full) THEN
 PRINT "文件存在, 大小=", FILE_SIZE(full)
 END IF
```

### 目录遍历

```
FUNCTION demo_iterate:
 p = PATH("/home/user/project")

 FOR entry IN DIRECTORY_ITERATOR(p):
 path = entry.PATH()
 IF entry.IS_DIRECTORY() THEN
 PRINT "[DIR] ", path.FILENAME()
 ELSE
 PRINT " ", path.FILENAME(), " (", entry.FILE_SIZE(), "b)"
 END IF
 END FOR
```

### 文件操作

```
FUNCTION demo_ops:
 // 创建目录（含父目录）
 CREATE_DIRECTORIES("/tmp/a/b/c")

 // 拷贝
 COPY("/tmp/src.txt", "/tmp/dst.txt")

 // 移动/重命名
 RENAME("/tmp/old.txt", "/tmp/new.txt")

 // 删除文件
 REMOVE("/tmp/new.txt")

 // 递归删除目录
 REMOVE_ALL("/tmp/a")
```

---

- **文件流**: [[fstream|fstream]] — 文件内容读写
- **控制台 IO**: [[iostream|iostream]] — 标准 IO
- **C 对照**: `stat`/`opendir`/`readdir`（POSIX `<sys/stat.h>` `<dirent.h>`）
- **返回目录**: 
