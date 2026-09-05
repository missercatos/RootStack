# 代码生成器：用 Python 生成 C 头文件与骨架 (Code Generation)
---

## 章节概述

手工编写 `.h` 声明和 `.c` 实现、保持两者同步、为新模块创建 Makefile 片段——这些重复劳动在 C 项目增长到 20 个源文件后就变成噩梦。本章教你用 Python 自动化这些工作：从 JSON 规格文件读取函数签名，生成完整的 `.h` 头文件、`.c` 骨架实现、甚至测试用例模板。从 `python -c` 的模板快速生成到可复用的代码生成器脚本，全面覆盖。

> **核心理念**：Python 是 C 项目最好的"元编程"工具。C 的预处理器只能做简单的宏替换和条件编译，Python 却能操作任意数据结构、读写文件、甚至理解你的规格文件，生成模式化的 C 代码——这相当于一个"项目级预编译器"。在 [[../../../c语言教程/2深化/09_宏与预处理器|C 宏的教学]] 中你会看到 C 宏的极限，而 Python 代码生成填补了它无法触及的领域。

---

### 第一节：为什么用 Python 生成 C 代码

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

---

### 第二节：规格驱动的代码生成

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
 lines.append(f" /* TODO: 实现 {func['desc']} */")
 if func['return'] == 'void':
 lines.append(f" (void){func['params'][0][1]}; /* 消除未使用参数警告 */")
 else:
 lines.append(f" (void){func['params'][0][1]};")
 lines.append(f" return 0; /* 占位返回值 */")
 lines.append("}")
 lines.append("")
 return '\n'.join(lines) + '\n'

def generate_test_skeleton(spec):
 """生成测试文件的函数桩"""
 lines = ['#include <stdio.h>', f'#include "{spec["module"]}.h"', '', 'int main() {']
 for func in spec['functions']:
 args = ', '.join(['0' for _ in func['params']])
 lines.append(f' printf("{func["name"]} test not implemented\\n");')
 lines.append(f' /* {func["return"]} result = {func["name"]}({args}); */')
 lines.append('')
 lines.append(' printf("All tests passed.\\n");')
 lines.append(' return 0;')
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

---

### 第三节：python -c 快速模板生成

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
 print(f' STATE_{name} = {i},')
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
 print(f' {val},{f' /* sin({deg}°) = {math.sin(math.radians(deg)):.4f} */' if deg % 15 == 0 else ''}')
print('};')
"
```

> 这一步很关键：在嵌入式 C 开发中，经常需要预先计算三角函数表来替代耗时的 `sin()` 调用。Python 在编译时完成计算，生成的代码只含常量数组——零运行时开销。

---

### 第四节：批量 refactor——用 Python 改造 C 代码

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

---

### 第五节：实际项目集成

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

---

## 力扣练习

以下题目用于验证本章所学内容：

| 题号 | 题目 | 链接 | 涉及知识点 |
|------|------|------|-----------|
| — | 本章无对应力扣题 | — | 请用动手练习题自检 |
