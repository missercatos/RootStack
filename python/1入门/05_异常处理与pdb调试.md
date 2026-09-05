# 异常处理与 pdb 调试 (Exceptions & Debugging)
---

## 章节概述

C 语言程序员习惯用 `errno`、返回值检查 `NULL` 或 `-1` 来排错。Python 走的是完全不同的路：错误通过**异常**（exception）向上冒泡，直到某个 `try/except` 块被捕获。本章对比这两种错误处理哲学，教你用 `try/except/finally/else` 写健壮的代码，用 `pdb`（Python Debugger）做交互式调试——并把它与 GDB 的操作方式做对比。对于 C 程序员来说，pdb 就是"只差没有 core dump"的 GDB 替代品。

> **核心理念**：C 的错误处理是"检查返回值，传播 `errno`"，Python 的错误处理是"抛出去，让调用者决定怎么处理"。异常不是故障——它们是控制流的一部分。pdb 则让你在异常爆发时，像 GDB 的 `backtrace` 一样看到完整的调用栈全景。

---

### 第一节：从 errno 到 try/except
---

1.1 C 风格的错误处理 vs Python 的异常
--------------------------------------

```c
// C: 每次函数调用都要检查返回值
#include <stdio.h>
#include <errno.h>
#include <string.h>

int read_config(const char *path, char *buf, size_t size) {
 FILE *f = fopen(path, "r");
 if (!f) {
 fprintf(stderr, "Cannot open %s: %s\n", path, strerror(errno));
 return -1;
 }
 if (fread(buf, 1, size, f) < size) {
 if (ferror(f)) {
 fprintf(stderr, "Read error: %s\n", strerror(errno));
 fclose(f);
 return -2;
 }
 }
 fclose(f);
 return 0;
}
// 主调方需要：int ret = read_config(...); if (ret < 0) { /* 处理 */ }
```

```python
# Python: 异常自动向上冒泡，只需在合适的层级捕获
def read_config(path):
 with open(path) as f: # 文件不存在？FileNotFoundError 自动上抛
 return f.read() # 读取失败？IOError 自动上抛

# 调用方决定何时处理
try:
 content = read_config('/etc/myapp.conf')
except FileNotFoundError:
 print('Config file not found, using defaults')
 content = 'defaults'
except IOError as e:
 print(f'Read error: {e}')
 raise SystemExit(1)
```

1.2 完整的异常处理结构
-----------------------

```bash
python -c "
def divide(a, b):
 return a / b

# 四种异常处理结构
numbers = [(10, 2), (10, 0), (10, 'x')]

for a, b in numbers:
 try:
 result = divide(a, b)
 except ZeroDivisionError:
 print(f'{a}/{b}: division by zero')
 except (TypeError, ValueError) as e:
 print(f'{a}/{b}: type error - {e}')
 else:
 print(f'{a}/{b} = {result}') # 无异常时执行
 finally:
 print(' (attempt done)')
"
```

`try/except/else/finally` 的执行顺序：

| 是否有异常 | `try` | `except` | `else` | `finally` |
|-----------|-------|----------|--------|-----------|
| 无异常 | 执行完 | 跳过 | **执行** | 总是执行 |
| 有匹配异常 | 跳到 except | 执行 | 跳过 | 总是执行 |
| 有未匹配异常 | 跳到 finally | 跳过 | 跳过 | 执行后异常继续上抛 |

1.3 常见内置异常类
-------------------

```mermaid
graph TB
 BE["BaseException"]
 BE --> SK["SystemExit / KeyboardInterrupt"]
 BE --> EX["Exception"]
 EX --> AE["ArithmeticError → ZeroDivisionError"]
 EX --> LE["LookupError → IndexError, KeyError"]
 EX --> TE["TypeError"]
 EX --> VE["ValueError"]
 EX --> OE["OSError → FileNotFoundError, PermissionError"]
 EX --> NE["NameError"]
 EX --> ATE["AttributeError"]
```

```bash
python -c '
# 对照 C 语言的常见错误
exceptions = {
 "ZeroDivisionError": "除以 0 ← C 中通过检查除数是否为 0 避免",
 "IndexError": "列表索引越界 ← C 中是未定义行为或段错误",
 "KeyError": "字典键不存在 ← C 哈希表中返回 NULL",
 "TypeError": "类型不匹配 ← C 中编译时捕捉（或隐式转换）",
 "ValueError": "值不合理（如 int(\\\"abc\\\")）← C 中 atoi 返回 0",
 "FileNotFoundError": "文件不存在 ← C 中 fopen 返回 NULL",
 "AttributeError": "属性不存在 ← C 中编译时捕捉（struct 字段）",
 "NameError": "变量名未定义 ← C 中编译时捕捉",
}
for ex, desc in exceptions.items():
 print(f"{ex}: {desc}")
'
```

> 注意 `IndexError` 和 `KeyError` 都是 `LookupError` 的子类。如果你要同时捕获索引错误和键错误，可以写 `except LookupError`。

---

### 第二节：raise 与自定义异常
---

2.1 `raise` 抛出异常
--------------------

```bash
python -c "
def validate_age(age):
 if not isinstance(age, int):
 raise TypeError(f'Age must be int, got {type(age).__name__}')
 if age < 0:
 raise ValueError(f'Age cannot be negative: {age}')
 if age > 150:
 raise ValueError(f'Age too large: {age}')
 return age

# 测试验证
for v in [25, -5, 200, 'thirty']:
 try:
 print(f'Valid: {validate_age(v)}')
 except (TypeError, ValueError) as e:
 print(f'Invalid: {e}')
"
```

2.2 异常链（Exception Chaining）
--------------------------------

```bash
python -c "
import json

def load_config(path):
 try:
 with open(path) as f:
 return json.load(f)
 except FileNotFoundError as e:
 raise RuntimeError(f'Config not found: {path}') from e
 except json.JSONDecodeError as e:
 raise ValueError(f'Invalid JSON in {path}: {e}') from e

# 测试
for path in ['/nonexistent.json', '/tmp/malformed.json']:
 try:
 load_config(path)
 except (RuntimeError, ValueError) as e:
 print(f'{type(e).__name__}: {e}')
 print(f' Caused by: {e.__cause__}')
 print()
" 2>/dev/null
```

> **跨平台提示**：
> - **Windows**：CMD 使用 `2>NUL`，PowerShell 使用 `2>$null`
> - **macOS**：与 Linux 一致，`2>/dev/null`
```

> `raise ... from e` 建立异常链，保留了原始异常作为 `__cause__`。这类似于 C 语言中逐层打印 `errno` 和 `strerror` 的调试日志，但 Python 的异常链是**结构化的**——可以被程序逻辑使用，而不只是日志文本。

2.3 自定义异常类
----------------

```bash
python -c "
class NetworkError(ConnectionError):
 '''网络相关错误'''
 def __init__(self, host, port, message):
 self.host = host
 self.port = port
 super().__init__(f'{host}:{port} - {message}')

class TimeoutError(NetworkError):
 '''网络超时'''
 pass

# 使用自定义异常
try:
 raise TimeoutError('db.example.com', 5432, 'connection timed out')
except NetworkError as e:
 print(f'Network {type(e).__name__}: {e}')
 print(f' host={e.host}, port={e.port}')
"
```

---

### 第三节：traceback —— 读懂错误信息
---

3.1 阅读 traceback
-------------------

```bash
python -c "
def func_c():
 1 / 0 # ZeroDivisionError

def func_b():
 func_c()

def func_a():
 func_b()

func_a()
" 2>&1 || true
```

输出解读：

```
Traceback (most recent call last): ← 从顶层调用方开始
 File "<string>", line 10, in <module> ← 第 10 行调用了 func_a()
 File "<string>", line 8, in func_a ← func_a() 中调用了 func_b()
 File "<string>", line 5, in func_b ← func_b() 中调用了 func_c()
 File "<string>", line 2, in func_c ← func_c() 中 1/0 触发
ZeroDivisionError: division by zero ← 最终异常类型和消息
```

**从下往上读**——最底部是"事故现场"，顶部是"始作俑者"的调用链。

3.2 以编程方式获取 traceback
-----------------------------

```bash
python -c "
import traceback
import sys

def risky_function():
 return [1, 2, 3][100]

try:
 risky_function()
except IndexError:
 # 获取完整的 traceback 字符串
 tb_str = traceback.format_exc()
 print('=== Formatted traceback ===')
 print(tb_str)
 print('============================')

 # 获取 traceback 对象（用于程序分析）
 exc_type, exc_value, exc_tb = sys.exc_info()
 print(f'Exception type: {exc_type.__name__}')
 frames = traceback.extract_tb(exc_tb)
 for frame in frames:
 print(f' File \"{frame.filename}\", line {frame.lineno}, in {frame.name}')
 if frame.line:
 print(f' {frame.line.strip()}')
"
```

---

### 第四节：pdb —— Python 的 GDB
---

4.1 启动 pdb 的三种方式
------------------------

```bash
# 方式一：命令行直接启动 pdb
python -m pdb my_script.py

# 方式二：在代码中插入断点
# 在 Python 3.7+ 中使用 breakpoint()
echo 'x = 42
breakpoint() # ← 执行到此处自动进入 pdb
print(x)' > /tmp/debug_me.py

python /tmp/debug_me.py

# 方式三：异常发生后进入 pdb
python -m pdb -c continue /tmp/debug_me.py 2>&1 | head
```

4.2 pdb 核心命令与 GDB 对照表
-----------------------------

| 操作 | pdb | GDB 等价 | 说明 |
|------|-----|----------|------|
| 设置断点（函数） | `b func_name` 或 `break func_name` | `break func_name` | 在函数入口设断点 |
| 设置断点（行号） | `b 42` | `break 42` | 在当前文件第 42 行 |
| 设置断点（文件:行） | `b script.py:42` | `break script.c:42` | 指定文件 |
| 列出断点 | `b` 或 `break` | `info breakpoints` | |
| 删除断点 | `clear` 或 `disable N` | `delete N` | |
| 继续执行 | `c` 或 `continue` | `continue` | 运行到下一断点 |
| 单步执行（不进函数） | `n` 或 `next` | `next` | |
| 单步执行（进函数） | `s` 或 `step` | `step` | |
| 返回当前函数 | `r` 或 `return` | `finish` | |
| 打印变量 | `p expr` 或 `pp expr` | `print expr` | `pp` 是美化打印 |
| 查看调用栈 | `w` 或 `where` 或 `bt` | `backtrace` | |
| 移动栈帧 | `u`（上）/ `d`（下） | `frame N` `up` `down` | pdb 方向与 GDB 相反 |
| 查看源码 | `l` 或 `ll` 或 `list` | `list` | |
| 查看参数 | `a` 或 `args` | `info args` | |
| 执行任意 Python | `!expr` | — | 如 `!len(variable)` |
| 查看类型 | `whatis variable`（pdb） | `ptype variable`（GDB） | |
| 退出 | `q` 或 `quit` | `quit` | |
| 帮助 | `h` 或 `help` | `help` | |

```bash
python -c "
# pdb 调试示例
def fibonacci(n):
 a, b = 0, 1
 for _ in range(n):
 a, b = b, a + b
 return a

# breakpoint() # 取消注释即可调试
print(f'fib(10) = {fibonacci(10)}')
"
```

4.3 调试实战
-------------

```bash
cat > /tmp/buggy.py << 'PYEOF'
def process(lst):
 result = []
 for item in lst:
 result.append(item / len(lst)) # BUG: 如果 lst 为空？
 return result

def main():
 data = [100, 200, 300]
 processed = process(data)
 print('OK:', processed)

 # 故意触发空列表
 bad = process([])
 print('Bad:', bad)

main()
PYEOF

python /tmp/buggy.py 2>&1 | head -20

# pdb 调试流程：
# python -m pdb /tmp/buggy.py
# (pdb) b process ← 在 process 函数设断点
# (pdb) c ← 继续执行
# > process(...) ← 第一次进入 process
# (pdb) n ← 逐步执行
# (pdb) p lst ← 打印参数
# (pdb) c ← 继续到第二次调用（空列表）
# (pdb) p len(lst) ← 查看列表长度
# (pdb) q ← 退出
```

4.4 `pdb.post_mortem` —— 异常后事分析
---------------------------------------

```bash
python -c "
import pdb
import sys

def crash():
 return [][0] # IndexError

try:
 crash()
except Exception:
 # 异常发生后进入 pdb
 pdb.post_mortem(sys.exc_info()[2])
" 2>&1 <<< 'q'
```

> `pdb.post_mortem()` 就像是给 Python 程序做的"尸检"——程序已经崩溃了，但你仍然可以检查崩溃瞬间的所有变量状态。这类似于用 GDB 加载 core dump 文件。

---

## 力扣练习

以下题目用于验证本章所学内容：

| 题号 | 题目 | 链接 | 涉及知识点 |
|------|------|------|-----------|
| 278 | 第一个错误的版本 | https://leetcode.cn/problems/first-bad-version/ | 二分查找、错误检测模式 |
| 374 | 猜数字大小 | https://leetcode.cn/problems/guess-number-higher-or-lower/ | 二分查找、边界处理 |
