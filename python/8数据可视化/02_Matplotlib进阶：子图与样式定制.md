# Matplotlib 进阶：子图与样式定制 (Advanced Matplotlib)
---

## 章节概述

当你需要在一张图中展示多个维度的数据时——比如同时对比 C 程序在不同编译器、不同优化级别、不同输入规模下的性能——单一子图已经不够用了。本章教你 `subplots` 的多子图布局、共享坐标轴、双 Y 轴、以及 Matplotlib 的完整样式定制链。这些技巧是制作论文级图表的基本功。

> **核心理念**：多子图布局相当于 C 语言中的多维数组——你需要精确控制每个单元的位置和内容。`plt.subplots(nrows, ncols)` 返回一个 `ax` 数组（类似 `int arr[rows][cols]`），每个元素都是独立的坐标系对象，就像每个数组元素可独立赋值。

---

### 第一节：子图布局 (Subplots)
---

1.1 基础多子图：subplots()
-------------------------

```python
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 2 * np.pi, 100)

fig, axes = plt.subplots(2, 2, figsize=(10, 8))
# axes 是一个 2×2 的 numpy 数组，类似于 C 的 int axes[2][2]

axes[0, 0].plot(x, np.sin(x), 'r-')
axes[0, 0].set_title('sin(x)')

axes[0, 1].plot(x, np.cos(x), 'b-')
axes[0, 1].set_title('cos(x)')

axes[1, 0].plot(x, np.tan(x), 'g-')
axes[1, 0].set_title('tan(x)')
axes[1, 0].set_ylim(-5, 5) # tan 值域较大，限制范围

axes[1, 1].plot(x, np.sin(x) * np.cos(x), 'm-')
axes[1, 1].set_title('sin(x)·cos(x)')

fig.suptitle('Trigonometric Functions', fontsize=16)
fig.tight_layout()
fig.savefig('trig_subplots.png')
```

> `axes[row, col]` 的二维索引方式直接对应 C 的 `arr[row][col]`。当只有一行或一列时，`axes` 是一维数组，用 `axes[i]` 访问。

1.2 非均匀子图：GridSpec
------------------------

当子图需要不同大小时，`GridSpec` 提供灵活的网格布局：

```python
import matplotlib.gridspec as gridspec

fig = plt.figure(figsize=(12, 6))
gs = gridspec.GridSpec(2, 3, figure=fig)

# 左上角：占据 (row=0:2, col=0:1)，即两行高度、一列宽度
ax_big = fig.add_subplot(gs[0:2, 0:2])
# 右上：两行一列中的上半行
ax_top = fig.add_subplot(gs[0, 2])
# 右下：两行一列中的下半行
ax_bottom = fig.add_subplot(gs[1, 2])

x = np.linspace(0, 10, 200)
ax_big.plot(x, np.sin(x))
ax_big.set_title('Main Plot')
ax_top.scatter(range(20), np.random.randn(20))
ax_top.set_title('Scatter')
ax_bottom.hist(np.random.randn(500), bins=30)
ax_bottom.set_title('Histogram')

fig.tight_layout()
fig.savefig('gridspec.png')
```

> `GridSpec` 相当于 CSS Grid 布局——定义行和列的轨道，然后让每个子图占据指定范围。这比 C 语言中用像素坐标手算位置的传统绑图方式灵活得多。

1.3 嵌套子图：subplot2grid 与 GridSpec 子网格
--------------------------------------------

```python
fig = plt.figure(figsize=(10, 8))

# 主坐标系
ax_main = plt.subplot2grid((3, 3), (0, 0), colspan=2, rowspan=2)
# 右侧柱状图
ax_bar = plt.subplot2grid((3, 3), (0, 2), rowspan=2)
# 底部大图
ax_bottom = plt.subplot2grid((3, 3), (2, 0), colspan=3)

ax_main.plot(np.random.randn(100).cumsum())
ax_bar.bar(['A', 'B', 'C', 'D'], [3, 7, 2, 5])
ax_bottom.hist(np.random.randn(1000), bins=40, alpha=0.7)

fig.savefig('nested_grid.png')
```

### 小节练习


> [!question] 判断题 1
> `GridSpec(2, 3)` 定义的网格中，子图必须完全占满某个网格单元，不能跨越多行多列。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 错误
> > > **解析**: `GridSpec` 支持的索引方式 `gs[row_start:row_end, col_start:col_end]` 允许子图跨越任意范围的行和列。这正是它相对于 `plt.subplots()` 的核心优势。

---

### 第二节：共享坐标轴与双 Y 轴
---

2.1 共享 X 轴或 Y 轴
--------------------

当多个子图展示同一维度的数据时，共享坐标轴可以节省空间并使对比更直观：

```python
fig, axes = plt.subplots(3, 1, figsize=(8, 10), sharex=True)

x = np.linspace(0, 10, 200)
for i, freq in enumerate([1, 2, 3]):
 axes[i].plot(x, np.sin(freq * x))
 axes[i].set_ylabel(f'sin({freq}x)')

axes[2].set_xlabel('x') # 只在最下方设置 xlabel
fig.savefig('shared_x.png')
```

> `sharex=True` 让所有子图共享同一个 X 轴。当缩放或平移一个子图时，其他子图同步变化——类似于 C 语言中用同一个指针引用数组的不同视图。

共享后，Matplotlib 自动隐藏中间子图的刻度标签，只保留底部的标签。

2.2 双 Y 轴：twinx()
--------------------

当两组数据量级不同但 X 轴相同时，用双 Y 轴可以将它们放在同一张图上：

```python
fig, ax1 = plt.subplots(figsize=(8, 5))

x = np.linspace(0, 10, 100)
y1 = np.sin(x) * 100
y2 = np.exp(x) * 0.1

color1 = 'tab:blue'
ax1.set_xlabel('x')
ax1.set_ylabel('sin(x)·100', color=color1)
ax1.plot(x, y1, color=color1)
ax1.tick_params(axis='y', labelcolor=color1)

ax2 = ax1.twinx() # 创建共享 X 轴的第二个 Y 轴
color2 = 'tab:red'
ax2.set_ylabel('exp(x)·0.1', color=color2)
ax2.plot(x, y2, color=color2)
ax2.tick_params(axis='y', labelcolor=color2)

# 可选：第三个 Y 轴
# ax3 = ax1.twinx()
# ax3.spines['right'].set_position(('outward', 60))

fig.tight_layout()
fig.savefig('twin_axes.png')
```

2.3 C 程序基准测试的多维度对比
-----------------------------

典型的 C 性能测试场景——同时展示时间、内存、和 CPU 利用率的对比：

```python
# C 程序输出格式：n time_ms memory_kb cpu_percent
import sys, numpy as np
import matplotlib.pyplot as plt

data = np.loadtxt(sys.stdin)
n, time, memory, cpu = data[:, 0], data[:, 1], data[:, 2], data[:, 3]

fig, (ax1, ax3) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# 上图：时间 + 内存（双 Y 轴）
ax1.plot(n, time, 'b-o', label='Time (ms)')
ax1.set_ylabel('Time (ms)', color='b')
ax1.tick_params(axis='y', labelcolor='b')

ax2 = ax1.twinx()
ax2.plot(n, memory, 'r-s', label='Memory (KB)')
ax2.set_ylabel('Memory (KB)', color='r')
ax2.tick_params(axis='y', labelcolor='r')

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

# 下图：CPU 利用率
ax3.plot(n, cpu, 'g-^')
ax3.set_ylabel('CPU (%)')
ax3.set_xlabel('Input Size (n)')
ax3.fill_between(n, 0, cpu, alpha=0.2, color='g')

fig.tight_layout()
fig.savefig('benchmark_multi.png')
```

### 小节练习


> [!question] 判断题 1
> `sharex=True` 的子图，修改任意一个子图的 X 轴标签会影响所有子图。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 错误
> > > **解析**: `sharex=True` 共享的是**轴的范围和刻度**，不是轴标签（label）。每个子图仍有独立的 `set_xlabel()`。建议只在最底部子图设置 X 标签，避免重复。

---

### 第三节：样式定制 —— 从颜色到字体
---

3.1 线的属性：颜色、线型、线宽、标记
-----------------------------------

Matplotlib 提供了极其精细的线属性控制：

```python
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 50)
fig, ax = plt.subplots(figsize=(8, 5))

ax.plot(x, np.sin(x),
 color='#2E86AB', # 十六进制颜色
 linestyle='-', # '-' '--' '-.' ':' 
 linewidth=2, # 线宽（点）
 marker='o', # 标记形状
 markersize=6,
 markerfacecolor='white',
 markeredgewidth=1.5,
 markeredgecolor='#2E86AB',
 label='sin(x)',
 alpha=0.8)

ax.legend()
fig.savefig('styled_line.png')
```

常用线型与标记速查：

| 线型 | 字符 | 标记 | 字符 |
|------|------|------|------|
| 实线 | `-` | 圆点 | `o` |
| 虚线 | `--` | 方形 | `s` |
| 点划线 | `-.` | 三角形 | `^` `v` `<` `>` |
| 点线 | `:` | 星形 | `*` |
| 无线 | `''` | 菱形 | `D` |

3.2 颜色映射：给数据赋予视觉含义
-------------------------------

```python
import numpy as np
import matplotlib.pyplot as plt

n = 200
x = np.random.randn(n)
y = np.random.randn(n)
colors = np.sqrt(x**2 + y**2) # 离原点距离决定颜色

fig, ax = plt.subplots(figsize=(7, 6))
scatter = ax.scatter(x, y, c=colors, cmap='plasma', s=50, alpha=0.7)
fig.colorbar(scatter, ax=ax, label='Distance from origin')
ax.axhline(y=0, color='gray', linewidth=0.5)
ax.axvline(x=0, color='gray', linewidth=0.5)
ax.set_aspect('equal')
fig.savefig('colormap.png')
```

> Matplotlib 内置数十种颜色映射（colormap），常用的有 `viridis`、`plasma`、`inferno`、`magma`、`coolwarm`、`RdYlBu`。选择原则：连续数据用感知均匀的 colormap（`viridis`），有零点对称的数据用发散型（`coolwarm`）。

3.3 文字元素：标题、轴标签、刻度、注释
-------------------------------------

```python
fig, ax = plt.subplots(figsize=(8, 5))

x = np.linspace(0, 2, 100)
ax.plot(x, x**2, 'b-', label='f(x)=x²')

ax.set_title('Quadratic Function', fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('x', fontsize=13)
ax.set_ylabel('f(x)', fontsize=13)
ax.legend(fontsize=12, loc='upper left', framealpha=0.8)

# 自定义刻度
ax.set_xticks([0, 0.5, 1.0, 1.5, 2.0])
ax.set_xticklabels(['0', '0.5', '1', '1.5', '2'], fontsize=11)
ax.tick_params(axis='both', which='major', labelsize=11, direction='in')

# 文本注释
ax.text(1.0, 3.0, 'minimum?', fontsize=11,
 ha='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# 箭头注释
ax.annotate('f(1)=1', xy=(1, 1), xytext=(1.3, 0.5),
 arrowprops=dict(arrowstyle='->', color='red'),
 fontsize=11, color='red')

ax.grid(True, linestyle='--', alpha=0.4)
fig.tight_layout()
fig.savefig('text_elements.png')
```

3.4 全局样式与样式表
--------------------

Matplotlib 提供预定义的样式表，一行代码即可切换整体外观：

```python
import matplotlib.pyplot as plt
import matplotlib.style as mplstyle

# 查看可用样式
print(mplstyle.available[:10])
# ['Solarize_Light2', '_classic_test_patch', ... 'seaborn-v0_8', 'tableau-colorblind10']

# 使用样式
plt.style.use('seaborn-v0_8-darkgrid')
# 或：plt.style.use('ggplot')
# 或：plt.style.use('fivethirtyeight')

x = [1, 2, 3, 4, 5]
y = [2, 4, 6, 8, 10]
plt.plot(x, y, 'o-')
plt.savefig('styled_global.png')
```

创建自定义样式文件 `my_style.mplstyle`：

```text
lines.linewidth: 2.0
lines.markersize: 8
font.size: 14
axes.grid: True
axes.grid.axis: both
grid.alpha: 0.3
figure.figsize: 10, 6
savefig.dpi: 150
savefig.bbox: tight
```

```python
plt.style.use('my_style.mplstyle')
# 之后所有的绑图都使用这个样式
```

> 样式文件相当于 C 项目中的 `.h` 头文件——定义全局常量，避免在每个源文件中重复设置。团队项目中使用统一的样式表确保图表外观一致。

### 小节练习


---

### 第四节：实战 —— 多面板 C 基准测试报告
---

4.1 完整的多面板性能报告
-----------------------

将多个 C 程序的基准测试结果汇总到一张信息密集的图中：

C 程序（`full_bench.c`）：
```c
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>

#define MAX_N 1000000

void bench_sort(int n) {
 int *arr = malloc(n * sizeof(int));
 for (int i = 0; i < n; i++) arr[i] = rand();
 // ... 排序算法 ...
 free(arr);
 printf("sort %d %f\n", n, /* time */ 0.0);
}

void bench_hash(int n) {
 // ... 哈希表操作 ...
 printf("hash %d %f\n", n, /* time */ 0.0);
}

void bench_tree(int n) {
 // ... 树操作 ...
 printf("tree %d %f\n", n, /* time */ 0.0);
}

int main() {
 for (int n = 1000; n <= MAX_N; n *= 10) {
 bench_sort(n);
 bench_hash(n);
 bench_tree(n);
 }
 return 0;
}
```

Python 绑图脚本：
```python
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# 读取管道数据
data = np.loadtxt(sys.stdin, dtype=[('algo', 'U10'), ('n', int), ('time', float)])

algos = np.unique(data['algo'])
colors = {'sort': '#2196F3', 'hash': '#4CAF50', 'tree': '#FF5722'}

fig = plt.figure(figsize=(14, 10))
gs = gridspec.GridSpec(2, 2, figure=fig)

# 面板 1：时间对比（双对数坐标）
ax1 = fig.add_subplot(gs[0, 0])
for algo in algos:
 mask = data['algo'] == algo
 ax1.loglog(data['n'][mask], data['time'][mask], 'o-',
 color=colors.get(algo, 'gray'), label=algo, markersize=6)
ax1.set_title('Performance Comparison (log-log)')
ax1.set_xlabel('Input Size (n)')
ax1.set_ylabel('Time (ms)')
ax1.legend()
ax1.grid(True, alpha=0.3)

# 面板 2：柱状图（最大输入规模下的时间对比）
ax2 = fig.add_subplot(gs[0, 1])
max_n = data['n'].max()
max_data = data[data['n'] == max_n]
ax2.bar(max_data['algo'], max_data['time'],
 color=[colors.get(a, 'gray') for a in max_data['algo']])
ax2.set_title(f'Time at n={max_n:,}')
ax2.set_ylabel('Time (ms)')

# 面板 3：加速比（相对最慢算法的加速倍数）
ax3 = fig.add_subplot(gs[1, 0])
for algo in algos:
 mask = data['algo'] == algo
 n_vals = data['n'][mask]
 t_vals = data['time'][mask]
 ax3.plot(n_vals, t_vals, 'o-', color=colors.get(algo, 'gray'), label=algo)
ax3.set_title('Time vs Input Size')
ax3.set_xlabel('n')
ax3.set_ylabel('Time (ms)')

# 面板 4：汇总表格
ax4 = fig.add_subplot(gs[1, 1])
ax4.axis('off')
summary = [f'{algo}: {t:.2f} ms' for algo, t in
 zip(max_data['algo'], max_data['time'])]
summary_text = '\n'.join(summary)
ax4.text(0.1, 0.5, f"Summary at n={max_n:,}:\n\n{summary_text}",
 fontsize=12, va='center', fontfamily='monospace')
ax4.set_title('Summary')

fig.suptitle('C Program Benchmark Report', fontsize=18, fontweight='bold')
fig.tight_layout()
fig.savefig('benchmark_report.png', dpi=150)
```

### 小节练习

> [!question] 判断题 1
> `ax.loglog()` 是将 X 轴和 Y 轴都设为对数坐标的方法。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 正确
> > > **解析**: `loglog()` 同时将两个坐标轴设为对数尺度（等价于 `plot()` + `set_xscale('log')` + `set_yscale('log')`）。对应的有 `semilogx()`（仅 X 轴对数）和 `semilogy()`（仅 Y 轴对数）。


---

## 章节测试

### 一、判断题（正确选，错误选）

> [!question] 判断题 1
> `plt.subplots(2, 2)` 创建的 4 个子图必须有相同的大小。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 正确
> > > **解析**: `subplots()` 按均匀网格排列，所有子图大小相同。如果需要不同的子图大小，应使用 `GridSpec` 或 `subplot2grid`。

> [!question] 判断题 2
> `ax.annotate()` 的箭头自动指向 `xy` 参数指定的数据坐标位置。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 正确
> > > **解析**: `annotate('text', xy=(x, y), xytext=(x', y'))` 中 `xy` 是箭头的**指向位置**（数据坐标），`xytext` 是文本的**放置位置**。箭头从文本位置指向 `xy`。

> [!question] 判断题 3
> `ax.tick_params(axis='both', direction='in')` 让刻度线显示在坐标轴的内侧。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 正确
> > > **解析**: `direction` 参数可取 `'in'`、`'out'`、`'inout'`，分别控制刻度线朝向坐标轴内侧、外侧或两侧。

> [!question] 判断题 4
> Matplotlib 的样式表（style sheets）只能使用内置的，不能自定义。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 错误
> > > **解析**: 你可以创建 `.mplstyle` 文件并在 `plt.style.use('path/to/my_style.mplstyle')` 中使用。样式表的内容是 `rcParams` 参数的键值对，功能等同于 `plt.rcParams.update({...})`。

> [!question] 判断题 5
> `ax.twinx()` 创建的新坐标系与原坐标系共享 Y 轴。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 错误
> > > **解析**: `twinx()` 共享的是 **X 轴**，创建独立的 Y 轴。`twiny()` 则是共享 Y 轴，创建独立的 X 轴。名字中的 `x` 表示"共享 x"。

> [!question] 判断题 6
> `np.loadtxt(sys.stdin, dtype=[('algo', 'U10'), ('n', int)])` 可以从管道直接读取结构化数据，不需要逐行解析。（ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > > 答案: 正确
> > > **解析**: `np.loadtxt` 接受文件路径或任何类文件对象（包括 `sys.stdin`），`dtype` 参数指定结构化数组的列类型。对于规整的文本数据，这是最高效的读取方式。

---


---

## 力扣练习

以下题目用于验证本章所学内容：

| 题号 | 题目 | 链接 | 涉及知识点 |
|------|------|------|-----------|
| — | 本章无对应力扣题 | — | 请用动手练习题自检 |



### 动手练习题

> [!example] 练习题 1：C 程序性能四面板报告
> **难度**: 简单
>
> 编写一个 C 程序，分别测试三种排序算法（冒泡、快速、归并）在不同输入规模（n=100, 500, 1000, 5000）下的耗时。输出格式：`sort_name n time_ms`。然后：
> 1. Python 脚本用 `np.loadtxt(sys.stdin, dtype=...)` 读取数据
> 2. 使用 `GridSpec(2, 2)` 创建 4 面板布局：
> - 左上：三条时间曲线（对数 X 轴）
> - 右上：n=5000 时的柱状图对比
> - 左下：相对快速排序的加速比曲线
> - 右下：汇总表格（`ax.table()` 或 `ax.text()`）
> 3. 保存为 `sort_benchmark_report.pdf`（DPI=200）

> [!example] 练习题 2：双 Y 轴数据展示
> **难度**: 简单
>
> 模拟一个 C 网络服务器程序输出的数据（CPU 使用率和 QPS 每秒查询数），时间点为 0-60 秒：
> 1. 手动创建数据或用 `numpy.random` 生成
> 2. 用 `twinx()` 在同一图上展示 CPU%（蓝色，左轴）和 QPS（红色，右轴）
> 3. 添加填充区域（`ax.fill_between`）标注 CPU > 80% 的高负载区间
> 4. 使用 "seaborn-v0_8-darkgrid" 样式
> 5. 标注最高 QPS 点的数值（`ax.annotate`）

> [!example] 练习题 3：自定义样式表
> **难度**: 简单
>
> 创建自定义样式表 `mono_style.mplstyle`：
> - 所有绑图线条为黑色（`lines.color: black`）
> - 线宽 2.0
> - 字体大小 14
> - 图例无边框（`legend.frameon: False`）
> - 图片尺寸 12×6 英寸
> - 保存 DPI 300
>
> 然后在 Python 脚本中应用这个样式表，绑制任意一组数据的折线图。观察效果并与默认样式对比。

> [!example] 练习题 4：从管道读取多维数据
> **难度**: 简单
>
> 编写 C 程序输出格式如下的数据（模拟三维传感器读数）：
> ```
> timestamp sensor1 sensor2 sensor3
> 0.0 23.5 18.2 31.0
> 0.1 23.8 18.0 30.8
> ...
> ```
> 用 Python 脚本从管道读取，创建 3×1 的共享 X 轴的子图，分别展示三个传感器的时序数据。每个子图用不同的颜色和标记，添加水平虚线标注平均值。保存为 `sensor_plot.png`。
