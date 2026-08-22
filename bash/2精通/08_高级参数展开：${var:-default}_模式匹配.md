# 高级参数展开：${var:-default}、模式匹配（Advanced Parameter Expansion: ${var:-default}, Pattern Matching）

## 章节概述

本章深入讲解 Bash 参数展开的高级特性，包括默认值、赋值、错误检查、字符串截取、模式匹配替换、大小写转换以及数组展开。参数展开是 Bash 纯内置操作中效率最高的字符串处理方式，无需外部命令。

> **核心理念**：参数展开是 Bash 的"瑞士军刀"——所有操作都在 shell 内部完成，无 fork/exec 开销。掌握它可以让脚本更简洁、更高效。

---

### 第1节：默认值与错误检查（Default Values & Error Checking）

#### 四种参数展开模式

| 语法 | 功能 | 条件 |
|------|------|------|
| `${var:-default}` | 使用默认值 | var 未设置或为空 |
| `${var:=default}` | 设置默认值 | var 未设置或为空 |
| `${var:+value}` | 替换值 | var 已设置且非空 |
| `${var:?error}` | 报错退出 | var 未设置或为空 |

```bash
# ${var:-default}：使用默认值
echo "${HOME:-/home/default}"     # $HOME 已设置
echo "${UNSET:-fallback}"         # 未设置，输出 fallback

# ${var:=default}：设置默认值
echo "${MYVAR:=initialized}"      # 设置 MYVAR=initialized
echo "$MYVAR"                     # initialized

# ${var:+value}：条件替换
echo "${MYVAR:+exists}"           # 已设置，输出 exists
echo "${UNSET:+exists}"           # 未设置，输出空

# ${var:?error}：强制检查
echo "${DB_HOST:?DB_HOST must be set}"  # 未设置时终止脚本
```

#### 实战用法

```bash
#!/bin/bash
set -euo pipefail

# 必需变量检查
: "${INPUT_FILE:?INPUT_FILE is required}"
: "${OUTPUT_DIR:?OUTPUT_DIR is required}"

# 可选变量默认值
TEMP_DIR="${TEMP_DIR:-/tmp}"
LOG_LEVEL="${LOG_LEVEL:-info}"
MAX_RETRIES="${MAX_RETRIES:-3}"

# 条件操作
[ -n "${CONFIG_FILE:-}" ] && source "$CONFIG_FILE"

# 函数参数默认值
process_file() {
    local file="${1:?Usage: process_file <filename>}"
    local mode="${2:-read}"
    echo "Processing $file in $mode mode"
}
```

---

### 第2节：字符串长度与截取（String Length & Substring）

```bash
# 长度
str="Hello World"
echo "${#str}"           # 11

# 子串：${var:offset:length}
echo "${str:0:5}"        # Hello
echo "${str:6}"          # World
echo "${str: -5}"        # World（注意空格）

# 负偏移（从末尾）
echo "${str: -5}"        # World
echo "${str:(-5)}"       # World（Bash 4.2+）
echo "${str: -5:3}"      # Wor

# 截取文件扩展名
file="/path/to/archive.tar.gz"
echo "${file##*/}"       # archive.tar.gz
echo "${file#*/}"        # path/to/archive.tar.gz
```

#### 带偏移的实战

```bash
# 解析日志时间戳
log_line="2024-01-15 10:30:45 ERROR Connection failed"
timestamp="${log_line:0:19}"
level="${log_line:20:5}"
message="${log_line:26}"
echo "Time: $timestamp"
echo "Level: $level"
echo "Message: $message"

# 字符串截取
data="key=value=extra"
echo "${data%%=*}"       # key（最大匹配）
echo "${data#*=}"        # value=extra（最小匹配）
echo "${data##*=}"       # extra（最大匹配）
```

---

### 第3节：模式匹配去头去尾（Pattern Matching: Strip Head & Tail）

#### 四种截取操作

| 语法 | 功能 | 匹配方式 |
|------|------|----------|
| `${var#pattern}` | 去头部（最短） | 从左向右，最小匹配 |
| `${var##pattern}` | 去头部（最长） | 从左向右，最大匹配 |
| `${var%pattern}` | 去尾部（最短） | 从右向左，最小匹配 |
| `${var%%pattern}` | 去尾部（最长） | 从右向左，最大匹配 |

```bash
# # 和 ##：去掉前缀
path="/home/user/docs/file.txt"
echo "${path#*/}"        # home/user/docs/file.txt（去掉第一个 / 及之前）
echo "${path##*/}"       # file.txt（去掉最后一个 / 及之前，等价于 basename）

# % 和 %%：去掉后缀
filename="archive.tar.gz"
echo "${filename%.*}"    # archive.tar（去掉最后一个 . 及之后）
echo "${filename%%.*}"   # archive（去掉第一个 . 及之后）

# 实用场景
filepath="/var/log/apache2/access.log"
echo "${filepath%/*}"    # /var/log/apache2（目录）
echo "${filepath##*/}"   # access.log（文件名）
echo "${filepath#*/}"    # var/log/apache2/access.log（去掉第一级）
```

#### 模式匹配规则

```bash
# 通配符
file="report-2024-01-15-final.pdf"
echo "${file#*-}"        # 2024-01-15-final.pdf
echo "${file##*-}"       # final.pdf
echo "${file%-*}"        # report-2024-01-15
echo "${file%%-*}"       # report

# 路径操作
full_path="/home/user/projects/bash/advanced.sh"
echo "${full_path##*/}"      # advanced.sh（文件名）
echo "${full_path%/*}"       # /home/user/projects/bash（目录）
echo "${full_path##*.}"      # sh（扩展名）
echo "${full_path##*/}"      # advanced.sh
echo "${full_path%/*}/"      # /home/user/projects/bash/
```

---

### 第4节：模式匹配替换（Pattern Matching: Substitution）

```bash
# ${var/pattern/replacement}：替换第一个匹配
str="hello world hello"
echo "${str/hello/Hi}"       # Hi world hello

# ${var//pattern/replacement}：替换所有匹配
echo "${str//hello/Hi}"      # Hi world Hi

# ${var/#pattern/replacement}：替换行首匹配
echo "${str/#hello/Hi}"      # Hi world hello

# ${var/%pattern/replacement}：替换行尾匹配
echo "${str/%hello/Hi}"      # hello world Hi

# 替换为空（删除）
echo "${str//hello/}"        #  world 

# 模式匹配
files="file1.txt file2.log file3.txt"
echo "${files//*.txt/}"      #  file2.log 
```

#### 替换实战

```bash
# URL 处理
url="https://api.example.com/v1/users"
echo "${url#https://}"       # api.example.com/v1/users
echo "${url##*/}"            # users
echo "${url#*/}"             # /api.example.com/v1/users

# 路径规范化
path="/home//user/../user/./docs/"
echo "${path//\///}"         # home..user..user..docs.
echo "${path//\/\//\/}"     # 简化连续斜杠

# 变量名构建
prefix="DB"
suffix="HOST"
varname="${prefix}_HOST"     # DB_HOST
echo "${!varname}"           # 引用变量值（间接引用）
```

---

### 第5节：大小写转换（Case Conversion）

```bash
# Bash 4.0+ 支持大小写转换
str="Hello World"

echo "${str^^}"      # HELLO WORLD（全部大写）
echo "${str,,}"      # hello world（全部小写）
echo "${str^}"       # Hello World（首字母大写）
echo "${str,}"       # hello World（首字母小写）

# 仅转换第一个字符
echo "${str^^}"      # HELLO World（Bash 4.4+ 不支持部分转换）
echo "${str,}"       # hello World

# 数组大小写转换
arr=("Hello" "World")
echo "${arr[@]^^}"   # HELLO WORLD
echo "${arr[@],,}"   # hello world
```

#### 大小写实战

```bash
# 配置文件键名规范化
key="my_config_key"
echo "${key^^}"      # MY_CONFIG_KEY
echo "${key^}"       # My_config_key

# 首字母大写
name="john"
echo "${name^}"      # John

# 全大写环境变量
env_var="production"
echo "${env_var^^}"  # PRODUCTION
```

---

### 第6节：数组展开（Array Expansion）

```bash
# 声明数组
arr=(apple banana cherry)

# 展开所有元素
echo "${arr[@]}"         # apple banana cherry
echo "${arr[*]}"         # apple banana cherry（单个字符串）

# 数组长度
echo "${#arr[@]}"        # 3

# 单个元素
echo "${arr[0]}"         # apple
echo "${arr[-1]}"        # cherry（Bash 4.3+）

# 切片
echo "${arr[@]:1:2}"     # banana cherry

# 追加
arr+=(date elderberry)

# 删除元素
unset 'arr[1]'

# 清空数组
arr=()

# 间接引用
idx=2
echo "${arr[$idx]}"      # cherry
```

#### 数组高级操作

```bash
# 关联数组
declare -A colors=([red]="#FF0000" [green]="#00FF00" [blue]="#0000FF")
echo "${colors[red]}"    # #FF0000
echo "${!colors[@]}"     # red green blue（所有键）
echo "${colors[@]}"      # 所有值
echo "${#colors[@]}"     # 3

# 数组与字符串互转
arr=(one two three)
IFS=','
echo "${arr[*]}"         # one,two,three

# 字符串转数组
str="one,two,three"
IFS=',' read -ra arr <<< "$str"
echo "${arr[@]}"         # one two three

# 数组过滤
arr=(1 2 3 4 5 6)
filtered=()
for item in "${arr[@]}"; do
    ((item % 2 == 0)) && filtered+=("$item")
done
echo "${filtered[@]}"    # 2 4 6
```

---

### 第7节：间接引用与变量名构建（Indirect Reference）

```bash
# ${!var}：间接引用
name="John"
ref="name"
echo "${!ref}"           # John

# 变量名构建
for i in 1 2 3; do
    declare "color_$i=red"
done
echo "${color_1}"        # red
echo "${color_2}"        # red

# 通过变量引用数组元素
idx=1
arr=(a b c d)
echo "${arr[$idx]}"      # b

# 动态变量名
set_var() {
    declare "var_${1}=${2}"
}
set_var "count" "42"
echo "$var_count"        # 42
```

#### 间接引用实战

```bash
# 配置系统
declare -A config=()
set_config() {
    config["$1"]="$2"
}
get_config() {
    echo "${config[$1]:-}"
}

set_config "db_host" "localhost"
set_config "db_port" "3306"
echo "Host: $(get_config db_host)"
echo "Port: $(get_config db_port)"

# 多语言支持
declare -A lang_en=([greeting]="Hello" [farewell]="Goodbye")
declare -A lang_zh=([greeting]="你好" [farewell]="再见")
current_lang="zh"
echo "${lang_${current_lang}[greeting]}"  # 你好
```

---

### 第8节：参数展开 vs 外部命令对比（Parameter Expansion vs External Commands）

| 操作 | 参数展开 | 外部命令 | 性能差异 |
|------|----------|----------|----------|
| 字符串长度 | `${#str}` | `echo -n "$str" \| wc -c` | ~100x |
| 子串截取 | `${str:0:5}` | `echo "$str" \| cut -c1-5` | ~50x |
| 去头去尾 | `${str##*/}` | `basename "$str"` | ~30x |
| 替换 | `${str//old/new}` | `echo "$str" \| sed 's/old/new/g'` | ~20x |
| 大小写 | `${str^^}` | `echo "$str" \| tr '[:lower:]' '[:upper:]'` | ~15x |
| 大小写转换 | `${str^^}` | `echo "$str" \| awk '{print toupper($0)}'` | ~25x |

```bash
# 性能测试示例
str="Hello World This Is A Test"

# 参数展开
time for i in {1..10000}; do
    result="${str^^}"
done

# 外部命令
time for i in {1..10000}; do
    result=$(echo "$str" | tr '[:lower:]' '[:upper:]')
done

# 结果：参数展开快 100-1000 倍
```

---

### 本章要点总结

- `${var:-default}` 提供默认值，`${var:?error}` 强制检查
- `${var#pattern}` / `${var##pattern}` 去头，`${var%pattern}` / `${var%%pattern}` 去尾
- `${var/pattern/replacement}` 模式替换，`//` 全局替换
- `${var^^}` / `${var,,}` 大小写转换（Bash 4.0+）
- `${arr[@]}` 展开数组，`${#arr[@]}` 获取长度
- 参数展开比外部命令快 100-1000 倍

---

**上一章**：[[07_子shell与命令替换：执行上下文|子 shell 与命令替换]]
**下一章**：[[09_陷阱与错误处理：errtrap_exittrap|陷阱与错误处理]]
