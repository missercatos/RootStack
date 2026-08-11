# 模块与包：import 机制与 pip (Modules & Packages)
---

## 📖 章节概述

C 语言用 `#include` 引入头文件，用链接器解决符号引用。Python 用 `import` 引入模块，用 `pip` 管理第三方库。这两个世界看似相似（都是"引入外部代码"），但机制完全不同：`#include` 是**文本级别的复制粘贴**（预处理），`import` 是**运行时动态加载并执行**。本章教你理解 `import` 的内部机制、如何组织多文件项目为包（package）、如何用 `pip` 和 `venv` 隔离项目依赖。任何一个 C 程序员在写"超过一个 .py 文件"的项目时，都需要掌握这些知识。

> **核心理念**：C 的 `#include` 是"编译时的文本拼接"，Python 的 `import` 是"运行时的命名空间注入"。理解了 `sys.path` 和 `__name__`，你就理解了 Python 模块系统的 80%。

---

### 📚 第一节：import —— 从 #include 到 import
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
#include "math_utils.h"   // 预处理：把 math_utils.h 的内容复制到这里
#include <stdio.h>         // 预处理：复制系统头文件的内容

int main() {
    int result = add(3, 4);   // add 的声明已通过 #include 可见
    printf("%d\n", result);
    return 0;
}
// 编译时：gcc -c math_utils.c → math_utils.o
//         gcc -c main.c → main.o
// 链接时：gcc main.o math_utils.o → a.out   ← 链接器解决符号引用
```

```python
# Python: import 是运行时加载并执行模块
# math_utils.py
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

# main.py
import math_utils              # 运行时：执行 math_utils.py，创建模块命名空间
                               # 所有定义的函数/类放在 math_utils 命名空间中
result = math_utils.add(3, 4)  # 通过模块名访问
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
import math                     # 导入整个模块

print('math.pi:', math.pi)
print('math.sqrt(16):', math.sqrt(16))
print('dir(math):', [m for m in dir(math) if not m.startswith('_')][:10])
"
```

```bash
python -c "
from math import pi, sqrt       # 从模块导入特定名称
print('pi:', pi)                # 直接使用，无需 math. 前缀
print('sqrt:', sqrt(25))

# ⚠️ 缺点：名称冲突风险
# from math import pi
# pi = 3.14                     # 覆盖了数学意义上的 pi
"
```

```bash
python -c "
from math import *              # 导入所有公开名称（不推荐）
print(sin(0))                   # 直接可用，但污染命名空间

# * 导入的"公开"定义：模块的 __all__ 列表
# 无 __all__ 时导入所有不以下划线开头的名称
"
```

```bash
python -c "
import numpy as np              # 用别名导入（社区习惯）
# arr = np.array([1, 2, 3])     # 需要 numpy 安装
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

import counter                  # 打印 \"Module counter is being loaded!\"
import counter                  # 什么都不打印！模块已被缓存
import counter                  # 依然不打印

# 查看被缓存的模块
print('counter in sys.modules:', 'counter' in sys.modules)
print('counter.counter:', counter.increment())

import importlib
importlib.reload(counter)       # 强制重新加载
"
```

> Python 的模块缓存（`sys.modules` 字典）保证了每个模块只被加载一次。这相当于 C 语言中每个 `.o` 文件只被链接一次——但 Python 是在运行时内存中做这道查重。

### 📝 小节练习

> [!question] 选择题 1
> C 语言的 `#include "header.h"` 和 Python 的 `import module` 最根本的区别是？
> - [ ] A. C 是运行时加载，Python 是编译时加载
> - [ ] B. C 是文本复制粘贴（预处理），Python 是运行时执行并创建命名空间
> - [ ] C. 两者机制完全相同
> - [ ] D. Python 的 import 不支持自定义模块
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `#include` 发生在预处理阶段——预处理器将头文件内容逐字复制到当前文件中。`import` 发生在运行时——Python 解释器查找模块文件或共享库，执行其中的代码，将结果放入独立的命名空间对象中。

> [!question] 判断题 1
> Python 中同一个模块被 `import` 多次，每次都会重新执行模块代码。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: Python 在 `sys.modules` 字典中缓存已加载的模块。后续的 `import` 直接从缓存返回模块对象，不会重新执行模块代码。需要使用 `importlib.reload()` 强制重新加载。

---

### 📚 第二节： `__name__ == "__main__"` 与模块的双重身份
---

2.1 模块可以作为脚本运行，也可以被导入
--------------------------------------

```bash
cat > /tmp/greeting.py << 'PYEOF'
"""一个同时支持直接运行和 import 的模块"""

GREETING = "Hello, World!"

def greet(name):
    return f"Hello, {name}!"

def _private_helper():      # _ 前缀约定：模块内部使用
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
// 编译为库:   gcc -c greeting.c -o greeting.o
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
    print(f"  Lines: {s['lines']}")
    print(f"  Words: {s['words']}")
    print(f"  Chars: {s['chars']}")
PYEOF

echo "=== 作为脚本 ==="
python /tmp/wordcount.py /tmp/wordcount.py

echo ""
echo "=== 作为模块 ==="
python -c "import sys; sys.path.insert(0, '/tmp'); import wordcount; print(wordcount.stats('hello world python'))"
```

### 📝 小节练习

> [!question] 选择题 1
> Python 文件中的 `if __name__ == "__main__":` 代码块何时执行？
> - [ ] A. 每次 `import` 时都执行
> - [ ] B. 仅在文件被直接运行时执行
> - [ ] C. 仅在文件被 `from ... import ...` 时执行
> - [ ] D. 永不执行
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `__name__` 在文件被直接运行时设为 `"__main__"`，在被导入时设为模块名（文件名不含 `.py`）。因此 `if __name__ == "__main__":` 的代码块只在该文件是**入口脚本**时运行。这是 Python 中给模块添加"可执行测试"或"命令行界面"的标准方式。

> [!question] 判断题 1
> C 语言可以用 `#ifdef __MAIN__` 宏实现与 Python 的 `if __name__ == "__main__"` 完全等价的功能。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: C 语言没有与 `__name__ == "__main__"` 完全等价的机制。虽然可以在编译时通过 `-DMAIN` 定义宏来条件编译 `main` 函数，但这是**编译时**决定而非**运行时**决定，且不支持"同一个 .o 既可链接到库也可作为可执行文件入口"的场景。

---

### 📚 第三节：包（Package）——多文件项目组织
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
print('  1. -I 选项（头文件搜索路径）')
print('  2. -L 选项（库文件搜索路径）')
print('  3. LD_LIBRARY_PATH（动态库搜索路径）')
print()
print('sys.path 的来源:')
print('  1. 当前脚本所在目录')
print('  2. PYTHONPATH 环境变量')
print('  3. 标准库目录')
print('  4. site-packages（pip 安装的第三方包）')
"
```

```bash
python -c "
import sys

# 运行时动态修改搜索路径
sys.path.insert(0, '/my/custom/modules')   # 在头部插入
sys.path.append('/another/path')            # 在尾部追加

# 检查模块位置
import os
print('os module location:', os.__file__)
import json
print('json module location:', json.__file__)
"
```

> `sys.path` 是 Python 中"查找模块"的路线图。修改 `sys.path` 相当于 C 语言中的 `-I`（头文件路径）和 `-L`/`LD_LIBRARY_PATH`（库路径）的运行时综合。

### 📝 小节练习

> [!question] 选择题 1
> 一个目录成为 Python 包的标志是什么？
> - [ ] A. 存在 `setup.py` 文件
> - [ ] B. 存在 `__init__.py` 文件
> - [ ] C. 目录名字以下划线开头
> - [ ] D. 存在 `package.json` 文件
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `__init__.py` 文件标识一个目录为 Python 包。在 Python 3.3+ 中，也支持**命名空间包**（namespace package）——不需要 `__init__.py` 文件。但普通包明确创建 `__init__.py` 仍是推荐的好做法。

> [!question] 选择题 2
> `from . import module`（以点号开头）属于什么类型的导入？
> - [ ] A. 绝对导入
> - [ ] B. 相对导入
> - [ ] C. 嵌套导入
> - [ ] D. 延迟导入
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `.` 表示当前包，`..` 表示父包——这是 Python 的相对导入语法。相对导入只能在包内部使用（不能用于顶层脚本），它使模块之间的引用不依赖于包的安装路径。

---

### 📚 第四节：pip 与 venv —— 第三方库管理
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
python -m pip install requests        # HTTP 请求（比 libcurl 好用 10 倍）
python -m pip install click           # 命令行工具（比 getopt 直观）
python -m pip install pytest          # 测试框架（比 CUnit 强大）
python -m pip install rich            # 终端美化输出
python -m pip install watchdog        # 文件系统监控（比 inotify 高层）
python -m pip install psutil          # 系统信息（比 /proc 读取方便）

# 搜索包
python -m pip search "json schema" 2>&1 || echo "(pip search 在较新版本中已禁用——请用 pip index 或浏览器)"

# 查看过期的包
python -m pip list --outdated
```

### 📝 小节练习

> [!question] 选择题 1
> `python -m pip install` 中的 `-m` 标志的作用是？
> - [ ] A. 以最大化模式安装
> - [ ] B. 将 `pip` 作为模块运行（不需要知道 pip 的可执行文件路径）
> - [ ] C. 启用多线程安装
> - [ ] D. 以最小化模式安装
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `python -m pip` 确保使用的是当前 Python 解释器对应的 pip 版本。不需要知道 pip 脚本的具体位置（可能在 `/usr/bin/pip`、`~/.local/bin/pip`、`venv/bin/pip` 等）。

> [!question] 判断题 1
> venv 虚拟环境会复制整个 Python 解释器到虚拟环境目录中。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `venv` 不会复制完整的 Python 解释器——它创建指向系统 Python 的符号链接（或轻量级副本），只复制 `site-packages` 等目录。不同的虚拟环境共享同一个解释器二进制文件，但各自有独立的库安装目录。

---

### 📚 第五节：常用标准库速览
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

### 📝 小节练习

> [!question] 选择题 1
> Python 中 `subprocess.run()` 的 `capture_output=True` 参数作用相当于 C 语言中的什么？
> - [ ] A. `system()` 的标准行为
> - [ ] B. `popen()` + 管道读取
> - [ ] C. `fork()` + `exec()`
> - [ ] D. `popen()` 不带管道
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `capture_output=True` 将子进程的标准输出和标准错误捕获到 Python 字符串中，等价于 C 语言中使用 `popen()` 创建管道，然后从管道中读取数据。`system()` 不捕获输出。

> [!question] 判断题 1
> Python 的 `os` 模块提供了与 C 标准库 `<unistd.h>` 完全一致的系统调用接口。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: Python 的 `os` 模块提供了**高级的、跨平台的抽象**，不是底层系统调用的一对一映射。例如 `os.listdir()` 内部在所有平台上调用不同的系统 API（Linux 是 `getdents`，Windows 是 `FindFirstFile`）。要直接访问 POSIX 系统调用，需要使用 `os` 模块的底层函数（如 `os.read()`）或 `ctypes` 库。

---

## 📋 章节测试

### 一、判断题（正确选✅，错误选❌）

> [!question] 判断题 1
> C 语言的 `#include` 不仅包含函数声明，还执行被包含文件中的代码。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `#include` 只在预处理阶段做文本替换——将头文件内容**复制粘贴**到源文件中。头文件中如果有函数定义（不是声明）会导致链接时重复定义错误。Python 的 `import` 则真正**执行**被导入模块的代码。

> [!question] 判断题 2
> Python 中 `import sys; sys.path.insert(0, '.')` 可以动态修改模块搜索路径。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `sys.path` 是一个普通的 Python 列表，可以在运行时修改（追加、插入、删除路径）。修改后的路径立即影响后续的 `import` 语句。这比 C 语言编译时的 `-I` 选项灵活得多。

> [!question] 判断题 3
> `pip install` 安装的第三方包会自动对所有 Python 虚拟环境生效。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 每个虚拟环境有独立的 `site-packages` 目录。pip 安装的包只对**当前激活的虚拟环境**有效。这也是虚拟环境的核心价值——不同项目可以依赖不同版本的同一包，互不冲突。

> [!question] 判断题 4
> Python 的模块缓存（`sys.modules`）在程序退出时自动清空。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `sys.modules` 是一个普通的字典，存于进程内存中。当 Python 进程退出时，操作系统回收所有进程内存，包括 `sys.modules`。下次启动时，所有模块需要重新加载。

> [!question] 判断题 5
> 如果没有 `__init__.py` 文件，一个包含 Python 文件的目录仍然可以被 Python 3.3+ 当作命名空间包导入。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: Python 3.3 引入了**隐式命名空间包**（PEP 420）——不需要 `__init__.py` 的目录也可以成为一个包。但普通包（regular package）创建 `__init__.py` 仍是推荐的明确做法。

> [!question] 判断题 6
> `from module import *` 会导入模块中所有变量和函数（包括以 `_` 开头的私有名称）。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 如果模块定义了 `__all__` 列表，`from module import *` 只导入该列表中的名称。如果未定义 `__all__`，则导入所有**不以下划线开头**的名称。这是 Python 的约定式封装。

> [!question] 判断题 7
> `python -m venv myenv` 创建的虚拟环境会被源代码管理系统（如 git）自动忽略。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: git 不会"自动"忽略虚拟环境目录——除非项目中存在 `.gitignore` 文件明确排除它。标准操作是在项目根目录的 `.gitignore` 中添加 `venv/` 或 `myenv/` 等虚拟环境目录名。

---

### 二、选择题（单项选择题）

> [!question] 选择题 1
> 以下哪个不是 `import` 的合法写法？
> - [ ] A. `import math`
> - [ ] B. `from math import pi`
> - [ ] C. `import math.pi`
> - [ ] D. `import math as m`
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: `import math.pi` 不是合法语法——`import` 后面必须跟模块名，不能用点号导入子模块或属性。正确写法是 `from math import pi` 或 `import math; math.pi`。

> [!question] 选择题 2
> `sys.path` 主要包含哪些路径来源？
> - [ ] A. 仅当前目录
> - [ ] B. 当前目录、PYTHONPATH 环境变量、标准库、site-packages
> - [ ] C. 仅标准库和 site-packages
> - [ ] D. 仅 PYTHONPATH 环境变量
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `sys.path` 的初始化顺序是：脚本所在目录 → `PYTHONPATH` 环境变量 → 标准库路径 → `site-packages`（pip 安装目录）。运行时可以修改这个列表。

> [!question] 选择题 3
> 如何查看一个已导入模块的文件路径？
> - [ ] A. `module.path`
> - [ ] B. `module.__file__`
> - [ ] C. `module.__location__`
> - [ ] D. `module.__dir__`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 模块的 `__file__` 属性包含模块源代码文件的绝对路径（对于内置模块如 `sys`，这个属性不存在）。`os.__file__` → `'/usr/lib/python3.12/os.py'`。

> [!question] 选择题 4
> `__init__.py` 文件的主要作用是什么？
> - [ ] A. 初始化 Python 解释器
> - [ ] B. 标识目录为 Python 包，控制包的初始化
> - [ ] C. 定义程序的入口点
> - [ ] D. 配置代码格式化规则
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `__init__.py` 告诉 Python 解释器该目录是一个包。它还可以包含包的初始化代码（如导入子模块、设置 `__all__` 列表、定义包级变量等）。

> [!question] 选择题 5
> `pip freeze > requirements.txt` 的作用是？
> - [ ] A. 锁定 pip 版本
> - [ ] B. 冻结当前安装的所有包为不可升级状态
> - [ ] C. 将当前环境中安装的包及版本号写入文件
> - [ ] D. 卸载所有第三方包
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: `pip freeze` 输出当前 Python 环境中所有已安装的包及其精确版本号（格式：`package==1.2.3`）。将输出重定向到 `requirements.txt` 后，可以通过 `pip install -r requirements.txt` 在其他环境精确复现相同的包集合。

> [!question] 选择题 6
> 在 Python 中 `import os; print(os.getcwd())` 获取当前工作目录。C 语言中哪个函数等价？
> - [ ] A. `chdir()`
> - [ ] B. `getcwd()`
> - [ ] C. `pwd()`
> - [ ] D. `getwd()`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: Python 的 `os.getcwd()` 直接调用 C 的 `getcwd()`（定义在 `<unistd.h>` 中）。`chdir()` 是改变目录，`getwd()` 是 `getcwd()` 的旧版本（POSIX 已弃用）。

> [!question] 选择题 7
> 以下关于虚拟环境（venv）的说法，**错误**的是？
> - [ ] A. 每个虚拟环境的 site-packages 是独立的
> - [ ] B. 激活虚拟环境后，`python` 命令会使用虚拟环境中的解释器
> - [ ] C. 虚拟环境会自动继承系统 Python 的所有已安装包
> - [ ] D. 虚拟环境可以通过 `rm -rf env/` 简单的删除
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: 默认创建的虚拟环境（不带 `--system-site-packages`）**不继承**系统级 Python 的已安装包——它从一个干净的包列表开始。这意味着你需要重新 `pip install` 项目依赖。如果希望继承系统包，用 `python -m venv --system-site-packages myenv`。

> [!question] 选择题 8
> 以下标准库模块中，哪个负责命令行参数解析？
> - [ ] A. `sys`
> - [ ] B. `os`
> - [ ] C. `argparse`
> - [ ] D. `getpass`
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: `argparse` 是 Python 标准库中的命令行参数解析模块（`sys.argv` 只提供原始参数列表）。它相当于 C 语言的 `getopt_long()`——支持位置参数、可选参数、类型转换、帮助信息自动生成。更现代化的替代是第三方库 `click`。

---

### 🛠️ 动手练习题

> [!example] 练习题 1：创建一个命令行工具包
> **难度**: ⭐⭐
>
> 创建一个名为 `filetool` 的 Python 包，包含以下目录结构：
> ```
> filetool/
> ├── __init__.py
> ├── core.py        # count_lines, count_words, count_bytes 函数
> ├── formatters.py  # format_json, format_csv 函数
> └── __main__.py    # python -m filetool <filename> 入口
> ```
>
> 要求：
> 1. `python -m filetool file.txt` 时自动调用 `core.py` 中的统计函数并打印结果
> 2. `__init__.py` 中导出核心函数，让用户能 `from filetool import count_lines`
> 3. 编写 `setup.py` 或 `pyproject.toml` 使包可以被 `pip install -e .` 安装

> [!example] 练习题 2：C 头文件 vs Python 模块对比实验
> **难度**: ⭐⭐
>
> 创建一对等价的程序：
>
> **C 版本**：
> - `math_utils.h` 和 `math_utils.c`（定义 `int add(int, int)`）
> - `main.c`（调用 `add`）
> - Makefile（编译并链接）
>
> **Python 版本**：
> - `math_utils.py`（定义 `def add(a, b): return a + b`）
> - `main.py`（`from math_utils import add`）
>
> 对比：
> 1. 从源代码到成功运行的步骤数
> 2. 修改 `math_utils` 后是否需要重新"编译"（Python 的 .pyc 更新）
> 3. 运行时的模块加载时间（用 `python -m timeit` 和 `time` 命令）
>
> 写一份简短的对比总结。

> [!example] 练习题 3：虚拟环境与依赖管理实战
> **难度**: ⭐
>
> 完成以下完整的依赖管理操作：
> 1. 创建一个虚拟环境 `project_env`
> 2. 激活虚拟环境
> 3. 安装 `requests`、`click`、`rich` 三个包
> 4. 用 `pip freeze` 导出 `requirements.txt`
> 5. 退出虚拟环境
> 6. 删除虚拟环境目录
> 7. 重新创建同名虚拟环境
> 8. 用 `pip install -r requirements.txt` 恢复依赖
> 9. 编写一个简短的脚本验证三个包都可以成功 `import`
>
> 将你执行的所有命令记录下来，形成一个"虚拟环境使用手册"。

> [!example] 练习题 4：使用标准库替代 C 工具
> **难度**: ⭐⭐⭐
>
> 从以下 C 常用命令行工具中选择一个，用 Python 标准库（不安装第三方包）重写：
>
> | C 工具 | 功能 | Python 标准库模块 |
> |--------|------|-------------------|
> | `grep` | 文件内容搜索 | `re`, `pathlib` |
> | `find` | 文件查找 | `pathlib`, `os` |
> | `tar` | 归档管理 | `tarfile` |
> | `diff` | 文件对比 | `difflib` |
>
> 你的 Python 实现要求：
> 1. 提供与原始工具兼容的命令行接口（用 `argparse`）
> 2. 作为模块可导入（`if __name__ == "__main__"` 守卫）
> 3. 正确处理错误情况（文件不存在、权限不足等）
>
> 对比：C 版本和 Python 版本的代码行数、错误处理代码量、可移植性。
