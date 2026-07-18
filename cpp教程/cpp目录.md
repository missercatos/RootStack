
# C++ 完整教程 (C++ Complete Tutorial)

> 本教程从零开始, 覆盖 C++ 从入门到精通的完整学习路径。包含基础教程(环境搭建+语法入门)、
> 深化教程(核心语言特性)、STL 容器、功能库和第三方库推荐。
>
> 每个章节配有底层原理剖析、实际案例, 以及可交互的选择题和判断题, 使用 Obsidian 可折叠答案格式, 点击即可查看解析。

---

## C++ 教程结构

```
cpp教程/
├── cpp目录.md            ← 你在这里
├── cpp基础教程/          环境搭建 + 语法入门 (11 章)
├── cpp深化教程/          核心语言特性 (16 章)
├── 容器库/               STL 容器详解
│   ├── 序列容器/         vector, deque, list, string
│   ├── 关联容器/         set, map (红黑树)
│   ├── 无序容器/         unordered_set, unordered_map (哈希)
│   ├── 适配器/           stack, queue, priority_queue
│   └── 其他/             pair, bitset
├── cpp功能库/            C++ 标准库非容器部分
└── cpp第三方库/          推荐第三方库索引
```

---

## 推荐学习路线

```
cpp基础教程(01→11) → cpp深化教程(01→15) → 容器类 → cpp功能库 → cpp第三方库
        |                     |                     |
        ▼                     ▼                     ▼
   环境搭建+语法           OOP+模板+并发            STL容器使用
```

**当你遇到底层问题时**: C++ 的很多机制(指针、内存、虚表)需要 C 语言功底才能深入理解。
建议在学习 `03_指针与引用` 和 `04_动态内存` 时, 同时参考 [[../c语言教程/c目录|C语言教程]] 中的指针与内存章节, 两者互补。

**当你需要算法知识时**: [[../数据结构/DSA学习路线|DSA学习路线]] 提供了语言无关的数据结构与算法学习路径。

---

## 第零部分 — cpp基础教程 (Getting Started)

> 面向零基础读者。从环境搭建到语法入门。

| # | 章节 | 核心内容 |
|---|------|---------|
| 01 | [[cpp基础教程/01_下载与安装]] | Windows/macOS/Linux 编译器下载安装 |
| 02 | [[cpp基础教程/02_环境配置]] | PATH 配置/编译选项/Makefile/CMake/GDB 调试 |
| 03 | [[cpp基础教程/03_编辑器与IDE推荐]] | VSCode/Visual Studio/CLion/Vim/在线编译器 |
| 04 | [[cpp基础教程/04_第一个程序与输入输出]] | Hello World/main 函数/cout/cin/格式化输出 |
| 05 | [[cpp基础教程/05_变量与数据类型]] | int/float/double/char/bool/const/auto/类型转换 |
| 06 | [[cpp基础教程/06_运算符与表达式]] | 算术/关系/逻辑/位运算/优先级/三目运算符 |
| 07 | [[cpp基础教程/07_条件语句]] | if/else/switch/短路求值/常见陷阱 |
| 08 | [[cpp基础教程/08_循环结构]] | for/while/do-while/break/continue/range-for |
| 09 | [[cpp基础教程/09_数组基础]] | 一维/二维数组/越界/函数参数/std::array |
| 10 | [[cpp基础教程/10_函数基础]] | 声明定义/值传递/引用传递/重载/递归/inline |
| 11 | [[cpp基础教程/11_字符串基础]] | C 风格字符串/string 类/查找替换/数字转换 |

**学习顺序**: 01-03(环境) → 04-08(语法) → 09-11(进阶基础)

---

## 第一部分 — cpp深化教程 (Core Language)

> 面向已掌握基础语法的读者, 深入讲解 C++ 核心机制、内存模型、OOP、模板、并发、网络编程和标准库。
> 覆盖 C++11/14/17/20 现代特性。

### 章节索引

| # | 章节 | 核心内容 |
|---|------|---------|
| 01 | [[cpp深化教程/01_命名空间]] | namespace/using/名称修饰原理 |
| 02 | [[cpp深化教程/02_预处理器]] | #include/#define/#ifdef/编译流程 |
| 03 | [[cpp深化教程/03_指针与引用]] | 指针/引用/智能指针/内存寻址/底层原理 |
| 04 | [[cpp深化教程/04_动态内存]] | new/delete/智能指针/堆与栈 |
| 04.5 | [[cpp深化教程/4.5_struct结构体]] | struct/C 兼容/POD/数据结构节点 |
| 05 | [[cpp深化教程/05_面向对象(一)类与对象基础]] | class/struct/构造/析构/拷贝/移动/this 底层 |
| 06 | [[cpp深化教程/06_面向对象(二)继承]] | 继承/vtable/多重继承/虚继承 |
| 07 | [[cpp深化教程/07_面向对象(三)多态与虚函数]] | virtual/override/抽象类/RTTI |
| 08 | [[cpp深化教程/08_面向对象(四)运算符重载]] | 运算符重载/类型转换/C++20 太空船 |
| 09 | [[cpp深化教程/09_函数模板]] | 模板/SFINAE/可变参数/concepts |
| 10 | [[cpp深化教程/10_异常处理]] | try/catch/throw/noexcept |
| 11 | [[cpp深化教程/11_文件与流]] | fstream/iostream/二进制读写 |
| 12 | [[cpp深化教程/12_信号处理]] | signal/sigaction/信号屏蔽字 |
| 13 | [[cpp深化教程/13_多线程]] | thread/mutex/atomic/future |
| 14 | [[cpp深化教程/14_Web编程]] | Socket/HTTP/WebSocket/RESTful |
| 15 | [[cpp深化教程/15_C++标准库]] | STL 六大组件/C++14/17/20 新特性 |

### 推荐阅读顺序

```
03_指针与引用 → 04_动态内存 → 01_命名空间 → 02_预处理器
  → 04.5_struct结构体 → 05_类与对象基础 → 06_继承 → 07_多态与虚函数
  → 08_运算符重载 → 09_函数模板 → 10_异常处理 → 11_文件与流
  → 12_信号处理 → 13_多线程 → 14_Web编程 → 15_C++标准库
```

> 注: 文件编号并非阅读顺序。以上路线按"底层认知递进"排列: 先理解"地址"和"内存", 再进入 OOP。

### C++ 与 C 的交叉引用

| CPP 章节 | 建议同步阅读的 C 内容 |
|----------|---------------------|
| `03_指针与引用` | [[../ISSUES|C指针深度剖析]] |
| `04_动态内存` | [[../ISSUES|C动态内存管理]] |
| `05_类与对象基础` | [[../ISSUES|C实现OOP]] |
| `13_多线程` | [[../ISSUES|C硬件操作]] |

---

## 第二部分 — STL 容器类

> 每个容器章节: 底层结构 → 用法大全 → 实际案例 → 练习 → 洛谷题目

| 章节 | 内容 |
|------|------|
| [[容器库/其他/pair]] | std::pair 键值对 |
| [[容器库/序列容器/vector|vector]] | 动态数组, 随机访问 O(1) |
| [[容器库/序列容器/string.md]] | std::string 字符序列 |
| [[容器库/适配器/stack]] | 栈适配器 LIFO |
| [[容器库/适配器/queue]] | 队列适配器 FIFO |
| [[容器库/序列容器/deque]] | 双端队列 |
| [[容器库/适配器/priority_queue]] | 优先队列(堆) |
| [[容器库/序列容器/list]] | 双向/单向链表 |
| [[容器库/关联容器/set]] | 有序集合(红黑树) |
| [[容器库/关联容器/map|map]] | 有序映射(红黑树) |
| [[容器库/无序容器/unordered_set]] | 无序集合(哈希) |
| [[容器库/无序容器/unordered_map]] | 无序映射(哈希) |
| [[容器库/其他/bitset]] | std::bitset 位集 |

---

## 库参考

| 类型 | 索引文件 | 说明 |
|------|---------|------|
| 容器库 | [[../ISSUES|容器库索引]] | 序列容器/关联容器/无序容器/适配器/其他 |
| 功能库 | [[../ISSUES|功能库索引]] | 字符串/IO/算法/数值/并发/内存/函数式/工具 |
| 第三方库 | [[../ISSUES|第三方库索引]] | 网络/GUI/游戏/数据库/序列化/测试/日志/加密/数学/并发/综合 |

---

## 第三部分 — cpp功能库 (标准库非容器部分)

> C++ 标准库不止容器。以下为核心功能库索引。

| 类别 | 内容 |
|------|------|
| 字符串处理 | std::string, std::string_view, std::regex |
| 输入输出 | iostream, fstream, stringstream, filesystem (C++17) |
| 算法 | sort, find, binary_search, next_permutation |
| 数值 | random, chrono, complex, ratio, numeric_limits |
| 并发 | thread, mutex, condition_variable, atomic, future |
| 内存 | unique_ptr, shared_ptr, weak_ptr, allocator |
| 函数式 | function, bind, lambda, reference_wrapper |

---

## 第四部分 — cpp第三方库推荐

| 领域 | 推荐库 | 说明 |
|------|--------|------|
| 网络 | Boost.Asio, libcurl, cpp-httplib | 异步网络, HTTP 客户端 |
| GUI | Qt, wxWidgets, imgui | 跨平台图形界面 |
| 游戏 | SDL2, SFML, raylib | 2D 游戏/多媒体 |
| 数据库 | sqlite3, SOCI, mysql-connector-cpp | 数据库连接 |
| 序列化 | protobuf, nlohmann/json, yaml-cpp | 数据格式 |
| 测试 | GoogleTest, Catch2, doctest | 单元测试框架 |
| 日志 | spdlog, glog | 高性能日志 |
| 加密 | OpenSSL, Crypto++ | 加密和 SSL |

---

## 配套资源

| 模块 | 入口 |
|------|------|
| 学习路径 | [[../ISSUES|C++主线学习路径]] |
| C 到 C++ | [[../ISSUES|C→C++ 向下兼容路径]] |
| 数据结构与算法 | [[../ISSUES|DSA学习路线]] |
| C 语言教程 | [[../ISSUES|C语言教程]] |
| 汇编基础 | [[../ISSUES|汇编基础]] |
| 内核思想 | [[../ISSUES|内核教程]] |
