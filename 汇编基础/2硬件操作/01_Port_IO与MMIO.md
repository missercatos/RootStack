# Port I/O 与 MMIO：两大硬件访问路径 (Port I/O & MMIO)
---

## 📖 章节概述

硬件操作的实质就是对"某个地址"读或写。但"地址"有两种——I/O 端口（独立的编号空间）和内存映射地址（共享物理内存空间）。本章深入解析这两条路径：`in`/`out` 指令如何操作 x86 专有的 64K 端口空间，`mov` 指令如何把设备寄存器当作内存来读写，以及在 CPU 层面这两种访问走的完全不同的总线周期。学完本章，你将能够读取键盘端口、写入 VGA 显存、以及通过 PCI 配置空间枚举设备。

> **核心理念**：Port I/O 和 MMIO 代表两种设计哲学——x86 的"地址空间隔离"（设备独立编号）vs ARM/RISC-V 的"统一地址空间"（一切皆内存）。两者各有优劣，但作为汇编程序员，你需要理解 CPU 在处理 `in al, 0x60` 和 `mov al, [0xB8000]` 时发生了完全不同的硬件动作。

---

### 📚 第一节：Port I/O —— x86 的专属通道

#### 1.1 独立的 64K 地址空间

x86 从 8086 时代就设计了独立的 I/O 地址空间，与内存地址空间物理隔离。这不是"内存的前 64K"——它是另一组物理导线、另一个总线协议：

```
内存地址空间                    I/O 端口空间
┌─────────────────┐           ┌─────────────────┐
│ 0x00000000      │           │ 0x0000          │
│    ...          │           │   键盘 0x60     │
│    ...          │           │   PIC  0x20     │
│ 0xFFFFFFFF      │           │   串口 0x3F8    │
│                 │           │   ...           │
│                 │           │ 0xFFFF          │
└─────────────────┘           └─────────────────┘
  mov 指令访问                  in/out 指令访问
```

#### 1.2 in / out 指令族

| 指令 | 操作数大小 | 含义 | 端口寻址方式 |
|------|-----------|------|------------|
| `in al, imm8` | 1 字节 | 从端口读 1 字节到 AL | 立即数（0~255） |
| `in ax, imm8` | 2 字节 | 从端口读 2 字节到 AX | 立即数（0~255） |
| `in eax, imm8` | 4 字节 | 从端口读 4 字节到 EAX | 立即数（0~255） |
| `in al, dx` | 1 字节 | 从端口读 1 字节到 AL | DX 寄存器（0~65535） |
| `in ax, dx` | 2 字节 | 从端口读 2 字节到 AX | DX 寄存器（0~65535） |
| `in eax, dx` | 4 字节 | 从端口读 4 字节到 EAX | DX 寄存器（0~65535） |
| `out imm8, al` | 1 字节 | 向端口写 1 字节 | 立即数 |
| `out imm8, ax` | 2 字节 | 向端口写 2 字节 | 立即数 |
| `out imm8, eax` | 4 字节 | 向端口写 4 字节 | 立即数 |
| `out dx, al` | 1 字节 | 向端口写 1 字节 | DX 寄存器 |
| `out dx, ax` | 2 字节 | 向端口写 2 字节 | DX 寄存器 |
| `out dx, eax` | 4 字节 | 向端口写 4 字节 | DX 寄存器 |
; AT&T 语法: inb $0x60, %al  |  outb %al, $0x60
;              inw $0x60, %ax  |  outw %ax, $0x60
;              inl $0x60, %eax |  outl %eax, $0x60
; 注意 AT&T 的操作数顺序与 Intel 相反 (源 ↔ 目标互换)
```

> 立即数寻址只支持 0~255（8 位端口号）。访问 256~65535 范围的端口必须使用 DX 寄存器间接寻址。

#### 1.3 IOPL：谁有权使用 in/out

EFLAGS 寄存器的 bits 12-13 记录了 IOPL（I/O Privilege Level）：

| IOPL 值 | 含义 |
|---------|------|
| 0 | 只有 Ring 0 可执行 in/out |
| 1 | Ring 0 和 Ring 1 可执行 |
| 2 | Ring 0~2 可执行 |
| 3 | 所有特权级可执行（极少见） |

Linux 将 IOPL 设为 0——意味着**用户态程序无法执行 `in`/`out` 指令**。这是 QEMU 裸机环境存在的核心原因之一。

> 用户态程序可以通过 `ioperm()` 或 `iopl()` 系统调用请求特定端口的访问权限（需要 root），但这本质是内核授予了你"临时特权"——并不改变 `in`/`out` 是特权指令的事实。

#### 1.4 实操：读取键盘扫描码

键盘控制器位于端口 0x60（数据）和 0x64（状态/命令）。当有按键时，0x60 端口保持最后一个字节的扫描码：

```asm
; read_key.asm — 读取键盘扫描码（需在 QEMU/裸机环境运行）
; 编译: nasm -f bin read_key.asm -o read_key.bin
; 运行: qemu-system-x86_64 -drive file=read_key.bin,format=raw -nographic

[BITS 16]
[ORG 0x7C00]

start:
    ; 等待键盘控制器输出缓冲区有数据
    in al, 0x64          ; 读键盘状态端口
    test al, 1           ; bit 0 = 输出缓冲区满
    jz start             ; 如果为空则继续轮询

    in al, 0x60          ; 读扫描码
    ; al 现在包含按键的扫描码（make code）
    ; 例如: 'A' 键按下 → 0x1E, 释放 → 0x9E

    ; 向串口输出（可选，用于 QEMU -serial stdio）
    mov dx, 0x3F8        ; COM1 数据端口
    out dx, al

    jmp start

times 510-($-$$) db 0
dw 0xAA55               ; 引导扇区签名
```

> 这段代码无法在 Linux 用户态运行——`in al, 0x64` 会被 CPU 拦截。你必须在 QEMU 裸机中测试。详细环境配置见 [[../1基础/04_工具链与调试环境#📚 第五节：QEMU 虚拟裸机环境|QEMU 环境搭建]]。

#### 1.5 PCI 配置空间：Port I/O 的高级应用

PCI 设备通过两个 32 位端口暴露配置空间：

```
端口 0xCF8 — CONFIG_ADDRESS（配置地址寄存器）
端口 0xCFC — CONFIG_DATA   （配置数据寄存器）

访问流程:
1. 向 0xCF8 写入目标地址（总线号+设备号+功能号+寄存器偏移）
2. 从 0xCFC 读/写 32 位数据
```

```asm
; pci_read.asm — 读取 PCI 设备的 Vendor ID（需 QEMU 裸机环境）
; 读取总线0、设备0、功能0、偏移0 = Vendor ID + Device ID

; Step 1: 构造 CONFIG_ADDRESS
mov eax, 0x80000000     ; bit 31 (Enable) = 1
                        ; bits 23:16 = Bus   (0)
                        ; bits 15:11 = Device (0)
                        ; bits 10:8  = Function (0)
                        ; bits 7:0   = Register offset (0)
mov dx, 0xCF8
out dx, eax

; Step 2: 读取 CONFIG_DATA
mov dx, 0xCFC
in eax, dx              ; eax = Device ID << 16 | Vendor ID
; 低 16 位 = Vendor ID (例如 Intel = 0x8086)
; 高 16 位 = Device ID
```

---

### 📚 第二节：MMIO —— 一切皆内存

#### 2.1 工作原理

MMIO（Memory-Mapped I/O）的核心思想极其简单：**把设备寄存器映射到物理地址空间的某个区域**。CPU 不知道（也不需要知道）某个地址对应的是 RAM 还是设备寄存器——它只负责执行 `mov` 指令，芯片组负责将总线周期路由到正确的目标。

```
物理地址空间布局（x86 典型）:

0x00000000 ┌────────────┐
           │   RAM      │ ← 普通内存
0x000A0000 ├────────────┤
           │   VGA 显存  │ ← 0xB8000 (文本模式), 0xA0000 (图形模式)
0x000C0000 ├────────────┤
           │  BIOS ROM  │ ← 固件（不可写）
0x000FFFFF ├────────────┤
           │   RAM      │ ← 扩展内存...
  ...      │            │
0xFEE00000 ├────────────┤
           │  LAPIC     │ ← Local APIC 寄存器 (MMIO)
0xFEC00000 ├────────────┤
           │  I/O APIC  │ ← I/O APIC 寄存器
0xFED00000 ├────────────┤
           │  HPET      │ ← 高精度定时器
...        │            │
```

#### 2.2 写 VGA 显存：最直观的 MMIO

```asm
; vga_write.asm — 向 VGA 文本模式显存写入彩色字符
; 在 QEMU 裸机环境或 DOS 环境中运行
; 物理地址: 0xB8000 是 VGA 文本模式显存的起始地址

[BITS 16]
[ORG 0x7C00]

start:
    mov ax, 0xB800
    mov es, ax           ; ES:DI = 0xB800:0000 → 物理 0xB8000

    ; 清屏（80列×25行）
    mov cx, 80 * 25
    xor di, di
    mov ax, 0x0F20       ; 属性0x0F(白底黑字) + 空格0x20
    rep stosw

    ; 第 0 行: 输出红色 'H' (属性 0x04 = 红字黑底)
    mov word [es:0], 0x0448     ; 'H', 红字

    ; 第 0 行第1列: 绿色 'i' (属性 0x02)
    mov word [es:2], 0x0269     ; 'i', 绿字

    ; 第 12 行居中: 输出一条消息
    mov di, (12 * 80 + 30) * 2  ; 第12行, 第30列, 每字符2字节
    mov si, message
    mov ah, 0x0E                ; 黄字黑底
.loop:
    lodsb
    test al, al
    jz .halt
    mov [es:di], ax
    add di, 2
    jmp .loop

.halt:
    hlt
    jmp .halt

message db 'Hello from MMIO!', 0

times 510-($-$$) db 0
dw 0xAA55
```

#### 2.3 CPU 层面：mov 的"另一面"

同样是 `mov` 指令，CPU 内部对 MMIO 访问和 RAM 访问有微妙但关键的区别：

```
mov eax, [普通RAM地址]    →  Cache hit → 快速返回
                           →  Cache miss → 从 RAM 读取 → 填入 cache → 返回

mov eax, [MMIO设备寄存器]  →  不可缓存 (Uncacheable)
                           →  直接发出内存总线周期
                           →  芯片组识别地址范围，路由到 PCIe/设备总线
                           →  设备解码地址，返回寄存器值
```

> 这就是为什么设备驱动中常用 `volatile` 修饰 MMIO 指针——告诉编译器"每次必须真实读写，不要优化成寄存器缓存"。

#### 2.4 内存屏障指令

MMIO 的异步特性带来了顺序问题——CPU 和编译器可能重排内存访问。以下屏障指令强制顺序：

| 指令 | 全称 | 作用 |
|------|------|------|
| `mfence` | Memory Fence | 保证所有之前的 load/store 在之后的 load/store 前完成 |
| `sfence` | Store Fence | 保证所有之前的 store 在之后的 store 前完成 |
| `lfence` | Load Fence | 保证所有之前的 load 在之后的 load 前完成 |

```asm
; 典型的设备驱动写序列
mov dword [dev_cmd_reg], 0x01    ; 向设备发送"开始DMA"命令
sfence                           ; 确保命令写入完成
mov dword [dev_status_reg], 0    ; 然后才能清除状态寄存器
```

> C 代码中对应 `asm volatile("sfence":::"memory")` — 此 C 代码无法表达 → 你必须使用内联汇编。详见 [[./03_内联汇编精通|内联汇编精通]]。

---

### 📚 第三节：Port I/O vs MMIO —— 全面对比

| 维度 | Port I/O | MMIO |
|------|---------|------|
| **地址空间** | 独立 64K（65,536 端口） | 共享物理地址空间（可达 2^52 字节） |
| **访问指令** | `in` / `out` / `ins` / `outs` | `mov`（和所有其他内存指令） |
| **C 语言支持** | ❌ 无 C 语法 → 必须内联汇编 | ✅ 用 `volatile` 指针访问（需内核映射） |
| **架构支持** | x86 专有 | 所有现代架构（x86, ARM, RISC-V, MIPS） |
| **缓存行为** | 不经过缓存（in/out 自带序列化） | 可配置（通常 UC: Uncacheable） |
| **排序保证** | 强保证（in/out 像序列化指令） | 无保证 → 需 `mfence`/`sfence`/`lfence` |
| **速度** | 较慢（专用总线协议，一次 1/2/4 字节） | 较快（可用 burst 传输、WC/USWC 内存类型） |
| **典型用途** | 旧式设备（键盘、PIC、PIT、串口、PCI 配置） | 现代设备（PCIe BAR、APIC、HPET、VGA、NVMe） |
| **访问粒度** | 1/2/4 字节（inb/inw/inl）| 任意（mov byte/word/dword/qword） |
| **调试可见** | QEMU Monitor: `info pic` 等命令 | QEMU Monitor: `xp`（查看物理内存） |

> 简言之：Port I/O 是 x86 的"历史遗产"——设计时内存很贵（640K"足够"），独立 64K 端口空间似乎是个好主意。现在回头看，每个现代架构（包括 x86 的新设备）都倾向 MMIO——统一地址空间设计更简洁、更快。

---

### 📚 第四节：在 C 语言中揭开的"遮羞布"

C 语言不能直接执行 `in`/`out` 指令，但可以通过两种方式间接使用：

#### 4.1 Linux 用户态：ioperm 系统调用

```c
#include <sys/io.h>
#include <stdio.h>

int main() {
    // 请求端口 0x60 的访问权限（需要 root）
    if (ioperm(0x60, 1, 1) != 0) {
        perror("ioperm");
        return 1;
    }

    unsigned char scancode = inb(0x60);  // 实际是一个函数调用
    // 在 glibc 中，inb() 封装了内联汇编的 in 指令
    printf("Scancode: 0x%02X\n", scancode);
    return 0;
}
```

> `inb()` 不是 C 语言的语法——它是 glibc 提供的宏/函数，内部是内联汇编。此 C 代码无法直接表达 `in` 指令，你看到的 `inb()` 本质上就是汇编的包装。

#### 4.2 内联汇编直接使用

```c
// 用 GCC 内联汇编直接操作端口
unsigned char read_port(unsigned short port) {
    unsigned char value;
    asm volatile("inb %1, %0"
                 : "=a"(value)      // value 放入 al
                 : "Nd"(port));     // port 作为立即数或 DX
    return value;
}

void write_port(unsigned short port, unsigned char value) {
    asm volatile("outb %0, %1"
                 :: "a"(value), "Nd"(port));
}
```

> 内联汇编的完整约束语法见 [[./03_内联汇编精通|内联汇编精通]] 章节——那里会覆盖全部 `asm volatile` 的约束规则。

---

### 📝 小节练习

> [!question] 选择题 1
> `in al, dx` 与 `in al, 0x60` 的操作数区别是什么？
> - [ ] A. 没有区别
> - [ ] B. `dx` 方式可访问 0~65535 端口，立即数方式仅限 0~255
> - [ ] C. `in al, dx` 快一倍
> - [ ] D. `in al, 0x60` 是 32 位传输
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 立即数寻址的 `in al, imm8` 只支持 8 位（0~255）端口号。使用 DX 寄存器间接寻址可以访问完整的 0~65535 端口范围。

> [!question] 选择题 2
> PCI 配置空间访问使用了哪两个 I/O 端口？
> - [ ] A. 0x60 和 0x64
> - [ ] B. 0x3F8 和 0x3F9
> - [ ] C. 0xCF8 和 0xCFC
> - [ ] D. 0x20 和 0x21
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: `0xCF8` 是 PCI CONFIG_ADDRESS 寄存器（写入目标地址），`0xCFC` 是 PCI CONFIG_DATA 寄存器（读写数据）。

> [!question] 判断题 1
> ARM 架构的 CPU 同样支持 `in`/`out` 端口 I/O 指令。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `in`/`out` 是 x86 专有指令。ARM 和 RISC-V 没有独立的 I/O 地址空间概念，所有设备访问都通过 MMIO（用 `ldr`/`str` 指令操作映射后的设备寄存器地址）。

---

## 📋 章节测试

### 一、判断题

> [!question] 判断题 1
> `out 0x60, al` 与 `mov [0x60], al` 在 x86 CPU 上执行的总线周期完全相同。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `out` 走 I/O 总线周期（IOR/IOW 信号），`mov [addr]` 走内存总线周期（MEMR/MEMW 信号）——CPU 引脚上的电信号就不同。这是物理层面的区别。

> [!question] 判断题 2
> VGA 文本模式的显存物理地址是 0xB8000，可通过 MMIO 方式用 `mov` 指令直接写入。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: 0xB8000 是物理地址，CPU 通过内存总线访问。在裸机/实模式下可以直接读写——这正是 MMIO 的标准用法。

> [!question] 判断题 3
> `sfence` 指令保证在其之前的所有 store 操作在之后的 store 操作之前完成，但不影响 load 操作的顺序。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `sfence` (Store Fence) 只序列化写操作。`lfence` 序列化读操作，`mfence` 同时序列化读和写。

> [!question] 判断题 4
> Linux 用户态程序可以通过 `ioperm()` 获取端口 I/O 权限后直接在 C 代码中使用 `in`/`out` 汇编指令而无需内联汇编。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `ioperm()` 只修改 I/O 权限位图——允许进程执行 `in`/`out` 指令，但 C 语言本身仍然不支持 `in`/`out` 指令。你仍然需要通过内联汇编或使用 glibc 的 `inb()`/`outb()` 封装函数（它们内部包含内联汇编）。

> [!question] 判断题 5
> MMIO 设备寄存器通常被映射为 Uncacheable（UC）内存类型，因为设备寄存器的值可能随时被硬件改变。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: 如果缓存设备寄存器，CPU 可能读到的是缓存中的旧值而非设备最新状态。MTRR（Memory Type Range Register）或 PAT（Page Attribute Table）用于将 MMIO 区域标记为 UC。

### 二、选择题

> [!question] 选择题 1
> 以下哪条指令是合法的 x86 Port I/O 写操作？
> - [ ] A. `out al, 0x60`
> - [ ] B. `out 0x60, al`
> - [ ] C. `mov [0x60], al`
> - [ ] D. `write 0x60, al`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: Intel 语法中 `out` 的格式是 `out 端口, 数据`。端口在前，数据（al/ax/eax）在后。AT&T 语法相反：`outb %al, $0x60`。

> [!question] 选择题 2
> 以下哪个端口是键盘控制器的数据端口？
> - [ ] A. 0x3F8
> - [ ] B. 0x20
> - [ ] C. 0x60
> - [ ] D. 0xCF8
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: 0x60 = 键盘数据寄存器（读 = 扫描码，写 = 键盘命令响应）。0x64 = 键盘状态/命令寄存器。0x3F8 = COM1 串口，0x20 = 主 PIC，0xCF8 = PCI 配置地址。

> [!question] 选择题 3
> MMIO 访问中，`volatile` 关键字在 C 语言中的作用是？
> - [ ] A. 防止编译器将该变量放到寄存器中
> - [ ] B. 使变量变为常量
> - [ ] C. 加速内存访问
> - [ ] D. 将变量存储在 ROM 中
>
> > [!success]- 点击查看答案
> > 正确答案: A
> > **解析**: `volatile` 告诉编译器"每次访问必须从内存读写，禁止优化为寄存器缓存"。对于 MMIO 设备寄存器，这是必须的——因为硬件可以随时改变这些值。

> [!question] 选择题 4
> IOPL（I/O Privilege Level）存储在哪个寄存器中？
> - [ ] A. CR0
> - [ ] B. EAX
> - [ ] C. EFLAGS (bits 12-13)
> - [ ] D. CS
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: IOPL 存储在 EFLAGS 寄存器的第 12 和第 13 位。它指定了可以执行 `in`/`out`/`cli`/`sti` 指令所需的最低特权级。

> [!question] 选择题 5
> 下列关于 PCI 配置空间访问流程的描述，正确的是？
> - [ ] A. 直接向 0xCFC 读即可，无需设置 0xCF8
> - [ ] B. 先向 0xCF8 写入目标地址（含 Enable 位），再从 0xCFC 读写数据
> - [ ] C. 只能通过 MMIO 访问
> - [ ] D. 0xCF8 和 0xCFC 是两个独立的端口，不需要配合使用
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 先向 CONFIG_ADDRESS（0xCF8）写入 32 位目标地址（需设置 bit 31 Enable 位），然后对 CONFIG_DATA（0xCFC）进行读/写操作。这是标准的"地址-数据"寄存器对模式。

---

### 🛠️ 动手练习题

> [!example] 练习题 1：键盘扫描码读取器
> **难度**: ⭐⭐
>
> 编写一个 QEMU 裸机程序（`-f bin`），持续轮询键盘端口（0x64 状态 + 0x60 数据），当有按键时打印扫描码到 VGA 显存（0xB8000）。要求：
> - 区分按键按下（make code）和释放（break code = make code | 0x80）
> - 用不同颜色显示按下和释放事件
> - 用你之前编写的读写逻辑组合成完整程序
>
> 提示：键盘状态端口 0x64 的 bit 0 为 1 表示输出缓冲区有数据可读。

> [!example] 练习题 2：VGA 彩虹屏幕
> **难度**: ⭐⭐
>
> 在 QEMU 裸机中，用 `rep stosw` 指令填充 VGA 显存，将屏幕的每一行（80 列）设为不同的颜色属性。要求：
> - 行 0：黑底红字 (0x04)
> - 行 1：黑底绿字 (0x02)
> - 以此类推，共 16 种颜色组合（0x00 ~ 0x0F）
> - 每行显示该行的颜色编号（用字符 '0'-'F'）
>
> 这题让你体会到"汇编操作显存"等同于"C 操作数组"——但汇编不做类型检查，直接写物理地址。

> [!example] 练习题 3：PCI 设备枚举
> **难度**: ⭐⭐⭐
>
> 在 QEMU 裸机中，编写代码扫描 PCI 总线 0 上的前 8 个设备（设备 0~7，功能 0），读取每个设备的 Vendor ID（偏移 0x00，16 位）和 Device ID（偏移 0x02，16 位）。在 VGA 屏幕上以表格形式显示：
> ```
> Dev:0 Vend:0x8086 DevID:0x1237  ← Intel 440FX 或 QEMU 模拟设备
> Dev:1 Vend:0x8086 DevID:0x7000  ← PIIX3 ISA Bridge
> ...
> ```
> 这题综合了 Port I/O（PCI 配置访问）、MMIO（VGA 输出）和循环结构。
