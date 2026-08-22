# 在bash中调用C程序 | Calling C Programs from Bash

## 章节概述

本章详细讲解如何在 Bash 脚本中调用 C 程序，涵盖编译与调用流程、系统调用机制、exec 家族函数、PATH 查找策略、参数传递方式，以及 C 语言 main(argc, argv) 与 Bash 参数处理的对比分析。

> **核心理念**：Bash 擅长流程控制和胶水编程，C 擅长性能密集型计算。将两者结合，让 Shell 脚本拥有 C 的执行效率，是系统编程的高级技巧。

---

## 第1节：编译并调用C程序

### 基本流程

```bash
# 1. 编写 C 程序
cat > hello.c << 'EOF'
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: %s <name>\n", argv[0]);
        return 1;
    }
    printf("Hello, %s!\n", argv[1]);
    return 0;
}
EOF

# 2. 编译
gcc -o hello hello.c

# 3. 在 Bash 中调用
./hello "World"
# 输出: Hello, World!
```

### 编译选项对照表

| 选项 | 作用 | 示例 |
|------|------|------|
| `-o` | 指定输出文件名 | `gcc -o myprog main.c` |
| `-Wall` | 开启所有警告 | `gcc -Wall -o myprog main.c` |
| `-g` | 包含调试信息 | `gcc -g -o myprog main.c` |
| `-O2` | 优化级别2 | `gcc -O2 -o myprog main.c` |
| `-lm` | 链接数学库 | `gcc -o myprog main.c -lm` |
| `-lpthread` | 链接线程库 | `gcc -o myprog main.c -lpthread` |
| `-std=c99` | 指定C标准 | `gcc -std=c99 -o myprog main.c` |

### 自动编译脚本

```bash
#!/usr/bin/env bash
set -euo pipefail

# 编译 C 程序
compile_c() {
  local src="${1}"
  local output="${2}"
  local flags="${3:-}"

  if [ ! -f "${src}" ]; then
    echo "Source file not found: ${src}" >&2
    return 1
  fi

  # 检查是否需要重新编译
  if [ -f "${output}" ] && [ "${src}" -ot "${output}" ]; then
    echo "Binary is up to date: ${output}"
    return 0
  fi

  echo "Compiling ${src} -> ${output}"
  gcc -Wall ${flags} -o "${output}" "${src}"
  echo "Compilation successful"
}

# 使用
compile_c "hello.c" "hello" "-O2"
./hello "World"
```

---

## 第2节：系统调用与exec家族

### 系统调用方式

```bash
# 方式1：子进程调用（最常用）
# 命令在子进程中执行，Bash 等待完成
./my_program

# 方式2：exec 替换当前进程
# 替换当前 Shell 进程，不返回
exec ./my_program

# 方式3：后台执行
./my_program &

# 方式4：命令替换捕获输出
result=$(./my_program)
echo "Output: ${result}"
```

### exec 家族函数对比

| 函数 | 作用 | 返回 | 使用场景 |
|------|------|------|----------|
| `exec command` | 替换当前进程 | 不返回 | 启动新进程替换当前 |
| `exec < file` | 重定向输入 | 0 | 从文件读取输入 |
| `exec > file` | 重定向输出 | 0 | 输出到文件 |
| `exec 2> file` | 重定向错误 | 0 | 错误输出到文件 |
| `exec 3<> file` | 打开文件描述符 | 0 | 高级 I/O 操作 |

### exec 使用示例

```bash
# 替换当前进程
exec /usr/bin/python3 script.py

# 重定向输出
exec > /var/log/script.log 2>&1
echo "This goes to log file"

# 打开文件描述符
exec 3< /etc/hosts
while read -r line <&3; do
  echo "${line}"
done
exec 3<&-

# 用 exec 设置文件描述符
exec 4> /tmp/output.txt
echo "data" >&4
exec 4>&-
```

---

## 第3节：PATH查找与命令定位

### PATH 查找机制

```bash
# 查看 PATH
echo "${PATH}" | tr ':' '\n'

# 检查命令是否存在
command -v my_program >/dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "Program found"
else
  echo "Program not found"
fi

# which 命令
which my_program

# whereis 命令
whereis my_program

# type 命令（Bash 内置）
type my_program
```

### 自定义 PATH 查找

```bash
# 添加自定义路径到 PATH
export PATH="/opt/mytools/bin:${PATH}"

# 查找可执行文件
find_executable() {
  local name="${1}"
  local dirs=("/usr/local/bin" "/opt/bin" "${HOME}/bin")

  for dir in "${dirs[@]}"; do
    if [ -x "${dir}/${name}" ]; then
      echo "${dir}/${name}"
      return 0
    fi
  done

  # 使用 which 作为后备
  which "${name}" 2>/dev/null || return 1
}

# 使用
MY_PROG=$(find_executable "my_program")
if [ -n "${MY_PROG}" ]; then
  "${MY_PROG}" --help
fi
```

---

## 第4节：传递参数到C程序

### 参数传递方式

```bash
# 方式1：直接传递命令行参数
./my_program --name "John" --age 30

# 方式2：通过变量传递
name="John"
age=30
./my_program --name "${name}" --age "${age}"

# 方式3：通过环境变量传递
export MY_VAR="hello"
./my_program

# 方式4：通过管道传递数据
echo "input data" | ./my_program

# 方式5：通过文件传递
echo "input data" > /tmp/input.txt
./my_program < /tmp/input.txt
```

### Bash 参数处理 vs C 参数处理

```bash
# Bash 参数处理
parse_args() {
  while [[ $# -gt 0 ]]; do
    case "${1}" in
      -n|--name)
        NAME="${2}"
        shift 2
        ;;
      -a|--age)
        AGE="${2}"
        shift 2
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        shift
        ;;
    esac
  done
}

# 对应的 C 语言实现
cat > args.c << 'EOF'
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int main(int argc, char *argv[]) {
    char *name = NULL;
    int age = 0;

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--name") == 0 && i + 1 < argc) {
            name = argv[++i];
        } else if (strcmp(argv[i], "--age") == 0 && i + 1 < argc) {
            age = atoi(argv[++i]);
        } else if (strcmp(argv[i], "--help") == 0) {
            printf("Usage: %s --name <name> --age <age>\n", argv[0]);
            return 0;
        }
    }

    if (name) printf("Name: %s\n", name);
    if (age > 0) printf("Age: %d\n", age);
    return 0;
}
EOF
```

---

## 第5节：main(argc, argv) 对比分析

### C 语言 main 函数签名

```c
// 标准形式
int main(int argc, char *argv[]);

// argc: 参数个数（包括程序名本身）
// argv: 参数字符串数组

// 示例
#include <stdio.h>
int main(int argc, char *argv[]) {
    printf("argc = %d\n", argc);
    for (int i = 0; i < argc; i++) {
        printf("argv[%d] = %s\n", i, argv[i]);
    }
    return 0;
}
```

### 对比表

| 特性 | Bash | C |
|------|------|---|
| 参数获取 | `$1`, `$2`, `$@`, `$*` | `argv[0]`, `argv[1]`, ... |
| 参数个数 | `$#` | `argc` |
| 程序名 | `$0` | `argv[0]` |
| 所有参数 | `"$@"` | 遍历 `argv[]` |
| 循环参数 | `for arg in "$@"` | `for (int i=1; i<argc; i++)` |
| shift | `shift` | `argv++; argc--;` |
| 退出码 | `exit $?` | `return main()` |

### 混合调用示例

```bash
#!/usr/bin/env bash
set -euo pipefail

# 编译 C 工具
gcc -o process process.c

# 构建参数
args=()
args+=("--input" "${INPUT_FILE}")
args+=("--output" "${OUTPUT_FILE}")
args+=("--verbose")
[ -n "${MAX_SIZE:-}" ] && args+=("--max-size" "${MAX_SIZE}")

# 调用 C 程序
./process "${args[@]}"

# 检查退出码
if [ $? -ne 0 ]; then
  echo "C program failed" >&2
  exit 1
fi
```

---

## 第6节：实战：Bash + C 混合编程

### 完整示例：数据处理管道

```bash
#!/usr/bin/env bash
set -euo pipefail

# 编译 C 加速工具
compile_tools() {
  local tools=("parser" "aggregator" "formatter")
  for tool in "${tools[@]}"; do
    if [ ! -x "./bin/${tool}" ] || [ "src/${tool}.c" -nt "./bin/${tool}" ]; then
      echo "Compiling ${tool}..."
      gcc -O2 -Wall -o "./bin/${tool}" "./src/${tool}.c"
    fi
  done
}

# 主处理流程
main() {
  local input="${1:-}"

  if [ -z "${input}" ]; then
    echo "Usage: $0 <input_file>" >&2
    exit 1
  fi

  # 步骤1：C 程序解析数据
  echo "Step 1: Parsing..."
  ./bin/parser "${input}" > /tmp/parsed.dat

  # 步骤2：Bash 逻辑判断
  local line_count
  line_count=$(wc -l < /tmp/parsed.dat)
  if [ "${line_count}" -eq 0 ]; then
    echo "No data to process" >&2
    exit 0
  fi

  # 步骤3：C 程序聚合数据
  echo "Step 2: Aggregating..."
  ./bin/aggregator /tmp/parsed.dat > /tmp/aggregated.dat

  # 步骤4：C 程序格式化输出
  echo "Step 3: Formatting..."
  ./bin/formatter /tmp/aggregated.dat > output.json

  echo "Done! Output: output.json"
}

compile_tools
main "$@"
```

### 性能对比脚本

```bash
#!/usr/bin/env bash

# 编写测试 C 程序
cat > benchmark.c << 'EOF'
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

long long fibonacci(int n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

int main(int argc, char *argv[]) {
    int n = atoi(argv[1]);
    clock_t start = clock();
    long long result = fibonacci(n);
    clock_t end = clock();
    double time_spent = (double)(end - start) / CLOCKS_PER_SEC;
    printf("fib(%d) = %lld\n", n, result);
    printf("Time: %.6f seconds\n", time_spent);
    return 0;
}
EOF

# Bash 实现
bash_fibonacci() {
  local n="${1}"
  if [ "${n}" -le 1 ]; then
    echo "${n}"
    return
  fi
  local a=0 b=1
  for ((i = 2; i <= n; i++)); do
    local temp=$((a + b))
    a="${b}"
    b="${temp}"
  done
  echo "${b}"
}

# 编译并运行 C 版本
gcc -O2 -o benchmark benchmark.c
echo "=== C Version ==="
time ./benchmark 30

echo ""
echo "=== Bash Version ==="
time bash_fibonacci 30
```

本节帮助你掌握 Bash 与 C 程序的交互技巧，充分发挥两种语言的优势。
