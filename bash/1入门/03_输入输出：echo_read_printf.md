# 输入输出：echo、read、printf (Input/Output: echo, read, printf)

## 章节概述

本章系统讲解 Bash 的输入输出机制：echo/printf 输出文本，read 接收用户输入，heredoc/herestring 构建多行文本，重定向控制数据流向。掌握这些工具是编写交互式脚本的基础。

> **核心理念**：Shell 的 I/O 就是三个数据流：标准输入(stdin)、标准输出(stdout)、标准错误(stderr)。所有 I/O 操作都是对这三个流的控制。

---

### 第1节：echo —— 最简单的输出

```bash
# 基本输出
echo "Hello, World!"

# 不换行输出 (-n)
echo -n "Loading..."
sleep 1
echo " done"

# 解析转义字符 (-e)
echo -e "Tab:\there"
echo -e "New\nline"
echo -e "Color:\033[31mRed\033[0m"
```

**echo 转义序列：**

| 序列 | 含义 |
|------|------|
| `\n` | 换行 |
| `\t` | 水平制表符 |
| `\\` | 反斜杠本身 |
| `\033[` | ANSI 转义码起始 |

**echo 的陷阱：**

```bash
# ✗ 不确定行为：不同实现对 -e 处理不同
echo -e "hello"

# ✓ 推荐：使用 $'...' 语法
$'hello\nworld'

# ✓ 或使用 printf
printf "hello\nworld\n"
```

---

### 第2节：printf —— 格式化输出

```bash
# 基本格式
printf "Name: %s\n" "Alice"
printf "Age: %d\n" 25
printf "Pi: %.2f\n" 3.14159

# 多个参数
printf "%s is %d years old\n" "Bob" 30

# 格式对齐
printf "%-10s %5d\n" "left" 100     # 左对齐
printf "%10s %5d\n" "right" 100     # 右对齐

# 填充
printf "%05d\n" 42                   # 00042
printf "%.3f\n" 3.14                 # 3.140
```

**printf 格式说明符：**

| 符号 | 类型 | 示例 |
|------|------|------|
| `%s` | 字符串 | `"hello"` |
| `%d` | 整数 | `42` |
| `%f` | 浮点数 | `3.14` |
| `%x` | 十六进制 | `ff` |
| `%o` | 八进制 | `77` |
| `%%` | 字面量 `%` | `%` |

**C printf 对比：**

```c
// C 的 printf 与 Bash 几乎相同
#include <stdio.h>
int main() {
    printf("Name: %s, Age: %d\n", "Alice", 25);
    printf("Pi: %.2f\n", 3.14159);
    return 0;
}
```

```bash
# Bash 等效
printf "Name: %s, Age: %d\n" "Alice" 25
printf "Pi: %.2f\n" 3.14159
```

---

### 第3节：read —— 接收用户输入

```bash
# 基本读取
echo "请输入你的名字:"
read name
echo "你好, $name!"

# 带提示的读取 (-p)
read -p "请输入你的年龄: " age
echo "你 $age 岁了"

# 静默读取 (-s)，用于密码
read -s -p "请输入密码: " password
echo ""
echo "密码长度: ${#password}"

# 超时读取 (-t)，单位秒
read -t 5 -p "5秒内输入: " answer
if [ -z "$answer" ]; then
    echo "超时了"
fi

# 限制输入长度 (-n)
read -n 1 -p "按任意键继续..." key
echo ""
```

**read 参数速查：**

| 参数 | 说明 | 示例 |
|------|------|------|
| `-p` | 显示提示信息 | `read -p "Name: " name` |
| `-s` | 静默输入（不回显） | `read -s -p "Pass: " pass` |
| `-t N` | 超时 N 秒 | `read -t 10 -p "Quick: " ans` |
| `-n N` | 限制读取 N 个字符 | `read -n 1 -p "Key: " key` |
| `-r` | 不处理反斜杠 | `read -r line` |
| `-a ARR` | 读入数组 | `read -a arr` |
| `-d CHAR` | 指定分隔符 | `read -d ':' val` |

---

### 第4节：命令替换 —— 反引号与 $()

```bash
# 反引号（旧写法）
current_date=`date +%Y-%m-%d`

# $() 语法（推荐）
current_date=$(date +%Y-%m-%d)

# 嵌套命令替换（$() 优势明显）
# 反引号嵌套需要转义，难以阅读
files=$(ls $(find /tmp -name "*.log" -maxdepth 1) 2>/dev/null)
```

**对比：**

| 特性 | 反引号 `` ` `` | `$(cmd)` |
|------|---------------|----------|
| 可读性 | 差（转义困难） | 好 |
| 嵌套 | 需要转义 | 自然嵌套 |
| 现代推荐 | 否 | 是 |

---

### 第5节：Heredoc 与 Herestring

```bash
# Heredoc：多行文本输入
cat << EOF
这是第一行
这是第二行
当前日期: $(date)
变量替换: $HOME
EOF

# Heredoc 禁止变量替换（加引号）
cat << 'EOF'
$HOME 不会被替换
$(date) 也不会被执行
EOF

# Herestring：字符串作为 stdin
grep "bash" <<< "I love bash scripting"

# 多行 herestring
grep -i "hello" <<< "Hello World"
```

**Heredoc 语法对比：**

| 语法 | 变量替换 | 命令替换 | 用途 |
|------|----------|----------|------|
| `<< EOF` | 是 | 是 | 动态文本 |
| `<< 'EOF'` | 否 | 否 | 静态文本/代码模板 |
| `<<- EOF` | 是 | 是 | 自动去除前导制表符 |

---

### 第6节：重定向详解

```bash
# 标准输出重定向
echo "hello" > output.txt        # 覆盖写入
echo "world" >> output.txt       # 追加写入

# 标准错误重定向
ls /nonexistent 2> error.log     # 错误写入文件
ls /nonexistent 2>> error.log    # 错误追加

# 合并 stdout 和 stderr
command > all.log 2>&1           # 传统写法
command &> all.log               # 简写 (Bash 4+)

# 丢弃所有输出
command > /dev/null 2>&1

# 重定向 stdin
wc -l < /etc/passwd

# Here-document 重定向
cat > config.txt << EOF
server=192.168.1.1
port=8080
EOF
```

**文件描述符：**

| 描述符 | 名称 | 说明 |
|--------|------|------|
| 0 | stdin | 标准输入 |
| 1 | stdout | 标准输出 |
| 2 | stderr | 标准错误 |

```bash
# 高级重定向
# 同时重定向 stdout 和 stderr 到不同文件
command > out.log 2> err.log

# 重定向 stdout 到文件，stderr 到终端
command > out.log 2>&1

# 重定向到多个文件 (tee)
echo "log message" | tee file1.txt | tee file2.txt
```

---

### 第7节：实战示例 —— 交互式菜单

```bash
#!/usr/bin/env bash

echo "==================="
echo "   系统信息查看器   "
echo "==================="

echo "1) 查看系统信息"
echo "2) 查看磁盘使用"
echo "3) 查看内存使用"
echo "4) 退出"

read -p "请选择 [1-4]: " choice

case $choice in
    1) uname -a ;;
    2) df -h ;;
    3) free -h ;;
    4) echo "再见！"; exit 0 ;;
    *) echo "无效选项" ;;
esac
```

**C 语言对比（菜单程序）：**

```c
#include <stdio.h>
int main() {
    int choice;
    printf("1) 查看系统信息\n");
    printf("2) 查看磁盘使用\n");
    printf("请选择: ");
    scanf("%d", &choice);
    switch (choice) {
        case 1: system("uname -a"); break;
        case 2: system("df -h"); break;
        default: printf("无效选项\n");
    }
    return 0;
}
```

---

### 第8节：课后练习

1. 编写脚本，用 `read` 接收姓名和年龄，用 `printf` 格式化输出个人信息卡片
2. 编写一个交互式计算器，支持加减乘除
3. 使用 heredoc 生成一个包含日期和主机名的 HTML 报告

**相关章节：**
- [[../02_变量与数据类型：字符串_整数_数组|上一章：变量与数据类型]]
- [[../04_条件判断：if_case_test|下一章：条件判断]]
