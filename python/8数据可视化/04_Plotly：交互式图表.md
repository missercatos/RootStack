# Plotly：交互式图表 (Plotly: Interactive Charts)
---

## 📖 章节概述

Matplotlib 和 Seaborn 生成的是静态图片——适合论文和报告，但当你需要放大查看异常数据点、悬停显示具体数值、或者用 C 程序持续输出数据并实时观察，交互式图表是更好的选择。Plotly 的 `plotly.express` 一行代码就能生成可缩放、可平移、可悬停的 HTML 图表，`plotly.graph_objects` 则提供精细控制的底层 API。对 C 程序员来说，Plotly 相当于给你的 C 程序输出装了一个"仪表盘"——不需要写任何前端代码。

> **核心理念**：Matplotlib 是"打印到纸上"，Plotly 是"显示在屏幕上"。当你需要交互式数据探索（特别是在 Jupyter 或浏览器中）时，Plotly 是首选。当你的目标是嵌入论文或生成高质量 PDF 时，Matplotlib 更合适。两者不是竞争关系，而是互补工具。

---

### 📚 第一节：Plotly Express —— 交互式图表的"python -c"模式
---

1.1 安装与基础用法
------------------

```bash
pip install plotly
```

最简单的交互式图表示例：

```python
import plotly.express as px

x = [1, 2, 3, 4, 5]
y = [1, 4, 9, 16, 25]

fig = px.line(x=x, y=y, title='Simple Line Chart')
fig.write_html('line.html')
```

打开 `line.html` 用浏览器查看——你可以：
- 鼠标悬停：查看每个数据点的坐标值
- 鼠标滚轮：缩放图表
- 拖拽：平移图表
- 双击：重置视图
- 工具栏：下载为 PNG、选区放大、套索选择等

> Plotly Express 的作用类似于 `python -c` 一行流——用最少的代码得到结果。你不需要了解 Figure、Layout、Trace 等底层概念就可以绑出专业级的交互式图表。

1.2 四种基础图表
----------------

```python
import plotly.express as px
import numpy as np

# 折线图
df = px.data.gapminder().query("country == 'China'")
fig1 = px.line(df, x='year', y='pop',
               title='China Population Over Time')
fig1.write_html('population.html')

# 散点图
df = px.data.iris()
fig2 = px.scatter(df, x='sepal_length', y='sepal_width',
                  color='species', size='petal_length',
                  hover_data=['petal_width'],
                  title='Iris Dataset')
fig2.write_html('iris.html')

# 柱状图
df = px.data.tips()
fig3 = px.bar(df, x='day', y='total_bill', color='sex',
              barmode='group', title='Tips by Day')
fig3.write_html('tips_bar.html')

# 直方图
fig4 = px.histogram(df, x='total_bill', nbins=30,
                     color='time', marginal='box',
                     title='Bill Amount Distribution')
fig4.write_html('tips_hist.html')
```

> `marginal='box'` 在直方图顶部同时显示箱线图——两个图表共享同一个 X 轴。这在 Matplotlib 中需要 `GridSpec` + `twinx` 的组合才能实现。

1.3 从 C 程序管道到交互式图表
----------------------------

```python
import sys
import plotly.express as px
import pandas as pd

# ./benchmark | python3 interactive_plot.py
df = pd.read_csv(sys.stdin,
                 sep='\s+',
                 names=['n', 'time_ms', 'memory_kb'])

fig = px.scatter(df, x='n', y='time_ms',
                 color='memory_kb',
                 size='memory_kb',
                 hover_data=['n', 'time_ms', 'memory_kb'],
                 title='C Program Benchmark (Interactive)',
                 log_x=True, log_y=True,
                 color_continuous_scale='Viridis')
fig.write_html('benchmark_interactive.html')
```

> 交互式图表让你可以直接在浏览器中悬停查看每个数据点的精确值——不再需要像 Matplotlib 那样在图上手动 `annotate` 标注关键点。

### 📝 小节练习

> [!question] 选择题 1
> `plotly.express` 生成的图表默认保存在什么格式中？
> - [ ] A. PNG
> - [ ] B. PDF
> - [ ] C. HTML（内含 JavaScript）
> - [ ] D. SVG
>
> > [!success]- 点击查看答案
> > > 正确答案: C
> > > **解析**: Plotly 图表本质上是基于 JavaScript 的 Web 图表（使用 plotly.js 渲染）。`fig.write_html()` 生成独立的 HTML 文件（包含所有数据和 JS 代码），可以用任何现代浏览器打开。也可以导出为 PNG、SVG、PDF（需要 kaleido 引擎）。

> [!question] 判断题 1
> Plotly 图表只能在 Jupyter Notebook 中交互，保存为 HTML 后失去交互功能。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > > 答案: 错误
> > > **解析**: `write_html()` 生成的 HTML 文件是**完整独立**的，包含所有交互功能和数据的 plotly.js 库（默认从 CDN 加载）。用浏览器打开后，所有交互功能（缩放、平移、悬停、选区）都正常可用。

---

### 📚 第二节：graph_objects —— 深入到每一层
---

2.1 Plotly 的数据模型：Figure → Trace → Data
--------------------------------------------

Plotly 的架构与 Matplotlib 完全不同。核心概念：

```
Figure
├── data (list of Traces)
│   ├── Trace 1 (scatter)
│   ├── Trace 2 (line)
│   └── Trace 3 (bar)
└── layout
    ├── title, xaxis, yaxis
    ├── legend, annotations
    └── shapes, images
```

每个 `Trace` 是一个独立的"图层"，拥有自己的数据、类型和样式。`Layout` 控制图表的全局外观。

```python
import plotly.graph_objects as go
import numpy as np

x = np.linspace(0, 10, 100)

fig = go.Figure()

# 添加 Trace（数据图层）
fig.add_trace(go.Scatter(
    x=x, y=np.sin(x),
    mode='lines+markers',
    name='sin(x)',
    line=dict(color='royalblue', width=3),
    marker=dict(size=6, symbol='circle')
))

fig.add_trace(go.Scatter(
    x=x, y=np.cos(x),
    mode='lines+markers',
    name='cos(x)',
    line=dict(color='firebrick', width=3, dash='dash'),
    marker=dict(size=6, symbol='square')
))

# 设置 Layout（全局外观）
fig.update_layout(
    title='Trigonometric Functions (graph_objects)',
    xaxis_title='x',
    yaxis_title='f(x)',
    hovermode='x unified',     # 统一悬停模式
    template='plotly_white',   # 内置模板
    font=dict(size=14),
)

fig.write_html('trig_go.html')
```

> `go.Figure().add_trace()` 的思维模型类似于 C 语言中逐个往数组里添加元素——每个 `trace` 是一组有意义的独立数据，`fig.data` 就是这些 trace 组成的列表。这与 Matplotlib 的"坐标系内绑制"思路完全不同。

2.2 子图布局：make_subplots()
---------------------------

```python
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np

fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=('sin(x)', 'cos(x)', 'tan(x)', 'sin·cos'),
    shared_xaxes=True,
    vertical_spacing=0.1,
)

x = np.linspace(0, 2*np.pi, 200)

fig.add_trace(go.Scatter(x=x, y=np.sin(x), name='sin'), row=1, col=1)
fig.add_trace(go.Scatter(x=x, y=np.cos(x), name='cos'), row=1, col=2)
fig.add_trace(go.Scatter(x=x, y=np.tan(x), name='tan'), row=2, col=1)
fig.add_trace(go.Scatter(x=x, y=np.sin(x)*np.cos(x), name='sin·cos'), row=2, col=2)

fig.update_yaxes(range=[-5, 5], row=2, col=1)  # 限制 tan 范围
fig.update_layout(height=700, title_text='Subplots with Plotly')
fig.write_html('subplots_plotly.html')
```

2.3 双 Y 轴
-----------

```python
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np

fig = make_subplots(specs=[[{"secondary_y": True}]])

x = np.linspace(0, 10, 100)

fig.add_trace(
    go.Scatter(x=x, y=np.sin(x), name='sin(x)', line_color='blue'),
    secondary_y=False,
)

fig.add_trace(
    go.Scatter(x=x, y=np.exp(x)*0.01, name='exp(x)', line_color='red'),
    secondary_y=True,
)

fig.update_xaxes(title_text='x')
fig.update_yaxes(title_text='sin(x)', secondary_y=False, color='blue')
fig.update_yaxes(title_text='exp(x)', secondary_y=True, color='red')

fig.write_html('dual_axis.html')
```

### 📝 小节练习

> [!question] 选择题 1
> `go.Figure().add_trace(go.Scatter(...))` 中，`trace` 的概念最接近 Matplotlib 中的什么？
> - [ ] A. Figure
> - [ ] B. Axes
> - [ ] C. 一次 `plot()` / `scatter()` 调用生成的数据图层
> - [ ] D. 整个图表
>
> > [!success]- 点击查看答案
> > > 正确答案: C
> > > **解析**: 在 Plotly 中，每个 `trace` 对应一个独立的数据图层（一次 `plot()` 或 `scatter()` 调用）。多个 trace 叠加在同一坐标系中。一个 `Figure` 可以包含多个 trace。

> [!question] 判断题 1
> `make_subplots(rows=2, cols=2)` 创建的四个子图必须使用相同的图表类型。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > > 答案: 错误
> > > **解析**: 每个子图可以独立使用不同的 trace 类型。比如 (1,1) 放 `go.Scatter`（折线图），(1,2) 放 `go.Bar`（柱状图），(2,1) 放 `go.Histogram`（直方图），(2,2) 放 `go.Heatmap`（热力图）。在同一 Figure 中混合多种图表类型是 Plotly 的一大优势。

---

### 📚 第三节：高级交互 —— 3D 图与联动
---

3.1 3D 散点图
-------------

```python
import plotly.express as px
import numpy as np

# 模拟 C 程序的三维性能数据
n = 200
data = {
    'input_size': 10 ** np.random.uniform(2, 5, n),
    'time_ms': np.random.lognormal(2, 1, n),
    'memory_kb': np.random.lognormal(6, 1.5, n),
    'algorithm': np.random.choice(['qsort', 'msort', 'heap', 'bsort'], n),
}

fig = px.scatter_3d(
    data, x='input_size', y='time_ms', z='memory_kb',
    color='algorithm',
    size='time_ms',       # 气泡大小
    opacity=0.7,
    title='3D Performance Visualization',
    log_x=True,
)
fig.write_html('3d_scatter.html')
```

> 在浏览器中，你可以拖拽旋转、缩放 3D 视角。这比任何二维投影更能直观展示三维数据之间的关系。当一个 C 程序输出三维数据时（比如 `(n, time, memory)`），3D 散点图是呈现数据的最佳方式。

3.2 3D 曲面图
-------------

适合展示 C 程序输出的二维参数空间的性能曲面：

```python
import plotly.graph_objects as go
import numpy as np

x = np.linspace(-5, 5, 50)
y = np.linspace(-5, 5, 50)
X, Y = np.meshgrid(x, y)
Z = np.sin(np.sqrt(X**2 + Y**2))  # 涟漪曲面

fig = go.Figure(data=[go.Surface(z=Z, x=X, y=Y, colorscale='Viridis')])
fig.update_layout(
    title='3D Surface Plot',
    scene=dict(
        xaxis_title='X',
        yaxis_title='Y',
        zaxis_title='Z'
    )
)
fig.write_html('3d_surface.html')
```

3.3 联动选择（Linked Selection）
--------------------------------

Plotly 支持多个图表之间联动——选择一个图表的数据点，其他图表同步高亮：

```python
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

df = px.data.iris()

fig = make_subplots(rows=1, cols=2,
                    subplot_titles=('Scatter', 'Box Plot'))

for species, color in zip(df['species'].unique(), ['blue', 'red', 'green']):
    mask = df['species'] == species
    subset = df[mask]

    fig.add_trace(
        go.Scatter(x=subset['sepal_length'], y=subset['sepal_width'],
                   mode='markers', name=species, marker_color=color,
                   legendgroup=species),
        row=1, col=1
    )

    fig.add_trace(
        go.Box(y=subset['petal_length'], name=species,
               marker_color=color, legendgroup=species,
               showlegend=False),
        row=1, col=2
    )

fig.update_layout(title='Linked Views (click legend to toggle)')
fig.write_html('linked_views.html')
```

> `legendgroup` 让同一组的 trace 共享图例项。点击图例中的某一项，所有图表中该组数据同时显示/隐藏——这对 C 程序的多维基准测试数据非常有用。

### 📝 小节练习

> [!question] 选择题 1
> `px.scatter_3d()` 绑定后，用户可以在浏览器中进行的操作包括？
> - [ ] A. 鼠标旋转 3D 视角
> - [ ] B. 缩放和平移
> - [ ] C. 悬停查看数据点的具体值
> - [ ] D. 以上全部
>
> > [!success]- 点击查看答案
> > > 正确答案: D
> > > **解析**: Plotly 的 3D 图支持完整的交互：鼠标拖拽旋转视角、滚轮缩放、右键平移（或 Shift+拖拽）、悬停显示数据。相当于在浏览器中查看一个可操作的 3D 模型。

> [!question] 判断题 1
> Plotly 的 `legendgroup` 参数仅影响图例的显示顺序，不影响其他功能。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > > 答案: 错误
> > > **解析**: `legendgroup` 将多个 trace 绑定到同一个图例项。点击该图例项时，所有同组的 trace 在多子图中**同时**显示/隐藏。这是实现多面板联动选择的关键参数。

---

### 📚 第四节：Plotly vs Matplotlib —— 选择指南与静态导出
---

4.1 选型决策表
--------------

| 场景 | 推荐工具 | 原因 |
|------|---------|------|
| 论文/报告用静态图 | Matplotlib | 精确的排版控制，PDF/EPS 矢量输出 |
| 数据分析探索 | Plotly | 交互式缩放、悬停、过滤，一次写多个 HTML |
| Jupyter Notebook | 两者皆可 | Plotly 内嵌更交互，Matplotlib 更快 |
| 自动化报告生成 | Matplotlib | 批量生成 PNG/PDF，不依赖浏览器 |
| C 程序性能仪表盘 | Plotly + Dash | Web 仪表盘，实时更新 |
| 统计数据可视化 | Seaborn | 一行代码绑箱线图、回归线、热力图 |
| 出版物级图表 | Matplotlib | `rcParams` 精确控制每一个像素 |
| GPU 密集型绑图 | 都不要 | 用 C 程序的 OpenGL 或 Vulkan 渲染 |

4.2 从 Plotly 导出静态图片
-------------------------

```python
import plotly.express as px

fig = px.line(x=[1, 2, 3], y=[1, 4, 9])

# 导出为各种格式（需要安装 kaleido）
fig.write_image('chart.png', width=800, height=600, scale=2)  # 高 DPI
fig.write_image('chart.pdf')
fig.write_image('chart.svg')

# 如果没有 kaleido，可以：
fig.show(renderer='png')  # 在 Jupyter 中渲染为 PNG
```

```bash
pip install kaleido  # 静态图片导出引擎
```

4.3 命令行一行流生成交互式 HTML
-----------------------------

```bash
# 从管道数据生成交互式图表
./my_c_program | python -c "
import sys, pandas as pd, plotly.express as px
df = pd.read_csv(sys.stdin, sep='\s+', names=['n', 'time'])
fig = px.line(df, x='n', y='time', title='C Program Output')
fig.write_html('output.html')
"
```

> 将交互式 HTML 分享给同事：他们不需要安装 Python、不需要编译 C 程序，甚至不需要任何开发环境——用浏览器就能看到完整的互动数据。

### 📝 小节练习

> [!question] 选择题 1
> 以下哪种场景**不适合**使用 Plotly？
> - [ ] A. Jupyter Notebook 中的交互式数据探索
> - [ ] B. 嵌入 LaTeX 论文的矢量图表
> - [ ] C. 分享给非技术人员的数据报告（HTML）
> - [ ] D. C 程序基准测试的交互式可视化
>
> > [!success]- 点击查看答案
> > > 正确答案: B
> > > **解析**: 虽然 Plotly 可以导出 PDF，但其排版控制不如 Matplotlib 精细。对于 LaTeX 论文这种要求精确字体、行距、边距的场景，Matplotlib 的 `rcParams` 提供像素级控制。Plotly 的设计重点在**屏幕交互**而非出版级排版。

> [!question] 判断题 1
> `fig.write_html('output.html')` 生成的文件包含所有数据和交互逻辑，不需要服务器支持。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > > 答案: 正确
> > > **解析**: Plotly 生成的 HTML 是**纯静态文件**，所有交互功能由浏览器端的 plotly.js 库完成（默认从 CDN 加载）。不需要 Python 服务器、不需要数据库、不需要任何后端——直接用 `file://` 协议打开即可。

---

## 📋 章节测试

### 一、判断题（正确选✅，错误选❌）

> [!question] 判断题 1
> Plotly 图表的核心是 HTML + JavaScript，浏览器负责渲染和数据交互。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > > 答案: 正确
> > > **解析**: Plotly Python 库本质上是一个数据驱动的前端——它将数据转化为 JSON，嵌入基于 plotly.js 的 HTML 模板。图表的渲染、缩放、悬停等交互都由浏览器端的 JavaScript 引擎完成。

> [!question] 判断题 2
> Plotly Express (`px`) 和 `graph_objects` (`go`) 是两个互斥的 API，不能混用。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > > 答案: 错误
> > > **解析**: `px` 生成的 `Figure` 对象与 `go.Figure()` 是同一种类型。你可以用 `px.line()` 创建基础图表，然后用 `fig.add_trace(go.Scatter(...))` 添加更多图层。两者可以无缝混用。

> [!question] 判断题 3
> Plotly 的 `write_html()` 默认包含 plotly.js 库（~3MB），导致生成的 HTML 文件较大。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > > 答案: 错误
> > > **解析**: 默认 `include_plotlyjs='cdn'`，HTML 只包含一个指向 CDN 的 `<script>` 标签（约 100 字节）。如果将 `include_plotlyjs=True`，plotly.js 会被内嵌，文件约 3MB；也可以设为 `'directory'` 让 JS 文件保存在本地目录。

> [!question] 判断题 4
> `px.scatter_3d()` 使用 OpenGL 或 WebGL 在浏览器中渲染。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > > 答案: 正确
> > > **解析**: Plotly 的 3D 图表（`scatter_3d`、`surface`、`mesh3d` 等）在浏览器中使用 WebGL 渲染，利用 GPU 加速。这也是为什么 3D 图表比 2D 消耗更多浏览器资源。

> [!question] 判断题 5
> Plotly 只能在 Python 中使用，没有其他语言的版本。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > > 答案: 错误
> > > **解析**: Plotly 同时支持 Python、R、Julia、MATLAB、JavaScript（plotly.js 是核心引擎）、F# 和 .NET 等多种语言。不同语言生成的图表在交互行为上完全一致。

> [!question] 判断题 6
> `make_subplots(rows=2, cols=1, shared_xaxes=True)` 在 Plotly 中不支持。（ ）
> - [ ] ✅ 正确
> - [ ] ❌ 错误
>
> > [!success]- 点击查看答案
> > > 答案: 错误
> > > **解析**: `make_subplots()` 的 `shared_xaxes=True` 和 `shared_yaxes=True` 参数完全支持。共享后，缩放/平移一个子图时其他子图同步变化。

---

### 二、选择题（单项选择题）

> [!question] 选择题 1
> `go.Scatter` 的 `mode` 参数不能取以下哪个值？
> - [ ] A. `'lines'`
> - [ ] B. `'markers'`
> - [ ] C. `'lines+markers'`
> - [ ] D. `'pie'`
>
> > [!success]- 点击查看答案
> > > 正确答案: D
> > > **解析**: `go.Scatter` 的 `mode` 可取 `'lines'`、`'markers'`、`'lines+markers'`、`'lines+markers+text'`、`'none'`。饼图（pie chart）是独立的 trace 类型：`go.Pie()`，不是 `mode` 的选项。

> [!question] 选择题 2
> Plotly 图表保存为 HTML 后，数据存储的方式是？
> - [ ] A. 数据被存储在外部 CSV 文件中
> - [ ] B. 数据以 JSON 格式嵌入 HTML 的 `<script>` 标签中
> - [ ] C. 数据通过 AJAX 从服务器动态加载
> - [ ] D. 数据以 Base64 编码存储在图片中
>
> > [!success]- 点击查看答案
> > > 正确答案: B
> > > **解析**: Plotly 将所有的数据、布局配置和样式以 JSON 格式嵌入在 HTML 的 `<script type="application/json">` 或直接作为 plotly.js 的 `newPlot()` 参数中。这意味着数据完全自包含，不依赖任何外部资源。

> [!question] 选择题 3
> `fig.update_layout(hovermode='x unified')` 的效果是？
> - [ ] A. 禁止悬停功能
> - [ ] B. 悬停时在同一 X 坐标显示所有 trace 的值
> - [ ] C. 悬停时只显示最近的一个数据点
> - [ ] D. 使用 X 射线模式高亮数据点
>
> > [!success]- 点击查看答案
> > > 正确答案: B
> > > **解析**: `hovermode='x unified'` 在鼠标悬停时，显示一条竖线并同时展示该 X 坐标上所有 trace 的 Y 值（在同一工具提示框中）。`hovermode='x'` 只显示当前 trace 的值，`'closest'` 显示最近数据点的值。

> [!question] 选择题 4
> 将 Plotly 图表嵌入到已有的 HTML 网页中，最好的方式是？
> - [ ] A. 使用 `<iframe>` 嵌入 `write_html()` 生成的文件
> - [ ] B. 使用 `fig.to_html(include_plotlyjs=False, full_html=False)` 获取图表的 HTML 片段
> - [ ] C. 将 `write_html()` 生成的 HTML 内容直接粘贴到目标页面
> - [ ] D. 将图表导出为 PNG 然后用 `<img>` 标签
>
> > [!success]- 点击查看答案
> > > 正确答案: B
> > > **解析**: `to_html()` 可以生成不带完整 HTML 结构（去掉 `<html>`、`<head>`、`<body>`）的图表片段，`include_plotlyjs=False` 避免重复包含 plotly.js。这样你可以将图表片段嵌入自己的网页模板中。

> [!question] 选择题 5
> Plotly 的 `template` 参数（如 `template='plotly_dark'`）控制什么？
> - [ ] A. HTML 文件的整体结构
> - [ ] B. 图表的配色、字体、背景等全局样式
> - [ ] C. 数据存储格式
> - [ ] D. 交互模式
>
> > [!success]- 点击查看答案
> > > 正确答案: B
> > > **解析**: `template` 是 Plotly 的全局样式表，控制图表的配色方案、背景色、字体类型和大小、网格线样式等。内置模板包括 `'plotly'`、`'plotly_white'`、`'plotly_dark'`、`'ggplot2'`、`'seaborn'`、`'simple_white'` 等。

> [!question] 选择题 6
> 与 Matplotlib 相比，Plotly 的一个主要劣势是？
> - [ ] A. 不支持 3D 图表
> - [ ] B. 生成的图片无法用于出版物
> - [ ] C. 绑图代码更复杂
> - [ ] D. 对无头服务器环境的支持较弱（静态导出依赖 kaleido）
>
> > [!success]- 点击查看答案
> > > 正确答案: D
> > > **解析**: Matplotlib 的 Agg 后端在纯命令行环境中开箱即用。Plotly 的静态图片导出依赖 `kaleido` 或 `orca`（已弃用）引擎，增加了部署复杂性。不过 `write_html()` 不依赖任何引擎，可用于纯服务器环境生成 HTML。

---

### 🛠️ 动手练习题

> [!example] 练习题 1：C 程序输出的交互式散点图
> **难度**: ⭐
>
> 编写 C 程序输出 200 个随机点（x, y, category）数据（空格分隔）。用 Plotly Express 生成交互式散点图：
> - X 轴：x，Y 轴：y
> - 颜色：`category` 分类着色
> - 悬停数据：同时显示 x 和 y 的精确值
> - 保存为 HTML 文件
> - 尝试在浏览器中缩放、平移、点击图例控制数据显隐

> [!example] 练习题 2：3D 性能数据可视化
> **难度**: ⭐⭐
>
> 编写 C 程序，模拟多个算法在不同输入规模和数据分布下的性能。输出四列：`algorithm n time memory`。Python 脚本：
> 1. 读取数据到 DataFrame
> 2. 用 `px.scatter_3d(x='n', y='time', z='memory', color='algorithm')` 生成 3D 散点图
> 3. 设置 `log_x=True`、`log_y=True`
> 4. 添加悬停提示（`hover_data`）显示完整的 n/time/memory 三维
> 5. 保存后截图，记录你的旋转角度观察

> [!example] 练习题 3：多面板联动仪表盘
> **难度**: ⭐⭐
>
> 使用 `make_subplots` 创建一个 2×1 的联动面板：
> - 上图：散点图（x vs y），按类别着色
> - 下图：箱线图（y 按类别分组），使用相同的颜色方案
> - 两个图使用 `legendgroup` 实现联动（点击图例切换）
> - 使用 Iris 或你自己生成的模拟数据
> - 保存为 `linked_dashboard.html`

> [!example] 练习题 4：Matplotlib vs Plotly 对比
> **难度**: ⭐⭐
>
> 使用同一份 C 程序生成的基准测试数据（至少包含 input_size 和 time_us 两列），分别用 Matplotlib 和 Plotly 绑制：
> - 折线图（对数坐标）
> - 散点图（带颜色映射的时间渐变）
> - 柱状图（三种不同数据规模的对比）
>
> 总结两者在代码量、图表美观度、交互性、文件大小方面的差异。
