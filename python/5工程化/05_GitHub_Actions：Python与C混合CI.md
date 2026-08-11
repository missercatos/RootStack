# GitHub Actions：Python 与 C 混合 CI (CI with GitHub Actions)
---

## 📖 章节概述

C 语言项目传统的 CI 流程是：`git push` → CI 服务器拉取代码 → `cmake -B build && cmake --build build` → `ctest` → 生成报告。Python 项目有自己的 CI 模式：安装依赖、运行 lint、运行测试。当你的项目同时包含 C 和 Python 代码时（这在工程实践中很常见——C 是核心引擎，Python 是测试/构建/胶水层），CI 工作流需要同时处理两种语言的编译和测试。

本章从一个最小化的混合项目 CI 开始，逐步展示矩阵构建（多 Python 版本 × 多操作系统）、缓存优化、编译器选择和 C/Python 联合测试的完整 GitHub Actions 工作流。

> **核心理念**：GitHub Actions 的 `.github/workflows/ci.yml` 之于项目，如同 Makefile 之于源代码——它定义了"如何验证这个项目是正确的"。区别在于 Makefile 运行在本地，Actions 运行在云端，每次 `git push` 自动触发，确保所有平台和配置下代码都能正确编译和运行。

---

### 📚 第一节：GitHub Actions 基础

#### 1.1 最小化 Python CI

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests
        run: pytest -v
```

> 与 C 对比：C 项目的 CI 需要安装编译器（`sudo apt install gcc`）、运行 cmake、make，然后 ctest。Python 项目的 CI 更简单——没有编译步骤，直接安装依赖即可测试。但当项目中同时有 C 代码时，两者的 CI 需要融合。

#### 1.2 矩阵构建

```yaml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        python-version: ["3.9", "3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests
        run: pytest -v
```

这个矩阵生成 2 × 4 = 8 个并行任务，每个任务使用不同的 OS 和 Python 版本组合。runner 上的 Python 环境是完全隔离的——类似 8 个独立的虚拟环境。

### 📝 小节练习

> [!question] 选择题 1
> GitHub Actions 中 `${{ matrix.python-version }}` 的值来自哪里？
> - [ ] A. 环境变量
> - [ ] B. `strategy.matrix` 定义
> - [ ] C. GitHub 仓库设置
> - [ ] D. 系统自动检测
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `strategy.matrix` 块定义构建矩阵的维度，`${{ matrix.python-version }}` 引用当前维度的值。GitHub Actions 会为每个矩阵组合创建独立的 job。

---

### 📚 第二节：Python + C 混合项目 CI

#### 2.1 最小混合 CI

```yaml
name: CI

on: [push, pull_request]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # --- C 工具链 ---
      - name: Install C build tools
        run: |
          sudo apt-get update
          sudo apt-get install -y gcc gdb cmake

      # --- Python 工具链 ---
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install Python dependencies
        run: pip install pytest

      # --- 构建 C 代码 ---
      - name: Build C program
        run: |
          gcc -Wall -Wextra -g -O0 -o build/program src/main.c

      # --- 测试 C 程序（通过 Python） ---
      - name: Test C program via pytest
        run: pytest tests/ -v
```

#### 2.2 完整的混合项目 CI 工作流

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  PYTHONUNBUFFERED: "1"

jobs:
  # ==================== Python 质量检查 ====================
  python-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install lint tools
        run: pip install ruff mypy

      - name: Lint (ruff)
        run: ruff check src/ tests/

      - name: Format check (ruff)
        run: ruff format --check src/ tests/

      - name: Type check (mypy)
        run: mypy --strict src/

  # ==================== C + Python 联合测试 ====================
  hybrid-test:
    needs: python-lint  # lint 通过后才运行
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        python-version: ["3.9", "3.12"]
        build-type: [Debug, Release]

    steps:
      - uses: actions/checkout@v4

      # --- 安装 C 编译器 ---
      - name: Install C toolchain (Ubuntu)
        if: runner.os == 'Linux'
        run: |
          sudo apt-get update
          sudo apt-get install -y gcc g++ gdb cmake valgrind

      - name: Install C toolchain (macOS)
        if: runner.os == 'macOS'
        run: |
          brew install gcc cmake

      # --- 安装 Python ---
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'

      - name: Install Python deps
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt

      # --- 构建 C 代码 ---
      - name: Build C code
        run: |
          mkdir -p build
          cd build
          cmake .. \
            -DCMAKE_BUILD_TYPE=${{ matrix.build-type }} \
            -DCMAKE_C_FLAGS="-Wall -Wextra"
          cmake --build . --parallel $(nproc 2>/dev/null || sysctl -n hw.ncpu)

      # --- 运行测试 ---
      - name: Run Python tests
        run: pytest tests/ -v --tb=short

      - name: Run C tests (CTest)
        run: |
          cd build
          ctest --output-on-failure

      # --- 内存检查（仅 Debug + Ubuntu） ---
      - name: Memory check with Valgrind
        if: matrix.build-type == 'Debug' && runner.os == 'Linux'
        run: |
          valgrind --leak-check=full --error-exitcode=1 ./build/myprogram
```

### 📝 小节练习

> [!question] 选择题 1
> 混合 CI 工作流中，`needs: python-lint` 的作用是什么？
> - [ ] A. 等待 lint job 完成后才开始运行
> - [ ] B. lint 失败时跳过后续 job
> - [ ] C. 两个 job 共享同一个 runner
> - [ ] D. A 和 B 都正确
>
> > [!success]- 点击查看答案
> > 正确答案: D
> > **解析**: `needs` 定义 job 间的依赖关系。`hybrid-test` 在 `python-lint` 完成后才开始（A），如果 lint 失败则 hybrid-test 被跳过（B）。这节省了 CI 资源。

---

### 📚 第三节：缓存与速度优化

#### 3.1 pip 缓存

```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: "3.12"
    cache: 'pip'                          # 自动缓存 pip
    cache-dependency-path: |
      requirements.txt
      requirements-dev.txt
```

`setup-python` 内置的 `cache: 'pip'` 自动缓存 `~/.cache/pip` 目录，后续运行无需重复下载包。

#### 3.2 uv 缓存（更快）

```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v3

- name: Install Python deps (uv)
  run: uv pip sync requirements-dev.txt --system
```

uv 自带全局缓存，比 pip 的缓存更高效。

#### 3.3 C 编译缓存（ccache）

```yaml
- name: Setup ccache
  uses: hendrikmuhs/ccache-action@v1
  with:
    key: ${{ matrix.os }}-${{ matrix.build-type }}
    max-size: 200M

- name: Build C code
  run: |
    cd build
    cmake .. -DCMAKE_C_COMPILER_LAUNCHER=ccache
    cmake --build .
```

> ccache 对 C 项目的加速效果类似于 uv 缓存对 Python 的加速——避免重复编译未修改的 `.c` 文件。

#### 3.4 完整缓存策略对比

| 缓存目标 | Python 方法 | C 方法 |
|---------|-------------|--------|
| 依赖包 | `cache: 'pip'` 或 uv 全局缓存 | ccache |
| 构建产物 | `actions/cache` 缓存 `.venv/` | `actions/cache` 缓存 `build/` |
| 系统包 | apt 缓存 | apt 缓存 |

### 📝 小节练习

> [!question] 选择题 1
> `actions/setup-python@v5` 的 `cache: 'pip'` 选项缓存的是什么？
> - [ ] A. 虚拟环境目录
> - [ ] B. pip 下载的包缓存（`~/.cache/pip`）
> - [ ] C. Python 解释器本身
> - [ ] D. 测试输出
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `cache: 'pip'` 自动缓存 pip 的下载缓存目录，避免每次 CI 运行都从 PyPI 下载包。它基于 `requirements.txt` 的哈希值决定是否恢复缓存。

---

### 📚 第四节：矩阵构建策略

#### 4.1 多维度矩阵

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
    python-version: ["3.9", "3.10", "3.11", "3.12"]
    compiler: [gcc, clang]
    exclude:
      # macOS 上不测试 gcc（macOS gcc 实际是 clang）
      - os: macos-latest
        compiler: gcc
      # Windows 上只测最新 Python
      - os: windows-latest
        python-version: "3.9"
      - os: windows-latest
        python-version: "3.10"
      - os: windows-latest
        python-version: "3.11"
```

> **重要**：3 × 4 × 2 = 24 个组合，减去 4 个 exclusion = 20 个并行 job。GitHub 免费计划限制 20 个并发 job，合理设计矩阵避免浪费资源。

#### 4.2 fail-fast 策略

```yaml
strategy:
  fail-fast: false  # 一个 job 失败不取消其他 job
  matrix:
    ...
```

默认 `fail-fast: true` 会在任意 job 失败时取消其他正在运行的 job。对于混合项目，建议设为 `false`——C 构建在 macOS 上失败不应阻止 Linux 上的测试完成。

### 📝 小节练习

> [!question] 判断题 1
> `fail-fast: true` 表示如果有 job 失败，立即取消所有正在运行的 job。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `fail-fast: true`（默认行为）会在矩阵中任意 job 失败时取消其他仍在运行的 job。设为 `false` 可以让所有 job 独立完成，便于全面了解哪些平台/配置有问题。

---

### 📚 第五节：C/Python 联合测试的 CI 实现

#### 5.1 项目结构

```
hybrid-project/
├── .github/
│   └── workflows/
│       └── ci.yml
├── src/
│   ├── mathlib.h
│   └── mathlib.c
├── python/
│   └── math_test.py         # 用 ctypes 测试 mathlib
├── tests/
│   ├── conftest.py
│   ├── test_cli.py          # 用 subprocess 测试可执行文件
│   └── test_mathlib.py      # 用 ctypes 测试 .so
├── CMakeLists.txt
├── pyproject.toml
├── requirements-dev.txt
└── Makefile
```

#### 5.2 conftest.py — 在 CI 中编译 C 库

```python
# tests/conftest.py
import subprocess
import pytest
import sys
import os

@pytest.fixture(scope="session")
def compiled_shared_lib():
    """在 CI 中使用 CMake 编译 C 共享库"""
    build_dir = "build"
    os.makedirs(build_dir, exist_ok=True)

    # CMake 配置
    result = subprocess.run(
        ["cmake", "..", "-DCMAKE_BUILD_TYPE=Release"],
        cwd=build_dir, capture_output=True, text=True
    )
    if result.returncode != 0:
        pytest.fail(f"CMake configure failed:\n{result.stderr}")

    # 构建
    result = subprocess.run(
        ["cmake", "--build", ".", "--parallel"],
        cwd=build_dir, capture_output=True, text=True
    )
    if result.returncode != 0:
        pytest.fail(f"Build failed:\n{result.stderr}")

    # 返回 .so 路径
    ext = ".dylib" if sys.platform == "darwin" else ".so"
    return os.path.join(build_dir, f"libmathlib{ext}")

@pytest.fixture
def mathlib(compiled_shared_lib):
    import ctypes
    lib = ctypes.CDLL(compiled_shared_lib)
    lib.add.argtypes = [ctypes.c_int, ctypes.c_int]
    lib.add.restype = ctypes.c_int
    return lib
```

#### 5.3 最终的 CI 工作流

```yaml
# .github/workflows/ci.yml
name: C + Python Hybrid CI

on:
  push:
    branches: [main]
  pull_request:

env:
  PYTHONUNBUFFERED: "1"
  CTEST_OUTPUT_ON_FAILURE: "1"

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.12"}
      - run: pip install ruff mypy
      - run: ruff check python/ tests/
      - run: ruff format --check python/ tests/
      - run: mypy python/ --ignore-missing-imports

  test:
    needs: lint
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest]
        python-version: ["3.9", "3.12"]
        build-type: [Debug, Release]

    steps:
      - uses: actions/checkout@v4

      - name: Install C tools (Linux)
        if: runner.os == 'Linux'
        run: sudo apt-get update && sudo apt-get install -y gcc cmake valgrind

      - name: Install C tools (macOS)
        if: runner.os == 'macOS'
        run: brew install cmake

      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install Python deps
        run: |
          pip install --upgrade pip
          pip install pytest

      - name: Build and test
        run: |
          mkdir -p build && cd build
          cmake .. -DCMAKE_BUILD_TYPE=${{ matrix.build-type }}
          cmake --build . --parallel
          ctest --output-on-failure

      - name: Python integration tests
        run: pytest tests/ -v

      - name: Valgrind memory check (Linux Debug only)
        if: matrix.build-type == 'Debug' && runner.os == 'Linux'
        run: valgrind --leak-check=full ./build/myprogram
```

> 这个工作流在每次 push 和 PR 时检查：C 代码能否编译、Python 测试能否通过、是否存在内存泄漏——覆盖了混合项目的完整质量维度。

### 📝 小节练习

> [!question] 选择题 1
> 在 CI 中编译 C 共享库用于 Python ctypes 测试时，库文件扩展名在 macOS 上是？
> - [ ] A. `.so`
> - [ ] B. `.dylib`
> - [ ] C. `.dll`
> - [ ] D. `.a`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: macOS 上共享库扩展名是 `.dylib`（Linux 是 `.so`，Windows 是 `.dll`）。CI 中需根据 `sys.platform` 判断。

---

## 📋 章节测试

### 一、判断题

> [!question] 判断题 1
> GitHub Actions 的 `runs-on: ubuntu-latest` 提供一个虚拟机，用户可以在上面安装任意软件。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: GitHub Actions runner 是完整的虚拟机（Linux/macOS/Windows），用户拥有 sudo 权限，可安装 GCC、Clang、Valgrind 等任意软件。

> [!question] 判断题 2
> `strategy.matrix` 中定义的每个维度组合会生成独立的 job，在独立的 runner 上并行运行。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: 每个矩阵组合在独立的 runner 上运行，彼此环境完全隔离。这是 GitHub Actions 实现多平台多版本测试的核心机制。

> [!question] 判断题 3
> GitHub Actions 的免费计划允许无限量的 job 并行运行。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: GitHub 免费计划限制最多 20 个并发 job。超出限制的 job 会排队等待。设计矩阵时需考虑此限制。

> [!question] 判断题 4
> `actions/setup-python@v5` 的 `cache: 'pip'` 会缓存虚拟环境中的所有已安装包。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `cache: 'pip'` 只缓存 pip 的下载缓存（`~/.cache/pip`），使后续安装不需要重新下载。它不缓存已安装的包（site-packages 内容）。

> [!question] 判断题 5
> 在混合项目 CI 中，C 编译和 Python 测试不能在同一 job 中执行。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 同一 job 中完全可以在安装 C 编译器后编译 C 代码，然后安装 Python 依赖并运行 pytest——job 内各 step 共享同一文件系统和环境。

> [!question] 判断题 6
> `needs` 关键字定义的 job 依赖关系是：如果被依赖的 job 失败，依赖它的 job 不会被跳过。 （ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 如果 `needs` 指向的 job 失败或跳过，依赖它的 job 也会被跳过。这是 CI 的快速失败机制——如果 lint 失败，测试 job 不必运行。

### 二、选择题

> [!question] 选择题 1
> 以下哪个 GitHub Actions 触发器表示"仅在 PR 合并到 main 后"运行？
> - [ ] A. `on: push`
> - [ ] B. `on: pull_request`
> - [ ] C. `on: workflow_dispatch`
> - [ ] D. 以上都不是
>
> > [!success]- 点击查看答案
> > 正确答案: D
> > **解析**: `on: push` 在 push 时触发，`on: pull_request` 在 PR 的每次更新时触发。已有 `push` 到 main 的触发，无需单独的"合并后"触发器。

> [!question] 选择题 2
> `ctest --output-on-failure` 的作用是？
> - [ ] A. 仅输出失败的测试
> - [ ] B. 在测试失败时打印详细输出
> - [ ] C. 失败时自动重试
> - [ ] D. 生成 XML 报告
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `--output-on-failure` 在测试失败时才输出 stdout/stderr，成功时静默。这减少了 CI 日志的噪音，同时保留了失败时的调试信息。

> [!question] 选择题 3
> `env: CTEST_OUTPUT_ON_FAILURE: "1"` 放在 CI 工作流顶部的作用是？
> - [ ] A. 仅为当前 job 设置环境变量
> - [ ] B. 为所有 job 和 step 设置环境变量
> - [ ] C. 仅设置编译时的宏定义
> - [ ] D. 以上都不对
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 顶层 `env` 为工作流中所有 job 和 step 设置环境变量。job 级别的 `env` 会覆盖顶层，step 级别的 `env` 会覆盖 job 级别。

> [!question] 选择题 4
> GitHub Actions 中 `${{ }}` 表达式语法的作用是？
> - [ ] A. 注释
> - [ ] B. 访问上下文和变量
> - [ ] C. 定义环境变量
> - [ ] D. 导入外部模块
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `${{ }}` 是 GitHub Actions 的表达式语法，用于访问上下文（如 `${{ matrix.os }}`、`${{ github.ref }}`）和执行函数（如 `${{ runner.os == 'Linux' }}`）。

> [!question] 选择题 5
> 在矩阵构建中，`exclude` 的作用是？
> - [ ] A. 跳过某些版本组合
> - [ ] B. 删除失败的 job
> - [ ] C. 排除缓存
> - [ ] D. 排除依赖
>
> > [!success]- 点击查看答案
> > 正确答案: A
> > **解析**: `exclude` 用于从矩阵组合中排除不需要的特定组合（如 macOS 上排除 gcc），避免浪费 CI 资源在不合理的构建配置上。

> [!question] 选择题 6
> `actions/checkout@v4` 的作用是？
> - [ ] A. 创建项目的 Git 分支
> - [ ] B. 将仓库代码下载到 runner
> - [ ] C. 验证 commit 签名
> - [ ] D. 检查 GitHub token 有效性
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `actions/checkout` 是每个 CI 工作流的第一个 step，将仓库代码 clone 到 runner 的工作目录中。`@v4` 指定 action 的版本。

---

### 🛠️ 动手练习题

> [!example] 练习题 1：为纯 Python 项目创建 CI
> **难度**: ⭐
>
> 1. 创建一个简单的 Python 项目（含 `src/`、`tests/`、`pyproject.toml`）
> 2. 编写 `.github/workflows/ci.yml`：
>    - Python 3.9 ~ 3.12 矩阵构建
>    - ruff lint + format 检查
>    - mypy 类型检查
>    - pytest 测试运行
> 3. Push 到 GitHub，观察 CI 运行结果

> [!example] 练习题 2：为 C 项目创建 pytest CI
> **难度**: ⭐⭐
>
> 1. 有一个 C 项目（含 `src/`、`CMakeLists.txt`），其中 `tests/` 目录是用 pytest + subprocess 编写的测试
> 2. 编写 CI 工作流：
>    - 安装 gcc 和 cmake
>    - 用 CMake 构建 C 代码
>    - 运行 pytest 测试（测试中调用编译好的 C 程序）
> 3. 添加矩阵：Linux/macOS，gcc/clang

> [!example] 练习题 3：混合项目 CI + 缓存优化
> **难度**: ⭐⭐⭐
>
> 为混合 C/Python 项目编写完整的 CI 工作流：
> 1. lint job（ruff + mypy + clang-format）
> 2. test job 矩阵（OS × Python 版本 × Debug/Release）
> 3. 使用 `cache: 'pip'` 缓存 Python 依赖
> 4. 使用 `ccache` 缓存 C 编译
> 5. 添加 Valgrind 检查（仅 Linux Debug）
> 6. 配置 `fail-fast: false`

> [!example] 练习题 4：CI 产物上传
> **难度**: ⭐⭐
>
> 在 test job 之后添加一个 build job：
> 1. 构建 Release 版本的 `.so` 和 wheel
> 2. 使用 `actions/upload-artifact` 上传构建产物
> 3. 添加一个 deploy job：在有 tag 推送时，使用 `actions/download-artifact` 获取产物并发布到 GitHub Release
> 4. 参考：[[../c语言教程/2深化/06_编译链接与ELF|C 编译链接]]
