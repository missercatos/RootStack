# pytest：单元测试与 C 项目联测 (Testing with pytest)
---

## 📖 章节概述

C 程序员测试 C 代码时，通常使用 Unity、CMock、Check 等框架——测试本身也是 C 代码，编译后运行。Python 的测试方式则不同：pytest 通过自动发现、内置断言、fixture 机制和参数化测试，让写测试变得几乎零开销。更强大的是，pytest 可以测试任何东西——包括你的 C 程序。本章从 pytest 基础语法开始，逐步深入到通过 subprocess 测试 C 可执行文件、通过 ctypes 直接调用 C 库函数，最后展示一个编译 + 测试 C 程序的完整 pytest fixture。

> **核心理念**：C 测试框架要求测试本身通过编译——"如果测试代码有 bug，谁来测试测试？"pytest 绕过了这个哲学问题：Python 是解释执行的，写错测试不会导致编译失败，而且 pytest 的断言失败信息远比 Unity 的 `TEST_ASSERT_EQUAL(3, result)` 直观。用 Python 测试 C 代码，是用一种更高效的语言去验证另一种更底层语言的行为。

---

### 📚 第一节：pytest 基础入门

#### 1.1 安装与第一个测试

```bash
# 安装 pytest
pip install pytest

# 或使用 uv
uv pip install pytest
```

创建第一个测试文件：

```python
# test_math.py
def add(a, b):
    return a + b

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0

def test_add_floats():
    assert add(1.5, 2.5) == 4.0
```

运行：

```bash
pytest test_math.py -v
```

输出：

```
test_math.py::test_add PASSED
test_math.py::test_add_floats PASSED

========================= 2 passed in 0.01s =========================
```

> 与 C 对比：Unity 测试需要 `TEST_ASSERT_EQUAL(5, add(2, 3))` 并编译运行，pytest 仅需 `assert add(2, 3) == 5` 加 `pytest` 命令。少了编译步骤，多了断言失败时的详细上下文（pytest 会显示表达式两边的值）。

#### 1.2 测试发现规则

pytest 自动发现以下模式的测试：

| 规则 | 示例 |
|------|------|
| 文件名以 `test_` 开头 | `test_math.py` |
| 文件名以 `_test` 结尾 | `math_test.py` |
| 类名以 `Test` 开头 | `class TestMath:` |
| 函数名以 `test_` 开头 | `def test_add():` |

```bash
# 运行所有测试
pytest

# 运行指定文件
pytest tests/test_math.py

# 运行匹配名称的测试
pytest -k "test_add"

# 显示详细输出（包括 print）
pytest -v -s
```

### 📝 小节练习

> [!question] 选择题 1
> pytest 默认发现测试文件的规则是什么？
> - [ ] A. 文件名包含 "test"
> - [ ] B. 文件名以 `test_` 开头或以 `_test` 结尾
> - [ ] C. 文件名以 `unittest` 开头
> - [ ] D. 所有 `.py` 文件
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: pytest 按约定发现测试：文件名匹配 `test_*.py` 或 `*_test.py`，函数名以 `test_` 开头，类名以 `Test` 开头。这与 Unity/Ceedling 的 `test/test_*.c` 命名约定类似。

---

### 📚 第二节：fixture 机制

fixture 是 pytest 最强大的特性——类似于 C 测试框架中的 `setUp()`/`tearDown()`，但更灵活。

#### 2.1 基础 fixture

```python
import pytest

@pytest.fixture
def sample_data():
    """准备测试数据，测试结束后清理"""
    data = {"name": "test", "values": [1, 2, 3]}
    yield data           # yield 前 = setUp, yield 后 = tearDown
    print("Cleaning up...")  # 只有使用 -s 时可见

def test_data_access(sample_data):
    assert sample_data["name"] == "test"
    assert len(sample_data["values"]) == 3
```

> 与 C 对比：Unity 的 `setUp()`/`tearDown()` 在每个测试前后执行，必须写在单独的 runner 文件中。pytest 的 fixture 在测试函数参数中声明即可，语法更自然。

#### 2.2 fixture 作用域

```python
@pytest.fixture(scope="function")   # 默认：每个测试函数都创建（类似 Unity setUp）
def per_test():
    return []

@pytest.fixture(scope="module")     # 每个模块创建一次
def module_data():
    return {"shared": True}

@pytest.fixture(scope="session")    # 整个测试会话创建一次（缓存编译产物）
def compiled_c_program():
    import subprocess
    subprocess.run(["gcc", "-o", "prog", "main.c"], check=True)
    yield "prog"
    import os
    os.remove("prog")
```

#### 2.3 conftest.py：共享 fixture

```
tests/
├── conftest.py       ← 此目录下所有测试共享这些 fixture
├── test_a.py
├── test_b.py
└── integration/
    ├── conftest.py   ← 仅 integration/ 目录共享
    └── test_c_program.py
```

```python
# tests/conftest.py
import pytest
import os

@pytest.fixture(scope="session")
def project_root():
    """返回项目根目录"""
    return os.path.dirname(os.path.dirname(__file__))

@pytest.fixture(scope="session")
def build_dir(project_root):
    build = os.path.join(project_root, "build")
    os.makedirs(build, exist_ok=True)
    return build
```

### 📝 小节练习

> [!question] 选择题 1
> pytest fixture 中 `yield` 的作用是？
> - [ ] A. 返回多个值
> - [ ] B. 分隔 setUp 和 tearDown 逻辑
> - [ ] C. 暂停测试执行
> - [ ] D. 标记 fixture 为生成器
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: fixture 中 `yield` 前的代码等价于 `setUp()`，`yield` 后的代码等价于 `tearDown()`。pytest 在测试函数执行完毕后继续执行 `yield` 后的清理代码。

> [!question] 判断题 1
> conftest.py 中的 fixture 需要显式导入才能在测试函数中使用。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: conftest.py 中的 fixture 会被 pytest 自动发现并注入到同目录及子目录下的测试函数中，无需显式 import。

---

### 📚 第三节：参数化测试与标记

#### 3.1 @pytest.mark.parametrize

```python
import pytest

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

@pytest.mark.parametrize("n,expected", [
    (0, 0),
    (1, 1),
    (2, 1),
    (3, 2),
    (5, 5),
    (10, 55),
])
def test_fibonacci(n, expected):
    assert fibonacci(n) == expected
```

运行时每个参数组合变成独立的测试用例：

```
test_fib.py::test_fibonacci[0-0]   PASSED
test_fib.py::test_fibonacci[1-1]   PASSED
test_fib.py::test_fibonacci[2-1]   PASSED
test_fib.py::test_fibonacci[3-2]   PASSED
test_fib.py::test_fibonacci[5-5]   PASSED
test_fib.py::test_fibonacci[10-55] PASSED
```

> 与 C 对比：Unity 的参数化需要手动写循环或使用宏展开（`TEST_RANGE`），pytest 的参数化是声明式的，且每个参数组合有独立的测试名称和通过/失败状态。

#### 3.2 标记与跳过

```python
@pytest.mark.slow
def test_heavy_computation():
    import time
    time.sleep(2)
    assert True

@pytest.mark.skip(reason="C library not yet compiled")
def test_cffi_call():
    pass

@pytest.mark.skipif(sys.platform == "win32", reason="Unix-only")
def test_unix_socket():
    pass

@pytest.mark.parametrize("compiler", ["gcc", "clang"])
def test_compiles(compiler):
    result = subprocess.run([compiler, "--version"], capture_output=True)
    assert result.returncode == 0
```

```bash
# 只运行标记为 slow 的测试
pytest -m slow

# 跳过标记为 slow 的测试
pytest -m "not slow"

# 列出所有标记
pytest --markers
```

### 📝 小节练习

> [!question] 选择题 1
> `@pytest.mark.parametrize("a,b,expected", [(1,2,3), (2,3,5)])` 会生成几个测试用例？
> - [ ] A. 1 个
> - [ ] B. 2 个
> - [ ] C. 3 个
> - [ ] D. 4 个
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 参数列表中每个元组生成一个独立测试用例。此处 `(1,2,3)` 和 `(2,3,5)` 各生成一个，共 2 个测试用例，分别命名为 `test_xxx[1-2-3]` 和 `test_xxx[2-3-5]`。

---

### 📚 第四节：用 pytest 测试 C 程序

#### 4.1 黑盒测试：subprocess 运行 C 可执行文件

这是最直接的方式——将 C 程序当作可执行文件，通过 subprocess 捕获 stdout/stderr 验证行为。

```python
# tests/test_sort.py
import subprocess
import pytest
import os

@pytest.fixture(scope="module")
def sort_program():
    """编译 C 排序程序，返回可执行文件路径"""
    src = "sort.c"
    out = "sort_prog"
    result = subprocess.run(
        ["gcc", "-Wall", "-Wextra", "-O0", "-o", out, src],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        pytest.fail(f"Compilation failed:\n{result.stderr}")
    yield out
    os.remove(out)

def run_sort(program, input_str):
    """运行排序程序并返回输出"""
    result = subprocess.run(
        [f"./{program}"],
        input=input_str,
        capture_output=True,
        text=True,
        timeout=5
    )
    return result.stdout.strip()

def test_sort_empty(sort_program):
    output = run_sort(sort_program, "")
    assert output == ""

def test_sort_single(sort_program):
    output = run_sort(sort_program, "5")
    assert output == "5"

def test_sort_normal(sort_program):
    output = run_sort(sort_program, "3 1 4 1 5 9 2 6")
    assert output == "1 1 2 3 4 5 6 9"

def test_sort_negative_numbers(sort_program):
    output = run_sort(sort_program, "-3 5 -1 0 2 -8")
    assert output == "-8 -3 -1 0 2 5"
```

> 这种模式类似于在 Shell 脚本中测试 C 程序，但 pytest 提供了更好的断言、参数化和报告。对于不暴露 C API 的独立 CLI 工具，这是最实用的测试方案。

#### 4.2 白盒测试：ctypes 调用 C 库函数

如果 C 代码编译为共享库（`.so`），pytest 可以通过 ctypes 直接调用 C 函数：

```c
// mathlib.h
#ifndef MATHLIB_H
#define MATHLIB_H
int add(int a, int b);
int factorial(int n);
int is_prime(int n);
#endif

// mathlib.c
#include "mathlib.h"
int add(int a, int b) { return a + b; }
int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}
int is_prime(int n) {
    if (n < 2) return 0;
    for (int i = 2; i * i <= n; i++)
        if (n % i == 0) return 0;
    return 1;
}
```

```bash
# 编译为共享库
gcc -shared -fPIC -o libmathlib.so mathlib.c
```

```python
# tests/test_mathlib.py
import ctypes
import pytest
import os

@pytest.fixture(scope="module")
def mathlib():
    lib = ctypes.CDLL("./libmathlib.so")
    lib.add.argtypes = [ctypes.c_int, ctypes.c_int]
    lib.add.restype = ctypes.c_int
    lib.factorial.argtypes = [ctypes.c_int]
    lib.factorial.restype = ctypes.c_int
    lib.is_prime.argtypes = [ctypes.c_int]
    lib.is_prime.restype = ctypes.c_int
    return lib

def test_add(mathlib):
    assert mathlib.add(2, 3) == 5
    assert mathlib.add(-1, 1) == 0

@pytest.mark.parametrize("n,expected", [(0, 1), (1, 1), (3, 6), (5, 120)])
def test_factorial(mathlib, n, expected):
    assert mathlib.factorial(n) == expected

@pytest.mark.parametrize("n,expected", [
    (2, 1), (3, 1), (4, 0), (17, 1), (97, 1), (100, 0)
])
def test_is_prime(mathlib, n, expected):
    assert mathlib.is_prime(n) == expected
```

> 与 C 对比：Unity 测试 C 代码时，测试本身也是 C 代码——`TEST_ASSERT_EQUAL(5, add(2, 3))`。pytest + ctypes 的优势是：测试逻辑用 Python 写，调用更灵活，断言输出更详细。

#### 4.3 完整的编译 + 测试 fixture

```python
# tests/conftest.py
import subprocess
import pytest
import os
import shutil

BUILD_DIR = "_build_test"

@pytest.fixture(scope="session")
def build_c_library():
    """编译 C 共享库，整个测试会话只编译一次"""
    os.makedirs(BUILD_DIR, exist_ok=True)

    sources = ["src/mathlib.c", "src/utils.c"]
    output = os.path.join(BUILD_DIR, "libtest.so")

    cmd = [
        "gcc", "-shared", "-fPIC",
        "-Wall", "-Wextra", "-g", "-O0",
        "-o", output, *sources,
        "-I", "include"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        shutil.rmtree(BUILD_DIR, ignore_errors=True)
        pytest.fail(f"Build failed:\n{result.stderr}")

    if result.stderr:
        print(f"[compiler warnings]\n{result.stderr}")

    yield output

    # 清理（也可保留用于调试）
    shutil.rmtree(BUILD_DIR, ignore_errors=True)

@pytest.fixture
def clib(build_c_library):
    """每个测试获取一个新的库加载句柄"""
    import ctypes
    lib = ctypes.CDLL(build_c_library)
    yield lib
    # ctypes 自动管理句柄
```

### 📝 小节练习

> [!question] 选择题 1
> pytest 通过 subprocess 测试 C 程序的方案属于什么类型的测试？
> - [ ] A. 单元测试
> - [ ] B. 集成测试 / 黑盒测试
> - [ ] C. 性能测试
> - [ ] D. 压力测试
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: subprocess 运行可执行文件，不直接访问 C 源码或内部函数——这是黑盒测试。这类似于在 Makefile 中用 Shell 脚本 `./prog input | diff expected -` 验证，但 pytest 提供了更好的断言和报告。

> [!question] 判断题 1
> 用 pytest 测试 C 代码时，ctypes 方案比 subprocess 方案更底层，能直接调用 C 函数。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: ctypes 直接加载 `.so` 并调用导出的 C 函数（白盒），`subprocess` 通过进程间通信与可执行文件交互（黑盒）。ctypes 适合测试库函数，subprocess 适合测试完整的 CLI 程序。

---

### 📚 第五节：pytest vs C 测试框架全面对比

| 特性 | pytest | Unity (C) | CMock (C) | Google Test (C++) |
|------|--------|-----------|-----------|-------------------|
| 测试语言 | Python | C | C | C++ |
| 断言语法 | `assert x == y` | `TEST_ASSERT_EQUAL(expected, actual)` | `TEST_ASSERT_EQUAL` | `EXPECT_EQ(x, y)` |
| 编译 | 无需编译 | 编译测试 + 被测代码 | 编译测试 + mock | 编译测试 + 被测代码 |
| Mock | `unittest.mock` | 无（需 CMock） | 自动生成 mock | `EXPECT_CALL` |
| 参数化 | `@parametrize` | 手动循环 | 手动循环 | `TEST_P` |
| fixture | `@pytest.fixture` | `setUp()`/`tearDown()` | `setUp()`/`tearDown()` | `SetUp()`/`TearDown()` |
| 并行执行 | `pytest-xdist` | 无内置 | 无内置 | 无内置 |
| 覆盖率报告 | `pytest-cov` | `gcov` + `lcov` | `gcov` + `lcov` | `gcov` + `lcov` |
| 发现测试 | 自动发现 | 手动注册 | 手动注册 | 自动发现（部分） |

> **关键洞察**：pytest 最大的优势不是语法糖，而是"用 Python 编写测试逻辑"。当你需要生成海量测试数据、读取 JSON 配置文件、调用外部 API 验证结果时，Python 的生态远胜于 C。

### 📝 小节练习

> [!question] 选择题 1
> 以下关于 pytest 与 C 测试框架的对比，哪项是错误的？
> - [ ] A. pytest 不需要编译测试代码
> - [ ] B. pytest 支持的 fixture 比 Unity 的 setUp/tearDown 更灵活
> - [ ] C. pytest 可以直接测试 C 共享库中的函数
> - [ ] D. pytest 可以替代 C 代码的内存泄漏检测
>
> > [!success]- 点击查看答案
> > 正确答案: D
> > **解析**: pytest 无法替代 Valgrind 或 AddressSanitizer 进行内存检测。pytest 验证的是程序行为，内存检测需要专门的运行时分析工具。

---

## 📋 章节测试

### 一、判断题

> [!question] 判断题 1
> pytest 只能测试 Python 代码，不能用于测试 C 程序。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: pytest 通过 `subprocess` 可以黑盒测试任何可执行文件（包括 C 程序），通过 `ctypes` 可以直接调用 C 共享库中的函数。

> [!question] 判断题 2
> pytest fixture 中 `yield` 前的代码在每次测试前执行，`yield` 后的代码在每次测试后执行。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: fixture 中的 `yield` 将代码分为 setUp（前）和 tearDown（后）两部分，这是 pytest fixture 实现资源管理的关键机制。

> [!question] 判断题 3
> conftest.py 必须放在项目根目录才能被 pytest 识别。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: conftest.py 可以放在任意测试目录下，其 fixture 自动对该目录及所有子目录中的测试可见。多个 conftest.py 可以共存，作用域分层。

> [!question] 判断题 4
> `@pytest.mark.parametrize` 中的每个参数组合对应独立的测试用例，有独立的通过/失败状态。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: 每个参数组合生成独立的测试节点，pytest 的输出中可看到 `test_name[param0-param1]` 格式的独立测试标识符。

> [!question] 判断题 5
> pytest 的 `assert` 和 Python 内置的 `assert` 是完全不同的两套机制。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: pytest 使用 Python 内置的 `assert` 语句，但通过 AST 重写提供了更丰富的失败信息（如显示表达式两边的值）。它是同一个 `assert` 关键字，但 pytest 增强了其输出。

> [!question] 判断题 6
> 使用 ctypes 调用 C 库时，必须在每个测试函数中重新加载 `.so` 文件。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 使用 `scope="module"` 或 `scope="session"` 的 fixture 可以在多个测试间共享同一个库加载句柄，避免重复加载。

### 二、选择题

> [!question] 选择题 1
> pytest 中 `-k` 选项的作用是？
> - [ ] A. 杀死运行中的测试进程
> - [ ] B. 按关键字过滤要运行的测试
> - [ ] C. 跳过指定测试
> - [ ] D. 设置测试超时
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `-k EXPRESSION` 运行名称匹配表达式的测试，如 `pytest -k "fibonacci"` 只运行名称包含 "fibonacci" 的测试。

> [!question] 选择题 2
> 以下哪个 fixture 作用域在整个测试会话期间只创建一次？
> - [ ] A. `scope="function"`
> - [ ] B. `scope="class"`
> - [ ] C. `scope="module"`
> - [ ] D. `scope="session"`
>
> > [!success]- 点击查看答案
> > 正确答案: D
> > **解析**: `scope="session"` 确保 fixture 在整个 pytest 运行期间只创建一次，适合编译 C 库、建立数据库连接等开销大的操作。

> [!question] 选择题 3
> 在混合 C/Python 项目中，哪个 pytest fixture 最适合编译 C 代码？
> - [ ] A. scope="function"（每次测试编译）
> - [ ] B. scope="class"
> - [ ] C. scope="module" 或 "session"
> - [ ] D. scope="package"
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: C 编译开销大，应在 module 或 session 级别编译一次，所有测试共享编译产物。function 级别会导致每个测试都重新编译，效率极低。

> [!question] 选择题 4
> `subprocess.run` 的 `capture_output=True` 参数的作用是？
> - [ ] A. 在终端显示程序输出
> - [ ] B. 捕获 stdout 和 stderr
> - [ ] C. 丢弃程序输出
> - [ ] D. 将输出写入文件
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `capture_output=True` 将子进程的 stdout 和 stderr 分别捕获到 `result.stdout` 和 `result.stderr` 中，便于在测试中断言程序输出。

> [!question] 选择题 5
> 以下关于 ctypes 测试 C 库的说法正确的是？
> - [ ] A. ctypes 需要在 C 代码中添加特殊标记
> - [ ] B. ctypes 调用 C 函数前需要声明 argtypes 和 restype
> - [ ] C. ctypes 只能调用以 `extern "C"` 声明的函数
> - [ ] D. ctypes 是 Python 标准库之外的第三方包
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 使用 ctypes 时应显式设置 `argtypes` 和 `restype`，否则 Python 可能错误推断参数类型导致栈损坏。ctypes 是 Python 标准库的一部分（`import ctypes`）。

> [!question] 选择题 6
> 以下操作中，pytest 的 `assert` 在失败时能提供最详细信息的表达式是？
> - [ ] A. `assert True`
> - [ ] B. `assert result is not None`
> - [ ] C. `assert add(2, 3) == 6`
> - [ ] D. `assert flag`
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: 对比表达式失败时，pytest 会显示两边的值——如 `assert 5 == 6`。而 `assert result is not None` 失败时只能看到 `None is not None`，`assert flag` 只能看到 `assert False`。

---

### 🛠️ 动手练习题

> [!example] 练习题 1：pytest 基础练习
> **难度**: ⭐
>
> 实现一个 `calculator.py`，包含 `add`、`subtract`、`multiply`、`divide` 函数：
> 1. 为每个函数编写 3 个以上测试用例
> 2. 使用 `@pytest.mark.parametrize` 参数化 `add` 测试
> 3. 为 `divide` 添加 `pytest.raises(ZeroDivisionError)` 测试
> 4. 运行 `pytest -v` 确保全部通过

> [!example] 练习题 2：用 pytest 测试 C 排序程序
> **难度**: ⭐⭐
>
> 1. 用 C 编写 `sort.c`：读取标准输入的整数（空格分隔），输出排序结果
> 2. 编写 pytest fixture：编译 `sort.c`，编译失败时 fails 测试
> 3. 编写参数化测试：空输入、单元素、正序、逆序、重复元素、大量随机数
> 4. 添加超时检测（`subprocess.run` 的 `timeout` 参数），防止死循环挂起测试

> [!example] 练习题 3：ctypes 测试 C 链表
> **难度**: ⭐⭐⭐
>
> 1. 用 C 实现链表：`list_create`、`list_append`、`list_get`、`list_size`、`list_destroy`
> 2. 编译为共享库
> 3. 用 ctypes 映射结构体 `struct Node` 和所有函数签名
> 4. 编写 pytest 测试：创建 → 追加 → 读取 → 检查大小 → 销毁
> 5. 使用 scope="module" 的 fixture 确保库只编译一次

> [!example] 练习题 4：为现有 C 项目添加 pytest 测试基础设施
> **难度**: ⭐⭐⭐
>
> 假设你有一个 C 项目（使用了 Makefile），为其建立 pytest 测试基础设施：
> 1. 编写 `tests/conftest.py`：包含编译 fixture、临时目录 fixture、测试数据 fixture
> 2. 编写 `tests/test_build.py`：验证 `make` 编译成功、可执行文件存在
> 3. 编写 `tests/test_integration.py`：用 subprocess 测试程序的典型输入输出
> 4. 编写 `Makefile` 的 `test` 目标：先编译 C 代码，再运行 `pytest`
