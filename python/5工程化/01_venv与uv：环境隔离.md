# venv 与 uv：环境隔离 (Virtual Environments)
---

## 📖 章节概述

C 语言的世界里，库文件（`.so`、`.a`）安装在系统路径（`/usr/lib`、`/usr/local/lib`），所有项目共享同一份库。Python 的世界截然不同——每个项目可能需要不同版本的 Django、NumPy 或 requests。如果所有项目共享同一个 Python 环境的 site-packages，版本冲突会像多米诺骨牌一样让所有项目崩溃。虚拟环境就是 Python 世界的"沙箱"，让每个项目拥有独立的依赖空间。

本章从 `venv` 基础操作开始，逐步引入现代工具 `uv`（Rust 重写的 pip/pip-tools 替代品），并与 C 语言的 pkg-config、LD_LIBRARY_PATH 等机制对比，帮助 C 程序员理解 Python 的依赖隔离哲学。

> **核心理念**：C 通过链接器路径区分库版本（`LD_LIBRARY_PATH`、`rpath`），Python 通过虚拟环境复制一个完整的 Python 解释器"副本"。这不是浪费，而是工程确定性——每个项目的 Python 环境和依赖可以精确复现。

---

### 📚 第一节：为什么需要虚拟环境

在 C 项目中，依赖管理靠系统包管理器（`apt install libcurl-dev`）或用 CMake `find_package` 查找：

```bash
# C 项目：全局库，用完即走
gcc -o myapp main.c -lcurl -lssl

# 查看链接的库
ldd ./myapp
```

问题来了：如果你的项目 A 需要 `libfoo 1.0`，项目 B 需要 `libfoo 2.0`，而系统只能装一个版本——这就是"DLL Hell"在 Linux 上的表现。

Python 的解决方案是**虚拟环境**——为每个项目创建一个独立的 Python 解释器目录，包括独立的 `site-packages`：

```bash
# 系统 Python 的 site-packages
python3 -c "import site; print(site.getsitepackages())"
# → ['/usr/lib/python3.12/site-packages']

# 虚拟环境中的 site-packages
~/myproject/.venv/lib/python3.12/site-packages/
```

> 与 C 对比：`LD_LIBRARY_PATH` 只是改变运行时库搜索顺序，而虚拟环境是真正隔离的"第二个 Python 安装"。类比：`LD_LIBRARY_PATH` 像是给链接器一个"优先看这里"的便条，而虚拟环境像是把整个编译链和库复制了一份。

---

### 📚 第二节：venv 基础操作

#### 2.1 创建虚拟环境

```bash
# 标准方式：使用内置 venv 模块
python3 -m venv .venv

# 目录结构
tree -L 2 .venv
```

输出：

```
.venv/
├── bin/
│   ├── python          → 指向系统 python3 的符号链接
│   ├── pip             → 虚拟环境专属的 pip
│   ├── activate        → 激活脚本
│   └── python3
├── lib/
│   └── python3.12/
│       └── site-packages/   → 安装的包放这里
├── include/
└── pyvenv.cfg
```

#### 2.2 激活与退出

```bash
# 激活（Linux/macOS）
source .venv/bin/activate

# 激活后，提示符会显示环境名
(.venv) user@host:~/myproject$

# 验证当前使用的是虚拟环境中的 Python
which python
# → /home/user/myproject/.venv/bin/python

python -c "import sys; print(sys.prefix)"
# → /home/user/myproject/.venv

# 退出虚拟环境
deactivate
```

> `python -c "import sys; print(sys.prefix)"` 是最可靠的验证方式——如果输出是系统路径（如 `/usr`），说明不在虚拟环境中。

#### 2.3 安装与导出依赖

```bash
# 激活环境后安装包
source .venv/bin/activate
pip install requests numpy

# 导出依赖列表（锁定版本）
pip freeze > requirements.txt

# 查看 requirements.txt
cat requirements.txt
# certifi==2024.2.2
# charset-normalizer==3.3.2
# idna==3.6
# numpy==1.26.4
# requests==2.31.0
# urllib3==2.2.1
```

在另一台机器上复现环境：

```bash
# 创建并激活新环境后
pip install -r requirements.txt
```

> 与 C 对比：`requirements.txt` 有点像 C 项目的 `apt list` 或 `brew bundle`，但它锁定到了具体的版本号。CMake 的 `find_package(libfoo 1.0 REQUIRED)` 只能检查版本下限，无法精确锁定。

#### 2.4 最佳实践

```bash
# 1. 虚拟环境目录命名为 .venv（隐藏目录，不会被意外提交）
python3 -m venv .venv

# 2. 将 .venv/ 加入 .gitignore
echo '.venv/' >> .gitignore

# 3. 提交 requirements.txt，不提交 .venv/
git add requirements.txt .gitignore
git commit -m "Add Python dependencies"

# 4. 克隆后重建环境
git clone <repo>
cd <repo>
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 📝 小节练习

> [!question] 选择题 1
> `python -m venv .venv` 创建的虚拟环境中，`sys.prefix` 会指向哪里？
> - [ ] A. `/usr`
> - [ ] B. `/usr/local`
> - [ ] C. 当前目录下的 `.venv` 目录
> - [ ] D. `~/.local`
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: 激活虚拟环境后，`sys.prefix` 指向虚拟环境的根目录（如 `/path/to/project/.venv`），这正是虚拟环境隔离的核心机制。

> [!question] 选择题 2
> `pip freeze` 输出的内容包含什么？
> - [ ] A. 仅项目直接依赖的包
> - [ ] B. 当前环境中安装的所有包及其版本
> - [ ] C. 仅标准库中的包
> - [ ] D. 系统级别的 Python 包
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `pip freeze` 输出当前虚拟环境中所有已安装包（包括传递依赖）及其精确版本号，格式为 `package==version`。

---

### 📚 第三节：深入理解虚拟环境机制

#### 3.1 pyvenv.cfg 的秘密

```bash
cat .venv/pyvenv.cfg
```

```ini
home = /usr/bin
include-system-site-packages = false
version = 3.12.3
```

- `home`：基 Python 安装位置
- `include-system-site-packages = false`：不继承系统 site-packages（隔离！）
- `version`：Python 版本

#### 3.2 指定 Python 版本

```bash
# 使用特定版本的 Python 创建环境
python3.11 -m venv .venv-py311
python3.12 -m venv .venv-py312

# 不依赖系统 Python（需要先安装对应版本）
sudo apt install python3.11-venv
```

#### 3.3 环境变量对比：Python vs C

| 概念 | C 语言 | Python |
|------|--------|--------|
| 库搜索路径 | `LD_LIBRARY_PATH` | `PYTHONPATH` |
| 头文件搜索 | `C_INCLUDE_PATH` | —（无头文件概念） |
| 编译器/解释器 | `PATH` 中的 `gcc` | `PATH` 中的 `python` |
| pkg-config 路径 | `PKG_CONFIG_PATH` | — |
| site-packages | — | `sys.path` |
| 链接器 rpath | `-Wl,-rpath,...` | —（无需链接） |

```bash
# C 语言：运行时库搜索顺序
# 1. LD_LIBRARY_PATH
# 2. /etc/ld.so.cache
# 3. /lib, /usr/lib

# Python：模块搜索顺序
python -c "import sys; [print(p) for p in sys.path]"
# 1. 当前目录（或脚本目录）
# 2. PYTHONPATH 环境变量
# 3. site-packages（虚拟环境或系统）
# 4. 标准库路径
```

### 📝 小节练习

> [!question] 判断题 1
> 虚拟环境激活后，`pip install` 安装的包会放到系统 site-packages 目录。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 激活虚拟环境后，pip 会将包安装到虚拟环境的 `lib/pythonX.Y/site-packages/` 目录，与系统 site-packages 完全隔离。

---

### 📚 第四节：uv — 现代 Python 包管理器

[uv](https://github.com/astral-sh/uv) 是用 Rust 重写的 pip/pip-tools/poetry 替代品，速度比 pip 快 10-100 倍。对于习惯了 C 工具链"编译快"的读者，uv 能消除 `pip install` 等待的焦虑。

#### 4.1 安装 uv

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或通过 pip 安装
pip install uv

# 验证
uv --version
```

#### 4.2 创建虚拟环境

```bash
# 创建虚拟环境（比 python -m venv 更快）
uv venv

# 指定 Python 版本
uv venv --python 3.12

# 指定路径
uv venv .venv
```

#### 4.3 安装依赖

```bash
# uv pip install（兼容 pip 语法，但更快）
uv pip install requests numpy

# 从 requirements.txt 安装
uv pip install -r requirements.txt

# 从 pyproject.toml 安装
uv pip install -e .
```

#### 4.4 锁定依赖

```bash
# 生成锁定的依赖文件（类似 pip-tools 的 pip-compile）
uv pip compile requirements.in -o requirements.txt

# 从 pyproject.toml 生成
uv pip compile pyproject.toml -o requirements.txt

# 同步环境到锁定版本
uv pip sync requirements.txt
```

#### 4.5 uv vs pip 速度对比

```bash
# 以下命令展示速度差异（非必须执行）
time pip install django      # 约 5-10 秒
time uv pip install django   # 约 0.5-1 秒
```

> uv 快的原理：Rust 实现 + 全局缓存 + 并行下载 + 复用已解析的依赖树。这类似 C 语言中 `ccache` 对 `gcc` 的加速效果。

#### 4.6 完整工作流

```bash
# 1. 创建项目并初始化
mkdir myproject && cd myproject
uv venv
source .venv/bin/activate

# 2. 添加依赖并记录
uv pip install fastapi uvicorn
uv pip freeze > requirements.txt

# 3. 团队成员克隆后
git clone <repo>
cd <repo>
uv venv
source .venv/bin/activate
uv pip sync requirements.txt
```

### 📝 小节练习

> [!question] 选择题 1
> `uv pip compile` 的作用是什么？
> - [ ] A. 编译 Python 源码为字节码
> - [ ] B. 将松散依赖声明解析为精确版本锁定文件
> - [ ] C. 安装依赖包
> - [ ] D. 导出当前环境的依赖列表
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `uv pip compile` 读取 `requirements.in` 或 `pyproject.toml` 中的依赖声明（可包含版本范围），解析依赖树后生成精确版本锁定的 `requirements.txt`。

> [!question] 判断题 1
> uv 完全兼容 pip 的命令行语法，可以无缝替代 pip。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `uv pip install`、`uv pip freeze`、`uv pip list` 等命令与 pip 语法保持一致，可以无缝替换。

---

### 📚 第五节：C 项目中使用 Python 虚拟环境

在混合 C/Python 项目中，虚拟环境的使用有讲究：

#### 5.1 项目布局

```
myproject/
├── .venv/              ← Python 虚拟环境（不提交）
├── src/                ← C 源码
│   ├── main.c
│   └── lib.c
├── python/             ← Python 工具脚本
│   ├── build_helper.py
│   └── test_runner.py
├── CMakeLists.txt
├── Makefile
├── pyproject.toml
└── requirements.txt
```

#### 5.2 CMake 中集成 Python 虚拟环境

```cmake
# CMakeLists.txt
cmake_minimum_required(VERSION 3.18)
project(MyHybridProject C)

# 查找 Python（优先使用虚拟环境中的）
find_package(Python3 COMPONENTS Interpreter)

# 使用 Python 脚本生成代码
add_custom_command(
    OUTPUT generated_config.h
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/python/generate_config.py
        --input config.json
        --output generated_config.h
    DEPENDS python/generate_config.py config.json
)
```

#### 5.3 Makefile 中集成

```makefile
# Makefile 片段
VENV = .venv
PYTHON = $(VENV)/bin/python

.PHONY: venv test

venv:
	uv venv $(VENV)
	$(VENV)/bin/uv pip install -r requirements.txt

test: venv
	$(PYTHON) -m pytest python/tests/
```

> 这个模式在 C 项目中很常见：用 Python 做代码生成（替代部分 awk/sed/m4），用 C 做核心逻辑。虚拟环境确保生成脚本的依赖不会污染系统。

### 📝 小节练习

> [!question] 选择题 1
> 在 CMake 的 `add_custom_command` 中执行 Python 脚本时，推荐使用 `${Python3_EXECUTABLE}` 而非硬编码 `python3`，原因是？
> - [ ] A. 性能更好
> - [ ] B. 自动找到虚拟环境中的 Python
> - [ ] C. 跨平台兼容性
> - [ ] D. 以上都是
>
> > [!success]- 点击查看答案
> > 正确答案: D
> > **解析**: `${Python3_EXECUTABLE}` 由 `find_package(Python3)` 设置，能自动找到虚拟环境中的 Python、在 Windows 上找 `python.exe`、在激活虚拟环境时指向正确的解释器，同时保证跨平台兼容。

---

## 📋 章节测试

### 一、判断题

> [!question] 判断题 1
> 虚拟环境是一个完整的 Python 安装副本，不依赖任何系统 Python 文件。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 虚拟环境通过符号链接（或复制少量文件）引用系统 Python 解释器，并非完整副本。它只复制了 pip、activate 脚本和空的 site-packages 目录。

> [!question] 判断题 2
> `deactivate` 命令会删除虚拟环境。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `deactivate` 仅退出当前虚拟环境，恢复到系统 Python。虚拟环境目录保留不变，可以再次 `source .venv/bin/activate` 激活。

> [!question] 判断题 3
> `requirements.txt` 和虚拟环境目录 `.venv/` 都应该提交到 Git 仓库。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `requirements.txt` 应提交（它是依赖清单），`.venv/` 不应提交（它包含平台相关的二进制文件，其他开发者应自己创建虚拟环境）。

> [!question] 判断题 4
> uv 是用 Python 实现的包管理器工具。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: uv 是用 Rust 编写的，正是 Rust 的高性能特性让 uv 比 pip 快 10-100 倍。

> [!question] 判断题 5
> 在虚拟环境激活状态下执行 `pip install`，包会安装到系统的 `/usr/lib/python3*/site-packages/`。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 激活虚拟环境后，pip 将包安装到虚拟环境的 `lib/pythonX.Y/site-packages/` 中，与系统完全隔离。

> [!question] 判断题 6
> `LD_LIBRARY_PATH` 的作用与 Python 虚拟环境完全等价。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `LD_LIBRARY_PATH` 仅改变运行时库搜索的优先级，不提供版本隔离。虚拟环境则提供完整的环境隔离，包括 pip、Python 解释器路径、site-packages。

### 二、选择题

> [!question] 选择题 1
> 以下哪个不是虚拟环境的正确创建方式？
> - [ ] A. `python3 -m venv .venv`
> - [ ] B. `uv venv`
> - [ ] C. `virtualenv .venv`
> - [ ] D. `pip install venv .venv`
>
> > [!success]- 点击查看答案
> > 正确答案: D
> > **解析**: `pip install` 用于安装 Python 包，不能创建虚拟环境。正确方式是 `python -m venv`、`uv venv` 或 `virtualenv`。

> [!question] 选择题 2
> 验证当前是否在虚拟环境中的最佳命令是？
> - [ ] A. `echo $PATH`
> - [ ] B. `which python`
> - [ ] C. `python -c "import sys; print(sys.prefix)"`
> - [ ] D. `pip list`
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: `sys.prefix` 直接显示 Python 安装路径，若输出不是系统路径（如 `/usr`），则当前处于虚拟环境中。`which python` 也能判断，但不如 `sys.prefix` 可靠。

> [!question] 选择题 3
> `pyvenv.cfg` 中 `include-system-site-packages = false` 的含义是？
> - [ ] A. 禁用 pip
> - [ ] B. 不继承系统安装的 Python 包
> - [ ] C. 不能安装任何包
> - [ ] D. 使用系统 Python 解释器
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 此设置确保虚拟环境中的 `sys.path` 不包含系统 site-packages 路径，实现真正的包隔离。

> [!question] 选择题 4
> `uv pip sync requirements.txt` 与 `pip install -r requirements.txt` 的关键区别是？
> - [ ] A. 没有区别
> - [ ] B. sync 会卸载不在 requirements.txt 中的包
> - [ ] C. sync 更快
> - [ ] D. sync 只安装新包
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `uv pip sync` 使环境与 requirements.txt **精确同步**——安装缺失的包、升级版本不同的包、卸载文件未列出的包。`pip install -r` 只安装/升级，不卸载。

> [!question] 选择题 5
> 在 CMake 项目中，`find_package(Python3 COMPONENTS Interpreter)` 设置的最关键变量是？
> - [ ] A. `PYTHON3_VERSION`
> - [ ] B. `Python3_EXECUTABLE`
> - [ ] C. `PYTHON3_INCLUDE_DIR`
> - [ ] D. `Python3_LIBRARIES`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `Python3_EXECUTABLE` 指向 Python 解释器路径，在 `add_custom_command` 中用于执行脚本。`COMPONENTS Interpreter` 仅查找解释器，不查找 Development 组件（头文件和库）。

> [!question] 选择题 6
> 以下关于 `sys.path` 的说法正确的是？
> - [ ] A. `sys.path` 是只读的，不可修改
> - [ ] B. `sys.path` 的第一个元素总是当前脚本所在目录
> - [ ] C. `sys.path` 中不含标准库路径
> - [ ] D. `sys.path` 只在模块导入时使用
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `sys.path` 的第一个元素是当前脚本所在目录（或交互模式下的空字符串表示当前目录），之后才是 `PYTHONPATH`、site-packages、标准库路径。`sys.path` 可以在运行时动态修改。

> [!question] 选择题 7
> 使用 uv 创建虚拟环境时，指定 Python 3.12 的正确命令是？
> - [ ] A. `uv venv --version 3.12`
> - [ ] B. `uv venv --python 3.12`
> - [ ] C. `uv venv -p 3.12`
> - [ ] D. `uv venv --py 3.12`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `uv venv --python 3.12` 是正确语法。`uv` 会自动搜索系统中可用的 Python 3.12 解释器，若未找到则报错。

---

### 🛠️ 动手练习题

> [!example] 练习题 1：虚拟环境全生命周期
> **难度**: ⭐
>
> 完成以下操作序列并记录每一步的输出：
> 1. 创建项目目录 `venv-lab/`，用 `python -m venv .venv` 创建虚拟环境
> 2. 激活前后分别运行 `python -c "import sys; print(sys.prefix)"`，对比输出
> 3. 在虚拟环境中安装 `requests`，用 `pip show requests` 查看安装位置
> 4. 用 `pip freeze > requirements.txt` 导出依赖
> 5. 删除 `.venv/`，用 `requirements.txt` 重建环境
> 6. 验证重建后 `requests` 仍然可用

> [!example] 练习题 2：uv 速度对比
> **难度**: ⭐
>
> 1. 分别用 `time pip install numpy pandas matplotlib` 和 `time uv pip install numpy pandas matplotlib` 安装同一组包，记录时间
> 2. 用 `uv pip compile pyproject.toml -o requirements.txt` 创建一个锁定文件
> 3. 阅读锁定文件，找出每个包的精确版本和其依赖树

> [!example] 练习题 3：混合项目中的虚拟环境
> **难度**: ⭐⭐
>
> 创建一个包含 C 代码和 Python 测试脚本的混合项目：
> 1. `src/main.c` — 计算斐波那契数列的 C 程序
> 2. `test/test_fib.py` — 用 `subprocess` 运行 C 程序并验证输出的 pytest 测试
> 3. 编写 Makefile，包含 `venv` 目标和 `test` 目标：
>    - `make venv` 创建虚拟环境并安装 pytest
>    - `make test` 编译 C 程序 + 在虚拟环境中运行 pytest
> 4. 将 `.venv/` 加入 `.gitignore`，`requirements.txt` 提交到 Git

> [!example] 练习题 4：理解 sys.path 与隔离机制
> **难度**: ⭐⭐
>
> 1. 分别在系统 Python 和虚拟环境中运行以下代码，对比 `sys.path` 的差异：
>    ```python
>    import sys
>    import pprint
>    pprint.pprint(sys.path)
>    ```
> 2. 修改 `pyvenv.cfg`，将 `include-system-site-packages` 设为 `true`，重新激活后再次打印 `sys.path`，观察变化
> 3. 解释为什么虚拟环境能隔离依赖——从 `sys.path` 的角度论证
