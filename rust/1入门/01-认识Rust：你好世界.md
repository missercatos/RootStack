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

## 语法

### 安装

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

三个核心工具：
- `rustc` — 编译器，将 `.rs` → 二进制
- `cargo` — 包管理器和构建系统
- `rustup` — 工具链版本管理

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

### Cargo.toml 结构

```toml
[package]
name = "hello"
version = "0.1.0"
edition = "2021"

[dependencies]
```

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
