# Rust

## 

Rust  LLVM `rustc` /Borrow Checker

`.rs`  → `rustc` → LLVM IR → 

```mermaid
flowchart LR
 A["main.rs"] --> B["rustc"]
 B --> C[""]
 C --> D[""]
```

Rust  C/C++  JIT  GC WebAssemblyCLI 

[[../../c/1/01_|C: ]]

---

## Rust 

### Zero-Cost Abstraction

 C++  Bjarne Stroustrup ****Rust 

Rust —— C 

```rust
// Rust 
fn sum_slice(data: &[i32]) -> i32 {
    data.iter().sum()
}

//  C 
// int sum_slice(const int* data, size_t len) {
//     int sum = 0;
//     for (size_t i = 0; i < len; i++) sum += data[i];
//     return sum;
// }
```

Rust  `data` ——

### Rust  GC 

C/C++ **** `free` use-after-freedouble-freememory leak

Rust 

```text

              C/C++                    
                                                   
  malloc() →  → free()                 
                                                
                            free          
                        ↓                  
                                   
     ↓                                              
                      



              Rust                       
                                                   
  let s = String::from("hi");                     
                                                  
      s                                  
       s2 s move               
                                                  
  s2  →  drop →       
                                                   
                     
   drop                  

```

 **Ownership**——ownerscopemove

### Borrow Checker 

`rustc`  HIRHigh-level IR→ MIRMid-level IR→ LLVM IR MIR 

```text
 (.rs)
    ↓ parse
AST ()
    ↓ type check + macro expansion
HIR ()
    ↓ borrow check + NLL analysis    ← 
MIR ( IR)
    ↓ optimization
LLVM IR
    ↓ codegen

```

 MIR live range—— NLLNon-Lexical Lifetimes

```rust
let mut s = String::from("hello");
let r1 = &s;
println!("{}", r1);     // r1 
let r2 = &mut s;        //  r1 
r2.push_str(" world");
```

###  C/C++ 

|  | C | C++ | Rust |
|------|---|-----|------|
|  | `malloc`/`free` | `new`/`delete`  |  |
|  |  |  |  |
|  | TSan |  |  |
|  |  |  | `Option<T>`  |
|  |  |  |  opt-out |
|  |  |  |  |

```rust
// Rust  vs C 

// C  crash
// char* s = malloc(5);
// free(s);
// printf("%s", s);  // use-after-free

// Rust 
let s = String::from("hi");
let r = &s;
drop(s);
// println!("{}", r);  // cannot borrow `s` as immutable
                       //           after it has been moved
```

---

## 

### 

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```


- `rustc` —  `.rs` → 
- `cargo` — 
- `rustup` — 

### rustup  cargo 

`rustup`  `rustc`toolchain

```text
~/.rustup/toolchains/
 stable-x86_64-unknown-linux-gnu/
    bin/
       rustc          ← 
       cargo          ← 
       rustfmt        ← 
       clippy-driver  ← lint 
    lib/
       rustlib/       ← 
    ...
 nightly-x86_64-unknown-linux-gnu/
 1.75.0-x86_64-unknown-linux-gnu/
```

`cargo` 

```text
cargo build
    
     1.  Cargo.toml
     2.  crates.io registry
     3. 
     4.  crate
     5.  .rlib/.so → 
    
      target/ 
```

`crates.io`  Rust  npmPyPI **crate** crate 

### 

```rust
// src/main.rs — cargo new 
fn main() {
 println!("Hello, world!");
}
```

```bash
cargo new hello # 
cargo build # debug
cargo build --release # release
cargo run #  + 
cargo check # 
```

> `println!` `!` 

### debug  release 

|  |  |  |  |  |
|------|---------|---------|---------|---------|
| `cargo build` | 0 | panic |  |  |
| `cargo build --release` | 3 | wrap |  |  |

```rust
// debug  panic
let x: u8 = 255;
// let y = x + 1;  // panic: attempt to add with overflow

// release 
// let y = x + 1;  // y = 0
```

### Cargo.toml 

```toml
[package]
name = "hello"
version = "0.1.0"
edition = "2021"

[dependencies]
serde = { version = "1.0", features = ["derive"] }
```

`edition`  Rust 2015201820212024 edition 

### 

|  |  |
|------|------|
| `cargo new <name>` |  |
| `cargo new <name> --lib` |  |
| `cargo build` | debug |
| `cargo run` |  |
| `cargo check` |  |
| `cargo test` |  |
| `cargo fmt` |  |
| `cargo clippy` | Lint  |
| `cargo add <crate>` |  |
| `cargo doc --open` |  |
| `rustc --explain E0382` |  |
| `rustup update` |  |

---

## 

### 1.  `cargo check` 
`cargo check`  `cargo build`  5-10  `check`  `build`

### 2.  `rustc`  `cargo`
 `rustc main.rs`  `cargo`

### 3. 
`cargo new mylib`  `cargo new mylib --lib`

---

## 

### 



:  Hello,World! 

```rust
fn main() {
 println!("Hello,World!");
}
```
