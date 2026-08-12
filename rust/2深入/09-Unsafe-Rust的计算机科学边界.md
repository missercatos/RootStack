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
