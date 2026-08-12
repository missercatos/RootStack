# Pandas：表格数据瑞士军刀 (Pandas Basics)
---

## 章节概述

量化分析处理的是表格化的金融数据：日线行情、财务报表、持仓记录。Pandas 是 Python 生态中处理二维表格数据的标准库。本章从 C 程序员的视角介绍 DataFrame 和 Series 的数据结构、CSV/Excel 读写、过滤/分组/合并操作，以及 `.loc`/`.iloc` 的索引哲学。最后简要介绍 Polars —— 用 Rust 重写的极速替代品。

> **核心理念**：如果说 NumPy 是"带 stride 的 C 数组"，那 Pandas 就是"带标签的 NumPy 列向量集合"。DataFrame 底层每一列都是一个 NumPy 数组，而行索引和列标签则提供了比数字下标更强大的数据访问方式。你仍然可以用 C 程序员的直觉来理解它：内存布局、类型一致性、向量化操作——这些核心概念不变。

---

### 第一节：Series 与 DataFrame —— 两种核心数据结构

#### 1.1 Series：带标签的一维数组

```bash
python -c "
import pandas as pd
import numpy as np

# Series = index + values（底层的 NumPy 数组）
s = pd.Series([1.0, 2.5, 3.8, 5.2], index=['a', 'b', 'c', 'd'])
print(s)
print()
print('values type:', type(s.values)) # numpy.ndarray
print('dtype:', s.dtype) # float64
"
```

Series 可以看作两个数组的组合：
- `s.values` —— 底层的 NumPy 数组（和 C 数组一样连续存储）
- `s.index` —— 标签索引（Python 对象数组）

```bash
python -c "
import pandas as pd

s = pd.Series([10, 20, 30, 40], index=['AAPL', 'GOOG', 'MSFT', 'TSLA'])
print('by label:', s['AAPL']) # 用标签访问
print('by position:', s.iloc[0]) # 用位置访问（和 C 数组相同）
print(s[['AAPL', 'TSLA']]) # 花式索引
"
```

#### 1.2 DataFrame：带标签的二维表格

DataFrame 底层是多个 Series 的列对齐组合。每一列是一个独立的 NumPy 数组：

```bash
python -c "
import pandas as pd
import numpy as np

df = pd.DataFrame({
 'symbol': ['AAPL', 'GOOG', 'MSFT'],
 'price': [150.0, 2800.0, 330.0],
 'volume': [80000000, 1200000, 25000000]
})
print(df)
print()
print('dtypes:')
print(df.dtypes)
# price 列底层是 float64 的 NumPy 数组
# volume 列底层是 int64 的 NumPy 数组
# symbol 列底层是 object 数组（Python 字符串）
"
```

**数据结构类比**：

| 概念 | C 语言 | NumPy | Pandas |
|------|--------|-------|--------|
| 一维数组 | `double arr[100]` | `np.array` (ndarray) | `pd.Series` |
| 二维表格 | `double mat[100][10]` | `np.array` (2D ndarray) | `pd.DataFrame` |
| 元素访问 | `arr[i]` | `arr[i]` | `s.iloc[i]`（位置） / `s.loc[label]`（标签） |
| 类型信息 | `double` | `dtype` | `dtype`（列级别） |

#### 1.3 DataFrame 的内存真相

```bash
python -c "
import pandas as pd
import numpy as np

df = pd.DataFrame({
 'a': np.random.randn(1000000),
 'b': np.random.randn(1000000),
 'c': np.random.randn(1000000)
})
print('memory usage (MB):')
print(df.memory_usage(deep=True) / 1024 / 1024)
# 每列约 8MB（100万 * 8字节 float64）
# 三列总计约 24MB — 和 C 中 double matrix[3][1000000] 一样！
"
```

---

### 第二节：数据读写 —— CSV、Excel 与更多

#### 2.1 CSV：量化数据的默认格式

```bash
python -c "
import pandas as pd

# 写入示例数据
df = pd.DataFrame({
 'date': ['2024-01-02', '2024-01-03', '2024-01-04'],
 'open': [150.0, 151.5, 149.8],
 'high': [152.0, 153.0, 151.0],
 'low': [149.0, 150.0, 148.5],
 'close':[151.5, 150.8, 150.2],
 'volume':[80000000, 75000000, 82000000]
})
df.to_csv('/tmp/sample_ohlcv.csv', index=False)
print('written to /tmp/sample_ohlcv.csv')
"
```

```bash
python -c "
import pandas as pd

df = pd.read_csv('/tmp/sample_ohlcv.csv')
print(df)
print()
print(df.describe()) # 统计摘要
"
```

关键参数：
- `parse_dates=['date']` — 自动解析日期列
- `index_col='date'` — 将某列设为行索引
- `dtype={'volume': 'int64'}` — 指定列的数据类型
- `usecols=['date', 'close']` — 只读需要的列

#### 2.2 Excel：财务报表的常用格式

```bash
python -c "
import pandas as pd
# 读取 Excel（需要 openpyxl 或 xlrd）
# df = pd.read_excel('financials.xlsx', sheet_name='Balance Sheet', skiprows=3)
# df.to_excel('output.xlsx', sheet_name='Summary', index=False)
print('Excel read/write requires: pip install openpyxl')
"
```

#### 2.3 与 NumPy 的无缝互操作

```python
# DataFrame 的某一列就是一个 NumPy 数组
close_prices = df['close'].values # 返回 np.ndarray
returns = np.diff(np.log(close_prices)) # 可以直接做 NumPy 运算

# NumPy 数组可以直接构造成 DataFrame
new_df = pd.DataFrame(np.random.randn(100, 4),
 columns=['A', 'B', 'C', 'D'])
```

> 向量化计算技巧详见 [[../7科学计算/01_NumPy向量化：告别C式循环|NumPy 向量化]]。

---

### 第三节：数据筛选与索引 —— .loc 与 .iloc

#### 3.1 .iloc：位置索引（C 程序员最熟悉的模式）

`iloc` 就是 C 数组的 `[i][j]`——纯粹的整数位置索引：

```bash
python -c "
import pandas as pd
import numpy as np

np.random.seed(42)
df = pd.DataFrame(np.random.randn(5, 4),
 columns=['A', 'B', 'C', 'D'])
print('original:')
print(df)
print()

# 位置索引 — 和 C 的 df[i][j] 一样
print('df.iloc[2, 1]:', df.iloc[2, 1]) # 第 3 行，第 2 列
print('df.iloc[1:3, 0:2]:') # 行切片 + 列切片
print(df.iloc[1:3, 0:2])
print('df.iloc[[0, 4], [1, 3]]:') # 花式索引
print(df.iloc[[0, 4], [1, 3]])
"
```

#### 3.2 .loc：标签索引（Pandas 独门武器）

```bash
python -c "
import pandas as pd

# 行有标签，列也有标签
df = pd.DataFrame(
 {'price': [150, 2800, 330], 'pe': [28, 22, 35]},
 index=['AAPL', 'GOOG', 'MSFT']
)
print('AAPL row:')
print(df.loc['AAPL'])
print()
print('price column:', df.loc[:, 'price'].values)
print('boolean condition:', df.loc[df['pe'] < 30])
"
```

#### 3.3 布尔索引：条件筛选的主力

```bash
python -c "
import pandas as pd
import numpy as np

np.random.seed(1)
df = pd.DataFrame({
 'returns': np.random.randn(1000) * 0.02,
 'volume': np.random.randint(1000000, 10000000, 1000)
})

# C 思维：遍历所有行检查条件
# Pandas 思维：一行布尔表达式
high_vol_up = df[(df['volume'] > 5000000) & (df['returns'] > 0)]
print(f'{len(high_vol_up)} days with high volume and positive returns')
print('condition speed: vectorized, not loop-based')
"
```

常用筛选模式：

```python
# 等值筛选
df[df['symbol'] == 'AAPL']

# 范围筛选
df[(df['price'] >= 100) & (df['price'] <= 200)]

# 列表筛选
df[df['symbol'].isin(['AAPL', 'GOOG', 'MSFT'])]

# 字符串匹配
df[df['symbol'].str.startswith('A')]

# 空值筛选
df[df['price'].notna()]
```

---

### 第四节：分组、聚合与透视表

#### 4.1 groupby：分类聚合

```bash
python -c "
import pandas as pd
import numpy as np

np.random.seed(0)
df = pd.DataFrame({
 'sector': ['Tech', 'Tech', 'Finance', 'Finance', 'Tech'],
 'symbol': ['AAPL', 'MSFT', 'JPM', 'GS', 'GOOG'],
 'returns': np.random.randn(5) * 0.02,
 'volume': np.random.randint(1e6, 1e7, 5)
})
print('By sector mean returns:')
print(df.groupby('sector')['returns'].mean())
print()
print('Multiple aggregations:')
print(df.groupby('sector').agg({
 'returns': ['mean', 'std', 'count'],
 'volume': 'sum'
}))
"
```

```bash
python -c "
import pandas as pd

# 更复杂的示例：多列分组 + transform
df = pd.DataFrame({
 'date': ['2024-01', '2024-01', '2024-01', '2024-02', '2024-02'],
 'symbol': ['AAPL', 'GOOG', 'MSFT', 'AAPL', 'GOOG'],
 'price': [150, 2800, 330, 155, 2850]
})
# 计算每个 symbol 的月度价格变化
df['prev_price'] = df.groupby('symbol')['price'].shift(1)
df['pct_change'] = (df['price'] / df['prev_price'] - 1) * 100
print(df)
"
```

#### 4.2 merge：表连接

```bash
python -c "
import pandas as pd

prices = pd.DataFrame({
 'symbol': ['AAPL', 'GOOG', 'MSFT'],
 'price': [150, 2800, 330]
})
fundamentals = pd.DataFrame({
 'symbol': ['AAPL', 'GOOG', 'TSLA'],
 'pe': [28, 22, 45]
})

# 类似 SQL JOIN
inner = prices.merge(fundamentals, on='symbol', how='inner')
left = prices.merge(fundamentals, on='symbol', how='left')
outer = prices.merge(fundamentals, on='symbol', how='outer')

print('inner (only matching):', list(inner['symbol']))
print('left (all prices):', list(left['symbol']))
print('outer (all symbols):', list(outer['symbol']))
"
```

#### 4.3 pivot_table：透视表

```bash
python -c "
import pandas as pd
import numpy as np

np.random.seed(1)
df = pd.DataFrame({
 'date': np.repeat(['2024-Q1', '2024-Q2', '2024-Q3', '2024-Q4'], 3),
 'sector': ['Tech', 'Finance', 'Energy'] * 4,
 'returns': np.random.randn(12) * 0.05
})
pivot = df.pivot_table(
 values='returns',
 index='date',
 columns='sector',
 aggfunc='mean'
)
print(pivot)
"
```

---

### 第五节：Polars —— 更快的 Pandas 替代品

Polars 用 Rust 重写了 DataFrame，提供零拷贝、惰性计算和 SIMD 优化：

```bash
python -c "
# pip install polars
import polars as pl
import numpy as np

# 类似 Pandas 但语法略有不同
df = pl.DataFrame({
 'symbol': ['AAPL', 'GOOG', 'MSFT'],
 'price': [150.0, 2800.0, 330.0],
 'volume': [80000000, 1200000, 25000000]
})
print(df)
print()
# Polars 的操作链式调用
result = df.filter(pl.col('price') > 200).select(['symbol', 'price'])
print(result)
"
```

Pandas vs Polars 关键差异：

| 特性 | Pandas | Polars |
|------|--------|--------|
| 底层语言 | C/Cython | Rust |
| 索引 | 有行索引/列标签 | 无行索引（更接近 NumPy） |
| 并行计算 | 部分操作 | 几乎所有操作 |
| 惰性计算 | 无 | `pl.LazyFrame` |
| 内存效率 | 一般 | 优秀（Apache Arrow 格式） |
| 生态成熟度 | 极成熟 | 快速成长中 |

> 对于大数据量的量化回测，Polars 可以带来 5-10 倍的性能提升。但 Pandas 的生态（文档、教程、第三方集成）目前仍然远胜 Polars。

---

### 小节练习


> [!question] 判断题 1
> `.iloc` 使用标签进行索引，`.loc` 使用整数位置进行索引。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 反过来。`.iloc` 是 integer-location，使用整数位置（0, 1, 2...）。`.loc` 是 label-location，使用行/列标签。C 程序员应优先理解 `.iloc`。

---

## 章节测试

### 一、判断题

> [!question] 判断题 1
> Pandas 的 Series 底层数据存储就是一个 NumPy 数组。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: `Series.values` 直接返回底层的 `ndarray`。Series 只是在 NumPy 数组的基础上添加了索引标签。

> [!question] 判断题 2
> DataFrame 中 `df['close']` 返回的是一个 Series，其 `.values` 属性返回 NumPy 数组。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: 选择一列返回 Series，`.values` 返回该列的 ndarray。可以用 `np.log(df['close'].values)` 做 NumPy 向量化计算。

> [!question] 判断题 3
> Pandas 的 `groupby` 操作返回的结果不能直接用于后续的链式操作。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: `groupby` 返回一个 `DataFrameGroupBy` 对象，可以继续链式调用 `.mean()`、`.agg()`、`.transform()` 等方法，支持流式数据处理。

> [!question] 判断题 4
> `pd.read_csv()` 会自动将日期字符串解析为 `datetime64` 类型。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 默认情况下日期列被读为字符串。需要使用 `parse_dates=['date']` 参数显式指定要解析的列，或使用 `pd.to_datetime()` 后处理。

> [!question] 判断题 5
> Pandas 中 `df[df['price'] > 100]` 的底层实现是 Python 的 for 循环遍历。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 错误
> > **解析**: 布尔索引底层返回的是布尔 NumPy 数组，利用 NumPy 的向量化操作进行筛选，不通过 Python 循环。这就是它比 C 中使用 `for` + `if` 手动筛选快得多的原因。

> [!question] 判断题 6
> Polars 比 Pandas 快是因为它用 Rust 编写了核心引擎。 （ ）
> - [ ] 正确
> - [ ] 错误
>
> > [!success]- 点击查看答案
> > 答案: 正确
> > **解析**: Polars 底层用 Rust 实现，使用 Apache Arrow 列式存储格式、SIMD 优化和自动并行化。对于大数据集，通常比 Pandas 快 5-10 倍。

---


---

## 力扣练习

以下题目用于验证本章所学内容：

| 题号 | 题目 | 链接 | 涉及知识点 |
|------|------|------|-----------|
| 175 | 组合两个表 | https://leetcode.cn/problems/combine-two-tables/ | 表连接、数据合并 |
| 176 | 第二高的薪水 | https://leetcode.cn/problems/second-highest-salary/ | 排序去重、子查询 |
| 178 | 分数排名 | https://leetcode.cn/problems/rank-scores/ | 窗口函数、排名思想 |



### 动手练习题

> [!example] 练习题 1：构建 OHLCV 分析流水线
> **难度**: 简单
>
> 下载或创建一份包含 `date`, `open`, `high`, `low`, `close`, `volume` 的 CSV 数据（至少 100 行）。用 Pandas 完成：
> 1. 读取并解析日期
> 2. 计算每日收益率 `returns = close.pct_change()`
> 3. 找出成交量最大的 10 个交易日
> 4. 计算月度平均收益率（用 `groupby` + `resample`）
> 5. 将结果保存为新的 CSV

> [!example] 练习题 2：Pandas vs Polars 性能对比
> **难度**: 简单
>
> 生成一个包含 100 万行和 10 列随机数据的 DataFrame。分别用 Pandas 和 Polars 执行：`groupby` 聚合、列筛选、条件过滤、排序。用 `%timeit` 比较执行时间。

> [!example] 练习题 3：财务数据透视表
> **难度**: 简单
>
> 创建一个包含 `date`, `sector`, `symbol`, `market_cap`, `returns` 的数据集。用 `pivot_table` 计算：
> 1. 每个 sector 每月的平均收益率
> 2. 每个 sector 的总市值（market_cap 的和）
> 3. 使用 `melt` 将宽表转回长表
