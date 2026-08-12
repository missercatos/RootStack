# 内核 Rust 抽象层

## 1. 为什么需要抽象层

内核 Rust 不能直接调用 C 内核函数：
1. **类型安全**：C API 大量使用原始指针（`*mut T`），直接使用失去 Rust 安全保证
2. **所有权模型**：C 没有所有权概念，内核对象生命周期依赖隐式约定
3. **错误处理**：C 使用整数错误码（-EINVAL），Rust 使用 `Result<T, Error>`
4. **并发模型**：内核锁和同步原语需要与 Rust 的 Send/Sync 集成
5. **内存分配**：内核使用 `kmalloc(GFP_KERNEL)`，需要适配 alloc crate

设计目标：零成本、安全 API 暴露、符合内核风格。

参阅 [[../系统内核/06_并发与同步|并发与同步（C视角）]] 理解 Rust 抽象层背后的 C 内核模式。

## 2. 关键抽象详解

### 2.1 bindings — 自动生成的 FFI 绑定

由 `bindgen` 从 C 头文件自动生成。内核使用 `bindings_helper.h`：

```c
// rust/bindings/bindings_helper.h
#include <linux/kernel.h>
#include <linux/slab.h>
#include <linux/errno.h>
#include <linux/mutex.h>
#include <linux/spinlock.h>
#include <linux/kref.h>
#include <linux/file.h>
// ...
```

生成的 Rust 代码（全部 unsafe）：
```rust
pub mod bindings_raw {
 pub type gfp_t = core::ffi::c_uint;
 pub const GFP_KERNEL: gfp_t = 0xcc0;
 pub const EINVAL: i32 = 22;
 #[repr(C)] pub struct kref { pub refcount: atomic_t, }
 extern "C" {
 pub fn kref_init(kref: *mut kref);
 pub fn kref_get(kref: *mut kref);
 pub fn kmalloc(size: usize, flags: gfp_t) -> *mut c_void;
 pub fn kfree(ptr: *const c_void);
 pub fn mutex_lock(lock: *mut mutex);
 pub fn mutex_unlock(lock: *mut mutex);
 }
}
```

驱动开发者**不直接**使用 bindings_raw，而是使用 `kernel::` 中的安全封装。

### 2.2 sync::Arc — 内核引用计数

封装 `struct kref`，内核中最广泛使用的抽象。

```rust
pub struct Arc<T: ?Sized> { ptr: NonNull<ArcInner<T>> }

#[repr(C)]
struct ArcInner<T: ?Sized> {
 refcount: bindings::kref,
 data: T,
}

impl<T> Arc<T> {
 pub fn new(contents: T, flags: Flags) -> Result<Self> { /* 分配 + kref_init */ }
}

impl<T: ?Sized> Clone for Arc<T> {
 fn clone(&self) -> Self {
 unsafe { bindings::kref_get(&(*self.ptr.as_ptr()).refcount) };
 Self { ptr: self.ptr }
 }
}

impl<T: ?Sized> Drop for Arc<T> {
 fn drop(&mut self) {
 unsafe { bindings::kref_put(&mut (*self.ptr.as_ptr()).refcount, Some(dec_ref_and_free::<T>)); }
 }
}
```

关键特性：Clone 自动 inc ref，Drop 自动 dec ref；线程安全通过 Send/Sync 编译时检查。

### 2.3 sync::Lock — 内核同步

封装自旋锁和互斥锁，锁与受保护数据绑定。

```rust
pub struct Lock<T: ?Sized, B: Backend> {
 pub(crate) state: B::State,
 pub(crate) data: UnsafeCell<T>,
}

pub trait Backend {
 type State; type GuardState;
 unsafe fn lock(ptr: *const Self::State) -> Self::GuardState;
 unsafe fn unlock(ptr: *const Self::State, guard_state: &Self::GuardState);
}

impl<T: ?Sized, B: Backend> Lock<T, B> {
 pub fn lock(&self) -> Guard<'_, T, B> { /* ... */ }
}

impl<T: ?Sized, B: Backend> Drop for Guard<'_, T, B> {
 fn drop(&mut self) { unsafe { B::unlock(self.lock.state.get(), &self.state) }; }
}
```

具体锁类型：
```rust
pub type Mutex<T> = Lock<T, MutexBackend>; // struct mutex
pub type SpinLock<T> = Lock<T, SpinLockBackend>; // raw_spinlock_t
```

安全性：编译器强制通过 `lock()` 获取 Guard 才能访问数据；Guard 的 Drop 自动释放锁；`Sync` trait 确保线程间共享的正确性。

### 2.4 error::Error — 内核错误处理

```rust
#[derive(Clone, Copy, PartialEq, Eq)]
pub struct Error(core::ffi::c_int); // 编译后等于 i32

impl Error {
 pub fn from_kernel_errno(errno: core::ffi::c_int) -> Error { Error(-errno) }
 pub fn to_kernel_errno(self) -> core::ffi::c_int { self.0 }
 pub fn to_errno(self) -> core::ffi::c_int { -self.0 }

 pub const EINVAL: Error = Error(-(bindings::EINVAL as i32));
 pub const ENOMEM: Error = Error(-(bindings::ENOMEM as i32));
 pub const ENODEV: Error = Error(-(bindings::ENODEV as i32));
 // ... 更多常量
}

pub type Result<T = ()> = core::result::Result<T, Error>;
```

零成本：编译后等于 i32，一个寄存器大小。`?` 运算符自动传播错误。C互操作通过 `.to_kernel_errno()` 转为 C 函数返回值。

### 2.5 str::CStr — 内核 C 字符串

```rust
pub struct CStr<'a>(&'a CoreCStr);

impl<'a> CStr<'a> {
 pub fn from_bytes_with_nul(bytes: &'a [u8]) -> Result<Self> { /* ... */ }
 pub unsafe fn from_ptr<'b>(ptr: *const u8) -> &'b Self {
 let core_ref = unsafe { CoreCStr::from_ptr(ptr as *const i8) };
 unsafe { &*(core_ref as *const CoreCStr as *const CStr) }
 }
 pub fn as_bytes(&self) -> &[u8] { self.0.to_bytes() }
 pub fn to_str(&self) -> Result<&str> { self.0.to_str().map_err(|_| Error::EINVAL) }
}
```

### 2.6 types::ForeignOwnable — 外部所有权

用于 Rust 对象被 C 代码拥有的场景（如 file->private_data）。

```rust
pub unsafe trait ForeignOwnable: Sized {
 fn into_foreign(self) -> *const core::ffi::c_void;
 unsafe fn from_foreign(ptr: *const core::ffi::c_void) -> Self;
 unsafe fn borrow<'a>(ptr: *const core::ffi::c_void) -> &'a Self;
}

// 对 Arc<T> 的实现
unsafe impl<T: Send + Sync + 'static> ForeignOwnable for Arc<T> { /* ... */ }
// 对 Box<T> 的实现
unsafe impl<T: 'static> ForeignOwnable for Box<T> { /* ... */ }
```

### 2.7 init::InPlaceInit — 内核对象初始化

```rust
pub trait InPlaceInit<T>: Sized {
 fn init(self, init: impl PinInit<T, Error>) -> Result<Pin<Self>>;
}
```

使用 `pin_init!` 宏在已分配的内存上直接构造对象，保证初始化完成前 Drop 不会被调用。

### 2.8 file::FileOperations — 文件操作

```rust
pub trait FileOperations: Sized {
 type Data: ForeignOwnable + Send + Sync;
 type OpenData: Sync;
 fn open(context: &Self::OpenData, file: &File) -> Result<Self::Data>;
 fn read(data: ..., file: &File, writer: &mut impl IoBufferWriter, offset: u64) -> Result<usize>;
 fn write(data: ..., file: &File, reader: &mut impl IoBufferReader, offset: u64) -> Result<usize>;
 fn ioctl(data: ..., file: &File, cmd: u32, arg: usize) -> Result<u32>;
 fn release(data: Self::Data, file: &File);
}
```

替代 C 的 `struct file_operations`，通过 trait 提供类型安全的操作集合。

## 3. 内存分配模型

内核适配的 alloc crate 通过自定义 `#[global_allocator]` 将分配转发到 kmalloc/kfree：

```rust
struct KernelAllocator;
unsafe impl GlobalAlloc for KernelAllocator {
 unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
 let size = layout.size();
 let ptr = if size > PAGE_SIZE {
 unsafe { bindings::kvmalloc(size, bindings::GFP_KERNEL) }
 } else {
 unsafe { bindings::kmalloc(size, bindings::GFP_KERNEL) }
 };
 ptr as *mut u8
 }
 unsafe fn dealloc(&self, ptr: *mut u8, layout: Layout) {
 if layout.size() > PAGE_SIZE {
 unsafe { bindings::kvfree(ptr as *const c_void) };
 } else {
 unsafe { bindings::kfree(ptr as *const c_void) };
 }
 }
}
```

GFP 标志：`GFP_KERNEL`（进程上下文）、`GFP_ATOMIC`（中断上下文）、`GFP_NOFS`（文件系统路径）等。

## 4. C vs Rust 并排比较

### 错误处理

C：手动检查 + goto 清理，编译时无强制。
Rust：`?` 运算符自动传播，编译器警告未使用的结果，Drop 自动清理。

### 并发安全

C：`sc->count++` 无锁访问编译通过，运行时竞态。
Rust：`Lock<T>` 强制通过 `lock()` 获取 Guard 访问数据，无锁访问编译失败。

### 资源清理

C：多个 goto 标签，每个新增分配需要修改所有错误路径。
Rust：`?` 出错自动返回，Drop 自动释放所有已分配资源。

## 5. 编译时保证总结

| 安全性保证 | C 内核 | Rust 内核 |
|-----------|--------|----------|
| 空指针检查 | 编译时无 | Option/NonNull 强制 |
| 缓冲区溢出 | 编译时无 | 切片边界检查 |
| UAF | 编译时无 | 所有权/借用检查 |
| 数据竞争 | 编译时无 | Send/Sync 检查 |
| 忘记释放锁 | 编译器不检查 | Guard Drop 自动释放 |
| 忘记检查返回值 | 编译器不检查 | ? 运算符强制检查 |
