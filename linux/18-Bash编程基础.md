# 16 - Bash 编程基础

> Shell 脚本是 Linux 系统管理的基石。本章从变量、条件判断到函数与数组，系统讲解 Bash 编程的核心语法。

---

## 16.1 Shebang — 脚本的第一行

```bash
#!/bin/bash
#!/usr/bin/env bash # 更通用，从 PATH 查找 bash
#!/bin/sh # POSIX sh（更可移植，但功能受限）
#!/usr/bin/env python3
```

Shebang (`#!`) 告诉内核用哪个解释器来执行脚本。两字节是一个"魔数"，内核读取后启动对应的解释器并将脚本路径作为参数传递。

```bash
# 如果没有 shebang，默认用当前 shell 解释
# 直接 ./script.sh 执行需要 +x 权限
# bash script.sh 执行不需要 +x 权限，且会覆盖 shebang
```

---

## 16.2 变量

### 变量定义与使用

```bash
# 定义（等号两边不允许有空格）
name="Arch Linux"
count=42
readonly PI=3.14159 # 只读变量

# 使用
echo "$name" # 推荐：双引号保护
echo "${name}_rocks" # 花括号明确边界
echo '$name' # 单引号：原样输出 $name，不展开

# 未定义变量和默认值 —— 见 [[19-Bash编程进阶]]
```

### 变量命名规范

- 变量名只能包含字母、数字、下划线，不能以数字开头
- 习惯上全局变量用大写、局部变量用小写
- Bash 没有布尔类型，用 0 表示真、非 0 表示假

```bash
# 局部变量（函数内）
local temp_file="/tmp/clean.$$"

# 环境变量（导出给子进程）
export PATH="/usr/local/bin:$PATH"
export EDITOR="vim"

# 使用 declare 声明类型
declare -i count=10 # 整数
declare -r version="1.0" # 只读
declare -a arr=("a" "b") # 索引数组
declare -A map # 关联数组
```

---

## 16.3 引号规则

```bash
# 单引号：一切原样输出，不进行任何展开
echo 'Today is $(date) and $HOME is here'
# 输出: Today is $(date) and $HOME is here

# 双引号：允许变量展开和命令替换，但保留空格和特殊字符
echo "Today is $(date) and $HOME is here"
# 输出: Today is Fri Jul 24 15:30:00 CST 2026 and /home/user is here

# 无引号：进行单词拆分和通配符展开
files=*.txt # 危险！会被展开为目录中的文件列表
echo $files # 会按空格拆分，丢失换行

# 最佳实践：始终用双引号包裹变量引用
echo "$files"
for file in "$@"; do # "$@" 保留每个参数独立性
 process "$file"
done
```

### 单双引号综合示例

```bash
name="Alice"
echo "Hello, $name" # Hello, Alice
echo 'Hello, $name' # Hello, $name
echo "She said \"Hello\"" # She said "Hello" (双引号内用\"转义)
echo 'She said "Hello"' # She said "Hello" (单引号内双引号无需转义)

# 拼接
full="$name Smith" # Alice Smith
full="${name}_2026" # Alice_2026
```

---

## 16.4 特殊变量

```bash
echo "\$0 = $0" # 脚本自身的名称（含路径）
echo "\$1 = $1" # 第一个位置参数
echo "\$2 = $2" # 第二个位置参数
echo "\$# = $#" # 位置参数的个数
echo "\$@ = $@" # 所有位置参数（"$@" 每个参数独立）
echo "\$* = $*" # 所有位置参数（"$*" 合并为一个字符串）
echo "\$? = $?" # 上一条命令的退出码（0 表示成功）
echo "\$\$ = $$" # 当前 shell 的 PID
echo "\$! = $!" # 最后一个放入后台的进程 PID
echo "\$_ = $_" # 上一条命令的最后一个参数
echo "\$- = $-" # 当前 shell 的选项标志（如 himBHs）
```

### `$@` 与 `$*` 的关键区别

```bash
#!/bin/bash
# 假设传入参数: "a b" "c d"

echo "=== 不加引号 ==="
for arg in $@; do echo "[$arg]"; done # 拆成 4 个: a b c d
for arg in $*; do echo "[$arg]"; done # 同样拆成 4 个

echo "=== 加双引号 ==="
for arg in "$@"; do echo "[$arg]"; done # 2 个: [a b] [c d] (推荐)
for arg in "$*"; do echo "[$arg]"; done # 1 个: [a b c d]
```

---

## 16.5 命令替换

```bash
# 写法一：$(command) —— 推荐，可嵌套
now=$(date)
current_dir=$(pwd)
lines=$(wc -l < /etc/passwd)
pid=$(ps aux | grep nginx | grep -v grep | awk '{print $2}')

# 写法二：`command` —— 旧式反引号，不可嵌套
now=`date`
pid=`ps aux | grep nginx | grep -v grep | awk '{print $2}'`

# 嵌套对比
result=$(echo $(basename $(pwd))) # 清晰
result=`echo \`basename \\\`pwd\\\`\`` # 混乱的反斜杠地狱

# 常见用途
files=$(ls /etc/*.conf 2>/dev/null) # 忽略错误输出
count=$(grep -c "error" app.log)
```

---

## 16.6 算术运算

```bash
# 方式一：$(( )) —— 推荐
a=10; b=3
echo $((a + b)) # 13
echo $((a - b)) # 7
echo $((a * b)) # 30
echo $((a / b)) # 3 (整数除法)
echo $((a % b)) # 1 (取模)
echo $((a ** b)) # 1000 (幂运算)
echo $(( (a + b) * 2 )) # 26 (括号分组)

# 自增/自减
((a++)) # 后自增
((++a)) # 前自增
((a--)) # 后自减

# 方式二：let 命令
let "result = a + b"
let "result = a * b"
let result++ # 自增

# 方式三：expr（外部命令，不推荐）
result=$(expr $a + $b) # 注意空格和转义
result=$(expr $a \* $b) # 星号需要转义

# C 风格 for 循环
for ((i = 0; i < 10; i++)); do
 echo "Index: $i"
done
```

---

## 16.7 条件判断

### test 命令 / [ ] — POSIX 标准

```bash
# 数值比较
if [ "$a" -eq "$b" ]; then echo "等于"; fi # -eq: equal
if [ "$a" -ne "$b" ]; then echo "不等于"; fi # -ne: not equal
if [ "$a" -gt "$b" ]; then echo "大于"; fi # -gt: greater than
if [ "$a" -lt "$b" ]; then echo "小于"; fi # -lt: less than
if [ "$a" -ge "$b" ]; then echo "大于等于"; fi # -ge: greater or equal
if [ "$a" -le "$b" ]; then echo "小于等于"; fi # -le: less or equal

# 字符串判断
if [ "$str1" = "$str2" ]; then echo "相等"; fi
if [ "$str1" != "$str2" ]; then echo "不等"; fi
if [ -z "$str" ]; then echo "字符串为空"; fi # -z: zero length
if [ -n "$str" ]; then echo "字符串非空"; fi # -n: non-zero length

# 文件测试
if [ -f "$path" ]; then echo "是普通文件"; fi # -f: regular file
if [ -d "$path" ]; then echo "是目录"; fi # -d: directory
if [ -e "$path" ]; then echo "存在"; fi # -e: exists (any type)
if [ -r "$path" ]; then echo "可读"; fi # -r: readable
if [ -w "$path" ]; then echo "可写"; fi # -w: writable
if [ -x "$path" ]; then echo "可执行"; fi # -x: executable
if [ -s "$path" ]; then echo "非空文件"; fi # -s: non-empty (size > 0)
if [ -L "$path" ]; then echo "是符号链接"; fi # -L: symbolic link
if [ -p "$path" ]; then echo "是命名管道"; fi # -p: named pipe
if [ -b "$path" ]; then echo "是块设备"; fi # -b: block device
if [ -c "$path" ]; then echo "是字符设备"; fi # -c: character device

# 文件时间比较
if [ "$file1" -nt "$file2" ]; then echo "file1 比 file2 新"; fi # newer than
if [ "$file1" -ot "$file2" ]; then echo "file1 比 file2 旧"; fi # older than

# 逻辑运算
if [ "$a" -gt 0 ] && [ "$b" -lt 100 ]; then echo "均满足"; fi
if [ "$a" -gt 0 ] || [ "$b" -lt 100 ]; then echo "至少一个满足"; fi
if ! [ -f "/etc/passwd" ]; then echo "文件不存在"; fi

# 也可以使用 -a (AND) 和 -o (OR)，但可读性差且 POSIX 已弃用
if [ "$a" -gt 0 -a "$b" -lt 100 ]; then echo "不推荐"; fi
```

### [[ ]] — Bash 增强版（推荐）

```bash
# 支持通配符匹配
if [[ "$filename" == *.txt ]]; then
 echo "这是一个 txt 文件"
fi

# 支持正则匹配 (=~)
if [[ "$str" =~ ^[0-9]+$ ]]; then
 echo "字符串是纯数字"
fi

# 逻辑运算符更直观
if [[ -f "$file" && -s "$file" ]]; then
 echo "文件存在且非空"
fi

# 不需要给变量加双引号也能正确处理空变量
# [ $str ] 在 str 为空时会报语法错误，但 [[ $str ]] 不会

# =~ 正则示例
ip="192.168.1.1"
if [[ "$ip" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]]; then
 echo "看起来是 IP 地址"
 echo "匹配的部分: ${BASH_REMATCH[0]}"
fi

email="user@example.com"
if [[ "$email" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
 echo "看起来是邮箱地址"
fi
```

### (( )) — 算术条件

```bash
if (( a > b )); then # 直接用 > < >= <= == !=
 echo "a 大于 b"
fi

if (( (a % 2) == 0 )); then
 echo "a 是偶数"
fi

if (( a == b - 10 )); then # 支持赋值表达式
 echo "a 等于 b-10"
fi
```

---

## 16.8 if / elif / else 语句

```bash
#!/bin/bash

# 基本形式
if [ "$1" = "start" ]; then
 echo "启动服务..."
 sudo systemctl start nginx
elif [ "$1" = "stop" ]; then
 echo "停止服务..."
 sudo systemctl stop nginx
elif [ "$1" = "restart" ]; then
 echo "重启服务..."
 sudo systemctl restart nginx
else
 echo "用法: $0 {start|stop|restart}"
 exit 1
fi

# 嵌套 if
if [ -f "/etc/nginx/nginx.conf" ]; then
 if grep -q "server" "/etc/nginx/nginx.conf"; then
 echo "配置文件中包含 server 块"
 else
 echo "配置文件中没有 server 块"
 fi
fi

# 单行写法（简短命令）
[ -f "/etc/passwd" ] && echo "passwd 存在" || echo "passwd 不存在"
[ -d "/backup" ] || { echo "备份目录不存在"; exit 1; }

# 命令退出码直接作为条件
if grep -q "root" /etc/passwd; then
 echo "root 用户存在"
fi

# 多条命令作为条件
if systemctl is-active --quiet nginx && curl -s -o /dev/null -w '%{http_code}' http://localhost | grep -q "200"; then
 echo "nginx 运行正常"
fi
```

---

## 16.9 case 语句

```bash
#!/bin/bash

read -p "请选择操作 (start/stop/restart/status): " action

case "$action" in
 start|boot)
 echo "启动服务"
 sudo systemctl start nginx
 ;;
 stop|shutdown)
 echo "停止服务"
 sudo systemctl stop nginx
 ;;
 restart|reload)
 echo "重启服务"
 sudo systemctl restart nginx
 ;;
 status|state)
 systemctl status nginx
 ;;
 *)
 echo "错误: 未知操作 '$action'"
 echo "支持: start|stop|restart|status"
 exit 1
 ;;
esac

# 通配符匹配
case "$filename" in
 *.jpg|*.jpeg) echo "JPEG 图片" ;;
 *.png) echo "PNG 图片" ;;
 *.txt) echo "文本文件" ;;
 *.sh) echo "Shell 脚本" ;;
 *) echo "未知类型" ;;
esac

# 正则风格匹配
case "$response" in
 [Yy]|[Yy][Ee][Ss]) echo "确认" ;;
 [Nn]|[Nn][Oo]) echo "取消" ;;
 *)
 echo "请输入 yes 或 no"
 ;;
esac
```

---

## 16.10 循环

### for 循环

```bash
# 方式一：单词列表
for color in 红色 绿色 蓝色 白色; do
 echo "当前颜色: $color"
done

# 方式二：花括号展开
for i in {1..10}; do
 echo "第 $i 次迭代"
done

for i in {a..z}; do
 echo "字母: $i"
done

for i in {0..20..2}; do # 步长
 echo "偶数: $i"
done

# 方式三：C 风格
for ((i = 0; i < 10; i++)); do
 echo "Index: $i"
done

for ((i = 100; i >= 0; i -= 10)); do
 echo "倒计时: $i"
done

# 方式四：通配符遍历文件
for conf in /etc/*.conf; do
 [ -f "$conf" ] || continue # 防止无匹配时的通配符原样返回
 echo "配置文件: $conf"
done

# 方式五：命令输出
for user in $(awk -F: '{print $1}' /etc/passwd); do
 echo "用户: $user"
done

# 方式六：遍历数组
servers=("web01" "web02" "db01" "db02")
for server in "${servers[@]}"; do
 echo "部署到: $server"
done
```

### while 循环

```bash
# 计数循环
count=1
while [ $count -le 5 ]; do
 echo "计数: $count"
 ((count++))
done

# 无限循环（配合 break 退出）
while true; do
 read -p "输入命令 (quit 退出): " cmd
 case "$cmd" in
 quit|exit) break ;;
 *) echo "执行: $cmd" ;;
 esac
done

# 读取文件每一行（推荐写法，保留首尾空格和反斜杠）
while IFS= read -r line || [ -n "$line" ]; do
 echo "行内容: $line"
done < "/etc/passwd"

# 从命令输出逐行读取（避免管道导致的变量作用域问题）
while IFS= read -r file; do
 echo "找到: $file"
done < <(find /var/log -name "*.log" -type f)

# 逐行读取 CSV 并处理字段
while IFS=',' read -r name age city; do
 echo "姓名: $name, 年龄: $age, 城市: $city"
done < users.csv
```

### until 循环

```bash
# 条件为假时执行，为真时退出
num=1
until [ $num -gt 5 ]; do
 echo "数值: $num"
 ((num++))
done

# 等待服务就绪
until curl -s -o /dev/null http://localhost:8080/health; do
 echo "等待服务启动..."
 sleep 2
done
echo "服务已就绪！"
```

### continue 与 break

```bash
for i in {1..20}; do
 # 跳过 3
 if [ $i -eq 3 ]; then
 continue
 fi

 # 到 15 停止
 if [ $i -gt 15 ]; then
 break
 fi

 echo "处理: $i"
done

# break N：跳出 N 层循环
for i in {1..5}; do
 for j in {a..e}; do
 if [ "$i" -eq 3 ] && [ "$j" = "c" ]; then
 break 2 # 跳出两层循环
 fi
 echo "$i$j"
 done
done
```

---

## 16.11 函数

### 函数定义与调用

```bash
# 定义方式一：function 关键字
function hello() {
 echo "Hello, World!"
}

# 定义方式二：省略 function 关键字（推荐）
hello() {
 echo "Hello, World!"
}

# 调用（无需括号）
hello

# 带参数的函数
greet() {
 local name="$1"
 local title="${2:-先生}"
 echo "你好, $title $name!"
}

greet "张三" "博士" # 输出: 你好, 博士 张三!
greet "李四" # 输出: 你好, 先生 李四!
```

### 函数参数与返回值

```bash
# 函数内部使用 $1 $2 ... $n 获取参数
# $@ $# $? 等在函数内部表示函数的参数和退出码

# return 方式返回（仅 0-255 整数）
is_even() {
 if (( $1 % 2 == 0 )); then
 return 0 # 成功/真
 else
 return 1 # 失败/假
 fi
}
is_even 4 && echo "4 是偶数"

# echo 方式返回（推荐，可返回字符串和大数）
add() {
 echo $(($1 + $2))
}
result=$(add 15 27)
echo "结果: $result"

# 全局变量方式（不推荐，可读性差）
get_user_info() {
 username="alice"
 home_dir="/home/alice"
}
get_user_info
echo "$username 的家目录是 $home_dir"

# 数组返回值
get_top_processes() {
 ps aux --sort=-%mem | head -6 | tail -5
}
declare -a top_procs
while IFS= read -r line; do
 top_procs+=("$line")
done < <(get_top_processes)
```

### local 变量

```bash
myfunc() {
 local name="内部变量" # 仅函数内可见
 global_name="全局变量" # 默认即全局

 local count=${1:-0} # local 可以捕获赋值命令的返回值

 echo "内部: name=$name"
}
myfunc
echo "外部: name=$name" # 空值（local 变量不可见）
echo "外部: global_name=$global_name" # 可见

# local 的陷阱：local combined = $(false) 不会触发 set -e
# 正确做法：
get_value() {
 local value
 value=$(some_command) || return 1
 echo "$value"
}
```

---

## 16.12 数组

### 索引数组

```bash
# 定义
fruits=("苹果" "香蕉" "樱桃" "榴莲")
numbers=(10 20 30 40 50)

# 下标赋值
fruits[4]="葡萄"
fruits[10]="芒果" # 下标可以不连续

# 访问
echo "${fruits[0]}" # 第一个: 苹果
echo "${fruits[2]}" # 第三个: 樱桃
echo "${fruits[@]}" # 所有元素
echo "${fruits[*]}" # 所有元素（合并为一个字符串）
echo "${#fruits[@]}" # 元素个数
echo "${!fruits[@]}" # 所有已赋值的索引

# 遍历
for fruit in "${fruits[@]}"; do
 echo "水果: $fruit"
done

# 按索引遍历
for i in "${!fruits[@]}"; do
 echo "索引 $i: ${fruits[$i]}"
done

# 追加
fruits+=("草莓" "蓝莓")

# 切片（Bash 4.0+）
echo "${fruits[@]:1:3}" # 从索引 1 开始取 3 个

# 删除
unset "fruits[2]" # 删除索引 2
unset fruits # 删除整个数组

# 转化为字符串（用逗号连接）
IFS=','; echo "${fruits[*]}"; unset IFS
```

### 关联数组（Bash 4.0+）

```bash
# 声明
declare -A user_info
declare -A server_ips

# 赋值
user_info["name"]="Alice"
user_info["age"]="28"
user_info["city"]="Tokyo"

server_ips["web01"]="10.0.1.10"
server_ips["web02"]="10.0.1.11"
server_ips["db01"]="10.0.2.10"

# 访问
echo "姓名: ${user_info[name]}"
echo "web01 IP: ${server_ips[web01]}"

# 遍历 key
for key in "${!user_info[@]}"; do
 echo "$key = ${user_info[$key]}"
done

# 遍历 value
for value in "${user_info[@]}"; do
 echo "值: $value"
done

# 检查 key 是否存在
if [[ -v user_info["name"] ]]; then
 echo "name 键存在"
fi

# 删除
unset "user_info[city]"
```

---

## 16.13 字符串操作

```bash
str="Hello, Arch Linux World"

# 长度
echo "${#str}" # 23

# 子字符串提取
echo "${str:7}" # Arch Linux World（从位置7到结尾）
echo "${str:7:4}" # Arch（从7起取4个字符）
echo "${str: -5}" # World（负数需要空格，从末尾取5个）
echo "${str:0:5}" # Hello

# 替换
echo "${str/World/Universe}" # 替换第一个匹配: Hello, Arch Linux Universe
echo "${str//o/O}" # 替换所有匹配: HellO, Arch Linux WOrld
echo "${str/#Hello/Hi}" # 替换开头: Hi, Arch Linux World
echo "${str/%World/OS}" # 替换结尾: Hello, Arch Linux OS

# 删除
echo "${str#Hello, }" # 删除最短前缀: Arch Linux World
echo "${str##*, }" # 删除最长前缀: World
echo "${str% World}" # 删除最短后缀: Hello, Arch Linux
echo "${str%%,*}" # 删除最长后缀: Hello

# 大小写转换（Bash 4.0+）
echo "${str^^}" # 全大写: HELLO, ARCH LINUX WORLD
echo "${str,,}" # 全小写: hello, arch linux world
echo "${str^}" # 首字母大写: Hello, Arch Linux World
echo "${str,}" # 首字母小写: hello, Arch Linux World

# 判断是否包含子串
if [[ "$str" == *"Arch"* ]]; then
 echo "包含 Arch"
fi
```

---

## 16.14 读取输入

```bash
# 基本读取
read -p "请输入用户名: " username
echo "你好, $username"

# 静默读取（密码）
read -s -p "请输入密码: " password
echo # 输出换行
echo "密码已输入"

# 带超时
read -t 5 -p "5秒内输入选择 [Y/n]: " choice
echo "你的选择: ${choice:-默认}"

# 限制字符数（不需要回车）
read -n 1 -p "按任意键继续..." key
echo

# 读取多个值
read -p "输入姓 名 年龄: " first last age
echo "$first $last, $age 岁"

# 从文件读取（配合重定向）
while read -r line; do
 echo "$line"
done < /etc/hosts

# 设置默认值（Bash 4.0+）
read -e -p "编辑目录 [/usr/local]: " -i "/usr/local" dir
echo "目录: $dir"

# 使用 IFS 控制分隔符
IFS=':' read -r user _ uid gid _ _ shell <<< "root:x:0:0:root:/root:/bin/bash"
echo "用户: $user, UID: $uid, Shell: $shell"
```

### stdin 常见模式

```bash
# 管道输入
echo "hello world" | while read -r word1 word2; do
 echo "词1: $word1, 词2: $word2"
done

# 多行输入到变量
content=$(cat << 'EOF'
第一行内容
第二行内容
第三行内容
EOF
)

# 读取标准输入全部内容
stdin_content=$(cat)
```

---

## 16.15 退出码与严格模式

### 退出码

```bash
# 任何命令执行后都会设置 $?
true
echo "true 的退出码: $?" # 0

false
echo "false 的退出码: $?" # 1

ls /nonexistent 2>/dev/null
echo "ls 失败: $?" # 2

# 脚本中自定义退出码
exit 0 # 成功
exit 1 # 通用错误
exit 2 # 误用
exit 127 # 命令未找到

# 退出码范围：0-255，超过 255 会取模
```

### 严格模式

```bash
#!/bin/bash
set -e # 任何命令失败立即退出（遇到错误就停止）
set -u # 使用未定义变量时报错
set -o pipefail # 管道中任何命令失败都视为失败
set -x # 打印执行的每条命令（调试用）
set -v # 打印读取的每一行（调试用）

# 组合用法
set -euo pipefail

# 局部忽略 -e
command_that_may_fail || true
set +e; risky_command; set -e

# 常见的 set -e 陷阱
# 1. 管道首命令失败不会触发
false | true
echo "不会触发 set -e: $?" # 输出 0，不是 1

# 应用 set -o pipefail 后：
set -o pipefail
false | true
echo "此时触发 set -e，脚本退出" # 不会执行到这一行

# 2. 在条件表达式、while/until、|| 或 && 中的失败不受 set -e 影响

# trap 配合 set -e 使用 — 见 [[19-Bash编程进阶]]
```

---

## 16.16 综合示例：简易系统信息脚本

```bash
#!/bin/bash
set -euo pipefail

check_root() {
 if [ "$(id -u)" -ne 0 ]; then
 echo "错误: 请使用 root 权限运行"
 exit 1
 fi
}

get_cpu_usage() {
 local idle cpu
 cpu=$(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}')
 echo "${cpu:-N/A}"
}

get_memory_info() {
 local total used free percent
 read -r total used free <<< "$(free -m | awk '/^Mem:/{print $2, $3, $4}')"
 percent=$((used * 100 / total))
 echo "总计: ${total}MB | 已用: ${used}MB | 空闲: ${free}MB | 使用率: ${percent}%"
}

get_disk_info() {
 echo "=== 磁盘使用情况 ==="
 df -h | grep -E '^/dev/' | awk '{printf " %-20s %5s / %s (%s)\n", $1, $3, $2, $5}'
}

main() {
 echo "========== 系统信息摘要 =========="
 echo "主机名: $(hostname)"
 echo "内核: $(uname -r)"
 echo "运行时间: $(uptime -p | sed 's/up //')"
 echo ""
 echo "CPU 使用率: $(get_cpu_usage)%"
 get_memory_info
 get_disk_info
}

main
```

---

## 16.17 本章要点速查

| 类别 | 关键语法 | 说明 |
|------|----------|------|
| 变量 | `name="val"`, `"${name}"`, `$(cmd)` | 双引号保护、花括号定界 |
| 特殊变量 | `$0 $1 $# $@ $? $$ $!` | 脚本名、参数、参数个数、退出码、PID |
| 条件 | `[ ]`, `[[ ]]`, `if/elif/else`, `case` | `[[ ]]` 支持正则和通配符 |
| 算术 | `$((a + b))`, `((a++))`, `let` | `(( ))` 用于条件和算术 |
| 循环 | `for/while/until`, `break/continue` | `while read` 逐行读取 |
| 函数 | `func() { ... }`, `local`, `return/echo` | echo 返回字符串和大于255的值 |
| 数组 | `arr=()`, `${arr[@]}`, `declare -A` | 索引数组和关联数组 |
| 字符串 | `${#str}`, `${str:0:5}`, `${str/old/new}` | 内置操作，无需外部工具 |
| 读取 | `read -p`, `-s`, `-t`, `-n` | stdin 交互输入 |
| 严格模式 | `set -euo pipefail` | 遇错即停，防范未定义变量 |

---

> **延伸阅读**: [[19-Bash编程进阶]] 涵盖参数展开高级技巧、调试方法、信号处理与健壮脚本编写。[[20-正则与文本处理三剑客]] 详解 grep/sed/awk 实战。[[06-命令行基础与Shell入门]] 为新手指南。
