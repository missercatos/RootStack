# Cargo工程化与企业级构建

## 原理

企业级 Rust 项目的核心要求：

**可重现构建**：`Cargo.lock` 提交到 Git，同一 commit 在任何机器产生完全相同二进制。依赖锁定使用精确版本号，无 `*` 通配符。构建在隔离 CI 容器中完成，不依赖开发机本地状态。

**供应链安全**：`cargo audit` 扫描依赖 CVE；`cargo deny` 检查许可证合规和重复依赖；`cargo vet` 记录每个第三方依赖的审查结果。发布产物应通过 GPG/Sigstore 代码签名。

**CI 流水线**：每次 PR 运行 `cargo test` + `cargo clippy -- -D warnings` + `cargo fmt --check` + `cargo audit`。wasm/嵌入式项目的交叉编译配置在 `rustup target add` 中管理。

**发布构建**：`[profile.release]` 配置 `opt-level = 3`, `lto = "fat"`, `codegen-units = 1`, `panic = "abort"` 以最小化二进制体积。

---

## Cargo.toml 字段详解

### `[package]` 元数据

`Cargo.toml` 的 `[package]` 段是 crate 的身份声明。每个字段都有精确语义：

```toml
[package]
name = "enterprise-app"          # crate 名称，发布到 crates.io 的唯一标识
version = "0.1.0"               # 语义化版本 (SemVer): MAJOR.MINOR.PATCH
edition = "2021"                # Rust 版本: 2015, 2018, 2021, 2024
rust-version = "1.70"           # MSRV (Minimum Supported Rust Version)
authors = ["Team <team@corp.com>"]
description = "Enterprise application"
license = "MIT OR Apache-2.0"   # SPDX 许可证表达式
repository = "https://github.com/corp/app"
readme = "README.md"
keywords = ["enterprise", "saas"]
categories = ["web-programming"]
exclude = ["/tests", "/benches", "/.github"]  # 发布时排除的文件
include = ["/src", "/LICENSE", "/Cargo.toml"]  # 显式包含（与 exclude 互斥）
```

**SemVer 与 Cargo 的兼容性规则**：

| 版本约束 | 含义 | 示例匹配 |
|---------|------|---------|
| `^1.2.3` | >=1.2.3, <2.0.0 | 1.2.4, 1.9.0, 但不匹配 2.0.0 |
| `~1.2.3` | >=1.2.3, <1.3.0 | 1.2.4, 但不匹配 1.3.0 |
| `=1.2.3` | 精确匹配 | 只有 1.2.3 |
| `>=1.2, <1.5` | 范围约束 | 1.2.0 ~ 1.4.x |
| `*` | 任何版本（不推荐） | 全部 |

**`edition` 字段的深层含义**：

Rust edition 不影响 API 兼容性，但改变语法行为：
- **2015**：默认所有项 `pub`，`macro_use` 导入宏，`dyn Trait` 可选
- **2018**：模块系统重写（`use crate::`），`dyn Trait` 必须显式，`async/await` 可用
- **2021**：闭包自动捕获改进，`IntoIterator for arrays`，`panic!` 格式化宏严格化
- **2024**：`unsafe extern` blocks，lifetime capture rules 变更，`gen` keyword 预留

---

### `[dependencies]` 依赖管理

```toml
[dependencies]
# 基本依赖 — 从 crates.io 拉取
serde = "1.0"                          # ^1.0.0 的简写
serde_json = "=1.0.100"                # 精确版本锁定

# 特性选择 — 编译期 feature flags
tokio = { version = "1", features = ["full"] }
# 等价于: ["rt", "rt-multi-thread", "net", "io-util", "time", "sync", "macros", "fs"]

# 可选依赖 — 条件编译
chrono = { version = "0.4", optional = true }
# 需要手动启用: cargo build --features chrono
# 或在 [features] 中声明: chrono = ["dep:chrono"]

# Git 依赖 — 从仓库拉取
my-lib = { git = "https://github.com/org/lib", branch = "main" }
my-lib = { git = "https://github.com/org/lib", tag = "v1.0" }
my-lib = { git = "https://github.com/org/lib", rev = "abc123" }  # 固定提交

# 路径依赖 — 本地 crate（workspace 内常用）
common = { path = "../common" }

# 重命名依赖 — 解决命名冲突
my_serde = { package = "serde", version = "1" }
```

### `[dev-dependencies]` 和 `[build-dependencies]`

```toml
[dev-dependencies]
# 仅在测试、benchmark、example 中编译
criterion = { version = "0.5", features = ["html_reports"] }
tempfile = "3"
mockall = "0.11"
assert_cmd = "2.0"     # 测试 CLI 工具
predicates = "3"       # 断言谓词

[build-dependencies]
# 仅在 build.rs 中使用
cc = "1.0"             # 编译 C/C++ 代码
bindgen = "0.65"       # 生成 FFI 绑定
```

**依赖解析的工作原理**：

Cargo 使用 SAT-solver 风格的算法解析依赖。当两个 crate 依赖同一个库的不同版本时，它们会在依赖树中共存（不是冲突）。这就是为什么 `cargo tree -d` 会显示重复依赖的原因。

---

### `[features]` Feature Flags

Feature flags 是 Rust 的编译期条件编译机制，类似于 C 的 `#ifdef`，但更安全、更可组合：

```toml
[features]
# 默认启用的 features
default = ["json", "logging"]

# 独立 feature — 启用条件编译
json = ["serde", "serde_json"]
logging = ["tracing/log", "dep:tracing-subscriber"]

# 可选依赖 feature — 依赖标记为 optional 后通过 dep: 启用
chrono = ["dep:chrono"]

# 强制启用某个 feature 的 feature
full = ["json", "logging", "chrono", "database"]

# 内部 feature — 不依赖外部 crate，仅作为 cfg 标记
unstable = []

# Feature 之间无层级关系，但可以互相引用
[dependencies]
serde = { version = "1", optional = true }
serde_json = { version = "1", optional = true }
tracing = { version = "1", optional = true }
tracing-subscriber = { version = "0.3", optional = true }
chrono = { version = "0.4", optional = true }
```

**Feature 统一（Unification）**：

当 workspace 中多个 crate 或同一个 crate 的多个 target 依赖不同的 feature 时，Cargo 会将所有 feature 合并。例如：

```toml
# crate A 依赖: serde = { features = ["derive"] }
# crate B 依赖: serde = { features = ["rc"] }
# 最终 serde 的 features: ["derive", "rc"] — 并集
```

**Feature 设计最佳实践**：

```rust
// 在代码中使用 feature gates
#[cfg(feature = "json")]
pub mod json_serde {
    pub fn serialize<T: serde::Serialize>(val: &T) -> String {
        serde_json::to_string(val).unwrap()
    }
}

// 组合 feature 条件
#[cfg(all(feature = "json", not(feature = "legacy")))]
pub mod modern_json { /* ... */ }

// platform-specific feature
#[cfg(all(target_os = "linux", feature = "io_uring"))]
pub mod io_uring_backend { /* ... */ }
```

---

### `[profile]` 构建 Profile 详解

构建 profile 控制编译器行为，直接影响编译时间、运行性能和二进制体积：

```toml
[profile.dev]
opt-level = 0                    # 不优化（编译最快）
debug = true                     # 生成调试信息
debug-assertions = true          # 启用 assert!() 检查
overflow-checks = true           # 整数溢出检查
incremental = true               # 增量编译（第二次编译更快）
codegen-units = 256              # 多编译单元并行（编译快，优化差）
lto = "off"                      # 不链接时优化

[profile.release]
opt-level = 3                    # 最高优化（运行最快）
lto = "fat"                      # 全量 LTO（单编译单元，优化最深）
codegen-units = 1                # 单编译单元（优化最深，编译最慢）
panic = "abort"                  # panic 直接 abort（不展开栈，体积小）
strip = "symbols"                # 剥离符号表
debug = false                    # 不生成调试信息
overflow-checks = false          # 无溢出检查（性能更好）
incremental = false              # 无增量编译
debug-assertions = false

# 自定义 profile — 基于现有 profile
[profile.profiling]
inherits = "release"
opt-level = 1                    # 保留调试信息可读
debug = true
debug-assertions = true
strip = "none"
```

**LTO（链接时优化）模式对比**：

| 模式 | 编译时间 | 优化效果 | 二进制体积 | 适用场景 |
|------|---------|---------|-----------|---------|
| `"off"` | 最快 | 无 | 最大 | 开发调试 |
| `"thin"` | 中等 | 良好 | 中等 | 平衡选择 |
| `"fat"` | 最慢 | 最佳 | 最小 | 发布构建 |

**`codegen-units` 的影响**：

编译器将源码拆分为 N 个编译单元并行编译，最后链接。单元数越少，跨单元优化机会越多，但编译并行度越低。企业级发布构建建议设为 `1`。

---

## Cargo Workspace

大型项目通常使用 workspace 管理多个相互依赖的 crate：

```toml
# 根 Cargo.toml
[workspace]
members = [
    "crates/core",
    "crates/api",
    "crates/cli",
    "crates/common",
]
# 虚拟 workspace — 根目录无 src/main.rs
resolver = "2"    # 新版依赖解析器（edition 2021+ 推荐）

# 共享依赖版本 — 所有 member 自动继承
[workspace.dependencies]
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
tracing = "0.1"
thiserror = "1.0"
anyhow = "1.0"

# Workspace 级别 profile
[profile.release]
lto = "fat"
codegen-units = 1
```

```toml
# crates/api/Cargo.toml — 子 crate 引用 workspace 依赖
[package]
name = "api"
version = "0.1.0"
edition = "2021"

[dependencies]
tokio.workspace = true           # 继承 workspace 的 tokio 配置
serde.workspace = true
core = { path = "../core" }      # 同 workspace 内的 crate
common = { path = "../common" }
```

**Workspace 的优势**：

1. **统一 `Cargo.lock`**：所有 crate 共享同一个锁文件，确保一致性
2. **共享 `target/` 目录**：避免重复编译公共依赖
3. **统一 profile**：所有 crate 使用相同的编译优化级别
4. **原子发布**：`cargo publish --workspace` 可以按依赖顺序发布

**Workspace 命令**：

```bash
# 运行所有 crate 的测试
cargo test --workspace

# 运行指定 crate 的测试
cargo test -p api

# 构建所有 crate
cargo build --workspace

# 检查所有 crate
cargo clippy --workspace --all-targets

# 检查依赖树
cargo tree --workspace

# 发布所有 crate（按依赖顺序）
cargo publish --workspace
```

---

## 交叉编译

Rust 支持交叉编译到不同目标平台：

```bash
# 查看可用目标
rustup target list

# 安装目标
rustup target add x86_64-unknown-linux-musl
rustup target add aarch64-linux-android
rustup target add wasm32-unknown-unknown

# 交叉编译
cargo build --target x86_64-unknown-linux-musl --release
```

```toml
# .cargo/config.toml — 为特定目标配置链接器
[target.x86_64-unknown-linux-musl]
linker = "rust-musl-gcc"
rustflags = ["-C", "target-feature=+crt-static"]

[target.aarch64-linux-android]
linker = "aarch64-linux-android-clang"

[target.wasm32-unknown-unknown]
# 无链接器（wasm 输出为 .wasm 文件）
```

**交叉编译工具链管理**：

| 目标 | 链接器 | C 工具链 | 备注 |
|------|--------|---------|------|
| `x86_64-unknown-linux-musl` | `musl-gcc` | musl | 静态链接 Linux |
| `aarch64-apple-darwin` | `clang` | Xcode | macOS ARM |
| `x86_64-pc-windows-msvc` | `lld-link` | MSVC | Windows |
| `wasm32-unknown-unknown` | 无 | wasm-opt | WebAssembly |

---

## 企业级工具链

### cargo expand — 宏展开调试

```bash
cargo install cargo-expand

# 查看宏展开后的实际代码
cargo expand --release

# 展开特定模块
cargo expand my_crate::my_module
```

**使用场景**：调试 derive 宏生成的代码、理解 `tokio::select!` 展开结果、验证宏正确性。

### cargo clippy — 代码质量检查

```bash
# 运行所有 lint
cargo clippy --all-targets --all-features

# 将 warning 转为 error（CI 必用）
cargo clippy -- -D warnings

# 启用 nursery lint（实验性 lint）
cargo clippy -- -W clippy::nursery

# 常用 lint
cargo clippy -- -W clippy::pedantic      # 严格模式
cargo clippy -- -W clippy::all           # 所有默认 lint
cargo clippy -- -A clippy::module_name  # 禁用特定 lint
```

**clippy 在 CI 中的配置**：

```rust
// 在 lib.rs 或 main.rs 顶部声明
#![warn(
    clippy::all,
    clippy::pedantic,
    clippy::nursery,
    clippy::unwrap_used,
    clippy::expect_used,
    clippy::panic,
    clippy::todo,
    clippy::unimplemented
)]
#![deny(clippy::correctness)]  // 正确性 lint 直接报错
```

### cargo audit — 安全审计

```bash
cargo install cargo-audit

# 扫描已知漏洞
cargo audit

# 仅报告严重漏洞
cargo audit --severity critical

# 自动修复（如果 crates.io 提供补丁）
cargo audit fix

# 输出 JSON 格式（供 CI 解析）
cargo audit --json
```

### cargo deny — 许可证与依赖审查

```toml
# deny.toml
[advisories]
vulnerability = "deny"           # 拒绝有漏洞的依赖
unmaintained = "warn"            # 警告无人维护的依赖
yanked = "warn"                 # 警告被 yank 的版本
notice = "warn"                 # 警告 notices

[licenses]
unlicensed = "deny"             # 拒绝无许可证的依赖
allow = [
    "MIT",
    "Apache-2.0",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "ISC",
    "Unicode-DFS-2016",
]
copyleft = "deny"               # 拒绝 copyleft 许可证

[bans]
multiple-versions = "warn"      # 多版本警告
wildcards = "allow"
highlight = "all"

[sources]
unknown-registry = "deny"       # 拒绝未知 registry
unknown-git = "deny"            # 拒绝未知 git 来源
allow-registry = ["https://github.com/rust-lang/crates.io-index"]
allow-git = []
```

---

## Release vs Debug 构建对比

| 维度 | Debug | Release |
|------|-------|---------|
| `opt-level` | 0 | 3 |
| 编译时间 | 快 | 慢（5-10x） |
| 运行速度 | 慢（10-100x） | 快 |
| 二进制体积 | 大 | 小（配合 LTO + strip） |
| 调试信息 | 完整 | 可选 |
| 溢出检查 | 是 | 否 |
| `assert!()` | 生效 | 生效（但无 debug-assertions 时部分跳过） |
| `#[cfg(debug_assertions)]` | 生效 | 不生效 |
| 增量编译 | 默认开启 | 默认关闭 |
| `panic` 展开 | 栈展开 | `abort`（可配置） |

**何时用 Debug 构建**：

- 开发阶段：快速编译、完整调试信息、断言检查
- 测试阶段：启用 `overflow-checks` 防止整数溢出漏洞
- 基准测试前：先用 Debug 跑通逻辑，再用 Release 测性能

**何时用 Release 构建**：

- 生产部署
- 性能基准测试
- 嵌入式/WASM（体积敏感）
- CI 的最终验证步骤

---

## 实践

### 力扣问题

算法与工程目标不同。此处强调工具链掌握。

### AI 自检

1. `lto = "fat"` 和 `lto = "thin"` 的区别？各自对编译时间和优化效果的权衡？
2. 可重现构建为什么需要 `Cargo.lock` 提交到 Git？
3. workspace 中如何管理多个 crate 的版本号？`cargo-release` 的工作流程是什么？
4. `#[cfg(feature = "x")]` 和 `#[cfg(feature_x)]` 有什么区别？feature naming 约定是什么？
5. 交叉编译到 musl 目标时，为什么需要 `target-feature=+crt-static`？
