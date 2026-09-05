# 字节码与 dis：Python 也是"编译"的 (Bytecode & dis)
---

## 章节概述

"Python 是解释型语言"——这句话只说对了一半。Python 源码在执行前会被**编译为字节码**（bytecode），由 Python 虚拟机（PVM）执行。本章使用 `dis` 模块反汇编 Python 代码，逐条解读字节码指令，并与 C 语言的四阶段编译流程进行系统对比。理解字节码层，是优化 Python 性能、理解生成器和 async/await 的必备基础。

> **核心理念**：Python 的"编译"与 C 的编译本质不同——Python 编译产物是平台无关的字节码（.pyc），由软件虚拟机解释执行；C 编译产物是平台相关的机器码，由 CPU 直接执行。但两者的分层抽象思想是相通的。

---

### 第一节：Python 的"编译"过程

#### 1.1 .py → 字节码 → 执行

```mermaid
graph LR
 A[".py 源代码"] -- "编译 (隐式)" --> B["字节码 .pyc<br/>(在 __pycache__)"]
 B -- "执行 (PVM)" --> C["输出"]
```

Python 的编译发生在**导入模块时**（import）或**执行脚本前**（隐式），不需要显式的编译命令。

```bash
# 查看编译后的字节码缓存
echo "x = 1 + 2" > test.py
python -c "import test" # 导入 → 编译 → 缓存
ls __pycache__/ # test.cpython-312.pyc
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

---

### 第二节：dis 模块入门

`dis` 是 Python 内置的反汇编器，将字节码转换回人类可读的助记符。

```bash
python -c "
import dis
dis.dis('x = 1 + 2')
"
```

输出及逐条解读：

```
 0 0 RESUME 0

 1 2 LOAD_CONST 0 (3)
 4 STORE_NAME 0 (x)
 6 RETURN_CONST 0 (None)
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
 0 0 RESUME 0

 2 2 LOAD_CONST 0 (10)
 4 STORE_NAME 0 (a)

 3 6 LOAD_CONST 1 (20)
 8 STORE_NAME 1 (b)

 4 10 LOAD_NAME 0 (a)
 12 LOAD_NAME 1 (b)
 14 BINARY_OP 0 (+)
 18 STORE_NAME 2 (c)
 20 RETURN_CONST 2 (None)
```

这里 `a + b` 无法在编译期折叠（因为 a 和 b 是变量，编译时不知道它们的值），所以保留了 `LOAD_NAME` + `LOAD_NAME` + `BINARY_OP` 三个指令。

---

### 第三节：常用字节码指令速查

CPython 3.12+ 有约 160 条字节码指令，以下是核心指令：

#### 3.1 栈操作

PVM 是基于**栈的虚拟机**（而非基于寄存器）。所有操作数从栈顶弹出，结果压入栈顶：

```
操作前栈 指令 操作后栈
[1, 2] BINARY_ADD [3]
[a, b] BINARY_OP [result]
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
 2 2 LOAD_CONST 0 (10)
 4 STORE_NAME 0 (x)

 3 6 LOAD_NAME 0 (x)
 8 LOAD_CONST 1 (5)
 10 COMPARE_OP 4 (>) # 比较并压入 True/False
 14 POP_JUMP_IF_FALSE 4 (to 24) # False → 跳转到 24

 4 16 LOAD_CONST 2 (1) # if 分支
 18 STORE_NAME 1 (y)
 20 JUMP_FORWARD 4 (to 28) # 跳过 else

 6 >> 24 LOAD_CONST 3 (2) # else 分支
 26 STORE_NAME 1 (y)

 7 >> 28 LOAD_NAME 2 (print)
 30 LOAD_NAME 1 (y)
 32 CALL 1
 40 POP_TOP
 42 RETURN_CONST 0 (None)
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
 2 0 RESUME 0

 3 2 LOAD_FAST 0 (a)
 4 LOAD_FAST 1 (b)
 6 BINARY_OP 0 (+)
 10 RETURN_VALUE
```

> **C 对比**：C 函数调用 `add(a, b)` 编译为 `call <add>` 汇编指令（压栈参数 → 跳转 → 执行 → ret 返回）。Python 中函数调用涉及创建栈帧、参数解析、字节码跳转——开销远超 C。这就是 Python 函数调用比你想象的慢的根本原因。

---

### 第四节：__pycache__ 和 py_compile

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
# mymodule.cpython-312.pyc ← 文件名包含 Python 版本和实现
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

---

### 第五节：PVM 字节码执行原理

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
 PyObject *res = PyNumber_Add(left, right); // 实际运算
 Py_DECREF(left); Py_DECREF(right);
 SET_TOP(res);
 break;
 }
 case POP_JUMP_IF_FALSE: {
 PyObject *cond = POP();
 if (!PyObject_IsTrue(cond)) {
 next_instr += oparg; // 跳转
 }
 break;
 }
 // ... 另外 157 个 case
 }
 }
}
```

> **这解释了 Python 慢的核心原因**：`x = a + b` 在 C 中是 `mov eax, a; add eax, b; mov x, eax`（3 条机器指令）。在 Python 中是 `LOAD_FAST` → `LOAD_FAST` → `BINARY_OP` → `STORE_FAST`（4 条字节码），每条字节码对应 C 中数十条指令（类型检查、溢出检查、引用计数操作）。

---

## 力扣练习

以下题目用于验证本章所学内容：

| 题号 | 题目 | 链接 | 涉及知识点 |
|------|------|------|-----------|
| — | 本章无对应力扣题 | — | 请用动手练习题自检 |
