# 认识 Python 与 python -c 一行流 (Python Quickstart)
---

## 章节概述

本章面向 C 程序员介绍 Python 作为"胶水工具"的核心理念。你将看到 Python 如何消除 C 语言的"编译-链接-运行"循环，用 `python -c "..."` 一行流实现快速验证。我们将对比 `gcc hello.c && ./a.out` 与 `python -c "print('hello')"` 的本质区别——解释型语言的即时反馈让 Python 成为 C 程序员手中最锋利的瑞士军刀。

> **核心理念**：Python 不是 C 的替代品，而是 C 的"外挂"。当你需要快速验证算法、操作文件、解析 JSON 或是写一个 50 行的胶水脚本时，Python 能让你在 3 秒内看到结果——这在 C 的世界里是不可想象的。

---

### 第一节：Python 的"编译-运行"模型 vs C 的编译模型
---

1.1 C 程序员的日常 vs Python 的日常
-------------------------------------

作为 C 程序员，你的日常工作流是这样的：

```bash
# 编辑源码
vim hello.c

> **跨平台提示**：
> - **Windows**：推荐 VSCode 或 PyCharm 编辑源码；vim 用户可用 WSL 或 gVim
> - **macOS**：系统自带 vim，也可用 VSCode/PyCharm

# 编译
gcc -Wall -Wextra -g -O0 -std=c11 -o hello hello.c

# 运行
./hello
```

这个过程至少需要：
1. 写源文件（手写 `#include`，写 `main` 函数，处理返回值）
2. 编译（如果编译失败，看错误信息，回到第 1 步）
3. 运行（如果段错误，回到第 1 步加调试代码）
4. 重复

总耗时：**至少 30 秒**（编辑 10s + 编译 10s + 运行 10s）

Python 的对等工作流：

```bash
python -c "print('Hello, World!')"
```

总耗时：**3 秒**（打字 2.5s + 执行 0.5s）。不需要写 `main` 函数，不需要指定返回类型，不需要 `#include`，不需要管内存——甚至不需要新建文件。

1.2 Python 在执行什么？
-----------------------

C 编译模型：
```
源码(.c) → 预处理 → 编译(.s) → 汇编(.o) → 链接 → 可执行文件 → CPU 执行机器码
```

Python 执行模型：
```
源码(.py) → 编译为字节码(.pyc) → PVM (Python 虚拟机) 解释执行
```

关键区别：Python **也有编译步骤**，但它是**自动且隐式的**。解释器将源码编译为平台无关的字节码（`.pyc`），然后由 Python Virtual Machine 逐条解释。你从一开始就不需要关心这个过程。

```bash
# Python 字节码藏在 __pycache__ 目录中
python -c "import hashlib; print('hello')"
ls __pycache__
# hashlib.cpython-312.pyc ← 编译后的字节码
```

> 这与 Java 的 `javac → java` 模式相似，但 Python 隐藏了编译步骤，让你感觉像在"直接运行源代码"。

1.3 为什么 C 程序员需要 Python
-------------------------------

**场景一：快速验证算法思路**

```bash
# C 方式：新建文件、写完整的 main、编译、运行
# Python 方式：
python -c "print(sum(i*i for i in range(100) if i % 3 == 0))"
```

**场景二：文件批量处理**

```bash
# 把当前目录所有 .c 文件中的 GPL 注释替换为 MIT 注释
python -c "
import os, glob
for f in glob.glob('*.c'):
 with open(f) as fp:
 content = fp.read()
 content = content.replace('GPL', 'MIT')
 with open(f, 'w') as fp:
 fp.write(content)
 print(f'Processed {f}')
"
```

**场景三：JSON/CSV 数据清洗**

```bash
python -c "
import json
data = json.load(open('input.json'))
# 过滤、计算、转换...
json.dump(data, open('output.json', 'w'), indent=2)
"
```

> 在做这些任务时，C 不是做不到——是**太慢了**。Python 的一行流让你把注意力放在逻辑上，而不是内存管理和头文件上。

### 小节练习


> [!question] 判断题 1
> `python -c "print(42)"` 与 `gcc hello.c && ./a.out` 的执行效率完全等价。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: C 编译为原生机器码由 CPU 直接执行；Python 需要通过 PVM 逐条解释字节码，执行效率通常比 C 慢 10-100 倍。Python 的优势在于**开发速度**而非执行速度。

---

### 第二节：python -c 一行流艺术
---

2.1 基本语法
------------

`python -c` 的核心是：**在命令行参数中直接写 Python 代码**。

```bash
# 最简单的用法
python -c "print('hello')"

# 用分号分隔多条语句
python -c "x = 42; print(x * 2)"

# 用 \n 换行（bash 中 $'...' 语法）
python -c $'for i in range(5):\n print(i)'

# 更实用的方式：引号内嵌入换行（bash 按回车后继续输入）
python -c "
for i in range(3):
 print(f'Line {i}: {i**2}')
"
```

> Bash 中双引号 `"` 内的 `${}` 和 `$()` 会被展开。如果你的 Python 代码中包含这些字符，要么用单引号，要么用 `\$` 转义。

2.2 常见一行流模式
------------------

```bash
# 计算数学表达式
python -c "print(3.14159 * 10 * 10)"

# 操作列表
python -c "arr = [i*2 for i in range(10)]; print(arr)"

# 操作系统命令
python -c "import os; print(os.listdir('.'))"

# JSON 处理
python -c "import json; print(json.dumps({'key': 'value'}, indent=2))"

# 字符串编码
python -c "print('你好世界'.encode('utf-8'))"

# Base64 编解码
python -c "import base64; print(base64.b64encode(b'hello').decode())"

# 查看模块路径
python -c "import sys; print('\n'.join(sys.path))"

# 时间戳转换
python -c "import time; print(time.strftime('%Y-%m-%d'))"

# 正则表达式
python -c "import re; print(re.findall(r'\d+', 'a1b22c333'))"

# 快速 HTTP 请求
python -c "import urllib.request; print(urllib.request.urlopen('https://httpbin.org/get').read()[:200])"
```

2.3 多语句 vs 单表达式
---------------------

`python -c` 的参数是一个**完整的 Python 语句块**。以下写法错误：

```bash
python -c "x = 5" # 合法：赋值语句
python -c "print(x)" # 错误：x 未定义（上一行已结束）
python -c "x = 5; print(x)" # 合法：分号连接多个语句
```

如果你需要在多个 `-c` 之间保持状态，请用 shell 变量中转：

```bash
RESULT=$(python -c "print(2**100)")
python -c "print($RESULT % 7)"
```

### 小节练习


---

### 第三节：python -m 模块模式
---

3.1 什么是 `-m` 模式
--------------------

`python -m module_name` 的作用是：**将模块当作脚本来运行**。

```bash
# 查看所有已安装模块
python -c "help('modules')"

# 将某个模块作为脚本执行
python -m http.server 8080 # 启动一个简易 HTTP 服务器
python -m json.tool data.json # 格式化 JSON 文件
python -m pdb my_script.py # 以调试模式运行脚本
python -m pip install requests # 安装第三方包
python -m venv myenv # 创建虚拟环境
python -m timeit "'-'.join(str(n) for n in range(100))" # 性能测试
```

3.2 `-m` 与直接调用的区别
--------------------------

```bash
# 方式一：直接运行脚本文件
python /usr/lib/python3.12/pdb.py myscript.py

> **跨平台提示**：
> - **Windows**：Python 标准库路径通常在 `%LOCALAPPDATA%\Programs\Python\Python312\Lib\`
> - **macOS**：路径类似 `/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/`

# 方式二：用 -m 运行模块
python -m pdb myscript.py
```

`-m` 的优势：
- **路径无关**：不需要知道模块文件的具体路径
- **自动处理 `__name__`**：被运行模块的 `__name__` 设为 `"__main__"`
- **包内相对导入正确**：模块内的 `from . import xxx` 在 `-m` 模式下正常工作

```bash
# 验证 __name__
python -c "print(__name__)"
# 输出: __main__ ← -c 模式中 __name__ 始终是 __main__

# 直接执行文件
echo 'print(__name__)' > test.py
python test.py
# 输出: __main__

# 作为模块导入
python -c "import test; print('done')"
# 输出: test ← import 时 __name__ 是模块名
```

3.3 Shebang 行：让 Python 脚本直接运行
--------------------------------------

```python
#!/usr/bin/env python3
"""一个可直接执行的 Python 脚本"""

import sys

def main():
 print(f"脚本名: {sys.argv[0]}")
 print(f"参数: {sys.argv[1:]}")

if __name__ == "__main__":
 main()
```

```bash
chmod +x script.py
./script.py arg1 arg2
```

> **跨平台提示**：
> - **Windows**：不需要 `chmod +x`，直接 `python script.py arg1 arg2` 运行。PowerShell 中也可在脚本首行加 `#!/usr/bin/env python3`（PowerShell 识别 shebang）后直接 `./script.py`。
> - **macOS**：与 Linux 一致，使用 `chmod +x script.py && ./script.py
```

对比 C 程序的 "shebang" 等价物：

```c
// C 语言没有真正的 shebang。你必须：
// 1. 编译：gcc -o program program.c
// 2. 运行：./program arg1 arg2
//
// 而 Python 脚本可以直接：
// ./script.py arg1 arg2
// 因为内核识别 #! 行，自动调用解释器
```

> C 的 `#include` 是**预处理指令**，Python 的 `#!/usr/bin/env python3` 是**内核级解释器指令**。两者都以 `#` 开头，但完全是不同的机制。

### 小节练习


---

### 第四节：REPL 交互模式
---

4.1 启动 REPL
-------------

```bash
python3 # 启动交互式解释器
python3 -i script.py # 执行脚本后进入交互模式（保留所有变量）
```

对 C 程序员来说，REPL 是一个陌生的概念——C 语言没有交互式编程模式。Python REPL 相当于一个"随时可以执行代码的计算器"：

```python
>>> 2 + 2
4
>>> import math
>>> math.sqrt(144)
12.0
>>> [i**3 for i in range(5)]
[0, 1, 8, 27, 64]
>>> type("hello")
<class 'str'>
>>> dir(str) # 查看 str 类型的所有方法
['__add__', '__class__', '__contains__', ...]
```

4.2 REPL 常用快捷操作
---------------------

| 操作 | 含义 |
|------|------|
| `_` | 引用上一条表达式的返回值 |
| `dir(obj)` | 列出对象的所有属性和方法 |
| `help(obj)` | 显示对象的帮助文档 |
| `Ctrl+D` / `exit()` | 退出 REPL |
| `Ctrl+C` | 中断当前执行的代码 |
| `↑` / `↓` | 浏览历史命令 |

```python
>>> sum(range(1000000))
499999500000
>>> _ # _ 保存上一个结果
499999500000
>>> _ / 1000000
499999.5
```

4.3 REPL vs C 的"即时反馈"机制
------------------------------

C 语言的即时反馈需要：
```bash
echo '#include <stdio.h>
int main() {
 printf("%d\n", 2 + 2);
 return 0;
}' | gcc -x c -o /tmp/test - && /tmp/test
# 输出: 4
```

Python 的一行流：
```bash
python -c "print(2 + 2)"
# 输出: 4
```

> C 编译器的 `-x c` 选项允许从 stdin 读取源代码，但这仍然需要完整的文件格式（包括 `main` 函数）。Python REPL 的一行流与之相比是本质性的简化。

### 小节练习

> [!question] 判断题 1
> Python REPL 中的 `_` 变量保存的是整个 REPL 会话中所有结果的列表。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `_` 变量仅保存**上一条表达式**的返回值，不是所有结果的列表。每次新的表达式求值后，`_` 会被覆盖。

> [!question] 判断题 2
> C 语言提供了与 Python REPL 等价的交互式编程环境。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: C 是编译型语言，不存在标准的交互式解释器。虽然有工具可以做 `gcc` 即时编译（如 `tcc -run`），但这不是标准语言特性，也无法在 C 中动态执行任意表达式。

---

## 章节测试

### 一、判断题（正确选，错误选）

> [!question] 判断题 1
> Python 是完全的解释型语言，不包含任何编译过程。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: Python 在运行时会将源码编译为字节码（`.pyc`），再由 PVM 解释执行。它包含编译阶段，只是这个过程被自动化隐藏了。

> [!question] 判断题 2
> `python -c "x = 10"` 执行后，在同一个 shell 中可以用 `echo $x` 访问这个变量。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `python -c` 启动的是一个独立进程，进程内的变量在进程结束后就消失了。Shell 变量和 Python 变量是完全隔离的两套系统。

> [!question] 判断题 3
> Python 脚本的 `#!/usr/bin/env python3` 是 C 预处理器指令的一种。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `#!`（shebang）是**操作系统内核**的可执行文件加载机制，不是 Python 或 C 的语法。内核读取文件的第一行，如果是 `#!`，则调用指定的解释器来执行该文件。

> [!question] 判断题 4
> `python -m pdb script.py` 和 `python /usr/lib/python3.12/pdb.py script.py` 的行为完全一致。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `-m` 会自动处理模块的包上下文和 `__name__` 设置，而直接调用文件路径做不到这一点。对于包含相对导入的包内模块，直接调用会失败。

> [!question] 判断题 5
> Python 的 `.pyc` 字节码是跨平台的，可以在不同的操作系统上直接使用。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `.pyc` 字节码是平台无关的（platform-independent），理论上可以在不同操作系统的 Python 虚拟机之间共享。但注意 Python 大版本之间的字节码格式不兼容（3.11 的 .pyc 不能在 3.12 上用）。

> [!question] 判断题 6
> 如果脚本的第一行是 `#!/usr/bin/env python3`，执行 `./script.py` 不需要先 `chmod +x script.py`。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 即使有 shebang 行，文件也需要**执行权限**。Linux 内核检查文件的执行位（x 位），如果不设置 `chmod +x`，内核会返回 `Permission denied`，根本不会去读 #! 行。

---


---

## 力扣练习

以下题目用于验证本章所学内容：

| 题号 | 题目 | 链接 | 涉及知识点 |
|------|------|------|-----------|
| — | 本章无对应力扣题 | — | 请用动手练习题自检 |



### 动手练习题

> [!example] 练习题 1：用一行流完成日常任务
> **难度**: 简单
>
> 用 `python -c` 一行流完成以下任务，不允许使用任何其他工具（如 `ls`、`grep`、`cat` 等）：
> 1. 列出当前目录下所有 `.md` 文件
> 2. 计算 1 到 1000 的所有质数之和
> 3. 读取一个 JSON 文件并统计其中顶层键的数量
> 4. 将标准输入的所有行倒序输出（模拟 `tac`）
>
> 提示：使用 `import os`、`import glob`、`import json`、`import sys`。

> [!example] 练习题 2：编写带 Shebang 的命令行工具
> **难度**: 简单
>
> 编写一个名为 `wc.py` 的脚本，放在当前目录，实现以下功能：
> - Shebang 使用 `#!/usr/bin/env python3`
> - 接受命令行参数：`./wc.py filename.txt`
> - 输出文件的行数、单词数、字符数（模仿 `wc` 命令）
> - 如果文件不存在，打印错误信息并以非零状态码退出
> - 包含 `if __name__ == "__main__":` 守卫
>
> 完成后用 `chmod +x wc.py && ./wc.py wc.py` 验证。

> [!example] 练习题 3：比较编译-运行工作流
> **难度**: 简单
>
> 分别用 C 和 Python 完成同一个任务：读取一个文本文件，统计每个单词出现的频率，按频率降序输出 Top 10。
>
> 1. 用 C 实现：
> - 记录从编写代码到成功运行的总耗时
> - 统计编译和运行的分别耗时
> 2. 用 Python 一行流实现：
> - 用 `python -c "..."` 完成同样功能
> - 对比两种方式的代码行数和总耗时
>
> 写一份简短的对比总结，记录你的发现。

> [!example] 练习题 4：探索 `python -m` 内置模块
> **难度**: 简单
>
> 在不查阅任何文档的情况下，使用 `python -m` 模式探索以下 Python 内置模块的功能：
> - `calendar`：打印当前月份的日历
> - `http.server`：启动一个本地 HTTP 服务器
> - `zipfile`：列出某个 `.zip` 文件的内容
> - `gzip`：压缩和解压文件
>
> 对每个模块，记录你找到的用法（命令行参数组合），并用一行流总结。
