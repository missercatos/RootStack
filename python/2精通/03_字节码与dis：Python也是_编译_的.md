# 字节码与 dis：Python 也是"编译"的 (Bytecode & dis)
---

## 📖 章节概述

"Python 是解释型语言"——这句话只说对了一半。Python 源码在执行前会被**编译为字节码**（bytecode），由 Python 虚拟机（PVM）执行。本章使用 `dis` 模块反汇编 Python 代码，逐条解读字节码指令，并与 C 语言的四阶段编译流程进行系统对比。理解字节码层，是优化 Python 性能、理解生成器和 async/await 的必备基础。

> **核心理念**：Python 的"编译"与 C 的编译本质不同——Python 编译产物是平台无关的字节码（.pyc），由软件虚拟机解释执行；C 编译产物是平台相关的机器码，由 CPU 直接执行。但两者的分层抽象思想是相通的。

---

### 📚 第一节：Python 的"编译"过程

#### 1.1 .py → 字节码 → 执行

```
┌──────────┐     编译     ┌──────────────┐     执行     ┌──────────┐
│  .py     │ ──────────▶ │  字节码 .pyc  │ ──────────▶ │   输出    │
│  源代码   │   (隐式)     │ (在__pycache__)│   (PVM)     │          │
└──────────┘              └──────────────┘              └──────────┘
```

Python 的编译发生在**导入模块时**（import）或**执行脚本前**（隐式），不需要显式的编译命令。

```bash
# 查看编译后的字节码缓存
echo "x = 1 + 2" > test.py
python -c "import test"        # 导入 → 编译 → 缓存
ls __pycache__/                # test.cpython-312.pyc
```

#### 1.2 对比：C 编译四步骤 vs Python 编译

差异是本质性的：

| 阶段 | C | Python |
|------|---|--------|
| 预处理 | `gcc -E` → .i 文件（展开 `#include`/`#define`） | 无预处理阶段 |
| 编译 | `gcc -S` → .s 汇编代码 | AST → 字节码（平台无关） |
| 汇编 | `gcc -c` → .o 机器码目标文件 | 无汇编阶段 |
| 链接 | `ld` 合并 .o + 库 → 可执行文件 | 无链接阶段 |
| 执行 | CPU 直接执行机器指令 | PVM 解释执行字节码 |
| 产物 | 平台相关的 ELF/PE/Mach-O | 平台无关的 .pyc（可跨平台） |

> **关键差异**：C 编译产物是 CPU 直接执行的机器码（一条 C 语句 ≈ 几条机器指令）。Python 编译产物是字节码（一条 Python 语句 ≈ 多条字节码），每条字节码由 PVM 的 `switch-case` 循环模拟执行——这额外引入了一到两个数量级的性能开销。

### 📝 小节练习

> [!question] 判断题 1
> Python 源码直接被解释器逐行解释，不存在"编译"阶段。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: Python 在执行前会将源码编译为字节码（.pyc），再由 PVM 执行。字节码缓存存储在 `__pycache__` 目录中。这与"逐行解释"的 shell 脚本不同。

> [!question] 选择题 1
> Python 字节码文件的扩展名是？
> - [ ] A. .pyo
> - [ ] B. .pyc
> - [ ] C. .pyd
> - [ ] D. .pyz
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: .pyc 是 Python 编译后的字节码文件，存放在 `__pycache__` 目录中。.pyo 是 Python 2 的优化字节码扩展名（已废弃），.pyd 是 Windows 上的 Python 扩展模块（实为 .dll），.pyz 是 zipapp 格式。

---

### 📚 第二节：dis 模块入门

`dis` 是 Python 内置的反汇编器，将字节码转换回人类可读的助记符。

```bash
python -c "
import dis
dis.dis('x = 1 + 2')
"
```

输出及逐条解读：

```
  0           0 RESUME                   0

  1           2 LOAD_CONST               0 (3)
              4 STORE_NAME               0 (x)
              6 RETURN_CONST             0 (None)
```

| 列 | 含义 |
|----|------|
| 第一列 `0` / `1` | 源码行号 |
| 第二列 `0` / `2` / `4` / `6` | 字节码偏移（字节） |
| 第三列 `LOAD_CONST` | 指令助记符 |
| 第四列 `0` / `3` | 操作数（参数） |
| 第五列 `(3)` | 操作数的实际值（提示） |

**关键发现**：`1 + 2` 在编译阶段就被**常量折叠**成了 `3`！字节码中直接 `LOAD_CONST 0 (3)`，而不是先加载 1 和 2 再执行加法。这是 CPython 编译器的 peephole 优化之一。

#### 2.1 带变量的表达式

```bash
python -c "
import dis
code = '''
a = 10
b = 20
c = a + b
'''
dis.dis(code)
"
```

输出：
```
  0           0 RESUME                   0

  2           2 LOAD_CONST               0 (10)
              4 STORE_NAME               0 (a)

  3           6 LOAD_CONST               1 (20)
              8 STORE_NAME               1 (b)

  4          10 LOAD_NAME                0 (a)
             12 LOAD_NAME                1 (b)
             14 BINARY_OP                0 (+)
             18 STORE_NAME               2 (c)
             20 RETURN_CONST             2 (None)
```

这里 `a + b` 无法在编译期折叠（因为 a 和 b 是变量，编译时不知道它们的值），所以保留了 `LOAD_NAME` + `LOAD_NAME` + `BINARY_OP` 三个指令。

### 📝 小节练习

> [!question] 选择题 1
> `dis.dis('x = 2 * 3')` 的输出中直接出现了哪个值？
> - [ ] A. 2 和 3 分别加载
> - [ ] B. 6
> - [ ] C. None
> - [ ] D. 空
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `2 * 3` 是编译时常量，会被 peephole 优化器折叠为 `6`，字节码中直接 `LOAD_CONST 6`。

> [!question] 判断题 1
> `dis.dis()` 可以反汇编任意已编译的函数对象。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `dis.dis(func)` 可以反汇编 Python 函数、方法、生成器等任何 `__code__` 属性非空的可调用对象。还可以反汇编模块和类。

---

### 📚 第三节：常用字节码指令速查

CPython 3.12+ 有约 160 条字节码指令，以下是核心指令：

#### 3.1 栈操作

PVM 是基于**栈的虚拟机**（而非基于寄存器）。所有操作数从栈顶弹出，结果压入栈顶：

```
操作前栈     指令       操作后栈
[1, 2]    BINARY_ADD   [3]
[a, b]    BINARY_OP    [result]
```

| 指令 | 操作数 | 说明 |
|------|--------|------|
| `LOAD_CONST` | const_index | 将常量推入栈顶 |
| `LOAD_NAME` | name_index | 从命名空间加载变量，推入栈 |
| `LOAD_FAST` | var_num | 从局部变量加载，推入栈（最快） |
| `LOAD_GLOBAL` | name_index | 从全局变量加载 |
| `STORE_NAME` | name_index | 弹出栈顶并存入命名空间 |
| `STORE_FAST` | var_num | 弹出栈顶并存入局部变量 |
| `POP_TOP` | — | 弹出并丢弃栈顶元素 |
| `DUP_TOP` | — | 复制栈顶元素 |
| `ROT_TWO` | — | 交换栈顶两个元素 |
| `RETURN_VALUE` | — | 弹出栈顶并返回 |
| `RETURN_CONST` | const_index | 直接返回常量 |

#### 3.2 控制流

```bash
python -c "
import dis
code = '''
x = 10
if x > 5:
    y = 1
else:
    y = 2
print(y)
'''
dis.dis(code)
"
```

输出：
```
  2           2 LOAD_CONST               0 (10)
              4 STORE_NAME               0 (x)

  3           6 LOAD_NAME                0 (x)
              8 LOAD_CONST               1 (5)
             10 COMPARE_OP               4 (>)      # 比较并压入 True/False
             14 POP_JUMP_IF_FALSE        4 (to 24)  # False → 跳转到 24

  4          16 LOAD_CONST               2 (1)      # if 分支
             18 STORE_NAME               1 (y)
             20 JUMP_FORWARD             4 (to 28)  # 跳过 else

  6     >>   24 LOAD_CONST               3 (2)      # else 分支
             26 STORE_NAME               1 (y)

  7     >>   28 LOAD_NAME                2 (print)
             30 LOAD_NAME                1 (y)
             32 CALL                     1
             40 POP_TOP
             42 RETURN_CONST             0 (None)
```

#### 3.3 函数调用

```bash
python -c "
import dis
def add(a, b):
    return a + b
dis.dis(add)
"
```

输出：
```
  2           0 RESUME                   0

  3           2 LOAD_FAST                0 (a)
              4 LOAD_FAST                1 (b)
              6 BINARY_OP                0 (+)
             10 RETURN_VALUE
```

> **C 对比**：C 函数调用 `add(a, b)` 编译为 `call <add>` 汇编指令（压栈参数 → 跳转 → 执行 → ret 返回）。Python 中函数调用涉及创建栈帧、参数解析、字节码跳转——开销远超 C。这就是 Python 函数调用比你想象的慢的根本原因。

### 📝 小节练习

> [!question] 选择题 1
> CPython 的虚拟机架构是？
> - [ ] A. 基于寄存器的虚拟机
> - [ ] B. 基于栈的虚拟机
> - [ ] C. 基于内存的虚拟机
> - [ ] D. 基于 LLVM 的 JIT
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: CPython 的 PVM 是基于栈的虚拟机，与 Java 虚拟机（基于栈）类似，而 Lua 5 和 V8 后端的 TurboFan 使用的是基于寄存器的架构。

> [!question] 选择题 2
> `LOAD_FAST` 和 `LOAD_NAME` 的区别是？
> - [ ] A. 没有区别
> - [ ] B. `LOAD_FAST` 访问局部变量（数组索引），更快
> - [ ] C. `LOAD_FAST` 访问全局变量
> - [ ] D. `LOAD_NAME` 更快
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `LOAD_FAST` 直接通过数组索引访问局部变量（O(1) 数组操作，无哈希查找），是最快的加载指令。`LOAD_NAME` 需要在命名空间字典中查找（哈希查找），较慢。

---

### 📚 第四节：__pycache__ 和 py_compile

#### 4.1 字节码缓存机制

```bash
# 创建模块
echo 'def greet(name):
    return f"Hello, {name}!"
' > mymodule.py

# 导入（触发编译 → 缓存）
python -c "import mymodule"

# 查看缓存
ls -la __pycache__/
# mymodule.cpython-312.pyc   ← 文件名包含 Python 版本和实现
```

字节码文件的命名规则：`{module}.cpython-{version}.pyc`，例如 `mymodule.cpython-312.pyc`。不同 Python 版本（甚至同版本的不同实现，如 CPython vs PyPy）的字节码**不兼容**。

#### 4.2 手动编译

```python
import py_compile

# 编译单个文件
py_compile.compile('mymodule.py', cfile='mymodule.pyc')

# 编译整个目录
import compileall
compileall.compile_dir('.', force=True)
```

#### 4.3 直接执行字节码

```bash
# .pyc 文件可以直接运行（只要 Python 版本匹配）
python __pycache__/mymodule.cpython-312.pyc
```

### 📝 小节练习

> [!question] 判断题 1
> Python 3.10 和 Python 3.12 生成的 .pyc 文件可以互相替换使用。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 字节码格式很可能会因版本而异。.pyc 文件名包含版本号（如 `cpython-312`），不同大版本间的字节码不兼容。这就是 `__pycache__` 会保留多个版本的原因。

> [!question] 选择题 1
> 如果 `__pycache__` 已存在一个 `.pyc`，Python 如何判断是否需要重新编译？
> - [ ] A. 每次都重新编译
> - [ ] B. 比较 .py 和 .pyc 的修改时间戳
> - [ ] C. 检查 .py 的 MD5
> - [ ] D. 永不重新编译
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: Python 比较 .py 源文件和 .pyc 缓存文件的 mtime（修改时间戳）。如果 .py 更新，则重新编译。这个时间戳也嵌入在 .pyc 文件头中用于校验。

---

### 📚 第五节：PVM 字节码执行原理

PVM 的核心是一个**巨大的 switch-case 循环**：

```c
// CPython 源码简化：Python/ceval.c
// 这是 Python 解释器的主循环

PyObject* _PyEval_EvalFrame(PyThreadState *tstate, PyFrameObject *frame) {
    // ...
    while (1) {
        opcode = _Py_OPCODE(*next_instr);
        switch (opcode) {
            case LOAD_FAST: {
                PyObject *value = GETLOCAL(oparg);
                Py_INCREF(value);
                PUSH(value);
                break;
            }
            case BINARY_OP: {
                PyObject *right = POP();
                PyObject *left = TOP();
                PyObject *res = PyNumber_Add(left, right);  // 实际运算
                Py_DECREF(left); Py_DECREF(right);
                SET_TOP(res);
                break;
            }
            case POP_JUMP_IF_FALSE: {
                PyObject *cond = POP();
                if (!PyObject_IsTrue(cond)) {
                    next_instr += oparg;  // 跳转
                }
                break;
            }
            // ... 另外 157 个 case
        }
    }
}
```

> **这解释了 Python 慢的核心原因**：`x = a + b` 在 C 中是 `mov eax, a; add eax, b; mov x, eax`（3 条机器指令）。在 Python 中是 `LOAD_FAST` → `LOAD_FAST` → `BINARY_OP` → `STORE_FAST`（4 条字节码），每条字节码对应 C 中数十条指令（类型检查、溢出检查、引用计数操作）。

### 📝 小节练习

> [!question] 选择题 1
> PVM 的主解释循环实现位于 CPython 源码的哪个文件中？
> - [ ] A. `Python/ast.c`
> - [ ] B. `Python/ceval.c`
> - [ ] C. `Python/compile.c`
> - [ ] D. `Python/import.c`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `Python/ceval.c` 包含 PVM 的主循环 `_PyEval_EvalFrame`，这是 Python 字节码执行的核心。`compile.c` 负责编译（AST→字节码），`import.c` 处理模块导入，`ast.c` 处理抽象语法树。

---

## 📋 章节测试

### 一、判断题

> [!question] 判断题 1
> CPython 中所有 Python 代码都会在执行前被编译为字节码。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: 所有 Python 代码（REPL 一行行输入、脚本文件、模块导入）都会先编译为字节码再执行。REPL 模式下是逐条语句编译和执行。

> [!question] 判断题 2
> `dis.dis()` 反汇编的是机器码。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `dis.dis()` 反汇编的是 Python 字节码（bytecode），不是机器码。Python 字节码是平台无关的中间表示。

> [!question] 判断题 3
> `.pyc` 文件包含了与 `.py` 文件相同的源代码。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `.pyc` 文件包含的是编译后的字节码和元数据（时间戳、magic number 等），不包含原始源代码。这也是为什么 `.pyc` 可以作为某种"闭源"分发的形式（虽然可以被反汇编）。

> [!question] 判断题 4
> `BINARY_OP` 指令完成一次运算后，结果会自动推入栈顶。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: 基于栈的虚拟机中，运算指令弹出操作数、计算结果后，结果会被压入栈顶供后续指令使用。

> [!question] 判断题 5
> 删除 `__pycache__` 目录会破坏 Python 程序的正常运行。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `__pycache__` 只是缓存。删除后 Python 会在下次导入模块时重新从 .py 编译字节码，只是首次执行会稍慢。

---

### 二、选择题

> [!question] 选择题 1
> Python 字节码编译中，"常量折叠"指的是什么？
> - [ ] A. 将所有变量替换为常量
> - [ ] B. 在编译时计算常量表达式的结果
> - [ ] C. 将常量和变量分开存储
> - [ ] D. 将代码折叠为一行
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 常量折叠（Constant Folding）是在编译时预计算常量表达式。如 `1 + 2 * 3` 在字节码中直接变为 `7`，减少运行时计算。

> [!question] 选择题 2
> `LOAD_FAST` 加载变量的查询复杂度是？
> - [ ] A. O(1) — 数组索引
> - [ ] B. O(n) — 链表遍历
> - [ ] C. O(log n) — 二分查找
> - [ ] D. O(1) 均摊 — 哈希表
>
> > [!success]- 点击查看答案
> > 正确答案: A
> > **解析**: 局部变量存储在数组（帧的 `localsplus`）中，`LOAD_FAST` 直接按索引访问，复杂度 O(1) 且常数极小。这也是局部变量比其他类型变量快的原因。

> [!question] 选择题 3
> 以下哪种代码在编译时会发生常量折叠？
> - [ ] A. `x = a + b`（a, b 是变量）
> - [ ] B. `x = len([1, 2])`
> - [ ] C. `x = "Hello" + " " + "World"`
> - [ ] D. `x = int(input())`
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: 字符串常量的拼接在编译时完成。`len([1,2])` 在 Python 3.12+ 也可能被折叠为 `2`（更激进的优化），但变量运算和依赖运行的表达式无法折叠。

> [!question] 选择题 4
> Python 每次启动时是否需要重新编译所有标准库？
> - [ ] A. 是
> - [ ] B. 否，使用 .pyc 缓存
> - [ ] C. 仅在第一次使用时编译
> - [ ] D. 取决于操作系统
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: CPython 安装时标准库的 .pyc 文件已预编译。仅在 .py 比 .pyc 更新时（如手动编辑了标准库源码）才会重新编译。

> [!question] 选择题 5
> Python 3.12 的字节码与 Python 3.11 的字节码兼容吗？
> - [ ] A. 完全兼容
> - [ ] B. 不兼容（格式变化）
> - [ ] C. 部分兼容
> - [ ] D. 仅在 Windows 上兼容
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: Python 各版本之间字节码格式可能变化。3.11 引入了自适应指令和 changed bytecode format；3.12 进一步改变了部分指令。.pyc 文件头包含 magic number 来标识版本。

> [!question] 选择题 6
> 以下哪个操作在 PVM 的执行开销最高？
> - [ ] A. `LOAD_FAST`（局部变量加载）
> - [ ] B. `BINARY_OP`（加法运算）
> - [ ] C. 函数调用 `CALL`
> - [ ] D. `POP_TOP`（弹出栈顶）
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: 函数调用 `CALL` 需要创建新栈帧、参数解析、`locals` 数组分配、上下文切换等，开销远超简单栈操作或二元运算。这就是 Python "函数调用昂贵"的字节码根源。

> [!question] 选择题 7
> 要查看一段 Python 代码编译成的字节码，应使用？
> - [ ] A. `python -m compile test.py`
> - [ ] B. `python -m dis test.py`
> - [ ] C. `gcc -S test.py`
> - [ ] D. `python -m ast test.py`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `python -m dis` 以模块形式运行 dis。`-m compile` 用于编译 .py 文件，`-m ast` 显示抽象语法树。GCC 不能编译 Python 文件。

---

### 🛠️ 动手练习题

> [!example] 练习题 1：字节码阅读
> **难度**: ⭐
>
> 编写一个包含以下元素的函数，用 `dis.dis()` 反汇编并逐条注释字节码：
> - 局部变量赋值和运算
> - `if/elif/else` 分支
> - `for` 循环（包括 `range`）
> - 函数内部调用另一个函数
>
> 特别注意循环中字节码的跳转指令（`JUMP_BACKWARD`、`POP_JUMP_IF_TRUE` 等）

> [!example] 练习题 2：性能实验
> **难度**: ⭐⭐
>
> 对比以下三种写法的字节码数量，并用 `timeit` 测试性能差异：
> 1. `result = []` + `result.append(i)` 循环
> 2. 列表推导式 `[i for i in range(n)]`
> 3. `list(range(n))`
>
> 解释字节码层面的性能差异原因（为什么列表推导式比 `append` 循环快）

> [!example] 练习题 3：pyc 文件探索
> **难度**: ⭐
>
> 1. 创建一个模块 `mylib.py`（包含几个函数和类）
> 2. 导入该模块，查看 `__pycache__/mylib.cpython-xxx.pyc` 的内容（前 16 字节为文件头）
> 3. 用 `py_compile` 手动编译同一文件，对比生成的文件
> 4. 用 `compileall` 编译当前目录的所有 .py 文件

> [!example] 练习题 4：PVM 模拟器
> **难度**: ⭐⭐⭐
>
> 实现一个极简的 Python 字节码解释器：
> - 支持指令：`LOAD_CONST`、`STORE_NAME`、`LOAD_NAME`、`BINARY_OP`、`RETURN_VALUE`
> - 实现栈、命名空间（dict）、指令指针
> - 用 `dis.Bytecode` 解析函数的字节码作为输入
> - 能正确执行简单的四则运算函数
>
> 这让你深刻理解 PVM 的工作原理！
