# Seaborn：统计图表 (Seaborn: Statistical Plots)
---

## 📖 章节概述

如果你的 C 程序输出的是统计数据——分布特征、变量关系、分组对比——Seaborn 就是为这类数据量身定做的工具。Seaborn 建立在 Matplotlib 之上，但提供了更高级的统计绑图接口：一行代码绑出带置信区间的回归线，三行代码绑出变量之间的相关性热力图。对于 C 程序员来说，Seaborn 相当于 Matplotlib 的"标准模板库"——它封装了常见的统计绑图模式，让你专注于数据本身而非绑图细节。

> **核心理念**：Matplotlib 给你画笔和绑布，Seaborn 给你预设的绑图模板。如果你的 C 程序只是输出几列数字，Seaborn 可以用最少的代码生成最具统计洞察力的图表。它和 pandas DataFrame 深度集成，对于表格化数据（C 程序最常输出的格式）尤其高效。

---

### 📚 第一节：Seaborn 入门与 DataFrame 基础
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
sns.set_theme(style="darkgrid")  # 可选：whitegrid, dark, white, ticks

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

### 📝 小节练习

> [!question] 选择题 1
> Seaborn 和 Matplotlib 的关系可以类比为什么？
> - [ ] A. C 和 C++ 的关系（不同语言）
> - [ ] B. C 标准库和 GLib 的关系（高层封装）
> - [ ] C. GCC 和 Clang 的关系（竞争品）
> - [ ] D. 汇编和 C 的关系（底层 vs 高层）
>
> > [!success]- 点击查看答案
> > > 正确答案: B
> > > **解析**: Seaborn 是 Matplotlib 的**高层封装**，底层仍调用 Matplotlib 的绑图函数。类似于 GLib 封装了 C 标准库的数据结构和工具函数——它提供了更便利的接口，但没有替换底层引擎。

> [!question] 判断题 1
> `pd.read_csv(sys.stdin)` 要求管道中的数据必须是严格的 CSV 格式（逗号分隔）。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > > 答案: 错误
> > > **解析**: `pd.read_csv()` 支持通过 `sep` 参数指定任意分隔符（空格：`sep='\s+'`，制表符：`sep='\t'`，竖线：`sep='|'`）。还支持 `skiprows`（跳过行）、`comment`（注释行）、`names`（指定列名）等参数。

---

### 📚 第二节：数据分布绑图 —— 箱线图与提琴图
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
        list(1.5 + 0.1 * np.random.randn(30)) +    # quick
        list(1.8 + 0.1 * np.random.randn(30)) +    # merge
        list(15.0 + 2.0 * np.random.randn(30)) +   # bubble
        list(2.2 + 0.2 * np.random.randn(30))      # heap
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
               inner='quartile',  # 显示四分位线
               palette='muted',
               cut=0)             # 不延伸到数据范围之外
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
               hue='optimize', split=True,  # 左右对称
               palette='Set1', ax=axes[1])
axes[1].set_title('Violin Plot (split)')

fig.tight_layout()
fig.savefig('grouped_distribution.png')
```

### 📝 小节练习

> [!question] 选择题 1
> 提琴图（violinplot）中，图的最大宽度代表什么？
> - [ ] A. 数据的最大值
> - [ ] B. 数据的标准差
> - [ ] C. 数据密度最高的位置
> - [ ] D. 数据的平均值
>
> > [!success]- 点击查看答案
> > > 正确答案: C
> > > **解析**: 提琴图的宽度对应数据的**核密度估计（KDE）**，越宽表示该 Y 值附近的观测值越多。这是箱线图无法展示的信息——箱线图只显示分位数，不显示分布的"峰"和"谷"。

> [!question] 选择题 2
> `sns.boxplot(data=df, x='group', y='value', hue='category')` 中 `hue` 参数的作用是？
> - [ ] A. 设置颜色亮度
> - [ ] B. 按二级分类变量进行颜色分组
> - [ ] C. 按数值大小渐变着色
> - [ ] D. 控制图的透明度
>
> > [!success]- 点击查看答案
> > > 正确答案: B
> > > **解析**: `hue` 是 seaborn 中通用的**分组参数**。按指定的分类变量对数据进行二次分组，每组用不同的颜色表示。在箱线图中，会在每个 `x` 类别旁边并排显示多个箱子（每个 `hue` 值一个）。

---

### 📚 第三节：变量关系绑图 —— 回归图与配对图
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
x = 10 ** np.random.uniform(1, 4, n)  # 对数均匀分布
y = 0.001 * x + np.random.lognormal(0, 0.5, n)  # 带噪声的线性关系

df = pd.DataFrame({'input_size': x, 'time_ms': y})

sns.lmplot(data=df, x='input_size', y='time_ms',
           height=5, aspect=1.5,           # 图片尺寸
           scatter_kws={'alpha': 0.5},     # 散点样式
           line_kws={'color': 'red'})      # 回归线样式
plt.savefig('lmplot_basic.png')
```

> `lmplot()` 默认绑制 95% 置信区间的回归线（半透明蓝色带）。`order=2` 可绑二次曲线拟合，`logistic=True` 可绑逻辑回归。这相当于 C 语言中你手写最小二乘法 + `plot` 的十行代码。

3.2 带分组的回归图
------------------

```python
# 模拟不同编译器的优化效果
df_tips = sns.load_dataset('tips')

sns.lmplot(data=df_tips, x='total_bill', y='tip',
           hue='smoker',         # 按是否吸烟着色
           col='time',           # 按餐时分列（Dinner/Lunch）
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
             diag_kind='hist',    # 对角线显示直方图
             plot_kws={'alpha': 0.6, 's': 20})
plt.savefig('pairplot_bench.png')
```

> `pairplot` 生成一个 n×n 的矩阵图（n=数值变量数）。对角线上是该变量自身的分布（直方图或 KDE），非对角线是两个变量的散点图矩阵。相当于一次性绑制所有两两组合的图——这在 C 语言中意味着一堆嵌套的 `for` 循环。

3.4 联合分布图：jointplot()
--------------------------

```python
# 同时展示散点图和两个变量的边缘分布
sns.jointplot(data=df_bench, x='input_size', y='time_ms',
              kind='hex',          # 'scatter', 'kde', 'hex', 'reg', 'resid', 'hist'
              height=7,
              marginal_kws={'bins': 30})
plt.savefig('jointplot.png')
```

### 📝 小节练习

> [!question] 选择题 1
> `sns.pairplot(df, hue='category')` 的对角线默认显示什么？
> - [ ] A. 空图
> - [ ] B. 该变量的直方图
> - [ ] C. KDE（核密度估计）曲线
> - [ ] D. 该变量的箱线图
>
> > [!success]- 点击查看答案
> > > 正确答案: B
> > > **解析**: 默认 `diag_kind='hist'`（直方图）。可使用 `diag_kind='kde'` 切换为核密度曲线，`diag_kind='auto'` 让 seaborn 自动选择。

> [!question] 判断题 1
> `lmplot()` 绑制的回归线是固定斜率的直线。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > > 答案: 错误
> > > **解析**: `lmplot()` 默认（`order=1`）绑制线性回归，但通过 `order=2` 可绑二次曲线，`logistic=True` 可绑逻辑回归曲线。它使用 `statsmodels` 或 `scipy` 在底层进行拟合计算。

---

### 📚 第四节：矩阵数据绑图 —— 热力图与聚类图
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
matrix = np.random.randn(12, 8)  # 12×8 的数据矩阵
labels_rows = [f'Row{i}' for i in range(12)]
labels_cols = [f'Col{j}' for j in range(8)]

fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(
    matrix,
    annot=True,          # 在每个格子中显示数值
    fmt='.2f',
    cmap='RdBu_r',       # 红-白-蓝（反转）
    center=0,            # 以 0 为颜色中心
    xticklabels=labels_cols,
    yticklabels=labels_rows,
    linewidths=0.5,      # 格子边界宽度
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
mask = np.triu(np.ones_like(corr, dtype=bool), k=1)  # 上三角遮罩

sns.heatmap(corr,
            mask=mask,        # 隐藏重复的上三角
            annot=True,
            fmt='.2f',
            cmap='coolwarm',
            vmin=-1, vmax=1,
            square=True,      # 正方形格子
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
    method='average',      # 聚类算法：'single', 'complete', 'average', 'ward'
    metric='euclidean',    # 距离度量
    cmap='viridis',
    figsize=(10, 10),
    xticklabels=labels_cols,
    yticklabels=labels_rows,
    annot=False
)
plt.savefig('clustermap.png')
```

> `clustermap` 在 heatmap 基础上增加了行和列的**层次聚类树状图**（dendrogram）。相似的行（或列）会被归到一起，方便发现数据中的隐藏模式。这是一种无监督学习，不要任何先验知识。

### 📝 小节练习

> [!question] 选择题 1
> `sns.heatmap(data, annot=True, fmt='.2f')` 中 `annot=True` 的作用是？
> - [ ] A. 自动添加数据标注
> - [ ] B. 在每个格子中显示数值
> - [ ] C. 添加统计注释
> - [ ] D. 启用交互式标注
>
> > [!success]- 点击查看答案
> > > 正确答案: B
> > > **解析**: `annot=True` 在每个单元格中心显示对应的矩阵数值。`fmt='.2f'` 控制显示格式（保留两位小数）。`annot` 也可以是一个与矩阵形状相同的数组，用于显示自定义标签。

> [!question] 判断题 1
> `sns.clustermap()` 的聚类结果依赖于数据矩阵的行和列顺序。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > > 答案: 错误
> > > **解析**: `clustermap` 会**重新排列**行和列的顺序，将相似的聚集在一起——原始顺序不影响最终聚类结果。如果你希望保留原始顺序，应使用普通的 `heatmap`。

---

### 📚 第五节：从 C 程序管道到 Seaborn 图表 —— 完整工作流
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

### 📝 小节练习

> [!question] 选择题 1
> `pd.read_csv(sys.stdin)` 可以处理来自 C 程序管道的数据，因为？
> - [ ] A. pandas 可以直接执行 C 程序
> - [ ] B. `sys.stdin` 是一个文件对象，`read_csv` 支持任何类文件对象
> - [ ] C. pandas 内部调用 `system()` 重定向到管道
> - [ ] D. C 程序的 printf 自动输出 CSV 格式
>
> > [!success]- 点击查看答案
> > > 正确答案: B
> > > **解析**: `pd.read_csv()` 的第一个参数可以是文件路径（字符串）、类文件对象（如 `sys.stdin`、`io.StringIO`）、URL 等。管道中的 `sys.stdin` 就是一个类文件对象，`read_csv` 从中逐行读取并解析。

> [!question] 判断题 1
> `sns.set_theme(style='whitegrid')` 只影响 Seaborn 绑图，不影响 Matplotlib 绑图。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > > 答案: 错误
> > > **解析**: `sns.set_theme()` 修改的是 Matplotlib 的全局 `rcParams`，因此会**同时影响** Seaborn 和 Matplotlib 的绑图。这是 Seaborn 的设计初衷——让所有 Matplotlib 绑图自动变好看。

---

## 📋 章节测试

### 一、判断题（正确选✅，错误选❌）

> [!question] 判断题 1
> Seaborn 是完全独立的绑图库，不依赖 Matplotlib。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > > 答案: 错误
> > > **解析**: Seaborn 建立在 Matplotlib 之上，所有绑图调用最终都会转化为 Matplotlib 的 API。导入 seaborn 后，`plt.savefig()` 仍然正常工作。

> [!question] 判断题 2
> 箱线图中箱子中间的横线是平均值。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > > 答案: 错误
> > > **解析**: 箱子中间的横线是**中位数**（median），不是平均值（mean）。中位数将数据分为上下各一半；平均值受极端值影响大，不是箱线图的主要展示对象。

> [!question] 判断题 3
> `sns.pairplot(df)` 可以处理包含分类变量的 DataFrame，分类变量自动被忽略。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > > 答案: 正确
> > > **解析**: `pairplot` 默认只对**数值型列**绑图（自动跳过字符串、类别等非数值列）。也可以用 `vars` 参数手动指定要绑图的列。

> [!question] 判断题 4
> `sns.heatmap()` 必须使用正方形的矩阵数据。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > > 答案: 错误
> > > **解析**: `heatmap()` 支持任意行列数的矩阵。使用 `square=True` 可以使每个单元格显示为正方形（但矩阵本身不必是方阵）。

> [!question] 判断题 5
> `sns.lmplot()` 使用 `hue` 分组后，每个组会绑制独立的回归线。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > > 答案: 正确
> > > **解析**: 当指定 `hue` 时，`lmplot` 对每个分组分别绑制回归线（不同颜色）。也可以使用 `col` 或 `row` 参数将不同组放在不同子图中。

> [!question] 判断题 6
> 相关矩阵中对角线的值始终为 1.0。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > > 答案: 正确
> > > **解析**: 对角线是每个变量与自身的相关系数，总是 1.0（完全正相关）。热力图常用 `mask=np.triu()` 隐藏对角线上方的重复信息。

---

### 二、选择题（单项选择题）

> [!question] 选择题 1
> Seaborn 的 `violinplot` 中 `inner='quartile'` 的作用是？
> - [ ] A. 只显示外部轮廓
> - [ ] B. 在提琴内部显示四分位线
> - [ ] C. 使用四分位数替代原始数据进行绑图
> - [ ] D. 将数据按四分位数分组着色
>
> > [!success]- 点击查看答案
> > > 正确答案: B
> > > **解析**: `inner` 参数控制提琴内部显示的内容：`'box'`（小箱线图）、`'quartile'`（四分位线）、`'point'`（每个数据点）、`'stick'`（细线）或 `None`。

> [!question] 选择题 2
> 以下哪个最适合用来快速评估 C 程序的多个性能指标（时间、内存、CPU、缓存）之间的关联模式？
> - [ ] A. `sns.boxplot()`
> - [ ] B. `sns.heatmap()`
> - [ ] C. `sns.pairplot()`
> - [ ] D. `sns.scatterplot()`
>
> > [!success]- 点击查看答案
> > > 正确答案: C
> > > **解析**: `pairplot()` 一次性显示所有数值变量两两之间的散点图矩阵和对角线直方图，是探索多维数据关系的最快方式。热力图适合展示已计算好的关系矩阵（如相关性），但不适合展示原始数据点。

> [!question] 选择题 3
> `sns.heatmap(data, center=0, cmap='RdBu_r')` 中 `center=0` 的作用是？
> - [ ] A. 将图表居中显示
> - [ ] B. 将 0 值映射到 colormap 的中间颜色
> - [ ] C. 将矩阵的中心元素高亮
> - [ ] D. 将坐标系的原点移到中心
>
> > [!success]- 点击查看答案
> > > 正确答案: B
> > > **解析**: `center` 参数指定 colormap 的**对称中心**。当 `center=0` 且 `cmap='RdBu_r'` 时，正值显示为红色渐变，负值为蓝色渐变，0 为白色。适合展示有正负两极的数据。

> [!question] 选择题 4
> `sns.boxplot(data=df, x='day', y='tip', hue='sex')` 会在每个 'day' 类别下显示几个箱子？
> - [ ] A. 1 个
> - [ ] B. 2 个（Male 和 Female）
> - [ ] C. 与 'sex' 中唯一值的数量相同
> - [ ] D. 不确定
>
> > [!success]- 点击查看答案
> > > 正确答案: B 和 C（取决于数据集中 'sex' 有多少个唯一值）
> > > 考虑到 `sex` 通常只有 Male/Female 两个唯一值，实际是 2 个。但一般规则是 `hue` 有多少个唯一值就有多少个子分组。所以最佳答案是：与 `hue` 列的唯一值数量相同。

> [!question] 选择题 5
> 如果 C 程序输出格式为 `n memory time cache`（空格分隔、无表头），正确读入 DataFrame 的方式是？
> - [ ] A. `pd.read_csv(sys.stdin)`
> - [ ] B. `pd.read_csv(sys.stdin, sep='\s+')`
> - [ ] C. `pd.read_csv(sys.stdin, sep=' ', names=['n', 'memory', 'time', 'cache'])`
> - [ ] D. B 和 C 都正确
>
> > [!success]- 点击查看答案
> > > 正确答案: C
> > > **解析**: B 可以解析空格分隔的数据，但没有列名（会使用默认的 0, 1, 2, 3）。C 通过 `names` 显式指定列名更清晰。严格来说，`sep=' '` 只能处理单个空格，`sep='\s+'` 处理任意数量空白字符更健壮。所以最佳实践是 C 中同时使用 `sep='\s+'` 或 `delim_whitespace=True` 和 `names`。

> [!question] 选择题 6
> `sns.clustermap()` 的树状图（dendrogram）显示的是什么信息？
> - [ ] A. 每个数据点的时间序列
> - [ ] B. 行之间的层次聚类结构（相似性关系）
> - [ ] C. 数据点的概率密度
> - [ ] D. 列之间的线性相关性
>
> > [!success]- 点击查看答案
> > > 正确答案: B
> > > **解析**: 树状图显示的是**层次聚类**的结果。树枝的分叉点高度表示合并的两组之间的"距离"（不相似度）。距离越近（分叉点越靠下）的行，其数据模式越相似。

---

### 🛠️ 动手练习题

> [!example] 练习题 1：C 排序算法性能 Seaborn 分析
> **难度**: ⭐⭐
>
> 编写 C 程序测试四种排序算法（bubble、insertion、quick、merge）在 5 种输入规模（100, 200, 500, 1000, 2000）下的运行时间，每种组合重复测试 10 次。输出 CSV 格式：
> ```
> algorithm,n,time_ms,run
> bubble,100,12.3,1
> bubble,100,11.8,2
> ...
> ```
> 用 Python + Seaborn 完成：
> 1. 箱线图：按 `algorithm` 分组，展示时间分布（`hue='algorithm'` 或直接用 `x='algorithm'`）
> 2. 提琴图：按 `algorithm` 分组，添加 `hue='algorithm'`
> 3. 对数坐标折线图（Seaborn 风格，手动 ax 操作）
> 4. `pairplot` 概览（需要将数据透视/重塑）
>
> 保存为 `sort_seaborn_report.png`（带 `fig.suptitle`）

> [!example] 练习题 2：相关性矩阵可视化
> **难度**: ⭐⭐
>
> 编写 C 程序生成一个 8 维随机数据（每维度 200 个样本），每列代表不同的性能度量（如 CPU、内存、磁盘 I/O、网络延迟等），在 C 程序中引入一定的相关性（例如 CPU 和内存正相关）。输出为空格分隔的数值矩阵。Python 脚本：
> 1. 用 `np.loadtxt` 读取数据
> 2. 计算 `np.corrcoef` 相关性矩阵
> 3. 用 `sns.heatmap` 绑制带注释的相关性热力图
> 4. 用 `sns.clustermap` 绑制带聚类的热力图
>
> 保存为 `correlation_analysis.png`

> [!example] 练习题 3：lmplot 分组回归分析
> **难度**: ⭐⭐
>
> 编写 C 程序生成两种数据结构（链表和动态数组）在不同元素数量下的插入、查找、删除耗时数据。输出格式：`structure,operation,n,time_us`
> Python 脚本：
> 1. 读取数据到 DataFrame
> 2. 用 `sns.lmplot` 分别展示结构 × 操作组合下的 n vs time 关系（使用 `hue='operation'` 和 `col='structure'`）
> 3. 观察回归线的斜率：链表和数组在哪种操作下差异最大？

> [!example] 练习题 4：python -c 一行流 Seaborn 绑图
> **难度**: ⭐
>
> 用 `python -c` 一行流完成以下 Seaborn 绑图（使用 tips 内置数据集）：
> 1. 箱线图：`tips` vs `day`，按 `sex` 分组着色
> 2. 保存为 `tips_boxplot.png`
>
> 使用 `python -c` 风格（分号 + 多行），确保 `matplotlib.use('Agg')` 已设置。
