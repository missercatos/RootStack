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

---

## 力扣练习

以下题目用于验证本章所学内容：

| 题号 | 题目 | 链接 | 涉及知识点 |
|------|------|------|-----------|
| — | 本章无对应力扣题 | — | 请用动手练习题自检 |
