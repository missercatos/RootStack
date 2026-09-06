# FFI

## 

FFIForeign Function Interface Rust  C/C++/Python  `extern "C"`  C ABI 

ABI x86_64 System V
-  6  `rdi, rsi, rdx, rcx, r8, r9` 
-  8  `xmm0-xmm7` 
- 
-  `rax` `xmm0`

FFI  unsafe Rust 
-  Optional
- 
- `#[repr(C)]` 
-  free Rust  drop

`cbindgen`  C `bindgen`  C  Rust FFI 

[[../../red_team/archstrike-malware/01-|: FFI]]
[[../2/09-Unsafe-Rust|Rust: Unsafe]]

---

## FFI 

###  1:  FFI 

```rust
//  Rust  C 
extern "C" {
    fn c_process(data: String);  // String  move  CRust 
}

//  Rust 
extern "C" {
    fn c_process(data: *const u8, len: usize);  // 
}
```

###  2:  FFI 

```rust
//  Rust  C 
extern "C" {
    fn c_get_string() -> *const u8;
}
// 

//   Rust 
extern "C" {
    fn c_fill_buffer(buf: *mut u8, capacity: usize) -> usize;
}

//   'static 
static GLOBAL_CONFIG: &[u8] = b"config data";
```

###  3:  Rust 

```rust
//   FFI 
// - String (Rust )
// - Vec<T> (Rust )
// - Box<T> (Rust )
// - Rc<T>, Arc<T> ()
// - HashMap, BTreeMap ()

//   C 
// - : i8, i16, i32, i64, u8, u16, u32, u64, usize, isize
// - : f32, f64
// - : bool ( C  0/1)
// - : *const T, *mut T
// - #[repr(C)] 
```

###  4:  FFI

```rust
//  1: 
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
    // C /
    ErrorCode::Ok
}

//  2:  out 
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

## #[repr(C)] 

### 

C  Rust 

```rust
// Rust  — 
struct RustDefault {
    a: u8,     // 1 
    b: u64,    // 8 
    c: u8,     // 1 
}
// Rust : b(8) + a(1) + c(1) + padding(6) = 16 
// : a(1) + padding(7) + b(8) + c(1) + padding(7) = 24 

// C  — 
#[repr(C)]
struct CLayout {
    a: u8,     //  0, 1 
    b: u64,    //  8, 8  8  7 
    c: u8,     //  16, 1 
}
// : 24  ( padding )
```

****

```rust
use std::mem;

#[repr(C)]
struct Aligned {
    a: u8,      // offset: 0, size: 1, align: 1
    b: u16,     // offset: 2, size: 2, align: 2  ( 2 )
    c: u32,     // offset: 4, size: 4, align: 4  ( 4 )
    d: u64,     // offset: 8, size: 8, align: 8  ( 8 )
}
// : 16 

assert_eq!(mem::size_of::<Aligned>(), 16);
assert_eq!(mem::align_of::<Aligned>(), 8);

//  —  C  offsetof 
assert_eq!(mem::offset_of!(Aligned, a), 0);
assert_eq!(mem::offset_of!(Aligned, b), 2);
assert_eq!(mem::offset_of!(Aligned, c), 4);
assert_eq!(mem::offset_of!(Aligned, d), 8);
```

**repr(C) **

```rust
#[repr(C)]
pub struct Message {
    pub tag: u32,           // 
    pub length: u32,        // 
    //  —  tag 
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

//  — C  tagged union
#[repr(C)]
pub enum Shape {
    Circle { radius: f64 },
    Rectangle { width: f64, height: f64 },
    Triangle { x: f64, y: f64, z: f64 },
}

//  C  0 
//  C  repr(u32) 
#[repr(u32)]
pub enum ErrorCode {
    Ok = 0,
    InvalidArgument = 1001,
    NotFound = 1002,
}
```

---

## 

### Rust String ↔ C 

```rust
use std::ffi::{CStr, CString};
use std::os::raw::c_char;

// Rust String → C  (*const c_char)
fn rust_to_c(s: &str) -> CString {
    CString::new(s).expect("CString::new failed (null byte in string)")
}

// C  → Rust &str
fn c_to_rust(ptr: *const c_char) -> Result<&'static str, std::ffi::FromCStrError> {
    unsafe { CStr::from_ptr(ptr) }.to_str()
}

// 
extern "C" {
    fn c_print_message(msg: *const c_char);
    fn c_get_name() -> *const c_char;
}

#[no_mangle]
pub extern "C" fn rust_print_message(msg: *const c_char) {
    if msg.is_null() {
        return;  // 
    }

    // CStr::from_ptr  unsafe  —  null 
    let c_str = unsafe { CStr::from_ptr(msg) };

    match c_str.to_str() {
        Ok(s) => println!("message: {}", s),
        Err(e) => eprintln!("invalid UTF-8: {}", e),
    }
}

#[no_mangle]
pub extern "C" fn rust_get_name() -> *const c_char {
    //  CString  drop 
    // let name = CString::new("Alice").unwrap();
    // name.as_ptr()  //  

    //   CString
    static mut NAME: Option<CString> = None;
    unsafe {
        let name = CString::new("Alice").unwrap();
        let ptr = name.as_ptr();
        NAME = Some(name);
        ptr
    }
}

// 
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

## 

### C  Rust 

```rust
// 
type ProgressCallback = extern "C" fn(current: u32, total: u32);

// C 
extern "C" {
    fn c_long_running_task(callback: ProgressCallback);
}

// Rust 
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

### 

```rust
use std::ffi::c_void;

//  — 
type EventCallback = extern "C" fn(event_type: u32, data: *const u8, user_data: *mut c_void);

//  C 
extern "C" {
    fn c_register_callback(cb: EventCallback, user_data: *mut c_void);
}

// Rust 
struct EventProcessor {
    count: u32,
    prefix: String,
}

extern "C" fn handle_event(event_type: u32, data: *const u8, user_data: *mut c_void) {
    //  user_data  Rust 
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

    // processor 
}
```

### Rust  C

```rust
// Rust  C 
//  + 

type Callback = extern "C" fn(*const u8) -> i32;

// 
static mut CALLBACK: Option<Callback> = None;

#[no_mangle]
pub extern "C" fn register_callback(cb: Callback) {
    unsafe { CALLBACK = Some(cb); }
}

// 
fn invoke_callback(data: &[u8]) -> i32 {
    unsafe {
        match CALLBACK {
            Some(cb) => cb(data.as_ptr()),
            None => -1,  // 
        }
    }
}
```

---

## bindgen —  Rust FFI 

```bash
# 
cargo install bindgen-cli

#  C  Rust 
bindgen input.h --output bindings.rs

# 
bindgen input.h \
    --no-layout-tests \        # 
    --no-doc-comments \        # 
    --use-core \               #  core  std
    --with-derive-default \    #  Default
    --allowlist-function "my_.*" \  # 
    --blocklist-type ".*" \    # 
    --output bindings.rs
```

```rust
// build.rs —  bindgen
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

## cbindgen —  C 

```toml
# cbindgen.toml
language = "C"
cpp_compat = true  #  C++ 

[defines]
"feature = json" = "HAS_JSON"

[export]
include = ["MyStruct", "MyEnum"]
exclude = ["internal_fn"]

[parse]
parse_deps = false
```

```rust
// lib.rs —  C  API
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
    drop(config);  // 
}
```

```bash
# 
cbindgen --crate my_library --output include/my_library.h
```

---

## unsafe FFI 

###  Rust  C 

```rust
use std::ffi::CStr;
use std::os::raw::c_char;

//  FFI unsafe
mod ffi {
    use super::*;

    extern "C" {
        pub fn db_open(path: *const c_char) -> *mut OpaqueDb;
        pub fn db_close(db: *mut OpaqueDb);
        pub fn db_get(db: *const OpaqueDb, key: *const c_char) -> *mut c_char;
        pub fn db_set(db: *mut OpaqueDb, key: *const c_char, value: *const c_char) -> i32;
    }

    //  — C Rust 
    #[repr(C)]
    pub struct OpaqueDb {
        _opaque: [u8; 0],
    }
}

//  Rust 
pub struct Database {
    ptr: *mut ffi::OpaqueDb,
}

//  Drop 
impl Drop for Database {
    fn drop(&mut self) {
        unsafe { ffi::db_close(self.ptr) };
    }
}

//  Send —  C 
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

        //  C 
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

## C++ extern "C" 

```rust
// Rust  C++  FFI 
// C++  extern "C"  C ABI

// 1.  C++  C 
extern "C" {
    fn cpp_process(data: *const u8, len: usize) -> i32;
}

// 2. C++  Rust 
// Rust 
#[no_mangle]
pub extern "C" fn rust_callback(value: i32) -> i32 {
    value * 2
}

// C++ 
// extern "C" int rust_callback(int value);

// 3. C++  RAII 
// C  C /
extern "C" {
    fn cpp_object_create() -> *mut OpaqueObject;
    fn cpp_object_destroy(obj: *mut OpaqueObject);
    fn cpp_object_method(obj: *mut OpaqueObject, arg: i32) -> i32;
}

// Rust  RAII 
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

## FFI 

```rust
//  FFI 
//
// 1. 
//    - Rust  →  C → Rust 
//    - C  →  Rust → C 
//    - 
//
// 2. 
//    - 
//    - 
//
// 3. C 
//    - 
//    -  Rust 
//
// 4. C 
//    - 
//    -  out 
//    - 
//
// 5. 
//    -  #[repr(C)]
//    -  mem::size_of  mem::align_of
//    -  C  sizeof  alignof 

#[cfg(test)]
mod ffi_tests {
    use super::*;

    #[test]
    fn test_layout_consistency() {
        //  Rust  C 
        assert_eq!(std::mem::size_of::<Point>(), 16);   // 2 * f64
        assert_eq!(std::mem::align_of::<Point>(), 8);   // f64 
    }
}
```

---

## 
