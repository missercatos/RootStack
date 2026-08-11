# 代码生成器：用 Python 生成 C 头文件与骨架 (Code Generation)
---

## 📖 章节概述

手工编写 `.h` 声明和 `.c` 实现、保持两者同步、为新模块创建 Makefile 片段——这些重复劳动在 C 项目增长到 20 个源文件后就变成噩梦。本章教你用 Python 自动化这些工作：从 JSON 规格文件读取函数签名，生成完整的 `.h` 头文件、`.c` 骨架实现、甚至测试用例模板。从 `python -c` 的模板快速生成到可复用的代码生成器脚本，全面覆盖。

> **核心理念**：Python 是 C 项目最好的"元编程"工具。C 的预处理器只能做简单的宏替换和条件编译，Python 却能操作任意数据结构、读写文件、甚至理解你的规格文件，生成模式化的 C 代码——这相当于一个"项目级预编译器"。在 [[../../../c语言教程/2深化/09_宏与预处理器|C 宏的教学]] 中你会看到 C 宏的极限，而 Python 代码生成填补了它无法触及的领域。

---

### 📚 第一节：为什么用 Python 生成 C 代码

---

C 语言在大型项目中的模板代码问题：

| 痛点 | C 原生方案 | Python 方案 |
|------|-----------|-------------|
| 新模块的 .h + .c 框架 | 复制粘贴旧文件，手工修改 | 脚本一键生成 |
| 保持 .h 和 .c 的函数签名一致 | 人工检查 | 从一份规格文件同时生成两个 |
| 添加新函数后更新测试文件 | 手工添加 | 扫描 .h 自动生成测试骨架 |
| 多平台条件编译配置 | `#ifdef` 嵌套混乱 | Python 生成不同平台的实现文件 |
| 协议/序列化代码 | 手工编写 struct 和 pack/unpack | Python 从 schema 生成 struct + 序列化函数 |

> Python 代码生成不是"用 Python 替代 C"，而是"用 Python 生成 C，然后 C 编译运行"。生成的代码仍然受你的掌控——你可以审查、修改、版本控制。

**最简单的入门例子**：

```bash
# 用 python -c 生成一个简单的 C 头文件
python -c "
macro = 'MAX_BUFFER'
value = 1024
print('#ifndef CONFIG_H')
print('#define CONFIG_H')
print(f'#define {macro} {value}')
print('#endif')
" > config.h
```

> 这已经比手动敲更不容易出错——如果 `macro` 和 `value` 来自 JSON 配置文件，改配置就能自动更新头文件。

### 📝 小节练习

> [!question] 判断题 1
> Python 代码生成本质上是用 Python 替代 C 编译器。 ( )
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: Python 代码生成只负责**产生 C 源代码**（.c/.h 文件），最终的编译仍由 GCC/Clang 完成。Python 是"元编程工具"，不是编译器替代品。

> [!question] 选择题 1
> C 语言预处理器实现代码生成的主要局限是？
> - [ ] A. 无法定义宏
> - [ ] B. 不能做文件 I/O 和外部数据读取
> - [ ] C. `#define` 速度太慢
> - [ ] D. 不支持 `#ifdef`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: C 预处理器只能操作当前翻译单元内的文本（`#include`、`#define`、`#if`），不能读取 JSON/CSV 等外部文件，不能遍历目录，不能进行字符串处理——这些都是 Python 的强项。

---

### 📚 第二节：规格驱动的代码生成

---

定义一个 JSON 规格文件作为"单一事实来源"，Python 读取它并生成所有派生物（头文件、源文件骨架、测试文件、Makefile 片段）。

**规格文件示例 `api_spec.json`**：

```json
{
  "module": "calculator",
  "version": "1.0.0",
  "author": "RootStack",
  "description": "四则运算模块",
  "functions": [
    {
      "name": "add",
      "return": "int",
      "params": [["int", "a"], ["int", "b"]],
      "desc": "两数相加"
    },
    {
      "name": "subtract",
      "return": "int",
      "params": [["int", "a"], ["int", "b"]],
      "desc": "两数相减"
    },
    {
      "name": "multiply",
      "return": "int",
      "params": [["int", "a"], ["int", "b"]],
      "desc": "两数相乘"
    },
    {
      "name": "divide",
      "return": "int",
      "params": [["int", "a"], ["int", "b"]],
      "desc": "两数相除，b 不能为 0"
    }
  ]
}
```

**代码生成器 `gen_calc.py`**：

```python
#!/usr/bin/env python3
"""从 JSON 规格文件生成 C 模块的 .h 和 .c 文件"""
import json
import sys
import os
from datetime import datetime

def param_str(params):
    """生成参数列表字符串 'int a, int b'"""
    return ', '.join(f'{t} {n}' for t, n in params)

def generate_header(spec):
    lines = []
    guard = f"{spec['module'].upper()}_H"
    lines.append(f"/* {spec['module']}.h —— {spec['description']}")
    lines.append(f" * 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f" * 生成器: {os.path.basename(__file__)}")
    lines.append(" * 规格来源: api_spec.json")
    lines.append(" */")
    lines.append(f"#ifndef {guard}")
    lines.append(f"#define {guard}")
    lines.append("")
    lines.append("#include <stddef.h>")
    lines.append("")
    for func in spec['functions']:
        lines.append(f"/** {func['desc']} */")
        lines.append(f"{func['return']} {func['name']}({param_str(func['params'])});")
        lines.append("")
    lines.append(f"#endif /* {guard} */")
    return '\n'.join(lines) + '\n'

def generate_source(spec):
    lines = []
    lines.append(f"/* {spec['module']}.c —— {spec['description']}")
    lines.append(f" * 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(" */")
    lines.append(f'#include "{spec["module"]}.h"')
    lines.append("#include <stddef.h>")
    lines.append("")
    for func in spec['functions']:
        lines.append(f"{func['return']} {func['name']}({param_str(func['params'])})")
        lines.append("{")
        lines.append(f"    /* TODO: 实现 {func['desc']} */")
        if func['return'] == 'void':
            lines.append(f"    (void){func['params'][0][1]}; /* 消除未使用参数警告 */")
        else:
            lines.append(f"    (void){func['params'][0][1]};")
            lines.append(f"    return 0; /* 占位返回值 */")
        lines.append("}")
        lines.append("")
    return '\n'.join(lines) + '\n'

def generate_test_skeleton(spec):
    """生成测试文件的函数桩"""
    lines = ['#include <stdio.h>', f'#include "{spec["module"]}.h"', '', 'int main() {']
    for func in spec['functions']:
        args = ', '.join(['0' for _ in func['params']])
        lines.append(f'    printf("{func["name"]} test not implemented\\n");')
        lines.append(f'    /* {func["return"]} result = {func["name"]}({args}); */')
        lines.append('')
    lines.append('    printf("All tests passed.\\n");')
    lines.append('    return 0;')
    lines.append('}')
    return '\n'.join(lines) + '\n'

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"用法: {sys.argv[0]} api_spec.json [--test]", file=sys.stderr)
        sys.exit(1)

    spec = json.load(open(sys.argv[1]))

    with open(f"{spec['module']}.h", 'w') as f:
        f.write(generate_header(spec))
    print(f"已生成: {spec['module']}.h")

    with open(f"{spec['module']}.c", 'w') as f:
        f.write(generate_source(spec))
    print(f"已生成: {spec['module']}.c")

    if '--test' in sys.argv:
        with open(f"test_{spec['module']}.c", 'w') as f:
            f.write(generate_test_skeleton(spec))
        print(f"已生成: test_{spec['module']}.c")
```

**运行并编译验证**：

```bash
python gen_calc.py api_spec.json --test
# 生成 calculator.h, calculator.c, test_calculator.c

# 编译验证
gcc -Wall -Wextra -std=c11 -c calculator.c -o calculator.o
gcc -Wall -Wextra -std=c11 -o test_calc test_calculator.c calculator.o
./test_calc
```

> 当你在规格文件中添加新函数时，只需重新运行 `python gen_calc.py api_spec.json`，所有的 `.h`、`.c`、测试文件都同步更新——不再需要手工维护三处的一致。

### 📝 小节练习

> [!question] 选择题 1
> `generate_header` 函数中 `guard` 变量的作用是？
> - [ ] A. 定义模块版本号
> - [ ] B. 生成 `#ifndef/#define/#endif` 的包含守卫，防止头文件重复包含
> - [ ] C. 保护代码不被编译器修改
> - [ ] D. 为每个函数添加访问控制
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `#ifndef MODULE_H` / `#define MODULE_H` / `#endif` 是 C 头文件的标准"包含守卫"（include guard）。如果同一个头文件被多次 `#include`，第二次及之后会被跳过，避免重复声明错误。

> [!question] 判断题 1
> `json.load(open(filename))` 读取大文件时会一次性全部加载到内存。 ( )
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `json.load()` 将整个文件内容读入内存并解析为 Python 对象。对于规格文件这种通常不超过几十 KB 的场景，这完全没问题。

---

### 📚 第三节：python -c 快速模板生成

---

当只需要生成一次性的小模板时，不需要写完整的 `.py` 脚本，`python -c` 足够。

**生成单个模块的头文件**

```bash
# 从命令行参数传入模块名和函数列表
python -c "
import sys
module = sys.argv[1]
funcs = sys.argv[2:]
guard = module.upper() + '_H'
print(f'#ifndef {guard}')
print(f'#define {guard}')
print()
for f in funcs:
    print(f'int {f}(int a, int b);')
print()
print(f'#endif')
" mathlib add subtract multiply divide > mathlib.h
```

**生成 enum 定义（从文本列表）**

```bash
# 将状态码列表转为 C 的 enum
echo -e "IDLE\nRUNNING\nSTOPPED\nERROR" | python -c "
import sys
print('typedef enum {')
for i, line in enumerate(sys.stdin):
    name = line.strip()
    if name:
        print(f'    STATE_{name} = {i},')
print('} State;')
"
```

输出：
```c
typedef enum {
    STATE_IDLE = 0,
    STATE_RUNNING = 1,
    STATE_STOPPED = 2,
    STATE_ERROR = 3,
} State;
```

**生成查找表（从数学公式计算）**

```bash
# 生成正弦查找表（0°~90°，每步 5°）
python -c "
import math
print('// 正弦查找表 sin_table[deg/5]，值放大 1000 倍，用整数存储')
print('const int16_t sin_table[19] = {')
for i in range(19):
    deg = i * 5
    val = int(math.sin(math.radians(deg)) * 1000)
    print(f'    {val},{f' /* sin({deg}°) = {math.sin(math.radians(deg)):.4f} */' if deg % 15 == 0 else ''}')
print('};')
"
```

> 这一步很关键：在嵌入式 C 开发中，经常需要预先计算三角函数表来替代耗时的 `sin()` 调用。Python 在编译时完成计算，生成的代码只含常量数组——零运行时开销。

### 📝 小节练习

> [!question] 选择题 1
> 用 Python 预计算查找表并生成 C 常量数组，相比于在 C 运行时计算的好处是？
> - [ ] A. 代码更短
> - [ ] B. 节省运行时的 CPU 计算开销（静态常量 vs 函数调用）
> - [ ] C. 更易于调试
> - [ ] D. 以上全部
>
> > [!success]- 点击查看答案
> > 正确答案: D
> > **解析**: 预计算的查找表生成编译时常量，运行时无需计算，减少 CPU 开销；Python 代码可读性好、易验证正确性；C 侧只需一个数组访问，非常简洁。

---

### 📚 第四节：批量 refactor——用 Python 改造 C 代码

---

代码生成不限于"生成新文件"，也可以"改造已有文件"。这在代码规范统一、批量重命名等场景非常有用。

**统一函数命名风格（snake_case → camelCase）**

```python
#!/usr/bin/env python3
"""将所有 C 文件中的函数调用从 snake_case 改为 CamelCase"""
import re
import os
import glob

def snake_to_camel(name):
    return ''.join(w.capitalize() for w in name.split('_'))

functions_to_rename = ['init_buffer', 'free_buffer', 'write_data', 'read_data']

for filepath in glob.glob('src/**/*.c', recursive=True):
    with open(filepath, 'r') as f:
        content = f.read()

    original = content
    for old_name in functions_to_rename:
        new_name = snake_to_camel(old_name)
        content = content.replace(old_name, new_name)

    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f'已更新: {filepath} ({old_name} → {new_name})')
```

> 在 C 中做同样的批量重构需要 IDE（如 CLion）的 Rename 功能，或者结合 `sed` 和模式匹配——前者强依赖 IDE，后者在函数名作为子串出现时会误改。Python 脚本可以加入边界判断（如 `re.sub(r'\b' + old_name + r'\b', ...)` 避免部分匹配），精确控制。

**自动添加 `#include` 守卫**

```python
#!/usr/bin/env python3
"""检查所有 .h 文件是否有 include guard，没有则自动添加"""
import os, glob

for filepath in glob.glob('**/*.h', recursive=True):
    with open(filepath, 'r') as f:
        lines = f.readlines()

    has_guard = any('#ifndef' in l for l in lines[:30])

    if not has_guard:
        guard = os.path.basename(filepath).upper().replace('.', '_')
        with open(filepath, 'w') as f:
            f.write(f'#ifndef {guard}\n')
            f.write(f'#define {guard}\n')
            f.write('\n')
            f.writelines(lines)
            f.write(f'\n#endif /* {guard} */\n')
        print(f'已添加守卫: {filepath}')
```

### 📝 小节练习

> [!question] 判断题 1
> Python 脚本可以安全地批量修改 C 源文件，因为 C 编译器会拒绝任何语法错误的修改。 ( )
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: C 编译器只能捕获语法错误，无法保证语义正确（如函数名替换错误不会导致编译失败）。批量重构应配合版本控制（`git diff` 检查变更）、编译验证、以及回归测试。

---

### 📚 第五节：实际项目集成

---

在 C 项目中集成 Python 代码生成的标准做法：

**1. 在 Makefile 中添加生成规则**

```makefile
# Makefile 片段
calculator.h calculator.c: api_spec.json gen_calc.py
	python gen_calc.py api_spec.json

test_calculator.c: api_spec.json gen_calc.py
	python gen_calc.py api_spec.json --test

#
```

> 这样，每次 `api_spec.json` 或生成器脚本变更时，`make` 会自动重新生成 C 文件。生成文件被声明为 `.PHONY` 以确保总是执行。

**2. 在 CMake 中使用 `add_custom_command`**

```cmake
add_custom_command(
    OUTPUT calculator.h calculator.c
    COMMAND python ${CMAKE_SOURCE_DIR}/tools/gen_calc.py
            ${CMAKE_SOURCE_DIR}/config/api_spec.json
    DEPENDS ${CMAKE_SOURCE_DIR}/tools/gen_calc.py
            ${CMAKE_SOURCE_DIR}/config/api_spec.json
    COMMENT "生成 calculator 模块文件"
)
add_executable(myapp main.c calculator.c)
```

**3. 使用 `python -c` 作为 git hook**

```bash
# .git/hooks/pre-commit —— 提交前确保 .h 和 .c 的函数声明一致
SHELL = bash

check-prototypes:
	@python -c "
import sys, re, os
errors = []
for h in [f for f in os.listdir('.') if f.endswith('.h')]:
    c = h.replace('.h', '.c')
    if os.path.exists(c):
        h_funcs = set(re.findall(r'(\w+)\(', open(h).read()))
        c_funcs = set(re.findall(r'\w+ (\w+)\(', open(c).read()))
        if h_funcs - c_funcs:
            errors.append(f'{h} 声明但 {c} 未实现: {h_funcs - c_funcs}')
if errors:
    print('\\n'.join(errors))
    sys.exit(1)
"
```

> 这个 git hook 在每次提交时自动检查：头文件中声明的函数在 `.c` 中是否有对应的实现定义，反之亦然。这是 C 项目中常见的 CI 检查项。

### 📝 小节练习

> [!question] 选择题 1
> Makefile 中将 `calculator.h` 声明为 `.PHONY` 的原因是什么？
> - [ ] A. 为了美观
> - [ ] B. 确保每次 `make` 都执行生成规则，不以文件存在作为跳过依据
> - [ ] C. 为了兼容 CMake
> - [ ] D. 为了并行编译
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 如果不声明 `.PHONY`，`make` 会比较目标文件和依赖文件的时间戳——只要 `calculator.h` 比 `api_spec.json` 新，就不会重新生成。`.PHONY` 强制每次都执行生成规则确保最新。

> [!question] 选择题 2
> CMake 的 `add_custom_command` 与 `add_custom_target` 的区别是？
> - [ ] A. 没有区别
> - [ ] B. `add_custom_command` 仅在 OUTPUT 文件被其他目标依赖时才执行
> - [ ] C. `add_custom_command` 总是执行
> - [ ] D. `add_custom_command` 仅用于 Python 脚本
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `add_custom_command` 定义的命令仅在其 OUTPUT 文件被其他构建目标依赖时才执行，支持增量构建。`add_custom_target` 总是执行（类似 `.PHONY`），适合 `make clean` 类任务。

---

## 📋 章节测试

### 一、判断题（正确选✅，错误选❌）

> [!question] 判断题 1
> Python 代码生成工具生成 `.c` 文件后，Python 解释器会在运行时将这些文件编译为机器码。 ( )
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: Python 只负责生成 C 源代码文本文件（.c/.h）。编译为机器码仍由 GCC/Clang 在之后的构建步骤中完成。Python 生成的文件是纯文本，不需要 Python 解释器即可编译。

> [!question] 判断题 2
> `json.load(open('spec.json'))` 和 `json.loads(open('spec.json').read())` 效果完全相同。 ( )
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `json.load(fp)` 从文件对象读取，`json.loads(s)` 从字符串读取。最终解析出的 Python 对象相同，前者在实现上更高效（不需要先全部读入字符串再解析）。

> [!question] 判断题 3
> `#ifndef` 包含守卫的目的是防止同一个源文件被多次编译。 ( )
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 包含守卫防止的是同一个**头文件**被同一个**编译单元**（.c 文件）多次 `#include`——如果 A 包含了 B，C 也包含了 B，当某个 .c 同时包含 A 和 C 时，B 会被间接包含两次。守卫避免了重复声明错误。它不影响编译单元之间的链接。

> [!question] 判断题 4
> Python 代码生成脚本的副作用是必须每次编译时都安装 Python 解释器。 ( )
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: 代码生成脚本需要 Python 运行。但生成的 .c/.h 是纯 C 代码——可以选择将生成步骤集成到构建系统（开发时必须安装 Python），也可以在发布时将生成好的 C 文件随源码分发（最终用户不依赖 Python）。

> [!question] 判断题 5
> 用 `python -c` 生成 C 头文件时, `print()` 输出的内容会被 Python 解释器检查语法。 ( )
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: Python 只负责执行 `print()` 语句并输出文本。输出的 C 代码语法是否正确，Python 并不知道——必须由 GCC/Clang 编译时检验。生成器可以加入额外验证步骤（如用正则检查括号匹配）。

> [!question] 判断题 6
> 在 Makefile 中使用 `.PHONY` 声明生成文件的规则后，每次 `make` 都会无条件重新生成该文件。 ( )
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `.PHONY` 告诉 make 该目标不是文件名，因此不检查文件时间戳，每次都执行其规则。这适合生成类目标（头文件可能被手工编辑，不能仅以来源文件时间戳判断）。

---

### 二、选择题（单项选择题）

> [!question] 选择题 1
> 一个合适的代码生成器输出应该是：
> - [ ] A. 二进制机器码
> - [ ] B. 人类可读的 C 源代码，可以手动修改和版本控制
> - [ ] C. 运行时动态生成的汇编代码
> - [ ] D. 加密的字节码
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 代码生成器的输出应是可读、可维护、可版本控制的 C 源代码。生成代码通常附带 `/* 自动生成 */` 注释，开发者在必要时应能理解和修改。

> [!question] 选择题 2
> 在 `"params": [["int", "a"], ["int", "b"]]` 的 JSON 结构中，每个元素 `["int", "a"]` 表示：
> - [ ] A. 函数返回值为 int，名称为 a
> - [ ] B. 参数类型为 int，参数名为 a
> - [ ] C. 数组类型为 int，变量名为 a
> - [ ] D. 这是一个 C 结构体定义
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 在规格文件中，`params` 数组中每个子数组表示一个函数参数：`[类型, 名称]`。`generate_source` 函数使用 `param_str()` 将其展开为 `int a, int b` 的形式。

> [!question] 选择题 3
> Python 中 `', '.join(f'{t} {n}' for t, n in params)` 的作用是？
> - [ ] A. 将参数转换为 JSON 格式
> - [ ] B. 生成类似 `"int a, int b"` 的参数列表字符串
> - [ ] C. 验证参数的合法性
> - [ ] D. 将参数写入文件
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `join` 将生成器表达式产生的每个字符串（如 `"int a"`）用逗号+空格连接，生成 C 函数声明中参数列表部分。

> [!question] 选择题 4
> 代码生成器 `gen_calc.py` 中，`if func['return'] == 'void'` 分支处理的作用是？
> - [ ] A. 忽略该函数的生成
> - [ ] B. 对 void 函数不生成 return 语句，避免编译错误
> - [ ] C. 将返回值改为 int
> - [ ] D. 添加额外的空行
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: void 函数不能有 `return 0;` 语句（会触发编译警告或错误），因此生成器针对 void 返回类型不做 return 只生成 `(void)param;` 消除未使用参数警告。

> [!question] 选择题 5
> 批量重构工具函数中使用 `content.replace(old_name, new_name)` 可能的问题是什么？
> - [ ] A. 速度太慢
> - [ ] B. 可能替换了注释或字符串中的同名文本
> - [ ] C. Python 不支持字符串替换
> - [ ] D. 替换顺序不影响结果
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 简单的 `.replace()` 无法区分函数调用和注释/字符串字面量中的同名文本。严谨的做法是使用正则 `re.sub(r'\b' + old_name + r'\b', new_name, content)` 要求单词边界，或使用 `libclang` 等 C 解析器做 AST 级重构。

> [!question] 选择题 6
> 将 Python 代码生成集成到 CMake 构建系统的正确方式是？
> - [ ] A. 在 CMakeLists.txt 中嵌入 Python 代码
> - [ ] B. 使用 `add_custom_command` 定义生成规则，用 `add_executable` 引用生成文件
> - [ ] C. 手动运行 Python 脚本，将输出加入版本控制
> - [ ] D. 用 `target_sources` 直接调用 Python 函数
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `add_custom_command` 定义如何从规格文件生成 C 代码，`add_executable` 或 `target_sources` 引用这些生成文件。CMake 自动处理依赖关系：规格文件变更时重新生成 C 代码，再触发重编译。

---

### 🛠️ 动手练习题

> [!example] 练习题 1：生成多平台兼容层
> **难度**: ⭐⭐
>
> 设计一个 JSON 规格文件，描述一个"平台抽象层"：包含 `thread_create`、`mutex_lock`、`file_open` 等函数。写一个 Python 生成器，同时生成两个文件：
> - `platform_posix.c` — 使用 `pthread` 和 POSIX 文件 API
> - `platform_win32.c` — 使用 Windows API
>
> 规格文件中每个函数应包含 `posix_impl_hint` 和 `win32_impl_hint` 字段（用注释形式插入到生成的骨架代码中）。

> [!example] 练习题 2：从 C 代码反向生成文档
> **难度**: ⭐⭐⭐
>
> 写一个 Python 脚本，读取所有 `.h` 头文件，提取函数声明和紧邻的 `/** ... */` 或 `//` 注释，生成 Markdown 格式的 API 文档。要求：
> - 用正则提取函数原型和注释
> - 按模块分组（每个 .h 文件为一个模块）
> - 输出包含回链到源文件的 Obsidian 链接
>
> 提示：参考本章 `re.compile` + 多行匹配的技巧。

> [!example] 练习题 3：协议代码生成器
> **难度**: ⭐⭐⭐
>
> 设计一个 JSON 规格描述自定义二进制协议的消息格式（字段名、类型、偏移量、字节序）。写 Python 生成器生成：
> 1. C 的 `struct` 定义（带 `__attribute__((packed))`）
> 2. `serialize` 函数（将 struct 写入 buffer）
> 3. `deserialize` 函数（从 buffer 解析 struct）
> 4. 每个字段的 getter/setter 宏
>
> 示例规格（部分）：
> ```json
> {"msg_name": "Heartbeat", "fields": [
>   {"name": "seq", "type": "uint32_t", "offset": 0},
>   {"name": "timestamp", "type": "uint64_t", "offset": 4}
> ]}
> ```
>
> 提示：使用 `struct` 模块验证生成的代码字节布局是否正确。
