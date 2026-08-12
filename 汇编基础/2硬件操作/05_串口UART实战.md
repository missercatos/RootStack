# 串口 UART 实战：裸机的 printf (Serial UART: Bare-Metal printf)
---

## 章节概述

串口（UART）是裸机开发中**第一个能输出信息的设备**——没有它，你不知道代码跑到了哪一步、寄存器里是什么值。这就是为什么操作系统内核在初始化显卡之前会先把所有日志通过串口输出。16550 UART 芯片兼容性好（QEMU 完美模拟），编程简单（几个 I/O 端口轮询即可），是裸机开发的"Hello World"起点。本章从端口初始化到字符输出，最终实现在 QEMU 裸机上打印 `Hello, world from bare metal!`。

> **核心理念**：This is ONLY possible in assembly — `out dx, al` 将字符直接写入 UART 发送寄存器，不经过任何系统调用、库函数和操作系统。C 语言的 `putchar()` 走的是 libc → write() 系统调用 → 内核 tty 驱动的漫长路径。汇编的 `out dx, al` 是唯一能在**一条指令**里把字符从 CPU 打到物理串口线上的方式。

---

### 第一节：16550 UART 芯片与端口布局
---

#### 1.1 什么是 UART

UART（Universal Asynchronous Receiver/Transmitter）是最古老的计算机外设之一——从 1960 年代的电传打字机到现在的嵌入式调试口，串口通信从未过时。16550 芯片是 IBM PC/AT 时代的标配，至今仍然是 x86 平台的"串口标准"，QEMU 默认模拟 16550A 型号。

**在裸机上，串口是你唯一的"眼睛"**。没有显示器驱动、没有文件系统、没有 `printf`——只有 `out` 指令向串口端口写字节，另一端（QEMU 的 `-serial stdio`）显示到你的终端。

#### 1.2 端口寄存器映射

COM1 串口的 I/O 基址为 **0x3F8**（COM2 = 0x2F8, COM3 = 0x3E8, COM4 = 0x2E8）：

| 偏移 | DLAB=0（读写） | DLAB=1（读写） | 缩写 | 说明 |
|------|:-:|:-:|------|------|
| +0 | RBR 接收 / THR 发送 | DLL 波特率除数低字节 | THR/RBR/DLL | **发送数据写这里** |
| +1 | IER 中断使能寄存器 | DLH 波特率除数高字节 | IER/DLH | 中断控制 / 除数高位 |
| +2 | IIR 中断识别(读) / FCR FIFO控制(写) | 同左 | IIR/FCR | 中断类型 / FIFO |
| +3 | LCR 线路控制寄存器 | 同左 | LCR | 数据格式 + DLAB 位 |
| +4 | MCR 调制解调器控制 | 同左 | MCR | 流控、环回 |
| +5 | LSR 线路状态寄存器 | 同左 | LSR | **状态查询（关键！）** |
| +6 | MSR 调制解调器状态 | 同左 | MSR | 设备状态 |

> DLAB（Divisor Latch Access Bit）是 LCR 寄存器的 bit7。设置 DLAB=1 后才能访问 DLL/DLH（波特率除数），读写完波特率后必须清 DLAB 才能正常收发。

#### 1.3 LSR（线路状态寄存器）：裸机程序员最重要的寄存器

| 位 | 名称 | 含义 |
|----|------|------|
| 0 | Data Ready | **收到新字节，可以读取！** |
| 1 | Overrun Error | 数据被覆盖（读了太慢） |
| 2 | Parity Error | 奇偶校验错 |
| 3 | Framing Error | 帧错误 |
| 4 | Break Interrupt | 检测到 Break 信号 |
| 5 | **THR Empty** | **发送保持寄存器空闲，可以发送！** |
| 6 | Transmitter Empty | 发送移位寄存器也空闲（所有数据已发出） |

> **LSR bit5（THR Empty）是串口发送的关键**：必须在 `out` 写入 THR 之前确保 bit5 = 1，否则数据会丢失或覆盖未发送完的字节。裸机程序**没有 DMA、没有中断、没有缓冲区**——你只能轮询（poll）这个 bit。

### 小节练习

> [!question] 判断题 1
> UART 的 THR 和 RBR 共享同一个端口地址 0x3F8。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: 端口 0x3F8（基址+0）读操作访问 RBR（接收缓冲寄存器），写操作访问 THR（发送保持寄存器）。CPU 根据读/写指令区分访问目标。

---

### 第二节：UART 初始化流程
---

初始化 16550 UART 需要按顺序完成以下步骤：

```asm
; ============ UART 初始化序列 ============
; 端口基址: 0x3F8 (COM1)
; 最终配置: 115200 8N1, FIFO 启用

serial_init:
 push ax
 push dx

 ; --- 步骤 1: 禁用中断（初始化期间不处理中断）---
 mov dx, 0x3F9 ; IER (Interrupt Enable Register)
 mov al, 0x00
 out dx, al ; 所有中断关闭

 ; --- 步骤 2: 设置 DLAB 位以访问波特率除数 ---
 mov dx, 0x3FB ; LCR (Line Control Register)
 mov al, 0x80 ; DLAB = 1
 out dx, al

 ; --- 步骤 3: 设置波特率 (115200) ---
 ; 除数 = 115200 / 目标波特率
 ; 115200 Hz / 115200 = 1
 ; 常见的除数: 1→115200, 2→57600, 3→38400, 12→9600
 mov dx, 0x3F8 ; DLL (Divisor Latch Low byte)
 mov al, 0x01 ; 低字节: 1 (115200 baud)
 out dx, al

 mov dx, 0x3F9 ; DLH (Divisor Latch High byte)
 mov al, 0x00 ; 高字节: 0
 out dx, al

 ; --- 步骤 4: 设置数据格式: 8 个数据位, 无校验, 1 个停止位 (8N1) ---
 mov dx, 0x3FB ; LCR
 mov al, 0x03 ; bit1:0 = 11 → 8 data bits
 ; bit2 = 0 → 1 stop bit
 ; bit5:3 = 000 → no parity
 ; bit7 = 0 → DLAB = 0 (恢复正常读写)
 out dx, al

 ; --- 步骤 5: 启用 FIFO 并清空 ---
 mov dx, 0x3FA ; FCR (FIFO Control Register)
 mov al, 0xC7 ; bit7:6 = 11 → 14 字节触发阈值
 ; bit3 = 1 → DMA 模式
 ; bit2 = 1 → 清空发送 FIFO
 ; bit1 = 1 → 清空接收 FIFO
 ; bit0 = 1 → 启用 FIFO
 out dx, al

 pop dx
 pop ax
 ret
```

**波特率对照表：**

| 波特率 | 除数 | `mov al, X` |
|--------|------|-------------|
| 115200 | 1 | `mov al, 1` |
| 57600 | 2 | `mov al, 2` |
| 38400 | 3 | `mov al, 3` |
| 19200 | 6 | `mov al, 6` |
| 9600 | 12 | `mov al, 12` |
| 4800 | 24 | `mov al, 24` |
| 2400 | 48 | `mov al, 48` |

> 波特率公式：`divisor = 115200 / target_baud`。QEMU 中波特率设置对虚拟串口影响不大（数据通过管道传递而非真实波形），但代码在真实硬件上必须正确配置。

### 小节练习

> [!question] 判断题 1
> 设置波特率前必须先置位 DLAB（LCR bit7=1）。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: DLL 和 DLH 寄存器与 THR 和 IER 共享端口偏移（+0 和 +1），必须通过设置 DLAB=1 来切换访问目标。设置完波特率后 DLAB 必须清零才能正常收发数据。

---

### 第三节：serial_putchar —— 向串口发送一个字符
---

#### 3.1 轮询发送逻辑

```asm
; ============ serial_putchar: 发送单字符 ============
; 输入: al = 要发送的字符
; 破坏: 无 (push/pop 保护)
; 原理: 一直读 LSR bit5 直到为 1, 然后写入 THR
serial_putchar:
 push ax ; 保存 ax
 push dx

 mov dx, 0x3FD ; LSR (Line Status Register)
.wait:
 in al, dx ; 读取状态
 test al, 0x20 ; bit5 = THR Empty?
 jz .wait ; 不为 1 → 持续轮询（发送器忙）

 mov dx, 0x3F8 ; THR (Transmitter Holding Register)
 pop ax ; 恢复 ax
 mov al, al ; (冗余操作，确保 al 正确)
 out dx, al ; 写入字符到发送 FIFO → 硬件开始发送

 pop dx
 ret
```

> **为什么必须轮询？** 硬件发送一个字节需要时间（约 87μs @115200 波特率）。如果在上一字节未被完全移出发送器之前写入下一个字节，数据将被覆盖。裸机没有中断驱动的发送队列——CPU 必须等硬件准备好。

**AT&T 语法对照（GCC 内联汇编参考）：**
```asm
; NASM/Intel:
 mov dx, 0x3FD
.wait:
 in al, dx
 test al, 0x20
 jz .wait
 out 0x3F8, al

; AT&T (GCC):
 movw $0x3FD, %dx
1: inb %dx, %al
 testb $0x20, %al
 jz 1b
 outb %al, $0x3F8
```

#### 3.2 添加超时保护（可选）

实际开发中，如果串口卡住（LSR bit5 永远不置位），上述轮询会死循环。可以加一个超时计数器：

```asm
; 带超时的 serial_putchar
serial_putchar_timeout:
 push ax
 push cx
 push dx

 mov dx, 0x3FD
 mov cx, 0xFFFF ; 最大轮询次数
.wait:
 in al, dx
 test al, 0x20
 jnz .send
 loop .wait ; cx--; if cx != 0 goto .wait
 ; 超时处理: 丢弃字符
 jmp .done
.send:
 mov dx, 0x3F8
 mov al, [esp + 8] ; 获取函数的原始 al
 out dx, al
.done:
 pop dx
 pop cx
 pop ax
 ret
```

> QEMU 中一般不需要超时——虚拟串口永远不会"卡住"。但真机开发必须加超时。

### 小节练习

> [!question] 判断题 1
> `serial_putchar` 可以直接 `out 0x3F8, al` 而不检查 LSR bit5。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 如果不检查 THR Empty，连续快速发送字符时后面的字符会覆盖前面尚未发出完成的字符，导致数据丢失。必须轮询 LSR bit5。

---

### 第四节：serial_puts 与调试输出
---

```asm
; ============ serial_puts: 发送以 0 结尾的字符串 ============
; 输入: esi = 字符串地址
; 破坏: esi (前进了 strlen 个字节), al
serial_puts:
 push ax
 push dx
 push si ; 保存 esi 的副本 (可选)

.loop:
 lodsb ; al = [esi], esi++
 test al, al ; 检查是否到达 '\0'
 jz .done
 call serial_putchar ; 发送 al 中的字符
 jmp .loop

.done:
 pop si
 pop dx
 pop ax
 ret
```

#### 4.1 辅助调试函数

```asm
; ============ serial_puthex8: 以十六进制输出 al ============
serial_puthex8:
 push ax
 push bx
 mov bl, al
 shr al, 4
 call .nibble ; 高 4 位
 mov al, bl
 and al, 0x0F
 call .nibble ; 低 4 位
 pop bx
 pop ax
 ret
.nibble:
 cmp al, 10
 sbb al, 0x69
 das
 call serial_putchar
 ret

; ============ serial_puthex32: 以十六进制输出 eax ============
serial_puthex32:
 push eax
 push ecx
 mov ecx, 8
.loop:
 rol eax, 4 ; 循环左移，每次取最高 4 位
 push eax
 and al, 0x0F
 cmp al, 10
 sbb al, 0x69
 das
 call serial_putchar
 pop eax
 loop .loop
 pop ecx
 pop eax
 ret

; ============ serial_putdec32: 以十进制输出 eax ============
serial_putdec32:
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
 call serial_putchar
 loop .print_loop
 pop edx
 pop ecx
 pop ebx
 pop eax
 ret

; ============ serial_newline: 输出 \r\n ============
serial_newline:
 push ax
 mov al, 0x0D ; '\r' 回车
 call serial_putchar
 mov al, 0x0A ; '\n' 换行
 call serial_putchar
 pop ax
 ret
```

> **串口需要 \r\n 而非 \n**：串口终端的行结束符是 CR+LF（0x0D 0x0A）。只发 \n（0x0A）可能导致光标只下移不回到行首（视终端软件而定）。QEMU `-serial stdio` 模式下，只发 \n 通常也能正确换行，但真机串口终端未必如此。

### 小节练习

---

### 第五节：完整裸机 "Hello World" 程序
---

以下是一个完整、可独立编译运行的裸机串口输出程序。

**文件结构：**
```
05_串口uart/
├── kernel.asm
├── link.ld
└── Makefile
```

**Makefile：**
```makefile
ASM = nasm
LD = ld
ASFLAGS = -f elf32
LDFLAGS = -m elf_i386

kernel.elf: kernel.o link.ld
	$(LD) $(LDFLAGS) -T link.ld -o $@ $<

kernel.o: kernel.asm
	$(ASM) $(ASFLAGS) -o $@ $<

run: kernel.elf
	qemu-system-x86_64 -kernel kernel.elf -nographic -serial stdio

run-gdb: kernel.elf
	qemu-system-x86_64 -kernel kernel.elf -nographic -serial stdio -s -S

clean:
	rm -f kernel.o kernel.elf

.PHONY: run run-gdb clean
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
 .bss BLOCK(4K) : ALIGN(4K) { *(.bss) }
}
```

**kernel.asm（核心代码）：**

```asm
; kernel.asm — 裸机串口 Hello World
; 编译: nasm -f elf32 kernel.asm -o kernel.o
; 链接: ld -m elf_i386 -T link.ld kernel.o -o kernel.elf
; 运行: qemu-system-x86_64 -kernel kernel.elf -nographic -serial stdio
;
; 在这个极简裸机程序中：
; 没有操作系统、没有 libc、没有 printf
; 只有 in/out 指令操作 UART 端口
; 你能看到 "Hello, world from bare metal!" 从串口输出

bits 32

; ──── Multiboot 头部 ────
MBALIGN equ 1<<0
MEMINFO equ 1<<1
MBFLAGS equ MBALIGN | MEMINFO
MAGIC equ 0x1BADB002
CHECKSUM equ -(MAGIC + MBFLAGS)

section .multiboot
align 4
 dd MAGIC
 dd MBFLAGS
 dd CHECKSUM

; ──── 数据段 ────
section .data
hello_msg db 'Hello, world from bare metal!', 0x0D, 0x0A, 0
info_msg db 'Serial UART initialized. COM1 115200 8N1.', 0x0D, 0x0A, 0
test_msg db 'Testing all printable ASCII characters:', 0x0D, 0x0A, 0
ready_msg db 'Stack pointer (ESP) = ', 0
newline db 0x0D, 0x0A, 0
separator db '---', 0x0D, 0x0A, 0

section .text
global _start

_start:
 mov esp, stack_top

 ; 1. 初始化串口
 call serial_init

 ; 2. 打印初始化信息
 mov esi, info_msg
 call serial_puts

 ; 3. 打印 Hello World
 mov esi, hello_msg
 call serial_puts

 mov esi, separator
 call serial_puts

 ; 4. 打印 ESP 的值（演示 hex 输出）
 mov esi, ready_msg
 call serial_puts
 mov eax, esp
 call serial_puthex32
 call serial_newline

 ; 5. 打印所有可打印 ASCII 字符
 mov esi, test_msg
 call serial_puts

 mov al, ' ' ; 从空格开始
.ascii_loop:
 cmp al, 0x7E ; 到 '~' 结束
 jg .done_ascii
 call serial_putchar
 inc al
 cmp al, 0x80 ; 每 32 个字符换行
 test al, 0x1F
 jnz .ascii_loop
 call serial_newline
 jmp .ascii_loop
.done_ascii:
 call serial_newline

 mov esi, separator
 call serial_puts

 ; 6. 打印十进制数字演示
 mov eax, 12345
 call serial_putdec32
 call serial_newline

 ; 7. 暂停（死循环——裸机没有"退出"概念）
 hlt
 jmp $ ; 如果 NMI 唤醒就继续停

; ============ serial_init ============
serial_init:
 push ax
 push dx

 ; 禁用中断
 mov dx, 0x3F9
 mov al, 0x00
 out dx, al

 ; DLAB = 1
 mov dx, 0x3FB
 mov al, 0x80
 out dx, al

 ; 波特率 = 115200 (除数 = 1)
 mov dx, 0x3F8
 mov al, 0x01
 out dx, al
 mov dx, 0x3F9
 mov al, 0x00
 out dx, al

 ; 8N1, DLAB = 0
 mov dx, 0x3FB
 mov al, 0x03
 out dx, al

 ; 启用 FIFO，清空缓冲区
 mov dx, 0x3FA
 mov al, 0xC7
 out dx, al

 pop dx
 pop ax
 ret

; ============ serial_putchar ============
serial_putchar:
 push ax
 push dx
 mov dx, 0x3FD
.wait:
 in al, dx
 test al, 0x20 ; LSR bit5: THR Empty?
 jz .wait
 mov dx, 0x3F8
 mov al, [esp + 4] ; 恢复原始 al（栈中 push ax 的值）
 out dx, al
 pop dx
 pop ax
 ret

; ============ serial_puts ============
serial_puts:
 push ax
 push si
.loop:
 lodsb
 test al, al
 jz .done
 call serial_putchar
 jmp .loop
.done:
 pop si
 pop ax
 ret

; ============ serial_puthex32 ============
serial_puthex32:
 push eax
 push ecx
 mov ecx, 8
.hex_loop:
 rol eax, 4
 push eax
 and al, 0x0F
 cmp al, 10
 sbb al, 0x69
 das
 call serial_putchar
 pop eax
 loop .hex_loop
 pop ecx
 pop eax
 ret

; ============ serial_putdec32 ============
serial_putdec32:
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
 call serial_putchar
 loop .print_loop
 pop edx
 pop ecx
 pop ebx
 pop eax
 ret

; ============ serial_newline ============
serial_newline:
 push ax
 mov al, 0x0D
 call serial_putchar
 mov al, 0x0A
 call serial_putchar
 pop ax
 ret

; ============ 栈空间 ============
section .bss
align 16
stack_bottom:
 resb 16384
stack_top:
```

**运行：**
```bash
$ make run
# 终端输出：
# Serial UART initialized. COM1 115200 8N1.
# Hello, world from bare metal!
# ---
# Stack pointer (ESP) = 00200000
# Testing all printable ASCII characters:
# !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~
# ---
# 12345
```

**对比 C 语言：**
```c
// C 版本需要的事情：
#include <stdio.h>
int main() {
 printf("Hello, world from bare metal!\n"); // → libc → write() → 内核 TTY 驱动 → 串口驱动
 return 0;
}
// 汇编版本只做的事：
// 1. out 0x3FB, 0x80 (设置 DLAB)
// 2. out 0x3F8, 1 (设置波特率)
// 3. out 0x3FB, 0x03 (8N1)
// 4. out 0x3F8, 'H' (发送字符)
// 5. out 0x3F8, 'e' ...
// That's it.
```

> C 语言的 `printf("Hello")` 到最终串口输出经历了：libc → stdout 缓冲 → `write()` 系统调用 → VFS 层 → TTY 行规则 → 串口驱动 → `out` 指令。**汇编删除了所有中间层——只有 `out` 指令**。This is ONLY possible in assembly.

### 小节练习

---

## 章节测试

### 一、判断题

> [!question] 判断题 1
> 16550 UART 的 LCR 寄存器用于控制数据格式和 DLAB 位。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确

> [!question] 判断题 2
> 设置波特率除数时，DLAB 位必须设为 0。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 设置波特率除数时 DLAB 必须为 1（LCR bit7=1），之后恢复为 0 才能正常读写 THR/RBR。

> [!question] 判断题 3
> 在 QEMU 中，无论 `-serial stdio` 是否存在，裸机程序的 `out 0x3F8, al` 都能正常执行（不会报错）。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: QEMU 模拟了完整的 I/O 端口空间，即使没有 `-serial stdio`，`out 0x3F8, al` 也不会报错——只是数据被丢弃。这也是 `out` 指令在裸机环境下的优势：不会像用户态那样触发段错误。

> [!question] 判断题 4
> 16550 FIFO 的启用是可选的——即使不启用，UART 也能正常收发数据。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: FIFO 是 16550 增强特性。即使不写 FCR 寄存器（默认 FIFO 不启用），芯片也能作为 8250 兼容模式工作（每个字符单独发送/接收）。但启用 FIFO 可显著降低中断次数和 CPU 轮询频率。

> [!question] 判断题 5
> `serial_puts` 可以直接循环调用 `out 0x3F8, [esi]` 而不检查 LSR。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 每次发送前必须轮询 LSR bit5 确认 THR 空闲。连续快速 `out` 会覆盖未发送完的字节。

---

### 动手练习题

> [!example] 练习题 1：修改波特率
> **难度**: 简单
>
> 修改 `serial_init` 函数，将波特率从 115200 改为 9600。确认除数为 `115200/9600 = 12`。运行 `make run` 测试输出是否正常。然后用不同波特率（38400、19200、2400）测试，理解波特率对输出速度的影响（在真机串口上，低波特率会导致字符输出明显变慢）。

> [!example] 练习题 2：实现串口输入（serial_getchar）
> **难度**: 简单
>
> 实现 `serial_getchar` 函数：轮询 LSR bit0（Data Ready），为 1 时从 RBR（端口 0x3F8）读取字符并返回 (`al`)。在 `_start` 中循环：等待键盘输入（通过 QEMU `-serial stdio` 输入的字符会到达 COM1），收到后回显（echo）该字符。
>
> ```asm
> serial_getchar:
> push dx
> mov dx, 0x3FD
> .wait:
> in al, dx
> test al, 0x01 ; LSR bit0: Data Ready?
> jz .wait
> mov dx, 0x3F8
> in al, dx ; 读取字符
> pop dx
> ret
> ```

> [!example] 练习题 3：实现 printf 风格的格式化输出
> **难度**: 简单
>
> 实现 `serial_printf`：接受 `\0` 结尾的格式字符串，支持 `%s`（字符串）、`%x`（十六进制）、`%d`（十进制）三个格式说明符。类似于 C 的 `printf("Value is %d (0x%x)", 42, 42)`——参数通过栈传递。
>
> 提示：用一个指针遍历格式字符串，遇到 `%` 时查看下一个字符确定类型，从栈中取出参数。

> [!example] 练习题 4：双串口输出
> **难度**: 简单
>
> 将 UART 函数改为参数化——所有函数的 I/O 端口基址不写死 0x3F8，而是放在某个寄存器或全局变量中。实现 `serial_select_com1` 和 `serial_select_com2` 切换函数。测试：COM1 输出 "Hello from COM1!"，然后切换到 COM2 输出 "Hello from COM2!"。
>
> 提示：QEMU 需要通过 `-serial stdio -serial file:com2.log` 启用两个串口。

---

> **下一章**：`[[06_VGA文本模式实战|VGA 文本模式实战]]` — 掌握直接写显存，在 QEMU 窗口中看到真正的屏幕输出。

> **前置章节**：`[[04_中断与IDT|中断与 IDT]]` `[[../1基础/04_工具链与调试环境|工具链]]` `[[01_Port_IO与MMIO|Port I/O 与 MMIO]]`

## 力扣练习

本章实践性强，请用动手练习题自检（串口读写、格式化输出、双串口通信）。
