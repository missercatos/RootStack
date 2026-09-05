# python -c 一行流：系统管理速查 (One-Liner Cookbook)
---

## 章节概述

本章是一份实战速查手册：在 C 语言开发者的日常工作中，许多需要临时写 bash 命令或 C 小工具才能完成的任务，其实用 `python -c "..."` 一行就能搞定。本章按类别整理了文件操作、文本处理、JSON/CSV、网络请求、数学计算、系统信息等场景的常用一行流，每条都配有"替代了什么 bash/C 工作流"的说明。

> **核心理念**：Python 是 C 开发者的"超级 Shell"。当你需要一个 awk/sed/grep 的 bash 管道串了 5 步才能完成的事情时，`python -c` 用 1 行就能做到——而且可读性更好、跨平台更一致、处理 Unicode/JSON/二进制数据时不会像 bash 那样容易出错。

---

### 第一节：文件与目录操作

---

当你在终端里批量处理文件时，bash 的 `for f in *.c; do ... done` 常常会遇到空格文件名、子目录递归、条件过滤等痛点。Python 的 `os`/`glob`/`shutil`/`pathlib` 一行流更健壮。

**批量重命名：空格替换为下划线**

```bash
# bash 的做法——遇到文件名含空格就会炸
for f in *; do mv "$f" "$(echo $f | tr ' ' '_')"; done

# python -c 一行——安全处理任意文件名
python -c "import os; [os.rename(f, f.replace(' ', '_')) for f in os.listdir('.')]"
```

> `os.listdir('.')` 列出当前目录所有条目，列表推导式遍历并执行 `os.rename`。Python 字符串的 `replace` 方法天然支持 Unicode，不像 `tr` 只处理 ASCII。

**查找当前目录下最大的 5 个文件**

```bash
# bash —— 需要 du + sort + head 管道
du -sh * | sort -rh | head -5

# python -c
python -c "import os; files=[(os.path.getsize(f),f) for f in os.listdir('.') if os.path.isfile(f)]; [print(f'{s:>10} {n}') for s,n in sorted(files,reverse=True)[:5]]"
```

**递归统计每种文件扩展名的数量**

```bash
# bash —— find + awk 组合
find . -type f | sed 's/.*\.//' | sort | uniq -c | sort -rn

# python -c：更清晰的输出，且 `collections.Counter` 不需 sort | uniq
python -c "import os,collections; c=collections.Counter(); [c.update([os.path.splitext(f)[1] or '(无后缀)']) for r,_,fs in os.walk('.') for f in fs]; [print(f'{v:>5} {k}') for k,v in c.most_common()]"
```

> `os.walk` 递归遍历目录树，`collections.Counter` 一行完成统计+排序，比 `sort | uniq -c | sort -rn` 的管道更简洁。

**批量修改文件权限**

```bash
# 将所有 .sh 文件改为可执行
python -c "import os,glob; [os.chmod(f,0o755) for f in glob.glob('*.sh')]"
```

> `glob.glob` 支持通配符匹配，`os.chmod` 的权限值用八进制 `0o755` 表示（对应 bash 的 `chmod 755`）。

**复制目录树（排除 .o 和 build/）**

```bash
# bash —— rsync --exclude 需要记住复杂语法
rsync -av --exclude='*.o' --exclude='build/' src/ dst/

# python -c
python -c "import shutil; shutil.copytree('src','dst',ignore=shutil.ignore_patterns('*.o','build'))"
```

---

### 第二节：文本处理——grep/sed/awk 的 Python 平替

---

C 开发者习惯用 `grep` 搜索日志、用 `sed` 替换文本、用 `awk` 提取列。但这些工具在跨平台（尤其是 Windows）、处理 Unicode、处理多行模式时各有局限。Python 一行流弥补这些短板。

**grep 替代：搜索含特定模式的行**

```bash
# bash grep —— 搜索所有 .c 文件中含 TODO 的行
grep -rn "TODO" --include="*.c" .

# python -c：等效一行
python -c "import os,re; [print(f'{r}/{f}:{i+1}:{l}',end='') for r,_,fs in os.walk('.') for f in fs if f.endswith('.c') for i,l in enumerate(open(r+'/'+f)) if 'TODO' in l]"
```

**sed 替代：全局替换**

```bash
# 将当前目录所有 .txt 文件中的 "foo" 替换为 "bar"（原地修改）
python -c "
import fileinput, sys
for line in fileinput.input(sys.argv[1:], inplace=True):
 print(line.replace('foo', 'bar'), end='')
" *.txt
```

> `fileinput` 模块的 `inplace=True` 直接原地修改文件（内部操作是先备份→重写→删除备份），等效于 `sed -i 's/foo/bar/g' *.txt`，但在 Windows 上也同样工作。

**awk 替代：提取第 N 列**

```bash
# bash awk —— 提取 ps 输出的 PID 和 COMMAND 列
ps aux | awk '{print $2, $11}'

# python -c
ps aux | python -c "import sys; [print(*l.split()[1:2]+l.split()[10:11]) for l in sys.stdin]"
```

**统计代码行数（按文件类型）**

```bash
# 统计项目中各类型文件的行数
python -c "
import os, collections
c = collections.Counter()
for r,_,fs in os.walk('.'):
 for f in fs:
 ext = os.path.splitext(f)[1] or '(none)'
 try:
 c[ext] += sum(1 for _ in open(r+'/'+f))
 except: pass
for k,v in c.most_common():
 print(f'{v:>8} lines {k}')
"
```

> 这是 `cloc` 或 `wc -l` 的轻量替代。选择 `c.most_common()` 按行数降序输出。

**正则提取：从日志中提取所有 IP 地址并去重**

```bash
# bash —— grep -oP 需要 GNU grep（macOS 默认不支持 -P）
grep -oP '\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}' access.log | sort -u

# python -c：跨平台，且可做更多处理
python -c "
import re, sys
ips = set(re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', sys.stdin.read()))
print('\n'.join(sorted(ips)))
" < access.log
```

---

### 第三节：JSON 与 CSV 数据处理

---

C 语言处理 JSON 需要引入 cJSON/json-c/parson 等第三方库，处理 CSV 需要手动解析分隔符。Python 内置 `json` 和 `csv` 模块，一行读取并操作结构化数据。

**从 API 获取 JSON 并提取字段**

```bash
# 从 REST API 获取数据，提取 name 字段并排序输出
python -c "
import json, urllib.request
data = json.load(urllib.request.urlopen('https://api.github.com/repos/torvalds/linux/commits?per_page=10'))
for c in data:
 print(c['commit']['author']['name'], c['commit']['message'].split('\n')[0][:60])
"
```

> 一个 `python -c` 代替了 `curl | jq | sort` 的管道。`urllib.request` 是标准库，无需 `pip install requests`。

**CSV 转 JSON**

```bash
# 将 data.csv 转换为 data.json
python -c "
import csv, json, sys
reader = csv.DictReader(open('data.csv'))
json.dump(list(reader), open('data.json','w'), indent=2, ensure_ascii=False)
"
```

> `csv.DictReader` 自动将第一行作为列名，每行转为字典。`json.dump` 带 `indent=2` 美化输出。

**JSON 转 CSV（提取指定列）**

```bash
# 从 JSON 数组中提取 id 和 name 并写入 CSV
python -c "
import json, csv
data = json.load(open('users.json'))
writer = csv.DictWriter(open('out.csv','w'), fieldnames=['id','name'])
writer.writeheader()
[writer.writerow({'id':d['id'],'name':d['name']}) for d in data]
"
```

**命令行 JSON 格式化（jq 替代）**

```bash
# bash jq —— 格式化压缩 JSON
cat minified.json | jq .

# python -c
python -c "import json,sys; print(json.dumps(json.load(sys.stdin),indent=2,ensure_ascii=False))" < minified.json

# 更短的版本——用 -m 标志
python -m json.tool minified.json
```

> `python -m json.tool` 是最短的方式。加 `--sort-keys` 可按键排序输出。

**合并多个 CSV 文件**

```bash
# 将 split_*.csv 合并为一个文件（保留表头一次）
python -c "
import csv, glob
writer = csv.writer(open('merged.csv','w'))
for i,f in enumerate(sorted(glob.glob('split_*.csv'))):
 reader = csv.reader(open(f))
 for j,row in enumerate(reader):
 if j==0 and i>0: continue # 跳过后续文件的表头
 writer.writerow(row)
"
```

---

### 第四节：网络与系统信息

---

临时检测端口、发起 HTTP 请求、查看系统资源——这些操作在 C 中需要写几十行 socket 代码，在 Python 中用一行就能完成。

**端口是否可连接**

```bash
# 检测 localhost:8080 是否在监听
python -c "import socket; s=socket.socket(); s.settimeout(2); r=s.connect_ex(('127.0.0.1',8080)); print('OPEN' if r==0 else 'CLOSED'); s.close()"
```

> 等效于 `nc -zv 127.0.0.1 8080`，但不依赖 netcat 是否安装。`connect_ex` 返回 0 表示连接成功。

**HTTP GET 快速测试**

```bash
# 测试一个 URL 是否可达，输出状态码和响应体前 200 字符
python -c "
import urllib.request
try:
 r = urllib.request.urlopen('http://httpbin.org/get', timeout=5)
 print(f'Status: {r.status}')
 print(r.read().decode()[:200])
except Exception as e:
 print(f'Error: {e}')
"
```

**列出所有监听端口**

```bash
# bash —— ss -tlnp 或 netstat -tlnp
ss -tlnp

# python -c 获取简易版本
python -c "
import subprocess, re
out = subprocess.check_output(['ss','-tlnp']).decode()
for line in out.split('\n'):
 if 'LISTEN' in line:
 print(line)
"
```

> 当 `ss`/`netstat` 可用时，直接用它们更简单。此处展示 Python 调用外部命令并解析输出的模式——这种"Python 作为胶水调用 C 编写的系统工具"正是本教程的核心思想。

**获取 CPU/内存基本信息**

```bash
# 读取 /proc/cpuinfo 获取 CPU 型号（Linux）
python -c "print([l.split(':')[1].strip() for l in open('/proc/cpuinfo') if 'model name' in l][0])"

# 读取 /proc/meminfo 获取内存总量（Linux）
python -c "
for l in open('/proc/meminfo'):
 if l.startswith('MemTotal:'):
 print(l.split()[1], l.split()[2])
 break
"
```

> `/proc` 文件系统是 Linux 内核暴露的伪文件系统，由 C 语言编写的内核代码生成。Python 读取它就像读取普通文本文件，这正是"用 Python 操作 C 内核接口"的经典模式。

**base64 编码/解码**

```bash
# 编码字符串
echo -n "Hello World" | python -c "import sys,base64; print(base64.b64encode(sys.stdin.read().encode()).decode())"

# 解码
echo "SGVsbG8gV29ybGQ=" | python -c "import sys,base64; print(base64.b64decode(sys.stdin.read().strip()).decode())"
```

---

### 第五节：数学计算与随机数

---

C 程序员需要 `<math.h>` + `-lm` 链接才能做数学计算，需要 `srand()/rand()` 才能生成随机数。Python 内置运算符和 `math`/`random` 模块零依赖可用。

**快速计算**

```bash
# 当作计算器用——Python 原生支持大整数和浮点
python -c "print(2 ** 100)" # 大整数
python -c "print(sum(range(1, 101)))" # 1+2+...+100
python -c "import math; print(math.factorial(20))" # 阶乘
python -c "print(hex(255), oct(255), bin(255))" # 进制转换
```

> C 语言计算 `2**100` 需要 `unsigned long long` 溢出或引入 GMP 大数库。Python 整数自动扩展，无上限。

**随机数生成**

```bash
# 生成 10 个 1-100 的随机整数
python -c "import random; print([random.randint(1,100) for _ in range(10)])"

# 从列表中等概率随机选取
python -c "import random; print(random.choice(['gcc','clang','msvc']))"

# 生成随机密码（16 位字母数字）
python -c "import secrets,string; print(''.join(secrets.choice(string.ascii_letters+string.digits) for _ in range(16)))"
```

> `secrets` 模块使用操作系统级的加密安全随机源（Linux 上读取 `/dev/urandom`），比 `random` 模块更适合生成密码、Token 等安全场景。

**统计计算**

```bash
# 从 stdin 读取一列数字，计算均值、最大、最小
echo -e "3\n7\n2\n9\n5" | python -c "
import sys
nums = [int(l) for l in sys.stdin]
print(f'count={len(nums)} sum={sum(nums)} avg={sum(nums)/len(nums):.2f} min={min(nums)} max={max(nums)}')
"
```

> 一个 `python -c` 替代了 `awk '{sum+=$1} END {print sum/NR}'` 这样的复杂 awk 脚本。

**三角函数与常量**

```bash
python -c "import math; print(f'π={math.pi:.15f} e={math.e:.15f}')"
python -c "import math; print(math.sin(math.radians(30)), math.cos(math.radians(60)))"
```

---

### 第六节：一行流的组合技巧

---

真正的威力来自组合。以下展示如何将多个操作串联成一个 `python -c` 调用，同时保持可读性。

**技巧 1：用 `-c` 内部换行**

```bash
# 不要在 bash 单行中写超长代码——用引号内的换行
python -c "
import os, json, subprocess

# 步骤1：获取 C 源文件列表
files = [f for f in os.listdir('.') if f.endswith('.c')]

# 步骤2：统计每个文件的行数
stats = {f: sum(1 for _ in open(f)) for f in files}

# 步骤3：输出为 JSON
print(json.dumps(stats, indent=2))
"
```

> 在 `python -c "..." ` 内部可以使用换行和缩进——Python 解析器只关心缩进一致性，不关心 bash 行的数量。

**技巧 2：用 `sys.argv` 传参**

```bash
# 而不是在 -c 字符串内部拼接变量
python -c "
import sys, os
pattern = sys.argv[1]
for f in os.listdir('.'):
 if pattern in f:
 print(f)
" "TODO"
```

> `sys.argv[1]` 接收外部参数，避免手动拼接字符串时引号灾难。

**技巧 3：管道组合——Python 接在 bash 管道中间**

```bash
# bash 生成数据 → Python 处理 → 输出结果
find . -name '*.c' | python -c "
import sys, os
for line in sys.stdin:
 f = line.strip()
 size = os.path.getsize(f)
 print(f'{size:>10} {f}')
" | sort -rn | head -10
```

> Python 作为管道中一环：bash 负责文件发现，Python 负责数据转换，bash 继续排序。各取所长。

---

## 力扣练习

以下题目用于验证本章所学内容：

| 题号 | 题目 | 链接 | 涉及知识点 |
|------|------|------|-----------|
| — | 本章无对应力扣题 | — | 请用动手练习题自检 |
