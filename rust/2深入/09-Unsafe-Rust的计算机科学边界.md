# Unsafe Rust

## 

`unsafe` 
1. `*const T`, `*mut T`
2.  unsafe  FFI
3. `static mut`
4.  unsafe trait`unsafe impl`
5.  union 

`unsafe`  borrow checker 5 ""

FFIForeign Function Interface `extern "C"`  ABI Rust  `#[no_mangle]` 

Unsafe safe Rust  unsafe Rust  unsafe invariant`Vec<T>`  unsafe  API

 `ptr::add()`, `ptr::offset()`  C  `p++` `ptr::read()` / `ptr::write()` drop  copy 

---

## unsafe 

### 1. 

Raw PointerReference
-  null
- 
- 
- 
-  `*mut T`

```rust
let mut x = 42;
let r1 = &x as *const i32;     // 
let r2 = &mut x as *mut i32;   // 
let r3 = 0x12345678 as *const i32; // 

unsafe {
    println!("{}", *r1); // unsafe 
    *r2 = 100;           // unsafe 
    // *r3;              // 
}
```

****

```text
Referencevs Raw Pointer:

: &T  &mut T
  -  null
  - 
  - 
  - &mut T 
  - 

: *const T  *mut T
  -  null
  - 
  - 
  - *mut T  *mut T 
  - 
  - 
```

### 2.  unsafe 

```rust
//  unsafe 
let v = vec![1, 2, 3, 4, 5];
let ptr = v.as_ptr();

unsafe {
    // std::ptr::read 
    let first = std::ptr::read(ptr);
    //  drop
    println!("first: {}", first);
}

//  unsafe 
unsafe fn dangerous_function(x: *mut i32) {
    *x = 42;
}

let mut val = 0;
unsafe { dangerous_function(&mut val); }
```

### 3. 

```rust
static mut COUNTER: u32 = 0;

unsafe fn increment() {
    COUNTER += 1; // 
}

// 
static COUNTER: std::sync::atomic::AtomicU32 = std::sync::atomic::AtomicU32::new(0);

fn safe_increment() {
    COUNTER.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
}
```

### 4.  unsafe trait

```rust
// Send  Sync  unsafe trait
// 

//  Rc 
// struct MyType(std::rc::Rc<i32>);
// unsafe impl Send for MyType {}  // UB

//  unsafe impl 
struct MyType {
    ptr: *mut u8,
    len: usize,
}

// 
// - ptr  len 
// -  MyType 
// - 
unsafe impl Send for MyType {}
unsafe impl Sync for MyType {} // 
```

### 5.  union 

```rust
union IntOrFloat {
    i: i32,
    f: f32,
}

let val = IntOrFloat { i: 42 };

//  unsafe 
unsafe {
    match val {
        IntOrFloat { i } => println!("int: {}", i),
        IntOrFloat { f } => println!("float: {}", f),
    }
}
```

---

## unsafe 

### Undefined Behavior

```text
UB Rust :
  1.  null/
  2. 
  3. release  wrapping
  4. 
  5. 
  6.  &mut T  &T 
  7.  Pin 
  8.  unsafe 

UB 
  - ""
  - 
  - """"
```

**LLVM  noalias **

```text
Rust  &mut T  LLVM  noalias 
LLVM 


fn add(x: &mut i32, y: &mut i32) {
    *x += 1;
    *y += 1;
    *x += 1;
}

LLVM 
  load x
  load y
  x = x + 2    ← 
  y = y + 1
  store x
  store y

 x  y UB
```

---

## 

### 

```rust
let mut arr = [10, 20, 30, 40, 50];
let ptr = arr.as_mut_ptr();

unsafe {
    // ptr.add(n) —  n 
    let p1 = ptr.add(0); //  10
    let p2 = ptr.add(2); //  30

    // ptr.offset(n) — 
    let p3 = ptr.offset(4); //  50
    let p4 = ptr.offset(-2); // UB

    // ptr.byte_add(n) — Rust 1.75+
    let p5 = ptr.byte_add(8); //  8 2  i32

    // 
    std::ptr::write(p1, 100);  //  100  arr[0]
    let val = std::ptr::read(p2); //  arr[2]
}
```

### ptr::read vs ptr::write

```rust
let src = 42;
let dst = 0;

unsafe {
    // ptr::read — 
    //  drop srcsrc 
    let val = std::ptr::read(&src as *const i32);
    println!("val: {}", val); // 42

    // ptr::write — 
    //  drop dst 
    std::ptr::write(&mut dst as *mut i32, 100);
}
// ptr::read src 
//  src  drop
```

### std::ptr::addr_of! / addr_of_mut!

```rust
// 
let mut x = 42;
let ptr = std::ptr::addr_of!(x);      // *const i32
let ptr_mut = std::ptr::addr_of_mut!(x); // *mut i32

//  &x as *const i32 
//  &x &mut T 
// addr_of! 
```

---

## unsafe trait 

### Send + Sync 

```text
:
  -  T: Send &T: Sync
  -  T: Sync &T: Send

:
  - Rc<T>: !Send, !Sync
  - Cell<T>: !Sync
  - RefCell<T>: !Sync
  - *const T: !Send, !Sync
  - *mut T: !Send, !Sync

:
  - : Send + Sync
  - Vec<T>: Send + Sync ( T: Send + Sync)
  - Arc<T>: Send + Sync ( T: Send + Sync)
  - Mutex<T>: Send + Sync ( T: Send)
  - RwLock<T>: Send + Sync ( T: Send + Sync)
```

###  Send 

```rust
use std::marker::PhantomData;
use std::cell::UnsafeCell;

// 
struct ThreadLocal<T> {
    value: UnsafeCell<T>,
    // 
    //  TLS 
    thread_id: std::thread::ThreadId,
}

// UnsafeCell  ThreadLocal  !Sync
// 
unsafe impl<T: Send> Send for ThreadLocal<T> {}
//  Sync
```

---

## FFIForeign Function Interface

### ABIApplication Binary Interface

```text
ABI 
  -  vs 
  - 
  - 
  - name mangling

x86_64 System V ABILinux/macOS:
  -  6 : RDI, RSI, RDX, RCX, R8, R9
  -  8 : XMM0-XMM7
  - : RAX (), XMM0 ()
  -  16 

x86_64 Windows ABI:
  -  4 : RCX, RDX, R8, R9
  -  32  shadow space
  -  16 

extern "C"  C ABI
extern "system"  ABI
extern "Rust"  Rust ABI
```

### FFI 

```text
C           Rust 

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

### FFI 

```rust
use std::ffi::{CStr, CString};
use std::os::raw::c_char;

extern "C" {
    fn strlen(s: *const c_char) -> usize;
    fn malloc(size: usize) -> *mut u8;
    fn free(ptr: *mut u8);
    fn printf(format: *const c_char, ...) -> i32;
}

// Rust  C
#[no_mangle]
pub extern "C" fn rust_add(a: i32, b: i32) -> i32 {
    a + b
}

//  FFI 
fn safe_strlen(s: &str) -> usize {
    let c_str = CString::new(s).unwrap();
    unsafe { strlen(c_str.as_ptr()) }
}

//  C 
fn call_printf() {
    let msg = CString::new("Hello from Rust! %d\n").unwrap();
    unsafe {
        printf(msg.as_ptr(), 42);
    }
}
```

### transmute 

```rust
// transmute: 
// 

// 
let bits: u32 = 0x3f800000;
let val: f32 = unsafe { std::mem::transmute(bits) };
assert_eq!(val, 1.0f32);

// 
// let dangling: &str = unsafe { std::mem::transmute("hello" as *const str) };

// 
let val = f32::from_bits(bits);           //  unsafe
let val = f32::from_be_bytes([0x3f, 0x80, 0x00, 0x00]); // 
```

---

## unsafe 

###  unsafe 

```rust
/// Vec 
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
            // 
            // 1. self.ptr grow 
            // 2. self.len < self.capgrow 
            // 3. T 
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
            // 
            // 1. self.len < self.cap
            // 2. ptr.add(self.len) 
            // 3. 
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
        //  drop 
        while self.pop().is_some() {}
        // 
        if self.cap > 0 {
            let layout = std::alloc::Layout::array::<T>(self.cap).unwrap();
            unsafe {
                std::alloc::dealloc(self.ptr as *mut u8, layout);
            }
        }
    }
}
```

### unsafe 

```text


1. Invariant:
   - 
   -  API 
   -  unsafe 

2.  — Vec<T> :
   - ptr cap > 0 
   - len <= cap
   - ptr[0..len]  T
   - ptr[len..cap] 

3.  API :
   - 
   -  unsafe 
   -  API 
```

---

## 

```rust
// 
let mut x = 5;
let raw = &mut x as *mut i32;
unsafe { *raw = 10; }

// FFI
extern "C" {
 fn abs(input: i32) -> i32;
}
unsafe { println!("{}", abs(-3)); }

//  C 
#[no_mangle]
pub extern "C" fn rust_fn(x: i32) -> i32 { x + 1 }

// Union
union MyUnion {
 i: i32,
 f: f32,
}
let u = MyUnion { i: 42 };
unsafe { println!("{}", u.i); }

// 
static mut COUNTER: u32 = 0;
unsafe { COUNTER += 1; }
```

### 

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
// impl 
```

---

## 

### 

unsafe  API 
