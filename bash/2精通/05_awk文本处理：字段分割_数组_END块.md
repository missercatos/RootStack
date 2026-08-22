# awk 文本处理：字段分割、数组、END 块（awk Text Processing: Fields, Arrays, END Block）

## 章节概述

本章深入讲解 `awk` 的核心机制——模式匹配与动作执行、字段分割、内置变量、BEGIN/END 块、关联数组以及自定义函数。`awk` 是 Bash 文本处理工具链中最强大的工具之一，其语法结构类似 C 语言。

> **核心理念**：awk 的设计哲学是"逐行扫描 + 模式匹配 + 字段操作"，BEGIN/END 块提供了初始化和汇总的天然钩子。

---

### 第1节：awk 基本语法（awk Basic Syntax）

```bash
# 基本结构
awk 'pattern {action}' file
awk -F: 'pattern {action}' file    # 指定字段分隔符
awk -v var=value 'pattern {action}' file  # 传递变量

# 单引号规则
awk '{print $1}' file              # 正确
awk "{print $1}" file              # 错误！$1 会被 shell 展开
```

#### 执行流程

```
┌─────────────────────────────┐
│  1. 执行 BEGIN 块（仅一次）   │
│  2. 逐行读取输入              │
│     ├─ 匹配 pattern？         │
│     │   └─ 是：执行 action    │
│     └─ 否：跳过              │
│  3. 执行 END 块（仅一次）     │
└─────────────────────────────┘
```

#### 模式匹配

```bash
# 关系模式
awk 'NR == 5' file.txt              # 第 5 行
awk 'NR >= 3 && NR <= 10' file.txt  # 第 3-10 行
awk 'NR == 1 || NR == NF' file.txt  # 第 1 行或最后字段

# 正则模式
awk '/error/' file.txt               # 包含 error 的行
awk '$3 ~ /^[0-9]+$/' file.txt       # 第 3 字段为纯数字
awk '$0 !~ /^#/' file.txt            # 非注释行

# 组合模式
awk '/error/ && /timeout/' file.txt
awk '/error/ || /critical/' file.txt
awk '!/debug/' file.txt
```

---

### 第2节：字段与记录（Fields & Records）

#### 字段操作

```bash
# $0 = 整行, $1 $2 ... $NF = 各字段
awk '{print $1, $3}' file.txt
awk -F: '{print $1, $3}' /etc/passwd

# NF = 字段数量
echo "a b c" | awk '{print NF}'     # 输出 3
echo "a b c" | awk '{print $NF}'    # 输出 c（最后一个字段）

# 修改字段
awk '{$2 = "NEW"; print}' file.txt

# 输出带分隔符
awk -F: '{OFS=":"; print $1, $3}' /etc/passwd
```

#### 记录分隔

```bash
# RS：记录分隔符（默认换行）
echo "a:b:c:d" | awk -F: 'BEGIN{RS=":"} {print}'
# 输出：
# a
# b
# c
# d

# 用 RS 处理多行记录
awk 'BEGIN{RS=""} {print "Paragraph:", NR}' paragraphs.txt
```

---

### 第3节：内置变量（Built-in Variables）

| 变量 | 含义 | 示例值 |
|------|------|--------|
| `NR` | 当前行号（全局） | `1`, `2`, ... |
| `NF` | 当前行字段数 | `3`, `5`, ... |
| `NR`/`FNR` | 全局行号/文件内行号 | 多文件时区分 |
| `FS` | 输入字段分隔符 | `:` ` ` `\t` |
| `OFS` | 输出字段分隔符 | `,` ` ` `:` |
| `RS` | 输入记录分隔符 | `\n` |
| `ORS` | 输出记录分隔符 | `\n` |
| `FILENAME` | 当前文件名 | `data.txt` |
| `OFMT` | 数字输出格式 | `%.6g` |
| `CONVFMT` | 数字转换格式 | `%.6g` |

```bash
# NR vs FNR（多文件处理）
awk 'FNR == NR {count[$1]++; next} {print $0, count[$1]}' file1 file2

# 自定义字段分隔
awk -F'[:/]' '{print $1, $2}' path/to/file

# 修改输出分隔符
awk 'BEGIN{OFS="\t"} {print $1, $2}' data.txt
```

---

### 第4节：BEGIN 与 END 块（BEGIN & END Blocks）

```bash
# BEGIN：初始化（在读取任何输入之前执行）
awk 'BEGIN {print "Start"; FS=":"} {print $1}' /etc/passwd

# END：汇总（在所有输入处理完毕后执行）
awk '{sum += $1} END {print "Total:", sum}' numbers.txt

# 组合使用
awk 'BEGIN {print "Name\tScore"} {print $1, $2} END {print "---"}' scores.txt
```

#### 统计报表示例

```bash
# 按部门统计平均工资
awk -F, 'BEGIN {
    print "Department    Average Salary"
    print "================================"
}
{
    dept = $3
    total[dept] += $2
    count[dept]++
}
END {
    for (d in total)
        printf "%-14s $%.2f\n", d, total[d]/count[d]
}' employees.csv
```

---

### 第5节：关联数组（Associative Arrays）

awk 的数组是关联数组（类似 Python 的 dict），键为字符串。

```bash
# 声明与使用
awk '{count[$1]++} END {for (k in count) print k, count[k]}' file.txt

# 遍历数组
awk '{a[$1]=$2} END {for (k in a) print k, a[k]}' data.txt

# 检查键是否存在
awk '{if ($1 in seen) print "Duplicate:", $1; seen[$1]=1}' file.txt

# 删除数组元素
awk '{delete a[$1]}' file.txt

# 数组长度
awk '{a[$1]} END {print length(a)}' file.txt
```

#### 多维数组（模拟）

```bash
# awk 用字符串连接模拟多维数组
awk '{
    key = $1 SUBSEP $2
    count[key]++
}
END {
    for (k in count)
        print k, count[k]
}' data.txt

# 或使用 @group 语法（gawk 4.0+）
awk '@group {count[$1][$2]++} END {for (i in count) for (j in count[i]) print i, j, count[i][j]}' data.txt
```

---

### 第6节：自定义函数（Custom Functions）

```bash
# 函数定义
awk '
function abs(x) {
    return (x < 0) ? -x : x
}
function max(a, b) {
    return (a > b) ? a : b
}
function min(a, b) {
    return (a < b) ? a : b
}
{
    print max($1, $2), min($1, $2), abs($1 - $2)
}' numbers.txt
```

#### 函数高级特性

```bash
# 局部变量（使用额外参数）
awk '
function count_words(line,    words, i) {
    n = split(line, words)
    return n
}
{
    print count_words($0)
}' file.txt

# 递归函数
awk '
function factorial(n) {
    if (n <= 1) return 1
    return n * factorial(n - 1)
}
{ print $1, "factorial =", factorial($1) }
' numbers.txt
```

#### 函数 vs C 函数对比

| 特性 | awk 函数 | C 函数 |
|------|----------|--------|
| 返回值 | `return expr` | `return expr` |
| 局部变量 | 额外空参数声明 | 局部声明 |
| 参数传递 | 值传递 | 值/指针 |
| 数组 | 内置关联数组 | 需手动管理 |
| 字符串 | 原生支持 | `char*` 手动管理 |
| 正则 | `~` `!~` 运算符 | `regexec()` |

---

### 第7节：awk 格式化输出（awk Formatted Output）

```bash
# printf 格式化
awk '{printf "%-20s %10d %8.2f\n", $1, $2, $3}' data.txt

# 常用格式符
# %s  字符串    %d  整数    %f  浮点数
# %e  科学计数  %x  十六进制 %o  八进制

# 对齐与宽度
awk '{printf "%-10s | %10d | %8.2f%%\n", $1, $2, $3}' report.txt

# 输出到文件
awk '{print $1 > "names.txt"; print $2 > "scores.txt"}' data.txt

# 追加输出
awk '{print $1 >> "log.txt"}' new_data.txt
```

---

### 第8节：awk 实战模式（awk Practical Patterns）

```bash
# 日志分析
awk '/ERROR/ {errors++} /WARN/ {warns++} END {print "Errors:", errors, "Warnings:", warns}' app.log

# CSV 处理
awk -F, 'NR>1 {total+=$2; count++} END {print "Avg:", total/count}' data.csv

# 去重
awk '!seen[$0]++' file.txt

# 字段重排
awk -F, '{print $3, $1, $2}' data.csv

# 条件累加
awk '/success/ {s++} /fail/ {f++} END {print "Success:", s, "Fail:", f}' results.log

# 生成报告
awk 'BEGIN {print "Report Generated:", strftime("%Y-%m-%d")} {print} END {print "Total lines:", NR}' data.txt

# 多文件关联
awk 'FNR==NR {a[$1]=$2; next} ($1 in a) {print $0, a[$1]}' file1.txt file2.txt

# 分组统计
awk -F: '{group[$1]++} END {for (g in group) print g, group[g]}' /etc/passwd
```

---

### 第9节：awk vs C 处理对比（awk vs C Processing）

| 任务 | awk | C |
|------|-----|---|
| 逐行读取 | 自动 | `fgets()` 循环 |
| 字段分割 | `$1 $2` 或 `-F` | `strtok()` |
| 关联数组 | `a[key]=val` | `hashmap` 库 |
| 格式化输出 | `printf` | `printf` |
| 正则匹配 | `~` 运算符 | `regexec()` |
| 文件输出 | `> file` | `fopen()` |

```c
// C: 简单字段处理
#include <stdio.h>
#include <string.h>

int main() {
    char line[1024];
    while (fgets(line, sizeof(line), stdin)) {
        char *token = strtok(line, ":");
        int field = 1;
        while (token) {
            if (field == 1) printf("%s\n", token);
            token = strtok(NULL, ":");
            field++;
        }
    }
    return 0;
}

// awk: awk -F: '{print $1}' file.txt
```

---

### 本章要点总结

- `awk 'pattern {action}'` 是基本语法结构
- `$1`-`$NF` 访问字段，`NR`/`NF`/`FS`/`OFS` 是核心内置变量
- `BEGIN` 块用于初始化，`END` 块用于汇总
- 数组是关联数组，`for (k in arr)` 遍历
- 函数使用额外空参数声明局部变量
- `printf` 提供格式化输出控制

---

**上一章**：[[04_sed流编辑器：增删改查_多行处理|sed 流编辑器]]
**下一章**：[[06_调试与性能：set_-x_shellcheck_profiling|调试与性能]]
