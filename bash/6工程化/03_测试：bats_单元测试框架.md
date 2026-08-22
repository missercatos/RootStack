# 测试：bats 单元测试框架 | Testing: bats Unit Testing Framework

## 章节概述

本章全面介绍 bats（Bash Automated Testing System）单元测试框架，涵盖安装配置、核心语法、断言函数、setup/teardown 机制、文件测试、管道测试以及 CI/CD 集成方案。掌握 bats 是编写可靠 Shell 脚本的必备技能。

> **核心理念**：没有测试的代码是定时炸弹。Shell 脚本同样需要测试覆盖，bats 让 Shell 测试变得简单、规范、可重复。

---

## 第1节：bats 安装与基础配置

### 安装方式

```bash
# 方式1：从源码安装（推荐）
git clone https://github.com/bats-core/bats-core.git
cd bats-core
sudo ./install.sh /usr/local

# 方式2：使用包管理器
brew install bats-core        # macOS
sudo apt install bats         # Ubuntu/Debian
sudo pacman -S bats           # Arch Linux
npm install -g bats           # npm

# 验证安装
bats --version
```

### 项目结构

```
project/
├── src/
│   └── my_script.sh
├── test/
│   ├── my_script.bats        # 主测试文件
│   └── fixtures/             # 测试数据
│       └── sample.txt
└── run_tests.sh
```

### 运行测试

```bash
bats test/                      # 运行所有测试
bats test/my_script.bats        # 运行单个文件
bats --verbose-run test/        # 详细输出
bats --timing test/             # 显示计时
bats --formatter tap test/      # TAP 格式（CI 友好）
```

---

## 第2节：@test 语法详解

### 基本测试

```bash
#!/usr/bin/env bats

load '../src/my_script'

@test "echo 命令正常工作" {
  run echo "hello"
  [ "$status" -eq 0 ]
  [ "$output" = "hello" ]
}

@test "当前目录存在" {
  run pwd
  [ "$status" -eq 0 ]
  [ -d "$output" ]
}
```

### run 命令与结果变量

```bash
@test "run 捕获命令结果" {
  run ls /nonexistent
  # $status = 退出码, $output = stdout, $lines = 按行分割数组

  [ "$status" -eq 2 ]
  [[ "$output" == *"No such file"* ]]
}

@test "输出行数检查" {
  run seq 1 5
  [ "${#lines[@]}" -eq 5 ]
}
```

### 测试分类与 skip

```bash
@test "unit: 字符串长度计算" {
  run str_len "hello"
  [ "$output" = "5" ]
}

@test "skip: 待实现的功能" {
  skip "此功能尚未实现"
  run some_function
}
```

---

## 第3节：assert 断言函数

### 内置 assert 函数

```bash
@test "assert_equal 示例" {
  run calculate_sum 2 3
  assert_equal "$output" "5"
}

@test "assert_success 示例" {
  run true
  assert_success
}

@test "assert_failure 示例" {
  run false
  assert_failure
}

@test "assert_output 包含文本" {
  run echo "Hello World"
  assert_output --partial "Hello"
}

@test "assert_line 检查特定行" {
  run seq 1 3
  assert_line --index 0 "1"
  assert_line --index 1 "2"
  assert_line "3"
}
```

### 自定义 assert 函数

```bash
# test/helpers/custom_assert.bash

assert_file_exists() {
  local file="${1}"
  if [ ! -f "${file}" ]; then
    echo "expected file to exist: ${file}"
    return 1
  fi
}

assert_contains() {
  local haystack="${1}"
  local needle="${2}"
  if [[ "${haystack}" != *"${needle}"* ]]; then
    echo "expected '${haystack}' to contain '${needle}'"
    return 1
  fi
}

assert_between() {
  local value="${1}"
  local min="${2}"
  local max="${3}"
  if (( value < min || value > max )); then
    echo "expected ${value} to be between ${min} and ${max}"
    return 1
  fi
}
```

---

## 第4节：setup/teardown 机制

```bash
#!/usr/bin/env bats

# 全局 setup：所有测试之前执行一次
setup_file() {
  export TEST_DIR="$(mktemp -d)"
  export TEST_FILE="${TEST_DIR}/test.txt"
  echo "test data" > "${TEST_FILE}"
}

# 全局 teardown：所有测试之后执行一次
teardown_file() {
  rm -rf "${TEST_DIR}"
}

# 每个测试之前执行
setup() {
  mkdir -p "${TEST_DIR}/work"
  cd "${TEST_DIR}/work"
}

# 每个测试之后执行
teardown() {
  rm -rf "${TEST_DIR}/work"/*
}

@test "setup 创建了工作目录" {
  [ -d "${TEST_DIR}/work" ]
}

@test "测试文件存在" {
  [ -f "${TEST_FILE}" ]
}
```

| 函数 | 执行时机 | 执行次数 | 用途 |
|------|----------|----------|------|
| `setup_file()` | 所有测试前 | 1次 | 初始化资源 |
| `teardown_file()` | 所有测试后 | 1次 | 清理资源 |
| `setup()` | 每个测试前 | 每测试1次 | 准备测试环境 |
| `teardown()` | 每个测试后 | 每测试1次 | 清理测试环境 |

---

## 第5节：文件测试与管道测试

### 文件测试

```bash
load '../src/file_utils'

@test "创建临时文件" {
  local tmpfile
  tmpfile=$(mktemp)
  run touch "${tmpfile}"
  assert_success
  [ -f "${tmpfile}" ]
  rm -f "${tmpfile}"
}

@test "文件权限检查" {
  local tmpfile
  tmpfile=$(mktemp)
  chmod 644 "${tmpfile}"
  run check_permissions "${tmpfile}" 644
  assert_success
  rm -f "${tmpfile}"
}

@test "目录递归创建" {
  run mkdir -p "${TEST_DIR}/a/b/c"
  assert_success
  [ -d "${TEST_DIR}/a/b/c" ]
}
```

### 管道测试

```bash
load '../src/text_processor'

@test "管道处理文本" {
  run bash -c 'echo "hello world" | to_upper'
  assert_output "HELLO WORLD"
}

@test "管道链式处理" {
  run bash -c 'echo -e "3\n1\n2" | sort | head -1'
  assert_output "1"
}

@test "管道错误传播" {
  run bash -c 'cat /nonexistent 2>&1 | head'
  assert_failure
}
```

---

## 第6节：CI 集成

### GitHub Actions 配置

```yaml
# .github/workflows/test.yml
name: Shell Script Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        shell: [bash, dash, ksh]
    steps:
      - uses: actions/checkout@v4

      - name: Install bats
        run: sudo apt-get install -y bats

      - name: Install additional shells
        run: |
          sudo apt-get install -y dash ksh

      - name: Run tests with ${{ matrix.shell }}
        run: |
          SHELL=${{ matrix.shell }} bats test/

      - name: Run shellcheck
        run: |
          sudo apt-get install -y shellcheck
          find src/ -name "*.sh" -exec shellcheck {} +
```

### GitLab CI 配置

```yaml
# .gitlab-ci.yml
test:
  image: ubuntu:latest
  before_script:
    - apt-get update && apt-get install -y bats shellcheck
  script:
    - bats test/
    - find src/ -name "*.sh" -exec shellcheck {} +
```

### 测试覆盖率

```bash
# 使用 bats-coverage
git clone https://github.com/bats-core/bats-coverage.git

# 在 CI 中生成覆盖率报告
bats --cover test/

# 详细覆盖率
bats --cover --count test/
```

### 测试报告格式

| 格式 | 命令 | 说明 |
|------|------|------|
| TAP | `bats --formatter tap test/` | 最通用，CI 兼容好 |
| JUnit | `bats --formatter junit test/` | GitHub Actions 支持 |
| Pretty | `bats --formatter pretty test/` | 终端友好 |

本节帮助你建立完整的 Shell 脚本测试体系，让代码质量有保障、持续集成更可靠。
