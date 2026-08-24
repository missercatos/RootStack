# SVG 基础

> SVG（Scalable Vector Graphics，可缩放矢量图形）是用 XML 描述二维图形的语言。
> 它画出来的不是"像素点"，而是"数学描述"——所以无论放大多少倍都不会失真。

---

## 1. SVG 是什么，定位在哪

SVG 本质是一份 XML 文档。浏览器把其中的标签解析成 DOM 节点，
再按几何公式渲染成图形。这带来三个关键特性：

1. **缩放无损**：描述的是形状而非像素，任意缩放都清晰。
2. **DOM 可交互**：每个图形都是真实节点，可以绑定事件、用 CSS 控制样式、用 JS 修改属性。
3. **文本性质**：可以用任何文本编辑器编写，可以被压缩、被检索、被版本管理。

### SVG vs Canvas：本质区别对照表

| 维度         | SVG                        | Canvas                      |
|--------------|----------------------------|-----------------------------|
| 本质         | 矢量，XML 描述形状          | 位图，像素级绘制             |
| DOM 结构     | 每个图形是独立节点           | 整张图是一个 canvas 节点      |
| 事件交互     | 直接给某个图形绑事件         | 只能监听整个画布，手动算坐标   |
| 缩放表现     | 无损放大                    | 放大模糊                     |
| 性能特点     | 节点多了变慢（几千个元素）    | 大量图形也快，但重绘要整幅重画 |
| 动画方式     | CSS / SMIL / JS 均可         | 主要靠 requestAnimationFrame |
| 文件可读性   | 打开就能看懂结构             | 二进制或像素指令              |
| 典型场景     | 图标、图表、插画、交互地图    | 游戏、图片处理、万级粒子       |

### 何时用谁：一句话决策

- 图标、Logo、需要交互的图表元素 → **SVG**
- 游戏画面、滤镜特效、上千个动态粒子 → **Canvas**
- 数据可视化：ECharts 默认用 Canvas 渲染，但支持切换成 SVG 渲染器
  （参见 [[前端开发/06-数据可视化/ECharts/01-ECharts基础|ECharts 基础]]）。

---

## 2. 三种引入方式

### 方式一：inline 内联（最常用，可交互）

直接把 `<svg>` 标签写进 HTML：

```html
<body>
  <svg width="120" height="120" viewBox="0 0 120 120">
    <circle cx="60" cy="60" r="50" fill="#4a90d9" />
  </svg>
</body>
```

内联的 svg 参与页面文档流，内部元素可以直接被 CSS 和 JS 控制——
做图标变色、图表交互必须用它。

### 方式二：img 标签引用

```html
<img src="./logo.svg" alt="站点标志" width="48" height="48" />
```

简单省事，浏览器会缓存。但 svg 内部无法访问外页面的 CSS 与 JS，
内部的动画（CSS animation 写在 svg 文件里）仍然有效。

### 方式三：background-image

```css
.icon-bg {
  width: 32px;
  height: 32px;
  background: url("./icon.svg") no-repeat center / contain;
}
```

纯装饰场景使用，同样无法从外部操控内部元素。

### 选型小结

| 方式        | 可交互 | 可缓存 | 适用场景           |
|-------------|--------|--------|--------------------|
| inline      | 是     | 否     | 图标系统、图表、动效 |
| img         | 否     | 是     | 内容型插图          |
| background  | 否     | 是     | 纯装饰背景          |

---

## 3. 基本形状七件套

所有基本形状都写在 `<svg>` 根标签内。先给一个公共画布：

```html
<svg width="300" height="200" viewBox="0 0 300 200"
     style="border: 1px solid #ccc">
  <!-- 下面各示例依次放入 -->
</svg>
```

### 3.1 rect 矩形

```html
<rect x="20" y="20" width="100" height="60"
      rx="8" ry="8" fill="#e74c3c" />
```

`x/y` 左上角坐标；`rx/ry` 圆角半径。

### 3.2 circle 圆形

```html
<circle cx="180" cy="50" r="30" fill="#3498db" />
```

`cx/cy` 圆心，`r` 半径。

### 3.3 ellipse 椭圆

```html
<ellipse cx="80" cy="140" rx="45" ry="25" fill="#2ecc71" />
```

横纵半径分开指定。

### 3.4 line 直线

```html
<line x1="150" y1="110" x2="260" y2="170"
      stroke="#333" stroke-width="2" />
```

线没有面积，填充无意义，必须给 `stroke` 才可见。

### 3.5 polyline 折线

```html
<polyline points="10,190 60,150 110,170 160,120 210,140"
          fill="none" stroke="#8e44ad" stroke-width="3" />
```

`points` 是 "x,y x,y x,y" 的序列。注意 `fill="none"`：
折线默认也会被填充出奇怪的多边形色块。

### 3.6 polygon 多边形

```html
<polygon points="250,20 290,70 250,120 210,70"
         fill="#f39c12" stroke="#b9770e" />
```

与 polyline 的唯一区别：自动首尾闭合。

### 3.7 path 路径（重点中的重点）

path 用一条 `d` 属性描述任意复杂形状，是 SVG 的终极武器。
前六个形状都能用 path 等价表达。命令字母大写表示绝对坐标，
小写表示相对坐标。

#### M — MoveTo 移动画笔（起点）

```html
<path d="M 20 20" stroke="#333" fill="none" />
```
把画笔移到 (20,20)，不画线。

#### L — LineTo 画直线

```html
<path d="M 20 180 L 100 100 L 180 180" stroke="#e67e22"
      stroke-width="3" fill="none" />
```

#### H / V — 水平、垂直线

```html
<path d="M 220 40 H 280 V 100 H 220 Z" fill="#16a085" />
```
H 后只跟一个 x 值，V 后只跟一个 y 值。

#### C — 三次贝塞尔曲线

```html
<path d="M 20 100 C 60 20, 140 20, 180 100"
      stroke="#c0392b" stroke-width="3" fill="none" />
```
`C c1x c1y, c2x c2y, x y`：两个控制点 + 终点。
曲线被两个控制点"拉扯"，像被两根橡皮筋牵引。

#### S — 平滑三次贝塞尔

```html
<path d="M 20 100 C 60 20, 140 20, 180 100
         S 300 180, 280 100"
      stroke="#c0392b" stroke-width="3" fill="none" />
```
S 自动把上一个 C 的第二控制点沿当前点镜像，作为自己的第一控制点，
只需再给一个控制点和终点，衔接处天然平滑。

#### Q — 二次贝塞尔曲线

```html
<path d="M 20 150 Q 90 40, 160 150"
      stroke="#2980b9" stroke-width="3" fill="none" />
```
只有一个控制点，适合简单的弧形弯曲。

#### T — 平滑二次贝塞尔

```html
<path d="M 20 150 Q 90 40, 160 150 T 300 150"
      stroke="#2980b9" stroke-width="3" fill="none" />
```
同理镜像上一控制点，连续波浪常用。

#### A — 圆弧（Arc）

```html
<path d="M 30 120 A 60 60 0 0 1 150 120"
      stroke="#27ae60" stroke-width="4" fill="none" />
```
参数依次为：`rx ry x-axis-rotation large-arc-flag sweep-flag x y`。
- `large-arc-flag`：1 取大弧，0 取小弧。
- `sweep-flag`：1 顺时针方向画，0 逆时针。

#### Z — 闭合路径

```html
<path d="M 200 40 L 240 40 L 240 80 Z" fill="#f1c40f" />
```
Z 从当前点画一条直线回到起点并封闭形状。

### path 命令速查表

| 命令 | 名称         | 参数                          |
|------|--------------|-------------------------------|
| M/m  | 移动         | x y                           |
| L/l  | 直线         | x y                           |
| H/h  | 水平线       | x                             |
| V/v  | 垂直线       | y                             |
| C/c  | 三次贝塞尔   | c1x c1y c2x c2y x y           |
| S/s  | 平滑三次     | c2x c2y x y                   |
| Q/q  | 二次贝塞尔   | cx cy x y                     |
| T/t  | 平滑二次     | x y                           |
| A/a  | 圆弧         | rx ry rot large sweep x y     |
| Z/z  | 闭合         | 无                            |

---

## 4. 坐标系与 viewBox

这是初学者最容易困惑的部分。先分清两个概念：

- **视口（viewport）**：svg 元素在页面上实际占据的矩形区域，
  由 `width/height` 决定，相当于"窗户"。
- **视图框（viewBox）**：svg 内部逻辑坐标系的可视范围，
  相当于"透过窗户看到的风景范围"。

```html
<!-- 视口 200x200，viewBox 显示逻辑坐标 0,0 到 400,400 的内容 -->
<svg width="200" height="200" viewBox="0 0 400 400">
  <circle cx="200" cy="200" r="150" fill="#8e44ad" />
</svg>
```

上面这个圆在逻辑坐标系里半径 150，渲染到 200x200 的视口时
整体被缩小了一半，视觉上半径 75。**内容随 viewBox 自动等比缩放**。

### preserveAspectRatio：宽高比不一致时怎么办

当视口和 viewBox 宽高比不同，浏览器需要一个对齐策略：

```html
<svg width="300" height="150" viewBox="0 0 200 200"
     preserveAspectRatio="xMidYMid meet">
</svg>
```

格式为 `preserveAspectRatio="<对齐X><对齐Y> <策略>"`：

| 参数值            | 行为                                     |
|-------------------|------------------------------------------|
| `xMidYMid meet`   | 居中，完整包含（默认），可能留白           |
| `xMidYMid slice`  | 居中，填满裁切（类似 object-fit: cover）  |
| `none`            | 强制拉伸，不保持比例（可能变形）           |

对齐部分还可以写 `xMin/xMax`、`YMin/YMax` 组合九宫格位置。

### 响应式图标原理

让 svg 随容器伸缩的经典套路：

```css
.responsive-svg {
  display: block;
  width: 100%;
  height: auto;
}
```

```html
<div style="width: 50%">
  <svg class="responsive-svg" viewBox="0 0 100 100">
    <circle cx="50" cy="50" r="40" fill="#3498db" />
  </svg>
</div>
```

要点：**只写 viewBox 不写 width/height**，svg 就会跟随 CSS 尺寸
等比缩放，内部坐标始终不变。这就是所有图标库"一个 svg 到处适配"的秘密。

---

## 5. fill 与 stroke 系列属性

SVG 的"上色"分两条线：fill 管内部，stroke 管轮廓。

```html
<rect x="40" y="40" width="160" height="90"
      fill="#3498db" fill-opacity="0.6"
      stroke="#1a5276" stroke-width="4"
      stroke-opacity="0.8"
      stroke-linecap="round"
      stroke-linejoin="round"
      stroke-dasharray="10 5"
      stroke-dashoffset="0" />
```

逐个说明：

| 属性              | 说明                                       |
|-------------------|--------------------------------------------|
| fill              | 填充色，`none` 表示不填充                   |
| fill-opacity      | 填充透明度 0~1                              |
| fill-rule         | 填充规则 nonzero/evenodd，影响镂空效果      |
| stroke            | 轮廓色                                      |
| stroke-width      | 轮廓宽度                                    |
| stroke-linecap    | 线端点样式 butt/round/square                |
| stroke-linejoin   | 转角样式 miter/round/bevel                  |
| stroke-dasharray  | 虚线模式，"实长 空长"，描边动画的核心（下一章）|
| stroke-dashoffset | 虚线起始偏移，同样服务于描边动画             |

fill 和 stroke 都支持三种值：颜色名、十六进制、函数式颜色
（rgb/rgba/hsl）。还支持 `url(#gradientId)` 引用渐变定义：

```html
<svg width="200" height="100" viewBox="0 0 200 100">
  <defs>
    <linearGradient id="grad1" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#ff7e5f" />
      <stop offset="100%" stop-color="#feb47b" />
    </linearGradient>
  </defs>
  <rect x="20" y="20" width="160" height="60" fill="url(#grad1)" />
</svg>
```

这些属性既可作为 presentation attribute 写在标签上，
也可以全部搬进 CSS——CSS 的优先级高于属性写法。

---

## 6. g 分组与 transform

`<g>` 是"组"容器，把若干元素打包，统一施加样式与变换：

```html
<svg width="300" height="200" viewBox="0 0 300 200">
  <g id="tree" fill="#27ae60" stroke="#145a32"
     transform="translate(150, 40)">
    <polygon points="0,60 -35,0 35,0" />
    <polygon points="0,30 -28,-20 28,-20" />
    <rect x="-6" y="58" width="12" height="22" fill="#795548" />
  </g>
</svg>
```

组内所有元素继承 g 上写的 fill/stroke（除非自己覆盖）。

### transform 四种变换

transform 可以叠加多个变换，从左到右依次应用：

```html
<g transform="translate(50,0) rotate(15) scale(1.2)"></g>
```

| 变换               | 说明                                   |
|--------------------|----------------------------------------|
| translate(x,y)     | 平移                                   |
| rotate(angle,cx,cy)| 旋转，可选绕某点（默认绕原点 0,0）      |
| scale(sx,sy)       | 缩放，sy 省略时等于 sx                 |
| skewX(a) skewY(a)  | 倾斜                                   |

特别注意：**rotate/scale 默认以画布原点 (0,0) 为中心**。
想绕图形自身中心转，惯用组合是先 translate 到中心、旋转、再平移回来：

```html
<rect x="-30" y="-20" width="60" height="40"
      transform="translate(150,100) rotate(30)" fill="#e74c3c" />
```

这里 rect 以自身中心为原点定义坐标，translate 把它放到目标位置，
rotate 就自然绕自身中心旋转了。这个技巧在 SVG 动画里极其常用。

---

## 7. 实战：手绘一个简单 Logo

目标：一个"山与太阳"风格的极简 Logo，只用 path/circle/polygon 完成。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<title>Mountain Sun Logo</title>
<style>
  body {
    margin: 0;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f4f6f8;
  }
  .logo { width: 240px; height: auto; }
  .logo .mountain { fill: #2c3e50; }
  .logo .snow { fill: #ecf0f1; }
  .logo .sun { fill: #f39c12; }
  .logo:hover .sun {
    fill: #e67e22;
    transition: fill 0.3s;
  }
</style>
</head>
<body>

<svg class="logo" viewBox="0 0 240 180"
     xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="山与太阳标志">

  <!-- 背景 -->
  <rect width="240" height="180" rx="18" fill="#dfe9f3" />

  <!-- 太阳：circle 即可 -->
  <circle class="sun" cx="172" cy="52" r="24" />

  <!-- 远山：一条 path，两个山峰用 Q 弧过渡 -->
  <path class="mountain" d="
    M 10 170
    L 78 66
    Q 92 46 106 66
    L 174 170
    Z" />

  <!-- 雪顶：小三角盖在主峰上 -->
  <polygon class="snow" points="78,66 64,88 70,82 78,94 86,82 92,88" />

  <!-- 近山：颜色更深，形成层次 -->
  <path fill="#1a252f" opacity="0.85" d="
    M 96 170
    L 158 84
    L 230 170
    Z" />

  <!-- 底部装饰线 -->
  <line x1="24" y1="170" x2="216" y2="170"
        stroke="#95a5a6" stroke-width="4" stroke-linecap="round" />
</svg>

</body>
</html>
```

拆解要点：

1. **只有 viewBox 没有 width/height**，靠 CSS 控制尺寸，天然响应式。
2. 山体用 `L` 直线 + `Q` 弧线混合，比纯三角柔和。
3. 雪顶用 polygon 的锯齿 points 模拟积雪边缘。
4. hover 时太阳变色——因为内联 svg 的元素可以被外部 CSS 选中，
   这是位图永远做不到的。

保存为 html 直接打开即可运行。尝试修改：
把远山的 Q 换成 C，观察控制点带来的形状变化；
给近山加 `transform="skewX(-6)"` 看倾斜效果。

---

## 小结

- SVG 是 XML 矢量语言：缩放无损、DOM 可交互，与 Canvas 位图互补。
- 引入三法：inline 要交互、img/background 要缓存。
- 七种基本形状中 path 是万能形态，十个命令 M L H V C S Q T A Z 必须熟记。
- viewBox 是理解 SVG 缩放的钥匙：内容坐标系与视口分离。
- fill/stroke 全家桶 + g 分组 transform，足以画出绝大多数静态图形。

下一篇我们让这些图形动起来：
[[前端开发/06-数据可视化/SVG/02-SVG动画|SVG 动画]]
