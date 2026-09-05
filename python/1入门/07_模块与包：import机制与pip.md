# 模块与包：import 机制与 pip (Modules & Packages)
---

## 章节概述

C 语言用 `#include` 引入头文件，用链接器解决符号引用。Python 用 `import` 引入模块，用 `pip` 管理第三方库。这两个世界看似相似（都是"引入外部代码"），但机制完全不同：`#include` 是**文本级别的复制粘贴**（预处理），`import` 是**运行时动态加载并执行**。本章教你理解 `import` 的内部机制、如何组织多文件项目为包（package）、如何用 `pip` 和 `venv` 隔离项目依赖。任何一个 C 程序员在写"超过一个 .py 文件"的项目时，都需要掌握这些知识。

> **核心理念**：C 的 `#include` 是"编译时的文本拼接"，Python 的 `import` 是"运行时的命名空间注入"。理解了 `sys.path` 和 `__name__`，你就理解了 Python 模块系统的 80%。

---

### 第一节：import —— 从 #include 到 import
---

1.1 `#include` vs `import`：本质区别
-------------------------------------

```c
// C: #include 是文本级别的复制粘贴
// math_utils.h
#ifndef MATH_UTILS_H
#define MATH_UTILS_H

int add(int a, int b);
int multiply(int a, int b);

#endif

// main.c
#include "math_utils.h" // 预处理：把 math_utils.h 的内容复制到这里
#include <stdio.h> // 预处理：复制系统头文件的内容

int main() {
 int result = add(3, 4); // add 的声明已通过 #include 可见
 printf("%d\n", result);
 return 0;
}
// 编译时：gcc -c math_utils.c → math_utils.o
// gcc -c main.c → main.o
// 链接时：gcc main.o math_utils.o → a.out ← 链接器解决符号引用
```

```python
# Python: import 是运行时加载并执行模块
# math_utils.py
def add(a, b):
 return a + b

def multiply(a, b):
 return a * b

# main.py
import math_utils # 运行时：执行 math_utils.py，创建模块命名空间
 # 所有定义的函数/类放在 math_utils 命名空间中
result = math_utils.add(3, 4) # 通过模块名访问
print(result)
```

关键区别：

| 维度 | C `#include` | Python `import` |
|------|-------------|-----------------|
| 发生时机 | 预处理阶段（编译前） | 运行时 |
| 机制 | 文本复制粘贴 | 执行模块代码，创建命名空间 |
| 作用域 | 全局（to the current translation unit） | 模块命名空间隔离 |
| 重复包含 | 需要 include guard | Python 自动缓存（只导入一次） |
| 循环引用 | 使用前向声明 | 部分导入可能导致 `AttributeError` |
| 二进制库 | 链接器处理 `.o`/`.so` | import 可加载 `.so`（C 扩展） |

1.2 import 的四种写法
---------------------

```bash
python -c "
import math # 导入整个模块

print('math.pi:', math.pi)
print('math.sqrt(16):', math.sqrt(16))
print('dir(math):', [m for m in dir(math) if not m.startswith('_')][:10])
"
```

```bash
python -c "
from math import pi, sqrt # 从模块导入特定名称
print('pi:', pi) # 直接使用，无需 math. 前缀
print('sqrt:', sqrt(25))

# 缺点：名称冲突风险
# from math import pi
# pi = 3.14 # 覆盖了数学意义上的 pi
"
```

```bash
python -c "
from math import * # 导入所有公开名称（不推荐）
print(sin(0)) # 直接可用，但污染命名空间

# * 导入的"公开"定义：模块的 __all__ 列表
# 无 __all__ 时导入所有不以下划线开头的名称
"
```

```bash
python -c "
import numpy as np # 用别名导入（社区习惯）
# arr = np.array([1, 2, 3]) # 需要 numpy 安装
print('np 别名: 约定俗成的命名空间缩写')
"
```

> **推荐原则**：`import module` 是所有写法的首选，`from module import specific_name` 用于明确需要的少量符号。避免 `from module import *`（除了在某些 REPL 探索场景）。

1.3 模块只加载一次
-------------------

```bash
python -c "
# 创建测试模块
import tempfile, os
tmpfile = os.path.join(tempfile.mkdtemp(), 'counter.py')
with open(tmpfile, 'w') as f:
 f.write('''
print(\"Module counter is being loaded!\")
counter = 0
def increment():
 global counter
 counter += 1
 return counter
''')

import sys
sys.path.insert(0, os.path.dirname(tmpfile))

import counter # 打印 \"Module counter is being loaded!\"
import counter # 什么都不打印！模块已被缓存
import counter # 依然不打印

# 查看被缓存的模块
print('counter in sys.modules:', 'counter' in sys.modules)
print('counter.counter:', counter.increment())

import importlib
importlib.reload(counter) # 强制重新加载
"
```

> Python 的模块缓存（`sys.modules` 字典）保证了每个模块只被加载一次。这相当于 C 语言中每个 `.o` 文件只被链接一次——但 Python 是在运行时内存中做这道查重。

---

### 第二节： `__name__ == "__main__"` 与模块的双重身份
---

2.1 模块可以作为脚本运行，也可以被导入
--------------------------------------

```bash
cat > /tmp/greeting.py << 'PYEOF'
"""一个同时支持直接运行和 import 的模块"""

GREETING = "Hello, World!"

def greet(name):
 return f"Hello, {name}!"

def _private_helper(): # _ 前缀约定：模块内部使用
 return "internal"

# 当直接运行此文件时执行，被 import 时不执行
if __name__ == "__main__":
 # 这里的代码只在作为脚本运行时生效
 import sys
 if len(sys.argv) > 1:
 print(greet(sys.argv[1]))
 else:
 print(GREETING)
 print(f"Module name is: {__name__}")
PYEOF

echo "=== 作为脚本运行 ==="
python /tmp/greeting.py Alice

echo ""
echo "=== 作为模块导入 ==="
python -c "import sys; sys.path.insert(0, '/tmp'); import greeting; print(greeting.greet('Bob')); print('Module name when imported:', greeting.__name__)"
```

对比 C 语言的对应模式：

```c
// C: 没有 __name__ 等价物
// 需要在编译时决定是库还是可执行文件
#ifdef STANDALONE
int main(int argc, char *argv[]) {
 printf("%s\n", greet("Alice"));
 return 0;
}
#endif
// 编译为库: gcc -c greeting.c -o greeting.o
// 编译为可执行: gcc -DSTANDALONE greeting.c -o greeting
```

`if __name__ == "__main__":` 是 Python 中最重要的设计模式之一——它让同一个文件既可以作为模块被导入（提供函数/类），也可以作为脚本直接运行（包含测试代码或命令行界面）。

2.2 实用的模块-脚本双模式示例
-----------------------------

```bash
cat > /tmp/wordcount.py << 'PYEOF'
"""Word count utility — usable as both module and script."""

def count_words(text):
 return len(text.split())

def count_lines(text):
 return len(text.splitlines())

def count_chars(text):
 return len(text)

def stats(text):
 return {
 'words': count_words(text),
 'lines': count_lines(text),
 'chars': count_chars(text)
 }

if __name__ == "__main__":
 import sys
 if len(sys.argv) != 2:
 print(f"Usage: python {sys.argv[0]} <filename>")
 sys.exit(1)

 with open(sys.argv[1]) as f:
 content = f.read()
 s = stats(content)
 print(f" Lines: {s['lines']}")
 print(f" Words: {s['words']}")
 print(f" Chars: {s['chars']}")
PYEOF

echo "=== 作为脚本 ==="
python /tmp/wordcount.py /tmp/wordcount.py

echo ""
echo "=== 作为模块 ==="
python -c "import sys; sys.path.insert(0, '/tmp'); import wordcount; print(wordcount.stats('hello world python'))"
```

---

### 第三节：包（Package）——多文件项目组织
---

3.1 `__init__.py` 与包的创建
-----------------------------

```bash
# 创建一个示例包结构
mkdir -p /tmp/mylib/utils

# __init__.py 让普通目录变成包
echo '"""mylib — A sample package."""
__version__ = "0.1.0"

# 控制 from mylib import * 的行为
__all__ = ["core_func", "CONFIG"]

# 在包级别导入常用的子模块符号
from .core import core_func, CONFIG
' > /tmp/mylib/__init__.py

echo '"""Core functionality."""
CONFIG = {"debug": False}

def core_func():
 return "core function called"
' > /tmp/mylib/core.py

echo '"""Utility functions."""
def helper():
 return "helper function called"
' > /tmp/mylib/utils/__init__.py
```

```bash
python -c "
import sys
sys.path.insert(0, '/tmp')

# 导入包
import mylib
print('Version:', mylib.__version__)
print('core_func:', mylib.core_func())

# 子模块可以单独导入
import mylib.core
from mylib.utils import helper
print('helper:', helper())
"
```

3.2 相对导入 vs 绝对导入
-------------------------

```bash
cat > /tmp/mylib/core.py << 'PYEOF'
"""Core functionality with relative imports."""
CONFIG = {"debug": False}

# 绝对导入（推荐新手使用）
# from mylib.utils import helper

# 相对导入（推荐包内部使用）
from .utils import helper

def core_func():
 return f"core + {helper()}"
PYEOF

python -c "
import sys; sys.path.insert(0, '/tmp')
import mylib.core
print(mylib.core.core_func())
" 2>&1
```

> 包内部建议使用**相对导入**（`from . import xxx`），因为它不依赖包的具体安装路径，移动包时不需要修改导入语句。顶层脚本建议使用**绝对导入**。

3.3 `sys.path` —— Python 的模块搜索路径
----------------------------------------

```bash
python -c "
import sys
print('Python version:', sys.version.split()[0])
print()
print('=== sys.path (模块搜索路径) ===')
for i, p in enumerate(sys.path):
 print(f'{i}: {p}')
print()
print('相当于 C 语言中的:')
print(' 1. -I 选项（头文件搜索路径）')
print(' 2. -L 选项（库文件搜索路径）')
print(' 3. LD_LIBRARY_PATH（动态库搜索路径）')
print()
print('sys.path 的来源:')
print(' 1. 当前脚本所在目录')
print(' 2. PYTHONPATH 环境变量')
print(' 3. 标准库目录')
print(' 4. site-packages（pip 安装的第三方包）')
"
```

```bash
python -c "
import sys

# 运行时动态修改搜索路径
sys.path.insert(0, '/my/custom/modules') # 在头部插入
sys.path.append('/another/path') # 在尾部追加

# 检查模块位置
import os
print('os module location:', os.__file__)
import json
print('json module location:', json.__file__)
"
```

> `sys.path` 是 Python 中"查找模块"的路线图。修改 `sys.path` 相当于 C 语言中的 `-I`（头文件路径）和 `-L`/`LD_LIBRARY_PATH`（库路径）的运行时综合。

---

### 第四节：pip 与 venv —— 第三方库管理
---

4.1 pip —— Python 的包管理器
------------------------------

```bash
# 查看 pip 版本
python -m pip --version

# 安装包
python -m pip install requests

# 列出已安装的包
python -m pip list

# 查看包的详细信息
python -m pip show requests

# 卸载包
python -m pip uninstall requests -y

# 从 requirements.txt 安装依赖
echo 'requests>=2.28.0
click>=8.0' > /tmp/requirements.txt
python -m pip install -r /tmp/requirements.txt 2>&1 | tail -5
```

> 对比 C 语言的包管理：C 没有统一的包管理器。`apt install libxxx-dev`（系统级）、`vcpkg`/`conan`（C++）、手写 Makefile 这三种方式分别解决不同层面的问题。Python 的 `pip` 将所有依赖管理统一到一个工具中。

4.2 venv —— 虚拟环境隔离
-------------------------

```bash
# 创建虚拟环境
python -m venv /tmp/myenv

# 激活虚拟环境
source /tmp/myenv/bin/activate

> **跨平台提示**：
> - **Windows**：CMD 用 `myenv\Scripts\activate`，PowerShell 用 `myenv\Scripts\Activate.ps1`（若执行策略受限，先运行 `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`）
> - **macOS**：与 Linux 一致，`source venv/bin/activate`

# 虚拟环境中安装包（不影响系统 Python）
pip install requests 2>&1 | tail -3

# 导出依赖
pip freeze > /tmp/requirements_frozen.txt

# 退出虚拟环境
deactivate
```

```bash
python -c "
import sys
print('Python executable:', sys.executable)
print('site-packages:', [p for p in sys.path if 'site-packages' in p])
"
```

> `venv` 创建的是一个**隔离的 Python 环境**——它复制（或链接）Python 解释器到虚拟环境目录，并创建独立的 `site-packages` 目录。这相当于 C 语言为每个项目设置独立的 `LD_LIBRARY_PATH` 和 `LIBRARY_PATH`。

4.3 pip 常用一行流
------------------

```bash
# 安装最常用的第三方库
python -m pip install requests # HTTP 请求（比 libcurl 好用 10 倍）
python -m pip install click # 命令行工具（比 getopt 直观）
python -m pip install pytest # 测试框架（比 CUnit 强大）
python -m pip install rich # 终端美化输出
python -m pip install watchdog # 文件系统监控（比 inotify 高层）

> **跨平台提示**：
> - **Windows**：`watchdog` 底层使用 `ReadDirectoryChangesW` API，功能等价
> - **macOS**：`watchdog` 底层使用 FSEvents API，`inotify` 为 Linux 特有
python -m pip install psutil # 系统信息（比 /proc 读取方便）

# 搜索包
python -m pip search "json schema" 2>&1 || echo "(pip search 在较新版本中已禁用——请用 pip index 或浏览器)"

# 查看过期的包
python -m pip list --outdated
```

---

### 第五节：常用标准库速览
---

5.1 "胶水语言"的瑞士军刀
-------------------------

```bash
python -c "
# os: 操作系统接口（相当于 C 的 <unistd.h> + <sys/stat.h> + 部分 shell 命令）
import os
print('cwd:', os.getcwd())
print('env HOME:', os.environ.get('HOME'))

# sys: 解释器相关（argv, path, stdin/stdout/stderr）
import sys
print('args:', sys.argv[:3])
print('platform:', sys.platform)
print('byteorder:', sys.byteorder)
"
```

```bash
python -c "
# subprocess: 运行外部命令（替代 C 的 system() + popen()）
import subprocess
result = subprocess.run(['echo', 'hello from subprocess'],
 capture_output=True, text=True)
print('stdout:', result.stdout.strip())
print('returncode:', result.returncode)
"
```

5.2 常用标准库清单
------------------

| 模块 | 用途 | C 语言等价 |
|------|------|-----------|
| `os` / `os.path` | 操作系统接口，文件路径 | `<unistd.h>` + `<sys/stat.h>` |
| `sys` | 解释器交互 | `argv`, `environ` |
| `subprocess` | 运行外部命令 | `system()` / `popen()` |
| `re` | 正则表达式 | `<regex.h>` (POSIX) |
| `json` | JSON 序列化 | cJSON / jansson (第三方) |
| `csv` | CSV 读写 | 手工解析 |
| `argparse` | 命令行参数解析 | `getopt_long()` |
| `logging` | 日志系统 | `syslog()` / 手工实现 |
| `datetime` | 日期时间 | `<time.h>` + 日历计算 |
| `collections` | 高级容器（deque, Counter, OrderedDict...） | 手工实现 |
| `itertools` | 迭代器工具 | 手工循环 |
| `functools` | 高阶函数工具 | 函数指针 |
| `hashlib` | 哈希函数 | OpenSSL / `<openssl/sha.h>` |
| `sqlite3` | SQLite 数据库 | `libsqlite3` + SQL API |

```bash
python -c "
import collections, itertools, functools

# Counter: 一键统计词频
words = 'the quick brown fox jumps over the lazy dog'.split()
print('Word count:', collections.Counter(words))

# itertools.chain: 平铺多层嵌套
nested = [[1, 2], [3, 4], [5]]
print('Flattened:', list(itertools.chain.from_iterable(nested)))

# functools.reduce: 累积操作
result = functools.reduce(lambda x, y: x * y, range(1, 6))
print('5! =', result)
"
```

---

## 力扣练习

以下题目用于验证本章所学内容：

| 题号 | 题目 | 链接 | 涉及知识点 |
|------|------|------|-----------|
| — | 本章无对应力扣题 | — | 请用动手练习题自检 |
