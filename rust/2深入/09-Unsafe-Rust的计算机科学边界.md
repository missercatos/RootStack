# Unsafe Rust的计算机科学边界

## 原理

`unsafe` 块关闭五项编译器安全检查：
1. 解引用裸指针（`*const T`, `*mut T`）
2. 调用 unsafe 函数（包括 FFI）
3. 读写可变静态变量（`static mut`）
4. 实现 unsafe trait（`unsafe impl`）
5. 访问 union 字段

`unsafe` 不关闭 borrow checker、类型检查、生命周期检查。仅开放上述 5 项"超级权限"。

FFI（Foreign Function Interface）通过 `extern "C"` 块声明外部函数。编译器按指定 ABI 生成调用代码（参数寄存器、栈对齐等）。Rust 侧的 `#[no_mangle]` 防止符号名混淆。

Unsafe 的契约模型：safe Rust 是 unsafe Rust 的安全封装。库作者负责在 unsafe 层确保所有安全不变量（invariant），用户无需关心实现细节。典型例子：`Vec<T>` 内部 unsafe 操作裸指针和分配器，对外暴露安全 API。

指针运算通过 `ptr::add()`, `ptr::offset()` 等方法，区别于 C 的 `p++`。读写通过 `ptr::read()` / `ptr::write()`，不调用 drop 或 copy 构造。

---

## unsafe 关键字的五项操作详解

### 1. 解引用裸指针

裸指针（Raw Pointer）不同于引用（Reference）：
- 可以为 null
- 不保证指向有效内存
- 不自动管理生命周期
- 不保证对齐
- 可以同时存在多个 `*mut T`

```rust
let mut x = 42;
let r1 = &x as *const i32;     // 从引用创建裸指针（安全）
let r2 = &mut x as *mut i32;   // 从可变引用创建裸指针（安全）
let r3 = 0x12345678 as *const i32; // 从整数创建（危险！）

unsafe {
    println!("{}", *r1); // 解引用裸指针（unsafe 操作）
    *r2 = 100;           // 写入裸指针（unsafe 操作）
    // *r3;              // 未定义行为！地址可能无效
}
```

**裸指针的内存模型**：

```text
引用（Reference）vs 裸指针（Raw Pointer）:

引用: &T 或 &mut T
  - 编译器保证非 null
  - 编译器保证对齐
  - 编译器保证指向有效内存
  - &mut T 保证独占（别名规则）
  - 携带生命周期信息

裸指针: *const T 或 *mut T
  - 可以为 null
  - 可能未对齐
  - 可能指向已释放内存
  - *mut T 不保证独占（可以有多个 *mut T 指向同一地址）
  - 无生命周期信息
  - 大小与引用相同（一个机器字）
```

### 2. 调用 unsafe 函数

```rust
// 标准库中的 unsafe 函数
let v = vec![1, 2, 3, 4, 5];
let ptr = v.as_ptr();

unsafe {
    // std::ptr::read 从指针读取值，不移动源
    let first = std::ptr::read(ptr);
    // 此时内存中仍有值，但可能已被 drop
    println!("first: {}", first);
}

// 自定义 unsafe 函数
unsafe fn dangerous_function(x: *mut i32) {
    *x = 42;
}

let mut val = 0;
unsafe { dangerous_function(&mut val); }
```

### 3. 读写可变静态变量

```rust
static mut COUNTER: u32 = 0;

unsafe fn increment() {
    COUNTER += 1; // 多线程下是数据竞争！
}

// 现代替代方案：使用原子类型
static COUNTER: std::sync::atomic::AtomicU32 = std::sync::atomic::AtomicU32::new(0);

fn safe_increment() {
    COUNTER.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
}
```

### 4. 实现 unsafe trait

```rust
// Send 和 Sync 是 unsafe trait
// 实现它们意味着你承诺类型满足线程安全不变量

// 这个实现是危险的，因为 Rc 的引用计数不是原子的
// struct MyType(std::rc::Rc<i32>);
// unsafe impl Send for MyType {}  // UB！

// 安全的 unsafe impl 示例
struct MyType {
    ptr: *mut u8,
    len: usize,
}

// 实现者承诺：
// - ptr 指向有效的 len 字节内存
// - 内存在 MyType 的生命周期内有效
// - 内存是线程安全的（或被适当同步）
unsafe impl Send for MyType {}
unsafe impl Sync for MyType {} // 需要额外保证线程安全
```

### 5. 访问 union 字段

```rust
union IntOrFloat {
    i: i32,
    f: f32,
}

let val = IntOrFloat { i: 42 };

// 必须在 unsafe 中访问，因为编译器无法知道当前哪个字段有效
unsafe {
    match val {
        IntOrFloat { i } => println!("int: {}", i),
        IntOrFloat { f } => println!("float: {}", f),
    }
}
```

---

## unsafe 操作的计算机科学基础

### 未定义行为（Undefined Behavior）

```text
UB 的类型（Rust 中）:
  1. 解引用 null/悬挂指针
  2. 缓冲区越界
  3. 整数溢出（release 模式下 wrapping）
  4. 数据竞争
  5. 违反对齐要求
  6. 违反类型不变量（如 &mut T 和 &T 同时存在）
  7. 违反 Pin 不变量
  8. 调用 unsafe 函数但不满足前置条件

UB 的危害：
  - 编译器可能"优化掉"你认为必要的代码
  - 可能发生任何事情（程序崩溃、产生错误结果、看似正常）
  - 不是"可能出错"，而是"编译器假设你不会这么做"
```

**LLVM 的 noalias 优化**：

```text
Rust 的 &mut T 编译为 LLVM 的 noalias 指针
LLVM 可以基于此进行激进优化

示例：
fn add(x: &mut i32, y: &mut i32) {
    *x += 1;
    *y += 1;
    *x += 1;
}

LLVM 优化为（概念性）：
  load x
  load y
  x = x + 2    ← 合并两次写入
  y = y + 1
  store x
  store y

但如果 x 和 y 实际指向同一地址（UB），结果会出错
```

---

## 裸指针操作详解

### 指针算术

```rust
let mut arr = [10, 20, 30, 40, 50];
let ptr = arr.as_mut_ptr();

unsafe {
    // ptr.add(n) — 偏移 n 个元素（不是字节！）
    let p1 = ptr.add(0); // 指向 10
    let p2 = ptr.add(2); // 指向 30

    // ptr.offset(n) — 有符号偏移
    let p3 = ptr.offset(4); // 指向 50
    let p4 = ptr.offset(-2); // 越界！UB！

    // ptr.byte_add(n) — 按字节偏移（Rust 1.75+）
    let p5 = ptr.byte_add(8); // 偏移 8 字节（2 个 i32）

    // 读写操作
    std::ptr::write(p1, 100);  // 写入 100 到 arr[0]
    let val = std::ptr::read(p2); // 读取 arr[2]（不移动）
}
```

### ptr::read vs ptr::write

```rust
let src = 42;
let dst = 0;

unsafe {
    // ptr::read — 从指针读取值（位复制）
    // 不会 drop src（src 仍在原位）
    let val = std::ptr::read(&src as *const i32);
    println!("val: {}", val); // 42

    // ptr::write — 向指针写入值
    // 不会 drop 旧值（dst 原来是什么就是什么）
    std::ptr::write(&mut dst as *mut i32, 100);
}
// 注意：ptr::read 后，src 的值仍然有效
// 但如果 src 是拥有所有权的类型，需要手动管理 drop
```

### std::ptr::addr_of! / addr_of_mut!

```rust
// 安全地获取裸指针（不创建引用）
let mut x = 42;
let ptr = std::ptr::addr_of!(x);      // *const i32
let ptr_mut = std::ptr::addr_of_mut!(x); // *mut i32

// 与 &x as *const i32 的区别：
// 后者创建了引用 &x（可能违反 &mut T 的别名规则）
// addr_of! 不创建引用，更安全
```

---

## unsafe trait 实现深入

### Send + Sync 实现规则

```text
自动实现规则:
  - 如果 T: Send，则 &T: Sync
  - 如果 T: Sync，则 &T: Send

不自动实现的类型:
  - Rc<T>: !Send, !Sync（非原子引用计数）
  - Cell<T>: !Sync（内部可变性不安全）
  - RefCell<T>: !Sync
  - *const T: !Send, !Sync（裸指针）
  - *mut T: !Send, !Sync

自动实现的类型:
  - 所有基本类型: Send + Sync
  - Vec<T>: Send + Sync (如果 T: Send + Sync)
  - Arc<T>: Send + Sync (如果 T: Send + Sync)
  - Mutex<T>: Send + Sync (如果 T: Send)
  - RwLock<T>: Send + Sync (如果 T: Send + Sync)
```

### 手动实现 Send 的场景

```rust
use std::marker::PhantomData;
use std::cell::UnsafeCell;

// 一个线程安全的单值容器
struct ThreadLocal<T> {
    value: UnsafeCell<T>,
    // 通过其他机制确保线程安全
    // （例如 TLS 或原子标志）
    thread_id: std::thread::ThreadId,
}

// UnsafeCell 使 ThreadLocal 变为 !Sync
// 但我们知道它是安全的，因为只在特定线程访问
unsafe impl<T: Send> Send for ThreadLocal<T> {}
// 注意：不实现 Sync，因为同一值不能跨线程共享
```

---

## FFI（Foreign Function Interface）深入

### ABI（Application Binary Interface）

```text
ABI 定义了函数调用的底层约定：
  - 参数如何传递（寄存器 vs 栈）
  - 返回值如何传递
  - 栈如何对齐
  - 名称修饰（name mangling）

x86_64 System V ABI（Linux/macOS）:
  - 前 6 个整数参数: RDI, RSI, RDX, RCX, R8, R9
  - 前 8 个浮点参数: XMM0-XMM7
  - 返回值: RAX (整数), XMM0 (浮点)
  - 栈 16 字节对齐

x86_64 Windows ABI:
  - 前 4 个参数: RCX, RDX, R8, R9
  - 需要 32 字节 shadow space
  - 栈 16 字节对齐

extern "C" 使用 C ABI
extern "system" 使用平台默认 ABI
extern "Rust" 使用 Rust ABI（不稳定！）
```

### FFI 类型映射

```text
C 类型          Rust 类型
─────────────────────────────
char            i8 / c_char
unsigned char   u8 / c_uchar
short           i16
unsigned short  u16
int             i32
unsigned int    u32
long            i64 (Linux) / i32 (Windows)
long long       i64
float           f32
double          f64
void            ()
char*           *const c_char
int*            *const i32
void*           *const c_void
size_t          usize
```

### FFI 示例

```rust
use std::ffi::{CStr, CString};
use std::os::raw::c_char;

extern "C" {
    fn strlen(s: *const c_char) -> usize;
    fn malloc(size: usize) -> *mut u8;
    fn free(ptr: *mut u8);
    fn printf(format: *const c_char, ...) -> i32;
}

// Rust 导出给 C
#[no_mangle]
pub extern "C" fn rust_add(a: i32, b: i32) -> i32 {
    a + b
}

// 安全封装 FFI 调用
fn safe_strlen(s: &str) -> usize {
    let c_str = CString::new(s).unwrap();
    unsafe { strlen(c_str.as_ptr()) }
}

// 使用 C 字符串
fn call_printf() {
    let msg = CString::new("Hello from Rust! %d\n").unwrap();
    unsafe {
        printf(msg.as_ptr(), 42);
    }
}
```

### transmute 危险

```rust
// transmute: 重新解释位模式
// 非常危险，编译器几乎无法验证正确性

// 正确用法：将整数转为浮点数
let bits: u32 = 0x3f800000;
let val: f32 = unsafe { std::mem::transmute(bits) };
assert_eq!(val, 1.0f32);

// 危险用法：绕过生命周期
// let dangling: &str = unsafe { std::mem::transmute("hello" as *const str) };

// 更安全的替代方案
let val = f32::from_bits(bits);           // 不需要 unsafe
let val = f32::from_be_bytes([0x3f, 0x80, 0x00, 0x00]); // 更明确
```

---

## unsafe 抽象模式

### 安全封装 unsafe 代码

```rust
/// 一个简单的栈（Vec 的简化版）
struct SimpleStack<T> {
    ptr: *mut T,
    len: usize,
    cap: usize,
}

impl<T> SimpleStack<T> {
    fn new() -> Self {
        SimpleStack {
            ptr: std::ptr::null_mut(),
            len: 0,
            cap: 0,
        }
    }

    fn push(&mut self, val: T) {
        if self.len == self.cap {
            self.grow();
        }
        unsafe {
            // 这里是安全的，因为：
            // 1. self.ptr 指向有效的内存（grow 保证）
            // 2. self.len < self.cap（grow 保证）
            // 3. T 不需要初始化（我们立即写入）
            std::ptr::write(self.ptr.add(self.len), val);
        }
        self.len += 1;
    }

    fn pop(&mut self) -> Option<T> {
        if self.len == 0 {
            return None;
        }
        self.len -= 1;
        unsafe {
            // 这里是安全的，因为：
            // 1. self.len < self.cap（不变量）
            // 2. ptr.add(self.len) 指向有效内存
            // 3. 我们立即读取并返回所有权
            Some(std::ptr::read(self.ptr.add(self.len)))
        }
    }

    fn grow(&mut self) {
        let new_cap = if self.cap == 0 { 4 } else { self.cap * 2 };
        let layout = std::alloc::Layout::array::<T>(new_cap).unwrap();
        let new_ptr = unsafe {
            if self.cap == 0 {
                std::alloc::alloc(layout)
            } else {
                std::alloc::realloc(self.ptr as *mut u8, layout, new_cap * std::mem::size_of::<T>())
            }
        };
        self.ptr = new_ptr as *mut T;
        self.cap = new_cap;
    }
}

impl<T> Drop for SimpleStack<T> {
    fn drop(&mut self) {
        // 先 drop 所有元素
        while self.pop().is_some() {}
        // 再释放内存
        if self.cap > 0 {
            let layout = std::alloc::Layout::array::<T>(self.cap).unwrap();
            unsafe {
                std::alloc::dealloc(self.ptr as *mut u8, layout);
            }
        }
    }
}
```

### unsafe 不变量维护

```text
安全封装的关键原则：

1. 不变量（Invariant）:
   - 定义类型的有效状态
   - 在所有公共 API 入口处维护
   - 在 unsafe 代码中假设不变量成立

2. 示例 — Vec<T> 的不变量:
   - ptr 指向有效的内存（cap > 0 时）
   - len <= cap
   - ptr[0..len] 是有效初始化的 T
   - ptr[len..cap] 是未初始化的

3. 安全 API 的职责:
   - 确保不变量在所有入口处成立
   - 不在 unsafe 块中做违反不变量的操作
   - 对外暴露的 API 不暴露内部表示
```

---

## 语法

```rust
// 裸指针解引用
let mut x = 5;
let raw = &mut x as *mut i32;
unsafe { *raw = 10; }

// FFI
extern "C" {
 fn abs(input: i32) -> i32;
}
unsafe { println!("{}", abs(-3)); }

// 导出给 C 使用
#[no_mangle]
pub extern "C" fn rust_fn(x: i32) -> i32 { x + 1 }

// Union
union MyUnion {
 i: i32,
 f: f32,
}
let u = MyUnion { i: 42 };
unsafe { println!("{}", u.i); }

// 全局可变状态
static mut COUNTER: u32 = 0;
unsafe { COUNTER += 1; }
```

### 原始指针操作

```rust
let mut v = vec![1, 2, 3];
let p = v.as_mut_ptr();
unsafe {
 ptr::write(p.add(0), 10);
 ptr::write(p.add(1), 20);
 let val = ptr::read(p.add(1));
}
```

### unsafe trait

```rust
unsafe trait UnsafeTrait { }
unsafe impl UnsafeTrait for i32 { }
// impl 者承诺满足契约
```

---

## 实践

### 力扣问题

对于算法竞赛，unsafe 通常不必要。注重标准安全 API 即可。

### AI 自检

1. `unsafe` 块中 borrow checker 仍然生效吗？举例证明。
2. `extern "C"` 和 `extern "Rust"` 的 ABI 区别？调用约定在 x86_64 上的具体差异是什么？
3. `ptr::read` 和直接解引用 `*ptr` 有什么区别？什么情况下必须使用 `ptr::read`？
4. `transmute` 有哪些安全的替代方案？`from_bits`、`from_be_bytes` 等？
5. unsafe 代码的不变量维护模式是什么？如何确保安全封装的正确性？
