# python -c 一行流：系统管理速查 (One-Liner Cookbook)
---

## 📖 章节概述

本章是一份实战速查手册：在 C 语言开发者的日常工作中，许多需要临时写 bash 命令或 C 小工具才能完成的任务，其实用 `python -c "..."` 一行就能搞定。本章按类别整理了文件操作、文本处理、JSON/CSV、网络请求、数学计算、系统信息等场景的常用一行流，每条都配有"替代了什么 bash/C 工作流"的说明。

> **核心理念**：Python 是 C 开发者的"超级 Shell"。当你需要一个 awk/sed/grep 的 bash 管道串了 5 步才能完成的事情时，`python -c` 用 1 行就能做到——而且可读性更好、跨平台更一致、处理 Unicode/JSON/二进制数据时不会像 bash 那样容易出错。

---

### 📚 第一节：文件与目录操作

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
python -c "import os; files=[(os.path.getsize(f),f) for f in os.listdir('.') if os.path.isfile(f)]; [print(f'{s:>10}  {n}') for s,n in sorted(files,reverse=True)[:5]]"
```

**递归统计每种文件扩展名的数量**

```bash
# bash —— find + awk 组合
find . -type f | sed 's/.*\.//' | sort | uniq -c | sort -rn

# python -c：更清晰的输出，且 `collections.Counter` 不需 sort | uniq
python -c "import os,collections; c=collections.Counter(); [c.update([os.path.splitext(f)[1] or '(无后缀)']) for r,_,fs in os.walk('.') for f in fs]; [print(f'{v:>5}  {k}') for k,v in c.most_common()]"
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

### 📝 小节练习

> [!question] 选择题 1
> `os.listdir('.')` 与 `os.walk('.')` 的核心区别是什么？
> - [ ] A. 完全一样，只是语法不同
> - [ ] B. `listdir` 只列当前目录，`walk` 递归遍历所有子目录
> - [ ] C. `walk` 只列文件，`listdir` 列出所有条目
> - [ ] D. `listdir` 更快所以应该总是用它
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `os.listdir(path)` 仅返回 path 目录下的条目名列表（不含子目录内容），`os.walk` 递归遍历整个目录树，每个迭代返回 (根路径, 子目录列表, 文件列表)。

> [!question] 选择题 2
> `os.chmod(f, 0o755)` 中的 `0o` 前缀表示什么？
> - [ ] A. 十进制数字
> - [ ] B. 十六进制数字
> - [ ] C. 八进制数字
> - [ ] D. 二进制数字
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: Python 中 `0o` 前缀表示八进制字面量，`0o755` 等于十进制 493，与 shell 中 `chmod 755` 的含义完全相同。

---

### 📚 第二节：文本处理——grep/sed/awk 的 Python 平替

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
    print(f'{v:>8} lines  {k}')
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

### 📝 小节练习

> [!question] 判断题 1
> `fileinput.input(inplace=True)` 会修改原文件内容。 ( )
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `inplace=True` 参数使 `fileinput` 将标准输出重定向到原文件，实现原地修改，等效于 `sed -i`。

> [!question] 选择题 1
> macOS 自带 `grep` 不支持 `-P` 选项，因为：
> - [ ] A. macOS 没有正则引擎
> - [ ] B. `-P` 是 GNU grep 专有的 PCRE 扩展，macOS 使用 BSD grep
> - [ ] C. 苹果禁止了正则表达式
> - [ ] D. 需要用 `brew install grep` 才支持
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: macOS 自带 BSD 版本的 grep，不支持 GNU 的 `-P`（Perl Compatible Regular Expressions）选项。Python 的 `re` 模块自带 PCRE 风格正则是更好的跨平台选择。

---

### 📚 第三节：JSON 与 CSV 数据处理

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
        if j==0 and i>0: continue  # 跳过后续文件的表头
        writer.writerow(row)
"
```

### 📝 小节练习

> [!question] 选择题 1
> `csv.DictReader` 的作用是？
> - [ ] A. 将 CSV 写入字典格式
> - [ ] B. 以字典形式读取 CSV 每一行，键为列名
> - [ ] C. 读取字典文件
> - [ ] D. 将 CSV 转为 Python 字典对象
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `csv.DictReader` 将 CSV 文件的第一行作为字段名，后续每行以 `{字段名: 值}` 的字典形式返回，方便按列名访问数据。

> [!question] 选择题 2
> `json.dump(obj, f, ensure_ascii=False)` 中 `ensure_ascii=False` 的效果是？
> - [ ] A. 允许输出非 ASCII 字符（如中文）的原形
> - [ ] B. 禁止输出任何 ASCII 字符
> - [ ] C. 加快 JSON 序列化速度
> - [ ] D. 使 JSON 失去跨平台兼容性
>
> > [!success]- 点击查看答案
> > 正确答案: A
> > **解析**: 默认 `ensure_ascii=True` 会将非 ASCII 字符转义为 `\uXXXX` 形式。设为 `False` 后中文等字符直接原形输出，可读性更好。

---

### 📚 第四节：网络与系统信息

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

### 📝 小节练习

> [!question] 判断题 1
> `socket.connect_ex()` 在连接成功时返回 0。 ( )
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `connect_ex` 返回错误码（而非抛出异常）。返回 0 表示连接成功，返回非 0 值对应 `errno` 错误码。

> [!question] 判断题 2
> `/proc/cpuinfo` 是一个真实的磁盘文件，由操作系统写入。 ( )
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `/proc` 是 procfs 伪文件系统，其中的"文件"不存储在磁盘上，而是由 Linux 内核在读取时动态生成内容。这是内核向用户态暴露信息的接口。

---

### 📚 第五节：数学计算与随机数

---

C 程序员需要 `<math.h>` + `-lm` 链接才能做数学计算，需要 `srand()/rand()` 才能生成随机数。Python 内置运算符和 `math`/`random` 模块零依赖可用。

**快速计算**

```bash
# 当作计算器用——Python 原生支持大整数和浮点
python -c "print(2 ** 100)"                   # 大整数
python -c "print(sum(range(1, 101)))"         # 1+2+...+100
python -c "import math; print(math.factorial(20))"   # 阶乘
python -c "print(hex(255), oct(255), bin(255))"     # 进制转换
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

### 📝 小节练习

> [!question] 选择题 1
> Python 中生成密码应优先使用 `secrets` 模块而非 `random` 模块，因为：
> - [ ] A. `secrets` 更快
> - [ ] B. `secrets` 使用操作系统加密安全随机源，不可预测
> - [ ] C. `random` 已被废弃
> - [ ] D. `secrets` 输出的字符串更短
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `random` 模块使用 Mersenne Twister 伪随机算法，在已知足够多样本后可以被预测。`secrets` 直接使用操作系统 `/dev/urandom` 等加密安全熵源，适用于安全场景。

> [!question] 选择题 2
> C 语言计算 `pow(2, 100)` 时可能遇到的问题是什么？
> - [ ] A. 编译失败
> - [ ] B. `double` 类型无法精确表示整数
> - [ ] C. 溢出（超出 `unsigned long long` 范围）
> - [ ] D. 以上全部
>
> > [!success]- 点击查看答案
> > 正确答案: D
> > **解析**: C 的 `pow()` 返回 `double`，对大整数会丢失精度；若用整数类型移位 `1ULL << 100` 会溢出（`unsigned long long` 通常 64 位，最大 `2^64-1`）。Python 整数精度无上限，`2**100` 精确计算。

---

### 📚 第六节：一行流的组合技巧

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
    print(f'{size:>10}  {f}')
" | sort -rn | head -10
```

> Python 作为管道中一环：bash 负责文件发现，Python 负责数据转换，bash 继续排序。各取所长。

### 📝 小节练习

> [!question] 判断题 1
> 在 `python -c "..."` 中不能使用换行，否则会报语法错误。 ( )
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: Python 语法允许在引号内使用换行，只要缩进正确即可。在 `python -c "..."` 中写多行代码是完全合法的常见做法。

> [!question] 选择题 1
> `python -c` 中获取命令行参数的正确方式是？
> - [ ] A. `$1`, `$2`
> - [ ] B. `sys.argv[1]`
> - [ ] C. `argc`, `argv`
> - [ ] D. `os.getenv('ARG1')`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `python -c` 后面的 `"..."` 是 Python 代码，bash 变量 `$1` 不会被展开（单引号内）。正确方式是 `python -c "... sys.argv[1] ..." "参数值"`，参数传入 `sys.argv`。

---

## 📋 章节测试

### 一、判断题（正确选✅，错误选❌）

> [!question] 判断题 1
> `python -c` 只能执行单行代码，不能写循环或条件语句。 ( )
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `python -c` 可执行任意 Python 代码，包括循环、条件、函数定义等。只需用引号括起多行代码（或在一行中用分号分隔）。

> [!question] 判断题 2
> `python -m json.tool` 可以用来格式化 JSON 文件。 ( )
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `python -m json.tool` 是标准库内置的 JSON 格式化工具，`-m` 表示以模块方式运行。

> [!question] 判断题 3
> `os.walk()` 比 `os.listdir()` 返回的结果更多，因为它递归遍历所有子目录。 ( )
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `os.walk` 递归遍历整个目录树，生成器每次 yield 一个三元组 (dirpath, dirnames, filenames)。`os.listdir` 只返回当前目录的条目名。

> [!question] 判断题 4
> Python 的 `random` 模块适合用于生成密码。 ( )
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `random` 使用可预测的 Mersenne Twister 算法，不应用于安全敏感场景。生成密码应使用 `secrets` 模块。

> [!question] 判断题 5
> `/proc/meminfo` 文件在 macOS 上也可以直接读取。 ( )
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `/proc` 是 Linux 特有的 procfs 伪文件系统，macOS 上不存在。macOS 获取系统信息需用 `sysctl` 命令或其他接口。

> [!question] 判断题 6
> 相比 bash 的 `sed -i`，`python -c` + `fileinput` 方案在 Windows 上同样可用。 ( )
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `fileinput` 模块是跨平台的。bash 的 `sed -i` 在 BSD sed（macOS）和 GNU sed 之间语法不同，而在 Windows 上根本没有 `sed`。

---

### 二、选择题（单项选择题）

> [!question] 选择题 1
> 以下哪个模块用于递归遍历目录树？
> - [ ] A. `os.listdir`
> - [ ] B. `os.walk`
> - [ ] C. `os.scandir`
> - [ ] D. `shutil.copytree`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `os.walk` 递归遍历目录树，`os.listdir` 仅列出单层，`os.scandir` 是 `listdir` 的高效替代，`shutil.copytree` 用于复制。

> [!question] 选择题 2
> `python -c "print(2 ** 100)"` 的输出结果与 C 语言 `printf("%llu", 1ULL << 100)` 相比：
> - [ ] A. 结果相同
> - [ ] B. Python 溢出，C 得到精确结果
> - [ ] C. Python 得到精确结果，C 溢出
> - [ ] D. 两者都溢出
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: Python 整数精度无上限，`2**100` 精确计算。C 的 `1ULL << 100` 在 64 位 `unsigned long long` 上行为是未定义的（移位位数 >= 类型宽度），可能得到 0 或其它结果。

> [!question] 选择题 3
> 在 `python -c` 中批量重命名文件的正确做法是：
> - [ ] A. 用 `subprocess.run('mv '+old+' '+new)` 逐文件调用外部命令
> - [ ] B. 用 `os.rename(old, new)` 直接调用系统调用
> - [ ] C. 用 `shutil.move` 加上 `--force` 参数
> - [ ] D. 没有内置方式，必须写 `.py` 脚本
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `os.rename` 直接调用 POSIX `rename(2)` 系统调用（Windows 上也模拟），高效且原子。用 `subprocess` 调用外部 `mv` 不仅慢，还会在文件名含空格时出错。

> [!question] 选择题 4
> `collections.Counter` 的 `most_common()` 方法返回：
> - [ ] A. 出现频率最高的元素的值
> - [ ] B. 按频率从高到低排序的 (元素, 计数) 列表
> - [ ] C. 计数最高的键
> - [ ] D. 出现频率的总和
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `most_common(n)` 返回前 n 个频率最高的 (元素, 计数) 元组，不指定 n 则返回所有元素，按频率降序排列。

> [!question] 选择题 5
> 以下哪种方式不能格式化 JSON 输出？
> - [ ] A. `python -m json.tool file.json`
> - [ ] B. `json.dumps(data, indent=2)`
> - [ ] C. `json.dump(data, f, indent=2)`
> - [ ] D. `json.format(file.json, indent=2)`
>
> > [!success]- 点击查看答案
> > 正确答案: D
> > **解析**: `json` 模块没有 `format` 函数。格式化 JSON 可用命令行 `python -m json.tool` 或代码中 `json.dumps(data, indent=2)` / `json.dump(data, f, indent=2)`。

> [!question] 选择题 6
> `python -c` 中访问外部命令行参数，应使用：
> - [ ] A. `sys.stdin`
> - [ ] B. `sys.argv`
> - [ ] C. `os.environ`
> - [ ] D. `sys.stdout`
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `sys.argv` 是命令行参数列表，`sys.argv[0]` 是脚本名（`-c` 的情况），`sys.argv[1:]` 是后续参数。`sys.stdin` 用于读取管道输入。

---

### 🛠️ 动手练习题

> [!example] 练习题 1：一行流替换 bash 管道
> **难度**: ⭐
>
> 你有一个 `access.log` 文件。原来的 bash 管道是：
> ```bash
> cat access.log | grep "404" | awk '{print $1}' | sort | uniq -c | sort -rn | head -10
> ```
> 请改写成单个 `python -c` 调用，实现相同的功能（找出产生 404 错误最多的前 10 个 IP）。

> [!example] 练习题 2：用 Python 做 C 项目的构建前检查
> **难度**: ⭐⭐
>
> 写一个 `python -c` 一行流，在你的 C 项目中完成以下检查：
> 1. 确保所有 `.c` 文件都有对应的 `.h` 文件（main.c 除外）
> 2. 确保所有 `.c` 文件都 `#include` 了对应的 `.h`
> 3. 输出缺失对应关系的结果
>
> 提示：使用 `os.listdir` + 文件内容 `in` 判断。

> [!example] 练习题 3：生成 C 数组字面量
> **难度**: ⭐
>
> 有时候在 C 代码中需要一个预计算的查找表（如三角函数表）。用 `python -c` 一行生成一个包含 0° 到 90° 每步 5° 的 sin 值的 C 数组声明：
> ```c
> const double sin_table[] = {0.000000, 0.087156, 0.173648, ... };
> ```
> 输出可直接复制到 C 源文件中。提示：`math.sin(math.radians(x))`。

> [!example] 练习题 4：JSON 配置 → C 宏定义
> **难度**: ⭐⭐
>
> C 项目经常用 `#define MAX_BUFFER 1024` 等宏配置。用 `python -c` 读取 JSON 配置文件 `config.json`：
> ```json
> {"MAX_BUFFER": 1024, "SERVER_PORT": 8080, "LOG_LEVEL": 2}
> ```
> 生成对应的 `#define` 语句，输出到 `config.h`。提示：`json.load` + 字符串格式化。
