# Rust vs C 

## 1. 

 C  Rust 

1. **** Rust  C 
2. ****Rust 
3. ****C  Rust  trait
4. **** Rust  C 


- **Android Binder **C  Rust 
- **NVMe **
- ****

> **C**RustCC [[../..///01_C|C: ]] [[../..///04_|C: C]][[../..///06_|C: C]][[../../c/2/03_|C: ]][[../../c/2/01_|C: ]]

## 2. Android Binder 

### 2.1 

Binder  Android  IPC  C  6000 `drivers/android/binder.c`2012 Rust `drivers/android/rust/` Samsung  Alice Ryhl 2024  3  Linux 6.8

### 2.2 C 

****

```c
struct binder_proc {
 int tmp_ref; // 
 struct mutex outer_lock; // 
 struct mutex inner_lock; // 
 spinlock_t tmp_lock; // 
 // ...  40 
};

// ——
static struct binder_proc *binder_get_proc(struct binder_proc *proc)
{
 atomic_inc(&proc->tmp_ref);
 return proc;
}

static void binder_put_proc(struct binder_proc *proc)
{
 if (atomic_dec_and_test(&proc->tmp_ref))
 binder_free_proc(proc); //  → 
}
```

** goto **

```c
static long binder_ioctl(struct file *filp, unsigned int cmd, unsigned long arg)
{
 int ret;
 struct binder_proc *proc = filp->private_data;

 proc = binder_get_proc(proc);
 if (proc == NULL) return -ENOMEM;

 thread = binder_get_thread(proc);
 if (thread == NULL) { ret = -ENOMEM; goto err_get_thread; }

 switch (cmd) {
 case BINDER_WRITE_READ:
 if (copy_from_user(&bwr, ubuf, sizeof(bwr)))
 { ret = -EFAULT; goto err_copy; }
 // ...  goto 
 }

err_write:
err_copy:
 binder_put_thread(thread);
err_get_thread:
 binder_put_proc(proc);
 return ret;
}
```

**C  CVE**

- **CVE-2019-2214**UAF ——binder  `epoll` 
- **CVE-2019-2181**TOCTOU ——`binder_get_proc` 
- **CVE-2020-0041**UAF——binder  `binder_dec_node` 


1. 
2. 
3. 

### 2.3 Rust 

****

```rust
// Rust ——Arc 
pub struct Process {
 inner: Mutex<ProcessInner>,
 // Process  Arc<Process> Clone  inc refDrop  dec ref
}

//  Arc
pub struct Thread {
 inner: Mutex<ThreadInner>,
 process: Arc<Process>, // —— Process 
}

impl Process {
 // —— clone Arc
 pub fn get_ref(self: &Arc<Self>) -> Arc<Self> {
 self.clone()
 }
}
```

**Mutex **

```rust
// Rust —— drivers/android/rust/
struct ProcessInner {
 threads: Vec<Arc<Thread>>,
 nodes: BTreeMap<u64, Arc<Node>>,
 refs_by_desc: BTreeMap<u32, Arc<Ref>>,
 refs_by_node: BTreeMap<u64, Arc<Ref>>,
 max_threads: u32,
 requested_threads: u32,
 is_dead: bool,
 work_available: CondVar,
}

impl Process {
 // ——Mutex 
 pub fn register_thread(self: &Arc<Self>) -> Result<Arc<Thread>> {
 let mut inner = self.inner.lock();
 if inner.is_dead {
 return Err(Error::EBADF);
 }
 if inner.threads.len() >= inner.max_threads as usize {
 return Err(Error::EBUSY);
 }
 // ...  Thread,  self.clone()
 // Arc  Process 
 }

 // —— CondVar 
 pub fn wait_for_work(self: &Arc<Self>) -> Result<bool> {
 let mut inner = self.inner.lock();
 if inner.is_dead {
 return Err(Error::EBADF);
 }
 // 
 inner.work_available.wait(&mut inner);
 Ok(!inner.is_dead)
 }
}
```

**ioctl —— trait  switch**

```rust
// Rust ——
// ( dispatcher )

// ioctl 
#[repr(u32)]
enum BinderIoctl {
 WriteRead = 0xc000, //  _IOWR macro 
 SetMaxThreads = 0xc001,
 SetContextMgr = 0xc002,
 ThreadExit = 0xc003,
 Version = 0xc004,
}

impl file::FileOperations for BinderDevice {
 type Data = Arc<Process>;
 type OpenData = ();

 fn ioctl(
 process: &Arc<Process>,
 _file: &File,
 cmd: u32,
 arg: usize,
 ) -> Result<u32> {
 match cmd.try_into() {
 Ok(BinderIoctl::WriteRead) => {
 let mut bwr: binder_write_read = unsafe { core::mem::zeroed() };
 // copy_from_user ——  IO buffer
 //  io_buffer  copy_from_user
 // ...
 Ok(0)
 }
 Ok(BinderIoctl::SetMaxThreads) => {
 let mut inner = process.inner.lock();
 inner.max_threads = arg as u32; // 
 Ok(0)
 }
 Ok(BinderIoctl::Version) => {
 // 
 Ok(BINDER_CURRENT_PROTOCOL_VERSION)
 }
 Err(_) => Err(Error::ENOTTY),
 }
 }
}
```

### 2.4 

|  | C  (binder.c) | Rust  (binder.rs) |
|------|------------------|---------------------|
|  | ~6000  | ~4500  25% |
|  |  `atomic_inc/dec` | `Arc<T>` Clone/Drop  |
|  |  | `Mutex<T>`  |
|  | goto  | `?`  |
| UAF  |  +  |  |
|  | lockdep | Send/Sync |
|  CVE |  UAF/ |  CVE 2025  |
|  |  C  |  Rust +  |

## 3. NVMe 

### 3.1 

NVMeNon-Volatile Memory Express SSD  PCIe  CPUNVMe  DMA

C  `drivers/nvme/host/pci.c` 4000 Rust Rust for Linux  3000 

### 3.2 C  DMA 

```c
// C DMA 
struct nvme_queue {
 struct nvme_dev *dev;
 spinlock_t q_lock;
 struct nvme_command *sq_cmds; // DMA
 struct nvme_completion *cqes; // DMA
 dma_addr_t sq_dma_addr; // 
 dma_addr_t cq_dma_addr; // 
 u32 sq_head;
 u32 sq_tail;
 u32 cq_head;
 u16 qid;
 u16 cq_vector;
 // ...
};

static int nvme_alloc_queue(struct nvme_queue **out_nvmeq, int qid)
{
 struct nvme_queue *nvmeq;

 nvmeq = kzalloc(sizeof(*nvmeq), GFP_KERNEL);
 if (!nvmeq)
 return -ENOMEM; //  cleanup

 // DMA 
 nvmeq->sq_cmds = dma_alloc_coherent(dev->dev, SQ_SIZE,
 &nvmeq->sq_dma_addr, GFP_KERNEL);
 if (!nvmeq->sq_cmds) {
 kfree(nvmeq); // 
 return -ENOMEM;
 }

 // 
 nvmeq->cqes = dma_alloc_coherent(dev->dev, CQ_SIZE,
 &nvmeq->cq_dma_addr, GFP_KERNEL);
 if (!nvmeq->cqes) {
 dma_free_coherent(dev->dev, SQ_SIZE, nvmeq->sq_cmds, nvmeq->sq_dma_addr);
 kfree(nvmeq);
 return -ENOMEM;
 }

 *out_nvmeq = nvmeq;
 return 0;
 //  3 
}

// ——
static irqreturn_t nvme_irq(int irq, void *data)
{
 struct nvme_queue *nvmeq = data;
 irqreturn_t ret = IRQ_NONE;
 u16 start, end;

 // 
 // 
 spin_lock(&nvmeq->q_lock);
 start = nvmeq->cq_head;
 end = nvmeq->cq_head;
 // ...
 spin_unlock(&nvmeq->q_lock);

 return ret;
}
```

### 3.3 Rust  DMA 

```rust
// Rust  rust/kernel/dma.rs 
use kernel::dma::{DmaAlloc, DmaDirection};

struct NvmeQueue {
 // DMA 
 sq: DmaAlloc<NvmeCommand>,
 cq: DmaAlloc<NvmeCompletion>,
 //  mutex 
 state: Mutex<QueueState>,
 // 
 _irq: IrqHandler<Self>,
}

struct QueueState {
 sq_head: u32,
 sq_tail: u32,
 cq_head: u32,
}

impl NvmeQueue {
 fn new(dev: &PciDevice, qid: u16) -> Result<Arc<Self>> {
 // DMA ——Drop 
 let sq = DmaAlloc::new(SQ_SIZE, dev, DmaDirection::Bidirectional, GFP_KERNEL)?;
 let cq = DmaAlloc::new(CQ_SIZE, dev, DmaDirection::Bidirectional, GFP_KERNEL)?;
 // ? 

 let queue = Arc::pin_init(
 pin_init!(NvmeQueue {
 sq,
 cq,
 state: Mutex::new(QueueState { sq_head: 0, sq_tail: 0, cq_head: 0 }),
 // IrqHandler  Drop 
 _irq: IrqHandler::register(irq_number, nvme_irq_handler)?,
 }),
 GFP_KERNEL,
 )?;

 Ok(queue)
 }

 // ——
 fn handle_irq(&self) -> IrqReturn {
 let mut state = self.state.lock(); // 
 // ... 
 IrqReturn::Handled
 }
}

// NvmeQueue  Drop 
// 1.  IrqHandler free_irq
// 2.  DmaAlloc  dma_free_coherent
// 3.  NvmeQueue 
// 
```

### 3.4 NVMe 

**DMA **
- C`dma_alloc_coherent`  `void *` `dma_free_coherent` UAF
- Rust`DmaAlloc<T>` `Drop` 

****
- C`free_irq`  `request_irq` 
- Rust`IrqHandler`  `Drop` Rust 

****
- C MMIO 
- Rust + `writeq` 

## 4. 

### 4.1 

 `/dev/mydevice` ioctl

### 4.2 C 

```c
// C ~120 
#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/uaccess.h>
#include <linux/io.h>

#define DEVICE_NAME "mydevice"
#define REG_SIZE 0x1000

struct my_device {
 void __iomem *regs;
 struct cdev cdev;
 dev_t devt;
};

static int my_open(struct inode *inode, struct file *filp)
{
 struct my_device *dev = container_of(inode->i_cdev,
 struct my_device, cdev);
 filp->private_data = dev;
 return 0;
}

static ssize_t my_read(struct file *filp, char __user *buf,
 size_t count, loff_t *off)
{
 struct my_device *dev = filp->private_data;
 u32 val;

 if (count < sizeof(val))
 return -EINVAL;

 val = ioread32(dev->regs + *off); // 

 if (copy_to_user(buf, &val, sizeof(val)))
 return -EFAULT;

 *off += sizeof(val);
 return sizeof(val);
}

static ssize_t my_write(struct file *filp, const char __user *buf,
 size_t count, loff_t *off)
{
 struct my_device *dev = filp->private_data;
 u32 val;

 if (count < sizeof(val))
 return -EINVAL;

 if (copy_from_user(&val, buf, sizeof(val)))
 return -EFAULT;

 iowrite32(val, dev->regs + *off); // 

 *off += sizeof(val);
 return sizeof(val);
}

static long my_ioctl(struct file *filp, unsigned int cmd, unsigned long arg)
{
 struct my_device *dev = filp->private_data;

 switch (cmd) {
 case 0x01: // 
 return ioread32(dev->regs + 0x100);
 case 0x02: // 
 iowrite32(0, dev->regs + 0x200);
 return 0;
 default:
 return -ENOTTY;
 }
}

static struct file_operations my_fops = {
 .owner = THIS_MODULE,
 .open = my_open,
 .read = my_read,
 .write = my_write,
 .unlocked_ioctl = my_ioctl,
};

static int my_probe(struct platform_device *pdev)
{
 struct my_device *dev;
 struct resource *res;
 int ret;

 dev = devm_kzalloc(&pdev->dev, sizeof(*dev), GFP_KERNEL);
 if (!dev)
 return -ENOMEM;

 res = platform_get_resource(pdev, IORESOURCE_MEM, 0);
 if (!res)
 return -ENODEV;

 dev->regs = devm_ioremap_resource(&pdev->dev, res);
 if (IS_ERR(dev->regs))
 return PTR_ERR(dev->regs);

 ret = alloc_chrdev_region(&dev->devt, 0, 1, DEVICE_NAME);
 if (ret)
 return ret;

 cdev_init(&dev->cdev, &my_fops);
 ret = cdev_add(&dev->cdev, dev->devt, 1);
 if (ret) {
 unregister_chrdev_region(dev->devt, 1);
 return ret;
 }

 platform_set_drvdata(pdev, dev);
 pr_info("mydevice: probed\n");
 return 0;
}

static int my_remove(struct platform_device *pdev)
{
 struct my_device *dev = platform_get_drvdata(pdev);
 cdev_del(&dev->cdev);
 unregister_chrdev_region(dev->devt, 1);
 // ioremap  devm 
 return 0;
}

static const struct of_device_id my_of_match[] = {
 { .compatible = "my,rust-device", },
 { /* sentinel */ }
};
MODULE_DEVICE_TABLE(of, my_of_match);

static struct platform_driver my_driver = {
 .probe = my_probe,
 .remove = my_remove,
 .driver = {
 .name = DEVICE_NAME,
 .of_match_table = my_of_match,
 },
};
module_platform_driver(my_driver);
MODULE_LICENSE("GPL");
```

**C **
1. `ioread32(dev->regs + *off)` — 
2. `iowrite32(val, dev->regs + *off)` — 
3. `filp->private_data` — 
4. `container_of` — 
5. `switch (cmd)` — 
6. `cdev_del` 

### 4.3 Rust 

```rust
// Rust ~130 
//  kernel crate  API 

use kernel::{
 cdev, chrdev,
 file::{File, FileOperations},
 io_buffer::{IoBufferReader, IoBufferWriter},
 platform,
 prelude::*,
 sync::SpinLock,
};

module! {
 type: MyDeviceDriver,
 name: "mydevice",
 author: "Demo",
 description: "Platform device demo in Rust",
 license: "GPL",
}

const REG_SIZE: usize = 0x1000;

/// ——MMIO 
struct MyDevice {
 regs: platform::IoMem<REG_SIZE>, //  IO
 // cdev  Registration 
}

/// 
struct OpenDevice {
 dev: Arc<MyDevice>,
}

#[vtable]
impl FileOperations for OpenDevice {
 type Data = Arc<MyDevice>;
 type OpenData = Arc<MyDevice>;

 fn open(dev: &Self::OpenData, _file: &File) -> Result<Self::Data> {
 pr_info!("mydevice: opened\n");
 Ok(dev.clone())
 }

 fn read(
 dev: &MyDevice,
 _file: &File,
 writer: &mut impl IoBufferWriter,
 offset: u64,
 ) -> Result<usize> {
 let offset = usize::try_from(offset)
 .map_err(|_| Error::ERANGE)?;

 // IoMem 
 let val = dev.regs.read32(offset)?; // offset  Error
 let bytes = val.to_le_bytes();
 writer.write_slice(&bytes)?;
 Ok(4)
 }

 fn write(
 dev: &MyDevice,
 _file: &File,
 reader: &mut impl IoBufferReader,
 offset: u64,
 ) -> Result<usize> {
 let offset = usize::try_from(offset)
 .map_err(|_| Error::ERANGE)?;

 let mut buf = [0u8; 4];
 reader.read_slice(&mut buf)?;
 let val = u32::from_le_bytes(buf);

 // IoMem 
 dev.regs.write32(offset, val)?;
 Ok(4)
 }

 fn ioctl(
 dev: &MyDevice,
 _file: &File,
 cmd: u32,
 _arg: usize,
 ) -> Result<u32> {
 match cmd {
 0x01 => {
 let status = dev.regs.read32(0x100)?;
 Ok(status)
 }
 0x02 => {
 dev.regs.write32(0x200, 0)?;
 Ok(0)
 }
 _ => Err(Error::ENOTTY),
 }
 }

 fn release(_data: Self::Data, _file: &File) {
 pr_info!("mydevice: released\n");
 }
}

/// 
struct MyDeviceDriver {
 _dev: Arc<MyDevice>,
 _cdev: chrdev::Registration<1>,
}

impl platform::Driver for MyDeviceDriver {
 type Data = Arc<MyDevice>;

 fn probe(
 pdev: &platform::Device,
 _id: Option<&platform::DeviceId>,
 ) -> Result<Self::Data> {
 pr_info!("mydevice: probing\n");

 //  MMIO ——
 let regs = pdev.ioremap_resource::<REG_SIZE>(0)?;

 let dev = Arc::new(MyDevice { regs }, GFP_KERNEL)?;

 Ok(dev)
 }
}

impl kernel::Module for MyDeviceDriver {
 fn init(module: &'static ThisModule) -> Result<Self> {
 pr_info!("mydevice: initializing\n");

 // 
 let platform_reg = platform::Driver::register(
 module,
 "mydevice",
 // 
 &[platform::DeviceId::new("my,rust-device")],
 // probe/remove  Driver trait 
 )?;

 // 
 let cdev = chrdev::Registration::new_pinned(
 module,
 "mydevice",
 0, // 
 )?;

 Ok(MyDeviceDriver {
 _dev: todo!("need device from probe"),
 _cdev: cdev,
 })
 }
}

impl Drop for MyDeviceDriver {
 fn drop(&mut self) {
 pr_info!("mydevice: unloaded\n");
 }
}
```

### 4.4 

|  | C  | Rust  |
|------|--------|----------|
| MMIO / | `ioread32(regs + off)` —  | `regs.read32(off)?` — + |
|  | `filp->private_data` (void *) | `Arc<MyDevice>` —  +  |
| CDEV  | `alloc_chrdev_region` + `cdev_init` + `cdev_add`  | `chrdev::Registration` Drop  |
|  | `if (ret) goto cleanup`  | `?`  |
|  |  | `usize::try_from` +  |
| of_match  |  sentinel |  |
|  |  devm  | Arc + Drop  |
|  | ~120  | ~130  |

## 5. 

### 5.1 

```
 C  C  Rust  Rust 
 (oops) (Option) 
 () (panic)
UAF 
 () 
 (lockdep) (Guard) 
 () 
 
IOMMU  () (panic)
 () () 
```

### 5.2 

 C ""
1. ****code review 2-3 
2. ****Sparse, Coverity, Coccinelle
3. ****KASANKMSANUBSANLockdep
4. ****Syzkaller

 Rust ****
-  →  KASAN  UAF 
- Send/Sync trait →  Lockdep 
-  →  Sparse 
- + →  switch 


- **** vs  vs 
- **** syzkaller  bug
- **** CVE 

## 6. 

### 6.1 

 LWN.net 

|  | C Binder | Rust Binder |  |
|----------|----------|------------|------|
| IPC  |  | ~99.5% |  |
| IPC 16 |  | ~101% |  |
| P50 |  | ~100% |  |
| P99 |  | ~99% |  |
|  |  | ~95% |  5% |

****Rust Rust 

### 6.2 Rust 

LLVM  Rust  IR C 
- `Arc::clone()` → `kref_get()` 
- `Mutex::lock()` → `mutex_lock()` 
- `Guard`  Drop → `mutex_unlock()` 
- `?`  →  C  `if (err) return err` 

Rust  C 

## 7. 

### 7.1 

**C **
```c
//  bug
static int foo(struct device *dev) {
 void *ptr = kmalloc(1024, GFP_KERNEL);
 //  ptr  NULL
 memset(ptr, 0, 1024); //  oops
 return 0;
}
```


**Rust **
```rust
fn foo() -> Result<()> {
 let mut v = Vec::with_capacity(1024, GFP_KERNEL)?; // ? 
 v.resize(1024, 0); // Vec  NULL
 Ok(())
}
```
 `unwrap()`  `?`clippy 

### 7.2 IDE 

 Rust  `vim`/`emacs` +  `rust-analyzer` 

```bash
# rust-project.json  make rust-analyzer 
#  rust-analyzer  crate
make LLVM=1 rust-analyzer
```

IDE 
-  crate 
- 
-  crate
- 

## 8.  C  Rust

### 8.1 

 ** C ** Binder 


1. ** Rust **
2. **** CVE Rust 
3. **C  Rust ** C Rust

### 8.2 C  Rust 

```makefile
#  C  Rust 
obj-m := hybrid_module.o
hybrid_module-y := c_part.o rust_part.o
# Kbuild  C (.c)  Rust (.rs) 
```

```c
// c_part.c —  Rust 
#include <linux/module.h>
extern int rust_function(int x); // Rust 
EXPORT_SYMBOL_GPL(rust_function);

// Rust  rust_part.rs
```

```rust
// rust_part.rs
use kernel::prelude::*;

#[no_mangle]
pub extern "C" fn rust_function(x: i32) -> i32 {
 x + 1
}
```

---

## [[03-]] | [[05-Rust]]

---
