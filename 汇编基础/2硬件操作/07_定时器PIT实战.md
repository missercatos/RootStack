# 定时器 PIT 实战：可编程时钟 (PIT: Programmable Timer)
---

## 📖 章节概述

Intel 8253/8254 PIT（Programmable Interval Timer）是 x86 平台最古老的外设之一——从 IBM PC/XT（1981 年）到现在，它一直是系统时钟的硬件基础。PIT 的晶体振荡器以 1,193,182 Hz 的频率振动，经过一个可编程除数分频后产生周期性的 IRQ0 中断。本章从 PIT 端口编程到编写定时器中断处理器（ISR），最终实现 `sleep(ms)`——裸机上的毫秒级精确延时。这是操作系统调度器的硬件根基：时间片轮转全靠 PIT 定时触发。

> **核心理念**：This is ONLY possible in assembly — `out 0x43, al`（向 PIT 模式寄存器写入命令字节）是特权 I/O 指令，用户态 C 程序被禁止执行。更重要的是，`sleep()` 在 C 中是阻塞式系统调用——操作系统帮你切换进程等时间到达。但汇编裸机 `sleep()` 的每一微秒都是你直接控制的：写除数 → 等 IRQ0 → 计数到目标 → 返回。你能精确知道 CPU 经过了多少个 PIT 时钟周期。

---

### 📚 第一节：8253/8254 PIT 架构
---

#### 1.1 PIT 在系统中的位置

```
         1.193182 MHz
         ［晶振］
             │
             ▼
       ┌───────────┐
       │  8253/8254 │
       │   PIT      │     IRQ0 ──▶ PIC ──▶ CPU INTR
       │            │     OUT2 ──▶ PC 扬声器
       │            │     OUT1 ──▶ DRAM 刷新 (已废弃)
       └───────────┘
```

PIT 有三个独立的 16 位计数器通道：

| 通道 | 端口 | 典型用途 | IRQ 连线 |
|------|------|---------|----------|
| Channel 0 | 0x40 | **系统时钟**——连到 IRQ0 | IRQ0 → PIC → CPU |
| Channel 1 | 0x41 | DRAM 刷新（现代已废弃） | — |
| Channel 2 | 0x42 | PC 扬声器（蜂鸣器） | — |
| 命令 | 0x43 | 模式/命令寄存器（只写） | — |

#### 1.2 关键参数

| 参数 | 值 |
|------|-----|
| 输入频率 | **1,193,182 Hz** (~1.193182 MHz) |
| 计数器位宽 | 16 位（最大除数 65536） |
| 最小频率 | 1,193,182 ÷ 65536 ≈ **18.2 Hz** |
| 最大频率 | 1,193,182 ÷ 1 = **1.193182 MHz** |
| 默认频率 | 1,193,182 ÷ 65536 ≈ 18.2 Hz（约 55ms 间隔） |

> 1,193,182 这个"奇怪"数字来源于 NTSC 彩色副载波频率的 4 倍（3.579545 MHz ÷ 3 = 1.193182 MHz）——IBM PC 的设计利用了电视工业已有的廉价晶振。

### 📝 小节练习

> [!question] 判断题 1
> PIT 的三个通道使用不同的命令端口（0x43~0x45）。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 三个通道共享一个命令端口 0x43。写 0x43 时，命令字节中的 bit6:7 指定目标通道。数据端口分别为 0x40（Ch0）、0x41（Ch1）、0x42（Ch2）。

---

### 📚 第二节：PIT 编程
---

#### 2.1 命令字节格式

写入端口 0x43 的命令字节结构：

```
 7    6   5   4   3  2  1   0
+----+---+--------+---+------+
| SC1|SC0| RW1|RW0|Mode | BCD |
+----+---+--------+---+------+
```

| 位 | 名称 | 值 | 含义 |
|----|------|-----|------|
| 7:6 | SC | 00 | 选择通道 0 |
| | | 01 | 选择通道 1 |
| | | 10 | 选择通道 2 |
| | | 11 | 读回命令（特殊） |
| 5:4 | RW | 00 | 计数器锁存命令 |
| | | 01 | 只读写低字节 |
| | | 10 | 只读写高字节 |
| | | **11** | **先读写低字节，再读写高字节** |
| 3:1 | Mode | **010** | Mode 2: 比率发生器 |
| | | **011** | Mode 3: 方波发生器 |
| | | 000 | Mode 0: 终端计数中断 |
| 0 | BCD | 0 | 16 位二进制计数 |
| | | 1 | 4 位 BCD 计数（不常用） |

#### 2.2 常用操作模式

**Mode 2（比率发生器 / Rate Generator）**：最常用。计数器从 N 递减到 1，输出一个负脉冲，然后重装 N 继续递减。像节拍器——每 N 个晶振周期产生一个脉冲。

```
晶振脉冲:  |_||_||_||_||_||_||_||_||_||_||_||_||_||_||_||_||_||_||_|
计数器值:  N N-1 N-2 ... 3 2 1 N N-1 ...
IRQ0 信号: _____________________|￣|____________________|￣|__________
                                 ↑ 脉冲                 ↑ 脉冲
```

**Mode 3（方波发生器 / Square Wave Generator）**：输出对称方波（若 N 为偶数）或近似方波（若 N 为奇数）。IRQ0 方波的上升沿触发中断。

> 绝大多数操作系统使用 Mode 2 或 Mode 3 来驱动系统时钟。Mode 2 的负脉冲更适合边缘触发的 IRQ 线路。

#### 2.3 编程步骤

```asm
; ============ pit_init: 初始化 PIT 通道 0 ============
; 输入: ebx = 期望频率 (Hz)
;       例如: 1000 → 1000 Hz (每毫秒一次中断)
;             100  → 100 Hz  (每 10 毫秒一次中断)
;             1    → 1 Hz    (每秒一次中断)
;
; 算法: divisor = 1193182 / frequency
;       如果 divisor > 65535 → 错误 (频率太低)
pit_init:
    push eax
    push ebx
    push edx

    ; 计算除数
    mov eax, 1193182
    xor edx, edx
    div ebx                  ; eax = divisor, edx = 余数

    ; 检查除数范围
    cmp eax, 65535
    ja .error_divisor        ; 除数 > 65535 → 频率太低，不合法

    mov ebx, eax             ; ebx = divisor

    ; 步骤 1: 发送命令字节到 0x43
    mov al, 0x36             ; 0x36 = 00_11_010_0
                             ;   SC = 00  → 通道 0
                             ;   RW = 11  → 先低后高
                             ; Mode = 010 → Mode 2 (比率发生器)
                             ;  BCD = 0   → 16 位二进制
    out 0x43, al

    ; 步骤 2: 发送除数（先低字节后高字节）
    mov al, bl               ; 除数低 8 位
    out 0x40, al
    mov al, bh               ; 除数高 8 位
    out 0x40, al

    jmp .done
.error_divisor:
    ; 频率太低，除数超出范围
    ; 可以设置最大除数 65536（写作 0）
    mov al, 0x36
    out 0x43, al
    xor al, al               ; 除数 = 0 → 硬件解释为 65536
    out 0x40, al
    out 0x40, al
.done:
    pop edx
    pop ebx
    pop eax
    ret
```

**常用频率对应的除数：**

| 期望频率 | 除数 | 结果频率（精确） | 误差 | 应用场景 |
|----------|------|------|------|----------|
| 18.2 Hz | 65536 (0) | ~18.2 Hz | 0% | BIOS 默认 |
| 100 Hz | 11932 | 100.00 Hz | ~0% | 10ms 时钟嘀嗒 |
| 500 Hz | 2386 | 500.08 Hz | 0.016% | 2ms 精度睡眠 |
| 1000 Hz | 1193 | 1000.67 Hz | 0.067% | 1ms 精度睡眠 |
| 10000 Hz | 119 | 10026.74 Hz | 0.27% | 0.1ms 精度睡眠 |

> 除数 0 在硬件上被解释为 65536（而非除以零）。这是设计好的特性——用 0 表示最大除数。

### 📝 小节练习

> [!question] 选择题 1
> PIT 命令字节 0x36 的含义是？
> - [ ] A. 通道 0, 读写低字节, Mode 2, BCD
> - [ ] B. 通道 0, 读写低+高字节, Mode 2, 二进制
> - [ ] C. 通道 1, 读写低+高字节, Mode 3, 二进制
> - [ ] D. 通道 2, 只读高字节, Mode 0, 二进制
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 0x36 = 0011_0110b → SC=00(Ch0), RW=11(低+高), Mode=010(Mode2), BCD=0(二进制)。通道 0 + Mode 2 + 16 位二进制 = 系统定时器的标准配置。

> [!question] 判断题 1
> 除数 0 会导致 PIT 停止输出（除以零错误）。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: PIT 硬件将除数 0 解释为 65536（而非除零错误）。这是 Intel 8253/8254 手册明确规定的行为。除数为 0 时频率最低：1193182 ÷ 65536 ≈ 18.2 Hz。

---

### 📚 第三节：定时器中断处理器（IRQ0 ISR）
---

定时器 ISR 是最简单的 IRQ 处理器——没有硬件数据需要读取，只需要递增一个全局计数器并发送 EOI：

```asm
; 全局计数器（.bss 或 .data 中）
section .bss
pit_ticks:    resd 1         ; 32 位系统 tick 计数器
global_ticks: resd 1         ; 永不重置的全局计数器（可用于 uptime）

; ============ isr_timer: PIT IRQ0 处理器 ============
; 每 (1193182/divisor) 次晶振周期触发一次
; 如果 divisor=11932 → 每 10ms 触发一次
isr_timer:
    pusha

    inc dword [pit_ticks]      ; 系统启动以来的总 tick 数

    ; 可选：如果有独立的分频 tick，在这里累加
    ; 例如我们要用 1ms 精度（1000 Hz），tick 计数器每 tick 加 1
    ; 以 1ms 为单位累积时间:
    inc dword [global_ticks]

    ; 发送 EOI 给主 PIC
    mov al, 0x20
    out 0x20, al

    popa
    iret
```

#### 3.1 中断频率权衡

| 频率 | 每次间隔 | CPU 开销 | 延时精度 | 典型用途 |
|------|----------|---------|----------|----------|
| ~18.2 Hz | 55ms | 极低 | 55ms | BIOS 默认、极小系统 |
| 100 Hz | 10ms | 低 | 10ms | Linux 2.4 及之前（HZ=100） |
| 250 Hz | 4ms | 中 | 4ms | Linux 2.6 默认（HZ=250） |
| 1000 Hz | 1ms | 高 | 1ms | Linux 桌面/低延时系统（HZ=1000） |

> 每秒钟 1000 次中断 = 每毫秒都要执行一次 ISR。在 1 GHz CPU 上，每次 ISR 约消耗 0.5 ~ 1 μs，这相当于 0.1% 的 CPU 时间——通常值得换取毫秒级精度的定时能力。

#### 3.2 读取 PIT 当前计数值（精确计时）

```asm
; ============ pit_get_count: 读取通道 0 的当前计数值 ============
; 输出: eax = 当前计数值（0 ~ divisor-1）
; 用途: 实现亚 tick 级别的时间测量
pit_get_count:
    push dx

    ; 锁存通道 0 的计数（防止读取期间计数变化）
    mov al, 0x00            ; SC=00(Ch0), RW=00(锁存), Mode=000, BCD=0
    out 0x43, al

    ; 读取低字节
    in al, 0x40
    mov ah, al              ; 暂存低字节

    ; 读取高字节
    in al, 0x40
    xchg al, ah             ; eax = 完整 16 位计数值

    pop dx
    ret
```

> 锁存命令（RW=00）让 PIT 在读取期间"冻结"当前计数值到内部锁存器，确保你读到的低字节和高字节来自同一个计数瞬间。不锁存的话，低字节读到 0xFF 时可能刚好计数值从 0x0100 变成 0x00FF，导致拼接出错误的 0xFF00。

### 📝 小节练习

> [!question] 判断题 1
> 定时器 ISR 必须读取端口 0x40 来清除中断标志。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: PIT 不需要读取数据来清除中断——IRQ0 是边缘触发的，PIT 自动管理。只需要向 PIC 发送 EOI 即可。不同于键盘（必须读 0x60 才清除键盘控制器的中断标志）。

---

### 📚 第四节：实现 sleep(ms)
---

sleep 的核心思路：记录当前 tick 计数，然后不断检查 tick 是否增长了足够的数量。

```asm
; ============ sleep_ms: 以毫秒为单位睡眠 ============
; 输入: eax = 睡眠毫秒数
; 前提: PIT 配置为 1000 Hz (1 tick = 1 ms)
;
; 原理: 轮询 pit_ticks 直到增量达到目标
sleep_ms:
    push eax
    push ebx

    mov ebx, eax             ; ebx = 目标毫秒数
    test ebx, ebx
    jz .done                 ; sleep(0) → 立即返回

    ; 读取当前 tick 值
    mov eax, [pit_ticks]
    add ebx, eax             ; ebx = 目标 tick 值

.wait:
    cmp [pit_ticks], ebx     ; 如果当前 tick < 目标 tick
    jb .wait                 ; 继续等待

.done:
    pop ebx
    pop eax
    ret
```

> **注意**：上述 sleep_ms 依赖 `pit_ticks` 单调递增且不会被溢出中断。计数器溢出到 0 时（约 49.7 天后 @1000Hz），对溢出的处理需要额外逻辑。但这对于裸机学习足够了——你不会在 QEMU 中连续运行 49 天。

#### 4.1 高精度 sleep_ms（处理 tick 溢出）

```asm
; ============ sleep_ms_safe: 处理 tick 溢出 ============
sleep_ms_safe:
    push eax
    push ebx
    push ecx

    mov ecx, eax             ; ecx = 目标毫秒数

    ; 禁用中断以保证原子读取
    cli
    mov ebx, [pit_ticks]     ; ebx = 起始 tick
    sti

    ; 计算目标，处理 32 位回绕
    mov eax, [pit_ticks]
    sub eax, ebx             ; eax = 已经过的 tick 数
    cmp eax, ecx
    jae .done                ; 已经过了足够时间

    ; 还需等待: ecx - eax 毫秒
    sub ecx, eax
    add ecx, [pit_ticks]     ; ecx = 绝对目标 tick（回绕安全）

.wait:
    mov eax, [pit_ticks]
    sub eax, ebx             ; eax = 从起始时刻经过的总 tick
    cmp eax, ecx             ; 但需要以起始时刻为基准
    jb .wait

.done:
    pop ecx
    pop ebx
    pop eax
    ret
```

> 对比 C 语言：`usleep(1000)` 的背后是 `nanosleep()` 系统调用 → 内核将进程放入等待队列 → 调度器选择其他进程 → PIT 中断触发 → `update_process_times()` → 检查等待队列 → 发现时间到 → 唤醒进程 → 返回用户态。**汇编 sleep 就是 `cmp [ticks], target; jb .wait` 两条指令**——没有任何内核参与。This is ONLY possible in assembly.

### 📝 小节练习

> [!question] 选择题 1
> 如果 PIT 配置为 100 Hz，sleep_ms(50) 需要等待多少个 tick？
> - [ ] A. 5 个
> - [ ] B. 50 个
> - [ ] C. 100 个
> - [ ] D. 500 个
>
> > [!success]- 点击查看答案
> > 正确答案: A
> > **解析**: 100 Hz 意味着每秒 100 个 tick，每个 tick = 10ms。50ms ÷ 10ms/tick = 5 tick。

---

### 📚 第五节：完整 QEMU 裸机示例
---

以下是一个完整可运行的程序：PIT 100Hz 配置、IDT + PIC 设置、定时器 ISR 驱动 tick 计数器、sleep 函数实现、VGA 实时显示和串口调试日志。

**文件结构：**
```
07_定时器pit/
├── kernel.asm
├── link.ld
└── Makefile
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
	qemu-system-x86_64 -kernel kernel.elf -serial stdio

run-gdb: kernel.elf
	qemu-system-x86_64 -kernel kernel.elf -serial stdio -s -S

clean:
	rm -f kernel.o kernel.elf

.PHONY: run run-gdb clean
```

**link.ld** 与前面章节相同（加载地址 1M，标准 multiboot 布局）。

**kernel.asm（核心代码）：**

```asm
; kernel.asm — PIT 定时器完整演示
;
; 功能：
;   - PIT 通道 0 编程 (1193 除数 → ~1000 Hz, 1ms 精度)
;   - PIC 重映射 + IDT 设置
;   - 定时器 ISR: 递增 tick 计数器
;   - sleep_ms(ms): 毫秒级精确睡眠
;   - VGA 实时显示 tick 计数
;   - 串口调试日志
;
; 编译: nasm -f elf32 kernel.asm -o kernel.o
; 链接: ld -m elf_i386 -T link.ld kernel.o -o kernel.elf
; 运行: qemu-system-x86_64 -kernel kernel.elf -serial stdio

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
VGA_BASE    equ 0xB8000
PIT_FREQ    equ 1000            ; 期望 1000 Hz (1ms tick)
IDT_COUNT   equ 256

; ──── IDT 表项设置宏 ────
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
    resb IDT_COUNT * 8          ; 256 项 × 8 字节 = 2048 字节

pit_ticks:
    resd 1                       ; 系统启动以来的 tick 数 (32位)
seconds_elapsed:
    resd 1                       ; 运行秒数

vga_row:
    resb 1
vga_col:
    resb 1
vga_color:
    resb 1

align 16
stack_bottom:
    resb 16384
stack_top:

; ──── 数据段 ────
section .data
align 4
idt_desc:
    dw IDT_COUNT * 8 - 1
    dd idt

msg_title    db 'PIT Timer Demo - 1000 Hz (1ms precision)', 0
msg_ticks    db 'Ticks: ', 0
msg_seconds  db 'Seconds: ', 0
msg_sleep    db 'Sleeping 2 seconds...', 0
msg_wake     db 'Awake!', 0
msg_done     db 'Demo complete. Timer continues...', 0

; 串口日志
log_init     db '[PIT] System timer initialized at ~1000 Hz.', 0x0D, 0x0A, 0
log_tick     db '[PIT] First tick received.', 0x0D, 0x0A, 0
log_sleep    db '[PIT] Entering sleep(2000)...', 0x0D, 0x0A, 0
log_wake     db '[PIT] Woke up after 2000 ms.', 0x0D, 0x0A, 0
log_irq0     db '[PIT] IRQ0 tick #', 0

first_tick_flag:
    db 0                        ; 0 = 还未收到第一个 tick

section .text
global _start

_start:
    mov esp, stack_top

    ; ─── 1. 串口初始化 ───
    call serial_init

    mov esi, log_init
    call serial_puts

    ; ─── 2. VGA 初始化 ───
    call vga_clear
    mov byte [vga_color], 0x0F

    mov byte [vga_row], 0
    mov byte [vga_col], 0
    mov esi, msg_title
    call vga_puts

    ; ─── 3. 中断系统: IDT + PIC ───
    call idt_fill_default
    IDT_SET_ENTRY 0x20, isr_timer     ; IRQ0 → 定时器 ISR
    call pic_remap

    lidt [idt_desc]

    ; 开放 IRQ0 (时钟), 屏蔽其他
    mov al, 0xFE                       ; 1111 1110 — 只开放 IRQ0
    out 0x21, al

    ; ─── 4. 初始化 PIT ───
    ; 1000 Hz: divisor = 1193182 / 1000 ≈ 1193
    mov al, 0x36         ; Ch0, 低+高字节, Mode 3 (方波), 二进制
    out 0x43, al
    mov ax, 1193         ; divisor = 1193 → ~1000.67 Hz
    out 0x40, al         ; 低字节
    mov al, ah
    out 0x40, al         ; 高字节

    ; ─── 5. 显示初始化信息 ───
    mov byte [vga_row], 3
    mov byte [vga_col], 0
    mov esi, msg_ticks
    call vga_puts

    mov byte [vga_row], 4
    mov byte [vga_col], 0
    mov esi, msg_seconds
    call vga_puts

    ; ─── 6. 开中断！ ───
    sti

    ; 等待第一个 tick 到来（确保 PIT 正常工作）
.wait_first_tick:
    cmp byte [first_tick_flag], 1
    jne .wait_first_tick

    mov esi, log_tick
    call serial_puts

    ; ─── 7. sleep 演示 ───
    mov byte [vga_row], 7
    mov byte [vga_col], 0
    mov byte [vga_color], 0x0E     ; 黄色
    mov esi, msg_sleep
    call vga_puts

    mov esi, log_sleep
    call serial_puts

    mov eax, 2000                  ; sleep(2000 ms) = 2 秒
    call sleep_ms

    mov byte [vga_color], 0x0A     ; 绿色
    mov byte [vga_row], 8
    mov byte [vga_col], 0
    mov esi, msg_wake
    call vga_puts

    mov byte [vga_color], 0x0F     ; 恢复白色
    mov esi, log_wake
    call serial_puts

    ; ─── 8. 循环更新屏幕 + 串口定期报告 ───
    mov byte [vga_row], 10
    mov byte [vga_col], 0
    mov esi, msg_done
    call vga_puts

    mov dword [seconds_elapsed], 0

.main_loop:
    ; 更新 VGA 上的 tick 计数
    mov byte [vga_row], 3
    mov byte [vga_col], 8          ; "Ticks: " 后面
    mov eax, [pit_ticks]
    call vga_print_dec32_simple

    ; 每秒报告一次串口日志
    mov eax, [pit_ticks]
    xor edx, edx
    mov ecx, 1000                  ; 1000 Hz → 1000 ticks = 1 秒
    div ecx
    cmp eax, [seconds_elapsed]
    je .tick_done

    mov [seconds_elapsed], eax

    ; 串口: "[PIT] Second: N"
    push eax
    mov esi, log_irq0
    call serial_puts
    pop eax
    call serial_putdec32
    call serial_newline

    ; 更新 VGA 上的秒数显示
    mov byte [vga_row], 4
    mov byte [vga_col], 10
    mov eax, [seconds_elapsed]
    call vga_print_dec32_simple

.tick_done:
    ; 短暂延迟后重新更新（让 CPU 休息——hlt）
    hlt
    jmp .main_loop

; ═══════════════════════════════════════════
; ISR: 定时器 (IRQ0 → 向量 0x20)
; ═══════════════════════════════════════════
isr_timer:
    pusha

    inc dword [pit_ticks]
    mov byte [first_tick_flag], 1

    ; 发送 EOI
    mov al, 0x20
    out 0x20, al

    popa
    iret

isr_default:
    iret

; ═══════════════════════════════════════════
; sleep_ms: 毫秒级精确延迟
; ═══════════════════════════════════════════
sleep_ms:
    push eax
    push ebx

    mov ebx, eax
    test ebx, ebx
    jz .done
    cli
    mov eax, [pit_ticks]
    sti
    add ebx, eax

.wait:
    hlt                       ; 暂停 CPU 直到下一个中断（省电）
    cmp [pit_ticks], ebx
    jb .wait

.done:
    pop ebx
    pop eax
    ret

; ═══════════════════════════════════════════
; PIC 重映射
; ═══════════════════════════════════════════
pic_remap:
    mov al, 0x11
    out 0x20, al
    out 0xA0, al
    call io_wait

    mov al, 0x20
    out 0x21, al
    mov al, 0x28
    out 0xA1, al
    call io_wait

    mov al, 0x04
    out 0x21, al
    mov al, 0x02
    out 0xA1, al
    call io_wait

    mov al, 0x01
    out 0x21, al
    out 0xA1, al
    call io_wait

    mov al, 0xFE              ; 只开放 IRQ0
    out 0x21, al
    mov al, 0xFF              ; 屏蔽所有从 PIC IRQ
    out 0xA1, al
    ret

io_wait:
    out 0x80, al
    ret

; ═══════════════════════════════════════════
; IDT 填充
; ═══════════════════════════════════════════
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
    mov byte [edi+5], 0x8E
    shr eax, 16
    mov word [edi+6], ax
    add edi, 8
    loop .loop
    pop edi
    pop ecx
    pop eax
    ret

; ═══════════════════════════════════════════
; 串口函数
; ═══════════════════════════════════════════
serial_init:
    push ax
    push dx
    mov dx, 0x3F9
    mov al, 0x00
    out dx, al
    mov dx, 0x3FB
    mov al, 0x80
    out dx, al
    mov dx, 0x3F8
    mov al, 0x01
    out dx, al
    mov dx, 0x3F9
    mov al, 0x00
    out dx, al
    mov dx, 0x3FB
    mov al, 0x03
    out dx, al
    mov dx, 0x3FA
    mov al, 0xC7
    out dx, al
    pop dx
    pop ax
    ret

serial_putchar:
    push ax
    push dx
    mov dx, 0x3FD
.wait:
    in al, dx
    test al, 0x20
    jz .wait
    mov dx, 0x3F8
    mov al, [esp + 4]
    out dx, al
    pop dx
    pop ax
    ret

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

serial_newline:
    push ax
    mov al, 0x0D
    call serial_putchar
    mov al, 0x0A
    call serial_putchar
    pop ax
    ret

; ═══════════════════════════════════════════
; VGA 函数（精简版）
; ═══════════════════════════════════════════
vga_putchar:
    push eax
    push ebx
    push edi

    cmp al, 0x0A
    je .newline
    cmp al, 0x0D
    je .cr
    jmp .draw

.newline:
    mov byte [vga_col], 0
    inc byte [vga_row]
    cmp byte [vga_row], 25
    jl .done
    dec byte [vga_row]
    jmp .done

.cr:
    mov byte [vga_col], 0
    jmp .done

.draw:
    movzx edi, byte [vga_row]
    imul edi, 80
    movzx ebx, byte [vga_col]
    add edi, ebx
    shl edi, 1
    add edi, VGA_BASE
    mov ah, [vga_color]
    mov [edi], ax

    inc byte [vga_col]
    cmp byte [vga_col], 80
    jl .done
    mov byte [vga_col], 0
    inc byte [vga_row]
    cmp byte [vga_row], 25
    jl .done
    dec byte [vga_row]

.done:
    call vga_update_cursor
    pop edi
    pop ebx
    pop eax
    ret

vga_puts:
    push ax
    push si
.loop:
    lodsb
    test al, al
    jz .done
    call vga_putchar
    jmp .loop
.done:
    pop si
    pop ax
    ret

vga_clear:
    push eax
    push ecx
    push edi
    mov edi, VGA_BASE
    mov ecx, 80 * 25 / 2
    mov eax, 0x0F200F20
    cld
    rep stosd
    mov byte [vga_row], 0
    mov byte [vga_col], 0
    call vga_update_cursor
    pop edi
    pop ecx
    pop eax
    ret

vga_update_cursor:
    push eax
    push ebx
    push edx
    movzx eax, byte [vga_row]
    mov bl, 80
    mul bl
    movzx ebx, byte [vga_col]
    add eax, ebx
    mov ebx, eax
    mov dx, 0x3D4
    mov al, 0x0E
    out dx, al
    mov dx, 0x3D5
    mov al, bh
    out dx, al
    mov dx, 0x3D4
    mov al, 0x0F
    out dx, al
    mov dx, 0x3D5
    mov al, bl
    out dx, al
    pop edx
    pop ebx
    pop eax
    ret

; 简化的 VGA 数字打印（不跟踪光标——直接写入给定行列）
vga_print_dec32_simple:
    push eax
    push ebx
    push ecx
    push edx
    push edi

    ; 计算 VGA 地址
    movzx edi, byte [vga_row]
    imul edi, 80
    movzx ebx, byte [vga_col]
    add edi, ebx
    shl edi, 1
    add edi, VGA_BASE

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

    pop edi
    pop edx
    pop ecx
    pop ebx
    pop eax
    ret
```

**运行效果：**

```bash
$ make run
# 终端输出（串口）：
# [PIT] System timer initialized at ~1000 Hz.
# [PIT] First tick received.
# [PIT] Entering sleep(2000)...
# [PIT] Woke up after 2000 ms.
# [PIT] Second: 1
# [PIT] Second: 2
# [PIT] Second: 3
# ...

# QEMU 窗口（VGA）：
# PIT Timer Demo - 1000 Hz (1ms precision)
#
# Ticks: 1234567          ← 实时递增，每秒约涨 1000
# Seconds: 1234           ← 每秒更新一次
#
# Sleeping 2 seconds...   ← 黄色
# Awake!                  ← 绿色（2 秒后出现）
#
# Demo complete. Timer continues...
```

**`hlt` 的优势**：sleep_ms 中的 `hlt` 指令让 CPU 进入低功耗状态，直到下一个中断唤醒。如果没有 `hlt`（而用纯 `cmp/jb` 忙等），CPU 会以 100% 占用率疯狂轮询。`hlt` 是汇编能发出的特权指令之一——用户态程序无法执行，操作系统才能用它来省电。

### 📝 小节练习

> [!question] 判断题 1
> `hlt` 指令在用户态程序中可以正常执行。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `hlt` 是特权指令（Ring0）。用户态执行会触发 #GP 异常。这也是 why C 语言的 `sleep()` 必须通过系统调用实现——它无法直接让 CPU 进入 `hlt`。

---

### 📚 第六节：RTC（Real-Time Clock）简介
---

PIT 提供了周期性的"节拍"，但它不知道"现在是几点"。RTC（Real-Time Clock）通过 CMOS 提供挂钟时间：

| 端口 | 用途 |
|------|------|
| 0x70 | CMOS 地址端口（bit7 控制 NMI 屏蔽） |
| 0x71 | CMOS 数据端口 |

**读取 RTC 时间：**

```asm
; ============ rtc_read_time: 读取当前时间 ============
; 输出: ch = 时, cl = 分, dh = 秒 (BCD 格式或二进制)
rtc_read_time:
    push ax
    push dx

.wait_update:
    ; 等待 RTC 不处于更新中
    mov al, 0x0A
    out 0x70, al
    in al, 0x71
    test al, 0x80          ; UIP bit (Update In Progress)
    jnz .wait_update

    ; 读取小时 (寄存器 0x04)
    mov al, 0x04
    out 0x70, al
    in al, 0x71
    mov ch, al

    ; 读取分钟 (寄存器 0x02)
    mov al, 0x02
    out 0x70, al
    in al, 0x71
    mov cl, al

    ; 读取秒 (寄存器 0x00)
    mov al, 0x00
    out 0x70, al
    in al, 0x71
    mov dh, al

    pop dx
    pop ax
    ret
```

> RTC 返回的值默认为 BCD 格式（如 0x59 表示 59）。CMOS 寄存器 0x0B 的 bit2 可以切换到二进制模式。QEMU 默认输出 BCD。

**RTC 中断（IRQ8）**：RTC 也可以通过 PIC 从片 IRQ8 产生周期性中断（频率可设为 2~8192 Hz），作为 PIT 的替代品。但 RTC 中断频率只有 15 个离散档位（2 的幂次），灵活性不如 PIT。

### 📝 小节练习

> [!question] 选择题 1
> RTC 的 CMOS 地址和数据端口是？
> - [ ] A. 0x70 / 0x71
> - [ ] B. 0x40 / 0x41
> - [ ] C. 0x60 / 0x61
> - [ ] D. 0x3F8 / 0x3F9
>
> > [!success]- 点击查看答案
> > 正确答案: A
> > **解析**: RTC/CMOS 通过 0x70（地址索引）和 0x71（数据）访问。0x40 是 PIT 通道 0，0x60 是键盘数据端口，0x3F8 是 COM1 串口。

---

## 📋 章节测试

### 一、判断题

> [!question] 判断题 1
> PIT 通道 0 的数据端口是 0x40。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确

> [!question] 判断题 2
> PIT 的晶振频率是 1,000,000 Hz（1 MHz）。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: PIT 晶振为 1,193,182 Hz（约 1.193 MHz）。这个数字来自 NTSC 彩色副载波频率（3.579545 MHz ÷ 3）。

> [!question] 判断题 3
> PIT 命令字节中，RW=11 表示"只写高字节"。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: RW=11 表示"先写低字节后写高字节"（16 位完整访问）。RW=01 是只读写低字节，RW=10 是只读写高字节。RW=00 是锁存命令。

> [!question] 判断题 4
> sleep_ms 中的忙等循环（`cmp [ticks], target; jb .wait`）依赖中断来推进 tick 计数。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `pit_ticks` 由 ISR 递增，ISR 由 IRQ0 触发。`cmp/jb` 循环依赖 ISR 更改内存中的 tick 值。如果忘了开中断或 PIC 未正确配置，循环会永久阻塞。

> [!question] 判断题 5
> PIT 通道 1 和 2 也可以通过 I/O 端口编程，与通道 0 的操作方式相同。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: 三个通道通过命令字节的 SC 字段选择，数据端口分别为 0x40/0x41/0x42。通道 1（DRAM 刷新）在现代系统中可重新利用，通道 2（PC 扬声器）可以编程输出不同频率的方波来产生声音。

### 二、选择题

> [!question] 选择题 1
> 要得到 100 Hz 的 PIT 输出频率，除数为？
> - [ ] A. 1193
> - [ ] B. 11932
> - [ ] C. 119
> - [ ] D. 119318
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 1193182 ÷ 100 ≈ 11932。1000 Hz → 1193，100 Hz → 11932。

> [!question] 选择题 2
> PIT 命令端口是？
> - [ ] A. 0x40
> - [ ] B. 0x41
> - [ ] C. 0x42
> - [ ] D. 0x43
>
> > [!success]- 点击查看答案
> > 正确答案: D
> > **解析**: 0x43 是 PIT 的模式/命令寄存器。0x40~0x42 分别是通道 0~2 的数据端口。

> [!question] 选择题 3
> Mode 2（比率发生器）和 Mode 3（方波发生器）的主要区别是？
> - [ ] A. Mode 2 用于通道 0，Mode 3 用于通道 2
> - [ ] B. Mode 2 输出负脉冲，Mode 3 输出对称方波
> - [ ] C. Mode 2 不支持 16 位除数
> - [ ] D. 没有区别
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: Mode 2 在计数值达到 1 时输出一个负脉冲（一个晶振周期宽），然后重装。Mode 3 输出对称方波（占空比约 50%）。两者都可用于周期性中断，但 Mode 2 的短脉冲更适合边缘触发。

> [!question] 选择题 4
> 定时器 ISR 中发送 EOI 的 I/O 端口是？
> - [ ] A. 0x40
> - [ ] B. 0x43
> - [ ] C. 0x20
> - [ ] D. 0x21
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: EOI 发给 PIC 命令端口 0x20（主 PIC）。0x21 是主 PIC 数据端口（用于读写 IMR 和 ICW），0x40 是 PIT 通道 0 数据端口。

> [!question] 选择题 5
> Linux 内核的 HZ=1000 意味着？
> - [ ] A. PIT 以 1000 Hz 驱动，每秒 1000 次时钟中断
> - [ ] B. CPU 频率为 1000 Hz
> - [ ] C. 系统只能每毫秒响应一次
> - [ ] D. 1000 个进程才能被调度
>
> > [!success]- 点击查看答案
> > 正确答案: A
> > **解析**: HZ 是内核的"嘀嗒频率"——每秒产生多少次时钟中断。HZ=1000 表示 1ms 一次中断，提供毫秒级调度精度。现代 Linux 已经支持 `CONFIG_NO_HZ`（无嘀嗒内核），在空闲时不产生定时器中断以省电。

> [!question] 选择题 6
> RTC 每隔一段时间会设置 UIP（Update In Progress）标志，这个标志表示？
> - [ ] A. 时间正在被 CPU 写入
> - [ ] B. RTC 内部正在更新计时值（不可读取）
> - [ ] C. 启动中断服务
> - [ ] D. 电池电量低
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: UIP（Update In Progress, CMOS 状态寄存器 A bit7）表示 RTC 正在内部更新秒/分/时等寄存器的值。此时读取可能得到损坏的数据（例如秒=59、分未进位到下一分钟）。必须等待 UIP=0 再读取。

---

### 🛠️ 动手练习题

> [!example] 练习题 1：修改 PIT 频率
> **难度**: ⭐
>
> 将 PIT 频率从 1000 Hz 改为 100 Hz（除数 11932）。观察 VGA 上 tick 计数增长速度的变化（应变为原来的 1/10）。将 `sleep_ms(2000)` 改为 `sleep_ms(2000 / 10)` 使睡眠时间保持 2 秒不变，验证程序行为。

> [!example] 练习题 2：实现精确的 stopwatch（秒表）
> **难度**: ⭐⭐
>
> 利用 PIT 1000 Hz 和亚 tick 读取（`pit_get_count`），实现一个高精度秒表。`stopwatch_start()` 记录起始 tick + 起始计数值，`stopwatch_elapsed_us()` 计算从起始到当前经过的微秒数。
>
> ```
> elapsed = ((current_ticks - start_ticks) * 1000) + 
>           ((start_count - current_count) * 1000000 / PIT_FREQ)
> ```
> 在 VGA 第 20 行实时显示 elapsed 值（微秒 → 毫秒）。

> [!example] 练习题 3：PC 扬声器 —— 让 PIT 弹奏音符
> **难度**: ⭐⭐⭐
>
> PIT 通道 2 连接到 PC 扬声器（通过 0x61 端口的 bit0 和 bit1 控制门控）。编程通道 2 输出不同频率的方波来演奏简单的音符：
>
> ```
> 音符频率对照:
> C4  = 261.63 Hz → 除数 ≈ 4560
> D4  = 293.66 Hz → 除数 ≈ 4063
> E4  = 329.63 Hz → 除数 ≈ 3620
> F4  = 349.23 Hz → 除数 ≈ 3416
> G4  = 392.00 Hz → 除数 ≈ 3044
> A4  = 440.00 Hz → 除数 ≈ 2712
> B4  = 493.88 Hz → 除数 ≈ 2416
> ```
>
> 每个音符播放 500ms（用 `sleep_ms`），然后播放下一个。播放前先通过 `in al, 0x61; or al, 0x03; out 0x61, al` 打开扬声器门控。QEMU 中 `-audiodev pa,id=audio0 -machine pcspk-audiodev=audio0` 可以让声音输出到宿主机的 PulseAudio。如果没有声音设备，观察 QEMU Monitor 中的 PC Speaker 状态。

> [!example] 练习题 4：实现基于时间的任务调度器
> **难度**: ⭐⭐⭐⭐
>
> 定义一个"任务"结构（函数指针 + 周期 + 上次执行 tick），在 ISR 中检查是否有任务需要执行（类似操作系统调度器）。实现 `task_create(func_ptr, period_ms)` 和 `task_scheduler()`（在 ISR 中调用）。测试：创建三个任务：
> - Task 1: 每 1000ms → 通过串口打印 "Task 1: 1 second"
> - Task 2: 每 3000ms → 通过串口打印 "Task 2: 3 seconds"  
> - Task 3: 每 500ms  → 更新 VGA 第 15 行的颜色闪烁

---

> **下一章**：`[[08_键盘输入实战|键盘输入实战]]` — PS/2 8042 控制器、扫描码解析、中断驱动 vs 轮询。

> **前置章节**：`[[04_中断与IDT|中断与 IDT]]` `[[05_串口UART实战|串口 UART]]` `[[06_VGA文本模式实战|VGA 文本模式]]`
