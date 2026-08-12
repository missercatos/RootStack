# 内嵌 CPython：在 C 程序里运行 Python (Embedding Python in C)
---

## 章节概述

上一章我们让 Python 调用 C 库；现在反过来——让 C 程序内嵌 Python 解释器。这是本教程的**核心章节**之一：Python 作为 C 项目的"脚本引擎"，让你在 C 项目中使用 Python 读取配置文件、执行动态逻辑、甚至运行完整的数据处理管道，而不必重新编译 C 代码。

> **核心理念**：Python 内嵌 = C 程序拥有一个可编程的运行时。你可以在编译后的 C 程序中动态加载、执行和修改业务逻辑——这正是游戏引擎、数据库系统、高性能服务器常用的"脚本化"架构。

---

### 第一节：最小内嵌示例

#### 1.1 第一个内嵌程序

```c
// embed_basic.c — 最小 Python 内嵌示例
// 编译: gcc -o embed_basic embed_basic.c $(python3-config --cflags --ldflags --embed)

#define PY_SSIZE_T_CLEAN
#include <Python.h>

int main(int argc, char *argv[]) {
 // 1. 初始化 Python 解释器（必须最先调用）
 Py_Initialize();

 // 2. 执行 Python 代码字符串
 PyRun_SimpleString("print('Hello from embedded Python!')");
 PyRun_SimpleString("import sys; print(f'Python {sys.version}')");
 PyRun_SimpleString("x = sum(range(100)); print(f'1+2+...+99 = {x}')");

 // 3. 清理
 if (Py_FinalizeEx() < 0) {
 return 120; // 清理失败
 }
 return 0;
}
```

```bash
# 编译（推荐使用 pkg-config / python3-config）
gcc -o embed_basic embed_basic.c \
 $(python3-config --cflags --ldflags --embed)

# 或者手动指定
gcc -o embed_basic embed_basic.c \
 -I/usr/include/python3.12 \
 -lpython3.12

> **跨平台提示**：
> - **Windows**：Python 开发头文件在 `%LOCALAPPDATA%\Programs\Python\Python312\include\`，库文件为 `python312.lib`，使用 MSVC 或 MinGW 编译
> - **macOS**：头文件路径如 `/Library/Frameworks/Python.framework/Versions/3.12/include/python3.12/`，推荐统一使用 `python3-config --cflags --ldflags --embed` 跨平台编译

# 运行
./embed_basic
```

输出：
```
Hello from embedded Python!
Python 3.12.3 (main, ...)
1+2+...+99 = 4950
```

> **关键对比**：上面的 `PyRun_SimpleString` 就等价于在终端执行 `python -c "..."`——但它在你的 C 进程内部运行，而不是启动外部子进程。这意味着 Python 代码可以直接访问 C 程序的数据结构（后面会展示）。

### 小节练习

> [!question] 判断题 1
> `Py_Initialize()` 和 `Py_FinalizeEx()` 可以在程序生命周期中被多次调用。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 一般情况下，`Py_Initialize()` 和 `Py_Finalize()` 配对使用一次。CPython 对重复初始化/清理的支持不完善（某些全局状态和扩展模块在清理后不能正确重建）。

---

### 第二节：C 和 Python 之间的值传递

#### 2.1 C → Python：创建 Python 对象

```c
#include <Python.h>

int main() {
 Py_Initialize();

 // 创建 Python 对象
 PyObject *py_int = PyLong_FromLong(42);
 PyObject *py_float = PyFloat_FromDouble(3.14159);
 PyObject *py_str = PyUnicode_FromString("Hello C → Python");
 PyObject *py_none = Py_None; // None 是单例，直接引用
 Py_INCREF(py_none); // 必须增加引用计数

 // 打印对象（调用 Python 的 str()）
 PyObject *repr = PyObject_Repr(py_int);
 printf("Python int: %s\n", PyUnicode_AsUTF8(repr));
 Py_DECREF(repr);

 // 清理
 Py_DECREF(py_int);
 Py_DECREF(py_float);
 Py_DECREF(py_str);
 Py_DECREF(py_none);

 Py_FinalizeEx();
 return 0;
}
```

#### 2.2 Python → C：提取 C 值

```c
#include <Python.h>
#include <stdio.h>

int main() {
 Py_Initialize();

 // 执行 Python 代码获取值
 PyObject *py_val = PyRun_String("2 ** 100", Py_eval_input,
 PyDict_New(), PyDict_New());
 if (py_val == NULL) {
 PyErr_Print();
 return 1;
 }

 // 方法一：用 API 提取
 long as_long = PyLong_AsLong(py_val);
 printf("2**100 = %ld (可能溢出!)\n", as_long); // 溢出！

 // 方法二：用 PyLong_AsLongLong
 long long as_ll = PyLong_AsLongLong(py_val);
 printf("2**100 = %lld\n", as_ll); // 也可能溢出

 // 方法三：转为字符串（安全但性能差）
 PyObject *str_repr = PyObject_Str(py_val);
 printf("2**100 = %s\n", PyUnicode_AsUTF8(str_repr));
 Py_DECREF(str_repr);

 Py_DECREF(py_val);
 Py_FinalizeEx();
 return 0;
}
```

#### 2.3 C 值 → Python 对象的 API 速查

| C 值 | CPython API | 返回值 |
|------|------------|--------|
| `long` | `PyLong_FromLong(val)` | `PyObject*` |
| `long long` | `PyLong_FromLongLong(val)` | `PyObject*` |
| `double` | `PyFloat_FromDouble(val)` | `PyObject*` |
| `const char*` | `PyUnicode_FromString(val)` | `PyObject*` |
| `const char*`(bytes) | `PyBytes_FromString(val)` | `PyObject*` |

| Python 对象 | 提取 C 值的 API | C 类型 |
|-------------|----------------|--------|
| int | `PyLong_AsLong(obj)` | `long` |
| int | `PyLong_AsLongLong(obj)` | `long long` |
| float | `PyFloat_AsDouble(obj)` | `double` |
| str | `PyUnicode_AsUTF8(obj)` | `const char*` |
| bytes | `PyBytes_AsString(obj)` | `const char*` |

> **重要规则**：每个 `PyObject*` 都遵循引用计数规则——获得新引用时引用计数 +1（创建函数自动处理），使用完后必须 `Py_DECREF()`。忘记 DECREF → 内存泄漏；过早 DECREF → 段错误。

### 小节练习


> [!question] 判断题 1
> `Py_None` 每次使用时都需要 `Py_INCREF`。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `Py_None` 是借用的引用（borrowed reference），如果你要持有一个引用（存储、返回等），必须先 `Py_INCREF(Py_None)`。否则它的引用计数可能被考虑为 0。

---

### 第三节：导入模块并调用 Python 函数

#### 3.1 完整的 C → Python 函数调用流程

```c
// embed_call.c — 从 C 调用 Python 函数
// 编译: gcc -o embed_call embed_call.c $(python3-config --cflags --ldflags --embed)

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdio.h>

int main() {
 Py_Initialize();

 // ===== 第 1 步：导入模块 =====
 PyObject *pModule = PyImport_ImportModule("json");
 if (pModule == NULL) {
 PyErr_Print();
 return 1;
 }

 // ===== 第 2 步：获取函数对象 =====
 PyObject *pFunc = PyObject_GetAttrString(pModule, "dumps");
 if (pFunc == NULL || !PyCallable_Check(pFunc)) {
 PyErr_Print();
 return 1;
 }

 // ===== 第 3 步：构造参数 =====
 PyObject *pArgs = PyTuple_New(1); // 参数元组

 // 构造 Python 字典: {"name": "Alice", "age": 30}
 PyObject *pDict = PyDict_New();
 PyDict_SetItemString(pDict, "name", PyUnicode_FromString("Alice"));
 PyDict_SetItemString(pDict, "age", PyLong_FromLong(30));

 PyTuple_SetItem(pArgs, 0, pDict); // 将 dict 作为第一个参数
 // 注意：PyTuple_SetItem 会"窃取"引用，不需要 Py_DECREF(pDict)

 // ===== 第 4 步：调用函数 =====
 PyObject *pResult = PyObject_CallObject(pFunc, pArgs);
 Py_DECREF(pArgs);

 if (pResult == NULL) {
 PyErr_Print();
 return 1;
 }

 // ===== 第 5 步：提取结果 =====
 printf("JSON 结果: %s\n", PyUnicode_AsUTF8(pResult));

 // ===== 第 6 步：清理 =====
 Py_DECREF(pResult);
 Py_DECREF(pFunc);
 Py_DECREF(pModule);

 Py_FinalizeEx();
 return 0;
}
```

输出：
```
JSON 结果: {"name": "Alice", "age": 30}
```

#### 3.2 调用 Python 函数的步法总结

```
1. PyImport_ImportModule("module_name") → 获取模块对象
2. PyObject_GetAttrString(module, "func") → 获取函数对象
3. PyTuple_New(n) → 创建参数元组
4. PyTuple_SetItem(tuple, index, arg) → 设置每个参数
5. PyObject_CallObject(func, args) → 调用函数
6. PyUnicode_AsUTF8 / PyLong_AsLong(result) → 提取返回值
7. 对每个 PyObject* 调用 Py_DECREF → 释放引用
```

### 小节练习

> [!question] 判断题 1
> `PyTuple_SetItem` 会自动增加传入对象的引用计数。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `PyTuple_SetItem` 会"窃取"（steal）传入对象的引用——它不增加引用计数，而是直接持有该引用。调用者不需要对传入的对象调用 `Py_DECREF`。


---

### 第四节：实战：配置驱动的 C 程序

这是一个完整的实际场景：C 程序用 Python 脚本做配置，读取并处理结果。

```c
// embed_config.c — Python 脚本驱动的 C 配置系统
// 编译: gcc -o embed_config embed_config.c $(python3-config --cflags --ldflags --embed)

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdio.h>
#include <stdlib.h>

// 配置结构体（C 端使用）
typedef struct {
 char *server_host;
 int server_port;
 int max_connections;
 double timeout;
 int debug_mode;
} ServerConfig;

// 从 Python dict 中提取配置
int load_config_from_python(const char *script_path, ServerConfig *cfg) {
 PyObject *pName = PyUnicode_DecodeFSDefault(script_path);
 PyObject *pModule = PyImport_Import(pName);
 Py_DECREF(pName);

 if (pModule == NULL) {
 PyErr_Print();
 return -1;
 }

 PyObject *pFunc = PyObject_GetAttrString(pModule, "get_config");
 if (pFunc == NULL || !PyCallable_Check(pFunc)) {
 PyErr_Print();
 Py_DECREF(pModule);
 return -1;
 }

 // 调用 Python 函数 get_config() → 返回 dict
 PyObject *pConfigDict = PyObject_CallObject(pFunc, NULL);
 Py_DECREF(pFunc);

 if (pConfigDict == NULL) {
 PyErr_Print();
 Py_DECREF(pModule);
 return -1;
 }

 // 从 Python dict 提取各字段
 PyObject *val;

 val = PyDict_GetItemString(pConfigDict, "host");
 cfg->server_host = strdup(PyUnicode_AsUTF8(val));

 val = PyDict_GetItemString(pConfigDict, "port");
 cfg->server_port = (int)PyLong_AsLong(val);

 val = PyDict_GetItemString(pConfigDict, "max_connections");
 cfg->max_connections = (int)PyLong_AsLong(val);

 val = PyDict_GetItemString(pConfigDict, "timeout");
 cfg->timeout = PyFloat_AsDouble(val);

 val = PyDict_GetItemString(pConfigDict, "debug");
 cfg->debug_mode = PyObject_IsTrue(val);

 Py_DECREF(pConfigDict);
 Py_DECREF(pModule);
 return 0;
}

int main() {
 ServerConfig cfg = {0};
 Py_Initialize();

 // 将当前目录加入 sys.path
 PyRun_SimpleString("import sys; sys.path.insert(0, '.')");

 if (load_config_from_python("server_config", &cfg) != 0) {
 Py_FinalizeEx();
 return 1;
 }

 printf("===== 服务器配置 =====\n");
 printf("Host: %s\n", cfg.server_host);
 printf("Port: %d\n", cfg.server_port);
 printf("Max Connections: %d\n", cfg.max_connections);
 printf("Timeout: %.1f 秒\n", cfg.timeout);
 printf("Debug Mode: %s\n", cfg.debug_mode ? "ON" : "OFF");

 // C 程序可以使用配置了...
 // start_server(&cfg);

 free(cfg.server_host);
 Py_FinalizeEx();
 return 0;
}
```

```python
# server_config.py — Python 配置文件（可随时修改，无需重新编译！）
import os

def get_config():
 """返回服务器配置字典"""
 return {
 "host": os.environ.get("HOST", "0.0.0.0"),
 "port": int(os.environ.get("PORT", "8080")),
 "max_connections": 1000,
 "timeout": 30.0,
 "debug": os.environ.get("DEBUG", "0") == "1",
 }
```

```bash
# 编译并运行
gcc -o embed_config embed_config.c $(python3-config --cflags --ldflags --embed)
./embed_config

# 通过环境变量覆盖配置
HOST=192.168.1.1 PORT=9090 DEBUG=1 ./embed_config
```

> **这就是内嵌 Python 的威力**：配置逻辑用 Python 编写——无需重新编译 C 代码、无需重启构建系统、甚至可以在运行时动态加载/更新配置脚本。

### 小节练习


> [!question] 判断题 1
> 内嵌 CPython 的 C 程序在调用 `PyRun_SimpleString` 时，当前的 GIL 状态由 C 线程持有。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `Py_Initialize()` 后，调用线程自动获取 GIL。所有 CPython API 调用（除非明确声明"可释放"）都假定调用者持有 GIL。

---

### 第五节：编译与链接详解

#### 5.1 使用 pkg-config / python3-config

```bash
# 查看编译选项
python3-config --cflags
# -I/usr/include/python3.12 -I/usr/include/python3.12 ...

# 查看链接选项
python3-config --ldflags
# -L/usr/lib/python3.12/config-3.12-x86_64-linux-gnu -lpython3.12 ...

> **跨平台提示**：
> - **Windows**：`python3-config` 在 Windows 上不可用，需用 MSVC 项目配置或直接指定路径
> - **macOS**：`python3-config` 行为一致，输出路径为 `/Library/Frameworks/...`，编译时也可用 `python3-config --cflags --ldflags --embed` 代替手动写路径

# Python 3.8+ 使用 --embed 嵌入链接选项
python3-config --ldflags --embed
# -L/usr/lib -lpython3.12 -lcrypt -ldl -lm ...

# 一键编译
gcc -o myapp myapp.c $(python3-config --cflags --ldflags --embed)
```

> Python < 3.8 时，`python3-config --ldflags` 不包含 `-lpython`，需要手动加 `$(python3-config --cflags --ldflags) -lpython3.x`。

#### 5.2 CMake 中内嵌 CPython

```cmake
cmake_minimum_required(VERSION 3.12)
project(EmbedPython C)

find_package(Python3 REQUIRED COMPONENTS Interpreter Development.Embed)

add_executable(myapp main.c)
target_include_directories(myapp PRIVATE ${Python3_INCLUDE_DIRS})
target_link_libraries(myapp PRIVATE Python3::Python)
```

#### 5.3 多版本共存

```bash
# 检查系统中安装的 Python 版本
ls /usr/include/python3*

# 针对特定版本编译
gcc -o myapp myapp.c -I/usr/include/python3.12 -lpython3.12

# 使用 python3.11
gcc -o myapp myapp.c -I/usr/include/python3.11 -lpython3.11
```

### 小节练习

> [!question] 判断题 1
> `python3-config --embed` 选项仅在 Python 3.8+ 可用。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: Python 3.8 开始提供 `--embed` 选项，它输出完整的链接参数（包括 `-lpython3.x`）。旧版本需要手动添加 `-lpython`。

---

## 章节测试

### 一、判断题

> [!question] 判断题 1
> `#define PY_SSIZE_T_CLEAN` 是可选的定义，不影响程序行为。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `PY_SSIZE_T_CLEAN` 必须在 `#include <Python.h>` 之前定义。它确保 `PyArg_ParseTuple` 等函数使用 `Py_ssize_t` 而非旧的 `int` 类型，避免 64 位系统上的截断错误。

> [!question] 判断题 2
> `PyRun_SimpleString` 和 `PyRun_String` 都是执行 Python 代码的 API。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `PyRun_SimpleString` 适合执行语句（自动处理打印），`PyRun_String` 更底层——可选择 `Py_eval_input`（表达式）、`Py_single_input`（交互式）或 `Py_file_input`（模块）。

> [!question] 判断题 3
> `PyObject_CallObject` 可以调用 Python 对象上实现 `__call__` 方法的任何对象。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `PyObject_CallObject` 调用实现了 `tp_call` 槽位的任何对象——函数、方法、类、可调用对象都适用。但应先用 `PyCallable_Check` 验证。

> [!question] 判断题 4
> 内嵌 Python 的 C 程序中，可以通过 `Py_FinalizeEx()` 后再次 `Py_Initialize()` 来重启解释器。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 虽然 API 文档说不应重复调用，实际上 CPython 的多次 init/finalize 支持不完善——内存泄漏和全局状态残留很常见。若需要此功能，考虑使用子进程隔离。

> [!question] 判断题 5
> Python 内嵌方式比 subprocess 方式性能更高，因为避免了进程创建和数据序列化开销。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: 内嵌方式在同一个进程内调用 Python API，数据传递是通过 C 指针和 Python 对象引用，零序列化开销。subprocess 需要启动新进程 + 序列化数据通过管道传输。

---


---

## 力扣练习

以下题目用于验证本章所学内容：

| 题号 | 题目 | 链接 | 涉及知识点 |
|------|------|------|-----------|
| — | 本章无对应力扣题 | — | 请用动手练习题自检 |



### 动手练习题

> [!example] 练习题 1：最简单的内嵌
> **难度**: 简单
>
> 编写一个 C 程序，内嵌 Python 解释器并：
> 1. 初始化解释器
> 2. 执行 `print("Hello Embedded Python!")`
> 3. 用 `PyRun_SimpleString` 执行循环计算 1 到 100 的和
> 4. 将结果提取到 C 中并用 `printf` 输出
>
> 编译并运行，确保链接正确。

> [!example] 练习题 2：C 调用 Python 数据处理
> **难度**: 简单
>
> C 程序中有一个 C 数组 `double data[1000]`，通过内嵌 Python 实现：
> 1. 将 C 数组转为 Python 的 `list`（用 `PyList_New` + `PyList_SetItem`）
> 2. 调用 `statistics.mean()` 和 `statistics.stdev()` 计算统计值
> 3. 将结果提取回 C 并打印
>
> 与纯 C 实现对比代码量。

> [!example] 练习题 3：Python 配置驱动
> **难度**: 简单
>
> 实现一个配置驱动的 C 服务器（简化版）：
> 1. Python 配置文件 `config.py` 定义端口、超时等参数
> 2. C 程序启动时读取配置并打印
> 3. 支持通过 SIGUSR1 信号重新加载 Python 配置（热更新）
> 4. 注意：信号处理函数中操作 CPython API 需要正确的 GIL 管理

> [!example] 练习题 4：双向互操作
> **难度**: 简单
>
> 实现完整双向互操作：C 调用 Python 函数，Python 函数内又回调 C 函数：
> 1. C 注册一个 `int c_add(int a, int b)` 函数为 Python 模块
> 2. Python 脚本 `def process(a, b): return c_add(a, b) * 2`
> 3. C 调用 `process(10, 20)` 获得 `60`
>
> 理解 C 扩展函数在 Python 中的注册流程（`PyModuleDef` + `PyMethodDef`），以及它是如何和 C 内嵌代码共存于同一进程的。
