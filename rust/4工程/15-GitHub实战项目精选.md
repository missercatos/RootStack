# Rust 开源实战项目精选

> 学完理论后, 最好的学习方式是阅读和贡献优秀的开源项目。以下按领域分类, 收录值得深入研究的 Rust 项目。
> 每个项目标注了难度、核心技术和学习价值。

---

## 网络与 Web

| 项目 | 说明 | 难度 | 核心技术 |
|------|------|------|---------|
| [tokio-rs/tokio](https://github.com/tokio-rs/tokio) | 异步运行时, 生态核心 | ⭐⭐⭐ | async/await, epoll/io_uring, work-stealing |
| [hyperium/hyper](https://github.com/hyperium/hyper) | HTTP 库 | ⭐⭐⭐ | 异步IO, 零拷贝, trait object |
| [seanmonstar/reqwest](https://github.com/seanmonstar/reqwest) | HTTP 客户端 | ⭐⭐ | 异步, TLS, 连接池 |
| [hyperium/axum](https://github.com/hyperium/axum) | Web 框架 | ⭐⭐ | Tower 中间件, 类型安全路由 |
| [actix/actix-web](https://github.com/actix/actix-web) | 高性能 Web 框架 | ⭐⭐⭐ | Actor 模型, 零拷贝 |
| [jman0129/tcpproxy](https://github.com/jman0129/tcpproxy) | TCP 代理 | ⭐ | 异步网络, tokio |

**学习路径**: tokio 基础 → reqwest/hyper 理解 HTTP → axum 实战 Web 开发

---

## 命令行与终端

| 项目 | 说明 | 难度 | 核心技术 |
|------|------|------|---------|
| [BurntSushi/ripgrep](https://github.com/BurntSushi/ripgrep) | 极速 grep 替代品 | ⭐⭐⭐ | 正则引擎, SIMD, 内存映射 |
| [sharkdp/fd](https://github.com/sharkdp/fd) | find 的现代替代 | ⭐⭐ | 并行搜索, 正则, 颜色输出 |
| [sharkdp/bat](https://github.com/sharkdp/bat) | cat 的增强版 | ⭐⭐ | 语法高亮, Git 集成, 分页 |
| [dalance/procs](https://github.com/dalance/procs) | ps 的现代替代 | ⭐⭐ | 进程信息, 彩色输出 |
| [cli/cli](https://github.com/cli/cli) | GitHub CLI (gh) | ⭐⭐⭐ | API 客户端, OAuth, 表格渲染 |

**学习路径**: fd → bat → ripgrep (阅读 SIMD 和内存映射代码)

---

## 系统工具

| 项目 | 说明 | 难度 | 核心技术 |
|------|------|------|---------|
| [astral-sh/uv](https://github.com/astral-sh/uv) | 极速 Python 包管理器 | ⭐⭐⭐ | 并行下载, 硬链接, 平台检测 |
| [tailwindlabs/watchman](https://github.com/facebook/watchman) | 文件监控 | ⭐⭐⭐ | inotify/kqueue, 增量更新 |
| [warp-tech/ratatui](https://github.com/ratatui-org/ratatui) | 终端 UI 框架 | ⭐⭐ | 终端渲染, 事件循环, 组件化 |
| [ClementTsang/bottom](https://github.com/ClementTsang/bottom) | 系统监控 (btm) | ⭐⭐ | 实时数据, 跨平台, 鼠标支持 |
| [dalance/procs](https://github.com/dalance/procs) | 进程查看器 | ⭐⭐ | /proc 读取, 信息聚合 |

**学习路径**: bottom 理解跨平台 → ratatui 构建 TUI → watchman 理解文件监控

---

## 数据库与存储

| 项目 | 说明 | 难度 | 核心技术 |
|------|------|------|---------|
| [tikv/tikv](https://github.com/tikv/tikv) | 分布式 KV 存储 | ⭐⭐⭐⭐ | Raft 共识, MVCC, LSM 树 |
| [apache/arrow-datafusion](https://github.com/apache/arrow-datafusion) | SQL 查询引擎 | ⭐⭐⭐ | 列式存储, 查询优化, Parquet |
| [launchbadge/sqlx](https://github.com/launchbadge/sqlx) | 异步 SQL 库 | ⭐⭐ | 编译时 SQL 检查, 连接池 |
| [rusqlite/rusqlite](https://github.com/rusqlite/rusqlite) | SQLite 绑定 | ⭐⭐ | FFI 包装, 零拷贝 |

**学习路径**: sqlx 理解异步数据库 → datafusion 理解查询引擎 → tikv 理解分布式存储

---

## 加密与安全

| 项目 | 说明 | 难度 | 核心技术 |
|------|------|------|---------|
| [RustCrypto/traits](https://github.com/RustCrypto/traits) | 加密原语框架 | ⭐⭐⭐ | trait-based 设计, 常量时间 |
| [dalek-cryptography/curve25519-dalek](https://github.com/dalek-cryptography/curve25519-dalek) | 椭圆曲线实现 | ⭐⭐⭐⭐ | 有限域算术, 椭圆曲线密码学 |
| [RustCrypto/aead](https://github.com/RustCrypto/aead) | AEAD 加密 | ⭐⭐ | AES-GCM, ChaCha20Poly1305 |

---

## 游戏与图形

| 项目 | 说明 | 难度 | 核心技术 |
|------|------|------|---------|
| [bevyengine/bevy](https://github.com/bevyengine/bevy) | ECS 游戏引擎 | ⭐⭐⭐ | ECS 架构, 资源系统, 状态机 |
| [ggez/ggez](https://github.com/ggez/ggez) | 2D 游戏框架 | ⭐⭐ | 粒子系统, 物理, 音频 |
| [gfx-rs/wgpu](https://github.com/gfx-rs/wgpu) | WebGPU 实现 | ⭐⭐⭐⭐ | GPU 抽象, 着色器, 渲染管线 |

**学习路径**: ggez 做 2D 小游戏 → bevy 理解 ECS → wgpu 理解 GPU 编程

---

## 嵌入式与 IoT

| 项目 | 说明 | 难度 | 核心技术 |
|------|------|------|---------|
| [rust-embedded/book](https://github.com/rust-embedded/book) | 嵌入式 Rust 手册 | ⭐⭐ | no_std, 链接脚本, 中断 |
| [esp-rs/esp-hal](https://github.com/esp-rs/esp-hal) | ESP32 HAL | ⭐⭐⭐ | 嵌入式 HAL, 异步嵌入式 |
| [nrf-rs/nrf-hal](https://github.com/nrf-rs/nrf-hal) | Nordic nRF HAL | ⭐⭐ | 低功耗, BLE |

---

## 编译器与语言

| 项目 | 说明 | 难度 | 核心技术 |
|------|------|------|---------|
| [rust-lang/rust](https://github.com/rust-lang/rust) | Rust 编译器本身 | ⭐⭐⭐⭐⭐ | MIR, borrowck, codegen |
| [rust-lang/chalk](https://github.com/rust-lang/chalk) | trait 求解器 | ⭐⭐⭐⭐ | Prolog 风格推导, WF 检查 |
| [rust-analyzer/rust-analyzer](https://github.com/rust-analyzer/rust-analyzer) | IDE 语言服务器 | ⭐⭐⭐⭐ | 增量编译, 语义分析, Salsa |
| [denoland/deno](https://github.com/denoland/deno) | JS/TS 运行时 | ⭐⭐⭐ | V8 绑定, 权限系统, TypeScript |

**学习路径**: rust-analyzer 理解 IDE 集成 → chalk 理解 trait 求解 → rust 编译器源码

---

## 数据科学与 AI

| 项目 | 说明 | 难度 | 核心技术 |
|------|------|------|---------|
| [pola-rs/polars](https://github.com/pola-rs/polars) | DataFrame 库 (比 pandas 快) | ⭐⭐⭐ | 列式存储, SIMD, Apache Arrow |
| [huggingface/tokenizers](https://github.com/huggingface/tokenizers) | BPE 分词器 | ⭐⭐ | 正则分割, BPE 算法, PyO3 |
| [pybind/pyo3](https://github.com/PyO3/pyo3) | Rust ↔ Python 绑定 | ⭐⭐ | FFI, GIL, 编译扩展 |
| [astral-sh/ruff](https://github.com/astral-sh/ruff) | Python linter (比 pylint 快 100x) | ⭐⭐⭐ | AST 解析, 增量编译 |

**学习路径**: tokenizers 理解 PyO3 → polars 理解高性能数据处理 → ruff 理解代码分析

---

## 学习建议

### 阅读源码的方法

```
1. 从 README 和 Cargo.toml 理解项目结构
2. 找到入口点 (main.rs / lib.rs)
3. 追踪核心数据流 (请求 → 处理 → 响应)
4. 理解关键 trait 和抽象
5. 尝试修改并观察行为变化
6. 查看 issue 和 PR 了解设计决策
```

### 推荐学习顺序

```
初级: fd → bat → sqlx
中级: ripgrep → axum → polars
高级: tokio → rust-analyzer → tikv
```

### 贡献开源的步骤

```
1. 从 "good first issue" 标签开始
2. 先写文档修复 (typo, example)
3. 写测试用例
4. 修复简单 bug
5. 实现小功能
6. 参与设计讨论
```
