# 用bash封装C工具链 | Wrapping C Toolchains with Bash

## 章节概述

本章讲解如何用 Bash 脚本封装 C 开发工具链，涵盖自动编译脚本、测试框架封装、性能对比脚本、批量编译管理，以及 CMake/Makefile 的 Bash 封装方案。Bash 封装能大幅简化 C 项目的构建、测试和部署流程。

> **核心理念**：C 负责性能，Bash 负责流程。让 Bash 成为 C 工具链的"指挥官"，统一管理编译、测试、部署的全流程。

---

## 第1节：自动编译脚本

### 基础自动编译

```bash
#!/usr/bin/env bash
set -euo pipefail

# 自动编译脚本
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="${SCRIPT_DIR}/src"
BIN_DIR="${SCRIPT_DIR}/bin"
BUILD_DIR="${SCRIPT_DIR}/build"

# 创建目录
mkdir -p "${BIN_DIR}" "${BUILD_DIR}"

# 编译单个文件
compile_file() {
  local src="${1}"
  local obj="${2}"

  if [ "${src}" -ot "${obj}" ] 2>/dev/null; then
    return 0
  fi

  echo "Compiling: ${src}"
  gcc -Wall -O2 -c -o "${obj}" "${src}"
}

# 链接程序
link_program() {
  local objs=("$@")
  local output="${BIN_DIR}/$(basename "${objs[0]}" .o)"

  echo "Linking: ${output}"
  gcc -o "${output}" "${objs[@]}"
  echo "Built: ${output}"
}

# 编译所有源文件
build_all() {
  local sources=("${SRC_DIR}"/*.c)
  local objs=()

  for src in "${sources[@]}"; do
    local obj="${BUILD_DIR}/$(basename "${src}" .c).o"
    compile_file "${src}" "${obj}"
    objs+=("${obj}")
  done

  link_program "${objs[@]}"
}

build_all
```

### 增量编译脚本

```bash
#!/usr/bin/env bash
set -euo pipefail

# 智能增量编译
needs_rebuild() {
  local src="${1}"
  local bin="${2}"

  [ ! -f "${bin}" ] && return 0
  [ "${src}" -nt "${bin}" ] && return 0
  return 1
}

# 自动检测依赖变化
check_header_deps() {
  local src="${1}"
  local deps=()

  # 提取 #include 的头文件
  while IFS= read -r header; do
    local dep_file
    dep_file=$(find /usr/include "${SRC_DIR}" -name "${header}" 2>/dev/null | head -1)
    [ -n "${dep_file}" ] && deps+=("${dep_file}")
  done < <(grep -oE '#include [<"](.+)[>"]' "${src}" | cut -d'"' -f2 | cut -d'>' -f1)

  echo "${deps[@]}"
}

# 智能编译
smart_build() {
  local src="${1}"
  local bin="${2}"

  # 检查源文件是否需要重新编译
  if needs_rebuild "${src}" "${bin}"; then
    echo "Rebuilding: ${src}"
    gcc -Wall -O2 -o "${bin}" "${src}"
    return 0
  fi

  # 检查头文件依赖
  local headers
  headers=$(check_header_deps "${src}")
  for header in ${headers}; do
    if [ "${header}" -nt "${bin}" ] 2>/dev/null; then
      echo "Rebuilding (header changed): ${src}"
      gcc -Wall -O2 -o "${bin}" "${src}"
      return 0
    fi
  done

  echo "Up to date: ${bin}"
}
```

---

## 第2节：测试框架封装

### 单元测试框架

```bash
#!/usr/bin/env bash
set -euo pipefail

# 测试框架
TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/tests"
BIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/bin"

# 测试计数器
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# 测试函数
run_test() {
  local name="${1}"
  local command="${2}"
  local expected="${3}"

  TESTS_RUN=$((TESTS_RUN + 1))

  local actual
  actual=$(eval "${command}" 2>&1)
  local exit_code=$?

  if [ "${exit_code}" -eq 0 ] && [ "${actual}" = "${expected}" ]; then
    TESTS_PASSED=$((TESTS_PASSED + 1))
    echo "PASS: ${name}"
  else
    TESTS_FAILED=$((TESTS_FAILED + 1))
    echo "FAIL: ${name}"
    echo "  Expected: ${expected}"
    echo "  Actual:   ${actual}"
    echo "  Exit:     ${exit_code}"
  fi
}

# 测试退出码
run_test_exit() {
  local name="${1}"
  local command="${2}"
  local expected_exit="${3}"

  TESTS_RUN=$((TESTS_RUN + 1))

  eval "${command}" >/dev/null 2>&1
  local actual_exit=$?

  if [ "${actual_exit}" -eq "${expected_exit}" ]; then
    TESTS_PASSED=$((TESTS_PASSED + 1))
    echo "PASS: ${name}"
  else
    TESTS_FAILED=$((TESTS_FAILED + 1))
    echo "FAIL: ${name}"
    echo "  Expected exit: ${expected_exit}"
    echo "  Actual exit:   ${actual_exit}"
  fi
}

# 测试结果汇总
print_results() {
  echo ""
  echo "========================================="
  echo "Tests run:    ${TESTS_RUN}"
  echo "Passed:       ${TESTS_PASSED}"
  echo "Failed:       ${TESTS_FAILED}"
  echo "========================================="

  if [ "${TESTS_FAILED}" -gt 0 ]; then
    return 1
  fi
  return 0
}

# 运行测试
test_basic() {
  echo "Running basic tests..."
  run_test "echo works" "echo hello" "hello"
  run_test "math works" "echo \$((2 + 2))" "4"
  run_test_exit "exit code 0" "true" 0
  run_test_exit "exit code 1" "false" 1
}

test_program() {
  echo "Running program tests..."
  run_test "program help" "${BIN_DIR}/myprogram --help" "Usage: myprogram"
  run_test "program version" "${BIN_DIR}/myprogram --version" "1.0.0"
}

# 主函数
main() {
  test_basic
  test_program
  print_results
}

main "$@"
```

### 测试文件组织

```bash
# tests/test_math.c
#include <assert.h>
#include "math.h"

void test_add() {
    assert(add(2, 3) == 5);
}

void test_multiply() {
    assert(multiply(2, 3) == 6);
}

int main() {
    test_add();
    test_multiply();
    printf("All tests passed!\n");
    return 0;
}
```

```bash
# 编译并运行测试
gcc -o test_math tests/test_math.c src/math.c
./test_math
```

---

## 第3节：性能对比脚本

### 基准测试框架

```bash
#!/usr/bin/env bash
set -euo pipefail

# 性能测试框架
benchmark() {
  local name="${1}"
  local command="${2}"
  local iterations="${3:-100}"

  echo "Benchmarking: ${name}"
  echo "Iterations: ${iterations}"

  local start_time end_time elapsed
  start_time=$(date +%s%N)

  for ((i = 0; i < iterations; i++)); do
    eval "${command}" >/dev/null
  done

  end_time=$(date +%s%N)
  elapsed=$(( (end_time - start_time) / 1000000 ))

  echo "Total time: ${elapsed}ms"
  echo "Average:    $((elapsed / iterations))ms"
  echo ""
}

# 对比测试
compare() {
  local name1="${1}"
  local cmd1="${2}"
  local name2="${3}"
  local cmd2="${4}"
  local iterations="${5:-100}"

  echo "=== Performance Comparison ==="
  echo ""

  local time1 time2

  # 测试第一个
  local start=$(date +%s%N)
  for ((i = 0; i < iterations; i++)); do
    eval "${cmd1}" >/dev/null
  done
  local end=$(date +%s%N)
  time1=$(( (end - start) / 1000000 ))

  # 测试第二个
  start=$(date +%s%N)
  for ((i = 0; i < iterations; i++)); do
    eval "${cmd2}" >/dev/null
  done
  end=$(date +%s%N)
  time2=$(( (end - start) / 1000000 ))

  # 输出结果
  printf "%-20s %8d ms\n" "${name1}" "${time1}"
  printf "%-20s %8d ms\n" "${name2}" "${time2}"

  if [ "${time1}" -lt "${time2}" ]; then
    local faster=$(( (time2 - time1) * 100 / time2 ))
    printf "%-20s %d%% faster\n" "${name1}" "${faster}"
  else
    local faster=$(( (time1 - time2) * 100 / time1 ))
    printf "%-20s %d%% faster\n" "${name2}" "${faster}"
  fi
}

# 使用示例
compare "Bash sort" "echo -e '3\n1\n2' | sort"         "C qsort" "./benchmark_qsort"
```

---

## 第4节：批量编译管理

### 多平台批量编译

```bash
#!/usr/bin/env bash
set -euo pipefail

# 批量编译脚本
BUILD_DIR="build"
SRC_FILE="main.c"

# 目标平台
PLATFORMS=(
  "linux:x86_64-linux-gnu-gcc"
  "linux:aarch64-linux-gnu-gcc"
  "macos:clang"
  "windows:x86_64-w64-mingw32-gcc"
)

# 创建输出目录
mkdir -p "${BUILD_DIR}"

# 批量编译
for platform in "${PLATFORMS[@]}"; do
  IFS=':' read -r os compiler <<< "${platform}"

  echo "Building for ${os}..."
  output="${BUILD_DIR}/program-${os}"

  if [ "${os}" = "windows" ]; then
    output="${output}.exe"
  fi

  ${compiler} -O2 -Wall -o "${output}" "${SRC_FILE}"

  if [ $? -eq 0 ]; then
    echo "  Success: ${output}"
  else
    echo "  Failed: ${output}" >&2
  fi
done

echo "Build complete!"
ls -la "${BUILD_DIR}/"
```

### 版本管理编译

```bash
#!/usr/bin/env bash
set -euo pipefail

# 从 Git 标签获取版本
get_version() {
  local version
  version=$(git describe --tags --always 2>/dev/null || echo "unknown")
  echo "${version}"
}

# 编译时注入版本信息
compile_with_version() {
  local version
  version=$(get_version)

  echo "Compiling version: ${version}"

  gcc -o myprogram     -DVERSION="${version}"     -DBUILD_DATE="$(date +%Y-%m-%d)"     main.c
}

# 生成版本文件
generate_version_info() {
  local version
  version=$(get_version)

  cat > version.h << EOF
#ifndef VERSION_H
#define VERSION_H

#define VERSION "${version}"
#define BUILD_DATE "$(date +%Y-%m-%d)"
#define BUILD_TIME "$(date +%H:%M:%S)"

#endif
EOF
}

generate_version_info
compile_with_version
```

---

## 第5节：CMake/Makefile的Bash封装

### CMake 封装脚本

```bash
#!/usr/bin/env bash
set -euo pipefail

# CMake 构建封装
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${PROJECT_DIR}/build"
INSTALL_DIR="${PROJECT_DIR}/install"

# 清理
clean() {
  echo "Cleaning build directory..."
  rm -rf "${BUILD_DIR}"
  mkdir -p "${BUILD_DIR}"
}

# 配置
configure() {
  local build_type="${1:-Release}"

  echo "Configuring CMake (type: ${build_type})..."
  cmake -B "${BUILD_DIR}"     -DCMAKE_BUILD_TYPE="${build_type}"     -DCMAKE_INSTALL_PREFIX="${INSTALL_DIR}"     -DBUILD_TESTING=ON     "${PROJECT_DIR}"
}

# 编译
build() {
  local jobs="${1:-$(nproc)}"

  echo "Building with ${jobs} jobs..."
  cmake --build "${BUILD_DIR}" --parallel "${jobs}"
}

# 安装
install() {
  echo "Installing..."
  cmake --install "${BUILD_DIR}"
}

# 运行测试
test() {
  echo "Running tests..."
  cmake --build "${BUILD_DIR}" --target test
}

# 打包
package() {
  echo "Creating package..."
  cd "${BUILD_DIR}"
  cpack -G TGZ
}

# 主函数
main() {
  local action="${1:-build}"

  case "${action}" in
    clean)    clean ;;
    config)   configure "${2:-Release}" ;;
    build)    build "${2:-$(nproc)}" ;;
    install)  install ;;
    test)     test ;;
    package)  package ;;
    all)
      clean
      configure
      build
      test
      ;;
    *)
      echo "Usage: $0 {clean|config|build|install|test|package|all}"
      exit 1
      ;;
  esac
}

main "$@"
```

### Makefile 封装

```bash
#!/usr/bin/env bash
set -euo pipefail

# Makefile 封装
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 检查 Makefile 是否存在
if [ ! -f "${PROJECT_DIR}/Makefile" ]; then
  echo "Error: Makefile not found" >&2
  exit 1
fi

# 封装 make 命令
make_target() {
  local target="${1:-all}"
  local jobs="${2:-$(nproc)}"

  echo "Running make ${target} with ${jobs} jobs..."
  make -C "${PROJECT_DIR}" -j "${jobs}" "${target}"
}

# 自动检测最优 job 数
optimal_jobs() {
  local cpu_count
  cpu_count=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)
  echo $((cpu_count + 1))
}

# 主函数
main() {
  local action="${1:-build}"

  case "${action}" in
    build)     make_target "all" "$(optimal_jobs)" ;;
    clean)     make_target "clean" ;;
    test)      make_target "test" ;;
    install)   make_target "install" ;;
    reinstall) make_target "clean" && make_target "install" ;;
    *)
      echo "Usage: $0 {build|clean|test|install|reinstall}"
      exit 1
      ;;
  esac
}

main "$@"
```

---

## 第6节：完整的C项目Bash工具链

### 项目脚手架

```bash
#!/usr/bin/env bash
set -euo pipefail

# C 项目脚手架
create_project() {
  local name="${1}"

  mkdir -p "${name}"/{src,include,tests,build,bin,docs}

  # 创建基础文件
  cat > "${name}/Makefile" << 'EOF'
CC = gcc
CFLAGS = -Wall -Wextra -O2
SRC = $(wildcard src/*.c)
OBJ = $(SRC:.c=.o)
BIN = bin/program

all: $(BIN)

$(BIN): $(OBJ) | bin
	$(CC) $(CFLAGS) -o $@ $^

src/%.o: src/%.c | build
	$(CC) $(CFLAGS) -c -o $@ $<

bin build:
	mkdir -p $@

clean:
	rm -rf build bin src/*.o

.PHONY: all clean
EOF

  cat > "${name}/src/main.c" << 'EOF'
#include <stdio.h>

int main(int argc, char *argv[]) {
    printf("Hello from %s!\n", argv[0]);
    return 0;
}
EOF

  echo "Project '${name}' created!"
  echo "  cd ${name}"
  echo "  make"
  echo "  ./bin/program"
}

# 使用
create_project "my_project"
```

### 自动化工作流

```bash
#!/usr/bin/env bash
set -euo pipefail

# 开发工作流
dev_workflow() {
  echo "=== Development Workflow ==="

  # 1. 代码检查
  echo "Step 1: Code linting..."
  if command -v cppcheck &>/dev/null; then
    cppcheck --enable=all src/
  fi

  # 2. 编译
  echo "Step 2: Building..."
  make clean && make

  # 3. 测试
  echo "Step 3: Testing..."
  make test

  # 4. 性能检查
  echo "Step 4: Performance..."
  if [ -f benchmarks/run.sh ]; then
    benchmarks/run.sh
  fi

  echo "=== Workflow Complete ==="
}

dev_workflow
```

本节帮助你构建完整的 Bash 封装 C 工具链，实现自动化、标准化的 C 项目开发流程。
