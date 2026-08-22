# 子 shell 与命令替换：执行上下文（Subshells & Command Substitution: Execution Context）

## 章节概述

本章深入讲解 Bash 中子 shell 的创建机制、命令替换 `$()` 与反引号的区别、进程替换 `<()` 的高级用法、命令组 `{}` 的执行上下文，以及变量继承与隔离的原理。理解执行上下文是编写正确脚本的基础。

> **核心理念**：子 shell 是独立的执行上下文，变量修改不会影响父 shell。理解哪些操作创建子 shell 是避免变量丢失和性能问题的关键。

---

### 第1节：子 shell 创建场景（Subshell Creation Scenarios）

以下操作会创建子 shell：

```bash
# 明确创建
(command)
(command1; command2)

# 管道
cmd1 | cmd2

# 命令替换
result=$(cmd)

# 进程替换
diff <(cmd1) <(cmd2)

# 后台执行
cmd &

# 括号分组
(cmd1 && cmd2)

# 子 shell 继承
(cmd3; cmd4) &

# 以下操作不会创建子 shell：
# 命令组 { }
# source / . 命令
# 函数调用
# 管道最后一个命令（Bash 4.2+ lastpipe）
```

#### 变量继承示例

```bash
# 管道中的变量丢失
count=0
echo -e "a\nb\nc" | while read line; do
    ((count++))
done
echo "Count: $count"  # 输出 0（子 shell 中的修改丢失）

# 解决方案 1：进程替换
count=0
while read line; do
    ((count++))
done < <(echo -e "a\nb\nc")
echo "Count: $count"  # 输出 3

# 解决方案 2：lastpipe（Bash 4.2+）
shopt -s lastpipe
count=0
echo -e "a\nb\nc" | while read line; do
    ((count++))
done
echo "Count: $count"  # 输出 3
```

---

### 第2节：$() 命令替换（Command Substitution）

```bash
# 基本用法
today=$(date +%Y-%m-%d)
echo "Today is $today"

# 嵌套
files=$(find / -name "$(whoami)_*.log" 2>/dev/null)

# 多行输出
result=$(cat << 'EOF'
line 1
line 2
line 3
EOF
)
echo "$result"

# 用于变量赋值
LINES=$(wc -l < file.txt)
PID=$(pgrep -f "process_name")

# 在字符串中使用
echo "The date is $(date +%Y-%m-%d)"
echo "File count: $(ls *.txt | wc -l)"
```

#### $() vs 反引号

| 特性 | `$()` | 反引号 |
|------|-------|--------|
| 可读性 | 高 | 低 |
| 嵌套 | 直接嵌套 | 需转义 `\`` |
| POSIX | 是 | 是 |
| 推荐 | 是 | 否 |

```bash
# 反引号的嵌套问题
echo "Today is $(date +%Y-%m-%d)"         # 清晰
echo "Today is `date +%Y-%m-%d`"          # 清晰但不推荐

# 反引号嵌套需要转义
echo "Files in $(ls $(dirname $file))"    # $() 嵌套
echo "Files in `ls \`dirname $file\``"    # 反引号嵌套（难以阅读）
```

#### 命令替换陷阱

```bash
# 陷阱 1：变量展开问题
filename="my file.txt"
# 错误：单词分割
cat $(echo $filename)
# 正确：引号保护
cat "$(echo $filename)"

# 陷阱 2：命令失败处理
result=$(false_command)  # result 为空，$? 为非零
echo "Result: $result"   # 空

# 陷阱 3：空格处理
files=$(ls *.txt)  # 文件名包含空格会出问题
while IFS= read -r file; do
    echo "Processing: $file"
done < <(ls *.txt)  # 正确方式
```

---

### 第3节：() 子 shell 详解（Parenthesized Subshell）

```bash
# 基本子 shell
(x=1; echo "Inside: $x")
echo "Outside: $x"  # 空

# 变量修改隔离
x=10
(x=20; echo "Subshell: $x")  # 20
echo "Parent: $x"              # 10

# 管道中的子 shell
(x=1; sleep 1) &
echo "After background: $x"  # 空

# 多命令子 shell
(
    echo "Step 1"
    cd /tmp
    echo "In /tmp: $(pwd)"
    echo "Step 2"
)
echo "Back in original: $(pwd)"

# 导出变量到子 shell
export MY_VAR="hello"
(x=1; echo "Subshell sees MY_VAR=$MY_VAR")  # 能看到
```

#### 子 shell vs 命令组

| 特性 | `()` 子 shell | `{}` 命令组 |
|------|---------------|-------------|
| 执行上下文 | 新进程 | 当前 shell |
| 变量修改 | 不传播 | 传播 |
| 重定向 | 可在组内 | 可在组外 |
| 分号要求 | 不需要 | 需要 `;}` 或 `\n}` |

```bash
# 命令组：变量修改传播
x=10
{ x=20; echo "Inside: $x"; }
echo "Outside: $x"  # 20

# 命令组：重定向作用于组内所有命令
{
    echo "line 1"
    echo "line 2"
    echo "line 3"
} > output.txt

# 子 shell：变量修改隔离
x=10
(x=20; echo "Inside: $x")
echo "Outside: $x"  # 10
```

---

### 第4节：进程替换详解（Process Substitution Details）

```bash
# 基本语法
diff <(sort file1) <(sort file2)

# 多个输入
paste <(cut -f1 data) <(cut -f2 data) > combined.txt

# 在循环中使用
while IFS= read -r line; do
    process "$line"
done < <(generate_data)

# 同时比较多个源
diff <(ssh server1 cmd) <(ssh server2 cmd)

# 反向进程替换（Bash 4.1+）
echo "data" > >(tee output.txt)

# 分发输出
cmd > >(tee file1.txt) > >(tee file2.txt)
```

#### 进程替换原理

```bash
# 进程替换创建命名管道（FIFO）
# 系统自动管理生命周期
ls <(echo "test")  # 等效于：
# mkfifo /tmp/sh-np.XXXXXX
# echo "test" > /tmp/sh-np.XXXXXX &
# ls /tmp/sh-np.XXXXXX
# rm /tmp/sh-np.XXXXXX

# 验证进程替换文件
ls /dev/fd/  # 显示打开的文件描述符
echo "test" > >(cat)  # 系统会创建临时 fd
```

---

### 第5节：命令组 {}（Command Groups）

```bash
# 语法要求：最后一条命令后必须有 ; 或换行
{ cmd1; cmd2; cmd3; }
{
    cmd1
    cmd2
    cmd3
}

# 重定向作用于组内所有命令
{
    echo "Header"
    cat data.txt
    echo "Footer"
} > output.txt

# 用于函数中组织代码
my_func() {
    {
        echo "Step 1"
        do_something
        echo "Step 2"
    } > /dev/null
}
```

#### 块重定向（Block Redirection）

```bash
# 读取整个文件到变量（避免子 shell）
content=$(cat file.txt)  # 子 shell
content=$(<file.txt)     # 更高效的读取

# 多命令重定向到不同文件
{
    echo "stdout data" >&1
    echo "stderr data" >&2
} > stdout.txt 2> stderr.txt

# 重定向到多个文件
{
    echo "shared data"
    echo "extra data"
} | tee file1.txt > file2.txt
```

---

### 第6节：变量继承与隔离（Variable Inheritance & Isolation）

#### 继承规则

```bash
# 环境变量：子 shell 继承
export MY_VAR="inherited"
(x=1; echo "Subshell: $MY_VAR")  # inherited

# 局部变量：子 shell 不继承
x=10
(x=1; echo "Subshell: ${x:-not set}")  # not set

# 数组：子 shell 不继承修改
arr=(a b c)
(arr[0]=x; echo "Subshell: ${arr[0]}")  # x
echo "Parent: ${arr[0]}"                  # a

# 关联数组
declare -A map=([key1]=val1 [key2]=val2)
(map[key1]=new; echo "Subshell: ${map[key1]}")  # new
echo "Parent: ${map[key1]}"                       # val1
```

#### 同步与通信

```bash
# 使用命名管道（FIFO）通信
FIFO=$(mktemp -u)
mkfifo "$FIFO"

# 生产者
{
    echo "data1"
    echo "data2"
    echo "data3"
} > "$FIFO" &

# 消费者
while IFS= read -r line; do
    echo "Got: $line"
done < "$FIFO"

rm "$FIFO"

# 使用文件描述符
exec 3<>"$FIFO"
echo "data" >&3
read -u 3 line
exec 3>&-
```

---

### 第7节：执行上下文综合实战（Execution Context Patterns）

#### 环境隔离模式

```bash
#!/bin/bash
# 临时环境子 shell
(
    export PATH="/opt/app/bin:$PATH"
    export APP_ENV="production"
    # 所有命令在隔离环境中运行
    run_app
)
# 主 shell 不受影响
```

#### 并行任务模式

```bash
#!/bin/bash
# 并行执行，收集结果
declare -A results
pids=()

for task in task1 task2 task3; do
    (
        result=$($task)
        echo "$result" > "/tmp/result_$task"
    ) &
    pids+=($!)
done

# 等待所有完成
for pid in "${pids[@]}"; do
    wait "$pid"
done

# 收集结果
for task in task1 task2 task3; do
    results[$task]=$(cat "/tmp/result_$task")
    rm -f "/tmp/result_$task"
done
```

#### 流水线模式

```bash
#!/bin/bash
# 数据流水线（各阶段在子 shell 中）
generate_data \
    | validate_data \
    | transform_data \
    | load_data

# 每个阶段是独立进程
# 失败处理：
generate_data \
    | validate_data \
    || { echo "Validation failed" >&2; exit 1; }
```

---

### 本章要点总结

- `()` 创建子 shell，变量修改隔离；`{}` 是命令组，变量修改传播
- `$()` 比反引号更可读且支持嵌套
- 进程替换 `<()` 将命令输出伪装为文件
- 管道 `|` 中的变量修改会丢失（子 shell）
- `shopt -s lastpipe` 让管道最后一个命令在当前 shell 执行
- 理解执行上下文是避免变量丢失和性能问题的关键

---

**上一章**：[[06_调试与性能：set_-x_shellcheck_profiling|调试与性能]]
**下一章**：[[08_高级参数展开：${var:-default}_模式匹配|高级参数展开]]
