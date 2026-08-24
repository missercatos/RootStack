# CSS 基础语法

从本章开始进入 CSS。先校准心态：CSS 不是编程语言，没有变量（原生层面）、没有逻辑，它是一套**声明式的规则匹配系统**——你描述"什么样的元素应该长什么样"，浏览器负责匹配执行。用后端思维类比：它更像 nginx 配置或正则表达式，而不是 Java。

上一章的博客页已有骨架，本章结束时你会把它变漂亮。

---

## CSS 是什么与基本语法

CSS（Cascading Style Sheets，层叠样式表）由一条条**规则**组成，每条规则分两半：

```css
/* 选择器 { 属性: 值; } */
h1 {
  color: #2563eb;
  font-size: 28px;
}

p, li {          /* 逗号分组：多个选择器共享一套样式 */
  line-height: 1.8;
}
```

- **选择器**：回答"给谁穿衣服"
- **声明块**：花括号内一组"属性: 值"，回答"穿什么"
- 注释只有 `/* ... */` 一种，不支持 `//`
- 大小写不敏感，但约定全小写；最后一条声明的分号可省略但**永远写上**，避免追加时出错

"层叠"（Cascading）是理解 CSS 的钥匙词：多条规则可以同时命中同一个元素，浏览器按优先级规则**叠出最终效果**。谁覆盖谁的详细算法下一章展开，本章建立直觉即可。

---

## 三种引入方式

### 1. 内联样式（style 属性）

```html
<p style="color: red; font-size: 14px;">写在标签上的样式</p>
```

### 2. 内部样式（style 标签）

```html
<head>
  <style>
    p { color: #333; }
  </style>
</head>
```

### 3. 外部样式（link 标签，推荐）

```html
<head>
  <link rel="stylesheet" href="style.css">
</head>
```

三种方式对比：

| 方式 | 作用范围 | 可缓存 | 可复用 | 适用场景 |
|------|---------|--------|--------|---------|
| 内联 style 属性 | 单个元素 | 否 | 否 | JS 动态设置、极特殊覆盖 |
| 内部 style 标签 | 单个页面 | 否 | 否 | 单页 demo、关键首屏样式 |
| **外部 link 文件** | 全站 | **是** | **是** | 一切正式项目 |

推荐外部样式的理由，后端工程师秒懂：

1. **关注点分离**：HTML 管结构、CSS 管外观，改皮肤不动骨架
2. **缓存红利**：十个页面引用同一个 style.css，浏览器只需下载一次——就像依赖包进了本地仓库
3. **复用**：一个文件管全站主题

内联样式还有个技术副作用：优先级极高难以覆盖（下一章细讲），代码审查时看到大段 style 属性通常视为坏味道。

---

## 选择器初识

四种最基础的选择器，覆盖日常一半以上的场景：

```css
/* 1. 元素选择器：所有该标签 */
p {
  color: #333;
}

/* 2. 类选择器：所有 class 含此名的元素（主力！） */
.highlight {
  background: #fef08a;
}

/* 3. id 选择器：文档中唯一的那个元素 */
#site-header {
  border-bottom: 1px solid #ddd;
}

/* 4. 后代选择器：空格连接，命中任意深度的子孙 */
article p {
  line-height: 1.8;   /* article 里所有的 p，不管嵌多深 */
}
```

类选择器是现代 CSS 的绝对主力，理由：

- 可复用（一个类贴无数个元素）
- 可叠加（一个元素挂多个类）
- 与 HTML 结构解耦（换标签不用改样式）

id 选择器要节制使用：它不可复用且优先级过高，覆盖它的样式需要更高代价。团队规范通常是"样式挂钩一律用类，id 只留给锚点和 JS 定位"。

更多选择器（属性/伪类/伪元素/组合器）见 [[前端开发/01-基础/CSS/02-选择器与盒模型|选择器与盒模型]]。

---

## 层叠与继承

两个核心概念，各用一个类比说清。

### 继承：子承父业

部分属性会从父元素**自动传给孩子**：

```html
<body style="font-family: sans-serif; color: #222">
  <!-- 不写任何样式，里面所有文字都是 sans-serif 和 #222 -->
  <p>我继承了 body 的字体和颜色 <strong>我也是</strong></p>
</body>
```

会继承的：字体类（font-*）、文本类（color、line-height、text-align）等"环境气质"型属性。
不会继承的：盒模型类（margin/padding/border/width）等"身体尺寸"型属性。

类比：继承像遗传气质——父亲的口音孩子自然会有（不必逐个设置），但身高体重不会自动一样。这也是为什么全局样式总是设在 `body` 或 `:root` 上：设一次，全站继承。

### 层叠：多方竞争

同一个元素可能被多条规则命中：

```css
p        { color: gray; }
.message { color: blue; }   /* 类比元素选择器更具体 */
```

```html
<p class="message">我是蓝色的</p>
```

两条都命中，`color` 只能有一个赢家——层叠机制按以下顺序裁决（简化版）：

1. 来源与重要性：浏览器默认样式 < 用户样式 < 开发者样式（!important 另算）
2. 优先级（specificity）：更具体的规则赢（下节初步感知）
3. 源码顺序：优先级打平，后写的赢

所以浏览器默认样式（比如 h1 的加粗大字、a 的蓝色下划线）才会被你的样式轻松覆盖。

---

## 优先级初步：谁覆盖谁

完整记分法下一章展开，这里先给直觉版结论：

**行内样式 > id > 类 > 元素选择器**

```css
p          { color: gray; }   /* 元素级 */
.note      { color: blue; }   /* 类级：赢过元素级 */
#special   { color: red; }    /* id 级：赢过一切类 */
```

```html
<p class="note" id="special">红色</p>
```

直觉记忆：越"点名道姓"的规则权力越大——泛泛而谈所有段落（p）不如指名一个分类（.note），分类又不如直接报身份证号（#special）。而 style 行内属性相当于当面耳提面命，权力最大。

还有一个核武器 `!important`，能强行越过整个层级：

```css
p { color: black !important; }
```

能用，但**强烈建议少用**：它会打破正常层叠秩序，一旦滥用就不得不用更多 !important 去对抗，项目样式从此失控。把它当"消防灭火器"，不当"日常点火工具"。

---

## 常用属性速览

### 颜色 color

四种写法等价任选：

```css
p {
  color: red;                    /* 关键字（147 个预定义色名） */
  color: #ff0000;                /* 十六进制，可缩写 #f00 */
  color: rgb(255, 0, 0);         /* RGB 函数 */
  color: rgba(255, 0, 0, 0.5);   /* 带透明度，0 全透明 1 不透明 */
}
```

### 字体 font 系列

```css
body {
  /* 字体栈：从左到右找用户机器上有的字体，逗号隔开 */
  font-family: "Microsoft YaHei", "PingFang SC", sans-serif;

  font-size: 16px;       /* 页面基准字号惯例 16px */
  font-weight: bold;     /* 100-900 数字或 bold/normal */
  font-style: italic;    /* 斜体 */
  line-height: 1.8;      /* 行高：无单位数字 = 字号的倍数，推荐写法 */
}
```

要点：

- **字体栈必须以通用族结尾**（sans-serif 无衬线 / serif 衬线 / monospace 等宽），兜底保证任何机器都有得渲染
- 中文字体栈惯例："PingFang SC"（macOS）、"Microsoft YaHei"（Windows）、sans-serif 兜底
- line-height 写无单位数字而不是 px：跟随字号自动缩放

### 背景 background

```css
.card {
  background-color: #fff;
  background-image: url("bg.png");
  background-repeat: no-repeat;
  background-position: center;
  background-size: cover;      /* 铺满裁切，contain 则完整显示 */

  /* 五项合成一句（顺序自由） */
  background: #fff url("bg.png") no-repeat center / cover;
}
```

### 边框 border

```css
.box {
  border: 1px solid #ddd;   /* 宽度 样式 颜色，三合一 */
  border-radius: 8px;       /* 圆角，50% 即圆形 */
  border-bottom: 2px dashed red;  /* 单边单独设置 */
}
```

border-style 可选值：solid 实线 / dashed 虚线 / dotted 点线 / double 双线 / none 无。

### 间距 margin 与 padding

这是盒模型的核心成员，下一章有完整展开，先建立最小认知：

```css
.box {
  margin: 16px;              /* 外边距：元素与其他元素之间的距离（推别人） */
  padding: 16px;             /* 内边距：边框与内容之间的距离（留自己肚里空间） */
  margin: 8px 16px;          /* 两值：上下 8 左右 16 */
  margin: 8px 16px 24px 32px;/* 四值：上右下左，顺时针 */
}
```

记忆法：padding 是"内衬"（衣服里的垫层），margin 是"个人距离"（与他人保持的间隔）。

### 尺寸与显示

```css
.box {
  width: 300px;
  height: 120px;
  max-width: 100%;           /* 响应式图片的经典搭配 */
  display: block;            /* 显示方式，详见下一章 */
}
```

---

## 调试工具：DevTools 必会操作

学 CSS 不能靠猜，F12 打开开发者工具：

1. **Elements 面板**点选任意元素，右侧 Styles 面板列出命中的所有规则——被划掉的就是被层叠淘汰的，一眼看清"谁覆盖了谁"
2. **Computed 面板**查看最终计算值，排查"我明明写了为什么没生效"
3. 取消勾选某条声明实时预览效果，调试神器
4. 盒模型图示直接标出 content/padding/border/margin 各占多少像素

这个工具贯穿整个前端学习生涯，现在就开始用它验证本章每个示例。

---

## 实战：美化博客页

把 [[前端开发/01-基础/HTML/04-HTML实战：语义化页面|HTML 实战：语义化页面]] 的博客页穿上外衣。将以下内容保存为 `style.css`，与 blog-post.html 同目录，并在其 head 中加入 `<link rel="stylesheet" href="style.css">`。

```css
/* ===== 全局基准 ===== */
/* 先清掉浏览器默认的杂散间距，统一度量衡 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;   /* 让宽度包含 padding 和 border，下一章详述 */
}

/* 全站字体气质：设在根上，靠继承传播 */
body {
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 16px;
  line-height: 1.8;         /* 中文正文 1.7-1.9 最舒适 */
  color: #1f2937;           /* 深灰而非纯黑，阅读不刺眼 */
  background-color: #f5f5f4;/* 浅灰底衬托白色卡片 */
  max-width: 800px;         /* 正文限宽：一行太长读起来累 */
  margin: 0 auto;           /* 水平居中：上下0 左右auto */
  padding: 24px 16px;
}

/* ===== 链接默认态 ===== */
a {
  color: #2563eb;
  text-decoration: none;    /* 去下划线，靠颜色区分链接 */
}
a:hover {
  text-decoration: underline;
}

/* ===== 站点头 ===== */
.site-title {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 8px;
}

nav ul {
  list-style: none;         /* 去圆点：导航栏标准第一步 */
}
nav li {
  display: inline-block;    /* 列表项横排 */
  margin-right: 16px;
}

/* ===== 文章区 ===== */
article {
  background: #ffffff;
  border-radius: 8px;
  padding: 32px;
  margin-bottom: 24px;
}

article h1 {
  font-size: 28px;
  line-height: 1.4;
  margin-bottom: 8px;
}

article h2 {
  font-size: 22px;
  margin-top: 32px;
  margin-bottom: 12px;
  border-left: 4px solid #2563eb;  /* 标题左侧竖条装饰 */
  padding-left: 12px;
}

article h3 {
  font-size: 18px;
  margin-top: 24px;
  margin-bottom: 8px;
}

/* 段落间距：兄弟选择器思路的前置版，先简单处理 */
article p {
  margin-bottom: 16px;
}

code {
  background: #eef2ff;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 90%;
}

figure {
  margin: 24px 0;
}
figcaption {
  text-align: center;
  color: #6b7280;
  font-size: 14px;
  margin-top: 8px;
}

blockquote {
  border-left: 4px solid #d1d5db;
  padding-left: 16px;
  color: #6b7280;
  margin: 24px 0;
}

/* ===== 表格 ===== */
table {
  width: 100%;
  border-collapse: collapse; /* 合并相邻单元格边线 */
  margin: 24px 0;
}
th, td {
  border: 1px solid #e5e7eb;
  padding: 8px 12px;
  text-align: left;
}
thead th {
  background: #f9fafb;
}
caption {
  caption-side: bottom;
  color: #6b7280;
  font-size: 14px;
  padding-top: 8px;
}

/* ===== 评论与侧栏 ===== */
.comment {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 16px;
  margin-bottom: 12px;
}

input[type="text"], textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font: inherit;            /* 控件默认不继承字体，手动接上 */
}
button {
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 10px 24px;
  cursor: pointer;          /* 手势提示可点击 */
}
button:hover {
  background: #1d4ed8;
}
```

代码讲解：

1. **通配符重置 + box-sizing 打头阵**：所有布局问题的第一预防针，机制下一章讲透
2. **全局气质设在 body 上**：字体、行高、颜色一次声明全站继承，正是"继承"概念的落地
3. **max-width + margin auto**：纯 CSS 的水平居中容器套路，无框架时代的经典
4. **语义标签直接作选择器**（article/comment 区）：这就是语义化的红利——结构即样式钩子，几乎不需要额外类名
5. **hover 反馈**：按钮变色、链接下划线，最小的交互反馈意识

刷新页面，上一章的素颜 HTML 已然像模像样。下一步深入选择器与盒模型：[[前端开发/01-基础/CSS/02-选择器与盒模型|选择器与盒模型]]。
