# ARM 汇编与硬件访问：另一种体系结构 (ARM Assembly & Hardware Access)
---

## 章节概述

ARM 是 x86 之外统治手机、嵌入式设备和物联网领域的 CPU 架构。本章从 x86 汇编程序员的视角审视 ARM——它的寄存器、指令集、寻址模式和硬件访问方式。核心差异在于：ARM 没有 x86 的 I/O 端口空间，一切外设统统通过内存映射 I/O（MMIO）访问。我们将以树莓派 GPIO 为例，展示如何用 ARM 汇编直接控制硬件引脚（点亮 LED），并简要介绍 QEMU 模拟和真机实验环境。在阅读本章前，建议先熟悉 [[../01_Port_IO与MMIO|Port I/O 与 MMIO 的概念]] 和 [[../00_硬件操作总览|硬件操作总览]]。

> **核心理念**：学习 ARM 汇编不是为了"学另一种语法"，而是为了理解 CPU 架构设计的另一种哲学——Load/Store 精简 vs CISC 复杂、无 I/O 端口 vs 独立 I/O 空间。掌握这两种范式后，面对任何新架构（RISC-V、MIPS、LoongArch）都能快速上手。

---

### 第一节：ARM 寄存器与架构概览

1.1 ARM 的通用寄存器
--------------------

ARM 架构（ARMv7-A 及更早）提供 16 个 32 位通用寄存器：

| 寄存器 | 别名 | 用途 | x86 对等 |
|--------|------|------|----------|
| r0 | — | 参数 1 / 返回值 | rdi / rax |
| r1 | — | 参数 2 | rsi |
| r2 | — | 参数 3 | rdx |
| r3 | — | 参数 4 | rcx |
| r4-r11 | — | 被调用者保存 | r12-r15, rbx |
| r12 | ip | 过程内调用暂存 (Intra-Procedure-call scratch) | — |
| r13 | sp | 栈指针 | rsp |
| r14 | lr | 链接寄存器（存放返回地址） | —（x86 用栈） |
| r15 | pc | 程序计数器 | rip（但可读写！） |

ARM 的 **pc 是可读写的**——这是一个巨大的设计差异：
- `mov r0, pc` → r0 得到当前指令地址 + 8（三级流水线偏移）
- `add pc, pc, #4` → 跳过下一条指令

1.2 CPSR——当前程序状态寄存器
-----------------------------

```
CPSR (32-bit) 位布局:

┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
│ N │ Z │ C │ V │ Q │...│ J │...│GE[3:0]│...│ E │ A │ I │ F │ T │ M[4:0]│
└───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘
 31 30 29 28 27 ... 24 ... 16-19 9 8 7 6 5 4-0
```

| 位 | 名称 | 含义 |
|----|------|------|
| N | Negative | 结果为负 |
| Z | Zero | 结果为零 |
| C | Carry | 进位/借位/移位溢出 |
| V | Overflow | 有符号溢出 |
| T | Thumb | 1 = Thumb 模式（16 位指令），0 = ARM 模式（32 位）|
| M[4:0] | Mode | 当前 CPU 模式（User/FIQ/IRQ/Supervisor/Abort/Undef/System）|

1.3 ARM 模式与指令集变体
-------------------------

| 模式 | 指令宽度 | 特征 |
|------|---------|------|
| **ARM (A32)** | 32 位 | 条件执行、桶形移位器、所有指令 32 位 |
| **Thumb (T16)** | 16 位 | 代码密度更高，仅基本指令，通过 `bx` 切换 |
| **Thumb-2 (T32)** | 16/32 位混合 | ARMv7 引入，兼具密度和功能 |
| **A64** | 32 位 | ARMv8 的 64 位模式（AArch64）|

> 本章默认使用 ARM 模式（32 位指令），这是学习指令集的最佳起点。AArch64 部分仅作概览。

### 小节练习

---

### 第二节：ARM 指令集——精简之美

2.1 Load/Store 架构
--------------------

ARM 是纯 **Load/Store** 架构——**所有数据处理指令只操作寄存器，不能直接访问内存**。要修改内存，必须：`LDR` 装入寄存器 → 运算 → `STR` 存回内存。

```asm
@ ARM 汇编 (GNU Assembler 语法)
@ 注：@ 是 ARM 汇编的注释符（等同 x86 的 ;）

 @ 把 r1 指向的数据加 5：必须三步
 ldr r0, [r1] @ r0 = *r1 （加载）
 add r0, r0, #5 @ r0 = r0 + 5 （运算）
 str r0, [r1] @ *r1 = r0 （存储）
```

x86 对比（一条指令完成）：
```asm
; x86 可以直接操作内存
add dword [rdi], 5 ; 一条指令完成 = ARM 三条指令
```

2.2 核心数据传送指令
---------------------

```asm
 @ 立即数加载（受限：8 位 + 4 位移位旋转）
 mov r0, #42 @ r0 = 42
 mov r1, #0xFF000000 @ r1 = 0xFF000000 (OK: 0xFF << 24)

 @ 内存加载 / 存储 (多种寻址模式)
 ldr r0, [r1] @ r0 = *r1
 ldr r0, [r1, #4] @ r0 = *(r1 + 4) 偏移寻址
 ldr r0, [r1, #4]! @ r0 = *(r1 + 4); r1 += 4 前索引写回
 ldr r0, [r1], #4 @ r0 = *r1; r1 += 4 后索引
 str r0, [r1, #-4] @ *(r1 - 4) = r0 负偏移

 @ 块传送 (多寄存器加载/存储)
 push {r4, r5, lr} @ = stmfd sp!, {r4, r5, lr}
 pop {r4, r5, pc} @ = ldmfd sp!, {r4, r5, pc} 返回
 stm r0!, {r1-r3} @ 依次存 r1,r2,r3 到 [r0]，每次 r0+=4
 ldm r0!, {r1-r3} @ 依次从 [r0] 加载 r1,r2,r3
```

2.3 算术与逻辑指令
-------------------

ARM 的算术指令是**三操作数**格式（x86 是两操作数）：

```asm
 add r0, r1, r2 @ r0 = r1 + r2 (三操作数)
 sub r0, r1, #5 @ r0 = r1 - 5
 mul r0, r1, r2 @ r0 = r1 * r2 (32×32→32, 无标志)
 and r0, r1, r2 @ r0 = r1 & r2
 orr r0, r1, r2 @ r0 = r1 | r2
 eor r0, r1, r2 @ r0 = r1 ^ r2
 bic r0, r1, r2 @ r0 = r1 & ~r2 (位清除)
 lsl r0, r1, #3 @ r0 = r1 << 3
 lsr r0, r1, #2 @ r0 = r1 >> 2 (逻辑右移)
 asr r0, r1, #2 @ r0 = r1 >> 2 (算术右移)
```

2.4 内置桶形移位器
-------------------

ARM 的**第二操作数**可以附带移位，零开销完成"加载+移位"：

```asm
 add r0, r1, r2, lsl #2 @ r0 = r1 + (r2 << 2)
 mov r0, #1, lsl #12 @ r0 = 1 << 12 = 0x1000
 add r0, r1, r2, lsr #4 @ r0 = r1 + (r2 >> 4)
```

2.5 分支与条件执行
-------------------

ARM 的**所有指令都可条件执行**——利用指令高 4 位的条件码：

| 后缀 | 含义 | CPSR 条件 |
|------|------|----------|
| `eq` | 等于 | Z == 1 |
| `ne` | 不等 | Z == 0 |
| `gt` | 有符号大于 | Z==0, N==V |
| `lt` | 有符号小于 | N != V |
| `ge` | 有符号大于等于 | N == V |
| `le` | 有符号小于等于 | Z==1 或 N!=V |
| `hi` | 无符号大于 | C==1, Z==0 |
| `lo` | 无符号小于 | C == 0 |
| `mi` | 负数 | N == 1 |
| `pl` | 正数或零 | N == 0 |
| `al` | 总是 | (默认) |

```asm
 @ 条件执行示例
 cmp r0, #0
 moveq r1, #1 @ 仅当 r0==0 时执行
 movne r1, #0 @ 仅当 r0!=0 时执行

 @ 不用 compare 的条件判断
 subs r0, r0, #1 @ subs 更新标志位
 addpl r1, r1, #1 @ 仅当结果 >=0 (PL) 时加
 bne loop @ 结果 !=0 则跳回

 @ 函数调用
 bl func @ r14(lr) = 返回地址; 跳转到 func
 bx lr @ 返回到 lr (等同 mov pc, lr)
```

> x86 中 `cmp` + `jne` 是两条指令；ARM 中 `subs r0, r0, #1` + `bne loop` 也是两条，但加上 `addpl` 可以无缝插入条件操作，无需额外跳转。

2.6 立即数的限制
-----------------

ARM 32 位指令中的立即数只有 12 位可用：**8 位常量 + 4 位偶数旋转**。

```asm
 mov r0, #0xFF @ OK: 0xFF << 0
 mov r0, #0xFF000000 @ OK: 0xFF << 24
 mov r0, #0x101 @ ERROR: 无法编码（101=0x101 不是旋转常数）
 ldr r0, =0x12345678 @ 伪指令：汇编器放入文字池，自动生成 ldr 指令
```

> 注意：NASM 是 x86 专属汇编器，不能汇编 ARM 代码。ARM 汇编使用 **GNU Assembler (GAS)** 或 **ARM 工具链 (arm-none-eabi-as)**。

### 小节练习

---

### 第三节：ARM 硬件访问——MMIO 的世界

3.1 ARM 没有 I/O 端口
----------------------

x86 有 64K 独立的 I/O 端口空间（`in`/`out` 指令）。ARM **根本没有端口概念**，所有硬件设备都映射到物理地址空间的特定区域。访问硬件 = 访问内存。

```
x86: 设备 ← in/out 端口指令 → CPU (独立空间)
ARM: 设备 ← mov/ldr/str 内存指令 → CPU (同一空间)
```

3.2 树莓派 GPIO——实战 MMIO
----------------------------

树莓派（BCM2835/BCM2836/BCM2711 SoC）的 GPIO 寄存器映射到物理地址 `0x3F200000`（或 `0x7E200000` 从 GPU 总线视角）。

GPIO 寄存器布局（BCM2835, 部分）：

| 偏移 | 寄存器 | 功能 |
|------|--------|------|
| `0x00` | GPFSEL0 | GPIO 0-9 功能选择（每引脚 3 位） |
| `0x04` | GPFSEL1 | GPIO 10-19 功能选择 |
| `0x08` | GPFSEL2 | GPIO 20-29 功能选择 |
| `0x1C` | GPSET0 | GPIO 0-31 置位（写 1 输出高电平） |
| `0x28` | GPCLR0 | GPIO 0-31 清零（写 1 输出低电平） |
| `0x34` | GPLEV0 | GPIO 0-31 电平读取 |

GPFSEL 引脚功能编码：

| 值 | 功能 |
|----|------|
| `000` | 输入 |
| `001` | 输出 |
| `100` | 功能 0 (ALT0 - SPI/UART/I2C 等) |
| `111` | 保留 |

3.3 裸机 ARM 汇编 GPIO 控制（QEMU 验证）
-----------------------------------------

```asm
@ gpio_led.s — QEMU 虚拟 ARM 平台的 LED 控制
@ 编译: arm-none-eabi-as -o gpio_led.o gpio_led.s
@ arm-none-eabi-ld -Ttext=0x10000 -o gpio_led.elf gpio_led.o
@ 运行: qemu-system-arm -M virt -cpu cortex-a15 -nographic \
@ -kernel gpio_led.elf

.equ GPIO_BASE, 0x3F200000 @ BCM2835 GPIO 基址
.equ GPFSEL2, 0x08 @ GPIO 20-29 功能选择偏移
.equ GPSET0, 0x1C @ 置位寄存器偏移
.equ GPCLR0, 0x28 @ 清零寄存器偏移
.equ LED_PIN, 21 @ 假设 LED 接在 GPIO21

.global _start
_start:
 @ 获取 GPIO 基址
 ldr r0, =GPIO_BASE

 @ 1. 设置 GPFSEL2: GPIO21 为输出 (FSEL21 = 001)
 ldr r1, [r0, #GPFSEL2] @ 读取当前值
 bic r1, r1, #(7 << 3) @ 清除 FSEL21 位 (21 % 10 = 1 → 位 3,4,5)
 orr r1, r1, #(1 << 3) @ 设置 FSEL21 = 001 (输出)
 str r1, [r0, #GPFSEL2]

 @ 2. 主循环：闪烁 LED
blink:
 @ 点亮 LED
 mov r1, #(1 << LED_PIN)
 str r1, [r0, #GPSET0]

 @ 延迟循环 (约 500ms @ 1GHz)
 ldr r2, =500000
delay_on:
 subs r2, r2, #1
 bne delay_on

 @ 熄灭 LED
 mov r1, #(1 << LED_PIN)
 str r1, [r0, #GPCLR0]

 @ 延迟循环
 ldr r2, =500000
delay_off:
 subs r2, r2, #1
 bne delay_off

 b blink @ 无限循环
```

3.4 在 Linux 用户空间操作 GPIO（/dev/mem）
------------------------------------------

ARM 上 Linux 用户空间可以通过 `mmap` `/dev/mem` 直接访问物理地址（需要 root 权限）。C 内联汇编或纯 C 均可：

```c
// gpio_mmap.c — Linux 用户空间通过 mmap 访问 GPIO
// 编译: gcc -o gpio_mmap gpio_mmap.c
// 运行: sudo ./gpio_mmap

#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>

#define BCM2835_GPIO_BASE 0x3F200000
#define BLOCK_SIZE 4096

volatile unsigned *gpio;

int main() {
 int fd = open("/dev/mem", O_RDWR | O_SYNC);
 if (fd < 0) { perror("open /dev/mem"); return 1; }

 gpio = (volatile unsigned *)mmap(
 NULL, BLOCK_SIZE,
 PROT_READ | PROT_WRITE, MAP_SHARED,
 fd, BCM2835_GPIO_BASE
 );
 if (gpio == MAP_FAILED) { perror("mmap"); return 1; }

 // GPFSEL2: GPIO21 → 输出 (FSEL21 = 001)
 gpio[2] &= ~(7 << 3); // +0x08 / 4 = index 2
 gpio[2] |= (1 << 3);

 for (int i = 0; i < 5; i++) {
 gpio[7] = (1 << 21); // GPSET0 (offset 0x1C / 4 = 7)
 usleep(500000);
 gpio[10] = (1 << 21); // GPCLR0 (offset 0x28 / 4 = 10)
 usleep(500000);
 }

 munmap((void *)gpio, BLOCK_SIZE);
 close(fd);
 return 0;
}
```

> `/dev/gpiomem` 是树莓派内核提供的受限设备，仅暴露 GPIO 寄存器区域，不需要 root。树莓派推荐使用 `wiringPi` 或 `pigpio` 库而非直接 MMIO，但理解 MMIO 原理对嵌入式开发至关重要。

### 小节练习

---

### 第四节：ARM 中断与异常模型

4.1 异常向量表
---------------

ARM 的中断/异常向量表固定位于 `0x00000000` 或 `0xFFFF0000`（由 SCTLR.V 位选择）。与 x86 的 IDT（含 256 个 8/16 字节条目）不同，ARM 的向量表是**8 个绝对跳转指令**：

| 偏移 | 异常类型 | 入口模式 |
|------|---------|---------|
| `0x00` | 复位 | Supervisor |
| `0x04` | 未定义指令 | Undefined |
| `0x08` | 软件中断 (SWI/SVC) | Supervisor |
| `0x0C` | 预取中止 | Abort |
| `0x10` | 数据中止 | Abort |
| `0x18` | 保留 / IRQ (ARMv7+) | IRQ |
| `0x1C` | 快速中断 (FIQ) | FIQ |

```asm
@ ARM 异常向量表（低位置 0x00000000）
.section .vectors, "ax"
 ldr pc, _reset_handler @ 0x00: 复位
 ldr pc, _undef_handler @ 0x04: 未定义指令
 ldr pc, _swi_handler @ 0x08: 软件中断
 ldr pc, _prefetch_handler @ 0x0C: 预取中止
 ldr pc, _data_handler @ 0x10: 数据中止
 ldr pc, _unused @ 0x14: 保留
 ldr pc, _irq_handler @ 0x18: IRQ 中断
 ldr pc, _fiq_handler @ 0x1C: FIQ 中断

_reset_handler: .word _start
_undef_handler: .word undef_isr
_swi_handler: .word swi_isr
_prefetch_handler: .word abort_isr
_data_handler: .word abort_isr
_unused: .word .
_irq_handler: .word irq_isr
_fiq_handler: .word fiq_isr
```

4.2 ARMv8 异常级别
-------------------

ARMv8 (AArch64) 引入了 4 个异常级别：

| EL | 用途 | x86 对等 |
|----|------|----------|
| EL0 | 用户态应用程序 | Ring 3 |
| EL1 | 操作系统内核 | Ring 0 |
| EL2 | 虚拟机监控器 (Hypervisor) | Ring -1 (VMX Root) |
| EL3 | 安全监控器 (Secure Monitor) | — |

> ARM 的中断处理模式与 x86 有很大差异——ARM 使用 banked 寄存器（进入异常模式后自动切换到专属的 r13/r14/SPSR），无需像 x86 IDT 那样复杂的门描述符结构。

### 小节练习

> [!question] 判断题 1
> ARM 的中断向量表可以任意放置在内存的任何位置。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: ARM 的异常向量表只能位于 `0x00000000` 或 `0xFFFF0000`（由系统控制寄存器的 V 位决定）。不能像 x86 那样通过 `lidt` 将 IDT 放置在任意地址。

---

### 第五节：ARM 开发工具链与环境

5.1 安装 ARM 交叉编译工具链
----------------------------

```bash
# Debian/Ubuntu
sudo apt install gcc-arm-none-eabi binutils-arm-none-eabi qemu-system-arm

# 验证
arm-none-eabi-as --version
arm-none-eabi-gcc --version
qemu-system-arm --version
```

5.2 GNU Assembler (GAS) 基础
-----------------------------

```asm
@ GAS 汇编基本结构
.section .text
.global _start

_start:
 @ 代码在此

.section .data
var: .word 0x12345678

 .end
```

GAS 与 NASM 的语法差异（ARM 版本）：

| 语法特性 | NASM (x86) | GAS (ARM) |
|---------|------------|-----------|
| 注释 | `; comment` | `@ comment` 或 `/* block */` |
| 标号 | `label:` | `label:` |
| 十六进制 | `0x1234` | `0x1234` |
| 整数 | `42` | `#42`（ARM 汇编中立即数需前缀 `#`）|
| 定义字节 | `db 0x12` | `.byte 0x12` |
| 定义字 | `dw 0x1234` | `.hword 0x1234` 或 `.short` |
| 定义双字 | `dd 0x12345678` | `.word 0x12345678` |
| 定义四字 | `dq 0x...` | `.quad 0x...` |
| 段 | `section .text` | `.section .text`, `.text` |
| 引用地址 | `mov r0, label` | `ldr r0, =label` |
| 入口点 | `global _start` | `.global _start` |

5.3 QEMU 模拟 ARM 环境
-----------------------

```bash
# 通用 ARM 虚拟机（versatilepb 开发板）
qemu-system-arm -M versatilepb -cpu arm1176 -m 128 \
 -nographic -kernel program.elf

# AArch64 (64-bit)
qemu-system-aarch64 -M virt -cpu cortex-a53 -m 512 \
 -nographic -kernel program.elf

# 使用 GDB 调试
qemu-system-arm -M virt -cpu cortex-a15 -s -S -kernel program.elf &
arm-none-eabi-gdb program.elf \
 -ex "target remote localhost:1234"
```

### 小节练习

---

## 章节测试

### 一、判断题

> [!question] 判断题 1
> ARM 指令 `add r0, [r1], #5` 是合法的。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: ARM 是 Load/Store 架构，ALU 指令不能直接操作内存。必须先用 `ldr` 加载到寄存器，运算后用 `str` 存回。

> [!question] 判断题 2
> ARM 的 `bl` 指令会将返回地址存入栈中。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `bl` (Branch with Link) 将返回地址存入 r14 (LR 寄存器)，而非栈。这与 x86 的 `call` 指令不同（`call` 将返回地址压栈）。需要嵌套调用时由程序员手动将 LR 压栈。

> [!question] 判断题 3
> 树莓派上可以通过 `/dev/mem` 直接以内存映射方式访问 GPIO 寄存器。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `/dev/mem` 提供对整个物理地址空间的访问。用户程序通过 `mmap` 映射 GPIO 基址（`0x3F200000` 在 BCM2835 上）即可直接读写 GPIO 寄存器。需要 root 权限。

> [!question] 判断题 4
> ARM 的 `mov` 指令可以加载任意 32 位立即数。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: ARM 32 位指令中立即数只有 12 位（8 位常量 + 4 位旋转）。无法编码的值需通过 `ldr rX, =value` 伪指令从文字池加载。

> [!question] 判断题 5
> NASM 可以用来汇编 ARM 代码。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: NASM 是 x86/x86-64 专属的汇编器。ARM 汇编代码需要使用 GNU Assembler (arm-none-eabi-as)、ARM Compiler (armasm) 或 LLVM 集成汇编器。

> [!question] 判断题 6
> ARM 的中断返回不需要发送 EOI 信号给中断控制器。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: ARM 本身的中断返回机制（`subs pc, lr, #4`）不自动完成 EOI，但 ARM 系统通常使用 GIC（Generic Interrupt Controller，ARM 的 PIC 等价物），ISR 结束后需要向 GIC 写 EOI 寄存器。

---

---

### 动手练习题

> [!example] 练习题 1：ARM 汇编 LED 闪烁（QEMU）
> **难度**: 简单
>
> 使用 QEMU 的 `-M virt` 平台编写 ARM 汇编程序：
> - 初始化 UART 串口（PL011 基址 `0x09000000`）以输出字符
> - 实现 GPIO LED 闪烁逻辑（使用虚拟 GPIO，MMIO 模拟）
> - 在 QEMU QEMU monitor 中观察 GPIO 状态变化
> 提示：`qemu-system-arm -M virt -cpu cortex-a15 -nographic -kernel program.elf -monitor stdio`

> [!example] 练习题 2：真机 GPIO 控制（树莓派）
> **难度**: 简单
>
> 在真实的树莓派（3B/4B/Zero）上：
> - 使用 C 或内联汇编通过 `/dev/mem` 或 `/dev/gpiomem` 映射 GPIO 寄存器
> - 编写程序使一个 LED（接在 GPIO 某引脚）以可调频率闪烁
> - 利用 BCM2835 的 Timer 外设（基址 `0x3F00B000`）替代忙等待 `delay` 循环
> - 编写 Makefile 使用 `arm-linux-gnueabihf-gcc` 交叉编译

> [!example] 练习题 3：ARM 中断处理程序（QEMU）
> **难度**: 简单
>
> 在 QEMU 的 ARM `virt` 平台上：
> - 设置异常向量表（在 `0x00000000`）
> - 初始化 GICv2（Generic Interrupt Controller）以启用定时器中断
> - 编写 IRQ 处理程序，在 UART 上打印中断次数
> - 使用 ARM 的 Timer（Generic Timer，频率寄存器 CNTFRQ_EL0）产生周期性中断
> - 程序结构参考 [[../04_中断与IDT|中断与 IDT]] 的 x86 ISR 模式

> [!example] 练习题 4：x86 与 ARM GPIO 对比分析
> **难度**: 简单
>
> 回顾 [[../01_Port_IO与MMIO|Port I/O 与 MMIO]] 的内容，编写一份对比总结：
> - 画图表示 x86 和 ARM 的硬件访问路径（Port IO vs MMIO）
> - 列举两种方式的优缺点（速度、安全性、编程复杂度）
> - 分别用 x86 NASM 和 ARM GAS 写出"点亮 GPIO"的最小完整示例
> - 思考：如果让你设计 RISC-V 的硬件访问模型，你会选择哪种方案？为什么？

## 力扣练习

以下题目从嵌入式/底层视角训练相关能力：

| 题号 | 题目 | 链接 | 涉及知识点 |
|------|------|------|-----------|
| 136 | 只出现一次的数字 | https://leetcode.cn/problems/single-number/ | 异或指令（ARM EOR对应） |
| 190 | 颠倒二进制位 | https://leetcode.cn/problems/reverse-bits/ | 位操作（ARM桶形移位器） |
| 338 | 比特位计数 | https://leetcode.cn/problems/counting-bits/ | 位运算递推 |
| 401 | 二进制手表 | https://leetcode.cn/problems/binary-watch/ | 位操作枚举 |
