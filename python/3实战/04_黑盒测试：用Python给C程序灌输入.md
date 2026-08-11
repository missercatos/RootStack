# 黑盒测试：用 Python 给 C 程序灌输入 (Black-Box Testing)
---

## 📖 章节概述

你写了一个 C 命令行工具（如排序器、计算器、文本过滤器），怎么系统性地测试它？手动在终端敲输入显然不够。本章教你用 Python 的 `subprocess` 模块自动化测试 C 程序：喂入各种输入、捕获输出、检查退出码、超时控制、批量测试用例管理——形成一套轻量但完整的黑盒测试框架。

> **核心理念**：C 程序编译后就是一个可执行文件，对外暴露的是 stdin/stdout/stderr 和退出码。Python 作为测试驱动器，完全不依赖 C 程序的内部实现——对 Python 来说，被测的 C 程序就是一个"有标准接口的黑盒"。这种测试方式与你在 C 中用 Unity/Check/CMock 做单元测试形成互补：单元测试测内部逻辑，黑盒测试测端到端行为。

---

### 📚 第一节：基础——subprocess 运行 C 程序

---

**示例 C 程序：一个简单的计算器**

```c
// calc.c —— 读取两个整数和一个运算符，输出结果
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    int a, b;
    char op;
    printf("输入算式 (如 3+5): ");
    fflush(stdout);
    if (scanf("%d%c%d", &a, &op, &b) != 3) {
        fprintf(stderr, "输入格式错误\n");
        return 1;
    }
    switch (op) {
        case '+': printf("%d\n", a + b); break;
        case '-': printf("%d\n", a - b); break;
        case '*': printf("%d\n", a * b); break;
        case '/':
            if (b == 0) { fprintf(stderr, "除数不能为 0\n"); return 2; }
            printf("%d\n", a / b); break;
        default:  fprintf(stderr, "不支持的运算符: %c\n", op); return 3;
    }
    return 0;
}
```

编译：
```bash
gcc -Wall -Wextra -std=c11 -o calc calc.c
```

**Python 测试驱动器——基础版**：

```python
import subprocess

def run_calc(input_str):
    """运行 calc 程序，传入输入字符串，返回 (stdout, stderr, exit_code)"""
    result = subprocess.run(
        ['./calc'],
        input=input_str,
        capture_output=True,
        text=True,
        timeout=5
    )
    return result.stdout, result.stderr, result.returncode

# 测试用例
out, err, code = run_calc('3+5')
print(f"stdout: {out!r}")
print(f"stderr: {err!r}")
print(f"exit_code: {code}")
assert '8' in out
assert code == 0

# 测试除零错误
out, err, code = run_calc('5/0')
assert code == 2
assert '除数不能为 0' in err
print("所有测试通过！")
```

**关键参数说明**：

| 参数 | 含义 |
|------|------|
| `input='3+5'` | 发送到子进程 stdin 的字符串 |
| `capture_output=True` | 捕获 stdout 和 stderr（等同于 `stdout=PIPE, stderr=PIPE`） |
| `text=True` | 以字符串而非字节方式处理 I/O |
| `timeout=5` | 5 秒后未完成则抛出 `TimeoutExpired` 异常 |

> 注意：`input` 参数传入的是完整字符串——如果 C 程序用 `scanf` 分多次读取，Python 一次提供全部输入即可；C 程序的 stdio 缓冲会自动按需分配。

**用 python -c 做快速黑盒测试**：

```bash
# 一行测试 calc 程序的各种输入
python -c "
import subprocess
for case in ['3+5', '10/3', '5/0', 'abc', '2^8']:
    r = subprocess.run('./calc', input=case, capture_output=True, text=True)
    print(f'输入={case:<6} 返回码={r.returncode} stdout={r.stdout.strip()!r} stderr={r.stderr.strip()!r}')
"
```

### 📝 小节练习

> [!question] 选择题 1
> `subprocess.run(capture_output=True, text=True)` 中 `text=True` 的作用是？
> - [ ] A. 使输出变成大写
> - [ ] B. 将 bytes 输出自动解码为 str，便于字符串比较
> - [ ] C. 格式化输出为 Markdown
> - [ ] D. 将 stderr 重定向到 stdout
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `text=True`（或 `universal_newlines=True`）使 `subprocess` 在 I/O 时使用文本模式：`input` 字符串自动编码，`stdout`/`stderr` 自动解码为 Python 字符串，省去 `.decode()` 步骤。

> [!question] 选择题 2
> `subprocess.run` 的 `timeout` 参数超时后会怎样？
> - [ ] A. 返回空字符串
> - [ ] B. 子进程被 kill，Python 抛出 `TimeoutExpired` 异常
> - [ ] C. 子进程继续运行但 Python 放弃等待
> - [ ] D. 自动重试一次
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `timeout` 到期后，Python 会 `kill()` 子进程并抛出 `subprocess.TimeoutExpired` 异常。捕获该异常可获取子进程已经产生的输出。

---

### 📚 第二节：结构化测试用例管理

---

当测试用例超过 10 个时，硬编码在脚本里变得不可维护。引入测试用例文件和测试框架。

**测试用例文件 `test_cases.json`**：

```json
[
  {
    "name": "基本加法",
    "input": "3+5\n",
    "expected_stdout": "8",
    "expected_exit_code": 0
  },
  {
    "name": "基本乘法",
    "input": "4*7\n",
    "expected_stdout": "28",
    "expected_exit_code": 0
  },
  {
    "name": "除零错误",
    "input": "5/0\n",
    "expected_stderr": "除数不能为 0",
    "expected_exit_code": 2
  },
  {
    "name": "格式错误",
    "input": "abc\n",
    "expected_stderr": "输入格式错误",
    "expected_exit_code": 1
  },
  {
    "name": "不支持的运算符",
    "input": "2^8\n",
    "expected_stderr": "不支持的运算符",
    "expected_exit_code": 3
  },
  {
    "name": "多空格容错",
    "input": "  10  -  3 \n",
    "expected_stdout": "7",
    "expected_exit_code": 0
  }
]
```

**测试脚本 `test_runner.py`**：

```python
#!/usr/bin/env python3
"""C 程序黑盒测试驱动器"""
import subprocess
import json
import sys
import os
import time

def run_test(program, case, timeout=5):
    """运行单个测试用例，返回 (passed, message)"""
    t0 = time.perf_counter()
    try:
        result = subprocess.run(
            [program],
            input=case.get('input', ''),
            capture_output=True,
            text=True,
            timeout=timeout
        )
    except subprocess.TimeoutExpired:
        return False, f"超时 (>{timeout}s)"
    except FileNotFoundError:
        return False, f"找不到可执行文件: {program}"
    elapsed = time.perf_counter() - t0

    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    exit_code = result.returncode

    checks = []

    if 'expected_stdout' in case:
        expected = case['expected_stdout']
        if expected not in stdout:
            checks.append(f"stdout 不匹配: 期望含 {expected!r}, 实际 {stdout!r}")

    if 'expected_stderr' in case:
        expected = case['expected_stderr']
        if expected not in stderr:
            checks.append(f"stderr 不匹配: 期望含 {expected!r}, 实际 {stderr!r}")

    if 'expected_exit_code' in case:
        expected = case['expected_exit_code']
        if exit_code != expected:
            checks.append(f"退出码不匹配: 期望 {expected}, 实际 {exit_code}")

    if checks:
        return False, '; '.join(checks) + f' ({elapsed:.3f}s)'

    return True, f"通过 ({elapsed:.3f}s)"

def main():
    if len(sys.argv) < 3:
        print(f"用法: {sys.argv[0]} <被测程序> <测试用例.json>", file=sys.stderr)
        print(f"示例: {sys.argv[0]} ./calc test_cases.json", file=sys.stderr)
        sys.exit(1)

    program = sys.argv[1]
    cases = json.load(open(sys.argv[2]))

    passed = 0
    failed = 0

    print(f"测试程序: {program}")
    print(f"测试用例: {sys.argv[2]}")
    print(f"共 {len(cases)} 个用例")
    print("=" * 60)

    for case in cases:
        ok, msg = run_test(program, case)
        status = "✓ PASS" if ok else "✗ FAIL"
        print(f"[{status}] {case['name']:<20} — {msg}")
        if ok:
            passed += 1
        else:
            failed += 1

    print("=" * 60)
    print(f"结果: {passed}/{len(cases)} 通过, {failed}/{len(cases)} 失败")

    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
```

**运行**：

```bash
# 先编译 C 程序
gcc -Wall -Wextra -std=c11 -o calc calc.c

# 运行测试
python test_runner.py ./calc test_cases.json
```

输出示例：
```
测试程序: ./calc
测试用例: test_cases.json
共 6 个用例
============================================================
[✓ PASS] 基本加法               — 通过 (0.002s)
[✓ PASS] 基本乘法               — 通过 (0.001s)
[✓ PASS] 除零错误              — 通过 (0.002s)
[✗ FAIL] 多空格容错             — stdout 不匹配: 期望含 '7', 实际 '' (0.002s)
============================================================
结果: 5/6 通过, 1/6 失败
```

> 这个框架的核心理念：**测试数据与测试逻辑分离**。JSON 文件管理所有用例（输入、期望输出），Python 脚本只负责执行和比对。测试人员不需要懂 Python 就能添加用例。

### 📝 小节练习

> [!question] 判断题 1
> `expected_stdout` 使用 `in` 而非 `==` 进行字符串比较，是为了允许输出中包含额外换行或空白。 ( )
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: 使用 `expected in actual`（子串匹配）比精确匹配更宽容，避免因尾部换行符或提示文字差异导致误报。需要精确匹配时可以用 `expected_stdout_exact` 字段区分。

> [!question] 选择题 1
> 测试用例 JSON 中某些字段设为可选的好处是？
> - [ ] A. 减少文件大小
> - [ ] B. 允许只验证关心的输出部分（如只检查退出码，不关心具体内容）
> - [ ] C. JSON 解析更快
> - [ ] D. 避免 JSON Schema 验证错误
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 灵活的匹配策略让用例编写更简洁——有时只关心程序是否正常退出（`expected_exit_code: 0`），有时只关心 stderr 是否报错，不需要每次都定义所有期望。

---

### 📚 第三节：高级技巧——交互式程序、二进制 I/O、压力测试

---

**技巧 1：测试交互式 C 程序**

有些 C 程序不是"一次性输入→一次性输出"，而是交互式的（如 REPL、游戏、网络协议交互）。`subprocess.Popen` 支持双向通信：

```python
import subprocess

# 测试一个简单的交互式 REPL
proc = subprocess.Popen(
    ['./repl'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

def send_cmd(cmd):
    """发送命令并读取直到下一个提示符"""
    proc.stdin.write(cmd + '\n')
    proc.stdin.flush()
    output = []
    while True:
        line = proc.stdout.readline()
        if not line or '> ' in line:  # 遇到提示符停止
            break
        output.append(line)
    return ''.join(output)

# 测试交互
send_cmd('help')
result = send_cmd('add 1 2')
assert '3' in result

proc.terminate()
proc.wait()
```

> `Popen` 提供管道级控制，`proc.stdin.write` + `proc.stdout.readline` 模拟终端交互。对于复杂的交互模式，建议使用 `pexpect` 第三方库。

**技巧 2：二进制 I/O 测试**

如果 C 程序读写二进制数据（通过 `fread`/`fwrite` 或原始 `read`/`write`），Python 用 `bytes` 类型处理：

```python
import subprocess
import struct

# C 程序期望读取 4 字节的 int（小端）再读取 4 字节的 int，返回它们的和
input_data = struct.pack('<ii', 42, 58)  # 打包为二进制

result = subprocess.run(
    ['./bin_sum'],
    input=input_data,
    capture_output=True
)

answer = struct.unpack('<i', result.stdout)[0]
print(f"42 + 58 = {answer}")
assert answer == 100
```

> Python 的 `struct` 模块直接对应 C 的 `int`/`float` 等类型的内存布局，是 C-Python 二进制数据交换的桥梁。详见 [[../../2精通/08_subprocess与进程管道：C与Python数据交换|精通 08 进程管道]]。

**技巧 3：压力测试——并发运行 C 程序**

```python
import subprocess
import concurrent.futures
import time

def run_instance(i):
    """运行 calc 的一个实例"""
    t0 = time.perf_counter()
    result = subprocess.run(
        ['./calc'],
        input=f'{i}+{i*2}\n',
        capture_output=True,
        text=True,
        timeout=2
    )
    elapsed = time.perf_counter() - t0
    return i, result.returncode, elapsed

# 并发运行 100 个实例
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(run_instance, i) for i in range(100)]
    for future in concurrent.futures.as_completed(futures):
        i, code, elapsed = future.result()
        if code != 0:
            print(f"实例 {i} 失败, 退出码={code}")
```

> `ThreadPoolExecutor` 模拟多用户并发。注意：这里是并发**启动**多个 C 进程——每个实例是独立进程，互不干扰。如果要测试单个多线程 C 程序，应在 C 侧使用 `pthread`。

### 📝 小节练习

> [!question] 选择题 1
> `subprocess.Popen` 相比于 `subprocess.run` 适合的场景是？
> - [ ] A. 所有场景
> - [ ] B. 需要与子进程进行**持续交互**（多次读写）的场景
> - [ ] C. 一次性运行并等待结束的场景
> - [ ] D. 不需要捕获输出的场景
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `subprocess.run` 适合"喂一次输入→等结束→取输出"的一次性调用。`Popen` 提供管道对象，支持在进程运行期间反复 `write`/`read`，适合交互式程序测试。

> [!question] 选择题 2
> `struct.pack('<ii', 42, 58)` 中的 `'<ii'` 表示？
> - [ ] A. 生成两个小端序的 4 字节有符号整数
> - [ ] B. 两个无符号 int 网络序
> - [ ] C. 生成字符串 `<ii`
> - [ ] D. 这不是有效的格式字符串
>
> > [!success]- 点击查看答案
> > 正确答案: A
> > **解析**: `<` 表示小端字节序，`i` 表示 C 的 `int` 类型（通常 4 字节有符号），两个 `i` 表示打包两个整数。`>ii` 为大端序。格式字符串的语法与 C 类型直接对应。

---

### 📚 第四节：与 C 语言单元测试框架的对比

---

| 维度 | Python 黑盒测试 | C 单元测试 (Unity/Check) |
|------|----------------|-------------------------|
| 测试对象 | 编译后的可执行文件 | `.c` 源文件中的单个函数 |
| 访问级别 | 仅 stdin/stdout/退出码 | 直接调用函数，可访问内部状态 |
| 依赖 | Python + subprocess | C 测试框架 + 链接被测代码 |
| 适合场景 | 集成测试、端到端验证、CLI 工具 | 单元测试、边界条件、内部逻辑 |
| 速度 | 较慢（每次 fork 进程） | 快（函数调用级别） |
| 隔离性 | 强（独立进程，不影响测试器） | 弱（共享地址空间，一个段错误 kill 整个测试） |

> **最佳实践**：两者结合。C 单元测试覆盖核心算法和边界条件，Python 黑盒测试覆盖命令行接口和集成场景。在 [[../../../c语言教程/3项目/|C 教程项目章节]] 中你会看到完整的混合测试策略。

**混合示例：同一个功能的双层测试**

```python
# Python 黑盒测试 + C 单元测试 协调运行
import subprocess
import os

# 1. 先运行 C 单元测试（编译为可执行文件 test_calc）
print("=== C 单元测试 ===")
result = subprocess.run(['./test_calc'], capture_output=True, text=True)
print(result.stdout)
if result.returncode != 0:
    print("C 单元测试失败，跳过黑盒测试")
    exit(1)

# 2. C 单元测试通过后，运行 Python 黑盒测试
print("=== Python 黑盒测试 ===")
result = subprocess.run(['python', 'test_runner.py', './calc', 'test_cases.json'])
exit(result.returncode)
```

### 📝 小节练习

> [!question] 选择题 1
> 以下哪种场景最适合用 Python 黑盒测试而非 C 单元测试？
> - [ ] A. 测试一个 C 内部函数的浮点精度
> - [ ] B. 测试命令行工具在不同参数组合下的行为和输出格式
> - [ ] C. 测试哈希表实现的插入性能
> - [ ] D. 测试内存分配器的碎片率
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: CLI 工具的端到端测试涉及参数解析、输出格式、退出码、stdin/stderr 交互——这些恰好是 `subprocess` 擅长而 C 单元测试框架不方便做的事。内部算法和性能测试则更适合 C 单元测试。

---

## 📋 章节测试

### 一、判断题（正确选✅，错误选❌）

> [!question] 判断题 1
> `subprocess.run` 的 `capture_output=True` 等同于 `stdout=subprocess.PIPE, stderr=subprocess.PIPE`。 ( )
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `capture_output=True` 是 Python 3.7 引入的便捷参数，内部实现就是 `stdout=PIPE, stderr=PIPE`。

> [!question] 判断题 2
> 黑盒测试可以替代所有的 C 单元测试。 ( )
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 黑盒测试只能验证"从外部可观测的行为"，无法覆盖内部逻辑分支、边界条件、内存管理细节。两者互补，不可相互替代。

> [!question] 判断题 3
> `subprocess.run(input='hello')` 的 `input` 参数可以传入任意二进制数据（bytes）。 ( )
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: 当不设置 `text=True` 时，`input` 接受 `bytes` 类型，可以传入任意二进制数据。设置 `text=True` 后 `input` 接受 `str` 类型。

> [!question] 判断题 4
> 使用 `subprocess.Popen` 测试交互式程序时，必须在读取响应前 `flush()` 写入的 stdin。 ( )
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: Python 的管道默认使用缓冲 I/O。如果不 `flush()`，写入的数据可能滞留在 Python 侧缓冲区而不发送给子进程，导致子进程一直等待输入而死锁。

> [!question] 判断题 5
> 被测 C 程序如果崩溃（SIGSEGV），`subprocess.run` 也会跟着崩溃。 ( )
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 子进程是独立进程，其崩溃（段错误、被信号终止）不会影响 Python 测试器进程。`subprocess.run` 会正常返回，`returncode` 为负值（表示被信号终止，如 `-11` 表示 SIGSEGV）。

> [!question] 判断题 6
> 测试用例 JSON 中的 `expected_stdout` 字段是必填的。 ( )
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 本章的测试框架设计中，`expected_stdout`、`expected_stderr`、`expected_exit_code` 均为可选字段。只填需要的验证项即可，框架会跳过未定义的字段。

---

### 二、选择题（单项选择题）

> [!question] 选择题 1
> 想在测试中同时捕获 stdout 和 stderr，但不需要分离它们时，应使用：
> - [ ] A. `capture_output=True`
> - [ ] B. `stdout=PIPE, stderr=STDOUT`
> - [ ] C. `capture_output=True, stderr=subprocess.STDOUT`
> - [ ] D. 以上都可，取决于需求
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `stderr=subprocess.STDOUT` 将 stderr 合并到 stdout 流中，`result.stdout` 将同时包含两路输出，这在只关心"有没有输出某内容"而不区分来源时更简单。

> [!question] 选择题 2
> 如果被测 C 程序进入了死循环，测试器应如何应对？
> - [ ] A. 手动 Ctrl+C
> - [ ] B. 设置 `timeout` 参数，超时自动 kill 子进程
> - [ ] C. Python 的 GIL 会自动检测
> - [ ] D. 不需要处理
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `subprocess.run(timeout=N)` 在 N 秒后向子进程发送 SIGKILL（Linux）或 TerminateProcess（Windows），并抛出 `TimeoutExpired` 异常。测试脚本应捕获该异常并标记为超时失败。

> [!question] 选择题 3
> `struct.pack('<i', 42)` 在 64 位 Linux 上输出多少字节？
> - [ ] A. 2
> - [ ] B. 4
> - [ ] C. 8
> - [ ] D. 取决于编译器
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `struct` 模块的 `i` 格式符固定对应 C 的 `int` 类型，在绝大多数平台（包括 Linux x86_64 和 ARM）上为 4 字节。`q` 对应 8 字节的 `long long`。

> [!question] 选择题 4
> 以下关于 `subprocess.run` 的说法错误的是？
> - [ ] A. 它是同步的，会阻塞直到子进程结束
> - [ ] B. 可以通过 `check=True` 让退出码非零时抛出异常
> - [ ] C. 它可以设置工作目录和环境变量
> - [ ] D. `input` 参数和 `stdin=subprocess.PIPE` 不能同时使用
>
> > [!success]- 点击查看答案
> > 正确答案: D
> > **解析**: `input` 参数实际上就是自动写入 `stdin=PIPE` 的数据——两者可以搭配使用，但 `input` 会自动处理写入和关闭。如果同时手动指定了另一个 `stdin` 源，`input` 会被忽略。

> [!question] 选择题 5
> 在 C 程序的测试用例 JSON 中添加 `timeout` 字段的作用是？
> - [ ] A. 加快测试执行
> - [ ] B. 为特定用例设置不同于默认值的超时时间
> - [ ] C. 让程序运行更慢以捕捉竞争条件
> - [ ] D. 跳过该测试用例
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 不同用例的执行时间可能差异很大——正常计算只需毫秒，但压测类用例可能需要几十秒。为每个用例设置 `timeout` 覆盖全局默认值，可以实现精细化超时控制。

> [!question] 选择题 6
> `subprocess.Popen` 的 `stdin=PIPE` 参数对应的 Python 操作是？
> - [ ] A. `proc.stdin.read()`
> - [ ] B. `proc.stdin.write(data)` + `proc.stdin.flush()`
> - [ ] C. `proc.send(data)`
> - [ ] D. `proc.communicate(data)`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `Popen` 返回对象后，`proc.stdin` 是一个可写的文件对象，通过 `.write()` 发送数据到子进程的 stdin，`.flush()` 确保数据立即传送。注意 `communicate()` 是一次性方法，发送完后关闭管道，不适合交互场景。

---

### 🛠️ 动手练习题

> [!example] 练习题 1：为你的 C 项目添加黑盒测试
> **难度**: ⭐
>
> 选择你在 [[../../../c语言教程/c目录|C 教程]] 中写过的任意一个命令行工具程序，做以下事情：
> 1. 编写 `test_cases.json`，包含至少 8 个测试用例（正常输入、边界值、错误输入、空输入）
> 2. 用 `test_runner.py`（复制本章代码）运行测试
> 3. 在 Makefile 中添加 `test` 目标，先编译后运行测试
> 4. 观察并修复测试中发现的任何 bug

> [!example] 练习题 2：生成器测试——验证代码生成器的输出
> **难度**: ⭐⭐
>
> 结合 [[03_代码生成器：用Python生成C头文件与骨架|实战 03 代码生成]] 中的代码生成器，写一个黑盒测试：
> 1. 用 Python 生成 `.h` 和 `.c` 文件
> 2. 用 `subprocess.run` 调用 GCC 编译生成的文件
> 3. 验证编译成功（退出码为 0）且无警告（stderr 为空）
> 4. 验证生成的头文件包含守卫宏
> 5. 验证生成的源文件中每个函数都有对应的实现
>
> 这实际上是一个"元测试"——用黑盒测试验证代码生成器的正确性。

> [!example] 练习题 3：模糊测试 (Fuzzing)
> **难度**: ⭐⭐⭐
>
> 写一个 Python 脚本，对你之前写的 C 计算器程序进行模糊测试：
> 1. 随机生成 1000 个输入字符串（包含正常算式、超长字符串、二进制随机数据、Unicode 字符）
> 2. 对每个输入运行 `./calc`，记录是否崩溃（返回码为负值表示收到信号）
> 3. 统计：崩溃数量、错误数量、成功数量
> 4. 如果发生崩溃，保存导致崩溃的输入到 `crash_inputs/` 目录
>
> 提示：
> - `os.urandom(N)` 生成随机字节
> - 正常算式可用模板随机生成：`f"{random.randint(-999,999)}{random.choice('+-*/')}{random.randint(-999,999)}"`
> - 退出码为负值（如 `-11`）表示收到信号终止（`-11` = SIGSEGV）
