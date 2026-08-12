# VGA 文本模式实战：直接写显存 (VGA Text Mode: Direct Framebuffer)
---

## 📖 章节概述

VGA 文本模式是 x86 裸机编程中最直观的输出设备——屏幕上的每个字符像素对应内存中的两个字节。把 `'A'` 写到地址 `0xB8000`，屏幕上就出现一个 `A`。没有系统调用、没有 `ncurses`、没有显卡驱动——只有 `mov word [0xB8000], 0x0F41` 这条指令。这就是 MMIO（Memory-Mapped I/O）的最纯粹形式：写内存 = 操作设备。本章实现完整的 VGA 文本驱动：写字符、设置颜色、控制光标、滚动屏幕，并与串口组合成"串口调试 + VGA 显示"双输出系统。

> **核心理念**：This is ONLY possible in assembly — `mov word [0xB8000], 0x0F41` 将字符和颜色用一个原子操作写入显存。C 语言可以写 `*(volatile uint16_t*)0xB8000 = 0x0F41`，但你**看不到**实际发生的 mov 指令、不知道它被编译成什么寻址模式、不知道编译器是否插入了多余操作。汇编让你精确控制显存中的每一个字节——这就是为什么 bootloader 和早期 kernel 的 VGA 初始化全部用汇编编写。

---

### 📚 第一节：VGA 显存布局
---

#### 1.1 物理地址 0xB8000

VGA 文本模式下的显存（framebuffer）映射在物理地址 **0xB8000**。每个屏幕字符占用 **2 字节**：

```
显存地址    0xB8000  0xB8001  0xB8002  0xB8003     ...  0xB8F9E  0xB8F9F
           +--------+--------+--------+--------+         +--------+--------+
           | 字符   | 属性   | 字符   | 属性   |  ...    | 字符   | 属性   |
           +--------+--------+--------+--------+         +--------+--------+
               ↑ 第 1 个字符           ↑ 第 2 个字符           ↑ 第 2000 个字符
           (第 0 行, 第 0 列)       (第 0 行, 第 1 列)        (第 24 行, 第 79 列)
```

| 参数 | 值 |
|------|-----|
| 列数 | 80 |
| 行数 | 25 |
| 总字符数 | 80 × 25 = 2000 |
| 每字符字节 | 2 |
| 显存总大小 | 4000 字节 (0xFA0) |
| 地址范围 | 0xB8000 ~ 0xB8F9F |

> 还有 4 页可选（共 32KB），但默认使用第 0 页。每页 4000 字节。页面通过 `CRTC Offset` 寄存器切换，但除非你需要双缓冲，否则很少使用。

#### 1.2 坐标 → 地址换算

```asm
; 将 (row, col) 坐标转为 VGA 显存偏移地址
; 输入:  bh = row (0-24), bl = col (0-79)
; 输出: edi = 显存地址 (0xB8000 + offset)
; 
; offset = (row * 80 + col) * 2

get_cursor_addr:
    imul edi, ebx, 80 * 2    ; edi = row * 160
    movzx eax, bl             ; eax = col
    shl eax, 1                ; eax = col * 2
    add edi, eax              ; edi = row*160 + col*2
    add edi, 0xB8000
    ret
```

或者直接计算：
```asm
; 更高效的版本（一行代码）
; VGA 地址 = 0xB8000 + (row * 80 + col) * 2
mov edi, 0xB8000
; row * 80 * 2 = row * 160 = row << 7 + row << 5
; 即 row * 128 + row * 32
```

#### 1.3 为什么是 0xB8000？

这个地址是 IBM VGA 标准规定的"物理窗口"——VGA 卡在系统总线上监听对 0xA0000~0xBFFFF 的读写，不需要显式"映射"（这是老式 ISA 总线的优势：设备可以声明自己负责某个地址范围）。现代 PCI/PCIe 显卡的 framebuffer 地址需要通过 PCI BAR 读取，但在 QEMU 模拟器和所有带传统 BIOS 兼容的机器上，文本模式的 0xB8000 永远可用。

> **MMIO 的本质**：CPU 发出 `mov [0xB8000], ax`，地址总线上的信号 0xB8000 被 VGA 卡识别，VGA 卡把数据总线上 `ax` 的值解释为"字符+属性"并更新屏幕像素。CPU 不知道、也不关心这个地址对应的是 RAM 还是显存——它只是在执行一条普通的 `mov` 指令。

### 📝 小节练习

> [!question] 选择题 1
> VGA 文本模式下一个屏幕显示多少字符？
> - [ ] A. 80×24 = 1920
> - [ ] B. 80×25 = 2000
> - [ ] C. 80×30 = 2400
> - [ ] D. 100×25 = 2500
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 标准 VGA 文本模式为 80 列 × 25 行 = 2000 个字符。虽然 VGA 支持 80×30 和 132×43 等非标准模式，但需要额外配置 CRTC 寄存器。

> [!question] 判断题 1
> VGA 显存 0xB8000 是"物理地址"——不需要页表映射就可以在裸机上直接访问。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: 裸机（无分页）或启用分页后正确映射的情况下，物理地址 0xB8000 可直接访问。Linux 用户态程序无法访问 0xB8000——它需要通过 `/dev/mem` 或内核模块来映射该物理页。

---

### 📚 第二节：属性字节与颜色
---

#### 2.1 属性字节格式

每个字符的属性字节控制前景色、背景色和闪烁：

```
  7    6  5  4    3  2  1  0
+-----+--------+-----------+
| Blk | 背景色  |  前景色    |
+-----+--------+-----------+
```

| 位 | 含义 |
|----|------|
| 0-3 | 前景色（0-15） |
| 4-6 | 背景色（0-7） |
| 7 | 闪烁位（1 = 闪烁, 0 = 不闪烁） |

#### 2.2 调色板

| 值 | 颜色 | 值 | 亮色版本 |
|----|------|-----|---------|
| 0 | 黑色 (Black) | 8 | 暗灰 (Dark Gray) |
| 1 | 蓝色 (Blue) | 9 | 亮蓝 (Light Blue) |
| 2 | 绿色 (Green) | 10 | 亮绿 (Light Green) |
| 3 | 青色 (Cyan) | 11 | 亮青 (Light Cyan) |
| 4 | 红色 (Red) | 12 | 亮红 (Light Red) |
| 5 | 品红 (Magenta) | 13 | 亮品红 (Light Magenta) |
| 6 | 棕色 (Brown) | 14 | 黄色 (Yellow) |
| 7 | 浅灰 (Light Gray) | 15 | 白色 (White) |

> 实践中 0x0F = 黑底白字，0x1F = 蓝底白字，0x4F = 红底白字，0xF0 = 白底黑字，0x0E = 黑底黄字。`[[07_定时器PIT实战|定时器章节]]` 中会用颜色变化来可视化时钟脉冲。

#### 2.3 属性字节构造宏

```asm
; 构造属性字节
; 用法: VGA_ATTR 前景色, 背景色
%define VGA_ATTR(fg, bg) ((fg) | ((bg) << 4))

; 常用预设
%define COLOR_WHITE_ON_BLACK   0x0F
%define COLOR_YELLOW_ON_BLUE   0x1E
%define COLOR_RED_ON_BLACK     0x0C
%define COLOR_GREEN_ON_BLACK   0x0A
%define COLOR_BLACK_ON_WHITE   0xF0
```

```asm
; 在寄存器中构造属性
; ax = (char << 8) | (fg_color | (bg_color << 4))
mov ah, 0x0F           ; 黑底白字
mov al, 'A'            ; 字符
mov [0xB8000], ax      ; 屏幕左上角显示白色 'A'
```

### 📝 小节练习

> [!question] 选择题 1
> 属性字节 0x1F 表示什么颜色组合？
> - [ ] A. 黑底白字
> - [ ] B. 蓝底白字
> - [ ] C. 白底蓝字
> - [ ] D. 蓝底红字
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 0x1F = 背景 1（蓝色）+ 前景 15（白色）→ 蓝底白字。0xF1 是白底蓝字。

> [!question] 判断题 1
> VGA 文本模式支持 16 种前景色和 16 种背景色。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 前景色 16 种（4 bit），但背景色只有 8 种（3 bit，值 0-7）。bit 7 被闪烁占用而非背景色的第 4 位。这是 VGA 兼容性的历史限制。

---

### 📚 第三节：vga_putchar 与 vga_puts
---

#### 3.1 跟踪光标位置

```asm
; 全局状态（.data 或 .bss）
section .data
cursor_row:   db 0
cursor_col:   db 0
vga_color:    db 0x0F        ; 当前属性

; ============ vga_putchar: 在光标位置写一个字符并前进光标 ============
; 输入: al = 字符
vga_putchar:
    push eax
    push ebx
    push edi

    ; 处理特殊字符
    cmp al, 0x0A            ; '\n' 换行
    je .newline
    cmp al, 0x0D            ; '\r' 回车
    je .carriage_return
    cmp al, 0x08            ; '\b' 退格
    je .backspace
    jmp .draw_char

.newline:
    mov byte [cursor_col], 0
    inc byte [cursor_row]
    cmp byte [cursor_row], 25
    jl .check_done
    call vga_scroll         ; 超出屏幕 → 滚屏
    dec byte [cursor_row]   ; row = 24 (最后一行)
    jmp .check_done

.carriage_return:
    mov byte [cursor_col], 0
    jmp .check_done

.backspace:
    cmp byte [cursor_col], 0
    je .backspace_prev_line
    dec byte [cursor_col]
    jmp .overwrite_space
.backspace_prev_line:
    cmp byte [cursor_row], 0
    je .check_done
    dec byte [cursor_row]
    mov byte [cursor_col], 79
.overwrite_space:
    mov al, ' '

.draw_char:
    ; 计算 VGA 偏移: (row * 80 + col) * 2
    movzx edi, byte [cursor_row]
    imul edi, 80
    movzx ebx, byte [cursor_col]
    add edi, ebx
    shl edi, 1              ; 乘以 2
    add edi, 0xB8000

    ; 写入字符+属性
    mov ah, [vga_color]
    mov [edi], ax

    ; 前进光标列
    inc byte [cursor_col]
    cmp byte [cursor_col], 80
    jl .check_done
    ; 列溢出 → 换行
    mov byte [cursor_col], 0
    inc byte [cursor_row]
    cmp byte [cursor_row], 25
    jl .check_done
    call vga_scroll
    dec byte [cursor_row]

.check_done:
    call vga_update_cursor    ; 更新硬件光标位置
    pop edi
    pop ebx
    pop eax
    ret
```

#### 3.2 vga_puts：字符串输出

```asm
; ============ vga_puts: 输出 '\0' 结尾的字符串 ============
; 输入: esi = 字符串地址
; 破坏: al, esi 前进
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
```

#### 3.3 vga_clear：清屏

```asm
; ============ vga_clear: 用空格填充整个屏幕 ============
vga_clear:
    push eax
    push ecx
    push edi

    mov edi, 0xB8000
    mov ecx, 80 * 25        ; 2000 个字符
    mov ax, 0x0F20          ; 空格 + 黑底白字属性
    rep stosw               ; 高效批量写入: 每次 2 字节 (word)

    mov byte [cursor_row], 0
    mov byte [cursor_col], 0
    call vga_update_cursor

    pop edi
    pop ecx
    pop eax
    ret
```

> `rep stosw` 是 x86 字符串操作指令——在一条指令里完成 2000 次 word 写入。**This is ONLY possible in assembly**——C 语言的 `memset(0xB8000, 0x0F20, 4000)` 最终也会展开为 `rep stos` 序列（如果编译器够聪明），但你无法精确控制它使用 `stosw` 还是 `stosb`。汇编给了你绝对的控制权。

### 📝 小节练习

> [!question] 判断题 1
> `rep stosw` 指令组合使用 ECX 作为计数器。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `rep stosw` 重复 `stosw` ECX 次。每次 `stosw` 写入 AX 到 [EDI]，并且 EDI += 2。`rep stosb` 每次写入 AL，EDI += 1。

---

### 📚 第四节：光标控制
---

#### 4.1 VGA 光标寄存器

VGA 控制器通过两个 I/O 端口控制硬件光标：

| 端口 | 方向 | 作用 |
|------|------|------|
| 0x3D4 | 写 | CRTC 地址索引寄存器（选择要操作的内部寄存器） |
| 0x3D5 | 读/写 | CRTC 数据寄存器（读写被选中的内部寄存器） |

光标位置相关寄存器：

| 索引 | 寄存器 | 内容 |
|------|--------|------|
| 0x0E | Cursor Location High | 光标偏移的高 8 位 |
| 0x0F | Cursor Location Low | 光标偏移的低 8 位 |

> 光标偏移 = row × 80 + col（0 ~ 1999）

#### 4.2 更新光标

```asm
; ============ vga_update_cursor: 将软件光标同步到硬件 ============
vga_update_cursor:
    push eax
    push ebx
    push edx

    ; 计算偏移 = row * 80 + col
    movzx eax, byte [cursor_row]
    mov bl, 80
    mul bl                   ; ax = al * bl = row * 80
    movzx ebx, byte [cursor_col]
    add eax, ebx             ; eax = row * 80 + col
    mov ebx, eax             ; 保存偏移值

    ; 写入高字节 (Cursor Location High)
    mov dx, 0x3D4
    mov al, 0x0E
    out dx, al               ; 选择寄存器 0x0E
    mov dx, 0x3D5
    mov al, bh               ; 偏移的高 8 位
    out dx, al               ; 写入

    ; 写入低字节 (Cursor Location Low)
    mov dx, 0x3D4
    mov al, 0x0F
    out dx, al               ; 选择寄存器 0x0F
    mov dx, 0x3D5
    mov al, bl               ; 偏移的低 8 位
    out dx, al               ; 写入

    pop edx
    pop ebx
    pop eax
    ret
```

> 硬件光标独立于显存内容——即使你禁用光标（通过 `Cursor Start` 寄存器的 bit5），VGA 显示不受影响。光标只是一个闪烁的视觉效果，帮助用户知道下一个字符将出现的位置。

#### 4.3 禁用/启用光标

```asm
; ============ vga_cursor_off: 隐藏光标 ============
vga_cursor_off:
    push ax
    push dx
    mov dx, 0x3D4
    mov al, 0x0A            ; Cursor Start Register
    out dx, al
    mov dx, 0x3D5
    in al, dx
    or al, 0x20             ; bit5 = 1 → 禁用光标
    out dx, al
    pop dx
    pop ax
    ret

; ============ vga_cursor_on: 显示光标 ============
vga_cursor_on:
    push ax
    push dx
    mov dx, 0x3D4
    mov al, 0x0A
    out dx, al
    mov dx, 0x3D5
    in al, dx
    and al, 0xDF            ; bit5 = 0 → 启用光标
    out dx, al
    pop dx
    pop ax
    ret
```

### 📝 小节练习

> [!question] 选择题 1
> VGA 光标控制端口是？
> - [ ] A. 0x3F8 / 0x3F9
> - [ ] B. 0x3D4 / 0x3D5
> - [ ] C. 0x60 / 0x64
> - [ ] D. 0x3C0 / 0x3C1
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: CRTC 寄存器通过 0x3D4（索引）和 0x3D5（数据）访问。0x3F8 是 COM1 串口，0x60/0x64 是键盘控制器，0x3C0/0x3C1 是 Attribute Controller。

---

### 📚 第五节：滚屏实现
---

当光标到达第 24 行（屏幕底线）并需要换行时，不能简单地把光标重置——整个屏幕的内容需要向上滚动一行：

```asm
; ============ vga_scroll: 将屏幕内容向上滚动一行 ============
; 算法:
;   1. 把第 1~24 行内容复制到第 0~23 行
;   2. 把第 24 行清空为空格
;   3. 保持光标列不变，光标行已经是 24
vga_scroll:
    push eax
    push ecx
    push esi
    push edi

    ; 源地址: 0xB8000 + 1行 = 0xB8000 + 160
    ; 目标地址: 0xB8000
    ; 复制 24 行 × 80 列 × 2 字节 = 3840 字节
    mov esi, 0xB8000 + 80*2   ; 源: 第 1 行开头
    mov edi, 0xB8000           ; 目标: 第 0 行开头
    mov ecx, 80 * 24           ; 复制 1920 个 word (3840 字节)

    ; 使用 rep movsd 每次复制 4 字节（更快）
    shr ecx, 1                 ; ecx = 960 个 dword
    cld                        ; 方向标志: 正向 (esi, edi 递增)
    rep movsd

    ; 如果还有剩余的 word (ecx 为奇数的情况)
    jnc .clear_last
    movsw

.clear_last:
    ; 清空最后一行 (第 24 行)
    mov edi, 0xB8000 + 80*2*24
    mov ecx, 80
    mov ax, 0x0F20            ; 空格 + 黑底白字
    rep stosw

    pop edi
    pop esi
    pop ecx
    pop eax
    ret
```

> **性能注记**：`rep movsd` 每次复制 4 字节（两个字符+属性对），比 `rep movsb`（每次 1 字节）快约 4 倍。1920 个 word = 960 个 dword。这是最底层的优化——你精确知道数据大小和硬件性能特征，不必依赖编译器的自动向量化猜测。

**滚屏优化技巧**：可以不复制显存，而是通过设置 CRTC 的 `Start Address High/Low` 寄存器（索引 0x0C/0x0D）来改变显存起始地址——这是 VGA 的硬件滚屏。但这种方法较复杂（需要处理换页和 4KB 边界），对于学习目的，软件复制更直观。

### 📝 小节练习

> [!question] 判断题 1
> 滚屏时使用 `rep movsd` 比使用 `rep movsb` 更快，因为它每次传输 4 字节。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `movsd` 每次复制一个 dword（4 字节）。在 32 位总线上，这是最优传输粒度。但需要注意对齐——如果显存未 4 字节对齐，`movsd` 也不会出错（x86 支持非对齐访问），只是性能略降。

---

### 📚 第六节：完整示例 —— VGA + 串口双输出
---

以下程序在一个裸机上同时使用 **VGA（屏幕显示）** 和 **串口（调试日志）**。这是后续所有章节的标配模式：VGA 给用户看，串口给开发者看。

```asm
; kernel.asm — VGA 文本模式 + 串口双输出
; 编译: nasm -f elf32 kernel.asm -o kernel.o
; 链接: ld -m elf_i386 -T link.ld kernel.o -o kernel.elf
; 运行: qemu-system-x86_64 -kernel kernel.elf -serial stdio
;       (打开 QEMU 窗口看 VGA, 串口输出到终端)

bits 32

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

; ──── 数据段 ────
section .data
cursor_row:  db 0
cursor_col:  db 0
vga_color:   db 0x0F          ; 黑底白字

msg_vga      db 'VGA demo: colors!', 0
msg_debug    db '[DEBUG] VGA + Serial initialized.', 0x0D, 0x0A, 0

section .text
global _start

_start:
    mov esp, stack_top

    call serial_init

    ; 串口：开发日志
    mov esi, msg_debug
    call serial_puts

    ; VGA：清屏并显示标题
    call vga_clear

    ; 颜色演示：用不同颜色显示 "Colors!"
    mov byte [cursor_row], 0
    mov byte [cursor_col], 0

    mov byte [vga_color], 0x0F
    mov esi, msg_vga
    call vga_puts

    ; 显示颜色条：16 种前景色在屏幕各行
    xor ecx, ecx
.color_loop:
    cmp ecx, 16
    jge .color_done
    mov byte [cursor_row], cl
    inc byte [cursor_row]      ; 从第 2 行开始
    mov byte [cursor_col], 0

    ; 设置不同颜色
    mov [vga_color], cl

    ; 打印颜色编号
    mov al, '0'
    cmp cl, 10
    jl .digit_ok
    add al, 7                  ; 'A' - '0' 的跳位
.digit_ok:
    add al, cl
    call vga_putchar

    mov al, ':'
    call vga_putchar
    mov al, ' '
    call vga_putchar

    ; 打印颜色名称
    shl ecx, 1
    mov esi, [color_names + ecx]
    shr ecx, 1
    call vga_puts

    inc ecx
    jmp .color_loop
.color_done:

    ; 最后一行显示光标操作提示
    mov byte [cursor_row], 24
    mov byte [cursor_col], 0
    mov byte [vga_color], 0x0E      ; 黄色
    mov esi, msg_footer
    call vga_puts

    ; 串口日志：VGA 初始化完成
    mov esi, msg_vga_done
    call serial_puts

    hlt
    jmp $

; ═══════════════════════════════════════════
; VGA 函数
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
    mov byte [cursor_col], 0
    inc byte [cursor_row]
    cmp byte [cursor_row], 25
    jl .done
    call vga_scroll
    dec byte [cursor_row]
    jmp .done

.cr:
    mov byte [cursor_col], 0
    jmp .done

.draw:
    movzx edi, byte [cursor_row]
    imul edi, 80
    movzx ebx, byte [cursor_col]
    add edi, ebx
    shl edi, 1
    add edi, 0xB8000
    mov ah, [vga_color]
    mov [edi], ax
    inc byte [cursor_col]
    cmp byte [cursor_col], 80
    jl .done
    mov byte [cursor_col], 0
    inc byte [cursor_row]
    cmp byte [cursor_row], 25
    jl .done
    call vga_scroll
    dec byte [cursor_row]

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
    mov edi, 0xB8000
    mov ecx, 80 * 25 / 2    ; 1000 个 dword (覆盖 2000 个 word)
    mov eax, 0x0F200F20     ; 两个连续的"空格+黑底白字"
    cld
    rep stosd
    mov byte [cursor_row], 0
    mov byte [cursor_col], 0
    call vga_update_cursor
    pop edi
    pop ecx
    pop eax
    ret

vga_scroll:
    push eax
    push ecx
    push esi
    push edi
    mov esi, 0xB8000 + 80*2
    mov edi, 0xB8000
    mov ecx, 80 * 24 / 2   ; 960 dword
    cld
    rep movsd
    mov edi, 0xB8000 + 80*2*24
    mov ecx, 80 / 2        ; 40 dword 填充最后一行
    mov eax, 0x0F200F20
    rep stosd
    pop edi
    pop esi
    pop ecx
    pop eax
    ret

vga_update_cursor:
    push eax
    push ebx
    push edx
    movzx eax, byte [cursor_row]
    mov bl, 80
    mul bl
    movzx ebx, byte [cursor_col]
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

; ═══════════════════════════════════════════
; 串口函数（精简版，完整版见 05_串口UART实战.md）
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

; ──── 数据 ────
section .data

color_names:
    dd name_black,  name_blue,   name_green,  name_cyan
    dd name_red,    name_mag,    name_brown,  name_lgray
    dd name_dgray,  name_lblue,  name_lgreen, name_lcyan
    dd name_lred,   name_lmag,   name_yellow, name_white

name_black   db 'Black', 0
name_blue    db 'Blue', 0
name_green   db 'Green', 0
name_cyan    db 'Cyan', 0
name_red     db 'Red', 0
name_mag     db 'Magenta', 0
name_brown   db 'Brown', 0
name_lgray   db 'Light Gray', 0
name_dgray   db 'Dark Gray', 0
name_lblue   db 'Light Blue', 0
name_lgreen  db 'Light Green', 0
name_lcyan   db 'Light Cyan', 0
name_lred    db 'Light Red', 0
name_lmag    db 'Light Magenta', 0
name_yellow  db 'Yellow', 0
name_white   db 'White', 0

msg_footer   db 'VGA+Serial Demo Complete. Press Ctrl-A X to quit QEMU.', 0
msg_vga_done db '[DEBUG] VGA display populated (color table).', 0x0D, 0x0A, 0

section .bss
align 16
stack_bottom:
    resb 16384
stack_top:
```

**运行效果：**
```bash
$ make run
# 终端输出（串口）：
# [DEBUG] VGA + Serial initialized.
# [DEBUG] VGA display populated (color table).

# QEMU 窗口（VGA）：
# VGA demo: colors!
# 1: Blue       ← 蓝色前景
# 2: Green      ← 绿色前景
# ...
# 15: White     ← 白色前景（第 16 行）
# (第 24 行) VGA+Serial Demo Complete.
```

> **串口 + VGA 双输出模式是裸机开发的最佳实践**：VGA 展示程序给用户的界面（如果这是一个终端程序或游戏），串口提供开发者可见的调试日志（变量值、函数调用栈、内存布局）。`[[05_串口UART实战|上一章]]` 和本章一起构成了后续所有章节的 I/O 基础设施。

### 📝 小节练习

> [!question] 判断题 1
> VGA 光标位置和显存内容之间没有任何关系——改变光标不影响显存。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: 光标是一个独立的硬件状态（存储于 CRTC 寄存器），与显存中的像素数据完全独立。改变光标位置不会改变显存中的任何字节，反之亦然。

---

## 📋 章节测试

### 一、判断题

> [!question] 判断题 1
> VGA 文本模式显存起始于物理地址 0xB0000。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 文本模式显存起始于 0xB8000。0xB0000 是单色文本模式的地址。0xA0000 是图形模式。

> [!question] 判断题 2
> VGA 文本模式下每个字符占用 1 字节显存。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 每个字符占用 2 字节——1 字节 ASCII 码 + 1 字节属性（颜色/闪烁）。

> [!question] 判断题 3
> `rep stosw` 配合 ECX 计数时，EDI 每次递增 2。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确

> [!question] 判断题 4
> 滚屏时必须通过复制显存数据——无法通过硬件实现。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: VGA 支持硬件滚屏——通过修改 CRTC Start Address 寄存器改变显存的"第一个像素"位置。当起始地址增加一行（160 字节），屏幕自动上滚一行。但需要处理显存绕回（0xB8FA0 ~ 0xBFFFF）。

> [!question] 判断题 5
> C 语言可以通过 `*(volatile uint16_t*)0xB8000 = 0x0F41` 直接写 VGA 显存——所以这个操作不是"汇编特有"的。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: C 确实可以通过 volatile 指针操作 MMIO。但 C 编译器插入的额外指令（加载基址到寄存器、可能的 sign extension、优化导致的乱序）是不可见的。汇编让你精确到**每一条指令**——这就是为什么 bootloader 和性能关键的内核代码仍然用汇编写显存操作。

### 二、选择题

> [!question] 选择题 1
> VGA 文本模式 80×25 的显存大小是？
> - [ ] A. 2000 字节
> - [ ] B. 4000 字节
> - [ ] C. 8000 字节
> - [ ] D. 16000 字节
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 2000 字符 × 2 字节/字符 = 4000 字节（0xFA0）。

> [!question] 选择题 2
> 属性字节 0x0E 表示？
> - [ ] A. 黑底白字
> - [ ] B. 黑底黄字
> - [ ] C. 蓝底白字
> - [ ] D. 白底黑字
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 0x0E = 背景 0（黑）+ 前景 14（黄）→ 黑底黄字。0x04 是黑底红字。

> [!question] 选择题 3
> VGA 光标控制寄存器的索引端口是？
> - [ ] A. 0x3D4
> - [ ] B. 0x3D5
> - [ ] C. 0x3D4 和 0x3D5 轮流
> - [ ] D. 既是索引也是数据
>
> > [!success]- 点击查看答案
> > 正确答案: A
> > **解析**: 0x3D4 是 CRTC 地址/索引端口（选择寄存器），0x3D5 是 CRTC 数据端口（读写选中的寄存器）。0x3C4/0x3C5 是 Sequencer，0x3CE/0x3CF 是 Graphics Controller。

> [!question] 选择题 4
> 光标偏移 = row × 80 + col，此值的范围是？
> - [ ] A. 0 ~ 255
> - [ ] B. 0 ~ 1999
> - [ ] C. 0 ~ 3999
> - [ ] D. 0 ~ 65535
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 光标偏移是字符索引（row × 80 + col），范围 0 ~ 1999（25 行 × 80 列 - 1）。不是字节偏移（0 ~ 3998）。

> [!question] 选择题 5
> `cld` 指令在 `rep movsd` 前的作用是？
> - [ ] A. 清除 ecx 计数器
> - [ ] B. 设置方向标志为正向（EDI/ESI 递增）
> - [ ] C. 禁用中断
> - [ ] D. 清除进位标志
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `cld`（Clear Direction Flag）将 EFLAGS.DF 设为 0，使得 `movsd` 和 `stosw` 等字符串指令从低地址向高地址操作（EDI/ESI 递增）。`std`（Set Direction Flag）则相反。

---

### 🛠️ 动手练习题

> [!example] 练习题 1：实现 vga_setcolor
> **难度**: ⭐
>
> 实现 `vga_setcolor(fg, bg)` 函数：参数通过 `al`（前景色）和 `ah`（背景色）传入，合并后存入 `[vga_color]`。扩展 vga_putchar 支持在同一个屏幕上同时显示多种前景色（比如第 1 行红色，第 2 行绿色）。

> [!example] 练习题 2：VGA 进度条
> **难度**: ⭐⭐
>
> 在屏幕中央（第 12 行附近）绘制一个进度条：用不同颜色的空格块填充。比如 `0x0F20` 是进度块，`0x0F00` 是非进度背景。通过改变填充长度来模拟 0%~100% 的进度。每个"进度块"是一个全角空格（或 `#` 字符）。

> [!example] 练习题 3：实现 vga_gotoxy
> **难度**: ⭐
>
> 实现 `vga_gotoxy(row, col)`：将光标移动到指定位置。参数 `bh = row`, `bl = col`。移动后自动调用 `vga_update_cursor`。用此函数重写颜色演示程序，将每种颜色名称定位在固定列（例如第 10 列），使所有颜色名称在一条垂直线对齐。

> [!example] 练习题 4：硬件滚屏实现
> **难度**: ⭐⭐⭐⭐
>
> 用硬件滚屏替代软件 `rep movsd`：通过修改 CRTC Start Address 寄存器实现。显存共有 32KB（8 页），当前显示起始地址由 Start Address 控制。每滚一行，起始地址 += 80 字节（一行字符对应的字节数，注意是字符偏移不是字节偏移——对 VGA 控制器而言，一"行" = 80 个字符偏移 = 160 字节）。
>
> 提示：`Start Address High` 在 CRTC 索引 0x0C，`Start Address Low` 在 0x0D。需要处理显存的环形绕回（到达 0xBFFFF 后回到 0xB8000）。

---

> **下一章**：`[[07_定时器PIT实战|定时器 PIT 实战]]` — 掌握可编程时钟，实现毫秒级精确延时和周期性中断。

> **前置章节**：`[[05_串口UART实战|串口 UART]]` `[[04_中断与IDT|中断与 IDT]]` `[[01_Port_IO与MMIO|Port I/O 与 MMIO]]`
