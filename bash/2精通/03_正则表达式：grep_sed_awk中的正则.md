# 正则表达式：grep、sed、awk 中的正则（Regular Expressions in grep, sed, awk）

## 章节概述

本章深入讲解 Bash 生态中的正则表达式体系，对比 BRE、ERE、PCRE 三种语法标准，详细解析元字符、分组与反向引用，并展示它们在 `grep`、`sed`、`awk` 中的实际应用差异。

> **核心理念**：正则表达式是文本模式匹配的通用语言，掌握 BRE/ERE/PCRE 的差异是高效文本处理的前提。

---

### 第1节：正则表达式基础（Regex Fundamentals）

#### 三种语法标准

| 标准 | 全称 | 特殊字符 | 工具支持 |
|------|------|----------|----------|
| BRE | Basic Regular Expression | `( )` `{ }` `\+` `\?` 需转义 | `grep`, `sed` |
| ERE | Extended Regular Expression | `()` `{}` `+` `?` 直接使用 | `grep -E`, `sed -E`, `awk` |
| PCRE | Perl Compatible Regex | `(?:...)` `(?!...)` `\d` `\w` 等 | `grep -P` |

#### 元字符一览表

| 元字符 | 含义 | 示例 | 匹配 |
|--------|------|------|------|
| `.` | 任意单字符（非换行） | `a.c` | `abc`, `aXc` |
| `*` | 前项零次或多次 | `ab*c` | `ac`, `abc`, `abbc` |
| `+` | 前项一次或多次（ERE/PCRE） | `ab+c` | `abc`, `abbc` |
| `?` | 前项零次或一次 | `colou?r` | `color`, `colour` |
| `^` | 行首锚定 | `^Start` | 以 Start 开头的行 |
| `$` | 行尾锚定 | `end$` | 以 end 结尾的行 |
| `[ ]` | 字符类 | `[aeiou]` | 元音字母 |
| `[^ ]` | 否定字符类 | `[^0-9]` | 非数字 |
| `{n,m}` | 重复次数 | `a{2,4}` | `aa`, `aaa`, `aaaa` |
| `\|` | 或（交替） | `cat\|dog` | cat 或 dog |
| `( )` | 分组 | `(ab)+` | `ab`, `abab` |
| `\b` | 单词边界 | `\bword\b` | 独立的 word |

---

### 第2节：grep 正则实战（grep Regex in Practice）

```bash
# BRE（默认）：分组和量词需转义
grep 'ab\{2,4\}' file.txt

# ERE：更简洁
grep -E 'ab{2,4}' file.txt
grep -E 'cat|dog' file.txt
grep -E '(foo)+bar' file.txt

# PCRE：最强大
grep -P '\d{3}-\d{4}' file.txt          # 匹配电话格式
grep -P '(?!TODO)' file.txt             # 负向前瞻
grep -P '\b\w+@\w+\.\w+\b' file.txt    # 邮箱模式

# 常用 grep 正则选项
grep -i "pattern" file        # 忽略大小写
grep -v "pattern" file        # 反向匹配
grep -c "pattern" file        # 计数
grep -l "pattern" *.txt       # 仅显示文件名
grep -n "pattern" file        # 显示行号
grep -o "pattern" file        # 仅显示匹配部分
grep -A3 "pattern" file       # 显示匹配后3行
grep -B3 "pattern" file       # 显示匹配前3行
grep -C3 "pattern" file       # 显示匹配前后3行
```

#### grep 正则实战示例

```bash
# 查找以 # 开头的注释行（非空行）
grep -E '^\s*#' config.conf | grep -v '^$'

# 查找 IP 地址
grep -P '\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b' file.txt

# 查找日期格式 YYYY-MM-DD
grep -P '\b\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])\b' file.txt

# 查找连续重复单词
grep -P '\b(\w+)\s+\1\b' file.txt

# 查找包含特殊字符的行
grep -F 'literal.string.with.dots' file.txt  # -F 禁用正则
```

---

### 第3节：sed 正则实战（sed Regex in Practice）

```bash
# BRE（默认）
sed 's/old/new/' file.txt
sed 's/\(foo\)\(bar\)/\2\1/' file.txt    # 交换 foo 和 bar

# ERE（-E 或 -r）
sed -E 's/(foo)(bar)/\2\1/' file.txt

# sed 中的元字符
sed 's/a.b/xxx/g' file.txt        # . 匹配任意字符
sed 's/ab*/xxx/g' file.txt        # * 零次或多次
sed 's/[0-9]//g' file.txt         # 删除数字
sed 's/^[[:space:]]*//' file.txt  # 删除前导空白
```

#### sed 正则高级用法

```bash
# 地址范围 + 正则
sed '/^BEGIN/,/^END/d' file.txt        # 删除 BEGIN 到 END 之间的内容
sed '/^server {/,/^}/s/charset.*/charset utf-8;/' nginx.conf

# 分组与反向引用
sed -E 's/([0-9]{4})-([0-9]{2})-([0-9]{2})/\3\/\2\/\1/' dates.txt

# 条件替换
sed -E '/^[0-9]+$/s/^/ID: /' file.txt   # 仅对数字行添加前缀

# 多行模式空间
sed -N 's/\n/ /g' file.txt              # 合并相邻两行
```

---

### 第4节：awk 正则实战（awk Regex in Practice）

```bash
# awk 使用 ERE 语法
awk '/pattern/ {print $1}' file.txt
awk '$0 ~ /^[0-9]+$/' file.txt          # 全行为数字
awk '!/^#/' file.txt                     # 过滤注释行

# awk 正则 vs 字符串匹配
awk '$3 == "error"' file.txt             # 精确匹配
awk '$3 ~ /error/' file.txt              # 正则匹配
awk '$3 !~ /debug/' file.txt             # 正则否定匹配
```

#### awk 正则高级用法

```bash
# 使用正则分割字段
echo "key=value" | awk -F'[=:]' '{print $1, $2}'

# 多条件正则
awk '/error/ && /timeout/' logfile.txt
awk '/error/ || /critical/' logfile.txt

# 正则捕获组（需用 match 函数）
echo "2024-01-15" | awk '{
    match($0, /([0-9]{4})-([0-9]{2})-([0-9]{2})/, arr)
    print "Year:", arr[1], "Month:", arr[2], "Day:", arr[3]
}'

# 字段级正则
awk '{gsub(/old/, "new"); print}' file.txt
awk 'BEGIN{FS="[ \t]+"} {print $NF}' file.txt  # 最后一个字段
```

---

### 第5节：分组与反向引用（Groups & Back-references）

#### 分组语法对比

| 特性 | BRE | ERE | PCRE |
|------|-----|-----|------|
| 普通分组 | `\(ab\)` | `(ab)` | `(ab)` |
| 非捕获分组 | — | — | `(?:ab)` |
| 命名分组 | — | — | `(?<name>ab)` |
| 反向引用 | `\1` `\2` | `\1` `\2` | `\1` `\k<name>` |
| 前瞻 | — | — | `(?=ab)` `(?!ab)` |
| 后顾 | — | — | `(?<=ab)` `(?<!ab)` |

#### 反向引用实战

```bash
# grep：查找重复单词
grep -P '\b(\w+)\s+\1\b' file.txt

# sed：交换字段
echo "hello world" | sed -E 's/(\w+) (\w+)/\2 \1/'
# 输出：world hello

# sed：给第一个单词加引号
echo "hello world" | sed -E 's/^(\w+)/"\1"/'
# 输出："hello" world

# awk：提取分组（使用 match + 数组）
echo "2024-01-15" | awk '{
    match($0, /([0-9]{4})-([0-9]{2})-([0-9]{2})/, a)
    print a[1]"/"a[2]"/"a[3]
}'
```

---

### 第6节：PCRE 高级特性（PCRE Advanced Features）

```bash
# 负向前瞻：匹配后面不跟特定模式的文本
grep -P 'error(?!_ignored)' file.txt

# 正向前瞻：匹配后面跟特定模式的文本
grep -P '\d+(?= dollars)' file.txt

# 负向后顾：匹配前面不跟特定模式的文本
grep -P '(?<!\$)\d+\.\d+' file.txt    # 不匹配货币格式

# 占有量词（避免回溯）
grep -P 'a++b' file.txt

# 原子组
grep -P '(?>ab|a)b' file.txt

# Unicode 支持
grep -P '\p{Han}' chinese.txt          # 匹配中文字符
grep -P '\p{L}+' text.txt              # 匹配任何字母
```

#### PCRE 修饰符

```bash
# 忽略大小写（内联）
grep -P '(?i)hello' file.txt

# 多行模式（^ $ 匹配每行）
grep -P '(?m)^start' file.txt

# 点号匹配换行
grep -P '(?s)start.*end' file.txt

# 扩展模式（允许空白和注释）
grep -P -x '(?x)
    \d{4}      # year
    -          # separator
    \d{2}      # month
    -          # separator
    \d{2}      # day
' dates.txt
```

---

### 第7节：BRE vs ERE vs PCRE 完整对比（Complete Comparison）

| 场景 | BRE | ERE | PCRE | 推荐 |
|------|-----|-----|------|------|
| 简单匹配 | `grep 'pattern'` | `grep -E 'pattern'` | `grep -P 'pattern'` | BRE |
| 量词 | `ab\{2,4\}` | `ab{2,4}` | `ab{2,4}` | ERE |
| 分组 | `\(ab\)` | `(ab)` | `(ab)` | ERE |
| 或 | `a\|b` | `a\|b` | `a\|b` | ERE |
| 前瞻后顾 | — | — | `(?=...)` | PCRE |
| Unicode | — | — | `\p{Han}` | PCRE |
| 可读性 | 差 | 好 | 最好 | PCRE |

#### 跨工具一致性建议

```bash
# 统一使用 ERE（最通用）
grep -E 'pattern' file
sed -E 's/pattern/repl/' file
awk '/pattern/ {action}' file

# 需要高级功能时使用 PCRE
grep -P '\d{3}-\d{4}' file
perl -ne 'print if /pattern/' file
```

---

### 本章要点总结

- BRE 需要转义 `()` 和 `{}`，ERE/PCRE 直接使用
- PCRE 支持前瞻、后顾、命名分组、Unicode
- `grep -E` 获得 ERE，`grep -P` 获得 PCRE
- `sed` 默认 BRE，`-E` 切换到 ERE
- `awk` 使用 ERE 语法
- 优先使用 ERE 保持跨工具一致性

---

**上一章**：[[02_管道与重定向：tee_xargs_exec|管道与重定向]]
**下一章**：[[04_sed流编辑器：增删改查_多行处理|sed 流编辑器]]
