# bash vs python：何时用哪个 | Bash vs Python: When to Use Which

## 章节概述

> **核心理念**：Bash 和 Python 不是竞争关系，而是互补关系。Bash 擅长系统管理、管道操作和快速脚本；Python 擅长复杂逻辑、数据处理和可维护性。选择正确的工具，就像选择 C 还是 Python 一样——关键在于场景。

---

### 第1节：性能对比

#### 1.1 执行速度

```bash
# Bash: 简单文件操作（秒级）
time (for i in $(seq 1 10000); do echo "line $i" >> /tmp/test.txt; done)
# 结果: ~0.5s

# Python: 相同操作（毫秒级）
python3 -c "
import time
start = time.time()
with open('/tmp/test.py', 'w') as f:
    for i in range(10000):
        f.write(f'line {i}\n')
print(f'{time.time()-start:.3f}s')
"
# 结果: ~0.003s
```

| 操作类型 | Bash 耗时 | Python 耗时 | 说明 |
|----------|-----------|-------------|------|
| 简单文件操作 | 0.5s | 0.003s | Python 快 150 倍 |
| 循环计算 | 2.3s | 0.01s | Python 快 200 倍 |
| 字符串处理 | 1.2s | 0.05s | Python 快 24 倍 |
| 系统命令调用 | 0.8s | 0.9s | 基本相同（I/O 瓶颈） |
| 管道操作 | 0.2s | 1.5s | Bash 更快（原生支持） |

#### 1.2 性能曲线

```
任务复杂度 vs 执行时间:

时间 ↑
     |     Bash
     |    /
     |   /
     |  /
     | /________________ Python
     +--------------------→ 任务复杂度
     简单    中等    复杂
```

### 第2节：适用场景表

| 场景 | 推荐工具 | 原因 |
|------|----------|------|
| 系统管理（用户/进程/磁盘） | **Bash** | 直接调用系统命令 |
| 文件批量操作 | **Bash** | find/xargs/管道高效 |
| 日志分析 | **两者** | 简单用 Bash，复杂用 Python |
| Web 爬虫 | **Python** | requests/BeautifulSoup 库 |
| API 调用 | **两者** | 简单 curl，复杂用 Python |
| 数据分析 | **Python** | pandas/numpy 库 |
| 机器学习 | **Python** | scikit-learn/PyTorch |
| 快速原型 | **Bash** | 无需编译/导入 |
| 可维护脚本 | **Python** | 更好的错误处理/类型 |
| CI/CD 脚本 | **Bash** | 更轻量/无依赖 |
| 复杂逻辑 | **Python** | 更清晰的语法 |
| 定时任务 | **Bash** | cron 原生支持 |
| 网络工具 | **两者** | curl/nc vs requests/socket |
| 自动化测试 | **Python** | pytest/unittest 框架 |

### 第3节：字符串处理对比

#### 3.1 Bash 字符串操作

```bash
# Bash 字符串操作（原生支持，速度快）
str="Hello, World!"

echo "${#str}"           # 长度: 12
echo "${str:0:5}"        # 子串: Hello
echo "${str/World/Bash}" # 替换: Hello, Bash!
echo "${str,,}"          # 转小写: hello, world!
echo "${str^^}"          # 转大写: HELLO, WORLD!
echo "${str##*,}"        # 删除前缀: World!
echo "${str%%,*}"        # 删除后缀: Hello
```

#### 3.2 Python 字符串操作

```python
# Python 字符串操作（更丰富的功能）
s = "Hello, World!"

print(len(s))           # 长度: 12
print(s[:5])            # 子串: Hello
print(s.replace("World", "Python"))  # 替换
print(s.lower())        # 转小写
print(s.upper())        # 转大写
print(s.split(", "))    # 分割: ['Hello', 'World!']
print(", ".join(s.split(", ")))  # 合并
```

#### 3.3 正则表达式对比

```bash
# Bash + grep/sed/awk
echo "2026-08-22 10:30:00" | grep -oP '\d{4}-\d{2}-\d{2}'

echo "foo123bar" | sed -E 's/[0-9]+/NUM/g'

echo "a=1 b=2 c=3" | awk '{for(i=1;i<=NF;i++) if($i~=/=/) print $i}'
```

```python
# Python re 模块
import re

match = re.search(r'\d{4}-\d{2}-\d{2}', "2026-08-22 10:30:00")

text = "foo123bar"
result = re.sub(r'\d+', 'NUM', text)

pairs = re.findall(r'(\w+)=(\d+)', "a=1 b=2 c=3")
```

### 第4节：系统调用对比

#### 4.1 进程管理

```bash
# Bash: 直接调用
ps aux | grep nginx
kill -9 $(pgrep nginx)
nice -n 10 ./heavy_task.sh
```

```python
# Python: subprocess 模块
import subprocess

result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
nginx_lines = [l for l in result.stdout.split('\n') if 'nginx' in l]

subprocess.run(['kill', '-9', str(pid)])
subprocess.run(['nice', '-n', '10', './heavy_task.sh'])
```

#### 4.2 文件系统操作

```bash
# Bash: 文件操作
find /var/log -name "*.log" -mtime +7 -delete
ls -la | awk '{print $5, $9}' | sort -rn
stat -c "%s %n" file.txt
```

```python
# Python: os/pathlib 模块
from pathlib import Path
import os

# 查找并删除
for f in Path('/var/log').rglob('*.log'):
    if f.stat().st_mtime < time.time() - 7*86400:
        f.unlink()

# 文件信息
for f in Path('.').iterdir():
    print(f'{f.stat().st_size} {f.name}')
```

### 第5节：网络操作对比

#### 5.1 HTTP 请求

```bash
# Bash: curl
curl -s https://api.example.com/data
curl -s -X POST https://api.example.com/data -d '{"key":"value"}'
curl -s -H "Authorization: Bearer TOKEN" https://api.example.com/me
```

```python
# Python: requests
import requests

resp = requests.get('https://api.example.com/data')
resp = requests.post('https://api.example.com/data', json={'key': 'value'})
resp = requests.get('https://api.example.com/me', headers={'Authorization': 'Bearer TOKEN'})
```

#### 5.2 JSON 处理

```bash
# Bash: jq
curl -s https://api.example.com/users | jq '.[] | {name: .name, email: .email}'
echo '{"a":1,"b":2}' | jq '.a + .b'
```

```python
# Python: json 模块
import json
import requests

data = requests.get('https://api.example.com/users').json()
users = [{'name': u['name'], 'email': u['email']} for u in data]

obj = json.loads('{"a":1,"b":2}')
result = obj['a'] + obj['b']
```

### 第6节：数据处理对比

#### 6.1 CSV 处理

```bash
# Bash: awk
awk -F',' '{print $1, $3}' data.csv
awk -F',' '{sum+=$3} END {print sum}' data.csv
sort -t',' -k3 -rn data.csv | head -10
```

```python
# Python: csv/pandas
import csv
import pandas as pd

# 基础读取
with open('data.csv') as f:
    reader = csv.DictReader(f)
    names = [(row['name'], row['amount']) for row in reader]

# pandas 高级操作
df = pd.read_csv('data.csv')
print(df[['name', 'amount']])
print(df['amount'].sum())
print(df.nlargest(10, 'amount'))
```

### 第7节：混合使用模式

#### 7.1 Bash 调用 Python

```bash
#!/bin/bash
# Bash 作为外层，Python 处理复杂逻辑

# 简单的 JSON 解析
config=$(python3 -c "
import json
with open('config.json') as f:
    data = json.load(f)
print(data['database']['host'])
")

echo "Database host: $config"

# Python 作为数据处理器
awk '{print $1, $3}' data.csv | python3 -c "
import sys
from collections import Counter
words = Counter(line.split()[0] for line in sys.stdin)
for word, count in words.most_common(10):
    print(f'{word}: {count}')
"
```

#### 7.2 Python 调用 Bash

```python
import subprocess

# 执行 Bash 命令
result = subprocess.run(
    ['ls', '-la'],
    capture_output=True,
    text=True,
    shell=False  # 安全考虑
)

# 处理管道
result = subprocess.run(
    'ps aux | grep nginx | wc -l',
    shell=True,  # 需要 shell=True 才能使用管道
    capture_output=True,
    text=True
)
print(f'Nginx processes: {result.stdout.strip()}')
```

#### 7.3 混合脚本模式

```bash
#!/usr/bin/env bash
# 混合模式：Bash 做系统操作，Python 做数据处理

set -euo pipefail

# 1. 使用 Bash 收集系统信息
echo "=== System Info ==="
echo "Hostname: $(hostname)"
echo "Uptime: $(uptime -p)"
echo "Memory: $(free -h | awk '/Mem:/ {print $3 "/" $2}')"

# 2. 使用 Python 分析日志
python3 << 'EOF'
import re
from collections import defaultdict

log_file = '/var/log/syslog'
error_counts = defaultdict(int)

with open(log_file) as f:
    for line in f:
        if 'error' in line.lower():
            # 提取程序名
            match = re.search(r'(\w+):', line)
            if match:
                error_counts[match.group(1)] += 1

print("\n=== Top Error Sources ===")
for source, count in sorted(error_counts.items(), key=lambda x: -x[1])[:10]:
    print(f"  {source}: {count}")
EOF

# 3. 使用 Bash 发送报告
echo "Report generated at $(date)"
```

### 第8节：决策树

```
需要处理复杂数据结构？
├── 是 → 使用 Python
└── 否 → 
    需要调用系统命令？
    ├── 是 → 使用 Bash
    └── 否 →
        需要良好的错误处理？
        ├── 是 → 使用 Python
        └── 否 →
            需要快速原型？
            ├── 是 → 使用 Bash
            └── 否 →
                需要长期维护？
                ├── 是 → 使用 Python
                └── 否 → 使用 Bash
```
