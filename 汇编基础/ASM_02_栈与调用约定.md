# x86-64 汇编 —— 栈与调用约定
---

## 栈（Stack）

栈是一块从高地址向低地址增长的内存区域，由 `rsp`（栈顶指针）管理。

```
高地址
┌──────────────┐
│  argv, envp  │  ← 程序启动时的栈
├──────────────┤
│  函数参数 n   │  ← 第7+个参数（超出入寄存器范围的）
├──────────────┤
│  返回地址     │  ← call 指令压入
├──────────────┤
│  旧的 rbp    │  ← 被调用者保存
├──────────────┤
│  局部变量     │  ← 函数内部分配
├──────────────┤
│  ...         │
├──────────────┤
│  (空闲)      │
└──────────────┘  ← rsp（栈顶，低地址）
低地址
```

### 基本栈操作

```asm
push rax        ; rsp = rsp - 8; [rsp] = rax（入栈）
pop  rax        ; rax = [rsp]; rsp = rsp + 8（出栈）
sub  rsp, 32    ; 分配 32 字节栈空间
add  rsp, 32    ; 释放 32 字节栈空间
```

### 函数调用全过程

以 `int add(int a, int b)` 为例（Linux System V ABI）：

```asm
; 调用者：
mov edi, 3       ; 第1参数 → rdi
mov esi, 5       ; 第2参数 → rsi
call add         ; 压入返回地址，跳转到 add
; rsp 指向返回地址

; 被调用者 (add)：
push rbp         ; 保存调用者的 rbp
mov  rbp, rsp    ; 建立自己的栈帧
mov  eax, edi    ; eax = a
add  eax, esi    ; eax = a + b（返回值在 eax）
pop  rbp         ; 恢复调用者的 rbp
ret              ; 弹出返回地址，返回调用者
```

## 调用约定（Calling Convention）

调用约定定义了函数参数的传递顺序和寄存器使用规则。C++ 教程中常出现两套 ABI：

### System V AMD64 ABI（Linux / macOS / BSD）

| 参数位置 | 寄存器 |
|:---------|:-------|
| 第1参数（整数/指针） | `rdi` |
| 第2参数 | `rsi` |
| 第3参数 | `rdx` |
| 第4参数 | `rcx` |
| 第5参数 | `r8` |
| 第6参数 | `r9` |
| 第7+ 参数 | **栈**（从右向左压入） |
| 返回值 | `rax` |

> C++ 非静态成员函数的隐式第一参数是 **this 指针**，因此在 Linux 上 this 通过 `rdi` 传递。这是 C++ 教程 [[../cpp教程/cpp深化教程/05_面向对象(一)类与对象基础]] 中讲解 this 指针底层机制的基础。

### Microsoft x64 ABI（Windows）

| 参数位置 | 寄存器 |
|:---------|:-------|
| 第1参数 | `rcx` |
| 第2参数 | `rdx` |
| 第3参数 | `r8` |
| 第4参数 | `r9` |
| 第5+ 参数 | **栈** |
| 返回值 | `rax` |

> Windows 上 this 通过 `rcx` 传递（因为它是第一个参数）。

### 对比示例

```cpp
int add(int a, int b) { return a + b; }

struct Foo {
    int val;
    int addTo(int x) { return val + x; }
};
```

Linux 上的汇编：

```asm
; int add(int a, int b)
; a→edi, b→esi
add:
    lea eax, [rdi+rsi]   ; eax = a + b
    ret

; int Foo::addTo(int x)
; this→rdi, x→esi
Foo::addTo:
    mov eax, [rdi]       ; eax = this->val（val 在偏移 0）
    add eax, esi         ; eax = this->val + x
    ret
```

Windows 上的汇编：

```asm
; int add(int a, int b)
; a→ecx, b→edx
add:
    lea eax, [rcx+rdx]   ; eax = a + b
    ret

; int Foo::addTo(int x)
; this→rcx, x→edx
Foo::addTo:
    mov eax, [rcx]       ; eax = this->val
    add eax, edx         ; eax = this->val + x
    ret
```

> 同一份 C++ 代码，Linux 和 Windows 生成不同的汇编，但语义等价。理解这一差异后就不会在看到不同平台的汇编时困惑。

## 被调用者保存 vs 调用者保存

| 分类 | 寄存器 | 规则 |
|:-----|:------|:-----|
| 被调用者保存 | `rbx`, `rbp`, `r12`~`r15` | 函数使用前必须保存原值，返回前恢复 |
| 调用者保存 | `rax`, `rcx`, `rdx`, `rsi`, `rdi`, `r8`~`r11` | 函数可自由修改，调用者需自行保存 |

> 编译器会处理这些细节。手动写汇编或阅读编译输出时需了解。

## 栈对齐

x86-64 ABI 要求 `call` 指令执行前 `rsp` 必须 16 字节对齐。`push`/`pop` 操作 8 字节，编译器自动插入 `sub rsp, 8` 等调整。在 C++ 教程 [[../cpp教程/cpp深化教程/05_面向对象(一)类与对象基础]] 的内存对齐章节中，对象大小必须是最大对齐值的整数倍，与此要求一脉相承。
