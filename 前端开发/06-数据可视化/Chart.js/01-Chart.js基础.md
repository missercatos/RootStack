# Chart.js 基础

> Chart.js 是最轻量的主流 canvas 图表库：一个 config 对象，
> 一行 new Chart，就能得到带动画、tooltip、图例的完整图表。

---

## 1. 定位：上手最快的图表库

Chart.js 的核心卖点是"简单"：

- **轻量**：gzip 后约 70KB，比 ECharts 小一半以上
- **canvas 渲染**：性能稳定，不产生大量 DOM 节点
- **八种内建图表**覆盖 90% 的业务报表需求
- **响应式**：自动跟随容器尺寸重绘
- **零配置可用**：默认样式已经相当好看

适用场景判断：

| 场景                       | 是否适合 Chart.js |
|----------------------------|-------------------|
| 后台管理系统的常规报表      | 非常适合          |
| 移动端 H5 简单图表          | 适合              |
| 复杂大屏（地图/3D/K线）     | 不适合，用 ECharts |
| 金融级专业图表              | 不适合，用 Highcharts |

与 ECharts 的对比详见章末及
[[前端开发/06-数据可视化/ECharts/01-ECharts基础|ECharts 基础]]。

---

## 2. 安装

### CDN 引入（推荐入门）

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
</head>
<body>
</body>
</html>
```

### npm 安装（工程化项目）

```bash
npm install chart.js
```

```js
import { Chart, registerables } from 'chart.js';
// v4 需要 register 组件后才能使用（支持 tree-shaking 按需引入）
Chart.register(...registerables);

import Chart from 'chart.js/auto';   // 或者一行引入全部，最省事
```

v4 的按需注册示例（追求体积时）：

```js
import {
  Chart, LineController, LineElement, PointElement,
  LinearScale, CategoryScale, Tooltip, Legend
} from 'chart.js';

Chart.register(
  LineController, LineElement, PointElement,
  LinearScale, CategoryScale, Tooltip, Legend
);
```

---

## 3. 第一个折线图：最小结构

`new Chart(ctx, config)` 只需要两样东西：
画布上下文和一个 config 对象。config 的最小骨架是
`type` + `data.labels` + `data.datasets`。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <title>第一个 Chart.js 图表</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
  <style>
    .chart-box {
      position: relative;     /* 响应式必需，见下文 */
      width: 600px;
      height: 360px;
    }
  </style>
</head>
<body>

<div class="chart-box">
  <canvas id="myChart"></canvas>
</div>

<script>
  const ctx = document.getElementById('myChart');

  new Chart(ctx, {
    type: 'line',                          // 图表类型
    data: {
      labels: ['一月', '二月', '三月', '四月', '五月', '六月'],
      datasets: [{
        label: '月销量',
        data: [320, 450, 280, 520, 410, 600]
      }]
    }
  });
</script>

</body>
</html>
```

逐项拆解：

| 配置                  | 含义                                        |
|-----------------------|---------------------------------------------|
| `type: 'line'`        | 决定渲染成什么图                             |
| `labels`              | X 轴的类目序列                              |
| `datasets[].label`    | 系列名，出现在图例和 tooltip 中              |
| `datasets[].data`     | 与 labels 一一对应的数值数组                |

多系列就是往 datasets 里加对象：

```js
datasets: [
  { label: '2025 年', data: [320, 450, 280, 520, 410, 600] },
  { label: '2026 年', data: [380, 420, 350, 560, 480, 650] }
]
```

---

## 4. canvas 相关注意事项

### 4.1 devicePixelRatio 与清晰度

canvas 默认按 CSS 尺寸渲染，高分屏上会模糊。
Chart.js 会读取 `window.devicePixelRatio` 自动放大画布内部分辨率，
通常无需干预。但两种情况要手动处理：

```js
new Chart(ctx, {
  type: 'bar',
  data,
  options: {
    // 导出图片模糊时提高此值；默认取设备值
    devicePixelRatio: window.devicePixelRatio || 2
  }
});
```

另外注意：**不要在 CSS 里把 canvas 设固定宽高**，
那会干扰库的响应式计算。让容器控制大小即可。

### 4.2 maintainAspectRatio 与容器高度配合

这是新手第一大坑。默认 `maintainAspectRatio: true`
会让图表保持 2:1 宽高比，你给容器设的高度经常被无视：

```js
options: {
  responsive: true,
  maintainAspectRatio: false   // 高度完全交给父容器决定
}
```

配套要求：**父容器必须有确定的高度，且 position: relative**：

```css
.chart-box {
  position: relative;
  height: 360px;        /* 或 flex/grid 分配的高度 */
}
```

记住这个组合拳，90% 的"图表高度不生效"问题就此解决。

---

## 5. 八种内建图表速览

改一个 `type` 就能换图表类型（部分数据结构略有差异）：

| type       | 名称     | 数据形态            | 典型用途           |
|------------|----------|---------------------|--------------------|
| line       | 折线图   | 数值数组            | 趋势               |
| bar        | 柱状图   | 数值数组            | 对比               |
| pie        | 饼图     | 数值数组（自动占比）| 构成               |
| doughnut   | 环形图   | 同饼图              | 构成（更现代）     |
| radar      | 雷达图   | 数值数组            | 多维能力对比       |
| scatter    | 散点图   | `{x, y}` 对象数组   | 相关性             |
| bubble     | 气泡图   | `{x, y, r}`         | 三维关系           |
| area       | 面积图   | line + fill         | 趋势+体量          |

注意 scatter/bubble 的数据不是纯数字：

```js
{
  type: 'scatter',
  data: {
    datasets: [{
      label: '样本',
      data: [
        { x: 12, y: 8 },
        { x: 20, y: 15 },
        { x: 33, y: 9 }
      ]
    }]
  }
}
```

area 不是独立类型，而是折线的填充模式：

```js
{
  type: 'line',
  data,
  options: {
    elements: {
      line: { fill: true },           // 开启填充
      point: { radius: 0 }
    }
  }
}
```

---

## 6. 全局默认配置 Chart.defaults

所有图表共享的样式，设置一次全局生效，避免每张图重复配置：

```js
// 字体与颜色
Chart.defaults.font.family = "'Helvetica Neue', 'PingFang SC', sans-serif";
Chart.defaults.font.size = 13;
Chart.defaults.color = '#555';

// 全局主题色系（按 series 顺序取用）
Chart.defaults.plugins.colors.enabled = true;

// 交互行为
Chart.defaults.interaction.mode = 'index';
Chart.defaults.interaction.intersect = false;

// 关闭动画（大量图表的报表页可提升性能）
// Chart.defaults.animation = false;
```

常用 defaults 一览：

| 配置路径                        | 作用                       |
|---------------------------------|----------------------------|
| `font.family / size / weight`   | 全局字体                   |
| `color`                         | 全局文字颜色               |
| `borderColor`                   | 默认边框色                 |
| `plugins.legend.position`       | 图例默认位置               |
| `interaction.mode`              | tooltip 命中模式           |

---

## 7. 实战：月度销售折线 + 柱状

一个页面两张图：折线看趋势，柱状看对比。
完整可运行单文件：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<title>月度销售报表</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>
  body {
    font-family: sans-serif;
    background: #f0f2f5;
    margin: 0;
    padding: 24px;
  }
  h1 { font-size: 20px; color: #333; }
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
    gap: 20px;
  }
  .card {
    background: #fff;
    border-radius: 10px;
    padding: 18px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, .08);
  }
  /* 响应式铁三角：relative 父容器 + 固定高度 + maintainAspectRatio:false */
  .chart-box {
    position: relative;
    height: 340px;
  }
</style>
</head>
<body>

<h1>2026 年上半年销售概览</h1>

<div class="grid">
  <div class="card">
    <div class="chart-box"><canvas id="trend"></canvas></div>
  </div>
  <div class="card">
    <div class="chart-box"><canvas id="compare"></canvas></div>
  </div>
</div>

<script>
  // 全局默认
  Chart.defaults.font.family = "sans-serif";
  Chart.defaults.color = '#666';

  const labels = ['一月', '二月', '三月', '四月', '五月', '六月'];
  const sales2025 = [320, 450, 280, 520, 410, 600];
  const sales2026 = [380, 420, 350, 560, 480, 650];

  // 折线图：两年趋势对比
  new Chart(document.getElementById('trend'), {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: '2026 年销量',
          data: sales2026,
          borderColor: '#3498db',
          backgroundColor: 'rgba(52, 152, 219, .12)',
          fill: true,
          tension: 0.35            // 平滑度 0~1
        },
        {
          label: '2025 年销量',
          data: sales2025,
          borderColor: '#bdc3c7',
          borderDash: [6, 4],      // 虚线区分去年
          tension: 0.35
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false }
    }
  });

  // 柱状图：同比分组对比
  new Chart(document.getElementById('compare'), {
    type: 'bar',
    data: {
      labels,
      datasets: [
        { label: '2025 年', data: sales2025, backgroundColor: '#95a5a6' },
        { label: '2026 年', data: sales2026, backgroundColor: '#3498db' }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { beginAtZero: true }     // Y 轴从零开始更客观
      }
    }
  });
</script>

</body>
</html>
```

本例引入的新配置：

| 配置                  | 说明                                     |
|-----------------------|------------------------------------------|
| `tension`             | 折线平滑度，0 是直线                     |
| `borderDash`          | 虚线边框                                 |
| `fill`                | 折线下方是否填充                         |
| `beginAtZero`         | Y 轴从 0 开始                            |
| `interaction.mode`    | index 模式让 tooltip 对齐整列            |

---

## 小结

- 最小结构 = type + data.labels + data.datasets，三行起一张图。
- canvas 清晰度交给 devicePixelRatio，导出模糊时手动调高。
- 响应式铁律：父容器 relative + 定高 + maintainAspectRatio: false。
- 八种内建图覆盖常规报表；area 是 line 的填充模式而非独立类型。
- 全局样式进 Chart.defaults，单图特例进 options。

下一篇深入配置体系：
[[前端开发/06-数据可视化/Chart.js/02-图表类型与配置|图表类型与配置]]
