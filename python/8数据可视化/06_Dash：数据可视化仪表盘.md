# Dash：数据可视化仪表盘 (Dash: Data Visualization Dashboards)

---

## 章节概述

Dash 是 Plotly 团队开发的纯 Python 数据可视化仪表盘框架。无需编写 HTML/JavaScript，纯 Python 即可构建交互式 Web 仪表盘。适合数据分析师、量化交易员、科研人员快速构建数据看板。

> **C 程序员视角**：如果 Flask 是 Web 的 printf，那 Dash 就是 Web 的 matplotlib——声明式地描述"我要什么图"，框架负责渲染和交互。

---

## 1. 安装与入门

```bash
pip install dash
```

```python
# app.py
import dash
from dash import html, dcc
import plotly.express as px
import pandas as pd

app = dash.Dash(__name__)

df = pd.DataFrame({
    'x': [1, 2, 3, 4, 5],
    'y': [10, 25, 18, 32, 22],
    'label': ['A', 'B', 'C', 'D', 'E']
})

app.layout = html.Div([
    html.H1("我的第一个 Dash 仪表盘"),
    dcc.Graph(
        figure=px.scatter(df, x='x', y='y', color='label', title="散点图")
    )
])

if __name__ == '__main__':
    app.run(debug=True)
# 访问 http://127.0.0.1:8050/
```

---

## 2. 布局组件

```python
from dash import html, dcc

app.layout = html.Div([
    # 标题
    html.H1("数据看板", style={'textAlign': 'center'}),

    # 下拉选择器
    dcc.Dropdown(
        id='metric-selector',
        options=[
            {'label': '销售额', 'value': 'sales'},
            {'label': '利润', 'value': 'profit'},
        ],
        value='sales'
    ),

    # 日期范围选择
    dcc.DatePickerRange(
        id='date-range',
        start_date_placeholder_text="开始日期",
        end_date_placeholder_text="结束日期"
    ),

    # 滑块
    dcc.Slider(min=0, max=100, step=5, value=50, marks={i: str(i) for i in range(0, 101, 20)}),

    # 图表
    dcc.Graph(id='main-chart'),

    # 刷新按钮
    html.Button('刷新数据', id='refresh-btn', n_clicks=0),

    # 定时器（自动刷新）
    dcc.Interval(id='interval', interval=5000, n_intervals=0)
])
```

---

## 3. 回调交互

```python
from dash import Input, Output, State, callback

# 基础回调：下拉框选择 → 更新图表
@callback(
    Output('main-chart', 'figure'),
    Input('metric-selector', 'value')
)
def update_chart(metric):
    fig = px.bar(df, x='category', y=metric, title=f"{metric} 分布")
    return fig

# 多输入回调
@callback(
    Output('main-chart', 'figure'),
    Input('metric-selector', 'value'),
    Input('date-range', 'start_date'),
    Input('date-range', 'end_date')
)
def update_chart_with_date(metric, start_date, end_date):
    filtered = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    return px.bar(filtered, x='category', y=metric)

# 按钮回调（使用 State 避免循环触发）
@callback(
    Output('output', 'children'),
    Input('refresh-btn', 'n_clicks'),
    State('metric-selector', 'value')
)
def refresh_data(n_clicks, metric):
    if n_clicks == 0:
        return "点击刷新按钮加载数据"
    return f"已刷新 {metric} 数据（第 {n_clicks} 次）"
```

---

## 4. 多页面应用

```python
from dash import Dash, html, dcc
from dash.dependencies import Input, Output

app = Dash(__name__, use_pages=True)

app.layout = html.Div([
    html.H1("多页面仪表盘"),
    # 导航
    dcc.Link("概览", href="/"), html.Span(" | "),
    dcc.Link("详细数据", href="/details"), html.Span(" | "),
    dcc.Link("设置", href="/settings"),
    # 页面内容
    dash.page_container
])
```

```python
# pages/overview.py
import dash
from dash import html, dcc
import plotly.express as px

dash.register_page(__name__, path='/', name='概览')

def layout():
    return html.Div([
        html.H2("概览页面"),
        dcc.Graph(figure=px.line(df, x='date', y='value'))
    ])
```

---

## 5. 实时数据更新

```python
from dash import Input, Output
from dash.dependencies import clientside_callback

# 服务端回调（定时器触发）
@callback(
    Output('live-chart', 'figure'),
    Input('interval', 'n_intervals')
)
def update_live_chart(n):
    # 从数据库/API 获取最新数据
    new_data = fetch_latest_data()
    return px.line(new_data, x='time', y='value')

# 客户端回调（JavaScript 执行，减少服务器负载）
clientside_callback("""
    function(n_intervals) {
        return fetch('/api/latest-data')
            .then(r => r.json())
            .then(data => ({
                data: [{x: data.time, y: data.value, type: 'scatter'}],
                layout: {title: '实时数据'}
            }));
    }
""", Output('live-chart', 'figure'), Input('interval', 'n_intervals'))
```

---

## 6. 部署

```bash
# 开发环境
python app.py

# 生产环境（gunicorn）
pip install gunicorn
gunicorn app:server -b 0.0.0.0:8050 -w 4

# Docker
FROM python:3.12
WORKDIR /app
COPY . .
RUN pip install dash pandas plotly gunicorn
CMD ["gunicorn", "app:server", "-b", "0.0.0.0:8050"]
```

---

## 7. 常用图表类型

```python
import plotly.express as px
import plotly.graph_objects as go

# 散点图
px.scatter(df, x='x', y='y', color='category')

# 折线图
px.line(df, x='date', y='value', color='series')

# 柱状图
px.bar(df, x='category', y='count', color='group')

# 饼图
px.pie(df, names='category', values='count')

# 热力图
px.density_heatmap(df, x='x', y='y', z='value')

# 3D 散点
px.scatter_3d(df, x='x', y='y', z='z', color='category')

# 地理图
px.choropleth(df, locations='country', color='value', hover_name='country')

# 树状图
px.treemap(df, path=['region', 'category'], values='sales')
```

---

## 速查卡片

| 需求 | 命令/代码 |
|------|----------|
| 安装 | `pip install dash` |
| 创建应用 | `app = dash.Dash(__name__)` |
| 布局 | `app.layout = html.Div([...])` |
| 回调 | `@callback(Output(...), Input(...))` |
| 启动 | `app.run(debug=True)` |
| 访问 | `http://127.0.0.1:8050/` |
| 生产部署 | `gunicorn app:server -b 0.0.0.0:8050` |
