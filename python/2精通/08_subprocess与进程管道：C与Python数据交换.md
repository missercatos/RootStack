# subprocess 与进程管道：C 与 Python 数据交换 (Process Integration)
---

## 章节概述

前面几章我们深入学习了 C ↔ Python 的紧耦合互操作——ctypes 调 C 库、CPython 内嵌。但还有一种更简单、更隔离的方式：**通过进程管道交换数据**。本章讲解 `subprocess` 模块，用 JSON、二进制 struct、MessagePack 等格式在 C 程序和 Python 脚本之间传递数据。这是最"低耦合"的互操作方案。

> **核心理念**：当你不想（或不能）修改 C 代码、不想要编译依赖、或者需要隔离崩溃风险时，进程管道是最朴实有效的方案。它遵循 Unix 哲学——每个程序做好一件事，用管道连接它们。

---

### 第一节：subprocess.run — 基础调用

#### 1.1 执行外部程序

```python
import subprocess

# 最简单：执行命令并等待完成
result = subprocess.run(['echo', 'Hello from C program!'],
 capture_output=True, text=True)
print(result.stdout) # Hello from C program!
print(result.returncode) # 0

# 无 capture_output 时，输出直接到终端
subprocess.run(['ls', '-la'])
```

`subprocess.run()` 的核心参数：

| 参数 | 作用 |
|------|------|
| `args` | 命令和参数（list 或 str） |
| `capture_output=True` | 捕获 stdout 和 stderr |
| `text=True` | 以文本模式（str）而非 bytes 返回 |
| `input="..."` | 向程序 stdin 发送数据 |
| `timeout=10` | 超时秒数，超时抛出 `TimeoutExpired` |
| `check=True` | 返回值非零时抛出 `CalledProcessError` |
| `env={...}` | 设置环境变量 |
| `cwd="/path"` | 设置工作目录 |

```bash
python -c "
import subprocess
result = subprocess.run(['python', '-c', 'print(1+2)'],
 capture_output=True, text=True)
print(repr(result.stdout)) # '3\n'
print('Exit:', result.returncode)
"
```

#### 1.2 与 C 程序交互

```c
// hello.c — 简单的 C 程序，从 stdin 读名字，向 stdout 输出
// 编译: gcc -o hello hello.c

#include <stdio.h>

int main() {
 char name[64];
 printf("What's your name? ");
 fflush(stdout);

 if (fgets(name, sizeof(name), stdin) == NULL) {
 fprintf(stderr, "Error reading input\n");
 return 1;
 }

 printf("Hello, %s", name); // name 已包含换行符
 return 0;
}
```

```python
import subprocess

result = subprocess.run(
 ['./hello'],
 input='Alice\n',
 capture_output=True,
 text=True
)
print(f"stdout: {result.stdout}")
print(f"stderr: {result.stderr}")
print(f"returncode: {result.returncode}")
```

输出：
```
stdout: What's your name? Hello, Alice
stderr: 
returncode: 0
```

---

### 第二节：Popen — 双向管道通信

`subprocess.run()` 是一次性的（等待子进程结束后获得输出）。`subprocess.Popen` 支持**双向通信**——启动子进程后，持续发送和接收数据。

#### 2.1 基础 Popen 用法

```python
import subprocess

# 启动子进程，不等待
proc = subprocess.Popen(
 ['./hello'],
 stdin=subprocess.PIPE,
 stdout=subprocess.PIPE,
 stderr=subprocess.PIPE,
 text=True
)

# 向 stdin 发送数据
stdout_data, stderr_data = proc.communicate(input='Bob\n')

print(f'stdout: {stdout_data!r}')
print(f'stderr: {stderr_data!r}')
print(f'returncode: {proc.returncode}')
```

#### 2.2 交互式双向通信

```c
// calc.c — 交互式计算器（读算式，写结果，直到输入 quit）
// 编译: gcc -o calc calc.c

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int main() {
 char line[256];
 double a, b;
 char op;

 while (1) {
 if (fgets(line, sizeof(line), stdin) == NULL) break;

 // 去掉换行符
 line[strcspn(line, "\n")] = '\0';

 if (strcmp(line, "quit") == 0) break;

 if (sscanf(line, "%lf %c %lf", &a, &op, &b) == 3) {
 double result;
 switch (op) {
 case '+': result = a + b; break;
 case '-': result = a - b; break;
 case '*': result = a * b; break;
 case '/': result = b != 0 ? a / b : 0; break;
 default:
 printf("ERROR: Unknown operator '%c'\n", op);
 fflush(stdout);
 continue;
 }
 printf("%g\n", result);
 } else {
 printf("ERROR: Invalid format\n");
 }
 fflush(stdout); // 立即刷新，确保 Python 端及时收到！
 }

 printf("BYE\n");
 fflush(stdout);
 return 0;
}
```

```python
# calc_client.py — Python 驱动 C 计算器
import subprocess

proc = subprocess.Popen(
 ['./calc'],
 stdin=subprocess.PIPE,
 stdout=subprocess.PIPE,
 stderr=subprocess.PIPE,
 text=True,
 bufsize=1 # 行缓冲
)

calculations = [
 "3.14 + 2.86",
 "100 * 0.5",
 "1 / 3",
 "invalid",
 "42 @ 10",
 "quit"
]

for expr in calculations:
 print(f">> {expr}")
 proc.stdin.write(expr + '\n')
 proc.stdin.flush()

 response = proc.stdout.readline().strip()
 print(f" {response}")

proc.wait()
print(f"Exit code: {proc.returncode}")
```

输出：
```
>> 3.14 + 2.86
 6
>> 100 * 0.5
 50
>> 1 / 3
 0.333333
>> invalid
 ERROR: Invalid format
>> 42 @ 10
 ERROR: Unknown operator '@'
>> quit
 BYE
Exit code: 0
```

> **关键细节**：C 程序中每次 `printf` 后必须 `fflush(stdout)`！否则输出留在 C 的缓冲区中，Python 端可能永远收不到。Python 端也可使用 `bufsize=1`（行缓冲）或 `bufsize=0`（无缓冲）。

---

### 第三节：数据交换格式

#### 3.1 JSON — 最通用的文本格式

C 端生成 JSON（需要一个 JSON 库，如 cJSON、json-c）：

```c
// json_writer.c — C 端输出 JSON 到 stdout
// 编译: gcc -o json_writer json_writer.c -lcjson

#include <stdio.h>
#include <cjson/cJSON.h>

int main() {
 cJSON *root = cJSON_CreateObject();

 cJSON_AddNumberToObject(root, "code", 0);
 cJSON_AddStringToObject(root, "message", "success");

 cJSON *data = cJSON_CreateObject();
 cJSON_AddNumberToObject(data, "count", 42);
 cJSON_AddStringToObject(data, "name", "sensor_01");

 double values[] = {1.1, 2.2, 3.3};
 cJSON *arr = cJSON_CreateDoubleArray(values, 3);
 cJSON_AddItemToObject(data, "values", arr);

 cJSON_AddItemToObject(root, "data", data);

 char *json_str = cJSON_Print(root);
 printf("%s\n", json_str);
 fflush(stdout);

 cJSON_free(json_str);
 cJSON_Delete(root);
 return 0;
}
```

```python
import subprocess
import json

result = subprocess.run(['./json_writer'], capture_output=True, text=True)
data = json.loads(result.stdout)

print(data) # {'code': 0, 'message': 'success', ...}
print(data['data']['values'][1]) # 2.2
```

JSON 的优缺点：

| 优点 | 缺点 |
|------|------|
| 人类可读，调试方便 | 有序列化/反序列化开销 |
| 跨语言，几乎所有语言都有库 | 二进制数据需 Base64 编码（膨胀 33%） |
| 格式灵活，字段可选 | 数值精度有限（double 范围内） |

#### 3.2 二进制结构体 — 高效紧凑

```c
// struct_gen.c — 输出二进制 struct 数组
// 编译: gcc -o struct_gen struct_gen.c

#include <stdio.h>
#include <stdint.h>

typedef struct {
 int32_t id;
 float value;
 uint32_t timestamp;
} Record; // 12 字节，紧凑！

int main() {
 Record records[3] = {
 {.id = 1, .value = 23.5, .timestamp = 1000},
 {.id = 2, .value = 24.1, .timestamp = 1001},
 {.id = 3, .value = 22.8, .timestamp = 1002},
 };

 fwrite(records, sizeof(Record), 3, stdout);
 fflush(stdout);
 return 0;
}
```

```python
import subprocess
import struct

result = subprocess.run(['./struct_gen'], capture_output=True)
data = result.stdout

# 解析二进制数据
record_format = '<i f I' # little-endian: int32, float, uint32
record_size = struct.calcsize(record_format) # 12

for i in range(len(data) // record_size):
 offset = i * record_size
 record = struct.unpack_from(record_format, data, offset)
 print(f'Record #{record[0]}: value={record[1]}, ts={record[2]}')
```

输出：
```
Record #1: value=23.5, ts=1000
Record #2: value=24.1, ts=1001
Record #3: value=22.8, ts=1002
```

二进制格式的优缺点：

| 优点 | 缺点 |
|------|------|
| 零解析开销（直接映射） | 不可读，调试困难 |
| 体积最小 | 跨平台问题（端序、对齐、类型大小） |
| 适合高频传输 | 字段固定，难以扩展 |

#### 3.3 MessagePack — 折中方案

```bash
# 安装
pip install msgpack
```

```python
# C 端: 用 mpac 库生成 MessagePack → stdout
# Python 端读取:
import subprocess
import msgpack

result = subprocess.run(['./msgpack_writer'], capture_output=True)
data = msgpack.unpackb(result.stdout)

print(data) # {'id': 1, 'values': [1.1, 2.2, 3.3], ...}
```

#### 3.4 格式选型建议

| 格式 | 体积 | 速度 | 可读性 | 最佳场景 |
|------|------|------|--------|---------|
| JSON | 大 | 慢 | 高 | 配置文件、低频数据、调试 |
| Binary struct | 极小 | 极快 | 无 | 高频采样、日志流、性能关键 |
| MessagePack | 中等 | 快 | 无 | 需要 schema-free 且体积敏感 |
| Protocol Buffers | 小 | 快 | 无 | 需要强 schema 验证和版本兼容 |

---

### 第四节：Python 调用 C 分析处理管道

#### 4.1 数据分析管道

```c
// sensor.c — 模拟传感器数据采集 C 程序
// 编译: gcc -O2 -o sensor sensor.c -lm

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <unistd.h>
#include <stdint.h>

typedef struct {
 uint32_t timestamp;
 float temperature;
 float humidity;
 float pressure;
} SensorData;

int main() {
 SensorData sample;

 for (int i = 0; i < 1000; i++) {
 sample.timestamp = 1000000 + i * 100; // 微秒
 sample.temperature = 25.0 + 5.0 * sin(i * 0.1);
 sample.humidity = 60.0 + 10.0 * cos(i * 0.05);
 sample.pressure = 1013.0 + (rand() % 50 - 25) * 0.1;

 fwrite(&sample, sizeof(SensorData), 1, stdout);
 fflush(stdout);
 usleep(1000); // 模拟实时采样间隔
 }
 return 0;
}
```

```python
# analyze.py — Python 端实时分析 C 传感器数据
import subprocess
import struct
from collections import deque

fmt = '<I f f f' # uint32, float * 3
record_size = struct.calcsize(fmt)

proc = subprocess.Popen(
 ['./sensor'],
 stdout=subprocess.PIPE,
 stderr=subprocess.DEVNULL
)

temps = deque(maxlen=100)
pressures = deque(maxlen=100)
count = 0

try:
 while count < 1000:
 raw = proc.stdout.read(record_size)
 if len(raw) < record_size:
 break

 ts, temp, humidity, pressure = struct.unpack(fmt, raw)
 temps.append(temp)
 pressures.append(pressure)
 count += 1

 # 每 50 条输出一次统计
 if count % 50 == 0:
 avg_temp = sum(temps) / len(temps)
 max_temp = max(temps)
 avg_press = sum(pressures) / len(pressures)
 print(f'[{count:4d}] temp: avg={avg_temp:.1f}°C '
 f'max={max_temp:.1f}°C '
 f'press: avg={avg_press:.1f}hPa')

finally:
 proc.terminate()
 proc.wait()

print(f'\n总计 {count} 条数据，分析完成')
```

---

### 第五节：对比 subprocess vs 内嵌 CPython

| 维度 | subprocess + 管道 | 内嵌 CPython |
|------|-------------------|-------------|
| 隔离性 | 强（独立进程，崩溃不互相影响） | 弱（同一进程，C crash → Python crash） |
| 性能 | 较低（序列化+进程创建+管道传输） | 高（零拷贝，直接 C API） |
| 复杂度 | 低（只需标准 I/O） | 高（需 CPython C API 编程） |
| 部署 | 简单（两独立可执行文件） | 需链接 `libpython` |
| 启动开销 | 大（每次启动新进程） | 小（已在同一进程） |
| 双向交互 | 受限于管道速度 | 直接函数调用 |
| 适用场景 | 批处理、管道链接、快速原型 | 高频调用、需零拷贝、长期运行 |

```python
# 场景 1：C 是独立的 CLI 工具 → 用 subprocess
result = subprocess.run(['ffmpeg', '-i', 'input.mp4', '-vn', 'output.mp3'])

# 场景 2：C 库需要高频调用 → 用内嵌
# 每秒 10000 次调用 Python 分析函数：subprocess 无法胜任
PyRun_SimpleString("analyze(data)"); // 零开销！
```

---

## 力扣练习

以下题目用于验证本章所学内容：

| 题号 | 题目 | 链接 | 涉及知识点 |
|------|------|------|-----------|
| — | 本章无对应力扣题 | — | 请用动手练习题自检 |
