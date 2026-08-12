# 内核驱动：Rust vs C 对比

## 1. Android Binder 驱动

Binder 是 Android 最重要的 IPC 机制。C 版本约 6000 行（2012 年合入），Rust 版本约 4500 行（2024 年合入 Linux 6.8）。

### C 版本 — 手动引用计数

```c
struct binder_proc { int tmp_ref; struct mutex outer_lock; struct mutex inner_lock; /* ~40字段 */ };

static struct binder_proc *binder_get_proc(struct binder_proc *proc) {
 atomic_inc(&proc->tmp_ref); return proc;
}
static void binder_put_proc(struct binder_proc *proc) {
 if (atomic_dec_and_test(&proc->tmp_ref)) binder_free_proc(proc);
}
```

### C 版本 — goto 错误处理

```c
static long binder_ioctl(struct file *filp, unsigned int cmd, unsigned long arg) {
 proc = binder_get_proc(proc);
 if (!proc) return -ENOMEM;
 thread = binder_get_thread(proc);
 if (!thread) { ret = -ENOMEM; goto err_get_thread; }
 switch (cmd) {
 case BINDER_WRITE_READ:
 if (copy_from_user(&bwr, ubuf, sizeof(bwr))) { ret = -EFAULT; goto err_copy; }
 }
err_write: err_copy: binder_put_thread(thread);
err_get_thread: binder_put_proc(proc); return ret;
}
```

### C 版本已知 CVE

- CVE-2019-2214: UAF — binder 线程释放后仍可通过 epoll 访问
- CVE-2019-2181: TOCTOU — binder_get_proc 和后续使用之间的竞态窗口
- CVE-2020-0041: UAF — binder 节点被并发释放

根本原因：手动引用计数、锁保护范围不明确、复杂并发模式缺乏编译时检查。

### Rust 版本 — Arc 自动管理

```rust
pub struct Process { inner: Mutex<ProcessInner> }
pub struct Thread { inner: Mutex<ThreadInner>, process: Arc<Process> }

impl Process {
 pub fn get_ref(self: &Arc<Self>) -> Arc<Self> { self.clone() }
 pub fn register_thread(self: &Arc<Self>) -> Result<Arc<Thread>> {
 let mut inner = self.inner.lock();
 if inner.threads.len() >= inner.max_threads as usize { return Err(Error::EBUSY); }
 // Arc 保证 Process 在线程存活期间不被释放
 }
}
```

### Rust ioctl — 穷举匹配

```rust
fn ioctl(process: &Arc<Process>, _file: &File, cmd: u32, arg: usize) -> Result<u32> {
 match cmd.try_into() {
 Ok(BinderIoctl::WriteRead) => { /* ... */ Ok(0) }
 Ok(BinderIoctl::SetMaxThreads) => {
 let mut inner = process.inner.lock();
 inner.max_threads = arg as u32;
 Ok(0)
 }
 Err(_) => Err(Error::ENOTTY),
 }
}
```

### 对比总结

| 维度 | C 版本 | Rust 版本 |
|------|--------|----------|
| 代码行数 | ~6000 | ~4500 (-25%) |
| 引用计数 | 手动 atomic_inc/dec | Arc Clone/Drop 自动 |
| 数据保护 | 手动加锁，注释标记 | Mutex 编译时强制 |
| 错误处理 | goto 标签，易遗漏 | ? 运算符，类型安全 |
| UAF 防御 | 开发者纪律 | 所有权系统编译时 |
| 已知 CVE | 多个 UAF/竞态 | 零内存安全 CVE |

参阅 [[../系统内核/06_并发与同步|并发与同步（C视角）]] 理解锁机制对比。

## 2. NVMe 驱动

### DMA 操作

C 版本：
```c
struct nvme_queue {
 struct nvme_command *sq_cmds; // 提交队列 (DMA)
 dma_addr_t sq_dma_addr; // 提交队列物理地址
 // dma_alloc_coherent 分配，手动 dma_free_coherent 释放
 // 释放后仍可通过其他指针访问 → UAF
};
```

Rust 版本：
```rust
struct NvmeQueue {
 sq: DmaAlloc<NvmeCommand>, // Drop 自动释放，类型安全
 cq: DmaAlloc<NvmeCompletion>,
 state: Mutex<QueueState>,
 _irq: IrqHandler<Self>, // Drop 自动释放中断
}
// Drop 自动调用 dma_free_coherent + free_irq
// 顺序由编译器保证，不会出现错误清理顺序
```

### 中断处理

C：`request_irq` 注册，`free_irq` 必须在设备移除时正确调用。中断可能在队列释放后触发。
Rust：`IrqHandler` 的 Drop 自动同步并释放。借用检查防止释放后使用队列数据。

## 3. 简单平台驱动

### C 版本

```c
static ssize_t my_read(struct file *filp, char __user *buf, size_t count, loff_t *off) {
 struct my_device *dev = filp->private_data;
 u32 val = ioread32(dev->regs + *off); // 无边界检查！
 copy_to_user(buf, &val, sizeof(val));
}
```

问题：`ioread32(regs + *off)` 无边界检查，用户可读取任意物理地址。`filp->private_data` 是 `void*`，无类型安全。

### Rust 版本

```rust
fn read(dev: &MyDevice, _file: &File, writer: &mut impl IoBufferWriter, offset: u64) -> Result<usize> {
 let offset = usize::try_from(offset).map_err(|_| Error::ERANGE)?;
 let val = dev.regs.read32(offset)?; // 自动边界检查
 writer.write_slice(&val.to_le_bytes())?;
 Ok(4)
}
```

`usize::try_from(offset)` 防止大偏量；`regs.read32(offset)?` 运行时边界检查。

## 4. 编译时保证对比

| 安全属性 | C 编译时 | C 运行时 | Rust 编译时 |
|---------|---------|---------|------------|
| 空指针检查 | 无 | oops | Option/NonNull |
| 缓冲区溢出 | 无 | 可能有 | 切片边界 |
| UAF | 无 | 无 | 借用检查器 |
| 数据竞争 | 无 | lockdep | Send/Sync |
| 忘记释放锁 | 无 | lockdep | Guard Drop |
| 类型混淆 | 无 | 无 | 类型系统 |
| 未初始化内存 | 无 | 可能有 | 类型系统强制 |

## 5. 性能数据

| 基准测试 | C Binder | Rust Binder | 差异 |
|----------|----------|------------|------|
| IPC 吞吐量（单线程） | 基准 | ~99.5% | 几乎无差异 |
| IPC 吞吐量（16线程） | 基准 | ~101% | 轻微改善 |
| 延迟 P50 | 基准 | ~100% | 无差异 |
| 内存占用 | 基准 | ~95% | 减少 5% |

Rust 抽象层没有可测量的性能开销。LLVM 对 Rust 生成的 IR 进行与 C 代码相同的优化。

## 6. C 和 Rust 共存

```makefile
# 模块同时使用 C 和 Rust
obj-m := hybrid_module.o
hybrid_module-y := c_part.o rust_part.o
```

```c
// c_part.c — C 侧导出外部符号
extern int rust_function(int x);
EXPORT_SYMBOL_GPL(rust_function);
```

```rust
// rust_part.rs
#[no_mangle]
pub extern "C" fn rust_function(x: i32) -> i32 { x + 1 }
```

## 7. 迁移策略

内核社区共识：**不重写现有 C 驱动**（除非有特殊安全需求如 Binder）。
- 新驱动用 Rust 编写
- 安全关键组件优先考虑 Rust 重写
- C 和 Rust 可在同一模块共存
- 选择语言综合考虑安全需求、团队技能、架构支持

### 决策框架

| 场景 | 推荐 | 理由 |
|------|------|------|
| 安全关键驱动，处理不受信任输入 | Rust | 所有权系统消除 UAF |
| 并发密集驱动，复杂中断处理 | Rust | Send/Sync 编译时检查 |
| 新硬件驱动 | Rust | 无历史 C 代码负担 |
| 现有稳定 C 驱动 | C | 维护成本低于重写 |
| 需要支持 unsupported 架构 | C | Rust toolchain 未就绪 |
| 极度性能敏感热路径 | C/Rust unsafe | 手写 SIMD/汇编 |
| 大量依赖 C 基础设施 | C+Rust 混合 | 渐进迁移 |

### Rust unsafe 按需使用模式

在性能关键路径中，可局部使用 unsafe 绕过安全检查：

```rust
// 安全版本（有边界检查开销）
let val = data.get(index).ok_or(Error::ERANGE)?;

// 热路径 unsafe 版本（需证明 index 已通过验证）
// SAFETY: index was validated against data.len() in caller
unsafe { data.get_unchecked(index) }
```

这种模式使得 95% 的安全代码 + 5% 的 unsafe 热路径优化成为可行策略——比 100% 不安全的 C 代码有本质安全性提升。
