#  Rust 

## 1. 

Linux  Rust for Linux ——**** C  Unix 


1. ****
2. ****
3. ****
4. ****
5. ****

"Rust for Linux " -- Wedson Almeida Filho Google Rust for Linux 

> **C**RustC [[../..///07_Linux|C: Linux]] list.hcontainer_of

## 2. 

### 2.1 

|  |  |  |
|------|---------|---------|
| **Rust** | traitunsafe  | Rust BookRust by Example |
| **C** |  C  |  + LWN  |
| **Linux ** | sysfs | Linux Device Drivers 3 |
| **Git** |  | Pro Git |
| **** | QEMU  |  |

### 2.2 

- **Linux ** DRM
- **LLVM/clang ** LLVM=1 
- ****
- ****fuzzing

### 2.3 


1.  C  probe 
2.  Rust  borrow checker 
3. 
4.  GFP_KERNEL  GFP_ATOMIC 
5. /



## 3. 

### 3.1 



|  |  |  |  |
|---------|------|------|------|
|  | 1 |  | Documentation/rust/  |
|  | 2 |  clippy  | unused importsnon_snake_case |
|  | 2 |  kunit  | rust/kernel/sync/arc.rs  |
|  | 3 |  C API |  kmem_cache  Rust  |
|  | 2 |  | samples/rust/  |
|  | 4 |  bug | syzbot  |

### 3.2 

**1. LKML**

 `rust-for-linux@vger.kernel.org` `rust-for-linux+subscribe@vger.kernel.org` 

**2. GitHub Issues**

Rust for Linux  GitHub `https://github.com/Rust-for-Linux/linux/issues` "good first issue" 

**3.  TODO **


```bash
grep -rn "TODO\|FIXME\|XXX" rust/ samples/rust/
grep -rn "TODO" rust/kernel/ | head -20
```

**4. **

 lore.kernel.org `https://lore.kernel.org/rust-for-linux/` "RFC v2 needed""needs review" 

### 3.3 

|  |  |  |
|------|---------|---------|
|  rust/kernel/str.rs  | 4-8  |  CStr API |
|  Mutex<T>  | 8-16  |  |
|  WARN_ON  Rust  | 8-12  |  API |
|  platform::Device  | 16-24  |  |
|  Rust  pr_*_ratelimited  | 12-20  |  |

### 3.4 


1. 
2.  C  API 
3. 
4.  RFC 

## 4. 

### 4.1 

```
[1] 
 |
[2] 
 |
[3] /
 |
[4]  
 |
[5]  & 
 |
[6]  & 
 |
[7] 
 |
[8] 
 |
[9] 
 |
[10] 
 |  5-10 
[11] 
 |
[12] 
```

### 4.2 

```bash
# 1. 
rustc --version
bindgen --version
#  Documentation/rust/quick-start.rst 

# 2.  Rust for Linux 
git clone https://github.com/Rust-for-Linux/linux.git rust-dev
cd rust-dev

# 3. 
git remote add torvalds \
 https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git

# 4. 
git fetch torvalds
git checkout -b my-rust-contribution torvalds/master

# 5. 
make LLVM=1 rustavailable #  Rust 
make LLVM=1 defconfig
scripts/config --enable CONFIG_RUST
scripts/config --enable CONFIG_SAMPLE_RUST_MINIMAL
make LLVM=1 olddefconfig
```

### 4.3 

****

 Rust  `rustfmt`

```bash
# 
rustfmt +nightly rust/kernel/your_file.rs
# 
make LLVM=1 rustfmt
```

****

```rust
// 1. 
// :
fn my_func() -> Result<u32> {
 Err(Error::EINVAL)
}
// :
// fn my_func() -> Result<u32, MyError> { Err(MyError::Invalid) }

// 2.  unwrap/expect
// :
let val = option.ok_or(Error::EINVAL)?;
// :
// let val = option.unwrap(); // panic in kernel!

// 3. SAFETY 
// SAFETY: ptr is valid because the Arc reference ensures
// the allocation is not freed while this reference exists.
unsafe { (*ptr).field = value; }

// 4.  kernel::prelude::* 
use kernel::prelude::*;

// 5.  /// 
/// Reads a 32-bit value from MMIO at the given offset.
///
/// # Errors
///
/// Returns ERANGE if the offset is out of bounds.
fn read32(&self, offset: usize) -> Result<u32> { Ok(0) }
```

****

```bash
# 
make LLVM=1 -j$(nproc)

# 
make LLVM=1 -j$(nproc) modules

# Clippy clippy 
make LLVM=1 CLIPPY=1

# 
make LLVM=1 -j$(nproc) 2>&1 | grep -E "warning:|error:"
```

### 4.4 



```text
subsystem: Brief summary (50 chars max)

A more detailed explanation of what the patch does and why.
This can span multiple paragraphs. Explain the motivation
for the change, not just what changed.

Describe the approach taken. Reference previous discussions
on the mailing list. Explain any trade-offs made.

Mention testing performed:
- Build-tested: make LLVM=1 -j$(nproc)
- Boot-tested: QEMU x86_64
- Module tested: loaded/unloaded successfully

Link: https://lore.kernel.org/rust-for-linux/...
Signed-off-by: Your Name <your.email@example.com>
```

****
1. :  50 
2. 
3.  72 
4. Signed-off-by git commit -s 

### 4.5 

****

```bash
# 
git format-patch -1 HEAD

# 
scripts/checkpatch.pl 0001-*.patch

#  msmtp  git send-email
git send-email \
 --to="rust-for-linux@vger.kernel.org" \
 --cc="linux-kernel@vger.kernel.org" \
 --cc="Miguel Ojeda <ojeda@kernel.org>" \
 --cc="Alex Gaynor <alex.gaynor@gmail.com>" \
 0001-*.patch
```

****

```bash
#  3 
git format-patch -3 --cover-letter

# cover letter
vim 0000-cover-letter.patch

# 
git send-email \
 --to="rust-for-linux@vger.kernel.org" \
 --cc="linux-kernel@vger.kernel.org" \
 0000-*.patch
```

****

- [ ] torvalds/master
- [ ] 
- [ ]  checkpatch
- [ ] 
- [ ] 
- [ ] Signed-off-by 

### 4.6 

****

> 

> ——
> []

****

```bash
# 1. 
vim rust/kernel/your_file.rs

# 2. 
git rebase -i HEAD~1
# 
# ---
# Changes in v2:
# - Fixed lock ordering issue as suggested by Reviewer Name
# - Added missing SAFETY comment
# - Link to v1: https://lore.kernel.org/.../msg12345.html

# 3. 
git format-patch -1 HEAD --subject-prefix="PATCH v2"
```

### 4.7 

|  |  |  |
|----------|------|------|
| "Please add a SAFETY comment" | unsafe  |  // SAFETY:  |
| "NIT: s/funtion/function/" |  |  |
| "Why not use ...?" |  |  |
| "This doesn't follow kernel style" |  |  |
| "Please split this patch" |  |  |
| "Needs more testing" |  |  |
| "I don't think this is the right approach" |  |  |
| "NAK" | Not Acknowledged |  |

## 5. 

### 5.1 

Rust for Linux  2025 

|  |  |  |
|------|------|------|
| Miguel Ojeda |  | ojeda@kernel.org |
| Alex Gaynor |  | alex.gaynor@gmail.com |
| Wedson Almeida Filho |  | wedsonaf@gmail.com |
| Boqun Feng |  | boqun.feng@gmail.com |
| Gary Guo |  | gary@garyguo.net |
| Bjorn Roy Baron |  | bjorn3_gh@protonmail.com |
| Andreas Hindborg | Rust  | a.hindborg@samsung.com |
| Alice Ryhl | Rust  | aliceryhl@google.com |

### 5.2 

```
[]
 |
[]
 |
[]
 |
[]
 |  1-10 
[]
 |
["Reviewed-by"  "Acked-by" ]
 |
[ rust-next ]
 |
[linux-next ]
 |
[ Linus]
 |
[Linus ]
```

### 5.3 

|  |  |  |
|------|---------|-------------|
|  | 1-7  | / |
|  | 3-10  |  |
|  | 2-8  |  |
|  | 2-6  |  |

****

## 6. 

### 6.1 

 kernel::error  from_kernel_errno 

### 6.2 v1

```rust
//  from_kernel_errno 
// rust: error: add Error::from_kernel_errno function
//
// Add a convenience function to create an Error from a kernel
// errno value (e.g., EINVAL = 22).

impl Error {
 /// Creates an Error from a kernel error code (positive errno).
 pub fn from_kernel_errno(errno: core::ffi::c_int) -> Error {
 Error(-errno)
 }
}
```

### 6.3 

** 1**
> Should this check that errno is in a valid range? If a caller
> accidentally passes a negative number, we'd create an Error
> with a positive internal value, which would be confusing.

** 2**
> Could you add a documentation example showing how this is used
> with a real C function wrapper?

** 3**
> NIT: the doc comment line is slightly over 100 chars, please wrap.

### 6.4 v2

```rust
// Changes in v2:
// - Added documentation example
// - Fixed doc comment line length

impl Error {
 /// Creates an [`Error`] from a kernel error code.
 ///
 /// This is typically used when wrapping a C function that
 /// returns a positive `errno` value.
 ///
 /// # Example
 ///
 /// ```
 /// # use kernel::error::Error;
 /// let err = Error::from_kernel_errno(bindings::EINVAL);
 /// assert_eq!(err.to_errno(), bindings::EINVAL);
 /// ```
 pub fn from_kernel_errno(errno: core::ffi::c_int) -> Error {
 // SAFETY: The caller ensures that errno is a valid
 // positive kernel error code.
 Error(-errno)
 }
}
```

### 6.5 v2

```
Reviewed-by: Reviewer Name <reviewer@example.com>
Acked-by: Another Reviewer <another@example.com>
```

### 6.6 

 rust-next  linux-next  Linus 

****
1. 
2. 
3. 
4.  SAFETY 

## 7. 

### 7.1 

|  |  |
|------|------|
|  |  +  |
|  |  |
|  |  |
|  |  |
|  blocking |  |
|  |  reviewer/maintainer |

### 7.2 


1. ****
2. ****
3. ****""
4. ****
5. ****

### 7.3 

|  |  |  |
|------|------|------|
| Linux Plumbers Conference |  | Rust for Linux  |
| Kernel Recipes |  |  |
| Kangrejos |  | Rust for Linux  |
| FOSDEM |  |  |

### 7.4 

- **Zulip**`https://rust-for-linux.zulipchat.com` -- 
- **Lore**`https://lore.kernel.org/rust-for-linux/` -- 
- **GitHub**`https://github.com/Rust-for-Linux/` --  WIP 

## 8. 

### 8.1 1-3 

- [ ] 
- [ ]  Rust 
- [ ]  Tested-by 
- [ ]  3  Rust 
- [ ] 

### 8.2 3-12 

- [ ]  kernel  list_head
- [ ]  bug
- [ ]  Linux Plumbers Conference  Kangrejos
- [ ] 
- [ ]  Rust 

### 8.3 1-3 

- [ ]  Rust 
- [ ] 
- [ ]  Rust 
- [ ] 
- [ ]  Rust for Linux  reviewer 

### 8.4 

```

 Rust --------------- 80%
 C  ---------- 60%
  ------ 40%
  -- 20%


 Rust --------------- 90%
 C  -------------- 80%
  -------------- 80%
  ---------- 60%
  -------------- 80%


 Rust ---------------- 100%
 C  ---------------- 100%
  --------------- 90%
  ---------------- 100%
  ---------------- 100%
  --------------- 90%
```

---

## [[04-Rust vs C]] | [[06-Rust]]

---
