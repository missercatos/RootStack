# 内核 Rust 未来展望

## 1. 现状（2025）

Rust 自 Linux 6.1（2022.12）进入主线后已取得显著进展：

- **基础设施**：稳健的 kernel crate，覆盖同步、内存分配、错误处理、文件操作、任务管理
- **首个重要驱动**：Android Binder（4500行，Linux 6.8）
- **GPU 驱动**：Asahi Linux Apple Silicon GPU 驱动大量使用 Rust
- **网络抽象**：`rust/kernel/net.rs` 封装 socket（自 Linux 6.9）
- **架构支持**：x86_64、aarch64（完善）；riscv64、loongarch（初步）
- **工具链**：GCC Rust (gccrs) 开发中，rustc_codegen_gcc 推进中

## 2. 即将采用 Rust 的子系统

### 网络子系统

- `rust/kernel/net.rs`：封装 `struct socket` 和相关操作
- UDP/TCP 抽象，允许 Rust 驱动创建网络套接字
- 挑战：SKB 生命周期、NAPI 轮询、零拷贝（XDP/AF_XDP）

### 文件系统

- **tarfs**：Wedson Almeida Filho 概念验证的只读文件系统（证明可行性）
- **bcachefs**：与 Kent Overstreet 讨论部分用 Rust 编写
- **puzzlefs**：下一代容器文件系统（用户态 Rust）
- 文件系统是数据完整性关键领域，安全攻击主要入口

### GPU 驱动（DRM）

- Asahi Linux 已在用 Rust 和内核 DRM Rust 抽象
- Nova 驱动（较新 NVIDIA GPU 的 Rust DRM 驱动）开发中
- `rust/kernel/drm/` 提供 GEM 缓冲区管理、DRM 设备注册、IOCtl 分发

### 其他子系统潜力评估

| 子系统 | 潜力 | 原因 |
|--------|------|------|
| USB | 中 | 复杂设备状态机，安全性重要 |
| NVMe | 高 | 已有 Rust 原型 |
| 输入（Input） | 高 | HID 解析器安全性重要 |
| 加密（Crypto） | 高 | 常量时间操作，安全性关键 |
| BPF | 中 | 验证器和 JIT 可从 Rust 受益 |
| KVM | 低 | 与硬件深度绑定 |

## 3. 技术挑战

### alloc 在内核上下文中

内核环境限制：
- 没有操作系统提供内存 — 需要自定义分配器
- GFP 标志控制分配行为 — 标准 alloc API 不支持
- `krealloc` 语义与 `realloc` 不完全相同
- 集合类型增长策略需适配内存压力

长期方案：可能实现内核专用 collections crate，或扩展 upstream alloc 使其更灵活。

### LKMM vs Rust 内存模型

- LKMM 使用 READ_ONCE/WRITE_ONCE 宏，Rust 使用 Atomic* + Ordering
- RCU 依赖"地址依赖排序"（类似 Ordering::Consume），Rust 中几乎未使用
- 内核 Rust sync 模块封装内核原子操作，Arc 基于 kref 而非 Rust 标准库 Arc

### 架构支持

| 架构 | 状态 | 瓶颈 |
|------|------|------|
| x86_64 | 完善 | — |
| aarch64 | 完善 | — |
| riscv64 | 初步 | rustc 支持，内核适配中 |
| loongarch | 初步 | 中国龙芯架构 |
| arm (32-bit) | 部分 | LLVM 支持限制 |
| ppc64le | 实验 | 有 LLVM 支持 |
| m68k/alpha | 无计划 | LLVM 不支持，需 GCC Rust |

### nightly 特性依赖

内核依赖约 20 个 nightly 特性（`allocator_api`、`new_uninit`、`pin_macro`、`arbitrary_self_types` 等）。内核团队与 Rust 语言团队合作推进稳定化。

已稳定化进展：`new_uninit`（1.75）、`offset_of`（1.77）。优先目标：`allocator_api` > `arbitrary_self_types` > `pin_macro` > `dispatch_from_dyn`。

长期目标：减少 nightly 特性依赖到 <5 个，最终在特定条件下可能使用 stable rustc。

### 代码大小与二进制体积

Rust 编译器的代码生成在某些场景下比 Clang 产生更大的二进制文件。差异通常在 5% 以内。通过调整 `opt-level` 和 `codegen-units` 可控制。内核团队监控 vmlinux 大小以确保 Rust 代码不会不合理地膨胀内核二进制。

## 4. 社区挑战

### C 内核开发者学习 Rust

最大的社区挑战。多数内核维护者有数十年 C 经验，Rust 所有权和借用需要"重新学习编程"。

帮助方案：完善 Documentation/rust/；Linux Foundation 提供培训；Rust 开发者与 C 维护者结对编程；从阅读 Rust 抽象开始再写代码。

### 代码审查容量

需同时理解 Rust 和内核子系统。当前具备双向能力者约 8-12 人。

扩展策略：培训现有 C 维护者（Greg KH 已开始审查 Rust 补丁）；自动化辅助（clippy、静态分析）；鼓励影子审查。

### 避免 Rust vs C 争论

- 强调 Rust 是**补充**而非**替代**C
- 用数据说话：CVE 统计、性能基准
- 尊重 C 维护者的经验
- Rust 代码达到与 C 代码同等质量标准
- 从无争议领域开始（新驱动），不在敏感子系统强行推进

## 5. 时间线预测

```
2025-2026: Rust Binder 稳定；首个 Rust 网络驱动；DRM 抽象成熟；allocator_api 稳定化
2026-2027: 更多生产环境 Rust 驱动（NVMe、input）；首个 Rust 文件系统（只读）；GCC Rust 可用
2027-2028: Rust 成为新驱动的事实标准；首个可写 Rust 文件系统；nightly 特性依赖 <5 个
2028-2030: 首个广泛使用内存安全语言的通用 OS 内核；可测量的内核 CVE 下降；Rust 在 5+ 主要子系统中使用
```

## 6. 更广阔视角

内存安全语言在系统编程中的兴起是不可逆趋势：
- 约 70% 的严重安全漏洞是内存安全问题
- 每个 CVE 修复成本估计 $50k-$100k
- CISA "Secure by Design"、EU Cyber Resilience Act 推动法规要求
- Google、Microsoft 公开承诺在新系统软件中使用内存安全语言

### 内核之外的 Rust 系统编程

| 领域 | 项目 | 状态 |
|------|------|------|
| OS 内核 | Windows（GDI 字体解析） | 内部使用 |
| Hypervisor | Cloud Hypervisor（AWS Nitro） | 生产 |
| Init 系统 | systemd | 讨论中 |
| 安全工具 | sudo-rs | 替代品可用 |
| 引导加载器 | oreboot（coreboot 替代） | 开发中 |
| 微控制器 | RTIC、embassy（ARM Cortex-M） | 广泛使用 |

### 为什么这个趋势不可逆

1. **经济驱动**：内存安全漏洞年度直接损失估计数十亿美元
2. **监管驱动**：法规开始要求"设计安全"(Secure by Design)
3. **人力驱动**：新一代系统程序员更倾向 Rust
4. **技术驱动**：Rust 已证明零成本抽象在生产内核中可行

Linux 内核是系统编程世界的"北极星"，其技术选择影响整个行业。如果 Linux 内核成功采纳 Rust，其他 OS 项目将跟随。

### vs 形式化验证（seL4）

seL4 使用形式化方法证明 C 代码的正确性（高成本，低覆盖面）。Rust 使用编译时类型检查（低成本，覆盖面广）。两者互补：
- Rust 提供"日常安全"：所有代码路径的类型安全
- 形式化验证提供"极端安全"：关键安全属性的数学证明

## 7. 如何成为这个历史转变的一部分

```bash
# 今天就做：
git clone https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
cd linux && make LLVM=1 defconfig && make LLVM=1 -j$(nproc)
cat samples/rust/rust_minimal.rs
make LLVM=1 rustavailable

# 本周：
# 订阅 rust-for-linux@vger.kernel.org
# 阅读 Documentation/rust/quick-start.rst

# 本月：
# 编写你的第一个 Rust 内核模块，在 QEMU 中测试
# 找到第一个文档修复并提交补丁
```

关键技能组合：内核内部知识（MM、调度器、中断、锁）+ 系统编程基础（指针布局、并发、I/O模型）+ 工具和流程（QEMU、ftrace、KASAN）。

今天学习内核 Rust 的人将成为明天最重要的系统开发者。
