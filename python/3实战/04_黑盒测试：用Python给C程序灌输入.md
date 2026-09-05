# 黑盒测试：用 Python 给 C 程序灌输入 (Black-Box Testing)
---

## 章节概述

你写了一个 C 命令行工具（如排序器、计算器、文本过滤器），怎么系统性地测试它？手动在终端敲输入显然不够。本章教你用 Python 的 `subprocess` 模块自动化测试 C 程序：喂入各种输入、捕获输出、检查退出码、超时控制、批量测试用例管理——形成一套轻量但完整的黑盒测试框架。

> **核心理念**：C 程序编译后就是一个可执行文件，对外暴露的是 stdin/stdout/stderr 和退出码。Python 作为测试驱动器，完全不依赖 C 程序的内部实现——对 Python 来说，被测的 C 程序就是一个"有标准接口的黑盒"。这种测试方式与你在 C 中用 Unity/Check/CMock 做单元测试形成互补：单元测试测内部逻辑，黑盒测试测端到端行为。

---

### 第一节：基础——subprocess 运行 C 程序

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
 default: fprintf(stderr, "不支持的运算符: %c\n", op); return 3;
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

---

### 第二节：结构化测试用例管理

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
 "input": " 10 - 3 \n",
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
 status = " PASS" if ok else " FAIL"
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
[ PASS] 基本加法 — 通过 (0.002s)
[ PASS] 基本乘法 — 通过 (0.001s)
[ PASS] 除零错误 — 通过 (0.002s)
[ FAIL] 多空格容错 — stdout 不匹配: 期望含 '7', 实际 '' (0.002s)
============================================================
结果: 5/6 通过, 1/6 失败
```

> 这个框架的核心理念：**测试数据与测试逻辑分离**。JSON 文件管理所有用例（输入、期望输出），Python 脚本只负责执行和比对。测试人员不需要懂 Python 就能添加用例。

---

### 第三节：高级技巧——交互式程序、二进制 I/O、压力测试

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
 if not line or '> ' in line: # 遇到提示符停止
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
input_data = struct.pack('<ii', 42, 58) # 打包为二进制

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

---

### 第四节：与 C 语言单元测试框架的对比

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

---

## 力扣练习

以下题目用于验证本章所学内容：

| 题号 | 题目 | 链接 | 涉及知识点 |
|------|------|------|-----------|
| — | 本章无对应力扣题 | — | 请用动手练习题自检 |
