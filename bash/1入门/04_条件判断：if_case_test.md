# 条件判断：if、case、test (Conditional Logic)

## 章节概述

本章系统讲解 Bash 的条件判断机制：if/elif/else 分支、test 命令与 `[[ ]]` 语法、文件测试运算符、字符串比较、数值比较，以及 case 模式匹配。

> **核心理念**：Bash 的条件判断基于"退出状态码"——命令成功返回 0 为真，非 0 为假。这与 C 语言的"非零为真"恰好相反。

---

### 第1节：if/elif/else 基础

```bash
if [ condition ]; then
    echo "条件为真"
fi

score=85
if [ $score -ge 90 ]; then
    grade="A"
elif [ $score -ge 80 ]; then
    grade="B"
elif [ $score -ge 70 ]; then
    grade="C"
else
    grade="D"
fi
```

| 要素 | 要求 |
|------|------|
| 条件前后 | 必须有空格 |
| `then` | 可换行或用 `;` |
| `fi` | 必须单独一行 |

---

### 第2节：test 命令与 [ ] vs [[ ]]]

```bash
test -f /etc/passwd && echo "存在"
[ -f /etc/passwd ] && echo "存在"
[[ -f /etc/passwd ]] && echo "存在"
```

| 特性 | `[ ]` | `[[ ]]` |
|------|-------|---------|
| POSIX | 是 | 否 |
| 正则 `=~` | 不支持 | 支持 |
| 变量引用 | 需引号 | 可省略 |

```bash
email="user@test.com"
[[ $email =~ ^[a-zA-Z0-9]+@ ]] && echo "有效"
```

---

### 第3节：文件测试运算符

| 运算符 | 含义 | 运算符 | 含义 |
|--------|------|--------|------|
| `-e` | 文件存在 | `-f` | 普通文件 |
| `-d` | 目录 | `-L` | 符号链接 |
| `-r` | 可读 | `-w` | 可写 |
| `-x` | 可执行 | `-s` | 非空 |
| `-nt` | 更新 | `-ot` | 更旧 |
| `-ef` | 同一 inode | `-c` | 字符设备 |
| `-b` | 块设备 | `-p` | 命名管道 |

```bash
# 实用文件检查脚本
target="/etc/passwd"
[ -e "$target" ] || { echo "不存在"; exit 1; }
[ -f "$target" ] && echo "是普通文件"
[ -d "$target" ] && echo "是目录"
[ -r "$target" ] && echo "可读"
[ -w "$target" ] && echo "可写"
[ -x "$target" ] && echo "可执行"
[ -s "$target" ] && echo "非空（$(( $(wc -c < "$target") )) 字节）"
```

---

### 第4节：字符串比较

| 运算符 | 含义 |
|--------|------|
| `=` / `==` | 相等 |
| `!=` | 不等 |
| `<` | 字典序小于 |
| `>` | 字典序大于 |
| `-z` | 空串 |
| `-n` | 非空 |

```bash
name=""
[ "$name" = "hello" ]    # 加引号安全
[[ $name = "hello" ]]    # [[ ]] 无需引号
```

---

### 第5节：数值比较

```bash
a=10; b=20
[ $a -eq $b ]      # 等于
[ $a -ne $b ]      # 不等于
[ $a -gt $b ]      # 大于
[ $a -lt $b ]      # 小于

# 更直观的写法
(( a == b ))
(( a > b ))
(( a < b ))
```

> **推荐**：数值比较优先用 `(( ))`，语法更接近 C。

---

### 第6节：逻辑组合

```bash
[[ $age -ge 18 && $age -le 65 ]] && echo "劳动年龄"
[[ $a -eq 0 || $a -eq 100 ]] && echo "边界值"
[ ! -f file ] && echo "文件不存在"
```

| 逻辑 | `[ ]` | `[[ ]]` |
|------|-------|---------|
| 与 | `-a` | `&&` |
| 或 | `-o` | `\|\|` |
| 非 | `!` | `!` |

---

### 第7节：case 语句

```bash
filename="report.pdf"
case "$filename" in
    *.txt)       echo "文本文件" ;;
    *.pdf)       echo "PDF 文档" ;;
    *.jpg|*.png) echo "图片文件" ;;
    *)           echo "未知类型" ;;
esac
```

**C switch 对比：**

```c
// C：仅限整数常量
switch (choice) {
    case 1: printf("A\n"); break;
    case 2: printf("B\n"); break;
    default: printf("Other\n");
}
```

```bash
# Bash：支持通配符和正则模式
case "$input" in
    [Yy]*)        echo "确认" ;;
    [Nn]*)        echo "否定" ;;
    [0-9]*)       echo "数字" ;;
    *.sh)         echo "脚本" ;;
    [a-z]*[A-Z]*) echo "混合大小写" ;;
    *)            echo "其他" ;;
esac
```

---

### 第8节：条件判断常见模式

```bash
# 1. 参数检查
[ $# -lt 2 ] && { echo "用法: $0 <src> <dst>"; exit 1; }

# 2. 文件存在性检查
[ -f "$1" ] || die "文件不存在: $1"

# 3. 环境变量检查
[ -z "$HOME" ] && { export HOME=/root; }

# 4. 命令存在性检查
command -v git >/dev/null 2>&1 || { echo "需要安装 git"; exit 1; }

# 5. 网络连通性检查
ping -c 1 -W 2 8.8.8.8 >/dev/null 2>&1 && echo "网络通" || echo "网络不通"
```

---

### 第9节：课后练习

1. 编写脚本检查 `/etc/passwd` 是否存在、可读、非空
2. 用 case 实现根据参数选择压缩格式（tar/gz/bz2/xz）
3. 验证邮箱格式的正则匹配

**相关章节：**
- [[../03_输入输出：echo_read_printf|上一章：输入输出]]
- [[../05_循环：for_while_until|下一章：循环]]
