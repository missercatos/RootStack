# sed 流编辑器：增删改查、多行处理（sed Stream Editor: CRUD & Multi-line）

## 章节概述

本章全面讲解 `sed` 流编辑器的核心功能，包括地址定位、增删改查操作、多命令组合、模式空间与保持空间的工作机制，以及与 C 语言字符串操作的对比。`sed` 是构建文本处理流水线的关键工具。

> **核心理念**：sed 是一个基于模式匹配的非交互式流编辑器，它的核心是"读取-匹配-执行-输出"循环，理解模式空间是掌握 sed 的关键。

---

### 第1节：sed 基础语法（sed Basic Syntax）

```bash
# 基本结构
sed [options] 'command' file
sed [options] -e 'command1' -e 'command2' file
sed [options] -f script.sed file

# 常用选项
sed -n 'p' file          # -n 抑制默认输出
sed -i 's/old/new/' file # -i 原地编辑（macOS 需 -i ''）
sed -E 's/pattern/repl/' file  # -E 启用 ERE
```

#### 地址语法

| 地址类型 | 语法 | 示例 | 说明 |
|----------|------|------|------|
| 行号 | `n` | `sed '3d'` | 第 3 行 |
| 行号范围 | `n,m` | `sed '2,5d'` | 第 2-5 行 |
| 最后一行 | `$` | `sed '$d'` | 最后一行 |
| 正则匹配 | `/regex/` | `sed '/^#/d'` | 匹配的行 |
| 范围 | `addr1,addr2` | `sed '/BEGIN/,/END/d'` | 范围删除 |
| 步进 | `~` | `sed '1~2d'` | 奇数行 |
| 地址取反 | `!` | `sed '/^#/!d'` | 不匹配的行 |

---

### 第2节：增删改查操作（CRUD Operations）

#### 查（p 打印）

```bash
# 打印特定行
sed -n '5p' file.txt          # 第 5 行
sed -n '1,10p' file.txt       # 前 10 行
sed -n '/error/p' file.txt    # 包含 error 的行

# 打印并显示行号
sed -n '/pattern/{=;p}' file.txt

# 打印范围外的行
sed -n '1,5!p' file.txt       # 除了 1-5 行
```

#### 删（d 删除）

```bash
# 删除行
sed '3d' file.txt              # 删除第 3 行
sed '1,5d' file.txt            # 删除前 5 行
sed '/^$/d' file.txt           # 删除空行
sed '/^#/d' file.txt           # 删除注释行
sed '$d' file.txt              # 删除最后一行

# 删除范围
sed '/BEGIN/,/END/d' file.txt  # 删除 BEGIN 到 END
sed '1d' file.txt              # 删除第一行
```

#### 改（s 替换）

```bash
# 基本替换
sed 's/old/new/' file.txt          # 每行第一个
sed 's/old/new/g' file.txt         # 所有匹配
sed 's/old/new/gi' file.txt        # 全局 + 忽略大小写

# 地址限定替换
sed '1s/old/new/' file.txt         # 仅第 1 行
sed '/^server/s/port/8080/' file.txt  # 仅 server 行

# 使用不同分隔符（处理路径）
sed 's|/usr/local|/opt|g' file.txt
sed 's#http://#https://#g' file.txt
```

#### 改（c 整行替换 / a 追加 / i 插入）

```bash
# c：替换整行
sed '/^server/c\server_name example.com;' nginx.conf

# a：在匹配行后追加
sed '/^server/a\    charset utf-8;' nginx.conf

# i：在匹配行前插入
sed '/^server/i\# Server configuration' nginx.conf

# 多行追加（使用 \n）
sed '/^server/a\    location / {\n        proxy_pass http://backend;\n    }' nginx.conf
```

---

### 第3节：替换高级技巧（Advanced Substitution）

#### 反向引用

```bash
# 交换字段
echo "John:Doe:30" | sed -E 's/([^:]+):([^:]+):(.+)/\2:\1:\3/'
# 输出：Doe:John:30

# 给第一个单词加引号
echo "hello world" | sed -E 's/(\w+)/"\1"/'
# 输出："hello" world

# 提取子字符串
echo "2024-01-15" | sed -E 's/([0-9]{4})-([0-9]{2})-([0-9]{2})/\1年\2月\3日/'
```

#### 特殊替换字符

| 字符 | 含义 | 示例 |
|------|------|------|
| `&` | 匹配的文本 | `sed 's/pattern/[&]/'` |
| `\l` | 下一个字符小写 | `sed 's/\(.\)/\l\1/'` |
| `\u` | 下一个字符大写 | `sed 's/\(.\)/\u\1/'` |
| `\L` | 后续字符小写 | `sed 's/.*/\L&/'` |
| `\U` | 后续字符大写 | `sed 's/.*/\U&/'` |
| `\E` | 结束大小写转换 | `sed 's/\U\1\E rest/\u\1/'` |

#### 替换修饰符

```bash
# g：全局替换（每行所有匹配）
sed 's/old/new/g' file.txt

# 数字：替换第 n 个匹配
sed 's/old/new/2' file.txt      # 第 2 个匹配

# p：替换成功时打印
sed -n 's/old/new/p' file.txt

# w：替换成功时写入文件
sed 's/old/new/w matches.txt' file.txt

# 组合使用
sed 's/old/new/giw changed.txt' file.txt
```

---

### 第4节：多命令处理（Multi-command Processing）

```bash
# 分号分隔（对同一行执行多个命令）
sed 's/foo/bar/g; s/baz/qux/g' file.txt

# 花括号分组
sed '/^server/{s/port/8080/; s/host/localhost/}' nginx.conf

# -e 多表达式
sed -e 's/foo/bar/' -e 's/baz/qux/' file.txt

# 地址 + 命令组合
sed -n '/^BEGIN/,/^END/{/^#/d; s/old/new/g; p}' file.txt
```

#### 执行顺序

```bash
# sed 按行读取，对每行依次执行所有命令
echo "hello" | sed 's/h/H/; s/o/O/; s/l/L/; s/o/O/'
# 输出：HELLo（每条命令依次处理同一行）

# 条件执行
sed '/pattern/{s/old/new/; w modified.txt}' file.txt
```

---

### 第5节：模式空间与保持空间（Pattern & Hold Space）

`sed` 有两个内部缓冲区：

| 缓冲区 | 默认值 | 作用 | 命令 |
|--------|--------|------|------|
| 模式空间 | 当前处理行 | 匹配和操作 | 默认工作区 |
| 保持空间 | 空行 `\n` | 临时存储 | `h`, `H`, `g`, `G`, `x` |

#### 空间操作命令

| 命令 | 功能 | 说明 |
|------|------|------|
| `h` | 复制到保持空间 | 覆盖 |
| `H` | 追加到保持空间 | 带 `\n` |
| `g` | 从保持空间复制到模式空间 | 覆盖 |
| `G` | 从保持空间追加到模式空间 | 带 `\n` |
| `x` | 交换模式空间和保持空间 | 互换 |

#### 多行处理示例

```bash
# 合并连续两行
sed 'N;s/\n/ /' file.txt

# 反转文件（tac）
sed '1!G;h;$!d' file.txt

# 删除连续空行（保留一个）
sed '/^$/N;/^\n$/d' file.txt

# 在匹配行后追加内容
sed '/pattern/G' file.txt

# 交换相邻两行
sed 'N;s/\(.*\)\n\(.*\)/\2\n\1/' file.txt
```

#### hold space 实战

```bash
# 收集所有匹配行，最后输出
sed -n '/error/{H; $ {x; s/\n//g; p}}' logfile.txt

# 在文件开头插入内容
sed '1{H; $!d}; ${x; s/\n//; p}' header.txt file.txt
```

---

### 第6节：sed 脚本与文件操作（sed Scripting）

```bash
# 创建 sed 脚本文件
echo 's/old/new/g' > transform.sed
echo '/^#/d' >> transform.sed
echo '/^$/d' >> transform.sed

# 执行脚本
sed -f transform.sed input.txt

# 地址 + 命令脚本
cat > cleanup.sed << 'ENDOFSED'
# 删除注释行
/^#/d
# 删除空行
/^$/d
# 替换所有 tabs 为空格
s/\t/    /g
ENDOFSED

sed -f cleanup.sed config.txt
```

---

### 第7节：sed 实战模式（sed Practical Patterns）

```bash
# 批量文件替换
find . -name "*.conf" -exec sed -i 's/old_server/new_server/g' {} +

# 配置文件修改
sed -i '/^#max_connections/s/=.*/= 1000/' my.cnf

# 删除指定范围的行
sed '/BEGIN_CONFIG/,/END_CONFIG/d' config.txt

# 提取两个标记之间的内容
sed -n '/BEGIN/,/END/p' data.txt

# 在指定行后插入多行
sed '3a\line4\nline5\nline6' file.txt

# 合并多行为一行
sed ':a; N; $!ba; s/\n/ /g' long.txt

# 删除文件最后 n 行
sed -n -e :a -e '1,10!{P;N;D;};N;ba' file.txt
```

---

### 第8节：sed vs C 字符串操作对比（sed vs C String Operations）

| 操作 | sed | C 语言 |
|------|-----|--------|
| 查找替换 | `sed 's/old/new/g'` | `strstr()` + `strcpy()` |
| 正则匹配 | `sed '/regex/p'` | `regexec()` |
| 删除行 | `sed '/pattern/d'` | 手动过滤 |
| 字段分割 | `sed 's/[^:]*//2'` | `strtok()` |
| 大小写转换 | `sed 's/.*/\U&/'` | `toupper()` |
| 字符串截取 | `sed 's/\(.\{5\}\).*/\1/'` | `strncpy()` |

```c
// C: 替换所有匹配（手动实现）
void replace_all(char *str, const char *old, const char *new) {
    char buffer[1024];
    char *p = strstr(str, old);
    while (p) {
        strncpy(buffer, str, p - str);
        buffer[p - str] = '\0';
        sprintf(buffer + (p - str), "%s%s", new, p + strlen(old));
        strcpy(str, buffer);
        p = strstr(str + strlen(new), old);
    }
}

// sed: sed 's/old/new/g' file.txt
// 简洁性差距明显
```

---

### 本章要点总结

- `sed` 地址支持行号、正则、范围、步进
- `s/old/new/g` 是最常用的替换命令
- `-n` + `p` 组合用于精确输出
- 模式空间和保持空间是多行处理的关键
- `-i` 原地编辑需谨慎，建议先备份
- 花括号 `{}` 用于命令分组，分号 `;` 用于命令分隔

---

**上一章**：[[03_正则表达式：grep_sed_awk中的正则|正则表达式]]
**下一章**：[[05_awk文本处理：字段分割_数组_END块|awk 文本处理]]
