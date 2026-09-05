# 认识Rust：你好世界

## 原理

Rust 是系统编程语言，编译后端基于 LLVM。编译器 `rustc` 将源码翻译为机器码，无运行时垃圾回收。类型系统在编译期通过所有权/借用检查器（Borrow Checker）保证内存安全，避免段错误和数据竞争。

编译管线：`.rs` 源文件 → `rustc` → LLVM IR → 目标平台机器码。

```mermaid
flowchart LR
 A["main.rs"] --> B["rustc"]
 B --> C["二进制文件"]
 C --> D["操作系统执行"]
```

Rust 将多数安全检查前移到编译期，运行时行为等价于手工管理的 C/C++ 代码，没有 JIT 和 GC 开销。面向的领域包括：系统编程、嵌入式、WebAssembly、网络服务、CLI 工具、密码学和安全底层。

[[../../c语言教程/1入门/01_环境配置|C: 语言概述]]

---

## 深入理解：Rust 如何实现零开销内存安全

### 什么是零开销抽象（Zero-Cost Abstraction）

零开销抽象是 C++ 首席设计师 Bjarne Stroustrup 提出的设计原则：**你不用的东西，不会付出运行时代价；你用的东西，手写代码也无法做得更好**。Rust 将这一原则推向了极致。

具体来说，Rust 的所有权系统、借用检查、生命周期标注——这些概念在运行时完全不存在。它们在编译期完成后，生成的机器码与等价的 C 代码几乎完全相同。

```rust
// Rust 版本
fn sum_slice(data: &[i32]) -> i32 {
    data.iter().sum()
}

// 等价的 C 版本
// int sum_slice(const int* data, size_t len) {
//     int sum = 0;
//     for (size_t i = 0; i < len; i++) sum += data[i];
//     return sum;
// }
```

两者编译后的汇编几乎一致。Rust 在编译期验证了 `data` 不会被意外修改、不会悬垂、不会越界——但运行时没有任何额外检查。

### Rust 如何在没有 GC 的情况下保证内存安全

C/C++ 的内存管理问题根源在于：**内存的分配和释放散落在代码各处，由程序员手动保证正确性**。一旦 `free` 的时机不对（use-after-free、double-free、memory leak），就是未定义行为。

Rust 的解法是将内存管理从「运行时动态检测」变为「编译期静态验证」：

```text
┌─────────────────────────────────────────────────┐
│              C/C++ 内存管理模型                   │
│                                                   │
│  malloc() ──→ 使用指针 ──→ free()                 │
│     │             │              │                │
│     │             │         可能忘记 free          │
│     │         可能悬垂          ↓                  │
│     │         指针使用        内存泄漏             │
│     ↓                                              │
│  分散在各处，编译器无法保证正确性                    │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│              Rust 内存管理模型                      │
│                                                   │
│  let s = String::from("hi");                     │
│     │                                             │
│     ├─ s 拥有数据                                 │
│     ├─ 赋值给 s2 时，s 失效（move）               │
│     │                                             │
│  s2 离开作用域 ──→ 自动调用 drop ──→ 释放内存      │
│                                                   │
│  编译器在编译期追踪每个值的所有权                   │
│  保证：恰好 drop 一次，永远不会悬垂                 │
└─────────────────────────────────────────────────┘
```

核心机制是 **所有权系统（Ownership）**——每个值有且只有一个所有者（owner），当所有者离开作用域（scope）时，值自动被释放。赋值时所有权转移（move），而非复制堆数据。

### 编译器内部：Borrow Checker 的工作原理

`rustc` 将源码编译为 HIR（High-level IR）→ MIR（Mid-level IR）→ LLVM IR。借用检查器工作在 MIR 阶段：

```text
源码 (.rs)
    ↓ parse
AST (抽象语法树)
    ↓ type check + macro expansion
HIR (高层中间表示)
    ↓ borrow check + NLL analysis    ← 所有权验证发生在这里
MIR (中间层 IR)
    ↓ optimization
LLVM IR
    ↓ codegen
机器码
```

在 MIR 阶段，编译器会分析每个变量的「活跃区间」（live range）。如果一个变量在某个点之后不再使用，它的所有权可以提前释放——这就是 NLL（Non-Lexical Lifetimes）的核心思想。

```rust
let mut s = String::from("hello");
let r1 = &s;
println!("{}", r1);     // r1 最后一次使用
let r2 = &mut s;        // ✅ r1 已不再使用，可以创建可变引用
r2.push_str(" world");
```

### 与 C/C++ 的对比

| 特性 | C | C++ | Rust |
|------|---|-----|------|
| 内存管理 | `malloc`/`free` | `new`/`delete` 或智能指针 | 所有权系统 |
| 悬垂指针 | 运行时崩溃 | 运行时崩溃 | 编译期拒绝 |
| 数据竞争 | 运行时检测（TSan） | 运行时检测 | 编译期阻止 |
| 空指针 | 段错误 | 段错误 | `Option<T>` 强制处理 |
| 缓冲区溢出 | 未定义行为 | 未定义行为 | 边界检查（可 opt-out） |
| 内存泄漏 | 可能 | 可能 | 可能（但极少） |

```rust
// Rust 编译期检查 vs C 运行时崩溃

// C 代码（可能 crash）：
// char* s = malloc(5);
// free(s);
// printf("%s", s);  // use-after-free，未定义行为

// Rust 等价代码：
let s = String::from("hi");
let r = &s;
drop(s);
// println!("{}", r);  // 编译错误：cannot borrow `s` as immutable
                       //           after it has been moved
```

---

## 语法

### 安装

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

三个核心工具：
- `rustc` — 编译器，将 `.rs` → 二进制
- `cargo` — 包管理器和构建系统
- `rustup` — 工具链版本管理

### rustup 与 cargo 的内部机制

`rustup` 管理的不只是一个 `rustc`，而是整套工具链（toolchain）：

```text
~/.rustup/toolchains/
├── stable-x86_64-unknown-linux-gnu/
│   ├── bin/
│   │   ├── rustc          ← 编译器
│   │   ├── cargo          ← 包管理器
│   │   ├── rustfmt        ← 格式化工具
│   │   └── clippy-driver  ← lint 检查器
│   ├── lib/
│   │   └── rustlib/       ← 标准库源码和预编译库
│   └── ...
├── nightly-x86_64-unknown-linux-gnu/
└── 1.75.0-x86_64-unknown-linux-gnu/
```

`cargo` 的工作流程：

```text
cargo build
    │
    ├─ 1. 解析 Cargo.toml，确定依赖
    ├─ 2. 从 crates.io（或 registry）下载依赖源码
    ├─ 3. 编译依赖（按拓扑顺序）
    ├─ 4. 编译当前 crate
    ├─ 5. 链接所有 .rlib/.so → 生成二进制
    │
    └─ 缓存在 target/ 目录，增量编译跳过未修改的文件
```

`crates.io` 是 Rust 的包仓库（类似 npm、PyPI），上面的包统称为 **crate**。每个 crate 是一个独立的编译单元。

### 创建和运行项目

```rust
// src/main.rs — cargo new 自动生成
fn main() {
 println!("Hello, world!");
}
```

```bash
cargo new hello # 创建项目
cargo build # 编译（debug）
cargo build --release # 编译（release，优化）
cargo run # 编译 + 运行
cargo check # 仅检查语法，不生成二进制（最快）
```

> `println!` 是宏，不是函数。`!` 表明宏调用，编译期展开为格式化代码。

### debug 与 release 的区别

| 配置 | 优化级别 | 溢出行为 | 调试信息 | 编译速度 |
|------|---------|---------|---------|---------|
| `cargo build` | 0（无优化） | panic | 完整 | 快 |
| `cargo build --release` | 3（全优化） | wrap | 无 | 慢 |

```rust
// debug 模式：溢出时 panic
let x: u8 = 255;
// let y = x + 1;  // panic: attempt to add with overflow

// release 模式：静默回绕
// let y = x + 1;  // y = 0（回绕）
```

### Cargo.toml 结构

```toml
[package]
name = "hello"
version = "0.1.0"
edition = "2021"

[dependencies]
serde = { version = "1.0", features = ["derive"] }
```

`edition` 字段表示 Rust 版本代际（2015、2018、2021、2024），不同 edition 间有语法差异但兼容编译。

### 关键命令速查

| 命令 | 作用 |
|------|------|
| `cargo new <name>` | 创建二进制项目 |
| `cargo new <name> --lib` | 创建库项目 |
| `cargo build` | 编译（debug） |
| `cargo run` | 编译并运行 |
| `cargo check` | 快速检查语法 |
| `cargo test` | 运行测试 |
| `cargo fmt` | 格式化代码 |
| `cargo clippy` | Lint 检查 |
| `cargo add <crate>` | 添加依赖 |
| `cargo doc --open` | 生成文档 |
| `rustc --explain E0382` | 查看错误码解释 |
| `rustup update` | 更新工具链 |

---

## 常见陷阱

### 1. 忘记 `cargo check` 就写代码
`cargo check` 比 `cargo build` 快 5-10 倍，因为它跳过了代码生成阶段。开发时先用 `check` 验证类型和借用，通过后再 `build`。

### 2. 混淆 `rustc` 和 `cargo`
直接调用 `rustc main.rs` 是可行的，但会丢失依赖管理和增量编译。始终使用 `cargo`。

### 3. 选择错误的项目类型
`cargo new mylib` 默认创建二进制项目。创建库需要用 `cargo new mylib --lib`。

---

## 实践

### 力扣问题

对于入门阶段，熟悉编译运行流程即可：

力扣: 力扣 Hello,World! 练习

```rust
fn main() {
 println!("Hello,World!");
}
```

### AI 自检

1. `cargo build` 和 `cargo check` 的区别是什么？哪个更快？为什么？
2. Rust 编译后端基于什么框架？编译出的机器码运行时是否有 GC 开销？
3. 零开销抽象的含义是什么？Rust 的所有权系统如何满足这一原则？
4. `rustc` 的编译管线分为哪几个阶段？借用检查器工作在哪一阶段？
