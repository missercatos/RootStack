# Rust 

Rust ********RootStack  Rust  C/C++ 

##  Rust 

 2024-2025 Rust 

- ****: NSA/CISA C/C++ Rust " +  +  GC"
- **Linux **: Linux 6.1  Rust Android  Rust 
- **AI/ML **: HuggingFace  tokenizersPolarsDataFusion  Rust  Python PyO3 Python
- **WebAssembly **: Rust  WASM ——wasm-bindgenwasm-pack 

Rust  C++ **C++ **—— Rust 

>  C  C++  [[../c/c|C ]]  5 

---

## 

```
rust/
 rust.md <-- 
 1/ (14) 
 2/ (11) 
 3/ (6) →→TUI 
 4/ (15) Cargo FFI + GitHub 
 5/ (6) C→Rust →
```

---

## 

### 2-3 

|  |  |  |  |
|------|------|------|----------|
| 1 | [[1/01-Rust|01  Rust]] | rustup cargo  | — |
| 2 | [[1/02-|02 ]] | `fn main`, `println!`,  |  |
| 3 | [[1/03-|03 ]] | /`let mut` |  |
| 4 | [[1/04-|04 ]] | `if/else` `loop`/`while`/`for` |  |
| 5 | [[1/05-|05 ]] | movecloneCopy trait | — |
| 6 | [[1/06-|06 ]] | `&T` vs `&mut T` | — |
| 7 | [[1/07-|07 ]] | structimpl |  |
| 8 | [[1/08-|08 ]] | enumOptionmatch  | — |
| 9 | [[1/09-|09 ]] | Vec/ HashMap/ HashSet |  |
| 10 | [[1/10-|10 ]] | `Result`/ `Option``?` panic | — |
| 11 | [[1/11-|11 ]] | / | — |
| 12 | [[1/12-Trait|12 Trait ]] | trait `derive` | — |
| 13 | [[1/13-|13 ]] |  | — |
| 14 | [[1/14-|14 ]] | `mod`/ `use`/ `pub`crate  |  |

>  10 

### 2-3 

|  |  |  |
|------|------|------|
| 15 | [[2/01-|01 ]] | DRAM/SRAMMMU |
| 16 | [[2/02-|02 ]] | Affine MIR drop elaboration |
| 17 | [[2/03-|03 ]] | borrow checker NLLPolonius |
| 18 | [[2/04-|04 ]] | Hindley-Milner trait bound |
| 19 | [[2/05-Trait|05 Trait ]] | vtable dyn dispatch |
| 20 | [[2/06-|06 ]] | Box/ Rc/ Arc/ RefCell  |
| 21 | [[2/07-|07 ]] | MESI  |
| 22 | [[2/08-|08 ]] | Future Waker tokio  |
| 23 | [[2/09-Unsafe-Rust|09 Unsafe Rust]] | FFI |
| 24 | [[2/10-|10 ]] | HIR → MIR → LLVM IRborrowck  |
| 25 | [[2/11-|11 ]] |  token tree proc_macro |

###  3-5 

|  |  |  |
|------|------|------|
| 26 | [[3/01-GUI|01 ]] | egui / iced GUI  |
| 27 | [[3/02-|02 ]] | clap + serde + CSV |
| 28 | [[3/03-TUI|03 TUI ]] | ratatui  UI |
| 29 | [[3/04-|04 ]] | rodio + reqwest |
| 30 | [[3/05-|05 ]] | ggez / piston  |

### 

|  |  |
|------|------|
|  | [[4/01-Cargo|Cargo ]][[4/02-|]] |
|  | [[4/03-|]][[4/04-|]] |
| / | [[4/05-|]][[4/06-|]] |
| / | [[4/07-|]][[4/08-|]] |
|  | [[4/09-FFI|FFI ]] |
|  | [[4/10-no_std|]] |
| / | [[4/11-|]][[4/12-niri|niri ]] |
|  | [[4/15-GitHub|GitHub ]] —  Rust  |

### C → Rust 

|  |  |  |
|------|------|------|
| 1 | [[5/01-C|C ]] | AST  |
| 2 | [[5/02-C|]] | unsafe  |
| 3 | [[5/03-C|]] |  → Makefile → Cargo |
| 4 | [[5/04-C|]] | < 1000  |
| 5 | [[5/05-C|]] | 1000-10000  |
| 6 | [[5/06-|]] |  |

---

## C ↔ Rust 

|  | C | C++ | Rust |
|------|---|-----|------|
|  | `malloc/free` | `new/delete` | `Box::new` / RAII  |
|  | `_Generic`  |  |  + trait bound |
|  |  |  (vtable) | trait object (`dyn Trait`) |
|  |  / `errno` |  | `Result<T, E>` / `?` |
|  | `#include` | `#include` + namespace | `mod` / `use` () |
|  | pthread | `std::thread` | `Send + Sync` trait |
|  | `char*` | `std::string` | `&str` / `String` |

---

## 

- [[../c/c|C ]] — 
- [[../cpp/cpp|C++ ]] — OOPSTL 
- [[..//CRust|C  Rust ]] — Linux  Rust 
- [[..//Rust/01-Rust|Rust ]] — 
- [[../red_team/Rust|Rust ]] —  Rust
- [[../red_team//05-Rust|Rust ]] — 

---

## 

- [Rust  ()](https://doc.rust-lang.org/book/)
- [Rust  ()](https://kaisery.github.io/trpl-zh-cn/)
- [Rust By Example](https://doc.rust-lang.org/rust-by-example/)
- [ (LeetCode)](https://leetcode.cn/)
- [Rust for Linux](https://rust-for-linux.com/)
