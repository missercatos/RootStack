# 01 - Shell 编程基础

> Shell 脚本是免修考试的核心，通常占比 30%-40%。

---

## 1.1 变量

```bash
# 定义变量（等号两边不能有空格）
name="Arch Linux"
count=42

# 使用变量
echo "$name"              # 推荐：双引号保护
echo "${name}_rocks"      # 花括号明确边界

# 特殊变量
echo "$0"    # 脚本名
echo "$1"    # 第一个参数
echo "$#"    # 参数个数
echo "$@"    # 所有参数（推荐用这个）
echo "$?"    # 上一条命令的退出码
echo "$$"    # 当前进程 PID

# 只读变量
readonly PI=3.14

# 命令替换
now=$(date)
files=$(ls /etc | wc -l)
```

---

## 1.2 条件判断

### test 命令（等价 `[ ]`）

```bash
# 数值比较（不能用 > <）
[ "$a" -eq "$b" ]   # 等于
[ "$a" -ne "$b" ]   # 不等于
[ "$a" -gt "$b" ]   # 大于
[ "$a" -lt "$b" ]   # 小于
[ "$a" -ge "$b" ]   # 大于等于
[ "$a" -le "$b" ]   # 小于等于

# 字符串判断
[ "$str1" = "$str2"  ]    # 相等
[ "$str1" != "$str2" ]    # 不等
[ -z "$str" ]              # 长度为零
[ -n "$str" ]              # 长度非零

# 文件判断
[ -f "/etc/passwd" ]       # 是普通文件
[ -d "/etc" ]               # 是目录
[ -e "/etc/hosts" ]        # 存在（不管类型）
[ -r "/etc/passwd" ]       # 可读
[ -w "/etc/passwd" ]       # 可写
[ -x "/usr/bin/bash" ]     # 可执行
[ -s "/etc/passwd" ]       # 非空文件

# 逻辑运算
[ "$a" -gt 0 ] && [ "$b" -lt 100 ]    # AND
[ "$a" -gt 0 ] || [ "$b" -lt 100 ]    # OR
! [ "$a" -eq 5 ]                        # NOT
```

### 双括号 `(( ))` — 算术运算专用

```bash
a=10; b=20
if (( a < b )); then
    echo "支持 > < >= <="
fi
if (( a == b - 10 )); then
    echo "支持赋值表达式"
fi
for (( i=0; i<10; i++ )); do
    echo "$i"
done
```

### 双中括号 `[[ ]]` — Bash 增强版（推荐）

```bash
str="hello world"
if [[ $str =~ ^h.*d$ ]]; then    # 支持正则匹配
    echo "匹配"
fi
if [[ $str == h* ]]; then         # 支持通配符
    echo "通配符匹配"
fi
```

---

## 1.3 if 语句

```bash
if [ "$1" = "start" ]; then
    echo "启动服务..."
elif [ "$1" = "stop" ]; then
    echo "停止服务..."
else
    echo "用法: $0 {start|stop}"
    exit 1
fi
```

---

## 1.4 case 语句

```bash
case "$1" in
    start)
        echo "启动"
        ;;
    stop)
        echo "停止"
        ;;
    restart|reload)
        echo "重启"
        ;;
    *)
        echo "用法: $0 {start|stop|restart|reload}"
        exit 1
        ;;
esac
```

---

## 1.5 循环

### for 循环

```bash
# 方式一：列表循环
for user in alice bob charlie; do
    echo "创建用户: $user"
done

# 方式二：C 风格
for (( i=1; i<=5; i++ )); do
    echo "第 $i 次"
done

# 方式三：通配符
for file in /etc/*.conf; do
    echo "配置文件: $file"
done

# 方式四：命令结果
for pid in $(pgrep bash); do
    echo "bash 进程: $pid"
done
```

### while 循环

```bash
count=1
while [ $count -le 5 ]; do
    echo "计数: $count"
    ((count++))       # 或 count=$((count + 1))
done

# 读取文件每一行
while IFS= read -r line; do
    echo "$line"
done < /etc/passwd
```

### until 循环

```bash
num=1
until [ $num -gt 5 ]; do    # 条件为真时停止
    echo "$num"
    ((num++))
done
```

### break 与 continue

```bash
for i in {1..10}; do
    if [ $i -eq 3 ]; then
        continue    # 跳过本次
    fi
    if [ $i -eq 8 ]; then
        break       # 退出循环
    fi
    echo "$i"
done
```

---

## 1.6 函数

```bash
# 定义方式一
function greet() {
    local name="$1"       # local 限定作用域
    echo "Hello, $name!"
}

# 定义方式二
greet() {
    echo "你好, $1!"
}

greet "World"

# 返回值（只能返回 0-255）
add() {
    return $(( $1 + $2 ))
}
add 3 5
echo "结果: $?"    # 8

# 建议用 echo 返回结果
add() {
    echo $(( $1 + $2 ))
}
result=$(add 3 5)
echo "结果: $result"
```

---

## 1.7 数组

```bash
# 定义
fruits=("apple" "banana" "cherry")
nums=(1 2 3 4 5)

# 访问
echo "${fruits[0]}"       # 第一个元素
echo "${fruits[@]}"       # 所有元素
echo "${#fruits[@]}"      # 数组长度
echo "${!fruits[@]}"      # 所有索引

# 遍历
for fruit in "${fruits[@]}"; do
    echo "$fruit"
done

# 追加
fruits+=("durian")

# 删除
unset "fruits[1]"
```

---

## 1.8 管道与重定向

```bash
# 重定向
command > file         # 覆盖写入
command >> file        # 追加写入
command 2> file        # 重定向 stderr
command &> file        # 重定向 stdout + stderr
command < file         # 从文件读取输入

# Here Document
cat << EOF > /tmp/config.txt
配置内容第一行
配置内容第二行
EOF

# Here String
grep "root" <<< "$(cat /etc/passwd)"

# 管道
cat /var/log/pacman.log | grep "installed" | wc -l

# tee — 同时输出到文件和屏幕
echo "hello" | tee output.txt
echo "world" | tee -a output.txt   # 追加
```

---

## 1.9 文本处理三剑客

### grep

```bash
grep "root" /etc/passwd               # 基本匹配
grep -i "error" /var/log/pacman.log   # 忽略大小写
grep -v "comment" file.txt            # 反向匹配
grep -r "TODO" ./src/                 # 递归搜索目录
grep -n "func" script.sh              # 显示行号
grep -c "error" app.log               # 计数
grep -E "^[0-9]+$" data.txt           # 扩展正则
grep "^#" config.conf                 # 匹配所有注释行
```

### sed

```bash
# 替换（最常用）
sed 's/old/new/' file             # 每行替换第一个
sed 's/old/new/g' file            # 全局替换
sed 's/old/new/2' file            # 替换每行第二个
sed -i 's/old/new/g' file         # 直接修改文件

# 删除
sed '/^$/d' file                  # 删除空行
sed '2,5d' file                   # 删除 2-5 行
sed '/^#/d' file                  # 删除注释行

# 打印
sed -n '3,7p' file                # 打印 3-7 行
sed -n '/error/p' log             # 打印包含 error 的行

# 行前/行后插入
sed '3i\新行' file                 # 第3行前插入
sed '3a\新行' file                 # 第3行后追加

# 多重操作
sed -e 's/foo/bar/g' -e '/^$/d' file
```

### awk

```bash
# 字段处理
awk '{print $1, $3}' /etc/passwd             # 打印第1、3列
awk -F: '{print $1, $7}' /etc/passwd         # 指定分隔符
awk -F: '/root/ {print $0}' /etc/passwd      # 匹配 + 打印整行

# 条件
awk -F: '$3 >= 1000 {print $1}' /etc/passwd  # UID >= 1000 的用户
awk '$1 > 50 {print $0}' data.txt

# BEGIN / END
awk 'BEGIN {print "开始处理"} {sum+=$1} END {print "总和:", sum}' nums.txt

# 内置变量
awk '{print NR, $0}' file         # NR = 行号
awk '{print NF, $0}' file         # NF = 字段数

# 格式化输出
awk -F: '{printf "用户: %-15s UID: %d\n", $1, $3}' /etc/passwd

# 经典：统计访问量最多的 IP
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -10
```

---

## 1.10 综合练习题

```bash
#!/bin/bash
# 练习：统计 /etc/passwd 中各类 Shell 的使用人数

declare -A shells

while IFS=: read -r user _ uid gid _ _ shell; do
    ((shells["$shell"]++))
done < /etc/passwd

echo "Shell 使用统计:"
echo "----------------"
for shell in "${!shells[@]}"; do
    printf "%-20s %d\n" "$shell" "${shells[$shell]}"
done
```

---

## 1.11 本章测验

> [!example] 📝 自测题目

> [!question]- 选择题 1：Shell 变量定义中，以下哪种写法是正确的？
> - A. `name = "hello"`
> - B. `name="hello"`
> - C. `$name="hello"`
> - D. `set name "hello"`
>
> > [!success]- 点击查看答案
> > **B**
> > Shell 变量赋值时等号两边不能有空格，且不使用 `$` 前缀

> [!question]- 判断题 2：`$@` 和 `$*` 在双引号中的行为完全相同
> - A. ✓ 正确
> - B. ✗ 错误
>
> > [!success]- 点击查看答案
> > **B. ✗ 错误**
> > `"$@"` 将每个参数作为独立字符串，`"$*"` 将所有参数合并为一个字符串

> [!question]- 选择题 3：在 `[ ]` 测试中，判断变量 `$a` 大于 `$b` 应使用哪个运算符？
> - A. `>`
> - B. `-gt`
> - C. `==`
> - D. `-bg`
>
> > [!success]- 点击查看答案
> > **B**
> > `[ ]` 中数值比较使用 `-gt`（大于）、`-lt`（小于）等，不能用 `>` `<`

> [!question]- 选择题 4：以下哪个命令可以读取文件的每一行？
> - A. `for line in $(cat file); do`
> - B. `while IFS= read -r line; do ... done < file`
> - C. `cat file | for line; do`
> - D. `loop file line`
>
> > [!success]- 点击查看答案
> > **B**
> > `while IFS= read -r line` 是逐行读取的标准写法，A 会按空格分词

> [!question]- 判断题 5：Shell 函数中 `return` 只能返回 0-255 的整数
> - A. ✓ 正确
> - B. ✗ 错误
>
> > [!success]- 点击查看答案
> > **A. ✓ 正确**
> > `return` 返回退出码（0-255），需要返回字符串或大数值应使用 `echo` 配合命令替换

> [!question]- 选择题 6：`sed -i 's/foo/bar/g' file` 中 `-i` 的作用是？
> - A. 忽略大小写
> - B. 直接修改文件
> - C. 交互模式
> - D. 只打印匹配行
>
> > [!success]- 点击查看答案
> > **B**
> > `-i` 表示 in-place，直接修改源文件而不是输出到标准输出

> [!question]- 选择题 7：`awk -F: '{print $1}' /etc/passwd` 中 `-F:` 的含义是？
> - A. 过滤含冒号的行
> - B. 指定字段分隔符为冒号
> - C. 格式化输出
> - D. 指定文件格式
>
> > [!success]- 点击查看答案
> > **B**
> > `-F` 指定输入字段分隔符，`-F:` 表示以冒号分隔字段

> [!question]- 判断题 8：`command 2>&1` 表示将标准错误重定向到标准输出
> - A. ✓ 正确
> - B. ✗ 错误
>
> > [!success]- 点击查看答案
> > **A. ✓ 正确**
> > `2>&1` 将文件描述符 2（stderr）重定向到文件描述符 1（stdout）

> [!question]- 选择题 9：`case` 语句中每个分支以什么符号结束？
> - A. `;;`
> - B. `break`
> - C. `end`
> - D. `done`
>
> > [!success]- 点击查看答案
> > **A**
> > Shell 的 `case` 语句每个分支以 `;;` 结束，整个 case 以 `esac` 结束

> [!question]- 判断题 10：`[[ $str =~ ^[0-9]+$ ]]` 可以判断字符串是否为纯数字
> - A. ✓ 正确
> - B. ✗ 错误
>
> > [!success]- 点击查看答案
> > **A. ✓ 正确**
> > `[[ ]]` 支持 `=~` 正则匹配，`^[0-9]+$` 匹配一个或多个数字组成的字符串
