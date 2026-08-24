# ECharts 实战

> 综合实战：1920 设计稿的数据监控大屏。六宫格布局、五类图表、
> 实时数据推送模拟、数字翻牌器，以及 Vue3 集成的生命周期管理。

---

## 1. 大屏适配：scale 等比缩放方案

大屏通常按 1920x1080 设计稿开发，但要投在不同分辨率的屏幕上。
两种主流方案：

| 方案         | 原理                       | 优缺点                     |
|--------------|----------------------------|----------------------------|
| scale 等比缩放 | 整个画布 transform: scale | 还原度 100%，但文字被拉伸模糊风险 |
| rem 方案     | 根字号随宽度变化           | 文字清晰，但需全站用 rem   |

大屏场景推荐 **scale 方案**——设计稿还原最省心：

```js
function fitScreen(designWidth = 1920, designHeight = 1080) {
  const stage = document.getElementById('stage');
  const scaleX = window.innerWidth / designWidth;
  const scaleY = window.innerHeight / designHeight;
  // 统一取 min 保持宽高比，多余部分居中留黑边
  const scale = Math.min(scaleX, scaleY);
  stage.style.transform =
    `translate(-50%, -50%) scale(${scale})`;
}

window.addEventListener('resize', fitScreen);
fitScreen();
```

```css
#stage {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 1920px;
  height: 1080px;
  transform-origin: center center;   /* 配合 translate 居中 */
}
```

注意两点：
- **所有图表容器尺寸在缩放前就确定**（写死 px），ECharts 按原始
  尺寸渲染再被整体放大，不需要 resize。
- 若追求极致清晰可改 rem 方案，代价是所有间距字号都要换算。

---

## 2. Grid 六宫格布局

```css
.stage-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: repeat(2, 1fr);
  gap: 16px;
  padding: 16px;
  height: calc(100% - 64px);       /* 减去标题栏 */
}
.g-main   { grid-column: span 2; } /* 中间主图占两格 */
```

```html
<div id="stage">
  <header class="bar">销售监控大屏</header>
  <div class="stage-grid">
    <div class="panel"><div id="kline" class="chart"></div></div>
    <div class="panel g-main"><div id="map" class="chart"></div></div>
    <div class="panel"><div id="pie" class="chart"></div></div>
    <div class="panel"><div id="heat" class="chart"></div></div>
    <div class="panel"><div id="counter"></div></div>
    <div class="panel"><div id="realtime" class="chart"></div></div>
  </div>
</div>
```

六格分配：K线 / 地图散点(占2格) / 饼图 / 热力 / 翻牌器 / 实时折线。

---

## 3. 五个图表的初始化

统一封装创建函数，集中管理实例便于销毁与轮播：

```js
const charts = {};

function createChart(id, option) {
  const el = document.getElementById(id);
  const chart = echarts.init(el, 'dark');
  chart.setOption(option);
  charts[id] = chart;

  // 大屏 scale 方案下无需 ResizeObserver，
  // 但若改用 rem 方案则必须加：
  new ResizeObserver(() => chart.resize()).observe(el);
  return chart;
}

// K 线 + 成交量（结构同上一章实战，此处省略 option 细节）
createChart('kline', klineOption);

// 地图散点占位：geo 组件 + effectScatter
createChart('map', {
  backgroundColor: 'transparent',
  geo: {
    map: 'china',                  // 需注册地图 JSON
    roam: false,
    itemStyle: { areaColor: '#12233f', borderColor: '#2c4a7c' }
  },
  series: [{
    type: 'effectScatter',
    coordinateSystem: 'geo',
    symbolSize: 10,
    rippleEffect: { scale: 3.5 },
    data: [
      { name: '深圳', value: [114.05, 22.55, 820] },
      { name: '上海', value: [121.47, 31.23, 640] },
      { name: '北京', value: [116.40, 39.90, 590] }
    ]
  }]
});

// 渠道占比玫瑰图
createChart('pie', {
  backgroundColor: 'transparent',
  series: [{
    type: 'pie',
    radius: ['25%', '65%'],
    roseType: 'area',
    data: [
      { value: 420, name: '直营' },
      { value: 350, name: '电商' },
      { value: 280, name: '分销' }
    ]
  }]
});

// 时段 x 品类热力
createChart('heat', {
  backgroundColor: 'transparent',
  tooltip: { position: 'inside' },
  grid: { left: 60, bottom: 40 },
  xAxis: { type: 'category', data: ['周一','周三','周五','周日'] },
  yAxis: { type: 'category', data: ['A 类', 'B 类', 'C 类'] },
  visualMap: { min: 0, max: 100, calculable: true,
               orient: 'horizontal', left: 'center', bottom: 0 },
  series: [{
    type: 'heatmap',
    data: [[0,0,52],[0,1,30],[1,2,88],[2,0,45],[2,1,66],[3,2,72]]
  }]
});

// 实时折线（初始为空，靠定时推送）
const rtChart = createChart('realtime', {
  backgroundColor: 'transparent',
  xAxis: { type: 'category', data: [] },
  yAxis: { type: 'value', scale: true },
  series: [{ type: 'line', showSymbol: false,
             areaStyle: { opacity: .2 }, data: [] }]
});

---

## 4. 实时折线：定时 setOption 模拟 WebSocket

真实项目里数据来自 WebSocket 推送；演示环境用定时器模拟同样的
"增量到达"模式：

```js
let tick = 0;
const MAX_POINTS = 30;               // 窗口内最多保留 30 个点

setInterval(() => {
  const value = +(400 + Math.sin(tick / 4) * 60 +
                  Math.random() * 40).toFixed(1);
  const time = new Date().toLocaleTimeString('zh-CN', { hour12: false });

  const opt = rtChart.getOption();
  const xData = opt.xAxis[0].data.concat(time);
  const yData = opt.series[0].data.concat(value);

  // 超出窗口就丢弃最旧的
  if (xData.length > MAX_POINTS) { xData.shift(); yData.shift(); }

  rtChart.setOption({ xAxis: { data: xData },
                      series: [{ data: yData }] });
  tick++;
}, 2000);
```

要点：
- **增量合并 setOption**：只传新增的数据数组。
- 维护固定长度滑动窗口，防止长时间运行后内存与渲染压力增长。
- 真实 WebSocket 版本只需把 setInterval 回调换成 `ws.onmessage`。

---

## 5. 数字翻牌器：原生 JS 实现

大屏顶部的核心指标常用"数字滚动"效果，原理是 rAF 补间：

```html
<div id="counter" class="counter">
  <span class="label">今日总销售额</span>
  <div class="digits"></div>
</div>

<style>
.counter { text-align: center; }
.digits { font-size: 44px; font-weight: bold; color: #ffd04b;
          font-variant-numeric: tabular-nums; }
</style>

<script>
function countUp(el, target, duration = 1200) {
  const startVal = parseFloat(el.textContent.replace(/,/g, '')) || 0;
  const startTime = performance.now();

  function frame(now) {
    const t = Math.min((now - startTime) / duration, 1);
    const eased = 1 - Math.pow(1 - t, 3);          // easeOutCubic
    const current = startVal + (target - startVal) * eased;
    el.textContent = current.toLocaleString('zh-CN',
                                           { maximumFractionDigits: 0 });
    if (t < 1) requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}

const digitsEl = document.querySelector('#counter .digits');
countUp(digitsEl, 482000);

// 每 10 秒随机推高一次，模拟实时总额
setInterval(() => {
  countUp(digitsEl, 482000 + Math.round(Math.random() * 5000));
}, 10000);
</script>
```

实现拆解：
1. **rAF + 缓动函数**从当前值补间到目标值，而不是瞬间跳变。
2. `toLocaleString` 加千分位；`tabular-nums` 保证数字等宽不跳动。
3. 反复调用 countUp 时以当前显示值为起点，天然支持连续推送。

---

## 6. loading 与空数据态处理

大屏数据源多、失败概率高，每个面板都要有降级表现：

```js
// 创建前显示 loading
chart.showLoading({
  text: '加载中...',
  color: '#4e9dd6',
  maskColor: 'rgba(13, 20, 36, .6)'
});

fetch(url)
  .then(r => r.json())
  .then(data => {
    chart.hideLoading();
    if (!data || !data.length) {
      showEmpty(chart);              // 空态
      return;
    }
    chart.setOption(buildOption(data));
  })
  .catch(() => {
    chart.hideLoading();
    showError(chart);
  });

function showEmpty(chart) {
  chart.clear();
  chart.setOption({
    title: {
      text: '暂无数据',
      left: 'center', top: 'middle',
      textStyle: { color: '#5a6a8a', fontSize: 14, fontWeight: 'normal' }
    }
  });
}
function showError(chart) {
  chart.clear();
  chart.setOption({
    title: {
      text: '加载失败，将自动重试',
      left: 'center', top: 'middle',
      textStyle: { color: '#c0392b', fontSize: 14, fontWeight: 'normal' }
    }
  });
  setTimeout(() => loadPanel(), 5000);   // 自动重试
}
```

三态齐全（loading / empty / error）是大屏可用性的底线，
尤其空数据态——新装环境的系统最容易在这里露出白板。

---

## 7. Vue3 中集成：生命周期管理与内存泄漏警告

### 方式一：vue-echarts 组件库

```bash
npm install echarts vue-echarts
```

```vue
<script setup>
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { BarChart } from 'echarts/charts';
import { GridComponent, TooltipComponent } from 'echarts/components';
import VChart from 'vue-echarts';

use([CanvasRenderer, BarChart, GridComponent, TooltipComponent]);
</script>

<template>
  <VChart :option="option" autoresize style="height: 320px" />
</template>
```

组件库内部已处理好挂载、更新与卸载，推荐优先使用。

### 方式二：手动集成（理解生命周期）

```vue
<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import * as echarts from 'echarts';

const el = ref(null);
let chart = null;
let ro = null;

onMounted(() => {
  chart = echarts.init(el.value);
  chart.setOption(props.option);
  ro = new ResizeObserver(() => chart.resize());
  ro.observe(el.value);
});

// 数据变化时增量更新
function update(option) {
  chart && chart.setOption(option);
}

onBeforeUnmount(() => {
  ro && ro.disconnect();
  chart && chart.dispose();       // 忘记 dispose = 内存泄漏
  chart = null;
});
</script>

<template><div ref="el" style="height: 320px"></div></template>
```

**内存泄漏警告**：Vue 的 keep-alive、路由复用都会让组件反复挂载，
每次 onMounted 都会 init 一个新实例。不 dispose 的后果：
canvas 引用、事件监听、ResizeObserver 全部残留，
切换十次页面就是十个僵尸实例。

---

## 8. 打包按需优化

大屏通常只用到五六个系列，按需引入收益巨大：

```js
// echarts/use.js —— 集中注册，全局唯一入口
import * as echarts from 'echarts/core';
import { LineChart, BarChart, PieChart, HeatmapChart,
         CandlestickChart, EffectScatterChart } from 'echarts/charts';
import { GridComponent, TooltipComponent, LegendComponent,
         TitleComponent, GeoComponent, VisualMapComponent,
         DataZoomComponent, MarkLineComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';

echarts.use([
  LineChart, BarChart, PieChart, HeatmapChart,
  CandlestickChart, EffectScatterChart,
  GridComponent, TooltipComponent, LegendComponent,
  TitleComponent, GeoComponent, VisualMapComponent,
  DataZoomComponent, MarkLineComponent,
  CanvasRenderer
]);

export default echarts;
```

配合构建工具的 tree-shaking，体积可从约 1MB 压到 400KB 左右；
再上 gzip 后传输体积约为十分之一。

---

## 9. 与 Java 后端的数据接口约定

前端图表需要的是"聚合好的结构化数据"，与
[[java/3工程化/15_全栈开发技巧|Java 后端]]
协作时接口形态有两种流派：

| 形态             | 说明                           | 适用                     |
|------------------|--------------------------------|--------------------------|
| 聚合接口         | 后端直接返回 option 可用的结构 | 大屏、报表等展示型场景   |
| 明细前端算       | 后端给原始明细，前端 reduce    | 分析型页面、维度多变场景 |

约定建议：
1. **大屏走聚合接口**：一个面板一个接口或一个大接口分 key 返回，
   后端 SQL/缓存算好，前端零计算、首屏快。
2. **字段名与 ECharts 结构对齐**：如 `{ categories: [...], values: [...] }`，
   前端一行 map 就能进 series。
3. **时间统一毫秒时间戳**，格式化交给前端，避免时区歧义。
4. **空数据返回空数组而非 null**，减少前端判空分支。
5. 明细量超过几千行时坚持后端聚合——把 group by 交给数据库，
   不要让浏览器做 OLAP。

---

## 小结

- scale 方案整画布 transform 缩放，1920 设计稿还原度最高。
- 六宫格 Grid + 固定 px 容器是大屏布局标准解。
- 实时曲线 = 定时 setOption + 滑动窗口；翻牌器 = rAF 缓动补间。
- 三态（loading/empty/error）必须齐全，空态比报错更常见。
- Vue3 手动集成务必 onBeforeUnmount 里 disconnect + dispose。
- 大屏接口走后端聚合，字段结构与 series 对齐，时间用时间戳。
