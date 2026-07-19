# Cargo工程化与企业级构建

## 原理

企业级 Rust 项目的核心要求：

**可重现构建**：`Cargo.lock` 提交到 Git，同一 commit 在任何机器产生完全相同二进制。依赖锁定使用精确版本号，无 `*` 通配符。构建在隔离 CI 容器中完成，不依赖开发机本地状态。

**供应链安全**：`cargo audit` 扫描依赖 CVE；`cargo deny` 检查许可证合规和重复依赖；`cargo vet` 记录每个第三方依赖的审查结果。发布产物应通过 GPG/Sigstore 代码签名。

**CI 流水线**：每次 PR 运行 `cargo test` + `cargo clippy -- -D warnings` + `cargo fmt --check` + `cargo audit`。wasm/嵌入式项目的交叉编译配置在 `rustup target add` 中管理。

**发布构建**：`[profile.release]` 配置 `opt-level = 3`, `lto = "fat"`, `codegen-units = 1`, `panic = "abort"` 以最小化二进制体积。

---

## 语法

```toml
# Cargo.toml — 企业级配置示例
[package]
name = "enterprise-app"
version = "0.1.0"
edition = "2021"
license = "MIT OR Apache-2.0"

[dependencies]
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }

[profile.release]
opt-level = 3
lto = "fat"
codegen-units = 1
panic = "abort"
strip = true

[profile.dev]
opt-level = 0

[[bin]]
name = "server"
path = "src/main.rs"
```

```yaml
# CI (GitHub Actions 示例)
# .github/workflows/ci.yml
- uses: actions-rs/cargo@v1
  with:
    command: test
    args: --all-features
- run: cargo fmt --all -- --check
- run: cargo clippy --all-targets -- -D warnings
- run: cargo audit
```

### 关键命令

| 命令 | 作用 |
|------|------|
| `cargo audit` | 依赖 CVE 扫描 |
| `cargo deny check` | 许可证/来源审查 |
| `cargo vet` | 依赖人工审计记录 |
| `cargo tree -d` | 重复依赖分析 |
| `cargo bloat --release` | 二进制体积分析 |
| `cargo build --timings` | 编译时间分析 |

---

## 实践

### 洛谷问题

算法与工程目标不同。此处强调工具链掌握。

### AI 自检

1. `lto = "fat"` 和 `lto = "thin"` 的区别？各自对编译时间和优化效果的权衡？
2. 可重现构建为什么需要 `Cargo.lock` 提交到 Git？
