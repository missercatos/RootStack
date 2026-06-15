# x86-64 汇编速览 —— 寄存器与基础指令
## ============================================================

本文件覆盖阅读 C++ 教程汇编示例所需的最小知识。建议与 [[../C兼容/C_02_指针与内存]] 对照阅读。

> 系统性深入学习汇编语言与计算机底层原理，请参阅专门的汇编教程：[[../../ASM教程/01_体系结构与寄存器]]

## 为什么看汇编？

C++ 教程在多处用汇编解释底层行为：
- this 指针如何传递（`rdi` vs `rcx`）
- 虚函数调用为何多一次间接跳转
- 构造函数/析构函数在何时被调用
- 成员变量访问的偏移计算

看懂汇编才能理解 C++ **为什么**是这样。

## x86-64 通用寄存器

x86-64 有 16 个 64 位通用寄存器。每个寄存器有 64/32/16/8 位子名：

| 64位 | 32位 | 16位 | 8位 | 常见用途 |
|:-----|:-----|:-----|:---|:---------|
| `rax` | `eax` | `ax` | `al` | 返回值 |
| `rbx` | `ebx` | `bx` | `bl` | 被调用者保存 |
| `rcx` | `ecx` | `cx` | `cl` | 第4参数(linux)/第1参数(win) |
| `rdx` | `edx` | `dx` | `dl` | 第3参数(linux)/第2参数(win) |
| `rsi` | `esi` | `si` | `sil` | 第2参数(linux) |
| `rdi` | `edi` | `di` | `dil` | 第1参数(linux)→this指针 |
| `rbp` | `ebp` | `bp` | `bpl` | 栈帧基址指针 |
| `rsp` | `esp` | `sp` | `spl` | 栈顶指针 |
| `r8` | `r8d` | `r8w` | `r8b` | 第5参数(linux)/第3参数(win) |
| `r9` | `r9d` | `r9w` | `r9b` | 第6参数(linux)/第4参数(win) |
| `r10`~`r15` | `r10d`~ | ... | ... | 通用/临时 |

> 记不住全部？只记住：**`rax`=返回值, `rdi`=第一参数(Linux this), `rcx`=第一参数(Windows this), `rsp`=栈顶**。其余用到时查阅即可。

## 基础指令

### 数据传送

```asm
mov rax, rbx        ; rax = rbx（寄存器→寄存器）
mov rax, [rdi]      ; rax = *rdi（内存→寄存器，读 rdi 指向的 8 字节）
mov [rdi], rax      ; *rdi = rax（寄存器→内存）
mov eax, 42         ; eax = 42（立即数→寄存器，高32位自动清零）
lea rax, [rdi+8]    ; rax = rdi + 8（加载地址，不读内存）
```

### 算术

```asm
add  rax, rbx       ; rax = rax + rbx
sub  rax, 10        ; rax = rax - 10
imul rbx            ; rdx:rax = rax * rbx（有符号乘法）
inc  rax            ; rax = rax + 1
dec  rax            ; rax = rax - 1
```

### 比较与跳转

```asm
cmp  rax, 10        ; 计算 rax - 10，设置标志位（不存结果）
je   label          ; 等于则跳转（jump if equal）
jne  label          ; 不等于则跳转
jg   label          ; 大于则跳转（有符号）
jl   label          ; 小于则跳转
jmp  label          ; 无条件跳转
```

### 函数调用

```asm
call func           ; push rip; rip = func（调用函数）
ret                 ; pop rip（返回）
```

## 寻址模式

```asm
[rdi]               ; 基址寻址：地址 = rdi
[rdi + 8]           ; 基址+偏移：地址 = rdi + 8
[rdi + rcx*4]       ; 基址+索引*比例：地址 = rdi + rcx*4
[rdi + rcx*4 + 8]   ; 完整形式：基址+索引*比例+偏移
```

> `[rdi + 8]` 是访问成员变量的核心指令。若 `rdi` = this 指针，`[rdi+8]` 就是偏移 8 处的成员（跳过 vptr 后的第一个成员）。

## 阅读示例：访问成员变量

```cpp
class Point { int x, y; };   // y 在 offset 4
void setY(Point* p, int v) { p->y = v; }
```

编译为（Linux System V ABI，`rdi`=p, `esi`=v）：

```asm
setY:
    mov [rdi+4], esi     ; *(p + 4) = v   → 即 p->y = v
    ret
```

> `y` 的偏移是 4（`x` 占 offset 0~3），因此 `p->y` 编译为 `[rdi+4]`。这就是 C++ 对象成员访问的汇编真面目。
