# Seaborn：统计图表 (Seaborn: Statistical Plots)
---

## 章节概述

如果你的 C 程序输出的是统计数据——分布特征、变量关系、分组对比——Seaborn 就是为这类数据量身定做的工具。Seaborn 建立在 Matplotlib 之上，但提供了更高级的统计绑图接口：一行代码绑出带置信区间的回归线，三行代码绑出变量之间的相关性热力图。对于 C 程序员来说，Seaborn 相当于 Matplotlib 的"标准模板库"——它封装了常见的统计绑图模式，让你专注于数据本身而非绑图细节。

> **核心理念**：Matplotlib 给你画笔和绑布，Seaborn 给你预设的绑图模板。如果你的 C 程序只是输出几列数字，Seaborn 可以用最少的代码生成最具统计洞察力的图表。它和 pandas DataFrame 深度集成，对于表格化数据（C 程序最常输出的格式）尤其高效。

---

### 第一节：Seaborn 入门与 DataFrame 基础
---

1.1 Seaborn 与 Matplotlib 的关系
--------------------------------

```python
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Seaborn 修改 Matplotlib 的全局 rcParams
# 所以导入后，所有 Matplotlib 绑图自动获得 Seaborn 的美化样式
sns.set_theme(style="darkgrid") # 可选：whitegrid, dark, white, ticks

# 所有 seaborn 绑图函数返回 Matplotlib 的 Axes 对象
# 因此你总是可以继续用 Matplotlib API 进行调整
ax = sns.scatterplot(x=[1, 2, 3], y=[4, 5, 6])
ax.set_title("Seaborn + Matplotlib = Power")
plt.savefig('seaborn_intro.png')
```

> Seaborn 是 Matplotlib 的补丁（不是替代品）。`sns.scatterplot()` 底层仍然调用 Matplotlib 的 `scatter`，但它自动添加了大量美化——颜色映射、图例位置、网格线样式等。你总可以用 `ax.set_*` 系列方法覆盖它。

1.2 从 C 程序输出到 DataFrame
-----------------------------

C 程序（`stats_gen.c`）输出统计数据：
```c
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>

int main() {
 srand(time(NULL));
 printf("group,value,category\n");
 for (int g = 0; g < 3; g++) {
 double base = 5.0 + g * 3.0;
 for (int i = 0; i < 50; i++) {
 double noise = ((double)rand() / RAND_MAX - 0.5) * 4;
 printf("%c,%.3f,cat%d\n", 'A' + g, base + noise, g % 2);
 }
 }
 return 0;
}
```

Python 读取并转换为 DataFrame：
```python
import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 从管道读取 CSV
df = pd.read_csv(sys.stdin)

# 查看数据结构
print(df.head())
print(df.describe())

# direct 绑图
sns.boxplot(data=df, x='group', y='value')
plt.savefig('boxplot.png')
```

> `pd.read_csv(sys.stdin)` 直接解析管道中的 CSV 数据到 DataFrame ——不需要逐行 `split()`，不需要声明列类型（自动推断）。DataFrame 相当于 C 语言中的结构体数组加强版——每列有名称，每行有索引，支持 SQL 式的查询和分组操作。

1.3 常用数据集加载（练习用）
---------------------------

Seaborn 内置多个示例数据集，方便快速尝试 API：

```python
import seaborn as sns

tips = sns.load_dataset('tips')
# columns: total_bill, tip, sex, smoker, day, time, size

iris = sns.load_dataset('iris')
# columns: sepal_length, sepal_width, petal_length, petal_width, species

penguins = sns.load_dataset('penguins')
# columns: species, island, bill_length_mm, bill_depth_mm, flipper_length_mm, body_mass_g, sex
```

---

### 第二节：数据分布绑图 —— 箱线图与提琴图
---

2.1 箱线图：boxplot()
---------------------

箱线图展示数据的五数概括：最小值、第一四分位数、中位数、第三四分位数、最大值：

```python
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

# C 程序输出的分组数据
df = pd.DataFrame({
 'algorithm': ['quick']*30 + ['merge']*30 + ['bubble']*30 + ['heap']*30,
 'time_ms': (
 list(1.5 + 0.1 * np.random.randn(30)) + # quick
 list(1.8 + 0.1 * np.random.randn(30)) + # merge
 list(15.0 + 2.0 * np.random.randn(30)) + # bubble
 list(2.2 + 0.2 * np.random.randn(30)) # heap
 )
})

fig, ax = plt.subplots(figsize=(8, 5))
sns.boxplot(data=df, x='algorithm', y='time_ms',
 palette='Set2', width=0.5, linewidth=1.5)
ax.set_title('Sort Algorithm Performance')
ax.set_ylabel('Time (ms)')
fig.savefig('boxplot_algorithms.png')
```

> 箱线图的解读：箱子中的横线是中位数，箱子的上下边是 Q1 和 Q3，须（whisker）延伸到 1.5 倍 IQR（四分位距）内的最远点。须外的点是离群值。这个解读逻辑等价于 C 语言中你手写 `qsort()` 然后遍历数据计算各个分位数。

2.2 提琴图：violinplot()
------------------------

提琴图在箱线图基础上展示完整的数据分布形态：

```python
fig, ax = plt.subplots(figsize=(10, 6))
sns.violinplot(data=df, x='algorithm', y='time_ms',
 inner='quartile', # 显示四分位线
 palette='muted',
 cut=0) # 不延伸到数据范围之外
ax.set_title('Distribution of Algorithm Performance')
fig.savefig('violin_algorithms.png')
```

> 提琴图的宽度表示数据密度——越宽表示该值附近的数据点越多。`inner='quartile'` 在提琴内部显示四分位线，结合了箱线图的优势。这相当于 C 语言中你用直方图（`hist()`）加分位数计算结合的结果。

2.3 分组与分面：hue 参数
-----------------------

`hue` 是 Seaborn 最强大的特性之一——按分类变量对数据进行颜色分组：

```python
# 模拟数据：算法 × 优化级别
import numpy as np
np.random.seed(42)

df_comp = pd.DataFrame({
 'algorithm': ['qsort']*60 + ['msort']*60 + ['bsort']*60,
 'optimize': (['-O0']*20 + ['-O2']*20 + ['-O3']*20) * 3,
 'time': np.concatenate([
 5.0 + np.random.randn(20),
 1.5 + np.random.randn(20)*0.3,
 1.2 + np.random.randn(20)*0.2,
 6.0 + np.random.randn(20),
 2.0 + np.random.randn(20)*0.3,
 1.5 + np.random.randn(20)*0.2,
 50.0 + np.random.randn(20)*5,
 48.0 + np.random.randn(20)*4,
 45.0 + np.random.randn(20)*3,
 ])
})

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

sns.boxplot(data=df_comp, x='algorithm', y='time',
 hue='optimize', palette='Set1', ax=axes[0])
axes[0].set_title('Box Plot by Algorithm × Optimization')

sns.violinplot(data=df_comp, x='algorithm', y='time',
 hue='optimize', split=True, # 左右对称
 palette='Set1', ax=axes[1])
axes[1].set_title('Violin Plot (split)')

fig.tight_layout()
fig.savefig('grouped_distribution.png')
```

---

### 第三节：变量关系绑图 —— 回归图与配对图
---

3.1 回归图：lmplot()
--------------------

适合展示两组连续变量之间的线性关系，自动绑制散点图并叠加拟合直线：

```python
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 模拟 C 程序的输入规模 vs 运行时间数据
n = 100
np.random.seed(42)
x = 10 ** np.random.uniform(1, 4, n) # 对数均匀分布
y = 0.001 * x + np.random.lognormal(0, 0.5, n) # 带噪声的线性关系

df = pd.DataFrame({'input_size': x, 'time_ms': y})

sns.lmplot(data=df, x='input_size', y='time_ms',
 height=5, aspect=1.5, # 图片尺寸
 scatter_kws={'alpha': 0.5}, # 散点样式
 line_kws={'color': 'red'}) # 回归线样式
plt.savefig('lmplot_basic.png')
```

> `lmplot()` 默认绑制 95% 置信区间的回归线（半透明蓝色带）。`order=2` 可绑二次曲线拟合，`logistic=True` 可绑逻辑回归。这相当于 C 语言中你手写最小二乘法 + `plot` 的十行代码。

3.2 带分组的回归图
------------------

```python
# 模拟不同编译器的优化效果
df_tips = sns.load_dataset('tips')

sns.lmplot(data=df_tips, x='total_bill', y='tip',
 hue='smoker', # 按是否吸烟着色
 col='time', # 按餐时分列（Dinner/Lunch）
 height=4, aspect=1)
plt.savefig('lmplot_grouped.png')
```

3.3 配对图：pairplot()
----------------------

当你的 C 程序输出多个维度的性能指标时，`pairplot` 一次展示所有变量两两关系的矩阵：

```python
# 模拟 C 基准测试的多维输出
np.random.seed(42)
n = 150
df_bench = pd.DataFrame({
 'input_size': 10 ** np.random.uniform(2, 5, n),
 'time_ms': np.random.lognormal(3, 0.8, n),
 'memory_kb': np.random.lognormal(8, 1.0, n),
 'cache_miss': np.random.lognormal(4, 1.5, n),
 'algorithm': np.random.choice(['qsort', 'msort', 'bsort'], n),
})

# 快速获取所有变量的概览
sns.pairplot(df_bench, hue='algorithm',
 diag_kind='hist', # 对角线显示直方图
 plot_kws={'alpha': 0.6, 's': 20})
plt.savefig('pairplot_bench.png')
```

> `pairplot` 生成一个 n×n 的矩阵图（n=数值变量数）。对角线上是该变量自身的分布（直方图或 KDE），非对角线是两个变量的散点图矩阵。相当于一次性绑制所有两两组合的图——这在 C 语言中意味着一堆嵌套的 `for` 循环。

3.4 联合分布图：jointplot()
--------------------------

```python
# 同时展示散点图和两个变量的边缘分布
sns.jointplot(data=df_bench, x='input_size', y='time_ms',
 kind='hex', # 'scatter', 'kde', 'hex', 'reg', 'resid', 'hist'
 height=7,
 marginal_kws={'bins': 30})
plt.savefig('jointplot.png')
```

---

### 第四节：矩阵数据绑图 —— 热力图与聚类图
---

4.1 热力图：heatmap()
---------------------

热力图以颜色编码矩阵值，是展示相关性矩阵或二维分布的首选：

```python
import seaborn as sns
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 从 C 程序输出的矩阵
# ./matrix_prog | python3 heatmap.py
np.random.seed(42)
matrix = np.random.randn(12, 8) # 12×8 的数据矩阵
labels_rows = [f'Row{i}' for i in range(12)]
labels_cols = [f'Col{j}' for j in range(8)]

fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(
 matrix,
 annot=True, # 在每个格子中显示数值
 fmt='.2f',
 cmap='RdBu_r', # 红-白-蓝（反转）
 center=0, # 以 0 为颜色中心
 xticklabels=labels_cols,
 yticklabels=labels_rows,
 linewidths=0.5, # 格子边界宽度
 linecolor='gray',
 cbar_kws={'label': 'Value'},
 ax=ax
)
ax.set_title('2D Data Matrix')
fig.savefig('heatmap_matrix.png')
```

4.2 相关性矩阵可视化
------------------

```python
# 计算 DataFrame 的相关性矩阵
df_num = df_bench.select_dtypes(include=[np.number])
corr = df_num.corr()

fig, ax = plt.subplots(figsize=(8, 6))
mask = np.triu(np.ones_like(corr, dtype=bool), k=1) # 上三角遮罩

sns.heatmap(corr,
 mask=mask, # 隐藏重复的上三角
 annot=True,
 fmt='.2f',
 cmap='coolwarm',
 vmin=-1, vmax=1,
 square=True, # 正方形格子
 linewidths=1,
 ax=ax)
ax.set_title('Correlation Matrix', fontsize=14)
fig.savefig('correlation_heatmap.png')
```

> 相关性矩阵的每个格子是皮尔逊相关系数（Pearson's r），范围[-1, 1]。1 表示完全正相关，-1 是完全负相关，0 是无线性相关。这是 C 程序中判断"输入规模影响运行时间"或"内存使用影响缓存命中率"的量化指标。

4.3 聚类热力图：clustermap()
---------------------------

```python
# 自动对行和列进行层次聚类
sns.clustermap(
 matrix,
 method='average', # 聚类算法：'single', 'complete', 'average', 'ward'
 metric='euclidean', # 距离度量
 cmap='viridis',
 figsize=(10, 10),
 xticklabels=labels_cols,
 yticklabels=labels_rows,
 annot=False
)
plt.savefig('clustermap.png')
```

> `clustermap` 在 heatmap 基础上增加了行和列的**层次聚类树状图**（dendrogram）。相似的行（或列）会被归到一起，方便发现数据中的隐藏模式。这是一种无监督学习，不要任何先验知识。

---

### 第五节：从 C 程序管道到 Seaborn 图表 —— 完整工作流
---

5.1 端到端示例：排序算法性能可视化
---------------------------------

C 程序（`sort_stats.c`）：
```c
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

// 冒泡排序（慢）
void bubble_sort(int *a, int n) {
 for (int i = 0; i < n-1; i++)
 for (int j = 0; j < n-1-i; j++)
 if (a[j] > a[j+1]) { int t = a[j]; a[j] = a[j+1]; a[j+1] = t; }
}

// 快速排序比较函数
int cmp(const void *a, const void *b) {
 return (*(int*)a - *(int*)b);
}

double measure(int n, int algo) {
 int *arr = malloc(n * sizeof(int));
 for (int i = 0; i < n; i++) arr[i] = rand();

 clock_t start = clock();
 if (algo == 0) bubble_sort(arr, n);
 else qsort(arr, n, sizeof(int), cmp);
 double elapsed = (double)(clock() - start) / CLOCKS_PER_SEC * 1000;

 free(arr);
 return elapsed;
}

int main() {
 srand(time(NULL));
 printf("n,algorithm,time_ms,optimization\n");
 for (int n = 100; n <= 5000; n += 100) {
 printf("%d,bubble,%.4f,-O0\n", n, measure(n, 0));
 printf("%d,qsort,%.4f,-O0\n", n, measure(n, 1));
 // 实际应该用不同优化级别分别编译
 }
 return 0;
}
```

Python 绑图脚本（`plot_sorts.py`）：
```python
import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sns.set_theme(style='whitegrid')

df = pd.read_csv(sys.stdin)

fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# 图 1：散点图 + 回归线
sns.scatterplot(data=df, x='n', y='time_ms', hue='algorithm',
 style='algorithm', s=40, ax=axes[0])
axes[0].set_title('Raw Data Points')
axes[0].set_ylabel('Time (ms)')

# 图 2：箱线图（按算法分组）
sns.boxplot(data=df, x='algorithm', y='time_ms',
 palette='Set2', ax=axes[1])
axes[1].set_title('Distribution Comparison')
axes[1].set_ylabel('Time (ms)')

# 图 3：对数坐标下的折线图
for algo in df['algorithm'].unique():
 subset = df[df['algorithm'] == algo]
 axes[2].plot(subset['n'], subset['time_ms'], 'o-', label=algo)
axes[2].set_xscale('log')
axes[2].set_yscale('log')
axes[2].set_title('Performance (log-log)')
axes[2].set_xlabel('Input Size (n)')
axes[2].set_ylabel('Time (ms)')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

fig.suptitle('Sorting Algorithm Performance Analysis', fontsize=15, fontweight='bold')
fig.tight_layout()
fig.savefig('sort_analysis.png', dpi=150)
```

运行：
```bash
gcc -O0 -o sort_stats sort_stats.c
./sort_stats | python3 plot_sorts.py
```

---

## 力扣练习

以下题目用于验证本章所学内容：

| 题号 | 题目 | 链接 | 涉及知识点 |
|------|------|------|-----------|
| — | 本章无对应力扣题 | — | 请用动手练习题自检 |
