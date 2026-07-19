# Rust 内核支持概述

> 前置：[[../../rust/rust目录|Rust 教程总目录]] | [[../../rust/2深入/09-Unsafe-Rust的计算机科学边界|Unsafe Rust 边界]]

## 1. 内存安全的困境

Linux 内核是世界上最庞大的 C 语言代码库之一，超过 3000 万行代码。根据 Google 和 Microsoft 的数据，约 70% 的高危安全漏洞是内存安全问题——use-after-free、缓冲区溢出、空指针解引用。内核中的这类漏洞尤其危险，通常导致权限提升、信息泄露或内核崩溃。

> 参阅 [[../系统内核/01_C语言与操作系统|C语言与操作系统]] 和 [[../系统内核/07_Linux内核源码导读|Linux内核源码导读]]。

## 2. Linux 6.1：Rust 进入主线

关键时间线：
- **2020 年 7 月**：Nick Desaulniers 在 Linux Plumbers Conference 讨论内核中的 Rust
- **2021 年 4 月**：Miguel Ojeda 发送"Rust for Linux"RFC 补丁系列
- **2022 年 9 月**：Linus 在内核维护者峰会上表示接受 Rust
- **Linux 6.1（2022 年 12 月）**：Rust 基础设施正式合并入主线

合并的内容包括：
- `rust/Makefile` — 内核构建系统对 Rust 的集成
- `rust/kernel/` — Rust 内核抽象层
- `rust/bindings/` — 自动生成的 C FFI 绑定
- `rust/macros/` — 过程宏（如 `module!`）
- `rust/alloc/` — 为内核定制的 alloc crate 分支

## 3. 当前内核中已有的 Rust 代码

### 内核 Rust 抽象层 (`rust/kernel/`)

| 模块 | 封装的 C API | 功能 |
|------|-------------|------|
| `sync::Arc` | `struct kref` | 内核引用计数智能指针 |
| `sync::Lock` | `spinlock_t` / `mutex` | 内核同步原语 |
| `error::Error` | `errno.h` 错误码 | 内核错误处理 |
| `str::CStr` | `char *` 字符串 | 安全的 C 字符串处理 |
| `file::File` | `struct file *` | 文件描述符操作 |
| `task::Task` | `struct task_struct *` | 进程/线程抽象 |

### Android Binder 驱动

Samsung 工程师用 Rust 重写了 Android Binder 驱动（Linux 6.8 合入）：
- C 版本约 6,000 行，Rust 版本约 4,500 行（减少约 25%）
- 消除了至少 3 类已知的 UAF 漏洞模式
- 性能持平，某些场景优于 C 版本

### Asahi Linux GPU 驱动

为 Apple Silicon（M1/M2/M3）芯片开发的开源 GPU 驱动，内核部分大量使用 Rust。驱动代码位于 `drivers/gpu/drm/asahi/`。

### NVMe 驱动

Rust NVMe 驱动正开发中，展示 Rust 如何处理 DMA 操作、中断处理、设备内存映射（MMIO）和复杂硬件状态机。

## 4. 内核构建系统集成

内核 Kbuild 系统通过顶层 Makefile 检测 Rust 工具链：

```makefile
# 顶层 Makefile（简化）
has_rust := $(shell rustc --version 2>/dev/null)
ifdef has_rust
  core-y += rust/
endif
```

`rust/Makefile` 负责：
1. 检查 Rust 编译器版本
2. 检查 bindgen 工具可用性
3. 编译 Rust 代码为 .o 对象文件
4. 链接到 vmlinux

关键编译标志：
```makefile
# rust/Makefile
RUSTC_FLAGS := --edition 2021 --crate-type rlib \
    -C opt-level=2 -C panic=abort -C no-redzone=y \
    -C code-model=kernel -C relocation-model=static --emit=obj
```

注意：`panic=abort`（内核中不能 unwind），`no-redzone=y`（内核栈没有 red zone），`code-model=kernel`（负地址偏移）。

Kconfig 配置：
```
CONFIG_RUST=y               # 启用 Rust 支持
CONFIG_RUST_IS_AVAILABLE=y   # 工具链就绪（自动设置）
CONFIG_SAMPLE_RUST_MINIMAL=y # 最小示例模块
CONFIG_SAMPLE_RUST_PRINT=y   # 打印示例
CONFIG_SAMPLE_RUST_HOSTPROGS=y # 主机 Rust 程序
```

## 5. 内核 crate 结构

```
rust/
├── Makefile          — Rust 构建规则
├── kernel/           — 内核抽象层（lib.rs entry, prelude, alloc, sync, error, str, types, init, file, task, print, io_buffer）
│   ├── alloc/        — Kmalloc/GFP 分配器
│   └── sync/         — Arc, Lock, CondVar
├── macros/           — module! 过程宏
├── bindings/         — bindgen 自动生成的 FFI
└── alloc/            — alloc crate 分支
```

`kernel` crate 入口点：
```rust
#![no_std]
extern crate alloc;
pub mod error; pub mod prelude; pub mod print;
pub mod str; pub mod sync; pub mod types;
pub mod init; pub mod file; pub mod task;
```

## 6. 内核 Rust 代码推荐阅读顺序

1. `samples/rust/rust_minimal.rs` — 最小内核模块（~20行）
2. `samples/rust/rust_print.rs` — 内核打印宏
3. `rust/kernel/prelude.rs` — 便利导入项
4. `rust/kernel/error.rs` — 内核错误处理模型
5. `rust/kernel/sync/arc.rs` — 内核引用计数
6. `rust/kernel/print.rs` — 内核日志系统

### 在线浏览

- GitHub mirror：`https://github.com/Rust-for-Linux/linux`（最新开发分支）
- kernel.org：`https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git`
- elixir.bootlin.com：代码交叉引用，支持 Rust 符号搜索

## 7. 内核 Rust 哲学

"安全封装不安全操作"：用 Rust 的安全类型系统封装不安全的 C API。驱动开发者使用安全 API，`kernel` crate 内部通过 unsafe FFI 调用 C 内核 API。

零成本抽象示例：
- `Arc<T>` 对 `struct kref` 的封装不增加额外间接层
- `Lock<T>` 编译后与原始 `spin_lock()`/`mutex_lock()` 等效
- `Error` 类型编译为与 C `errno` 相同的整数表示

渐进式采用：新驱动用 Rust，现有 C 驱动保持不变，安全关键部分优先迁移。

## 8. 与用户态 Rust 的关键差异

| 特性 | 用户态 Rust | 内核 Rust |
|------|-----------|----------|
| 标准库 | `std` | `#![no_std]` |
| 内存分配 | `std::alloc` | `kernel::alloc` + GFP flags |
| 线程 | `std::thread` | 内核线程（kthread） |
| 同步 | `std::sync` | `kernel::sync`（基于内核原语） |
| Panic | Unwind + catch | Abort（不能 unwind） |
| 栈大小 | 可扩展 | 固定（8KB/16KB） |
| 浮点/SIMD | 可用 | 内核中禁用（默认） |

## 9. 工具链要求

内核使用最新 Rust 编译器（通常 nightly）获取必需特性：`new_uninit`、`allocator_api`、`pin_macro`、`arbitrary_self_types`、`coerce_unsized` 等。

```bash
# 内核内置检测脚本
make LLVM=1 rustavailable
# 成功输出：Rust is available!
```

## 10. 社区资源

- 邮件列表：`rust-for-linux@vger.kernel.org`
- 主仓库：`https://github.com/Rust-for-Linux/linux`
- Zulip：`rust-for-linux.zulipchat.com`
- 邮件存档：`lore.kernel.org/rust-for-linux/`
