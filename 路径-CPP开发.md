## 路径 -- C++ 开发

> 本路径面向应用开发、后端服务、数据库、Web 与网络编程、跨平台开发等上层工程方向。以 C++ 为核心语言，从现代 C++ 特性入手，逐步覆盖数据结构工程实践、网络编程、数据库和前后端技术栈。
>
> 更注重 **工程效率和系统设计**——知道如何选择合适的抽象、如何组织大型项目、如何让软件可靠地运行在生产环境。

---

### 目标受众

| 维度 | 描述 |
|------|------|
| 目标 | 后端开发工程师、全栈应用开发者、数据库开发、桌面/移动应用开发 |
| 前置 | 任意语言编程基础 (C++ 零基础可入门) |
| 适用人群 | 想从语言学习进阶到实际项目开发的工程师，需要系统补全网络/数据库/系统工程能力的开发者 |
| 建议周期 | 4-6 个月 |

---

### Phase 1: C++ 基础 (建议 2 周)

- [[cpp教程/cpp基础教程/01_下载与安装|01 下载与安装]]
- [[cpp教程/cpp基础教程/02_环境配置|02 环境配置]]
- [[cpp教程/cpp基础教程/03_编辑器与IDE推荐|03 编辑器与IDE推荐]]
- [[cpp教程/cpp基础教程/04_第一个程序与输入输出|04 第一个程序与输入输出]]
- [[cpp教程/cpp基础教程/05_变量与数据类型|05 变量与数据类型]]
- [[cpp教程/cpp基础教程/06_运算符与表达式|06 运算符与表达式]]
- [[cpp教程/cpp基础教程/07_条件语句|07 条件语句]]
- [[cpp教程/cpp基础教程/08_循环结构|08 循环结构]]
- [[cpp教程/cpp基础教程/09_数组基础|09 数组基础]]
- [[cpp教程/cpp基础教程/10_函数基础|10 函数基础]]
- [[cpp教程/cpp基础教程/11_字符串基础|11 字符串基础]]

---

### Phase 2: C++ 深化 (建议 4 周)

> 推荐阅读顺序 (非文件编号顺序，按底层认知递进排列):
> 先理解"地址"和"内存"，再进入 OOP。

1. [[cpp教程/cpp深化教程/03_指针与引用|03 指针与引用]]
2. [[cpp教程/cpp深化教程/04_动态内存|04 动态内存]]
3. [[cpp教程/cpp深化教程/01_命名空间|01 命名空间]]
4. [[cpp教程/cpp深化教程/02_预处理器|02 预处理器]]
5. [[cpp教程/cpp深化教程/4.5_struct结构体|4.5 struct 结构体]]
6. [[cpp教程/cpp深化教程/05_面向对象(一)类与对象基础|05 类与对象基础]]
7. [[cpp教程/cpp深化教程/06_面向对象(二)继承|06 继承]]
8. [[cpp教程/cpp深化教程/07_面向对象(三)多态与虚函数|07 多态与虚函数]]
9. [[cpp教程/cpp深化教程/08_面向对象(四)运算符重载|08 运算符重载]]
10. [[cpp教程/cpp深化教程/09_函数模板|09 函数模板]]
11. [[cpp教程/cpp深化教程/10_异常处理|10 异常处理]]
12. [[cpp教程/cpp深化教程/11_文件与流|11 文件与流]]
13. [[cpp教程/cpp深化教程/12_信号处理|12 信号处理]]
14. [[cpp教程/cpp深化教程/13_多线程|13 多线程]]
15. [[cpp教程/cpp深化教程/14_Web编程|14 Web编程]]
16. [[cpp教程/cpp深化教程/15_C++标准库|15 C++标准库]]

---

### Phase 3: STL 容器库 (建议 2 周)

**基础：**
- [[cpp教程/容器库/其他/pair|std::pair]]

**序列容器：**
- [[cpp教程/容器库/序列容器/vector|std::vector]]
- [[cpp教程/容器库/序列容器/string|std::string]]
- [[cpp教程/容器库/序列容器/deque|std::deque]]
- [[cpp教程/容器库/序列容器/list|std::list]]
- [[cpp教程/容器库/序列容器/array|std::array]]

**适配器：**
- [[cpp教程/容器库/适配器/stack|std::stack]]
- [[cpp教程/容器库/适配器/queue|std::queue]]
- [[cpp教程/容器库/适配器/priority_queue|std::priority_queue]]

**关联容器：**
- [[cpp教程/容器库/关联容器/set|std::set]]
- [[cpp教程/容器库/关联容器/map|std::map]]

**无序容器：**
- [[cpp教程/容器库/无序容器/unordered_set|std::unordered_set]]
- [[cpp教程/容器库/无序容器/unordered_map|std::unordered_map]]

**其他：**
- [[cpp教程/容器库/其他/bitset|std::bitset]]

---

### Phase 4: STL 功能库 (建议 1 周)

**字符串：**
- [[cpp教程/cpp功能库/字符串/string|std::string]]
- [[cpp教程/cpp功能库/字符串/regex|std::regex]]

**输入输出：**
- [[cpp教程/cpp功能库/输入输出/iostream|iostream]]
- [[cpp教程/cpp功能库/输入输出/fstream|fstream]]
- [[cpp教程/cpp功能库/输入输出/sstream|stringstream]]
- [[cpp教程/cpp功能库/输入输出/filesystem|filesystem]]

**算法：**
- [[cpp教程/cpp功能库/算法/sort_search|sort / search]]
- [[cpp教程/cpp功能库/算法/find_count|find / count]]
- [[cpp教程/cpp功能库/算法/modify|modify]]
- [[cpp教程/cpp功能库/算法/range|range]]

**数值：**
- [[cpp教程/cpp功能库/数值/chrono|chrono]]
- [[cpp教程/cpp功能库/数值/random|random]]
- [[cpp教程/cpp功能库/数值/numeric|numeric]]

**并发：**
- [[cpp教程/cpp功能库/并发/thread|thread]]
- [[cpp教程/cpp功能库/并发/mutex|mutex]]
- [[cpp教程/cpp功能库/并发/atomic|atomic]]
- [[cpp教程/cpp功能库/并发/future|future]]

**内存：**
- [[cpp教程/cpp功能库/内存/smart_ptr|smart_ptr]]
- [[cpp教程/cpp功能库/内存/allocator|allocator]]

**函数式：**
- [[cpp教程/cpp功能库/函数式/lambda|lambda]]
- [[cpp教程/cpp功能库/函数式/function|function]]
- [[cpp教程/cpp功能库/函数式/hash|hash]]

**工具：**
- [[cpp教程/cpp功能库/工具/pair_tuple|pair / tuple]]
- [[cpp教程/cpp功能库/工具/optional_variant|optional / variant]]
- [[cpp教程/cpp功能库/工具/span_bitset|span / bitset]]

---

### Phase 5: 数据结构 + 算法 (建议 4 周)

按 [[数据结构/DSA学习路线|DSA 学习路线]] 推进：

**线形结构与排序:**
- [[数据结构/D_容器_Container|A 容器 Container]]
- [[数据结构/E_链表_LinkedList|D 链表 LinkedList]]
- [[数据结构/F_栈_Stack|B 栈 Stack]]
- [[数据结构/G_队列_Queue|F 队列 Queue]]
- [[数据结构/H_排序_八大排序_Sorting|Q 八大排序 Sorting]]

**核心数据结构:**
- [[数据结构/N_哈希表_HashTable|G 哈希表 HashTable]]
- [[数据结构/I_堆_Heap|C 堆 Heap]]
- [[数据结构/J_树_Tree_BST_AVL|I 树 / BST / AVL]]
- [[数据结构/L_字典树_Trie|J 字典树 Trie]]

**图论:**
- [[数据结构/S_图_Graph|H 图 Graph]]
- [[数据结构/O_并查集_UnionFind|K 并查集 UnionFind]]
- [[数据结构/T_图的高级算法_AdvancedGraph|P 图高级算法]]

**算法技巧核心:**
- [[算法/算法技巧/二分查找|二分查找]]
- [[算法/算法技巧/二分答案|二分答案]]
- [[算法/算法技巧/前缀和|前缀和]] + [[算法/算法技巧/差分|差分]]
- [[算法/算法技巧/贪心|贪心]]
- [[算法/算法技巧/滑动窗口|滑动窗口]] + [[算法/算法技巧/双指针|双指针]]
- [[算法/算法技巧/递推递归|递推与递归]]
- [[算法/算法技巧/搜索|搜索 DFS/BFS]]
- [[算法/算法技巧/动态规划|动态规划]]

**选学进阶:**
- [[数据结构/Q_线段树_SegmentTree|L 线段树]]
- [[数据结构/R_树状数组_BIT|M 树状数组 BIT]]
- [[数据结构/K_红黑树_RedBlackTree|E 红黑树]]
- [[数据结构/M_B树_BTree|O B树]]
- [[数据结构/P_跳表_SkipList|N 跳表]]

---

### Phase 6: 第三方库实战 (选学)

| 领域 | 入口 |
|------|------|
| 网络 | [[cpp教程/cpp第三方库/网络/Boost.Asio|Boost.Asio]] / [[cpp教程/cpp第三方库/网络/libcurl|libcurl]] / [[cpp教程/cpp第三方库/网络/cpp-httplib|cpp-httplib]] / [[cpp教程/cpp第三方库/网络/gRPC|gRPC]] |
| GUI | [[cpp教程/cpp第三方库/GUI/Qt|Qt]] / [[cpp教程/cpp第三方库/GUI/wxWidgets|wxWidgets]] / [[cpp教程/cpp第三方库/GUI/DearImGui|Dear ImGui]] |
| 游戏 | [[cpp教程/cpp第三方库/游戏/SDL2|SDL2]] / [[cpp教程/cpp第三方库/游戏/SFML|SFML]] / [[cpp教程/cpp第三方库/游戏/raylib|raylib]] |
| 数据库 | [[cpp教程/cpp第三方库/数据库/SQLite|SQLite]] / [[cpp教程/cpp第三方库/数据库/SOCI|SOCI]] / [[cpp教程/cpp第三方库/数据库/MongoDB|MongoDB]] |
| 序列化 | [[cpp教程/cpp第三方库/序列化/Protobuf|Protobuf]] / [[cpp教程/cpp第三方库/序列化/nlohmann-json|nlohmann/json]] / [[cpp教程/cpp第三方库/序列化/yaml-cpp|yaml-cpp]] / [[cpp教程/cpp第三方库/序列化/simdjson|simdjson]] |
| 测试 | [[cpp教程/cpp第三方库/测试/GoogleTest|GoogleTest]] / [[cpp教程/cpp第三方库/测试/Catch2|Catch2]] / [[cpp教程/cpp第三方库/测试/doctest|doctest]] |
| 日志 | [[cpp教程/cpp第三方库/日志/spdlog|spdlog]] / [[cpp教程/cpp第三方库/日志/glog|glog]] |
| 加密 | [[cpp教程/cpp第三方库/加密/OpenSSL|OpenSSL]] / [[cpp教程/cpp第三方库/加密/Crypto++|Crypto++]] / [[cpp教程/cpp第三方库/加密/Botan|Botan]] |
| 数学 | [[cpp教程/cpp第三方库/数学/Eigen|Eigen]] / [[cpp教程/cpp第三方库/数学/OpenCV|OpenCV]] / [[cpp教程/cpp第三方库/数学/CGAL|CGAL]] |
| 并发 | [[cpp教程/cpp第三方库/并发/TBB|Intel TBB]] / [[cpp教程/cpp第三方库/并发/taskflow|Taskflow]] / [[cpp教程/cpp第三方库/并发/OpenMP|OpenMP]] |
| 综合 | [[cpp教程/cpp第三方库/综合/Boost|Boost]] / [[cpp教程/cpp第三方库/综合/Abseil|Abseil]] / [[cpp教程/cpp第三方库/综合/fmt|fmt]] / [[cpp教程/cpp第三方库/综合/Folly|Folly]] |

---

### 推荐阅读物

- The C++ Programming Language (Bjarne Stroustrup)
- Effective Modern C++ (Scott Meyers)
- C++ Concurrency in Action (Anthony Williams)
- A Tour of C++ (Bjarne Stroustrup)
- C++ Templates: The Complete Guide

### 语言官方文档

- cppreference: https://en.cppreference.com/
- ISO C++ Standard: https://isocpp.org/
- C++ Core Guidelines: https://isocpp.github.io/CppCoreGuidelines/
- Compiler Explorer (Godbolt): https://godbolt.org/

---

### 相关模块

- [[多语言工程化/多语言工程化目录|多语言工程化]] — C++ 作为高性能核心与其他语言协作（FFI/gRPC/容器化）
- [[cpp教程/cpp深化教程/17_包管理器Conan与vcpkg|Conan 与 vcpkg]] — C++ 依赖管理与私有仓库基础
