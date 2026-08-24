# Highcharts 基础

> 老牌商业图表库：文档与示例质量业界第一，金融时间序列能力最强。
> 个人学习与非商用免费，商用需授权——先看清楚协议再上生产。

---

## 1. 定位

Highcharts 2009 年发布，比 Chart.js 与 ECharts 都早，
长期服务于金融、政企等高要求场景：

- **文档范例之王**：官网 demo 覆盖几乎所有 imaginable 的配置组合，
  每个 demo 都带完整可改的源码。
- **金融图表强**：Highstock 子产品内置范围选择器、navigator、
  十字光标、数据分组（dataGrouping），做行情图几乎零成本。
- **兼容性极好**：老浏览器支持历史包袱处理得最完善。
- **商业授权**：个人/非商用免费；商用需购买 license。

与另外两库的关系：
- 比 Chart.js 功能全得多，尤其时间轴与导出；
- 与 ECharts 同为全能型，但 option 风格更"扁平"。

---

## 2. CDN 引入与第一个图

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<script src="https://code.highcharts.com/highcharts.js"></script>
</head>
<body>

<div id="container"></div>

<script>
  Highcharts.chart('container', {
    title: { text: '月度销量' },
    series: [{
      name: '销量',
      data: [320, 450, 280, 520, 410, 600]
    }]
  });
</script>

</body>
</html>
```

注意最小结构有多小：没有 xAxis.data、没有 type——
Highcharts 会自动推断。容器同样必须有宽高
（默认自动占满父级宽度，高度默认 400px）。

### 与 ECharts option 结构相似性对照

两者都是"一个大对象描述一切"，逐块对照着学最快：

| 概念       | Highcharts            | ECharts                  |
|------------|-----------------------|---------------------------|
| 图表类型   | `chart.type`          | `series[].type`           |
| 数据       | `series[].data`       | `series[].data` / dataset |
| 标题       | `title.text`          | `title.text`              |
| 提示框     | `tooltip`             | `tooltip`                 |
| X 轴类目   | `xAxis.categories`    | `xAxis.data`              |
| 图例       | `legend`              | `legend`                  |

最大心智差异：Highcharts 把"类型"放在 chart 全局层，
ECharts 放在每个系列上（所以 ECharts 做混合图天然方便）。

---

## 3. 核心结构详解

```js
Highcharts.chart('container', {

  chart: {
    type: 'column',            // line/column/pie/area/spline...
    height: 400,
    zoomType: 'x'              // 框选缩放方向，金融页常开
  },

  title: { text: '销售趋势' },
  subtitle: { text: '2026 年' },

  xAxis: {
    categories: ['一月', '二月', '三月', '四月', '五月', '六月'],
    crosshair: true            // 悬停十字线
  },
  yAxis: {
    title: { text: '万元' }
  },

  tooltip: {
    shared: true,               // 多系列合并到一个提示框
    valueSuffix: ' 万元'
  },

  legend: { layout: 'vertical', align: 'right', verticalAlign: 'middle' },

  credits: { enabled: false }, // 版权水印，见下节

  series: [
    { name: '线上', data: [120, 200, 150, 230, 260, 300] },
    { name: '线下', data: [90, 140, 120, 180, 200, 240] }
  ]
});
```

### credits 版权注意

Highcharts 免费版会在右下角渲染 "Highcharts.com" 水印：

```js
credits: { enabled: false }     // 关闭
// 或保留并自定义文字链接
credits: { text: '数据来源：内部系统', href: '#' }
```

合规要点：关闭水印不等于获得商用权——
**商用部署仍需购买 license**，这是三库里唯一双协议收费的。

---

## 4. 常用图表速做

### 折线（含平滑）

```js
{ name: '温度', type: 'spline', data: [7.0, 6.9, 9.5, 14.5] }
```

`spline` 即平滑折线，`line` 是直线连接。

### 柱状

```js
chart: { type: 'column' },      // 纵向
chart: { type: 'bar' },         // 横向条形
```

### 饼图

```js
{
  chart: { type: 'pie' },
  series: [{
    name: '渠道占比',
    data: [
      { name: '直营', y: 420 },
      { name: '电商', y: 350 },
      { name: '分销', y: 280 }
    ]
  }]
}
```

饼图数据用 `{name, y}` 对象形态，label 自动带百分比。
环形图加 `plotOptions.pie.innerSize: '60%'`。

---

## 5. 亮点：datetime 时间轴自动格式化

Highcharts 对时间序列的支持是三库中最省心的——
数据直接给 `[时间戳, 值]`，轴刻度、跨年跨月标签全自动：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<script src="https://code.highcharts.com/highcharts.js"></script>
</head>
<body>

<div id="ts" style="max-width: 800px; margin: auto"></div>

<script>
  // 生成 30 天的日活数据
  const day = 24 * 3600 * 1000;
  const now = Date.now();
  const data = Array.from({ length: 30 }, (_, i) => {
    return [now - (29 - i) * day,
            Math.round(8000 + Math.sin(i / 3) * 1500 + i * 60)];
  });

  Highcharts.chart('ts', {
    title: { text: '近 30 日活跃用户' },
    chart: { zoomType: 'x' },

    xAxis: {
      type: 'datetime',              // 关键：时间轴
      title: { text: null }
    },
    yAxis: { title: { text: 'DAU' } },

    tooltip: {
      shared: true,
      xDateFormat: '%Y-%m-%d %A'     // 提示框日期格式
    },

    series: [{
      name: 'DAU',
      data                            // [timestamp, value] 数组
    }]
  });
</script>

</body>
</html>
```

自动化的部分：
- 刻度按数据跨度智能选单位（小时/天/月），
- 缩放到不同粒度时标签自动切换格式，
- 不需要任何"格式化函数"，开箱即得。

对比 ECharts 的 time 轴：能力相当，
但 Highcharts 连 tooltip 的星期几都帮你本地化好了。

---

## 6. 导出功能内置

`exporting` 模块让每张图自带下载菜单（PNG/JPEG/PDF/SVG/CSV）：

```html
<script src="https://code.highcharts.com/modules/exporting.js"></script>
<script src="https://code.highcharts.com/modules/export-data.js"></script>
```

```js
exporting: {
  enabled: true,
  filename: 'sales-report',
  buttons: {
    contextButton: {
      menuItems: ['downloadPNG', 'downloadCSV']   // 精简菜单
    }
  }
}
```

Chart.js 需要自己写 toBase64Image + a 标签的导出逻辑
（见 [[前端开发/06-数据可视化/Chart.js/03-Chart.js实战|Chart.js 实战]]），
Highcharts 一个模块搞定还附赠 CSV。

---

## 7. 实战：股价走势（datetime + rangeSelector）

rangeSelector 属于 Highstock 能力，但普通引入 stock 模块即可使用：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<script src="https://code.highcharts.com/stock/highstock.js"></script>
<script src="https://code.highcharts.com/stock/modules/exporting.js"></script>
</head>
<body>

<div id="stock" style="height: 480px; max-width: 900px; margin: auto"></div>

<script>
  // 模拟一年日收盘价
  function genSeries(n, startPrice) {
    let price = startPrice;
    const out = [];
    const day = 24 * 3600 * 1000;
    for (let i = n; i >= 0; i--) {
      price += (Math.random() - 0.48) * 2.5;
      out.push([Date.now() - i * day, +price.toFixed(2)]);
    }
    return out;
  }

  Highcharts.stockChart('stock', {
    title: { text: 'DEMO 股价走势' },

    rangeSelector: {                 // 左上角范围按钮组
      buttons: [
        { type: 'month', count: 1, text: '1月' },
        { type: 'month', count: 3, text: '3月' },
        { type: 'year',  count: 1, text: '1年' },
        { type: 'all',          text: '全部' }
      ],
      selected: 1                    // 默认选中第 2 个按钮
    },

    yAxis: {
      title: { text: '价格（元）' },
      labels: { format: '{value:.2f}' }
    },

    plotOptions: {
      area: { fillColor: {
        linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
        stops: [
          [0, 'rgba(46, 204, 113, .35)'],
          [1, 'rgba(46, 204, 113, 0)']
        ]
      } }
    },

    series: [{
      name: '收盘价',
      type: 'area',
      data: genSeries(365, 120),
      tooltip: { valueDecimals: 2 }
    }]
  });
</script>

</body>
</html>
```

这个 demo 里 Highcharts 免费送了什么：
1. **rangeSelector 快捷范围**：点一下切 1 月/3 月/1 年。
2. **navigator 底部缩略图**：拖动选窗口（下一章细讲）。
3. **dataGrouping**：缩到"1 年"视图时自动按周聚合，
   放大回"1 月"恢复日线——性能与可读性兼得。
4. datetime 轴 + 渐变面积 + 十字光标全套默认开启。

同样的效果在 ECharts 里需要手配 dataZoom + 主副图 +
聚合策略（参考 [[前端开发/06-数据可视化/ECharts/02-高级图表|ECharts 高级图表]] 的 K 线实战），
工作量差一个量级。金融时间序列选 Highcharts 的理由就在这。

---

## 小结

- `Highcharts.chart(el, options)` 最小结构只需一个 series.data。
- 类型在 chart.type 全局声明；对照 ECharts 记忆效率最高。
- credits 可关但商用必须买 license，双协议是硬约束。
- datetime 轴吃时间戳数组，刻度与格式化全自动。
- exporting 模块一行配置自带 PNG/CSV 导出。
