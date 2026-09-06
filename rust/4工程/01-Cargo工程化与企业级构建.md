# Cargo

## 

 Rust 

****`Cargo.lock`  Git commit  `*`  CI 

****`cargo audit`  CVE`cargo deny` `cargo vet`  GPG/Sigstore 

**CI ** PR  `cargo test` + `cargo clippy -- -D warnings` + `cargo fmt --check` + `cargo audit`wasm/ `rustup target add` 

****`[profile.release]`  `opt-level = 3`, `lto = "fat"`, `codegen-units = 1`, `panic = "abort"` 

---

## Cargo.toml 

### `[package]` 

`Cargo.toml`  `[package]`  crate 

```toml
[package]
name = "enterprise-app"          # crate  crates.io 
version = "0.1.0"               #  (SemVer): MAJOR.MINOR.PATCH
edition = "2021"                # Rust : 2015, 2018, 2021, 2024
rust-version = "1.70"           # MSRV (Minimum Supported Rust Version)
authors = ["Team <team@corp.com>"]
description = "Enterprise application"
license = "MIT OR Apache-2.0"   # SPDX 
repository = "https://github.com/corp/app"
readme = "README.md"
keywords = ["enterprise", "saas"]
categories = ["web-programming"]
exclude = ["/tests", "/benches", "/.github"]  # 
include = ["/src", "/LICENSE", "/Cargo.toml"]  #  exclude 
```

**SemVer  Cargo **

|  |  |  |
|---------|------|---------|
| `^1.2.3` | >=1.2.3, <2.0.0 | 1.2.4, 1.9.0,  2.0.0 |
| `~1.2.3` | >=1.2.3, <1.3.0 | 1.2.4,  1.3.0 |
| `=1.2.3` |  |  1.2.3 |
| `>=1.2, <1.5` |  | 1.2.0 ~ 1.4.x |
| `*` |  |  |

**`edition` **

Rust edition  API 
- **2015** `pub``macro_use` `dyn Trait` 
- **2018**`use crate::``dyn Trait` `async/await` 
- **2021**`IntoIterator for arrays``panic!` 
- **2024**`unsafe extern` blockslifetime capture rules `gen` keyword 

---

### `[dependencies]` 

```toml
[dependencies]
#  —  crates.io 
serde = "1.0"                          # ^1.0.0 
serde_json = "=1.0.100"                # 

#  —  feature flags
tokio = { version = "1", features = ["full"] }
# : ["rt", "rt-multi-thread", "net", "io-util", "time", "sync", "macros", "fs"]

#  — 
chrono = { version = "0.4", optional = true }
# : cargo build --features chrono
#  [features] : chrono = ["dep:chrono"]

# Git  — 
my-lib = { git = "https://github.com/org/lib", branch = "main" }
my-lib = { git = "https://github.com/org/lib", tag = "v1.0" }
my-lib = { git = "https://github.com/org/lib", rev = "abc123" }  # 

#  —  crateworkspace 
common = { path = "../common" }

#  — 
my_serde = { package = "serde", version = "1" }
```

### `[dev-dependencies]`  `[build-dependencies]`

```toml
[dev-dependencies]
# benchmarkexample 
criterion = { version = "0.5", features = ["html_reports"] }
tempfile = "3"
mockall = "0.11"
assert_cmd = "2.0"     #  CLI 
predicates = "3"       # 

[build-dependencies]
#  build.rs 
cc = "1.0"             #  C/C++ 
bindgen = "0.65"       #  FFI 
```

****

Cargo  SAT-solver  crate  `cargo tree -d` 

---

### `[features]` Feature Flags

Feature flags  Rust  C  `#ifdef`

```toml
[features]
#  features
default = ["json", "logging"]

#  feature — 
json = ["serde", "serde_json"]
logging = ["tracing/log", "dep:tracing-subscriber"]

#  feature —  optional  dep: 
chrono = ["dep:chrono"]

#  feature  feature
full = ["json", "logging", "chrono", "database"]

#  feature —  crate cfg 
unstable = []

# Feature 
[dependencies]
serde = { version = "1", optional = true }
serde_json = { version = "1", optional = true }
tracing = { version = "1", optional = true }
tracing-subscriber = { version = "0.3", optional = true }
chrono = { version = "0.4", optional = true }
```

**Feature Unification**

 workspace  crate  crate  target  feature Cargo  feature 

```toml
# crate A : serde = { features = ["derive"] }
# crate B : serde = { features = ["rc"] }
#  serde  features: ["derive", "rc"] — 
```

**Feature **

```rust
//  feature gates
#[cfg(feature = "json")]
pub mod json_serde {
    pub fn serialize<T: serde::Serialize>(val: &T) -> String {
        serde_json::to_string(val).unwrap()
    }
}

//  feature 
#[cfg(all(feature = "json", not(feature = "legacy")))]
pub mod modern_json { /* ... */ }

// platform-specific feature
#[cfg(all(target_os = "linux", feature = "io_uring"))]
pub mod io_uring_backend { /* ... */ }
```

---

### `[profile]`  Profile 

 profile 

```toml
[profile.dev]
opt-level = 0                    # 
debug = true                     # 
debug-assertions = true          #  assert!() 
overflow-checks = true           # 
incremental = true               # 
codegen-units = 256              # 
lto = "off"                      # 

[profile.release]
opt-level = 3                    # 
lto = "fat"                      #  LTO
codegen-units = 1                # 
panic = "abort"                  # panic  abort
strip = "symbols"                # 
debug = false                    # 
overflow-checks = false          # 
incremental = false              # 
debug-assertions = false

#  profile —  profile
[profile.profiling]
inherits = "release"
opt-level = 1                    # 
debug = true
debug-assertions = true
strip = "none"
```

**LTO**

|  |  |  |  |  |
|------|---------|---------|-----------|---------|
| `"off"` |  |  |  |  |
| `"thin"` |  |  |  |  |
| `"fat"` |  |  |  |  |

**`codegen-units` **

 N  `1`

---

## Cargo Workspace

 workspace  crate

```toml
#  Cargo.toml
[workspace]
members = [
    "crates/core",
    "crates/api",
    "crates/cli",
    "crates/common",
]
#  workspace —  src/main.rs
resolver = "2"    # edition 2021+ 

#  —  member 
[workspace.dependencies]
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
tracing = "0.1"
thiserror = "1.0"
anyhow = "1.0"

# Workspace  profile
[profile.release]
lto = "fat"
codegen-units = 1
```

```toml
# crates/api/Cargo.toml —  crate  workspace 
[package]
name = "api"
version = "0.1.0"
edition = "2021"

[dependencies]
tokio.workspace = true           #  workspace  tokio 
serde.workspace = true
core = { path = "../core" }      #  workspace  crate
common = { path = "../common" }
```

**Workspace **

1. ** `Cargo.lock`** crate 
2. ** `target/` **
3. ** profile** crate 
4. ****`cargo publish --workspace` 

**Workspace **

```bash
#  crate 
cargo test --workspace

#  crate 
cargo test -p api

#  crate
cargo build --workspace

#  crate
cargo clippy --workspace --all-targets

# 
cargo tree --workspace

#  crate
cargo publish --workspace
```

---

## 

Rust 

```bash
# 
rustup target list

# 
rustup target add x86_64-unknown-linux-musl
rustup target add aarch64-linux-android
rustup target add wasm32-unknown-unknown

# 
cargo build --target x86_64-unknown-linux-musl --release
```

```toml
# .cargo/config.toml — 
[target.x86_64-unknown-linux-musl]
linker = "rust-musl-gcc"
rustflags = ["-C", "target-feature=+crt-static"]

[target.aarch64-linux-android]
linker = "aarch64-linux-android-clang"

[target.wasm32-unknown-unknown]
# wasm  .wasm 
```

****

|  |  | C  |  |
|------|--------|---------|------|
| `x86_64-unknown-linux-musl` | `musl-gcc` | musl |  Linux |
| `aarch64-apple-darwin` | `clang` | Xcode | macOS ARM |
| `x86_64-pc-windows-msvc` | `lld-link` | MSVC | Windows |
| `wasm32-unknown-unknown` |  | wasm-opt | WebAssembly |

---

## 

### cargo expand — 

```bash
cargo install cargo-expand

# 
cargo expand --release

# 
cargo expand my_crate::my_module
```

**** derive  `tokio::select!` 

### cargo clippy — 

```bash
#  lint
cargo clippy --all-targets --all-features

#  warning  errorCI 
cargo clippy -- -D warnings

#  nursery lint lint
cargo clippy -- -W clippy::nursery

#  lint
cargo clippy -- -W clippy::pedantic      # 
cargo clippy -- -W clippy::all           #  lint
cargo clippy -- -A clippy::module_name  #  lint
```

**clippy  CI **

```rust
//  lib.rs  main.rs 
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
#![deny(clippy::correctness)]  //  lint 
```

### cargo audit — 

```bash
cargo install cargo-audit

# 
cargo audit

# 
cargo audit --severity critical

#  crates.io 
cargo audit fix

#  JSON  CI 
cargo audit --json
```

### cargo deny — 

```toml
# deny.toml
[advisories]
vulnerability = "deny"           # 
unmaintained = "warn"            # 
yanked = "warn"                 #  yank 
notice = "warn"                 #  notices

[licenses]
unlicensed = "deny"             # 
allow = [
    "MIT",
    "Apache-2.0",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "ISC",
    "Unicode-DFS-2016",
]
copyleft = "deny"               #  copyleft 

[bans]
multiple-versions = "warn"      # 
wildcards = "allow"
highlight = "all"

[sources]
unknown-registry = "deny"       #  registry
unknown-git = "deny"            #  git 
allow-registry = ["https://github.com/rust-lang/crates.io-index"]
allow-git = []
```

---

## Release vs Debug 

|  | Debug | Release |
|------|-------|---------|
| `opt-level` | 0 | 3 |
|  |  | 5-10x |
|  | 10-100x |  |
|  |  |  LTO + strip |
|  |  |  |
|  |  |  |
| `assert!()` |  |  debug-assertions  |
| `#[cfg(debug_assertions)]` |  |  |
|  |  |  |
| `panic`  |  | `abort` |

** Debug **

- 
-  `overflow-checks` 
-  Debug  Release 

** Release **

- 
- 
- /WASM
- CI 

---

## 

### 


