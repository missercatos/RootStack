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

## FFI 安全规则

### 规则 1: 所有权不跨 FFI 边界

```rust
// ❌ 危险：Rust 的所有权语义在 C 侧不成立
extern "C" {
    fn c_process(data: String);  // String 被 move 给 C，Rust 不再管理
}

// ✅ 正确：传递借用指针，Rust 保留所有权
extern "C" {
    fn c_process(data: *const u8, len: usize);  // 借用，不转移所有权
}
```

### 规则 2: 生命周期不跨 FFI 边界

```rust
// ❌ 危险：Rust 不知道 C 侧何时释放
extern "C" {
    fn c_get_string() -> *const u8;
}
// 返回的指针可能指向已释放的内存

// ✅ 正确：传递缓冲区，由 Rust 管理生命周期
extern "C" {
    fn c_fill_buffer(buf: *mut u8, capacity: usize) -> usize;
}

// ✅ 正确：使用 'static 生命周期的静态数据
static GLOBAL_CONFIG: &[u8] = b"config data";
```

### 规则 3: 不传递 Rust 特有类型

```rust
// ❌ 以下类型不能安全地跨 FFI 传递
// - String (Rust 的堆分配字符串)
// - Vec<T> (Rust 的堆分配数组)
// - Box<T> (Rust 的堆分配智能指针)
// - Rc<T>, Arc<T> (引用计数)
// - HashMap, BTreeMap (复杂结构)

// ✅ 只传递 C 兼容类型
// - 整数: i8, i16, i32, i64, u8, u16, u32, u64, usize, isize
// - 浮点: f32, f64
// - 布尔: bool (但注意 C 侧可能用 0/1)
// - 指针: *const T, *mut T
// - #[repr(C)] 结构体
```

### 规则 4: 错误处理跨 FFI

```rust
// 模式 1: 返回错误码
#[repr(C)]
pub enum ErrorCode {
    Ok = 0,
    InvalidArgument = -1,
    NotFound = -2,
    InternalError = -3,
}

#[no_mangle]
pub extern "C" fn process(
    input: *const u8,
    len: usize,
    output: *mut u8,
    output_len: *mut usize,
) -> ErrorCode {
    // C 侧通过返回值判断成功/失败
    ErrorCode::Ok
}

// 模式 2: 通过 out 参数返回错误信息
#[no_mangle]
pub extern "C" fn process_with_error(
    input: *const u8,
    len: usize,
    error_buf: *mut u8,
    error_buf_len: usize,
) -> bool {
    match do_process(input, len) {
        Ok(()) => true,
        Err(e) => {
            let msg = e.to_string();
            let bytes = msg.as_bytes();
            let copy_len = bytes.len().min(error_buf_len - 1);
            unsafe {
                std::ptr::copy_nonoverlapping(bytes.as_ptr(), error_buf, copy_len);
                *error_buf.add(copy_len) = 0;  // null terminator
            }
            false
        }
    }
}
```

---

## #[repr(C)] 布局详解

### 内存对齐规则

C 和 Rust 的默认内存布局不同：

```rust
// Rust 默认布局 — 编译器可以重排字段以优化对齐
struct RustDefault {
    a: u8,     // 1 字节
    b: u64,    // 8 字节
    c: u8,     // 1 字节
}
// Rust 可能重排为: b(8) + a(1) + c(1) + padding(6) = 16 字节
// 或者: a(1) + padding(7) + b(8) + c(1) + padding(7) = 24 字节

// C 布局 — 严格按照声明顺序排列
#[repr(C)]
struct CLayout {
    a: u8,     // 偏移 0, 1 字节
    b: u64,    // 偏移 8, 8 字节（需要 8 字节对齐，前面填充 7 字节）
    c: u8,     // 偏移 16, 1 字节
}
// 总大小: 24 字节 (含尾部 padding 以满足最大对齐要求)
```

**对齐计算**：

```rust
use std::mem;

#[repr(C)]
struct Aligned {
    a: u8,      // offset: 0, size: 1, align: 1
    b: u16,     // offset: 2, size: 2, align: 2  (需要 2 字节对齐)
    c: u32,     // offset: 4, size: 4, align: 4  (需要 4 字节对齐)
    d: u64,     // offset: 8, size: 8, align: 8  (需要 8 字节对齐)
}
// 总大小: 16 字节

assert_eq!(mem::size_of::<Aligned>(), 16);
assert_eq!(mem::align_of::<Aligned>(), 8);

// 字段偏移量 — 与 C 的 offsetof 宏等价
assert_eq!(mem::offset_of!(Aligned, a), 0);
assert_eq!(mem::offset_of!(Aligned, b), 2);
assert_eq!(mem::offset_of!(Aligned, c), 4);
assert_eq!(mem::offset_of!(Aligned, d), 8);
```

**repr(C) 结构体设计**：

```rust
#[repr(C)]
pub struct Message {
    pub tag: u32,           // 消息类型标签
    pub length: u32,        // 数据长度
    // 不透明数据 — 通过 tag 决定如何解释
}

#[repr(C)]
pub struct Point {
    pub x: f64,
    pub y: f64,
}

#[repr(C)]
pub struct Rect {
    pub top_left: Point,
    pub bottom_right: Point,
}

// 枚举 — C 兼容的 tagged union
#[repr(C)]
pub enum Shape {
    Circle { radius: f64 },
    Rectangle { width: f64, height: f64 },
    Triangle { x: f64, y: f64, z: f64 },
}

// ⚠️ 注意：C 枚举的值从 0 开始递增
// 如果 C 侧需要特定值，使用 repr(u32) 等
#[repr(u32)]
pub enum ErrorCode {
    Ok = 0,
    InvalidArgument = 1001,
    NotFound = 1002,
}
```

---

## 字符串转换

### Rust String ↔ C 字符串

```rust
use std::ffi::{CStr, CString};
use std::os::raw::c_char;

// Rust String → C 字符串 (*const c_char)
fn rust_to_c(s: &str) -> CString {
    CString::new(s).expect("CString::new failed (null byte in string)")
}

// C 字符串 → Rust &str
fn c_to_rust(ptr: *const c_char) -> Result<&'static str, std::ffi::FromCStrError> {
    unsafe { CStr::from_ptr(ptr) }.to_str()
}

// 完整示例
extern "C" {
    fn c_print_message(msg: *const c_char);
    fn c_get_name() -> *const c_char;
}

#[no_mangle]
pub extern "C" fn rust_print_message(msg: *const c_char) {
    if msg.is_null() {
        return;  // 安全检查
    }

    // CStr::from_ptr 是 unsafe 的 — 必须保证指针有效且以 null 结尾
    let c_str = unsafe { CStr::from_ptr(msg) };

    match c_str.to_str() {
        Ok(s) => println!("message: {}", s),
        Err(e) => eprintln!("invalid UTF-8: {}", e),
    }
}

#[no_mangle]
pub extern "C" fn rust_get_name() -> *const c_char {
    // ⚠️ 危险：CString 被 drop 后指针失效
    // let name = CString::new("Alice").unwrap();
    // name.as_ptr()  // ❌ 返回悬垂指针！

    // ✅ 正确：泄漏 CString，调用者负责释放
    static mut NAME: Option<CString> = None;
    unsafe {
        let name = CString::new("Alice").unwrap();
        let ptr = name.as_ptr();
        NAME = Some(name);
        ptr
    }
}

// 更安全的模式：调用者提供缓冲区
#[no_mangle]
pub extern "C" fn rust_get_name_to_buf(buf: *mut u8, buf_len: usize) -> usize {
    let name = b"Alice";
    let copy_len = name.len().min(buf_len);
    unsafe {
        std::ptr::copy_nonoverlapping(name.as_ptr(), buf, copy_len);
    }
    copy_len
}
```

---

## 回调模式

### C 回调 Rust 函数

```rust
// 定义回调类型
type ProgressCallback = extern "C" fn(current: u32, total: u32);

// C 函数接受回调
extern "C" {
    fn c_long_running_task(callback: ProgressCallback);
}

// Rust 函数作为回调
extern "C" fn progress_handler(current: u32, total: u32) {
    let percent = (current as f64 / total as f64 * 100.0) as u32;
    println!("progress: {}%", percent);
}

fn run_task() {
    unsafe {
        c_long_running_task(progress_handler);
    }
}
```

### 带用户数据的回调

```rust
use std::ffi::c_void;

// 回调签名 — 包含用户数据指针
type EventCallback = extern "C" fn(event_type: u32, data: *const u8, user_data: *mut c_void);

// 注册回调的 C 函数
extern "C" {
    fn c_register_callback(cb: EventCallback, user_data: *mut c_void);
}

// Rust 端的回调处理
struct EventProcessor {
    count: u32,
    prefix: String,
}

extern "C" fn handle_event(event_type: u32, data: *const u8, user_data: *mut c_void) {
    // 从 user_data 恢复 Rust 对象引用
    let processor = unsafe { &mut *(user_data as *mut EventProcessor) };

    let msg = unsafe {
        CStr::from_ptr(data as *const c_char)
    }.to_string_lossy();

    processor.count += 1;
    println!("[{}] event {}: {}", processor.prefix, event_type, msg);
}

fn register_processor() {
    let mut processor = EventProcessor {
        count: 0,
        prefix: "main".into(),
    };

    unsafe {
        c_register_callback(handle_event, &mut processor as *mut _ as *mut c_void);
    }

    // processor 在此作用域内有效，回调安全
}
```

### Rust 函数指针传给 C

```rust
// Rust 闭包不能直接作为 C 回调
// 解决方案：使用函数指针 + 单例模式

type Callback = extern "C" fn(*const u8) -> i32;

// 全局状态（线程安全）
static mut CALLBACK: Option<Callback> = None;

#[no_mangle]
pub extern "C" fn register_callback(cb: Callback) {
    unsafe { CALLBACK = Some(cb); }
}

// 调用已注册的回调
fn invoke_callback(data: &[u8]) -> i32 {
    unsafe {
        match CALLBACK {
            Some(cb) => cb(data.as_ptr()),
            None => -1,  // 未注册
        }
    }
}
```

---

## bindgen — 自动生成 Rust FFI 绑定

```bash
# 安装
cargo install bindgen-cli

# 从 C 头文件生成 Rust 绑定
bindgen input.h --output bindings.rs

# 常用选项
bindgen input.h \
    --no-layout-tests \        # 不生成布局测试
    --no-doc-comments \        # 不生成文档注释
    --use-core \               # 使用 core 而不是 std
    --with-derive-default \    # 自动派生 Default
    --allowlist-function "my_.*" \  # 只包含匹配的函数
    --blocklist-type ".*" \    # 排除匹配的类型
    --output bindings.rs
```

```rust
// build.rs — 自动化 bindgen
fn main() {
    println!("cargo:rerun-if-changed=wrapper.h");

    let bindings = bindgen::Builder::default()
        .header("wrapper.h")
        .parse_callbacks(Box::new(bindgen::CargoCallbacks))
        .generate()
        .expect("unable to generate bindings");

    let out_path = std::path::PathBuf::from(std::env::var("OUT_DIR").unwrap());
    bindings.write_to_file(out_path.join("bindings.rs")).unwrap();
}
```

---

## cbindgen — 自动生成 C 头文件

```toml
# cbindgen.toml
language = "C"
cpp_compat = true  # 同时生成 C++ 兼容头文件

[defines]
"feature = json" = "HAS_JSON"

[export]
include = ["MyStruct", "MyEnum"]
exclude = ["internal_fn"]

[parse]
parse_deps = false
```

```rust
// lib.rs — 导出给 C 使用的 API
#[repr(C)]
pub struct Config {
    pub width: u32,
    pub height: u32,
    pub fullscreen: bool,
}

#[no_mangle]
pub extern "C" fn config_create(width: u32, height: u32) -> Box<Config> {
    Box::new(Config { width, height, fullscreen: false })
}

#[no_mangle]
pub extern "C" fn config_destroy(config: Box<Config>) {
    drop(config);  // 显式释放
}
```

```bash
# 生成头文件
cbindgen --crate my_library --output include/my_library.h
```

---

## unsafe FFI 包装模式

### 安全 Rust 包装 C 库

```rust
use std::ffi::CStr;
use std::os::raw::c_char;

// 底层 FFI 声明（unsafe）
mod ffi {
    use super::*;

    extern "C" {
        pub fn db_open(path: *const c_char) -> *mut OpaqueDb;
        pub fn db_close(db: *mut OpaqueDb);
        pub fn db_get(db: *const OpaqueDb, key: *const c_char) -> *mut c_char;
        pub fn db_set(db: *mut OpaqueDb, key: *const c_char, value: *const c_char) -> i32;
    }

    // 不透明类型 — C 侧定义，Rust 侧不关心内部结构
    #[repr(C)]
    pub struct OpaqueDb {
        _opaque: [u8; 0],
    }
}

// 安全 Rust 包装
pub struct Database {
    ptr: *mut ffi::OpaqueDb,
}

// 实现 Drop 以自动释放
impl Drop for Database {
    fn drop(&mut self) {
        unsafe { ffi::db_close(self.ptr) };
    }
}

// 不实现 Send — 除非 C 库保证线程安全
// unsafe impl Send for Database {}

impl Database {
    pub fn open(path: &str) -> Result<Self, Error> {
        let c_path = CString::new(path).map_err(|_| Error::InvalidPath)?;

        let ptr = unsafe { ffi::db_open(c_path.as_ptr()) };

        if ptr.is_null() {
            return Err(Error::OpenFailed);
        }

        Ok(Self { ptr })
    }

    pub fn get(&self, key: &str) -> Result<Option<String>, Error> {
        let c_key = CString::new(key).map_err(|_| Error::InvalidKey)?;

        let c_value = unsafe { ffi::db_get(self.ptr, c_key.as_ptr()) };

        if c_value.is_null() {
            return Ok(None);
        }

        let value = unsafe { CStr::from_ptr(c_value) }
            .to_str()
            .map_err(|_| Error::InvalidUtf8)?
            .to_string();

        // 释放 C 分配的字符串
        unsafe { libc::free(c_value as *mut libc::c_void) };

        Ok(Some(value))
    }

    pub fn set(&mut self, key: &str, value: &str) -> Result<(), Error> {
        let c_key = CString::new(key).map_err(|_| Error::InvalidKey)?;
        let c_value = CString::new(value).map_err(|_| Error::InvalidValue)?;

        let result = unsafe { ffi::db_set(self.ptr, c_key.as_ptr(), c_value.as_ptr()) };

        if result != 0 {
            return Err(Error::SetFailed);
        }

        Ok(())
    }
}
```

---

## C++ extern "C" 对比

```rust
// Rust 与 C++ 的 FFI 交互
// C++ 的 extern "C" 块使用 C ABI

// 1. 调用 C++ 的 C 导出函数
extern "C" {
    fn cpp_process(data: *const u8, len: usize) -> i32;
}

// 2. C++ 调用 Rust 导出函数
// Rust 侧
#[no_mangle]
pub extern "C" fn rust_callback(value: i32) -> i32 {
    value * 2
}

// C++ 侧（示意）
// extern "C" int rust_callback(int value);

// 3. C++ 类的 RAII 包装
// C 侧提供 C 风格的创建/销毁函数
extern "C" {
    fn cpp_object_create() -> *mut OpaqueObject;
    fn cpp_object_destroy(obj: *mut OpaqueObject);
    fn cpp_object_method(obj: *mut OpaqueObject, arg: i32) -> i32;
}

// Rust 侧的 RAII 包装
#[repr(C)]
struct OpaqueObject {
    _opaque: [u8; 0],
}

struct CppObject {
    ptr: *mut OpaqueObject,
}

impl CppObject {
    fn new() -> Self {
        let ptr = unsafe { cpp_object_create() };
        assert!(!ptr.is_null(), "failed to create C++ object");
        Self { ptr }
    }

    fn method(&mut self, arg: i32) -> i32 {
        unsafe { cpp_object_method(self.ptr, arg) }
    }
}

impl Drop for CppObject {
    fn drop(&mut self) {
        unsafe { cpp_object_destroy(self.ptr) };
    }
}
```

---

## FFI 安全检查清单

```rust
// 每次写 FFI 代码时检查：
//
// 1. 所有权：谁分配？谁释放？
//    - Rust 分配 → 传给 C → Rust 释放（通过回调或约定）
//    - C 分配 → 传给 Rust → C 释放
//    - 绝不：两侧都尝试释放
//
// 2. 生命周期：指针在使用期间有效吗？
//    - 函数内使用的指针：确保参数有效期内指针有效
//    - 返回的指针：确保调用者在使用前指针有效
//
// 3. 线程安全：C 函数可重入吗？
//    - 不可重入函数：使用互斥锁
//    - 全局状态：确保 Rust 侧同步访问
//
// 4. 错误处理：C 函数失败时返回什么？
//    - 检查返回值
//    - 检查 out 参数
//    - 不假设成功
//
// 5. 内存对齐：结构体布局一致吗？
//    - 使用 #[repr(C)]
//    - 测试 mem::size_of 和 mem::align_of
//    - 与 C 侧的 sizeof 和 alignof 对比

#[cfg(test)]
mod ffi_tests {
    use super::*;

    #[test]
    fn test_layout_consistency() {
        // 确保 Rust 结构体布局与 C 一致
        assert_eq!(std::mem::size_of::<Point>(), 16);   // 2 * f64
        assert_eq!(std::mem::align_of::<Point>(), 8);   // f64 对齐
    }
}
```

---

## 实践

### AI 自检

1. `#[repr(C)]` 和默认 `#[repr(Rust)]` 的内存布局差异？为什么 FFI 必须用 C repr？
2. `ManuallyDrop` 在 FFI 中的作用？如果不使用 `ManuallyDrop` 直接用 `into_raw_parts` 会怎样？
3. 为什么 Rust 字符串不能直接传递给 C？`CString` 和 `CStr` 的区别是什么？
4. 如何在 FFI 中安全地传递 Rust 闭包？为什么闭包不能直接作为 C 函数指针？
5. `bindgen` 和 `cbindgen` 的使用场景分别是什么？工作流程有何不同？
