# 脚本规范：Google Shell Style Guide要点 | Script Standards: Google Shell Style Guide Essentials

## 章节概述

本章详细讲解 Google Shell Style Guide 的核心规范，包括文件头格式、变量命名、缩进规则、函数命名、注释标准以及错误处理最佳实践。遵循这些规范能显著提升 Shell 脚本的可读性、可维护性和团队协作效率。

> **核心理念**：代码是写给人看的，附带能在机器上执行。Google Shell Style Guide 将这一哲学贯彻到每一个细节，让 Shell 脚本也能像工程化语言一样优雅、一致、可维护。

---

## 第1节：文件头规范（Shebang + 注释）

文件头是脚本的第一印象，必须包含 shebang 行和版权/用途注释。

### Shebang 行

```bash
#!/bin/bash
# 必须是文件的第一行
# bash 优于 sh，因为 bash 提供更多现代特性

#!/usr/bin/env bash
# 推荐方式，可移植性更好，自动寻找 PATH 中的 bash
```

### 标准文件头模板

```bash
#!/usr/bin/env bash
#
# Copyright 2026 Your Company Name.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# ============================================================
# 文件名: script.sh
# 描述: 该脚本用于处理用户数据并生成报告
# 用法: ./script.sh [OPTIONS] <input_file>
# 作者: 张三 (zhangsan@example.com)
# 日期: 2026-08-22
# ============================================================
```

### 文件头规范对照表

| 元素 | 要求 | 说明 |
|------|------|------|
| Shebang | `#!/usr/bin/env bash` | 第一行，无空行 |
| 版权声明 | Apache 2.0 或 MIT | 团队统一选择 |
| 文件描述 | 必须 | 包含用途、用法、参数说明 |
| 作者信息 | 推荐 | 方便联系和维护 |
| 版本信息 | 推荐 | `VERSION="1.0.0"` |

---

## 第2节：变量命名规范

变量命名是代码可读性的基石，Google 规范有严格的命名约定。

### 变量命名规则

```bash
# ✅ 正确：全大写 + 下划线（常量/环境变量）
readonly MAX_RETRIES=3
export DATABASE_URL="mysql://localhost/mydb"

# ✅ 正确：小写 + 下划线（局部变量）
local count=0
local user_name=""

# ❌ 错误：驼峰命名
local userName=""     # 不要用驼峰
local USERNAME=""     # 常量才全大写

# ❌ 错误：连字符（bash 不支持）
local my-var=""       # 连字符在 bash 中是减号
```

### 变量命名速查表

| 类型 | 风格 | 示例 |
|------|------|------|
| 常量 | `UPPER_SNAKE_CASE` | `MAX_BUFFER_SIZE=1024` |
| 环境变量 | `UPPER_SNAKE_CASE` | `export PATH="/usr/bin"` |
| 局部变量 | `lower_snake_case` | `local file_count=0` |
| 循环变量 | 单字母或语义名 | `i`, `item`, `line` |
| 布尔变量 | `is_/has_/can_` 前缀 | `is_valid=true` |
| 数组 | `lower_snake_case` | `local files=()` |

### 变量引用

```bash
# ✅ 始终用双引号包裹变量（防止分词和通配符展开）
echo "${user_name}"
cat "${config_file}"

# ✅ 数组展开必须用 "${array[@]}"
files=("a.txt" "b.txt")
cat "${files[@]}"

# ❌ 危险：不加引号
echo $user_name    # 如果值含空格会出错
cat $config_file   # 如果路径含空格会出错
```

---

## 第3节：缩进与格式（2空格）

Google 规范明确要求 **2空格缩进**，不使用 Tab。

### 缩进规则

```bash
# ✅ 2空格缩进
if [[ -f "${file}" ]]; then
  echo "Found file: ${file}"
  if [[ -r "${file}" ]]; then
    echo "File is readable"
  fi
fi

# ❌ 不要用 Tab 或 4空格
if [[ -f "${file}" ]]; then
    echo "4 spaces is wrong"    # 不要用 4 空格
fi

# ✅ case 语句缩进
case "${action}" in
  start)
    start_service
    ;;
  stop)
    stop_service
    ;;
  *)
    echo "Unknown action: ${action}" >&2
    return 1
    ;;
esac

# ✅ 函数体缩进
my_function() {
  local result=""
  result=$(do_something)
  echo "${result}"
}
```

### 格式规范

| 项目 | 规则 | 示例 |
|------|------|------|
| 缩进 | 2空格 | `  local x=1` |
| Tab | 禁止使用 | — |
| 续行 | 4空格缩进 | `command \`<br>`    --option \`<br>`    --value` |
| 空行 | 函数间1空行 | 函数与函数之间 |
| 行尾 | 无尾随空格 | — |
| 文件尾 | 1个换行符 | — |

### 续行格式

```bash
# ✅ 长命令续行：4空格缩进
very_long_command \
    --option1 value1 \
    --option2 value2 \
    --option3 value3

# ✅ 管道链续行
cat "${input_file}" \
    | grep "^ERROR" \
    | sort \
    | uniq -c \
    | sort -rn \
    > "${output_file}"
```

---

## 第4节：函数命名与结构

函数是代码复用的核心，命名和结构需遵循统一标准。

### 函数命名

```bash
# ✅ 正确：小写 + 下划线，动词开头
do_something() { ... }
get_user_input() { ... }
validate_config() { ... }
is_valid_email() { ... }

# ✅ 内部辅助函数用下划线前缀（约定私有）
_is_valid_port() {
  local port="${1}"
  [[ "${port}" =~ ^[0-9]+$ ]] && (( port >= 1 && port <= 65535 ))
}

# ❌ 错误：驼峰或大写
DoSomething() { ... }   # 不要用大写开头
getUserInput() { ... }   # 不要用驼峰
```

### 函数定义格式

```bash
# ✅ 推荐格式：括号单独一行
my_function() {
  # 函数体
}

# 也可以用 function 关键字（但不推荐，可移植性差）
function my_function {
  # 函数体
}

# 函数结构模板
calculate_sum() {
  # 1. 参数校验
  if [[ $# -lt 2 ]]; then
    echo "Usage: calculate_sum <num1> <num2>" >&2
    return 1
  fi

  # 2. 参数解析
  local num1="${1}"
  local num2="${2}"

  # 3. 核心逻辑
  local result=$(( num1 + num2 ))

  # 4. 输出结果
  echo "${result}"
}
```

### 函数文档注释

```bash
# 计算两个数字的和
#
# 参数:
#   $1 - 第一个数字
#   $2 - 第二数字
#
# 返回值:
#   0 - 成功
#   1 - 参数错误
#
# 示例:
#   result=$(calculate_sum 3 5)
#   echo "${result}"  # 输出: 8
calculate_sum() {
  # ...
}
```

---

## 第5节：注释规范

注释是代码的说明书，好的注释能节省大量维护时间。

### 注释类型

```bash
# ✅ 行注释：# 后跟一个空格
# 这是注释

# ✅ 文件头注释：描述脚本用途
# 该脚本用于自动化部署

# ✅ TODO 注释：标记待办事项
# TODO(zhangsan): 需要添加错误处理
# TODO(2026-12-01): 重构为更通用的实现

# ✅ BUG 注释：记录已知问题
# BUG: 在 CentOS 7 上会出错，已知问题

# ✅ HACK 注释：记录临时解决方案
# HACK: 为了兼容旧版本，暂时使用这个方法

# ❌ 无用注释
echo "hello"  # 输出 hello    # 这种注释是多余的
x=1           # x 等于 1      # 这种注释也是多余的

# ✅ 解释"为什么"而非"是什么"
# 使用 sleep 而非等待循环，因为目标服务启动需要时间
sleep 10

# 而不是：
# 等待 10 秒
sleep 10
```

### 注释最佳实践对照

| 场景 | 做法 | 示例 |
|------|------|------|
| 复杂逻辑 | 必须注释 | 说明算法思路 |
| 正则表达式 | 必须注释 | 解释每个部分的含义 |
| 临时方案 | 用 HACK 标记 | `# HACK: ...` |
| 已知问题 | 用 BUG 标记 | `# BUG: ...` |
| 待办事项 | 用 TODO 标记 | `# TODO(owner): ...` |
| 简单赋值 | 不加注释 | `count=0` 不需要注释 |

---

## 第6节：错误处理规范

健壮的脚本必须有完善的错误处理机制。

### 基本错误处理

```bash
# ✅ set -euo pipefail（推荐组合）
set -euo pipefail

# -e: 命令失败时立即退出
# -u: 使用未定义变量时报错
# -o pipefail: 管道中任意命令失败则整体失败

# ✅ trap 捕获错误
cleanup() {
  local exit_code=$?
  echo "Script failed with exit code: ${exit_code}" >&2
  # 清理临时文件
  rm -f "${TMP_FILE:-}"
  exit "${exit_code}"
}
trap cleanup EXIT ERR

# ✅ 函数返回值检查
if ! do_something; then
  echo "Failed to do something" >&2
  return 1
fi
```

### 错误处理模式

```bash
# 模式1：错误信息输出到 stderr
error() {
  echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') $*" >&2
}

# 模式2：带退出码的错误
die() {
  local code="${1:-1}"
  shift
  echo "[FATAL] $*" >&2
  exit "${code}"
}

# 使用示例
validate_input() {
  local input="${1}"
  if [[ -z "${input}" ]]; then
    die 2 "Input cannot be empty"
  fi
}

# 模式3：可恢复错误
safe_execute() {
  local description="${1}"
  shift
  if ! "$@"; then
    error "Failed: ${description}"
    return 1
  fi
  return 0
}

# 使用
safe_execute "database backup" pg_dump -h localhost mydb > backup.sql
```

### 常见错误处理对照

| 错误场景 | 推荐做法 | 避免做法 |
|----------|----------|----------|
| 命令失败 | `set -e` + `trap` | 忽略错误 |
| 未定义变量 | `set -u` | 直接使用空变量 |
| 管道失败 | `set -o pipefail` | 只检查最后一条命令 |
| 资源清理 | `trap cleanup EXIT` | 不清理临时文件 |
| 错误输出 | `>&2` 重定向到 stderr | 输出到 stdout |

---

## 第7节：Google Shell Style Guide 核心要点汇总

### 必须遵守的规则（Must）

| 规则 | 说明 |
|------|------|
| Shebang | 第一行必须是 `#!/usr/bin/env bash` |
| 2空格缩进 | 禁止 Tab，禁止 4 空格 |
| 变量加引号 | `"${var}"` 而非 `$var` |
| `set -euo pipefail` | 每个脚本都应设置 |
| 函数用 `()` | `my_func() {` 而非 `function my_func {` |
| 命令替换用 `$()` | `$()` 而非反引号 `` ` ` `` |
| `[[ ]]` 优于 `[ ]` | bash 脚本用 `[[ ]]` |

### 应该遵守的规则（Should）

| 规则 | 说明 |
|------|------|
| 文件头注释 | 包含版权、用途、用法 |
| 函数文档 | 描述参数和返回值 |
| 常量用 `readonly` | 不可变值标记为只读 |
| 局部变量用 `local` | 函数内变量加 `local` |
| 错误信息到 stderr | `echo "error" >&2` |
| 临时文件用 `mktemp` | 不要硬编码临时路径 |

### 工具链推荐

| 工具 | 用途 |
|------|------|
| `shellcheck` | 静态分析，检测常见错误 |
| `shfmt` | 自动格式化 Shell 脚本 |
| `editorconfig` | 统一编辑器配置 |
| `git hooks` | 提交前自动检查格式 |

```bash
# shellcheck 示例
# shellcheck shell=bash
#!/usr/bin/env bash

# shellcheck disable=SC2086  # 故意不加引号的情况
echo $unquoted_var
```

---

## 实战：完整的脚本模板

```bash
#!/usr/bin/env bash
#
# Copyright 2026 Your Company.
#
# Licensed under the Apache License, Version 2.0

set -euo pipefail

# ============================================================
# 全局常量
# ============================================================
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"
readonly VERSION="1.0.0"

# ============================================================
# 日志函数
# ============================================================
log_info()  { echo "[INFO]  $(date '+%Y-%m-%d %H:%M:%S') $*"; }
log_error() { echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') $*" >&2; }
die()       { log_error "$@"; exit 1; }

# ============================================================
# 清理函数
# ============================================================
cleanup() {
  local exit_code=$?
  rm -f "${TMP_FILE:-}"
  exit "${exit_code}"
}
trap cleanup EXIT ERR

# ============================================================
# 参数解析
# ============================================================
usage() {
  cat <<EOF
Usage: ${SCRIPT_NAME} [OPTIONS] <file>
Version: ${VERSION}

Options:
  -h, --help      Show this help message
  -v, --verbose   Enable verbose output
  -o <output>     Output file (default: stdout)
EOF
}

main() {
  local verbose=false
  local output=""

  while [[ $# -gt 0 ]]; do
    case "${1}" in
      -h|--help)    usage; exit 0 ;;
      -v|--verbose) verbose=true; shift ;;
      -o)           output="${2}"; shift 2 ;;
      -*)           die "Unknown option: ${1}" ;;
      *)            break ;;
    esac
  done

  [[ $# -eq 0 ]] && die "Missing required argument: <file>"

  local input_file="${1}"

  if [[ ! -f "${input_file}" ]]; then
    die "File not found: ${input_file}"
  fi

  log_info "Processing file: ${input_file}"

  # 核心逻辑
  process_file "${input_file}" "${output}"
}

process_file() {
  local input="${1}"
  local output="${2:-}"

  if [[ -n "${output}" ]]; then
    cat "${input}" > "${output}"
    log_info "Output written to ${output}"
  else
    cat "${input}"
  fi
}

main "$@"
```

本节内容覆盖了 Google Shell Style Guide 的核心要点，遵循这些规范能让你的 Shell 脚本达到工程级质量标准。
