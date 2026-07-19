# FFI与跨语言安全

## 原理

FFI（Foreign Function Interface）使 Rust 与 C/C++/Python 等语言互操作。通过 `extern "C"` 块声明外部函数，编译器按 C ABI 生成调用代码。

ABI 约定（x86_64 System V）：
- 前 6 个整数参数通过 `rdi, rsi, rdx, rcx, r8, r9` 寄存器传递
- 前 8 个浮点参数通过 `xmm0-xmm7` 寄存器传递
- 更多参数通过栈传递（从右向左压栈）
- 返回值在 `rax`（整数）或 `xmm0`（浮点）

安全边界：FFI 是 unsafe 代码的主要入口。Rust 侧必须验证以下不变量：
- 指针非空且对齐（或 Optional）
- 指向的内存有效且生命周期正确
- 跨语言的数据布局一致（`#[repr(C)]` 锁定）
- 如果另一侧 free 内存，Rust 侧不能 drop

`cbindgen` 自动生成 C 头文件，`bindgen` 从 C 头文件生成 Rust FFI 绑定。

[[../../red_team/archstrike-malware教学/01-恶意软件分析入门|安全: FFI注入]]
[[../2深入/09-Unsafe-Rust的计算机科学边界|Rust: Unsafe]]

---

## 语法

```rust
// 调用 C 函数
extern "C" {
    fn abs(input: i32) -> i32;
    fn malloc(size: usize) -> *mut u8;
    fn free(ptr: *mut u8);
}

unsafe {
    let result = abs(-42);
}

// 导出给 C 使用
#[no_mangle]
pub extern "C" fn add_numbers(a: i32, b: i32) -> i32 {
    a + b
}

// C 兼容的结构体
#[repr(C)]
struct Point {
    x: f64,
    y: f64,
}

// 将 Rust Vec 转为 C 数组
fn to_c_array(v: Vec<i32>) -> (*mut i32, usize) {
    let mut v = std::mem::ManuallyDrop::new(v);
    (v.as_mut_ptr(), v.len())
    // 调用者负责 free！
}
```

### 跨语言内存管理

```rust
// C 分配 → Rust 使用 → C 释放
unsafe {
    let ptr: *mut u8 = malloc(1024);
    // ... 通过 ptr 读写 ...
    free(ptr);
}

// Rust 分配 → 传给 C → 通过回调释放
extern "C" fn rust_free(ptr: *mut c_void) {
    unsafe { drop(Box::from_raw(ptr as *mut MyStruct)); }
}
```

---

## 实践

### AI 自检

1. `#[repr(C)]` 和默认 `#[repr(Rust)]` 的内存布局差异？为什么 FFI 必须用 C repr？
2. `ManuallyDrop` 在 FFI 中的作用？如果不使用 `ManuallyDrop` 直接用 `into_raw_parts` 会怎样？
