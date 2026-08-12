# 中断与 IDT：硬件通知 CPU 的机制 (Interrupts & IDT)
---

## 📖 章节概述

中断是硬件与 CPU 之间最基础的通信协议。当键盘被按下、网卡收到数据包、时钟走了一拍——硬件通过中断信号告诉 CPU "我有事找你"。CPU 暂停当前执行流，查阅 IDT（Interrupt Descriptor Table）找到对应处理器，执行完成后再用 `iret` 回到原位置。本章从零搭建完整的中断系统：IDT 结构、PIC 8259 初始化、用纯汇编编写 ISR（Interrupt Service Routine），并在 QEMU 裸机上看到键盘按键和时钟嘀嗒。

> **核心理念**：This is ONLY possible in assembly — 中断入口的现场保存（push 所有寄存器）和恢复（pop + iret）是 C 语言无法表达的。C 可以写 ISR 的函数体，但 ISR 的**入口**和**出口**必须是汇编。本教程不依赖 C，全部用 NASM 完成——让你看见 CPU 收到中断信号的每一个指令周期。

---

### 📚 第一节：中断向量与分类
---

x86 架构定义了 **256 个中断向量**（0 ~ 255），按来源分为三类：

| 向量范围 | 来源 | 示例 |
|----------|------|------|
| 0 ~ 31 | CPU 异常（Exception） | 除零错误(0)、NMI(2)、断点(3)、缺页(14)、双重错误(8) |
| 32 ~ 47 | 硬件 IRQ（通过 PIC） | 时钟 IRQ0、键盘 IRQ1、串口 COM1 IRQ4 |
| 48 ~ 255 | 软件中断 / 用户定义 | Linux `int 0x80`（32 位系统调用） |

**常见 CPU 异常：**

| 向量 | 名称 | 触发条件 | CPU 处理 |
|------|------|----------|----------|
| 0 | #DE (Divide Error) | `div` 指令除数为零或商溢出 | 发送异常 0 |
| 1 | #DB (Debug) | 单步调试 / 硬件断点 | 调试器用 |
| 2 | NMI | 硬件不可屏蔽中断 | 内存校验错等 |
| 3 | #BP (Breakpoint) | `int3` 指令 | GDB 断点的硬件基础 |
| 6 | #UD (Invalid Opcode) | 执行未定义的机器码 | CPU 不认识这条指令 |
| 8 | #DF (Double Fault) | 处理异常时又发生异常 | 严重——通常系统崩溃 |
| 13 | #GP (General Protection) | 段权限违规、MSR 越权访问等 | 用户态执行 `cli` 触发 |
| 14 | #PF (Page Fault) | 页表项不存在或权限错误 | 缺页中断——虚拟内存的基础 |
| 15 | — (Reserved by Intel) | — | — |
| 16 | #MF (x87 FPU) | x87 浮点异常 | — |

> 异常是**同步**的——由 CPU 正在执行的指令触发。IRQ 是**异步**的——可以在任何指令边界到达。这是 `[[../1基础/01_寄存器与指令基础|指令集]]` 层面无法回避的硬件事实。

**硬件 IRQ 的默认映射问题：**

Intel 规定 IRQ 0~15 通过 8259 PIC（Programmable Interrupt Controller）送入 CPU。默认映射下：
- **IRQ 0~7 映射到中断向量 0x08~0x0F**
- 但向量 0x08 ~ 0x0F 正好与 CPU 异常重叠（#DF 在 0x08）！

这意味着如果不重新映射 PIC，一个时钟中断可能被 CPU 当作 Double Fault 处理——系统立即崩溃。因此 **PIC 重映射是所有中断编程的第一步**（详见第四节）。

```asm
; AT&T 语法等价示例（GCC 内联汇编中常见）：
; IRQ 号与中断向量的关系：Vector = IRQ + PIC_OFFSET
; 重映射后：IRQ0 → 0x20, IRQ1 → 0x21, ... IRQ7 → 0x27
```

### 📝 小节练习

> [!question] 判断题 1
> 缺页异常（Page Fault）是硬件 IRQ 而非 CPU 异常。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 缺页异常（向量 14）是 CPU 在地址转换时发现页表项无效或权限不足而**同步**产生的异常，不是异步 IRQ。它是虚拟内存管理的基础机制。

> [!question] 选择题 1
> PIC 默认将 IRQ0 映射到哪个中断向量？
> - [ ] A. 0x00
> - [ ] B. 0x08
> - [ ] C. 0x20
> - [ ] D. 0x80
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: PIC 默认 IRQ 0~7 映射到中断向量 0x08~0x0F，与 CPU 异常向量（0x00~0x1F）重叠，必须通过重映射避开冲突。

---

### 📚 第二节：IDT 结构与 IDTR 寄存器
---

#### 2.1 IDT：中断描述符表

IDT 是一张存放在内存中的表，共 256 项，每项 8 字节（32 位保护模式下）。每一项称为一个"门描述符"（Gate Descriptor），告诉 CPU：当中断 N 发生时，跳转到哪个地址、用哪个代码段、以什么权限执行。

**32 位中断门描述符结构（8 字节）：**

```
 63                             48 47   45 44    40 39   37     32
+----------------------------------+------+-------+------+--------+
| Handler Offset 31:16             |  P   |  DPL  |  0   | Type   |
+----------------------------------+------+-------+------+--------+
 31           16 15                           0
+---------------+-----------------------------+
| Seg Selector  | Handler Offset 15:0          |
+---------------+-----------------------------+
```

| 字段 | 位 | 含义 |
|------|-----|------|
| Offset 15:0 | [15:0] | 处理器入口地址的低 16 位 |
| Segment Selector | [31:16] | 代码段选择子（通常 0x08 = GDT 第 1 项） |
| Reserved | [39:32] | 必须为 0（否则 CPU 报 #GP） |
| Type | [40:43] | 门类型：0xE = 32 位中断门，0xF = 32 位陷阱门 |
| S (Storage) | [44] | 0 = 系统段/门 |
| DPL | [45:46] | 特权级（00 = Ring0, 11 = Ring3） |
| P (Present) | [47] | 1 = 有效，0 = 不存在 |
| Offset 31:16 | [63:48] | 处理器入口地址的高 16 位 |

> 构建一个 IDT 门描述符 = 把处理器地址切成三块分别填入 bit[15:0], bit[31:16], bit[63:48]，再把段选择子写入 bit[31:16]。**This is ONLY possible in assembly**——C 语言里没有"把某个函数地址的某 16 位填到特定内存偏移"的语法，但 NASM 的 `mov word [idt+N*8], ax` 一行搞定。

#### 2.2 IDTR 寄存器 与 `lidt` 指令

IDT 的基地址和大小存储在 **IDTR**（IDT Register）中——CPU 用 `lidt` 指令加载：

```
IDTR 结构 (48 位):
 47                 16 15          0
+--------------------+-------------+
| IDT Base (32-bit)  | Limit (16b) |
+--------------------+-------------+
```

```asm
; 内存中定义 IDT 描述符，然后 lidt 加载
idt_descriptor:
    dw 256*8 - 1      ; Limit = 表大小 - 1
    dd idt             ; Base  = IDT 基地址（32 位物理地址）

section .text
    lidt [idt_descriptor]   ; 一条指令，CPU 从此知道中断来了往哪跳
```

`lidt` 是**特权指令**——只能在 Ring0 执行。这就是为什么用户态程序不能"安装"自己的中断处理器；只有操作系统内核（或裸机程序）才能操作 IDT。我们的 QEMU 裸机程序天然运行在 Ring0。

> `[[../1基础/04_工具链与调试环境|工具链章节]]` 中演示的 Linux 用户态 NASM 程序无法执行 `lidt`——会触发 #GP 异常。裸机环境是学习中断系统的唯一途径。

#### 2.3 中断门 vs 陷阱门

| 属性 | 中断门 (Type=0xE) | 陷阱门 (Type=0xF) |
|------|-------------------|-------------------|
| 进入时 IF 标志 | **自动清除**（关中断） | **保持不变** |
| 用途 | 硬件 IRQ 处理器 | 异常处理器、系统调用 |
| `iret` 返回时 IF | 恢复原值 | 恢复原值 |

> 硬件 IRQ 必须用中断门——你不想在处理一个 IRQ 时被同一个 IRQ 嵌套打断。陷阱门则用于异常和软件中断，保留原中断状态。

### 📝 小节练习

> [!question] 选择题 1
> 32 位保护模式下，一个 IDT 表项占多少字节？
> - [ ] A. 4 字节
> - [ ] B. 8 字节
> - [ ] C. 16 字节
> - [ ] D. 12 字节
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 32 位保护模式下每个 IDT 门描述符为 8 字节。64 位长模式下为 16 字节。256 个表项 × 8 = 2048 字节。

> [!question] 判断题 1
> `lidt` 指令可以用于 Linux 用户态程序。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `lidt` 是 Ring0 特权指令，用户态（Ring3）执行会触发 #GP（一般保护异常）。只有操作系统内核或裸机程序能使用。

---

### 📚 第三节：编写中断处理器（ISR）
---

#### 3.1 ISR 的基本骨架

每一个 ISR（Interrupt Service Routine）必须遵循以下模式：

```asm
isr_timer:
    pusha               ; ① 保存所有通用寄存器（eax, ecx, edx, ebx, esp, ebp, esi, edi）
                        ;    注意：段寄存器 (ds, es, fs, gs) 根据需要保存
                        
    ; === ② 处理中断逻辑 ===
    ;     硬件 IRQ：读取数据、更新计数器、处理设备状态
    
    mov al, 0x20        ; ③ 如果是硬件 IRQ：发送 EOI 给 PIC
    out 0x20, al        ;    告诉 PIC "处理完毕，可以发送下一个中断"
    
    popa                ; ④ 恢复通用寄存器（与 pusha 顺序相反）
    iret                ; ⑤ 中断返回——弹出 EIP、CS、EFLAGS
```

> **关键细节**：`pusha` 保存的是 `eax, ecx, edx, ebx, 原 esp, ebp, esi, edi`（共 8 个 32 位寄存器 = 32 字节）。`popa` 按相反顺序恢复（除了 `esp`——`popa` 会丢弃保存的 esp 值以保持当前栈指针不变）。

**ISR 入口"必须用汇编"的原因：**

```
C 函数入口（GCC 生成）：
    push rbp             ← 这已经是第二条指令了
    mov rbp, rsp
    
ISR 入口（必须用汇编）：
    pusha                ← 必须在任何 C 代码前保存 ALL 寄存器
    ...                   ← C 代码不知道哪些寄存器被中断打断
    popa                 ← 必须在返回前恢复 ALL 寄存器
    iret                 ← C 没有 iret——它甚至不是 C 关键字
```

> C 编译器不会生成 `pusha`/`popa`/`iret`。函数调用约定只要求保存被调用者保存寄存器（rbx/rbp/r12~15），但 ISR 可能在任何指令边界触发——被打断的代码可能正持有 `eax` 的关键中间结果。**Only assembly can guarantee full context save and restore.**

#### 3.2 cli / sti：手动控制中断

```asm
cli          ; Clear Interrupt Flag → 禁止硬件中断（NMI 除外）
; ... 临界区代码 ...
sti          ; Set Interrupt Flag → 允许硬件中断
```

| 指令 | 全称 | 效果 | 使用场景 |
|------|------|------|----------|
| `cli` | Clear Interrupt Flag | IF ← 0，屏蔽可屏蔽中断 | 保护临界区、修改 IDT 时 |
| `sti` | Set Interrupt Flag | IF ← 1，允许可屏蔽中断 | 初始化完成后开启中断 |

> `cli`/`sti` 在用户态执行会触发 #GP。这也是为什么 C 语言用户态程序无法屏蔽中断——**只有汇编的裸机代码才能完全控制 CPU 的中断标志**。

### 📝 小节练习

> [!question] 选择题 1
> `pusha` 指令在 32 位模式下保存几个寄存器？
> - [ ] A. 4 个
> - [ ] B. 6 个
> - [ ] C. 8 个
> - [ ] D. 16 个
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: `pusha` 保存 8 个 32 位通用寄存器：`eax, ecx, edx, ebx, esp, ebp, esi, edi`。不保存段寄存器和标志寄存器（标志由 `iret` 从栈中恢复）。

> [!question] 判断题 1
> C 语言函数可以直接使用 `iret` 指令返回。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: C 编译器不生成 `iret` 指令。普通函数用 `ret` 返回（弹出返回地址），ISR 必须用 `iret`（额外弹出 CS 和 EFLAGS）。即使 C 函数被注册为 ISR，其**入口入口和出口**仍必须由汇编 wrapper 提供。

---

### 📚 第四节：PIC 8259 可编程中断控制器
---

#### 4.1 PIC 架构

x86 平台传统上有两个级联的 8259 PIC：

```
         ┌──────────────┐
IRQ0 ──▶ │              │
IRQ1 ──▶ │  Master PIC  │────▶ CPU INTR 引脚
...      │  Port 0x20   │
IRQ7 ──▶ │  (data 0x21) │
         │              │
         │  IRQ2 ──────────┐
         └──────────────┘  │   ┌──────────────┐
                           └─▶ │  Slave PIC   │
                    IRQ8 ──▶  │  Port 0xA0    │
                    ...       │  (data 0xA1)  │
                    IRQ15──▶  └──────────────┘
```

| 端口 | 用途 |
|------|------|
| 0x20 | 主 PIC 命令端口 |
| 0x21 | 主 PIC 数据端口 |
| 0xA0 | 从 PIC 命令端口 |
| 0xA1 | 从 PIC 数据端口 |

常见 IRQ 分配：

| IRQ | 设备 |
|-----|------|
| 0 | 8253/8254 PIT 定时器 |
| 1 | PS/2 键盘 |
| 2 | 级联从 PIC |
| 3 | COM2 / COM4 |
| 4 | COM1 / COM3 串口 |
| 5 | LPT2 / 声卡 |
| 6 | 软盘控制器 |
| 7 | LPT1 并口 |
| 8 | RTC 实时时钟 |
| 9 | ACPI / 网卡 (PCI) |
| 12 | PS/2 鼠标 |
| 14 | 主 IDE 控制器 |
| 15 | 从 IDE 控制器 |

#### 4.2 ICW1 ~ ICW4：PIC 初始化序列

PIC 必须按固定顺序初始化——四个 ICW（Initialization Command Word）：

```asm
; ============ PIC 重映射 ============
; 将 IRQ 0~7 映射到 0x20~0x27
; 将 IRQ 8~15 映射到 0x28~0x2F
;
; 步骤固定，不可调换顺序！

pic_remap:
    ; --- ICW1: 开始初始化，告诉 PIC 后面有 ICW4 ---
    mov al, 0x11        ; 0x11 = ICW1_INIT (bit4) | ICW1_ICW4 (bit0)
    out 0x20, al        ; 写入主 PIC 命令端口
    out 0xA0, al        ; 写入从 PIC 命令端口
    ; 注: out 之间需要等待 PIC 处理（约 1-2 μs），用 I/O 端口延迟实现
    call io_wait

    ; --- ICW2: 设置中断向量偏移 ---
    mov al, 0x20        ; 主 PIC: IRQ 0~7 → 向量 0x20~0x27
    out 0x21, al
    mov al, 0x28        ; 从 PIC: IRQ 8~15 → 向量 0x28~0x2F
    out 0xA1, al
    call io_wait

    ; --- ICW3: 告诉主 PIC IRQ2 级联了从 PIC ---
    mov al, 0x04        ; 主 PIC: IRQ2 是从 PIC（bit2 = 1）
    out 0x21, al
    mov al, 0x02        ; 从 PIC: 我是通过 IRQ2 级联的（标识 = 2）
    out 0xA1, al
    call io_wait

    ; --- ICW4: 设置工作模式 ---
    mov al, 0x01        ; 0x01 = 8086/8088 模式（不是 8080 模式）
    out 0x21, al        ;    bit0 = 1 表示 x86 模式
    out 0xA1, al
    call io_wait

    ; --- 设置中断屏蔽寄存器（IMR）---
    ; bit = 0 → 开放该 IRQ, bit = 1 → 屏蔽该 IRQ
    mov al, 0xFC        ; 0xFC = 1111 1100 → 只开放 IRQ0(时钟) 和 IRQ1(键盘)
    out 0x21, al        ; 屏蔽主 PIC 的 IRQ2~7
    mov al, 0xFF        ; 屏蔽从 PIC 的所有 IRQ（暂时不需要）
    out 0xA1, al

    ret

io_wait:
    ; 向未使用的端口写入 0：消耗约 1-2μs，给 PIC 处理时间
    out 0x80, al        ; 端口 0x80 是 POST 诊断端口，通常安全用于延迟
    ret
```

> 为什么重映射到 0x20 而不是其他值？0x20 是惯例——Linux 和大多数操作系统都使用这个偏移。0x20 = 32，恰好紧跟在 32 个 CPU 异常向量之后。

#### 4.3 EOI（End of Interrupt）

每个硬件 IRQ 处理完后，必须向 PIC 发送 EOI 命令：

```asm
; 主 PIC IRQ 处理完后发送 EOI
mov al, 0x20        ; 0x20 = EOI 命令码
out 0x20, al        ; 发送给主 PIC

; 如果 IRQ 来自从 PIC（IRQ 8~15），需要向两个 PIC 都发 EOI
mov al, 0x20
out 0xA0, al        ; 先发给从 PIC
out 0x20, al        ; 再发给主 PIC
```

> 忘记发送 EOI = 该 IRQ 以后永不触发。这是最常见的中断 bug！

### 📝 小节练习

> [!question] 选择题 1
> PIC ICW2 的值 0x20 表示什么？
> - [ ] A. 选择 ICW2 模式
> - [ ] B. IRQ0 映射到中断向量 0x20
> - [ ] C. 启用 32 个 IRQ
> - [ ] D. 设置 EOI 地址
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: ICW2 设置中断向量基址。值为 0x20 意味着 IRQ0→0x20, IRQ1→0x21, ... IRQ7→0x27。

> [!question] 判断题 1
> 忘记向 PIC 发送 EOI 不会影响后续中断。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 未收到 EOI 的 PIC 会认为该 IRQ 仍在处理中，不再向 CPU 发送新的中断请求。该 IRQ 通道被永久阻塞。

---

### 📚 第五节：完整 QEMU 裸机示例
---

以下是一个完整、可运行的裸机程序：设置 IDT、重映射 PIC、处理键盘 IRQ1 和时钟 IRQ0，在 QEMU 中运行。

**文件结构：**
```
04_中断_idt/
├── kernel.asm       # 主程序（本节）
├── link.ld          # 链接脚本
└── Makefile         # 构建规则
```

**link.ld：**
```ld
OUTPUT_FORMAT(elf32-i386)
ENTRY(_start)

SECTIONS
{
    . = 1M;
    .text BLOCK(4K) : ALIGN(4K)
    {
        *(.multiboot)
        *(.text)
    }
    .rodata BLOCK(4K) : ALIGN(4K) { *(.rodata) }
    .data BLOCK(4K) : ALIGN(4K) { *(.data) }
    .bss  BLOCK(4K) : ALIGN(4K) { *(.bss)  }
}
```

**Makefile：**
```makefile
ASM = nasm
LD  = ld
ASFLAGS = -f elf32
LDFLAGS = -m elf_i386

kernel.elf: kernel.o link.ld
	$(LD) $(LDFLAGS) -T link.ld -o $@ $<

kernel.o: kernel.asm
	$(ASM) $(ASFLAGS) -o $@ $<

run: kernel.elf
	qemu-system-x86_64 -kernel kernel.elf -nographic

run-gdb: kernel.elf
	qemu-system-x86_64 -kernel kernel.elf -nographic -s -S

clean:
	rm -f kernel.o kernel.elf

.PHONY: run run-gdb clean
```

**kernel.asm（核心代码）：**

```asm
; kernel.asm — 中断与 IDT 完整演示
; 编译: nasm -f elf32 kernel.asm -o kernel.o
; 链接: ld -m elf_i386 -T link.ld kernel.o -o kernel.elf
; 运行: qemu-system-x86_64 -kernel kernel.elf -nographic
;
; 功能:
;   - 设置 IDT (256 项，中断门)
;   - 重映射 PIC (IRQ0→0x20, IRQ1→0x21)
;   - 时钟 ISR (IRQ0): 递增计数器，在 VGA 底部显示
;   - 键盘 ISR (IRQ1): 读扫描码，在 VGA 顶部显示
;   - 主循环中打印 "." 表示正常运行

bits 32

; ──── Multiboot 头部 ────
MBALIGN   equ 1<<0
MEMINFO   equ 1<<1
MBFLAGS   equ MBALIGN | MEMINFO
MAGIC     equ 0x1BADB002
CHECKSUM  equ -(MAGIC + MBFLAGS)

section .multiboot
align 4
    dd MAGIC
    dd MBFLAGS
    dd CHECKSUM

; ──── 常量 ────
VGA_BASE  equ 0xB8000
IDT_COUNT equ 256

; ──── 宏：设置 IDT 表项 ────
%macro IDT_SET_ENTRY 2
    mov eax, %2
    mov word [idt + %1*8], ax
    mov word [idt + %1*8 + 2], 0x08
    mov byte [idt + %1*8 + 4], 0x00
    mov byte [idt + %1*8 + 5], 0x8E
    shr eax, 16
    mov word [idt + %1*8 + 6], ax
%endmacro

; ──── BSS 段 ────
section .bss
align 16
idt:
    resb IDT_COUNT * 8      ; IDT 表: 256 项 × 8 字节 = 2048 字节

tick_count:
    resd 1                   ; 时钟计数器 (32 位)

kbd_pos:
    resd 1                   ; 键盘显示位置 (VGA 偏移)

; ──── 数据段 ────
section .data
align 4
idt_desc:
    dw IDT_COUNT * 8 - 1    ; IDT 大小 - 1
    dd idt                   ; IDT 基地址

msg_ready  db 'IDT + PIC ready. Press keys (scancodes appear at top).', 0
msg_tick   db 'Ticks: ', 0

; ──── 代码段 ────
section .text
global _start

_start:
    mov esp, stack_top       ; 设置栈（在 BSS 中分配）

    ; 1. 用默认处理器填充整个 IDT
    call idt_fill_default

    ; 2. 设置 IRQ0 (时钟) 和 IRQ1 (键盘) 的专用处理器
    IDT_SET_ENTRY 0x20, isr_timer
    IDT_SET_ENTRY 0x21, isr_keyboard

    ; 3. 重映射 PIC
    call pic_remap

    ; 4. 加载 IDT
    lidt [idt_desc]

    ; 5. 初始化变量
    mov dword [tick_count], 0
    mov dword [kbd_pos], 0

    ; 6. 显示启动信息
    mov esi, msg_ready
    mov edi, VGA_BASE + 80*2*2   ; VGA 第 3 行
    call vga_print_string

    mov edi, VGA_BASE + 80*2*23  ; VGA 第 24 行
    mov esi, msg_tick
    call vga_print_string

    ; 7. 开中断！
    sti

    ; 8. 主循环：定期在屏幕输出 '.' 表示程序活着
.main_loop:
    mov edi, VGA_BASE + 80*2*1   ; VGA 第 2 行
    mov byte [edi], '.'
    mov dword ecx, 5000000
.delay:
    loop .delay
    jmp .main_loop

; ──── 默认 ISR（什么也不做） ────
isr_default:
    iret

; ──── 时钟 ISR (IRQ0 → 向量 0x20) ────
isr_timer:
    pusha
    inc dword [tick_count]

    ; 在 VGA 第 24 行显示 tick 计数（十进制）
    mov edi, VGA_BASE + 80*2*23 + 7*2   ; "Ticks: " 后面
    mov eax, [tick_count]
    call print_dec32

    ; 发送 EOI 给主 PIC
    mov al, 0x20
    out 0x20, al
    popa
    iret

; ──── 键盘 ISR (IRQ1 → 向量 0x21) ────
isr_keyboard:
    pusha
    xor eax, eax
    in al, 0x60              ; 读取键盘扫描码

    ; 在 VGA 第 0 行输出扫描码
    mov edi, [kbd_pos]
    and edi, (80 - 1)        ; 第 0 行循环显示（80 列）
    shl edi, 1               ; ×2（每字符 2 字节）
    add edi, VGA_BASE
    call print_hex8           ; 以十六进制显示扫描码
    inc dword [kbd_pos]

    ; 发送 EOI
    mov al, 0x20
    out 0x20, al
    popa
    iret

; ──── idt_fill_default: 用 isr_default 填充全部 256 个 IDT 项 ────
idt_fill_default:
    push eax
    push ecx
    push edi
    mov ecx, IDT_COUNT
    mov edi, idt
.loop:
    mov eax, isr_default
    mov word [edi], ax
    mov word [edi+2], 0x08
    mov byte [edi+4], 0x00
    mov byte [edi+5], 0x8E    ; 存在 + Ring0 + 32位中断门
    shr eax, 16
    mov word [edi+6], ax
    add edi, 8
    loop .loop
    pop edi
    pop ecx
    pop eax
    ret

; ──── pic_remap: 重映射 PIC 8259 ────
pic_remap:
    ; ICW1: 初始化 + ICW4 模式
    mov al, 0x11
    out 0x20, al
    out 0xA0, al
    call io_wait

    ; ICW2: 向量偏移
    mov al, 0x20              ; 主: IRQ0→0x20
    out 0x21, al
    mov al, 0x28              ; 从: IRQ8→0x28
    out 0xA1, al
    call io_wait

    ; ICW3: 级联配置
    mov al, 0x04              ; 主: IRQ2 连接从 PIC
    out 0x21, al
    mov al, 0x02              ; 从: 级联标识 = 2
    out 0xA1, al
    call io_wait

    ; ICW4: 8086 模式
    mov al, 0x01
    out 0x21, al
    out 0xA1, al
    call io_wait

    ; IMR: 只开放 IRQ0 和 IRQ1
    mov al, 0xFC              ; 1111 1100 → 仅 bit0 和 bit1 = 0
    out 0x21, al              ; 主 PIC IMR
    mov al, 0xFF              ; 全屏蔽从 PIC
    out 0xA1, al

    ret

io_wait:
    out 0x80, al
    ret

; ──── vga_print_string: 打印字符串到 VGA ────
; 参数: esi = 字符串地址, edi = VGA 目标地址
vga_print_string:
    push eax
.loop:
    lodsb                     ; al = [esi], esi++
    test al, al
    jz .done
    mov ah, 0x0F              ; 白色前景，黑色背景
    mov [edi], ax
    add edi, 2
    jmp .loop
.done:
    pop eax
    ret

; ──── print_hex8: 以十六进制显示 al ────
print_hex8:
    push eax
    push ebx
    mov bl, al
    shr al, 4
    call .nibble
    mov al, bl
    and al, 0x0F
    call .nibble
    mov byte [edi+4], ' '     ; 空格分隔
    mov byte [edi+5], 0x0F    ; 白色
    pop ebx
    pop eax
    ret
.nibble:
    cmp al, 10
    sbb al, 0x69
    das
    mov ah, 0x0F
    mov [edi], ax
    add edi, 2
    ret

; ──── print_dec32: 以十进制显示 eax ────
print_dec32:
    push eax
    push ebx
    push ecx
    push edx
    mov ecx, 0
    mov ebx, 10
.div_loop:
    xor edx, edx
    div ebx
    push edx
    inc ecx
    test eax, eax
    jnz .div_loop
.print_loop:
    pop eax
    add al, '0'
    mov ah, 0x0F
    mov [edi], ax
    add edi, 2
    loop .print_loop
    pop edx
    pop ecx
    pop ebx
    pop eax
    ret

; ──── 栈空间 ────
section .bss
align 16
stack_bottom:
    resb 16384               ; 16 KB 栈
stack_top:
```

**运行效果：**
```bash
$ make run
# QEMU 窗口打开：
#   第 0 行：不断出现键盘扫描码（按下键盘看到十六进制字节闪现）
#   第 2 行：'.................'（主循环输出 → 表示程序正常）
#   第 3 行："IDT + PIC ready. Press keys..."
#   第 24 行："Ticks: 12345"（时钟中断不断递增）

# 无图形界面模式（-nographic）：
$ make run
# 在终端中看到 QEMU，按 Ctrl-A 再按 C 进入 Monitor：
# (qemu) info pic
# IRQ0=1 (timer 在触发), IRQ1=0 (等待按键)
```

> 当你按下键盘时，CPU 执行了以下路径：按键闭合 → 键盘控制器触发 IRQ1 → PIC 发送 INT 0x21 到 CPU → CPU 查 IDT[0x21] → 跳转到 `isr_keyboard` → `pusha` 保存现场 → `in al, 0x60` 读硬件 → `mov [0xB8000+...], ...` 写显存 → `out 0x20, 0x20` EOI → `popa` + `iret` 返回。**这一切都是在裸机上，没有操作系统，没有 libc，每一字节都是你的汇编代码在驱动硬件。**

### 📝 小节练习

> [!question] 判断题 1
> 进入中断门处理器时 CPU 自动清除 IF 标志（关中断）。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: 中断门（Type=0xE）进入时 CPU 自动将 EFLAGS.IF 清零，防止同优先级中断嵌套。`iret` 时从栈中恢复原 IF 值。陷阱门（Type=0xF）不改变 IF。

---

### 📚 第六节：APIC 与 PIC 对比
---

传统 8259 PIC 在现代多核系统中被 **APIC**（Advanced Programmable Interrupt Controller）取代：

| 特性 | 8259 PIC | I/O APIC + Local APIC |
|------|----------|----------------------|
| 中断源数量 | 15 个 IRQ | 24+ 个 IRQ |
| 多核支持 | 不支持（固定发往 BSP） | 支持——可为不同 IRQ 分配不同 CPU 核心 |
| 优先级 | 固定（IRQ0 最高） | 可编程 |
| 中断向量范围 | 0x20 ~ 0x2F | 0x20 ~ 0xFE |
| 编程接口 | 8 位 I/O 端口 | MMIO 寄存器和 MSR |
| QEMU 默认 | 存在但可被 APIC 覆盖 | `-M q35` 默认使用 APIC |

> APIC 的编程复杂度远高于 PIC——涉及 LAPIC MMIO 基址（通常 0xFEE00000）、I/O APIC IOREGSEL/IOWIN 间接寄存器，以及 MSR 操作。但 APIC 是多核调度的硬件基础。对于单核裸机学习，PIC 已经完全够用，且每个字节都需要手动 I/O 端口操作——更能体会"汇编是硬件操作的唯一语言"。

```asm
; 检测 APIC 是否存在（通过 CPUID.01h EDX bit9）
mov eax, 1
cpuid
test edx, 1<<9      ; APIC 标志
jz  no_apic         ; 不存在，使用 PIC
```

> 关于 CPUID 和 MSR 的详细操作参见 `[[02_特权级与系统寄存器|特权级与系统寄存器]]`。关于 APIC 在内核中的使用参见 `[[../../内核/系统内核/...|内核开发]]`。

---

## 📋 章节测试

### 一、判断题

> [!question] 判断题 1
> CPU 的 256 个中断向量中，向量 0~31 专门用于硬件 IRQ。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 向量 0~31 是 CPU 保留的异常向量。硬件 IRQ（经 PIC 重映射后）使用向量 0x20~0x2F。

> [!question] 判断题 2
> 32 位保护模式下 IDT 表项的大小与 64 位长模式下相同。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 32 位保护模式下每项 8 字节，64 位长模式下每项 16 字节（地址宽度翻倍）。

> [!question] 判断题 3
> `iret` 指令从栈中弹出 EIP、CS 和 EFLAGS 三个值。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `iret` 弹出 (EIP, CS, EFLAGS)，如果是涉及特权级切换的中断还会弹出 (ESP, SS)。

> [!question] 判断题 4
> 中断门（Interrupt Gate）和陷阱门（Trap Gate）的进入行为完全一致。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 中断门进入时自动清除 IF（关中断），陷阱门保留 IF 原值。其他行为一致。

> [!question] 判断题 5
> 向 PIC 发送 EOI 命令 0x20 只需要在 IRQ 8~15 时发送，IRQ 0~7 不需要。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 任何硬件 IRQ 处理完后都必须向对应 PIC 发送 EOI。IRQ 0~7 只发给主 PIC（端口 0x20），IRQ 8~15 先发从 PIC（0xA0）再发主 PIC（0x20）。

> [!question] 判断题 6
> `pusha` 保存的寄存器集合与 `popa` 恢复的寄存器集合完全一致（顺序相反）。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `pusha` 保存 `eax, ecx, edx, ebx, esp, ebp, esi, edi`。`popa` 按反序恢复，但丢弃保存的 `esp`（不改变当前 esp），其余 7 个寄存器恢复原值。

### 二、选择题

> [!question] 选择题 1
> PIC 重映射后，键盘 IRQ1 对应的中断向量是？
> - [ ] A. 0x01
> - [ ] B. 0x09
> - [ ] C. 0x21
> - [ ] D. 0x29
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: 重映射后主 PIC 向量基址为 0x20，IRQ1 → 0x20 + 1 = 0x21。

> [!question] 选择题 2
> IDT 描述符中 DPL 字段的作用是？
> - [ ] A. 指定处理器地址
> - [ ] B. 指定允许调用该门的最低特权级
> - [ ] C. 指定门类型
> - [ ] D. 指定代码段选择子
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: DPL（Descriptor Privilege Level）指定访问该门描述符所需的最低特权级。DPL=0 只能 Ring0 调用，DPL=3 允许用户态通过 `int` 指令触发（如 Linux `int 0x80` 系统调用）。

> [!question] 选择题 3
> `lidt` 指令的操作数是？
> - [ ] A. 寄存器
> - [ ] B. 立即数
> - [ ] C. 内存地址（6 字节描述符）
> - [ ] D. 中断向量号
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: `lidt [mem]` 从内存中读取 6 字节（32 位基址 + 16 位 limit）加载到 IDTR 寄存器。

> [!question] 选择题 4
> 主 PIC 的 I/O 端口号是？
> - [ ] A. 0x70 / 0x71
> - [ ] B. 0x20 / 0x21
> - [ ] C. 0x40 / 0x41
> - [ ] D. 0x60 / 0x61
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 主 PIC 命令端口 0x20，数据端口 0x21。从 PIC 是 0xA0 / 0xA1。0x60/0x61 是键盘控制器，0x70/0x71 是 CMOS/RTC。

> [!question] 选择题 5
> 以下哪条指令用于在中断处理完成后返回被打断的代码？
> - [ ] A. `ret`
> - [ ] B. `retf`
> - [ ] C. `iret`
> - [ ] D. `sysexit`
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: `iret`（Interrupt Return）从栈中弹出 EIP、CS、EFLAGS 并恢复执行。普通函数调用用 `ret`（只弹出返回地址）。

> [!question] 选择题 6
> ICW4 的值 0x01 表示？
> - [ ] A. 启用所有 IRQ
> - [ ] B. 8086/8088 模式
> - [ ] C. 自动 EOI 模式
> - [ ] D. 级联模式
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: ICW4 bit0 = 1 选择 8086/8088 (x86) 模式，bit0 = 0 选择 8080/8085 模式。现代 x86 统一使用 0x01。

---

### 🛠️ 动手练习题

> [!example] 练习题 1：在 IDT 中添加一个异常处理器
> **难度**: ⭐⭐
>
> 在 `kernel.asm` 中添加一个除零异常处理器（向量 0）：当执行 `div` 除以零时，处理器在 VGA 屏幕中央打印 "DIV BY ZERO!"，然后进入死循环。测试：在主循环中插入 `xor edx, edx; mov eax, 1; mov ecx, 0; div ecx`。
>
> 提示：设置 `IDT_SET_ENTRY 0, isr_divide_error`，处理器用中断门（0x8E）。

> [!example] 练习题 2：PIC 从片中断实验
> **难度**: ⭐⭐⭐
>
> 开放从 PIC 的 IRQ8（RTC 实时时钟，向量 0x28），编写处理 RTC 中断的 ISR。读取 CMOS 寄存器 0x0C（状态寄存器 C）来确认中断来源（否则 RTC 不会重新触发 IRQ8）。
>
> 提示：需要配置 RTC 寄存器 B（CMOS 0x0B）使能周期性中断：
> ```asm
> mov al, 0x0B
> out 0x70, al
> call io_wait
> in al, 0x71
> or al, 0x40       ; 使能 PIE (Periodic Interrupt Enable)
> out 0x71, al
> ```

> [!example] 练习题 3：GDB 远程调试中断
> **难度**: ⭐⭐⭐
>
> 用 `make run-gdb` 启动 QEMU（挂起模式），另开终端 `gdb kernel.elf -ex "target remote :1234"`，设置断点 `break *isr_keyboard`，按下键盘观察是否命中。单步执行 `si`，观察 `pusha` 和 `popa` 前后寄存器变化。

> [!example] 练习题 4：构建键盘环形缓冲区
> **难度**: ⭐⭐⭐⭐
>
> 修改键盘 ISR，不直接显示扫描码到 VGA，而是将扫描码写入一个 256 字节的环形缓冲区（ring buffer）。主循环从缓冲区读取并显示。这模拟了操作系统中 ISR 的工作方式：ISR 只做最少的事（把数据放入缓冲区），让用户态或内核线程做重的处理。
>
> 提示：定义 `buffer[256]`、`head`、`tail` 指针（`.bss` 段）。注意 `cli`/`sti` 保护 head/tail 的修改。

---

> **下一章**：`[[05_串口UART实战|串口 UART 实战]]` — 掌握串口输出，为后续所有章节提供调试日志能力。

> **前置章节**：`[[../1基础/04_工具链与调试环境|工具链与调试环境]]` `[[01_Port_IO与MMIO|Port I/O 与 MMIO]]` `[[02_特权级与系统寄存器|特权级与系统寄存器]]`
