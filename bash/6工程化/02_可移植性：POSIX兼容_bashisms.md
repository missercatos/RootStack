# 可移植性：POSIX兼容与bashisms | Portability: POSIX Compatibility and bashisms

## 章节概述

本章深入分析 POSIX sh 与 Bash 的差异，列出常见 bashisms（Bash 特有语法），介绍 checkbashisms 工具的使用，并提供编写 POSIX 兼容脚本的完整指南。理解这些差异是编写跨平台、可移植 Shell 脚本的关键。

> **核心理念**：可移植性不是妥协，而是工程能力的体现。写出能在 dash、ash、ksh 等多种 Shell 上运行的脚本，才是真正的 Shell 编程高手。

---

## 第1节：POSIX sh 与 Bash 差异概览

POSIX sh 是 Shell 的标准规范，而 Bash 是其最常见的实现之一，但 Bash 扩展了许多 POSIX 不包含的特性。

### 差异对比表

| 特性 | POSIX sh | Bash | 说明 |
|------|----------|------|------|
| `[[ ]]` | 不支持 | 支持 | 条件表达式 |
| `$(( ))` 算术 | 基础 | 扩展 | Bash 支持 `**` 幂运算 |
| `declare -A` | 不支持 | 支持 | 关联数组 |
| `declare -i` | 不支持 | 支持 | 整数变量 |
| 数组 `${arr[@]}` | 不支持 | 支持 | 索引数组 |
| `<()` 进程替换 | 不支持 | 支持 | 进程替换 |
| `{1..10}` 花括号展开 | 不支持 | 支持 | 序列生成 |
| `function` 关键字 | 不支持 | 支持 | 函数定义 |
| `$RANDOM` | 不支持 | 支持 | 随机数 |
| `read -p` | 不支持 | 支持 | 带提示读取 |
| `echo -e` | 部分支持 | 支持 | 转义字符 |
| `local` | 非标准 | 支持 | 局部变量 |
| `source` | 不支持 | 支持 | 用 `.` 代替 |

### 执行 Shell 的区别

```bash
#!/bin/sh
# 在 Debian/Ubuntu 上，/bin/sh 是 dash，不是 bash
# 在 macOS 上，/bin/sh 是 bash 的 POSIX 模式

#!/bin/bash
# 明确使用 bash

#!/usr/bin/env bash
# 推荐方式，通过 PATH 查找 bash
```

### 查看当前 Shell

```bash
# 查看当前 shell 的名称
echo "$0"

# 查看 shell 的路径
echo "$SHELL"

# 查看当前 shell 的版本
echo "$BASH_VERSION"    # 仅 bash 有
echo "$SH_VERSION"      # sh 可能有

# 查看 /bin/sh 指向什么（Linux）
ls -la /bin/sh
# lrwxrwxrwx 1 root root 4 ... /bin/sh -> dash    (Ubuntu)
# lrwxrwxrwx 1 root root 4 ... /bin/sh -> bash    (CentOS)
```

---

## 第2节：Bashisms 列表——常见 Bash 特有语法

Bashisms 是指 Bash 独有的语法特性，在 POSIX sh 中不可用。

### 条件表达式

```bash
# Bashisms: [[ ]]
if [[ "${name}" == "test" ]]; then
  echo "match"
fi

# POSIX 兼容
if [ "${name}" = "test" ]; then
  echo "match"
fi

# Bashisms: [[ 中的正则匹配
if [[ "${email}" =~ ^[a-z]+@ ]]; then
  echo "valid email"
fi

# POSIX 兼容：使用 grep
if echo "${email}" | grep -qE '^[a-z]+@'; then
  echo "valid email"
fi

# Bashisms: [[ 中的通配符匹配
if [[ "${file}" == *.txt ]]; then
  echo "text file"
fi

# POSIX 兼容：使用 case
case "${file}" in
  *.txt) echo "text file" ;;
esac
```

### 数组

```bash
# Bashisms: 索引数组
arr=("one" "two" "three")
echo "${arr[0]}"
echo "${arr[@]}"

# POSIX 兼容：使用空格分隔的字符串
arr="one two three"
for item in ${arr}; do
  echo "${item}"
done

# 或者使用 eval
set -- one two three
echo "$1"  # one
echo "$2"  # two

# Bashisms: 关联数组
declare -A map
map[name]="John"
echo "${map[name]}"

# POSIX 兼容：使用变量名模拟
eval map_name="John"
echo "${map_name}"
```

### 算术运算

```bash
# Bashisms: (( )) 算术语句
(( count++ ))
if (( count > 10 )); then
  echo "done"
fi

# POSIX 兼容: test + -gt
count=$((count + 1))
if [ "${count}" -gt 10 ]; then
  echo "done"
fi

# Bashisms: ** 幂运算
result=$(( 2 ** 10 ))

# POSIX 兼容: 使用 bc 或循环
result=$(echo "2^10" | bc)
```

### 字符串操作

```bash
# Bashisms: ${var:offset:length}
sub="${string:2:3}"

# POSIX 兼容: 使用 cut 或 expr
sub=$(echo "${string}" | cut -c3-5)

# Bashisms: ${var//pattern/replacement}
result="${string//old/new}"

# POSIX 兼容: 使用 sed
result=$(echo "${string}" | sed 's/old/new/g')

# Bashisms: ${var,,} 小写转换
lower="${string,,}"

# POSIX 兼容: 使用 tr
lower=$(echo "${string}" | tr '[:upper:]' '[:lower:]')
```

### 其他常见 Bashisms

```bash
# Bashisms: 花括号展开
echo {1..10}
echo file{1..5}.txt

# POSIX 兼容: 使用 seq
seq 1 10

# Bashisms: 进程替换
diff <(sort file1) <(sort file2)

# POSIX 兼容: 使用临时文件
sort file1 > /tmp/sorted1
sort file2 > /tmp/sorted2
diff /tmp/sorted1 /tmp/sorted2
rm -f /tmp/sorted1 /tmp/sorted2

# Bashisms: read -p 提示
read -p "Enter name: " name

# POSIX 兼容
printf "Enter name: "
read name

# Bashisms: select 菜单
select opt in "Start" "Stop" "Quit"; do
  case "${opt}" in
    Start) break ;;
  esac
done

# POSIX 兼容: 手动实现菜单
echo "1) Start"
echo "2) Stop"
echo "3) Quit"
printf "Choose: "
read choice
```

---

## 第3节：checkbashisms 工具使用

`checkbashisms` 是 Debian 开发工具包中的静态分析工具，专门检测脚本中的 bashisms。

### 安装

```bash
# Debian/Ubuntu
sudo apt install devscripts

# macOS
brew install checkbashisms

# 手动安装（从源码）
git clone https://gitlab.com/esr/checkbashisms.git
cd checkbashisms && sudo make install
```

### 基本用法

```bash
# 检查单个脚本
checkbashisms my_script.sh

# 检查并显示详细信息
checkbashisms -p my_script.sh

# 检查所有 .sh 文件
find . -name "*.sh" -exec checkbashisms {} +

# 检查并输出到文件
checkbashisms my_script.sh 2>&1 | tee report.txt
```

### 输出解读

```
#!/bin/sh -e
possible bashism in my_script.sh line 10: [[ -f "$file" ]]
possible bashism in my_script.sh line 15: for i in {1..10}
possible bashism in my_script.sh line 20: declare -A map
```

| 输出信息 | 含义 | 修复建议 |
|----------|------|----------|
| `[[ ]]` | 使用了 Bash 条件表达式 | 改用 `[ ]` |
| `{1..10}` | 花括号展开 | 使用 `seq` |
| `declare -A` | 关联数组 | 使用其他方式 |
| `$RANDOM` | 随机数 | 使用其他方式 |
| `<<<` Here String | Here String | 使用管道 |

---

## 第4节：如何写 POSIX 兼容脚本

### 编写原则

```bash
#!/bin/sh
# 明确使用 sh 而非 bash

# 原则1：使用 [ ] 而非 [[ ]]
if [ -f "${file}" ]; then
  echo "exists"
fi

# 原则2：使用 $() 而非反引号
result=$(command)

# 原则3：使用 printf 而非 echo -e
printf "Hello\n"

# 原则4：避免数组，使用字符串
set -- a b c
for arg; do
  echo "${arg}"
done

# 原则5：使用 case 替代 [[ pattern match ]]
case "${string}" in
  *.txt) echo "text" ;;
  *)     echo "other" ;;
esac

# 原则6：使用 expr 或 $(( )) 替代 (( ))
count=$((count + 1))

# 原则7：使用 seq 替代 {1..10}
for i in $(seq 1 10); do
  echo "${i}"
done
```

### 可移植函数库

```bash
#!/bin/sh
# portable_utils.sh - POSIX 兼容的工具函数

# 兼容的字符串包含检查
str_contains() {
  case "${1}" in
    *"${2}"*) return 0 ;;
    *)        return 1 ;;
  esac
}

# 兼容的字符串替换
str_replace() {
  echo "${1}" | sed "s/${2}/${3}/g"
}

# 兼容的小写转换
to_lower() {
  echo "${1}" | tr '[:upper:]' '[:lower:]'
}

# 兼容的大写转换
to_upper() {
  echo "${1}" | tr '[:lower:]' '[:upper:]'
}

# 兼容的字符串长度
str_len() {
  echo "${1}" | wc -c | tr -d ' '
}

# 兼容的去首尾空格
trim() {
  echo "${1}" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//'
}

# 使用示例
if str_contains "hello world" "world"; then
  echo "found"
fi

result=$(str_replace "hello world" "world" "bash")
echo "${result}"  # hello bash
```

---

## 第5节：dash vs bash 性能对比

### 执行速度对比

```bash
#!/bin/bash
# benchmark.sh - dash vs bash 性能对比

echo "=== dash vs bash 性能对比 ==="
echo ""

# 测试1：简单循环
echo "测试1: 简单循环 (1-10000)"
echo "---"
time sh -c 'for i in $(seq 1 10000); do echo $i > /dev/null; done'
echo ""
time bash -c 'for i in {1..10000}; do echo $i > /dev/null; done'
echo ""

# 测试2：字符串操作
echo "测试2: 字符串操作"
echo "---"
time sh -c 'i=0; while [ $i -lt 1000 ]; do str="hello_world"; echo "${str}" > /dev/null; i=$((i+1)); done'
echo ""
time bash -c 'i=0; while ((i < 1000)); do str="hello_world"; echo "${str}" > /dev/null; ((i++)); done'
echo ""

# 测试3：文件操作
echo "测试3: 文件操作"
echo "---"
time sh -c 'for f in /usr/bin/*; do cat "$f" > /dev/null 2>&1; done'
echo ""
time bash -c 'for f in /usr/bin/*; do cat "$f" > /dev/null 2>&1; done'
```

### dash vs bash 选择指南

| 场景 | 推荐 Shell | 原因 |
|------|-----------|------|
| 系统启动脚本 | dash | 速度快，依赖少 |
| 简单脚本 | dash | 可移植性好 |
| 复杂逻辑 | bash | 功能更丰富 |
| 数组操作 | bash | 原生支持数组 |
| 交互式使用 | bash | 历史、补全支持 |
| 嵌入式/容器 | ash/dash | 体积小 |
| 生产部署 | sh (POSIX) | 兼容性最好 |

### 实际部署建议

```bash
#!/bin/sh
# 推荐：明确指定 POSIX sh 以保证最大兼容性
# 如果需要 bash 特性，使用 #!/usr/bin/env bash 并添加版本检查

# 在脚本开头检查 bash 版本（如果使用 bash）
if [ -n "${BASH_VERSION:-}" ]; then
  if [ "${BASH_VERSINFO[0]}" -lt 4 ]; then
    echo "Error: This script requires bash 4.0 or later" >&2
    exit 1
  fi
fi
```

本节帮助你理解 Shell 间的差异，编写出真正可移植的脚本，在任何环境下都能可靠运行。
