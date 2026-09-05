# R 与 Julia 跨语言调用 (R & Julia Interop)

---

## 章节概述

Python 的生态优势在于"胶水语言"特性——可以无缝调用 R 和 Julia 的库。对于 C 程序员来说，这相当于 Python 提供了一套 FFI 层，让你用 Python 的语法调用其他语言的函数。

> **为什么需要跨语言？** R 的统计分析和绘图（ggplot2、dplyr）比 Python 更成熟；Julia 的数值计算速度接近 C。通过 rpy2 和 juliacall，你可以在 Python 项目中直接使用这些优势。

---

## 1. rpy2：在 Python 中调用 R

```bash
pip install rpy2
# 需要系统安装 R：sudo apt install r-base
```

```python
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri

# 启用 pandas ↔ R DataFrame 自动转换
pandas2ri.activate()

# 直接执行 R 代码
ro.r('x <- rnorm(100)')
ro.r('print(summary(x))')

# 调用 R 函数
r_norm = ro.r('rnorm')
result = r_norm(100, mean=50, sd=10)  # 生成100个正态分布数
print(type(result))  # <class 'numpy.ndarray'>

# Python ↔ R DataFrame 转换
import pandas as pd
df = pd.DataFrame({'x': [1,2,3,4,5], 'y': [10,20,30,40,50]})

# 转为 R DataFrame
r_df = pandas2ri.py2rpy(df)

# 在 R 中使用
ro.globalenv['r_df'] = r_df
ro.r('r_df$x <- r_df$x * 2')

# 转回 Python
df_back = pandas2ri.rpy2py(ro.r('r_df'))
```

---

## 2. Rpy2 调用 ggplot2

```python
from rpy2.robjects import ggplot2, fonts
from rpy2.robjects.packages import importr

# 导入 R 包
gg = importr('ggplot2')
dplyr = importr('dplyr')

# 构建 ggplot2 图表
plot = (
    gg.ggplot(r_df) +
    gg.aes(x='x', y='y') +
    gg.geom_point() +
    gg.geom_smooth(method='lm') +
    gg labs(title='Python → R ggplot2', x='X', y='Y')
)

# 保存为文件
gg.ggsave('plot.pdf', plot)
```

---

## 3. pyjulia：在 Python 中调用 Julia

```bash
pip install juliacall
# 首次运行会自动安装 Julia
```

```python
from juliacall import Main as jl

# 执行 Julia 代码
jl.eval('println("Hello from Julia!")')

# 调用 Julia 函数
jl.eval('function fib(n::Int)::Int; n <= 1 ? n : fib(n-1) + fib(n-2); end')
result = jl.fib(30)
print(f"Julia fib(30) = {result}")

# 使用 Julia 包
jl.eval('using Pkg')
jl.eval('Pkg.add("PyPlot")')
jl.eval('using PyPlot')

# Julia 数组 ↔ Python numpy
jl.eval('a = [1, 2, 3, 4, 5]')
jl.eval('b = a .^ 2')  # Julia 的广播操作
result = jl.eval('b')
print(result)  # [1, 4, 9, 16, 25]
```

---

## 4. rpy2 与 Python 科学计算栈结合

```python
import pandas as pd
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri, packages

pandas2ri.activate()

# 数据分析流水线
df = pd.read_csv('data.csv')

# 用 R 的 dplyr 做数据处理
dplyr = packages.importr('dplyr')
r_df = pandas2ri.py2rpy(df)

# R 的管道操作
result_r = dplyr.summarise(
    dplyr.group_by(r_df, 'category'),
    mean_value=dplyr.mean('value')
)

# 转回 Python
result_py = pandas2ri.rpy2py(result_r)
print(result_py)
```

---

## 5. 使用背景

| 场景 | 推荐方案 | 理由 |
|------|---------|------|
| 统计分析 + 出版级图表 | rpy2 + ggplot2 | R 的统计生态最成熟 |
| 高性能数值计算 | juliacall | Julia 速度接近 C |
| 机器学习 | Python (sklearn/PyTorch) | Python 生态最强 |
| 混合项目 | rpy2 / juliacall | 按需调用最佳工具 |

---

## 6. 注意事项

- **性能开销**：跨语言调用有数据转换成本，批量操作优于逐个调用
- **内存管理**：R 和 Python 各自管理内存，大数据转换注意复制开销
- **安装依赖**：rpy2 需要系统安装 R；juliacall 首次运行自动安装 Julia
- **调试困难**：跨语言错误信息可能不直观，建议在各语言环境中分别测试

---

## 速查卡片

| 需求 | 命令 |
|------|------|
| 安装 rpy2 | `pip install rpy2` |
| 安装 juliacall | `pip install juliacall` |
| Python 执行 R | `ro.r('r_code')` |
| Python 调用 R 函数 | `ro.r('func_name')(args)` |
| Python 执行 Julia | `jl.eval('julia_code')` |
| Python 调用 Julia | `jl.func_name(args)` |
| pd ↔ R | `pandas2ri.py2rpy(df)` / `pandas2ri.rpy2py(r_df)` |
