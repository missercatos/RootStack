# Rust 

> , ,  Rust 
> 

---

##  Web

|  |  |  |  |
|------|------|------|---------|
| [tokio-rs/tokio](https://github.com/tokio-rs/tokio) | ,  |  | async/await, epoll/io_uring, work-stealing |
| [hyperium/hyper](https://github.com/hyperium/hyper) | HTTP  |  | IO, , trait object |
| [seanmonstar/reqwest](https://github.com/seanmonstar/reqwest) | HTTP  |  | , TLS,  |
| [hyperium/axum](https://github.com/hyperium/axum) | Web  |  | Tower ,  |
| [actix/actix-web](https://github.com/actix/actix-web) |  Web  |  | Actor ,  |
| [jman0129/tcpproxy](https://github.com/jman0129/tcpproxy) | TCP  |  | , tokio |

****: tokio  → reqwest/hyper  HTTP → axum  Web 

---

## 

|  |  |  |  |
|------|------|------|---------|
| [BurntSushi/ripgrep](https://github.com/BurntSushi/ripgrep) |  grep  |  | , SIMD,  |
| [sharkdp/fd](https://github.com/sharkdp/fd) | find  |  | , ,  |
| [sharkdp/bat](https://github.com/sharkdp/bat) | cat  |  | , Git ,  |
| [dalance/procs](https://github.com/dalance/procs) | ps  |  | ,  |
| [cli/cli](https://github.com/cli/cli) | GitHub CLI (gh) |  | API , OAuth,  |

****: fd → bat → ripgrep ( SIMD )

---

## 

|  |  |  |  |
|------|------|------|---------|
| [astral-sh/uv](https://github.com/astral-sh/uv) |  Python  |  | , ,  |
| [tailwindlabs/watchman](https://github.com/facebook/watchman) |  |  | inotify/kqueue,  |
| [warp-tech/ratatui](https://github.com/ratatui-org/ratatui) |  UI  |  | , ,  |
| [ClementTsang/bottom](https://github.com/ClementTsang/bottom) |  (btm) |  | , ,  |
| [dalance/procs](https://github.com/dalance/procs) |  |  | /proc ,  |

****: bottom  → ratatui  TUI → watchman 

---

## 

|  |  |  |  |
|------|------|------|---------|
| [tikv/tikv](https://github.com/tikv/tikv) |  KV  |  | Raft , MVCC, LSM  |
| [apache/arrow-datafusion](https://github.com/apache/arrow-datafusion) | SQL  |  | , , Parquet |
| [launchbadge/sqlx](https://github.com/launchbadge/sqlx) |  SQL  |  |  SQL ,  |
| [rusqlite/rusqlite](https://github.com/rusqlite/rusqlite) | SQLite  |  | FFI ,  |

****: sqlx  → datafusion  → tikv 

---

## 

|  |  |  |  |
|------|------|------|---------|
| [RustCrypto/traits](https://github.com/RustCrypto/traits) |  |  | trait-based ,  |
| [dalek-cryptography/curve25519-dalek](https://github.com/dalek-cryptography/curve25519-dalek) |  |  | ,  |
| [RustCrypto/aead](https://github.com/RustCrypto/aead) | AEAD  |  | AES-GCM, ChaCha20Poly1305 |

---

## 

|  |  |  |  |
|------|------|------|---------|
| [bevyengine/bevy](https://github.com/bevyengine/bevy) | ECS  |  | ECS , ,  |
| [ggez/ggez](https://github.com/ggez/ggez) | 2D  |  | , ,  |
| [gfx-rs/wgpu](https://github.com/gfx-rs/wgpu) | WebGPU  |  | GPU , ,  |

****: ggez  2D  → bevy  ECS → wgpu  GPU 

---

##  IoT

|  |  |  |  |
|------|------|------|---------|
| [rust-embedded/book](https://github.com/rust-embedded/book) |  Rust  |  | no_std, ,  |
| [esp-rs/esp-hal](https://github.com/esp-rs/esp-hal) | ESP32 HAL |  |  HAL,  |
| [nrf-rs/nrf-hal](https://github.com/nrf-rs/nrf-hal) | Nordic nRF HAL |  | , BLE |

---

## 

|  |  |  |  |
|------|------|------|---------|
| [rust-lang/rust](https://github.com/rust-lang/rust) | Rust  |  | MIR, borrowck, codegen |
| [rust-lang/chalk](https://github.com/rust-lang/chalk) | trait  |  | Prolog , WF  |
| [rust-analyzer/rust-analyzer](https://github.com/rust-analyzer/rust-analyzer) | IDE  |  | , , Salsa |
| [denoland/deno](https://github.com/denoland/deno) | JS/TS  |  | V8 , , TypeScript |

****: rust-analyzer  IDE  → chalk  trait  → rust 

---

##  AI

|  |  |  |  |
|------|------|------|---------|
| [pola-rs/polars](https://github.com/pola-rs/polars) | DataFrame  ( pandas ) |  | , SIMD, Apache Arrow |
| [huggingface/tokenizers](https://github.com/huggingface/tokenizers) | BPE  |  | , BPE , PyO3 |
| [pybind/pyo3](https://github.com/PyO3/pyo3) | Rust ↔ Python  |  | FFI, GIL,  |
| [astral-sh/ruff](https://github.com/astral-sh/ruff) | Python linter ( pylint  100x) |  | AST ,  |

****: tokenizers  PyO3 → polars  → ruff 

---

## 

### 

```
1.  README  Cargo.toml 
2.  (main.rs / lib.rs)
3.  ( →  → )
4.  trait 
5. 
6.  issue  PR 
```

### 

```
: fd → bat → sqlx
: ripgrep → axum → polars
: tokio → rust-analyzer → tikv
```

### 

```
1.  "good first issue" 
2.  (typo, example)
3. 
4.  bug
5. 
6. 
```
