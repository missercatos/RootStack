
# C 与 Rust 的内核新时代

> 从 C 的三十年统治到 Rust 的编译期安全革命——内存安全不再是运行时负担。

## C 语言的历史统治

C 语言自诞生以来一直是操作系统内核的"默认语言"。Linux 内核 (3000 万行 C), Windows NT 内核, FreeBSD, XNU (macOS/iOS 内核), 以及数以亿计的嵌入式系统, 全部以 C 为主实现——这不是偶然的。

## C 的内核优势

| 特性 | 意义 |
|------|------|
| 零成本抽象 | 没有 GC, 没有虚表, 没有对象头——代码直接映射为 CPU 指令 |
| 直接硬件访问 | 指针直接操作物理地址, volatile 强制内存访问, 内联汇编嵌入 |
| 可预测内存布局 | struct 字段排列由程序员控制, sizeof 精确可知, 缓存行可规划 |
| 无运行时 | 不需要 JVM, 不需要 GC 线程, 不需要 JIT 编译预热 |
| FFI 通用语言 | C ABI 是所有语言互操作的标准——Rust, Python, Java, Go 都提供 C FFI |

## 内存安全危机

尽管如此, C 的手动内存管理是把双刃剑。微软和 Google 的安全数据给出了触目惊心的结论:

- 约 **70% 的 CVE (安全漏洞)** 根因是内存安全问题
- 典型漏洞类型: 缓冲区溢出 (buffer overflow), 使用后释放 (use-after-free), 两次释放 (double free), 空指针解引用
- 这些问题在 C 中无法由编译器检测——所有责任落在程序员身上
- 静态分析工具 (Coverity, CodeQL) 和动态工具 (Valgrind, ASan) 只能事后检测

```
// C 中内存安全的典型失败模式
char buffer[64];
strcpy(buffer, user_input); // 如果 user_input > 63 字节 → 栈溢出

int *ptr = malloc(sizeof(int));
free(ptr);
*ptr = 42; // use-after-free: 未定义行为

int *a = malloc(100);
free(a);
free(a); // double free: 破坏 malloc 内部数据结构
```

## Rust 的编译期安全

Rust 在 2015 年发布 1.0 版本, 提出了一个全新方案: **所有权 (Ownership) + 借用 (Borrowing) + 生命周期 (Lifetimes)** 系统。这三者在编译期进行深度的静态分析, 从根源上阻止了内存安全问题——不需要 GC, 不需要引用计数 (除非显式用 Rc/Arc)。

```
// Rust 等价代码 → 编译期阻止所有上述漏洞

// 栈溢出: Rust 的 str 操作使用切片, 编译期检查长度或运行时 panic (安全)
let mut buffer = vec![0u8; 64];
// buffer.copy_from_slice(&user_input); // 长度不匹配 → 编译错

// use-after-free: 编译器拒绝编译
let ptr = Box::new(42);
// let x = *ptr; // 如果 ptr 已被 move, 编译器拒绝编译

// double free: Box 的 Drop 只调用一次, 编译器保证
```

## Rust 在内核中的应用

2022 年 12 月 Linux 6.1 正式合入 Rust 语言支持, 标志着 Rust 进入内核领域:

```
mermaid
graph TD
 subgraph "Linux 内核架构"
 CORE["稳定核心 (C)<br/>进程调度, 内存管理, VFS, 网络栈"]
 RUST["新子系统 (Rust)<br/>Rust-for-Linux 项目"]
 FFI["C ABI 接口层<br/>bindgen / cbindgen"]
 end

 CORE <--> |"FFI 调用"| RUST
 DRIVER1["NVMe 驱动 (Rust)"] --> RUST
 DRIVER2["GPU DRM 驱动 (Asahi Linux)"] --> RUST
 DRIVER3["Android Binder 驱动"] --> RUST
 FS["新文件系统"] --> RUST

 style CORE fill:#369,stroke:#333,color:#fff
 style RUST fill:#963,stroke:#333,color:#fff
 style FFI fill:#696,stroke:#333,color:#fff
```

关键里程碑:
- **Asahi Linux** (Apple Silicon): GPU 驱动部分用 Rust 编写, 在实生产环境中验证了 Rust 内核代码的可行性
- **Android**: 正在将 Binder 驱动用 Rust 重写, 减少 Android 内核中最高风险的攻击面
- **Windows 内核**: 微软也在探索用 Rust 编写新的 Windows 内核组件

## 新范式: C AND Rust, 不是 C OR Rust

未来的内核是**混合架构**:

| 场景 | 推荐语言 | 原因 |
|------|---------|------|
| 核心调度器、内存管理、网络栈 | C | 成熟稳定, 30 年验证, 无必要重写 |
| 新设备驱动 | Rust | 大量 CVEs 来自驱动代码, Rust 从源头消除 |
| 文件系统 | Rust | 复杂状态管理, Rust 的类型系统帮助消除逻辑错误 |
| 安全敏感模块 (TPM, 加密) | Rust | 内存安全 + 无 GC + 编译期保证 |
| 内核模块/插件 | Rust | 加载不可信代码, Rust 提供更强的隔离保证 |
| 用户态工具 (eBPF, perf, 审计) | Rust | 开发效率高, 安全性要求高 |

## FFI: C ABI 作为通用接口

```
C ABI 是操作系统和语言互操作的"通用语言":

 C 侧 (内核核心):
 extern "C" void register_rust_driver(void *ops);

 Rust 侧 (新驱动):
 use std::ffi::c_void;

 extern "C" fn my_driver_init() -> *mut c_void {
 // 驱动初始化逻辑
 Box::into_raw(Box::new(MyDriver::new())) as *mut c_void
 }

 // bindgen: 从 C 头文件自动生成 Rust FFI 绑定
 // cbindgen: 从 Rust 定义自动生成 C 头文件
```

关键: C ABI 作为桥接层, C 和 Rust 之间不需要复杂的序列化——它们在内存布局层面直接互通。

## 未来展望

1. **短期 (2-3 年)**: 更多 Linux 子系统的 Rust 驱动合入, 驱动质量提升
2. **中期 (3-5 年)**: Rust 内核框架成熟 (kernel crate), 新文件系统和网络模块用 Rust
3. **长期 (5-10 年)**: 混合内核哲学被验证——C 核心稳定 + Rust 生态扩展, 可能部分核心模块渐进式迁移

C 不是 "遗留代码", Rust 也不是 "替代品"——它们在同一内核中共存, 各自发挥优势。C 提供了底层控制和无约束的灵活性, Rust 在 C 的基础上添加了编译期的安全保证。这代表了系统编程的**新范式**: 不是放弃控制, 而是让编译器帮助你管理复杂性。

---

## Rust 内核模块

- [[Rust内核/01-Rust内核支持概述|Rust 内核支持概述]]
- [[Rust内核/02-内核Rust抽象层|内核 Rust 抽象层]]
- [[Rust内核/03-内核模块开发实战|内核模块开发实战]]
- [[Rust内核/04-内核驱动Rust对比C|内核驱动: Rust vs C 对比]]
- [[Rust内核/05-参与内核Rust开发|参与内核 Rust 开发]]
- [[Rust内核/06-内核Rust未来展望|内核 Rust 未来展望]]

