# HTML 基础语法

## HTML 是什么

HTML（HyperText Markup Language，超文本标记语言）是浏览器用来"理解页面结构"的标记语言。要精确定位它，最好的方式是和真正的编程语言对比：

| 对比维度 | 编程语言（Java/C/Python） | 标记语言（HTML/XML/Markdown） |
|---------|--------------------------|------------------------------|
| 本质 | 描述**计算过程**，有逻辑分支与循环 | 描述**数据结构**，声明"这段内容是什么" |
| 执行 | 被解释或编译执行 | 被**解析**成树形结构 |
| 变量与逻辑 | 有变量、条件、循环、函数 | 完全没有 |
| 出错行为 | 语法错误通常直接报错中断 | 浏览器容错极强，写错了也尽量渲染 |

给有后端背景的读者一个类比：**HTML 之于网页，就像 XML/JSON 之于配置文件**——它不执行任何逻辑，只负责声明结构。Spring 的 `application.yml` 声明"端口是 8080"，HTML 声明"这个标题是一级标题"。真正干活的是 JavaScript（逻辑）和 CSS（样式），它们分别对应编程语言和另一套声明式规则系统。

"超文本"指的是文本中可以包含指向其他文档的链接（hyperlink），这也是 Web 得名的原因——整个互联网就是由 HTML 文档通过链接编织成的网。

另一个重要认知：**HTML 不是被"编译"的，而是被浏览器解析成一棵 DOM 树**（Document Object Model）。你在浏览器按 F12 看到的 Elements 面板，就是这棵树。后续所有 CSS 选择器和 JS 操作都发生在这棵树上。

---

## 文档结构

一个最小但完整的 HTML5 文档长这样：

```html
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8">
    <title>我的第一个页面</title>
  </head>
  <body>
    <h1>你好，世界</h1>
    <p>这是我的第一个 HTML 页面。</p>
  </body>
</html>
```

逐行拆解：

### DOCTYPE 声明

```html
<!DOCTYPE html>
```

这不是标签，而是**文档类型声明**，告诉浏览器"请用现代标准模式渲染我"。历史包袱：2014 年之前的 HTML 4 时代，DOCTYPE 是一长串引用 DTD 的文字；HTML5 把它简化成了上面这一行。如果漏掉它，浏览器会进入"怪异模式"（quirks mode），用上世纪的兼容规则渲染——最典型的坑是盒模型计算方式变化，布局莫名错乱。记住：**永远第一行写 `<!DOCTYPE html>`**。

### html 根元素

```html
<html lang="zh-CN">
```

整棵树只有一个根节点。`lang` 属性声明页面语言，搜索引擎和无障碍屏幕阅读器依赖它（比如中文页面朗读时切换中文语音库）。中国区页面写 `zh-CN`。

### head：给机器看的元信息

`head` 里的内容**不会显示在页面上**，它是给浏览器、搜索引擎、爬虫看的：

- `<meta charset="UTF-8">`：字符编码声明。不写的话中文可能乱码。必须放在 head 最前面
- `<title>`：浏览器标签页标题，也是搜索结果的标题来源
- 其他 meta（SEO、viewport 等）详见 [[前端开发/01-基础/HTML/02-HTML表单与语义化|HTML 表单与语义化]]

类比后端：head 相当于 HTTP 响应头 + 配置元数据，body 才是响应体。

### body：给人看的内容

用户在页面上看到的一切都在 body 里。下面进入正题。

---

## 常用元素全解

### 元素的语法形态

HTML 元素有三种形态，先认识一下：

```html
<!-- 双标签：有开有闭，中间包内容（最常见） -->
<p>这是一个段落</p>

<!-- 单标签（自闭合）：没有内容，只有属性 -->
<img src="logo.png" alt="站点标志">
<br>
<hr>

<!-- 属性：写在开标签内，键值对形式 -->
<a href="https://example.com" target="_blank">示例链接</a>
```

标签名**不区分大小写**，但约定俗成全部小写。属性值可以用双引号、单引号甚至不加引号，但规范推荐统一双引号。

### 标题：h1 到 h6

```html
<h1>一级标题：每个页面只用一次</h1>
<h2>二级标题：章节</h2>
<h3>三级标题：小节</h3>
```

要点：

- `h1` 是页面主标题，**一个页面原则上只出现一次**（类似一本书的书名）
- 标题层级要连续，不要从 `h2` 直接跳到 `h5`——爬虫靠标题层级理解文档大纲，类似你读技术书时的目录树
- **不要因为 h1 字号大就拿来当普通大字用**，字号是 CSS 的事，标题表达的是结构含义

类比：标题体系就是 Markdown 的 `#` 到 `######`，或者 Word 的标题样式。你不会在 Word 里拿正文加粗当章节名，同理。

### 段落与文本

```html
<p>这是一个段落。浏览器会自动在段落之间加上下间距。</p>

<p>行内强调：<strong>加粗且语义为重要</strong>，
<em>斜体且语义为强调</em>。</p>

<p>换行用 br 标签<br>地址等强制换行场景。</p>

<p>长单词或 URL 可以用 wbr 提示浏览器可断行处。</p>
```

区分两组容易混淆的标签：

| 语义标签 | 只管样式的旧标签 | 说明 |
|---------|-----------------|------|
| `<strong>` 重要 | `<b>` 加粗 | strong 有语义，屏幕阅读器会重读 |
| `<em>` 强调 | `<i>` 斜体 | em 有语义 |
| `<del>` 已删除 | `<s>` 不再准确 | del 常配合 ins（插入）展示修订 |

原则：**能用语义标签就用语义标签**，纯视觉需求交给 CSS。

### 链接：a 元素

```html
<!-- 外部链接 -->
<a href="https://developer.mozilla.org">MDN 文档</a>

<!-- 在新标签页打开（外部链接惯例） -->
<a href="https://example.com" target="_blank" rel="noopener">新窗口打开</a>

<!-- 页内锚点：跳到 id 为 section2 的元素 -->
<a href="#section2">跳到第二章</a>
<h2 id="section2">第二章</h2>

<!-- 相对路径链接站内页面 -->
<a href="./about.html">关于我们</a>

<!-- 链接到邮箱 / 电话 -->
<a href="mailto:someone@example.com">发邮件</a>
<a href="tel:+8613800000000">打电话</a>
```

要点：

- `href` 是 hypertext reference，缺了它的 `a` 只是占位符
- `target="_blank"` 打开新标签页时**务必加 `rel="noopener"`** 防止新页面通过 `window.opener` 操纵你的页面（安全问题）
- 锚点跳转是纯客户端行为，不产生网络请求

### 图片：img 元素

```html
<!-- 必备三属性：src 来源、alt 替代文本、宽高防抖动 -->
<img src="cat.jpg" alt="一只橘猫趴在键盘上" width="640" height="480">

<!-- alt 的正确用法：图片无法加载或用户使用读屏器时朗读的内容 -->
<!-- 装饰性图片 alt 留空即可，不要省略属性 -->
<img src="divider.png" alt="">

<!-- 响应式图片：根据屏幕宽度选择不同尺寸源 -->
<img src="photo-small.jpg"
     srcset="photo-small.jpg 480w, photo-large.jpg 1080w"
     sizes="(max-width: 600px) 480px, 1080px"
     alt="风景照片">
```

alt 是新手最容易漏的属性。它有三重价值：图片挂了显示占位文字；视障用户的屏幕阅读器朗读它；搜索引擎用它理解图片内容（图片 SEO 的核心）。**写 alt 时描述图片内容本身，而不是"图片"两个字**。

width/height 显式声明可以让浏览器提前预留空间，避免图片加载完成时页面跳动（CLS 累积布局偏移，性能优化核心指标之一）。

### 列表

三种列表各有用途：

```html
<!-- 无序列表：菜单、要点集合，最常用 -->
<ul>
  <li>前端三件套</li>
  <li>框架</li>
</ul>

<!-- 有序列表：步骤、排行榜 -->
<ol>
  <li>下载安装包</li>
  <li>运行安装程序</li>
  <li>配置环境变量</li>
</ol>

<!-- 描述列表：术语定义、键值对展示 -->
<dl>
  <dt>HTTP</dt>
  <dd>超文本传输协议，Web 的应用层协议</dd>
  <dt>DNS</dt>
  <dd>域名解析系统</dd>
</dl>
```

注意 `ul/ol` 的**直接子元素只能是 li**，需要嵌套就嵌套在 li 内部：

```html
<ul>
  <li>
    前端基础
    <ul>
      <li>HTML</li>
      <li>CSS</li>
    </ul>
  </li>
</ul>
```

列表默认样式（圆点、序号、缩进）都可以用 CSS 清掉，导航栏几乎都是用 ul 搭建的。

### 表格

表格用于展示**二维数据**，不是用来布局的（上古时代曾用 table 排版，早已废弃）：

```html
<table>
  <caption>2024 年度语言排行</caption>
  <thead>
    <tr>
      <th scope="col">排名</th>
      <th scope="col">语言</th>
      <th scope="col">评分</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>Python</td>
      <td>15.2%</td>
    </tr>
    <tr>
      <td>2</td>
      <td>Java</td>
      <td>9.7%</td>
    </tr>
  </tbody>
</table>
```

结构要点：

- `caption` 表格标题，thead/tbody/tfoot 分区，爬虫和阅读器靠这些分区理解表格
- `th` 是表头单元格（默认加粗居中），`scope="col"/"row"` 声明表头作用方向，无障碍必需
- 跨行列用 `colspan="2"`（横向合并两列）、`rowspan="3"`（纵向合并三行）

类比后端：一张语义完整的 table 就像数据库结果集带上了元数据——caption 是表注释，thead 是字段名，tbody 是数据行。

### div 与 span：无语义容器

```html
<!-- div：块级无语义容器，独占一行 -->
<div class="card">
  <div class="card-header">标题区</div>
  <div class="card-body">内容区</div>
</div>

<!-- span：行内无语义容器，包裹一小段文字做样式钩子 -->
<p>价格：<span class="price">199 元</span></p>
```

两者都是"没有含义的透明容器"，存在的唯一意义是**作为 CSS 和 JS 的挂载点**。区别只在显示方式：

| 元素 | 显示方式 | 典型用途 |
|------|---------|---------|
| div | block，独占一行 | 划分页面区块 |
| span | inline，跟随文字流 | 给几个字加样式 |

关键纪律：**当你找不到合适的语义标签时才用 div/span**；如果有 header、nav、article 这些语义标签可用却用了 div，就叫"div 滥用"。语义化标签详见 [[前端开发/01-基础/HTML/02-HTML表单与语义化|HTML 表单与语义化]]。

---

## 属性全局观

有些属性可以写在任何元素上，称为全局属性。四个最重要的：

### id：唯一标识

```html
<div id="app">整个页面 id 必须唯一</div>
```

- 全文档唯一，重复 id 是 bug（CSS 只命中第一个，JS 查询也只返回第一个）
- 主要用途：锚点定位、JS 快速获取（`document.getElementById`）
- 现代开发约定：id 少用，class 为主——因为 id 无法复用，且优先级过高难以覆盖（优先级问题详见 [[前端开发/01-基础/CSS/02-选择器与盒模型|选择器与盒模型]]）

### class：分类标记

```html
<div class="card highlighted">可叠加多个类，空格分隔</div>
```

- 可复用、可叠加，是 CSS 样式的主要挂钩点
- 类比后端：class 像"标签注解"，同一个对象可以打多个注解，多个对象共享同一注解

### style：行内样式

```html
<p style="color: red; font-size: 14px;">紧急提示</p>
```

直接把 CSS 写在属性里，优先级极高（仅次于 !important）。仅用于 JS 动态设置样式或极特殊的临时覆盖，日常样式不应这样写，原因见 [[前端开发/01-基础/CSS/01-CSS基础语法|CSS 基础语法]] 中三种引入方式的对比。

### data-*：自定义数据

```html
<li data-user-id="42" data-role="admin">管理员甲</li>
```

以 `data-` 开头的自定义属性，浏览器不解析但保留在 DOM 上，JS 通过 `element.dataset.userId` 读取。用途：把业务数据暂存在 DOM 上，供交互脚本取用（框架出现前的经典手法，如今仍常用于无框架页面）。

其他常用全局属性速览：

| 属性 | 用途 |
|------|------|
| title | 鼠标悬停提示文字 |
| hidden | 隐藏元素（等效 display:none） |
| tabindex | 控制 Tab 键聚焦顺序 |
| contenteditable | 让元素内容可编辑 |

---

## 注释与实体字符

### 注释

```html
<!-- 这是 HTML 注释，不会显示在页面上 -->
<!--
  多行注释也可以。
  注意：注释虽然不显示，但会随源码发给浏览器，
  不要在注释里写敏感信息。
-->
```

条件注释（IE 时代的黑科技）已成历史，了解即可。

### 实体字符

HTML 中 `<`、`>`、`&`、引号有特殊语法含义，想在正文里原样显示它们就要用实体转义：

| 写法 | 显示 | 说明 |
|------|------|------|
| `&lt;` | < | less than |
| `&gt;` | > | greater than |
| `&amp;` | & | and 符号本身 |
| `&quot;` | " | 双引号 |
| `&nbsp;` | 空格 | 不会被折叠的不换行空格 |
| `&copy;` | © | 版权符 |
| `&#169;` | © | 十进制 Unicode 码点写法 |

最常见的实际场景：在技术博客里展示代码 `<div>` 要写成 `&lt;div&gt;`。另外浏览器会把连续空白折叠为一个空格，想保留多个空格用 `&nbsp;`。

---

## 实战：个人简介页

综合运用本章知识，写一个完整可运行的个人简介页。保存为 `profile.html`，双击即可在浏览器打开。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>张三 · 个人简介</title>
</head>
<body>
  <!-- 头部：姓名与一句话介绍 -->
  <header>
    <img src="avatar.jpg" alt="张三的头像" width="96" height="96">
    <h1>张三</h1>
    <p><strong>后端工程师</strong>，正在学习前端，目标是成为全栈开发者。</p>
  </header>

  <hr>

  <!-- 技能清单：无序列表 -->
  <section id="skills">
    <h2>技能清单</h2>
    <ul>
      <li>Java / Spring Boot —— 三年企业级开发经验</li>
      <li>MySQL / Redis —— 数据建模与缓存设计</li>
      <li>HTML / CSS —— 学习中，见本页即为练习成果</li>
    </ul>
  </section>

  <!-- 项目经历：有序列表 + 表格 -->
  <section id="projects">
    <h2>项目经历</h2>

    <h3>订单中心重构</h3>
    <ol>
      <li>梳理老系统接口并编写迁移方案</li>
      <li>基于 Spring Boot 重构订单服务</li>
      <li>灰度切换流量，平滑下线老服务</li>
    </ol>

    <table>
      <caption>主要项目概览</caption>
      <thead>
        <tr>
          <th scope="col">项目</th>
          <th scope="col">角色</th>
          <th scope="col">技术栈</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>订单中心</td>
          <td>主力开发</td>
          <td>Java, MySQL, Redis</td>
        </tr>
        <tr>
          <td>数据看板</td>
          <td>独立开发</td>
          <td>HTML, ECharts</td>
        </tr>
      </tbody>
    </table>
  </section>

  <!-- 联系方式：描述列表 + 链接 -->
  <section id="contact">
    <h2>联系我</h2>
    <dl>
      <dt>邮箱</dt>
      <dd><a href="mailto:zhangsan@example.com">zhangsan@example.com</a></dd>
      <dt>Github</dt>
      <dd><a href="https://github.com/zhangsan" target="_blank" rel="noopener">github.com/zhangsan</a></dd>
    </dl>
  </section>

  <footer>
    <p><small>&copy; 2026 张三 &middot; 用记事本也能写网页</small></p>
  </footer>
</body>
</html>
```

代码讲解：

1. **结构划分**：header / section / footer 先搭骨架，即使此刻还不深究其语义细节（下一章展开），也比一坨 div 强得多
2. **每张图片都有 alt**：头像加载失败时会显示"张三的头像"
3. **外链带 rel="noopener"**：安全习惯从一开始养成
4. **实体字符实战**：页脚版权符用了 `&copy;` 与 `&middot;`
5. **id 用于锚点**：三个 section 都有 id，方便日后做目录跳转

下一步把这个页面变漂亮——请继续 [[前端开发/01-基础/CSS/01-CSS基础语法|CSS 基础语法]]；先补完 HTML 的表单与语义化则看 [[前端开发/01-基础/HTML/02-HTML表单与语义化|HTML 表单与语义化]]。
