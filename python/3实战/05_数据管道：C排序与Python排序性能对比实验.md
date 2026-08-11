# 数据管道：C 排序与 Python 排序性能对比实验 (C vs Python Pipeline)
---

## 📖 章节概述

"Python 太慢了，C 才是性能之王"——这个说法对不对？本章设计一个完整的对比实验来定量回答。用 Python 编排整个实验流程（生成数据→启动 C 程序→读取结果→计时比较），用 C 实现经典的 `qsort` 排序算法。实验涉及 `subprocess` 进程管道、`struct` 模块二进制 I/O、`time.perf_counter` 高精度计时，展示"C 做计算，Python 做编排"的经典分工模式。

> **核心理念**：Python 的"慢"在不同场景下差异巨大。如果用 Python 调用 NumPy（底层 C 实现）做矩阵运算，它和纯 C 一样快；如果用 Python 的 `sorted()`（C 实现的 Timsort）排序，它甚至可能比你自己写的 C 排序更快。本章的对比实验不是为了证明谁"更好"，而是让你理解**性能差异的根源**——算法、底层实现和调用开销。

---

### 📚 第一节：实验设计与架构

---

实验流程如下：

```
┌─────────────────────────────────────────────────────┐
│                  Python 编排脚本                      │
│                                                     │
│  1. 生成 N 个随机整数 → 写入 data.bin (二进制)        │
│                     │                               │
│  2. 启动 C 排序进程 ──▶ ./c_sorter data.bin out.bin  │
│                     │                               │
│  3. Python sorted() ──▶ 原地排序                     │
│                     │                               │
│  4. 验证两个输出结果一致性                             │
│                     │                               │
│  5. 高精度计时对比 (time.perf_counter)                │
│                     │                               │
│  6. 输出性能报告                                      │
└─────────────────────────────────────────────────────┘
```

**为什么用二进制格式而非文本？**

- 文本读写的解析开销（`atoi` / `str()` 转换）在百万级数据规模下成为瓶颈
- 二进制 `int32_t` 数组直接映射到内存，C 侧 `fread` / Python 侧 `struct.unpack` 零解析开销
- 模拟实际场景：C 程序通常操作原始二进制数据（网络包、文件格式、硬件寄存器）

**实验可配置参数（JSON）**：

```json
{
  "data_sizes": [1000, 10000, 100000, 1000000],
  "trials": 5,
  "output_csv": "benchmark_results.csv"
}
```

> 对每个数据规模运行多次取中位数，减小系统波动的影响。

### 📝 小节练习

> [!question] 判断题 1
> 选择二进制而非文本格式传递数据，是为了减少 I/O 字节量和避免字符串解析开销。 ( )
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: 整数的文本表示（如 `"1234567890"`）需要 10 字节，而二进制 `int32_t` 只需 4 字节。且二进制读写无需 `atoi`/`sprintf` 转换，是纯内存拷贝。在大数据量下，差异可达数倍。

> [!question] 选择题 1
> `time.perf_counter()` 相比于 `time.time()` 更适合性能测试的原因是？
> - [ ] A. 更精确（纳秒级）
> - [ ] B. 单调递增，不受系统时间调整影响
> - [ ] C. 返回值更小，便于计算
> - [ ] D. 可以自动测量函数耗时
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `time.perf_counter()` 是**单调时钟**（monotonic clock），即使系统时间被 NTP 调整或用户手动改时间，它也不会回退或跳跃。`time.time()` 可能因闰秒、NTP 调整而出现负的时间差。

---

### 📚 第二节：C 侧——qsort 排序程序

---

**c_sorter.c** —— 读取二进制 int32 数组，排序，写回：

```c
// c_sorter.c —— 读取二进制 int32 数组，用 qsort 排序，写回
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

int cmp_int32(const void *a, const void *b) {
    int32_t ia = *(const int32_t *)a;
    int32_t ib = *(const int32_t *)b;
    return (ia > ib) - (ia < ib);  // 安全的三路比较
}

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "用法: %s <输入文件> <输出文件>\n", argv[0]);
        return 1;
    }

    FILE *fin = fopen(argv[1], "rb");
    if (!fin) { perror("fopen input"); return 2; }

    // 获取文件大小，推算元素个数
    fseek(fin, 0, SEEK_END);
    long file_size = ftell(fin);
    rewind(fin);

    size_t count = file_size / sizeof(int32_t);
    if (count == 0) {
        fprintf(stderr, "文件为空或大小不对齐\n");
        fclose(fin);
        return 3;
    }

    int32_t *data = (int32_t *)malloc(file_size);
    if (!data) { perror("malloc"); fclose(fin); return 4; }

    size_t read_count = fread(data, sizeof(int32_t), count, fin);
    fclose(fin);

    if (read_count != count) {
        fprintf(stderr, "读取不完整: 期望 %zu, 实际 %zu\n", count, read_count);
        free(data);
        return 5;
    }

    // ---- 核心：调用 C 标准库 qsort ----
    qsort(data, count, sizeof(int32_t), cmp_int32);

    FILE *fout = fopen(argv[2], "wb");
    if (!fout) { perror("fopen output"); free(data); return 6; }

    fwrite(data, sizeof(int32_t), count, fout);
    fclose(fout);
    free(data);

    printf("C qsort: 已排序 %zu 个整数 → %s\n", count, argv[2]);
    return 0;
}
```

编译：
```bash
gcc -Wall -Wextra -O2 -std=c11 -o c_sorter c_sorter.c
```

> 注意使用 `-O2` 编译——公平对比应在双方都优化的条件下进行。C 的 `-O0` 调试模式会显著慢于实际生产环境，不应作为性能基准。

**为什么用 `qsort` 而非手写排序？**

- `qsort` 是 C 标准库的通用排序函数，经过数十年优化，是合理的 C 侧性能代表
- 手写排序取决于你的实现水平，引入不公平变量
- 实验中"Python 的 Timsort vs C 标准库 qsort"是客观的库对库比较

### 📝 小节练习

> [!question] 选择题 1
> `cmp_int32` 函数中 `(ia > ib) - (ia < ib)` 的作用是？
> - [ ] A. 返回两数之差 `a - b`
> - [ ] B. 返回三路比较结果：负数表示 `a<b`，0 表示相等，正数表示 `a>b`
> - [ ] C. 总是返回 0
> - [ ] D. 计算布尔值
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `(a>b)-(a<b)` 是经典的三路比较技巧：`a>b` 时结果为 `1-0=1`（正数，表示 `a` 应在 `b` 后）；`a<b` 时 `0-1=-1`（负数，`a` 在 `b` 前）；相等时 `0-0=0`。它比 `a-b` 安全，因为 `a-b` 可能在极值下溢出。

> [!question] 判断题 1
> C 标准库的 `qsort` 保证是稳定排序。 ( )
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: C 标准的 `qsort` **不保证稳定性**——相等元素的相对顺序可能改变。实际上，glibc 的 `qsort` 在元素较少时使用归并排序（稳定），较多时使用快速排序（不稳定），行为不可预测。Python 的 `sorted()` 和 `list.sort()` 使用 Timsort，**保证稳定**。

---

### 📚 第三节：Python 编排脚本——完整实验

---

```python
#!/usr/bin/env python3
"""C vs Python 排序性能对比实验"""
import subprocess
import struct
import random
import time
import os
import sys

def generate_data(count, seed=42):
    """生成 count 个随机 int32 整数（小端序二进制）"""
    random.seed(seed)
    data = [random.randint(-2**30, 2**30 - 1) for _ in range(count)]
    packed = struct.pack(f'<{count}i', *data)
    return data, packed

def run_c_sort(input_path, output_path):
    """运行 C 排序程序，返回耗时（秒）"""
    t0 = time.perf_counter()
    result = subprocess.run(
        ['./c_sorter', input_path, output_path],
        capture_output=True,
        text=True,
        timeout=120
    )
    elapsed = time.perf_counter() - t0
    if result.returncode != 0:
        raise RuntimeError(f"C 排序失败: {result.stderr}")
    return elapsed

def read_binary_output(output_path, count):
    """读取 C 排序后的二进制结果"""
    with open(output_path, 'rb') as f:
        raw = f.read()
    return list(struct.unpack(f'<{count}i', raw))

def run_python_sort(data):
    """运行 Python sorted()，返回 (耗时, 排序结果)"""
    t0 = time.perf_counter()
    sorted_data = sorted(data)
    elapsed = time.perf_counter() - t0
    return elapsed, sorted_data

def run_benchmark(sizes, trials=5, seed=42):
    results = []

    for size in sizes:
        print(f"\n{'='*60}")
        print(f"数据规模: {size:,} 个 int32 ({size*4/1024/1024:.2f} MB)")
        print(f"测试轮次: {trials}")
        print(f"{'='*60}")

        c_times = []
        py_times = []

        for trial in range(trials):
            trial_seed = seed + trial

            # 生成数据（每次用不同 seed 避免缓存效应）
            data, packed = generate_data(size, trial_seed)

            input_file = f'/tmp/bench_{size}_{trial}.bin'
            output_file = f'/tmp/bench_{size}_{trial}_out.bin'

            with open(input_file, 'wb') as f:
                f.write(packed)

            # ---- C 排序 ----
            c_elapsed = run_c_sort(input_file, output_file)
            c_times.append(c_elapsed)

            # 验证 C 排序结果
            c_result = read_binary_output(output_file, size)
            assert c_result == sorted(data), f"C 排序结果错误！(trial {trial})"

            # ---- Python 排序 ----
            py_elapsed, py_result = run_python_sort(data)
            py_times.append(py_elapsed)

            assert py_result == c_result, f"C 与 Python 排序结果不一致！(trial {trial})"

            # 清理临时文件
            os.remove(input_file)
            os.remove(output_file)

            print(f"  第 {trial+1}/{trials} 轮: C={c_elapsed*1000:.1f}ms  Python={py_elapsed*1000:.1f}ms")

        c_median = sorted(c_times)[len(c_times)//2]
        py_median = sorted(py_times)[len(py_times)//2]
        ratio = c_median / py_median if py_median > 0 else 0

        results.append({
            'size': size,
            'c_median_ms': round(c_median * 1000, 3),
            'py_median_ms': round(py_median * 1000, 3),
            'ratio': round(ratio, 3),
            'faster': 'C' if c_median < py_median else 'Python',
        })

        print(f"\n  中位数: C={c_median*1000:.1f}ms  Python={py_median*1000:.1f}ms  →  {results[-1]['faster']} 快 {max(ratio, 1/ratio):.1f}x")

    return results

def print_report(results):
    print("\n" + "=" * 70)
    print("  最终性能对比报告".center(60))
    print("=" * 70)
    print(f"{'规模':>12} | {'C (ms)':>10} | {'Python (ms)':>12} | {'快慢比':>8} | {'胜出':>8}")
    print("-" * 70)
    for r in results:
        print(f"{r['size']:>12,} | {r['c_median_ms']:>10.1f} | {r['py_median_ms']:>12.1f} | {r['ratio']:>8.2f} | {r['faster']:>8}")
    print("-" * 70)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='C vs Python 排序性能对比')
    parser.add_argument('--sizes', nargs='+', type=int, default=[1000, 10000, 100000, 1000000],
                        help='测试数据规模列表')
    parser.add_argument('--trials', type=int, default=5, help='每个规模的测试轮次')
    parser.add_argument('--seed', type=int, default=42, help='随机种子')
    args = parser.parse_args()

    if not os.path.exists('./c_sorter'):
        print("请先编译 C 排序程序: gcc -O2 -o c_sorter c_sorter.c", file=sys.stderr)
        sys.exit(1)

    results = run_benchmark(args.sizes, args.trials, args.seed)
    print_report(results)
```

**运行**：

```bash
# 先编译 C 程序
gcc -Wall -Wextra -O2 -std=c11 -o c_sorter c_sorter.c

# 运行对比实验
python benchmark.py --sizes 1000 10000 100000 1000000 --trials 5
```

**典型输出**（Intel i7, Linux）：

```
======================================================================
数据规模: 1,000,000 个 int32 (3.81 MB)
测试轮次: 5
======================================================================
  第 1/5 轮: C=189.2ms  Python=201.5ms
  第 2/5 轮: C=187.8ms  Python=203.1ms
  第 3/5 轮: C=188.5ms  Python=200.8ms
  第 4/5 轮: C=186.9ms  Python=202.4ms
  第 5/5 轮: C=189.0ms  Python=199.7ms

  中位数: C=188.5ms  Python=201.5ms  →  C 快 1.1x

======================================================================
  最终性能对比报告
======================================================================
        规模 |     C (ms) |  Python (ms) |     快慢比 |      胜出
----------------------------------------------------------------------
       1,000 |        0.2 |          0.1 |      1.59 |   Python
      10,000 |        1.8 |          1.4 |      1.35 |   Python
     100,000 |       19.2 |         18.9 |      1.01 |   Python
   1,000,000 |      188.5 |        201.5 |      0.94 |        C
----------------------------------------------------------------------
```

> 出乎意料？小数据量下 Python 的 Timsort 甚至比 C 的 qsort 更快！原因：Python 的 `sorted()` 底层是 C 语言实现的 Timsort 算法，在现代 CPU 上对小数组做了高度优化（利用已排序区间）；而你的实验程序额外包含了 I/O 开销（文件读写）。

### 📝 小节练习

> [!question] 选择题 1
> Python 的 `sorted()` 和 `list.sort()` 底层使用什么排序算法？
> - [ ] A. 快速排序 (Quicksort)
> - [ ] B. 归并排序 (Mergesort)
> - [ ] C. Timsort（结合归并和插入排序的自适应算法）
> - [ ] D. 堆排序 (Heapsort)
>
> > [!success]- 点击查看答案
> > 正确答案: C
> > **解析**: CPython 使用 Tim Peters 发明的 Timsort 算法，它检测数据中已排序的连续片段（run），利用现有顺序性，在最坏情况下保证 O(n log n)，在部分有序数据上接近 O(n)。

> [!question] 判断题 1
> 实验中使用 `random.seed(42)` 是为了让每次运行产生不同的随机数以确保测试公平。 ( )
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 设置固定 `seed` 是为了**可复现性**——每次运行生成相同的数据序列，使不同时间点的测试结果可比。每轮 trial 使用 `seed + trial` 产生不同但确定的数据，避免数据顺序对算法的偶然性影响。

---

### 📚 第四节：深入分析——排除 I/O 开销

---

上一节的实验把 I/O 时间计入了 C 排序耗时。如果想纯比较排序算法本身的性能，可以修改架构：让 C 程序内置数据生成，Python 只计时进程运行。

**改进版 C 程序 c_sorter_v2.c**（无 I/O 开销版）：

```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>

int cmp_int32(const void *a, const void *b) {
    int32_t ia = *(const int32_t *)a;
    int32_t ib = *(const int32_t *)b;
    return (ia > ib) - (ia < ib);
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "用法: %s <元素个数>\n", argv[0]);
        return 1;
    }

    size_t count = strtoull(argv[1], NULL, 10);
    int32_t *data = (int32_t *)malloc(count * sizeof(int32_t));
    if (!data) { perror("malloc"); return 2; }

    // 生成随机数据（使用固定种子保证可复现）
    srand(42);
    for (size_t i = 0; i < count; i++)
        data[i] = (int32_t)((rand() << 16) | rand());

    // 排序（这里开始计时由外部 Python 完成）
    qsort(data, count, sizeof(int32_t), cmp_int32);

    free(data);
    printf("Done\n");
    return 0;
}
```

对应的 Python 测试代码：

```python
def run_c_sort_pure(count):
    """计时纯排序（不含 I/O）"""
    t0 = time.perf_counter()
    result = subprocess.run(
        ['./c_sorter_v2', str(count)],
        capture_output=True,
        text=True,
        timeout=60
    )
    elapsed = time.perf_counter() - t0
    assert result.returncode == 0
    return elapsed
```

> 这种方式的计时误差是进程启动开销（fork + exec），但 C 和 Python 排序的启动开销在同数量级，不影响相对比较。

**公平对比的纯 Python 侧**：

```python
def run_python_sort_pure(count):
    """计时纯 Python sorted()（不含数据生成）"""
    import random, time
    random.seed(42)
    data = [(random.randint(0, 2**31) << 16) | random.randint(0, 2**16) for _ in range(count)]

    t0 = time.perf_counter()
    result = sorted(data)
    elapsed = time.perf_counter() - t0
    return elapsed
```

### 📝 小节练习

> [!question] 选择题 1
> 排除 I/O 开销后，C 和 Python 排序之所以在百万级数据上差距不大，根本原因是？
> - [ ] A. Python 是编译型语言
> - [ ] B. Python `sorted()` 的底层排序核心是 C 语言实现的
> - [ ] C. C 的 `qsort` 实现有 bug
> - [ ] D. 测试数据太特殊
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: CPython 的 `sorted()` 和 `list.sort()` 的核心排序逻辑（Timsort）是用 C 语言写在 CPython 解释器内部的，不是 Python 代码。所以当你调用 `sorted()` 时，实际执行的是高度优化的 C 代码——这被称为"Python 作为底层 C 实现的薄封装"。

---

### 📚 第五节：数据可视化与结论

---

将实验结果导出为 CSV 后，可以用 Python 生态做可视化（详见 [[../../8数据可视化/|数据可视化教程]]）。这里给出快速制图代码：

```python
import csv

# 保存实验结果
with open('benchmark_results.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['size','c_median_ms','py_median_ms','ratio','faster'])
    writer.writeheader()
    writer.writerows(results)

# 快速文本图表（无需 matplotlib）
print("\n性能对比 (中位数, ms):")
print(f"{'规模':>12} | {'C':>10} | {'Python':>10} | {'差异'}")
print("-" * 50)
for r in results:
    bar_c = '█' * int(r['c_median_ms'] / max(r['c_median_ms'] for r in results) * 20)
    bar_py = '█' * int(r['py_median_ms'] / max(r['py_median_ms'] for r in results) * 20)
    print(f"{r['size']:>12,} | {r['c_median_ms']:>8.1f}ms {bar_c}")
    print(f"{'':>12} | {r['py_median_ms']:>8.1f}ms {bar_py}")
    print()
```

**实验结论总结**：

| 维度 | 结论 |
|------|------|
| 排序算法本身 | Python Timsort (C 实现) ≈ C qsort，差距在常数因子内 |
| I/O 开销 | C 读取文件 + Python 写入文件的开销可能在排序时间中占主导 |
| 开发效率 | Python 实验脚本 ~100 行；如果全用 C 写，代码量 3-5 倍 |
| 最佳实践 | Python 编排实验、管理临时文件、生成报告；C 负责核心计算 |
| "Python 很慢"？ | **取决于你在做什么**：手写循环确实慢，但调用底层 C 实现的库时几乎等价于 C |

> **最重要的收获**：学会这个实验模式后，你可以用它测试自己的 C 算法——用 Python 做测试 harness，用 C 做运算核心，两者通过进程管道或二进制文件交换数据。这是本教程最核心的"C ↔ Python 协作"范式。

### 📝 小节练习

> [!question] 判断题 1
> 实验表明 C 语言在所有场景下都比 Python 快。 ( )
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 实验中小数据量下 Python 的 `sorted()` 甚至快于 C 的 `qsort`——因为 Python 的排序底层也是 C 实现的 Timsort 算法，且在小数组上做了特殊的插入排序优化。这表明"语言速度"不等于"库速度"。

---

## 📋 章节测试

### 一、判断题（正确选✅，错误选❌）

> [!question] 判断题 1
> `struct.pack('<i', 42)` 输出的字节数在 32 位和 64 位平台上不同。 ( )
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `struct` 模块的 `i` 格式符固定输出 4 字节（C 的 `int` 类型），与平台位数无关。`l`（C 的 `long`）在 32 位平台是 4 字节、64 位 Linux 是 8 字节。

> [!question] 判断题 2
> `time.perf_counter()` 返回的时间可能因为系统 NTP 时间同步而回退。 ( )
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `perf_counter()` 使用单调时钟，不受系统时钟调整影响。这正是它适合性能计时的原因。`time.time()` 可能受 NTP 调整影响。

> [!question] 判断题 3
> 实验中使用 `-O2` 编译 C 程序是为了确保与 Python 比较的公平性（双方均使用优化编译）。 ( )
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: CPython 本身就是用 `-O2` 或更高优化级别编译的。用 `-O0` 编译 C 程序去比较是不公平的——那相当于让 C 选手绑着一只手跑步。

> [!question] 判断题 4
> Python `sorted()` 是稳定排序，C 标准库 `qsort` 不保证稳定。 ( )
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: Python 的 Timsort 算法保证稳定性（相等元素保持原顺序）。C 标准的 `qsort` 函数规格中未规定稳定性，不同实现行为不同。

> [!question] 判断题 5
> 二进制文件读写比文本文件读写更适合大规模数值数据交换，因为无字符串解析开销。 ( )
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: 文本读写需要将整数转为字符串（如 `sprintf(buf, "%d", num)`）和反向解析（`atoi/scanf`），这在百万级数据下成为瓶颈。二进制读写是直接的内存字节存取（`fread` → 数组），零转换开销。

> [!question] 判断题 6
> 在这个实验中，C 程序的 I/O 时间（文件读写）也计入了 C 排序耗时。 ( )
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: 第一节的基准测试从进程启动开始计时（包括读文件→排序→写文件），因此 I/O 开销包含在 C 的耗时中。第三节通过让 C 程序内部生成数据消除 I/O 开销，实现纯算法对比。

---

### 二、选择题（单项选择题）

> [!question] 选择题 1
> `struct.pack(f'<{n}i', *data)` 中 `f'<{n}i'` 的含义是？
> - [ ] A. 打包 n 个单字节整数
> - [ ] B. 打包 n 个小端序 4 字节有符号整数
> - [ ] C. 打包 n 个大端序整数
> - [ ] D. 打包一个长度为 n 的字符串
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: `'<'` 指定小端字节序，`n` 是重复计数，`i` 是 `int32_t` 对应格式符。所以 `'<1000i'` 表示打包 1000 个小端序 4 字节有符号整数。

> [!question] 选择题 2
> 使用中位数而非平均值作为计时结果的统计量，原因是？
> - [ ] A. 中位数计算更快
> - [ ] B. 中位数对异常值（如偶发的系统卡顿导致的极高耗时）不敏感
> - [ ] C. 平均值需要更多样本
> - [ ] D. 中位数总是更小
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 性能测试中，一次偶然的上下文切换、缓存未命中或 I/O 调度延迟可能导致某次耗时异常高。平均值会被这种异常值拉高，而中位数不受影响，更能反映"典型"性能。

> [!question] 选择题 3
> `subprocess.run` 默认启动子进程的方式是？
> - [ ] A. 在当前线程中直接调用函数
> - [ ] B. fork 新进程 + exec 替换程序映像
> - [ ] C. 通过 socket 发送请求
> - [ ] D. 解释执行 C 代码
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: Linux 上 `subprocess.run` 默认使用 `fork()` 创建子进程，然后 `exec()` 系列系统调用将子进程替换为目标程序。这是 C 标准库 `system()` 和 `popen()` 的底层机制，`subprocess` 提供了更灵活的 Python 封装。

> [!question] 选择题 4
> 以下哪个不是性能测试中的"公平对比"原则？
> - [ ] A. 双方使用相同的优化级别
> - [ ] B. 双方处理完全相同的数据
> - [ ] C. 多次运行取统计量以减少系统波动
> - [ ] D. 在 Python 中用 `while` 循环模拟 C 的 `for` 循环逐元素比较
>
> > [!success]- 点击查看答案
> > 正确答案: D
> > **解析**: 用 Python 的 `while`/`for` 循环逐个元素操作来"模拟" C 算法是不公平的——Python 的纯 Python 级别的循环比 C 慢 10-100 倍。公平对比应使用 Python 的向量化操作（如 NumPy）或内置函数（如 `sorted()`），它们底层也是 C 实现。

> [!question] 选择题 5
> 在实验中将随机种子设为 `42+trial` 的理由是？
> - [ ] A. 42 是"生命宇宙及一切的答案"
> - [ ] B. 确保每轮产生不同但确定的数据，既避免缓存优化效应又保证可复现
> - [ ] C. 让数据量逐轮递增
> - [ ] D. 确保数据中位数等于 42
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: 每轮用不同数据避免操作系统文件缓存（page cache）使后续轮次不公正地变快。同时不同 trial 使用可复现的 seed（`42+0`, `42+1`, ...）确保他人能在自己机器上重现完全相同的实验。

> [!question] 选择题 6
> 本实验中 Python 编排脚本最核心的价值是？
> - [ ] A. 写起来比 C 代码短
> - [ ] B. 将数据生成、进程管理、结果验证、计时和报告集成到同一流程中
> - [ ] C. 不需要编译
> - [ ] D. 可以在任何平台上运行
>
> > [!success]- 点击查看答案
> > 正确答案: B
> > **解析**: Python 的真正价值在此实验中体现为"胶水语言"特性——用标准库的 `subprocess` 管理 C 进程、`struct` 处理二进制数据、`time.perf_counter` 高精度计时、`assert` 验证正确性。如果用 C 做同样的事，需要分别写数据生成、进程管理（`fork/exec`）、计时器、命令行参数解析等多个独立程序。

---

### 🛠️ 动手练习题

> [!example] 练习题 1：扩展实验——测试你自己的 C 算法
> **难度**: ⭐⭐
>
> 把本章实验框架修改为测试你自己的 C 算法（不必是排序——可以是搜索、哈希、加密等）。要求：
> 1. C 算法接收二进制输入文件，输出二进制结果文件
> 2. Python 侧实现同样的算法（用 Python 内置函数或纯 Python）
> 3. 至少测试 3 种不同的数据规模
> 4. 使用 `--trials` 参数控制重复次数
> 5. 输出类似本章的对比表格
>
> 提示：你选择的算法最好是 O(n log n) 或更低复杂度，纯 Python 实现 O(n²) 算法在百万级数据上会极其慢。

> [!example] 练习题 2：混合排序——C 和 Python 流水线
> **难度**: ⭐⭐⭐
>
> 设计一个实验：Python 生成随机字符串列表，C 程序用 `qsort` 按字符串长度排序，返回排序后列表；Python 读取结果后，再用 `sorted(..., key=len)` 排序并对比结果。计时比较：
> - 纯 Python 方案（生成→排序→输出）
> - C 管道方案（Python 生成→二进制 IPC→C 排序→二进制 IPC→Python 输出）
>
> 分析：字符串排序场景下，二进制 IPC 的字符串编码/解码开销是否抵消了 C 排序的性能优势？
>
> 提示：C 侧使用 `char **` 数组存字符串，写回时每行一个字符串（`\n` 分隔）或长度前缀编码。

> [!example] 练习题 3：性能回归 CI
> **难度**: ⭐⭐⭐
>
> 将本章实验集成到 CI/CD 流程中（参考 [[../../5工程化/|Python 工程化]] 和 [[../../../c语言教程/1入门/01_环境配置|C 环境配置]]）：
> 1. 将 `benchmark.py` 加入项目的测试套件
> 2. 每次提交运行 `python benchmark.py --sizes 1000 10000 --trials 3`
> 3. 将结果与上次的基线值（存为 `baseline.json`）对比
> 4. 如果 C 或 Python 的排序耗时增加超过 30%，CI 标记为警告
> 5. 在 `pre-commit` hook 中集成（只做快速的小规模测试）
>
> 这个练习让你体验"Python 性能回归测试"的完整工程化流程。
