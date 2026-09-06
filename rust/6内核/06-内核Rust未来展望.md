#  Rust 

## 1. 2025

Rust  Linux  2022  12  Linux 6.1 2025 

- **** craterust/kernel/
- ****Android Binder 4500  RustLinux 6.8
- **GPU **Asahi Linux  Apple Silicon GPU  Rust
- ****rnullRust null block Rust 
- ****socket  Rust rust/kernel/net.rs, Linux 6.9+
- ****x86_64aarch64ARM64 riscv64  loongarch
- ****GCC Rust (gccrs) rustc_codegen_gcc 

> ****RustLinuxLinuxC C C [[../..///02_|C: ]] C

## 2.  Rust

### 2.1 

Rust 

- `rust/kernel/net.rs` Linux 6.9  `struct socket` 
- UDP/TCP  Rust 
-  Rust 

 Rust 
-  SKBsocket buffer
- NAPINew API
- XDPAF_XDP

### 2.2 

 Rust 
- 
-  bug 
- ""


- **bcachefs**Kent Overstreet  Rust for Linux  Rust  bcachefs 
- **tarfs**Wedson Almeida Filho  Rust  Rust 
- **puzzlefs** Rust  Rust 
- **Ext4/Btrfs Rust ** Rust API 

### 2.3 GPU DRM 

- **Asahi Linux GPU ** Rust  DRM Rust 
- **Nova ** NVIDIA GPU  Rust DRM  NVIDIA  GSP 
- **Intel Xe **Intel  GPU  Rust 

DRM  Rust `rust/kernel/drm/`
- GEMGraphics Execution Manager
- DRM 
- IOCTL 

### 2.4 

|  | Rust  |  |
|--------|-----------|------|
| **USB** |  |  |
| **I2C/SPI** |  |  Rust  |
| **NVMe** |  |  Rust  |
| **SCSI** |  |  |
| **Input** |  | HID  |
| **Crypto** |  |  |
| **BPF** |  | BPF  JIT  Rust  |
| **KVM** |  |  C/ |

## 3. 

### 3.1 alloc 

 `alloc` crate 

****
- `rust/alloc/`  `alloc` crate 
-  `#[global_allocator]`  `kmalloc`/`kfree`
- >PAGE_SIZE `kvmalloc`

****
- `Vec::reserve`  `realloc` `krealloc` 
- `String`  GFP 
- 

****
-  `collections` crate  `alloc`
-  `alloc` crate  Rust 

### 3.2 LKMM

Linux LKMMRust  C++ 

****
- LKMM  `READ_ONCE`/`WRITE_ONCE`  Rust  `Atomic*` 
- LKMM ""address dependency orderingRCU 
- Rust  `Ordering::Consume` 

****
-  Rust  `sync` 
- `Arc`  `kref`  Rust  `Arc` `alloc::sync::Arc` 
-  LKMM Paul McKenney 

### 3.3 

|  |  |  |
|------|---------|------|
| x86_64 |  |  |
| aarch64 (ARM64) |  | Android |
| riscv64 |  | rustc  |
| loongarch |  |  |
| arm (32-bit) |  |  LLVM  |
| powerpc |  | ppc64le  LLVM  |
| m68k |  | LLVM  |
| alpha |  | LLVM  |

****
- LLVM 
- GCC Rust (gccrs)  GCC-only 
-  Rust 

### 3.4 nightly 

 Rust  nightly-only 

```rust
//  nightly  rust/kernel/lib.rs
#![feature(new_uninit)] // Box::new_uninit
#![feature(allocator_api)] // 
#![feature(pin_macro)] // pin! 
#![feature(arbitrary_self_types)] //  self 
#![feature(coerce_unsized)] // Unsized 
#![feature(dispatch_from_dyn)] // 
#![feature(receiver_trait)] //  trait
#![feature(unsize)] // Unsize trait
#![feature(offset_of)] // offset_of! 
#![feature(ptr_metadata)] // 
#![feature(inline_const)] // 
// ...  20 
```

** nightly**
-  Rust 
-  `allocator_api` 5+ 
-  Rust 

****
- `new_uninit`  1.75 
- `offset_of`  1.77 
- `allocator_api`  1.76 
-  nightly 

### 3.5 stabilization

 Rust 1-2 

```

1. allocator_api -- 
2. arbitrary_self_types --  API 
3. pin_macro -- 
4. dispatch_from_dyn -- 
```

## 4. 

### 4.1 C  Rust

 C  C  Rust

****
- Rust ""
-  Rust  no_std 
-  C  API  Rust 

****
- Documentation/rust/ 
- Linux Foundation  Rust 
- Rust  C 
-  Rust 

### 4.2  API

 C API Rust 

****
- bindgen 
- "" C API 
- C API C  Rust 
- CI  C 

### 4.3 

Rust  Rust 

****

|  |  |  |
|------|----------|------|
| Miguel Ojeda | Rust  |  |
| Alice Ryhl | Binder/Android |  |
| Andreas Hindborg | /NVMe |  |
| Wedson Almeida Filho | /DRM |  Microsoft |
| Danilo Krummrich | DRM/GPU |  |
| Asahi Lina | Apple GPU |  |

****
- Greg KH  Rust 
-  Rust 
- clippy

### 4.4 "Rust vs C"

"Rust vs C"

****
-  Rust ******** C
- CVE 
-  C 
- Rust  C 
- "Rust  C ""Rust "

## 5.  OS 

### 5.1 

 Linux 

- ****""""
- **** Linux WindowsmacOS 
- ****
- **** bug 

### 5.2  seL4 

seL4 formal verification OS seL4  C 

Rust for Linux 
- seL4****= 
- Rust for Linux****= 


- Rust ""
- ""

### 5.3 

```
2025-2026
 - Rust Binder 
 -  Rust 
 - DRM Rust 
 - allocator_api 

2026-2027
 -  Rust NVMeinputI2C
 -  Rust 
 - GCC Rust 
 -  riscv64  ppc64le

2027-2028
 - Rust 
 -  Rust 
 - nightly  < 5 
 -  Rust 

2028-2030
 - Linux  OS 
 -  CVE 
 - Rust  5 
```

****

## 6. 

### 6.1 

 Rust

****
- MMpage allocatorslabkmallocvmallocmmap
- CFScgroup
- top half / bottom halfsoftirqtaskletworkqueue
- spinlockmutexRCUseqlockcompletion
- busdriverdeviceplatform_devicedevice tree
- VFS inodedentrysuperblock

****
- sizealignmentpadding
- 
- I/O MMIOPMIODMA
-  x86_64 

****
- QEMU 
- ftraceperfeBPF 
- KASANKMSANUBSAN 
-  `printk`  `dmesg` 

### 6.2 

```bash
#  5 
# 1. 
git clone https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git

# 2. 
cd linux
make LLVM=1 defconfig
make LLVM=1 -j$(nproc)

# 3.  Rust 
cat samples/rust/rust_minimal.rs
cat rust/kernel/prelude.rs

# 4. 
#  rust-for-linux+subscribe@vger.kernel.org

# 5.  Zulip
#  https://rust-for-linux.zulipchat.com
```

### 6.3 

|  |  | / |
|---------|------|----------|
|  | Linux Device Drivers, 3rd Edition | lwn.net/Kernel/LDD3/ |
|  | Understanding the Linux Kernel | O'Reilly |
|  | Linux Kernel Development (Robert Love) |  |
|  | Linux Kernel Module Programming Guide | sysprog21.github.io/lkmpg/ |
|  | Rust for Linux Documentation |  Documentation/rust/ |
|  | LWN.net  | lwn.net/Kernel/ |
|  | Linux Plumbers Conference talks |  YouTube |
|  |  Rust  | linux/rust/ |

### 6.4 

- **Zulip** rust-for-linux Zulip 
- ****
- **Kangrejos** Rust for Linux 
- ****

## 7. Rust 

### 7.1  Rust 

 Rust 

- **** Rust RTICembassy 
- **hypervisor** Cloud Hypervisor Rust  VMM AWS Nitro
- **TEE/** Rust 
- **** orebootcoreboot  Rust 
- ****Rust  ARM Cortex-M 

### 7.2 Rust 

|  |  |  |
|------|------|------|
| Linux  | OS  |  |
| Windows  | OS  |  Windows  Rust GDI  |
| Android |  OS | Binder  |
| AWS Nitro | Hypervisor | Rust VMM  |
| systemd | Init  |  |
| QEMU |  |  Rust vhost-user |
| sudo/su |  | Rust sudo-rs |
| curl |  | Rust  (hyper) |

### 7.3 


- 
-  CVE  $50,000-$100,000
- ""Secure by Design--  CISA Cyber Resilience Act
- Google

** Rust **

## 8. 

### 8.1 

 Rust 

1. ****
2. ****
3. ****
4. ****

### 8.2 

Linux C  30 Rust 



****

### 8.3 

```

 git clone https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
 cd linux
 cat samples/rust/rust_minimal.rs
 make LLVM=1 rustavailable


  rust-for-linux@vger.kernel.org
  Documentation/rust/quick-start.rst
  Rust 


  Rust 
  QEMU 
 


  Rust for Linux 
 
 
```

---

## [[05-Rust]] | [[01-LinuxRust]] | [[../4/10-no_std]]

---
