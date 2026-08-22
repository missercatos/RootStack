# 循环：for、while、until (Loops)

## 章节概述

本章讲解 Bash 的三种循环结构：for（遍历）、while（条件真时循环）、until（条件假时循环），以及 break/continue 控制流。通过与 C 语言对比掌握 Bash 循环的特色用法。

> **核心理念**：Bash 循环处理的是"列表"和"命令退出码"，而非 C 语言的"条件表达式"和"计数器"。

---

### 第1节：for 循环 —— 列表遍历

```bash
for fruit in apple banana cherry; do
    echo "$fruit"
done

for f in *.txt; do
    echo "$f"
done
```

**C 风格 for 循环：**

```bash
for ((i=0; i<5; i++)); do
    echo "i = $i"
done
```

**seq / 范围语法：**

```bash
for i in $(seq 1 5); do echo "$i"; done
for i in {1..5}; do echo "$i"; done
for i in {0..20..5}; do echo "$i"; done   # 步长5
```

| 形式 | 语法 | 适用场景 |
|------|------|----------|
| 列表 | `for x in a b c` | 已知元素 |
| 通配符 | `for f in *.txt` | 文件匹配 |
| C 风格 | `for ((i=0;i<n;i++))` | 计数循环 |
| 范围 | `for i in {1..n}` | 数字范围 |

---

### 第2节：while 循环

```bash
count=1
while [ $count -le 5 ]; do
    echo "Count: $count"
    ((count++))
done
```

**逐行读取文件：**

```bash
while IFS= read -r line; do
    echo "$line"
done < /etc/passwd
```

**无限循环：**

```bash
while true; do
    read -p "输入 (q 退出): " input
    [ "$input" = "q" ] && break
    echo "你输入了: $input"
done
```

---

### 第3节：until 循环

```bash
# until 与 while 相反：条件为假时执行
count=1
until [ $count -gt 5 ]; do
    echo "Count: $count"
    ((count++))
done
```

**while vs until 对比：**

| 结构 | 条件为真时 | 条件为假时 |
|------|------------|------------|
| `while` | 继续循环 | 退出 |
| `until` | 退出 | 继续循环 |

---

### 第4节：break 与 continue

```bash
# break: 跳出循环
for i in {1..10}; do
    [ $i -eq 5 ] && break
    echo "$i"
done
# 输出: 1 2 3 4

# continue: 跳过本次迭代
for i in {1..10}; do
    [ $((i % 2)) -eq 0 ] && continue
    echo "$i"
done
# 输出: 1 3 5 7 9 (奇数)
```

**C 对比：**

```c
for (int i=0; i<10; i++) {
    if (i == 5) break;
    if (i % 2 == 0) continue;
    printf("%d\n", i);
}
```

---

### 第5节：循环中的管道陷阱

```bash
# ✗ 错误：管道创建子进程，变量修改不影响父 shell
count=0
cat file.txt | while read -r line; do
    ((count++))
done
echo "$count"    # 输出: 0 (子进程的修改丢失)

# ✓ 正确：重定向代替管道
count=0
while read -r line; do
    ((count++))
done < file.txt
echo "$count"    # 输出: 文件行数
```

> **核心理解**：管道 `|` 每个阶段都在子 shell 中执行，变量修改不会传递回调用者。

---

### 第6节：嵌套循环与实战

```bash
# 九九乘法表
for ((i=1; i<=9; i++)); do
    for ((j=1; j<=i; j++)); do
        printf "%d×%d=%-4d" $j $i $((i*j))
    done
    echo ""
done
```

**C 等效代码：**

```c
for (int i=1; i<=9; i++) {
    for (int j=1; j<=i; j++) {
        printf("%d×%d=%-4d", j, i, i*j);
    }
    printf("\n");
}
```

---

### 第7节：循环性能技巧

```bash
# ✗ 慢：外部命令 seq
for i in $(seq 1 10000); do :; done

# ✓ 快：Bash 内建
for ((i=0; i<10000; i++)); do :; done

# ✓ 快：范围语法
for i in {1..10000}; do :; done
```

---

### 第8节：课后练习

1. 用 for 循环计算 1 到 100 的和
2. 编写脚本逐行读取 `/etc/passwd`，统计用户数量
3. 用 while + read 实现批量重命名文件

**相关章节：**
- [[../04_条件判断：if_case_test|上一章：条件判断]]
- [[../06_函数：定义_参数_返回值|下一章：函数]]
