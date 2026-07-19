## 路径 F — Rust 学习路径 (C++ 之后的系统编程进阶)

> 本教程体系可当作类百科全书使用，内容完善但体量庞大。若作为教程从头通读，效率不高。
> 建议按照本路线中的推荐阅读顺序，结合索引文件进行选择性学习。
> 同时推荐与 AI 进行问答互动学习——在自认为掌握语法或数据结构之后，去 [洛谷](https://www.luogu.com.cn/problem/list?tag=303) 刷题验证。
> 如遇到错误，不建议死磕，可用 AI 辅助纠正思路。

> 前置条件：已完成路径 B (C++ 主线) 的至少 Phase 1-3，或已有 C++/C 的扎实基础（理解指针、堆栈、RAII、OOP）。

---

### Rust 的战略定位：为什么 C++ 程序员要学 Rust

C++ 和 Rust 共享零开销抽象的哲学，但走的是两条路：

| 维度 | C++ | Rust |
|------|-----|------|
| 内存安全 | 靠程序员自律 + 静态分析工具 | 编译期所有权/借用检查，数学证明级别 |
| 并发安全 | `std::thread` + `std::mutex`，数据竞争是 UB | `Send` + `Sync` trait，编译期拒绝数据竞争 |
| 依赖管理 | 无官方工具（vcpkg/conan 第三方） | Cargo 内置，依赖解析、构建、发布一体 |
| 模块系统 | `#include` 文本拼接 + 预处理 | `mod` / `use` / `crate`，真正的模块系统 |
| 错误处理 | 异常 / 错误码 / `std::expected` | `Result<T, E>` / `?` 操作符，类型安全 |
| 学习曲线 | 浅入深出（写对容易，写优秀很难） | 深入浅出（前期陡峭，写对后很少出 bug） |

**2024-2025 年的趋势信号**：
1. 白宫 ONCD 发布《Back to the Building Blocks》报告，要求关键基础设施软件使用内存安全语言
2. Linux 6.1+ 内核正式支持 Rust，Android 将 Rust 列为新系统代码首选
3. 多家企业（Microsoft、Google、Amazon、Cloudflare）在生产中大规模使用 Rust 编写核心基础设施

Rust 不是要取代 C++，而是在**安全敏感、并发密集、基础设施**这三个维度提供更优的实现方案。掌握 C++ 后学 Rust，你将同时拥有两套最强大的系统编程思维。

---

### Phase 1: Rust 语法入门 (建议 2-3 周)

目标：用 Rust 写出能过洛谷基础题的程序。

| 顺序 | 文件 | 与 C++ 的对应概念 | 洛谷练习 |
|------|------|-------------------|----------|
| 1 | [[rust/1入门/01-认识Rust：你好世界|01 认识 Rust]] | rustup ≈ vcpkg/conan, cargo ≈ CMake | — |
| 2 | [[rust/1入门/02-第一个程序：从零开始|02 第一个程序]] | `fn main()` vs `int main()` | P1001 A+B |
| 3 | [[rust/1入门/03-变量与数据|03 变量与数据]] | `let` vs `auto`, `mut` vs `const` | P1425 |
| 4 | [[rust/1入门/04-做决策：条件与循环|04 条件与循环]] | `if` 是表达式不是语句 | P1085 |
| 5 | [[rust/1入门/05-盒子与标签：所有权入门|05 所有权]] | move 语义 = `unique_ptr` 转移, 无 GC | — |
| 6 | [[rust/1入门/06-借东西：引用与借用|06 引用与借用]] | `&T` = const 引用, `&mut T` = 独占可变引用 | — |
| 7 | [[rust/1入门/07-自定义类型：结构体|07 结构体]] | `impl` vs 类成员函数, 无继承 | P5740 |
| 8 | [[rust/1入门/08-多种选择：枚举与匹配|08 枚举]] | `enum` + `match` = `variant` + `visit` | — |
| 9 | [[rust/1入门/09-装东西的容器：集合|09 集合]] | `Vec` = `std::vector`, `HashMap` = `std::unordered_map` | P1996 |
| 10 | [[rust/1入门/10-出错了怎么办：错误处理|10 错误处理]] | `Result` ≈ `std::expected`, `?` ≈ try/throw | — |
| 11 | [[rust/1入门/11-万能模板：泛型|11 泛型]] | 泛型 + trait bound ≈ 模板 + concept | — |
| 12 | [[rust/1入门/12-共享行为：Trait入门|12 Trait]] | trait ≈ 纯虚基类 (接口), 无多重继承 | — |
| 13 | [[rust/1入门/13-引用有效期：生命周期入门|13 生命周期]] | 编译器自动计算引用有效期, 对标 address sanitizer | — |
| 14 | [[rust/1入门/14-组织代码：模块与包|14 模块]] | `mod` ≈ namespace, `crate` ≈ translation unit | P1200 |

> 完成 Phase 1 后去 [洛谷 Rust 题单](https://www.luogu.com.cn/problem/list?tag=303) 独立解决 10 题。

---

### Phase 2: Rust 底层原理 (建议 2-3 周)

目标：理解 Rust 编译器和运行时的底层机制——对应 C++ 中理解"编译器如何翻译虚函数调用/模板/函数对象"的阶段。

| 顺序 | 文件 | 对应 C++ 底层知识 |
|------|------|-------------------|
| 15 | [[rust/2深入/01-内存本质：从比特到指针|01 内存本质]] | 虚拟内存、TLB、DRAM 时序 — 与 C++ 共享的基础 |
| 16 | [[rust/2深入/02-所有权系统的计算机科学基础|02 所有权系统]] | MIR drop elaboration = C++ 编译器隐式析构调用 |
| 17 | [[rust/2深入/03-引用与生命周期的底层实现|03 生命周期底层]] | NLL borrowck = C++ lifetime annotation + clang-tidy |
| 18 | [[rust/2深入/04-类型系统的力量|04 类型系统]] | Hindley-Milner 推导 vs C++ 模板推导 |
| 19 | [[rust/2深入/05-Trait系统的计算机科学|05 Trait 系统]] | vtable 布局、胖指针 = 虚函数表指针 + 数据指针 |
| 20 | [[rust/2深入/06-智能指针的内存管理原理|06 智能指针]] | `Box` = `unique_ptr`, `Rc` = `shared_ptr`, `Arc` = `atomic shared_ptr` |
| 21 | [[rust/2深入/07-并发的硬件基础|07 并发硬件]] | 缓存一致性 MESI — 同体系，不同实现 |
| 22 | [[rust/2深入/08-异步编程的底层机制|08 异步底层]] | Future 状态机 = C++20 coroutine + executor |
| 23 | [[rust/2深入/09-Unsafe-Rust的计算机科学边界|09 Unsafe]] | `unsafe` 块 = 手写原始指针/汇编, 等同 C 编程 |
| 24 | [[rust/2深入/10-编译器如何理解你的代码|10 编译器]] | HIR→MIR→LLVM = AST→IR→rli |
| 25 | [[rust/2深入/11-宏系统的编译原理|11 宏系统]] | 过程宏 = C++ template metaprogramming (更可控) |

---

### Phase 3: 项目实践与工程 (选学)

| 顺序 | 文件 | 对应项目类型 |
|------|------|------------|
| 26 | [[rust/3实践/01-简易计算器：从零到GUI|01 计算器]] | 桌面 GUI (egui) |
| 27 | [[rust/3实践/02-学生管理系统：命令行工具|02 学生管理]] | CLI 工具 (clap) |
| 28 | [[rust/3实践/03-工具栏管理工具：TUI入门|03 TUI 工具]] | 终端 UI (ratatui) |
| 29 | [[rust/3实践/04-音乐流媒体播放器|04 音乐播放]] | 网络 + 音频 (reqwest + rodio) |
| 30 | [[rust/3实践/05-贪吃蛇游戏：从零开发|05 贪吃蛇]] | 游戏开发 (ggez) |

---

### Phase 4: 企业工程与安全 (选学)

| 文件 | 对应领域 |
|------|---------|
| [[rust/4工程/01-Cargo工程化与企业级构建|Cargo 工程化]] | CI/CD、workspace、feature flag |
| [[rust/4工程/02-企业级测试策略|测试策略]] | unit test、integration test、property test |
| [[rust/4工程/03-安全错误处理|错误处理]] | thiserror、anyhow、错误链 |
| [[rust/4工程/04-内存安全与后门防范|内存安全]] | supply chain attack 防护 |
| [[rust/4工程/05-网络安全：零信任架构|零信任]] | TLS、mTLS、certificate pinning |
| [[rust/4工程/06-数据安全与加密|数据安全]] | AES-GCM、Argon2、zeroize |
| [[rust/4工程/07-并发与异步安全|并发安全]] | tokio、actix、deadlock 预防 |
| [[rust/4工程/08-性能优化与安全权衡|性能优化]] | criterion、perf、flamegraph |
| [[rust/4工程/09-FFI与跨语言安全|FFI 安全]] | C ABI 稳定性、bindgen、cbindgen |
| [[rust/4工程/10-嵌入式与no_std企业应用|嵌入式]] | `#![no_std]`、cortex-m、embedded-hal |

---

### Phase 5: C → Rust 实战重构 (选学)

| 顺序 | 文件 | 练习规模 |
|------|------|---------|
| 1 | [[rust/5重构/01-C代码阅读理解方法论|C 代码理解]] | 方法论 — 分析任意 C 代码 |
| 2 | [[rust/5重构/02-简单C函数重构实战|简单函数]] | 单个函数, < 50行 C |
| 3 | [[rust/5重构/03-C项目结构重构|项目结构]] | Makefile → Cargo, 头文件 → 模块 |
| 4 | [[rust/5重构/04-开源C项目重构：小型|小型项目]] | < 1000 行 |
| 5 | [[rust/5重构/05-开源C项目重构：中型|中型项目]] | 1000-10000 行 |
| 6 | [[rust/5重构/06-重构方法论总结|方法论总结]] | 渐进式、增量验证 |

---

### Rust 与 RootStack 其他模块的关联

| 模块 | 关联点 | 链接 |
|------|--------|------|
| 数据结构 | Rust 标准库的 `Vec`/`HashMap`/`BTreeMap` 对应数据结构章节 | [[数据结构/DSA学习路线|DSA 学习路线]] |
| 算法 | 所有洛谷算法题均可用 Rust 实现 | [[算法/算法技巧/动态规划|DP 技巧]] |
| C 语言 | Rust FFI 大量使用 C ABI | [[c语言教程/2深化/06_编译链接与ELF|C 编译链接与 ELF]] |
| C++ 进阶 | trait object `dyn` 与虚函数 vtable 对比 | [[cpp教程/cpp深化教程/07_面向对象(三)多态与虚函数|CPP 多态]] |
| 内核 | Linux Rust 内核开发 | [[内核/C与Rust的内核新时代|C 与 Rust 内核新时代]] |
| 红队 | Rust 在网络安全工具链中的应用 | [[red_team/Rust红队脚本编程|Rust 红队脚本]] |

---

### 说明

本路径是 RootStack 体系中最新建立的学习路径之一。Rust 的内容持续迭代中——建议每完成一个 Rust 教程文件后，回到本路径查阅下一步。

对于有 C++ 基础的读者，Rust 的学习重在理解**所有权/借用/生命周期**这三个核心概念——它们是 Rust 独占的，C++ 没有直接对应物。前两周碰到编译错误不要气馁，这是编译器在教你怎么写安全的代码。
